# prepare_data.py
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from utils import compute_team_form
import joblib

def build_training_features(df):
    le_team = LabelEncoder()
    le_league = LabelEncoder()

    df['home_team_enc'] = le_team.fit_transform(df['home_team_api_id'])
    df['away_team_enc'] = le_team.transform(df['away_team_api_id'])
    df['league_enc'] = le_league.fit_transform(df['league_id'])

    features = []

    for _, row in df.iterrows():
        home_stats = compute_team_form(df, row['home_team_api_id'])
        away_stats = compute_team_form(df, row['away_team_api_id'])

        features.append({
            'home_team_enc': row['home_team_enc'],
            'away_team_enc': row['away_team_enc'],
            'league_enc': row['league_enc'],

            # form stats
            'home_form_points': home_stats['points'],
            'away_form_points': away_stats['points'],
            'home_goal_diff': home_stats['avg_goal_diff'],
            'away_goal_diff': away_stats['avg_goal_diff'],
            'home_avg_scored': home_stats['avg_goals_scored'],
            'away_avg_scored': away_stats['avg_goals_scored'],
            'home_avg_conceded': home_stats['avg_goals_conceded'],
            'away_avg_conceded': away_stats['avg_goals_conceded'],

            # home advantage weight
            'home_advantage': 1
        })

    X = pd.DataFrame(features)

    # Target
    y = []
    for _, r in df.iterrows():
        if r['home_team_goal'] > r['away_team_goal']:
            y.append(2)
        elif r['home_team_goal'] < r['away_team_goal']:
            y.append(0)
        else:
            y.append(1)

    return X, y, le_team, le_league


if __name__ == "__main__":
    df = pd.read_csv("matches.csv")  # full dataset
    X, y, le_team, le_league = build_training_features(df)

    joblib.dump((X, y), "training_features.joblib")
    joblib.dump({'team': le_team, 'league': le_league}, "encoders.joblib")
