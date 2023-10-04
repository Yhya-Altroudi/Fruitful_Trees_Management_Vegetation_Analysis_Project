"""Farms Admin."""
from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin
from .models import Farm, Tree


# Register your models here.
admin.site.register(Farm, LeafletGeoAdmin)
admin.site.register(Tree, LeafletGeoAdmin)

# admin.site.register(Farm, admin.GISModelAdmin)
# admin.site.register(Tree, admin.GISModelAdmin)

# class CustomGISModelAdmin(admin.GISModelAdmin):
#     """Custom GIS Model Admin."""

#     gis_widget_kwargs = {
#         "attrs": {
#             "default_lon": 37.980672,
#             "default_lat": 34.988515,
#             "default_zoom": 6,
#             "map_width": 600,
#             "map_height": 400,
#         },
#     }


# @admin.register(Farm)
# class FarmAdmin(CustomGISModelAdmin):
#     """Farm Admin."""

#     pass
