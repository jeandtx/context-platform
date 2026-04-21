{{ config(materialized='table') }}

/*
  fact_country_performance
  Grain: one row per country.
  Scope: home matches only (away matches are intentionally excluded per context spec).
  Bug fix applied: wins counted as matches where winner = team_name, NOT winner != 'draw',
  which would incorrectly count away-team wins as home-country wins.
*/

with home_matches as (

    select
        f.match_id,
        f.home_team,
        f.winner
    from {{ ref('dim_matches') }} f

),

team_country as (

    select
        tc.team_name,
        tc.country_name
    from {{ ref('dim_team_country') }} tc
    where tc.country_name is not null  -- drop unmatched teams (no country resolved via text matching)

),

aggregated as (

    select
        tc.country_name,
        count(hm.match_id)                                                       as matches_played,
        -- fix: count wins where the home team (= this country's team) is the actual winner
        -- using winner = team_name; winner != 'draw' would also count away-team wins
        sum(case when hm.winner = tc.team_name then 1 else 0 end)::integer       as wins
    from home_matches hm
    inner join team_country tc
        on hm.home_team = tc.team_name
    group by tc.country_name

)

select
    country_name,
    matches_played,
    wins
from aggregated
