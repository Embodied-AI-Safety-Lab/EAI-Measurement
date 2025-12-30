# EI Text Classifier

A lightweight text classification pipeline for identifying EI-related candidates from app metadata using sentence embeddings and a high-recall classifier.

The system is designed for large-scale candidate discovery, prioritizing recall over precision.

---

## Repository Structure

ei_text_classifier/  
│  
├── train_ei_classifier.py  
├── score_unlabeled_apps.py  
├── README.md  
│  
├── artifacts/ # Generated after training  
│ ├── ei_classifier.pkl  
│ ├── ei_centroid.npy  
│ └── ei_threshold.txt  
│  
└── outputs/ # Generated after scoring  


---

## Overview

This repository implements a two-stage text classification workflow:

1. **Train a high-recall EI classifier** using labeled data  
2. **Score unlabeled data** to identify EI candidates

The pipeline combines:
- Multilingual Sentence-BERT embeddings
- Logistic regression with balanced class weights
- A centroid-based semantic similarity signal for interpretability

All trained artifacts are stored locally and reused during inference.

---

## Requirements

- Python 3.8+
- torch
- sentence-transformers
- scikit-learn
- pandas
- numpy
- joblib

---

## Step 1: Train the Classifier

### Script
```
train_ei_classifier.py
```

### Input CSV Requirements (Labeled Data)

The training CSV file **must contain the following columns**:

| Column | Description |
|------|-------------|
| title | App or product title |
| description | App or product description |
| label | Binary label (1 = EI, 0 = non-EI) |

Other columns (if present) are ignored.

### What This Script Does

- Loads the labeled dataset from a user-specified file
- Concatenates `title` and `description` into a single text field
- Encodes text using a multilingual Sentence-BERT model
- Trains a logistic regression classifier optimized for high recall
- Computes:
  - A centroid of positive (EI) embeddings
  - A probability threshold achieving approximately 99% recall
- Saves all artifacts to the `artifacts/` directory

### Run

```
python3 train_ei_classifier.py <labeled_dataset.csv>
```

Outputs (artifacts/)

- ei_classifier.pkl — trained logistic regression classifier
- ei_centroid.npy — normalized centroid of positive samples
- ei_threshold.txt — high-recall probability threshold

---

## Step 2: Score Unlabeled Data
### Script
```
score_unlabeled_apps.py
```
### Input CSV Requirements (Unlabeled Data)

The scoring CSV file must contain the following columns:

| Column | Description |
|------|-------------|
| title | App or product title |
| description | App or product description |

The file must contain exactly these two columns in order.

No label column is required.

### What This Script Does

- Loads trained artifacts from artifacts/

- Encodes text using the same Sentence-BERT model

- Computes:

  - EI probability score from the classifier

  - Cosine similarity to the EI centroid

  - A binary candidate flag based on the learned threshold

- Sorts results by EI probability in descending order

### Run
```
python3 score_unlabeled_apps.py <unlabeled_dataset.csv>
```
### Output

A scored CSV file saved to the outputs/ directory:
```
<unlabeled_dataset>_scored.csv
```

Additional columns in the output:

| Column                 | Description                       |
| ---------------------- | --------------------------------- |
| ei_probability         | Classifier probability score      |
| similarity_to_centroid | Cosine similarity to EI centroid  |
| is_candidate           | 1 if above threshold, otherwise 0 |

### Design Notes
- The system is recall-first by design
- The probability threshold is learned from positive samples only
- Centroid similarity provides an interpretable semantic signal
- Fully offline once training artifacts are generated

### Typical Use Cases
- App or product discovery
- Weak-signal mining
- Early-stage category identification
- Human-in-the-loop review pipelines