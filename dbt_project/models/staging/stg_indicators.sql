{%- set model_name = 'stg_indicators' -%}

-- Staging: stg_indicators
-- Purpose: Passthrough of World Bank indicators in wide format (one column per year)
-- Grain: One row per country/indicator combination
-- Note: No transformations applied at this stage. Filtering to SP.POP.TOTL happens downstream in dim_population

select *
from {{ ref('raw_indicators') }}
