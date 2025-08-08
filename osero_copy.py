# osero.py
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
        self.history = []
        self.turn = 0  # ←ここを 1 から 0 に修正
        self.not_piece = 0  # 置けない人数

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
        print("Turn:", self.turn + 1)
        print("  c " + " ".join(map(str, list(range(self.size)))))
        print("r + " + "- " * len(board[0]) + "+")
        for i, row in enumerate(board):
            print(str(i) + " | " + " ".join(row) + " |")  # map(str, row) を削除
        print("  + " + "- " * len(board[0]) + "+")

    def print_board_human_can_place(self, piece): # 人間用
        # "B" = -1 (黒), "W" = 1 (白), "." = 空き
        board = [['B' if cell == -1 else 'W' if cell == 1 else '.' for cell in row] for row in self.board]
        # 盤面の表示
        print("Othello Board(human):")
        print("Turn:", self.turn + 1)
        print("  c " + " ".join(map(str, list(range(self.size)))))
        print("r + " + "- " * len(board[0]) + "+")
        for i, row in enumerate(board):
            row_str = " ".join(row)
            # 駒を置ける場所を示す
            for j in range(len(row)):
                if self.can_place_piece(i, j, piece):
                    row_str = row_str[:j*2] + '*' + row_str[j*2+1:]
            print(str(i) + " | " + row_str + " |")
        print("  + " + "- " * len(board[0]) + "+")

    def print_board_pc(self): # PC用
        print("Othello Board(PC):")
        for row in self.board:
            print(row)

    def will_can_piece(self, row, col, task = False):
        self.not_piece += 1  # 置けない人数をカウント
        if self.not_piece >= 2:  # 置けない人数が2人
            s = set()
            print("Both players cannot move.")
            for r in range(self.size):
                for c in range(self.size):
                    if self.board[r][c] == 0:
                        for dr, dc in self.directions:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.size and 0 <= nc < self.size and (self.board[nr][nc] == 1 or self.board[nr][nc] == -1):
                                s.add((r, c))
            if (row, col) in s:
                return True if task == False else list(s)
        return False if task == False else []

    def can_place_piece(self, row = None, col = None, piece = None, task = False): # Github Copilotのから提供 Thanks! (自己改良済み)
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
        for dr, dc in self.directions:
            r, c = row + dr, col + dc
            found_opponent = False

            # 相手の駒が続いているか確認
            while 0 <= r < rows and 0 <= c < cols and board[r][c] == opponent_piece:
                found_opponent = True
                r += dr
                c += dc

            # 相手の駒が続いた後に自分の駒があるか確認
            if found_opponent and 0 <= r < rows and 0 <= c < cols and board[r][c] == piece:
                self.not_piece = 0  # 置ける場合は置けない人数をリセット
                return True

        # どの方向でも駒を置けない場合は専用関数を呼び出す
        return self.will_can_piece(row, col, task)

    def line_change_piece(self, row, col, piece): # Github Copilotのから提供 Thanks! (自己改良済み)
        # 盤面のサイズ
        board = self.board
        rows = len(board)
        cols = len(board[0])

        # 各方向を確認して裏返す
        for dr, dc in self.directions:
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
                    # 履歴に記録
                    self.history[-1]["row"].append(pr)
                    self.history[-1]["col"].append(pc)

    def add_piece(self, row, col, piece):
        board = self.board
        if row < 0 or row >= len(board) or col < 0 or col >= len(board[0]):
            raise ValueError("Row or column out of bounds")
        if self.can_place_piece(row, col, piece):
            board[row][col] = piece
            # ここで履歴を切り詰める
            if len(self.history) > self.turn:
                self.history = self.history[:self.turn]
            self.history.append({"row": [row], "col": [col], "piece": piece})
            self.turn += 1
            self.line_change_piece(row, col, piece)
        else:
            raise ValueError("Invalid move")

    def isnot_finished(self):
        # 盤面に空きがあるか確認
        for row in self.board:
            if 0 in row:
                return True
        return False

    def count_pieces(self):
        # どちらが多いか
        count = {1: 0, -1: 0, 0: 0}
        for row in self.board:
            for cell in row:
                if cell in count:
                    count[cell] += 1
        return count

    def piece_back(self):
        # 最後の手を戻す
        if self.turn <= 0:  # ←ここも0に修正
            raise ValueError("No moves to undo")
        print("piece_back")
        last_move = self.history[self.turn - 1]
        row, col = last_move["row"][0], last_move["col"][0]
        piece = last_move["piece"]
        self.board[row][col] = 0
        for i, j in zip(last_move["row"][1:], last_move["col"][1:]):
            self.board[i][j] = -piece
        self.turn -= 1
        return -piece  # 次に打つべき駒の色

    def piece_forward(self):
        # 最後の手を進める
        if self.turn >= len(self.history):
            raise ValueError("No moves to redo")
        print("piece_forward")
        last_move = self.history[self.turn]
        row, col = last_move["row"][0], last_move["col"][0]
        piece = last_move["piece"]
        self.board[row][col] = piece
        for i, j in zip(last_move["row"][1:], last_move["col"][1:]):
            self.board[i][j] = piece
        self.turn += 1
        return -piece  # 次に打つべき駒の色

def main():
    import random
    import time
    size = int(input("Enter board size (default 8): ") or 8)
    piece = int(input("Enter your piece (1 or -1): "))
    if piece not in [1, -1]:
        print("Invalid piece. Please enter 1 or -1.")
        return "Invalid piece start"

    maps = []
    di = {1:0, -1:0}
    n = int(input("Enter number of games to play (default 10): ") or 10)
    for j in range(n):
        board = osero(size)
        turn_piece = [1, -1][j % 2]
        pass_count = 0  # 連続パス回数
        while board.isnot_finished():
            count = board.count_pieces()
            can_li = board.can_place_piece(turn_piece, task=True)
            try:
                row, col = random.choice(can_li)
                board.add_piece(row, col, turn_piece)
                turn_piece = 1 if turn_piece == -1 else -1
            except ValueError as e:
                print(e)
            except KeyboardInterrupt:
                print("\nGame interrupted by user.")
                return "Game interrupted"
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Please contact the developer.")
        count = board.count_pieces()
        x = 1 if count[1] > count[-1] else -1
        try:
            maps.append((board, count))
            di[x] += 1
        except:
            pass
        # 進捗
        if j % (n // 10) == 0:
            print(f"Progress: {j * 100 // n}%")
    print("Game results:")
    """for i, (b, c) in enumerate(maps):
        print(f"Game {i+1}:")
        b.print_board_human()
        print(f"Count -> " + ", ".join(f"{k}: {v}" for k, v in c.items()) + ":")
    """
    print(di)
    input("Press Enter to exit...")
    return 0

if __name__ == "__main__":
    n = main()
    print("Exit code:", n)