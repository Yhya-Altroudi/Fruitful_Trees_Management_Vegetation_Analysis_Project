"""Tree Detection."""
from farms import downloader
import cv2
import numpy as np
import glob
from django.contrib.gis.geos import Polygon


def detectTrees(polygon, circles, smoothing, threshold):
    """Detect Trees."""

    polygon = Polygon(polygon)

    l, b, r, t = polygon.extent
    z = 19

    img, pt = downloader.f(l, t, r, b, z)

    w, h = (pt[1][0] - pt[0][0]), (pt[0][1] - pt[1][1])
    img_w, img_h = (img.shape[1] / w), (img.shape[0] / h)

    def lonlat2pixel(lon, lat):
        x = round((lon - pt[0][0]) * img_w)
        y = round((pt[0][1] - lat) * img_h)
        return x, y

    def pixel2lonlat(x, y):
        lon = x / img_w + pt[0][0]
        lat = -(y / img_h) + pt[0][1]
        return lon, lat

    polygon = [lonlat2pixel(mx, my) for mx, my in polygon.coords[0]]
    circles = [(lonlat2pixel(mx, my), int(r * 5))
               for (mx, my), r in circles]

    min_tree_size = 0.5
    max_tree_size = 1.5

    templates = [
        cv2.imread(file, 0) for file in glob.glob("farms\\Templates\\template*.png")
    ]
    # Data augmentation resizing templates
    templates = [
        cv2.resize(template, None, fx=i, fy=i,
                   interpolation=cv2.INTER_CUBIC)
        for i in np.arange(min_tree_size, max_tree_size + 0.1, 0.1)[::-1]
        for template in templates
    ]


    img_blur = cv2.blur(
        cv2.cvtColor(img, cv2.COLOR_RGB2GRAY), (smoothing, smoothing)
    )
    stencil = np.zeros(img_blur.shape, dtype=img_blur.dtype)
    cv2.fillPoly(stencil, [np.array(polygon)], [255])
    img_blur = cv2.bitwise_and(img_blur, stencil, dst=img_blur)
    mask = np.zeros(img_blur.shape[:2], np.uint8)
    for circle in circles:
        cv2.circle(mask, circle[0], circle[1], (255,), -1)
    for tmp in templates:
        res = cv2.matchTemplate(img_blur, tmp, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        shape = tmp.shape

        for point in zip(*loc):
            center = point[0] + int(round(shape[0] / 2)), point[1] + int(  # type: ignore
                round(shape[1] / 2)
            )
            radius = int((np.sum(shape)) / 4)
            if mask[center] != 255:
                cv2.circle(
                    mask, center[::-
                                 1], int((np.sum(shape) * 1.2) / 4), (255,), -1
                )
                circles.append([center[::-1], radius])  # type: ignore

    # test
    # print(circles)
    # cv2.fillPoly(img, [np.array(polygon)], (0, 255, 0))
    # for circle in circles:
    #     cv2.circle(img, circle[0], circle[1], (255, 0, 0), -1)
    # cv2.imwrite("output2.jpg", img)
    # cv2.imwrite("output3.jpg", mask)

    circles = [(pixel2lonlat(px, py), r / 5) for (px, py), r in circles]
    return circles
