bits 64
default rel
global _start
	
_start:
	call main
	jmp exit
main:
	;; declaring function main
	mov rbp, rsp
	;; init string: STR(test_string)
	sub rsp, 24
	mov [rbp-8], 11        ;; string size
	mov [rbp-14], 'g'
	mov [rbp-15], 'n'
	mov [rbp-16], 'i'
	mov [rbp-17], 'r'
	mov [rbp-18], 't'
	mov [rbp-19], 's'
	mov [rbp-20], '_'
	mov [rbp-21], 't'
	mov [rbp-22], 's'
	mov [rbp-23], 'e'
	mov [rbp-24], 't'
	mov rax, rbp
	sub rax, 8
	mov rbx, rax        ;; init with value
	mov r9, 8
	mov r8, [rbx]
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
	pop rax
	pop rdx
	mov r9, rbx
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