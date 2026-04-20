{% snapshot snapshot_dim_population %}
{{
    config(
        target_schema='snapshots',
        unique_key=['country_code', 'indicator_code', 'year'],
        strategy='check',
        check_cols='all',
        invalidate_hard_deletes=True,
    )
}}
SELECT * FROM {{ ref('dim_population') }}
{% endsnapshot %}
