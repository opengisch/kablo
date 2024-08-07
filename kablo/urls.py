"""
URL configuration for kablo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django_oapif.urls import oapif_router

from kablo.core import views as core_views
from kablo.network import urls as network_urls
from kablo.webviewer import views as webviewer_views

urlpatterns = [
    path("", core_views.home, name="home"),
    path("demo-qgis-project", core_views.demo_qgis_project, name="demo_qgis_project"),
    path("viewer", webviewer_views.viewer, name="viewer"),
    path("admin/", admin.site.urls, {"extra_context": {"DEBUG": settings.DEBUG}}),
    path("network/", include(network_urls)),
    path("oapif/", include(oapif_router.urls)),
    path("users/", include("allauth.urls")),
]

if settings.DEBUG:
    urlpatterns = [path("__debug__/", include("debug_toolbar.urls"))] + urlpatterns
