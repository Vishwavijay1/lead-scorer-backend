# app.py

import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

offer_data = {}
leads_data = []

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Server is running"}), 200


@app.route('/offer', methods=['POST'])
def set_offer():
    
    global offer_data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    if 'name' not in data or 'value_props' not in data or 'ideal_use_cases' not in data:
        return jsonify({"error": "Missing required fields in offer data"}), 400
        
    offer_data = data
    return jsonify({"message": "Offer data received successfully", "offer": offer_data}), 201

@app.route('/leads/upload', methods=['POST'])
def upload_leads():
 
    global leads_data
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and file.filename.endswith('.csv'):
        try:
            df = pd.read_csv(file.stream)
            df.fillna('', inplace=True)
            leads_data = df.to_dict('records')
            return jsonify({
                "message": f"{len(leads_data)} leads uploaded successfully"
            }), 201
        except Exception as e:
            return jsonify({"error": f"Failed to process CSV file: {e}"}), 500
    
    return jsonify({"error": "Invalid file type, please upload a CSV"}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5001)