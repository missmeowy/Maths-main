from flask import request, jsonify
import uuid


def register_practice_api(app, practice_engine):

    sessions = {}

    # -----------------------------------
    # New Question
    # -----------------------------------

    @app.route("/practice/question", methods=["POST"])
    def get_question():

        data = request.get_json() or {}

        subject = data.get("subject")

        difficulty = data.get("difficulty")

        session_id = str(uuid.uuid4())

        session = practice_engine.create_session(

            subject,

            difficulty

        )

        sessions[session_id] = session

        question = session["question"]

        return jsonify({

            "status": "success",

            "session_id": session_id,

            "question": question["question"],

            "topic": question["topic"],

            "difficulty": question["difficulty"]

        })

    # -----------------------------------
    # Get Hint
    # -----------------------------------

    @app.route("/practice/hint", methods=["POST"])
    def get_hint():

        data = request.get_json()

        session_id = data.get("session_id")

        if session_id not in sessions:

            return jsonify({

                "status": "error",

                "message": "Session not found."

            }), 404

        result = practice_engine.get_hint(

            sessions[session_id]

        )

        return jsonify(result)

    # -----------------------------------
    # Check Answer
    # -----------------------------------

    @app.route("/practice/check", methods=["POST"])
    def check_answer():

        data = request.get_json()

        session_id = data.get("session_id")

        answer = data.get("answer", "")

        if session_id not in sessions:

            return jsonify({

                "status": "error",

                "message": "Session expired."

            }), 404

        result = practice_engine.generate_feedback(

            sessions[session_id],

            answer

        )

        return jsonify(result)

    # -----------------------------------
    # Next Question
    # -----------------------------------

    @app.route("/practice/next", methods=["POST"])
    def next_question():

        data = request.get_json()

        session_id = data.get("session_id")

        subject = data.get("subject")

        difficulty = data.get("difficulty")

        if session_id not in sessions:

            return jsonify({

                "status": "error",

                "message": "Session expired."

            }), 404

        sessions[session_id] = practice_engine.next_question(

            sessions[session_id],

            subject,

            difficulty

        )

        question = sessions[session_id]["question"]

        return jsonify({

            "status": "success",

            "question": question["question"],

            "topic": question["topic"],

            "difficulty": question["difficulty"]

        })

    # -----------------------------------
    # Statistics
    # -----------------------------------

    @app.route("/practice/stats", methods=["POST"])
    def stats():

        data = request.get_json()

        session_id = data.get("session_id")

        if session_id not in sessions:

            return jsonify({

                "status": "error"

            })

        return jsonify(

            practice_engine.get_statistics(

                sessions[session_id]

            )

        )
