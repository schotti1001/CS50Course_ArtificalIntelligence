"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None
maxDepth = 5


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    xCount = 0
    oCount=0
    for i in range(3):
        for a in range(3):
            if board[i][a] == X:
                xCount+=1
            elif board[i][a] == O:
                oCount+=1
    if xCount<=oCount:
        return X
    else: 
        return O

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possibleMoves = set()
    for i in range(3):
        for a in range(3):
            if board[i][a] is EMPTY:
                possibleMoves.add((i,a))
    return possibleMoves

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    newBoard = copy.deepcopy(board)
    if board[action[0]][action[1]] is not EMPTY:
        raise Exception()
    newBoard[action[0]][action[1]] = player(board)   
    return newBoard 

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    
    """
    Check horizontal
    """
    for i in range(3):
        player = board[i][0]
        gotThreeInARow=True
        for a in range(3):
            if board[i][a] != player:
                gotThreeInARow=False
                break
        if gotThreeInARow:
            return player

    """
    Check vertikal
    """
    for i in range(3):
        player = board[0][i]
        gotThreeInARow=True
        for a in range(3):
            if board[a][i] != player:
                gotThreeInARow=False
                break
        if gotThreeInARow:
            return player       
    """
    Check diagonal
    """
    if board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
   
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    
    for i in range(3):
        for a in range(3):
            if board[i][a] is EMPTY:
                return False
    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winningPlayer = winner(board)
    if winningPlayer == X:
        return 1
    elif winningPlayer == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    
    if player(board) == X:
        return maxValue(board, 0)[1]
    else:
        return minValue(board, 0)[1]


def minValue(board, depth):
        if terminal(board):
            return (utility(board), None)
        global maxDepth
        depth +=1 
        v = math.inf
        bestAction = None
        for action in actions(board):
            newMin = min(v, float(maxValue(result(board,action), depth)[0]))
            if v > newMin:
                v = newMin
                bestAction = action
            if depth > maxDepth:
                return (v, action)
            
        return (v,bestAction)

def maxValue(board, depth):
        if terminal(board):
            return (utility(board), None)
        global maxDepth
        depth +=1  
        v = -math.inf
        bestAction = None
        for action in actions(board):
            newMax = max(v, float(minValue(result(board,action), depth)[0]))
            if v < newMax:
                v = newMax
                bestAction = action
            if depth > maxDepth:
                return (v, bestAction)  
        return (v,bestAction)