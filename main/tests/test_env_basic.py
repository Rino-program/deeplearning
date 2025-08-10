"""
基本的なユニットテスト:
  pytest -q
で実行可能。

テスト観点:
1. 初期配置が正しいか
2. 初手で合法手が 4 つ (標準8x8の場合) 前後になっているか (オセロ初期の合法手は4マス: 白黒どちらが先手かで視点は変わるが数は同じ)
3. 合法手を1つ打って石が裏返るか
4. 合法手が無い状態で pass のみマスクされるか (人工的に盤面を細工)
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from othello_env import OthelloEnv

import numpy as np
from othello_env import OthelloEnv

def test_initial_setup():
    env = OthelloEnv(size=8)
    env.reset()
    mid = env.size // 2
    # 初期4石
    assert env.board[mid-1, mid-1] == 1
    assert env.board[mid, mid] == 1
    assert env.board[mid-1, mid] == -1
    assert env.board[mid, mid-1] == -1

def test_initial_legal_moves_count():
    env = OthelloEnv(size=8)
    env.reset()
    mask = env.get_legal_action_mask()
    # 合法セル数を数える (pass を除いて)
    legal_cell_count = int(mask[:-1].sum())
    # 4 が基本 (先手が白でも黒でも)
    assert legal_cell_count == 4

def test_place_and_flip():
    env = OthelloEnv(size=8)
    env.reset()
    mask = env.get_legal_action_mask()
    legal_indices = np.where(mask[:-1] == 1)[0]
    action = int(legal_indices[0])
    # 1手進める
    obs, reward, done, info = env.step(action)
    assert not done
    # 石数合計が初期4 -> 5 以上になっているはず (裏返し含め増える場合有)
    assert (env.board != 0).sum() >= 5

def test_pass_only_mask():
    env = OthelloEnv(size=4)
    env.reset()
    # 盤面を人工的に埋める（合法手無し状態を作る）
    env.board.fill(1)
    env.board[0,0] = -1
    # current_player を 1 に固定
    env.current_player = 1
    mask = env.get_legal_action_mask()
    assert mask[:-1].sum() == 0  # セルは置けない
    assert mask[-1] == 1         # pass が 1
