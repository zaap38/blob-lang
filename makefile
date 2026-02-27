NASM=/mnt/c/Users/Benoît/AppData/Local/bin/NASM/nasm.exe
PYTH=/mnt/c/Users/Benoît/AppData/Local/Programs/Python/Python310/python.exe

# Default target
all: output.exe

# output.exe depends on output.asm
output.exe: output.asm
	$(NASM) -f elf64 output.asm -o output.o
	ld output.o -o output.exe
	@echo "\033[32m=====RUN=====\033[0m"
	./output.exe
	@echo ""

# Generate output.asm by compiling a source file passed as SRC=
output.asm:
	$(PYTH) ./compiler.py $(SRC)

clean:
	rm -f output.o output.exe output.asm