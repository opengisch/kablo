import json
import math
from typing import NamedTuple

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

    class _Pos(NamedTuple):
        x: int
        z: int

    class _Cable(NamedTuple):
        id: str
        identifier: str

    class _Tube(NamedTuple):
        id: str
        diameter: int
        pos: _Pos
        offset_x: int
        offset_x_2: int
        offset_z: int
        offset_z_2: int
        cables: list[_Cable]

    for tube_section in qs:

        cables = []
        cable_tube_qs = tube_section.tube.cabletube_set.all()
        for cable_tube in cable_tube_qs:
            cables.append(
                _Cable(id=cable_tube.cable.id, identifier=cable_tube.cable.identifier)
            )

        tube = _Tube(
            id=tube_section.tube.id,
            diameter=tube_section.tube.diameter,
            pos=_Pos(
                x=(
                    tube_section.offset_x
                    + (tube_section.offset_x_2 or tube_section.offset_x)
                )
                / 2,
                z=(
                    tube_section.offset_z
                    + (tube_section.offset_z_2 or tube_section.offset_z)
                )
                / 2,
            ),
            offset_x=tube_section.offset_x,
            offset_x_2=tube_section.offset_x,
            offset_z=tube_section.offset_z,
            offset_z_2=tube_section.offset_z_2,
            cables=cables,
        )
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

    if _format == "json":
        return JsonResponse({"section": section_id, "tubes": json.dumps(tubes)})

    else:
        fig = go.Figure()

        fig.update_layout(
            plot_bgcolor="white",
            showlegend=False,
            autosize=True,
            width=600,
            height=600,
        )

        fig.update_xaxes(
            range=[x_min, x_max],
            showgrid=False,
        )
        fig.update_yaxes(
            range=[z_min, z_max],
            showgrid=False,
        )

        for tube in tubes:
            fig.add_shape(
                type="circle",
                xref="x",
                yref="y",
                x0=tube.pos.x - tube.diameter / 2,
                x1=tube.pos.x + tube.diameter / 2,
                y0=tube.pos.z - tube.diameter / 2,
                y1=tube.pos.z + tube.diameter / 2,
                line_color="Grey",
            )

            # display the cables in a grid within the tube
            n_cables = len(tube.cables)
            if n_cables > 0:
                # we prefer more cols than rows (cols is max rows+1)
                cols = math.ceil(math.sqrt(n_cables))
                rows = math.ceil(n_cables / cols)
                # potentially, if we have more cols than rows, we could have a rectangle grid instead of a squared one
                grid_max_size = tube.diameter * math.sqrt(2) / 2
                cell_max_size = grid_max_size / cols

                start_x = tube.pos.x - grid_max_size / 2
                start_z = tube.pos.z + grid_max_size / 2

                cables_x = []
                cables_z = []
                cable_texts = []
                for i, cable in enumerate(tube.cables):
                    row = math.floor(i / cols)
                    col = i - row * cols
                    cables_x.append(start_x + (col + 0.5) * cell_max_size)
                    cables_z.append(start_z - (row + 0.5) * cell_max_size)
                    cable_texts.append(str(i))

                fig.add_trace(
                    go.Scatter(
                        x=cables_x,
                        y=cables_z,
                        marker=dict(color="red", size=8),
                        mode="markers",
                        text=cable_texts,
                        textposition="bottom center",
                    )
                )

        fig.update_yaxes(
            scaleanchor="x",
            scaleratio=1,
        )

        profile = fig.to_html()
        context = {"profile": profile}
        return render(request, "profile.html", context)
