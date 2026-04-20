{% snapshot snapshot_dim_teams %}
{{
    config(
        target_schema='snapshots',
        unique_key='team_id',
        strategy='check',
        check_cols='all',
        invalidate_hard_deletes=True,
    )
}}
SELECT * FROM {{ ref('dim_teams') }}
{% endsnapshot %}
