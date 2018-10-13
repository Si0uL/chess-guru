from time import time
from copy import deepcopy
from random import shuffle

from board import Piece

def available_movements_raw(location, board):
    """
    Takes a location and a board and return the available moves as a series of
    arrival position tuple.
    WARNING: does not take into account check
    TODO: add castling and en-passant
    """

    typ = board[location[0]][location[1]].type
    col = board[location[0]][location[1]].color

    if typ == 'rook' or typ == 'queen':
        # down
        r, c = location[0] + 1, location[1]
        while r < 8 and board[r][c].is_blank:
            yield (r, c)
            r += 1
        if r < 8 and board[r][c].color != col:
            yield (r, c)
        # up
        r, c = location[0] - 1, location[1]
        while r > -1 and board[r][c].is_blank:
            yield (r, c)
            r -= 1
        if r > -1 and board[r][c].color != col:
            yield (r, c)
        # right
        r, c = location[0], location[1] + 1
        while c < 8 and board[r][c].is_blank:
            yield (r, c)
            c += 1
        if c < 8 and board[r][c].color != col:
            yield (r, c)
        # left
        r, c = location[0], location[1] - 1
        while c > -1 and board[r][c].is_blank:
            yield (r, c)
            c -= 1
        if c > -1 and board[r][c].color != col:
            yield (r, c)

    if typ == 'bishop' or typ == 'queen':
        # downright
        r, c = location[0] + 1, location[1] + 1
        while r < 8 and c < 8 and board[r][c].is_blank:
            yield (r, c)
            r += 1
            c += 1
        if r < 8 and c < 8 and board[r][c].color != col:
            yield (r, c)
        # upright
        r, c = location[0] - 1, location[1] + 1
        while r > -1 and c < 8 and board[r][c].is_blank:
            yield (r, c)
            r -= 1
            c += 1
        if r > -1 and c < 8 and board[r][c].color != col:
            yield (r, c)
        # upleft
        r, c = location[0] - 1, location[1] - 1
        while r > -1 and c > -1 and board[r][c].is_blank:
            yield (r, c)
            r -= 1
            c -= 1
        if r > -1 and c > -1 and board[r][c].color != col:
            yield (r, c)
        # downleft
        r, c = location[0] + 1, location[1] - 1
        while r < 8 and c > -1 and board[r][c].is_blank:
            yield (r, c)
            r += 1
            c -= 1
        if r < 8 and c > -1 and board[r][c].color != col:
            yield (r, c)

    elif typ == 'pawn':
        # black: +1 / white: -1
        _sense = int(col == 'black')*2 - 1

        # Straight
        if board[location[0] + _sense][location[1]].is_blank:
            yield (location[0] + _sense, location[1])
            # 2 straight
            if location[0] == 6 and col == 'white' and \
                board[4][location[1]].is_blank:
                yield (4, location[1])
            elif location[0] == 1 and col == 'black' and \
                board[3][location[1]].is_blank:
                yield (3, location[1])
            else:
                pass
        # Kill an enemy (left)
        if location[1] != 0 and \
            board[location[0] + _sense][location[1] - 1].color == enemy(col):
            yield (location[0] + _sense, location[1] - 1)
        # Kill an enemy (right)
        if location[1] != 7 and \
            board[location[0] + _sense][location[1] + 1].color == enemy(col):
            yield (location[0] + _sense, location[1] + 1)

    elif typ == 'knight':
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2),
                        (1, -2), (-1, -2)]
        for addr, addc in knight_moves:
            nr, nc = location[0] + addr, location[1] + addc
            if nr < 8 and nc < 8 and nr > -1 and nc > -1 and \
                board[nr][nc].color != col:
                yield(nr, nc)

    elif typ == 'king':
        for addr in range(-1, 2):
            for addc in range(-1, 2):
                if not (addr == 0 and addc == 0):
                    nr, nc = location[0] + addr, location[1] + addc
                    if nr < 8 and nc < 8 and nr > -1 and nc > -1 and \
                        board[nr][nc].color != col:
                        yield(nr, nc)

