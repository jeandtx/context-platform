---
name: Context Platform dbt POC
description: Project details for the ECL/Context Platform POC being evaluated for broader adoption or pitch
type: project
---

A dbt POC ("dbt_poc") on DuckDB demonstrating an "atomic context bubbles" concept where every dbt model has a paired `.context.md` file documenting business context for AI agents.

**Stack**: dbt + DuckDB + Evidence.dev  
**Domain**: Sports match data (StatsBomb open data) + World Bank population data  
**Architecture**: raw → staging → marts (dims + facts + kpi)  
**Key innovation claim**: `.context.md` files at each model as "Late Binding" context for AI agents, paired with dbt schema.yml tests as "Early Binding"

**Why:** POC being evaluated for potential broader adoption or pitch by Ippon consulting.  
**How to apply:** When reviewing further work on this project, evaluate against the structural flaws identified in the initial critique — particularly: (1) the KPI is mathematically broken due to the population table not being year-filtered, (2) the tests are currently failing in production, (3) the AI agent integration is purely theoretical with no actual implementation, (4) the Evidence.dev dashboard still shows default template content unrelated to the project data.
