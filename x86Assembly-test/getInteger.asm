
extern print_string, read_unsigned_int, read_char, print_unsigned_int

segment .data
    msg1    db "Enter ", 0
    msg2    db " integers: ", 0
    note1   db "[*] Note 1: If you enter a number greater than 4294967295, the program will automatically turn it to 4294967295", 0xa, 0
    note2   db "[*] Note 2: If you enter a non-numeric character, the program will only take the previous valid number and ask you to enter again the rest", 0xa, 0
    note3   db "[*] Note 3: If you enter a negative number, the program will convert that negative number to a positive number by formular (positive number = 4294967296 + negative number)", 0xa, 0


segment .text
    global getInteger

;   FUNCTION: getInterger
;   Takes 2 parameters: an address in memory in which integers are stored, and the number of integers
;   Return: void
getInteger:
    enter   0, 0                     ; Save EBP, reserve 0 bytes for local variables
    pusha                            ; Save all registers
    pushf                            ; Save all flag registers

    mov     ecx, [ebp+12]            ; ecx = address of the array (parameter #2)
    mov     ebx, [ebp+8]             ; ebx = array size (parameter #1)
    mov     edx, ebx                 ; edx = array size
    shl     ebx, 2                   ; ebx = ebx * 4
    add     ebx, ecx                 ; ebx = ebx + ecx = address after the last byte address of array

    mov     eax, note1               ; eax = address of note1
    call    print_string             
    mov     eax, note2               ; eax = address of note2
    call    print_string
    mov     eax, note3               ; eax = address of note3
    call    print_string
    mov     eax, msg1                ; eax = address of msg1
    call    print_string
    mov     eax, edx                 ; eax = array size
    call    print_unsigned_int
    mov     eax, msg2                ; eax = address of msg2
    call    print_string

loop_int:
    call    read_unsigned_int       ; Get an integer from keyboard and store in eax

    mov     [ecx], eax              ; Store the integer in memory at correct address
    add     ecx, 4                  ; Move to the next address
    cmp     ecx, ebx                ; Check if this is the last address
    jb      loop_int                ; Jump if exc < ebx

    popf                            ; Restore all flag registers
    popa                            ; Restore all registers
    leave                           ; Restore EBP, remove space for local variables
    ret                             ; Pop the return address and jump to it

