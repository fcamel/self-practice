#include <iostream>
#include <stdint.h>

#define LSB(n) ((n) & -(n))

// Idea from Frog https://github.com/fcamel/self-practice/pull/1
int nqueen(int n) {
  int count = 0;
  const uint32_t full_columns = (1 << n) - 1;
  uint32_t col_stack[n];
  uint32_t valid_columns_stack[n];
  uint32_t middle_stack[n];
  uint32_t left_stack[n];
  uint32_t right_stack[n];

  uint32_t middle = 0;
  uint32_t left = 0;
  uint32_t right = 0;
  int row = 0;
  while (true) {
  new_call:
    uint32_t valid_columns = (~(middle | left | right)) & full_columns;
    uint32_t col = LSB(valid_columns);
  loop:
    for (; col; valid_columns ^= col, col = LSB(valid_columns)) {
      if ((col | middle) == full_columns) {
        count++;
        goto back;
      }
      middle_stack[row] = middle;
      left_stack[row] = left;
      right_stack[row] = right;
      valid_columns_stack[row] = valid_columns;
      col_stack[row] = col;
      middle = middle | col;
      left = (left | col) << 1;
      right = (right | col) >> 1;
      row++;
      goto new_call;
    }
  back:
    if (--row < 0)
      break;
    middle = middle_stack[row];
    left = left_stack[row];
    right = right_stack[row];
    valid_columns = valid_columns_stack[row];
    col = col_stack[row];
    valid_columns ^= col, col = LSB(valid_columns);
    goto loop;
  }
  return count;
}

int main(int argc, char *argv[]) {
  if (argc != 2)
    return 1;
  int n = atoi(argv[1]);
  printf("%d\n", nqueen(n));
  return 0;
}
