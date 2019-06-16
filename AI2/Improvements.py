import numpy as np
from Reversi.consts import EM, OPPONENT_COLOR, BOARD_COLS, BOARD_ROWS,lineBonus


def createBonusTable():
    bonusTable = np.zeros((BOARD_COLS,BOARD_ROWS))
    bonusTable[0] = [lineBonus]*BOARD_COLS
    bonusTable[BOARD_ROWS-1] = [lineBonus]*BOARD_COLS
    bonusTable[:,0] = [lineBonus]*BOARD_ROWS
    bonusTable[:, BOARD_COLS-1] = [lineBonus] * BOARD_ROWS

    bonusTable[0][0] = 99
    bonusTable[0][BOARD_COLS-1] = 99
    bonusTable[BOARD_ROWS-1][0] = 99
    bonusTable[BOARD_ROWS-1][BOARD_COLS-1] = 99

    bonusTable[BOARD_ROWS-2][BOARD_COLS-2] = -24
    bonusTable[1][BOARD_COLS - 2] = -24
    bonusTable[BOARD_ROWS - 2][1] = -24
    bonusTable[1][1] = -24

    bonusTable[0][1] = -24
    bonusTable[1][0] = -24

    bonusTable[0][6] = -24
    bonusTable[1][7] = -24

    bonusTable[6][0] = -24
    bonusTable[7][1] = -24

    bonusTable[6][7] = -24
    bonusTable[7][6] = -24

    return bonusTable

def updateTable(bonusTable , move):
    if isCorner(move[0] , move[1]):
        for i in range(move[0] - 1, 3):
            for j in range(move[1] - 1, 3):
                if i < BOARD_ROWS and j < BOARD_COLS and i >= 0 and j >= 0:
                    if bonusTable[i][j] == -24:
                        bonusTable[i][j] = lineBonus
    return bonusTable

def isCorner(x,y):
     return (x % (BOARD_COLS - 1) == 0) and (y % (BOARD_ROWS - 1) == 0)

def holesScore(board):
    countOdd = 0
    countPair = 0
    for x in range(BOARD_COLS):
        for y in range(BOARD_ROWS):
            len = holeLength(x,y,board)
            if len != 0:
                countOdd += len %2
                countPair += 1 - len %2
    return (countOdd - countPair)*5

def holeLength(x , y , board):

    if x < 0 or y < 0 or x >= BOARD_COLS or y >= BOARD_COLS or board[x][y] != ' ':
        return 0

    board[x][y] = '*'
    sum = 0

    for i in range(x - 1, 3):
        for j in range(y - 1, 3):
            if i < BOARD_ROWS and j < BOARD_COLS and i >= 0 and j >= 0:
                sum += holeLength(x + 1, y, board)

    return sum