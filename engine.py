import numpy as np

class GameState():

    def __init__(self):
    
        #Initialize board
        empty_row = np.array(["--", "--", "--", "--", "--", "--", "--", "--"])
        self.board = np.array([
        ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
        empty_row,
        empty_row,
        empty_row,
        empty_row,
        ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
        ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]])
        
        #Who's turn is it?
        self.whiteToMove = True
        
        #Remember which Kings and Rooks where previously moved (Important for Castling)
        self.whiteKingMoved = False
        self.blackKingMoved = False
        self.leftWhiteRookMoved = False
        self.rightWhiteRookMoved = False
        self.leftBlackRookMoved = False
        self.rightBlackRookMoved = False
        
        #Remember current location of both Kings (Important for Checks)
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        
        #List of all moves that were made
        self.moveLog = []
        
    def make_move(self, move):
        
        #Add move to list
        self.moveLog.append(move)
    
        #Move piece from start square to end square
        self.board[move.start[0]][move.start[1]] = "--"
        self.board[move.end[0]][move.end[1]] = move.pieceMoved
        
        if move.pieceMoved[1] == 'p':
            #If move was En passant: Remove piece from square below/above (Depending on player color) end square
            if move.pieceCaptured == "--" and move.end[1] != move.start[1]:
                if self.whiteToMove:
                    self.board[move.end[0]+1][move.end[1]] = "--"
                else: self.board[move.end[0]-1][move.end[1]] = "--"
            #If move was pawn promotion: Replace pawn with Queen
            #To-Do: Enable players to choose to which piece the pawn is promoted
            if move.end[0] == 0 or move.end[0] == 7:
                self.board[move.end] = move.pieceMoved[0] + 'Q'
        
        #If King was moved: Update king location
        if move.pieceMoved[1] == 'K':
            if move.pieceMoved[0] == 'b':
                self.blackKingLocation = move.end
            else: self.whiteKingLocation = move.end
        
        #Update Kings and Rooks moved
        #Previously there was a bug where a player could Castle with a Rook that was captured the turn before
        self.updatePiecesMoved()
        
        #If move was Castle: Set Rook to the square to the left/right (Depending on long/short Castle) of end square
        if move.pieceMoved[1] == 'K':
            if move.start[1] < move.end[1]-1:
                self.board[move.end[0]][move.end[1]-1] = move.pieceMoved[0] + 'R'
                self.board[move.end[0]][move.end[1]+1] = "--"
            elif move.start[1] > move.end[1]+1:
                self.board[move.end[0]][move.end[1]+1] = move.pieceMoved[0] + 'R'
                self.board[move.end[0]][move.end[1]-2] = "--"
        
        #Switch who's turn it is
        self.whiteToMove = not self.whiteToMove
        
    def undo_move(self):
    
        #Mirror of make_move
        #Exactly undo everything done in make_move
    
        if len(self.moveLog) > 0:
        
            #Remove last move from list
            last_move = self.moveLog.pop()
            
            #Move piece from end square to start square
            self.board[last_move.start[0]][last_move.start[1]] = last_move.pieceMoved
            self.board[last_move.end[0]][last_move.end[1]] = last_move.pieceCaptured
            
            if last_move.pieceMoved[1] == 'p':
            
                #If move was En passant: Add pawn of enemy color to square below/above end square
                if last_move.pieceCaptured == "--" and last_move.end[1] != last_move.start[1]:
                    if self.whiteToMove:
                        self.board[last_move.end[0]-1][last_move.end[1]] = "wp"
                    else: self.board[last_move.end[0]+1][last_move.end[1]] = "bp"
                    
                #If last move was pawn promotion: Replace promoted piece with pawn
                if last_move.end[0] == 0 or last_move.end[0] == 7:
                    self.board[last_move.start] = last_move.pieceMoved[0] + 'p'
                    
            #Update Kings and Rooks moved
            self.updatePiecesMoved()
                    
            if last_move.pieceMoved[1] == 'K':
                
                #If King was moved: Update king location
                if last_move.pieceMoved[0] == 'b':
                    self.blackKingLocation = last_move.start
                else: self.whiteKingLocation = last_move.start
                
                #If move was Castle: Move Rook back to its starting square
                if last_move.start[1] < last_move.end[1]-1:
                    self.board[last_move.end[0]][last_move.end[1]+1] = last_move.pieceMoved[0] + 'R'
                    self.board[last_move.end[0]][last_move.end[1]-1] = "--"
                elif last_move.start[1] > last_move.end[1]+1:
                    self.board[last_move.end[0]][last_move.end[1]-2] = last_move.pieceMoved[0] + 'R'
                    self.board[last_move.end[0]][last_move.end[1]+1] = "--"
                    
            #Update who's turn it is
            self.whiteToMove = not self.whiteToMove
        
    def valid_moves(self):
    
        #Idea: Generate all possible moves for every (White/Black) piece
        #Then check for every possible move, if that move leaves the player in Check (Not valid!)
        
        moves = self.possible_moves()
        
        #Go through move list in reverse order to not mess up indexing when removing moves
        for i in range(len(moves)-1, -1, -1):
        
            #For every possible move: Make the move. Then check if it leaves the player in Check
            #If yes: Remove this move from the list. Then undo the move
            self.make_move(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undo_move()
        return moves
        
    def possible_moves(self):
    
        moves = []
        #For every square: If square contains a piece of current player: Generate possible moves for that piece
        for row in range(8):
            for col in range(8):
                if self.board[row][col] != "--":
                    pieceColor = self.board[row][col][0]
                    if (pieceColor == 'w' and self.whiteToMove) or (pieceColor == 'b' and not self.whiteToMove):
                        piece = self.board[row][col][1]
                        self.getPieceMoves(piece, row, col, moves)
 
        return moves
                        
    def getPieceMoves(self, piece, row, col, moves):
    
        if piece == 'p':
            self.getPawnMoves(row, col, moves)
        elif piece == 'R':
            self.getRookMoves(row, col, moves)
        elif piece == 'N':
            self.getKnightMoves(row, col, moves)
        elif piece == 'B':
            self.getBishopMoves(row, col, moves)
        elif piece == 'Q':
            self.getQueenMoves(row, col, moves)
        elif piece == 'K':
            self.getKingMoves(row, col, moves)
        
    def getPawnMoves(self, row, col, moves):
    
        moveDirection = -1 if self.whiteToMove else 1
        startRow = 6 if self.whiteToMove else 1
        enPassantRow = 3 if self.whiteToMove else 4
        enemyColor = 'b' if self.whiteToMove else 'w'

        #Single square forward
        if self.board[row + moveDirection][col] == "--":
            moves.append(Move((row, col), (row + moveDirection, col), self.board))
                
            #Two squares forward (Only if pawn hasn't moved yet)
            if row == startRow and self.board[row + (2*moveDirection)][col] == "--":
                moves.append(Move((row, col), (row + (2*moveDirection), col), self.board))
                    
        #Capture: Pawn can move one square diagonally up, if that square contains enemy piece
        if col > 0 and self.board[row + moveDirection][col-1][0] == enemyColor:
            moves.append(Move((row, col), (row + moveDirection, col-1), self.board))
        if col < 7 and self.board[row + moveDirection][col+1][0] == enemyColor:
            moves.append(Move((row, col), (row + moveDirection, col+1), self.board))
                
        #En passant: If an enemy pawn went two squares forward to pass this pawn in the previous turn:
        #Pawn can capture enemy pawn by moving one square diagonally up
        if (row == enPassantRow and self.moveLog[-1].pieceMoved == enemyColor + 'p'
            and self.moveLog[-1].start[0] == 7 - startRow):
            if col > 0 and self.moveLog[-1].end == (row, col-1):
                moves.append(Move((row,col), (row + moveDirection, col-1), self.board))
            if col < 7 and self.moveLog[-1].end == (row, col+1):
                moves.append(Move((row,col), (row + moveDirection, col+1), self.board))
        
    def getRookMoves(self, row, col, moves):
    
        #Rooks move in straight lines
        directions = ((-1,0), (0,-1), (1, 0), (0,1))
        self.getBasicPieceMoves(row, col, directions, moves)
                
    def getBishopMoves(self, row, col, moves):
    
        #Bishops move diagonally
        directions = ((-1,-1), (1,-1), (-1,1), (1,1))
        self.getBasicPieceMoves(row, col, directions, moves)
        
    def getQueenMoves(self, row, col, moves):
    
        #A Queen moves like a Rook and a Bishop combined
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)
        
    def getBasicPieceMoves(self, row, col, directions, moves):
    
        #Rooks, Bishops and Queens have the exact movement behavior, only in different directions
        
        enemyColor = 'b' if self.whiteToMove else 'w'
        
        #For each possible direction: Move one step at a time until you hit a piece or the edge of the board
        for d in directions:
            for i in range(1, 8):
                end = (row + d[0] * i, col + d[1] * i)
                if 0 <= end[0] < 8 and 0 <= end[1] < 8:
                    if self.board[end[0]][end[1]] == "--":
                        moves.append(Move((row, col), (end[0], end[1]), self.board))
                        continue
                    elif self.board[end[0]][end[1]][0] == enemyColor:
                        moves.append(Move((row, col), (end[0], end[1]), self.board))
                break
        
    def getKnightMoves(self, row, col, moves):
    
        #Knights move in an L shape, but only one step per turn
        
        directions = ((-2,-1), (-2,1), (2,-1), (2,1), (-1,-2), (-1,2), (1,-2), (1,2))
        ownColor = 'w' if self.whiteToMove else 'b'
        for d in directions:
            end = (row + d[0], col + d[1])
            if 0 <= end[0] < 8 and 0 <= end[1] < 8:
                if self.board[end[0]][end[1]][0] != ownColor:
                    moves.append(Move((row, col), (end[0], end[1]), self.board))
                
        
    def getKingMoves(self, row, col, moves):
    
        #A King moves in every direction but only one step a time
        directions = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1))
        ownColor = 'w' if self.whiteToMove else 'b'
        enemyKingLocation = self.blackKingLocation if self.whiteToMove else self.whiteKingLocation
        
        for d in directions:
            end = (row + d[0], col + d[1])
            if 0 <= end[0] < 8 and 0 <= end[1] < 8:
                #King can't move to a square that is adjacent to enemy King's square
                if (self.board[end[0]][end[1]][0] != ownColor and (np.abs(end[0] - enemyKingLocation[0]) > 1
                    or np.abs(end[1] - enemyKingLocation[1]) > 1)):
                    moves.append(Move((row, col), (end[0], end[1]), self.board))
                    
        #Castling: If King is not in Check and King hasn't moved:
        #If left Rook hasn't moved: Long castle possible. If right Rook hasn't moved: Short Castle possible
        left_castle_possible = False
        right_castle_possible = False
        if not self.inCheck():
            if ((self.whiteToMove and not self.whiteKingMoved and not self.leftWhiteRookMoved)
                or (not self.whiteToMove and not self.blackKingMoved and not self.leftBlackRookMoved)):
                left_castle_possible = True
            if ((self.whiteToMove and not self.whiteKingMoved and not self.rightWhiteRookMoved)
                or (not self.whiteToMove and not self.blackKingMoved and not self.rightBlackRookMoved)):
                right_castle_possible = True
            self.castle(row, col, left_castle_possible, right_castle_possible, moves)
            
    def castle(self, row, col, left_castle_possible, right_castle_possible, moves):
    
        move_directions = (-1, 1)
        
        #Castling is only possible if no pieces are in the way and the King doesn't move through Check
        
        for direction in move_directions:
            castle_possible = left_castle_possible if direction == -1 else right_castle_possible
            
            #Check if pieces are in the way
            if (castle_possible and self.board[row][col + direction] == "--"
                and self.board[row][col + (direction * 2)] == "--"):
                
                #Move the King one square to the left/right and check if he's in Check. Then move him back.
                self.make_move(Move((row, col), (row, col + direction), self.board))
                self.whiteToMove = not self.whiteToMove
                if self.inCheck():
                    castle_possible = False
                self.whiteToMove = not self.whiteToMove
                self.undo_move()
                
                if castle_possible:
                    moves.append(Move((row, col), (row, col + (direction * 2)), self.board))
                    
                    
    def inCheck(self):
    
        #Idea: Let King move like every piece
        #If he can reach an enemy piece when moving as that piece, he's in that enemy piece's direct line of sight
        #If the King is in direct line of sight of any enemy piece, he's in Check
        moves = []
        pieces = ['p', 'R', 'N', 'B', 'Q']
        king_location = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation
        enemyColor = 'b' if self.whiteToMove else 'w'
            
        for piece in pieces:
            self.getPieceMoves(piece, king_location[0], king_location[1], moves)
            for move in moves:
                if self.board[move.end[0]][move.end[1]] == enemyColor + piece:
                    return True
            moves = []
        return False
        
    def checkMate(self):
        
        #Checkmate if player has no valid moves and his King is in Check
        return len(self.valid_moves()) == 0 and self.inCheck()
        
    def staleMate(self):
    
        #Stalemate if player has no valid moves, but his King is not in Check
        return len(self.valid_moves()) == 0 and not self.inCheck()
        
              
    def updatePiecesMoved(self):
    
        #Go through entire move list. If a King or Rook was moved or a Rook was captured, set it to Moved
    
        self.whiteKingMoved = False
        self.blackKingMoved = False
        self.leftWhiteRookMoved = False
        self.rightWhiteRookMoved = False
        self.leftBlackRookMoved = False
        self.rightBlackRookMoved = False
        
        for move in self.moveLog:
            if move.pieceMoved == "wK":
                self.whiteKingMoved = True
            elif move.pieceMoved == "bK":
                self.blackKingMoved = True
            elif move.pieceMoved == "wR" or move.pieceCaptured == "wR":
                if move.start == (7,0) or move.end == (7,0):
                    self.leftWhiteRookMoved = True
                elif move.start == (7,7) or move.end == (7,7):
                    self.rightWhiteRookMoved = True
            elif move.pieceMoved == "bR" or move.pieceCaptured == "bR":
                if move.start == (0,0) or move.end == (0,0):
                    self.leftBlackRookMoved = True
                elif move.start == (0,7) or move.end == (0,7):
                    self.rightBlackRookMoved = True
        
