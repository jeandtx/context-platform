-- models/silver/silver_team_country.sql

select
    t.team_name,
    c.country_name
from {{ ref('dim_teams') }} t
left join {{ ref('dim_countries') }} c
    on t.team_name like '%' || c.country_name || '%'


-- 👉 💥 volontairement bancal