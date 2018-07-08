from time import time
from copy import deepcopy

def available_movements_raw(location, board):
    """
    Takes a location and a board and return the available moves as a series of
    arrival position tuple.
    WARNING: does not take into account check
    TODO: add castling and en-passant
    """

    to_return = []
    typ = board[location[0]][location[1]].get('type')
    col = board[location[0]][location[1]]['color']

    if typ == 'pawn':
        # black: +1 / white: -1
        _sense = int(col == 'black')*2 - 1

        # Straight
        if board[location[0] + _sense][location[1]]['color'] == 'blank':
            to_return.append((location[0] + _sense, location[1]))
            # 2 straight
            if location[0] == 6 and col == 'white' and \
                board[4][location[1]]['color'] == 'blank':
                to_return.append((4, location[1]))
            elif location[0] == 1 and col == 'black' and \
                board[3][location[1]]['color'] == 'blank':
                to_return.append((3, location[1]))
            else:
                pass
        # Kill an enemy (left)
        if location[1] != 0 and \
            board[location[0] + _sense][location[1] - 1]['color'] == enemy(col):
            to_return.append((location[0] + _sense, location[1] - 1))
        # Kill an enemy (right)
        if location[1] != 7 and \
            board[location[0] + _sense][location[1] + 1]['color'] == enemy(col):
            to_return.append((location[0] + _sense, location[1] + 1))

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
        for addr, addc in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2),
                           (1, -2), (-1, -2)]:
            nr, nc = location[0] + addr, location[1] + addc
            if nr < 8 and nc < 8 and nr > -1 and nc > -1 and \
                board[nr][nc]['color'] != col:
                to_return.append((nr, nc))

    if typ == 'king':
        for addr in range(-1, 2):
            for addc in range(-1, 2):
                if not (addr == 0 and addc == 0):
                    nr, nc = location[0] + addr, location[1] + addc
                    if nr < 8 and nc < 8 and nr > -1 and nc > -1 and \
                        board[nr][nc]['color'] != col:
                        to_return.append((nr, nc))

    return to_return

def available_movements(location, board):
    """
    Take a departure location and a board and returns a list of possible arrival
    positions, using available_movements_raw, but taking check into account
    fast_is_check only works if the king isn't moved and you are not already
    check
    """
    to_return = []
    color = board[location[0]][location[1]]['color']
    checker = fast_is_check
    if board[location[0]][location[1]]['type'] == 'king' or \
        is_check(color, board):
        checker = is_check
    amv = available_movements_raw(location, board)
    for arrival in amv:
        unplay_infos = play(location, arrival, board)

        if not checker(color, board):
            to_return.append(arrival)

        unplay(*unplay_infos, board=board)
    return to_return

def play(start, arrival, board):
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
    return start, former_start, arrival, former_arrival

def unplay(pos_start, former_start, pos_arrival, former_arrival, board):
    """
    Undo the efect of the play() function. MODIFIES board
    """
    board[pos_start[0]][pos_start[1]] = former_start
    board[pos_arrival[0]][pos_arrival[1]] = former_arrival

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
    kpos = king_position(color, board)
    for r, row in enumerate(board):
        for c, p in enumerate(row):
            if p['color'] == target_col and \
                kpos in available_movements_raw((r, c), board):
                return True
    return False

def fast_is_check(color, board):
    """
    Quicker version of is_check, as designed to be used in available_movements
    to remove potential movements that will lead to a check against a player.
    If you are not already in check, and it is not the king that is moved,
    only enemy queen, rooks and bishops need to be checked
    """
    target_col = enemy(color)
    kpos = king_position(color, board)
    for r, row in enumerate(board):
        for c, p in enumerate(row):
            if p['color'] == target_col and \
                p['type'] in ['queen', 'rook', 'bishop'] and\
                kpos in available_movements_raw((r, c), board):
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

def build_tree(color, board, depth):
    """
    Constructs a tree of possible actions
    """
    current_score = get_score(color, board)

    def internal_evaluate(current_board, current_depth, current_score,
                          current_color, alpha, beta):
        """
        Returns subtree, current_lambda, best_index
        """
        if current_depth == 0:
            return [], current_score, -1
        moves = all_available_movements(current_color, current_board,
                                        current_score, current_color == color)

        # Positive if current color is hero's one
        sign = 2 * int(current_color == color) - 1

        # Treat checkmate and draw cases
        if len(moves) == 0:
            if is_check(current_color, current_board):
                return [], -sign*1000, -1
            return [], 0, -1

        new_alpha, new_beta = alpha, beta

        if sign == 1:
            nu = -5000
        else:
            nu = 5000

        best_index = -1

        if depth - current_depth < 4:
            sort_by_interest(moves, current_color, current_color == color,
                             current_board)

        for n, move in enumerate(moves):

            if current_depth == depth:
                print('{}/{}'.format(n+1, len(moves)))

            unplay_infos = play(move['from'], move['to'], current_board)

            next_list, next_nu, _ = internal_evaluate(
                current_board,
                current_depth - 1,
                move['score'],
                enemy(current_color),
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

            unplay(*unplay_infos, board=current_board)

            if new_alpha >= new_beta:
                break

        return moves, nu, best_index

    t1 = time()
    tr, _, best_index = internal_evaluate(deepcopy(board), depth, current_score,
                                          color, -5000, 5000)
    t2 = time()
    print('Time Elapsed: %.2f s' % (t2-t1))
    return tr, best_index

def readable_position(pos):
    """
    Converts tuple to readable chess position:
    example: (6, 3) -> "d2"
    """
    return ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'][pos[1]] + str(8 - pos[0])

def sort_by_interest(tree, color, maximize, board):
    """
    Unefficient function to sort nodes from a tree in order of potential
    interest (check positions first, then enemy pieces killing)
    """
    _sorted = 0
    # Checkers first
    for n, elt in enumerate(tree):
        unplay_data = play(elt['from'], elt['to'], board)
        if is_check(enemy(color), board):
            tree[_sorted], tree[n] = tree[n], tree[_sorted]
            _sorted += 1
        unplay(*unplay_data, board=board)
    # Basic sorting method by direct score (kills first !)
    for i in range(_sorted, len(tree)):
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
