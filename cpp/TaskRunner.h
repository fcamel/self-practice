#ifndef _TASK_RUNNER_H
#define _TASK_RUNNER_H

#include <iostream>
#include <condition_variable>
#include <sstream>
#include <functional>
#include <memory>
#include <queue>
#include <chrono>
#include <string>
#include <vector>
#include <mutex>
#include <type_traits>
#include <stdint.h>

// TODO: bind TaskRunner with an existed thread.
// TODO: bind TaskRunner with a new thread.

namespace {

void NOP() {}

}

template <typename T>
struct UnretainedPointer
{
  UnretainedPointer(T* p) : pointer(p) {}
  T& operator*() const { return *pointer; }
  T* pointer;
};

template <typename T>
UnretainedPointer<T> Unretained(T* p)
{
  return UnretainedPointer<T>(p);
}

class Function;

template <typename Method, typename Class, typename... Args>
Function Bind(Method m, Class o, Args&&... args);

template <typename Method, typename Class, typename... Args>
Function BindWeakPtr(Method m, Class o, Args&&... args);

class Function
{
public:
  void operator()() { m_function(); }
  void Reset() { m_function = std::bind(NOP); }

private:
  template <typename Method, typename Class, typename... Args>
  friend Function Bind(Method m, Class o, Args&&... args);

  template <typename Method, typename Class, typename... Args>
  friend Function BindWeakPtr(Method m, Class o, Args&&... args);

  Function(std::function<void()> function) : m_function(function) {}

private:
  std::function<void()> m_function;
};

template <typename T>
class WeakFunction
{
public:
  typedef std::function<void(std::shared_ptr<T>)> SafeFunction;
  WeakFunction(std::weak_ptr<T> p, const SafeFunction& function)
    : m_p(p)
    , m_function(function)
  {
  }

  void operator()()
  {
    auto p = m_p.lock();
    if (p) {
      m_function(p);
    }
  }

private:
  std::weak_ptr<T> m_p;
  SafeFunction m_function;
};

template <typename T>
struct IsSharedPtr { static const bool value = false; };

template <typename T>
struct IsSharedPtr<std::shared_ptr<T> > { static const bool value = true; };

template <typename T>
struct IsWeakPtr { static const bool value = false; };

template <typename T>
struct IsWeakPtr<std::weak_ptr<T> > { static const bool value = true; };

template <typename Method, typename Class, typename... Args>
Function Bind(Method m, Class o, Args&&... args)
{
  static_assert(!std::is_pointer<Class>::value || IsSharedPtr<Class>::value,
                "Not a shared_ptr. Use Unretained() if you're sure it is safe to put the raw pointer.");
  return Function(std::bind(m, o, std::forward<Args>(args)...));
}

template <typename Method, typename Class, typename... Args>
Function BindWeakPtr(Method m, Class o, Args&&... args)
{
  static_assert(IsWeakPtr<Class>::value, "Not a weak_ptr.");
  auto f = std::bind(m, std::placeholders::_1, std::forward<Args>(args)...);
  WeakFunction<typename Class::element_type> wf(o, f);
  return Function(std::bind(wf));
}

struct Location
{
  Location(const char* functionName, const char* fileName, int lineNumber)
  : functionName(functionName)
  , fileName(fileName)
  , lineNumber(lineNumber)
  {
  }

  std::string ToString() const
  {
    std::ostringstream ss;
    ss << functionName << "() " << fileName << ":" << lineNumber;
    return ss.str();
  }

  const char* functionName;
  const char* fileName;
  int lineNumber;
};

#define FROM_HERE Location(__FUNCTION__, __FILE__, __LINE__)

class Task
{
public:
  Task(const Function& function,
       std::chrono::steady_clock::time_point time,
       int32_t sn,
       const Location& location)
  : m_function(function)
  , m_time(time)
  , m_sn(sn)
  , m_location(location)
  {
  }

  void Run();
  void Cancel();
  const std::chrono::steady_clock::time_point& GetRunTime() const { return m_time; }
  bool Greater(const Task& other) const;

private:
  Function m_function;
  std::chrono::steady_clock::time_point m_time;
  int32_t m_sn;
  Location m_location;
};

class TaskComparator
{
public:
  bool operator() (const Task &lhs, const Task &rhs)
  {
    return lhs.Greater(rhs);
  }
};

class TaskRunner
{
public:
  TaskRunner()
      : m_running(false)
      , m_sn(0)
  {
  }

  void Start();
  void Stop();

  void PostTask(const Location& location, const Function& task);
  void PostDelayedTask(const Location& location,
                       const Function& task,
                       std::chrono::seconds delay);
  void PostDelayedTask(const Location& location,
                       const Function& task,
                       std::chrono::milliseconds delay);
  void PostDelayedTask(const Location& location,
                       const Function& task,
                       std::chrono::microseconds delay);
  void PostDelayedTask(const Location& location,
                       const Function& task,
                       std::chrono::nanoseconds delay);

private:
  void DoStop();

private:
  std::mutex m_mutex;
  std::condition_variable m_cv;
  std::priority_queue<Task, std::vector<Task>, TaskComparator> m_queue;
  bool m_running;
  int32_t m_sn;
};

#endif // _TASK_RUNNER_H
