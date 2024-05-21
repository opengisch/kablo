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


class _Pos(NamedTuple):
    x: int
    z: int


class _Cable(NamedTuple):
    id: str
    identifier: str
    pos: _Pos


class _Tube(NamedTuple):
    id: str
    diameter: int
    pos: _Pos
    offset_x: int
    offset_x_2: int
    offset_z: int
    offset_z_2: int
    cables: list[_Cable]


def section_profile(request, section_id, distance: int = 0, _format="json"):

    section = get_object_or_404(Section, id=section_id)
    qs = section.tubesection_set.all()

    x_min = None
    x_max = None
    z_min = None
    z_max = None

    _tubes: list[_Tube] = []

    for tube_section in qs:

        tube_pos_x = (
            tube_section.offset_x + (tube_section.offset_x_2 or tube_section.offset_x)
        ) / 2
        tube_pos_z = (
            tube_section.offset_z + (tube_section.offset_z_2 or tube_section.offset_z)
        ) / 2

        _diameter = tube_section.tube.diameter or 100

        cables_data = []
        _cables: list[_Cable] = []
        cable_tube_qs = tube_section.tube.cabletube_set.all()
        for cable_tube in cable_tube_qs:
            cables_data.append((str(cable_tube.cable.id), cable_tube.cable.identifier))

        # display the cables in a grid within the tube
        n_cables = len(cables_data)
        if n_cables > 0:
            # we prefer more cols than rows (cols is max rows+1)
            cols = math.ceil(math.sqrt(n_cables))
            rows = math.ceil(n_cables / cols)
            # potentially, if we have more cols than rows, we could have a rectangle grid instead of a squared one
            grid_max_size = _diameter * math.sqrt(2) / 2
            cell_max_size = grid_max_size / cols
            start_x = tube_pos_x - grid_max_size / 2
            start_z = tube_pos_z + grid_max_size / 2
            for i, cable in enumerate(cables_data):
                row = math.floor(i / cols)
                col = i - row * cols
                cable_pos_x = start_x + (col + 0.5) * cell_max_size
                cable_pos_z = start_z - (row + 0.5) * cell_max_size
                _cable = _Cable(
                    id=cable[0], identifier=cable[1], pos=_Pos(cable_pos_x, cable_pos_z)
                )
                _cables.append(_cable)

        _tube = _Tube(
            id=tube_section.tube.id,
            diameter=_diameter,
            pos=_Pos(
                x=tube_pos_x,
                z=tube_pos_z,
            ),
            offset_x=tube_section.offset_x,
            offset_x_2=tube_section.offset_x,
            offset_z=tube_section.offset_z,
            offset_z_2=tube_section.offset_z_2,
            cables=_cables,
        )
        _tubes.append(_tube)

        x_min = _min(
            x_min,
            tube_section.offset_x,
            tube_section.offset_x_2,
            _diameter,
        )
        x_max = _max(
            x_max,
            tube_section.offset_x,
            tube_section.offset_x_2,
            _diameter,
        )
        z_min = _min(
            z_min,
            tube_section.offset_z,
            tube_section.offset_z_2,
            _diameter,
        )
        z_max = _max(
            z_max,
            tube_section.offset_z,
            tube_section.offset_z_2,
            _diameter,
        )

    if _format == "json":
        return JsonResponse({"section": section_id, "tubes": json.dumps(_tubes)})

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

        tubes_x = []
        tubes_y = []
        tubes_customdata = []
        tubes_size = []
        for _tube in _tubes:
            tubes_x.append(_tube.pos.x)
            tubes_y.append(_tube.pos.z)
            tubes_customdata.append(
                [f"<b>{_tube.id}</b><br>Diameter: {_tube.diameter}"]
            )
            tubes_size.append(_tube.diameter / 2)
        fig.add_trace(
            go.Scatter(
                x=tubes_x,
                y=tubes_y,
                marker=dict(color="aquamarine", size=tubes_size),
                mode="markers",
                customdata=tubes_customdata,
                hovertemplate="<b>%{customdata[0]}</b><br>",
            )
        )

        for _tube in _tubes:
            cables_x = []
            cables_y = []
            cables_customdata = []
            for _cable in _tube.cables:
                cables_x.append(_cable.pos.x)
                cables_y.append(_cable.pos.z)
                cables_customdata.append([f"<b>{_cable.identifier or _cable.id}</b>"])

            fig.add_trace(
                go.Scatter(
                    x=cables_x,
                    y=cables_y,
                    marker=dict(color="red", size=8),
                    mode="markers",
                    customdata=cables_customdata,
                    hovertemplate="<b>%{customdata[0]}</b><br>",
                )
            )

        fig.update_yaxes(
            scaleanchor="x",
            scaleratio=1,
        )

        profile = fig.to_html()
        context = {"profile": profile}
        return render(request, "profile.html", context)
