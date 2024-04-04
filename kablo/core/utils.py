from django.contrib.gis.geos import LineString, MultiLineString


def wkt_from_line(line: list[tuple[float, float]]) -> str:
    geom_line_wkt = ", ".join([f"{x} {y}" for (x, y) in line])
    return f"LINESTRING ({geom_line_wkt})"


def wkt_from_multiline(line: list[tuple[float, float]]) -> str:
    geom_line_wkt = ", ".join([f"{x} {y}" for (x, y) in line])
    return f"MULTILINESTRING (({geom_line_wkt}))"


def import_arcsde_linestrings_to_geos(geometry):
    geom = None
    try:
        if geometry["type"] == "MultiLineString":
            geom = MultiLineString(geometry["coordinates"])
        elif geometry["type"] == "LineString":
            geom = MultiLineString(LineString(geometry["coordinates"]))
    except:
        # TODO: report broken geometries
        pass
    return geom
