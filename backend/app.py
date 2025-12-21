from flask import Flask, request, jsonify
from flask_cors import CORS
from sandbox.validator import validate_code
from sandbox.executor import safe_execute
from sandbox.metrics import loop_depth_hint
from llm.reviewer import llm_review

app = Flask(__name__)

CORS(app)

@app.route("/review", methods=["POST"])
def review_code():
    data = request.get_json(force=True)
    code = data.get("code", "")

    allowed, reason = validate_code(code)

    if not allowed:
        return jsonify({
            "allowed": False,
            "reason": reason
        })

    execution_result = safe_execute(code)
    execution_result["loop_depth_hint"] = loop_depth_hint(code)

    review = llm_review(code)

    return jsonify({
        "allowed": True,
        "execution": execution_result,
        "llm_review": review
    })


if __name__ == "__main__":
    app.run(debug=True)
