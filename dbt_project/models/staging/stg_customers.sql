-- Staging model: Load raw customer data
{{ config(materialized='view') }}

select
    id,
    name,
    email,
    created_at,
    amount as order_amount
from {{ ref('raw_customers') }}
