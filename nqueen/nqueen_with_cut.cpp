#include <iostream>

const int MAX = 20;

int n;
int count;
bool cols[MAX];
bool diag[MAX];  // col + row
bool diag2[MAX];  // col - row + (n - 1)

int begins[MAX];
int ends[MAX];
int next[MAX];

// NOTE: % is slow. For n = 14
// 1st version: no begins, ends, next       : 3.522s
// 2nd version: use begins, ends and no next: 3.412s
// 3rd version: use begins, ends, enxt      : 1.726s
//
// However, still slower than basic.cpp.
void nqueen(int row, int begin, int end) {
  bool run = true;
  for (int col = begin; run; col = next[col]) {
    //printf("debug: row=%d, [%d,%d] col=%d\n", row, begin, end, col);
    if (col == end) {
      run = false;
    }
    if (cols[col])
      continue;
    if (diag[col+row])
      continue;
    if (diag2[col-row+n-1])
      continue;
    if (row + 1 == n) {
      count++;
      return;
    }

    cols[col] = diag[col+row] = diag2[col-row+n-1] = true;
    nqueen(row + 1, begins[col], ends[col]);
    cols[col] = diag[col+row] = diag2[col-row+n-1] = false;
  }
}

int main(int argc, char *argv[]) {
  if (argc != 2)
    return 1;
  n = atoi(argv[1]);
  if (n < 4) {
    printf("0\n");
    return 0;
  }

  for (int col = 0; col < n; col++) {
    next[col] = (col + 1) % n;
    if (col <= 1) {
      begins[col] = col + 2;
      ends[col] = n - 1;
    } else if (col >= n - 2) {
      begins[col] = 0;
      ends[col] = col - 2;
    } else {
      begins[col] = col + 2;
      ends[col] = (col - 2 + n) % n;
    }
  }

  nqueen(0, 0, n-1);
  printf("%d\n", count);
  return 0;
}
