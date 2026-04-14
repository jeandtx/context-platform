-- Raw model: Load matches from parquet
-- Source: dbt_project/data/matches.parquet

select * from read_parquet('data/matches.parquet')
