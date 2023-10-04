from django.urls import path, include
from .views import NDVI_View, BAI_View, Change_Det_View, Time_Series_view, test
from django.views.generic import TemplateView

app_name = 'changedet'

urlpatterns = [

    #  path("", TemplateView.as_view(
    #      template_name="changeDet/main.html"), name="main_list"),
    path("NDVI/", NDVI_View.as_view(), name="NDVI_view"),
    path('BAI/', BAI_View.as_view(), name='BAI_view'),
    path("Change_detection_ser/", Change_Det_View.as_view(), name="ChangeDet_view"),
    path("Time_Series_ser/", Time_Series_view.as_view(), name="TimeSeries_view"),
    # path("test/", test, name="testing_url"),
]
