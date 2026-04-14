-- models/silver/silver_teams.sql

select distinct
    home_team_id AS team_id,
    home_team_name AS team_name,
    home_team_gender AS team_gender,
    home_team_country AS team_country,
from {{ ref('stg_matches') }}