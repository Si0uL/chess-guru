#include <stdio.h>
#include <stdlib.h>

#include "game.h"

void test_av_mvt_raw(chess_game *p_game, int position) {
  int *movements = malloc(50 * sizeof(int));
  int found = available_movements_raw(p_game, position, movements);
  printf("Movements for position %d:\n", position);
  for (int i=0; i<found; i++) {
    printf("%d ", movements[i]);
  }
  printf("\n");
  free(movements);
}

int main(int argc, char const *argv[]) {

  chess_game *p_game = nil();
  printf("White Turn = %d\n", p_game->w_turn);
  print_board(p_game);
  load_game(p_game, "board.txt");
  printf("\nWhite Turn = %d\n", p_game->w_turn);
  print_board(p_game);

  int unplay_infos[4];
  play(p_game, 55, 47, unplay_infos);
  printf("\nWhite Turn = %d\n", p_game->w_turn);
  print_board(p_game);

  unplay(p_game, unplay_infos);
  printf("\nWhite Turn = %d\n", p_game->w_turn);
  print_board(p_game);

  printf("\nIs check = %d\n", is_check(p_game));

  test_av_mvt_raw(p_game, 8);
  test_av_mvt_raw(p_game, 34);
  test_av_mvt_raw(p_game, 4);
  test_av_mvt_raw(p_game, 60);
  test_av_mvt_raw(p_game, 57);
  test_av_mvt_raw(p_game, 18);

  deallocate_game(p_game);

  return 0;
}
