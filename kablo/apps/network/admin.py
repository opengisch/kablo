from django.contrib import admin

from .models import (
    Cable,
    NetworkNode,
    Station,
    Switch,
    Terminal,
    Track,
    TrackSection,
    TrackTrackSection,
    Tube,
)

admin.site.register(NetworkNode)
admin.site.register(TrackSection)
admin.site.register(Track)
admin.site.register(TrackTrackSection)
admin.site.register(Tube)
admin.site.register(Station)
admin.site.register(Cable)
admin.site.register(Switch)
admin.site.register(Terminal)
