"""Farms Models."""
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Area, GeoFunc
from django.contrib.gis.geos import Point
import csv

from django.forms import ValidationError


# Create your models here.
class Farm(models.Model):
    """Farm model."""

    name = models.CharField("Farm Name", max_length=20,
                            help_text="farm name", blank=True)  # type: ignore
    polygon = models.PolygonField(
        "Farm borders as a polygon", null=False, blank=False, geography=True
    )
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False)

    TREES_TYPE: list[tuple[str, str]] = [
        (row[0], row[1]) for row in csv.reader(open("Types of Fruit Trees.csv", "r"))
    ]
    TREES_TYPE.pop(0)
    trees_type = models.CharField(
        "Farm trees type", choices=TREES_TYPE, max_length=20)

    date = models.DateField("Farm Date", null=False, blank=False)
    created_date = models.DateTimeField("Created Date", auto_now_add=True)

    @property
    def year_month(self) -> str:
        """Farm date (YYYY-MM)."""
        return self.date.strftime("%Y-%m")

    @property
    def area(self) -> float:
        """Trees Count."""
        return self.polygon.transform(3857, clone=True).area * 0.67

    @property
    def trees_count(self) -> int:
        """Trees Count."""
        return Tree.objects.filter(farm=self).count()

    @property
    def population(self):
        """Farm population.

        trees count over the area of the farm.
        averge trees count in 1 meter squared.
        """
        return self.trees_count / self.area

    @property
    def density(self):
        """Farm density.

        to sum the areas of all trees on the farm and divide by the area of the farm.
        """

        class Buffer(GeoFunc):
            function = "ST_Buffer"

        area__sum = (
            Tree.objects.filter(farm=self)
            .annotate(
                area=Area(
                    Buffer(
                        models.F("center"),
                        models.F("radius"),
                        output_field=models.PointField(),
                    )
                )
            )
            .aggregate(models.Sum("area"))["area__sum"]
        )

        return (area__sum.sq_m / self.area) if area__sum else 0

    def clean(self) -> None:  # noqa: D102
        super().clean()
        if (
            self.__class__.objects.filter(
                date=self.date, polygon__intersects=self.polygon
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("Farms cannot intersect.")

    def save(self, *args, **kwargs) -> None:  # noqa: D102
        if self.name is None or self.name == "":
            self.name: str = "Farm" + str(self.year_month) + self.trees_type
        self.date.replace(day=1)
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Farm Name."""
        return self.name


class Tree(models.Model):
    """Tree model."""

    # table for species
    center = models.PointField(null=False, blank=False)
    radius = models.FloatField(default=1, null=False, blank=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)

    @property
    def area(self) -> float:
        """Area of the tree crown."""
        return self.center.buffer(self.radius).area

    def clean(self) -> None:  # noqa: D102
        super().clean()
        if not self.center.intersects(self.farm.polygon):
            raise ValidationError("Tree is outside Farm.")

    def __str__(self) -> str:
        """Tree Type."""
        return "tree-" + str(self.pk) + "-" + str(self.farm)
