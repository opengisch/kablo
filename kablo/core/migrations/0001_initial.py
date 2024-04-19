# Generated by Django 5.0.3 on 2024-04-19 12:56

import migrate_sql.operations
from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrate_sql.operations.CreateSQL(
            name="azimuth_along_line",
            sql="\n        CREATE OR REPLACE FUNCTION azimuth_along_line(geom geometry)\n           RETURNS integer[]\n           LANGUAGE plpgsql\n          AS\n        $$\n        declare\n           azimuts integer[];\n        begin\n            SELECT ARRAY(\n                SELECT\n                    CASE\n                     WHEN angle_post IS NULL THEN DEGREES(angle_ante)\n                     WHEN angle_ante IS NULL THEN DEGREES(angle_post)\n                     ELSE DEGREES(ATAN2(\n                       (SIN(angle_ante)+SIN(angle_post))/2,\n                       (COS(angle_ante)+COS(angle_post))/2\n                       ))\n                    END AS azm\n                    FROM (\n                        SELECT\n                            ST_Azimuth(LAG(dmp.geom) OVER (ORDER BY dmp.path), dmp.geom) AS angle_ante,\n                            ST_Azimuth(dmp.geom, LEAD(dmp.geom) OVER (ORDER BY dmp.path)) AS angle_post\n                            FROM ST_DumpPoints(geom) AS dmp\n                    ) azm_ante_post\n                ) INTO azimuts;\n           return azimuts;\n        end;\n        $$;\n        ",
            reverse_sql="\n            DROP FUNCTION azimuth_along_line(geom geometry);\n        ",
        ),
    ]
