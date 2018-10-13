#include <stdio.h>
#include <stdlib.h>

#include "game.h"


chess_game *nil() {
  chess_game *p_g = malloc(sizeof(chess_game));
  p_g->w_turn = 1;
  p_g->w_score = 0;

  int FIRST_ROW[] = {2, 3, 4, 5, 6, 4, 3, 2};
  p_g->board = malloc(8 * 8 * sizeof(int));
  for (size_t r = 0; r < 8; r++) {
    for (size_t c = 0; c < 8; c++) {
      if (r == 0) { // white 1st line
        *(p_g->board + 8*r + c) = FIRST_ROW[c];
      } else if (r == 7) { // black 1st line
        *(p_g->board + 8*r + c) = -FIRST_ROW[c];
      } else if (r == 1) { // white 2nd line
        *(p_g->board + 8*r + c) = 1;
      } else if (r == 6) { // black 2nd line
        *(p_g->board + 8*r + c) = -1;
      } else { // rest
        *(p_g->board + 8*r + c) = 0;
      }
    }
  }
  return p_g;
};

void deallocate_game(chess_game *p_game) {
  free(p_game->board);
  free(p_game);
};

void print_board(chess_game *p_game) {
  char labels[] = {' ', 'P', 'R', 'K', 'B', 'Q', 'G'};
  for (int r = 7; r > -1; r--) {
    printf("|");
    for (size_t c = 0; c < 8; c++) {
      printf(" %c ", labels[abs(*(p_game->board + 8*r + c))]);
    }
    printf("|\n");
  }
}

void load_game(chess_game *p_game, char *path) {
  FILE *p_file = NULL;

  p_file = fopen(path, "r");

  if (p_file == NULL) {
      error(1, 0, "Cannot read file %s!\n", path);
  }

  int board_idx = 0;
  int fscanf_result = 0;

  fscanf_result = fscanf(p_file, "w_turn = %d", &p_game->w_turn);

  while (fscanf_result != EOF) {
      if (fscanf_result != 1) {
          error(1, 0, "Line number %d is not syntactically correct!\n",
                board_idx + 1);
      }

      fscanf_result = fscanf(p_file, "%d", (p_game->board + board_idx));
      board_idx += 1;
  }

  fclose(p_file);

  p_file = NULL;
};
