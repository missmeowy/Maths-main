from flask import request, jsonify
import os
import uuid


def register_revision_api(app, revision_engine):

    @app.route("/revision", methods=["POST"])
    def revision():

        if "file" not in request.files:

            return jsonify({

                "status": "error",

                "message": "No file uploaded."

            }), 400

        file = request.files["file"]

        if file.filename == "":

            return jsonify({

                "status": "error",

                "message": "No file selected."

            }), 400

        extension = os.path.splitext(file.filename)[1]

        filename = f"{uuid.uuid4().hex}{extension}"

        filepath = os.path.join("uploads", filename)

        file.save(filepath)

        try:

            result = revision_engine.analyze(filepath)

            os.remove(filepath)

            return jsonify(result)

        except Exception as e:

            if os.path.exists(filepath):

                os.remove(filepath)

            return jsonify({

                "status": "error",

                "message": str(e)

            }), 500
            
