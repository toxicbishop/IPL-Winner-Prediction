# IPL Winner Prediction System

### Temporal ML · Dynamic Modeling · Probability-Based Forecasting

---

## Project Overview
This is a technical implementation of a dynamic machine learning system designed to model team strength and simulate IPL 2026 outcomes. The project focuses on **Strict Temporal Feature Engineering** to eliminate data leakage and captures the high-scoring, volatile trends of the modern "Impact Player" era.

### UI Previews
![Win Probability Breakdown](dashboard/public/assets/Win-probability.png)
*Win Probability Distribution across the 2026 tournament cycle.*

![Feature Intelligence](dashboard/public/assets/Why.png)
*Explaining the "Why" behind team rankings via heuristic signaling.*

![Match Forecast](dashboard/public/assets/Forcast.png)
*Upcoming match predictions and venue-specific win probabilities.*

### Core Methodology
- **Temporal Feature Engineering**: Models are trained on chronological snapshots, ensuring features like "team form" only use data available before the match date.
- **Ball-by-Ball Analytics**: Derives granular signals (Powerplay SR, Death Over Economy, Boundary Percentage) to track evolving team performance.
- **Probabilistic Forecasting**: Uses a calibrated XGBoost model to estimate win probabilities, followed by a 5,000-iteration Monte Carlo simulation of the tournament structure.
- **Model-Informed Insights**: Generates qualitative justifications for rankings by surfacing the underlying performance metrics (heuristics) driving the model's output.

---

## Technical Architecture
- **Dynamic Ingestion Pipeline**: Processes raw Cricsheet JSON data (currently synced up to April 23, 2026).
- **Heuristic Confidence Scoring**: Confidence levels (High/Medium/Low) are derived from probability separation and model certainty thresholds.
- **Trend Modeling**: Tracks shifts in tournament win probability across data snapshots to reflect current momentum.
- **Calibrated Estimates**: Employs Isotonic regression to ensure model probabilities correspond to real-world outcomes.

---

## Performance & Accuracy
- **Model Stability**: Maintains ~56–60% accuracy on the 2024/2026 seasons (which are historically stochastic due to record-breaking scores).
- **Net Gain**: **+6.7%** improvement over the baseline (momentum-only) model.
- **Signal Discovery**: Successfully surfaces the critical impact of "Powerplay Wickets" and "Death Over Efficiency" in the 2026 meta.

---

## Quick Start
```bash
# 1. Setup Environment
pip install -r requirements.txt

# 2. Re-ingest and Engineer Features
python main.py --mode setup

# 3. Generate 2026 Predictions
python main.py --mode predict
```

---

## Live Snapshots (As of May 23, 2026)
| Rank | Team | Win Prob | Trend | Confidence | Key Signal |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **RCB** | 22.50% | +3.05% | High | Table Toppers, Strong NRR |
| 2 | **GT** | 20.10% | +2.10% | High | Qualified, Squad Depth |
| 3 | **SRH** | 18.70% | +0.91% | High | 9 Wins, Aggressive Batting |
| 4 | RR | 14.20% | +0.50% | Medium | Fighting for 4th Spot |
| - | CSK | 0.00% | -0.51% | Eliminated | Out of Playoff Contention |
| - | MI | 0.00% | -0.27% | Eliminated | Out of Playoff Contention |
| - | LSG | 0.00% | -1.50% | Eliminated | Out of Playoff Contention |

> **Last Updated**: May 23, 2026  
> **Data Coverage**: Matches till May 23, 2026  
> **Method**: Temporal XGBoost + MC Simulation  

---

## Important Considerations
This system is a research project designed to demonstrate advanced ML engineering patterns. Cricket is a stochastic sport with high variance; these predictions represent probabilistic estimates based on historical patterns and should not be treated as deterministic certainties.

---
*Created by [toxicbishop] — ML Engineering Portfolio*
