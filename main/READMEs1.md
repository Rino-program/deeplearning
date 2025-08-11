# Othello RL Project (Step 0-1)

※このREADME.mdファイルは一部、GitHub Copilot によって作成されています。

## 現在の進捗
- Step0: 環境 (OthelloEnv) 実装済み
- Step1: ランダム検証 / 統計 / ベースライン導入

## 新しくできること (Step1)
1. 大量ランダム自己対戦 (scripts/run_random_stats.py)
2. 統計集計 (勝率 / 平均手数 / 石差分布 / パス統計)
3. CSV 出力 (logs/random_stats_YYYYmmdd_HHMMSS.csv)
4. GreedyAgent を追加し Random と比較 (scripts/benchmark_agents.py)
5. 簡易 ELO レーティング評価 (utils/elo.py)
6. 再現性のため seed 指定 (--seed)

## すぐ試す
```bash
# ランダム自己対戦 1000局
python scripts/run_random_stats.py --episodes 1000 --size 8 --seed 42

# Random vs Greedy 200局
python scripts/benchmark_agents.py --episodes 200 --size 8 --seed 123
```

## 生成した CSV の例のカラム
- game_index
- winner (1, -1, 0=draw)
- final_diff (|white - black|)
- total_moves
- passes
- early_pass (最初のパス手数)
- black_count / white_count
- starting_player (1 or -1)
- seed
- agent_black / agent_white

## 今後 (Step2 予定)
- 4x4 盤でタブラー Q-learning
- 対称性増強前の素朴な学習ループ
- 評価指標を使って改善を実感
