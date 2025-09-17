# app.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    """A simple endpoint to check if the server is running."""
    return jsonify({"status": "Server is running"}), 200

# This part allows us to run the app directly from the terminal
if __name__ == '__main__':
    app.run(debug=True, port=5001)