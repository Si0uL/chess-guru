CC=gcc
CFLAGS=-W -O3 -Wall -std=c99 -pedantic
LDFLAGS=
EXEC=simple_tester

all: $(EXEC)

simple_tester: game.o simple_tester.o
	$(CC) -o $@ $^ $(LDFLAGS)

game.o: game.c
	$(CC) -o $@ -c $< $(CFLAGS)

simple_tester.o: simple_tester.c game.h
	$(CC) -o $@ -c $< $(CFLAGS)

clean:
	rm -rf *.o

mrproper: clean
	rm -rf $(EXEC)
