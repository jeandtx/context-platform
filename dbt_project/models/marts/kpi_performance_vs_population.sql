{{ config(materialized='table') }}

{%- set model_name = 'kpi_performance_vs_population' -%}

-- KPI: kpi_performance_vs_population
-- Purpose: Calculate performance ratio (wins / population) for equity comparison across countries
-- Grain: One row per country
-- Materialization: Table
-- Note: Joins fact_country_performance with dim_population for most recent year (2023)
--       Bug fixes: 
--         #1 - Filter dim_population to year 2023 to avoid cartesian product (66 years × countries)
--         #4 - Guard division by zero with population_value > 0

select
    f.country_name,
    f.wins,
    p.population_value,
    cast(f.wins as FLOAT) / cast(p.population_value as FLOAT) as performance_ratio
from {{ ref('fact_country_performance') }} f
inner join {{ ref('dim_population') }} p
    on f.country_name = p.country_name
    and p.year = 2023  -- Known bug fix #1: filter to most recent complete year
where p.population_value is not null
    and p.population_value > 0  -- Known bug fix #4: prevent division by zero
