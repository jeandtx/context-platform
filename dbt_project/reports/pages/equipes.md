---
title: Équipes & Pays
---

# 🌍 Équipes & Pays

## Référentiel des Équipes

```sql all_teams
SELECT
    t.team_name,
    c.country_name,
    t.team_gender
FROM sports_db.dim_teams t
LEFT JOIN sports_db.dim_countries c ON t.team_country = c.iso2
ORDER BY c.country_name, t.team_name
```

<DataTable data={all_teams} />

## Référentiel des Pays

```sql all_countries
SELECT
    country_name,
    iso2 as country_code
FROM sports_db.dim_countries
ORDER BY country_name
```

<DataTable data={all_countries} />

## Distribution des Équipes par Genre

```sql teams_by_gender
SELECT
    team_gender,
    COUNT(DISTINCT team_name) as nombre_equipes
FROM sports_db.dim_teams
GROUP BY team_gender
ORDER BY nombre_equipes DESC
```

<DataTable data={teams_by_gender} />

<BarChart
    data={teams_by_gender}
    x=team_gender
    y=nombre_equipes
    title="Équipes par Genre"
    xAxisTitle="Genre"
    yAxisTitle="Nombre d'Équipes"
/>

## Pays & Leurs Équipes

```sql countries_teams
SELECT
    c.country_name,
    COUNT(t.team_name) as nombre_equipes
FROM sports_db.dim_teams t
LEFT JOIN sports_db.dim_countries c ON t.team_country = c.iso2
GROUP BY c.country_name
ORDER BY nombre_equipes DESC
```

<DataTable data={countries_teams} />
