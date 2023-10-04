"""Farms Serializers."""
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from farms.models import Farm, Tree
from rest_framework import serializers


class FarmGeoSerializer(GeoFeatureModelSerializer):
    """Farm Serializer."""

    density = serializers.FloatField(read_only=True)
    population = serializers.FloatField(read_only=True)
    area = serializers.FloatField(read_only=True)
    trees_count = serializers.IntegerField(read_only=True)

    # def get_density(self, obj):
    #     return obj.density

    # polygon__area = serializers.Field()

    # def to_representation(self, value):
    #     # return the representation that should be used to serialize the target
    #     return value

    # def get_area(self, obj):
    #     return obj.polygon__area

    class Meta:
        """Meta."""

        model = Farm
        geo_field: str = "polygon"
        fields: str = "__all__"
        read_only_fields: list[str] = ["created_date"]


class TreeGeoSerializer(GeoFeatureModelSerializer):
    """Tree Serializer."""

    area = serializers.FloatField(read_only=True)

    class Meta:
        """Meta."""

        model = Tree
        geo_field: str = "center"
        fields: str = "__all__"
        many = True
