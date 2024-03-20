from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from .models import Section, Track


@login_required
@cache_page(60 * 15)
def map_view(request):
    tracks = Track.objects.all()
    tracks_geojson = serialize(
        "geojson",
        tracks,
        geometry_field="geom",
        fields=("id", "identifier"),
    )

    sections = Section.objects.all()
    sections_geojson = serialize(
        "geojson",
        sections,
        geometry_field="geom",
        fields=("pk", "order_index"),
    )

    return render(
        request,
        "map.html",
        {
            "tracks_geojson": tracks_geojson,
            "sections_geojson": sections_geojson,
        },
    )
