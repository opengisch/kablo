from django.contrib import admin

from .models import Cable, NetworkNode, Section, Station, Switch, Terminal, Track, Tube


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0


class TrackAdmin(admin.ModelAdmin):
    model = Track
    inlines = [SectionInline]


class CableInline(admin.TabularInline):
    model = Cable.tubes.through
    extra = 0


class TubeInline(admin.TabularInline):
    model = Tube.sections.through
    extra = 0
    inlines = [CableInline]


class TubeAdmin(admin.ModelAdmin):
    model = Tube
    inlines = [CableInline]


admin.site.register(Cable)
admin.site.register(NetworkNode)
admin.site.register(Station)
admin.site.register(Switch)
admin.site.register(Terminal)
admin.site.register(Track, TrackAdmin)
admin.site.register(Section)
admin.site.register(Tube, TubeAdmin)
