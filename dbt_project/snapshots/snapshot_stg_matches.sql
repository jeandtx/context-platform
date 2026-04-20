{% snapshot snapshot_stg_matches %}
{{
    config(
        target_schema='snapshots',
        unique_key='match_id',
        strategy='check',
        check_cols='all',
        invalidate_hard_deletes=True,
    )
}}
SELECT * FROM {{ ref('stg_matches') }}
{% endsnapshot %}
