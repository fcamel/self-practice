#ifndef _VEC_H_
#define _VEC_H_

#include <memory>
#include <cstddef>
#include <cmath>

// Practice topics in Accelerated C++ ch11
// 
// Mainly practice template and using memory.

template <class T>
class Vec {
public:
  typedef T value_type;
  typedef T* pointer;
  typedef T& reference;
  typedef const T* const_pointer;
  typedef const T& const_reference;
  typedef size_t size_type;
  typedef ptrdiff_t difference_type;
  typedef T* iterator;
  typedef const T* const_iterator;

  Vec() { create(); }
  Vec(size_type n, const T& v) { create(n, v); }
  Vec(const_iterator begin, const_iterator end) { create(begin, end); }
  ~Vec() { uncreate(); }


  size_type size() { return m_avail - m_data; }
  void push_back(const T& v);

  T& operator=(const T& v);
  T& operator[](size_type i);
  const T& operator[](size_type i) const;

  iterator begin();
  const_iterator  begin() const;
  iterator end();
  const_iterator end() const;

private:
  void create();
  void create(const_iterator begin, const_iterator end);
  void create(size_type n, const T& v);
  void uncreate();
  void grow();

  std::allocator<T> m_allocator;
  iterator m_data;
  iterator m_avail;
  iterator m_limit;
};


template <class T>
void Vec<T>::push_back(const T& v) {
  if (m_avail == m_limit) {
    grow();
  }

  m_allocator.construct(m_avail++, v);
}

template <class T>
T& Vec<T>::operator=(const T& v) {
  if (this == &v) {
    return this;
  }

  uncreate();
  create(v.m_data, v.m_avail);

  return this;
}

// Effective C++ item 7: use casting to avoid duplicated codes between
//   const and non-const implementations.
template <class T>
T& Vec<T>::operator[](size_type i) {
  return const_cast<T&>(
    static_cast<const Vec&>(*this)[i]
  );
}

template <class T>
const T& Vec<T>::operator[](size_type i) const {
  return *(m_data + i);
}

// Effective C++ item 42: the compiler cannot identify a dependent type.
//   Use "typename" to tell it it's a typename.
template <class T>
typename Vec<T>::const_iterator Vec<T>::begin() const {
  return m_data;
}

template <class T>
typename Vec<T>::iterator Vec<T>::begin() {
  return const_cast<Vec::iterator>(static_cast<const T&>(*this).begin());
}

template <class T>
typename Vec<T>::const_iterator Vec<T>::end() const {
  return m_avail;
}

template <class T>
typename Vec<T>::iterator Vec<T>::end() {
  return m_avail;
}

template <class T>
void Vec<T>::create() {
  m_data = m_avail = m_limit = 0;
}

template <class T>
void Vec<T>::create(size_type n, const T& v) {
  m_data = m_allocator.allocate(n);
  m_limit = m_avail = m_data + n;
  std::uninitialized_fill(m_data, m_limit, v);
}

template <class T>
void Vec<T>::create(const_iterator begin, const_iterator end) {
  m_data = m_allocator.allocate(end - begin);
  m_limit = m_avail = std::uninitialized_copy(begin, end, m_data);
}

template <class T>
void Vec<T>::uncreate() {
  if (m_data) {
    
    for (iterator it = m_data; it != m_avail; it++) {
      m_allocator.destroy(it);
    }
    m_allocator.deallocate(m_data, m_limit - m_data);
  }
  m_data = m_avail = m_limit;
}

template <class T>
void Vec<T>::grow() {
  size_type new_size = std::max(ptrdiff_t(1), (m_limit - m_data) * 2);
  iterator new_data = m_allocator.allocate(new_size);
  iterator new_avail = std::uninitialized_copy(m_data, m_avail, new_data);

  uncreate();

  m_data = new_data;
  m_avail = new_avail;
  m_limit = m_data + new_size;
}

#endif // _VEC_H_
