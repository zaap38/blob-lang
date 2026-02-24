bits 64
default rel
global _start

_start:
jmp main
main:
push rbp        ;; load space for local var
mov rbp, rsp
sub rsp, 16
mov rbx, 2        ;; init with value
add rbx, 1
mov rcx, rbx        ;; init with value