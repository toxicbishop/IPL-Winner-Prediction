"""
Venue-level features computed from real IPL data:
  - Average first-innings score at venue
  - Toss impact at venue: does winning toss help?
  - Boundary size encoding (small=batting friendly, large=bowling friendly)
"""

import os
from functools import lru_cache

import pandas as pd

from config import BASE_DIR

IPL_CSV = os.path.join(BASE_DIR, "IPL.csv")

# Ground size category: 0 = small (batting paradise), 1 = medium, 2 = large
VENUE_SIZE = {
    "Wankhede Stadium": 0,
    "M Chinnaswamy Stadium": 0,
    "Sharjah Cricket Stadium": 0,
    "MA Chidambaram Stadium": 1,
    "Eden Gardens": 1,
    "Rajiv Gandhi International Cricket Stadium": 1,
    "Punjab Cricket Association IS Bindra Stadium": 1,
    "Punjab Cricket Association Stadium": 1,
    "Sawai Mansingh Stadium": 1,
    "BRSABV Ekana Cricket Stadium": 1,
    "DY Patil Stadium": 1,
    "Arun Jaitley Stadium": 1,
    "Feroz Shah Kotla": 1,
    "Brabourne Stadium": 1,
    "Himachal Pradesh Cricket Association Stadium": 1,
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium": 1,
    "Narendra Modi Stadium": 2,
    "Dubai International Cricket Stadium": 1,
    "Sheikh Zayed Stadium": 1,
    "Maharashtra Cricket Association Stadium": 1,
    "Saurashtra Cricket Association Stadium": 1,
    "Holkar Cricket Stadium": 1,
}

GLOBAL_AVG_SCORE = 160
GLOBAL_TOSS_IMPACT = 0.52


@lru_cache(maxsize=1)
def _compute_venue_stats() -> dict:
    """Compute venue-level stats from real ball-by-ball data."""
    if not os.path.exists(IPL_CSV):
        return {}

    df = pd.read_csv(
        IPL_CSV,
        low_memory=False,
        usecols=[
            "match_id",
            "innings",
            "venue",
            "runs_total",
            "toss_winner",
            "match_won_by",
            "batting_team",
        ],
    )

    # --- Average first-innings score per venue ---
    first_inns = df[df["innings"] == 1]
    match_scores = first_inns.groupby(["match_id", "venue"])["runs_total"].sum().reset_index()
    venue_avg = match_scores.groupby("venue")["runs_total"].mean()

    # --- Toss impact per venue ---
    match_meta = (
        df.groupby("match_id")
        .agg(
            toss_winner=("toss_winner", "first"),
            match_won_by=("match_won_by", "first"),
            venue=("venue", "first"),
        )
        .reset_index()
    )
    match_meta = match_meta[match_meta["match_won_by"] != "Unknown"]
    match_meta["toss_won_match"] = (match_meta["toss_winner"] == match_meta["match_won_by"]).astype(
        int
    )
    venue_toss = match_meta.groupby("venue").agg(
        toss_win_rate=("toss_won_match", "mean"),
        n_matches=("match_id", "count"),
    )
    # Only use venues with >= 5 matches for reliability
    venue_toss = venue_toss[venue_toss["n_matches"] >= 5]

    stats = {}
    for venue in set(venue_avg.index) | set(venue_toss.index):
        stats[venue] = {
            "avg_score": float(venue_avg.get(venue, GLOBAL_AVG_SCORE)),
            "toss_impact": float(venue_toss.loc[venue, "toss_win_rate"])
            if venue in venue_toss.index
            else GLOBAL_TOSS_IMPACT,
        }
    return stats


def get_venue_avg_score(venue: str) -> float:
    """Normalized venue average score (0-1, where 1 = highest scoring)."""
    stats = _compute_venue_stats()
    raw = stats.get(venue, {}).get("avg_score", GLOBAL_AVG_SCORE)
    # Normalize to 0-1 range (120=0, 200=1)
    return max(0, min(1, (raw - 120) / (200 - 120)))


def get_venue_toss_impact(venue: str) -> float:
    """Returns toss win probability at this venue (>0.5 = toss matters more)."""
    stats = _compute_venue_stats()
    return stats.get(venue, {}).get("toss_impact", GLOBAL_TOSS_IMPACT)


def get_venue_size(venue: str) -> int:
    """0=small, 1=medium, 2=large."""
    return VENUE_SIZE.get(venue, 1)
