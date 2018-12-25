#include <stdio.h>
#include <stdlib.h>
#include <error.h>

#include "game.h"

int main(int argc, char const *argv[]) {

  if (argc != 3)
    error(1, 1, "Usage: %s <filepath> <depth>", argv[0]);

  chess_game *p_game = nil();
  load_game(p_game, argv[1]);

  int depth = atoi(argv[2]);
  int from, to;
  alpha_beta_predict(p_game, depth, &from, &to);
  printf("%d %d\n", from, to);

  deallocate_game(p_game);
  return 0;
}
