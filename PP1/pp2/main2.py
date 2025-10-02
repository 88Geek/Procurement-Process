import gspread
from google.oauth2.service_account import Credentials
import random
import csv
import datetime


# Google Sheets Setup

CREDENTIALS_FILE= "credentials.json"
SCOPES= ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Connect to Google Sheets
creds= Credentials.from_service_account_file(CREDENTIALS_FILE, scopes= SCOPES)
client= gspread.authorize(creds)

SHEET_ID= "1BosXISXJ7rkUr57W3zy8DA7FQJkmDUqt9Fif95AOJq0"
WORKSHEET= "Form Responses 1"


# RFP & TOR Criteria

criteria= {
    "budget_min": 50000,
    "budget_max": 150000,
    "timeline_max": 12,
    "experience_min": 3,
    "compliance_keywords": ["ISO", "GDPR", "CAC", "TIN"]
}

weights= {
    "budget": 0.4,
    "timeline": 0.15,
    "experience": 0.25,
    "compliance": 0.2,
    "performance": 0.2,
    "documents": 0.3
}


# Proposal Generator (Simulation Mode)

def generate_proposal():
    return {
        "company": f"Vendor_{random.randint(100,999)}",
        "budget": random.randint(40000, 180000),
        "timeline": random.randint(6, 18),
        "experience": random.randint(1, 10),
        "compliance": random.choice(["ISO", "GDPR", "CAC", "TIN", "None"]),
        "past_projects_success_rate": round(random.uniform(0.5, 1.0), 2),
        "abandoned_contract": random.choice([True, False]),
        "documents": {
            "cac": random.choice([True, False]),
            "tin": random.choice([True, False]),
            "financials": random.choice([True, False])
        }
    }


# Evaluate Proposals

def evaluate_proposal(proposal, criteria_, weights_):
    if proposal["abandoned_contract"]:
        return -1
    if not proposal["documents"]["cac"] or not proposal["documents"]["tin"]:
        return -1

    score = 0
    if criteria_["budget_min"] <= proposal["budget"] <= criteria_["budget_max"]:
        score += weights_["budget"]
    if proposal["timeline"] <= criteria_["timeline_max"]:
        score += weights_["timeline"]
    if proposal["experience"] >= criteria_["experience_min"]:
        score += weights_["experience"]
    if any(k in proposal["compliance"] for k in criteria_["compliance_keywords"]):
        score += weights_["compliance"]

    score += proposal["past_projects_success_rate"] * weights_["performance"]

    if all(proposal["documents"].values()):
        score += weights_["documents"]

    return score


# Load Proposals from Google Sheets

def load_from_google():
    sheet= client.open_by_key(SHEET_ID).worksheet(WORKSHEET)
    rows= sheet.get_all_records()

    proposals= []
    for row in rows:
        proposals.append({
            "company": row.get("Company Name", f"Vendor_{random.randint(100,999)}"),
            "budget": int(row.get("Proposed Budget (₦)", 0)),
            "timeline": int(row.get("Proposed Timeline (months)", 0)),
            "experience": int(row.get("Years of Experience", 0)),
            "compliance": row.get("Compliance Certification", "None"),
            "past_projects_success_rate": float(row.get("Past Performance Score", 0.7)),
            "abandoned_contract": row.get("Has your company ever abandoned a government contract?") == "Yes",
            "documents": {
                "cac": row.get("Is your company registered with CAC?") == "Yes",
                "tin": row.get("Does your company have a valid Tax Identification Number (TIN)?") == "Yes",
                "financials": row.get("Do you have audited financial statements for the last 3 years?") == "Yes"
            }
        })
    return proposals


# Run Evaluation

def run_evaluation(mode= "simulation", n=500):
    proposals= []

    if mode == "simulation":
        proposals= [generate_proposal() for _ in range(n)]
    elif mode == "real":
        proposals= load_from_google()

    results= []
    for p in proposals:
        score= evaluate_proposal(p, criteria, weights)
        results.append({
            "company": p["company"],
            "score": score,
            "budget": p["budget"],
            "timeline": p["timeline"],
            "experience": p["experience"],
            "compliance": p["compliance"],
            "performance": p["past_projects_success_rate"],
            "docs": p["documents"],
            "abandoned": p["abandoned_contract"]
        })

    qualified= [r_ for r_ in results if r_["score"] != -1]
    ranked_= sorted(qualified, key= lambda x: (-x["score"], x["budget"]))
    shortlist_= ranked_[:3]

    save_results(results, mode)
    # save_results(ranked_, mode)
    return ranked_, shortlist_


# Step 7: Save Results

def save_results(results, mode):
    filename= f"procurement_results_{mode}_{datetime.date.today()}.csv"
    with open(filename, mode= "w", newline="") as f:
        writer= csv.writer(f)
        writer.writerow(["Company", "Score", "Budget", "Timeline", "Experience", "Compliance", "Performance", "Docs",
                         "Abandoned"])
        for r__ in results:
            writer.writerow([r__["company"], r__["score"], r__["budget"], r__["timeline"], r__["experience"],
                             r__["compliance"], r__["performance"], r__["docs"], r__["abandoned"]])
    print(f"📊 Results exported to {filename}")


# Step 8: Main Program

if __name__ == "__main__":
    print("Choose mode:")
    print("1. Simulation mode")
    print("2. Real mode (Google Form responses)")
    choice= input("Enter 1 or 2: ")

    if choice == "1":
        ranked, shortlist= run_evaluation("simulation", 500)
    else:
        ranked, shortlist= run_evaluation("real")

    print("\n🏆 Final Ranking:")
    for r in ranked:
        print(f"{r['company']} | Score: {r['score']:.2f} | Budget: {r['budget']} | Timeline: {r['timeline']} months")

    print("\n✅ Shortlist (Top 3):")
    for r in shortlist:
        print(f"{r['company']} | Score: {r['score']:.2f}")
