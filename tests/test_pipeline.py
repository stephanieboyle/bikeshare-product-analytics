"""Offline integration tests: real dbt models against invented source records."""
import json
import os
import subprocess
import sys
from pathlib import Path

import duckdb
import pytest

from bikeshare_analytics.collect import validate_stations
from bikeshare_analytics.history import FIELDS, ingest


def test_schema_validation_rejects_duplicates_negative_counts():
    r = dict(station_id='a', num_bikes_available=1, num_docks_available=2,
             is_installed=1, is_renting=1, is_returning=1, last_reported=0)
    with pytest.raises(ValueError):
        validate_stations({'data': {'stations': [r, r]}})
    with pytest.raises(ValueError):
        validate_stations({'data': {'stations': [dict(r, num_bikes_available=-1)]}})


def test_dbt_dst_dedup_and_quality(tmp_path):
    db = tmp_path / 'fixture.duckdb'
    c = duckdb.connect(str(db))
    c.execute('create table raw_trips (' + ','.join(f'{n} varchar' for n in FIELDS) + ', source_month varchar)')
    def row(ride, start, end, month='202611', station='001'):
        return [ride, 'classic_bike', start, end, 'A', station, 'B', '002', '38', '-77',
                '38', '-77', 'member', month]
    records = [
        row('ok', '2026-11-02 08:00:00', '2026-11-02 08:10:00'),
        row('ok', '2026-11-02 08:00:00', '2026-11-02 08:10:00'),
        row('ambiguous', '2026-11-01 01:10:00', '2026-11-01 01:20:00'),
        row('spring_missing', '2026-03-08 02:10:00', '2026-03-08 03:20:00', '202603'),
        row('negative', '2026-11-02 08:10:00', '2026-11-02 08:00:00'),
        row('long', '2026-11-02 08:00:00', '2026-11-04 08:00:00'),
        row('missing_station', '2026-11-02 09:00:00', '2026-11-02 09:05:00', station=''),
        row('winter', '2026-11-02 08:00:00', '2026-11-02 08:10:00'),
        row('summer', '2026-08-02 08:00:00', '2026-08-02 08:10:00', '202608'),
    ]
    c.executemany('insert into raw_trips values (' + ','.join(['?'] * 14) + ')', records)
    c.close()
    env = dict(os.environ, BIKESHARE_DB=str(db), DBT_SEND_ANONYMOUS_USAGE_STATS='false')
    result = subprocess.run([str(Path(sys.executable).with_name('dbt')), 'build', '--project-dir', 'dbt', '--profiles-dir', 'dbt',
                             '--target-path', str(tmp_path / 'dbt_target'),
                             '--log-path', str(tmp_path / 'dbt_logs')],
                            env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    c = duckdb.connect(str(db))
    assert c.sql('select count(*) from fct_trips').fetchone()[0] == 4
    assert c.sql("select count(*) from stg_trips where quality_status='unresolved_dst'").fetchone()[0] == 2
    assert c.sql("select departure_station_code from fct_trips where ride_id='ok'").fetchone()[0] == '001'
    assert c.sql("select departure_station_code from fct_trips where ride_id='missing_station'").fetchone()[0] is None
    c.execute("set timezone='UTC'")
    hours = dict(c.sql("select ride_id, extract(hour from start_utc) from fct_trips where ride_id in ('summer','winter')").fetchall())
    assert hours == {'summer': 12, 'winter': 13}
    c.close()


def test_ingestion_replaces_month_idempotently(tmp_path, monkeypatch):
    import zipfile
    monkeypatch.chdir(tmp_path)
    archive = tmp_path / 'fixture.zip'
    import csv
    import io
    text = io.StringIO()
    writer = csv.writer(text)
    writer.writerow(FIELDS)
    writer.writerow(['abc', 'classic_bike', '2026-10-01 08:00:00', '2026-10-01 08:05:00',
                     'A', '001', 'B', '002', '38', '-77', '38', '-77', 'member'])
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('invented.csv', text.getvalue())
    archive.with_suffix('.provenance.json').write_text(json.dumps({'url': 'synthetic_fixture'}))
    monkeypatch.setattr('bikeshare_analytics.history.download', lambda month: archive)
    for _ in range(2):
        ingest(['202610'])
    c = duckdb.connect('data/bikeshare.duckdb')
    assert c.sql('select count(*) from raw_trips').fetchone()[0] == 1
    assert c.sql('select start_station_id from raw_trips').fetchone()[0] == '001'
    c.close()


def test_collector_idempotence_provenance_and_failure(tmp_path, monkeypatch):
    from bikeshare_analytics.collect import collect_once
    monkeypatch.chdir(tmp_path)
    base = dict(last_updated=100, ttl=60, version='2.3')
    station = dict(station_id='a', num_bikes_available=1, num_docks_available=2,
                   is_installed=1, is_renting=1, is_returning=1, last_reported=95)
    info = dict(station_id='a', short_name='001', name='Invented A', lat=38, lon=-77, capacity=3)
    names = ['station_information', 'station_status', 'system_information', 'vehicle_types']
    docs = {
        'discovery': dict(base, data={'en': {'feeds': [dict(name=n, url=n) for n in names]}}),
        'station_information': dict(base, data={'stations': [info]}),
        'station_status': dict(base, data={'stations': [station]}),
        'system_information': dict(base, data={'timezone': 'America/New_York'}),
        'vehicle_types': dict(base, data={'vehicle_types': []}),
    }
    def fetch(s, url):
        return docs[url if url in docs else 'discovery'], 100.
    monkeypatch.setattr('bikeshare_analytics.collect.fetch_json', fetch)
    for _ in range(2):
        assert collect_once() == 60
    c = duckdb.connect('data/bikeshare.duckdb')
    assert c.sql('select count(*) from live_status').fetchone()[0] == 1
    assert c.sql('select feed_time,last_reported,retrieved from live_status').fetchone() == (100, 95, 100.)
    assert c.sql('select count(*) from station_metadata').fetchone()[0] == 1
    c.close()
    def fail(s, url):
        raise ValueError('invented schema failure')
    monkeypatch.setattr('bikeshare_analytics.collect.fetch_json', fail)
    with pytest.raises(ValueError):
        collect_once()
    c = duckdb.connect('data/bikeshare.duckdb')
    assert c.sql('select count(*) from live_status').fetchone()[0] == 1
    assert c.sql('select count(*) from collection_runs where not success').fetchone()[0] == 1
    c.close()
