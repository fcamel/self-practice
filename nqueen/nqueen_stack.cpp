#include <iostream>

const int MAX = 20;

int stack[MAX];
bool cols[MAX];
bool diag[MAX];  // col + row
bool diag2[MAX];  // col - row + (n - 1)

int nqueen(int n) {
  int count = 0;
  int row = 0;
  stack[row] = -1;
  while (true) {
  begin:
    int col = stack[row] + 1;
    for (; col < n; col++) {
      //printf("debug: %d %d\n", row, col);
      if (cols[col])
        continue;
      if (diag[col+row])
        continue;
      if (diag2[col-row+n-1])
        continue;
      if (row + 1 == n) {
        count++;
        break;
      }

      //printf("debug: set %d %d\n", row, col);
      cols[col] = diag[col+row] = diag2[col-row+n-1] = true;
      // Push the state.
      stack[row++] = col;
      // Prepare to enter the next "recursion call".
      stack[row] = -1;
      goto begin;
    }
    if (row == 0)
      break;
    // Back to the "previous call".
    col = stack[--row];
    //printf("debug: reset %d %d\n", row, col);
    // Reset the state updated by the call.
    cols[col] = diag[col+row] = diag2[col-row+n-1] = false;
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
