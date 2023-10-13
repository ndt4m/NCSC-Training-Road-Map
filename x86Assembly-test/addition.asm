
extern print_string, read_unsigned_int, print_unsigned_int, allocateMemory, getInteger, print_long_unsigned


section .data
    upper_bound_arr     dd 1000                                                      ; The highest size of the array
    lower_bound_arr     dd 1                                                         ; The lowest size of the array
    arr_size_msg	    db "Enter the size of array: ", 0                            
    resutl_msg          db "The sum is: ", 0                                         
    arr_size_bound      db "[+] Please enter a number between 1 and 1000!!!", 0xa, 0
    newline             db 0xa, 0                                                    ; Newline character
    sum                 dq 0                                                         ; The sum of the array                 
    overflow_msg        db "The sum is overflow", 0xa, 0                             ; The message appears as the sum is overflow


section .bss
    arr_size        resd 1                                                           ; The array size
    mem_addr_arr    resd 1                                                           ; The pointer to the array


section .text
    global addition


;   FUNCTION: addition
;   Takes 0 parameter
;   Return: eax = 0 (successfull) or eax = 1 (overflow) 
addition:
    enter   0, 0                         ; Save EBP, reserve 0 bytes for local variables
    pusha                                ; Save all registers

get_arr_size:                            

    mov     eax, arr_size_bound          ; eax = address of arr_size_bound
    call    print_string                 ; Print array size bound message

    mov     eax, arr_size_msg            ; eax = address of arr_size_msg
    call    print_string                 ; Print the message that asks user to enter array size

    call    read_unsigned_int            ; Get an unsigned int from the keyboard and store in eax
    
    cmp     eax, [upper_bound_arr]       ; Check if the value in eax is greater than 1000
    jg      get_arr_size                 ; Jump if greater to ask user enter again
    cmp     eax, [lower_bound_arr]       ; Check if the value in eax is less than 1
    jl      get_arr_size                 ; Jump if less to ask user enter again

    mov     [arr_size], eax              ; Save the array size in arr_size variable

    push    eax                          ; Put the array size on the stack (#parameter 1) 
    call    allocateMemory               ; Call allocateMemory function to reserve memory
    mov     [mem_addr_arr], eax          ; Save the address of the array in mem_addr_arr variable
    add     esp, 4                       ; Remove parameter of allocateMemory from the stack

    mov     ebx, [mem_addr_arr]          ; ebx = address of the array
    push    ebx                          ; Put the address of the array on the stack (parameter #2)
    mov     ebx, [arr_size]              ; ebx = array size
    push    ebx                          ; Put array size on the stack (parameter #1)
    call    getInteger                   ; Call the getInteger function to fill out the array
    add     esp, 8                       ; Remove 2 parameters of getInteger from the stack

    mov     ebp, [mem_addr_arr]          ; ebp = address of the array
    mov     ebx, [arr_size]              ; ebx = array size
    shl     ebx, 2                       ; ebx = ebx * 4
    add     ebx, ebp                     ; ebx = ebx + ebp = address after the last address of the array
   
loop_sum:
    mov     edx, [ebp]                   ; edx = an integer in array
    add     dword [sum], edx             ; add the lowest 32 bit of sum to edx
    adc     dword [sum+4], 0             ; if the lowest 32 bit is overflow the add the highest 32 bit of sum with the CF flag register
    jc      overflow                     ; if the highest 32 bit is also overflow, the sum is overflow then jump to overflow label

    add     ebp, 4                       ; move ebp point to the next integer
    cmp     ebp, ebx                     ; Check if this the last integer
    jb      loop_sum                     ; jump if ebp < address after the last address of the array 

    mov     eax, resutl_msg              ; eax = address of result_msg
    call    print_string                 ; call print_string

    mov     eax, [sum]                   ; eax = lower 32-bit of sum
    mov     edx, [sum+4]                 ; edx = higher 32-bit of sum
    call    print_long_unsigned          ; call print_long_unsigned

    mov     eax, newline                 ; eax = address of newline
    call    print_string                 ; call print_string

    popa				                 ; Restore all registers
	mov	    eax, 0		                 ; Set the return value to 0
	leave				                 ; Restore EBP, remove space for local variables
	ret	                                 ; Pop the return address and jump to it
overflow:
    mov     eax, overflow_msg            ; eax = address of overflow_msg
    call    print_string                 ; call print_string 
    popa				                 ; Restore all registers
	mov	    eax, 1		                 ; Set the return value to 1
	leave			                     ; Restore EBP, remove space for local variables
	ret	                                 ; Pop the return address and jump to it