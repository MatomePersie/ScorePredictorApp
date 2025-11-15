from fpdf import FPDF
from datetime import datetime
from football_predictor import fetch_today_matches, predict_match

# Fetch today's matches
matches_df = fetch_today_matches()

if matches_df.empty:
    print("No matches available today to generate report.")
    exit()

# Initialize PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, f"Soccer Predictions Report - {datetime.now().strftime('%Y-%m-%d')}", ln=True, align="C")
pdf.ln(10)

# Loop over matches
for _, row in matches_df.iterrows():
    result = predict_match(row["home_id"], row["away_id"], row["league_id"])

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, f"{row['home_name']} vs {row['away_name']} [{row['status']}]", ln=True)

    if "error" in result:
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 6, f"Prediction: {result['error']}")
    else:
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 6, f"Predicted Score: {result['predicted_score']}", ln=True)
        pdf.cell(0, 6, f"Expected Goals: {result['expected_goals'][0]} - {result['expected_goals'][1]}", ln=True)
        pdf.cell(0, 6, f"Outcome: {result['outcome']}", ln=True)
        pdf.cell(0, 6, "Win/Draw/Win Probabilities:", ln=True)
        pdf.cell(10)
        pdf.cell(0, 6, f"Home: {result['wdw']['home']}%, Draw: {result['wdw']['draw']}%, Away: {result['wdw']['away']}%", ln=True)
        pdf.cell(0, 6, "Top 3 Scorelines:", ln=True)
        for s, p in result['top3']:
            pdf.cell(10)
            pdf.cell(0, 6, f"{s} => {p}%", ln=True)
    pdf.ln(5)

# Save PDF
filename = f"soccer_predictions_{datetime.now().strftime('%Y%m%d')}.pdf"
pdf.output(filename)
print(f"PDF report generated: {filename}")
