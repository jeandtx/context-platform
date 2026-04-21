{{ config(materialized='table') }}

/*
  KPI: performance sportive rapportée à la taille de la population.
  Grain : une ligne par pays unique.

  Bug fixes applied:
  - dim_population has one row per country per year (1960-2025).
    Without a year filter the join creates ~66 rows per country (cartesian product).
    Fix: filter to p.year = 2023 (most recent complete year with reliable World Bank data).
  - Guard against division by zero: p.population_value > 0.
*/

with performance as (
    select
        country_name,
        wins
    from {{ ref('fact_country_performance') }}
),

population as (
    select
        country_name,
        population_value
    from {{ ref('dim_population') }}
    -- using 2023 as most recent complete year for World Bank population data
    where year = 2023
      and population_value is not null
      and population_value > 0
)

select
    p.country_name,
    f.wins,
    p.population_value,
    -- ratio = victoires / population; very small number (e.g. 3e-7 for large countries)
    f.wins::double / p.population_value::double as performance_ratio
from performance f
inner join population p
    on f.country_name = p.country_name
