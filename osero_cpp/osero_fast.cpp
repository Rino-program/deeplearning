#include <iostream>
#include <vector>
#include <random>
#include <ctime>

// 超高速オセロ自動対局シミュレータ
class Osero {
public:
    int size;
    std::vector<std::vector<int>> board;
    static constexpr int dr[8] = { -1, 1, 0, 0, -1, -1, 1, 1 };
    static constexpr int dc[8] = { 0, 0, -1, 1, -1, 1, -1, 1 };

    Osero(int sz = 8) : size(sz), board(sz, std::vector<int>(sz, 0)) {
        int m = sz / 2;
        board[m-1][m-1] = 1;
        board[m-1][m]   = -1;
        board[m][m-1]   = -1;
        board[m][m]     = 1;
    }

    // 駒を置ける場所を列挙
    inline void get_moves(int piece, std::vector<std::pair<int,int>>& moves) const {
        moves.clear();
        for (int r = 0; r < size; ++r) for (int c = 0; c < size; ++c) {
            if (board[r][c] != 0) continue;
            for (int d = 0; d < 8; ++d) {
                int nr = r + dr[d], nc = c + dc[d], cnt = 0;
                while (nr >= 0 && nr < size && nc >= 0 && nc < size && board[nr][nc] == -piece) {
                    nr += dr[d]; nc += dc[d]; cnt++;
                }
                if (cnt && nr >= 0 && nr < size && nc >= 0 && nc < size && board[nr][nc] == piece) {
                    moves.emplace_back(r, c); break;
                }
            }
        }
    }

    // 石を置いて裏返す
    inline void place(int r, int c, int piece) {
        board[r][c] = piece;
        for (int d = 0; d < 8; ++d) {
            int nr = r + dr[d], nc = c + dc[d], cnt = 0;
            while (nr >= 0 && nr < size && nc >= 0 && nc < size && board[nr][nc] == -piece) {
                nr += dr[d]; nc += dc[d]; cnt++;
            }
            if (cnt && nr >= 0 && nr < size && nc >= 0 && nc < size && board[nr][nc] == piece) {
                int tr = r + dr[d], tc = c + dc[d];
                while (tr != nr || tc != nc) {
                    board[tr][tc] = piece;
                    tr += dr[d]; tc += dc[d];
                }
            }
        }
    }

    // 空きがあるか
    inline bool has_space() const {
        for (const auto& row : board) for (int x : row) if (x == 0) return true;
        return false;
    }

    // 石の数
    inline std::pair<int,int> count() const {
        int w = 0, b = 0;
        for (const auto& row : board) for (int x : row) { if (x == 1) w++; else if (x == -1) b++; }
        return {w, b};
    }
};

int main() {
    constexpr int size = 8;
    constexpr int games = 100000;  // 非常にたくさん自動対局
    int win_white = 0, win_black = 0;
    std::vector<std::pair<int,int>> moves;
    std::mt19937 rng((unsigned)std::time(nullptr));
    for (int t = 0; t < games; ++t) {
        Osero o(size);
        int turn = (t & 1) ? 1 : -1; // 交互に先手
        int pass = 0;
        while (o.has_space() && pass < 2) {
            o.get_moves(turn, moves);
            if (moves.empty()) { ++pass; turn = -turn; continue; }
            pass = 0;
            std::uniform_int_distribution<> dist(0, (int)moves.size()-1);
            auto mv = moves[dist(rng)];
            o.place(mv.first, mv.second, turn);
            turn = -turn;
        }
        auto [w, b] = o.count();
        if (w > b) win_white++;
        else win_black++;
        // 進捗表示は1000試合ごとなど
        if ((t+1) % (games/10) == 0) std::cout << (t+1) * 100 / games << "% ";
    }
    std::cout << "\n白(1)の勝ち: " << win_white << "\n黒(-1)の勝ち: " << win_black << std::endl;
    return 0;
}