def score_per_play(arrival, board):
    """
    Return positive score gain if movement kills a piece, else 0
    TODO: take into account piece creation
    """
    _type = board[arrival[0]][arrival[1]].type
    if _type is None:
        return 0
    elif _type == 'pawn':
        return 1
    elif _type == 'knight' or _type == 'bishop':
        return 3
    elif _type == 'rook':
        return 5
    elif _type == 'queen':
        return 9
    return 0

def enemy(color):
    """
    'inverts' the color
    """
    if color == 'white':
        return 'black'
    elif color == 'black':
        return 'white'
    return None

def _is_in_danger(position, board):
    """
    Checks if the piece located at position is in danger (in sight of an enemy
    piece)
    """
    row, col = position
    color = board[row][col].color
    enemy_col = enemy(color)

    # Down Right diag
    dist = 1
    while row + dist < 8 and col + dist < 8 and \
        board[row + dist][col + dist].is_blank:
        dist += 1
    if row + dist < 8 and col + dist < 8:
        _piece = board[row + dist][col + dist]
        _type = _piece.type
        if _piece.color == enemy_col and (
                _type == 'queen' or
                _type == 'bishop' or
                (dist == 1 and (
                    _type == 'king' or
                    (color == 'black' and _type == 'pawn')
                ))
        ):
            return True

    # Down Left diag
    dist = 1
    while row + dist < 8 and col - dist >= 0 and \
        board[row + dist][col - dist].is_blank:
        dist += 1
    if row + dist < 8 and col - dist >= 0:
        _piece = board[row + dist][col - dist]
        _type = _piece.type
        if _piece.color == enemy_col and (
                _type == 'queen' or
                _type == 'bishop' or
                (dist == 1 and (
                    _type == 'king' or
                    (color == 'black' and _type == 'pawn')
                ))
        ):
            return True

    # Up Left diag
    dist = 1
    while row - dist >= 0 and col - dist >= 0 and \
        board[row - dist][col - dist].is_blank:
        dist += 1
    if row - dist >= 0 and col - dist >= 0:
        _piece = board[row - dist][col - dist]
        _type = _piece.type
        if _piece.color == enemy_col and (
                _type == 'queen' or
                _type == 'bishop' or
                (dist == 1 and (
                    _type == 'king' or
                    (color == 'white' and _type == 'pawn')
                ))
        ):
            return True

    # Up Right diag
    dist = 1
    while row - dist >= 0 and col + dist < 8 and \
        board[row - dist][col + dist].is_blank:
        dist += 1
    if row - dist >= 0 and col + dist < 8:
        _piece = board[row - dist][col + dist]
        _type = _piece.type
        if _piece.color == enemy_col and (
                _type == 'queen' or
                _type == 'bishop' or
                (dist == 1 and (
                    _type == 'king' or
                    (color == 'white' and _type == 'pawn')
                ))
        ):
            return True

    # Up line
    dist = 1
    while row - dist >= 0 and board[row - dist][col].is_blank:
        dist += 1
    if row - dist >= 0:
        _piece = board[row - dist][col]
        if _piece.color == enemy_col and (
                _piece.type == 'queen' or
                _piece.type == 'rook' or
                (dist == 1 and _piece.type == 'king')
        ):
            return True

    # Right line
    dist = 1
    while col + dist < 8 and board[row][col + dist].is_blank:
        dist += 1
    if col + dist < 8:
        _piece = board[row][col + dist]
        if _piece.color == enemy_col and (
                _piece.type == 'queen' or
                _piece.type == 'rook' or
                (dist == 1 and _piece.type == 'king')
        ):
            return True

    # Down line
    dist = 1
    while row + dist < 8 and board[row + dist][col].is_blank:
        dist += 1
    if row + dist < 8:
        _piece = board[row + dist][col]
        if _piece.color == enemy_col and (
                _piece.type == 'queen' or
                _piece.type == 'rook' or
                (dist == 1 and _piece.type == 'king')
        ):
            return True

    # Left line
    dist = 1
    while col - dist >= 0 and board[row][col - dist].is_blank:
        dist += 1
    if col - dist >= 0:
        _piece = board[row][col - dist]
        if _piece.color == enemy_col and (
                _piece.type == 'queen' or
                _piece.type == 'rook' or
                (dist == 1 and _piece.type == 'king')
        ):
            return True

    # Checking for knights to end with
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2),
                    (1, -2), (-1, -2)]
    for addr, addc in knight_moves:
        nr, nc = row + addr, col + addc
        if nr < 8 and nc < 8 and nr > -1 and nc > -1 and \
            board[nr][nc].color == enemy_col and \
            board[nr][nc].type == 'knight':
            return True

    return False

