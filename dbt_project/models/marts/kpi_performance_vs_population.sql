-- models/gold/kpi_performance_vs_population.sql

select
    f.country_name,
    f.wins,
    p.population_value,
    f.wins / p.population_value as performance_ratio
from {{ ref('fact_country_performance') }} f
join {{ ref('dim_population') }} p
    on f.country_name = p.country_name