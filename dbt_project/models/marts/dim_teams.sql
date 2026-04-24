-- models/silver/silver_teams.sql

select distinct
  home_team_id as team_id,
  home_team_name as team_name,
  home_team_gender as team_gender,
  home_team_country as team_country
from {{ ref('stg_matches') }}
