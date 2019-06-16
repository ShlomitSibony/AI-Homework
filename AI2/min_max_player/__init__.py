# ===============================================================================
# Imports
# ===============================================================================

import time

import abstract
from Reversi.consts import OPPONENT_COLOR, BOARD_COLS, BOARD_ROWS
from players.AI2_311155543_319201257.Improvements import updateTable, holesScore, createBonusTable
from players.AI2_311155543_319201257.utils import INFINITY, ExceededTimeError, MiniMaxAlgorithm


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

        self.deepSum = 0
        self.moves = 0
        self.bonusTable = createBonusTable()

    def get_move(self, game_state, possible_moves):
        self.clock = time.time()
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05
        if len(possible_moves) == 1:
            return possible_moves[0]

        best_move = None
        depth = 1
        minimax = MiniMaxAlgorithm(self.utility,self.color,self.no_more_time,self.selective_deepening_criterion)
        timeRemaining = True
        possibleMoves = game_state.get_possible_moves()
        #print(possibleMoves)
        while timeRemaining:
            try:
                #if there still is time try and looker deeper in the posibility tree, So
                #when the time is over, an exeption will be thrown, well catch it and break the loop
                u,move = minimax.search(game_state,depth,True)
                best_move = move
                depth += 1

                if u == INFINITY or u == -INFINITY:
                    break

            except (ExceededTimeError):
                timeRemaining = False

        self.deepSum += depth
        self.moves += 1

        if self.turns_remaining_in_round == 1:
            self.turns_remaining_in_round = self.k
            self.time_remaining_in_round = self.time_per_k_turns
        else:
            self.turns_remaining_in_round -= 1
            self.time_remaining_in_round -= (time.time() - self.clock)

        self.bonusTable = updateTable(self.bonusTable, best_move)
        #print('depth:  ' , depth)
        return best_move

    def utility(self, state):
        my_u = 0
        my_total_u = -len(state.get_possible_moves())
        op_u = 0
        op_total_u = 0
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                if state.board[x][y] == self.color:
                    my_u += 1
                    my_total_u += self.bonusTable[x][y] + 1
                if state.board[x][y] == OPPONENT_COLOR[self.color]:
                    op_u += 1
                    op_total_u += self.bonusTable[x][y] + 1

        if my_u + op_u > BOARD_COLS * BOARD_ROWS * 0.85:
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

    # @staticmethod
    # def createBonusTable():
    #     bonusTable = np.zeros((BOARD_COLS, BOARD_ROWS))
    #     bonusTable[0] = [lineBonus] * BOARD_COLS
    #     bonusTable[BOARD_ROWS - 1] = [lineBonus] * BOARD_COLS
    #     bonusTable[:, 0] = [lineBonus] * BOARD_ROWS
    #     bonusTable[:, BOARD_COLS - 1] = [lineBonus] * BOARD_ROWS
    #
    #     # bonusTable[1] = [-8] * BOARD_COLS
    #     # bonusTable[BOARD_ROWS - 2] = [-8] * BOARD_COLS
    #     # bonusTable[:, 1] = [-8] * BOARD_ROWS
    #     # bonusTable[:, BOARD_COLS - 2] = [-8] * BOARD_ROWS
    #
    #
    #     bonusTable[0][0] = 99
    #     bonusTable[0][BOARD_COLS - 1] = 99
    #     bonusTable[BOARD_ROWS - 1][0] = 99
    #     bonusTable[BOARD_ROWS - 1][BOARD_COLS - 1] = 99
    #
    #     bonusTable[BOARD_ROWS - 2][BOARD_COLS - 2] = -24
    #     bonusTable[1][BOARD_COLS - 2] = -24
    #     bonusTable[BOARD_ROWS - 2][1] = -24
    #     bonusTable[1][1] = -24
    #
    #     bonusTable[0][1] = -24
    #     bonusTable[1][0] = -24
    #
    #     bonusTable[0][6] = -24
    #     bonusTable[1][7] = -24
    #
    #     bonusTable[6][0] = -24
    #     bonusTable[7][1] = -24
    #
    #     bonusTable[6][7] = -24
    #     bonusTable[7][6] = -24
    #
    #     return bonusTable

    def selective_deepening_criterion(self, state):
        # Simple player does not selectively deepen into certain nodes.
        return False

    def no_more_time(self):
        return (time.time() - self.clock) >= self.time_for_current_move

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'min_max')


    def printStat(self):
        print('algorithm: min max in a total of {} moves we arrive in avg to {} deep' , self.moves , self.deepSum/self.moves)


# c:\python35\python.exe run_game.py 3 3 3 y simple_player random_player
