from django.urls import path

from . import views

urlpatterns = [
    path("profile/<slug:_format>/<slug:section_id>/", views.section_profile),
    path(
        "profile/<slug:_format>/<slug:section_id>/<int:distance>/",
        views.section_profile,
    ),
]
