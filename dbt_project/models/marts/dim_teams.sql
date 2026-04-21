{{ config(materialized='table') }}

/*
  dim_teams — Reference table of unique teams that have played at least one home match.
  Grain: one row per team_id (identified by home_team_id from stg_matches).
  Teams that have never played at home are absent — documented limitation in context file.
  ROW_NUMBER deduplication handles cases where the same team_id has inconsistent
  home_team_country or home_team_gender metadata across different matches.
*/

with home_teams as (
    select
        home_team_id   as team_id,
        home_team_name as team_name,
        -- Capitalise gender to match accepted_values: "Male", "Female", "Mixed"
        -- DuckDB has no initcap(); use explicit CASE for the three known values
        CASE lower(home_team_gender)
            WHEN 'male'   THEN 'Male'
            WHEN 'female' THEN 'Female'
            WHEN 'mixed'  THEN 'Mixed'
            ELSE home_team_gender
        END as team_gender,
        home_team_country as team_country
    from {{ ref('stg_matches') }}
    where home_team_id   is not null
      and home_team_name is not null
      and home_team_name != ''
),

deduped as (
    select
        team_id,
        team_name,
        team_gender,
        team_country,
        row_number() over (partition by team_id order by team_name) as rn
    from home_teams
)

select
    team_id,
    team_name,
    team_gender,
    team_country
from deduped
where rn = 1
