import json

import matplotlib.pyplot as plt
import requests
from matplotlib.colors import LinearSegmentedColormap
from shapely.geometry import shape
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon

hits = list(map(len, requests.get("http://localhost:5000/heatmap").json()))
with open("data/districts.geojson") as file:
    country = json.load(file)
colors = LinearSegmentedColormap.from_list("", ["beige", "tomato"])
for feature, number in zip(country["features"], hits):
    region = shape(feature["geometry"])
    color = colors(number / max(hits))
    for geometry in shape(feature["geometry"]).geoms:
        match geometry:
            case Polygon():
                plt.fill(*geometry.exterior.xy, color=color)
            case MultiPolygon():
                for geometry in geometry.geoms:
                    plt.fill(*geometry.exterior.xy, color=color)
plt.show()
