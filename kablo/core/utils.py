from django.contrib.gis.geos import LineString, MultiLineString


def wkt_from_line(line: list[tuple[float, float]], force3d=True) -> str:
    _3d = " 0" if force3d else ""
    geom_line_wkt = ", ".join([f"{x} {y}{_3d}" for (x, y) in line])
    return f"LINESTRING ({geom_line_wkt})"


def wkt_from_multiline(multiline: list[list[tuple[float, float]]]) -> str:
    line_wkts = []
    for line in multiline:
        line_wkts.append(", ".join([f"{x} {y} 0" for (x, y) in line]))
    line_wkts = ", ".join([f"({line})" for line in line_wkts])
    return f"MULTILINESTRING ({line_wkts})"


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
