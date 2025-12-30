import os
import sys
import joblib
import torch
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression

# =====================
# Command-line arguments
# =====================
if len(sys.argv) < 2:
    print("Usage: python3 train_ei_classifier.py <labeled_dataset.csv>")
    sys.exit(1)

DATA_PATH = sys.argv[1]

# =====================
# Config
# =====================
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
ARTIFACT_DIR = "artifacts"
RANDOM_STATE = 42

os.makedirs(ARTIFACT_DIR, exist_ok=True)

# =====================
# Load dataset
# =====================
print(f"Loading labeled dataset from {DATA_PATH}...")

df = pd.read_csv(
    DATA_PATH,
    encoding="latin1",
    engine="python",
    on_bad_lines="skip"
)

print("Original columns:", df.columns.tolist())

# 必须包含的字段
required_cols = ["title", "description", "label"]
missing = set(required_cols) - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# 只选择我们需要的列（其余全部忽略）
df = df[required_cols].copy()

df["title"] = df["title"].fillna("")
df["description"] = df["description"].fillna("")
df["label"] = df["label"].astype(int)

df["text"] = df["title"] + " " + df["description"]

print(f"Total apps: {len(df)}")
print(f"Positive apps: {(df.label == 1).sum()}")

# =====================
# Encode
# =====================
device = "cuda" if torch.cuda.is_available() else "cpu"
encoder = SentenceTransformer(MODEL_NAME, device=device)

embeddings = encoder.encode(
    df["text"].tolist(),
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True
)

X = embeddings
y = df["label"].values

# =====================
# Train classifier
# =====================
print("Training high-recall classifier...")

clf = LogisticRegression(
    class_weight="balanced",
    max_iter=1000,
    random_state=RANDOM_STATE
)

clf.fit(X, y)

joblib.dump(clf, f"{ARTIFACT_DIR}/ei_classifier.pkl")

# =====================
# Positive centroid
# =====================
positive_embeddings = X[y == 1]
centroid = positive_embeddings.mean(axis=0)
centroid /= np.linalg.norm(centroid)

np.save(f"{ARTIFACT_DIR}/ei_centroid.npy", centroid)

# =====================
# High-recall threshold
# =====================
positive_probs = clf.predict_proba(positive_embeddings)[:, 1]
threshold = np.percentile(positive_probs, 1)  # ≈99% recall

with open(f"{ARTIFACT_DIR}/ei_threshold.txt", "w") as f:
    f.write(str(threshold))

print("====================================")
print("Training finished")
print(f"Threshold (≈99% recall): {threshold:.4f}")
print("Artifacts saved to /artifacts")
print("====================================")