def is_check2(color, board, kpos):
    """
    Quicker version of is_check
    Takes a color and a board and returns a boolean whether the player is check
    or not
    """
    position = kpos[color]
    return _is_in_danger(position, board)

def fast_is_check2(color, board, departure, arrival, kpos):
    """
    Quicker version of is_check2
    You have not to be in check position before playing departure -> arrival.
    Your movement should not concern your king.
    board is just before the play departure -> arrival
    We check here if moving this doesn't affect you check state. To do so, only
    the concerned row or diag shared by the king and the moved piece is
    re-checked.
    Done to be used BEFORE using play() (to avoid using it if unauthorised) but
    you can use it after.
    """
    enemy_col = enemy(color)
    rkg, ckg = kpos[color]

    delta_row, delta_col = departure[0] - rkg, departure[1] - ckg

    # Alterate board!
    org_color = board[departure[0]][departure[1]].color
    board[departure[0]][departure[1]].color = 'blank'

    if delta_row == 0:
        if delta_col > 0:
            # Right line
            dist = 1
            while ckg + dist < 8 and board[rkg][ckg + dist].is_blank:
                dist += 1
            if ckg + dist < 8:
                _piece = board[rkg][ckg + dist]
                if _piece.color == enemy_col and (
                        _piece.type == 'queen' or
                        _piece.type == 'rook'
                ):
                    if not (arrival[0] - rkg == 0 and arrival[1] > ckg and
                            arrival[1] - ckg <= dist):
                        board[departure[0]][departure[1]].color = org_color
                        return True
        else:
            # Left line
            dist = 1
            while ckg - dist >= 0 and board[rkg][ckg - dist].is_blank:
                dist += 1
            if ckg - dist >= 0:
                _piece = board[rkg][ckg - dist]
                if _piece.color == enemy_col and (
                        _piece.type == 'queen' or
                        _piece.type == 'rook'
                ):
                    if not (arrival[0] - rkg == 0 and arrival[1] < ckg and
                            ckg - arrival[1] <= dist):
                        board[departure[0]][departure[1]].color = org_color
                        return True

    elif delta_col == 0:
        if delta_row > 0:
            # Down line
            dist = 1
            while rkg + dist < 8 and board[rkg + dist][ckg].is_blank:
                dist += 1
            if rkg + dist < 8:
                _piece = board[rkg + dist][ckg]
                if _piece.color == enemy_col and (
                        _piece.type == 'queen' or
                        _piece.type == 'rook'
                ):
                    if not (arrival[1] - ckg == 0 and arrival[0] > rkg and
                            arrival[0] - rkg <= dist):
                        board[departure[0]][departure[1]].color = org_color
                        return True
        else:
            # Up line
            dist = 1
            while rkg - dist >= 0 and board[rkg - dist][ckg].is_blank:
                dist += 1
            if rkg - dist >= 0:
                _piece = board[rkg - dist][ckg]
                if _piece.color == enemy_col and (
                        _piece.type == 'queen' or
                        _piece.type == 'rook'
                ):
                    if not (arrival[1] - ckg == 0 and arrival[0] < rkg and
                            rkg - arrival[0] <= dist):
                        board[departure[0]][departure[1]].color = org_color
                        return True

    elif abs(delta_row) == abs(delta_col):
        if delta_row > 0:
            if delta_col > 0:
                # Down Right diag
                dist = 1
                while rkg + dist < 8 and ckg + dist < 8 and \
                    board[rkg + dist][ckg + dist].is_blank:
                    dist += 1
                if rkg + dist < 8 and ckg + dist < 8:
                    _piece = board[rkg + dist][ckg + dist]
                    _type = _piece.type
                    if _piece.color == enemy_col and (
                            _type == 'queen' or
                            _type == 'bishop'
                    ):
                        if not (arrival[0] - rkg == arrival[1] - ckg and
                                arrival[0] - rkg <= dist):
                            board[departure[0]][departure[1]].color = org_color
                            return True
            else:
                # Down Left diag
                dist = 1
                while rkg + dist < 8 and ckg - dist >= 0 and \
                    board[rkg + dist][ckg - dist].is_blank:
                    dist += 1
                if rkg + dist < 8 and ckg - dist >= 0:
                    _piece = board[rkg + dist][ckg - dist]
                    _type = _piece.type
                    if _piece.color == enemy_col and (
                            _type == 'queen' or
                            _type == 'bishop'
                    ):
                        if not (arrival[0] - rkg == ckg - arrival[1] and
                                arrival[0] - rkg <= dist):
                            board[departure[0]][departure[1]].color = org_color
                            return True

        else:
            if delta_col > 0:
                # Up Right diag
                dist = 1
                while rkg - dist >= 0 and ckg + dist < 8 and \
                    board[rkg - dist][ckg + dist].is_blank:
                    dist += 1
                if rkg - dist >= 0 and ckg + dist < 8:
                    _piece = board[rkg - dist][ckg + dist]
                    _type = _piece.type
                    if _piece.color == enemy_col and (
                            _type == 'queen' or
                            _type == 'bishop'
                    ):
                        if not (rkg - arrival[0] == arrival[1] - ckg and
                                rkg - arrival[0] <= dist):
                            board[departure[0]][departure[1]].color = org_color
                            return True
            else:
                # Up Left diag
                dist = 1
                while rkg - dist >= 0 and ckg - dist >= 0 and \
                    board[rkg - dist][ckg - dist].is_blank:
                    dist += 1
                if rkg - dist >= 0 and ckg - dist >= 0:
                    _piece = board[rkg - dist][ckg - dist]
                    _type = _piece.type
                    if _piece.color == enemy_col and (
                            _type == 'queen' or
                            _type == 'bishop'
                    ):
                        if not (rkg - arrival[0] == ckg - arrival[1] and
                                rkg - arrival[0] <= dist):
                            board[departure[0]][departure[1]].color = org_color
                            return True

    board[departure[0]][departure[1]].color = org_color
    return False

