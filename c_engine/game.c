#include <stdio.h>
#include <stdlib.h>

#include "game.h"

/*
 * sign = color (white : > 0)
 * pawn = 1
 * rook = 2
 * knight = 3
 * bishop = 4
 * queen = 5
 * king = 6
 */

chess_game *nil() {
  chess_game *p_g = malloc(sizeof(chess_game));
  p_g->w_turn = 1;
  p_g->w_score = 0;

  // Where are both kings ?
  p_g->w_king_pos = 4;
  p_g->b_king_pos = 60;

  // Is castling available ?
  p_g->castling_wl = 1;
  p_g->castling_wr = 1;
  p_g->castling_bl = 1;
  p_g->castling_br = 1;

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

/*
 * Unplay_unfos has to be a 6-long allocated int array
 * It will the contain [from, to, former_start, former_arrival, former_CL,
 * former_CR]
 */
void play(chess_game *p_game, int from, int to, int *unplay_infos) {

  int former_start = *(p_game->board + from);
  int former_arrival = *(p_game->board + to);

  // Save unplay_infos
  *(unplay_infos + 0) = from;
  *(unplay_infos + 1) = to;
  *(unplay_infos + 2) = former_start;
  *(unplay_infos + 3) = former_arrival;
  if (p_game->w_turn) {
    *(unplay_infos + 4) = p_game->castling_wl;
    *(unplay_infos + 5) = p_game->castling_wr;
  } else {
    *(unplay_infos + 4) = p_game->castling_bl;
    *(unplay_infos + 5) = p_game->castling_br;
  }

  // Move to arrival
  *(p_game->board + to) = former_start;
  // Remove from former position
  *(p_game->board + from) = 0;

  // If pawn at edge
  if (abs(former_start) == 1 && (to >= 56 || to <= 7)) {
    *(p_game->board + to) = former_start * 5; // transfrom it to queen
  }

  // If king
  if (abs(former_start) == 6) {
    // Update king's position and Remove castling possiilities
    if (p_game->w_turn) {
      p_game->w_king_pos = to;
      p_game->castling_wl = 0;
      p_game->castling_wr = 0;
    } else {
      p_game->b_king_pos = to;
      p_game->castling_bl = 0;
      p_game->castling_br = 0;
    }
    // If you rook, move the rook too
    if (abs(from - to) == 2) {
      if (to == 2) {
        *(p_game->board + 3) = 2;
        *(p_game->board + 0) = 0;
      } else if (to == 6) {
        *(p_game->board + 5) = 2;
        *(p_game->board + 7) = 0;
      } else if (to == 58) {
        *(p_game->board + 59) = -2;
        *(p_game->board + 56) = 0;
      } else { // to == 62
        *(p_game->board + 61) = -2;
        *(p_game->board + 63) = 0;
      }
    }
  }

  // Update Turn
  p_game->w_turn = (p_game->w_turn + 1) % 2;

};


void unplay(chess_game *p_game, int *unplay_infos) {

  // Update Turn
  p_game->w_turn = (p_game->w_turn + 1) % 2;

  // Replace former pieces at their original places
  *(p_game->board + *(unplay_infos + 0)) = *(unplay_infos + 2);
  *(p_game->board + *(unplay_infos + 1)) = *(unplay_infos + 3);

  // Restore previous castling permissions
  if (p_game->w_turn) {
    p_game->castling_wl = *(unplay_infos + 4);
    p_game->castling_wr = *(unplay_infos + 5);
  } else {
    p_game->castling_bl = *(unplay_infos + 4);
    p_game->castling_br = *(unplay_infos + 5);
  }

  // If king unmoved
  if (abs(*(unplay_infos + 2)) == 6) {

    int from = *(unplay_infos + 0);
    int to = *(unplay_infos + 1);

    // Update king position
    if (p_game->w_turn) {
      p_game->w_king_pos = from;
    } else {
      p_game->b_king_pos = from;
    }

    // Unrook if needed
    if (abs(from - to) == 2) {
      if (to == 2) {
        *(p_game->board + 0) = 2;
        *(p_game->board + 3) = 0;
      } else if (to == 6) {
        *(p_game->board + 7) = 2;
        *(p_game->board + 5) = 0;
      } else if (to == 58) {
        *(p_game->board + 56) = -2;
        *(p_game->board + 59) = 0;
      } else { // to == 62
        *(p_game->board + 63) = -2;
        *(p_game->board + 61) = 0;
      }
    }
  }
};
