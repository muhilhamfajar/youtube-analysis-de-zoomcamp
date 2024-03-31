{{ 
    config(
        materialized='table',
        partition_by={
            "field": "trending_date",
            "data_type": "date",
            "granularity": "day"
        },
        cluster_by=['country']
    ) 
}}

SELECT
    v.video_id,
    PARSE_DATE('%y.%d.%m', v.trending_date) AS trending_date,
    v.title,
    v.channel_title,
    dc.category_id,
    v.publish_time,
    v.views,
    v.likes,
    v.dislikes,
    v.comment_count,
    v.thumbnail_link,
    v.comments_disabled,
    v.ratings_disabled,
    v.video_error_or_removed,
    v.country
FROM
    {{ source('youtube_warehouse', 'raw_videos') }} AS v
JOIN
    {{ source('youtube_warehouse', 'raw_category') }} AS rc ON v.category_id = rc.id
JOIN
    {{ ref('dim_category') }} AS dc ON rc.snippet_title = dc.title