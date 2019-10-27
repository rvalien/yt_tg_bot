
/* month , week */

select distinct
     date, day, dayofweek, week, month, last_value - first_value as views
from (
    select
	    date_trunc('day', datetime + interval '{0} hours' ) as date,
	    extract('day' from datetime + interval '{0} hours' ) as day,
	    extract('week' from datetime + interval '{0} hours') as week,
        extract('month' from datetime + interval '{0} hours' ) as month,
	    extract(isodow from  datetime + interval '{0} hours' ) as  dayofweek,
        first_value(views) over w,
        last_value(views) over w
    from detektivo
    where date_part('{2}', datetime + interval '{0} hours') >= date_part('{2}', now() - interval '{1} {2}')
        window w as (
            PARTITION BY date_trunc('day', datetime + interval '{0} hours' )
            ORDER BY datetime
            range between unbounded preceding and unbounded following
            )
    ORDER BY datetime) foo
ORDER BY date