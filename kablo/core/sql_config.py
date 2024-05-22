from migrate_sql.config import SQLItem

sql_items = [
    SQLItem(
        "project_z_on_line",
        r"""
        CREATE OR REPLACE FUNCTION project_z_on_line(line_2d geometry, line_z geometry)
           RETURNS geometry
           LANGUAGE plpgsql
          AS
        $$
        declare
           geom geometry;
        begin
            SELECT ST_MakeLine(points.geom) INTO geom from (
                SELECT ST_SetSRID(
                    ST_MakePoint(
                        ST_X((points_2d.dp).geom),
                        ST_Y((points_2d.dp).geom),
                        ST_Z((points_z.dp).geom)
                    ),
                    ST_Srid(line_2d)
                ) as geom
                FROM (
                    SELECT ST_DumpPoints(line_z) AS dp) points_z
                    INNER JOIN (SELECT ST_DumpPoints(line_2d) AS dp) points_2d
                        ON (points_z.dp).path = (points_2d.dp).path
                    ORDER BY (points_z.dp).path
                ) points;
           return geom;
        end;
        $$;
        """,
        r"""
            DROP FUNCTION project_z_on_line(line_2d geometry, line_z geometry);
        """,
    ),
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
