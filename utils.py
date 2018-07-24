from time import time
from copy import deepcopy
from random import shuffle

def available_movements_raw(location, board):
    """
    Takes a location and a board and return the available moves as a series of
    arrival position tuple.
    WARNING: does not take into account check
    TODO: add castling and en-passant
    """

    typ = board[location[0]][location[1]].get('type')
    col = board[location[0]][location[1]]['color']

    if typ == 'rook' or typ == 'queen':
        # down
        r, c = location[0] + 1, location[1]
        while r < 8 and board[r][c]['color'] == 'blank':
            yield (r, c)
            r += 1
        if r < 8 and board[r][c]['color'] != col:
            yield (r, c)
        # up
        r, c = location[0] - 1, location[1]
        while r > -1 and board[r][c]['color'] == 'blank':
            yield (r, c)
            r -= 1
        if r > -1 and board[r][c]['color'] != col:
            yield (r, c)
        # right
        r, c = location[0], location[1] + 1
        while c < 8 and board[r][c]['color'] == 'blank':
            yield (r, c)
            c += 1
        if c < 8 and board[r][c]['color'] != col:
            yield (r, c)
        # left
        r, c = location[0], location[1] - 1
        while c > -1 and board[r][c]['color'] == 'blank':
            yield (r, c)
            c -= 1
        if c > -1 and board[r][c]['color'] != col:
            yield (r, c)

    if typ == 'bishop' or typ == 'queen':
        # downright
        r, c = location[0] + 1, location[1] + 1
        while r < 8 and c < 8 and board[r][c]['color'] == 'blank':
            yield (r, c)
            r += 1
            c += 1
        if r < 8 and c < 8 and board[r][c]['color'] != col:
            yield (r, c)
        # upright
        r, c = location[0] - 1, location[1] + 1
        while r > -1 and c < 8 and board[r][c]['color'] == 'blank':
            yield (r, c)
            r -= 1
            c += 1
        if r > -1 and c < 8 and board[r][c]['color'] != col:
            yield (r, c)
        # upleft
        r, c = location[0] - 1, location[1] - 1
        while r > -1 and c > -1 and board[r][c]['color'] == 'blank':
            yield (r, c)
            r -= 1
            c -= 1
        if r > -1 and c > -1 and board[r][c]['color'] != col:
            yield (r, c)
        # downleft
        r, c = location[0] + 1, location[1] - 1
        while r < 8 and c > -1 and board[r][c]['color'] == 'blank':
            yield (r, c)
            r += 1
            c -= 1
        if r < 8 and c > -1 and board[r][c]['color'] != col:
            yield (r, c)

    elif typ == 'pawn':
        # black: +1 / white: -1
        _sense = int(col == 'black')*2 - 1

        # Straight
        if board[location[0] + _sense][location[1]]['color'] == 'blank':
            yield (location[0] + _sense, location[1])
            # 2 straight
            if location[0] == 6 and col == 'white' and \
                board[4][location[1]]['color'] == 'blank':
                yield (4, location[1])
            elif location[0] == 1 and col == 'black' and \
                board[3][location[1]]['color'] == 'blank':
                yield (3, location[1])
            else:
                pass
        # Kill an enemy (left)
        if location[1] != 0 and \
            board[location[0] + _sense][location[1] - 1]['color'] == enemy(col):
            yield (location[0] + _sense, location[1] - 1)
        # Kill an enemy (right)
        if location[1] != 7 and \
            board[location[0] + _sense][location[1] + 1]['color'] == enemy(col):
            yield (location[0] + _sense, location[1] + 1)

    elif typ == 'knight':
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2),
                        (1, -2), (-1, -2)]
        for addr, addc in knight_moves:
            nr, nc = location[0] + addr, location[1] + addc
            if nr < 8 and nc < 8 and nr > -1 and nc > -1 and \
                board[nr][nc]['color'] != col:
                yield(nr, nc)

    elif typ == 'king':
        for addr in range(-1, 2):
            for addc in range(-1, 2):
                if not (addr == 0 and addc == 0):
                    nr, nc = location[0] + addr, location[1] + addc
                    if nr < 8 and nc < 8 and nr > -1 and nc > -1 and \
                        board[nr][nc]['color'] != col:
                        yield(nr, nc)

