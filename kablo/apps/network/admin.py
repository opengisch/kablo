from django.contrib import admin

from .models import Cable, NetworkNode, Station, Track, TrackSection, Tube

admin.site.register(NetworkNode)
admin.site.register(TrackSection)
admin.site.register(Track)
admin.site.register(Tube)
admin.site.register(Station)
admin.site.register(Cable)
