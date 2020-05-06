select
-- max_day_max_hour.max_hour ->> 'viewCount' as db_view,
max_day_max_hour.max_hour ->> 'subscriberCount' as db_subscribers
from (
select
    coalesce(
        hour_23, hour_22, hour_21, hour_20, hour_19, hour_18, hour_17, hour_16, hour_15, hour_14, hour_13,
        hour_12, hour_11, hour_10, hour_9, hour_8, hour_7, hour_6, hour_5, hour_4, hour_3, hour_2, hour_1, hour_0
    ) as max_hour
from channel_statistics
where stat_date = (select max(stat_date) from channel_statistics)
) max_day_max_hour