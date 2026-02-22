; example 1 - this is a comment
int doStuff(int a, int b) {
    a = a + 1
    return a + b, 0
}

void main(string argv, int argc) { ; this is the program entry point

    int a = 5
    int b
    float c = 2.5
    b = doStuff(a * 3, 0)
    a++
    --b
    if a > b {
        for i = 0, 10, i = i + 1 {
            print("Sum of i and a:", doStuff(i, c))
        }
    } else {
        array<array<float>> myTab; nested array
        myTab[1][a * 2]
    }
}