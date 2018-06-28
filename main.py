from flask import Flask, render_template, url_for, redirect
from utils import available_movements, is_check_mate, get_score

app = Flask(__name__)

BOARD = [[{"color": "blank"} for _ in range(8)] for _ in range(8)]
BOARD[7] = [
    {
        "color": "white",
        "type": "rook",
    },
    {
        "color": "white",
        "type": "knight",
    },
    {
        "color": "white",
        "type": "bishop",
    },
    {
        "color": "white",
        "type": "queen",
    },
    {
        "color": "white",
        "type": "king",
    },
    {
        "color": "white",
        "type": "bishop",
    },
    {
        "color": "white",
        "type": "knight",
    },
    {
        "color": "white",
        "type": "rook",
    },
]
BOARD[0] = [
    {
        "color": "black",
        "type": "rook",
    },
    {
        "color": "black",
        "type": "knight",
    },
    {
        "color": "black",
        "type": "bishop",
    },
    {
        "color": "black",
        "type": "queen",
    },
    {
        "color": "black",
        "type": "king",
    },
    {
        "color": "black",
        "type": "bishop",
    },
    {
        "color": "black",
        "type": "knight",
    },
    {
        "color": "black",
        "type": "rook",
    },
]

BOARD[6] = [{"color": "white", "type": "pawn"} for _ in range(8)]
BOARD[1] = [{"color": "black", "type": "pawn"} for _ in range(8)]

HIGHLIGHTED = []
SELECTED = []
TURN = 'white'
SCORE = 0

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
def play(subpath):
    _split = subpath.split('/')
    assert len(_split) == 4
    srow, scol, arow, acol = _split
    srow, scol = int(srow), int(scol)
    arow, acol = int(arow), int(acol)

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
    global TURN
    TURN = {'white': 'black', 'black': 'white'}[TURN]
    # Change score
    global SCORE
    SCORE = get_score('white', BOARD)

    return redirect('/')
