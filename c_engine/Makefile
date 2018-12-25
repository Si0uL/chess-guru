CC=gcc
CFLAGS=-W -O3 -Wall -std=c99 -pedantic
LDFLAGS=
EXEC=simple_tester

all: $(EXEC)

predictor: predictor.o game.o
	$(CC) -o $@.out $^ $(LDFLAGS)

simple_tester: simple_tester.o game.o
	$(CC) -o $@.out $^ $(LDFLAGS)

game.o: game.c
	$(CC) -o $@ -c $< $(CFLAGS)

predictor.o: predictor.c game.h
	$(CC) -o $@ -c $< $(CFLAGS)

simple_tester.o: simple_tester.c game.h
	$(CC) -o $@ -c $< $(CFLAGS)

clean:
	rm -rf *.o

mrproper: clean
	rm -rf $(EXEC)
