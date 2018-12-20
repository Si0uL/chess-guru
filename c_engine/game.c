#include <stdio.h>
#include <stdlib.h>
#include <time.h>

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
        p_g->board[8*r + c] = FIRST_ROW[c];
      } else if (r == 7) { // black 1st line
        p_g->board[8*r + c] = -FIRST_ROW[c];
      } else if (r == 1) { // white 2nd line
        p_g->board[8*r + c] = 1;
      } else if (r == 6) { // black 2nd line
        p_g->board[8*r + c] = -1;
      } else { // rest
        p_g->board[8*r + c] = 0;
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
      printf(" %c ", labels[abs(p_game->board[8*r + c])]);
    }
    printf("|\n");
  }
}

void print_location(int location) {
  int col_label[] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'};
  printf("%c%d", col_label[location / 8], location % 8 + 1);
}

void load_game(chess_game *p_game, char *path) {
  FILE *p_file = NULL;

  p_file = fopen(path, "r");

  if (p_file == NULL) {
      error(1, 0, "Cannot read file %s!\n", path);
  }

  // Read game parameters
  if (fscanf(p_file, "w_turn = %d\n", &p_game->w_turn) != 1) {
    printf("%s\n", "Error reading w_turn");
  };
  if (fscanf(p_file, "w_score = %d\n", &p_game->w_score) != 1) {
    printf("%s\n", "Error reading w_score");
  };
  if (fscanf(p_file, "w_king_pos = %d\n", &p_game->w_king_pos) != 1) {
    printf("%s\n", "Error reading w_king_pos");
  };
  if (fscanf(p_file, "b_king_pos = %d\n", &p_game->b_king_pos) != 1) {
    printf("%s\n", "Error reading b_king_pos");
  };
  if (fscanf(p_file, "castling_wl = %d\n", &p_game->castling_wl) != 1) {
    printf("%s\n", "Error reading castling_wl");
  };
  if (fscanf(p_file, "castling_wr = %d\n", &p_game->castling_wr) != 1) {
    printf("%s\n", "Error reading castling_wr");
  };
  if (fscanf(p_file, "castling_bl = %d\n", &p_game->castling_bl) != 1) {
    printf("%s\n", "Error reading castling_bl");
  };
  if (fscanf(p_file, "castling_br = %d\n", &p_game->castling_br) != 1) {
    printf("%s\n", "Error reading castling_br");
  };

  // Read board
  int board_idx = 0;
  int fscanf_result = 1;

  while (fscanf_result != EOF) {
      if (fscanf_result != 1) {
          error(1, 0, "Line number %d is not syntactically correct!\n",
                board_idx + 9);
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

  int former_start = p_game->board[from];
  int former_arrival = p_game->board[to];

  // Save unplay_infos
  unplay_infos[0] = from;
  unplay_infos[1] = to;
  unplay_infos[2] = former_start;
  unplay_infos[3] = former_arrival;
  if (p_game->w_turn) {
    unplay_infos[4] = p_game->castling_wl;
    unplay_infos[5] = p_game->castling_wr;
  } else {
    unplay_infos[4] = p_game->castling_bl;
    unplay_infos[5] = p_game->castling_br;
  }

  // Move to arrival
  p_game->board[to] = former_start;
  // Remove from former position
  p_game->board[from] = 0;

  // If pawn at edge
  if (abs(former_start) == 1 && (to >= 56 || to <= 7)) {
    p_game->board[to] = former_start * 5; // transfrom it to queen
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
        p_game->board[3] = 2;
        p_game->board[0] = 0;
      } else if (to == 6) {
        p_game->board[5] = 2;
        p_game->board[7] = 0;
      } else if (to == 58) {
        p_game->board[59] = -2;
        p_game->board[56] = 0;
      } else { // to == 62
        p_game->board[61] = -2;
        p_game->board[63] = 0;
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
  p_game->board[unplay_infos[0]] = unplay_infos[2];
  p_game->board[unplay_infos[1]] = unplay_infos[3];

  // Restore previous castling permissions
  if (p_game->w_turn) {
    p_game->castling_wl = unplay_infos[4];
    p_game->castling_wr = unplay_infos[5];
  } else {
    p_game->castling_bl = unplay_infos[4];
    p_game->castling_br = unplay_infos[5];
  }

  // If king unmoved
  if (abs(unplay_infos[2]) == 6) {

    int from = unplay_infos[0];
    int to = unplay_infos[1];

    // Update king position
    if (p_game->w_turn) {
      p_game->w_king_pos = from;
    } else {
      p_game->b_king_pos = from;
    }

    // Unrook if needed
    if (abs(from - to) == 2) {
      if (to == 2) {
        p_game->board[0] = 2;
        p_game->board[3] = 0;
      } else if (to == 6) {
        p_game->board[7] = 2;
        p_game->board[5] = 0;
      } else if (to == 58) {
        p_game->board[56] = -2;
        p_game->board[59] = 0;
      } else { // to == 62
        p_game->board[63] = -2;
        p_game->board[61] = 0;
      }
    }
  }
};


/*
 * -----------------------------------------------------------------------------
 * All the following functions are meant to scan a row / diagonal to check if
 * the first encountered piece is a threat or not for the location argument
 * Either returns 1 or 0
 * -----------------------------------------------------------------------------
 */

/*
 * Up row scanner (see over)
 */
int _scan_u(chess_game *p_game, int location, int sign) {
  int scope_pos = location + 8;
  while (scope_pos < 64 && p_game->board[scope_pos] == 0) {
    scope_pos += 8;
  }
  if (scope_pos < 64 && p_game->board[scope_pos] * sign < 0) {
    if (
      abs(p_game->board[scope_pos]) == 2 ||
      abs(p_game->board[scope_pos]) == 5 ||
      abs(p_game->board[scope_pos]) == 6
    ) {
      return 1;
    }
  }
  return 0;
}


/*
 * Down row scanner (see over)
 */
int _scan_d(chess_game *p_game, int location, int sign) {
  int scope_pos = location - 8;
  while (scope_pos >= 0 && p_game->board[scope_pos] == 0) {
    scope_pos -= 8;
  }
  if (scope_pos >= 0 && p_game->board[scope_pos] * sign < 0) {
    if (
      abs(p_game->board[scope_pos]) == 2 ||
      abs(p_game->board[scope_pos]) == 5 ||
      abs(p_game->board[scope_pos]) == 6
    ) {
      return 1;
    }
  }
  return 0;
}


/*
 * Right row scanner (see over)
 */
int _scan_r(chess_game *p_game, int location, int sign) {
  int scope_pos = location + 1;
  while (scope_pos %8 != 0 && p_game->board[scope_pos] == 0) {
    scope_pos += 1;
  }
  if (scope_pos %8 != 0 && p_game->board[scope_pos] * sign < 0) {
    if (
      abs(p_game->board[scope_pos]) == 2 ||
      abs(p_game->board[scope_pos]) == 5 ||
      abs(p_game->board[scope_pos]) == 6
    ) {
      return 1;
    }
  }
  return 0;
}


/*
 * Left row scanner (see over)
 */
int _scan_l(chess_game *p_game, int location, int sign) {
  int scope_pos = location - 1;
  while (scope_pos >= 0 && scope_pos %8 != 7 && p_game->board[scope_pos] == 0) {
    scope_pos -= 1;
  }
  if (scope_pos >= 0 && scope_pos % 8 != 7 &&
    p_game->board[scope_pos] * sign < 0) {
    if (
      abs(p_game->board[scope_pos]) == 2 ||
      abs(p_game->board[scope_pos]) == 5 ||
      abs(p_game->board[scope_pos]) == 6
    ) {
      return 1;
    }
  }
  return 0;
}


/*
 * Up Right diagonal scanner (see over)
 */
int _scan_ur(chess_game *p_game, int location, int sign) {
  int scope_pos = location + 9;
  while (scope_pos < 64 && scope_pos %8 != 0 &&
    p_game->board[scope_pos] == 0) {
    scope_pos += 9;
  }
  if (scope_pos < 64 && scope_pos %8 != 0 &&
    p_game->board[scope_pos] * sign < 0) {
    if (
      abs(p_game->board[scope_pos]) == 4 ||
      abs(p_game->board[scope_pos]) == 5 ||
      abs(p_game->board[scope_pos]) == 6 ||
      (p_game->board[scope_pos] == -1 && sign == 1 &&
        scope_pos - location == 9)
    ) {
      return 1;
    }
  }
  return 0;
}


/*
 * Down Right diagonal scanner (see over)
 */
int _scan_dr(chess_game *p_game, int location, int sign) {
  int scope_pos = location - 7;
  while (scope_pos >= 0 && scope_pos %8 != 0 &&
    p_game->board[scope_pos] == 0) {
    scope_pos -= 7;
  }
  if (scope_pos >= 0 && scope_pos %8 != 0 &&
    p_game->board[scope_pos] * sign < 0) {
    if (
      abs(p_game->board[scope_pos]) == 4 ||
      abs(p_game->board[scope_pos]) == 5 ||
      abs(p_game->board[scope_pos]) == 6 ||
      (p_game->board[scope_pos] == 1 && sign == -1 &&
        scope_pos - location == -7)
    ) {
      return 1;
    }
  }
  return 0;
}


/*
 * Up Left diagonal scanner (see over)
 */
int _scan_ul(chess_game *p_game, int location, int sign) {
  int scope_pos = location + 7;
  while (scope_pos < 64 && scope_pos %8 != 7 &&
    p_game->board[scope_pos] == 0) {
    scope_pos += 7;
  }
  if (scope_pos < 64 && scope_pos %8 != 7 &&
    p_game->board[scope_pos] * sign < 0) {
    if (
      abs(p_game->board[scope_pos]) == 4 ||
      abs(p_game->board[scope_pos]) == 5 ||
      abs(p_game->board[scope_pos]) == 6 ||
      (p_game->board[scope_pos] == -1 && sign == 1 &&
        scope_pos - location == 7)
    ) {
      return 1;
    }
  }
  return 0;
}


/*
 * Down Left diagonal scanner (see over)
 */
int _scan_dl(chess_game *p_game, int location, int sign) {
  int scope_pos = location - 9;
  while (scope_pos >= 0 && scope_pos %8 != 7 &&
    p_game->board[scope_pos] == 0) {
    scope_pos -= 9;
  }
  if (scope_pos >= 0 && scope_pos %8 != 7 &&
    p_game->board[scope_pos] * sign < 0) {
    if (
      abs(p_game->board[scope_pos]) == 4 ||
      abs(p_game->board[scope_pos]) == 5 ||
      abs(p_game->board[scope_pos]) == 6 ||
      (p_game->board[scope_pos] == 1 && sign == -1 &&
        scope_pos - location == -9)
    ) {
      return 1;
    }
  }
  return 0;
}


/*
 * Check if the player up is check or not by scanning all lines + diags starting
 * from the king + watching for knights
 */
int is_check(chess_game *p_game, int white_turn) {
  // +1 if white, -1 if black
  int kpos, sign = 2 * white_turn - 1;
  if (white_turn) {
    kpos = p_game->w_king_pos;
  } else {
    kpos = p_game->b_king_pos;
  }

  // Scanning all lines & diags
  if (_scan_u(p_game, kpos, sign)) return 1;
  if (_scan_d(p_game, kpos, sign)) return 1;
  if (_scan_r(p_game, kpos, sign)) return 1;
  if (_scan_l(p_game, kpos, sign)) return 1;
  if (_scan_ur(p_game, kpos, sign)) return 1;
  if (_scan_dr(p_game, kpos, sign)) return 1;
  if (_scan_ul(p_game, kpos, sign)) return 1;
  if (_scan_dl(p_game, kpos, sign)) return 1;

  // Add knight watch
  if (kpos % 8 != 7) {
    if (kpos + 17 < 64 && p_game->board[kpos + 17] * sign == -3) {
      return 1;
    }
    if (kpos - 15 >= 0 && p_game->board[kpos - 15] * sign == -3) {
      return 1;
    }

    if (kpos % 8 != 6) {
      if (kpos + 10 < 64 && p_game->board[kpos + 10] * sign == -3) {
        return 1;
      }
      if (kpos - 6 >= 0 && p_game->board[kpos - 6] * sign == -3) {
        return 1;
      }
    }
  }

  if (kpos % 8 != 0) {
    if (kpos + 15 < 64 && p_game->board[kpos + 15] * sign == -3) {
      return 1;
    }
    if (kpos - 17 >= 0 && p_game->board[kpos - 17] * sign == -3) {
      return 1;
    }

    if (kpos % 8 != 1) {
      if (kpos + 6 < 64 && p_game->board[kpos + 6] * sign == -3) {
        return 1;
      }
      if (kpos - 10 >= 0 && p_game->board[kpos - 10] * sign == -3) {
        return 1;
      }
    }
  }

  return 0;
};


/*
 * Puts all available movements inside from & to_ (they should be allocated
 * before). Adds castling postitions and checks if move doesn't affect
 * checkstate. If not am_i_check, uses will_be_check() to save time on
 * moves checking.
 * six_long_int_cache is a pre-allocated 6-long int array only used to store
 * temporary datas (when playing and unplaying)
 * Returns the number of available movements found.
 */
int available_movements(chess_game *p_game, int position, int am_i_check,
  int *from, int *to_, int *six_long_int_cache) {

  int found = 0;
  // +/- 1 according to the piece's color
  int sign = 2 * (p_game->board[position] > 0) - 1;
  int w_turn = p_game->board[position] > 0;
  int type = abs(p_game->board[position]);
  int scope_pos;

  void add_mvt(int arrival) {
    // Check if this move can be played without ending up being check
    // If you do not move the king and are not check, use will_be_check()
    if (type != 6 && am_i_check == 0) {
      if (!will_be_check(p_game, position, arrival)) {
        from[found] = position;
        to_[found] = arrival;
        found ++;
      }
    } else {
      play(p_game, position, arrival, six_long_int_cache);
      if (!is_check(p_game, w_turn)) {
        from[found] = position;
        to_[found] = arrival;
        found ++;
      }
      unplay(p_game, six_long_int_cache);
    }
  }

  // rook or queen
  if (type == 2 || type == 5) {
    // Up
    scope_pos = position + 8;
    // find empty locations
    while (scope_pos < 64 && p_game->board[scope_pos] == 0) {
      add_mvt(scope_pos);
      scope_pos += 8;
    }
    // eat a potential enemy piece
    if (scope_pos < 64 && p_game->board[scope_pos] * sign < 0) {
      add_mvt(scope_pos);
    }
    // Down
    scope_pos = position - 8;
    while (scope_pos >= 0 && p_game->board[scope_pos] == 0) {
      add_mvt(scope_pos);
      scope_pos -= 8;
    }
    if (scope_pos >= 0 && p_game->board[scope_pos] * sign < 0) {
      add_mvt(scope_pos);
    }
    // Right
    scope_pos = position + 1;
    while (scope_pos %8 != 0 && p_game->board[scope_pos] == 0) {
      add_mvt(scope_pos);
      scope_pos += 1;
    }
    if (scope_pos %8 != 0 && p_game->board[scope_pos] * sign < 0) {
      add_mvt(scope_pos);
    }
    // Left
    scope_pos = position - 1;
    while (scope_pos >= 0 && scope_pos % 8 != 7 &&
      p_game->board[scope_pos] == 0) {
      add_mvt(scope_pos);
      scope_pos -= 1;
    }
    if (scope_pos >= 0 && scope_pos % 8 != 7 &&
      p_game->board[scope_pos] * sign < 0) {
      add_mvt(scope_pos);
    }
  }

  // bishop or queen
  if (type == 4 || type == 5) {
    // Up-Right
    scope_pos = position + 9;
    while (scope_pos < 64 && scope_pos % 8 != 0 &&
      p_game->board[scope_pos] == 0) {
      add_mvt(scope_pos);
      scope_pos += 9;
    }
    if (scope_pos < 64 && scope_pos % 8 != 0 &&
      p_game->board[scope_pos] * sign < 0) {
      add_mvt(scope_pos);
    }
    // Down-Right
    scope_pos = position - 7;
    while (scope_pos >= 0 && scope_pos % 8 != 0 &&
      p_game->board[scope_pos] == 0) {
      add_mvt(scope_pos);
      scope_pos -= 7;
    }
    if (scope_pos >= 0 && scope_pos % 8 != 0 &&
      p_game->board[scope_pos] * sign < 0) {
      add_mvt(scope_pos);
    }
    // Up-Left
    scope_pos = position + 7;
    while (scope_pos < 64 && scope_pos % 8 != 7 &&
      p_game->board[scope_pos] == 0) {
      add_mvt(scope_pos);
      scope_pos += 7;
    }
    if (scope_pos < 64 && scope_pos % 8 != 7 &&
      p_game->board[scope_pos] * sign < 0) {
      add_mvt(scope_pos);
    }
    // Down-Left
    scope_pos = position - 9;
    while (scope_pos >= 0 && scope_pos % 8 != 7 &&
      p_game->board[scope_pos] == 0) {
      add_mvt(scope_pos);
      scope_pos -= 9;
    }
    if (scope_pos >= 0 && scope_pos % 8 != 7 &&
      p_game->board[scope_pos] * sign < 0) {
      add_mvt(scope_pos);
    }
  }

  // pawn
  if (type == 1) {
    // 1 in front
    if (p_game->board[position + sign * 8] == 0) {
      add_mvt(position + sign * 8);
      // on first line and nobody 2 rows after
      if (sign > 0 && position > 7 && position < 16 &&
        p_game->board[position + 16] == 0) {
        add_mvt(position + 16);
      } else if (sign < 0 && position > 55 && position < 64 &&
        p_game->board[position - 16] == 0) {
        add_mvt(position - 16);
      }
    }
    // Kill on the left
    if (position%8 != 0 && p_game->board[position - 1 + 8 * sign] * sign < 0) {
      add_mvt(position - 1 + 8 * sign); // position +7/-9
    }
    // Kill on the right
    if (position%8 != 7 && p_game->board[position + 1 + 8 * sign] * sign < 0) {
      add_mvt(position + 1 + 8 * sign); // position +9/-7
    }
  }

  // knight
  if (type == 3) {
    if (position % 8 != 7) {
      if (position + 17 < 64 && p_game->board[position + 17] * sign <= 0) {
        add_mvt(position + 17);
      }
      if (position - 15 >= 0 && p_game->board[position - 15] * sign <= 0) {
        add_mvt(position - 15);
      }

      if (position % 8 != 6) {
        if (position + 10 < 64 && p_game->board[position + 10] * sign <= 0) {
          add_mvt(position + 10);
        }
        if (position - 6 >= 0 && p_game->board[position - 6] * sign <= 0) {
          add_mvt(position - 6);
        }
      }
    }

    if (position % 8 != 0) {
      if (position + 15 < 64 && p_game->board[position + 15] * sign <= 0) {
        add_mvt(position + 15);
      }
      if (position - 17 >= 0 && p_game->board[position - 17] * sign <= 0) {
        add_mvt(position - 17);
      }

      if (position % 8 != 1) {
        if (position + 6 < 64 && p_game->board[position + 6] * sign <= 0) {
          add_mvt(position + 6);
        }
        if (position - 10 >= 0 && p_game->board[position - 10] * sign <= 0) {
          add_mvt(position - 10);
        }
      }
    }
  }

  // king
  if (type == 6) {
    // Up
    if (position + 8 < 64 && p_game->board[position + 8] * sign <= 0) {
      add_mvt(position + 8);
    }
    // Down
    if (position - 8 >= 0 && p_game->board[position - 8] * sign <= 0) {
      add_mvt(position - 8);
    }
    // Right
    if ((position + 1) % 8 != 0 && p_game->board[position + 1] * sign <= 0) {
      add_mvt(position + 1);
    }
    // Left
    if (position != 0 && (position - 1) % 8 != 7 &&
      p_game->board[position - 1] * sign <= 0) {
      add_mvt(position - 1);
    }
    // Up-Right
    if (position + 9 < 64 && (position + 9) % 8 != 0 &&
      p_game->board[position + 9] * sign <= 0) {
      add_mvt(position + 9);
    }
    // Down-Right
    if (position - 7 >= 0 && (position - 7) % 8 != 0 &&
      p_game->board[position - 7] * sign <= 0) {
      add_mvt(position - 7);
    }
    // Up-Left
    if (position + 7 < 64 && (position + 7) % 8 != 7 &&
      p_game->board[position + 7] * sign <= 0) {
      add_mvt(position + 7);
    }
    // Down-Left
    if (position - 9 > 0 && (position - 9) % 8 != 7 &&
      p_game->board[position - 9] * sign <= 0) {
      add_mvt(position - 9);
    }

    // -------------------------------------------------------------------------
    // Only castling cases below !
    // -------------------------------------------------------------------------
    // Add potential castling moves, play() will deduce and move the rook too
    // White case
    if (!am_i_check && w_turn) {
      // If castling left is available and nobody is on the way (position == 4)
      if (p_game->castling_wl && p_game->board[1] == 0 && p_game->board[2] == 0
        && p_game->board[3] == 0) {
        // Has to be 2 to validate the castling (no check on the way nor at the
        // arrival)
        int checked = 0;
        // Am i check on the way ?
        play(p_game, position, 3, six_long_int_cache);
        if (!is_check(p_game, w_turn)) {
          checked ++;
        }
        unplay(p_game, six_long_int_cache);
        // Am i check at the arrival ?
        play(p_game, position, 2, six_long_int_cache);
        if (!is_check(p_game, w_turn)) {
          checked ++;
        }
        unplay(p_game, six_long_int_cache);
        if (checked == 2) {
          from[found] = position;
          to_[found] = 2;
          found ++;
        }
      }
      // If castling right is available and nobody is on the way (position == 4)
      if (p_game->castling_wl && p_game->board[5] == 0 &&
        p_game->board[6] == 0) {
        // Has to be 2 to validate the castling (no check on the way nor at the
        // arrival)
        int checked = 0;
        // Am i check on the way ?
        play(p_game, position, 5, six_long_int_cache);
        if (!is_check(p_game, w_turn)) {
          checked ++;
        }
        unplay(p_game, six_long_int_cache);
        // Am i check at the arrival ?
        play(p_game, position, 6, six_long_int_cache);
        if (!is_check(p_game, w_turn)) {
          checked ++;
        }
        unplay(p_game, six_long_int_cache);
        if (checked == 2) {
          from[found] = position;
          to_[found] = 6;
          found ++;
        }
      }
    // Black case
    } else if (!am_i_check && !w_turn) {
      // If castling left is available and nobody is on the way (position == 60)
      if (p_game->castling_wl && p_game->board[59] == 0 &&
        p_game->board[58] == 0 && p_game->board[57] == 0) {
        // Has to be 2 to validate the castling (no check on the way nor at the
        // arrival)
        int checked = 0;
        // Am i check on the way ?
        play(p_game, position, 59, six_long_int_cache);
        if (!is_check(p_game, w_turn)) {
          checked ++;
        }
        unplay(p_game, six_long_int_cache);
        // Am i check at the arrival ?
        play(p_game, position, 58, six_long_int_cache);
        if (!is_check(p_game, w_turn)) {
          checked ++;
        }
        unplay(p_game, six_long_int_cache);
        if (checked == 2) {
          from[found] = position;
          to_[found] = 58;
          found ++;
        }
      }
      // If castling right is available and nobody is on the way (position ==60)
      if (p_game->castling_wl && p_game->board[61] == 0 &&
        p_game->board[62] == 0) {
        // Has to be 2 to validate the castling (no check on the way nor at the
        // arrival)
        int checked = 0;
        // Am i check on the way ?
        play(p_game, position, 61, six_long_int_cache);
        if (!is_check(p_game, w_turn)) {
          checked ++;
        }
        unplay(p_game, six_long_int_cache);
        // Am i check at the arrival ?
        play(p_game, position, 62, six_long_int_cache);
        if (!is_check(p_game, w_turn)) {
          checked ++;
        }
        unplay(p_game, six_long_int_cache);
        if (checked == 2) {
          from[found] = position;
          to_[found] = 62;
          found ++;
        }
      }
    }
  }

  return found;
};


int all_available_movements(chess_game *p_game, int w_turn, int am_i_check,
  int *from, int *to_, int *six_long_int_cache) {

  int found = 0;
  int sign = 2 * (w_turn > 0) - 1;
  for (int pos = 0; pos < 64; pos++) {
    if (p_game->board[pos] * sign > 0) {
      found += available_movements(p_game, pos, am_i_check, from + found,
        to_ + found, six_long_int_cache);
    }
  }
  return found;
};


/*
 * Will the player be check after moving this ?
 * You must not be checked or move your king before calling this.
 * Only line / diag shared by king and moved piece is re-evaluated
 * Either returns 1 or 0
 */
int will_be_check(chess_game *p_game, int start, int arrival) {
  int sign = 2 * (p_game->board[start] > 0) - 1;
  int kpos;
  if (sign > 0) {
    kpos = p_game->w_king_pos;
  } else {
    kpos = p_game->b_king_pos;
  }

  int delta_row = start / 8 - kpos / 8;
  int delta_col = (start - kpos) % 8;
  int to_return = 0;

  // "Play" the move
  int cache = p_game->board[arrival];
  p_game->board[arrival] = p_game->board[start];
  p_game->board[start] = 0;
  // Re-check only the concerned line / diag
  if (delta_row == 0) {
    if (start > kpos) to_return = _scan_r(p_game, kpos, sign);
    else to_return = _scan_l(p_game, kpos, sign);

  } else if (delta_col == 0) {
    if (start > kpos) to_return = _scan_u(p_game, kpos, sign);
    else to_return = _scan_d(p_game, kpos, sign);

  } else if (delta_col == delta_row) {
    if (start > kpos) to_return = _scan_ur(p_game, kpos, sign);
    else to_return = _scan_dl(p_game, kpos, sign);

  } else if (delta_col == -delta_row) {
    if (start > kpos) to_return = _scan_ul(p_game, kpos, sign);
    else to_return = _scan_dr(p_game, kpos, sign);

  }
  p_game->board[start] = p_game->board[arrival];
  p_game->board[arrival] = cache;
  return to_return;
};


/*
 * What if it worth to kill this
 */
int _score_per_piece(int piece) {
  switch (abs(piece)) {
    case 1: return 1;
    case 2: return 5;
    case 3: return 3;
    case 4: return 3;
    case 5: return 9;
  }
  return 0;
}


/*
 * Total score (white is positive)
 */
int _total_w_score(chess_game *p_game) {
  int to_return = 0;
  for (int idx = 0; idx < 64; idx++) {
    to_return += (2 * (p_game->board[idx] > 0) - 1) * \
    _score_per_piece(p_game->board[idx]);
  }
  return to_return;
}


/*
 * Positive score increase for the guy who played this.
 * TODO: improve this by adding castling, & central positionning...
 */
int _score_per_play(chess_game *p_game, int from, int to) {
  return _score_per_piece(p_game->board[to]);
}


/*
 * Buils an alpha beta tree and return the best play be do (stores it into
 * best_from and best_to)
 */
void alpha_beta_predict(chess_game *p_game, int depth, int *p_best_from,
  int *p_best_to) {

  if (depth < 2 || depth % 2 != 0)
    error(1, 0, "Depth should be >= 2 and even !\n");

  long int seen = 0;
  int hero_sign = 2 * (p_game->w_turn) - 1;
  double start = clock();
  double time_elapsed;

  // Allocate from and to arrays
  int *froms = malloc(100 * depth * sizeof(int));
  int *tos = malloc(100 * depth * sizeof(int));

  /* Length of tree for each depth (available mouvements) */
  int mvt_nbs[depth];

  /* Unplays caches (one per depth) */
  int unplay_caches[6 * depth];

  /* Common cache -> we don't care (only for all_available_movements) */
  int common_cache[6];

  /* Where am I in the tree ? (idx on each depth) */
  int current_depth = 0;
  int current_index[depth];
  for (int idx=0; idx < depth; idx++) current_index[idx] = -1;

  /* Nu values at every depth */
  int nus[depth + 1];

  /* Best index (for depth 0) */
  int best_index;

  /* -------------------------------------------------------------------------*/
  /* Main Eval Loop */
  while (current_depth >= 0) {

    /* 1. If we touch the bottom, go up */
    if (current_depth == depth) {

      /* increment common node counter */
      seen ++;
      /* Update Nu */
      nus[current_depth] = p_game->w_score * hero_sign;
      /* Unplay the move that made us come here */
      unplay(p_game, &unplay_caches[current_depth - 1]);
      /* Decrese depth */
      current_depth --;

    /* 2. If we have not already (re)initialized moves at this depth & go down*/
    } else if (current_index[current_depth] == -1) {

      /* Evaluates all available movements for lower depth */
      mvt_nbs[current_depth] = all_available_movements(
        p_game,
        p_game->w_turn,
        is_check(p_game, p_game->w_turn),
        &froms[current_depth * 100],
        &tos[current_depth * 100],
        common_cache
      );

      /* If no mouvements are available: draw or mate (should not be called at
      depth 0 !!)*/
      if (mvt_nbs[current_depth] == 0) {
        /* Remove pathological case */
        if (current_depth == 0)
          error(1, 0, "You called the engine while the game is already over !");
        /* checkmate +/-1000 if hero wins or loses */
        if (is_check(p_game, p_game->w_turn)) {
          nus[current_depth] = 1000 * (2 * (current_depth % 2 == 0) - 1);
        /* draw */
        } else {
          nus[current_depth] = 0;
        }
        /* Counts as a terminal node, so increase seen */
        seen ++;
        /* Init index at this depth so that it will be re-init next time */
        current_index[current_depth] = -1;
        /* Unplay the move that made us come here */
        unplay(p_game, &unplay_caches[current_depth - 1]);
        /* Decrese depth */
        current_depth --;

      /* Normal case: no end-game -> go deeper through all possibilities */
      } else {
        /* Set your index at this depth */
        current_index[current_depth] = 0;
        /* Initialize Nu for this depth (+/- 5000) */
        nus[current_depth] = 5000 * (2 * (current_depth % 2 == 1) - 1);

        /* play the first move */
        play(
          p_game,
          froms[100 * current_depth + current_index[current_depth]],
          tos[100 * current_depth + current_index[current_depth]],
          &unplay_caches[current_depth]
        );
        /* increase depth */
        current_depth ++;
      }

    /* 3. If we have reached the end of the moves at this depth, go up */
    } else if (current_index[current_depth] == mvt_nbs[current_depth]) {

      /* Update Nu */
      if (current_depth % 2 == 0) {
        if (nus[current_depth + 1] > nus[current_depth]) {
          nus[current_depth] = nus[current_depth + 1];
          if (current_depth == 0)
            best_index = current_index[0];
        }
      } else if (nus[current_depth + 1] < nus[current_depth])
          nus[current_depth + 1] = nus[current_depth];

      /* Init index at this depth so that it will be re-initialized next time */
      current_index[current_depth] = -1;

      /* Unplay the move that made us come here (unless depth == 0, then this is
       the final loop)*/
      if (current_depth != 0)
        unplay(p_game, &unplay_caches[current_depth - 1]);

      /* Decrese depth */
      current_depth --;

    /* 4. We Check next move at this depth (we just went up), then go down */
    } else {

      /* Update Nu */
      if (current_depth % 2 == 0) {
        if (nus[current_depth + 1] > nus[current_depth]) {
          nus[current_depth] = nus[current_depth + 1];
          if (current_depth == 0)
            best_index = current_index[0];
        }
      } else if (nus[current_depth + 1] < nus[current_depth])
          nus[current_depth] = nus[current_depth];

      /* increase index at this depth */
      current_index[current_depth] ++;

      /* play the next move */
      play(
        p_game,
        froms[100 * current_depth + current_index[current_depth]],
        tos[100 * current_depth + current_index[current_depth]],
        &unplay_caches[current_depth]
      );
      /* increase depth */
      current_depth ++;
    }

  }

  /* Store best move in the given destinations */
  *p_best_from = froms[best_index];
  *p_best_to = tos[best_index];

  // Deallocate
  free(froms);
  free(tos);

  time_elapsed = (clock() - start) / CLOCKS_PER_SEC;
  printf("Time elapsed: %f s\n", time_elapsed);
  printf("Avg. Nodes/sec: %f\n", seen / time_elapsed);
  printf("Nodes Seen: %li\n", seen);

};
