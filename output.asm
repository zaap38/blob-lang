bits 64
default rel
global _start

_start:
jmp main
main:
push rbp        ;; load space for local var
mov rbp, rsp
sub rsp, 8
sub rbp, 8        ;; loading string 'fooSuperLong string' on stack
mov rsp, rbp
sub rsp, 32
mov [rbp], 19        ;; string size
mov [rbp-6], 'g'
mov [rbp-7], 'n'
mov [rbp-8], 'i'
mov [rbp-9], 'r'
mov [rbp-10], 't'
mov [rbp-11], 's'
mov [rbp-12], ' '
mov [rbp-13], 'g'
mov [rbp-14], 'n'
mov [rbp-15], 'o'
mov [rbp-16], 'L'
mov [rbp-17], 'r'
mov [rbp-18], 'e'
mov [rbp-19], 'p'
mov [rbp-20], 'u'
mov [rbp-21], 'S'
mov [rbp-22], 'o'
mov [rbp-23], 'o'
mov [rbp-24], 'f'
mov rax, rbp
mov rbx, rax        ;; init with value
mov r8, rbx
mov rax, 1        ;; syscall: write
mov rdi, 1        ;; std out
mov rdx, [r8]        ;; length of the string
sub r8, 8
mov rsi, r8        ;; address of the string
syscall
mov rax, 60
xor rdi, rdi
syscall