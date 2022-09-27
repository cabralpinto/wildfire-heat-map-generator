import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import ShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

data = pd.read_excel("data/news.xlsx", usecols=["text", "label"])
pipeline = Pipeline([("1", CountVectorizer()), ("2", TfidfTransformer()), ("3", SVC())])
metrics = pd.DataFrame(0, index=range(30), columns=("accuracy", "precision", "recall"))
splits = ShuffleSplit(n_splits=30, test_size=0.1, random_state=0).split(data)
for index, (train, test) in enumerate(splits):
    pipeline.fit(data["text"][train], data["label"][train])
    predictions = pipeline.predict(data["text"][test])
    (tn, fp), (fn, tp) = confusion_matrix(data["label"][test], predictions)
    metrics.at[index, "accuracy"] = (tp + tn) / (tp + fp + fn + tn) * 100
    metrics.at[index, "precision"] = tp / (tp + fp) * 100
    metrics.at[index, "recall"] = tp / (tp + fn) * 100
    metrics.at[index, "f1"] = 200 * tp / (2 * tp + fp + fn)
metrics.to_csv("models/svm/metrics.csv", index=False)
print(metrics.mean().combine(metrics.sem(), "{0:.1f} ± {1:.1f}".format).to_string())