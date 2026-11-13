"""Independent source-to-dashboard audit using pandas, not the dbt/SQL transformations.

Requires the original local ZIPs. Does not download or redistribute source data.
Run from the repository root: uv run python scripts/audit_numerical_accuracy.py
"""
import hashlib
import itertools
import json
import math
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MONTHS = ['202608', '202609', '202610']


def main():
    data = json.loads((ROOT / 'dashboard/data.json').read_text())
    summary = json.loads((ROOT / 'reports/summary.json').read_text())
    daily, hourly, departures, arrivals, core, wide, quality = (Counter() for _ in range(7))
    seen = set()
    source_rows = 0
    hashes = {}
    for month in MONTHS:
        path = ROOT / f'data/raw/{month}.zip'
        provenance = json.loads(path.with_suffix('.provenance.json').read_text())
        hashes[month] = hashlib.sha256(path.read_bytes()).hexdigest()
        assert hashes[month] == provenance['sha256'], f'Archive changed: {month}'
        with zipfile.ZipFile(path) as archive:
            names = [n for n in archive.namelist() if n.endswith('.csv') and not n.startswith('__MACOSX')]
            assert len(names) == 1
            for raw in pd.read_csv(archive.open(names[0]), dtype=str, keep_default_na=False,
                                   chunksize=100000):
                source_rows += len(raw)
                ids = set(raw.ride_id)
                assert len(ids) == len(raw) and not seen.intersection(ids), 'Duplicate source ride IDs'
                seen.update(ids)
                start = pd.to_datetime(raw.started_at, format='mixed', errors='coerce')
                end = pd.to_datetime(raw.ended_at, format='mixed', errors='coerce')
                start_z = start.dt.tz_localize('America/New_York', ambiguous='NaT', nonexistent='NaT')
                end_z = end.dt.tz_localize('America/New_York', ambiguous='NaT', nonexistent='NaT')
                duration = (end_z - start_z).dt.total_seconds()
                actual_month = start.dt.strftime('%Y%m')
                reasons = np.select([
                    raw.ride_id.eq(''), start.isna() | end.isna(),
                    start_z.isna() | end_z.isna(),
                    (duration <= 0) | (duration > 86400),
                    ~raw.rideable_type.isin(['classic_bike', 'electric_bike']),
                    ~raw.member_casual.isin(['member', 'casual']),
                    ~actual_month.isin(MONTHS)],
                    ['missing_ride_id', 'invalid_timestamp', 'unresolved_dst', 'invalid_duration',
                     'unknown_rideable', 'unknown_category', 'outside_analysis_period'], default='valid')
                quality.update({(month, str(k)): int(v) for k, v in pd.Series(reasons).value_counts().items()})
                keep = reasons == 'valid'
                valid = raw.loc[keep].copy()
                local = start.loc[keep]
                valid['month'] = actual_month.loc[keep]
                valid['day'] = local.dt.strftime('%Y-%m-%d')
                valid['dow'] = local.dt.dayofweek + 1
                valid['hour'] = local.dt.hour
                valid['n'] = 1
                valid['missing_start'] = valid.start_station_id.eq('').astype(int)
                valid['missing_end'] = valid.end_station_id.eq('').astype(int)
                keys = ['day', 'month', 'rideable_type', 'member_casual']
                grouped = valid.groupby(keys)[['n', 'missing_start', 'missing_end']].sum()
                for key, values in grouped.iterrows():
                    for field in ['n', 'missing_start', 'missing_end']:
                        daily[(*key, field)] += int(values[field])
                grouped = valid.groupby(['month', 'dow', 'hour', 'rideable_type', 'member_casual']).size()
                hourly.update({k: int(v) for k, v in grouped.items()})
                for direction, counter in [('start', departures), ('end', arrivals)]:
                    known = valid[valid[f'{direction}_station_id'].ne('')]
                    keys = ['month', f'{direction}_station_id', 'rideable_type', 'member_casual']
                    grouped = known.groupby(keys).size()
                    counter.update({k: int(v) for k, v in grouped.items()})
                for counter, hours in [(core, {7, 8, 9, 16, 17, 18}),
                                       (wide, set(range(6, 10)) | set(range(15, 20)))]:
                    window = valid[(valid.dow <= 5) & valid.hour.isin(hours) & valid.start_station_id.ne('')]
                    grouped = window.groupby(['month', 'start_station_id', 'rideable_type', 'member_casual']).size()
                    counter.update({k: int(v) for k, v in grouped.items()})
    expected_quality = Counter({(r['source_month'], r['quality_status']): r['n']
                                for r in summary['quality_audit']})
    assert quality == expected_quality, 'Exclusion waterfall differs from source recomputation'
    expected_daily = Counter({(r['day'], r['month'], r['bike'], r['rider'], field): r[field]
                              for r in data['daily'] for field in ['n', 'missing_start', 'missing_end']})
    assert daily == expected_daily, 'Daily cells differ'
    assert hourly == Counter({(r['month'], r['dow'], r['hour'], r['bike'], r['rider']): r['n']
                              for r in data['hourly']}), 'Weekday/hour cells differ'
    for field, counter in [('departures', departures), ('arrivals', arrivals), ('core', core), ('wide', wide)]:
        expected = Counter({(r['month'], r['code'], r['bike'], r['rider']): r[field]
                            for r in data['stations']})
        assert counter == expected, f'Station {field} cells differ'
    # Every public historical filter combination, including 'all' options.
    combinations = 0
    for month, bike, rider in itertools.product(['all', *MONTHS],
            ['all', 'classic_bike', 'electric_bike'], ['all', 'member', 'casual']):
        combinations += 1
        chosen = [r for r in data['daily'] if (month == 'all' or r['month'] == month)
                  and (bike == 'all' or r['bike'] == bike) and (rider == 'all' or r['rider'] == rider)]
        months = MONTHS if month == 'all' else [month]
        calendar_days = sum(pd.Period(m[:4] + '-' + m[4:]).days_in_month for m in months)
        assert len({r['day'] for r in chosen}) == calendar_days, 'Average/day omits zero-ride calendar days'
        total = sum(r['n'] for r in chosen)
        for field in ['missing_start', 'missing_end']:
            assert 0 <= sum(r[field] for r in chosen) <= total
    for key, counts in data['calendar'].items():
        dates = pd.date_range(f'2026-{int(key):02d}-01', periods=pd.Period(f'2026-{int(key):02d}').days_in_month)
        assert counts == [int((dates.dayofweek == d).sum()) for d in range(7)]
    totals = {field: sum(r[field] for r in data['daily']) for field in ['n', 'missing_start', 'missing_end']}
    totals['electric'] = sum(r['n'] for r in data['daily'] if r['bike'] == 'electric_bike')
    totals['members'] = sum(r['n'] for r in data['daily'] if r['rider'] == 'member')
    assert sum(core.values()) == summary['core_window_departures']
    assert sum(wide.values()) == summary['wide_window_departures']
    core_stations, wide_stations = Counter(), Counter()
    for counter, output in [(core, core_stations), (wide, wide_stations)]:
        for key, value in counter.items():
            output[key[1]] += value
    overlap = len(set(dict(core_stations.most_common(10))) & set(dict(wide_stations.most_common(10))))
    assert overlap == summary['top10_overlap_core_wide']
    for row in summary['top_candidates']:
        assert core_stations[row['departure_station_code']] == row['core']
        assert wide_stations[row['departure_station_code']] == row['wide']
    result = {'method': 'Independent pandas recomputation from original SHA-256-verified ZIPs; no dbt models used',
              'source_rows': source_rows, 'excluded_rows': sum(v for (_, reason), v in quality.items() if reason != 'valid'),
              'totals': totals, 'filter_combinations_checked': combinations,
              'daily_cells_checked': len(data['daily']), 'hourly_cells_checked': len(data['hourly']),
              'station_cells_checked': len(data['stations']), 'top10_window_overlap': overlap,
              'source_sha256': hashes}
    for field in ['missing_start', 'missing_end', 'electric', 'members']:
        result[field + '_percentage'] = 100 * totals[field] / totals['n']
    assert math.isclose(totals['n'] / 92, 21730.782608695652)
    (ROOT / 'reports/numerical_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
