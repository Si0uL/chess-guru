
typedef struct chess_game chess_game;

struct chess_game {
  int w_score;
  int *board;
  int w_turn; // 1: true / 0: false (black's turn)
};


chess_game *nil();


void deallocate_game(chess_game *p_game);


void print_board(chess_game *p_game);


void load_game(chess_game *p_game, char *path);
