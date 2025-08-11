"""
統計関連ヘルパー

提供機能:
- aggregate_game_records: 対局ログ (dict の list) から集計メトリクスを作成
- histogram_data: 分布生成用（後で可視化利用）
- safe_mean: ゼロ割防止平均
"""

from __future__ import annotations
from typing import List, Dict, Any
import math
import numpy as np
import pandas as pd

def safe_mean(x):
    return float(np.mean(x)) if len(x) > 0 else 0.0

def aggregate_game_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    records: 1ゲームにつき 1 dict
    各 dict 推奨キー:
        winner, final_diff, total_moves, passes, early_pass,
        black_count, white_count, starting_player
    """
    if len(records) == 0:
        return {}

    winners = [r["winner"] for r in records]
    wins_1 = winners.count(1)
    wins_m1 = winners.count(-1)
    draws = winners.count(0)

    diffs = [r["final_diff"] for r in records]
    moves = [r["total_moves"] for r in records]
    passes = [r["passes"] for r in records]
    early_passes = [r["early_pass"] for r in records if r["early_pass"] is not None]

    mean_diff = safe_mean(diffs)
    mean_moves = safe_mean(moves)
    mean_passes = safe_mean(passes)
    mean_early_pass = safe_mean(early_passes)

    res = {
        "games": len(records),
        "win_rate_player1": wins_1 / len(records),
        "win_rate_player_minus1": wins_m1 / len(records),
        "draw_rate": draws / len(records),
        "mean_final_diff": mean_diff,
        "mean_total_moves": mean_moves,
        "mean_passes_per_game": mean_passes,
        "mean_early_pass_turn": mean_early_pass,
        "min_moves": int(min(moves)),
        "max_moves": int(max(moves)),
        "median_moves": float(np.median(moves)),
        "std_moves": float(np.std(moves)),
        "median_final_diff": float(np.median(diffs)),
    }
    return res

def histogram_data(values, bins=10):
    if len(values) == 0:
        return [], []
    hist, edges = np.histogram(values, bins=bins)
    return hist.tolist(), edges.tolist()

def records_to_dataframe(records: List[Dict[str, Any]]):
    return pd.DataFrame(records)

def final_winner_from_counts(black_count: int, white_count: int) -> int:
    if white_count > black_count:
        return 1
    elif white_count < black_count:
        return -1
    else:
        return 0