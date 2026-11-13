"""Half-open, capped station-state intervals; UTC seconds are the weighting unit."""
import json

import numpy as np
import pandas as pd


def intervals(rows, start, end, freshness=300, hold=180, threshold=1, vehicle_type=None):
    if end <= start or min(freshness, hold, threshold) <= 0:
        raise ValueError('Positive horizon and thresholds required')
    rows = rows.sort_values(['station_id', 'retrieved', 'snapshot_id']).drop_duplicates(
        ['station_id', 'retrieved'], keep='last')
    result = []
    for station, group in rows.groupby('station_id'):
        records = group.to_dict('records')
        for i, r in enumerate(records):
            next_time = records[i + 1]['retrieved'] if i + 1 < len(records) else end
            left = max(start, r['retrieved'])
            # Even closures expire; an old closure cannot erase days of missing coverage.
            basic_right = min(end, next_time, r['retrieved'] + hold)
            fresh = (0 <= r['retrieved'] - r['last_reported'] <= freshness and
                     0 <= r['retrieved'] - r['feed_time'] <= freshness)
            right = min(basic_right, r['last_reported'] + freshness, r['feed_time'] + freshness)
            if not fresh or right <= left:
                continue
            types = {x['vehicle_type_id']: x['count'] for x in json.loads(r['types_json'])}
            bikes = r['bikes'] if vehicle_type is None else types.get(vehicle_type)
            result.append({'station_id': station, 'left': left, 'right': right,
                           'seconds': right - left,
                           'departure_operating': bool(r['installed'] and r['renting']),
                           'arrival_operating': bool(r['installed'] and r['accepting_returns']),
                           'departure_known': bikes is not None,
                           'departure_available': bikes is not None and bikes >= threshold,
                           'arrival_available': r['docks'] >= threshold,
                           'departure_zero': bikes == 0,
                           'arrival_zero': r['docks'] == 0})
    return pd.DataFrame(result, columns=['station_id', 'left', 'right', 'seconds',
        'departure_operating', 'arrival_operating', 'departure_known', 'departure_available',
        'arrival_available', 'departure_zero', 'arrival_zero'])


def summarise(frame, universe, start, end, kind='departure'):
    if len(universe) != len(set(universe)) or end <= start:
        raise ValueError('Unique station universe and positive horizon required')
    output = []
    for station in universe:
        g = frame[frame.station_id == station]
        operating = g[f'{kind}_operating'].astype(bool)
        closed = g.loc[~operating, 'seconds'].sum()
        valid = operating
        if kind == 'departure':
            valid = valid & g.departure_known.astype(bool)
        denominator = g.loc[valid, 'seconds'].sum()
        numerator = g.loc[valid & g[f'{kind}_available'].astype(bool), 'seconds'].sum()
        eligible = end - start - closed
        output.append({'station_id': station, 'available_seconds': numerator,
            'valid_seconds': denominator, 'observed_closed_seconds': closed,
            'expected_eligible_seconds': eligible,
            'coverage': denominator / eligible if eligible else np.nan,
            'availability': numerator / denominator if denominator else np.nan})
    return pd.DataFrame(output)


def weighted_availability(summary, weights=None):
    """Time-weighting by default; explicit weights produce a mean of station ratios."""
    if weights is None:
        den = summary.valid_seconds.sum()
        return summary.available_seconds.sum() / den if den else np.nan
    s = summary.set_index('station_id').join(weights.rename('weight'), how='left')
    s = s[s.availability.notna() & s.weight.notna() & (s.weight >= 0)]
    return np.average(s.availability, weights=s.weight) if s.weight.sum() else np.nan


def zero_episodes(frame, kind='departure'):
    """Observed zero runs, split at all gaps/closures; duration is support, not exact episode length."""
    runs = []
    for station, group in frame.sort_values(['station_id', 'left']).groupby('station_id'):
        run = None
        for r in group.to_dict('records'):
            zero = r[f'{kind}_operating'] and r[f'{kind}_zero']
            if zero:
                if run is not None and abs(run['right'] - r['left']) < 1e-6:
                    run['right'] = r['right']
                else:
                    if run is not None:
                        runs.append(run)
                    run = {'station_id': station, 'left': r['left'], 'right': r['right']}
            elif run is not None:
                runs.append(run)
                run = None
        if run is not None:
            runs.append(run)
    return [dict(r, observed_seconds=r['right'] - r['left']) for r in runs]


def block_interval(daily, seed=173, repetitions=2000, block=7):
    """Future-day mean, moving blocks; require 56 consecutive daily ratios, no missing days."""
    if len(daily) < 56 or daily.isna().any():
        raise ValueError('At least 56 complete consecutive days required; report descriptively meanwhile')
    if not isinstance(daily.index, pd.DatetimeIndex):
        raise ValueError('Daily series must have a consecutive DatetimeIndex')
    # Calendar days can be 23 or 25 elapsed hours across daylight-saving changes.
    dates = daily.index.tz_localize(None).normalize()
    if not (dates.to_series().diff().dropna() == pd.Timedelta(days=1)).all():
        raise ValueError('Daily series must have a consecutive DatetimeIndex')
    rng = np.random.default_rng(seed)
    x = daily.to_numpy()
    means = []
    for _ in range(repetitions):
        starts = rng.integers(0, len(x) - block + 1, int(np.ceil(len(x) / block)))
        means.append(np.concatenate([x[s:s + block] for s in starts])[:len(x)].mean())
    return np.quantile(means, [.025, .975])
