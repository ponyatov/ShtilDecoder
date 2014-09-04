CC = mingw32-gcc
CXX = mingw32-g++
STRICT = -Wall -Wextra -Werror -ansi -pedantic
OPT = -Os -march=i486 -mtune=i686
CFLAGS = $(STRICT) $(OPT)

all: decoder.exe 

decoder.exe: decoder.cpp
	$(CXX) $(CFLAGS) -o $@ $<
