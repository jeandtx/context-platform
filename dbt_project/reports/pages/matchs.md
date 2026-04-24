---
title: Résultats des Matchs
---

# ⚽ Résultats des Matchs

## Tous les Matchs

```sql all_matches
SELECT
    match_date,
    home_team,
    away_team,
    home_score,
    away_score,
    winner
FROM sports_db.dim_matches
ORDER BY match_date DESC
```

<DataTable data={all_matches} />

## Statistiques par Équipe

```sql team_stats
SELECT
    home_team as equipe,
    COUNT(*) as matchs_joues,
    SUM(CASE WHEN winner = home_team THEN 1 ELSE 0 END) as victoires,
    ROUND(100.0 * SUM(CASE WHEN winner = home_team THEN 1 ELSE 0 END) / COUNT(*), 1) as taux_victoire_pct
FROM sports_db.dim_matches
GROUP BY home_team
UNION ALL
SELECT
    away_team as equipe,
    COUNT(*) as matchs_joues,
    SUM(CASE WHEN winner = away_team THEN 1 ELSE 0 END) as victoires,
    ROUND(100.0 * SUM(CASE WHEN winner = away_team THEN 1 ELSE 0 END) / COUNT(*), 1) as taux_victoire_pct
FROM sports_db.dim_matches
GROUP BY away_team
ORDER BY victoires DESC
```

<DataTable data={team_stats} />

<BarChart
    data={team_stats}
    x=equipe
    y=victoires
    title="Victoires par Équipe"
    xAxisTitle="Équipe"
    yAxisTitle="Victoires"
/>
