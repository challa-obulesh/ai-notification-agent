"""
Phase 3 & 4 – NLP Preprocessing + Feature Engineering
────────────────────────────────────────────────────────
Pipeline:
  Raw notification
      ↓ lowercase + punctuation removal
      ↓ tokenisation
      ↓ stopword removal
      ↓ lemmatisation
      → clean text (for TF-IDF & ML models)
"""

import re
import string
import nltk
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ── Download required NLTK data (silent if already present) ──────────────────
for pkg in ["punkt", "stopwords", "wordnet", "punkt_tab", "averaged_perceptron_tagger"]:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ── Constants ────────────────────────────────────────────────────────────────
STOP_WORDS = set(stopwords.words("english"))
# Keep some important words that are in stopwords but matter for notifications
KEEP_WORDS = {"not", "no", "urgent", "alert", "warning", "never", "do", "don't"}
STOP_WORDS -= KEEP_WORDS

# Regex patterns
URL_PATTERN = re.compile(r"http\S+|www\.\S+")
PHONE_PATTERN = re.compile(r"\b\d{10,13}\b")
OTP_PATTERN = re.compile(r"\b\d{4,8}\b")  # OTPs and numbers
MONEY_PATTERN = re.compile(r"(rs\.?|₹|inr)\s?\d+[\d,]*", re.IGNORECASE)

lemmatizer = WordNetLemmatizer()


def preprocess(text: str, keep_numbers: bool = True) -> str:
    """
    Full NLP preprocessing pipeline.

    Args:
        text: Raw notification string.
        keep_numbers: If True, replaces numbers with semantic tokens (OTP_NUM, MONEY_AMT).

    Returns:
        Cleaned, lemmatized text string.
    """
    if not text or not isinstance(text, str):
        return ""

    # Step 1: Lowercase
    text = text.lower()

    # Step 2: Replace URLs
    text = URL_PATTERN.sub("url_token", text)

    # Step 3: Tag money amounts before removing numbers
    if keep_numbers:
        text = MONEY_PATTERN.sub("money_amt", text)

    # Step 4: Remove punctuation (keep spaces)
    text = text.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))

    # Step 5: Tokenise
    try:
        tokens = word_tokenize(text)
    except Exception:
        tokens = text.split()

    # Step 6: Tag OTP/numeric tokens
    if keep_numbers:
        def tag_numbers(tok):
            if re.match(r"^\d{4,8}$", tok):
                return "otp_num"
            if re.match(r"^\d+$", tok):
                return "number_token"
            return tok
        tokens = [tag_numbers(t) for t in tokens]

    # Step 7: Remove stopwords, keep only alphabetic + special tokens
    cleaned = [
        t for t in tokens
        if t not in STOP_WORDS and (t.isalpha() or "_" in t)
    ]

    # Step 8: Lemmatise
    lemmatized = [lemmatizer.lemmatize(t) for t in cleaned]

    return " ".join(lemmatized)


def batch_preprocess(texts: list, keep_numbers: bool = True) -> list:
    """Apply preprocess() to a list of texts."""
    return [preprocess(t, keep_numbers) for t in texts]


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    samples = [
        "Your bank OTP is 456732. Valid for 10 minutes. Do not share.",
        "HDFC Bank: Rs.5000 debited from A/C XX1234 on 15 Mar 2024.",
        "🎉 BIG SALE! Up to 70% OFF on fashion. Shop now on Amazon!",
        "Meeting reminder: Project Update at 3:00 PM today.",
        "{name} liked your photo.",
        "Your Amazon order #987654 has been shipped and will arrive by 20 Apr.",
    ]

    print("\n" + "=" * 60)
    print("NLP Preprocessing Pipeline — Sample Output")
    print("=" * 60)
    for s in samples:
        cleaned = preprocess(s)
        print(f"\n  Input : {s}")
        print(f"  Output: {cleaned}")
    print("=" * 60)
