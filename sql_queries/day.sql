select
	min(subscribers) as subscribers,
	min(views) as views,
	date_part('day', datetime + interval '{0} hours') as day,
	date_part('hour', datetime + interval '{0} hours') as hour
from
    detektivo where datetime + interval '{0} hours' >= current_date - INTERVAL '{1} DAY'
group by day, hour
order by day, hour
