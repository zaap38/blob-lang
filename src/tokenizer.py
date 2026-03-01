from src.const_names import *
import string


def tokenizer(lines):

    codes = []
    line_no = 0

    for line in lines:
        line_no += 1
        if line == "\n":
            continue
        # print("Line:", line[:-1])
        index = 0
        while index < len(line):
            c = line[index]
            word = ""
            op_code = None

            if c in string.ascii_letters:
                while c in string.ascii_letters + string.digits + '_':
                    word += c
                    index += 1
                    if index >= len(line):
                        break
                    c = line[index]

                if word in ["void", "int", "float", "string", "bool"]:
                    op_code = TYP
                elif word in ["null"]:
                    op_code = NUL
                elif word == "array":
                    op_code = ARR
                elif word in ["if", "else"]:
                    op_code = ITE
                elif word == "for":
                    op_code = FOR
                elif word == "return":
                    op_code = RETURN
                elif word in ["and", "or"]:
                    op_code = BOP
                else:
                    op_code = ID

            elif c in "+-*/^=<>!":
                op_code = OP

                while c in "+-*/^=<>!":
                    word += c
                    index += 1
                    if index >= len(line):
                        break
                    c = line[index]
                    if word[0] in "<>":
                        break

            elif c in ",":
                op_code = SEP
                word = c
                index += 1

            elif c in ";":
                op_code = CMT
                while c != NL:
                    word += c
                    index += 1
                    if index >= len(line):
                        break
                    c = line[index]

            elif c in "()":
                op_code = PAR
                word = c
                index += 1
            elif c in "}{":
                op_code = BRC
                word = c
                index += 1
            elif c in "][":
                op_code = SBS
                word = c
                index += 1

            elif c in string.digits + ".":
                op_code = LIT
                while c in string.digits + ".":
                    word += c
                    index += 1
                    if index >= len(line):
                        break
                    c = line[index]
                if word[0] == ".":
                    word = "0" + word

            elif c in ["\n"]:
                op_code = NL
                word = c
                index += 1

            elif c in ["\t"] and False:
                op_code = TAB
                while c in ['\t']:
                    word += c
                    index += 1
                    if index >= len(line):
                        break
                    c = line[index]
            elif c == "\"":
                op_code = STRING
                escaped = False
                index += 1
                c = line[index]
                while c != "\"" or escaped:
                    escaped = False
                    if c == "\\" and not escaped:
                        escaped = True
                    word += c
                    index += 1
                    if index >= len(line):
                        break
                    c = line[index]
                index += 1
                
            else:
                index += 1

            if op_code not in [None, CMT]:
                codes.append((op_code, word, line_no))

            if index >= len(line):
                break

    return codes