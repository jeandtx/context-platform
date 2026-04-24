-- Staging model: Clean and transform country codes data
{{ config(materialized='view') }}

select
  name,
  code
from {{ ref('raw_country_codes') }}
