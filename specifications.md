## This files details the specifications of the blobfish language

# File naming

Blobfish source files end with `.bf`

> myFile.bf

# Program skeleton and variable scope

Blobfish source require at least a main function that is the entry point of the program.

```
void main() {
    [code here]
}
```

Variables are typed. The generic types are:
- int
- float
- bool
- string
- array

There is a way to define a variable as a container using `var` as a type. This can only be used as a function parameter. It comes with the primitive `.type()` that returns its true type.

The scope of the variable is defined with the braces `{}`. It can also be done at declaration time.

```
void main() {
    int *a
    int *b, *c {
        [code here]
    }
    ; variable 'a' is defined here, but not 'b' and 'c'
}
```

Variables cannot be defined outside of a function. Hence there cannot be global variables.

All variables are constants by default. To enable mutation on a variable, you need to use the star `*` to define a variable as mutable.

```
int a; this is a constant
int *b; this is a variable
```

Variable affectation is by default a reference copy, not a value copy. To affect a variable by copy, you need to use `*` before it. For example:
```
int a = 3
int b = a
b = 4; this line will not compile as 'a' and 'b' are constants
-------------------
int a = 3
int *b = a; this line will not compile as 'a' is a constant but not 'b'
-------------------
int *a = 3
int b = a; this is possible. The value of 'a' can be changed through direct modifications to 'a', but not through the variable 'b'
-------------------
int a = 3
int b = a
int *c = *b; the value of 'c' is 3
c = 5; the value of 'a' and 'b' is still 3
-------------------
int *a = 3
int *b = a
b = 5; the value of 'a' is now 5
```

# Loops

In blobfish, there exist only `for` loops. This comes in four variants:

```
; value loop
for i = 0 to 10 {}; 'i' can only be an integer

; range loop
for v in array {}
for k, v in array {}

; condition loop (while)
for *c > t { ; 'c' is mutable but not 't'
    c = foo()
}

; do-for
do for *c > t {
    ; this is executed before checking for the exit condition
}
```