---
title: Rapport Sportif — Context Platform
---

# 🏆 Rapport Sportif

Bienvenue sur le rapport de données sportives du projet **Context Platform**.
Ce tableau de bord analyse les performances des équipes nationales à travers les matchs internationaux.

## Navigation

- [📊 Performances par pays](/performances) — KPIs et ratio performance/population
- [⚽ Matchs](/matchs) — Résultats et scores détaillés
- [🌍 Équipes & Pays](/equipes) — Référentiel des équipes et pays

## Vue d'ensemble

```sql total_matches
SELECT COUNT(*) as nb_matchs FROM sports_db.dim_matches
```

```sql total_teams
SELECT COUNT(*) as nb_equipes FROM sports_db.dim_teams
```

```sql total_countries
SELECT COUNT(*) as nb_pays FROM sports_db.dim_countries
```

<BigValue data={total_matches} value=nb_matchs title="Total Matchs" />
<BigValue data={total_teams} value=nb_equipes title="Équipes" />
<BigValue data={total_countries} value=nb_pays title="Pays" />
