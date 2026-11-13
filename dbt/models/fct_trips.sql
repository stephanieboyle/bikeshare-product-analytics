-- Grain: one eligible completed rental per ride_id. Missing stations do not remove trips.
select * exclude (row_number)
from (
 select *, row_number() over (partition by ride_id order by source_month, started_at, ended_at,
 start_station_id, end_station_id, rideable_type, member_casual) as row_number
 from {{ ref('stg_trips') }} where quality_status = 'valid'
) where row_number = 1
