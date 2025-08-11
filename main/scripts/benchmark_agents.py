"""
GreedyAgent と RandomAgent を対戦させて性能比較 + ELO 推定を行う。

使い方:
  python scripts/benchmark_agents.py --episodes 200 --size 8 --seed 123

出力:
  - 勝率・引分率
  - ELO 推定 (初期 1500 同士)
"""

import argparse
import numpy as np
from tqdm import tqdm

from othello_env import OthelloEnv
from agents.random_agent import RandomAgent
from agents.greedy_agent import GreedyAgent
from utils.stats import final_winner_from_counts
from utils.elo import run_elo_series

def play_game(env: OthelloEnv, black_agent, white_agent):
    env.reset()
    done = False
    move_count = 0
    while not done:
        if env.current_player == -1:
            action = black_agent.select_action(env)
        else:
            action = white_agent.select_action(env)
        obs, reward, done, info = env.step(action)
        move_count += 1

    board = env.board
    black = int(np.sum(board == -1))
    white = int(np.sum(board == 1))
    winner = final_winner_from_counts(black, white)
    return winner, move_count, black, white

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=200)
    parser.add_argument("--size", type=int, default=8)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    np.random.seed(args.seed)
    env = OthelloEnv(size=args.size)

    random_agent = RandomAgent()
    greedy_agent = GreedyAgent()

    # Greedy を "Agent A" (白番想定) とし、Random を "Agent B" (黒番想定) で交互スタートも検討可
    # ここでは交互に先手/後手を入れ替えバイアスを軽減
    results_for_elo = []  # Greedy 視点の結果 (1,0,0.5)

    counts = {
        "greedy_wins": 0,
        "random_wins": 0,
        "draws": 0
    }

    for i in tqdm(range(args.episodes), desc="Benchmark Greedy vs Random"):
        # 交互に先手・後手
        if i % 2 == 0:
            black_agent = random_agent
            white_agent = greedy_agent
            greedy_is_white = True
        else:
            black_agent = greedy_agent
            white_agent = random_agent
            greedy_is_white = False

        winner, moves, b_count, w_count = play_game(env, black_agent, white_agent)

        if winner == 1:  # 白勝ち
            if greedy_is_white:
                counts["greedy_wins"] += 1
                results_for_elo.append(1.0)
            else:
                counts["random_wins"] += 1
                results_for_elo.append(0.0)
        elif winner == -1:  # 黒勝ち
            if greedy_is_white:
                counts["random_wins"] += 1
                results_for_elo.append(0.0)
            else:
                counts["greedy_wins"] += 1
                results_for_elo.append(1.0)
        else:
            counts["draws"] += 1
            results_for_elo.append(0.5)

    total = args.episodes
    print("=== Greedy vs Random ===")
    print(f"Total games: {total}")
    print(f"Greedy wins: {counts['greedy_wins']}  ({counts['greedy_wins']/total:.3f})")
    print(f"Random wins: {counts['random_wins']}  ({counts['random_wins']/total:.3f})")
    print(f"Draws      : {counts['draws']}  ({counts['draws']/total:.3f})")

    # ELO 計算
    r_greedy, r_random, history = run_elo_series(results_for_elo, r_a_init=1500, r_b_init=1500, k=32)
    print(f"Estimated ELO Greedy: {r_greedy:.1f}, Random: {r_random:.1f}")
    print("Last 5 ELO entries (index, Greedy, Random):")
    for h in history[-5:]:
        print(h)

if __name__ == "__main__":
    main()