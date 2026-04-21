{{ config(materialized='table') }}

{%- set model_name = 'dim_population' -%}

-- Dimension: dim_population
-- Purpose: Annual population by country (1960–2025) for comparisions with sports performance
-- Grain: One row per country + year combination
-- Materialization: Table
-- Note: Pivots from wide format (columns per year) to long format (rows per year)
--       Filters to SP.POP.TOTL indicator only (known bug fix #3)

with indicators_cast as (
    -- Cast all year columns to VARCHAR to ensure consistent types for UNPIVOT
    select
        "Country Name",
        "Country Code",
        "Indicator Name",
        "Indicator Code",
        cast("1960" as VARCHAR) as "1960", cast("1961" as VARCHAR) as "1961", cast("1962" as VARCHAR) as "1962", cast("1963" as VARCHAR) as "1963", cast("1964" as VARCHAR) as "1964", cast("1965" as VARCHAR) as "1965", cast("1966" as VARCHAR) as "1966", cast("1967" as VARCHAR) as "1967", cast("1968" as VARCHAR) as "1968", cast("1969" as VARCHAR) as "1969",
        cast("1970" as VARCHAR) as "1970", cast("1971" as VARCHAR) as "1971", cast("1972" as VARCHAR) as "1972", cast("1973" as VARCHAR) as "1973", cast("1974" as VARCHAR) as "1974", cast("1975" as VARCHAR) as "1975", cast("1976" as VARCHAR) as "1976", cast("1977" as VARCHAR) as "1977", cast("1978" as VARCHAR) as "1978", cast("1979" as VARCHAR) as "1979",
        cast("1980" as VARCHAR) as "1980", cast("1981" as VARCHAR) as "1981", cast("1982" as VARCHAR) as "1982", cast("1983" as VARCHAR) as "1983", cast("1984" as VARCHAR) as "1984", cast("1985" as VARCHAR) as "1985", cast("1986" as VARCHAR) as "1986", cast("1987" as VARCHAR) as "1987", cast("1988" as VARCHAR) as "1988", cast("1989" as VARCHAR) as "1989",
        cast("1990" as VARCHAR) as "1990", cast("1991" as VARCHAR) as "1991", cast("1992" as VARCHAR) as "1992", cast("1993" as VARCHAR) as "1993", cast("1994" as VARCHAR) as "1994", cast("1995" as VARCHAR) as "1995", cast("1996" as VARCHAR) as "1996", cast("1997" as VARCHAR) as "1997", cast("1998" as VARCHAR) as "1998", cast("1999" as VARCHAR) as "1999",
        cast("2000" as VARCHAR) as "2000", cast("2001" as VARCHAR) as "2001", cast("2002" as VARCHAR) as "2002", cast("2003" as VARCHAR) as "2003", cast("2004" as VARCHAR) as "2004", cast("2005" as VARCHAR) as "2005", cast("2006" as VARCHAR) as "2006", cast("2007" as VARCHAR) as "2007", cast("2008" as VARCHAR) as "2008", cast("2009" as VARCHAR) as "2009",
        cast("2010" as VARCHAR) as "2010", cast("2011" as VARCHAR) as "2011", cast("2012" as VARCHAR) as "2012", cast("2013" as VARCHAR) as "2013", cast("2014" as VARCHAR) as "2014", cast("2015" as VARCHAR) as "2015", cast("2016" as VARCHAR) as "2016", cast("2017" as VARCHAR) as "2017", cast("2018" as VARCHAR) as "2018", cast("2019" as VARCHAR) as "2019",
        cast("2020" as VARCHAR) as "2020", cast("2021" as VARCHAR) as "2021", cast("2022" as VARCHAR) as "2022", cast("2023" as VARCHAR) as "2023", cast("2024" as VARCHAR) as "2024", cast("2025" as VARCHAR) as "2025"
    from {{ ref('stg_indicators') }}
    where "Indicator Code" = 'SP.POP.TOTL'  -- Known bug fix: filter to population only
),

indicators_unpivoted as (
    select
        "Country Name" as country_name,
        "Country Code" as country_code,
        "Indicator Name" as indicator_name,
        "Indicator Code" as indicator_code,
        year,
        value as population_value
    from indicators_cast
    unpivot (value for year in (
        '1960', '1961', '1962', '1963', '1964', '1965', '1966', '1967', '1968', '1969',
        '1970', '1971', '1972', '1973', '1974', '1975', '1976', '1977', '1978', '1979',
        '1980', '1981', '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989',
        '1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999',
        '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009',
        '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019',
        '2020', '2021', '2022', '2023', '2024', '2025'
    ))
)

select
    country_name,
    country_code,
    indicator_name,
    indicator_code,
    year::Integer as year,
    try_cast(population_value as BIGINT) as population_value
from indicators_unpivoted
where try_cast(population_value as BIGINT) is not null
    and try_cast(population_value as BIGINT) > 0
order by country_name, year
