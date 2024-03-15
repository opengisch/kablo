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


# Basic demo showing cascaded relationships: track sections => tubes => cables
class CableInline(admin.TabularInline):
    model = Cable.tubes.through


class TubeInline(admin.TabularInline):
    model = Tube.track_sections.through
    inlines = [
        CableInline,
    ]


class TrackSectionInline(admin.TabularInline):
    model = Track.track_sections.through


class TubeAdmin(admin.ModelAdmin):
    model = Tube
    inlines = [
        CableInline,
    ]


class TrackAdmin(admin.ModelAdmin):
    model = Track
    inlines = [
        TrackSectionInline,
    ]


class TrackSectionAdmin(admin.ModelAdmin):
    model = TrackSection
    inlines = [
        TubeInline,
    ]


admin.site.register(Cable)
admin.site.register(NetworkNode)
admin.site.register(Station)
admin.site.register(Switch)
admin.site.register(Terminal)
admin.site.register(Track, TrackAdmin)
admin.site.register(TrackSection, TrackSectionAdmin)
admin.site.register(Tube, TubeAdmin)
