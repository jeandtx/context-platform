{{ config(materialized='table') }}

-- Grain: one row per country. Only home matches are counted (per context file).
select
  tc.country_name,
  count(*)::bigint as matches_played,
  -- a win = the winner is the home team itself (draws and away wins excluded)
  sum(case when f.winner = tc.team_name then 1 else 0 end)::bigint as wins
from {{ ref('dim_matches') }} as f
inner join {{ ref('dim_team_country') }} as tc
  on f.home_team = tc.team_name
-- dim_team_country uses a LEFT JOIN upstream: unmatched teams have a NULL country
-- and must not form a NULL-country group
where tc.country_name is not null
group by 1
