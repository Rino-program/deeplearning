#include <iostream>
#include <vector>
#include <tuple>
#include <string>
#include <fstream>
#include <sstream>
#include <random>
#include <ctime>
#include <map>
#include <algorithm>

// オセロのクラス定義
class Osero {
public:
    int size;
    std::vector<std::pair<int, int>> directions;
    std::vector<std::vector<int>> board;
    std::vector<std::map<std::string, std::vector<int>>> history;
    int turn;

    Osero(int size_ = 8) : size(size_), turn(0) {
        // 8方向
        directions = {
            {-1, 0},  // 上
            {1, 0},   // 下
            {0, -1},  // 左
            {0, 1},   // 右
            {-1, -1}, // 左上
            {-1, 1},  // 右上
            {1, -1},  // 左下
            {1, 1}    // 右下
        };

        board = std::vector<std::vector<int>>(size, std::vector<int>(size, 0));
        int mid = size / 2;
        // 初期配置
        board[mid - 1][mid - 1] = 1;
        board[mid][mid] = 1;
        board[mid - 1][mid] = -1;
        board[mid][mid - 1] = -1;
    }

    std::vector<std::vector<int>> load_board_from_file(const std::string& filename) {
        std::vector<std::vector<int>> loaded_board;
        std::ifstream infile(filename);
        std::string line;
        while (std::getline(infile, line)) {
            std::vector<int> row;
            std::istringstream iss(line);
            int cell;
            while (iss >> cell) {
                row.push_back(cell);
            }
            loaded_board.push_back(row);
        }
        return loaded_board;
    }

    void print_board_human() const {
        std::cout << "Othello Board(human):" << std::endl;
        std::cout << "Turn: " << turn + 1 << std::endl;
        std::cout << "  c ";
        for (int i = 0; i < size; ++i) std::cout << i << " ";
        std::cout << std::endl;
        std::cout << "r + ";
        for (int i = 0; i < size; ++i) std::cout << "- ";
        std::cout << "+" << std::endl;
        for (int i = 0; i < size; ++i) {
            std::cout << i << " | ";
            for (int j = 0; j < size; ++j) {
                char ch = '.';
                if (board[i][j] == -1) ch = 'B';
                else if (board[i][j] == 1) ch = 'W';
                std::cout << ch << " ";
            }
            std::cout << "|" << std::endl;
        }
        std::cout << "  + ";
        for (int i = 0; i < size; ++i) std::cout << "- ";
        std::cout << "+" << std::endl;
    }

    void print_board_human_can_place(int piece) const {
        std::cout << "Othello Board(human):" << std::endl;
        std::cout << "Turn: " << turn + 1 << std::endl;
        std::cout << "  c ";
        for (int i = 0; i < size; ++i) std::cout << i << " ";
        std::cout << std::endl;
        std::cout << "r + ";
        for (int i = 0; i < size; ++i) std::cout << "- ";
        std::cout << "+" << std::endl;
        for (int i = 0; i < size; ++i) {
            std::cout << i << " | ";
            for (int j = 0; j < size; ++j) {
                char ch = '.';
                if (board[i][j] == -1) ch = 'B';
                else if (board[i][j] == 1) ch = 'W';
                if (can_place_piece(i, j, piece)) ch = '*';
                std::cout << ch << " ";
            }
            std::cout << "|" << std::endl;
        }
        std::cout << "  + ";
        for (int i = 0; i < size; ++i) std::cout << "- ";
        std::cout << "+" << std::endl;
    }

    void print_board_pc() const {
        std::cout << "Othello Board(PC):" << std::endl;
        for (const auto& row : board) {
            for (auto cell : row) std::cout << cell << " ";
            std::cout << std::endl;
        }
    }

    bool can_place_piece(int row, int col, int piece) const {
        if (row < 0 || row >= size || col < 0 || col >= size || board[row][col] != 0)
            return false;
        int opponent_piece = (piece == -1) ? 1 : -1;

        for (const auto& dir : directions) {
            int r = row + dir.first, c = col + dir.second;
            bool found_opponent = false;
            while (r >= 0 && r < size && c >= 0 && c < size && board[r][c] == opponent_piece) {
                found_opponent = true;
                r += dir.first;
                c += dir.second;
            }
            if (found_opponent && r >= 0 && r < size && c >= 0 && c < size && board[r][c] == piece)
                return true;
        }
        return false;
    }

    void line_change_piece(int row, int col, int piece) {
        int rows = size, cols = size;
        for (const auto& dir : directions) {
            int r = row + dir.first, c = col + dir.second;
            std::vector<std::pair<int, int>> path;
            while (r >= 0 && r < rows && c >= 0 && c < cols && board[r][c] != 0 && board[r][c] != piece) {
                path.push_back({r, c});
                r += dir.first;
                c += dir.second;
            }
            if (r >= 0 && r < rows && c >= 0 && c < cols && board[r][c] == piece) {
                for (const auto& p : path) {
                    board[p.first][p.second] = piece;
                    history.back()["row"].push_back(p.first);
                    history.back()["col"].push_back(p.second);
                }
            }
        }
    }

