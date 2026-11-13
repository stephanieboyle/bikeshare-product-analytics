select * from {{ ref('fct_trips') }}
where duration_seconds <= 0 or duration_seconds > 86400 or dst_unresolved
