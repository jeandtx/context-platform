-- Raw model: Load events from parquet
-- Source: dbt_project/data/events.parquet

select * from read_parquet('data/events.parquet')  -- noqa: AM04
