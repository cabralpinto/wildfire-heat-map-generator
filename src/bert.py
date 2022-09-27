from pathlib import Path

import numpy as np
import pandas as pd
from datasets import Dataset
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import ShuffleSplit
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          Trainer, TrainingArguments)

tokenizer = AutoTokenizer.from_pretrained(
    "neuralmind/bert-large-portuguese-cased", do_lower_case=False)
dataset = (
    Dataset.from_pandas(pd.read_excel("data/news.xlsx", usecols=["text", "label"]))
    .map(
        lambda example: tokenizer(
            example["text"],
            padding="max_length",
            truncation=True,
            max_length=100,
        ),
        remove_columns=["text"]
    )
)
if Path("models/bert/metrics.csv").exists():
    metrics = pd.read_csv("models/bert/metrics.csv")
else:
    metrics = pd.DataFrame(columns=("accuracy", "precision", "recall", "f1"))
splits = ShuffleSplit(n_splits=30, test_size=0.1, random_state=0).split(dataset)
for index, (train, test) in enumerate(splits):
    if index < metrics.shape[0]:
        continue
    classifier = AutoModelForSequenceClassification.from_pretrained(
        "neuralmind/bert-base-portuguese-cased", num_labels=2)
    arguments = TrainingArguments("checkpoints", num_train_epochs=3)
    trainer = Trainer(classifier, arguments, train_dataset=dataset.select(train))
    trainer.train()
    predictions = np.argmax(trainer.predict(dataset.select(test)).predictions, 1)
    (tn, fp), (fn, tp) = confusion_matrix(dataset.select(test)["label"], predictions)
    metrics.at[index, "accuracy"] = 100 * (tp + tn) / (tp + fp + fn + tn)
    metrics.at[index, "precision"] = 100 * tp / (tp + fp)
    metrics.at[index, "recall"] = 100 * tp / (tp + fn)
    metrics.at[index, "f1"] = 200 * tp / (2 * tp + fp + fn)
    if metrics.size == 4 or metrics.at[index, "f1"] > metrics["f1"][:index].max():
        trainer.save_model("models/bert")
    metrics.to_csv("models/bert/metrics.csv", index=False)
print(metrics.mean().combine(metrics.sem(), "{0:.1f} ± {1:.1f}".format).to_string())
