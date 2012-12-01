#include <iostream>
#include <sys/syscall.h>

struct A {
  void Out() {
    std::cout << "tid=" << syscall(__NR_gettid)
        << " A.Out()" << std::endl;
  }

  void Out1(int n) {
    std::cout << "tid=" << syscall(__NR_gettid)
        << " A.Out(" << n << ")" << std::endl;
  }
};
