from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from kablo.network.models import Section


def section_profile(request, section_id, distance: int = 0):

    section = get_object_or_404(Section, id=section_id)

    qs = section.tubesection_set.all()

    tubes = []

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
                "x": tube_section.offset_x,
                "z": tube_section.offset_z,
            },
            "cables": cables,
        }
        tubes.append(tube)

    return JsonResponse({"section": section_id, "tubes": tubes})
