import os
import cv2
import easyocr
from flask import request, jsonify

reader = easyocr.Reader(["en"], gpu=False)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def register_scan_api(app, engine):

    @app.route("/scan", methods=["POST"])
    def scan():

        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        image = request.files["image"]

        filepath = os.path.join(UPLOAD_FOLDER, image.filename)

        image.save(filepath)

        results = reader.readtext(filepath)

        question = " ".join([r[1] for r in results]).strip()
        question = " ".join(
    text
    for (_, text, conf) in results
    if conf > 0.30
).strip()
        if question == "":
            return jsonify({
                "status": "error",
                "message": "Couldn't detect any text."
            })

        hint_result = engine.get_hint(question)

        if not hint_result["found"]:
            return jsonify({
                "status": "not_found",
                "question": question,
                "message": "Question detected but no matching hint found."
            })

        return jsonify({
            "status": "success",
            "question": question,
            "topic": hint_result["topic"],
            "hints": hint_result["hints"]
        })
