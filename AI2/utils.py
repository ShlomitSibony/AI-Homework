"""Generic utility functions
"""
# from __future__ import print_function
from threading import Thread
from multiprocessing import Queue
import time
import copy

import os

import numpy

INFINITY = float(6000)


class ExceededTimeError(RuntimeError):
    """Thrown when the given function exceeded its runtime.
    """
    pass


def function_wrapper(func, args, kwargs, result_queue):
    """Runs the given function and measures its runtime.

    :param func: The function to run.
    :param args: The function arguments as tuple.
    :param kwargs: The function kwargs as dict.
    :param result_queue: The inter-process queue to communicate with the parent.
    :return: A tuple: The function return value, and its runtime.
    """
    start = time.time()
    try:
        result = func(*args, **kwargs)
    except MemoryError as e:
        result_queue.put(e)
        return

    runtime = time.time() - start
    result_queue.put((result, runtime))


def run_with_limited_time(func, args, kwargs, time_limit):
    """Runs a function with time limit

    :param func: The function to run.
    :param args: The functions args, given as tuple.
    :param kwargs: The functions keywords, given as dict.
    :param time_limit: The time limit in seconds (can be float).
    :return: A tuple: The function's return value unchanged, and the running time for the function.
    :raises PlayerExceededTimeError: If player exceeded its given time.
    """
    q = Queue()
    t = Thread(target=function_wrapper, args=(func, args, kwargs, q))
    t.start()

    # This is just for limiting the runtime of the other thread, so we stop eventually.
    # It doesn't really measure the runtime.
    t.join(time_limit)

    if t.is_alive():
        raise ExceededTimeError

    q_get = q.get()
    if isinstance(q_get, MemoryError):
        raise q_get
    return q_get


def initDictionnary():
    path = os.path.dirname(os.path.abspath(__file__)) + "/book.gam"
    print(path)
    bashCommand = "cat " + path + " | cut -c1-30 | uniq -c | sort -rn | head -70"
    import subprocess
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(output)





class MiniMaxAlgorithm:

    def __init__(self, utility, my_color, no_more_time, selective_deepening):
        """Initialize a MiniMax algorithms without alpha-beta pruning.

        :param utility: The utility function. Should have state as parameter.
        :param my_color: The color of the player who runs this MiniMax search.
        :param no_more_time: A function that returns true if there is no more time to run this search, or false if
                             there is still time left.
        :param selective_deepening: A functions that gets the current state, and
                        returns True when the algorithm should continue the search
                        for the minimax value recursivly from this state.
                        optional
        """
        self.utility = utility
        self.my_color = my_color
        self.no_more_time = no_more_time
        self.selective_deepening = selective_deepening

    def search(self, state, depth, maximizing_player , print = False):
        """Start the MiniMax algorithm.

        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :return: A tuple: (The min max algorithm value, The move in case of max node or None in min mode)
        """
        if self.no_more_time():
            #the min_max get_move algorithm will catch it and return the best move he found so far.
            raise ExceededTimeError

        possibleMoves = state.get_possible_moves()
        if depth == 0 or len(possibleMoves) == 0:
            return self.utility(state),None


        #state.curr_player != self.my_color
        if maximizing_player:
            currMax = -INFINITY
            bestMove = None
            for move in possibleMoves:
                new_state = copy.deepcopy(state)
                new_state.perform_move(move[0], move[1])
                v,_ = self.search(new_state,depth-1,False)
                if currMax <= v:
                    currMax = v
                    bestMove = move
            return currMax,bestMove
        else:
            currMin = INFINITY
            for move in possibleMoves:
                new_state = copy.deepcopy(state)
                new_state.perform_move(move[0], move[1])
                v,_ = self.search(new_state,depth-1,True)
                self.lastMove = move
                if v < currMin:
                    currMin = v;
            return currMin,None



class MiniMaxWithAlphaBetaPruning:

    def __init__(self, utility, my_color, no_more_time, selective_deepening):
        """Initialize a MiniMax algorithms with alpha-beta pruning.

        :param utility: The utility function. Should have state as parameter.
        :param my_color: The color of the player who runs this MiniMax search.
        :param no_more_time: A function that returns true if there is no more time to run this search, or false if
                             there is still time left.
        :param selective_deepening: A functions that gets the current state, and
                        returns True when the algorithm should continue the search
                        for the minimax value recursivly from this state.
        """
        self.utility = utility
        self.my_color = my_color
        self.no_more_time = no_more_time
        self.selective_deepening = selective_deepening

    def search(self, state, depth, alpha, beta, maximizing_player):
        """Start the MiniMax algorithm.

        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param alpha: The alpha of the alpha-beta pruning.
        :param beta: The beta of the alpha-beta pruning.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :return: A tuple: (The alpha-beta algorithm value, The move in case of max node or None in min mode)
        """
        if self.no_more_time():
            # the alpha_beta get_move algorithm will catch it and return the best move he found so far.
            raise ExceededTimeError

        possibleMoves = state.get_possible_moves()
        if depth == 0 or len(possibleMoves) == 0:
            return self.utility(state), None

        # state.curr_player != self.my_color
        if maximizing_player:
            currMax = -INFINITY
            bestMove = None
            for move in possibleMoves:
                new_state = copy.deepcopy(state)
                new_state.perform_move(move[0], move[1])
                v, _ = self.search(new_state, depth - 1, alpha,beta,False)
                if currMax <= v:
                    currMax = v
                    bestMove = move
                if currMax > alpha:
                    alpha = currMax
                if currMax >= beta and beta != INFINITY:
                    return INFINITY,None
            return currMax, bestMove
        else:
            currMin = INFINITY
            for move in possibleMoves:
                new_state = copy.deepcopy(state)
                new_state.perform_move(move[0], move[1])
                v, _ = self.search(new_state, depth - 1,alpha,beta, True)
                self.lastMove = move
                if v < currMin:
                    currMin = v;
                #currMin = numpy.min(v, currMin) numpy min exepct integer not float
                if currMin < beta:
                    beta = currMin
                if currMin <= alpha and alpha != -INFINITY:
                    return -INFINITY,None
            return currMin, None

