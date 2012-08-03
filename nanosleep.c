#include <stdio.h>
#include <time.h>

int main(int argc, char** argv) {
	struct timespec tim, tim2;

	if (argc!=2) {
		printf("Error, requires one argument.\n");
		printf("\tUsage: nanosleep <nanoseconds>\n");
		return -1;
	}

	tim.tv_sec = 1;
	tim.tv_nsec = atoi(argv[argc-1]);
	if (tim.tv_nsec<=0) {
		printf("Error converting given time to integer!\n");
		return -1;
	}

	if(nanosleep(&tim , &tim2) < 0 ) {
		printf("Nano sleep system call failed!\n");
		return -1;
	}

	//printf("Nano sleep successfull \n");

	return 0;
}
