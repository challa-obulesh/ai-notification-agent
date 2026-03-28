# 🤖 AI Notification Agent

> **Smart notification analyzer powered by NLP + Machine Learning**
> Reads any notification, classifies its importance, detects its category, and generates a human-readable explanation.

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 🔍 **NLP Preprocessing** | Tokenization, stopword removal, lemmatization |
| 🤖 **ML Classification** | TF-IDF + Logistic Regression / Random Forest / Naive Bayes |
| 📂 **20+ Categories** | OTP, Bank, Delivery, Health, Emergency, Promotions… |
| 💬 **Explanation Engine** | Rule-based natural language explanations |
| 🌐 **REST API** | Flask API with single & batch analysis endpoints |
| 🎨 **Modern UI** | Dark-mode glassmorphism web interface |
| 📊 **Live Stats** | Real-time analytics dashboard |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or newer
- pip

### 1. Setup (install + train — run once)
```bash
python setup.py
```

### 2. Start the server
```bash
python app.py
```

### 3. Open the UI
Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## 📂 Project Structure

```
ai agent/
├── data/
│   ├── notifications_dataset.py   # Synthetic 10k dataset generator
│   └── notifications.csv          # Generated dataset (after setup)
├── models/
│   ├── tfidf_vectorizer.pkl       # Trained TF-IDF vectorizer
│   ├── classifier.pkl             # Best ML classifier
│   ├── label_encoder.pkl          # Label encoder
│   └── model_info.pkl             # Model metadata
├── preprocess.py                  # Phase 3: NLP preprocessing pipeline
├── train_model.py                 # Phase 5: Model training & evaluation
├── explainer.py                   # Phase 6: Explanation generation
├── agent.py                       # Phase 7: Core AI agent logic
├── app.py                         # Phase 9: Flask REST API
├── index.html                     # Phase 10: Web UI
├── setup.py                       # One-click setup script
├── requirements.txt               # Python dependencies
└── README.md
```

---

## 🔌 API Reference

### `POST /api/analyze`
Analyze a single notification.

**Request:**
```json
{ "text": "Your OTP is 456782. Valid for 10 minutes." }
```

**Response:**
```json
{
  "status": "success",
  "label": "important",
  "importance": "HIGH",
  "category": "OTP",
  "icon": "🔐",
  "explanation": "One-Time Password received. Never share this code.",
  "detail": "Code: 456782 (do NOT share)",
  "confidence": 0.9821,
  "action_required": true,
  "processing_time_ms": 12.4
}
```

### `POST /api/analyze/batch`
Analyze up to 100 notifications at once.

**Request:**
```json
{ "messages": ["msg1", "msg2", "..."] }
```

### `GET /api/health`
Check if the model is loaded and the API is running.

### `GET /api/stats`
Get live analysis statistics.

---

## 📊 Notification Categories

| Category | Importance | Example |
|----------|-----------|---------|
| OTP | 🔴 HIGH | "Your OTP is 456782" |
| BANK_TXN | 🔴 HIGH | "Rs.5000 debited from account" |
| SECURITY | 🔴 HIGH | "New login detected" |
| EMERGENCY | 🔴 HIGH | "Server down! Critical failure" |
| HEALTH | 🔴 HIGH | "Doctor appointment tomorrow" |
| WORK | 🟡 MEDIUM | "Meeting at 3 PM" |
| DELIVERY | 🟡 MEDIUM | "Order shipped, arrives today" |
| PROMOTION | 🟢 LOW | "70% OFF sale today!" |
| SOCIAL | 🟢 LOW | "Liked your photo" |
| NEWS | 🟢 LOW | "Breaking: top headlines" |

---

## 🧪 Testing the Agent Directly

```bash
# Run the agent in demo mode
python agent.py

# Test preprocessing pipeline
python preprocess.py

# Test explanation engine
python explainer.py
```

---

## 📱 Android Integration (Phase 8)

To read notifications from an Android device:

1. Create a `NotificationListenerService` in Android Studio
2. Send notification text to this API via HTTP POST to `/api/analyze`
3. Display the AI response in your app UI

See `android_integration_guide.md` for detailed steps.

---

## 🏗️ Architecture

```
Smartphone Notification
        ↓
[NotificationListenerService] (Android)
        ↓
POST /api/analyze  (Flask REST API)
        ↓
NLP Preprocessing  (preprocess.py)
        ↓
TF-IDF Vectorization
        ↓
ML Classifier (Logistic Regression / Random Forest)
        ↓
Category Detection + Explanation Engine
        ↓
JSON Response → Web UI / Android App
```

---

## 🔧 Configuration

Set environment variables to customize:

```bash
PORT=5000       # API server port (default: 5000)
```

---

*Built with ❤️ using Python, Flask, NLTK, scikit-learn*
