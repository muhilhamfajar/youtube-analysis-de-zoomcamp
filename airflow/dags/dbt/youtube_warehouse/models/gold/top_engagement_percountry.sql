{{ config(materialized='table') }}

SELECT
    v.trending_date,
    v.country,
    SUM(v.views) AS total_views,
    SUM(v.likes) AS total_likes,
    SUM(v.comment_count) AS total_comments,
    ROW_NUMBER() OVER (PARTITION BY v.country ORDER BY (SUM(v.views) + SUM(v.likes) + SUM(v.comment_count)) DESC) AS engagement_rank
FROM
    {{ ref('fact_videos') }} AS v
GROUP BY
    v.country,
    v.trending_date