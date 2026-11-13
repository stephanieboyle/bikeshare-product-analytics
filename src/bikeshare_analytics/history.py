"""Idempotent CSV ingestion with provenance; rejection happens visibly in dbt."""
import json
import zipfile
from pathlib import Path

import duckdb

from .io import atomic, download

FIELDS = ['ride_id', 'rideable_type', 'started_at', 'ended_at', 'start_station_name',
          'start_station_id', 'end_station_name', 'end_station_id', 'start_lat', 'start_lng',
          'end_lat', 'end_lng', 'member_casual']


def ingest(months, db='data/bikeshare.duckdb', limit=None):
    if limit is not None and limit < 1:
        raise ValueError('limit must be positive')
    Path(db).parent.mkdir(parents=True, exist_ok=True)
    c = duckdb.connect(str(db))
    c.execute('create table if not exists ingestion_manifest (month varchar primary key, manifest varchar)')
    for month in months:
        path = download(month)
        with zipfile.ZipFile(path) as z:
            members = [n for n in z.namelist() if n.endswith('.csv') and not n.startswith('__MACOSX')]
            if len(members) != 1:
                raise ValueError('Expected one CSV per month; review schema before extending')
            csv = Path('data/processed') / f'{month}.csv'
            if not csv.exists():
                atomic(csv, z.read(members[0]))
        # All strings: numeric-looking identifiers must retain their exact source representation.
        relation = c.read_csv(str(csv), header=True, all_varchar=True)
        if relation.columns != FIELDS:
            raise ValueError(f'CSV schema changed: {relation.columns}')
        c.execute('create or replace temp view incoming as select * from relation')
        c.execute('create table if not exists raw_trips as select *, ?::varchar as source_month from incoming limit 0',
                  [month])
        c.execute('begin')
        c.execute('delete from raw_trips where source_month = ?', [month])
        query = 'insert into raw_trips select *, ? from incoming'
        if limit is not None:
            query += f' limit {int(limit)}'
        c.execute(query, [month])
        provenance = json.loads(path.with_suffix('.provenance.json').read_text())
        provenance['row_limit'] = limit
        c.execute('insert or replace into ingestion_manifest values (?, ?)', [month, json.dumps(provenance)])
        c.execute('commit')
    c.close()
