from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/ping")
def ping():
    """Health-check endpoint."""
    return jsonify(ok=True)


if __name__ == "__main__":
    # Run with:  python backend/app.py
    app.run(host="0.0.0.0", port=8000, debug=True)