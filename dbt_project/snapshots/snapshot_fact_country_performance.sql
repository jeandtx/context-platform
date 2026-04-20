{% snapshot snapshot_fact_country_performance %}
{{
    config(
        target_schema='snapshots',
        unique_key='country_name',
        strategy='check',
        check_cols='all',
        invalidate_hard_deletes=True,
    )
}}
SELECT * FROM {{ ref('fact_country_performance') }}
{% endsnapshot %}
