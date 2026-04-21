-- stg_country_codes
-- Staging model: reference table of world countries with ISO codes.
-- Source: raw_country_codes (read_parquet on data/country_codes.parquet)
-- Grain: one row per country (no deduplication applied — source is assumed clean)

select
    "Name" as country_name,
    "Code" as code
from {{ ref('raw_country_codes') }}
