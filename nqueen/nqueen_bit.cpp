#include <iostream>
#include <stdint.h>

// Idea from Frog https://github.com/fcamel/self-practice/pull/1
int nqueen(uint32_t middle, uint32_t left, uint32_t right, uint32_t full_columns) {
  int count = 0;
  uint32_t valid_columns = (~(middle | left | right)) & full_columns;
  for (uint32_t col = 1; col < full_columns; col <<= 1) {
    if ((valid_columns & col) == 0)
      continue;
    if ((col | middle) == full_columns)
      return 1;
    count += nqueen(middle | col, (left | col) << 1, (right | col) >> 1, full_columns);
  }
  return count;
}

int main(int argc, char *argv[]) {
  if (argc != 2)
    return 1;
  int n = atoi(argv[1]);
  printf("%d\n", nqueen(0, 0, 0, (1<<n) - 1));
  return 0;
}
