from copy import deepcopy

def available_movements_raw(location, board):
    """
    Takes a location and a board and return the available moves as a series of
    arrival position tuple.
    WARNING: does not take into account check
    TODO: add castling and en-passant
    """
    def remove_out_of_board(location_list):
        """
        (auxiliary) Remove out of board positions from a list of tuples and
        and return the new list
        """
        _tr = []
        for r, c in location_list:
            if not (max(r, c) > 7 or min(r, c) < 0):
                _tr.append((r, c))
        return _tr

    to_return = []
    typ = board[location[0]][location[1]].get('type')
    col = board[location[0]][location[1]]['color']
    if typ == 'pawn':
        # black: +1 / white: -1
        _sense = int(col == 'black')*2 - 1
        to_add = [
            (location[0] + _sense, location[1] - 1),
            (location[0] + _sense, location[1]),
            (location[0] + _sense, location[1] + 1),
        ]
        if col == 'white' and location[0] == 6:
            to_add.append((4, location[1]))
        elif col == 'black' and location[0] == 1:
            to_add.append((3, location[1]))
        to_add = remove_out_of_board(to_add)
        for r, c in to_add:
            # going straight
            if c == location[1] and \
                board[location[0] + _sense][c]['color'] == 'blank' and \
                board[r][c]['color'] == 'blank':
                to_return.append((r, c))
            # killing an enemy piece
            elif c != location[1] and board[r][c]['color'] != col and \
                board[r][c]['color'] != 'blank':
                to_return.append((r, c))
            else:
                pass

    if typ == 'rook' or typ == 'queen':
        # down
        r, c = location[0] + 1, location[1]
        while r < 8 and board[r][c]['color'] == 'blank':
            to_return.append((r, c))
            r += 1
        if r < 8 and board[r][c]['color'] != col:
            to_return.append((r, c))
        # up
        r, c = location[0] - 1, location[1]
        while r > -1 and board[r][c]['color'] == 'blank':
            to_return.append((r, c))
            r -= 1
        if r > -1 and board[r][c]['color'] != col:
            to_return.append((r, c))
        # right
        r, c = location[0], location[1] + 1
        while c < 8 and board[r][c]['color'] == 'blank':
            to_return.append((r, c))
            c += 1
        if c < 8 and board[r][c]['color'] != col:
            to_return.append((r, c))
        # left
        r, c = location[0], location[1] - 1
        while c > -1 and board[r][c]['color'] == 'blank':
            to_return.append((r, c))
            c -= 1
        if c > -1 and board[r][c]['color'] != col:
            to_return.append((r, c))

    if typ == 'bishop' or typ == 'queen':
        # downright
        r, c = location[0] + 1, location[1] + 1
        while r < 8 and c < 8 and board[r][c]['color'] == 'blank':
            to_return.append((r, c))
            r += 1
            c += 1
        if r < 8 and c < 8 and board[r][c]['color'] != col:
            to_return.append((r, c))
        # upright
        r, c = location[0] - 1, location[1] + 1
        while r > -1 and c < 8 and board[r][c]['color'] == 'blank':
            to_return.append((r, c))
            r -= 1
            c += 1
        if r > -1 and c < 8 and board[r][c]['color'] != col:
            to_return.append((r, c))
        # upleft
        r, c = location[0] - 1, location[1] - 1
        while r > -1 and c > -1 and board[r][c]['color'] == 'blank':
            to_return.append((r, c))
            r -= 1
            c -= 1
        if r > -1 and c > -1 and board[r][c]['color'] != col:
            to_return.append((r, c))
        # downleft
        r, c = location[0] + 1, location[1] - 1
        while r < 8 and c > -1 and board[r][c]['color'] == 'blank':
            to_return.append((r, c))
            r += 1
            c -= 1
        if r < 8 and c > -1 and board[r][c]['color'] != col:
            to_return.append((r, c))

    if typ == 'knight':
        to_add = []
        for addr, addc in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2),
                           (1, -2), (-1, -2),]:
            to_add.append((location[0] + addr, location[1] + addc))
        to_add = remove_out_of_board(to_add)
        for r, c in to_add:
            if board[r][c]['color'] != col:
                to_return.append((r, c))

    if typ == 'king':
        to_add = []
        for addr in range(-1, 2):
            for addc in range(-1, 2):
                if not (addr == 0 and addc == 0):
                    to_add.append((location[0] + addr, location[1] + addc))
        to_add = remove_out_of_board(to_add)
        for r, c in to_add:
            if board[r][c]['color'] != col:
                to_return.append((r, c))

    return to_return

