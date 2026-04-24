-- models/silver/silver_countries.sql

select
  name as country_name,
  code as iso2
from {{ ref('stg_country_codes') }}
