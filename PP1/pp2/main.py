import random
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# === CONFIG ===
CREDENTIALS_FILE = "credentials.json"
SHEET_ID = "1BosXISXJ7rkUr57W3zy8DA7FQJkmDUqt9Fif95AOJq0"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# === AUTHENTICATION ===
# creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
# client = gspread.authorize(creds)
# sheet = client.open_by_key(SHEET_ID).sheet1


# === PROCUREMENT QUESTIONS ===
# QUESTIONS = [
#     "Is your company registered with CAC?",
#     "Does your company have a valid Tax Identification Number (TIN)?",
#     "Has your company completed road construction projects in the past?",
#     "Do you have qualified civil engineers on staff?",
#     "Does your company own the required road construction equipment?",
#     "Can your company provide a performance bond?",
#     "Do you have audited financial statements for the last 3 years?",
#     "Has your company ever abandoned a government contract?",
#     "Has your company ever had legal disputes with the government?",
# ]

# Questions 1–7 must be YES
# Questions 8–9 must be NO

SCORING_RULES = {
    "Is your company registered with CAC?": 20,
    "Does your company have a valid Tax Identification Number (TIN)?": 15,
    "Has your company completed road construction projects in the past?": 25,
    "Do you have qualified civil engineers on staff?": 20,
    "Does your company own the required road construction equipment?": 20,
    "Can your company provide a performance bond?": 15,
    "Do you have audited financial statements for the last 3 years?": 15,
    "Has your company ever abandoned a government contract?": -30,
    "Has your company ever had legal disputes with the government?": -20
}

QUESTIONS = list(SCORING_RULES.keys())

# def check_company_responses(responses: list[str]) -> bool:
#     """
#     Takes a list of Yes/No responses (in order) and
#     returns True if company is eligible, False otherwise.
#     """
#     must_be_yes = responses[0:7]
#     must_be_no = responses[7:9]
#
#     # Check Yes requirements
#     if not all(ans.strip().lower() == "yes" for ans in must_be_yes):
#         return False
#
#     # Check No requirements
#     if not all(ans.strip().lower() == "no" for ans in must_be_no):
#         return False
#
#     return True
#
#
# def run_simulation():
#     """Run eligibility test with fake sample answers"""
#     sample_company = [
#         "Yes", "Yes", "Yes", "Yes", "Yes", "Yes", "Yes", "No", "No"
#     ]
#     result = check_company_responses(sample_company)
#     print("🧪 Simulation result:", "✅ Eligible" if result else "❌ Not Eligible")
#
#
# def run_real():
#     """Run eligibility test using actual Google Form responses"""
#     rows = sheet.get_all_values()
#     headers = rows[0]
#     responses = rows[1:]  # skip header row
#
#     for i, row in enumerate(responses, start=1):
#         # Extract only the Yes/No columns
#         company_answers = row[1:10]  # adjust if your sheet structure changes
#         eligible = check_company_responses(company_answers)
#         print(f"Company {i}: {'✅ Eligible' if eligible else '❌ Not Eligible'}")
#
#
# if __name__ == "__main__":
#     print("Choose mode:")
#     print("1. Simulation mode")
#     print("2. Real mode (Google Form responses)")
#     choice = input("Enter 1 or 2: ")
#
#     if choice == "1":
#         run_simulation()
#     elif choice == "2":
#         run_real()
#     else:
#         print("Invalid choice.")

def score_proposal(proposal):
    score = 0
    for q, ans in proposal.items():
        if ans == "Yes":
            score += SCORING_RULES.get(q, 0)
        elif ans == "No" and SCORING_RULES.get(q, 0) < 0:
            # If negative question and answer is No, it's a good thing
            score += abs(SCORING_RULES[q])
    return score

def simulation_mode():
    proposals = []
    for i in range(500):  # generate 500 random proposals
        proposal = {q: random.choice(["Yes", "No"]) for q in QUESTIONS}
        score_val = score_proposal(proposal)
        proposals.append({"Proposal ID": f"Sim-{i+1}", **proposal, "Score": score_val})

    df = pd.DataFrame(proposals)
    df = df.sort_values(by="Score", ascending=False)
    df.to_csv("simulation_results.csv", index=False)
    print("🧪 Simulation completed! Top 10 proposals:")
    print(df.head(10))

def real_mode():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    rows = sheet.get_all_records()

    proposals = []
    for i, row in enumerate(rows):
        proposal = {q: row.get(q, "No") for q in QUESTIONS}
        score_val = score_proposal(proposal)
        proposals.append({"Proposal ID": f"Real-{i+1}", **proposal, "Score": score_val})

    df = pd.DataFrame(proposals)
    df = df.sort_values(by="Score", ascending=False)
    df.to_csv("real_results.csv", index=False)
    print("📊 Real data processed! Top 10 proposals:")
    print(df.head(10))

if __name__ == "__main__":
    print("Choose mode:")
    print("1. Simulation mode")
    print("2. Real mode (Google Form responses)")
    choice = input("Enter 1 or 2: ")

    if choice == "1":
        simulation_mode()
    elif choice == "2":
        real_mode()
    else:
        print("❌ Invalid choice.")