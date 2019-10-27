select
min(subscribers) as subscribers,
min(views) as views,
date_part('day', moscow_dt) as day,
date_part('hour', moscow_dt) as hour,
moscow_dt as date
from (

select
	subscribers,
	views,
	datetime,
	datetime + interval '{0} hours' as moscow_dt

from  detektivo
    ) raw
        where moscow_dt >= current_date - INTERVAL '{1} DAY'
group by date, day, hour
order by date, day, hour

