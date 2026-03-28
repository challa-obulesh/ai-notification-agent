"""
Updated app.py — supports PORT env variable for cloud deployment
and sets PYTHONIOENCODING for Windows compatibility.
"""

import os
import sys
import time
import logging
from datetime import datetime, timezone
from collections import defaultdict

# Fix Windows encoding for emoji in logs if needed
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from agent import get_agent

# ─── App setup ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)

# ─── In-memory analytics ─────────────────────────────────────────────────────
stats = {
    "total_analyzed": 0,
    "important":      0,
    "not_important":  0,
    "categories":     defaultdict(int),
    "start_time":     datetime.now(timezone.utc).isoformat(),
    "recent":         [],
}
MAX_RECENT = 50
MAX_BATCH  = 100


def _update_stats(result: dict):
    stats["total_analyzed"] += 1
    if result.get("label") == "important":
        stats["important"] += 1
    else:
        stats["not_important"] += 1
    cat = result.get("category", "UNKNOWN")
    stats["categories"][cat] += 1
    entry = {
        "message":    result.get("original_message", "")[:80],
        "label":      result.get("label"),
        "importance": result.get("importance"),
        "category":   cat,
        "icon":       result.get("icon"),
        "timestamp":  datetime.now(timezone.utc).isoformat(),
    }
    stats["recent"].insert(0, entry)
    if len(stats["recent"]) > MAX_RECENT:
        stats["recent"].pop()


# ─── Routes ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/health", methods=["GET"])
def health():
    agent = get_agent()
    return jsonify({
        "status":       "ok",
        "model_loaded": agent._loaded,
        "model_name":   agent.model_name,
        "uptime_since": stats["start_time"],
    })

@app.route("/api/stats", methods=["GET"])
def get_stats():
    return jsonify({
        "total_analyzed": stats["total_analyzed"],
        "important":      stats["important"],
        "not_important":  stats["not_important"],
        "categories":     dict(stats["categories"]),
        "recent":         stats["recent"][:10],
    })

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"status": "error", "message": "Missing 'text' field."}), 400
    message = str(data["text"]).strip()
    if not message:
        return jsonify({"status": "error", "message": "Empty notification."}), 400
    result = get_agent().analyze(message)
    _update_stats(result)
    return jsonify(result)

@app.route("/api/analyze/batch", methods=["POST"])
def analyze_batch():
    data = request.get_json(silent=True)
    if not data or "messages" not in data:
        return jsonify({"status": "error", "message": "Missing 'messages' list."}), 400
    messages = data["messages"]
    if not isinstance(messages, list):
        return jsonify({"status": "error", "message": "'messages' must be a list."}), 400
    if len(messages) > MAX_BATCH:
        return jsonify({"status": "error", "message": f"Max batch size is {MAX_BATCH}."}), 400
    agent = get_agent()
    results = [agent.analyze(str(m).strip()) for m in messages]
    for r in results:
        _update_stats(r)
    return jsonify({"status": "success", "count": len(results), "results": results})


# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"AI Notification Agent API starting on http://localhost:{port}")
    get_agent()   # pre-load model
    logger.info("Agent ready!")
    app.run(host="0.0.0.0", port=port, debug=False)
