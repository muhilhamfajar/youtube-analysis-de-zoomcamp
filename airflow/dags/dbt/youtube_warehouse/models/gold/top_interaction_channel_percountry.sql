{{ config(materialized='table') }}

WITH ranked_channels AS (
    SELECT
        v.channel_title,
        v.country,
        SUM(v.views) AS total_views,
        SUM(v.likes) AS total_likes,
        SUM(v.comment_count) AS total_comments,
        ROW_NUMBER() OVER (PARTITION BY v.country ORDER BY (SUM(v.views) + SUM(v.likes) + SUM(v.comment_count)) DESC) AS channel_rank
    FROM
        {{ ref('fact_videos') }} AS v
    GROUP BY
        v.channel_title,
        v.country
)
SELECT
    channel_title,
    country,
    total_views,
    total_likes,
    total_comments,
    (total_views + total_likes + total_comments) AS total_interaction
FROM
    ranked_channels
WHERE
    channel_rank <= 10