{{ config(materialized='table') }}

{%- set model_name = 'fact_country_performance' -%}

-- Fact: fact_country_performance
-- Purpose: Aggregated country sports performance (matches played and victories)
-- Grain: One row per country
-- Materialization: Table
-- Note: Only home matches are counted
--       Bug fix: winner calculation uses CASE WHEN to check if team name matches winner

select
    tc.country_name,
    count(distinct m.match_id) as matches_played,
    sum(case when m.winner = tc.team_name then 1 else 0 end) as wins  -- Known bug fix #2
from {{ ref('dim_matches') }} m
inner join {{ ref('dim_team_country') }} tc
    on m.home_team = tc.team_name
where tc.country_name is not null
group by tc.country_name