def available_movements(location, board, castling_left=False,
                        castling_right=False, kpos=None, am_i_check=None):
    """
    Take a departure location and a board and returns a list of possible arrival
    positions, using available_movements_raw, but taking check into account
    fast_is_check only works if the king isn't moved and you are not already
    check
    """
    to_return = []
    color = board[location[0]][location[1]]['color']

    if am_i_check is None:
        am_i_check = is_check2(color, board, kpos)

    if am_i_check:
        castling_left = castling_right = False

    use_slow = am_i_check or board[location[0]][location[1]]['type'] == 'king'

    for arrival in available_movements_raw(location, board):

        if use_slow:
            unplay_infos = play(location, arrival, board, kpos)
            if not is_check2(color, board, kpos):
                to_return.append(arrival)
            unplay(*unplay_infos, board=board, kpos=kpos)

        else:
            if not fast_is_check2(color, board, location, arrival, kpos):
                to_return.append(arrival)


    # Add castling moves (only king move, play() will deduce and move the rook)
    if board[location[0]][location[1]]['type'] == 'king' and \
        (castling_left or castling_right):
        row = location[0]
        # If left castling is available and there is no "obstacle" -> go
        if castling_left and board[row][1]['color'] == 'blank' and \
            board[row][2]['color'] == 'blank' and \
            board[row][3]['color'] == 'blank':
            # Check if in check on the way
            unplay_infos = play(location, (row, location[1] - 1), board, kpos)
            if not is_check2(color, board, kpos):
                # Check if not checked at arrival
                unplay_infos2 = play((row, location[1] - 1),
                                     (row, location[1] - 2), board, kpos)
                if not is_check2(color, board, kpos):
                    to_return.append((row, location[1] - 2))
                unplay(*unplay_infos2, board=board, kpos=kpos)
            unplay(*unplay_infos, board=board, kpos=kpos)

        # If right castling is available and there is no "obstacle" -> go
        if castling_right and board[row][5]['color'] == 'blank' and \
            board[row][6]['color'] == 'blank':
            # Check if in check on the way
            unplay_infos = play(location, (row, location[1] + 1), board, kpos)
            if not is_check2(color, board, kpos):
                # Check if not checked at arrival
                unplay_infos2 = play((row, location[1] + 1),
                                     (row, location[1] + 2), board, kpos)
                if not is_check2(color, board, kpos):
                    to_return.append((row, location[1] + 2))
                unplay(*unplay_infos2, board=board, kpos=kpos)
            unplay(*unplay_infos, board=board, kpos=kpos)

    return to_return

def play(start, arrival, board, kpos=None):
    """
    Puts piece located at start at arrival position, MODIFIES board
    TODO: add piece creation
    """
    former_start = board[start[0]][start[1]]
    former_arrival = board[arrival[0]][arrival[1]]
    board[arrival[0]][arrival[1]] = former_start
    board[start[0]][start[1]] = {'color': 'blank'}
    # If pawn at edge: transform it into a queen by default
    if former_start['type'] == 'pawn' and (arrival[0] == 0 or arrival[0] == 7):
        # Recreate an object to avoid side effects
        board[arrival[0]][arrival[1]] = {
            'type': 'queen',
            'color': former_start['color'],
        }
    # If king castling: move also the rook:
    if former_start['type'] == 'king' and abs(start[1] - arrival[1]) == 2:
        # Left castling
        if arrival[1] == 2:
            board[start[0]][3] = {
                'type': 'rook',
                'color': former_start['color']
            }
            board[start[0]][0] = {'color': 'blank'}
        # Right castling
        if arrival[1] == 6:
            board[start[0]][5] = {
                'type': 'rook',
                'color': former_start['color']
            }
            board[start[0]][7] = {'color': 'blank'}

    # Update kpos
    if not kpos is None and former_start['type'] == 'king':
        kpos[former_start['color']] = arrival

    return start, former_start, arrival, former_arrival

