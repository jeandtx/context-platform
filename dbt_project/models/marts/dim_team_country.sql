{{ config(materialized='table') }}

/*
  dim_team_country
  Correspondance équipe ↔ pays via matching textuel (volontairement fragile).
  Les équipes dont le nom ne contient pas un nom de pays connu obtiennent country_name = NULL (LEFT JOIN).
*/

with teams as (
    select
        team_id,
        team_name,
        team_gender,
        team_country
    from {{ ref('dim_teams') }}
),

countries as (
    select
        country_name,
        iso2
    from {{ ref('dim_countries') }}
),

matched as (
    select
        t.team_id,
        t.team_name,
        -- NULL when no country name is found within the team name (LEFT JOIN)
        c.country_name
    from teams t
    left join countries c
        -- textual match: check if country name appears inside team name (case-insensitive)
        -- this approach is intentionally fragile by design
        on lower(t.team_name) like '%' || lower(c.country_name) || '%'
)

select
    team_id,
    team_name,
    country_name
from matched
