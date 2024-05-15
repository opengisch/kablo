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


def import_arcsde_linestrings_to_geos(geometry, output_type="MultiLineString"):
    geom = None
    try:
        # TODO: handle deagregation from multiline to line
        if geometry["type"] == "MultiLineString" and output_type == "MultiLineString":
            coordinates = []
            for part in geometry["coordinates"]:
                parts = []
                for vertex in part:
                    parts.append(vertex.append(999))
                coordinates.append(parts)
            geom = MultiLineString(coordinates)

        elif geometry["type"] == "LineString":
            coordinates = []
            for vertex in geometry["coordinates"]:
                vertex.append(999)
                coordinates.append(vertex)
            if output_type == "MultiLineString":
                geom = MultiLineString(LineString(coordinates))
            else:
                geom = LineString(coordinates)
    except:
        # TODO: report broken geometries
        pass
    return geom
