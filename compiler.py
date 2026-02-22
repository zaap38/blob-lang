import sys
import string


# base tokens
ID = "ID"  # identifier
OP = "OP"  # operator
NUM = "NUM"  # number
LIT = "LIT"  # literal
TAB = "INDENT"  # indentation
NL = "NLINE"  # new line
TYP = "TYPE"  # type
PAR = "PAR"  # parenthesis
BRC = "BRC"  # braces
SEP = "SEP"  # separator
CMT = "CMT"  # comment
ITE = "IF-ELSE"  # if-then-else
FOR = "FOR"  # for-loop
RETURN = "RET"
RTYP = "R-TYPE"
ARR = "ARRAY"  # array

# AST tokens
XP = "EXPR"  # expression
FDEC = "F-DEC"  # function declaration
CALL = "CALL"  # function call
VDEC = "V-DEC"  # variable declaration
CONST = "CONST"
ARGS = "args"
UOP = "UNOP"
BOP = "BINOP"
VAR = "VAR"
FBODY = "F-BODY"
BLOCK = "BLOCK"

BLUE = "\033[96m"
YELLOW = "\033[93m"
ENDCOLOR = "\033[0m"


def tokenizer(lines):

    codes = []

    for line in lines:
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
                elif word == "array":
                    op_code = ARR
                elif word in ["if", "else"]:
                    op_code = ITE
                elif word == "for":
                    op_code = FOR
                elif word == "return":
                    op_code = RETURN
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

            elif c in string.digits:
                op_code = LIT
                while c in string.digits:
                    word += c
                    index += 1
                    if index >= len(line):
                        break
                    c = line[index]

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
                op_code = LIT
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
                codes.append((op_code, word))

            if index >= len(line):
                break

    return codes


class Parser:

    def __init__(self):
        self.pos = 0
        self.codes = []

    def parse(self, codes):
        self.codes = codes
        self.pos = 0

        tree = Tree()
        tree.root = Node("ROOT", "ROOT")

        while self.peek()[0] is not None:
            expr = self.parse_statement()
            if expr is not None:
                tree.root.add(expr)

        return tree
    
    def peek(self):
        if self.pos >= len(self.codes):
            return (None, None)
        return self.codes[self.pos]
            
    def consume(self):
        token = self.peek()
        self.pos += 1
        return token
    
    def parse_literal(self):
        token = self.peek()
        if token[0] == LIT:
            self.consume()
            return Node(LIT, token[1])
        return None
    
    def parse_factor(self):
        token = self.peek()

        # number
        if token[0] == LIT:
            return self.parse_literal()

        # identifier: variable OR function call
        if token[0] == ID:
            name = token[1]
            self.consume()

            # function call
            if self.peek()[1] == "(":
                self.consume()  # consume '('
                args = []

                if self.peek()[1] != ")":
                    args.append(self.parse_expression())
                    while self.peek()[1] == ",":
                        self.consume()
                        args.append(self.parse_expression())

                self.consume()  # consume ')'

                call = Node(CALL, name)
                call.children = args
                return call

            # variable
            return Node(VAR, name)

        # parenthesized expression
        if token[1] == "(":
            self.consume()
            expr = self.parse_expression()
            self.consume()  # consume ')'
            return expr

    def parse_term(self):
        node = self.parse_factor()
        while self.peek()[1] in ("*", "/"):
            op = self.consume()
            right = self.parse_factor()
            new = Node(BOP, op[1])
            new.children = [node, right]
            node = new
        return node

    def parse_expression(self):
        node = self.parse_term()
        while self.peek()[1] in ("+", "-"):
            op = self.consume()
            right = self.parse_term()
            new = Node(BOP, op[1])
            new.children = [node, right]
            node = new
        return node
    
    def parse_comparison(self):
        node = self.parse_expression()
        while self.peek()[1] in ("<", ">", "<=", ">=", "==", "!="):
            op = self.consume()
            right = self.parse_expression()
            new = Node(BOP, op[1])
            new.children = [node, right]
            node = new
        return node
    
    def parse_affectation(self):
        node = self.parse_comparison()
        while self.peek()[1] in ("=", "+=", "-=", "++", "--"):
            op = self.consume()
            new = None
            right = self.parse_comparison()
            if op[1] == "=":
                new = Node(BOP, op[1])
                new.children = [node, right]
            else:
                new = Node(UOP, op[1])
                if right is not None and right.kind == VAR:
                    new.children = [right]
                else:
                    new.children = [node]
            node = new
        return node
    
    def parse_return(self):
        node = Node(RETURN)
        ret_node = self.parse_comparison()
        while ret_node is not None:
            node.add(ret_node)
            self.consume()  # ','
            ret_node = self.parse_comparison()
        node.value = len(node.children)
        return node
    
    def parse_newline(self):
        node = self.parse_affectation()
        if node is None and self.peek()[0] in [NL, RETURN]:
            op = self.consume()  # NL or RETURN
            if op[0] == NL:
                new = self.parse_affectation()
                return new
            else:
                new = self.parse_return()
                return new
        return node
    
    def parse_block(self, name=""):
        block = Node(BLOCK, name)
        open_count = 0
        if self.peek()[1] == '{':
            self.consume()
            while self.peek()[1] != '}' or open_count > 0:
                if self.peek()[1] == '{':
                    open_count += 1
                    self.consume()
                elif self.peek()[1] == '}':
                    open_count -= 1
                    self.consume()
                else:
                    new = self.parse_statement()
                    if new is not None:
                        block.add(new)
            self.consume()
        return block
    
    def parse_ifthenelse(self):
        
        op = self.consume()
        if_then_else = Node(op[0], "if-then-else")

        if_then_else.add(Node("COND", "if"))
        ifblock = if_then_else.children[-1]

        cond = self.parse_comparison()
        ifblock.add(cond)

        thenblock = self.parse_block("then")
        if_then_else.add(thenblock)

        if self.peek()[1] == "else":
            self.consume()
            elseblock = self.parse_block("else")
            if_then_else.add(elseblock)
            
        return if_then_else
    
    def parse_forloop(self):
        op = self.consume()
        for_loop = Node(op[0], "for-loop")

        head = Node("HEAD")

        init_var = self.parse_affectation()
        init_block = Node("INIT")
        init_block.add(init_var)
        head.add(init_block)

        self.consume()  # ','

        limit_node = self.parse_expression()
        limit_block = Node("LIMIT")
        limit_block.add(limit_node)
        head.add(limit_block)

        increment_node = Node(LIT, '1')
        if self.peek()[1] == ',':
            self.consume()  # ','
            increment_node = self.parse_affectation()
        
        increment_block = Node("INCREMENT")
        increment_block.add(increment_node)
        head.add(increment_block)

        for_loop.add(head)

        body = self.parse_block("body")
        for_loop.add(body)
            
        return for_loop
    
    def parse_fun_dec(self, type_node, name_tok):
        node = Node(FDEC, name_tok[1])
        if type_node is not None:
            type_node.kind = RTYP
            node.add(type_node)

        self.consume()  # '('

        # parameters
        params = Node("PARAMS")
        if self.peek()[1] != ")":
            while True:
                p_type = self.consume()   # TYPE
                p_name = self.consume()   # ID
                p = Node(ARGS, p_name[1])
                p.add(Node(TYP, p_type[1]))
                params.add(p)

                if self.peek()[1] != ",":
                    break
                self.consume()  # ,

        self.consume()  # ')'
        params.value = len(params.children)
        node.add(params)

        body = self.parse_block("body")
        node.add(body)

        return node
    
    def parse_type(self):
        tok = self.peek()

        # base type
        if tok[0] == TYP:
            self.consume()
            return Node(TYP, tok[1])
        # array type
        if tok[0] == ARR:
            self.consume()              # consume 'array'
            if self.peek()[1] != "<":
                raise SyntaxError("Expected '<' after array")
            self.consume()              # consume '<'
            inner = self.parse_type()   # parse inner type
            if self.peek()[1] != ">":
                raise SyntaxError("Expected '>' after array type")
            self.consume()              # consume '>'
            node = Node(TYP, ARR)
            node.add(inner)
            return node

        return None
    
    def parse_var_dec(self, type_node, name_tok):
        node = Node(VDEC, name_tok[1])
        node.add(type_node)

        if self.peek()[1] == "=":
            self.consume()
            node.add(self.parse_comparison())

        return node

    def parse_declaration(self):
        type_node = self.parse_type()
        name_tok = self.consume()  # ID

        if self.peek()[1] == "(":
            return self.parse_fun_dec(type_node, name_tok)
        else:
            return self.parse_var_dec(type_node, name_tok)
    
    def parse_statement(self):
        tok = self.peek()

        # variable or function declaration
        if tok[0] in [TYP, ARR]:
            return self.parse_declaration()
        # if then else
        elif tok[0] == ITE:
            return self.parse_ifthenelse()
        # for loop
        elif tok[0] == FOR:
            return self.parse_forloop()
        # otherwise: expression statement
        return self.parse_newline()
        

