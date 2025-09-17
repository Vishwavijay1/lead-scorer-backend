# tests/test_scoring_logic.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scoring_logic import calculate_rule_score


mock_offer = {
    "ideal_use_cases": ["B2B SaaS", "Enterprise Software"]
}

def test_decision_maker_role():
    lead = {"role": "VP of Sales", "industry": "B2B SaaS", "name": "test", "company": "test", "location": "test", "linkedin_bio": "test"}
    assert calculate_rule_score(lead, mock_offer) == 50 # 20 (role) + 20 (industry) + 10 (complete)

def test_influencer_role():
    lead = {"role": "Senior Marketing Manager", "industry": "B2B SaaS", "name": "test", "company": "test", "location": "test", "linkedin_bio": "test"}
    assert calculate_rule_score(lead, mock_offer) == 40 # 10 (role) + 20 (industry) + 10 (complete)

def test_no_role_match():
    lead = {"role": "Software Engineer", "industry": "B2B SaaS", "name": "test", "company": "test", "location": "test", "linkedin_bio": "test"}
    assert calculate_rule_score(lead, mock_offer) == 30 # 0 (role) + 20 (industry) + 10 (complete)

def test_no_industry_match():
    lead = {"role": "Head of Growth", "industry": "Retail", "name": "test", "company": "test", "location": "test", "linkedin_bio": "test"}
    assert calculate_rule_score(lead, mock_offer) == 30 # 20 (role) + 0 (industry) + 10 (complete)

def test_incomplete_data():
    lead = {"role": "VP of Sales", "industry": "B2B SaaS", "name": "test", "company": "", "location": "test", "linkedin_bio": "test"}
    assert calculate_rule_score(lead, mock_offer) == 40 # 20 (role) + 20 (industry) + 0 (complete)