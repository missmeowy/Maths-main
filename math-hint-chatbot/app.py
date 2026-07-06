from flask import Flask, request, jsonify
from hint_engine import HintEngine
from scan_api import register_scan_api
from graph_engine import GraphEngine
from graph_api import register_graph_api 





app = Flask(__name__)




graph_engine = GraphEngine()

register_graph_api(app, graph_engine)
# Store hint sessions
session_hints = {}

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


print("🚀 Loading Hint Engine...")
engine = HintEngine(csv_path='data/maths_only.csv')
print("✅ Engine ready!")

# Register Scan API
register_scan_api(app, engine)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "message": "Math Hint Chatbot Backend is live!"
    })


@app.route("/ask", methods=["POST"])
def ask_question():

    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({"error": "Question field required"}), 400

    user_question = data["question"].strip()

    session_id = data.get("session_id", "default")

    hint_level = data.get("hint_level", 1)

    if not user_question:
        return jsonify({"error": "Question cannot be empty"}), 400

    result = engine.get_hint(user_question)

    if not result["found"]:
        return jsonify({
            "status": "not_found",
            "message": result["message"],
            "hints": [],
            "confidence": "0%"
        })

    session_hints[session_id] = {
        "question": user_question,
        "all_hints": result["hints"],
        "current_level": hint_level
    }

    max_level = min(hint_level, len(result["hints"]))

    return jsonify({
        "status": "success",
        "question_understood": result["matched_question"],
        "topic": result["topic"],
        "hints": result["hints"][:max_level],
        "total_hints_available": len(result["hints"]),
        "hint_level": max_level,
        "confidence": f"{round(result['score'] * 100, 1)}%",
        "message": "No direct answers here — work through the hints and give it a try! 😊"
    })


@app.route("/next-hint", methods=["POST"])
def next_hint():

    data = request.get_json()

    session_id = data.get("session_id", "default")

    if session_id not in session_hints:
        return jsonify({
            "error": "Please ask a question first!"
        }), 400

    session = session_hints[session_id]

    current_level = session["current_level"]

    all_hints = session["all_hints"]

    if current_level >= len(all_hints):

        return jsonify({
            "status": "max_hints_reached",
            "message": "All hints have been provided! Now give it your best shot — you've got this! 💪",
            "hints": all_hints
        })

    next_level = current_level + 1

    session_hints[session_id]["current_level"] = next_level

    return jsonify({
        "status": "success",
        "hints": all_hints[:next_level],
        "hint_level": next_level,
        "total_hints_available": len(all_hints)
    })


@app.route("/topics", methods=["GET"])
def get_topics():

    topics = engine.df["topic"].dropna().unique().tolist()

    return jsonify({
        "topics": topics
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
