BOARD = [[{"color": "blank"} for _ in range(8)] for _ in range(8)]

# Normal start board
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
