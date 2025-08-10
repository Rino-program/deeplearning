"""
ランダム自己対戦を所定回数行い、勝敗統計を出すスクリプト (Step 0 検証用)。

使い方:
  python scripts/run_random_selfplay.py --episodes 10 --size 8

後で:
  - 勝率ログやELO等の評価に拡張
  - Agent を差し替え（Random vs 将来の学習済みAgent）
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import numpy as np
from othello_env import OthelloEnv
from agents.random_agent import RandomAgent

def play_one_game(env: OthelloEnv, agent_a, agent_b, render: bool = False):
    obs = env.reset()
    done = False
    current_agent = agent_a if env.current_player == 1 else agent_b

    while not done:
        action = current_agent.select_action(env)
        obs, reward, done, info = env.step(action)
        if render:
            env.render()
        if done:
            # reward は「step 実行後の current_player 視点」で定義済みのため、
            # 途中で current_player が変わっている点に注意が必要。
            # ここでは env.current_player 視点の reward なので、
            # 「ゲーム直前の手を打ったプレイヤー」視点に変換したいなら追加処理が必要。
            return reward
        current_agent = agent_a if env.current_player == 1 else agent_b

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=5)
    parser.add_argument("--size", type=int, default=8)
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()

    env = OthelloEnv(size=args.size)
    agent_a = RandomAgent()
    agent_b = RandomAgent()

    results = []
    for i in range(args.episodes):
        r = play_one_game(env, agent_a, agent_b, render=args.render)
        results.append(r)
        print(f"Game {i+1}/{args.episodes} reward(from current final perspective): {r}")

    # 簡易集計
    wins = sum(1 for x in results if x > 0)
    losses = sum(1 for x in results if x < 0)
    draws = sum(1 for x in results if x == 0)
    print("Summary:")
    print(f"  Wins: {wins}")
    print(f"  Losses: {losses}")
    print(f"  Draws: {draws}")

if __name__ == "__main__":
    main()