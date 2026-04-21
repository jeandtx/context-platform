{{ config(materialized='table') }}

-- dim_countries
-- Reference dimension table of world countries with ISO 2-letter codes.
-- Source: stg_country_codes
-- Grain: one row per unique country

select
    country_name,
    -- stg_country_codes exposes the ISO code as "code"; renaming to iso2 per context spec
    code as iso2
from {{ ref('stg_country_codes') }}
