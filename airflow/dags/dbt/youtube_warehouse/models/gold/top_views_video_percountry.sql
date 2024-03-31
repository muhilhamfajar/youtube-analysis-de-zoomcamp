{{ config(materialized='table') }}

WITH ranked_videos AS (
    SELECT
        v.title,
        v.channel_title as channel,
        v.country,
        SUM(v.views) as total_views,
        SUM(v.likes) as total_likes,
        SUM(v.dislikes) as total_dislikes,
        SUM(v.comment_count) as total_comments,
        ROW_NUMBER() OVER (PARTITION BY v.country ORDER BY (SUM(v.views)) DESC) AS video_rank
    FROM
        {{ ref('fact_videos') }} AS v
    GROUP BY
        v.title,
        v.channel_title,
        v.country
)

SELECT
    title,
    channel,
    country,
    total_views,
    total_likes,
    total_dislikes,
    total_comments
FROM
    ranked_videos
WHERE
    video_rank <= 10