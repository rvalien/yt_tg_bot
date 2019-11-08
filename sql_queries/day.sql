
/* day */

select distinct
    hour, date, day, dayofweek, week, month, lv - fv as views,  ls - fs as subscribers
from (
    select

        date_part('hour', datetime + interval '{0} hours') as hour,
        date_trunc('day', datetime + interval '{0} hours' ) as date,
        extract('day' from datetime + interval '{0} hours' ) as day,
        extract('week' from datetime + interval '{0} hours') as week,
        extract('month' from datetime + interval '{0} hours' ) as month,
        extract(isodow from  datetime + interval '{0} hours' ) as  dayofweek,
        first_value(views) over w as fv,
        last_value(views) over w as lv,
        first_value(subscribers) over w as fs,
        last_value(subscribers) over w as ls

    from {3}
    /*date_trunc returns timestamp like 2019-08-25 00:00:00 */
    where date_trunc('{2}', datetime + interval '{0} hours')  >= (current_date - interval '{1} {2}')
        window w as (
            PARTITION BY date_trunc('hour', datetime + interval '{0} hours' )
            ORDER BY datetime
            range between unbounded preceding and unbounded following
            )
            ORDER BY datetime) foo
            ORDER BY date, hour
