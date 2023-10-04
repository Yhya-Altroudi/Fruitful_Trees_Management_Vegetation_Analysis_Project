"""Farms app urls."""

from django.urls import URLPattern, path
from django.views.generic.base import TemplateView
from .views import FarmAPIView, FarmAPIDetail, TreeAPIView, FarmView, DetectTreeAPIView

app_name = "farms"
urlpatterns: list[URLPattern] = [
    path("", FarmView.as_view(), name=FarmView.name),
    path("api/", FarmAPIView.as_view(), name=FarmAPIView.name),
    path("api/<int:pk>/", FarmAPIDetail.as_view(), name=FarmAPIDetail.name),
    path("api/<int:pk>/trees/", TreeAPIView.as_view(), name=TreeAPIView.name),
    path(
        "api/trees/detect",
        DetectTreeAPIView.as_view(),
        name=DetectTreeAPIView.name,
    ),
]
