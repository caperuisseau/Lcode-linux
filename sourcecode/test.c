#include <stdio.h>
#include <stdlib.h>

int cacaboudin = 0;

int main() {
	int plusenplus = 0;
	while (1) {
		printf("%d\n", plusenplus);
		printf("%p\n", *plusenplus);
		plusenplus++;
	}
	return 0;
}
