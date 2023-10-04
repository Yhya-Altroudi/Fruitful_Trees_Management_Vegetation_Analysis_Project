"""Farms Loading Script."""
import csv  # https://docs.python.org/3/library/csv.html
from datetime import datetime
import json

# https://django-extensions.readthedocs.io/en/latest/runscript.html

# python manage.py runscript load --script-args date(YYYY-MM)

from farms.models import Farm, Tree

from django.contrib.gis.geos import GEOSGeometry, Polygon, Point


def run(*args) -> None:
    """
    Farm load script run to load farms and trees to database as csv.

    loading from two files farms/farms.csv, farms/trees.csv
    Type, Polygon, Circles(Center, Radius)
    str, iterable[iterable[]], iterable[iterable[], iterable[]]
    """
    with open("farms/Samples.csv") as file:
        reader = csv.reader(file)
        Farm.objects.all().delete()
        Tree.objects.all().delete()
        i = 0
        for trees_type, polygon, circles in reader:
            print(i)
            i += 1
            polygon = [(lng, lat) for lat, lng in json.loads(polygon)]
            polygon.append(polygon[0])
            farm: Farm = Farm.objects.create(
                polygon=Polygon(polygon),
                date=datetime.strptime("2019-4", "%Y-%m").date(),
                trees_type=trees_type,
            )

            for center, radius in json.loads(
                circles.replace("(", "[").replace(")", "]")
            ):
                tree: Tree = Tree.objects.create(
                    center=Point(center[::-1]), radius=radius / 5, farm=farm
                )
