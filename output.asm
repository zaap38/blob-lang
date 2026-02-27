bits 64
default rel
global _start
	
_start:
	jmp main
main:
	;;declaring function main
	push rbp        ;; load space for local var
	mov rbp, rsp
	mov rsp, rbp
	sub rsp, 16
	mov [rbp], 9        ;; string size
	mov [rbp-8], '9'
	mov [rbp-9], '8'
	mov [rbp-10], '7'
	mov [rbp-11], '6'
	mov [rbp-12], '5'
	mov [rbp-13], '4'
	mov [rbp-14], '3'
	mov [rbp-15], '2'
	mov [rbp-16], '1'
	mov rax, rbp
	mov rbx, rax        ;; init with value
	mov r9, 8
	mov r8, [rbx]
	push rax
	push rbx
	push rdx
	mov rax, r8
	mov rbx, r9
	mov bh, 0
	cmp rbx, 0        ;; check division by zero
	je exit
	xor rdx, rdx
	div rbx
	mov ah, 0
	mov r8, rax
	pop rax
	pop rbx
	pop rdx
	inc r8
	mov r10, 8
	push rax
	push rdx
	mov rax, r8
	xor rdx, rdx
	mul r10
	mov r8, rax
	pop rax
	pop rdx
	mov r9, rbx
	mov rax, 1        ;; syscall: write
	mov rdi, 1        ;; std out
	mov rdx, [r9]        ;; length of the string
	sub r9, r8
	mov rsi, r9        ;; address of the string
	syscall
exit:
	mov rax, 60
	xor rdi, rdi
	syscall