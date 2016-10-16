#include <time.h>
#include <stdint.h>
#include <stdlib.h>
#include <chrono>
#include <iostream>
#include <stdlib.h>
#include <string.h>
#include <algorithm>
#include <stack>

const int kDataSize = 1000000;

uint64_t urand64()
{
      uint64_t hi = lrand48();
      uint64_t md = lrand48();
      uint64_t lo = lrand48();
      return (hi << 42) + (md << 21) + lo;
}

void prepare_input(uint64_t* data, int size)
{
    for (int i = 0 ; i < size; i++) {
        data[i] = urand64();
    }
}

bool verify(uint64_t* data, int size)
{
    for (int i = 1; i < size; i++) {
        if (data[i] < data[i - 1]) {
            return false;
        }
    }
    return true;
}

uint64_t buf0[kDataSize];
uint64_t buf1[kDataSize];
void radix_sort(uint64_t* data, int size)
{
    int zero_size, one_size;
    for (int i = 0; i < sizeof(data[0]) * 8; i++) {
        const uint64_t target_bit = 1ll << i;
        zero_size = one_size = 0;
        for (int j = 0; j < size; j++) {
            if ((data[j] & target_bit) == target_bit) {
                buf1[one_size++] = data[j];
            } else {
                buf0[zero_size++] = data[j];
            }
        }

        int k = 0;
        for (int j = 0; j < zero_size; j++) {
            data[k++] = buf0[j];
        }
        for (int j = 0; j < one_size; j++) {
            data[k++] = buf1[j];
        }
    }
}

// Sort data in [begin, end)
void _radix_sort_inplace(uint64_t* data, int begin, int end, int depth)
{
    if ((end - begin) <= 1 || depth < 0) {
        return;
    }

    const uint64_t target_bit = 1ll << depth;
    int leftest_one = -1;
    int i = begin;
    for (; i < end; i++) {
        if ((data[i] & target_bit) == target_bit) {
            leftest_one = i;
            break;
        }
    }
    if (i >= end) {
        // All zero.
        _radix_sort_inplace(data, begin, end, depth - 1);
        return;
    }

    for (i++; i < end; i++) {
        if (!(data[i] & target_bit)) {
            std::swap(data[i], data[leftest_one]);
            leftest_one++;
        }
    }

    _radix_sort_inplace(data, begin, leftest_one, depth - 1);
    _radix_sort_inplace(data, leftest_one, end, depth - 1);
}

void radix_sort_inplace(uint64_t* data, int size)
{
    _radix_sort_inplace(data, 0, size, sizeof(data[0]) * 8 - 1);
}

struct Record {
    int begin;
    int end;
    int depth;

    Record(int begin, int end, int depth)
        : begin(begin), end(end), depth(depth)
    {
    }
};

void radix_sort_inplace_stack(uint64_t* data, int size)
{
    std::stack<Record> stack;
    stack.push(Record(0, size, sizeof(data[0]) * 8 - 1));
    while (!stack.empty()) {
        Record r = stack.top();
        stack.pop();
        if ((r.end - r.begin) <= 1 || r.depth < 0) {
            continue;
        }

        const uint64_t target_bit = 1ll << r.depth;
        int leftest_one = -1;
        int i = r.begin;
        for (; i < r.end; i++) {
            if ((data[i] & target_bit) == target_bit) {
                leftest_one = i;
                break;
            }
        }
        if (i >= r.end) {
            if (r.end - r.begin > 1 && r.depth > 0)
                stack.push(Record(r.begin, r.end, r.depth - 1));
            continue;
        }

        for (i++; i < r.end; i++) {
            if (!(data[i] & target_bit)) {
                std::swap(data[i], data[leftest_one]);
                leftest_one++;
            }
        }

        if (leftest_one - r.begin > 1 && r.depth > 0)
            stack.push(Record(r.begin, leftest_one, r.depth - 1));
        if (r.end - leftest_one > 1 && r.depth > 0)
            stack.push(Record(leftest_one, r.end, r.depth - 1));
    }
}

int cmp(const void *a, const void *b)
{
    uint64_t ta = *(uint64_t*)a;
    uint64_t tb = *(uint64_t*)b;
    if (ta < tb) {
        return -1;
    } else if (ta > tb) {
        return 1;
    } else {
        return 0;
    }
}

void quick_sort(uint64_t* data, int size)
{
    qsort(data, size, sizeof(data[0]), cmp);
}

void test(const char* name, void (*func)(uint64_t* data, int size), uint64_t* data, int size)
{
    std::chrono::time_point<std::chrono::high_resolution_clock> begin, end;
    begin = std::chrono::high_resolution_clock::now();
    func(data, size);
    end = std::chrono::high_resolution_clock::now();

    std::cout << name << ": verify=" << verify(data, size) << ", duration="
        << std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin).count()
        << " ns" << std::endl;
}

uint64_t input[kDataSize];
uint64_t tmp[kDataSize];

int main(void) {
    srand48(time(NULL));
    prepare_input(input, kDataSize);

    memcpy(tmp, input, sizeof(tmp));
    test("quick sort                          ", quick_sort, tmp, kDataSize);

    memcpy(tmp, input, sizeof(tmp));
    test("radix sort                          ", radix_sort, tmp, kDataSize);

    memcpy(tmp, input, sizeof(tmp));
    test("radix sort (in-place, recursive)    ", radix_sort_inplace, tmp, kDataSize);

    memcpy(tmp, input, sizeof(tmp));
    test("radix sort (in-place, non-recursive)", radix_sort_inplace_stack, tmp, kDataSize);

    return 0;
}
