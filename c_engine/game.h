
typedef struct chess_game chess_game;

struct chess_game {
  int w_score;
  int *board;
  int w_turn; // 1: true / 0: false (black's turn)

  int w_king_pos;
  int b_king_pos;

  int castling_wl;
  int castling_wr;
  int castling_bl;
  int castling_br;
};


chess_game *nil();


void deallocate_game(chess_game *p_game);


void print_board(chess_game *p_game);


void print_location(int location);


void load_game(chess_game *p_game, const char *path);


void play(chess_game *p_game, int from, int to, int *unplay_infos);


void unplay(chess_game *p_game, int *unplay_infos);


int is_check(chess_game *p_game, int white_turn);


int available_movements(chess_game *p_game, int position, int am_i_check,
  int *from, int *to_, int *six_long_int_cache);


int all_available_movements(chess_game *p_game, int w_turn, int am_i_check,
  int *from, int *to_, int *six_long_int_cache);


int will_be_check(chess_game *p_game, int start, int arrival);


void alpha_beta_predict(chess_game *p_game, int depth, int *p_best_from,
  int *p_best_to);