def is_enemy_check(enemy_color, board, departure, arrival,
                   kpos):
    """
    To be used after play() method
    """
    rkg, ckg = kpos[enemy_color]
    return kpos in available_movements_raw(arrival, board) or \
        fast_is_check2(enemy_color, board, departure, arrival, kpos)

def get_score(color, board):
    """
    Takes a color and a board and return a score (+ in favour of the color)
    """
    values = {
        'pawn': 1,
        'rook': 5,
        'knight': 3,
        'bishop': 3,
        'queen': 9,
    }
    to_return = 0
    for row in board:
        for piece in row:
            to_return += (2*int(piece.color == color) - 1) * \
                values.get(piece.type, 0)
    return to_return

def readable_position(pos):
    """
    Converts tuple to readable chess position:
    example: (6, 3) -> "d2"
    """
    return ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'][pos[1]] + str(8 - pos[0])

def missing_pieces(board):
    """
    Finds who is missing in the board to show taken pieces
    """
    missing = {
        'black': {
            'king': 1,
            'queen': 1,
            'bishop': 2,
            'knight': 2,
            'rook': 2,
            'pawn': 8,
        },
    }
    missing['white'] = deepcopy(missing['black'])
    for row in board:
        for elt in row:
            if not elt.is_blank:
                missing[elt.color][elt.type] -= 1
    to_return = {
        "black": [],
        "white": [],
    }
    for _color in to_return:
        for _type in ['queen', 'rook', 'bishop', 'knight', 'pawn']:
            for _ in range(missing[_color][_type]):
                to_return[_color].append(_type)
    to_return['black'].reverse()
    return to_return

def print_board(board):
    """
    To print a board in console.
    """
    def _print_piece(piece):
        initials = {
            'pawn': 'p',
            'rook': 'r',
            'knight': 'k',
            'bishop': 'b',
            'queen': 'q',
            'king': 'g',
        }
        if piece.is_blank:
            print('   ', end=' ')
        elif piece.color == 'black':
            print(' B' + initials[piece.type], end=' ')
        else:
            print(' W' + initials[piece.type], end=' ')

    line = '\n' + '-' * (8 * 4 + 9)
    for row in board:
        print(line)
        print('|', end='')
        for piece in row:
            _print_piece(piece)
            print('|', end='')
    print(line)
