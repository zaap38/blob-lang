bits 64
default rel
global _start
	
_start:
	call main
	jmp exit
main:
	;; declaring function main
	mov rbp, rsp
	;; init string: NUM(123)
	mov rax, 123
	;; int_to_string()
	push rax
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
	add r8, 1
	mov rcx, 8
	push rax
	push rcx
	push rdx
	mov rax, r8
	xor rdx, rdx
	mul rcx
	mov r8, rax
	pop rax
	pop rcx
	pop rdx
	add r8, 8
	pop rax
	sub rsp, r8        ;; reserve space
	mov r10, rsp
	mov r9, 0
	mov r11, rax
label_1:
	mov rcx, 10
	push rax
	push rdx
	mov rax, r11
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov r11, rax
	mov rcx, rdx
	pop rax
	pop rdx
	add rcx, 48        ;; convert to char digit
	mov [r10+r9], rcx
	inc r9
	cmp r11, 0
	jne label_1
	mov rax, r10
	add rax, r8
	sub rax, 8
	mov [rax], r9
	mov r8, [rax]        ;; load len in r8
	mov r9, 8
	push rax
	push rdx
	mov rax, r8
	xor rdx, rdx
	cmp r9, 0        ;; check division by zero
	je exit
	div r9        ;; len // 8
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
	;; init string: STR(abcdefghij)
	sub rsp, 24
	mov [rbp-8], 10        ;; string size
	mov [rbp-15], 'j'
	mov [rbp-16], 'i'
	mov [rbp-17], 'h'
	mov [rbp-18], 'g'
	mov [rbp-19], 'f'
	mov [rbp-20], 'e'
	mov [rbp-21], 'd'
	mov [rbp-22], 'c'
	mov [rbp-23], 'b'
	mov [rbp-24], 'a'
	mov rax, rbp
	sub rax, 8
	mov r8, [rax]        ;; load len in r8
	mov r9, 8
	push rax
	push rdx
	mov rax, r8
	xor rdx, rdx
	cmp r9, 0        ;; check division by zero
	je exit
	div r9        ;; len // 8
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
	;; init string: STR(my_string_to_print)
	sub rsp, 32
	mov [rbp-8], 18        ;; string size
	mov [rbp-15], 't'
	mov [rbp-16], 'n'
	mov [rbp-17], 'i'
	mov [rbp-18], 'r'
	mov [rbp-19], 'p'
	mov [rbp-20], '_'
	mov [rbp-21], 'o'
	mov [rbp-22], 't'
	mov [rbp-23], '_'
	mov [rbp-24], 'g'
	mov [rbp-25], 'n'
	mov [rbp-26], 'i'
	mov [rbp-27], 'r'
	mov [rbp-28], 't'
	mov [rbp-29], 's'
	mov [rbp-30], '_'
	mov [rbp-31], 'y'
	mov [rbp-32], 'm'
	mov rax, rbp
	sub rax, 8
	mov rbx, rax        ;; init with value
	mov r8, [rbx]        ;; load len in r8
	mov r9, 8
	push rax
	push rdx
	mov rax, r8
	xor rdx, rdx
	cmp r9, 0        ;; check division by zero
	je exit
	div r9        ;; len // 8
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
	mov r9, rbx
	mov rax, 1        ;; syscall: write
	mov rdi, 1        ;; std out
	mov rdx, [r9]        ;; length of the string
	sub r9, r8
	mov rsi, r9        ;; address of the string
	syscall
	mov rbx, 123        ;; init with value
	;; init string: VAR(b)
	mov rax, rbx
	;; int_to_string()
	push rax
	mov rdx, rbx
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
	add r8, 1
	mov rcx, 8
	push rax
	push rcx
	push rdx
	mov rax, r8
	xor rdx, rdx
	mul rcx
	mov r8, rax
	pop rax
	pop rcx
	pop rdx
	add r8, 8
	pop rax
	sub rsp, r8        ;; reserve space
	mov r10, rsp
	mov r9, 0
	mov r11, rax
label_2:
	mov rcx, 10
	push rax
	push rdx
	mov rax, r11
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov r11, rax
	mov rcx, rdx
	pop rax
	pop rdx
	add rcx, 48        ;; convert to char digit
	mov [r10+r9], rcx
	inc r9
	cmp r11, 0
	jne label_2
	mov rax, r10
	add rax, r8
	sub rax, 8
	mov [rax], r9
	mov r8, [rax]        ;; load len in r8
	mov r9, 8
	push rax
	push rdx
	mov rax, r8
	xor rdx, rdx
	cmp r9, 0        ;; check division by zero
	je exit
	div r9        ;; len // 8
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