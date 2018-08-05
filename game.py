"""
Chess game object
"""

from copy import deepcopy
import pickle

from board import BOARD
from utils import (
    print_board,
    get_score,
    missing_pieces,
    is_check_mate_or_draw,
    available_movements_raw,
    is_check2,
    fast_is_check2,
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
        Calls is_check_mate_or_draw to determine if the game if finished
        """
        return is_check_mate_or_draw(self.turn, self.board)


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
