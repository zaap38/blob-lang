bits 64
default rel
global _start

_start:
jmp main
main:
push rbp        ;; load space for local var
mov rbp, rsp
sub rsp, 8
sub rbp, 8        ;; loading string 'foo' on stack
mov rsp, rbp
sub rsp, 16
mov [rbp], 3        ;; string size
mov [rbp-6], 'o'
mov [rbp-7], 'o'
mov [rbp-8], 'f'
mov rax, rbp
mov rbx, rax        ;; init with value
mov r8, rbx
mov rax, 1        ;; syscall: write
mov rdi, 1        ;; std out
mov rdx, [r8]        ;; length of the string
sub r8, 8
mov rsi, r8        ;; address of the string
syscall
mov rax, 1