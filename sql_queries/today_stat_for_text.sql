select
stat_date::date as date
, (max_hour ->> 'viewCount')::int - (min_hour ->> 'viewCount')::int as views
, (max_hour ->> 'subscriberCount')::int - (min_hour ->> 'subscriberCount')::int as subs

from (
select
stat_date
, coalesce(hour_0, hour_1, hour_2, hour_3, hour_4, hour_5, hour_6, hour_7, hour_8, hour_9, hour_10, hour_11, hour_12, hour_13, hour_14, hour_15, hour_16, hour_17, hour_18, hour_19, hour_20, hour_21, hour_22, hour_23) as min_hour
, coalesce(hour_23, hour_22, hour_21, hour_20, hour_19, hour_18, hour_17, hour_16, hour_15, hour_14, hour_13, hour_12, hour_11, hour_10, hour_9, hour_8, hour_7, hour_6, hour_5, hour_4, hour_3, hour_2, hour_1, hour_0) as max_hour
from channel_statistics cs
where stat_date = (select max(stat_date) from channel_statistics)
) foo

