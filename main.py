import pickle
from board import BOARD
from flask import Flask, render_template, redirect
from utils import (
    available_movements,
    get_score,
    build_tree,
    play,
    is_check_mate_or_draw,
    enemy,
    update_castling,
)

app = Flask(__name__)

HIGHLIGHTED = []
SELECTED = []
TURN = 'white'
SCORE = get_score('white', BOARD)
DEPTH = 4
CASTLING = {
    'white': {
        'left': True,
        'right': True,
    },
    'black': {
        'left': True,
        'right': True,
    }
}

"""
with open('board.p', 'rb') as _file:
    BOARD = pickle.load(_file)
"""

@app.route('/')
def index():
    message = "{}'s turn".format(TURN.title())
    is_ended, end_type = is_check_mate_or_draw(TURN, BOARD)
    if is_ended and end_type == 'mate':
        message = 'Check Mate ! {} wins.'.format(enemy(TURN).title())
    if is_ended and end_type == 'draw':
        message = 'Match ends: draw'
    return render_template('index.html', board=BOARD, highlight=HIGHLIGHTED,
                           selected=SELECTED, turn=TURN, score=SCORE,
                           message=message)

@app.route('/moves/<path:subpath>')
def show_moves(subpath):
    _split = subpath.split('/')
    assert len(_split) == 2
    row, col = _split
    row = int(row)
    col = int(col)
    to_highlight = available_movements((row, col), BOARD, CASTLING[TURN]['left'],
                                       CASTLING[TURN]['right'])
    # replace HIGHLIGHTED by to_highlight
    for _ in range(len(HIGHLIGHTED)):
        del HIGHLIGHTED[0]
    for elt in to_highlight:
        HIGHLIGHTED.append(elt)
    # replace SELECTED by (row, col)
    for _ in range(len(SELECTED)):
        del SELECTED[0]
    SELECTED.append((row, col))

    return redirect('/')

@app.route('/play/<path:subpath>')
def play_route(subpath):
    _split = subpath.split('/')
    assert len(_split) == 4
    srow, scol, arow, acol = _split
    srow, scol = int(srow), int(scol)
    arow, acol = int(arow), int(acol)

    # Move the piece
    play((srow, scol), (arow, acol), BOARD)
    # empty HIGHLIGHTED
    for _ in range(len(HIGHLIGHTED)):
        del HIGHLIGHTED[0]
    # empty SELECTED
    for _ in range(len(SELECTED)):
        del SELECTED[0]
    # Change player up next
    global TURN
    TURN = {'white': 'black', 'black': 'white'}[TURN]
    # Change score
    global SCORE
    SCORE = get_score('white', BOARD)

    # Update CASTLING
    CASTLING[TURN]['left'], CASTLING[TURN]['right'] = update_castling(
        (srow, scol),
        TURN,
        CASTLING[TURN]['left'],
        CASTLING[TURN]['right'],
    )

    return redirect('/')

@app.route('/autoplay')
def autoplay():

    # find the best move
    global TURN
    tree, best_index = build_tree(TURN, BOARD, DEPTH, CASTLING[TURN]['left'],
                                  CASTLING[TURN]['right'])

    # Get departure/arrival positions
    srow, scol = tree[best_index]['from']
    arow, acol = tree[best_index]['to']

    return redirect('/play/{}/{}/{}/{}'.format(srow, scol, arow, acol))

@app.route('/save')
def save_board():
    with open('board.p', 'wb') as _file:
        pickle.dump(BOARD, _file)
    return redirect('/')