def available_movements(location, board):
    """
    Take a departure location and a board and returns a list of possible arrival
    positions, using available_movements_raw, but taking check into account
    """
    to_return = []
    amv = available_movements_raw(location, board)
    for nr, nc in amv:
        new_board = deepcopy(board)
        new_board[nr][nc] = new_board[location[0]][location[1]]
        new_board[location[0]][location[1]] = {'color': 'blank'}
        if not is_check(board[location[0]][location[1]]['color'], new_board):
            to_return.append((nr, nc))
    return to_return

def play(start, arrival, board):
    """
    Puts piece located at start at arrival position, MODIFIES board
    TODO: add piece creation
    """
    board[arrival[0]][arrival[1]] = board[start[0]][start[1]]
    board[start[0]][start[1]] = {'color': 'blank'}

def score_per_play(arrival, board):
    """
    Return positive score gain if movement kills a piece, else 0
    TODO: take into account piece creation
    """
    values = {
        'pawn': 1,
        'rook': 5,
        'knight': 3,
        'bishop': 3,
        'queen': 7,
    }
    return values.get(board[arrival[0]][arrival[1]].get('type'), 0)


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
    return {'white': 'black', 'black': 'white'}[color]

def is_check(color, board):
    """
    Takes a color and a board and returns a boolean whether the player is check
    or not
    """
    target_col = enemy(color)
    kr, kc = king_position(color, board)
    for r, row in enumerate(board):
        for c, p in enumerate(row):
            if p['color'] == target_col and \
                (kr, kc) in available_movements_raw((r, c), board):
                return True
    return False

def is_check_mate(color, board):
    """
    Tests if a situation is a checkmate or a draw
    """
    return is_check(color, board) and \
        all_available_movements(color, board, 0) == []

def my_hash(board, turn):
    """
    Converts a board into a unique string
    """
    to_return = turn[0].capitalize()
    translate = {
        'pawn': 'P',
        'rook': 'T',
        'knight': 'K',
        'bishop': 'B',
        'queen': 'Q',
        'king': 'G',
        'white': 'W',
        'black': 'B',
    }
    for r, row in enumerate(board):
        for c, piece in enumerate(row):
            if piece['color'] != 'blank':
                to_return += str(r) + str(c) + translate[piece['color']] + \
                    translate[piece['type']]
    return to_return

def get_score(color, board):
    """
    Takes a color and a board and return a score (+ in favour of the color)
    """
    values = {
        'pawn': 1,
        'rook': 5,
        'knight': 3,
        'bishop': 3,
        'queen': 7,
    }
    to_return = 0
    for row in board:
        for piece in row:
            to_return += (2*int(piece['color'] == color) - 1) * \
                values.get(piece.get('type'), 0)
    return to_return

def all_available_movements(color, board, current_score, pos_score=True):
    """
    Takes a color, a board a current score and returns a list of dict containing
        'from': departure location
        'to': arrival location
        'score': next score after this play
        'next': empty list to be used in evaluate_best
    """
    to_return = []
    for r, row in enumerate(board):
        for c, piece in enumerate(row):
            if piece['color'] == color:
                amv = available_movements((r, c), board)
                for nr, nc in amv:
                    to_return.append({
                        'from': (r, c),
                        'to': (nr, nc),
                        'next': [],
                        'score': current_score + \
                            score_per_play((nr, nc), board)*(2*int(pos_score)-1)
                    })
    return to_return

