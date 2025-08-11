"""
簡易 ELO 計算ユーティリティ
- update_elo: 2プレイヤーの ELO を 1 ゲーム結果で更新
- expected_score: 期待スコア計算
- run_elo_series: 複数結果にまとめて適用

前提:
  プレイヤー A / B のレーティング RA / RB
  期待スコア EA = 1 / (1 + 10^((RB - RA)/400))
  結果 S (勝=1, 引分=0.5, 負=0)
  新レート: R'A = RA + K*(S - EA)
K は 16, 24, 32 など（調整可）
"""

from typing import List, Tuple

def expected_score(r_a: float, r_b: float) -> float:
    return 1.0 / (1.0 + 10 ** ((r_b - r_a) / 400.0))

def update_elo(r_a: float, r_b: float, result_a: float, k: float = 32.0) -> Tuple[float, float]:
    ea = expected_score(r_a, r_b)
    eb = expected_score(r_b, r_a)
    r_a_new = r_a + k * (result_a - ea)
    r_b_new = r_b + k * ((1 - result_a) - eb)
    return r_a_new, r_b_new

def run_elo_series(results: List[int], r_a_init=1500.0, r_b_init=1500.0, k=32.0):
    """
    results: A 視点の結果 (1=勝, 0=負, 0.5=引分) の配列
    """
    r_a = r_a_init
    r_b = r_b_init
    history = []
    for i, res in enumerate(results):
        r_a, r_b = update_elo(r_a, r_b, res, k=k)
        history.append((i, r_a, r_b))
    return r_a, r_b, history