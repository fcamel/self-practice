#include <iostream>
#include <sstream>
#include <string>
#include "vec.h"

int main(void) {
  Vec<std::string> strs;
  for (int i = 0; i < 10; i++) {
    std::stringstream ss;
    ss << i;
    strs.push_back(ss.str());
  }
  for (int i = 0; i < 10; i++) {
    std::cout << strs[i] << " ";
  }
  std::cout << std::endl;

  return 0;
}
