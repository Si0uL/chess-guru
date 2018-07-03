import pickle
from board import BOARD
from flask import Flask, render_template, url_for, redirect
from utils import available_movements, get_score, build_tree, play

app = Flask(__name__)

HIGHLIGHTED = []
SELECTED = []
TURN = 'white'
SCORE = get_score('white', BOARD)
DEPTH = 4

"""
with open('2_turn_checkmate.p', 'rb') as _file:
    BOARD = pickle.load(_file)
"""

@app.route('/')
def index():
    return render_template('index.html', board=BOARD, highlight=HIGHLIGHTED,
                           selected=SELECTED, turn=TURN, score=SCORE)

@app.route('/moves/<path:subpath>')
def show_moves(subpath):
    _split = subpath.split('/')
    assert len(_split) == 2
    row, col = _split
    row = int(row)
    col = int(col)
    to_highlight = available_movements((row, col), BOARD)
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

    return redirect('/')

@app.route('/autoplay')
def autoplay():

    # find the best move
    global TURN
    tree = build_tree(TURN, BOARD, DEPTH)
    best_score = -5000
    best_index = -1
    for idx, move in enumerate(tree):
        if best_score < move['score']:
            best_score = move['score']
            best_index = idx

    # Get departure/arrival positions
    srow, scol = tree[best_index]['from']
    arow, acol = tree[best_index]['to']

    # Move the piece
    BOARD[arow][acol] = BOARD[srow][scol]
    BOARD[srow][scol] = {'color': 'blank'}
    # empty HIGHLIGHTED
    for _ in range(len(HIGHLIGHTED)):
        del HIGHLIGHTED[0]
    # empty SELECTED
    for _ in range(len(SELECTED)):
        del SELECTED[0]
    # Change player up next
    TURN = {'white': 'black', 'black': 'white'}[TURN]
    # Change score
    global SCORE
    SCORE = get_score('white', BOARD)

    return redirect('/')

@app.route('/save')
def save_board():
    with open('board.p', 'wb') as _file:
        pickle.dump(BOARD, _file)
    return redirect('/')
