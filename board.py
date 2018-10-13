class Piece(object):
    """docstring for Piece."""
    def __init__(self, color, piece_type=None):
        super(Piece, self).__init__()
        self.color = color
        self.type = piece_type
        self.is_blank = color == "blank"
        if self.is_blank:
            self.type = None


BOARD = [[Piece("blank") for _ in range(8)] for _ in range(8)]
BOARD[6] = [Piece("white", "pawn") for _ in range(8)]
BOARD[1] = [Piece("black", "pawn") for _ in range(8)]

# Normal start board
BOARD[7] = [
    Piece("white", "rook"),
    Piece("white", "knight"),
    Piece("white", "bishop"),
    Piece("white", "queen"),
    Piece("white", "king"),
    Piece("white", "bishop"),
    Piece("white", "knight"),
    Piece("white", "rook"),
]
BOARD[0] = [
    Piece("black", "rook"),
    Piece("black", "knight"),
    Piece("black", "bishop"),
    Piece("black", "queen"),
    Piece("black", "king"),
    Piece("black", "bishop"),
    Piece("black", "knight"),
    Piece("black", "rook"),
]
