#include <stdio.h>
#include <stdlib.h>

#include "game.h"


int main(int argc, char const *argv[]) {

  chess_game *p_game = nil();
  printf("White Turn = %d\n", p_game->w_turn);
  print_board(p_game);
  load_game(p_game, "first_turn.txt");
  printf("\nWhite Turn = %d\n", p_game->w_turn);
  print_board(p_game);
  deallocate_game(p_game);

  return 0;
}
