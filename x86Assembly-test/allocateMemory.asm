
extern print_string
section .data
    error_msg   db "failed to allocate memory", 0xa, 0


section .text
    global allocateMemory

;   Function: allocateMemory
;   Takes 1 parameter: the number of 32-bit integers need to reserve memory
;   Return eax = Address of the first integers
allocateMemory:
    enter   4, 0                                ; Save EBP, reserve 4 bytes for local variables
    pusha                                       ; Save all registers
    pushf                                       ; Save all flag registers

    mov     eax, 45                             ; System call number (sys_brk)
    xor     ebx, ebx                            ; ebx = 0 (to request current end of the data segment)
    int     0x80                                ; Call the kernel to get the current end of data segment, and store the value in eax

    mov     edx, [ebp+8]                        ; edx = array size (parameter #1)
    shl     edx, 2                              ; edx = edx * 4 = the number of bytes need to reserve
    add     eax, edx                            ; eax = the current end of data segment + the number of bytes need to reserve = the new end of data segment
    mov     ebx, eax                            ; ebx = the new end of data segment
    mov     eax, 45                             ; System call number (sys_brk)
    int     0x80                                ; Call the kernel to set the new end of the data segment, and store the address to eax

    cmp     eax, 0                              ; Check if the allocation is success
    jl      fail                                ; Jump if eax < 0

    mov     dword [ebp-4], eax                  ; Save the new address to stack
    popf                                        ; Restore all flag registers
    popa                                        ; Restore all registers     
    mov     eax, dword [ebp-4]                  ; eax = new address
    leave                                       ; Restore EBP, remove space for local variables
    ret                                         ; Pop the return address and jump to it

fail:
    mov     eax, error_msg                      ; eax = address of error_msg
    call    print_string
    
    mov     eax, 1                              ; System call number (sys_exit)
    xor     ebx, ebx                            ; Exit status 0 - successful exit
    int     0x80                                ; Call the kernel to exit the program
