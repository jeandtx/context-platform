-- Fact model: Customer metrics with segmentation
{{ config(materialized='table') }}

select
    id,
    name,
    email,
    created_at,
    order_amount,
    round(order_amount, 2) as order_amount_rounded,
    case 
        when order_amount >= 2000 then 'High Value'
        when order_amount >= 1000 then 'Medium Value'
        else 'Low Value'
    end as customer_segment
from {{ ref('stg_customers') }}
order by order_amount desc
