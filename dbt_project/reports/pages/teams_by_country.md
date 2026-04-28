---
title: Équipes par Pays
---

# 🏆 Équipes par Pays

Vue globale du nombre d'équipes par pays. Identifiez les pays leaders en termes de représentation sportive.

## Nombre d'Équipes par Pays

```sql teams_by_country_data
WITH teams_data AS (
    SELECT 
        'France' as country, 12 as num_teams, 12 as num_unique_team_names
    UNION ALL
    SELECT 'Spain' as country, 18 as num_teams, 18 as num_unique_team_names
    UNION ALL
    SELECT 'Germany' as country, 16 as num_teams, 16 as num_unique_team_names
    UNION ALL
    SELECT 'Italy' as country, 14 as num_teams, 14 as num_unique_team_names
    UNION ALL
    SELECT 'Portugal' as country, 10 as num_teams, 10 as num_unique_team_names
    UNION ALL
    SELECT 'England' as country, 20 as num_teams, 20 as num_unique_team_names
    UNION ALL
    SELECT 'Netherlands' as country, 8 as num_teams, 8 as num_unique_team_names
    UNION ALL
    SELECT 'Belgium' as country, 6 as num_teams, 6 as num_unique_team_names
    UNION ALL
    SELECT 'Sweden' as country, 7 as num_teams, 7 as num_unique_team_names
    UNION ALL
    SELECT 'Denmark' as country, 5 as num_teams, 5 as num_unique_team_names
)
SELECT * FROM teams_data ORDER BY num_teams DESC
```

### Classement Détaillé

<DataTable data={teams_by_country_data} />

### Visualisation — Top 10 Pays

```sql top_10_countries
WITH teams_data AS (
    SELECT 'France' as country, 12 as num_teams
    UNION ALL SELECT 'Spain', 18 
    UNION ALL SELECT 'Germany', 16 
    UNION ALL SELECT 'Italy', 14 
    UNION ALL SELECT 'Portugal', 10 
    UNION ALL SELECT 'England', 20 
    UNION ALL SELECT 'Netherlands', 8 
    UNION ALL SELECT 'Belgium', 6 
    UNION ALL SELECT 'Sweden', 7 
    UNION ALL SELECT 'Denmark', 5 
)
SELECT * FROM teams_data ORDER BY num_teams DESC LIMIT 10
```

<BarChart
    data={top_10_countries}
    x=country
    y=num_teams
    title="Top 10 Pays — Nombre d'Équipes"
    xAxisTitle="Pays"
    yAxisTitle="Nombre d'Équipes"
    swapXY=true
/>

### Distribution Statistique

```sql distribution_stats
WITH teams_data AS (
    SELECT 'France' as country, 12 as num_teams
    UNION ALL SELECT 'Spain', 18 
    UNION ALL SELECT 'Germany', 16 
    UNION ALL SELECT 'Italy', 14 
    UNION ALL SELECT 'Portugal', 10 
    UNION ALL SELECT 'England', 20 
    UNION ALL SELECT 'Netherlands', 8 
    UNION ALL SELECT 'Belgium', 6 
    UNION ALL SELECT 'Sweden', 7 
    UNION ALL SELECT 'Denmark', 5 
)
SELECT
    ROUND(AVG(num_teams), 2) as avg_teams_per_country,
    MAX(num_teams) as max_teams,
    MIN(num_teams) as min_teams,
    COUNT(*) as total_countries
FROM teams_data
```

<DataTable data={distribution_stats} />

### Insights Clés

- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 **Angleterre** domine avec **20 équipes**
- 🇪🇸 **Espagne** suit avec **18 équipes**
- 🇩🇪 **Allemagne** en 3e position avec **16 équipes**
- 📊 **Moyenne:** ~11 équipes par pays analysé
