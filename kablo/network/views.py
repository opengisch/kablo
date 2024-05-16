import plotly.graph_objects as go
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from kablo.network.models import Section


def _min(current, offset, offset_optional, diameter):
    offset_min = min(offset, offset_optional or offset)
    if not current:
        return offset_min - diameter / 2
    return min(current, offset_min - diameter / 2)


def _max(current, offset, offset_optional, diameter):
    offset_max = max(offset, offset_optional or offset)
    if not current:
        return offset_max + diameter / 2
    return max(current, offset_max + diameter / 2)


def section_profile(request, section_id, distance: int = 0, _format="json"):

    section = get_object_or_404(Section, id=section_id)

    qs = section.tubesection_set.all()

    tubes = []

    x_min = None
    x_max = None
    z_min = None
    z_max = None

    for tube_section in qs:

        cables = []
        cable_tube_qs = tube_section.tube.cabletube_set.all()
        for cable_tube in cable_tube_qs:
            cables.append(
                {
                    "id": cable_tube.cable.id,
                    "identifier": cable_tube.cable.identifier,
                }
            )

        tube = {
            "id": tube_section.tube.id,
            "diameter": tube_section.tube.diameter,
            "pos": {
                "x": (
                    tube_section.offset_x
                    + (tube_section.offset_x_2 or tube_section.offset_x)
                )
                / 2,
                "z": (
                    tube_section.offset_z
                    + (tube_section.offset_z_2 or tube_section.offset_z)
                )
                / 2,
            },
            "offset_x": tube_section.offset_x,
            "offset_x_2": tube_section.offset_x,
            "offset_z": tube_section.offset_z,
            "offset_z_2": tube_section.offset_z_2,
            "cables": cables,
        }
        tubes.append(tube)

        x_min = _min(
            x_min,
            tube_section.offset_x,
            tube_section.offset_x_2,
            tube_section.tube.diameter,
        )
        x_max = _max(
            x_max,
            tube_section.offset_x,
            tube_section.offset_x_2,
            tube_section.tube.diameter,
        )
        z_min = _min(
            z_min,
            tube_section.offset_z,
            tube_section.offset_z_2,
            tube_section.tube.diameter,
        )
        z_max = _max(
            z_max,
            tube_section.offset_z,
            tube_section.offset_z_2,
            tube_section.tube.diameter,
        )

    if format == "json":
        return JsonResponse({"section": section_id, "tubes": tubes})

    else:
        fig = go.Figure()

        fig.update_xaxes(range=[x_min, x_max], zeroline=False)
        fig.update_yaxes(range=[z_min, z_max])

        for tube in tubes:
            fig.add_shape(
                type="circle",
                xref="x",
                yref="y",
                x0=tube["pos"]["x"] - tube["diameter"] / 2,
                x1=tube["pos"]["x"] + tube["diameter"] / 2,
                y0=tube["pos"]["z"] - tube["diameter"] / 2,
                y1=tube["pos"]["z"] + tube["diameter"] / 2,
                line_color="Grey",
            )

        fig.update_yaxes(
            scaleanchor="x",
            scaleratio=1,
        )

        profile = fig.to_html()
        context = {"profile": profile}
        return render(request, "profile.html", context)
