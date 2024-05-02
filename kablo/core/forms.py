from django.contrib.gis.forms import OpenLayersWidget


class MapWidgetFor3Dgeom(OpenLayersWidget):
    supports_3d = True
    template_name = "gis/openlayers.html"
