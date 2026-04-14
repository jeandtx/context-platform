-- models/silver/silver_countries.sql

select
    Name as country_name,
    Code as iso2
from {{ ref('stg_country_codes') }}