{{ config(materialized='table') }}

{%- set model_name = 'dim_matches' -%}

-- Dimension: dim_matches
-- Purpose: Match dimension with teams, scores, and winner determination
-- Grain: One row per unique match
-- Materialization: Table
-- Note: Winner is calculated based on score comparison (draw if tied)

select
    match_id,
    home_team_name as home_team,
    away_team_name as away_team,
    home_score,
    away_score,
    match_date,
    case
        when home_score > away_score then home_team_name
        when away_score > home_score then away_team_name
        else 'draw'
    end as winner
from {{ ref('stg_matches') }}
