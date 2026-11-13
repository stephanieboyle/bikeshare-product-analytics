"""Rebuild aggregate outputs from local real data, with no snapshot-level inference."""
import json
from pathlib import Path

import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .availability import intervals, summarise, weighted_availability, zero_episodes

COLOUR = '#23676f'
SOURCE = 'Source: Capital Bikeshare published trips; independent non-commercial analysis.'


def save(fig, name, note=SOURCE):
    fig.text(.01, -.10, note, fontsize=9, color='#555555', va='top')
    fig.savefig(f'reports/figures/{name}.png', dpi=170, bbox_inches='tight')
    plt.close(fig)


def report(db='data/bikeshare.duckdb'):
    Path('reports/figures').mkdir(parents=True, exist_ok=True)
    c = duckdb.connect(db, read_only=True)
    c.execute("set timezone='UTC'")
    plt.rcParams.update({'axes.spines.top': False, 'axes.spines.right': False,
                         'font.size': 10, 'axes.titlesize': 13})
    audit = c.sql('select source_month, quality_status, count(*) n from stg_trips group by all order by all').df()
    trips = c.sql('''select analysis_month, count(*) n,
       count(*) filter(where departure_station_code is null) missing_start,
       count(*) filter(where arrival_station_code is null) missing_end,
       count(*) filter(where duration_seconds < 60) subminute,
       count(*) filter(where member_casual = 'member') members,
       count(*) filter(where rideable_type = 'electric_bike') electric
       from fct_trips group by all order by all''').df()
    duplicates = c.sql('select count(*)-count(distinct ride_id) from stg_trips').fetchone()[0]
    conflicts = c.sql('''select count(*) from (select ride_id from raw_trips group by ride_id having
      count(distinct (rideable_type, started_at, ended_at, start_station_id, end_station_id,
                      member_casual)) > 1)''').fetchone()[0]
    if conflicts:
        raise ValueError(f'{conflicts} conflicting ride IDs: resolve before publishing')
    daily = c.sql('select start_local::date as day, count(*) n from fct_trips group by all order by day').df()
    fig, ax = plt.subplots(figsize=(10, 3.8), layout='constrained')
    ax.plot(pd.to_datetime(daily.day), daily.n, color=COLOUR, linewidth=1.4)
    ax.set(title='HISTORICAL • Completed rentals vary across the observed period',
           ylabel='Eligible completed rentals / local day', xlabel='2026 • America/New_York')
    ax.ticklabel_format(axis='y', style='plain')
    save(fig, '01_historical_daily')
    hourly = c.sql('''select extract(isodow from start_local)::int dow,
      extract(hour from start_local)::int as hour, count(*) n from fct_trips group by all''').df()
    dates = pd.date_range(daily.day.min(), daily.day.max(), freq='D')
    day_counts = pd.Series(dates.dayofweek + 1).value_counts()
    grid = hourly.pivot(index='dow', columns='hour', values='n').reindex(index=range(1, 8),
             columns=range(24), fill_value=0).fillna(0)
    grid = grid.div(day_counts.reindex(grid.index), axis=0)
    fig, ax = plt.subplots(figsize=(10, 3.8), layout='constrained')
    im = ax.imshow(grid, aspect='auto', cmap='YlGnBu')
    ax.set(title='HISTORICAL • Time windows describe served trips, not unmet demand',
           xlabel='Departure hour • America/New_York', yticks=range(7),
           yticklabels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], xticks=range(0, 24, 2))
    fig.colorbar(im, ax=ax, label='Mean completed rentals per matching day')
    save(fig, '02_historical_hour_weekday')
    mix = c.sql('select member_casual, rideable_type, count(*) n from fct_trips group by all').df()
    table = mix.pivot(index='member_casual', columns='rideable_type', values='n').fillna(0)
    fig, ax = plt.subplots(figsize=(8, 4), layout='constrained')
    table.rename(columns={'classic_bike': 'Classic bike', 'electric_bike': 'Electric bike'}).plot.barh(
        stacked=True, ax=ax, color=[COLOUR, '#cd9062'])
    ax.set(title='HISTORICAL • Rental mix does not identify rider purpose',
           xlabel='Eligible completed rentals', ylabel='Published rider category')
    ax.ticklabel_format(axis='x', style='plain')
    ax.legend(title='Rideable type', loc='lower right')
    save(fig, '03_historical_mix')
    candidates = c.sql('''select departure_station_code, max(start_station_name) as name,
     count(*) filter(where extract(isodow from start_local) <= 5 and
       (extract(hour from start_local) between 7 and 9 or extract(hour from start_local) between 16 and 18)) core,
     count(*) filter(where extract(isodow from start_local) <= 5 and
       (extract(hour from start_local) between 6 and 9 or extract(hour from start_local) between 15 and 19)) wide
     from fct_trips where departure_station_code is not null group by all order by core desc''').df()
    top = candidates.head(10).sort_values('core')
    fig, ax = plt.subplots(figsize=(10, 5), layout='constrained')
    y = np.arange(len(top))
    ax.barh(y + .18, top.wide, height=.34, label='06–10 + 15–20', color='#c4d9d9')
    ax.barh(y - .18, top.core, height=.34, label='07–10 + 16–19', color=COLOUR)
    ax.set(yticks=y, yticklabels=top['name'], xlabel='Weekday completed departures in assumed windows',
           title='HISTORICAL • High-volume candidates for investigation')
    ax.legend(title='Local windows (end excluded)')
    save(fig, '04_historical_candidates', SOURCE + '\nSelection: top 10 by core-window served trips; no claim of stockouts.')
    summary = {'evidence_class': 'HISTORICAL completed rentals',
        'months': trips.to_dict('records'), 'quality_audit': audit.to_dict('records'),
        'duplicate_ride_rows': duplicates, 'conflicting_ride_ids': conflicts,
        'core_window_departures': int(candidates.core.sum()),
        'wide_window_departures': int(candidates.wide.sum()),
        'top_candidates': candidates.head(10).to_dict('records'),
        'top10_overlap_core_wide': len(set(candidates.head(10).departure_station_code) &
            set(candidates.nlargest(10, 'wide').departure_station_code)),
        'period_start_local': str(daily.day.min()), 'period_end_local': str(daily.day.max()),
        'full_month_ingestion': all(json.loads(x[0])['row_limit'] is None for x in
                                    c.sql('select manifest from ingestion_manifest').fetchall())}
    arrivals = c.sql("""select extract(hour from end_local)::int as hour, count(*) n
        from fct_trips where extract(isodow from end_local) <= 5
        and end_local::date between (select min(start_local)::date from fct_trips)
        and (select max(start_local)::date from fct_trips) group by all order by 1""").df()
    departures = hourly[hourly.dow <= 5].groupby('hour').n.sum().reindex(range(24), fill_value=0)
    nweekdays = int(sum(dates.dayofweek < 5))
    fig, ax = plt.subplots(figsize=(9, 4), layout='constrained')
    ax.plot(departures.index, departures / nweekdays, color=COLOUR, label='Departures')
    ax.plot(arrivals.hour, arrivals.n / nweekdays, color='#b46d3b', label='Arrivals')
    ax.set(title='HISTORICAL • Journey timing includes departure and return needs',
           xlabel='Local hour • America/New_York', ylabel='Mean eligible rentals per weekday',
           xticks=range(0, 24, 2))
    ax.legend()
    save(fig, '06_historical_departure_arrival', SOURCE +
         '\nSame local date horizon; arrivals after 31 October excluded. Rides selected by departure month.')
    summary['archive_month_boundaries'] = c.sql("""select source_month, strftime(start_local,'%Y%m') as start_month,
      strftime(end_local,'%Y%m') as end_month, count(*) n from stg_trips group by all order by all""").df().to_dict('records')
    summary['duration_audit'] = c.sql("""select
      count(*) filter(where duration_seconds <= 0) as nonpositive,
      count(*) filter(where duration_seconds > 86400) as over_24h,
      count(*) filter(where dst_unresolved) as dst_unresolved,
      count(*) filter(where strftime(start_local, '%Y%m') != source_month) as start_outside_month
      from stg_trips""").df().to_dict('records')[0]
    summary['missing_stations_by_type'] = c.sql("""select rideable_type, count(*) n,
       count(*) filter(where departure_station_code is null) as missing_start,
       count(*) filter(where arrival_station_code is null) as missing_end
       from fct_trips group by all order by 1""").df().to_dict('records')
    summary['weekday_arrivals_within_horizon'] = int(arrivals.n.sum())
    summary['weekday_departures_within_horizon'] = int(departures.sum())
    summary['weekday_calendar_days'] = nweekdays
    # Live-data summaries are a separate evidence class and remain descriptive.
    if c.sql("select count(*) from information_schema.tables where table_name='live_status'").fetchone()[0]:
        rows = c.sql('select * from live_status').df()
        if not rows.empty:
            start, end = float(rows.retrieved.min()), float(rows.retrieved.max())
            universe_path = Path(db).parent / 'raw/monitored_universe.json'
            universe = json.loads(universe_path.read_text())['stations']
            info = json.loads(c.sql('select payload from station_metadata order by retrieved desc limit 1')
                              .fetchone()[0])['data']['stations']
            codes = [x['short_name'] for x in info]
            if len(codes) != len(set(codes)):
                raise ValueError('Station short_name mapping is not one-to-one')
            historical_codes = c.sql('''select distinct departure_station_code code from fct_trips
                where departure_station_code is not null''').df()
            unmatched = historical_codes[~historical_codes.code.isin(codes)]
            matched_rides = c.sql('''select departure_station_code, count(*) n from fct_trips
                where departure_station_code is not null group by all''').df()
            summary['station_mapping'] = {'historical_departure_codes': len(historical_codes),
                'current_metadata_codes': len(codes), 'unmatched_codes': len(unmatched),
                'unmatched_departures': int(matched_rides.loc[
                    ~matched_rides.departure_station_code.isin(codes), 'n'].sum()),
                'caveat': 'Current metadata lookup is not a historical station dimension; no historical capacity join.'}
            age = rows.retrieved - rows.last_reported
            live = {'evidence_class': 'PROSPECTIVE technical pilot, not stable reliability estimates',
                    'start_utc': pd.Timestamp(start, unit='s', tz='UTC').isoformat(),
                    'end_utc': pd.Timestamp(end, unit='s', tz='UTC').isoformat(),
                    'horizon_seconds': end - start, 'stations_in_frozen_universe': len(universe),
                    'snapshots': int(rows.snapshot_id.nunique()), 'station_observations': len(rows),
                    'report_age_seconds_median': float(age.median()),
                    'report_age_seconds_p95': float(age.quantile(.95)),
                    'stale_station_observation_share': float(((age < 0) | (age > 300)).mean()),
                    'collector_runs': c.sql('select success, count(*) n from collection_runs group by all').df()
                                      .to_dict('records')}
            if end > start:
                metrics = []
                for freshness in [180, 300, 600]:
                    for hold in [120, 180]:
                        for threshold in [1, 2]:
                            frame = intervals(rows, start, end, freshness, hold, threshold)
                            for kind in ['departure', 'arrival']:
                                station = summarise(frame, universe, start, end, kind)
                                Path('reports/private').mkdir(exist_ok=True)
                                if (freshness, hold, threshold) == (300, 180, 1):
                                    station.to_csv(f'reports/private/pilot_{kind}.csv', index=False)
                                    live[f'{kind}_observed_zero_runs'] = len(zero_episodes(frame, kind))
                                metrics.append({'freshness_s': freshness, 'hold_s': hold,
                                    'threshold': threshold, 'kind': kind,
                                    'time_weighted_availability': float(weighted_availability(station)),
                                    'equal_station_availability': float(station.availability.mean()),
                                    'coverage': float(station.valid_seconds.sum() /
                                        station.expected_eligible_seconds.sum()),
                                    'stations_coverage_ge_80pct': int((station.coverage >= .8).sum()),
                                    'stations_with_defined_availability': int(station.availability.notna().sum()),
                                    'observed_closed_station_seconds': float(station.observed_closed_seconds.sum()),
                                    'valid_station_seconds': float(station.valid_seconds.sum()),
                                    'expected_eligible_station_seconds': float(station.expected_eligible_seconds.sum())})
                live['sensitivity'] = metrics
                live['vehicle_type_availability'] = []
                for vehicle_type in ['1', '2']:
                    typed = summarise(intervals(rows, start, end, vehicle_type=vehicle_type),
                                      universe, start, end)
                    live['vehicle_type_availability'].append({'vehicle_type_id': vehicle_type,
                        'time_weighted_availability': float(weighted_availability(typed)),
                        'coverage': float(typed.valid_seconds.sum() / typed.expected_eligible_seconds.sum())})
                live['feed_age_seconds_median'] = float((rows.retrieved - rows.feed_time).median())
                live['feed_age_seconds_p95'] = float((rows.retrieved - rows.feed_time).quantile(.95))
            Path('reports/pilot_summary.json').write_text(json.dumps(live, indent=2, allow_nan=False))
    manifests = [dict(month=m, **json.loads(v)) for m, v in
                 c.sql('select month, manifest from ingestion_manifest order by month').fetchall()]
    Path('reports/source_manifest.json').write_text(json.dumps(manifests, indent=2))
    Path('reports/summary.json').write_text(json.dumps(summary, indent=2, default=str))
    c.close()
    return summary
