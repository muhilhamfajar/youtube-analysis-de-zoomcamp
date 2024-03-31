{{ config(materialized='table') }}

SELECT 
  ANY_VALUE(rc.id) AS category_id,
  rc.snippet_title AS title
  FROM {{ source('youtube_warehouse', 'raw_category') }} rc
GROUP BY 
  snippet_title
