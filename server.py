import sys
import pandas as pd
import numpy as np

sys.stdout.write("Welcome to Othello(Reversi) Game!\n")
input("Press Enter to start the game...")
sys.stdout.write('Game starts now!\n')
turn = 'Black'
board = {}
# 보드생성
col_map = {chr(ord('A') + i): i for i in range(8)}
row_map = {str(i): i for i in range(8)}
inv_col_map = {v: k for k, v in col_map.items()}
inv_row_map = {v: k for k, v in row_map.items()}
where_set_dict = dict()

# 기능(함수)
def create_board_df():
    # 현재 보드를 Pandas와 DataFrame으로 변환
    df = pd.DataFrame(np.full((8, 8), '-'), index=list('01234567'), columns=list('ABCDEFGH'), dtype=str)
    for (r, c), piece in board.items():
        df.at[inv_row_map[r], inv_col_map[c]] = piece
    # 가능한 위치에 * 표시
    for pos_key in where_set_dict.keys():
        col, row = pos_key[0], pos_key[1]
        # 이미 돌이 놓여있지 않은 곳만 *로 표시
        if df.at[row, col] == '-':
            df.at[row, col] = '*'
    return df

def reset_game():
    # 게임 초기화
    global turn, board, where_set_dict
    turn = 'Black'
    board = {
        (3, 3): 'W', (3, 4): 'B',
        (4, 3): 'B', (4, 4): 'W'
    }
    where_set_dict.clear()

def where_set(current_turn):
    # 가능한 움직임을 찾고 그 움직임을 where_set_dict에 저장
    # 상대 돌을 최소한 하나 이상 뒤집을 수 있는 위치를 찾기
    global board, where_set_dict
    where_set_dict.clear()
    player_piece = 'B' if current_turn == 'Black' else 'W'
    opponent_piece = 'W' if current_turn == 'Black' else 'B'

    for r_start in range(8):
        for c_start in range(8):
            # 빈 공간에만 놓을 수 있음
            if (r_start, c_start) in board:
                continue

            # 주변 8칸을 확인
            for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                pieces_to_flip = []
                r, c = r_start + dr, c_start + dc

                # 상대 돌이 있는지 확인
                while 0 <= r < 8 and 0 <= c < 8 and board.get((r, c)) == opponent_piece:
                    pieces_to_flip.append((r, c))
                    r += dr
                    c += dc

                # 상대 돌이 있고, 그 끝에 자신의 돌이 있는 경우 그 수는 유효한 수임
                if 0 <= r < 8 and 0 <= c < 8 and board.get((r, c)) == player_piece:
                    if pieces_to_flip:
                        pos_key = f"{inv_col_map[c_start]}{inv_row_map[r_start]}"
                        if pos_key not in where_set_dict:
                            where_set_dict[pos_key] = []
                        where_set_dict[pos_key].extend(pieces_to_flip)

def make_move(pos_key, current_turn):
    # 돌을 놓고 상대 돌을 뒤집기
    global board
    player_piece = 'B' if current_turn == 'Black' else 'W'
    
    # 돌 놓기
    col, row_str = pos_key[0], pos_key[1]
    r, c = row_map[row_str], col_map[col]
    board[(r, c)] = player_piece

    # 상대 돌 뒤집기
    for r_flip, c_flip in where_set_dict[pos_key]:
        board[(r_flip, c_flip)] = player_piece

def check_game_end():
    # 게임이 끝났는지 확인하고 결과 출력
    black_count = sum(1 for piece in board.values() if piece == 'B')
    white_count = sum(1 for piece in board.values() if piece == 'W')
    
    sys.stdout.write(f"Game Over!\nBlack: {black_count} - White: {white_count}\n")
    if black_count > white_count:
        sys.stdout.write('Black Wins!\n')
    elif white_count > black_count:
        sys.stdout.write('White Wins!\n')
    else:
        sys.stdout.write('Draw!\n')

    # 게임 재시작 여부 묻기
    sys.stdout.write('Play again? (Y/N): ')
    sys.stdout.flush()
    user_input = sys.stdin.readline().strip().upper()
    while user_input not in ['Y', 'N']:
        sys.stdout.write('Invalid input. Play again? (Y/N): ')
        sys.stdout.flush()
        user_input = sys.stdin.readline().strip().upper()
    
    if user_input == 'Y':
        sys.stdout.write("\nStarting new game...\n")
        reset_game()
        game()
    else:
        sys.exit()

def game():
    # 메인 게임 루프
    global turn
    passes = 0
    reset_game()

    while True:
        # 게임이 끝났는지 확인
        board_full = len(board) == 64
        no_pieces = not any(p == 'B' for p in board.values()) or not any(p == 'W' for p in board.values())
        
        if passes >= 2 or board_full or no_pieces:
            sys.stdout.write(str(create_board_df()) + '\n')
            check_game_end()
            break

        # 현재 턴의 가능한 위치 찾기
        where_set(turn)

        if not where_set_dict:
            sys.stdout.write(str(create_board_df()) + '\n')
            sys.stdout.write(f"{turn} has no available moves. Turn passes.\n")
            passes += 1
            turn = 'White' if turn == 'Black' else 'Black'
            continue
        
        # 가능한 움직임이면 아래의 변수 초기화
        passes = 0

        # 현재 보드 출력
        sys.stdout.write(str(create_board_df()) + '\n')
        sys.stdout.write(f"{turn}'s turn.\n")
        sys.stdout.write(f"Available moves: {sorted(list(where_set_dict.keys()))}\n")
        
        # 사용자 입력 받기
        pos_key = ''
        while pos_key not in where_set_dict:
            sys.stdout.write('Enter your move (ex. E3): ')
            sys.stdout.flush()
            pos_key = sys.stdin.readline().strip().upper()
            if pos_key not in where_set_dict:
                sys.stdout.write("Invalid move. Please choose from the available moves.\n")

        # 보드를 업데이트하고 턴 바꾸기
        make_move(pos_key, turn)
        turn = 'White' if turn == 'Black' else 'Black'
        sys.stdout.write("\n")

# 게임 시작하기
if __name__ == "__main__":
    game()
