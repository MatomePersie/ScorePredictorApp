# utils.py
import pandas as pd
import numpy as np

def compute_team_form(df, team_id, n=5):
    """Return form stats for last n matches of a team."""
    matches = df[
        (df['home_team_api_id'] == team_id) |
        (df['away_team_api_id'] == team_id)
    ].sort_values('date', ascending=False).head(n)

    if matches.empty:
        return {
            'points': 0,
            'avg_goal_diff': 0,
            'avg_goals_scored': 0,
            'avg_goals_conceded': 0
        }

    points = 0
    goal_diffs = []
    goals_scored = []
    goals_conceded = []

    for _, m in matches.iterrows():
        if m['home_team_api_id'] == team_id:
            diff = m['home_team_goal'] - m['away_team_goal']
            goal_diffs.append(diff)
            goals_scored.append(m['home_team_goal'])
            goals_conceded.append(m['away_team_goal'])
        else:
            diff = m['away_team_goal'] - m['home_team_goal']
            goal_diffs.append(diff)
            goals_scored.append(m['away_team_goal'])
            goals_conceded.append(m['home_team_goal'])

        if diff > 0: points += 3
        elif diff == 0: points += 1

    return {
        'points': points / (n*3),
        'avg_goal_diff': np.mean(goal_diffs),
        'avg_goals_scored': np.mean(goals_scored),
        'avg_goals_conceded': np.mean(goals_conceded)
    }
