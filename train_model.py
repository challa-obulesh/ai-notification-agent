"""
Phase 5 – Importance Classification Model Training
────────────────────────────────────────────────────
Trains multiple ML classifiers on the notification dataset,
evaluates them, and saves the best model + vectorizer to disk.

Models compared:
  • Naive Bayes (baseline)
  • Logistic Regression
  • Random Forest
  • Gradient Boosting (XGB-like via sklearn)

Feature extraction:
  • TF-IDF (unigrams + bigrams)
"""

import os
import sys
import time
import joblib
import logging
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB, ComplementNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report, accuracy_score, confusion_matrix, roc_auc_score
)
from sklearn.preprocessing import LabelEncoder

from preprocess import batch_preprocess

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────────
DATA_PATH = Path("data/notifications.csv")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)


def load_data():
    """Load dataset; generate it first if missing."""
    if not DATA_PATH.exists():
        logger.info("Dataset not found — generating synthetic data …")
        import importlib.util, pathlib
        spec = importlib.util.spec_from_file_location(
            "notifications_dataset",
            pathlib.Path("data") / "notifications_dataset.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        generate_dataset = mod.generate_dataset
        df = generate_dataset()
        DATA_PATH.parent.mkdir(exist_ok=True)
        df.to_csv(DATA_PATH, index=False)
        logger.info(f"Dataset saved to {DATA_PATH} ({len(df)} rows)")
    else:
        df = pd.read_csv(DATA_PATH)
        logger.info(f"Loaded dataset: {len(df)} rows")

    return df


def prepare_features(df):
    """Preprocess text and encode labels."""
    logger.info("Preprocessing text …")
    df["clean"] = batch_preprocess(df["message"].tolist())

    # Encode labels
    le = LabelEncoder()
    df["label_enc"] = le.fit_transform(df["label"])  # important=0, not_important=1

    return df, le


def build_tfidf_vectorizer():
    return TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=15000,
        sublinear_tf=True,
        min_df=2,
        max_df=0.97,
    )


def train_and_evaluate(X_train, X_test, y_train, y_test, label_names):
    """Train all models, return results dict and best pipeline."""

    vectorizer = build_tfidf_vectorizer()
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    models = {
        "Complement Naive Bayes": ComplementNB(alpha=0.1),
        "Logistic Regression": LogisticRegression(
            max_iter=1000, C=5.0, solver="lbfgs", class_weight="balanced"
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=20, n_jobs=-1, class_weight="balanced", random_state=42
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=150, learning_rate=0.1, max_depth=5, random_state=42
        ),
    }

    results = {}
    best_acc = 0.0
    best_name = None
    best_clf = None

    for name, clf in models.items():
        logger.info(f"Training {name} …")
        t0 = time.time()
        clf.fit(X_train_vec, y_train)
        elapsed = time.time() - t0

        y_pred = clf.predict(X_test_vec)
        acc = accuracy_score(y_test, y_pred)

        try:
            proba = clf.predict_proba(X_test_vec)[:, 1]
            auc = roc_auc_score(y_test, proba)
        except Exception:
            auc = None

        results[name] = {
            "accuracy": acc,
            "auc": auc,
            "report": classification_report(y_test, y_pred, target_names=label_names),
            "confusion": confusion_matrix(y_test, y_pred).tolist(),
            "train_time": elapsed,
        }

        logger.info(
            f"  {name}: acc={acc:.4f}"
            + (f"  auc={auc:.4f}" if auc else "")
            + f"  ({elapsed:.1f}s)"
        )

        if acc > best_acc:
            best_acc = acc
            best_name = name
            best_clf = clf

    logger.info(f"\nBest model: {best_name} (accuracy={best_acc:.4f})")
    return results, vectorizer, best_clf, best_name


def save_model(vectorizer, clf, le, model_name):
    """Persist the vectorizer, classifier, and label-encoder."""
    joblib.dump(vectorizer, MODEL_DIR / "tfidf_vectorizer.pkl")
    joblib.dump(clf, MODEL_DIR / "classifier.pkl")
    joblib.dump(le, MODEL_DIR / "label_encoder.pkl")
    joblib.dump({"model_name": model_name}, MODEL_DIR / "model_info.pkl")
    logger.info(f"Model artifacts saved to '{MODEL_DIR}/'")


def print_results(results):
    print("\n" + "=" * 70)
    print("  MODEL COMPARISON REPORT")
    print("=" * 70)
    for name, r in results.items():
        auc_str = f"  AUC: {r['auc']:.4f}" if r["auc"] else ""
        print(f"\n  {name}")
        print(f"   Accuracy: {r['accuracy']:.4f}{auc_str}  |  Train time: {r['train_time']:.1f}s")
        print(r["report"])
    print("=" * 70)


def main():
    logger.info("=" * 55)
    logger.info("  AI Notification Agent — Model Training")
    logger.info("=" * 55)

    # 1. Load data
    df = load_data()

    # 2. Preprocess
    df, le = prepare_features(df)
    label_names = list(le.classes_)

    # 3. Split
    X_train, X_test, y_train, y_test = train_test_split(
        df["clean"], df["label_enc"],
        test_size=0.20, random_state=42, stratify=df["label_enc"]
    )
    logger.info(f"Train: {len(X_train)}  |  Test: {len(X_test)}")

    # 4. Train & evaluate
    results, vectorizer, best_clf, best_name = train_and_evaluate(
        X_train, X_test, y_train, y_test, label_names
    )

    # 5. Print summary
    print_results(results)

    # 6. Save best model
    save_model(vectorizer, best_clf, le, best_name)

    logger.info("Training complete! Run 'python app.py' to start the API.")


if __name__ == "__main__":
    main()
