"""
GreedyAgent:
  その手で「ひっくり返せる枚数（石数）」が最大になる合法手を選ぶ単純ヒューリスティック。
  同点が複数あればランダムに 1 手。

目的:
  - RandomAgent より多少強いベースライン
  - 学習エージェントとの比較対象
"""

import numpy as np
from othello_env import OthelloEnv

class GreedyAgent:
    def select_action(self, env: OthelloEnv) -> int:
        mask = env.get_legal_action_mask()
        legal_idxs = np.where(mask == 1)[0]
        if len(legal_idxs) == 1:
            return int(legal_idxs[0])

        size = env.size
        best = []
        best_gain = -1
        for idx in legal_idxs:
            if idx == size * size:  # pass
                gain = 0
            else:
                r, c = divmod(idx, size)
                gain = self._flip_gain(env, r, c, env.current_player)
            if gain > best_gain:
                best_gain = gain
                best = [idx]
            elif gain == best_gain:
                best.append(idx)
        return int(np.random.choice(best))

    def _flip_gain(self, env: OthelloEnv, row: int, col: int, player: int) -> int:
        """
        置いた時に裏返せる数を数える（実際には盤を変えない）。
        """
        if env.board[row, col] != 0:
            return -999
        opp = -player
        total = 0
        for dr, dc in env.directions:
            r, c = row + dr, col + dc
            path = 0
            while 0 <= r < env.size and 0 <= c < env.size and env.board[r, c] == opp:
                path += 1
                r += dr
                c += dc
            if path > 0 and 0 <= r < env.size and 0 <= c < env.size and env.board[r, c] == player:
                total += path
        return total