class Tree:

    def __init__(self):
        self.root = None

    def print(self):
        if self.root is not None:
            print(self.root.to_string())
        else:
            print("Empty AST")


class Node:

    def __init__(self, kind=None, value=None, info=""):
        assert type(kind) != tuple
        self.kind = kind
        self.value = value
        self.info = info
        self.children = []

    def __str__(self):
        return "Node=" + str(tuple([self.kind, self.value]))
    
    def add(self, node):
        assert node is not None
        self.children.append(node)
    
    def to_string(self, depth=0, pipes=[]):
        prefix = ""
        offset = 3
        for i in range(depth + 1 + offset):
            if i in pipes:
                prefix += "║"
            else:
                prefix += " "
        cprefix = prefix + "╠"
        lprefix = prefix + "╚"

        pipe_value = len(prefix)
        if pipe_value not in pipes:
            pipes.append(pipe_value)

        name = ""
        code = (self.kind, self.value)
        if code is not None:
            name = BLUE + str(code[0]) + ENDCOLOR + '<' + YELLOW + str(code[1]) + ENDCOLOR + '>'
            if len(self.children) > 0:
                name += ':'
            else:
                pipes.pop(-1)
            if self.info != "":
                name += '  # ' + self.info
            name += "\n"
        child_text = ""
        for i, c in enumerate(self.children):
            if c is None:
                continue
            p = cprefix
            if i == len(self.children) - 1:
                pipes.pop(-1)
                p = lprefix
            child_text += p + c.to_string(depth + 1 + offset, pipes)
        return name + child_text
    

if __name__ == "__main__":
    program_path = sys.argv[1]
    print("Compiling", "\"" + program_path + "\"")

    lines = []
    with open(program_path, "r") as program_file:
        lines = [line.replace("\r", "").replace("    ", "\t") for line in program_file.readlines()]  # remove \r

    program = []

    print("Tokenizing...")
    codes = tokenizer(lines)

    print("Codes:")
    # print("\n".join([str(code) for code in codes]))
    print("".join(["" + code[0] + " '" + code[1].replace("\n", "\\n")
                                                  .replace("\t", "\\t") + "'| "
                   for code in codes]))

    print("==========AST==========")
    # ast = AST(codes)
    # ast.print()
    ast = Parser().parse(codes)
    ast.print()