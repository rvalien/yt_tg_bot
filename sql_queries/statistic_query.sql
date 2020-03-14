with
body as (select generate_series{1} as day_of_{0}),
cur_{0} as (
select
	max(views) - min(views) as views
	, extract({2} from datetime at time zone 'utc' at time zone 'MSK') as day
from detektivo d where datetime at time zone 'utc' at time zone 'MSK' >= date_trunc('{0}', now())
group by day
order by day
),
prew_{0} as (
select
	max(views) - min(views) as views
	, extract({2} from datetime at time zone 'utc' at time zone 'MSK') as day
from detektivo where datetime at time zone 'utc' at time zone 'MSK' between date_trunc('{0}', now()- interval '1 {0}') and date_trunc('{0}', now())
group by day
order by day
)
select body.day_of_{0} as {0}, cur_{0}.views as current_{0}_views, prew_{0}.views as previous_{0}_views from body
left join cur_{0} on body.day_of_{0} = cur_{0}.day
left join prew_{0} on body.day_of_{0} = prew_{0}.day