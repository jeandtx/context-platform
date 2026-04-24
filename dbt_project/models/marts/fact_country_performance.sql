-- models/gold/fact_country_performance.sql

select
  tc.country_name,
  count(*) as matches_played,
  sum(case when f.winner <> 'draw' then 1 else 0 end) as wins
from {{ ref('dim_matches') }} as f
inner join {{ ref('dim_team_country') }} as tc
  on f.home_team = tc.team_name
group by 1
