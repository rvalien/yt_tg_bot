select distinct
    date, day, month, last_value - first_value as views
from (
    select
	    date_trunc('day', datetime + interval '{0} hours' ) as date,
        extract('month' from datetime + interval '{0} hours' ) as month,
	    extract('day' from datetime + interval '{0} hours' ) as day,
        first_value(views) over w,
        last_value(views) over w
    from detektivo
    where datetime + interval '{0} hours' >= current_date - interval '{1} DAY'
        window w as (
            PARTITION BY date_trunc('day', datetime + interval '{0} hours' )
            ORDER BY datetime
            range between unbounded preceding and unbounded following
            )
    ORDER BY datetime) foo
ORDER BY date