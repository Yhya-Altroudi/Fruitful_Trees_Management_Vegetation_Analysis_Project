"""Farms save script."""
import csv
from farms.models import Farm, Tree

# python manage.py runscript farms_save --script-args farms trees


def run(*args) -> None:
    """
    Farm save script run to save farms and trees from database as csv.

    saving two files farms/farms.csv, farms/trees.csv
    farms = "pk", "name", "polygon", "date", "trees_type"
    trees = "pk", "center", "radius", "farm"
    """
    if not args or "farms" in args:
        with open("farms/farms.csv", mode="w") as file:
            writer = csv.writer(file)
            writer.writerow(["pk", "name", "polygon", "date", "trees_type"])
            for farm in Farm.objects.all():
                writer.writerow(
                    [
                        farm.pk,
                        farm.name,
                        farm.polygon.wkt,
                        farm.date.strftime("%Y-%m"),
                        farm.trees_type,
                    ]
                )

    if not args or "trees" in args:
        with open("farms/trees.csv", mode="w") as file:
            writer = csv.writer(file)
            writer.writerow(["pk", "center", "radius", "farm"])
            for tree in Tree.objects.all():
                writer.writerow([tree.pk, tree.center.wkt, tree.radius, tree.farm.pk])
