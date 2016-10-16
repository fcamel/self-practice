#include <time.h>
#include <stdint.h>
#include <stdlib.h>
#include <chrono>
#include <iostream>

// Comment out this if your CPU doesn't support SSE4.
#define SUPPORT_SSE4

const int kMax8 = 1 << 8;
const int kMax16 = 1 << 16;

void prepare_input(uint16_t* data, int size)
{
    for (int i = 0 ; i < size; i++) {
        data[i] = rand() % kMax16;
    }
}

//-------------------------------------------------------------------------------
// Direct count.
//-------------------------------------------------------------------------------
int count16(uint16_t a)
{
    int n = 0;
    for (int i = 0; i < 16; i++) {
        n += a & 1;
        a >>= 1;
    }
    return n;
}

int count_directly(uint16_t* data, int size)
{
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += count16(data[i]);
    }
    return sum;
}

//-------------------------------------------------------------------------------
// Lookup table.
//-------------------------------------------------------------------------------
int s_table16[kMax16];
void prepare_bit_count_table16()
{
    for (int i = 0; i < kMax16; i++) {
        s_table16[i] = count16(i);
    }
}

int count_by_table(uint16_t* data, int size)
{
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += s_table16[ data[i] ];
    }
    return sum;
}

//-------------------------------------------------------------------------------

int count8(uint8_t a)
{
    int n = 0;
    for (int i = 0; i < 8; i++) {
        n += a & 1;
        a >>= 1;
    }
    return n;
}

uint8_t s_table8[kMax8];
void prepare_bit_count_table8()
{
    for (int i = 0; i < kMax8; i++) {
        s_table8[i] = count8(i);
    }
}

int count_by_table8(uint16_t* data, int size)
{
    int sum = 0;
    size *= 2;
    uint8_t* p = (uint8_t*)data;
    for (int i = 0; i < size; i++) {
        sum += s_table8[ p[i] ];
    }
    return sum;
}

//-------------------------------------------------------------------------------
// Bit operation.
//-------------------------------------------------------------------------------

// Ref. https://en.wikipedia.org/wiki/Hamming_weight
const uint64_t m1  = 0x5555555555555555; //binary: 0101...
const uint64_t m2  = 0x3333333333333333; //binary: 00110011..
const uint64_t m4  = 0x0f0f0f0f0f0f0f0f; //binary:  4 zeros,  4 ones ...
const uint64_t m8  = 0x00ff00ff00ff00ff; //binary:  8 zeros,  8 ones ...
const uint64_t m16 = 0x0000ffff0000ffff; //binary: 16 zeros, 16 ones ...
const uint64_t m32 = 0x00000000ffffffff; //binary: 32 zeros, 32 ones
const uint64_t hff = 0xffffffffffffffff; //binary: all ones
const uint64_t h01 = 0x0101010101010101; //the sum of 256 to the power of 0,1,2,3...

int popcount_3(uint64_t x)
{
    x -= (x >> 1) & m1;             //put count of each 2 bits into those 2 bits
    x = (x & m2) + ((x >> 2) & m2); //put count of each 4 bits into those 4 bits 
    x = (x + (x >> 4)) & m4;        //put count of each 8 bits into those 8 bits 
    return (x * h01)>>56;  //returns left 8 bits of x + (x<<8) + (x<<16) + (x<<24) + ... 
}

int count_by_bit_operation(uint16_t* data, int size)
{
    int sum = 0;
    int i = 0;
    for (; i <= size - 4; i += 4) {
        sum += popcount_3(*(uint64_t*)&data[i]);
    }
    for (; i < size; i++) {
        sum += s_table16[ data[i] ];
    }
    return sum;
}

//-------------------------------------------------------------------------------
// SSE4 popcnt.
//-------------------------------------------------------------------------------

#ifdef SUPPORT_SSE4
// Copied and modified from https://github.com/WojciechMula/sse-popcount
// -> builtin-popcnt-unrolled-errata-manual.
//
// Here's a version that doesn't rely on the compiler not doing
// bad optimizations.
// This code is from Alex Yee.
int count_by_popcnt(uint16_t* data, int size)
{
    uint64_t cnt[4];
    for (int i = 0; i < 4; ++i) {
        cnt[i] = 0;
    }
    uint64_t* p = (uint64_t*)data;
    int pSize = size / 4;

    int i = 0;
    for (; i <= pSize - 4; i += 4) {
        __asm__ __volatile__(
            "popcnt %4, %4  \n\t"
            "add %4, %0     \n\t"
            "popcnt %5, %5  \n\t"
            "add %5, %1     \n\t"
            "popcnt %6, %6  \n\t"
            "add %6, %2     \n\t"
            "popcnt %7, %7  \n\t"
            "add %7, %3     \n\t"
            : "+r" (cnt[0]), "+r" (cnt[1]), "+r" (cnt[2]), "+r" (cnt[3])
            : "r"  (p[i]), "r"  (p[i+1]), "r"  (p[i+2]), "r"  (p[i+3])
        );
    }
    int sum = cnt[0] + cnt[1] + cnt[2] + cnt[3];

    // Handle the rest.
    i = i * 4;
    for (; i < size; i++) {
        sum += s_table16[ data[i] ];
    }
    return sum;
}
#endif

//-------------------------------------------------------------------------------
// main.
//-------------------------------------------------------------------------------

void test(const char* name, int (*func)(uint16_t* data, int size), uint16_t* data, int size)
{
    std::chrono::time_point<std::chrono::high_resolution_clock> begin, end;
    begin = std::chrono::high_resolution_clock::now();
    int64_t sum = 0;
    for (int i = 0; i < 1000; i++) {
        sum += func(data, size);
    }
    end = std::chrono::high_resolution_clock::now();

    std::cout << name << ": sum=" << sum << ", duration="
        << std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin).count()
        << " ns" << std::endl;
}

int main(void)
{
    int kDataSize = 1000000;
    uint16_t data[kDataSize];
    int sum = 0;

    srand(time(NULL));

    prepare_bit_count_table8();
    prepare_bit_count_table16();
    prepare_input(data, kDataSize);

    test("count_directly        ", count_directly, data, kDataSize);
    test("count_by_table        ", count_by_table, data, kDataSize);
    test("count_by_table8       ", count_by_table8, data, kDataSize);
    test("count_by_bit_operation", count_by_bit_operation, data, kDataSize);
#ifdef SUPPORT_SSE4
    test("count_by_popcnt       ", count_by_popcnt, data, kDataSize);
#endif

    return 0;
}
