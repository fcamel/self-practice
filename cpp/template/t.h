#include <pthread.h>

template<class T>
struct MethodWrapper0 {
  typedef void(T::*Method)();
  MethodWrapper0(T *object, Method method)
      : m_object(object), m_method(method) {}

  void Run() { (m_object->*m_method)(); }

  T *m_object;
  Method m_method;
};

template<class T, class A>
struct MethodWrapper1 {
  typedef void(T::*Method)(A);
  MethodWrapper1(T *object, Method method, A a)
      : m_object(object), m_method(method), m_a(a) {}

  void Run() { (m_object->*m_method)(m_a); }

  T *m_object;
  Method m_method;
  A m_a;
};

// The interface for pthread's usage.
template <class T>
void* CallMethod0(void *v) {
  MethodWrapper0<T> *p = (MethodWrapper0<T>*)v;
  p->Run();
  delete p;
  return NULL;
}

template <class T, class A>
void* CallMethod1(void *v) {
  MethodWrapper1<T, A> *p = (MethodWrapper1<T, A>*)v;
  p->Run();
  delete p;
  return NULL;
}

template <class T>
inline pthread_t RunInNewThread(T *object, void (T::*method)()) {
  MethodWrapper0<T> *param = new MethodWrapper0<T>(object, method);
  pthread_t th;
  pthread_create(&th, NULL, CallMethod0<T>, (void*)param);

  return th;
}

template <class T, class A>
inline pthread_t RunInNewThread(T *object, void(T::*method)(A), A a) {
  MethodWrapper1<T, A> *param = new MethodWrapper1<T, A>(object, method, a);
  pthread_t th;
  pthread_create(&th, NULL, CallMethod1<T, A>, (void*)param);

  return th;
}
