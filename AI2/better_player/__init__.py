# ===============================================================================
# Imports
# ===============================================================================

import copy
import time

import numpy as np

import abstract
from Reversi.consts import OPPONENT_COLOR, BOARD_COLS, BOARD_ROWS
from players.AI2_311155543_319201257.Improvements import createBonusTable, holesScore, updateTable
from players.AI2_311155543_319201257.book import makeBookDictionnary, boardToVec
from players.AI2_311155543_319201257.utils import INFINITY

protectCornerMinus =  -24
lineBonus = 2

# ===============================================================================
# Player
# ===============================================================================

class Player(abstract.AbstractPlayer):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        abstract.AbstractPlayer.__init__(self, setup_time, player_color, time_per_k_turns, k)
        self.clock = time.time()

        # We are simply providing (remaining time / remaining turns) for each turn in round.
        # Taking a spare time of 0.05 seconds.
        self.turns_remaining_in_round = self.k
        self.time_remaining_in_round = self.time_per_k_turns
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05

        self.bonusTable = createBonusTable()  # special score table

        self.openBook = makeBookDictionnary()


    def get_move(self, game_state, possible_moves):
        self.clock = time.time()
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05
        if len(possible_moves) == 1:
            return possible_moves[0]

        #look for the move in the dictionnary
        move = self.opening_move(game_state)
        if move != None:
            #print("move was chosen from dictionnary" , move[0] , move[1])
            return move


        best_move = possible_moves[0]
        next_state = copy.deepcopy(game_state)
        next_state.perform_move(best_move[0], best_move[1])
        # Choosing an arbitrary move
        # Get the best move according the utility function
        for move in possible_moves:
            new_state = copy.deepcopy(game_state)
            new_state.perform_move(move[0], move[1])
            if self.utility(new_state) > self.utility(next_state):
                next_state = new_state
                best_move = move

        if self.turns_remaining_in_round == 1:
            self.turns_remaining_in_round = self.k
            self.time_remaining_in_round = self.time_per_k_turns
        else:
            self.turns_remaining_in_round -= 1
            self.time_remaining_in_round -= (time.time() - self.clock)

        self.bonusTable = updateTable(self.bonusTable,best_move)


        return best_move

    def utility(self, state):
        # if len(state.get_possible_moves()) == 0:
        #     return INFINITY if state.curr_player != self.color else -INFINITY

        my_u = 0
        #substruct the number of moves the open have from our score,
        #in that way well always prefer letting the opponet a small set of choices
        my_total_u = -len(state.get_possible_moves())
        op_u = 0
        op_total_u = 0
        #add a bonus for each tool we have on the board in function of its position
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                if state.board[x][y] == self.color:
                    my_u += 1
                    my_total_u += self.bonusTable[x][y] + 1
                if state.board[x][y] == OPPONENT_COLOR[self.color]:
                    op_u += 1
                    op_total_u += self.bonusTable[x][y] + 1

        #if we're close to the game end, we'll always prefer putting a piece surrounded by
        #other pieces, (not nesseceraly ours),so in that way it would be harder to change it color.
        #thinking like that well prefer not putting pieces where there are 2 (or any pair number)
        #places left.
        if my_u + op_u > BOARD_COLS*BOARD_ROWS * 0.85:
            op_total_u = holesScore(state.board) + op_u
            my_total_u = my_u

        if my_u == 0:
            # I have no tools left
            return -INFINITY
        elif op_u == 0:
            # The opponent has no tools left
            return INFINITY
        else:
            return my_total_u - op_total_u

    def selective_deepening_criterion(self, state):
        # Simple player does not selectively deepen into certain nodes.
        return False

    def no_more_time(self):
        return (time.time() - self.clock) >= self.time_for_current_move

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'better')




    def opening_move(self, game_state):

        #the board is one of the dictionnary keys
        vec = boardToVec(game_state.board)
        if vec in self.openBook.keys():
            move = self.openBook[vec]
            return move

        # the transposed boad is one of the keys
        #so well return the transposed move
        t = np.transpose(game_state.board)
        vec = boardToVec(t)
        if vec in self.openBook.keys():
            move = self.openBook[vec]
            return (move[1], move[0])


        # the 180 degree rotated boad is one of the keys
        # so well return the matching move
        t = np.rot90(game_state.board, 2)
        vec = boardToVec(t)
        if vec in self.openBook.keys():
            move = self.openBook[vec]
            return (7 - move[0], 7 - move[1])


        # the 180 degree rotated and transposed boad is one of the keys
        # so well return the matching move
        t = np.transpose(t)
        vec = boardToVec(t)
        if vec in self.openBook.keys():
            move = self.openBook[vec]
            return (7 - move[1], 7 - move[0])

        return None



# c:\python35\python.exe run_game.py 3 3 3 y simple_player random_player