"""Farms Views."""
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView

from farms.treedetection import detectTrees

from .models import Farm, Tree
from .serializers import FarmGeoSerializer, TreeGeoSerializer
from .filters import FarmFilter

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_gis.filters import InBBoxFilter

from rest_framework.response import Response


# Create your views here.
class FarmAPIView(ListCreateAPIView):
    """Farm API View."""

    serializer_class = FarmGeoSerializer
    queryset = Farm.objects.all()
    name: str = "farm_api"
    # filter_backends = (
    # OrderingFilter,
    # DjangoFilterBackend,
    # )
    filterset_class = FarmFilter
    # filterset_fields = ("trees_type", "date")
    # filterset_fields: dict[str, list[str]] = {
    #     "trees_type": ["in"],
    #     "date": ["exact"],
    #     "area": ["range"],
    #     "density": ["range"],
    # }
    bbox_filter_field: str = "polygon"
    bbox_filter_include_overlapping = True
    filter_backends = [InBBoxFilter, DjangoFilterBackend]

    # ordering_property_field = ("density", "area")
    # ordering = ("area",)


class FarmAPIDetail(RetrieveUpdateDestroyAPIView):
    """Farm Detail."""

    serializer_class = FarmGeoSerializer
    queryset = Farm.objects.all()
    name: str = "farm_detail_api"

    def delete(self, request, *args, **kwargs) -> Response:  # noqa: D102
        # delete all trees of the farm
        Tree.objects.filter(farm=self.kwargs["pk"]).all().delete()
        return super().delete(request, *args, **kwargs)


class TreeAPIView(ListCreateAPIView):
    """Farm API View."""

    serializer_class = TreeGeoSerializer
    name: str = "tree_api"

    def get_queryset(self):
        """Get Farm Trees."""
        return Tree.objects.filter(farm=self.kwargs["pk"]).all()  # type: ignore

    def get_serializer(self, *args, **kwargs):  # noqa: D102
        if "data" in kwargs:
            kwargs["many"] = True if isinstance(
                kwargs["data"], list) else False
        return super().get_serializer(*args, **kwargs)


class DetectTreeAPIView(APIView):
    """API View for detecting trees of farm.

    this view is responsible of detecting trees of the farm.
    farm id is in kwargs pk.
    only post method is acceptable.
    can accept list of tree as geojson for post data that considered as default trees.
    call a script which return detected trees from satellite images.
    """

    name: str = "tree_detect_api"

    def post(self, request) -> Response:  # noqa: D102
        # handle request data
        polygon = request.data["polygon"][0]
        circles = request.data["circles"]
        smoothing = int(request.data.get("smoothing", 7))
        threshold = float(request.data.get("threshold", 0.8))
        
        print(request.data)

        circles = detectTrees(polygon, circles, smoothing, threshold)
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": point},
                    "properties": {"radius": radius},
                }
                for point, radius in circles
            ],
        }
        return Response(geojson)


class FarmView(APIView):
    """
    Farm Main View.

    this view is for the main html page.
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name: str = "farms/farm_list1.html"
    name: str = "farm_view"

    def get(self, request) -> Response:
        """Set The Context for Rendering."""
        serializer = FarmGeoSerializer()
        return Response(
            {
                "serializer": serializer,
                "trees_types": dict(Farm.TREES_TYPE),  # type: ignore
            }
        )
