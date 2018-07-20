import pickle
from utils import *

with open('board.p', 'rb') as _file:
    board, castling, turn = pickle.load(_file)

tree, best_index = build_tree(turn, board, 6, castling[turn]['left'],
                              castling[turn]['right'])

best_elt = tree[best_index]

print("Best move: {} {} -> {}".format(
    board[best_elt['from'][0]][best_elt['from'][1]]['type'],
    best_elt['from'],
    best_elt['to']))

"""
for elt in tree:
    print('{} {} -> {} ({})'.format(
        board[elt['from'][0]][elt['from'][1]]['type'],
        elt['from'],
        elt['to'],
        elt['score']))
"""
