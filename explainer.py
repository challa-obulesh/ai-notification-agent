"""
Phase 6 – Message Explanation System
──────────────────────────────────────────────────────────────────
Generates human-readable explanations for notification messages.

Strategy (no internet required):
  1. Rule-based template engine (fast, deterministic) — primary
  2. Lightweight local summarization via rule heuristics
  3. Optional: HuggingFace transformer pipeline (lazy-loaded)

Architecture keeps the system fully offline-capable.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Category Detection Patterns ─────────────────────────────────────────────
CATEGORY_PATTERNS = [
    # (pattern, category, importance, icon)
    (r"\botp\b|\bverification code\b|\bsecurity code\b|\bauthentication\b",     "OTP",          "HIGH",   "🔐"),
    (r"\bdebited\b|\bcredited\b|\btransaction\b|\bneft\b|\bimps\b|\bupi\b",     "BANK_TXN",     "HIGH",   "🏦"),
    (r"\bpayment due\b|\bemi\b|\bloan\b|\boutstanding\b|\bdue date\b",           "PAYMENT_DUE",  "HIGH",   "💳"),
    (r"\bsalary\b|\bpayroll\b|\bpay slip\b",                                    "SALARY",       "HIGH",   "💰"),
    (r"\bpassword\b|\bsecurity alert\b|\bnew login\b|\bunauthorized\b",          "SECURITY",     "HIGH",   "🚨"),
    (r"\bkYC\b|\bkyc\b|\bpan\b|\baadhaar\b|\bverif",                           "KYC",          "HIGH",   "📋"),
    (r"\bdoctor\b|\bappointment\b|\bhospital\b|\bmedic\b|\bmedicine\b",          "HEALTH",       "HIGH",   "🏥"),
    (r"\bemergency\b|\burgent\b|\bserver down\b|\bcritical\b",                   "EMERGENCY",    "HIGH",   "🆘"),
    (r"\bflight\b|\bticket\b|\bboarding\b|\birctc\b|\btrain\b",                 "TRAVEL",       "HIGH",   "✈️"),
    (r"\binterview\b|\bdeadline\b|\bmeeting\b|\bschedule\b|\breminder\b",        "WORK",         "MEDIUM", "📅"),
    (r"\bshipped\b|\bdelivery\b|\bdelivered\b|\bpackage\b|\boutfordelivery\b",   "DELIVERY",     "MEDIUM", "📦"),
    (r"\brefund\b|\border cancel\b",                                             "REFUND",       "MEDIUM", "💸"),
    (r"\bexpir\b|\brenew\b|\bsubscription\b|\binsurance\b",                     "RENEWAL",      "MEDIUM", "🔔"),
    (r"\btax\b|\bitr\b|\bincome tax\b|\bepfo\b|\bpf\b",                         "GOVERNMENT",   "MEDIUM", "🏛️"),
    (r"\bwhatsapp\b|\bmissed call\b|\bcall me\b|\bvideo call\b",                "PERSONAL_MSG", "MEDIUM", "📱"),
    # Not-important
    (r"\bsale\b|\bdiscount\b|\boffer\b|\bcashback\b|\bflash\b|\bexclusive\b",   "PROMOTION",    "LOW",    "🛍️"),
    (r"\bliked your\b|\bcommented\b|\bfollowing\b|\bfriend request\b|\bretweet", "SOCIAL",      "LOW",    "👍"),
    (r"\bnew episode\b|\bbreaking\b|\btrending\b|\bscore update\b|\bheadline\b", "NEWS",        "LOW",    "📰"),
    (r"\breward\b|\bpoints\b|\bspin\b|\blucky draw\b|\bwon\b|\bwinner\b",        "GAMIFICATION","LOW",    "🎁"),
    (r"\bweather\b|\bforecast\b|\btemperature\b",                                "WEATHER",      "LOW",    "⛅"),
    (r"\bhoroscope\b|\bzodiac\b|\bquiz\b|\bpoll\b",                              "ENTERTAINMENT","LOW",   "🎭"),
]

# ─── Explanation Templates ────────────────────────────────────────────────────
EXPLANATION_TEMPLATES = {
    "OTP": (
        "🔐 One-Time Password (OTP) received. "
        "This is a temporary code sent by a service or bank to verify your identity. "
        "⚠️ Never share this code with anyone — banks and companies will never ask for it."
    ),
    "BANK_TXN": (
        "🏦 Bank transaction alert. "
        "Money has been moved in or out of your bank account. "
        "Please verify this matches an expected transaction. "
        "If unrecognised, contact your bank immediately."
    ),
    "PAYMENT_DUE": (
        "💳 Payment reminder. You have an outstanding payment due soon. "
        "Missing the deadline may result in a penalty or late fee. "
        "Pay before the due date to avoid charges."
    ),
    "SALARY": (
        "💰 Salary credited! Your monthly salary or payroll payment has been processed "
        "and deposited into your account."
    ),
    "SECURITY": (
        "🚨 Security alert! An unusual activity or login attempt has been detected on your account. "
        "If you did not initiate this action, change your password immediately and contact support."
    ),
    "KYC": (
        "📋 KYC / Document Verification required. "
        "Your service provider needs to verify your identity documents. "
        "Failure to comply may result in account suspension."
    ),
    "HEALTH": (
        "🏥 Health reminder. You have a medical appointment, prescription, "
        "or health-related update that needs attention."
    ),
    "EMERGENCY": (
        "🆘 URGENT: This message requires your immediate attention. "
        "Please act on it right away to prevent any disruption or serious issue."
    ),
    "TRAVEL": (
        "✈️ Travel alert. You have an upcoming flight, train, or transport booking. "
        "Please check-in on time and keep your ticket handy."
    ),
    "WORK": (
        "📅 Work/Calendar reminder. You have a scheduled meeting, interview, or work deadline. "
        "Please prepare accordingly and join on time."
    ),
    "DELIVERY": (
        "📦 Delivery update. Your ordered package is on its way or has been delivered. "
        "Ensure someone is available to receive it."
    ),
    "REFUND": (
        "💸 Refund processed. A refund for your order has been initiated. "
        "It typically takes 3–7 business days to reflect in your account."
    ),
    "RENEWAL": (
        "🔔 Subscription/Policy renewal reminder. "
        "One of your services, policies, or domains is about to expire. "
        "Renew it to avoid service interruption."
    ),
    "GOVERNMENT": (
        "🏛️ Official government notification. This may contain important information "
        "about your taxes, provident fund, or official documents. Review it carefully."
    ),
    "PERSONAL_MSG": (
        "📱 Personal message alert. Someone is trying to reach you urgently "
        "via call or message. It may require a prompt response."
    ),
    "PROMOTION": (
        "🛍️ Promotional offer. This is an advertisement or discount notification. "
        "No immediate action required unless you are interested in the offer."
    ),
    "SOCIAL": (
        "👍 Social media activity. Someone interacted with your social media content "
        "(liked, commented, or shared). No urgent action required."
    ),
    "NEWS": (
        "📰 News or entertainment update. "
        "This is a non-urgent content notification from a news or entertainment app."
    ),
    "GAMIFICATION": (
        "🎁 Reward or promotional notification. You may have earned points, a reward, "
        "or been entered into a contest. Verify if legitimate before clicking any links."
    ),
    "WEATHER": (
        "⛅ Weather update. Today's forecast or weather conditions for your area."
    ),
    "ENTERTAINMENT": (
        "🎭 Entertainment notification. This is a non-urgent content update "
        "from an entertainment or media app."
    ),
    "UNKNOWN": (
        "📬 Notification received. The content does not match any known pattern. "
        "Please read the message carefully and decide if action is required."
    ),
}

# ─── Key-info Extractors ──────────────────────────────────────────────────────
def _extract_amount(text: str) -> Optional[str]:
    m = re.search(r"(?:rs\.?|₹|inr)\s?([\d,]+)", text, re.IGNORECASE)
    if m:
        return f"₹{m.group(1)}"
    return None


def _extract_otp(text: str) -> Optional[str]:
    m = re.search(r"\b(\d{4,8})\b", text)
    if m:
        return m.group(1)
    return None


def _extract_sender(text: str) -> Optional[str]:
    m = re.match(r"^([A-Za-z][A-Za-z\s]{1,20})[\s:–-]", text)
    if m:
        return m.group(1).strip()
    return None


def _build_detail_line(category: str, text: str) -> str:
    """Build a short context line with extracted facts."""
    parts = []
    amount = _extract_amount(text)
    otp = _extract_otp(text)
    sender = _extract_sender(text)

    if sender:
        parts.append(f"Sender: {sender}")
    if category == "OTP" and otp:
        parts.append(f"Code: {otp} (do NOT share)")
    if amount:
        parts.append(f"Amount: {amount}")

    return " | ".join(parts) if parts else ""


def detect_category(text: str):
    """Return (category, icon) based on pattern matching."""
    lower = text.lower()
    for pattern, category, importance, icon in CATEGORY_PATTERNS:
        if re.search(pattern, lower):
            return category, importance, icon
    return "UNKNOWN", "LOW", "📬"


def generate_explanation(message: str, predicted_label: str = None) -> dict:
    """
    Generate a structured explanation for a notification.

    Returns:
        {
            "category": str,
            "importance": str,   # HIGH / MEDIUM / LOW
            "icon": str,
            "explanation": str,
            "detail": str,
            "action_required": bool,
        }
    """
    category, importance, icon = detect_category(message)

    # If classifier says not_important, downgrade to LOW anyway
    if predicted_label == "not_important" and importance == "HIGH":
        importance = "MEDIUM"

    explanation = EXPLANATION_TEMPLATES.get(category, EXPLANATION_TEMPLATES["UNKNOWN"])
    detail = _build_detail_line(category, message)
    action_required = importance == "HIGH"

    return {
        "category": category,
        "importance": importance,
        "icon": icon,
        "explanation": explanation,
        "detail": detail,
        "action_required": action_required,
    }


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    samples = [
        "HDFC Bank: Your OTP is 783421. Valid for 10 mins. Do NOT share.",
        "Rs.15000 debited from your SBI account. Available balance: Rs.42000.",
        "Your Amazon order #456789 has been shipped. Arriving tomorrow.",
        "🎉 BIG SALE! 70% OFF on Myntra. Shop now!",
        "Urgent: Server down! Contact DevOps immediately.",
        "Meeting reminder: Scrum standup at 10:00 AM. Join now.",
    ]

    print("\n" + "=" * 65)
    print("  EXPLANATION ENGINE — Sample Output")
    print("=" * 65)
    for s in samples:
        r = generate_explanation(s)
        print(f"\n📩 Input : {s[:70]}")
        print(f"   {r['icon']} Category   : {r['category']}")
        print(f"   ⚡ Importance : {r['importance']}")
        print(f"   💬 Explanation: {r['explanation'][:120]}…")
        if r["detail"]:
            print(f"   ℹ️  Detail     : {r['detail']}")
        print(f"   🔴 Action req : {r['action_required']}")
