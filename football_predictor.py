import requests
import pandas as pd
import numpy as np
import math

# -----------------------------
# CONFIG
# -----------------------------
API_KEY = "206b7f91de16477f840fafd142941d92"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {"X-Auth-Token": API_KEY}

# -----------------------------
# FETCH FUNCTIONS
# -----------------------------
def fetch_today_matches():
    url = BASE_URL + "matches"
    r = requests.get(url, headers=HEADERS).json()
    matches = []

    for m in r.get("matches", []):
        if m.get("status") not in ["FINISHED", "POSTPONED", "CANCELLED"]:
            matches.append({
                "home_name": m["homeTeam"]["name"],
                "away_name": m["awayTeam"]["name"],
                "home_id": m["homeTeam"]["id"],
                "away_id": m["awayTeam"]["id"],
                "league_id": m["competition"]["id"],
                "league_name": m["competition"]["name"],
                "status": m.get("status"),
                "home_logo": "",  # placeholder
                "away_logo": "",  # placeholder
            })
    return pd.DataFrame(matches)

def fetch_last_matches(team_id, limit=10):
    url = BASE_URL + f"teams/{team_id}/matches?limit={limit}"
    r = requests.get(url, headers=HEADERS).json()
    rows = []

    for m in r.get("matches", []):
        if m.get("status") != "FINISHED":
            continue
        ft = m.get("score", {}).get("fullTime", {})
        rows.append({
            "date": m.get("utcDate", "2000-01-01"),
            "home_id": m["homeTeam"]["id"],
            "away_id": m["awayTeam"]["id"],
            "home_goal": ft.get("home", 0),
            "away_goal": ft.get("away", 0)
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.sort_values("date", ascending=False).head(limit)

def fetch_league_recent_matches(league_id, limit=50):
    url = BASE_URL + f"competitions/{league_id}/matches"
    r = requests.get(url, headers=HEADERS).json()
    rows = []
    for m in r.get("matches", []):
        if m.get("status") != "FINISHED":
            continue
        ft = m.get("score", {}).get("fullTime", {})
        rows.append({
            "home_id": m["homeTeam"]["id"],
            "away_id": m["awayTeam"]["id"],
            "home_goal": ft.get("home", 0),
            "away_goal": ft.get("away", 0)
        })
    return pd.DataFrame(rows)

# -----------------------------
# STATS CALCULATION
# -----------------------------
def compute_strength_from_df(df, team_id, home_bias=1.0):
    if df.empty:
        return None
    goals_for = []
    goals_against = []

    for _, m in df.iterrows():
        if m["home_id"] == team_id:
            goals_for.append(m["home_goal"] * home_bias)
            goals_against.append(m["away_goal"])
        elif m["away_id"] == team_id:
            goals_for.append(m["away_goal"])
            goals_against.append(m["home_goal"] * home_bias)

    if len(goals_for) == 0:
        return None

    avg_scored = np.mean(goals_for)
    avg_conceded = np.mean(goals_against)

    return {
        "attack": max(0.3, avg_scored / 1.4),
        "defense": max(0.3, avg_conceded / 1.4),
        "avg_scored": avg_scored,
        "avg_conceded": avg_conceded
    }

def get_team_strength(team_id, league_id, home_bias=1.0):
    df_personal = fetch_last_matches(team_id, limit=10)
    strength = compute_strength_from_df(df_personal, team_id, home_bias)
    if strength:
        return strength

    df_league = fetch_league_recent_matches(league_id, limit=50)
    strength = compute_strength_from_df(df_league, team_id, home_bias)
    if strength:
        return strength

    return None  # Not enough data

# -----------------------------
# POISSON TOOLS
# -----------------------------
def poisson(l, k):
    return (l ** k * math.exp(-l)) / math.factorial(k)

def score_probabilities(exp_h, exp_a, max_goals=5):
    table = {}
    for hg in range(0, max_goals + 1):
        for ag in range(0, max_goals + 1):
            table[(hg, ag)] = poisson(exp_h, hg) * poisson(exp_a, ag)
    return table

def win_draw_win(prob_table):
    hw = dw = aw = 0
    for (hg, ag), p in prob_table.items():
        if hg > ag:
            hw += p
        elif hg == ag:
            dw += p
        else:
            aw += p
    total = hw + dw + aw
    return {
        "home": round(hw / total * 100, 2),
        "draw": round(dw / total * 100, 2),
        "away": round(aw / total * 100, 2)
    }

# -----------------------------
# FINAL PREDICTION
# -----------------------------
def predict_match(home_id, away_id, league_id):
    home_strength = get_team_strength(home_id, league_id, home_bias=1.1)
    away_strength = get_team_strength(away_id, league_id)

    if home_strength is None or away_strength is None:
        return {"error": "Not enough data to predict this match."}

    exp_h = home_strength["attack"] * away_strength["defense"] * 1.20
    exp_a = away_strength["attack"] * home_strength["defense"] * 0.90

    prob_table = score_probabilities(exp_h, exp_a)
    top3 = sorted(prob_table.items(), key=lambda x: x[1], reverse=True)[:3]
    wdws = win_draw_win(prob_table)

    best_score, _ = top3[0]
    hg, ag = best_score
    outcome = "Home Win" if hg > ag else "Away Win" if ag > hg else "Draw"

    return {
        "predicted_score": f"{hg}-{ag}",
        "expected_goals": (round(exp_h, 2), round(exp_a, 2)),
        "outcome": outcome,
        "wdw": wdws,
        "top3": [(f"{a}-{b}", round(p * 100, 2)) for ((a, b), p) in top3]
    }
