"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random
import isolation

class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    # TODO: finish this function!
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    def func1(game, player):
       ##### first function is distance from center ###
       ##### getting center coordinates ###
       center_x = game.width / 2
       center_y = game.height / 2
       #####getting player locations ###
       player_loc = game.get_player_location(player)
       ####separating x and y coordinates of player locations ###
       player_x = player_loc[0]
       player_y = player_loc[1]
       ####getting distance between x coordinates of center and player location and taking square ###
       player_x = player_x - center_x
       player_x = player_x * player_x
       ####getting distance between y coordinates of center and player location and taking square ###
       player_y = player_y - center_y
       player_y = player_y * player_y
       #### adding the squred difference of x and y coordinates ####
       distance = player_x + player_y
       #### getting the square root ###
       distance = distance**(1/2.0)
       #### Inverting the distance, so that lower the distance higher the score ###
       distance = 1 / distance
       return distance
    def func2(game, player):
       ##### second function is difference between player's move and twice the opponents move ####
       return float(own_moves - 2 * opp_moves)
    def func3(game, player):
       ##### third function is the ratio between player's move and weighted opponents move###
       ##### had to add 1 because zero move would give divide by zero. Multiplied by 1.25 so that score is more aggressive for the student player ###
       return float((1 + own_moves) / (1.25 * (1 + opp_moves)))

    #return func1(game, player)
    #return func2(game, player)
    return func3(game, player)


class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left

        # TODO: finish this function!

        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves
        if game.get_legal_moves() is None:
          return self.score(game, self), (-1, -1)
        best_move = (-1, -1)
        

        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            
            if self.iterative:
              depth = 1
              while len(game.get_legal_moves()) > 0:
                   if self.method == 'minimax':
                      myscore, best_move = self.minimax(game, depth)
                   if self.method == 'alphabeta':
                      myscore, best_move = self.alphabeta(game, depth)
                   depth += 1 
            else:
              if self.method == 'minimax':
                myscore, best_move = self.minimax(game,1)
              else:
                myscore, best_move = self.alphabeta(game,1)            

            pass

        except Timeout:
            # Handle any actions required at timeout, if necessary
            return best_move
            pass

        # Return the best move from the last completed search iteration
        return best_move
        raise NotImplementedError

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # TODO: finish this function!
        if game.get_legal_moves() is None:
          return self.score(game, self), (-1, -1)

        if depth == 0:
          return self.score(game, self), game.get_player_location(self)

        if maximizing_player:
               current_value = -99999999999
               best_move = (-1, -1)
               for each_move in game.get_legal_moves():
                  new_game = game.forecast_move(each_move)
                  got_back_value, got_back_coord = self.minimax(new_game,depth-1,not maximizing_player)
                  if current_value < got_back_value:
                    best_move = each_move
                  current_value = max(current_value, got_back_value)

        else:
               current_value = 99999999999999
               best_move = (-1,-1)
               for each_move in game.get_legal_moves():
                     new_game = game.forecast_move(each_move)
                     got_back_value, got_back_coord = self.minimax(new_game,depth-1,not maximizing_player)
                     if current_value > got_back_value:
                         best_move =each_move
                     current_value = min(current_value, got_back_value)


        current_value =  float(current_value)
        return [current_value,best_move]      
   
        raise NotImplementedError

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # TODO: finish this function!
        
        if game.get_legal_moves() is None:
          return self.score(game, self), (-1, -1)
        
        if depth == 0:
          return self.score(game, self), game.get_player_location(self)


        if maximizing_player:
               current_value = -99999999999
               best_move = (-1, -1)
               for each_move in game.get_legal_moves():
                  new_game = game.forecast_move(each_move)
                  got_back_value, got_back_coord = self.alphabeta(new_game,depth-1,alpha,beta,not maximizing_player)
                  if current_value < got_back_value:
                    best_move = each_move
                  current_value = max(current_value, got_back_value)                
                  alpha = max(alpha,current_value)       
                  if alpha >= beta:
                    return [current_value,best_move]

        else:
               current_value = 99999999999999
               best_move = (-1,-1)
               for each_move in game.get_legal_moves():
                     new_game = game.forecast_move(each_move)
                     got_back_value, got_back_coord = self.alphabeta(new_game,depth-1,alpha,beta,not maximizing_player)
                     if current_value > got_back_value:
                         best_move =each_move
                     current_value = min(current_value, got_back_value)
                     beta = min(beta,current_value)
                     if alpha >= beta:
                         return [current_value,best_move]

        return [current_value,best_move]
        raise NotImplementedError
