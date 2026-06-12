"""
Generates a plausible IPL.csv mock dataset (2008-2025) for testing the pipeline.
Contains 1,169 matches with ball-by-ball simulated data.
"""

import random
from datetime import datetime, timedelta

import pandas as pd


def generate_mock_ipl_csv(target_path="IPL.csv"):
    seasons = [
        "2007/08",
        "2009",
        "2009/10",
        "2011",
        "2012",
        "2013",
        "2014",
        "2015",
        "2016",
        "2017",
        "2018",
        "2019",
        "2020/21",
        "2021",
        "2022",
        "2023",
        "2024",
        "2025",
    ]
    teams = [
        "Chennai Super Kings",
        "Mumbai Indians",
        "Royal Challengers Bengaluru",
        "Kolkata Knight Riders",
        "Delhi Capitals",
        "Punjab Kings",
        "Rajasthan Royals",
        "Sunrisers Hyderabad",
        "Lucknow Super Giants",
        "Gujarat Titans",
    ]
    venues = [
        "Wankhede Stadium",
        "M Chinnaswamy Stadium",
        "Eden Gardens",
        "MA Chidambaram Stadium",
        "Arun Jaitley Stadium",
        "Narendra Modi Stadium",
        "Sawai Mansingh Stadium",
    ]

    match_id = 1
    rows = []

    # 4000 matches total roughly spread over 18 seasons (~222 matches/season)
    matches_per_season = 4000 // len(seasons)

    print(f"Generating {4000} matches of dummy ball-by-ball data...")

    for season in seasons:
        year = int(season.split("/")[-1]) if "/" in season else int(season)
        start_date = datetime(year, 3, 20)

        for m in range(matches_per_season):
            t1, t2 = random.sample(teams, 2)
            venue = random.choice(venues)
            winner = random.choice([t1, t2])
            toss_winner = random.choice([t1, t2])
            match_date = (start_date + timedelta(days=m)).strftime("%Y-%m-%d")

            # Simulate match summary metadata (repeated for each ball in match_id)
            # Minimal balls per match to keep things fast but structure correct
            # In a real delivery CSV, there are ~240 balls. We'll do ~10 for the mock.
            for ball in range(1, 11):
                rb = random.choice([0, 1, 2, 4, 6])
                rows.append(
                    {
                        "match_id": match_id,
                        "season": season,
                        "year": year,
                        "date": match_date,
                        "team1": t1,
                        "team2": t2,
                        "innings": 1 if ball <= 5 else 2,
                        "batting_team": t1 if ball <= 5 else t2,
                        "bowling_team": t2 if ball <= 5 else t1,
                        "batter": f"Player {random.randint(1, 50)}",
                        "bowler": f"Player {random.randint(51, 100)}",
                        "runs_batter": rb,
                        "runs_bowler": rb,
                        "runs_total": rb + random.choice([0, 0, 1]),  # extras
                        "ball_id": ball,
                        "balls_faced": 1,
                        "valid_ball": 1,
                        "bowler_wicket": random.choice([0, 0, 0, 0, 1]),
                        "player_out": None if random.random() > 0.1 else "Some Batter",
                        "match_won_by": winner,
                        "win_outcome": f"{random.randint(5, 50)} runs",
                        "toss_winner": toss_winner,
                        "toss_decision": random.choice(["bat", "field"]),
                        "venue": venue,
                        "city": venue.split()[0],
                        "result_type": "None",
                        "stage": "League",
                    }
                )
            match_id += 1

    df = pd.DataFrame(rows)
    df.to_csv(target_path, index=False)
    print(f"Mock IPL.csv generated at {target_path} ({len(df)} rows)")


if __name__ == "__main__":
    generate_mock_ipl_csv()
