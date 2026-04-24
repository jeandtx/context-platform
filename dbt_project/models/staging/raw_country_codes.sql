-- Raw model: Load country codes from parquet
-- Source: dbt_project/data/country_codes.parquet

select * from read_parquet('data/country_codes.parquet')  -- noqa: AM04
