"""
統計ユーティリティの基本テスト
pytest -q で実行

目的:
- aggregate_game_records が期待通りキーを生成するか
- final_winner_from_counts の単純検証
"""

from utils.stats import aggregate_game_records, final_winner_from_counts

def test_aggregate_game_records():
    dummy = [
        {
            "winner": 1,
            "final_diff": 10,
            "total_moves": 50,
            "passes": 2,
            "early_pass": 40,
            "black_count": 27,
            "white_count": 37,
            "starting_player": 1
        },
        {
            "winner": -1,
            "final_diff": 4,
            "total_moves": 58,
            "passes": 1,
            "early_pass": 45,
            "black_count": 34,
            "white_count": 30,
            "starting_player": -1
        },
        {
            "winner": 0,
            "final_diff": 0,
            "total_moves": 60,
            "passes": 3,
            "early_pass": 50,
            "black_count": 32,
            "white_count": 32,
            "starting_player": 1
        }
    ]
    summary = aggregate_game_records(dummy)
    assert summary["games"] == 3
    assert 0.0 <= summary["win_rate_player1"] <= 1.0
    assert "mean_total_moves" in summary

def test_final_winner_from_counts():
    assert final_winner_from_counts(30, 34) == 1
    assert final_winner_from_counts(40, 20) == -1
    assert final_winner_from_counts(10, 10) == 0