class Move():

    #Lookup to easily match rows and columns to the corresponding ranks and files of the Chess board (and vice versa)

    rankToRow = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowToRank = {row: rank for rank, row in rankToRow.items()}
    
    fileToCol = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colToFile = {col: file for file, col in fileToCol.items()}
    
    def __init__(self, start, end, board):
    
        self.start = start
        self.end = end
        self.pieceMoved = board[start[0]][start[1]]
        self.pieceCaptured = board[end[0]][end[1]]
        
    def __eq__(self, other):
    
        #override equals method to compare moves
        
        if isinstance(other, Move):
            if self.start == other.start and self.end == other.end:
                return True
        return False
        
    def get_notation(self):
    
        #Chess notation:
            #Start with abbreviation of piece moved, except if it's a pawn
            #If move was a capture: Add an "x". If the piece moved was a pawn, also add its starting file
            #Add the square the piece was moved to
            #If move was pawn promotion (to Queen): Add "=Q"
            
            #Special notation: If move was short Castle: "O-O". If move was long castle: "O-O-O"
            
        notation = ""
        
        if self.pieceMoved[1] != "p":
            notation += self.pieceMoved[1]
            if self.pieceCaptured != "--":
                notation += 'x'
        elif self.end[1] != self.start[1]:
            notation += self.get_file(self.start[1]) + 'x'
        
        notation += self.get_square(self.end[0], self.end[1])
        
        if self.pieceMoved[1] == 'p' and (self.end[0] == 0 or self.end[0] == 7):
            notation += "=Q"
        
        if self.pieceMoved[1] == 'K':
            if self.start[1] < self.end[1]-1:
                notation = "O-O"
            elif self.start[1] > self.end[1]+1:
                notation = "O-O-O"
                
        return notation
        
    def get_square(self, row, col):
        return self.get_file(col) + self.get_rank(row)
       
    def get_file(self, col):
        return self.colToFile[col]
        
    def get_rank(self, row):
        return self.rowToRank[row]