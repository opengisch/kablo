from django.contrib import admin

from .models import (
    Cable,
    CableTensionType,
    NetworkNode,
    Section,
    Station,
    StatusType,
    Switch,
    Terminal,
    Track,
    Tube,
    TubeCableProtectionType,
)


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0


class TrackAdmin(admin.ModelAdmin):
    model = Track
    inlines = [SectionInline]


class CableInline(admin.TabularInline):
    model = Tube.cables.through
    extra = 0


class TubeInline(admin.TabularInline):
    model = Tube.sections.through
    extra = 0
    inlines = [CableInline]


class TubeAdmin(admin.ModelAdmin):
    model = Tube
    inlines = [CableInline]
    fields = ["status", "cable_protection_type", "geom"]
    list_display = [
        "id",
        "status",
        "cable_protection_type",
    ]
    list_filter = [
        "status",
        "cable_protection_type",
    ]


class CableTubeInline(admin.TabularInline):
    model = Tube.cables.through
    extra = 0


class CableAdmin(admin.ModelAdmin):
    model = Cable
    search_fields = ("id",)
    exclude = ["tubes"]
    inlines = [CableTubeInline]
    list_display = [
        "id",
        "status",
        "tension",
    ]
    list_filter = [
        "status",
        "tension",
    ]


admin.site.register(Cable, CableAdmin)
admin.site.register(NetworkNode)
admin.site.register(Station)
admin.site.register(Switch)
admin.site.register(Terminal)
admin.site.register(Track, TrackAdmin)
admin.site.register(Section)
admin.site.register(Tube, TubeAdmin)
admin.site.register(StatusType)
admin.site.register(TubeCableProtectionType)
admin.site.register(CableTensionType)
