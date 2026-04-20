{% snapshot snapshot_kpi_performance_vs_population %}
{{
    config(
        target_schema='snapshots',
        unique_key='snapshot_key',
        strategy='check',
        check_cols=['wins', 'population_value', 'performance_ratio'],
        invalidate_hard_deletes=True,
    )
}}
-- No natural unique key: kpi model joins fact (by country) x population (by country+year+indicator).
-- snapshot_key = hash of (country_name, wins, population_value) to create a stable row identity.
SELECT
    md5(
        coalesce(country_name, '') || '|' ||
        coalesce(cast(wins as bigint)::varchar, '') || '|' ||
        coalesce(cast(population_value as bigint)::varchar, '')
    ) AS snapshot_key,
    *
FROM {{ ref('kpi_performance_vs_population') }}
{% endsnapshot %}
