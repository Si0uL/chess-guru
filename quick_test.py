import pickle
from utils import *

with open('complex.p', 'rb') as _file:
    board = pickle.load(_file)

tree = build_tree('white', board, 4)

_max = -5000
best_elt = {}
for n, elt in enumerate(tree):
    if elt['score'] > _max:
        _max = elt['score']
        best_elt = elt

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
