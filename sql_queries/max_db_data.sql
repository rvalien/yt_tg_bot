with
raw as (select hour, views, subscribers
    from (select unnest(array['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']) as hour,
    unnest(array[
    hour_0 ->> 'viewCount', hour_1 ->> 'viewCount', hour_2 ->> 'viewCount', hour_3 ->> 'viewCount', hour_4 ->> 'viewCount', hour_5 ->> 'viewCount', hour_6 ->> 'viewCount',
    hour_7 ->> 'viewCount', hour_8 ->> 'viewCount', hour_9 ->> 'viewCount', hour_10 ->> 'viewCount', hour_11 ->> 'viewCount', hour_12 ->> 'viewCount', hour_13 ->> 'viewCount',
    hour_14 ->> 'viewCount', hour_15 ->> 'viewCount', hour_16 ->> 'viewCount', hour_17 ->> 'viewCount', hour_18 ->> 'viewCount', hour_19 ->> 'viewCount', hour_20 ->> 'viewCount',
    hour_21 ->> 'viewCount', hour_22 ->> 'viewCount', hour_23 ->> 'viewCount']) as views,
    unnest(array[
    hour_0 ->> 'subscriberCount', hour_1 ->> 'subscriberCount', hour_2 ->> 'subscriberCount', hour_3 ->> 'subscriberCount', hour_4 ->> 'subscriberCount', hour_5 ->> 'subscriberCount', hour_6 ->> 'subscriberCount',
    hour_7 ->> 'subscriberCount', hour_8 ->> 'subscriberCount', hour_9 ->> 'subscriberCount', hour_10 ->> 'subscriberCount', hour_11 ->> 'subscriberCount', hour_12 ->> 'subscriberCount', hour_13 ->> 'subscriberCount',
    hour_14 ->> 'subscriberCount', hour_15 ->> 'subscriberCount', hour_16 ->> 'subscriberCount', hour_17 ->> 'subscriberCount', hour_18 ->> 'subscriberCount', hour_19 ->> 'subscriberCount', hour_20 ->> 'subscriberCount',
    hour_21 ->> 'subscriberCount', hour_22 ->> 'subscriberCount', hour_23 ->> 'subscriberCount']) as subscribers
    from channel_statistics cs
--     where stat_date = current_date
    ) too_raw
)
select hour::int, views::int, subscribers::int from raw
where views = (select max(views) from raw)