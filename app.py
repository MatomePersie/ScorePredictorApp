from flask import Flask, render_template, send_file
from football_predictor import fetch_today_matches, predict_match
from fpdf import FPDF
import io

app = Flask(__name__)

# -----------------------------------------------------
# HOME ROUTE
# -----------------------------------------------------
@app.route("/")
def home():
    df_today = fetch_today_matches()

    matches = []
    leagues_dict = {}

    if not df_today.empty:
        for _, m in df_today.iterrows():
            # Run prediction
            result = predict_match(m["home_id"], m["away_id"], m["league_id"])

            # League name handling
            league_name = m.get("league_name", f"League {m['league_id']}")
            leagues_dict[m["league_id"]] = league_name

            matches.append({
                "home_name": m["home_name"],
                "away_name": m["away_name"],
                "league_id": m["league_id"],
                "league_name": league_name,
                "home_logo": f"https://crests.football-data.org/{m['home_id']}.svg",
                "away_logo": f"https://crests.football-data.org/{m['away_id']}.svg",
                "predicted_score": result.get("predicted_score") if "error" not in result else result["error"],
                "expected_goals": result.get("expected_goals") if "error" not in result else None,
                "outcome": result.get("outcome") if "error" not in result else None,
                "wdw": result.get("wdw") if "error" not in result else None,
                "top3": result.get("top3") if "error" not in result else None
            })

    leagues = [{"league_id": k, "league_name": v} for k, v in leagues_dict.items()]

    return render_template("dashboard.html", matches=matches, leagues=leagues)


# -----------------------------------------------------
# PDF DOWNLOAD ROUTE
# -----------------------------------------------------
@app.route("/download_pdf")
def download_pdf():
    df_today = fetch_today_matches()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Soccer Predictions Report", ln=True, align='C')
    pdf.ln(5)

    if df_today.empty:
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, "No matches available today.", ln=True)
    else:
        for _, m in df_today.iterrows():
            result = predict_match(m["home_id"], m["away_id"], m["league_id"])
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 8, f"{m['home_name']} vs {m['away_name']}", ln=True)
            pdf.set_font("Arial", '', 12)

            if "error" in result:
                pdf.cell(0, 8, result["error"], ln=True)
            else:
                pdf.cell(0, 8, f"Predicted Score: {result['predicted_score']} | Outcome: {result['outcome']}", ln=True)
                pdf.cell(0, 8, f"Win/Draw/Win %: Home {result['wdw']['home']}%, Draw {result['wdw']['draw']}%, Away {result['wdw']['away']}%", ln=True)
                pdf.cell(0, 8, "Top 3 Scorelines:", ln=True)
                for s, p in result['top3']:
                    pdf.cell(0, 8, f"   {s} => {p}%", ln=True)
            pdf.ln(5)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="predictions_report.pdf", mimetype='application/pdf')


# -----------------------------------------------------
# RUN APP
# -----------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
