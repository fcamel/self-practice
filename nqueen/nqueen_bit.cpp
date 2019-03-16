#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

int nqueen(uint16_t col, uint16_t left, uint64_t right, uint16_t target) {
	uint64_t m = col | left |right;
	int c = 0;
	for (uint32_t i = 1; i < (uint32_t)target; i <<= 1) {
		if (i & m) continue;
		if ((i | col) == target) return 1;
		c += nqueen(col | i, (left | i) << 1, (right | i) >> 1, target);
	}

	return c;
}

int main(int argc, char **argv)
{
	int n = atoi(argv[1]);
	uint16_t x = (1 << n) - 1;
	printf("Calculating %x\n", x);
	int a = nqueen(0, 0, 0, (1 << n) - 1);
	printf("%d\n", a);

	return 0;
}
