"""Invented, hand-checkable fixtures; never source observations."""
import json

import numpy as np
import pandas as pd
import pytest

from bikeshare_analytics.availability import (
    block_interval, intervals, summarise, weighted_availability, zero_episodes,
)


def rows(times=(0, 60, 120), bikes=2, docks=3, **changes):
    result = []
    for i, t in enumerate(times):
        r = dict(station_id='a', retrieved=t, feed_time=t, last_reported=t,
                 bikes=bikes, docks=docks, installed=True, renting=True, accepting_returns=True,
                 types_json=json.dumps([{'vehicle_type_id': '1', 'count': bikes}]), snapshot_id=str(i))
        r.update(changes)
        result.append(r)
    return pd.DataFrame(result)


def metric(r, end=180, **kwargs):
    return summarise(intervals(r, 0, end, **kwargs), ['a'], 0, end).iloc[0]


def test_always_available():
    s = metric(rows())
    assert s.availability == 1
    assert s.coverage == 1
    assert s.valid_seconds == 180


def test_always_empty_episode():
    f = intervals(rows(bikes=0), 0, 180)
    assert summarise(f, ['a'], 0, 180).iloc[0].availability == 0
    assert zero_episodes(f) == [dict(station_id='a', left=0, right=180, observed_seconds=180)]


def test_irregular_intervals_are_time_weighted():
    r = rows(times=(0, 30, 150))
    r.loc[1, 'bikes'] = 0
    s = metric(r, end=180)
    assert s.availability == pytest.approx(60 / 180)


def test_gap_expires_and_splits_zero_runs():
    r = rows(times=(0, 600), bikes=0)
    s = metric(r, end=660, hold=120)
    assert s.coverage == pytest.approx(180 / 660)
    assert len(zero_episodes(intervals(r, 0, 660, hold=120))) == 2


def test_stale_report_is_missing_not_empty():
    r = rows(last_reported=-301, bikes=0)
    s = metric(r)
    assert s.valid_seconds == 0
    assert s.coverage == 0
    assert np.isnan(s.availability)


def test_feed_age_and_report_age_both_cap_state():
    r = rows(times=(100,), feed_time=90, last_reported=80)
    f = intervals(r, 100, 300, freshness=60)
    assert f.iloc[0].seconds == 40
    assert metric(rows(feed_time=-400)).coverage == 0


def test_future_timestamp_rejected():
    assert metric(rows(last_reported=1000)).coverage == 0


def test_closed_station_never_counts_as_success_or_stockout():
    f = intervals(rows(bikes=0, renting=False), 0, 180)
    s = summarise(f, ['a'], 0, 180).iloc[0]
    assert s.valid_seconds == 0
    assert s.expected_eligible_seconds == 0
    assert np.isnan(s.coverage)
    assert not zero_episodes(f)
    # Arrival can still be operating when departure rental is disabled.
    assert summarise(f, ['a'], 0, 180, 'arrival').iloc[0].availability == 1


def test_duplicate_snapshot_does_not_double_time():
    r = rows()
    assert metric(pd.concat([r, r])).valid_seconds == 180


def test_unobserved_station_stays_in_denominator():
    f = intervals(rows(), 0, 180)
    s = summarise(f, ['a', 'unobserved'], 0, 180)
    assert s.iloc[1].coverage == 0
    assert np.isnan(s.iloc[1].availability)
    assert s.valid_seconds.sum() / s.expected_eligible_seconds.sum() == .5


def test_type_missing_is_not_zero_and_threshold_sensitivity():
    assert metric(rows(), vehicle_type='missing').coverage == 0
    assert metric(rows(bikes=1), threshold=2).availability == 0
    assert metric(rows(bikes=1), threshold=1).availability == 1


def test_weighted_average_examples():
    s = pd.DataFrame({'station_id': ['a', 'b'], 'valid_seconds': [90, 10],
                      'available_seconds': [90, 0], 'availability': [1., 0.]})
    assert weighted_availability(s) == .9
    assert weighted_availability(s, pd.Series({'a': 1, 'b': 1})) == .5
    assert weighted_availability(s, pd.Series({'a': 1, 'b': 3})) == .25


def test_dst_fall_back_uses_elapsed_utc_time():
    start = pd.Timestamp('2026-11-01T05:30:00Z').timestamp()
    end = pd.Timestamp('2026-11-01T06:30:00Z').timestamp()
    # Both map to 01:30 local, yet an hour actually elapses.
    assert pd.Timestamp(start, unit='s', tz='UTC').tz_convert('America/New_York').hour == 1
    assert pd.Timestamp(end, unit='s', tz='UTC').tz_convert('America/New_York').hour == 1
    r = rows(times=(start,))
    f = intervals(r, start, end, hold=3600, freshness=3600)
    assert summarise(f, ['a'], start, end).iloc[0].valid_seconds == 3600


def test_inference_refuses_short_or_gapped_series():
    with pytest.raises(ValueError):
        block_interval(pd.Series([.9] * 14))
    index = pd.date_range('2026-01-01', periods=56)
    interval = block_interval(pd.Series([.9] * 56, index=index), repetitions=100)
    assert np.allclose(interval, [.9, .9])
