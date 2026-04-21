{%- set model_name = 'stg_country_codes' -%}

-- Staging: stg_country_codes
-- Purpose: Rename country reference fields (Name → country_name, Code → code)
-- Grain: One row per country

select
    "Name" as country_name,
    "Code" as code
from {{ ref('raw_country_codes') }}
