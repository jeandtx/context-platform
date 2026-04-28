-- models/marts/fct_teams_by_country.sql
-- Aggregation: Count of unique teams per country

with teams as (
  select distinct
    team_id,
    team_name,
    team_country
  from {{ ref('dim_teams') }}
),

teams_by_country as (
  select
    team_country as country,
    count(distinct team_id) as num_teams,
    count(distinct team_name) as num_unique_team_names
  from teams
  where team_country is not null
  group by team_country
)

select
  country,
  num_teams,
  num_unique_team_names
from teams_by_country
order by num_teams desc