    void add_piece(int row, int col, int piece) {
        if (row < 0 || row >= size || col < 0 || col >= size)
            throw std::invalid_argument("Row or column out of bounds");
        if (can_place_piece(row, col, piece)) {
            board[row][col] = piece;
            if ((int)history.size() > turn)
                history.resize(turn);
            history.push_back({{"row", {row}}, {"col", {col}}, {"piece", {piece}}});
            turn += 1;
            line_change_piece(row, col, piece);
        } else {
            throw std::invalid_argument("Invalid move");
        }
    }

    bool isnot_finished() const {
        for (const auto& row : board) {
            if (std::find(row.begin(), row.end(), 0) != row.end())
                return true;
        }
        return false;
    }

    std::map<int, int> count_pieces() const {
        std::map<int, int> count{{1, 0}, {-1, 0}, {0, 0}};
        for (const auto& row : board) {
            for (auto cell : row) {
                if (count.find(cell) != count.end())
                    count[cell]++;
            }
        }
        return count;
    }

    int piece_back() {
        if (turn <= 0)
            throw std::invalid_argument("No moves to undo");
        std::cout << "piece_back" << std::endl;
        const auto& last_move = history[turn - 1];
        int row = last_move.at("row")[0], col = last_move.at("col")[0];
        int piece = last_move.at("piece")[0];
        board[row][col] = 0;
        auto row_it = last_move.at("row").begin() + 1;
        auto col_it = last_move.at("col").begin() + 1;
        for (; row_it != last_move.at("row").end() && col_it != last_move.at("col").end(); ++row_it, ++col_it) {
            board[*row_it][*col_it] = -piece;
        }
        turn -= 1;
        return -piece;
    }

    int piece_forward() {
        if (turn >= (int)history.size())
            throw std::invalid_argument("No moves to redo");
        std::cout << "piece_forward" << std::endl;
        const auto& last_move = history[turn];
        int row = last_move.at("row")[0], col = last_move.at("col")[0];
        int piece = last_move.at("piece")[0];
        board[row][col] = piece;
        auto row_it = last_move.at("row").begin() + 1;
        auto col_it = last_move.at("col").begin() + 1;
        for (; row_it != last_move.at("row").end() && col_it != last_move.at("col").end(); ++row_it, ++col_it) {
            board[*row_it][*col_it] = piece;
        }
        turn += 1;
        return -piece;
    }

    std::vector<std::pair<int, int>> piece_proposal(int piece) const {
        std::vector<std::pair<int, int>> proposals;
        for (int r = 0; r < size; ++r) {
            for (int c = 0; c < size; ++c) {
                if (can_place_piece(r, c, piece)) {
                    proposals.push_back({r, c});
                }
            }
        }
        return proposals;
    }
};

int main() {
    std::srand((unsigned int)std::time(nullptr));
    int size;
    std::cout << "Enter board size (default 8): ";
    std::string size_in;
    std::getline(std::cin, size_in);
    size = size_in.empty() ? 8 : std::stoi(size_in);

    int piece;
    std::cout << "Enter your piece (1 or -1): ";
    std::string piece_in;
    std::getline(std::cin, piece_in);
    piece = piece_in.empty() ? 1 : std::stoi(piece_in);
    if (piece != 1 && piece != -1) {
        std::cout << "Invalid piece. Please enter 1 or -1." << std::endl;
        std::cout << "Invalid piece start" << std::endl;
        return 1;
    }

    std::vector<std::tuple<Osero, std::map<int, int>>> maps;
    std::map<int, int> di{{1, 0}, {-1, 0}};
    int n;
    std::cout << "Enter number of games to play (default 10): ";
    std::string n_in;
    std::getline(std::cin, n_in);
    n = n_in.empty() ? 10 : std::stoi(n_in);

    for (int j = 0; j < n; ++j) {
        Osero board(size);
        int turn_piece = (j % 2 == 0) ? 1 : -1;
        int pass_count = 0;
        while (board.isnot_finished()) {
            auto count = board.count_pieces();
            auto can_li = board.piece_proposal(turn_piece);
            if (can_li.empty()) {
                turn_piece = (turn_piece == -1) ? 1 : -1;
                board.turn += 1;
                pass_count += 1;
                if (pass_count >= 2) {
                    std::cout << "Both players cannot move. Game over." << std::endl;
                    break;
                }
                continue;
            }
            pass_count = 0;
            try {
                std::pair<int, int> move = can_li[std::rand() % can_li.size()];
                board.add_piece(move.first, move.second, turn_piece);
                turn_piece = (turn_piece == -1) ? 1 : -1;
            } catch (const std::exception& e) {
                std::cout << e.what() << std::endl;
            }
        }
        auto count = board.count_pieces();
        int x = (count[1] > count[-1]) ? 1 : -1;
        try {
            maps.push_back(std::make_tuple(board, count));
            di[x]++;
        } catch (...) {
        }
        if (j % std::max(1, n / 10) == 0) {
            std::cout << "Progress: " << j * 100 / n << "%" << std::endl;
        }
    }
    std::cout << "Game results:" << std::endl;
    // 結果表示省略
    std::cout << "1: " << di[1] << ", -1: " << di[-1] << std::endl;
    std::cout << "Press Enter to exit..." << std::endl;
    std::cin.get();
    return 0;
}