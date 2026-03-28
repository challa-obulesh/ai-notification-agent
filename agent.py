"""
Phase 7 – AI Agent Core Logic
────────────────────────────────────────────────────────────────
The NotificationAgent orchestrates:
  1. Text preprocessing
  2. ML importance classification
  3. Category detection & explanation generation
  4. Structured response assembly
"""

import joblib
import logging
import time
from pathlib import Path
from preprocess import preprocess
from explainer import generate_explanation, detect_category

logger = logging.getLogger(__name__)

MODEL_DIR = Path("models")


class NotificationAgent:
    """
    Core AI agent that processes notifications end-to-end.

    Usage:
        agent = NotificationAgent()
        result = agent.analyze("Your OTP is 456782. Valid for 10 mins.")
    """

    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.label_encoder = None
        self.model_name = "Not loaded"
        self._loaded = False
        self._load_model()

    def _load_model(self):
        """Load trained model artifacts."""
        try:
            self.vectorizer = joblib.load(MODEL_DIR / "tfidf_vectorizer.pkl")
            self.classifier = joblib.load(MODEL_DIR / "classifier.pkl")
            self.label_encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")
            info = joblib.load(MODEL_DIR / "model_info.pkl")
            self.model_name = info.get("model_name", "Unknown")
            self._loaded = True
            logger.info(f"✅ Model loaded: {self.model_name}")
        except FileNotFoundError:
            logger.warning(
                "⚠️  Model files not found. "
                "Run 'python train_model.py' to train the model first. "
                "Using rule-based fallback."
            )
            self._loaded = False

    def _classify(self, clean_text: str) -> tuple[str, float]:
        """Return (label, confidence) using the ML model or fallback."""
        if not self._loaded:
            return self._rule_based_classify(clean_text)

        vec = self.vectorizer.transform([clean_text])
        pred_enc = self.classifier.predict(vec)[0]
        label = self.label_encoder.inverse_transform([pred_enc])[0]

        try:
            proba = self.classifier.predict_proba(vec)[0]
            confidence = float(max(proba))
        except Exception:
            confidence = 1.0

        return label, confidence

    @staticmethod
    def _rule_based_classify(clean_text: str) -> tuple[str, float]:
        """Simple keyword-based fallback classifier."""
        HIGH_KEYWORDS = {
            "otp", "debit", "credit", "transaction", "bank", "alert",
            "urgent", "emergency", "password", "kyc", "salary", "emi",
            "expire", "renew", "appointment", "doctor", "flight", "ticket"
        }
        NOT_KEYWORDS = {
            "sale", "offer", "discount", "cashback", "flash", "exclusive",
            "liked", "commented", "follow", "trending", "horoscope", "quiz",
            "download", "reward", "earn"
        }

        words = set(clean_text.lower().split())
        imp_score = len(words & HIGH_KEYWORDS)
        not_score = len(words & NOT_KEYWORDS)

        if imp_score > not_score:
            return "important", min(0.7 + imp_score * 0.05, 0.99)
        else:
            return "not_important", min(0.7 + not_score * 0.05, 0.99)

    def analyze(self, message: str) -> dict:
        """
        Main agent entry point.

        Args:
            message: Raw notification string.

        Returns:
            Structured analysis dict.
        """
        t_start = time.time()

        if not message or not message.strip():
            return {
                "status": "error",
                "message": "Empty notification received.",
                "importance": "LOW",
                "action_required": False,
            }

        # Step 1: Preprocess
        clean = preprocess(message)

        # Step 2: Classify importance
        label, confidence = self._classify(clean)

        # Step 3: Generate explanation
        explanation_data = generate_explanation(message, predicted_label=label)

        # Step 4: Assemble response
        processing_time_ms = round((time.time() - t_start) * 1000, 1)

        response = {
            "status": "success",
            "original_message": message,
            "clean_text": clean,
            "label": label,
            "confidence": round(confidence, 4),
            "importance": explanation_data["importance"],
            "category": explanation_data["category"],
            "icon": explanation_data["icon"],
            "explanation": explanation_data["explanation"],
            "detail": explanation_data["detail"],
            "action_required": explanation_data["action_required"],
            "model_used": self.model_name if self._loaded else "rule-based",
            "processing_time_ms": processing_time_ms,
        }

        # Logging summary
        logger.info(
            f"[{label.upper()}] [{explanation_data['category']}] "
            f"conf={confidence:.2f}  {message[:60]}…"
        )

        return response


# Singleton instance (reused across API requests)
_agent_instance = None


def get_agent() -> NotificationAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = NotificationAgent()
    return _agent_instance


# ── Quick demo ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = NotificationAgent()

    demo_messages = [
        "HDFC Bank: OTP for your transaction is 847321. Do NOT share.",
        "Rs.12000 debited from your account. Avl Bal: Rs.8000.",
        "Amazon: Your order #789012 has been shipped. Arrives by tomorrow.",
        "Server DOWN! Critical failure. Contact on-call engineer NOW.",
        "🎉 Flipkart Flash Sale: 60% OFF! Grab deals before midnight!",
        "{name} liked your Instagram photo.",
        "Reminder: Dentist appointment on 20 Mar at 11:00 AM.",
        "Your Netflix subscription expires on 25 Mar. Renew now.",
        "Congratulations! You won Rs.5000 in our lucky draw. Click to claim!",
        "Meeting: Sprint Review at 3:00 PM. Join on Google Meet.",
    ]

    print("\n" + "=" * 70)
    print("  AI NOTIFICATION AGENT — Demo")
    print("=" * 70)

    for msg in demo_messages:
        r = agent.analyze(msg)
        print(f"\n📩 {msg[:70]}")
        print(f"   {r['icon']}  [{r['importance']}] [{r['category']}]  conf={r['confidence']:.2f}")
        print(f"   {r['explanation'][:120]}")
        if r["detail"]:
            print(f"   ℹ️  {r['detail']}")
        action = "⚠️  ACTION REQUIRED" if r["action_required"] else "✅ No action needed"
        print(f"   {action}  ({r['processing_time_ms']}ms)")
