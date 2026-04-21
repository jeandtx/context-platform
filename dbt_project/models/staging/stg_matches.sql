{%- set model_name = 'stg_matches' -%}

-- Staging: stg_matches
-- Purpose: Passthrough of raw match data
-- Grain: One row per unique match
-- Note: No transformations applied at this stage

select *
from {{ ref('raw_matches') }}
