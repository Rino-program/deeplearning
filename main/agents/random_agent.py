"""
ランダムエージェント:
  - 現在の合法手マスクから一様ランダムに 1 アクションを選ぶ
  - pass も含めて合法手が1つならそれを選ぶ
"""

import numpy as np
from othello_env import OthelloEnv

class RandomAgent:
    def select_action(self, env: OthelloEnv) -> int:
        mask = env.get_legal_action_mask()
        legal = np.where(mask == 1)[0]
        return int(np.random.choice(legal))