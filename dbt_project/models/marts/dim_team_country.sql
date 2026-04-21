{{ config(materialized='table') }}

{%- set model_name = 'dim_team_country' -%}

-- Dimension: dim_team_country
-- Purpose: Linking table mapping teams to countries for aggregating team performance by country
-- Grain: One row per team-country pair
-- Materialization: Table
-- Note: Uses fragile text matching - team name must contain country name
--       Teams without matching country get NULL country_name (LEFT JOIN behavior)

select
    t.team_id,
    t.team_name,
    c.country_name
from {{ ref('dim_teams') }} t
left join {{ ref('dim_countries') }} c
    on lower(t.team_name) like '%' || lower(c.country_name) || '%'
