from copy import deepcopy

def available_movements_raw(location, board):
    def remove_out_of_board(location_list):
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

    if typ == 'tower' or typ == 'queen':
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
    to_return = []
    amv = available_movements_raw(location, board)
    for nr, nc in amv:
        new_board = deepcopy(board)
        new_board[nr][nc] = new_board[location[0]][location[1]]
        new_board[location[0]][location[1]] = {'color': 'blank'}
        if not is_check(board[location[0]][location[1]]['color'], new_board):
            to_return.append((nr, nc))
    return to_return


def king_position(color, board):
    for r, row in enumerate(board):
        for c, piece in enumerate(row):
            if piece.get('type') == 'king' and piece['color'] == color:
                return r, c
    return None

def is_check(color, board):
    target_col = {'white': 'black', 'black': 'white'}[color]
    kr, kc = king_position(color, board)
    for r, row in enumerate(board):
        for c, p in enumerate(row):
            if p['color'] == target_col and \
                (kr, kc) in available_movements_raw((r, c), board):
                return True
    return False

def is_check_mate(color, board):
    if is_check(color, board):
        # Try to find a solution
        for r, row in enumerate(board):
            for c, p in enumerate(row):
                if p['color'] == color and \
                    available_movements((r, c), board) != []:
                    return False
        return True
    return False
