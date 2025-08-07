# osero.py
"""
今後の目標
一手戻る機能 -> 間違い修正 -> 履歴を残す
置く座標を分かりやすく
出力を見やすく(日本語化とか？)
駒が置けなくなった時の対処法
投了機能
駒が置ける所を提案
class化 # 完了！
"""
class osero:
    def __init__(self, size = 8):
        self.size = size
        # 駒を置けるかチェックする方向
        self.directions = [
            (-1, 0),  # 上
            (1, 0),   # 下
            (0, -1),  # 左
            (0, 1),   # 右
            (-1, -1), # 左上
            (-1, 1),  # 右上
            (1, -1),  # 左下
            (1, 1)    # 右下
        ]
        import sys

        # Github Copilotのから提供 Thanks!
        """
        今後の予定
        強化学習に対応するために複数マップをすようできるようにする。
        案：
        initの引数で個数指定またはadd_board関数を作って実行
        動かすボードを引数で指定できるようにする
        """
        board_init = [[0 for _ in range(size)] for _ in range(size)]
        mid = size // 2
        # 初期配置
        board_init[mid-1][mid-1] = 1
        board_init[mid][mid] = 1
        board_init[mid-1][mid] = -1
        board_init[mid][mid-1] = -1
        self.board = board_init

    def load_board_from_file(self, filename):
        board = []
        with open(filename, 'r') as file:
            for line in file:
                row = [int(cell) for cell in line.strip().split()]  # 空白を分割して整数に変換
                board.append(row)
        return board

    def print_board_human(self): # 人間用
        # "B" = -1 (黒), "W" = 1 (白), "." = 空き
        board = [['B' if cell == -1 else 'W' if cell == 1 else '.' for cell in row] for row in self.board]
        # 盤面の表示
        print("Othello Board(human):")
        print("  c " + " ".join(map(str, list(range(self.size)))))
        print("r + " + "- " * len(board[0]) + "+")
        for i, row in enumerate(board):
            print(str(i) + " | " + " ".join(row) + " |")  # map(str, row) を削除
        print("  + " + "- " * len(board[0]) + "+")

    def print_board_pc(self): # PC用
        print("Othello Board(PC):")
        for row in self.board:
            print(row)

    def can_place_piece(self, row, col, piece): # Github Copilotのから提供 Thanks!
        # 盤面のサイズ
        board = self.board
        rows = len(board)
        cols = len(board[0])

        # 駒の種類と相手の駒を定義
        opponent_piece = 1 if piece == -1 else -1

        # 座標が盤面外の場合、またはすでに駒が置かれている場合はFalse
        if row < 0 or row >= rows or col < 0 or col >= cols or board[row][col] != 0:
            return False

        # 8方向を確認
        for dr, dc in directions:
            r, c = row + dr, col + dc
            found_opponent = False

            # 相手の駒が続いているか確認
            while 0 <= r < rows and 0 <= c < cols and board[r][c] == opponent_piece:
                found_opponent = True
                r += dr
                c += dc

            # 相手の駒が続いた後に自分の駒があるか確認
            if found_opponent and 0 <= r < rows and 0 <= c < cols and board[r][c] == piece:
                return True

        # どの方向でも駒を置けない場合はFalse
        return False

    def line_change_piece(self, row, col, piece): # Github Copilotのから提供 Thanks!
        # 盤面のサイズ
        board = self.board
        rows = len(board)
        cols = len(board[0])

        # 各方向を確認して裏返す
        for dr, dc in directions:
            r, c = row + dr, col + dc
            path = []  # 挟んだ駒の座標を記録するリスト
            while 0 <= r < rows and 0 <= c < cols and board[r][c] != 0 and board[r][c] != piece:
                path.append((r, c))
                r += dr
                c += dc

            # 挟んだ駒がある場合、裏返す
            if 0 <= r < rows and 0 <= c < cols and board[r][c] == piece:
                for pr, pc in path:
                    self.board[pr][pc] = piece

    def add_piece(self, row, col, piece):
        # 駒を置く前に、置けるか確認
        board = self.board
        if row < 0 or row >= len(board) or col < 0 or col >= len(board[0]):
            raise ValueError("Row or column out of bounds")
        if can_place_piece(row, col, piece):
            board[row][col] = piece
            line_change_piece(row, col, piece)  # 追加: 駒を置いた後に裏返す処理を呼び出す
        else:
            raise ValueError("Invalid move")

    def isnot_finished(self):
        # 盤面に空きがあるか確認
        for row in self.board:
            if 0 in row:
                return True
        return False

    # どちらが多いか
    def count_pieces(self):
        count = {1: 0, -1: 0, 0: 0}
        for row in self.board:
            for cell in row:
                if cell in count:
                    count[cell] += 1
        return count

def main():
    board = osero()
    board.print_board_pc()
    board.print_board_human()

    piece = int(input("Enter your piece (1 or -1): "))
    if piece not in [1, -1]:
        print("Invalid piece. Please enter 1 or -1.")
        return

    while board.isnot_finished():
        print("Current board:")
        count = board.count_pieces()
        print(f"Count -> 1: {count[1]}, -1: {count[-1]}, Empty: {count[0]}")
        board.print_board_human()
        print(f"Your piece: {piece}")
        try:
            col = int(input("Enter column (0-7): "))
            row = int(input("Enter row (0-7): "))
            board.add_piece(row, col, piece)
            piece = 1 if piece == -1 else -1  # Switch pieces
        except ValueError as e:
            print(e)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please contact the developer.")
    print("finish!\nFinal board:")
    count = board.count_pieces()
    print(f"Count -> 0: {count[1]}, 1: {count[-1]}, Empty: {count[0]}")
    board.print_board_human()

if __name__ == "__main__":
    main()
