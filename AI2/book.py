import operator
import re
from Reversi.board import GameState
from Reversi.consts import EM, OPPONENT_COLOR, BOARD_COLS, BOARD_ROWS,lineBonus
import numpy as np

def makeMiniBook():
    lines = {}
    file = open("Reversi//book.gam", "r")
    for line in file:
        buf = line[0:30]
        if buf not in lines:
            lines[buf] = 1
        else:
            lines[buf] += 1


    sorted_lines = sorted(lines.items(), key=operator.itemgetter(1),reverse=True)
    sortedKeys = [str(a[0]) for a in sorted_lines]
    cuttedSortedLines = sortedKeys[0:70]
    splittedSortedLines = []
    for line in cuttedSortedLines:
        splittedSortedLines.append(re.split("[+-]+",line)[1:11])

    return splittedSortedLines

def makeBookDictionnary():
    miniBook = makeMiniBook()

    openBook = {}

    for line in reversed(miniBook):
        state = GameState()

        for move in line:
            vec = boardToVec(state.board)
            moveX = ord(move[0]) - ord('a')
            moveY = ord(move[1]) - ord('1')
            row = 7 - moveX
            col = moveY
            openBook[vec] = (row,col)
            #print("move: {} , {} ", move[0], move[1], " ==> " , row , col)
            state.perform_move(row, col)
    return openBook




def boardToVec(board):
    vec = ""
    for x in range(BOARD_COLS):
        for y in range(BOARD_ROWS):
            vec = vec + board[x][y]

    return vec

def vecToBoard(vec):
    state = GameState()
    board = []
    for i in range(BOARD_COLS):
        board.append([EM] * BOARD_ROWS)

    i=0
    for x in range(BOARD_COLS):
        for y in range(BOARD_ROWS):
            board[x][y] = vec[i]
            i += 1
    state.board = board
    return state

