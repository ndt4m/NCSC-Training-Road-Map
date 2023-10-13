segment .data
    unsigned_int_format 	db "%u", 0
	long_unsigned_format 	db "%llu", 0
	string_format 			db "%s", 0
	input_error 			db "Please just enter number: ", 0


segment .text
    global read_unsigned_int, print_unsigned_int, print_string, print_long_unsigned, read_char
    extern scanf, printf, getchar

;	FUNCTION: read_unsigned_int
;	Takes 0 parameters
;	Return: eax = a 32-bit integer from user
read_unsigned_int:
	enter	4,0									; Save EBP, reserve 4 bytes for local variables
	pusha										; Save all registers
	pushf										; Save all flag registers

start:
	lea		ebx, [ebp-4]						; ebx = ebp - 4 = address in which store the 32-bit integer from user
	push	ebx									; Put ebx on the stack (parameter #2)
	push	dword unsigned_int_format			; Put format on the stack (parameter #1)
	call	scanf								; Call scanf function in Standard C lib
	add 	esp, 8								; Remove 2 parameters of scanf from the stack
	
	cmp 	eax, 0								; If user enter numberic character (0-9) eax = 1; else eax = 0
	jz 		clear_stdin							; Jump if eax = 0 <=> non-numeric characters from user
	
	popf										; Restore all flag registers
	popa										; Restore all registers
	mov		eax, [ebp-4]						; Return eax = a 32-bit integer from user 
	leave										; Restore EBP, remove space for local variables
	ret											; Pop the return address and jump to it
clear_stdin:
	call 	read_char							; read an ASCII character from stdin
	cmp 	eax, 0xa							; Check if sdtin is clear
	jnz 	clear_stdin							; Jump if eax != 0xa <=> stdin isn't clear
	
	mov 	eax, input_error					; eax = address of input_error
	call 	print_string						
	jmp 	start								; Restart the task to ask user enter an 32-bit integer



;	FUNCTION: read_char
;	Takes 0 parameter
;	Return: eax = the 
read_char:
	enter	4,0									; Save EBP, reserve 4 bytes for local variables
	pusha										; Save all registers
	pushf										; Save all flag registers

	call	getchar								; Call getchar fuction in Standard C lib, return resutl in eax
	mov		[ebp-4], eax						; Save result on the stack

	popf										; Restore all flag registers
	popa										; Restore all registers
	mov		eax, [ebp-4]						; eax = character stored in ebp - 4
	leave										; Restore EBP, remove space for local variables
	ret											; Pop the return address and jump to it



;	FUNCTION: print_unsigned_int
;	Takes 1 parameter: eax = the 32-bit unsigned integer need to print
;	Return: void
print_unsigned_int:
    enter   0, 0								; Save EBP, reserve 0 bytes for local variables
    pusha										; Save all registers
    pushf										; Save all flag registers

    push    eax									; Put the eax = the 32-bit unsigned integer need to print on the stack (parameter #2)
    push    dword unsigned_int_format			; Put format on the stack (Parameter #1)
    call    printf								; Call printf function in Standard C lib
    add 	esp, 8								; Remove 2 parameters of printf from the stack

    popf										; Restore all flag registers
    popa										; Restore all registers
    leave										; Restore EBP, remove space for local variables
    ret											; Pop the return address and jump to it



;	FUNCTION: print_string
; 	Takes 1 parameter: eax = address of the null terminated string need to print
; 	Return: void
print_string:
	enter	0,0									; Save EBP, reserve 0 bytes for local variables
	pusha										; Save all registers
	pushf										; Save all flag registers

	push	eax									; Put the eax = address of the string need to print on the stack (parameter #2)
	push    dword string_format					; Put format on the stack (parameter #1)
	call	printf								; Call printf function in Standard C lib
	add 	esp, 8								; Remove 2 parameters of printf from the stack

	popf										; Restore all flag registers
	popa										; Restore all registers
	leave										; Restore EBP, remove space for local variables
	ret											; Pop the return address and jump to it



;	FUNCTION: print_long_unsigned
;	Takes 2 parameter: eax = the lower 32 bits of the 64-bit number, edx = the higher 32 bits of the 64-bit number
; 	Return: void
print_long_unsigned:
	enter 	0, 0								; Save EBP, reserve 0 bytes for local variables
	pusha										; Save all registers
	pushf										; Save all flag registers

	push 	edx									; Put the edx = the higher 32 bits of the 64-bit number on the stack (parameter #3)
	push 	eax									; Put the eax = the lower 32 bits of the 64-bit number on the stack (parameter #2)
	push 	dword long_unsigned_format			; Put format on the stack (parameter #1)
	call 	printf								; Call printf function in Standard C lib
	add 	esp, 12								; Remove 3 parameters of printf from the stack

	popf										; Restore all flag registers
	popa										; Restore all registers
	leave										; Restore EBP, remove space for local variables
	ret											; Pop the return address and jump to it





