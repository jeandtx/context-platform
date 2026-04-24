---
title: Performances par Pays
---

# 📊 Performances par Pays

## KPI : Performance vs Population

```sql kpi_perf
SELECT
    country_name,
    wins,
    population_value,
    ROUND(performance_ratio * 1000000, 4) as ratio_par_million_hab
FROM sports_db.kpi_performance_vs_population
ORDER BY performance_ratio DESC
```

<DataTable data={kpi_perf} />

<BarChart
    data={kpi_perf}
    x=country_name
    y=ratio_par_million_hab
    title="Ratio Performance / Million d'habitants"
    xAxisTitle="Pays"
    yAxisTitle="Ratio"
/>

## Matchs joués et Victoires

```sql fact_perf
SELECT
    country_name,
    matches_played,
    wins,
    ROUND(100.0 * wins / matches_played, 1) as win_rate_pct
FROM sports_db.fact_country_performance
ORDER BY wins DESC
```

<DataTable data={fact_perf} />

<BarChart
    data={fact_perf}
    x=country_name
    y=wins
    title="Victoires par Pays"
    xAxisTitle="Pays"
    yAxisTitle="Victoires"
/>
