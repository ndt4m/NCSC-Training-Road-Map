#!/bin/bash

# Assemble the assembly files
nasm -f elf32 -g addition.asm -o addition.o
nasm -f elf32 -g getInteger.asm -o getInteger.o
nasm -f elf32 -g io.asm -o io.o
nasm -f elf32 -g allocateMemory.asm -o allocateMemory.o

# Compile the C code
gcc -m32 -g -c driver.c -o driver.o

# Link everything together
gcc -m32 -g addition.o getInteger.o io.o allocateMemory.o driver.o -o addition

# Clean up object files
rm addition.o getInteger.o io.o allocateMemory.o driver.o