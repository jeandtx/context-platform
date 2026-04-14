-- Seed data: Raw customer data
-- This model creates the base data that other models will reference

select 
    1 as id, 'Alice Johnson' as name, 'alice@example.com' as email, '2024-01-15'::date as created_at, 1200.50 as amount
union all
select 2, 'Bob Smith', 'bob@example.com', '2024-01-20'::date, 950.75
union all
select 3, 'Charlie Brown', 'charlie@example.com', '2024-02-01'::date, 2150.00
union all
select 4, 'Diana Prince', 'diana@example.com', '2024-02-10'::date, 1875.25
union all
select 5, 'Eve Wilson', 'eve@example.com', '2024-02-15'::date, 500.00
union all
select 6, 'Frank Miller', 'frank@example.com', '2024-03-01'::date, 3200.50
union all
select 7, 'Grace Lee', 'grace@example.com', '2024-03-05'::date, 1100.00
union all
select 8, 'Henry Davis', 'henry@example.com', '2024-03-10'::date, 2500.75
