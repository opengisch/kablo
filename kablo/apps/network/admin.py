from django.contrib import admin

from .models import Cable, NetworkSegment, Station, Trasse, Tube

admin.site.register(NetworkSegment)
admin.site.register(Trasse)
admin.site.register(Tube)
admin.site.register(Station)
admin.site.register(Cable)