def unplay(start, former_start, arrival, former_arrival, board, kpos=None):
    """
    Undo the efect of the play() function. MODIFIES board
    """
    board[start[0]][start[1]] = former_start
    board[arrival[0]][arrival[1]] = former_arrival
    # If king castling: move also the rook:
    if former_start['type'] == 'king' and abs(start[1] - arrival[1]) == 2:
        # Left castling
        if arrival[1] == 2:
            board[start[0]][0] = {
                'type': 'rook',
                'color': former_start['color']
            }
            board[start[0]][3] = {'color': 'blank'}
        # Right castling
        if arrival[1] == 6:
            board[start[0]][7] = {
                'type': 'rook',
                'color': former_start['color']
            }
            board[start[0]][5] = {'color': 'blank'}

    # If kpos given, update it:
    if not kpos is None and former_start['type'] == 'king':
        kpos[former_start['color']] = start

def score_per_play(arrival, board):
    """
    Return positive score gain if movement kills a piece, else 0
    TODO: take into account piece creation
    """
    _type = board[arrival[0]][arrival[1]].get('type')
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

def king_position(color, board):
    """
    Takes a color and a board and return the color's king location
    """
    for r, row in enumerate(board):
        for c, piece in enumerate(row):
            if piece.get('type') == 'king' and piece['color'] == color:
                return r, c
    return None

def enemy(color):
    """
    'inverts' the color
    """
    if color == 'white':
        return 'black'
    elif color == 'black':
        return 'white'
    return None

