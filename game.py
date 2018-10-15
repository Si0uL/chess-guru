"""
Chess game object
"""

from copy import deepcopy
import pickle
from time import time
from random import shuffle

from board import BOARD
from utils import (
    print_board,
    get_score,
    missing_pieces,
    available_movements_raw,
    is_check2,
    fast_is_check2,
    score_per_play,
    readable_position,
)


class ChessGame(object):
    """docstring for ChessGame."""
    def __init__(self, board=None, castling=None, white_turn=True):
        super(ChessGame, self).__init__()

        # Init Board
        if board is None:
            self.board = deepcopy(BOARD)
        else:
            self.board = board

        # Init Castling
        if castling is None:
            self.castling = {
                'white': {
                    'left': True,
                    'right': True,
                },
                'black': {
                    'left': True,
                    'right': True,
                }
            }
        else:
            self.castling = castling

        # Init turn
        self.white_turn = white_turn

        # Init King position
        self.king_position = {}
        for r_nb, row in enumerate(self.board):
            for c_nb, piece in enumerate(row):
                if piece.get('type') == 'king':
                    self.king_position[piece['color']] = (r_nb, c_nb)

        # Init Unplay Infos
        self.unplay_infos = []



    def display(self):
        """
        Print the board
        """
        print_board(self.board)


    @property
    def missing_pieces(self):
        """
        Get missing_pieces
        """
        return missing_pieces(self.board)


    def score(self, color='white'):
        """
        Get Game's score
        """
        return get_score(color, self.board)

    @property
    def turn(self):
        return 'white' if self.white_turn else 'black'


    def _update_castling(self, start, color):
        """
        Updates self.castling after piece was moved from start to ? This piece's
        color was color
        """
        row = 7
        if color == 'black':
            row = 0
        castling_l = self.castling[color]['left']
        castling_r = self.castling[color]['right']
        if castling_l and start[0] == row and (start[1] == 4 or start[1] == 0):
            self.castling[color]['left'] = False
        if castling_r and start[0] == row and (start[1] == 4 or start[1] == 7):
            self.castling[color]['right'] = False


    def play(self, start, arrival, save=False, update_cast=True):
        """
        Puts piece located at start at arrival position, modifies board.
        Return former pieces at start and arrival locations to allow unplay
        update_cast will be false while using this inside available_movements
        as it doesn't need an update

        Inputs:
            - start {tuple} start position
            - arrival {tuple} arrival position
            - save {bool} whether or not to add to unplay_infos cache
            - update_cast {bool} use False not to update self.castling

        Returns:
            - start {tuple}
            - former_start {dict}
            - arrival {tuple}
            - former_arrival {dict}
        """
        former_start = self.board[start[0]][start[1]]
        former_arrival = self.board[arrival[0]][arrival[1]]
        color = former_start['color']
        self.board[arrival[0]][arrival[1]] = former_start
        self.board[start[0]][start[1]] = {'color': 'blank'}
        # If pawn at edge: transform it into a queen by default
        if former_start['type'] == 'pawn' and \
            (arrival[0] == 0 or arrival[0] == 7):
            # Recreate an object to avoid side effects
            self.board[arrival[0]][arrival[1]] = {
                'type': 'queen',
                'color': color,
            }
        # If king castling: move also the rook:
        if former_start['type'] == 'king' and abs(start[1] - arrival[1]) == 2:
            # Left castling
            if arrival[1] == 2:
                self.board[start[0]][3] = {
                    'type': 'rook',
                    'color': color
                }
                self.board[start[0]][0] = {'color': 'blank'}
            # Right castling
            if arrival[1] == 6:
                self.board[start[0]][5] = {
                    'type': 'rook',
                    'color': color
                }
                self.board[start[0]][7] = {'color': 'blank'}

        # Update turn:
        self.white_turn = not self.white_turn

        # Update kpos
        if former_start['type'] == 'king':
            self.king_position[color] = arrival

        unplay_infos = (
            start,
            former_start,
            arrival,
            former_arrival,
            self.castling[color]['left'],
            self.castling[color]['right'],
        )

        # Update self.castling if asked to
        if update_cast:
            self._update_castling(start, color)

        if save:
            self.unplay_infos.append(unplay_infos)

        return unplay_infos


    def unplay(self, start=None, former_start=None, arrival=None,
               former_arrival=None, c_left=None, c_right=None):
        """
        Undo the efect of the play() function. Modifies the board. If
        save == False, you have to give the arguments "manually", in slow mode,
        uses the history self.unplay_infos.
        """
        # If no arguments are given, use history (#slow_mode)
        if start is None:
            if self.unplay_infos == []:
                return
            start, former_start, arrival, former_arrival, c_left, c_right = \
                self.unplay_infos.pop()

        self.board[start[0]][start[1]] = former_start
        self.board[arrival[0]][arrival[1]] = former_arrival
        color = former_start['color']
        # If king castling: move also the rook:
        if former_start['type'] == 'king' and abs(start[1] - arrival[1]) == 2:
            # Left castling
            if arrival[1] == 2:
                self.board[start[0]][0] = {
                    'type': 'rook',
                    'color': color
                }
                self.board[start[0]][3] = {'color': 'blank'}
            # Right castling
            if arrival[1] == 6:
                self.board[start[0]][7] = {
                    'type': 'rook',
                    'color': color
                }
                self.board[start[0]][5] = {'color': 'blank'}

        # Update turn:
        self.white_turn = not self.white_turn

        # Restore previous castling:
        self.castling[color]['left'] = c_left
        self.castling[color]['right'] = c_right

        # Update kpos
        if former_start['type'] == 'king':
            self.king_position[color] = start


    def save(self, path):
        """
        Save the board as a pickle containing,
        """
        with open(path, 'wb') as _file:
            pickle.dump([
                self.board,
                self.white_turn,
                self.castling,
                self.unplay_infos
            ], _file)


    def save_for_c_engine(self, path):
        """
        Save the board as a text file, to be parsed & used by the C engine
        """
        correspondance = {
            "pawn": 1,
            "rook": 2,
            "knight": 3,
            "bishop": 4,
            "queen": 5,
            "king": 6,
        }
        to_dump = "w_turn = {}\n".format(int(self.white_turn))
        to_dump += "w_score = {}\n".format(self.score())
        to_dump += "w_king_pos = {}\n".format(
            8 * (7 - self.king_position['white'][0]) +
            self.king_position['white'][1]
        )
        to_dump += "b_king_pos = {}\n".format(
            8 * (7 - self.king_position['black'][0]) +
            self.king_position['black'][1]
        )
        to_dump += "castling_wl = {}\n".format(
            int(self.castling['white']['left']))
        to_dump += "castling_wr = {}\n".format(
            int(self.castling['white']['right']))
        to_dump += "castling_bl = {}\n".format(
            int(self.castling['black']['left']))
        to_dump += "castling_br = {}\n".format(
            int(self.castling['black']['right']))

        for row in range(7, -1, -1):
            for col in range(8):
                if self.board[row][col]["color"] == "blank":
                    to_dump += "0\n"
                else:
                    to_dump += "{}\n".format(
                        (2*int(self.board[row][col]["color"] == "white") - 1) *\
                        correspondance[self.board[row][col]["type"]]
                    )
        with open(path, 'w') as _file:
            _file.write(to_dump)


    def load(self, path):
        """
        Loads a file and changes the object to match the stored one.
        """
        with open(path, 'rb') as _file:
            board, white_turn, castling, unplay_infos = pickle.load(_file)
        self.__init__(board=board, castling=castling, white_turn=white_turn)
        self.unplay_infos = unplay_infos


    @property
    def am_i_finished(self):
        """
        Tests if a situation is a checkmate or a draw
        """
        if not self.all_available_movements(self.turn, 0):
            if self.am_i_check():
                return True, 'mate'
            return True, 'draw'
        return False, ''


    def am_i_check(self, color=None):
        """
        Uses is_check2 to determine wheter or not your are checked. Uses current
        turn by default.
        """
        if color is None:
            color = self.turn
        return is_check2(color, self.board, self.king_position)


    def am_i_check_fast(self, start, arrival, color=None):
        """
        Uses fast_is_check2 to determine wheter or not your are checked.
        Uses current turn by default.
        """
        if color is None:
            color = self.turn
        return fast_is_check2(color, self.board, start, arrival,
                              self.king_position)


    def available_movements(self, location, am_i_check=None):
        """
        Take a departure location and a board and returns a list of possible
        arrival positions, using available_movements_raw, but taking check into
        account fast_is_check only works if the king isn't moved and you are not
        already check
        """
        to_return = []
        board = self.board
        color = board[location[0]][location[1]]['color']
        type_ = board[location[0]][location[1]]['type']

        if am_i_check is None:
            am_i_check = self.am_i_check()

        castling_left = self.castling[color]['left'] and not am_i_check
        castling_right = self.castling[color]['right'] and not am_i_check

        use_slow = am_i_check or type_ == 'king'

        for arrival in available_movements_raw(location, board):

            if use_slow:
                unplay_infos = self.play(location, arrival, update_cast=False)
                if not self.am_i_check(color):
                    to_return.append(arrival)
                self.unplay(*unplay_infos)

            else:
                if not self.am_i_check_fast(location, arrival, color=color):
                    to_return.append(arrival)


        # Add castling moves (only king move, play() will deduce and move the
        # rook)
        if type_ == 'king' and (castling_left or castling_right):
            row = location[0]
            # If left castling is available and there is no "obstacle" -> go
            if castling_left and board[row][1]['color'] == 'blank' and \
                board[row][2]['color'] == 'blank' and \
                board[row][3]['color'] == 'blank':
                # Check if in check on the way
                unplay_infos = self.play(location, (row, location[1] - 1),
                                         update_cast=False)
                if not self.am_i_check(color):
                    # Check if not checked at arrival
                    unplay_infos2 = self.play((row, location[1] - 1),
                                              (row, location[1] - 2),
                                              update_cast=False)
                    if not self.am_i_check(color):
                        to_return.append((row, location[1] - 2))
                    self.unplay(*unplay_infos2)
                self.unplay(*unplay_infos)

            # If right castling is available and there is no "obstacle" -> go
            if castling_right and board[row][5]['color'] == 'blank' and \
                board[row][6]['color'] == 'blank':
                # Check if in check on the way
                unplay_infos = self.play(location, (row, location[1] + 1),
                                         update_cast=False)
                if not self.am_i_check(color):
                    # Check if not checked at arrival
                    unplay_infos2 = self.play((row, location[1] + 1),
                                              (row, location[1] + 2),
                                              update_cast=False)
                    if not self.am_i_check(color):
                        to_return.append((row, location[1] + 2))
                    self.unplay(*unplay_infos2)
                self.unplay(*unplay_infos)

        return to_return


    def all_available_movements(self, color, current_score, am_i_check=None,
                                pos_score=True):
        """
        Takes a color, a board a current score and returns a list of dict
        containing:
            'from': departure location
            'to': arrival location
            'score': next score after this play
            'next': empty list to be used in evaluate_best
        """
        to_return = []
        tr_app = to_return.append
        castling_left = self.castling[color]['left']
        castling_right = self.castling[color]['right']
        for r_nb, row in enumerate(self.board):
            for c_nb, piece in enumerate(row):
                if piece['color'] == color:
                    amv = self.available_movements((r_nb, c_nb),
                                                   am_i_check=am_i_check)
                    for new_r, new_c in amv:
                        new_score = current_score + \
                            score_per_play((new_r, new_c), self.board) * \
                                (2*int(pos_score)-1)
                        # Bring a pawn to the edge -> +/- 8
                        if piece['type'] == 'pawn' and \
                            (new_r == 0 or new_r == 7):
                            new_score += 8 * (2*int(pos_score)-1)

                        # Castling: fictive +0.1 bonus
                        krow = 7 if color == 'white' else 0
                        if piece['type'] == 'king' and abs(new_c - c_nb) == 2:
                            new_score += 0.1 * (2*int(pos_score)-1)

                        # Lose both future castling: fictive -0.1
                        elif castling_left and not castling_right and \
                            (r_nb, c_nb) == (krow, 0):
                            new_score -= 0.1 * (2*int(pos_score)-1)
                        elif castling_right and not castling_left and \
                            (r_nb, c_nb) == (krow, 7):
                            new_score -= 0.1 * (2*int(pos_score)-1)
                        elif (castling_right or castling_left) and \
                            piece['type'] == 'king':
                            new_score -= 0.1 * (2*int(pos_score)-1)

                        tr_app({
                            'from': (r_nb, c_nb),
                            'to': (new_r, new_c),
                            'score': new_score,
                        })

        return to_return


    def build_tree(self, depth):
        """
        Constructs a tree of possible actions
        """
        killers = [None for _ in range(depth + 1)]
        nodes_seen = [0]
        is_hero_white = self.white_turn

        def sort_by_interest(tree, randomize=False, danger_first=False,
                             checkers_first=False, killer_move=None):
            """
            Unefficient function to sort nodes from a tree in order of potential
            interest (check positions first, then enemy pieces killing)
            """
            maximize = self.white_turn == is_hero_white

            # Randomize first
            if randomize:
                shuffle(tree)
            _sorted = 0

            # Killer move first
            if not killer_move is None:
                for n, elt in enumerate(tree):
                    if elt['from'] == killer_move['from'] and \
                        elt['to'] == killer_move['to']:
                        tree[0], tree[n] = tree[n], tree[0]
                        _sorted += 1
                        break

            # Checkers first
            if checkers_first:
                for n in range(_sorted + 1, len(tree)):
                    unplay_data = self.play(tree[n]['from'], tree[n]['to'])
                    if self.am_i_check():
                        tree[_sorted], tree[n] = tree[n], tree[_sorted]
                        _sorted += 1
                    self.unplay(*unplay_data)

            # Basic sorting method by direct score (kills first !)
            for i in range(_sorted + 1, len(tree)):
                _idx = i
                _max_or_min = tree[i]['score']
                for j in range(i + 1, len(tree)):
                    if maximize and tree[j]['score'] > _max_or_min:
                        _max_or_min = tree[j]['score']
                        _idx = j
                    if (not maximize) and tree[j]['score'] > _max_or_min:
                        _max_or_min = tree[j]['score']
                        _idx = j
                tree[i], tree[_idx] = tree[_idx], tree[i]

            if danger_first:
                # Avoid kill first (amongst null scores)
                # index is to be at the beginning of null score
                index = len(tree) - 1
                while index >= 0 and tree[index]['score'] == tree[-1]['score']:
                    index -= 1
                # List all in danger pieces
                in_danger = []
                enemy_moves = self.all_available_movements(
                    'black' if self.white_turn else 'white',
                    0,
                )
                for elt in enemy_moves:
                    if elt['score'] > 0:
                        in_danger.append(elt['to'])
                # Put endangered pieces moves first (after other sorted pieces)
                for idx2 in range(index, len(tree)):
                    if tree[idx2]['from'] in in_danger:
                        tree[index], tree[idx2] = tree[idx2], tree[index]
                        index += 1

        def internal_evaluate(current_depth, current_score, current_checked,
                              alpha, beta):
            """
            Returns subtree, current_lambda, best_index
            """
            nodes_seen[0] += 1
            if current_depth == 0:
                return [], current_score, -1

            moves = self.all_available_movements(
                self.turn,
                current_score,
                pos_score=self.white_turn == is_hero_white,
                am_i_check=None
            )

            # Positive if current color is hero's one
            sign = 2 * (self.white_turn == is_hero_white) - 1

            # Treat checkmate and draw cases
            if not moves:
                if self.am_i_check(color=self.turn):
                    return [], -sign*1000, -1
                return [], 0, -1

            new_alpha, new_beta = alpha, beta

            if sign == 1:
                nu = -5000
            else:
                nu = 5000

            best_index = -1

            sort_by_interest(
                moves,
                randomize=depth - current_depth < 2,
                danger_first=depth - current_depth < 4,
                checkers_first=depth - current_depth < 4,
                killer_move=killers[current_depth],
            )

            for n, move in enumerate(moves):

                if current_depth == depth:
                    print('{}/{} {} {} -> {}'.format(
                        str(n+1).zfill(2),
                        len(moves),
                        self.board[move['from'][0]]
                            [move['from'][1]]['type'].ljust(6),
                        readable_position(move['from']),
                        readable_position(move['to']),
                    ))
                    print('{}%'.format(int(100*n/len(moves))), end='\r')

                unplay_infos = self.play(move['from'], move['to'])

                next_list, next_nu, _ = internal_evaluate(
                    current_depth - 1,
                    move['score'],
                    # TODO: use is_enemy_check
                    False,
                    new_alpha,
                    new_beta,
                )

                move['next'] = next_list

                # Hero play (maximiser)
                if sign == 1 and next_nu > nu:
                    nu = next_nu
                    best_index = n
                if sign == -1 and next_nu < nu:
                    nu = next_nu
                    best_index = n

                # update alpha, beta (avoiding using min/max)
                if sign == 1 and nu > new_alpha:
                    new_alpha = next_nu
                if sign == -1 and nu < new_beta:
                    new_beta = next_nu

                self.unplay(*unplay_infos)

                if new_alpha >= new_beta or new_alpha > 900 or new_beta < -900:
                    killers[current_depth] = move
                    break

            return moves, nu, best_index

        time_start = time()
        tree, _, best_index = internal_evaluate(
            depth,
            self.score(),
            is_check2(self.turn, self.board, self.king_position),
            -5000,
            5000
        )

        elapsed = time()-time_start
        print('Time Elapsed: {:.2f} s'.format(elapsed))
        print('Nodes Explored: {}, {:.0f} n/s'.format(
            nodes_seen[0],
            nodes_seen[0] / elapsed
        ))
        return tree, best_index
