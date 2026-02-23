; example 1 - this is a comment
int do_stuff(int a, int b) {
    a = a + 1
    return a + b
}

int, float multi_arg(int a, int b) {
    return a * b, .3
}

void print(string text) {
    ; not implemented
}

string str(int value) {
    return "not-implemented"
}

void main(string argv, int argc) { ; this is the program entry point

    int a = 5
    int b
    int c = 2
    b = do_stuff(a * 3, 0)
    a++
    --b
    if a > b {
        for i = 0, 10, i = i + 1 {
            print("Sum of i and a:" + str(do_stuff(i, c)))
        }
    } else {
        array<array<float>> my_tab; nested array
        my_tab[1][a // 2]
    }
}