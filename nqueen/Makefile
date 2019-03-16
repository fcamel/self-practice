.PHONY: all bit

all: nqueen nqueen_with_cut nqueen_stack
bit: nqueen_bit nqueen_lsb

%: %.cpp
	g++ -O2 $< -o $@

