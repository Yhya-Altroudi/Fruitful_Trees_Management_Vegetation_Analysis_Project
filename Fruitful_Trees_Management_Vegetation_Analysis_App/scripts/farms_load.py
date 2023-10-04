"""Farms Loading Script."""
import csv  # https://docs.python.org/3/library/csv.html
from datetime import datetime

# https://django-extensions.readthedocs.io/en/latest/runscript.html

# python manage.py runscript farms_load --script-args farms trees

from farms.models import Farm, Tree
from django.contrib.gis.geos import GEOSGeometry


def run(*args) -> None:
    """
    Farm load script run to load farms and trees to database as csv.

    loading from two files farms/farms.csv, farms/trees.csv
    farms = "pk", "name", "polygon", "date", "trees_type"
    trees = "pk", "center", "radius", "farm"
    """
    if not args or "farms" in args:
        with open("farms/farms.csv") as file:
            reader = csv.reader(file)
            header: list[str] = next(reader)

            Farm.objects.all().delete()

            for row in reader:
                if row == []:
                    continue
                farm: Farm = Farm.objects.create(
                    pk=int(row[0]),
                    name=row[1],
                    polygon=GEOSGeometry(row[2]),
                    date=datetime.strptime(row[3], "%Y-%m").date(),
                    trees_type=row[4],
                )

    if not args or "trees" in args:
        with open("farms/trees.csv") as file:
            reader = csv.reader(file)
            header: list[str] = next(reader)

            Tree.objects.all().delete()

            for row in reader:
                if row == []:
                    continue
                tree: Tree = Tree.objects.create(
                    pk=int(row[0]),
                    center=GEOSGeometry(row[1]),
                    radius=float(row[2]),
                    farm=Farm.objects.get(pk=int(row[3])),
                )
