global _start
section .data
otherVar dq 0
resultVar dq 0
myVariable dq 0
buffer times 20 db 0
nl db 10
section .text
_start:
    mov rax, 3
    mov [myVariable], rax
    mov rax, 4
    mov [otherVar], rax
    mov rax, [myVariable]
    push rax
    mov rax, [otherVar]
    pop rbx
    add rax, rbx
    mov [resultVar], rax
    mov rax, [resultVar]
    mov rbx, buffer
    call int_to_string
    mov rdx, r10
    mov rsi, rbx
    mov rax, 1
    mov rdi, 1
    syscall
    mov rax, 1
    mov rdi, 1
    lea rsi, [rel nl]
    mov rdx, 1
    syscall
    mov rax, 60
    xor rdi, rdi
    syscall

; Convert integer in rax to string at rbx
; Result length in r10
int_to_string:
    mov rcx, 10
    mov r11, rbx
    add r11, 19
    mov r10, 0
.convert_loop:
    xor rdx, rdx
    div rcx
    add dl, '0'
    dec r11
    mov [r11], dl
    inc r10
    test rax, rax
    jnz .convert_loop
    mov rbx, r11
    ret