def is_check2(color, board, kpos=None):
    """
    Quicker version of is_check
    Takes a color and a board and returns a boolean whether the player is check
    or not
    """
    enemy_col = enemy(color)
    if kpos is None:
        rkg, ckg = king_position(color, board)
    else:
        rkg, ckg = kpos[color]
    # Down Right diag
    dist = 1
    while rkg + dist < 8 and ckg + dist < 8 and \
        board[rkg + dist][ckg + dist]['color'] == 'blank':
        dist += 1
    if rkg + dist < 8 and ckg + dist < 8:
        _piece = board[rkg + dist][ckg + dist]
        _type = _piece['type']
        if _piece['color'] == enemy_col and (
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
    while rkg + dist < 8 and ckg - dist >= 0 and \
        board[rkg + dist][ckg - dist]['color'] == 'blank':
        dist += 1
    if rkg + dist < 8 and ckg - dist >= 0:
        _piece = board[rkg + dist][ckg - dist]
        _type = _piece['type']
        if _piece['color'] == enemy_col and (
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
    while rkg - dist >= 0 and ckg - dist >= 0 and \
        board[rkg - dist][ckg - dist]['color'] == 'blank':
        dist += 1
    if rkg - dist >= 0 and ckg - dist >= 0:
        _piece = board[rkg - dist][ckg - dist]
        _type = _piece['type']
        if _piece['color'] == enemy_col and (
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
    while rkg - dist >= 0 and ckg + dist < 8 and \
        board[rkg - dist][ckg + dist]['color'] == 'blank':
        dist += 1
    if rkg - dist >= 0 and ckg + dist < 8:
        _piece = board[rkg - dist][ckg + dist]
        _type = _piece['type']
        if _piece['color'] == enemy_col and (
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
    while rkg - dist >= 0 and board[rkg - dist][ckg]['color'] == 'blank':
        dist += 1
    if rkg - dist >= 0:
        _piece = board[rkg - dist][ckg]
        if _piece['color'] == enemy_col and (
                _piece['type'] == 'queen' or
                _piece['type'] == 'rook'
        ):
            return True

    # Right line
    dist = 1
    while ckg + dist < 8 and board[rkg][ckg + dist]['color'] == 'blank':
        dist += 1
    if ckg + dist < 8:
        _piece = board[rkg][ckg + dist]
        if _piece['color'] == enemy_col and (
                _piece['type'] == 'queen' or
                _piece['type'] == 'rook'
        ):
            return True

    # Down line
    dist = 1
    while rkg + dist < 8 and board[rkg + dist][ckg]['color'] == 'blank':
        dist += 1
    if rkg + dist < 8:
        _piece = board[rkg + dist][ckg]
        if _piece['color'] == enemy_col and (
                _piece['type'] == 'queen' or
                _piece['type'] == 'rook'
        ):
            return True

    # Left line
    dist = 1
    while ckg - dist >= 0 and board[rkg][ckg - dist]['color'] == 'blank':
        dist += 1
    if ckg - dist >= 0:
        _piece = board[rkg][ckg - dist]
        if _piece['color'] == enemy_col and (
                _piece['type'] == 'queen' or
                _piece['type'] == 'rook'
        ):
            return True

    # Checking for knights to end with
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2),
                    (1, -2), (-1, -2)]
    for addr, addc in knight_moves:
        nr, nc = rkg + addr, ckg + addc
        if nr < 8 and nc < 8 and nr > -1 and nc > -1 and \
            board[nr][nc]['color'] == enemy_col and \
            board[nr][nc]['type'] == 'knight':
            return True

    return False

def fast_is_check2(color, board, departure, arrival, kpos=None):
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
    if kpos is None:
        rkg, ckg = king_position(color, board)
    else:
        rkg, ckg = kpos[color]

    delta_row, delta_col = departure[0] - rkg, departure[1] - ckg

    # Alterate board!
    org_color = board[departure[0]][departure[1]]['color']
    board[departure[0]][departure[1]]['color'] = 'blank'

    if delta_row == 0:
        if delta_col > 0:
            # Right line
            dist = 1
            while ckg + dist < 8 and board[rkg][ckg + dist]['color'] == 'blank':
                dist += 1
            if ckg + dist < 8:
                _piece = board[rkg][ckg + dist]
                if _piece['color'] == enemy_col and (
                        _piece['type'] == 'queen' or
                        _piece['type'] == 'rook'
                ):
                    if not (arrival[0] - rkg == 0 and arrival[1] > ckg and
                            arrival[1] - ckg <= dist):
                        board[departure[0]][departure[1]]['color'] = org_color
                        return True
        else:
            # Left line
            dist = 1
            while ckg - dist >= 0 and board[rkg][ckg - dist]['color'] == 'blank':
                dist += 1
            if ckg - dist >= 0:
                _piece = board[rkg][ckg - dist]
                if _piece['color'] == enemy_col and (
                        _piece['type'] == 'queen' or
                        _piece['type'] == 'rook'
                ):
                    if not (arrival[0] - rkg == 0 and arrival[1] < ckg and
                            ckg - arrival[1] <= dist):
                        board[departure[0]][departure[1]]['color'] = org_color
                        return True

    elif delta_col == 0:
        if delta_row > 0:
            # Down line
            dist = 1
            while rkg + dist < 8 and board[rkg + dist][ckg]['color'] == 'blank':
                dist += 1
            if rkg + dist < 8:
                _piece = board[rkg + dist][ckg]
                if _piece['color'] == enemy_col and (
                        _piece['type'] == 'queen' or
                        _piece['type'] == 'rook'
                ):
                    if not (arrival[1] - ckg == 0 and arrival[0] > rkg and
                            arrival[0] - rkg <= dist):
                        board[departure[0]][departure[1]]['color'] = org_color
                        return True
        else:
            # Up line
            dist = 1
            while rkg - dist >= 0 and board[rkg - dist][ckg]['color'] == 'blank':
                dist += 1
            if rkg - dist >= 0:
                _piece = board[rkg - dist][ckg]
                if _piece['color'] == enemy_col and (
                        _piece['type'] == 'queen' or
                        _piece['type'] == 'rook'
                ):
                    if not (arrival[1] - ckg == 0 and arrival[0] < rkg and
                            rkg - arrival[0] <= dist):
                        board[departure[0]][departure[1]]['color'] = org_color
                        return True

    elif abs(delta_row) == abs(delta_col):
        if delta_row > 0:
            if delta_col > 0:
                # Down Right diag
                dist = 1
                while rkg + dist < 8 and ckg + dist < 8 and \
                    board[rkg + dist][ckg + dist]['color'] == 'blank':
                    dist += 1
                if rkg + dist < 8 and ckg + dist < 8:
                    _piece = board[rkg + dist][ckg + dist]
                    _type = _piece['type']
                    if _piece['color'] == enemy_col and (
                            _type == 'queen' or
                            _type == 'bishop'
                    ):
                        if not (arrival[0] - rkg == arrival[1] - ckg and
                                arrival[0] - rkg <= dist):
                            board[departure[0]][departure[1]]['color'] = org_color
                            return True
            else:
                # Down Left diag
                dist = 1
                while rkg + dist < 8 and ckg - dist >= 0 and \
                    board[rkg + dist][ckg - dist]['color'] == 'blank':
                    dist += 1
                if rkg + dist < 8 and ckg - dist >= 0:
                    _piece = board[rkg + dist][ckg - dist]
                    _type = _piece['type']
                    if _piece['color'] == enemy_col and (
                            _type == 'queen' or
                            _type == 'bishop'
                    ):
                        if not (arrival[0] - rkg == ckg - arrival[1] and
                                arrival[0] - rkg <= dist):
                            board[departure[0]][departure[1]]['color'] = org_color
                            return True

        else:
            if delta_col > 0:
                # Up Right diag
                dist = 1
                while rkg - dist >= 0 and ckg + dist < 8 and \
                    board[rkg - dist][ckg + dist]['color'] == 'blank':
                    dist += 1
                if rkg - dist >= 0 and ckg + dist < 8:
                    _piece = board[rkg - dist][ckg + dist]
                    _type = _piece['type']
                    if _piece['color'] == enemy_col and (
                            _type == 'queen' or
                            _type == 'bishop'
                    ):
                        if not (rkg - arrival[0] == arrival[1] - ckg and
                                rkg - arrival[0] <= dist):
                            board[departure[0]][departure[1]]['color'] = org_color
                            return True
            else:
                # Up Left diag
                dist = 1
                while rkg - dist >= 0 and ckg - dist >= 0 and \
                    board[rkg - dist][ckg - dist]['color'] == 'blank':
                    dist += 1
                if rkg - dist >= 0 and ckg - dist >= 0:
                    _piece = board[rkg - dist][ckg - dist]
                    _type = _piece['type']
                    if _piece['color'] == enemy_col and (
                            _type == 'queen' or
                            _type == 'bishop'
                    ):
                        if not (rkg - arrival[0] == ckg - arrival[1] and
                                rkg - arrival[0] <= dist):
                            board[departure[0]][departure[1]]['color'] = org_color
                            return True

    board[departure[0]][departure[1]]['color'] = org_color
    return False

def is_enemy_check(enemy_color, board, departure, arrival,
                   kpos):
    """
    To be used after play() method
    """
    rkg, ckg = kpos[enemy_color]
    return kpos in available_movements_raw(arrival, board) or \
        fast_is_check2(enemy_color, board, departure, arrival, kpos)

def is_check_mate_or_draw(color, board):
    """
    Tests if a situation is a checkmate or a draw
    """
    if all_available_movements(color, board, 0, None, False, False) == []:
        if is_check2(color, board):
            return True, 'mate'
        return True, 'draw'
    return False, ''

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
            to_return += (2*int(piece['color'] == color) - 1) * \
                values.get(piece.get('type'), 0)
    return to_return

def all_available_movements(color, board, current_score, kpos, castling_left,
                            castling_right, am_i_check=None, pos_score=True):
    """
    Takes a color, a board a current score and returns a list of dict containing
        'from': departure location
        'to': arrival location
        'score': next score after this play
        'next': empty list to be used in evaluate_best
    """
    to_return = []
    tr_app = to_return.append
    for r, row in enumerate(board):
        for c, piece in enumerate(row):
            if piece['color'] == color:
                amv = available_movements((r, c), board, castling_left,
                                          castling_right, kpos)
                for nr, nc in amv:
                    new_score = current_score + \
                        score_per_play((nr, nc), board)*(2*int(pos_score)-1)
                    # Bring a pawn to the edge -> +/- 8
                    if piece['type'] == 'pawn' and (nr == 0 or nr == 7):
                        new_score += 8 * (2*int(pos_score)-1)
                    # Castling: fictive +0.1 bonus
                    if color == 'white':
                        krow = 7
                    else:
                        krow = 0
                    if piece['type'] == 'king' and abs(nc - c) == 2:
                        new_score += 0.1 * (2*int(pos_score)-1)
                    # Lose both future castling: fictive -0.1
                    elif castling_left and not castling_right and \
                        (r, c) == (krow, 0):
                        new_score -= 0.1 * (2*int(pos_score)-1)
                    elif castling_right and not castling_left and \
                        (r, c) == (krow, 7):
                        new_score -= 0.1 * (2*int(pos_score)-1)
                    elif (castling_right or castling_left) and \
                        piece['type'] == 'king':
                        new_score -= 0.1 * (2*int(pos_score)-1)
                    tr_app({
                        'from': (r, c),
                        'to': (nr, nc),
                        'score': new_score,
                    })
    return to_return

def build_tree(color, board, depth, castling):
    """
    Constructs a tree of possible actions
    """
    current_score = get_score(color, board)
    killers = [None for _ in range(depth + 1)]

    def internal_evaluate(current_board, current_cast, current_depth,
                          current_score, current_kpos, current_color,
                          current_checked, alpha, beta):
        """
        Returns subtree, current_lambda, best_index
        """
        if current_depth == 0:
            return [], current_score, -1
        moves = all_available_movements(current_color, current_board,
                                        current_score, current_kpos,
                                        current_cast[current_color]['left'],
                                        current_cast[current_color]['right'],
                                        pos_score=current_color == color,
                                        am_i_check=current_checked)

        # Positive if current color is hero's one
        sign = 2 * int(current_color == color) - 1

        # Treat checkmate and draw cases
        if len(moves) == 0:
            if is_check2(current_color, current_board, current_kpos):
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
            current_color,
            current_color == color,
            current_board,
            current_kpos,
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
                    current_board[move['from'][0]]
                    [move['from'][1]]['type'].ljust(6),
                    move['from'],
                    move['to'],
                ))
                print('{}%'.format(int(100*n/len(moves))), end='\r')

            unplay_infos = play(move['from'], move['to'], current_board,
                                current_kpos)

            # Update castling infos if needed:
            old_cl = current_cast[current_color]['left']
            old_cr = current_cast[current_color]['right']
            new_cl, new_cr = update_castling(move['from'], current_color,
                                             old_cl, old_cr)
            current_cast[current_color] = {
                'left': new_cl,
                'right': new_cr,
            }


            next_list, next_nu, _ = internal_evaluate(
                current_board,
                current_cast,
                current_depth - 1,
                move['score'],
                current_kpos,
                enemy(current_color),
                is_enemy_check(
                    enemy(color),
                    current_board,
                    move['from'],
                    move['to'],
                    current_kpos
                ),
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

            unplay(*unplay_infos, board=current_board, kpos=current_kpos)

            current_cast[current_color] = {
                'left': old_cl,
                'right': old_cr,
            }

            if new_alpha >= new_beta:
                killers[current_depth] = move
                break

        return moves, nu, best_index

    kpos = {
        'white': king_position('white', board),
        'black': king_position('black', board),
    }
    t1 = time()
    tr, _, best_index = internal_evaluate(deepcopy(board), castling, depth,
                                          current_score, kpos, color,
                                          is_check2(color, board, kpos), -5000,
                                          5000)
    t2 = time()
    print('Time Elapsed: %.2f s' % (t2-t1))
    return tr, best_index

def readable_position(pos):
    """
    Converts tuple to readable chess position:
    example: (6, 3) -> "d2"
    """
    return ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'][pos[1]] + str(8 - pos[0])

def sort_by_interest(tree, color, maximize, board, kpos, randomize=False,
                     danger_first=False, checkers_first=False,
                     killer_move=None):
    """
    Unefficient function to sort nodes from a tree in order of potential
    interest (check positions first, then enemy pieces killing)
    """
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
            unplay_data = play(tree[n]['from'], tree[n]['to'], board, kpos)
            if is_check2(enemy(color), board, kpos):
                tree[_sorted], tree[n] = tree[n], tree[_sorted]
                _sorted += 1
            unplay(*unplay_data, board=board, kpos=kpos)
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
        enemy_moves = all_available_movements(enemy(color), board, 0, kpos,
                                              False, False, pos_score=True)
        in_danger = []
        for elt in enemy_moves:
            if elt['score'] > 0:
                in_danger.append(elt['to'])
        # Put endangered pieces moves first (after other sorted pieces)
        for idx2 in range(index, len(tree)):
            if tree[idx2]['from'] in in_danger:
                tree[index], tree[idx2] = tree[idx2], tree[index]
                index += 1

def update_castling(start, color, castling_left, castling_right):
    new_cl, new_cr = castling_left, castling_right
    row = {'white': 7, 'black': 0}[color]
    if castling_left and start[0] == row and (start[1] == 4 or start[1] == 0):
        new_cl = False
    if castling_right and start[0] == row and (start[1] == 4 or start[1] == 7):
        new_cr = False
    return new_cl, new_cr

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
            if elt['color'] != 'blank':
                missing[elt['color']][elt['type']] -= 1
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
