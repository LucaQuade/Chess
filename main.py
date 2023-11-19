import pygame as game
import numpy as np
from engine import GameState
from engine import Move

#Declare size of window and divide it into 64 squares of equal size
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION

MAX_FPS = 15
IMAGES = {}

def load_images():
#Load images of pieces
    pieces = np.array(["wR", "wN", "wB", "wQ", "wK", "wp", "bR", "bN", "bB", "bQ", "bK", "bp"])
    for piece in pieces:
        IMAGES[piece] = game.transform.scale(game.image.load("images\\" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        
def main():
    game.init()
    screen = game.display.set_mode((WIDTH, HEIGHT))
    clock = game.time.Clock()
    screen.fill(game.Color("white"))
    state = GameState()
    load_images()
    running = True
    
    game_loop(screen, state, clock)
    
def game_loop(screen, state, clock):

    square = ()
    player_clicks = []
    
    #Generate valid moves for White's first turn
    valid_moves = state.valid_moves()
    move_made = False
    notation = ""
    
    while True:
        for e in game.event.get():
            if e.type == game.QUIT:
                return
            if e.type == game.MOUSEBUTTONDOWN:
                location = game.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                
                #If same square is clicked twice, reset selection
                if square == (row, col):
                    square = ()
                    player_clicks = []
                
                #If empty square is clicked, only add it to selection if another square was selected first
                elif len(player_clicks) == 0 and state.board[row][col] != "" or len(player_clicks) == 1:
                    square = (row, col)
                    player_clicks.append(square)
                    
                #After 2 squares were selected, check if move is legal. If it is, make the move
                #If move is not legal, reset selection and add the square that was just clicked
                if len(player_clicks) == 2:
                    move = Move(player_clicks[0], player_clicks[1], state.board)
                    if move in valid_moves:
                        state.make_move(move)
                        move_made = True
                        notation = move.get_notation()
                        if state.inCheck():
                            notation += '+'
                        if state.checkMate():
                            notation += "+"
                        square = ()
                        player_clicks = []
                    else: player_clicks = [square]
                    
            #After [Z] is pressed: undo last move, also reset selection
            elif e.type == game.KEYDOWN:
                if e.key == game.K_z:
                    state.undo_move()
                    move_made = True
                    square = ()
                    player_clicks = []
                    
        #After move was made or move was undone:
            #If move was made: Print chess notation of move
            #Check if game ended (Checkmate / Stalemate). If yes, print result and quit
            #Generate valid moves for next turn
            
        if move_made:
            if notation != "":
                print(notation)
            color = "Black" if state.whiteToMove else "White"
            if state.checkMate():
                print(color + " won by Checkmate!")
                return
            elif state.staleMate():
                print("Draw by Stalemate")
                return
            move_made = False
            notation = ""
            valid_moves = state.valid_moves()
            
        #update display of board
        draw_gamestate(screen, state)
        clock.tick(MAX_FPS)
        game.display.flip()
    
def draw_gamestate(screen, state):
    draw_board(screen)
    draw_pieces(screen, state.board)
    
def draw_board(screen):
    colors = [game.Color("white"), game.Color("grey")]
    
    #draw 8x8 board
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            game.draw.rect(screen, color, game.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    
def draw_pieces(screen, board):

    #for each square of board: if a piece is on it, draw piece on top of square
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], game.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                
if __name__ == "__main__":
    main()