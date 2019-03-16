#include <iostream>

const int MAX = 20;

int n;
bool cols[MAX];
bool diag[MAX];  // col + row
bool diag2[MAX];  // col - row + (n - 1)

void solve(int row, int *count) {
  for (int col = 0; col < n; col++) {
    if (cols[col])
      continue;
    if (diag[col+row])
      continue;
    if (diag2[col-row+n-1])
      continue;

    // Check before entering the next depth. This is faster.
    if (row + 1 == n) {
      (*count)++;
      return;
    }

    cols[col] = diag[col+row] = diag2[col-row+n-1] = true;
    solve(row + 1, count);
    cols[col] = diag[col+row] = diag2[col-row+n-1] = false;
  }
}

int main(int argc, char *argv[]) {
  if (argc != 2)
    return 1;
  n = atoi(argv[1]);
  int count = 0;
  solve(0, &count);
  printf("%d\n", count);
  return 0;
}
