from django.contrib import admin

from .models import Cable, NetworkNode, NetworkSegment, Station, Track, Tube

admin.site.register(NetworkNode)
admin.site.register(NetworkSegment)
admin.site.register(Track)
admin.site.register(Tube)
admin.site.register(Station)
admin.site.register(Cable)