def build_tree_old(color, board, depth=4, seen=set()):
    """
    Constructs a tree of possible actions
    """
    current_score = get_score(color, board)
    current_board = deepcopy(board)

    def internal_evaluate(current_board, current_depth, current_score,
                          current_color, counter):
        """
        Returns (list of next moves, status ['normal', 'checkmate', 'draw'],
        new counter)
        """
        if current_depth == 0:
            return [], 'normal', counter + 1
        new_count = counter
        moves = all_available_movements(current_color, current_board,
                                        current_score, current_color == color)

        # Treat checkmate and draw cases
        if len(moves) == 0:
            if is_check(current_color, current_board):
                return [], 'checkmate', counter + 1
            return [], 'draw', counter + 1

        # Positive if we are current color is hero's one
        sign = 2 * int(current_color == color) - 1
        for n, move in enumerate(moves):

            if current_depth == depth:
                print('{}/{}'.format(n+1, len(moves)))

            _board = deepcopy(current_board)
            seen.add(my_hash(_board, current_color))
            play(move['from'], move['to'], _board)

            next_list, next_status, new_count = internal_evaluate(
                _board, current_depth - 1,
                move['score'],
                enemy(current_color),
                new_count
            )
            if next_status == 'checkmate':
                # +/- 1000 if you win / lose
                move['score'] = sign * 1000
            elif next_status == 'draw':
                # 0 if you get a draw (worth if you are late in points)
                move['score'] = 0
            else:
                if len(next_list) != 0:
                    if sign > 0:
                        move['score'] = min([elt['score'] for elt in next_list])
                    else:
                        move['score'] = max([elt['score'] for elt in next_list])
            move['next'] = next_list
        return moves, 'normal', new_count

    tr, _, ct = internal_evaluate(current_board, depth, current_score, color, 0)
    print('Total Explored: {}'.format(ct))
    print('Total Unique: {}'.format(len(seen)))
    return tr


def build_tree(color, board, depth=4, seen=set()):
    """
    Constructs a tree of possible actions
    """
    current_score = get_score(color, board)
    current_board = deepcopy(board)

    memory = {}

    def internal_evaluate(current_board, current_depth, current_score,
                          current_color, counter):
        """
        Returns (list of next moves, status ['normal', 'checkmate', 'draw'],
        new counter)
        """
        if current_depth == 0:
            return [], 'normal', counter + 1
        new_count = counter
        moves = all_available_movements(current_color, current_board,
                                        current_score, current_color == color)

        # Treat checkmate and draw cases
        if len(moves) == 0:
            if is_check(current_color, current_board):
                return [], 'checkmate', counter + 1
            return [], 'draw', counter + 1

        # Positive if we are current color is hero's one
        sign = 2 * int(current_color == color) - 1
        for n, move in enumerate(moves):

            if current_depth == depth:
                print('{}/{}'.format(n+1, len(moves)))

            _board = deepcopy(current_board)
            play(move['from'], move['to'], _board)
            seen.add(my_hash(_board, current_color))

            new_hash = str(current_depth - 1) + my_hash(_board,
                                                        enemy(current_color))
            if new_hash in memory:
                next_list, next_status, new_count = memory[new_hash]
            else:
                next_list, next_status, new_count = internal_evaluate(
                    _board,
                    current_depth - 1,
                    move['score'],
                    enemy(current_color),
                    new_count
                )
                memory[new_hash] = (next_list, next_status, new_count)

            if next_status == 'checkmate':
                # +/- 1000 if you win / lose
                move['score'] = sign * 1000
            elif next_status == 'draw':
                # 0 if you get a draw (worth if you are late in points)
                move['score'] = 0
            else:
                if len(next_list) != 0:
                    if sign > 0:
                        move['score'] = min([elt['score'] for elt in next_list])
                    else:
                        move['score'] = max([elt['score'] for elt in next_list])
            move['next'] = next_list
        return moves, 'normal', new_count

    tr, _, ct = internal_evaluate(current_board, depth, current_score, color, 0)
    print('Total Explored: {}'.format(ct))
    print('Total Unique: {}'.format(len(seen)))
    return tr
