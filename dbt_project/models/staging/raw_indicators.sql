-- Raw model: Load indicators from parquet
-- Source: dbt_project/data/indicators.parquet

select * from read_parquet('data/indicators.parquet')
