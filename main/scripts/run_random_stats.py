"""
大量ランダム自己対戦を行い統計を出力・CSV 保存するスクリプト。

使い方例:
  python scripts/run_random_stats.py --episodes 1000 --size 8 --seed 42 --csv

出力:
  - コンソール: 集計サマリ
  - (オプション) CSV: logs/random_stats_YYYYmmdd_HHMMSS.csv
"""

import argparse
import os
import csv
from datetime import datetime
import numpy as np
from tqdm import tqdm

from othello_env import OthelloEnv
from agents.random_agent import RandomAgent
from utils.stats import aggregate_game_records, final_winner_from_counts

def play_one_game(env: OthelloEnv, agent_black, agent_white, rng: np.random.Generator):
    """
    1 ゲーム実行。
    env.reset() 後、current_player が 1/ -1 どちらかで開始。
    ここでは「表示上の黒 = -1」「白 = 1」とみなす。
    終局後、盤面カウントで勝敗決定（環境 reward 視点とは独立に再計算）
    """
    obs = env.reset()
    starting_player = env.current_player
    done = False
    passes = 0
    first_pass_turn = None
    move_count = 0

    # 対局ループ
    while not done:
        mask = env.get_legal_action_mask()
        legal = np.where(mask == 1)[0]
        # エージェント選択 (env.current_player == 1 → 白番, == -1 → 黒番)
        if env.current_player == -1:
            action = agent_black.select_action(env)
        else:
            action = agent_white.select_action(env)

        # パス判定 (pass アクション index)
        if action == env.size * env.size:
            passes += 1
            if first_pass_turn is None:
                first_pass_turn = move_count
        else:
            passes += 0

        obs, reward, done, info = env.step(action)
        move_count += 1

    # 最終石数
    board = env.board
    black_count = int(np.sum(board == -1))
    white_count = int(np.sum(board == 1))
    winner = final_winner_from_counts(black_count, white_count)

    return {
        "winner": winner,
        "final_diff": abs(white_count - black_count),
        "total_moves": move_count,
        "passes": passes,
        "early_pass": first_pass_turn,
        "black_count": black_count,
        "white_count": white_count,
        "starting_player": starting_player
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=1000)
    parser.add_argument("--size", type=int, default=8)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--csv", action="store_true", help="結果を CSV 保存")
    parser.add_argument("--outdir", type=str, default="logs")
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    np.random.seed(args.seed)

    env = OthelloEnv(size=args.size)
    agent_black = RandomAgent()
    agent_white = RandomAgent()

    records = []
    for i in tqdm(range(args.episodes), desc="Random self-play"):
        rec = play_one_game(env, agent_black, agent_white, rng)
        rec["game_index"] = i
        rec["agent_black"] = "Random"
        rec["agent_white"] = "Random"
        rec["seed"] = args.seed
        records.append(rec)

    # 集計
    from utils.stats import aggregate_game_records
    summary = aggregate_game_records(records)

    # 出力
    print("==== Summary (Random vs Random) ====")
    for k, v in summary.items():
        print(f"{k}: {v}")

    # CSV 保存
    if args.csv:
        os.makedirs(args.outdir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(args.outdir, f"random_stats_{ts}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
            writer.writeheader()
            writer.writerows(records)
        print(f"Saved CSV: {path}")

if __name__ == "__main__":
    main()