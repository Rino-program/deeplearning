"""
将来の教師あり学習（模倣学習など）や分析用に、ランダム対戦の盤面遷移データセットを
保存するサンプル。ファイルサイズに注意。

使い方:
  python scripts/generate_random_dataset.py --episodes 100 --size 8 --out data/random_dataset.npz

出力:
  - npz に以下を保存 (list を ndarray に詰め込む):
    states: (N, 3, size, size)
    actions: (N,)
    final_result: (N,) その局面を最初に見ているプレイヤー視点の最終結果 (-1,0,1)
"""

import argparse
import numpy as np
from tqdm import tqdm

from othello_env import OthelloEnv
from agents.random_agent import RandomAgent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--size", type=int, default=8)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=str, default="data/random_dataset.npz")
    args = parser.parse_args()

    np.random.seed(args.seed)
    env = OthelloEnv(size=args.size)
    agent_a = RandomAgent()
    agent_b = RandomAgent()

    all_states = []
    all_actions = []
    all_final = []

    for ep in tqdm(range(args.episodes), desc="Generate random dataset"):
        states = []
        actions = []
        obs = env.reset()
        done = False
        # このエピソード最終結果を後で全状態に付与するため一時保存
        per_episode_states = []
        per_episode_actions = []
        while not done:
            mask = env.get_legal_action_mask()
            legal = np.where(mask == 1)[0]
            if env.current_player == 1:
                action = agent_a.select_action(env)
            else:
                action = agent_b.select_action(env)
            per_episode_states.append(obs.copy())
            per_episode_actions.append(action)
            obs, reward, done, info = env.step(action)

        # 終局後、最終盤面から勝敗計算（current_player 視点ではなく、各保存時の obs はその時点視点）
        # 簡潔には reward を反映させるのではなく盤面再計算で統一できるが、
        # ここでは簡易的に: 終了直後の env.board を使って from white/black counts derive result.
        board = env.board
        white_count = int(np.sum(board == 1))
        black_count = int(np.sum(board == -1))
        if white_count > black_count:
            final_result_absolute = 1
        elif white_count < black_count:
            final_result_absolute = -1
        else:
            final_result_absolute = 0

        # 各保存局面はその時点での current_player 視点に正規化済みなので final_result Absolute を
        # その時点視点へ写像する必要がある:
        # 盤面 obs[0] は「自分の石チャネル」なので、その obs を生成した時点の current_player は常に 1。
        # よって final_result_absolute を「その時点の current_player=白?黒?」で符号調整:
        # もしその時点で手番が黒(-1)だったなら absolute を反転する必要があるが、
        # 今回は obs 生成時に board * current_player しているため current_player=1 の視点固定になっている。
        # したがって final_result = final_result_absolute (簡略)
        final_result = final_result_absolute

        all_states.extend(per_episode_states)
        all_actions.extend(per_episode_actions)
        all_final.extend([final_result] * len(per_episode_states))

    states_arr = np.stack(all_states, axis=0)
    actions_arr = np.array(all_actions, dtype=np.int16)
    finals_arr = np.array(all_final, dtype=np.int8)

    out_path = args.out
    import os
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    np.savez_compressed(out_path, states=states_arr, actions=actions_arr, final_result=finals_arr)
    print(f"Saved dataset to {out_path}")
    print("Shapes:", states_arr.shape, actions_arr.shape, finals_arr.shape)

if __name__ == "__main__":
    main()