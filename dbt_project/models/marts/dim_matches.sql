{{ config(materialized='table') }}

with source as (

    select * from {{ ref('stg_matches') }}

),

renamed as (

    select
        match_id,
        home_team_name                              as home_team,
        away_team_name                              as away_team,
        home_score,
        away_score,

        -- winner determined by score comparison at full time;
        -- note: scores may include extra time / penalties (ambiguity documented in context)
        case
            when home_score > away_score then home_team_name
            when away_score > home_score then away_team_name
            else 'draw'
        end                                         as winner,

        match_date

    from source

)

select * from renamed
