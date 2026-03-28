"""
Dataset Generator for AI Notification Agent
Generates a synthetic dataset of 10,000+ realistic notifications
with labels: important / not_important
"""

import pandas as pd
import random

# ─── Seed for reproducibility ───────────────────────────────────────────────
random.seed(42)

# ─── Template pools ──────────────────────────────────────────────────────────

IMPORTANT_TEMPLATES = [
    # OTP / Security
    "Your OTP for {bank} transaction is {otp}. Valid for 10 minutes. Do not share with anyone.",
    "{bank} Alert: OTP {otp} for login. Never share this OTP.",
    "Your verification code is {otp}. Use within 5 minutes.",
    "Security alert: New login detected on your {bank} account from {city}.",
    "ALERT: Your {bank} password was changed. If not you, call {phone}.",
    "2-Step Verification code: {otp}. This code expires in 10 minutes.",
    "Your Google security code is {otp}",
    "PayPal: Your security code is {otp}. It expires in 10 minutes.",
    # Bank / Finance
    "{bank}: Rs.{amount} debited from A/C XX{acc} on {date}. Avl Bal Rs.{bal}.",
    "Dear Customer, Rs.{amount} credited to your {bank} account. UPI Ref: {ref}",
    "HDFC Bank: Your FD of Rs.{amount} has matured. Please contact your branch.",
    "Alert! Your credit card ending {acc} has a payment due of Rs.{amount} on {date}.",
    "{bank} Loan EMI of Rs.{amount} is due on {date}. Pay now to avoid penalty.",
    "Salary of Rs.{amount} credited to your {bank} account on {date}.",
    "NEFT transfer of Rs.{amount} to {name} successful. Ref No: {ref}",
    "Your {bank} credit card statement for {date} is ready. Total due: Rs.{amount}.",
    "Cheque No.{ref} for Rs.{amount} presented for payment. Bal: Rs.{bal}.",
    "URGENT: Outstanding balance Rs.{amount} on your {bank} account. Pay immediately.",
    # Health / Emergency
    "Reminder: Your doctor appointment is scheduled for {date} at {time}.",
    "Hospital: Your blood test report is ready. Please collect from {city} branch.",
    "Medicine reminder: Take {med} {dose} at {time}.",
    "EMERGENCY: Server down! Immediate action required. Contact {name}.",
    "Alert: Fire drill at office on {date} at {time}. Please cooperate.",
    # Work / Professional
    "Meeting reminder: {subject} at {time} today. Join link: meet.google.com/{ref}",
    "Your flight {ref} to {city} departs at {time} tomorrow. Check-in now.",
    "Interview scheduled for {date} at {time} with {name}. Location: {city}.",
    "Project deadline: {subject} is due on {date}. Please submit.",
    "HR: Your salary slip for {date} is ready. Download from portal.",
    "Leave request #{ref} approved by {name}. Enjoy your leave!",
    "Action Required: Complete your KYC by {date} to avoid account suspension.",
    "Your passport application {ref} has been approved.",
    "Visa approved for {city}. Please collect your passport.",
    # Delivery / Orders
    "Your order #{ref} has been shipped and will arrive by {date}.",
    "OFD: Your {courier} package #{ref} is out for delivery today.",
    "Delivery failed for order #{ref}. Rescheduled to {date}.",
    "Your Amazon order of {product} has been delivered.",
    "Refund of Rs.{amount} for order #{ref} processed to your account.",
    # Subscriptions / Renewals
    "Your {service} subscription expires on {date}. Renew now.",
    "Netflix: Your payment of Rs.{amount} was successful. Happy streaming!",
    "Domain {ref} expires on {date}. Renew to keep your website live.",
    "Insurance policy #{ref} renewal premium Rs.{amount} due on {date}.",
    # WhatsApp / Personal (important)
    "{name}: Can you call me urgently? It's important.",
    "{name}: Emergency! Please call back ASAP.",
    "Missed call from {phone}. {name} is trying to reach you.",
    "Video call request from {name}. Accept?",
    # Government / Official
    "Income Tax Dept: Your ITR for AY {date} has been processed. Refund: Rs.{amount}.",
    "Aadhaar: Your OTP for e-KYC is {otp}. Do not share.",
    "EPFO: PF amount Rs.{amount} credited to your account.",
    "IRCTC: Your ticket for train {ref} on {date} is confirmed.",
]

