from flask import Flask, render_template, redirect

from game import ChessGame

app = Flask(__name__)

HIGHLIGHTED = []
SELECTED = []
DEPTH = 6
AUTOSAVE = True
GAME = ChessGame()

"""
GAME.load('board.p')
"""

FINISHED, _ = GAME.am_i_finished

@app.route('/')
def index():
    message = "{}'s turn".format(GAME.turn.title())
    is_ended, end_type = GAME.am_i_finished
    if is_ended and end_type == 'mate':
        message = 'Check Mate ! {} wins.'.format(GAME.turn.title())
    if is_ended and end_type == 'draw':
        message = 'Match ends: draw'
    return render_template('index.html', board=GAME.board,
                           highlight=HIGHLIGHTED,
                           selected=SELECTED, turn=GAME.turn,
                           score=GAME.score(),
                           message=message, missing=GAME.missing_pieces)

@app.route('/moves/<path:subpath>')
def show_moves(subpath):

    # If game is finished, do nothing
    if FINISHED:
        return redirect('/')

    _split = subpath.split('/')
    assert len(_split) == 2
    row, col = _split
    row = int(row)
    col = int(col)

    # Update HIGHLIGHTED & SELECTED
    global HIGHLIGHTED, SELECTED
    HIGHLIGHTED = GAME.available_movements((row, col))
    SELECTED = [(row, col)]

    return redirect('/')

@app.route('/play/<path:subpath>')
def play_route(subpath):

    # If game is finished, do nothing
    global FINISHED
    if FINISHED:
        return redirect('/')

    _split = subpath.split('/')
    assert len(_split) == 4
    srow, scol, arow, acol = _split
    srow, scol = int(srow), int(scol)
    arow, acol = int(arow), int(acol)

    # Move the piece
    GAME.play((srow, scol), (arow, acol), save=True)

    # empty HIGHLIGHTED & SELECTED
    global HIGHLIGHTED, SELECTED
    HIGHLIGHTED, SELECTED = [], []

    # Autosave in board.p on white's turns
    if AUTOSAVE:
        GAME.save('board.p')
        GAME.save_for_c_engine('board.txt')

    # update FINISHED boolean
    FINISHED, _ = GAME.am_i_finished

    return redirect('/')

@app.route('/undo')
def undo_move():
    GAME.unplay()
    return redirect('/')

@app.route('/load')
def load_board():
    GAME.load('board.p')
    return redirect('/')

@app.route('/autoplay')
def autoplay():

    # If game is finished, do nothing
    if FINISHED:
        return redirect('/')

    # find the best move
    tree, best_index = GAME.build_tree(DEPTH)

    # Get departure/arrival positions
    srow, scol = tree[best_index]['from']
    arow, acol = tree[best_index]['to']

    return redirect('/play/{}/{}/{}/{}'.format(srow, scol, arow, acol))

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host="127.0.0.1", port=5000)
