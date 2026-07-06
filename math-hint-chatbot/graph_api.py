from flask import request, jsonify

def register_graph_api(app, graph_engine):

    @app.route("/graph", methods=["POST"])
    def graph():

        data = request.get_json()

        if not data or "equation" not in data:
            return jsonify({
                "status": "error",
                "message": "Equation is required."
            }), 400

        equation = data["equation"]

        try:

            result = graph_engine.analyze(equation)

            return jsonify(result)

        except Exception as e:

            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
