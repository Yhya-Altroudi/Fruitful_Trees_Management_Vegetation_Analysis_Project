"""Farms Filters."""
# from rest_framework_gis.filterset import GeoFilterSet

# # from rest_framework_gis.filters import GeometryFilter
# from django_filters import rest_framework as filters

# # from django_filters import rest_framework as filters
# from .models import Farm
# from django.contrib.gis.db.models.functions import Area, GeoFunc
# from django.contrib.gis.db.models import F, PolygonField, Sum
# from django.contrib.gis.geos import Polygon


# class FarmFilter(GeoFilterSet):
#     """Farm Filter."""

#     def filter_area(self, *args, **kwargs):
#         """Area Filter."""
#         # print("Hi", *args, kwargs)
#         # polygon.transform(3857, clone=True).area
#         print(args[1])

#         class Transform(GeoFunc):
#             function = "ST_Transform"

#         print(
#             Farm.objects.alias(
#                 transform=Transform(F("polygon"), 3857, output_field=PolygonField())
#             )
#             .alias(area=Area(Polygon(F("transform"))))
#             .filter(area=args[1])
#             .all()
#         )
#         return Farm.objects.all()

#     # polygon = filters.GeometryFilter(field_name="polygon", lookup_expr="intersects")
#     min_area = filters.NumberFilter(method=filter_area)
#     # density = filters.NumberFilter(field_name="density", lookup_expr="range")
#     trees_type = filters.MultipleChoiceFilter(
#         field_name="trees_type", choices=Farm.TREES_TYPE
#     )

#     class Meta:
#         """Farm Filter Meta."""

#         model = Farm
#         fields = (
#             "trees_type",
#             "date",
#             "min_area",
#             # "density",
#         )

#         # fields: dict[str, list[str]] = {
#         #     "trees_type": ["in"],
#         #     "date": ["exact"],
#         #     "area": ["range"],
#         #     "density": ["range"],
#         #     # "polygon": ["intersects"],
#         # }

import django_property_filter as filters

from farms.models import Farm


class FarmFilter(filters.PropertyFilterSet):
    """Farm Filter."""

    ordering = filters.PropertyOrderingFilter(fields=("area", "density", "population"))

    class Meta:
        """Farm Filter Meta."""

        model = Farm
        fields = ("ordering", "date")
        exclude = ("name", "created_date", "polygon")
        property_fields = [
            ("area", filters.PropertyNumberFilter, ["lt", "gt"]),
            ("density", filters.PropertyNumberFilter, ["lt", "gt"]),
            ("population", filters.PropertyNumberFilter, ["lt", "gt"]),
            ("trees_type", filters.BaseInFilter, ["in"]),
        ]
