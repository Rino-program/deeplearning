# osero.py
class osero:
    def __init__(self, size = 8):
        self.size = size
        self.directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        board_init = [[0 for _ in range(size)] for _ in range(size)]
        mid = size // 2
        board_init[mid-1][mid-1] = 1
        board_init[mid][mid] = 1
        board_init[mid-1][mid] = -1
        board_init[mid][mid-1] = -1
        self.board = board_init
        self.history = []
        self.turn = 0

    def load_board_from_file(self, filename):
        """ファイルからボードを読み込む"""
        board = []
        with open(filename, 'r') as file:
            for line in file:
                row = [int(cell) for cell in line.strip().split()]  # 空白を分割して整数に変換
                board.append(row)
        return board

    def print_board_human(self): # 人間用
        """人が読み取りやすいマップを表示"""
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
        """人が読み取りやすいマップを表示しながら置ける場所を示す"""
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
        """PC用の盤面を表示(内部データをそのまま表示)"""
        print("Othello Board(PC):")
        for row in self.board:
            print(row)

    def can_place_piece(self, row, col, piece):
        board = self.board
        rows = len(board)
        cols = len(board[0])
        opponent_piece = 1 if piece == -1 else -1
        if row < 0 or row >= rows or col < 0 or col >= cols or board[row][col] != 0:
            return False
        for dr, dc in self.directions:
            r, c = row + dr, col + dc
            found_opponent = False
            while 0 <= r < rows and 0 <= c < cols and board[r][c] == opponent_piece:
                found_opponent = True
                r += dr
                c += dc
            if found_opponent and 0 <= r < rows and 0 <= c < cols and board[r][c] == piece:
                return True
        return False

    def will_can_piece(self, piece):
        """置けるところをリストで返す"""
        li_can = []
        for r in range(self.size):
            for c in range(self.size):
                if self.can_place_piece(r, c, piece):
                    li_can.append((r, c))
        return li_can

    def line_change_piece(self, row, col, piece): # Github Copilotのから提供 Thanks! (自己改良済み)
        """置いた駒に応じて裏返す"""
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
        """盤面に駒を置く"""
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
            print(row, col, piece)
            raise ValueError("Invalid move")

    def isnot_finished(self):
        """ゲームが終了しているか確認"""
        # 盤面に空きがあるか確認
        for row in self.board:
            if 0 in row:
                return True
        return False

    def count_pieces(self):
        """盤面にある駒の数をカウント"""
        # どちらが多いか
        count = {1: 0, -1: 0, 0: 0}
        for row in self.board:
            for cell in row:
                if cell in count:
                    count[cell] += 1
        return count

def main():
    """オセロ実行メイン関数 """
    import random
    import time
    size = int(input("Enter board size (default 8): ") or 8)
    piece = int(input("Enter your piece (1 or -1)(default 1): ") or 1)
    if piece not in [1, -1]:
        print("Invalid piece. Please enter 1 or -1")
        return "Invalid piece start"

    maps = []
    di = {1:0, -1:0}
    game_over = 0
    n = int(input("Enter number of games to play (default 100): ") or 100)
    for j in range(n):
        board = osero(size)
        turn_piece = [1, -1][j % 2]
        pass_count = 0
        while board.isnot_finished():
            can_li = board.will_can_piece(piece=turn_piece)
            if not can_li:
                pass_count += 1
                if pass_count >= 2:
                    game_over += 1
                    print(f"Game {j+1} over.")
                    break
                turn_piece = 1 if turn_piece == -1 else -1
                continue
            else:
                pass_count = 0
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
        if j % (n // 10) == 0:
            print(f"Progress: {j * 100 // n}%")
    print("Game results:")
    print(di)
    input("Press Enter to exit...")
    return 0

if __name__ == "__main__":
    n = main()
    print("Exit code:", n)