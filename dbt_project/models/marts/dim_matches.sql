-- models/gold/fact_matches.sql

select
    match_id,
    match_date,
    home_team_name AS home_team,
    away_team_name AS away_team,
    home_score,
    away_score,
    case 
        when home_score > away_score then home_team
        when away_score > home_score then away_team
        else 'draw'
    end as winner
from {{ ref('stg_matches') }}