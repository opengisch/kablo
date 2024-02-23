from django.contrib import admin

from .models import (
    Cable,
    NetworkNode,
    Station,
    Switch,
    Terminal,
    Track,
    TrackSection,
    Tube,
)

admin.site.register(NetworkNode)
admin.site.register(Track)
admin.site.register(Station)
admin.site.register(Cable)
admin.site.register(Switch)
admin.site.register(Terminal)


# Basic demo showing cascaded relationships: track sections => tubes => cables
class CableInline(admin.TabularInline):
    model = Cable.tubes.through


class TubeAdmin(admin.ModelAdmin):
    model = Tube
    inlines = [
        CableInline,
    ]


class TubeInline(admin.TabularInline):
    model = Tube.track_sections.through
    inlines = [
        CableInline,
    ]


class TrackSectionAdmin(admin.ModelAdmin):
    model = Track
    inlines = [
        TubeInline,
    ]


admin.site.register(Tube, TubeAdmin)
admin.site.register(TrackSection, TrackSectionAdmin)
