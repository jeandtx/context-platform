{%- set model_name = 'stg_events' -%}

-- Staging: stg_events
-- Purpose: Passthrough of raw event/team data
-- Grain: One row per unique event within a match
-- Note: No transformations applied at this stage

select *
from {{ ref('raw_events') }}
