bits 64
default rel
global _start
	
_start:
	call main
	jmp exit
main:
	;; declaring function main
	mov rbp, rsp
	mov r9, 8
	;; init string: STR(test)
	sub rsp, 16
	mov [rbp-8], 4        ;; string size
	mov [rbp-13], 't'
	mov [rbp-14], 's'
	mov [rbp-15], 'e'
	mov [rbp-16], 't'
	mov rax, rbp
	sub rax, 8
	mov r8, [rax]
	push rax
	push rdx
	mov rax, r8
	xor rdx, rdx
	cmp r9, 0        ;; check division by zero
	je exit
	div r9
	mov r8, rax
	mov r9, rdx
	pop rdx
	pop rax
	inc r8
	mov r10, 8
	push rax
	push rdx
	mov rax, r8
	xor rdx, rdx
	mul r10
	mov r8, rax
	pop rdx
	pop rax
	mov r9, rax
	mov rax, 1        ;; syscall: write
	mov rdi, 1        ;; std out
	mov rdx, [r9]        ;; length of the string
	sub r9, r8
	mov rsi, r9        ;; address of the string
	syscall
	mov rsp, rbp        ;; free stack memory
	ret
exit:
	mov rax, 60
	xor rdi, rdi
	syscall