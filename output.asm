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
	;; init string: NUM(66)
	mov rax, 66
	;; int_to_string
	push rbx
	push rcx
	push rdx
	push r8
	push r9
	push r10
	mov rdx, rax
	mov r8, rdx
	mov rcx, 100000000
	push rax
	push rdx
	mov rax, r8
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov r8, rax
	mov rcx, rdx
	pop rdx
	pop rax
	add r8, 1
	mov rcx, 8
	push rax
	push rdx
	mov rax, r8
	xor rdx, rdx
	mul rcx
	mov r8, rax
	pop rdx
	pop rax
	add r8, 8
	mov rax, r8
	pop r10
	pop r9
	pop r8
	pop rdx
	pop rcx
	pop rbx
	sub rsp, rax        ;; reserve space
	mov r10, rsp
	push rbx
	push rcx
	push rdx
	push r8
	push r9
	push r10
	mov r8, rax
	mov r9, 0
	mov rbx, rax
label_1:
	mov rcx, 10
	push rax
	push rdx
	mov rax, rbx
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov rbx, rax
	mov rcx, rdx
	pop rdx
	pop rax
	add rcx, 48        ;; convert to char digit
	mov [r10+r9], rcx
	inc r9
	cmp rbx, 0
	jne label_1
	mov rax, r10
	add rax, r8
	sub rax, 8
	mov [rax], r9
	pop r10
	pop r9
	pop r8
	pop rdx
	pop rcx
	pop rbx
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