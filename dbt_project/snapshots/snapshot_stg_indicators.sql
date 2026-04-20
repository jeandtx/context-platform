{% snapshot snapshot_stg_indicators %}
{{
    config(
        target_schema='snapshots',
        unique_key='snapshot_key',
        strategy='check',
        check_cols='all',
        invalidate_hard_deletes=True,
    )
}}
SELECT
    md5("Country Code" || '|' || "Indicator Code") AS snapshot_key,
    *
FROM {{ ref('stg_indicators') }}
{% endsnapshot %}
