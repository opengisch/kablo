from django import forms
from django.contrib import admin

from ..core.forms import MapWidgetFor3Dgeom
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


class SectionAdminForm(forms.ModelForm):
    class Meta:
        model = Section
        widgets = {
            "geom": MapWidgetFor3Dgeom(),
        }
        readonly_fields = ["geom"]
        fields = "__all__"


class SectionInline(admin.TabularInline):
    form = SectionAdminForm
    model = Section
    readonly_fields = ["geom"]
    extra = 0


class SectionAdmin(admin.ModelAdmin):
    form = SectionAdminForm


class StationAdminForm(forms.ModelForm):
    class Meta:
        model = Station
        widgets = {
            "geom": MapWidgetFor3Dgeom(),
        }
        readonly_fields = ["geom"]
        fields = "__all__"


class StationAdmin(admin.ModelAdmin):
    form = StationAdminForm


class NetworkNodeAdminForm(forms.ModelForm):
    class Meta:
        model = NetworkNode
        widgets = {
            "geom": MapWidgetFor3Dgeom(),
        }
        readonly_fields = ["geom"]
        fields = "__all__"


class NetworkNodeAdmin(admin.ModelAdmin):
    form = NetworkNodeAdminForm


class TrackAdminForm(forms.ModelForm):
    class Meta:
        model = Track
        widgets = {
            "geom": MapWidgetFor3Dgeom(),
        }
        readonly_fields = ["geom"]
        fields = "__all__"


class TrackAdmin(admin.ModelAdmin):
    form = TrackAdminForm
    inlines = [SectionInline]


class CableInline(admin.TabularInline):
    model = Tube.cables.through
    extra = 0


class TubeInline(admin.TabularInline):
    model = Tube.sections.through
    extra = 0
    inlines = [CableInline]


class TubeAdminForm(forms.ModelForm):
    class Meta:
        model = Tube
        widgets = {
            "geom": MapWidgetFor3Dgeom(),
        }
        readonly_fields = ["geom"]
        fields = "__all__"


class TubeAdmin(admin.ModelAdmin):
    form = TubeAdminForm
    model = Tube
    inlines = [CableInline, TubeInline]
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


class CableAdminForm(forms.ModelForm):
    class Meta:
        model = Cable
        widgets = {
            "geom": MapWidgetFor3Dgeom(),
        }
        # FIXME: make mwidget effetively readonly
        readonly_fields = ["geom"]
        fields = "__all__"


class CableAdmin(admin.ModelAdmin):
    form = CableAdminForm
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
admin.site.register(NetworkNode, NetworkNodeAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Switch)
admin.site.register(Terminal)
admin.site.register(Track, TrackAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Tube, TubeAdmin)
admin.site.register(StatusType)
admin.site.register(TubeCableProtectionType)
admin.site.register(CableTensionType)
