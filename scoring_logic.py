import os
import json
import re
import time
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def calculate_rule_score(lead, offer):
    score = 0
    role = lead.get('role', '')

    decision_maker_pattern = r'\b(vp|vice president|head|director|founder|c.o)\b'
    influencer_pattern = r'\b(manager|lead|senior|principal|architect)\b'

    if re.search(decision_maker_pattern, role, re.IGNORECASE):
        score += 20
    elif re.search(influencer_pattern, role, re.IGNORECASE):
        score += 10
        
    lead_industry = lead.get('industry', '').lower()
    ideal_use_cases = [uc.lower() for uc in offer.get('ideal_use_cases', [])]
    if any(uc in lead_industry for uc in ideal_use_cases):
        score += 20
    
    required_fields = ['name', 'role', 'company', 'industry', 'location', 'linkedin_bio']
    if all(lead.get(field) for field in required_fields):
        score += 10
        
    return score

def get_ai_score_and_reasoning(lead, offer):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    **Objective:** Analyze a sales lead and classify their buying intent.

    **Context:**
    - Product Name: "{offer['name']}"
    - Product Value: {', '.join(offer['value_props'])}
    - Target Customer: {', '.join(offer['ideal_use_cases'])}
    - Lead Role: {lead['role']}
    - Lead Bio: "{lead['linkedin_bio']}"

    **Task:**
    Respond with ONLY a valid JSON object. Do not add any text before or after the JSON.
    The JSON object must have the following structure:
    {{
      "intent": "High" | "Medium" | "Low",
      "reasoning": "A one-sentence explanation for the classification."
    }}
    """

    try:
        generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
        response = model.generate_content(prompt, generation_config=generation_config)
        
        result_json = json.loads(response.text)
        intent_str = result_json.get("intent", "Low")
        reasoning = result_json.get("reasoning", "Could not parse AI reasoning.")

        intent_map = {"High": 50, "Medium": 30, "Low": 10}
        ai_points = intent_map.get(intent_str, 10)
        
        return {
            "points": ai_points, 
            "intent": intent_str, 
            "reasoning": reasoning
        }

    except (json.JSONDecodeError, Exception) as e:
        print(f"Error processing AI JSON response: {e}")
        return {
            "points": 10, 
            "intent": "Low", 
            "reasoning": "An error occurred during AI analysis."
        }

def run_scoring_pipeline(leads, offer):
    scored_results = []
    
    for lead in leads:
        rule_score = calculate_rule_score(lead, offer)
        ai_result = get_ai_score_and_reasoning(lead, offer)
        
        final_score = rule_score + ai_result["points"]
        
        scored_results.append({
            "name": lead.get('name', ''),
            "role": lead.get('role', ''),
            "company": lead.get('company', ''),
            "intent": ai_result["intent"],
            "score": final_score,
            "reasoning": ai_result["reasoning"]
        })
        
        time.sleep(5) 
        
    return scored_results