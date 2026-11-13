"""Independently verify pilot summaries from raw saved GBFS bundles (no model imports)."""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    pilot = json.loads((ROOT / 'reports/pilot_summary.json').read_text())
    universe = json.loads((ROOT / 'data/raw/monitored_universe.json').read_text())['stations']
    bundles = [json.loads(p.read_text()) for p in (ROOT / 'data/raw/gbfs').glob('*.json')]
    bundles.sort(key=lambda b: b['retrieved']['station_status'])
    start, end = (bundles[i]['retrieved']['station_status'] for i in [0, -1])
    assert abs(end - start - pilot['horizon_seconds']) < 1e-6
    assert len(universe) == pilot['stations_in_frozen_universe']
    by_station = {s: [] for s in universe}
    ages = []
    for b in bundles:
        t = b['retrieved']['station_status']
        feed = b['feeds']['station_status']['last_updated']
        for row in b['feeds']['station_status']['data']['stations']:
            ages.append(t - row['last_reported'])
            if row['station_id'] in by_station:
                by_station[row['station_id']].append((t, feed, row))
    assert np.isclose(np.median(ages), pilot['report_age_seconds_median'])
    assert np.isclose(np.quantile(ages, .95), pilot['report_age_seconds_p95'])
    assert np.isclose(np.mean((np.array(ages) < 0) | (np.array(ages) > 300)),
                      pilot['stale_station_observation_share'])

    def evaluate(freshness, hold, threshold, kind, vehicle_type=None):
        numerators, denominators, eligible = [], [], []
        for records in by_station.values():
            available = valid = closed = 0.
            for i, (t, feed, r) in enumerate(records):
                nxt = records[i + 1][0] if i + 1 < len(records) else end
                report = r['last_reported']
                if not (0 <= t - report <= freshness and 0 <= t - feed <= freshness):
                    continue
                length = max(0., min(end, nxt, t + hold, report + freshness,
                                     feed + freshness) - max(start, t))
                operating = bool(r['is_installed']) and bool(r['is_renting' if kind == 'departure'
                                                               else 'is_returning'])
                if not operating:
                    closed += length
                    continue
                count = r['num_bikes_available' if kind == 'departure' else 'num_docks_available']
                if vehicle_type is not None:
                    counts = {v['vehicle_type_id']: v['count'] for v in r.get('vehicle_types_available', [])}
                    count = counts.get(vehicle_type)
                if count is not None:
                    valid += length
                    available += length * (count >= threshold)
            numerators.append(available)
            denominators.append(valid)
            eligible.append(end - start - closed)
        numerator, denominator = np.array(numerators), np.array(denominators)
        defined = denominator > 0
        return {'time_weighted_availability': float(numerator.sum() / denominator.sum()),
                'equal_station_availability': float((numerator[defined] / denominator[defined]).mean()),
                'coverage': float(denominator.sum() / sum(eligible)),
                'stations_coverage_ge_80pct': int(sum(v / e >= .8 for v, e in zip(denominators, eligible) if e)),
                'valid_station_seconds': float(denominator.sum())}
    for row in pilot['sensitivity']:
        actual = evaluate(row['freshness_s'], row['hold_s'], row['threshold'], row['kind'])
        for key, value in actual.items():
            assert np.isclose(value, row[key], rtol=1e-12, atol=1e-8), (row, key, value)
    for row in pilot['vehicle_type_availability']:
        actual = evaluate(300, 180, 1, 'departure', row['vehicle_type_id'])
        for key in ['coverage', 'time_weighted_availability']:
            assert np.isclose(actual[key], row[key], rtol=1e-12)
    result = {'method': 'Independent arithmetic from original saved GBFS JSON; no collector/model functions imported',
              'snapshots': len(bundles), 'stations': len(universe), 'horizon_seconds': end - start,
              'sensitivity_summaries_checked': len(pilot['sensitivity']), 'vehicle_type_summaries_checked': 2,
              'freshness_diagnostics': 'median, p95 and stale-observation share match'}
    (ROOT / 'reports/pilot_numerical_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
