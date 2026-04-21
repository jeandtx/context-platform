{{ config(materialized='table') }}

/*
  dim_team_country
  Correspondance équipe ↔ pays selon deux stratégies en cascade :
    1. Jointure structurelle sur dim_teams.team_country = dim_countries.iso2 (prioritaire)
    2. Repli textuel : team_name ILIKE '%country_name%' (filet de sécurité)
  Les équipes sans correspondance conservent country_name = NULL, iso2 = NULL (LEFT JOIN).
*/

with teams as (
    select
        team_id,
        team_name,
        team_country   -- code pays issu de la source brute (ex. code ISO2 ou valeur vide)
    from {{ ref('dim_teams') }}
),

countries as (
    select
        country_name,
        iso2
    from {{ ref('dim_countries') }}
),

-- Stratégie 1 : jointure directe sur le code ISO2 structuré
iso2_matched as (
    select
        t.team_id,
        t.team_name,
        c.country_name,
        c.iso2,
        'iso2' as match_method
    from teams t
    inner join countries c
        on t.team_country = c.iso2
        and t.team_country is not null
        and t.team_country != ''
),

-- Équipes non résolues par la stratégie ISO2
unmatched as (
    select t.*
    from teams t
    left join iso2_matched m on t.team_id = m.team_id
    where m.team_id is null
),

-- Stratégie 2 : repli textuel (insensible à la casse)
-- Si plusieurs pays correspondent au nom d'une équipe, on garde le nom de pays le plus long
-- (correspondance la plus spécifique), afin de préserver le grain team_id → 1 pays
text_matched_raw as (
    select
        u.team_id,
        u.team_name,
        c.country_name,
        c.iso2,
        'text'                                         as match_method,
        row_number() over (
            partition by u.team_id
            order by length(c.country_name) desc       -- pays le plus spécifique en premier
        )                                              as rn
    from unmatched u
    left join countries c
        on lower(u.team_name) like '%' || lower(c.country_name) || '%'
),

text_matched as (
    select
        team_id,
        team_name,
        -- si aucun pays n'a été trouvé, country_name et iso2 restent NULL
        country_name,
        iso2,
        case when country_name is null then null else match_method end as match_method
    from text_matched_raw
    where rn = 1
),

-- Union des deux stratégies
combined as (
    select team_id, team_name, country_name, iso2, match_method
    from iso2_matched

    union all

    select team_id, team_name, country_name, iso2, match_method
    from text_matched
)

select
    team_id,
    team_name,
    country_name,
    iso2,
    match_method
from combined
