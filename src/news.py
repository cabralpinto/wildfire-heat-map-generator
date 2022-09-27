import re

import pandas as pd
import requests
from tqdm import tqdm

news = pd.read_excel(
    "data/ref_fire_face_v3_102019.xlsx",
    sheet_name="referencia",
    names=["", "text", "", "", "", "", "label", "id"],
    usecols=["text", "label", "id"],
).drop_duplicates()
fires = pd.read_excel(
    "data/ref_fire_face_v3_102019.xlsx",
    sheet_name="id_evento",
    names=["id", "fire"],
    usecols=["id", "fire"]
)
regex = re.compile(r" ?(?:Incêndio|florestal|urbano|automóvel|em|na|/|\d+) ?")
for i, fire in enumerate(tqdm(fires["fire"])):
    geocode = regex.sub("", fire)
    location = requests.get(
        "https://nominatim.openstreetmap.org/search",
        {"q": geocode, "addressdetails": 1, "format": "json", "limit": 1},
    ).json()
    if not location:
        continue
    address: dict = location[0]["address"]
    fires.loc[i, address.keys()] = address.values()
merged = news.join(fires.set_index("id"), on="id").drop(columns=["id", "fire"])
merged.to_excel("data/news.xlsx", index=False)
