#include <iostream>
#include <chrono>


struct M {
  M& operator=(const M& a) {
    for (int i = 0; i < 2; i++)
      for (int j = 0; j < 2; j++)
        d[i][j] = a.d[i][j];

    return *this;
  }

  long long d[2][2];
};

struct V {
  long long d[2];
};

M operator*(const M& a, const M& b) {
  M c;

  c.d[0][0] = a.d[0][0] * b.d[0][0] + a.d[0][1] * b.d[1][0];
  c.d[0][1] = a.d[0][0] * b.d[0][1] + a.d[0][1] * b.d[1][1];
  c.d[1][0] = a.d[1][0] * b.d[0][0] + a.d[1][1] * b.d[1][0];
  c.d[1][1] = a.d[1][0] * b.d[0][1] + a.d[1][1] * b.d[1][1];

  return c;
}

M operator^(const M& m, unsigned n) {
  if (n == 0) {
    M t;
    t.d[0][0] = t.d[0][1] = t.d[1][0] = t.d[1][1] =  1;
    return t;
  }

  if (n == 1)
    return m;

  unsigned k = n / 2;
  M t = m ^ k;
  if (n & 1)
    return t * t * m;
  return t * t;
}

V operator*(const M& m, const V& v) {
  V r;

  r.d[0] = m.d[0][0] * v.d[0] + m.d[0][1] * v.d[1];
  r.d[1] = m.d[1][0] * v.d[0] + m.d[1][1] * v.d[1];

  return r;
}

long long fib_by_matrix(bool optimization, int n) {
  if (n <= 1)
    return 1;

  /*
    M = [1 1]  V = [Fn+1]
        [1 0]      [Fn]

    M * V = [Fn+1 + Fn] = [Fn+2]
            [Fn+1     ]   [Fn+1]
  */
  V v;
  v.d[0] = v.d[1] = 1;

  M m;
  m.d[0][0] = m.d[0][1] = m.d[1][0] = 1;
  m.d[1][1]  = 0;

  if (optimization) {
    m = m ^ (n - 2 + 1);
    v = m * v;
  } else {
    for (int i = 2; i <= n; i++) {
      v = m * v;
    }
  }

  return v.d[0];
}

long long fib(int n) {
  if (n <= 1)
    return 1;

  long long a = 1;
  long long b = 1;
  long long c;
  for (int i = 2; i <= n; i++) {
    c = a + b;
    a = b;
    b = c;
  }
  return c;
}

void time_it(const char* name, long long (*f)(int), int n, int k) {
  auto start = std::chrono::system_clock::now();
  long long r;
  for (int i = 0; i < k; i++) {
    r = f(n);
  }
  auto end = std::chrono::system_clock::now();
  std::chrono::duration<double> elapsed_seconds = end - start;

  std::cout << name << " " << r << " " << elapsed_seconds.count() << std::endl;
}

int main(int argc, char **argv) {
  if (argc < 3) {
    std::cout << argv[0] << " <N> <k>" << std::endl;
    std::cout << std::endl;
    std::cout << "Run fib(N) k times and output the execution time in second." << std::endl << std::endl;
    return -1;
  }

  int n = atoi(argv[1]);
  int k = atoi(argv[2]);

  auto fm = [](int n) { return fib_by_matrix(false, n); };
  auto fm2 = [](int n) { return fib_by_matrix(true, n); };

  time_it("fib           (loop)  ", fib, n, k);
  time_it("fib by matrix (linear)", fm, n, k);
  time_it("fib by matrix (log(N))", fm2, n, k);

  return 0;
}
