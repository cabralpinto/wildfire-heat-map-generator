import json
import os
import warnings
from itertools import chain, islice
from operator import attrgetter
from pathlib import Path

import requests
import spacy
from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api, Resource
from shapely.geometry import shape
from shapely.geometry.point import Point
from snscrape.modules.twitter import TwitterSearchScraper
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline


class Classify(Resource):
    classifier = pipeline(
        "text-classification",
        model=AutoModelForSequenceClassification.from_pretrained("./models/bert"),
        tokenizer=AutoTokenizer.from_pretrained(
            "neuralmind/bert-large-portuguese-cased",
            do_lower_case=False,
        ),
    )

    @classmethod
    def classify(cls, text) -> dict[str, str]:
        predictions = cls.classifier(text)[0]
        return {
            "fire": predictions["label"] == "LABEL_1",
            "confidence": predictions["score"]
        }

    def post(self) -> dict[str, str]:
        return self.classify(request.json["text"])


class Geoparse(Resource):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ner = spacy.load("pt_core_news_lg")

    @classmethod
    def geoparse(cls, text) -> dict[str, str]:
        geocode = ", ".join(str(ne) for ne in cls.ner(text).ents if ne.label_ == "LOC")
        if not geocode:
            return {"error": "Unable to extract geocode."}
        location = requests.get(
            "https://nominatim.openstreetmap.org/search",
            {
                "q": geocode,
                "addressdetails": 1,
                "format": "json",
                "polygon_geojson": 1,
                "limit": 1
            },
        ).json()
        if not location:
            return {"error": "Unable to find location."}
        return {"address": location[0]["address"], "geometry": location[0]["geojson"]}

    def post(self) -> tuple[dict[str, str] | str, int]:
        location = self.geoparse(request.json["text"])
        return location.get("error", location), 200 + 200 * ("error" in location)


class Heatmap(Resource):
    with open("data/districts.geojson") as file:
        regions = [shape(feature["geometry"]).buffer(0)
                   for feature in json.load(file)["features"]]
    if Path("data/hits.json").exists():
        with open("data/hits.json") as file:
            hits = json.load(file)
    else:
        hits = [[] for _ in regions]

    def get(self) -> list[list[str]]:
        return Heatmap.hits

    def put(self) -> list[list[str]]:
        assert type(request.json) is dict
        keywords = request.json.get("keywords") or ["incêndio"]
        options = request.json.get("options") or {"-filter": "replies", "lang": "pt"}
        volume = request.json.get("volume") or 100
        query = " ".join(chain(keywords, map("{0[0]}:{0[1]}".format, options.items())))
        tweets = map(attrgetter("content"), TwitterSearchScraper(query).get_items())
        Heatmap.hits = [[] for _ in Heatmap.regions]
        for tweet in tweets:
            if not Classify.classify(tweet)["fire"]:
                continue
            if "error" in (location := Geoparse.geoparse(tweet)):
                continue
            geometry = shape(location["geometry"])
            included = False
            for index, region in enumerate(Heatmap.regions):
                if geometry.intersects(region):
                    intersection = geometry.intersection(region)
                    if intersection.area > 1e-5 or type(intersection) is Point:
                        Heatmap.hits[index].append(tweet)
                        included = True
            if not included:
                continue
            if (volume := volume - 1) == 0:
                break
        with open("data/hits.json", "w") as file:
            json.dump(Heatmap.hits, file)
        return Heatmap.hits


if __name__ == "__main__":
    CORS(app := Flask(__name__))
    api = Api(app)
    api.add_resource(Classify, "/classify")
    api.add_resource(Geoparse, "/geoparse")
    api.add_resource(Heatmap, "/heatmap")
    app.run(port=5000)
