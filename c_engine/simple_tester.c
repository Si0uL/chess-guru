#include <stdio.h>
#include <stdlib.h>

#include "game.h"

void test_av_mvt(chess_game *p_game, int position) {
  int movements[30];
  int cache[6];
  int am_i_check = is_check(p_game, p_game->board[position] > 0);
  int found = available_movements(p_game, position, am_i_check, movements,
    cache);
  printf("Movements for position %d:\n", position);
  for (int i=0; i<found; i++) {
    printf("%d ", movements[i]);
  }
  printf("\n");
}

int main(int argc, char const *argv[]) {

  chess_game *p_game = nil();
  printf("White Turn = %d\n", p_game->w_turn);
  print_board(p_game);
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

  test_av_mvt(p_game, 57);
  test_av_mvt(p_game, 58);
  test_av_mvt(p_game, 59);
  test_av_mvt(p_game, 60);
  test_av_mvt(p_game, 8);

  deallocate_game(p_game);

  return 0;
}
