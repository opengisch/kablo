from migrate_sql.config import SQLItem

sql_items = [
    SQLItem(
        "azimuth_along_line",
        r"""
        CREATE OR REPLACE FUNCTION azimuth_along_line(geom geometry)
           RETURNS integer[]
           LANGUAGE plpgsql
          AS
        $$
        declare
           azimuts integer[];
        begin
            SELECT ARRAY(
                SELECT
                    CASE
                     WHEN angle_post IS NULL THEN DEGREES(angle_ante)
                     WHEN angle_ante IS NULL THEN DEGREES(angle_post)
                     ELSE DEGREES(ATAN2(
                       (SIN(angle_ante)+SIN(angle_post))/2,
                       (COS(angle_ante)+COS(angle_post))/2
                       ))
                    END AS azm
                    FROM (
                        SELECT
                            ST_Azimuth(LAG(dmp.geom) OVER (ORDER BY dmp.path), dmp.geom) AS angle_ante,
                            ST_Azimuth(dmp.geom, LEAD(dmp.geom) OVER (ORDER BY dmp.path)) AS angle_post
                            FROM ST_DumpPoints(geom) AS dmp
                    ) azm_ante_post
                ) INTO azimuts;
           return azimuts;
        end;
        $$;
        """,
        r"""
            DROP FUNCTION azimuth_along_line(geom geometry);
        """,
    ),
]
