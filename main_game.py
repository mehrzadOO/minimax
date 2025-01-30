import numpy as np
import pygame
import sys
import math
import random
from threading import Timer

# Colors
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Board dimensions
ROW_COUNT = 6
COLUMN_COUNT = 7

# Initialize pygame
pygame.init()

# Screen size
SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)

# Create screen
screen = pygame.display.set_mode(size)

# Font
font = pygame.font.SysFont("monospace", 75)

# Function to create board
def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

# Function to draw the board
def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[ROW_COUNT - 1 - r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[ROW_COUNT - 1 - r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()

# Function to check winning move
def winning_move(board, piece):
    # Horizontal
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    # Vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    # Positive Diagonal
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    # Negative Diagonal
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

# Function to evaluate board for AI
def evaluate_window(window, piece):
    opponent_piece = 1 if piece == 2 else 2
    score = 0
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2
    if window.count(opponent_piece) == 3 and window.count(0) == 1:
        score -= 4
    return score

# Function to calculate AI score
def score_position(board, piece):
    score = 0
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 6

    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)

    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

# Function for AI move
def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = [c for c in range(COLUMN_COUNT) if board[ROW_COUNT-1][c] == 0]
    is_terminal = winning_move(board, 1) or winning_move(board, 2) or len(valid_locations) == 0

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, 2):
                return (None, 100000000000000)
            elif winning_move(board, 1):
                return (None, -10000000000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, 2))

    if maximizing_player:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = np.where(board[:, col] == 0)[0][-1]
            temp_board = board.copy()
            temp_board[row][col] = 2
            new_score = minimax(temp_board, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = np.where(board[:, col] == 0)[0][-1]
            temp_board = board.copy()
            temp_board[row][col] = 1
            new_score = minimax(temp_board, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

# Game loop for AI mode
def ai_game():
    board = create_board()
    game_over = False
    turn = random.randint(0, 1)

    draw_board(board)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION and turn == 0:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN and turn == 0:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if np.any(board[:, col] == 0):
                    row = np.where(board[:, col] == 0)[0][-1]
                    board[row][col] = 1

                    if winning_move(board, 1):
                        label = font.render("Player wins!", True, RED)
                        screen.blit(label, (40, 10))
                        pygame.display.update()
                        pygame.time.wait(3000)
                        game_over = True

                    turn = 1
                    draw_board(board)

        if turn == 1 and not game_over:
            col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

            if np.any(board[:, col] == 0):
                row = np.where(board[:, col] == 0)[0][-1]
                board[row][col] = 2

                if winning_move(board, 2):
                    label = font.render("AI wins!", True, YELLOW)
                    screen.blit(label, (40, 10))
                    pygame.display.update()
                    pygame.time.wait(3000)
                    game_over = True

                turn = 0
                draw_board(board)

# Main menu
def main_menu():
    screen.fill(BLACK)
    title = font.render("Connect 4", True, YELLOW)
    screen.blit(title, (width // 4, height // 4))

    option1 = font.render("1. Two Players", True, RED)
    screen.blit(option1, (width // 6, height // 2 - 50))

    option2 = font.render("2. Play vs AI", True, RED)
    screen.blit(option2, (width // 6, height // 2 + 50))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "two_players"
                if event.key == pygame.K_2:
                    return "vs_ai"

# Game loop for two players
def two_player_game():
    board = create_board()
    game_over = False
    turn = 0

    draw_board(board)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
                else:
                    pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if np.any(board[:, col] == 0):
                    row = np.where(board[:, col] == 0)[0][-1]
                    board[row][col] = 1 if turn == 0 else 2

                    if winning_move(board, 1 if turn == 0 else 2):
                        label = font.render(f"Player {turn + 1} wins!", True, RED if turn == 0 else YELLOW)
                        screen.blit(label, (40, 10))
                        pygame.display.update()
                        pygame.time.wait(3000)
                        game_over = True

                    turn = (turn + 1) % 2

                    draw_board(board)

# Main logic
if __name__ == "__main__":
    mode = main_menu()
    if mode == "two_players":
        two_player_game()
    elif mode == "vs_ai":
        ai_game()
