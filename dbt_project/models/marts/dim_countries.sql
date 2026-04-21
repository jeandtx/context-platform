{{ config(materialized='table') }}

{%- set model_name = 'dim_countries' -%}

-- Dimension: dim_countries
-- Purpose: Official reference table for countries
-- Grain: One row per unique country
-- Materialization: Table

select
    "Name" as country_name,
    "Code" as iso2
from {{ ref('raw_country_codes') }}
