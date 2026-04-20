{% snapshot snapshot_dim_countries %}
{{
    config(
        target_schema='snapshots',
        unique_key='iso2',
        strategy='check',
        check_cols='all',
        invalidate_hard_deletes=True,
    )
}}
SELECT * FROM {{ ref('dim_countries') }}
{% endsnapshot %}