NOT_IMPORTANT_TEMPLATES = [
    # Promotions / Ads
    "🎉 BIG SALE! Up to 70% OFF on fashion. Shop now on {brand}!",
    "{brand} SALE is LIVE! Buy 2 Get 1 Free. Limited time only!",
    "Exclusive offer just for you! Get Rs.{amount} cashback on {brand}.",
    "Flash Sale: {product} starting at just Rs.{amount}. Grab now!",
    "Hurry! Only {count} items left. Buy now before the deal expires.",
    "Congratulations! You've won a gift voucher worth Rs.{amount}. Claim now.",
    "Your {brand} rewards expire soon. Redeem {count} points today.",
    "{brand}: New arrivals just dropped. Shop the latest trends!",
    "Free shipping on orders above Rs.{amount}. Shop now on {brand}!",
    "Weekend sale: Extra 10% off with code SAVE10. Valid till {date}.",
    "New app update available. Update now to get exciting new features.",
    "{brand}: Thank you for your order. Rate us with 5 stars!",
    "Refer a friend to {brand} and earn Rs.{amount} reward.",
    "Your {brand} account has {count} unread notifications.",
    "Don't miss out! {product} goes out of stock soon.",
    "Hot deal of the day: {product} at just Rs.{amount}!",
    # Social media notifications
    "{name} liked your photo.",
    "{name} commented on your post: 'Nice one!'",
    "{name} tagged you in a photo.",
    "{count} people reacted to your Facebook post.",
    "You have {count} new friend suggestions on Facebook.",
    "{name} started following you on Instagram.",
    "Your reel got {count} views! Keep creating.",
    "{name} sent you a friend request.",
    "Twitter: {name} retweeted your tweet.",
    "LinkedIn: {count} people viewed your profile this week.",
    # News / Entertainment
    "Breaking: {subject} — Read more on our app.",
    "Today's top headlines are ready for you. Open news app.",
    "Match alert: {subject} score update. Click to view.",
    "New episode of {subject} is now available on {brand}.",
    "{brand}: {name} just uploaded a new video. Watch now!",
    "Trending now: {subject}. Join the conversation.",
    "Daily horoscope for {date}: Stars are in your favor!",
    "Quiz time! Answer today's question and win prizes.",
    # App engagement
    "{brand} app: You haven't opened us in a while. Come back!",
    "Good morning! Here's your daily digest from {brand}.",
    "Your weekly summary is ready. Here's what happened this week.",
    "{brand}: Complete your profile to get more connections.",
    "Reminder: You left items in your cart. Complete your purchase!",
    "Your favourite team {subject} has a match tonight!",
    "Weather update: {city} forecast for today — Sunny, 32°C.",
    "Daily reward available! Open {brand} app to claim.",
    # Spam / Generic
    "You are selected for a special offer. Click here to know more.",
    "Congratulations! Your number has been selected for a lucky draw.",
    "Earn money from home. Join our program today!",
    "Free recharge offer: Refer friends and get free mobile data.",
    "Limited time: Get a FREE subscription to {brand} for 30 days.",
    "Your opinion matters! Take a 2-minute survey and win Rs.{amount}.",
    "New games available on {brand}. Play and win cash prizes!",
    "Download {brand} app and get Rs.{amount} welcome bonus.",
    "Upcoming webinar: {subject}. Register for free now.",
    "Poll: {subject}? Vote now and see what others think.",
]

# ─── Placeholder fillers ──────────────────────────────────────────────────────

BANKS = ["HDFC Bank", "SBI", "ICICI Bank", "Axis Bank", "Kotak Bank", "PNB", "IndusInd Bank"]
BRANDS = ["Amazon", "Flipkart", "Myntra", "Meesho", "Ajio", "Nykaa", "Zomato", "Swiggy", "BigBasket"]
COURIERS = ["FedEx", "BlueDart", "Delhivery", "Ekart", "DTDC"]
SERVICES = ["Netflix", "Amazon Prime", "Hotstar", "Spotify", "YouTube Premium"]
NAMES = ["Rahul", "Priya", "Amit", "Sneha", "Rohit", "Deepa", "Arjun", "Kavya", "Nikhil", "Pooja"]
CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata"]
MEDS = ["Metformin", "Paracetamol", "Vitamin D", "Atorvastatin", "Aspirin"]
PRODUCTS = ["iPhone 15", "Samsung TV", "Nike Shoes", "Laptop", "Headphones", "Watch", "Book"]
SUBJECTS = ["Project Update", "Q3 earnings fall", "IPL 2024 final", "Team meeting", "Dark Matter", "AI Revolution"]


def _rand(lst):
    return random.choice(lst)


def _fill(template):
    """Fill template placeholders with random realistic values."""
    return template.format(
        bank=_rand(BANKS),
        otp=random.randint(100000, 999999),
        amount=random.choice([500, 1000, 2000, 5000, 10000, 25000, 50000]),
        acc=random.randint(1000, 9999),
        bal=random.randint(1000, 100000),
        ref=f"{random.randint(100000,999999)}",
        date=_rand(["15 Mar 2024", "20 Apr 2024", "01 May 2024", "10 Jun 2024", "25 Dec 2024"]),
        time=_rand(["9:00 AM", "2:30 PM", "4:00 PM", "11:00 AM", "6:00 PM"]),
        name=_rand(NAMES),
        city=_rand(CITIES),
        phone=f"98{random.randint(10000000, 99999999)}",
        subject=_rand(SUBJECTS),
        med=_rand(MEDS),
        dose="500mg",
        courier=_rand(COURIERS),
        brand=_rand(BRANDS),
        product=_rand(PRODUCTS),
        service=_rand(SERVICES),
        count=random.randint(2, 100),
    )


def generate_dataset(n_important=5000, n_not_important=5000):
    """Generate the full synthetic notification dataset."""
    rows = []

    for _ in range(n_important):
        tmpl = _rand(IMPORTANT_TEMPLATES)
        msg = _fill(tmpl)
        rows.append({"message": msg, "label": "important"})

    for _ in range(n_not_important):
        tmpl = _rand(NOT_IMPORTANT_TEMPLATES)
        msg = _fill(tmpl)
        rows.append({"message": msg, "label": "not_important"})

    df = pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)
    return df


if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    df = generate_dataset()
    df.to_csv("data/notifications.csv", index=False)
    print(f"Dataset generated: {len(df)} rows")
    print(df["label"].value_counts())
    print(df.head(5))
