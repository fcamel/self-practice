#include "f.h"
#include "t.h"

/* Compilation: g++ f.cpp -o f -g -Wall -lpthread */
int main(void) {
  A a;
  a.Out();  // Direct call.

  MethodWrapper0<A>* m = new MethodWrapper0<A>(&a, &A::Out);
  m->Run();  // Called via the wrapper.

  CallMethod0<A>(m);  // Called via a template function.

  pthread_t th = RunInNewThread(&a, &A::Out);  // Called in a new thread.
  pthread_join(th, NULL);

  a.Out1(1);  // Direct call.

  th = RunInNewThread(&a, &A::Out1, 2);  // Called in a new thread.
  pthread_join(th, NULL);

  return 0;
}
