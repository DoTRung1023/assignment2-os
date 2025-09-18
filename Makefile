all:
	gcc -Wall -Wextra -std=c99 -o memsim memsim.c
# 	./memsim trace.txt 4 rand debug
clean:
	rm -f memsim
