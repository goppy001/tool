WITH
data_2017_1 AS (
  SELECT
   "id"
   ,SUM(CASE WHEN TRUNC(DATE_TRUNC('month',"add_ymd")) IN ('2017/01/01') THEN 1 ELSE 0 END) as medias_q
   ,'2017_1' as extract_ymd
 FROM
  "kaiinn_data"
 WHERE 
  TRUNC(DATE_TRUNC('month',"add_ymd")) IN ('2017/01/01')
 GROUP BY
  id,TRUNC(DATE_TRUNC('month',"add_ymd"))
  )
,data_2017_2 AS (
  SELECT
   "id"
   ,SUM(CASE WHEN TRUNC(DATE_TRUNC('month',"add_ymd")) IN ('2017/02/01') THEN 1 ELSE 0 END) as medias_q
   ,'2017_2' as extract_ymd
 FROM
  "kaiinn_data"
 WHERE 
  TRUNC(DATE_TRUNC('month',"add_ymd")) IN ('2017/02/01')
 GROUP BY
  id,TRUNC(DATE_TRUNC('month',"add_ymd"))
  )
,data_2017_3 AS (
  SELECT
   "id"
   ,SUM(CASE WHEN TRUNC(DATE_TRUNC('month',"add_ymd")) IN ('2017/03/01') THEN 1 ELSE 0 END) as medias_q
   ,'2017_3' as extract_ymd
 FROM
  "kaiinn_data"
 WHERE 
  TRUNC(DATE_TRUNC('month',"add_ymd")) IN ('2017/03/01')
 GROUP BY
  id,TRUNC(DATE_TRUNC('month',"add_ymd"))
  )
,data_2017_4 AS (
  SELECT
   "id"
   ,SUM(CASE WHEN TRUNC(DATE_TRUNC('month',"add_ymd")) IN ('2017/04/01') THEN 1 ELSE 0 END) as medias_q
   ,'2017_4' as extract_ymd
 FROM
  "kaiinn_data"
 WHERE 
  TRUNC(DATE_TRUNC('month',"add_ymd")) IN ('2017/04/01')
 GROUP BY
  id,TRUNC(DATE_TRUNC('month',"add_ymd"))
  )
,data_2017_q1 AS (
select 
"id"
,extract_ymd
,sum(medias_q) as medias
,row_number() over (order by aa.extract_ymd) as row
FROM
 (
SELECT 
 *
FROM data_2017_1
union all
SELECT 
 *
FROM data_2017_2
union all
SELECT 
 *
FROM data_2017_3
) aa
GROUP BY
aa.id
,aa.extract_ymd
)
,devision_2017_q1 AS (
SELECT
"id"
,extract_ymd
,medias
,row
,medias - avg(sum(medias)) over (partition by id) as devision_medias
,row - avg(sum(row)) over (partition by id) as devision_month
FROM
  data_2017_q1
group by
 id,
 extract_ymd,
 medias,
 row
)
,slope_2017_q1 AS (
SELECT
  "id"
  ,extract_ymd
  ,row
  ,medias
  ,avg(devision_medias*devision_month) over (partition by id) / nullif(var_pop(row) over (partition by id),0)  as slope
FROM
  devision_2017_q1
GROUP by
  "id"
  ,extract_ymd
  ,devision_medias
  ,devision_month
  ,row
  ,medias
)
, data_2017_q2 AS (
select 
"id"
,extract_ymd
,sum(medias_q) as medias
,row_number() over (order by aa.extract_ymd) as row
FROM
 (
SELECT 
 *
FROM data_2017_4
union all
SELECT 
 *
FROM data_2017_5
union all
SELECT 
 *
FROM data_2017_6
) aa
GROUP BY
aa.id
,aa.extract_ymd
)
,devision_2017_q2 AS (
SELECT
"id"
,extract_ymd
,medias
,row
,medias - avg(sum(medias)) over (partition by id) as devision_medias
,row - avg(sum(row)) over (partition by id) as devision_month
FROM
  data_2017_q2
group by
 id,
 extract_ymd,
 medias,
 row
)
,slope_2017_q2 AS (
SELECT
  "id"
  ,extract_ymd
  ,row
  ,medias
  ,avg(devision_medias*devision_month) over (partition by id) / nullif(var_pop(row) over (partition by id),0)  as slope
FROM
  devision_2017_q2
GROUP by
  "id"
  ,extract_ymd
  ,devision_medias
  ,devision_month
  ,row
  ,medias
)
SELECT
  "id"
  ,extract_ymd
  ,medias
  ,slope
FROM
  (
  SELECT
    *
  FROM slope_2017_q1
  union all
  SELECT
    *
  FROM slope_2017_q2
  union all
  SELECT
    *
  FROM slope_2017_q3
) aaa
WHERE
  slope < 0
GROUP BY
  "id"
  ,extract_ymd
  ,medias
  ,slope
ORDER BY
  "id"
  ,extract_ymd asc
;
