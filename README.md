# Blob-lang

Compiler for blob-lang (.bf). This is not done as a professional project, but rather as a hobby to learn about compilers.

This is still a Work-In-Progress!

## Compiling

If you wish to try it, use the makefile to compile and run your .bf file.

NOTE: It requires `python3` and `nasm` to work. Edit the makefile and replace the following lines with your actual executable locations:

```sh
NASM=/mnt/c/Users/Benoît/AppData/Local/bin/NASM/nasm.exe
PYTH=/mnt/c/Users/Benoît/AppData/Local/Programs/Python/Python310/python.exe
```

Then run the following:

```sh
# this will compile the .bf file to a binary and run it
# it will not compile if the output already exists
# in such case, use 'make clean'
make SRC=my/file/location.bf
```

## The language

The philosophy of the language is to keep the low-level aspect of C/C++ while adding functionnalities inspired by other languages that make it convenient to write code fast or to avoid bugs.

## Contributing

At this stage, the repository is not open to contributions. Maybe it will be once the language reaches a more advanced state.