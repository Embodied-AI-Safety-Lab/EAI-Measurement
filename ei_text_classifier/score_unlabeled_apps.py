import os
import sys
import joblib
import torch
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# =====================
# Command-line arguments
# =====================
if len(sys.argv) < 2:
    print("Usage: python3 score_unlabeled.py <filename>")
    sys.exit(1)

DATA_PATH = sys.argv[1]
OUTPUT_PATH = os.path.splitext(DATA_PATH)[0] + "_scored.csv"

# =====================
# Config
# =====================
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
ARTIFACT_DIR = "artifacts"

os.makedirs("outputs", exist_ok=True)

# =====================
# Load dataset
# =====================
print(f"Loading unlabeled dataset from {DATA_PATH}...")

df = pd.read_csv(
    DATA_PATH,
    encoding="latin1",
    engine="python",
    on_bad_lines="skip"
)

df.columns = ["title", "description"]
df["title"] = df["title"].fillna("")
df["description"] = df["description"].fillna("")
df["text"] = df["title"] + " " + df["description"]

print(f"Total apps: {len(df)}")

# =====================
# Load artifacts
# =====================
clf = joblib.load(f"{ARTIFACT_DIR}/ei_classifier.pkl")
centroid = np.load(f"{ARTIFACT_DIR}/ei_centroid.npy")

with open(f"{ARTIFACT_DIR}/ei_threshold.txt") as f:
    threshold = float(f.read().strip())

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

# =====================
# Score
# =====================
df["ei_probability"] = clf.predict_proba(embeddings)[:, 1]
df["similarity_to_centroid"] = cosine_similarity(
    embeddings,
    centroid.reshape(1, -1)
).flatten()

df["is_candidate"] = (df["ei_probability"] >= threshold).astype(int)

# =====================
# Save
# =====================
output_file = os.path.join("outputs", os.path.basename(OUTPUT_PATH))
df.sort_values("ei_probability", ascending=False).to_csv(
    output_file, index=False
)

print("====================================")
print("Scoring finished")
print(f"Threshold: {threshold:.4f}")
print(f"Candidates: {df.is_candidate.sum()}")
print(f"Saved to {output_file}")
print("====================================")
