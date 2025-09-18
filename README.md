# AI Lead Scoring Backend

This backend service accepts product information and a list of sales leads, then scores each lead's buying intent on a scale of 0-100. It uses a hybrid approach, combining a deterministic rule-based layer for objective data points and an AI-powered layer using Google Gemini for nuanced, contextual analysis.

**Live API Base URL:** `https://lead-scorer-backend.onrender.com`

---
## Tech Stack

- **Framework**: Python (Flask)
- **AI Model**: Google Gemini Pro (`gemini-1.5-flash`)
- **Libraries**: Pandas, google-generativeai, python-dotenv
- **Deployment**: Render

---
## Setup & Run Locally

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Vishwavijay1/lead-scorer-backend]
    cd lead-scorer-backend
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a file named `.env` in the root directory and add your Google API key:
    ```
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    ```

5.  **Run the application:**
    ```bash
    python app.py
    ```
    The server will start on `http://127.0.0.1:5001`.

---
## API Usage

### 1. Set the Product/Offer
Defines the product you are scoring leads against.

**Endpoint:** `POST /offer`

**Body (JSON):**
```json
{
  "name": "AI Outreach Automation",
  "value_props": ["24/7 outreach", "6x more meetings"],
  "ideal_use_cases": ["B2B SaaS mid-market"]
}
```
**cURL Example:**
```bash
curl -X POST [http://127.0.0.1:5001/offer](http://127.0.0.1:5001/offer) \
-H "Content-Type: application/json" \
-d '{
  "name": "AI Outreach Automation",
  "value_props": ["24/7 outreach", "6x more meetings"],
  "ideal_use_cases": ["B2B SaaS mid-market"]
}'
```

### 2. Upload Leads CSV
Uploads a CSV file of leads to be scored.

**Endpoint:** `POST /leads/upload`

**Body (form-data):**
- Key: `file`
- Value: Your `leads.csv` file. The CSV must have the columns: `name,role,company,industry,location,linkedin_bio`.

**cURL Example:**
```bash
curl -X POST [http://127.0.0.1:5001/leads/upload](http://127.0.0.1:5001/leads/upload) \
-F "file=@/path/to/your/leads.csv"
```

### 3. Trigger Scoring
Initiates the scoring pipeline for the uploaded leads and offer.

**Endpoint:** `POST /score`

**cURL Example:**
```bash
curl -X POST [http://127.0.0.1:5001/score](http://127.0.0.1:5001/score)
```

### 4. Get Results
Retrieves the scored leads as a JSON array.

**Endpoint:** `GET /results`

**cURL Example:**
```bash
curl [http://127.0.0.1:5001/results](http://127.0.0.1:5001/results)
```
**Example Response:**
```json
[
  {
    "company": "FlowMetrics",
    "intent": "High",
    "name": "Ava Patel",
    "reasoning": "As Head of Growth in B2B SaaS, Ava is a key decision-maker in the ideal customer profile, making her a high-intent lead.",
    "role": "Head of Growth",
    "score": 90
  }
]
```

---
## Scoring Logic Explained

The final score (0-100) for each lead is a sum of two components:

### Rule Layer (Max 50 points)
This layer provides a baseline score using objective, deterministic rules.
- **Role Relevance (20 pts):** Uses regular expressions to match job titles.
  - `+20` for decision-makers (e.g., "VP", "Vice President", "Director", "C-level").
  - `+10` for influencers (e.g., "Manager", "Senior", "Lead").
- **Industry Match (20 pts):**
  - `+20` if the lead's `industry` string contains any of the `ideal_use_cases` from the offer.
- **Data Completeness (10 pts):**
  - `+10` if all required fields in the lead's profile are present.

### AI Layer (Max 50 points)
This layer provides nuanced, context-aware scoring by sending lead and offer details to the Google Gemini AI.
- The AI is prompted to return a structured JSON object classifying intent as `High`, `Medium`, or `Low` and providing a one-sentence justification.
- The intent is mapped to points:
  - **High**: 50 points
  - **Medium**: 30 points
  - **Low**: 10 points