{% snapshot snapshot_dim_team_country %}
{{
    config(
        target_schema='snapshots',
        unique_key=['team_name', 'country_name'],
        strategy='check',
        check_cols='all',
        invalidate_hard_deletes=True,
    )
}}
SELECT * FROM {{ ref('dim_team_country') }}
{% endsnapshot %}
