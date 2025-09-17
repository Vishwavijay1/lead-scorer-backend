import pandas as pd
from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv

load_dotenv()
from scoring_logic import run_scoring_pipeline

app = Flask(__name__)

offer_data = {}
leads_data = []
results_data = []

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

@app.route('/score', methods=['POST'])
def score_leads():
    global results_data
    if not offer_data:
        return jsonify({"error": "Offer data not set. Please POST to /offer first."}), 400
    if not leads_data:
        return jsonify({"error": "Leads not uploaded. Please POST to /leads/upload first."}), 400
        
    try:
        results_data = run_scoring_pipeline(leads_data, offer_data)
        return jsonify({
            "message": "Scoring complete. GET /results to see the output."
        }), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred during scoring: {e}"}), 500

@app.route('/results', methods=['GET'])
def get_results():
    if not results_data:
        return jsonify({"message": "No results available. Run scoring via POST /score first."}), 404
        
    return jsonify(results_data), 200


@app.route('/results/export', methods=['GET'])
def export_results():
    if not results_data:
        return jsonify({"message": "No results available to export."}), 404
        
    try:
        df = pd.DataFrame(results_data)
        
        csv_data = df.to_csv(index=False)
        
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=scored_leads.csv"})
    except Exception as e:
        return jsonify({"error": f"Failed to export CSV: {e}"}), 500



if __name__ == '__main__':
    app.run(debug=True, port=5001, use_reloader=False)