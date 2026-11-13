-- Grain: one source row before ride-ID deduplication. Keep invalid rows for audit.
with parsed as (
 select *, try_cast(started_at as timestamp) as start_local,
        try_cast(ended_at as timestamp) as end_local,
        nullif(start_station_id, '') as departure_station_code,
        nullif(end_station_id, '') as arrival_station_code
 from raw_trips
), zoned as (
 select *, timezone('America/New_York', start_local) as start_utc,
        timezone('America/New_York', end_local) as end_utc from parsed
), flagged as (
 select *, epoch(end_utc - start_utc) as duration_seconds,
  (timezone('America/New_York', start_utc) != start_local
   or timezone('America/New_York', start_utc + interval 1 hour) = start_local
   or timezone('America/New_York', start_utc - interval 1 hour) = start_local
   or timezone('America/New_York', end_utc) != end_local
   or timezone('America/New_York', end_utc + interval 1 hour) = end_local
   or timezone('America/New_York', end_utc - interval 1 hour) = end_local) as dst_unresolved
 from zoned
)
select *, case
 when nullif(ride_id, '') is null then 'missing_ride_id'
 when start_local is null or end_local is null then 'invalid_timestamp'
 when dst_unresolved then 'unresolved_dst'
 when duration_seconds <= 0 or duration_seconds > 86400 then 'invalid_duration'
 when rideable_type not in ('classic_bike','electric_bike') or rideable_type is null then 'unknown_rideable'
 when member_casual not in ('member','casual') or member_casual is null then 'unknown_category'
 when strftime(start_local, '%Y%m') != source_month then 'outside_source_month'
 else 'valid' end as quality_status
from flagged
