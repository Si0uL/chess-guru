#include <stdio.h>
#include <stdlib.h>

#include "game.h"


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

  deallocate_game(p_game);

  return 0;
}
