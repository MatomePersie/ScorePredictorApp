# fetch_api.py
import requests
import pandas as pd

API_KEY = "206b7f91de16477f840fafd142941d92"
BASE_URL = "https://api.football-data.org/v4/"

headers = {
    "X-Auth-Token": API_KEY
}


def fetch_today_matches():
    url = BASE_URL + "matches"
    r = requests.get(url, headers=headers)
    data = r.json()

    matches = []

    for m in data.get("matches", []):
        if m["status"] in ["TIMED", "SCHEDULED"]:  # upcoming matches
            matches.append({
                "home_team_name": m["homeTeam"]["name"],
                "away_team_name": m["awayTeam"]["name"],
                "home_team_api_id": m["homeTeam"]["id"],
                "away_team_api_id": m["awayTeam"]["id"],
                "league_id": m["competition"]["id"],
            })

    return pd.DataFrame(matches)


def fetch_match_history(team_id, limit=20):
    """Fetch previous matches for a team."""
    url = BASE_URL + f"teams/{team_id}/matches?limit={limit}"
    r = requests.get(url, headers=headers)
    data = r.json()

    rows = []

    for m in data.get("matches", []):
        if m["status"] != "FINISHED":
            continue

        rows.append({
            "date": m["utcDate"],
            "home_team_api_id": m["homeTeam"]["id"],
            "away_team_api_id": m["awayTeam"]["id"],
            "home_team_goal": m["score"]["fullTime"]["home"],
            "away_team_goal": m["score"]["fullTime"]["away"],
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df_today = fetch_today_matches()
    print(df_today)

    # test history for first match
    if not df_today.empty:
        team_id = df_today.iloc[0]["home_team_api_id"]
        df_hist = fetch_match_history(team_id)
        print(df_hist.head())
