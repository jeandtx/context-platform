{{ config(materialized='table') }}

-- Pivot from wide format (one column per year) to long format (one row per country/year).
-- Bug fix: filter to indicator_code = 'SP.POP.TOTL' to exclude other World Bank indicators
-- (e.g. birth rate, GDP) that exist in the same source table.
-- Note: the 2025 column arrives as VARCHAR in the source; all year columns are cast to VARCHAR
-- before UNPIVOT so DuckDB can handle the mixed types uniformly.
-- Rows with NULL population (years with no data) are excluded per business rule.

with wide as (
    select
        "Country Name"             as country_name,
        "Country Code"             as country_code,
        "Indicator Name"           as indicator_name,
        "Indicator Code"           as indicator_code,
        -- Cast every year column to VARCHAR for uniform UNPIVOT (2025 arrives as VARCHAR in source)
        try_cast("1960" as varchar) as "1960", try_cast("1961" as varchar) as "1961",
        try_cast("1962" as varchar) as "1962", try_cast("1963" as varchar) as "1963",
        try_cast("1964" as varchar) as "1964", try_cast("1965" as varchar) as "1965",
        try_cast("1966" as varchar) as "1966", try_cast("1967" as varchar) as "1967",
        try_cast("1968" as varchar) as "1968", try_cast("1969" as varchar) as "1969",
        try_cast("1970" as varchar) as "1970", try_cast("1971" as varchar) as "1971",
        try_cast("1972" as varchar) as "1972", try_cast("1973" as varchar) as "1973",
        try_cast("1974" as varchar) as "1974", try_cast("1975" as varchar) as "1975",
        try_cast("1976" as varchar) as "1976", try_cast("1977" as varchar) as "1977",
        try_cast("1978" as varchar) as "1978", try_cast("1979" as varchar) as "1979",
        try_cast("1980" as varchar) as "1980", try_cast("1981" as varchar) as "1981",
        try_cast("1982" as varchar) as "1982", try_cast("1983" as varchar) as "1983",
        try_cast("1984" as varchar) as "1984", try_cast("1985" as varchar) as "1985",
        try_cast("1986" as varchar) as "1986", try_cast("1987" as varchar) as "1987",
        try_cast("1988" as varchar) as "1988", try_cast("1989" as varchar) as "1989",
        try_cast("1990" as varchar) as "1990", try_cast("1991" as varchar) as "1991",
        try_cast("1992" as varchar) as "1992", try_cast("1993" as varchar) as "1993",
        try_cast("1994" as varchar) as "1994", try_cast("1995" as varchar) as "1995",
        try_cast("1996" as varchar) as "1996", try_cast("1997" as varchar) as "1997",
        try_cast("1998" as varchar) as "1998", try_cast("1999" as varchar) as "1999",
        try_cast("2000" as varchar) as "2000", try_cast("2001" as varchar) as "2001",
        try_cast("2002" as varchar) as "2002", try_cast("2003" as varchar) as "2003",
        try_cast("2004" as varchar) as "2004", try_cast("2005" as varchar) as "2005",
        try_cast("2006" as varchar) as "2006", try_cast("2007" as varchar) as "2007",
        try_cast("2008" as varchar) as "2008", try_cast("2009" as varchar) as "2009",
        try_cast("2010" as varchar) as "2010", try_cast("2011" as varchar) as "2011",
        try_cast("2012" as varchar) as "2012", try_cast("2013" as varchar) as "2013",
        try_cast("2014" as varchar) as "2014", try_cast("2015" as varchar) as "2015",
        try_cast("2016" as varchar) as "2016", try_cast("2017" as varchar) as "2017",
        try_cast("2018" as varchar) as "2018", try_cast("2019" as varchar) as "2019",
        try_cast("2020" as varchar) as "2020", try_cast("2021" as varchar) as "2021",
        try_cast("2022" as varchar) as "2022", try_cast("2023" as varchar) as "2023",
        try_cast("2024" as varchar) as "2024", try_cast("2025" as varchar) as "2025"
    from {{ ref('stg_indicators') }}
    -- Bug fix: restrict to total population indicator only
    where "Indicator Code" = 'SP.POP.TOTL'
),

unpivoted as (
    unpivot wide
    on "1960", "1961", "1962", "1963", "1964", "1965", "1966", "1967", "1968", "1969",
       "1970", "1971", "1972", "1973", "1974", "1975", "1976", "1977", "1978", "1979",
       "1980", "1981", "1982", "1983", "1984", "1985", "1986", "1987", "1988", "1989",
       "1990", "1991", "1992", "1993", "1994", "1995", "1996", "1997", "1998", "1999",
       "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009",
       "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019",
       "2020", "2021", "2022", "2023", "2024", "2025"
    into
        name  year_str
        value population_raw
)

select
    country_name,
    country_code,
    indicator_name,
    indicator_code,
    try_cast(year_str     as integer) as year,
    try_cast(population_raw as bigint) as population_value
from unpivoted
-- Exclude years with no available population data
where try_cast(population_raw as bigint) is not null
