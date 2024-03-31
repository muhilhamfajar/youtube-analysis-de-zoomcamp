{{ config(materialized='table') }}

SELECT
    v.country,
    dc.title,
    COUNT(*) as total
FROM
    {{ ref('fact_videos') }} AS v
JOIN
    {{ ref('dim_category') }} AS dc ON v.category_id = dc.category_id
GROUP BY
    v.country,
    dc.title