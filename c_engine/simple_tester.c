#include <stdio.h>
#include <stdlib.h>

#include "game.h"

char *number_to_piece(int nb) {
  switch (abs(nb)) {
    case 1:
      return "pawn  ";
    case 2:
      return "rook  ";
    case 3:
      return "knight";
    case 4:
      return "bishop";
    case 5:
      return "queen ";
    case 6:
      return "king  ";
  }
  return "";
}

void test_all_av_mvt(chess_game *p_game, int w_turn) {
  int from[100], to_[100];
  int cache[6];
  int am_i_check = is_check(p_game, w_turn);
  int found = all_available_movements(p_game, w_turn, am_i_check, from, to_,
    cache);
  printf("Movements for w_turn = %d (total: %d):\n", w_turn, found);
  for (int i=0; i<found; i++) {
    printf("%s: ", number_to_piece(p_game->board[from[i]]));
    print_location(from[i]);
    printf(" -> ");
    print_location(to_[i]);
    printf("\n");
  }
  printf("\n");
}

void test_prediction(chess_game *p_game, int depth) {
  int from, to;
  // TODO remove this
  from = 0;
  to = 0;
  alpha_beta_predict(p_game, depth, &from, &to);
  printf("\nBest Move:\n%s : ", number_to_piece(p_game->board[from]));
  print_location(from);
  printf(" -> ");
  print_location(to);
  printf("\n");
}

int main(int argc, char const *argv[]) {

  chess_game *p_game = nil();
  load_game(p_game, "board.txt");
  printf("\nWhite Turn = %d\n", p_game->w_turn);
  print_board(p_game);

  int unplay_infos[6];
  play(p_game, 55, 47, unplay_infos);
  printf("\nWhite Turn = %d\n", p_game->w_turn);
  print_board(p_game);

  unplay(p_game, unplay_infos);
  printf("\nWhite Turn = %d\n", p_game->w_turn);
  print_board(p_game);

  printf("\nIs check = %d\n", is_check(p_game, p_game->w_turn));

  test_all_av_mvt(p_game, 0);
  test_all_av_mvt(p_game, 1);

  test_prediction(p_game, 4);

  deallocate_game(p_game);

  return 0;
}
