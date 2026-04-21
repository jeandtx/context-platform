{{ config(materialized='table') }}

{%- set model_name = 'dim_teams' -%}

-- Dimension: dim_teams
-- Purpose: Reference table of sports teams with characteristics (gender, country)
-- Grain: One row per unique team that has played a home match
-- Materialization: Table
-- Note: Teams that have never played at home are excluded
-- Note: Deduplicate by team_id (primary key) to ensure grain

select distinct on (home_team_id)
    home_team_id::Integer as team_id,
    home_team_name as team_name,
    home_team_gender as team_gender,
    home_team_country as team_country
from {{ ref('stg_matches') }}
where home_team_id is not null
    and home_team_name is not null
order by home_team_id
