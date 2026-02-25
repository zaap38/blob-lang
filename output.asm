bits 64
default rel
global _start

_start:
jmp main
main:
push rbp        ;; load space for local var
mov rbp, rsp
sub rsp, 32
mov rbx, 2        ;; init with value
mov rcx, None        ;; init with value
mov xmm0, rbx        ;; init with value
add rbx, 1
mov rcx, rbx        ;; init with value