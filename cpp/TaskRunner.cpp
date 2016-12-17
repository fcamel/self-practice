#include "TaskRunner.h"

void Task::Run()
{
  m_function();
#ifndef NDEBUG
  std::cout << "TaskRunner: " << m_location.ToString() << std::endl;
#endif
}

void Task::Cancel()
{
  m_function.Reset();
}

bool Task::Greater(const Task& other) const
{
  bool result = m_time > other.m_time;
  if (result)
    return true;
  return m_sn > other.m_sn;
}

//------------------------------------------------------------------------------

void TaskRunner::Start()
{
  std::unique_lock<std::mutex> lock(m_mutex);
  m_running = true;
  while (true) {
    if (!m_running) {
      break;
    }

    m_cv.wait(lock, [this]{ return !m_queue.empty(); });
    auto now = std::chrono::steady_clock::now();
    while (!m_queue.empty()) {
      const Task& task = m_queue.top();
      if (now < task.GetRunTime()) {
        break;
      }
      lock.unlock();

      // Executing the task may take a long time, release the lock first.
      const_cast<Task*>(&task)->Run();

      lock.lock();
      m_queue.pop();
    }
    if (!m_queue.empty()) {
      const Task& task = m_queue.top();
      std::chrono::nanoseconds diff = task.GetRunTime() - std::chrono::steady_clock::now();
#ifndef NDEBUG
      std::cout << "TaskRunner: No task to run. Wait for "
        << (std::chrono::duration_cast<std::chrono::milliseconds>(diff).count()  /1000.)
        << "s" << std::endl;
#endif
      m_cv.wait_for(lock, diff);
    }
  }
}

void TaskRunner::Stop()
{
  PostTask(FROM_HERE, Bind(&TaskRunner::DoStop, Unretained<TaskRunner>(this)));
}

void TaskRunner::DoStop()
{
  // Inside the lock.
  m_running = false;
}

void TaskRunner::PostTask(const Location& location, const Function& task)
{
  PostDelayedTask(location, task, std::chrono::nanoseconds(0));
}

void TaskRunner::PostDelayedTask(const Location& location,
    const Function& task,
    std::chrono::seconds delay)
{
  PostDelayedTask(location, task, std::chrono::duration_cast<std::chrono::nanoseconds>(delay));
}

void TaskRunner::PostDelayedTask(const Location& location,
    const Function& task,
    std::chrono::milliseconds delay)
{
  PostDelayedTask(location, task, std::chrono::duration_cast<std::chrono::nanoseconds>(delay));
}

void TaskRunner::PostDelayedTask(const Location& location,
    const Function& task,
    std::chrono::microseconds delay)
{
  PostDelayedTask(location, task, std::chrono::duration_cast<std::chrono::nanoseconds>(delay));
}

void TaskRunner::PostDelayedTask(const Location& location,
    const Function& task,
    std::chrono::nanoseconds delay)
{
  auto now = std::chrono::steady_clock::now() + delay;

  std::lock_guard<std::mutex> lock(m_mutex);
  m_queue.push(Task(task, now, ++m_sn, location));
  if (m_queue.size() == 1) {
    m_cv.notify_one();
  }
}
