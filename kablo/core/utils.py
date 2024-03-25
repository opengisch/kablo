def wkt_from_line(line: list[tuple[float, float]]) -> str:
    geom_line_wkt = ", ".join([f"{x} {y}" for (x, y) in line])
    return f"LINESTRING ({geom_line_wkt})"


def wkt_from_multiline(line: list[tuple[float, float]]) -> str:
    geom_line_wkt = ", ".join([f"{x} {y}" for (x, y) in line])
    return f"MULTILINESTRING (({geom_line_wkt}))"
