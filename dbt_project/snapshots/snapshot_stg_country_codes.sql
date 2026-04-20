{% snapshot snapshot_stg_country_codes %}
{{
    config(
        target_schema='snapshots',
        unique_key='code',
        strategy='check',
        check_cols='all',
        invalidate_hard_deletes=True,
    )
}}
SELECT * FROM {{ ref('stg_country_codes') }}
{% endsnapshot %}
