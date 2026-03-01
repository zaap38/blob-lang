bits 64
default rel
global _start
	
_start:
	call main
	jmp exit
main:
	;; declaring function main
	mov rbp, rsp
	mov rcx, 1        ;; init with value
	mov rdx, 1        ;; init with value
	;; init string: VAR(a)
	;; int_to_string()
	push rcx
	mov r8, rcx
	mov rcx, 100000000
	push rcx
	;; log_n(r8, rcx)
	mov rax, 0
label_1:
	inc rax
	push rcx
	push rax
	mov rax, r8
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov r8, rax
	mov rcx, rdx
	pop rax
	pop rcx
	cmp r8, 0
	jne label_1
	mov r8, rax
	pop rcx
	sub r8, 1
	mov rax, rcx
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov rcx, rax
	mov rcx, rdx
	mov r9, 10
	;; log_n(rcx, r9)
	mov rax, 0
label_2:
	inc rax
	push r9
	push rax
	mov rax, rcx
	xor rdx, rdx
	cmp r9, 0        ;; check division by zero
	je exit
	div r9
	mov rcx, rax
	mov r9, rdx
	pop rax
	pop r9
	cmp rcx, 0
	jne label_2
	mov rcx, rax
	mov rdx, rcx
	add rdx, r8
	sub rdx, 1
	add r8, 1
	mov rcx, 8
	push rdx
	mov rax, r8
	xor rdx, rdx
	mul rcx
	mov r8, rax
	pop rdx
	add r8, 8
	pop rax
	mov rcx, rax
	sub rsp, r8        ;; reserve space
	mov r10, rsp
	mov r9, 0
	mov r11, rax
label_3:
	mov rcx, 10
	push rcx
	push rax
	push rdx
	mov rax, r11
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov r11, rax
	mov rcx, rdx
	pop rdx
	pop rax
	pop rcx
	add rcx, 48        ;; convert to char digit
	push r11
	mov r11, rdx
	sub r11, r9
	mov [r10+r11], cl
	inc r9
	pop r11
	cmp r11, 0
	jne label_3
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
	;; init string: VAR(a)
	;; int_to_string()
	push rcx
	mov r8, rcx
	mov rcx, 100000000
	push rcx
	;; log_n(r8, rcx)
	mov rax, 0
label_4:
	inc rax
	push rcx
	push rax
	mov rax, r8
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov r8, rax
	mov rcx, rdx
	pop rax
	pop rcx
	cmp r8, 0
	jne label_4
	mov r8, rax
	pop rcx
	sub r8, 1
	mov rax, rcx
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov rcx, rax
	mov rcx, rdx
	mov r9, 10
	;; log_n(rcx, r9)
	mov rax, 0
label_5:
	inc rax
	push r9
	push rax
	mov rax, rcx
	xor rdx, rdx
	cmp r9, 0        ;; check division by zero
	je exit
	div r9
	mov rcx, rax
	mov r9, rdx
	pop rax
	pop r9
	cmp rcx, 0
	jne label_5
	mov rcx, rax
	mov rdx, rcx
	add rdx, r8
	sub rdx, 1
	add r8, 1
	mov rcx, 8
	push rdx
	mov rax, r8
	xor rdx, rdx
	mul rcx
	mov r8, rax
	pop rdx
	add r8, 8
	pop rax
	mov rcx, rax
	sub rsp, r8        ;; reserve space
	mov r10, rsp
	mov r9, 0
	mov r11, rax
label_6:
	mov rcx, 10
	push rcx
	push rax
	push rdx
	mov rax, r11
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov r11, rax
	mov rcx, rdx
	pop rdx
	pop rax
	pop rcx
	add rcx, 48        ;; convert to char digit
	push r11
	mov r11, rdx
	sub r11, r9
	mov [r10+r11], cl
	inc r9
	pop r11
	cmp r11, 0
	jne label_6
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
	;; binop '+'
	add rcx, rdx
	mov rbx, rcx        ;; init with value
	;; init string: VAR(a)
	;; int_to_string()
	push rcx
	mov r8, rcx
	mov rcx, 100000000
	push rcx
	;; log_n(r8, rcx)
	mov rax, 0
label_7:
	inc rax
	push rcx
	push rax
	mov rax, r8
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov r8, rax
	mov rcx, rdx
	pop rax
	pop rcx
	cmp r8, 0
	jne label_7
	mov r8, rax
	pop rcx
	sub r8, 1
	mov rax, rcx
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov rcx, rax
	mov rcx, rdx
	mov r9, 10
	;; log_n(rcx, r9)
	mov rax, 0
label_8:
	inc rax
	push r9
	push rax
	mov rax, rcx
	xor rdx, rdx
	cmp r9, 0        ;; check division by zero
	je exit
	div r9
	mov rcx, rax
	mov r9, rdx
	pop rax
	pop r9
	cmp rcx, 0
	jne label_8
	mov rcx, rax
	mov rdx, rcx
	add rdx, r8
	sub rdx, 1
	add r8, 1
	mov rcx, 8
	push rdx
	mov rax, r8
	xor rdx, rdx
	mul rcx
	mov r8, rax
	pop rdx
	add r8, 8
	pop rax
	mov rcx, rax
	sub rsp, r8        ;; reserve space
	mov r10, rsp
	mov r9, 0
	mov r11, rax
label_9:
	mov rcx, 10
	push rcx
	push rax
	push rdx
	mov rax, r11
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov r11, rax
	mov rcx, rdx
	pop rdx
	pop rax
	pop rcx
	add rcx, 48        ;; convert to char digit
	push r11
	mov r11, rdx
	sub r11, r9
	mov [r10+r11], cl
	inc r9
	pop r11
	cmp r11, 0
	jne label_9
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
	;; init string: VAR(c)
	;; int_to_string()
	push rbx
	mov r8, rbx
	mov rcx, 100000000
	;; log_n(r8, rcx)
	mov rax, 0
label_10:
	inc rax
	push rcx
	push rax
	mov rax, r8
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov r8, rax
	mov rcx, rdx
	pop rax
	pop rcx
	cmp r8, 0
	jne label_10
	mov r8, rax
	sub r8, 1
	mov rax, rbx
	xor rdx, rdx
	cmp rcx, 0        ;; check division by zero
	je exit
	div rcx
	mov rbx, rax
	mov rcx, rdx
	mov r9, 10
	;; log_n(rcx, r9)
	mov rax, 0
label_11:
	inc rax
	push r9
	push rax
	mov rax, rcx
	xor rdx, rdx
	cmp r9, 0        ;; check division by zero
	je exit
	div r9
	mov rcx, rax
	mov r9, rdx
	pop rax
	pop r9
	cmp rcx, 0
	jne label_11
	mov rcx, rax
	mov rdx, rcx
	add rdx, r8
	sub rdx, 1
	add r8, 1
	mov rcx, 8
	push rdx
	mov rax, r8
	xor rdx, rdx
	mul rcx
	mov r8, rax
	pop rdx
	add r8, 8
	pop rax
	mov rbx, rax
	sub rsp, r8        ;; reserve space
	mov r10, rsp
	mov r9, 0
	mov r11, rax
label_12:
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
	pop rdx
	pop rax
	add rcx, 48        ;; convert to char digit
	push r11
	mov r11, rdx
	sub r11, r9
	mov [r10+r11], cl
	inc r9
	pop r11
	cmp r11, 0
	jne label_12
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