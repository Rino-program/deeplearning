"""
Othello (Reversi) Environment for Reinforcement Learning.

主な特徴:
- Gym ライク: reset(), step(action), render()
- 行動空間: 0..(size*size-1) = 盤面セル, 最後に pass アクション index
- 観測: (channels, size, size) の numpy 配列 (自分石 / 相手石 / 合法手マスク)
  + current_player (内部で符号正規化済みなので観測には明示不要でもよい)
- 終局条件: 両者連続 pass または両者合法手なし
- 報酬: 終局で勝ち +1, 負け -1, 引分 0 (中間報酬なし)
- 不正手: step 内で info["illegal"]=True を返し終了させる実装 (学習時はマスクで防止予定)

使い方例:
    env = OthelloEnv(size=8)
    obs = env.reset()
    done = False
    while not done:
        legal_mask = env.get_legal_action_mask()
        # ランダム選択 (合法手のみ)
        action = np.random.choice(np.where(legal_mask == 1)[0])
        obs, reward, done, info = env.step(action)
    print("Final reward:", reward)
"""

from __future__ import annotations
import numpy as np
from typing import List, Tuple, Dict, Optional

class OthelloEnv:
    def __init__(self, size: int = 8, allow_illegal: bool = False):
        """
        :param size: 盤の一辺の長さ (標準 8)
        :param allow_illegal: True の場合、不正手でも終了させず -1 ペナルティだけ与えて続行する等の改造がしやすい
                              今回は False 推奨 (不正手は即終了)
        """
        self.size = size
        self.action_size = size * size + 1  # 最後の index が pass
        self.allow_illegal = allow_illegal

        # 方向 (8近傍)
        self.directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        # 状態変数
        self.board: np.ndarray = np.zeros((self.size, self.size), dtype=np.int8)
        self.current_player: int = 1
        self.pass_streak: int = 0
        self.done: bool = False
        self.turn_count: int = 0  # デバッグ用

    # =========================================================
    # 公開 API
    # =========================================================
    def reset(self) -> np.ndarray:
        """ゲームを初期化し観測を返す。"""
        self.board.fill(0)
        mid = self.size // 2
        self.board[mid - 1, mid - 1] = 1
        self.board[mid, mid] = 1
        self.board[mid - 1, mid] = -1
        self.board[mid, mid - 1] = -1
        # 先手をランダムにすることでデータ偏りを減らす
        self.current_player = np.random.choice([1, -1])
        self.pass_streak = 0
        self.done = False
        self.turn_count = 0
        return self._get_obs()

    def step(self, action: int):
        """
        指定アクションを適用し (obs, reward, done, info) を返す。

        不正手:
            allow_illegal=False の場合 → 即座に done=True, reward=-1 として終了 (学習が壊れるのを防ぐ)
        pass アクション:
            index == size*size のとき
            - 合法手が存在するのに pass を選んだ場合は不正手扱い(設計選択)
            - 合法手が無い場合のみ pass が有効

        終局報酬:
            勝ち +1, 負け -1, 引分 0
            (current_player 視点で返すため、視点正規化していることに注意:
             ここでは最後に '勝敗' は「手番を持っていたプレイヤーが直前に指した後」ではなく
             最終盤面を current_player=1 の解釈で返す。)
        """
        if self.done:
            raise RuntimeError("Episode already finished. Call reset().")

        info: Dict = {}
        reward = 0.0
        pass_action_index = self.size * self.size

        legal_moves = self.legal_moves(self.current_player)
        has_legal = len(legal_moves) > 0

        # アクション分解
        if action == pass_action_index:
            if has_legal:
                # 合法手があるのに pass は不正とする
                return self._handle_illegal_action(info)
            # 合法手無し: 正当な pass
            self.pass_streak += 1
        else:
            r, c = divmod(action, self.size)
            if not has_legal:
                # 合法手がないのにセルを選択 = 不正
                return self._handle_illegal_action(info)
            if not self._can_place(r, c, self.current_player):
                # 不正手
                return self._handle_illegal_action(info)
            self._place_and_flip(r, c, self.current_player)
            self.pass_streak = 0

        self.turn_count += 1
        # ターン交代
        self.current_player *= -1

        # 相手に合法手が無い場合は自動 pass (pass_streak++)
        if not self.legal_moves(self.current_player):
            self.pass_streak += 1
            self.current_player *= -1  # 手番を戻す (両者合法手無しを検査)
            if not self.legal_moves(self.current_player):
                self.pass_streak += 1  # 両者ゼロ: 実質二連続passと同じ

        # 終局条件
        if self.pass_streak >= 2:
            self.done = True
            reward = self._final_reward()
        else:
            reward = 0.0

        return self._get_obs(), reward, self.done, info

    def render(self):
        """人間が読める形で盤面を表示。デバッグ用なので学習中は頻繁に呼ばない。"""
        chars = {1: 'W', -1: 'B', 0: '.'}
        print(f"Current player (internal): {self.current_player}  Turn: {self.turn_count}")
        print("   " + " ".join(map(str, range(self.size))))
        for r in range(self.size):
            row_str = " ".join(chars[int(x)] for x in self.board[r])
            print(f"{r:2d} {row_str}")
        print()

    def get_legal_action_mask(self) -> np.ndarray:
        """
        行動マスクを返す。
        shape: (action_size,)  1=合法, 0=不正
        """
        mask = np.zeros(self.action_size, dtype=np.int8)
        legal = self.legal_moves(self.current_player)
        for (r, c) in legal:
            idx = r * self.size + c
            mask[idx] = 1
        if len(legal) == 0:
            # pass のみ合法
            mask[self.size * self.size] = 1
        return mask

    # =========================================================
    # 内部補助
    # =========================================================
    def _handle_illegal_action(self, info: Dict):
        """不正手処理: 即終了 & reward=-1"""
        info["illegal"] = True
        self.done = True
        return self._get_obs(), -1.0, True, info

    def _get_obs(self) -> np.ndarray:
        """
        観測を返す。
        チャネル:
            0: 自分の石 (current_player 視点で +1 を自分として扱うので board * current_player == 1)
            1: 相手の石
            2: 合法手マスク（セル部分のみ）
        """
        # 視点正規化
        norm_board = self.board * self.current_player
        c_self = (norm_board == 1).astype(np.float32)
        c_oppo = (norm_board == -1).astype(np.float32)
        legal_mask_2d = np.zeros_like(self.board, dtype=np.float32)
        for (r, c) in self.legal_moves(self.current_player):
            legal_mask_2d[r, c] = 1.0
        obs = np.stack([c_self, c_oppo, legal_mask_2d], axis=0)
        return obs  # shape: (3, size, size)

    def _final_reward(self) -> float:
        """
        終局時の報酬を current_player 視点 (self.current_player が 1 になるよう正規化された盤ではない点に注意) で返す。

        注意:
            ここまでの流れで current_player が最終的にどちらを向いているかで視点が紛らわしいため、
            通常は「盤面を数えて白黒比較 → current_player の符号をかけて正規化」する。
            しかし self.board は固定で -1 / 1 なので単純比較後、最後に視点正規化する。
        """
        counts = self._count_stones()
        # counts = { -1: x, 0: y, 1: z }
        if counts[1] > counts[-1]:
            result = 1
        elif counts[1] < counts[-1]:
            result = -1
        else:
            result = 0
        # self.current_player は最終的に「次に打つはずのプレイヤー」を指しているため、
        # 視点正規化するには result * self.current_player を使うより、
        # ここでは「勝った側が current_player だったか」を考えるとやや混乱する。
        # 簡潔に: current_player から見た価値を計算するには board を current_player で正規化し直し数えても良い。
        # ここでは単純に: 盤面を current_player で正規化し再度比較:
        norm_board = self.board * self.current_player
        norm_counts_self = np.sum(norm_board == 1)
        norm_counts_oppo = np.sum(norm_board == -1)
        if norm_counts_self > norm_counts_oppo:
            return 1.0
        elif norm_counts_self < norm_counts_oppo:
            return -1.0
        else:
            return 0.0

    def _count_stones(self) -> Dict[int, int]:
        unique, counts = np.unique(self.board, return_counts=True)
        d = {-1: 0, 0: 0, 1: 0}
        for u, c in zip(unique, counts):
            d[int(u)] = int(c)
        return d

    def legal_moves(self, player: int) -> List[Tuple[int, int]]:
        moves: List[Tuple[int, int]] = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r, c] == 0 and self._can_place(r, c, player):
                    moves.append((r, c))
        return moves

    def _can_place(self, row: int, col: int, piece: int) -> bool:
        if self.board[row, col] != 0:
            return False
        opp = -piece
        size = self.size
        for dr, dc in self.directions:
            r, c = row + dr, col + dc
            found = False
            while 0 <= r < size and 0 <= c < size and self.board[r, c] == opp:
                found = True
                r += dr
                c += dc
            if found and 0 <= r < size and 0 <= c < size and self.board[r, c] == piece:
                return True
        return False

    def _place_and_flip(self, row: int, col: int, piece: int):
        self.board[row, col] = piece
        size = self.size
        for dr, dc in self.directions:
            r, c = row + dr, col + dc
            path = []
            while 0 <= r < size and 0 <= c < size and self.board[r, c] == -piece:
                path.append((r, c))
                r += dr
                c += dc
            if path and 0 <= r < size and 0 <= c < size and self.board[r, c] == piece:
                for pr, pc in path:
                    self.board[pr, pc] = piece

if __name__ == "__main__":
    # 簡単な動作テスト
    env = OthelloEnv(size=8)
    obs = env.reset()
    env.render()
    mask = env.get_legal_action_mask()
    legal_indices = np.where(mask == 1)[0]
    print("Legal actions at start:", legal_indices)