from src.const_names import *
import string


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
        # tree.root.add(Node(CALL, "main"))

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
        if token[0] in [LIT, NUL, STRING]:
            self.consume()
            if token[0] == STRING:
                return Node(STRING, token[1], token[2])
            elif token[1][0] in string.digits:
                return Node(NUM, token[1], token[2])
            elif token[0] == NUL:
                return Node(token[0], token[1], token[2])
            else:
                return Node(STRING, token[1], token[2])
        return None
    
    def parse_factor(self):
        token = self.peek()

        # number
        if token[0] in [LIT, NUL, STRING]:
            return self.parse_literal()

        # identifier: variable OR function call
        if token[0] in [ID, SBS]:
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

                call = Node(CALL, name, token[2])
                call.children = args
                return call
            # array
            if self.peek()[1] == '[':
                node = Node(VAR, name, token[2])
                
                while self.peek()[1] == '[':
                    self.consume()  # '['
                    index = self.parse_expression()
                    self.consume()  # ']'

                    get = Node("GET", "index", token[2])
                    get.add(node)
                    get.add(index)
                    node = get

                return node

            # variable
            return Node(VAR, name, token[2])

        # parenthesized expression
        if token[1] == "(":
            self.consume()
            expr = self.parse_expression()
            self.consume()  # consume ')'
            return expr

    def parse_term(self):
        node = self.parse_factor()
        while self.peek()[1] in ("*", "/", "//"):
            op = self.consume()
            right = self.parse_factor()
            new = Node(BOP, op[1], op[2])
            new.children = [node, right]
            node = new
        return node

    def parse_expression(self):
        node = self.parse_term()
        while self.peek()[1] in ("+", "-"):
            op = self.consume()
            right = self.parse_term()
            new = Node(BOP, op[1], op[2])
            new.children = [node, right]
            node = new
        return node
    
    def parse_comparison(self):
        node = self.parse_expression()
        while self.peek()[1] in ("<", ">", "<=", ">=", "==", "!="):
            op = self.consume()
            right = self.parse_expression()
            new = Node(BOP, op[1], op[2])
            new.children = [node, right]
            node = new
        return node
    
    def parse_boolean_op(self):
        node = self.parse_comparison()
        while self.peek()[1] in ("and", "or"):
            op = self.consume()
            right = self.parse_comparison()
            new = Node(BOP, op[1], op[2])
            new.children = [node, right]
            node = new
        return node
    
    def parse_affectation(self):
        node = self.parse_boolean_op()
        while self.peek()[1] in ("=", "+=", "-=", "++", "--"):
            op = self.consume()
            new = None
            right = self.parse_boolean_op()
            if op[1] == "=":
                new = Node(BOP, op[1], op[2])
                new.children = [node, right]
            else:
                new = Node(UOP, op[1], op[2])
                if right is not None and right.kind == VAR:
                    new.children = [right]
                else:
                    new.children = [node]
            node = new
        return node
    
    def parse_return(self):
        node = Node(RETURN, "", self.peek()[2])
        ret_node = self.parse_boolean_op()
        while ret_node is not None:
            node.add(ret_node)
            self.consume()  # ','
            ret_node = self.parse_boolean_op()
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
        block = Node(BLOCK, name, self.peek()[2])
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
        if_then_else = Node(op[0], "if-then-else", op[2])

        if_then_else.add(Node("COND", "if", op[2]))
        ifblock = if_then_else.children[-1]

        cond = self.parse_boolean_op()
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
        for_loop = Node(op[0], "for-loop", op[2])

        head = Node("HEAD", "", op[2])

        init_var = self.parse_declaration(True)
        init_block = Node("INIT", "", op[2])
        init_block.add(init_var)
        head.add(init_block)

        self.consume()  # ','

        limit_node = self.parse_expression()
        limit_block = Node("LIMIT", "", op[2])
        limit_block.add(limit_node)
        head.add(limit_block)

        increment_node = Node(LIT, '1', op[2])
        default = True
        if self.peek()[1] == ',':
            default = False
            self.consume()  # ','
            increment_node = self.parse_affectation()
        
        increment_block = Node("INCREMENT", "default" if default else "", op[2])
        increment_block.add(increment_node)
        head.add(increment_block)

        for_loop.add(head)

        body = self.parse_block("body")
        for_loop.add(body)
            
        return for_loop
    
    def parse_fun_dec(self, type_nodes, name_tok):
        node = Node(FDEC, name_tok[1], name_tok[2])

        for type_node in type_nodes:
            if type_node is not None:
                type_node.kind = RTYP
                node.add(type_node)

        self.consume()  # '('

        # parameters
        params = Node("PARAMS", "", self.peek()[2])
        if self.peek()[1] != ")":
            while True:
                p_type = self.consume()   # TYPE
                p_name = self.consume()   # ID
                p = Node(VDEC, p_name[1], self.peek()[2])
                p.add(Node(TYP, p_type[1], self.peek()[2]))
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
            return Node(TYP, tok[1], tok[2])
        
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
            node = Node(TYP, ARR, tok[2])
            node.add(inner)
            return node

        return None
    
    def parse_var_dec(self, type_node, name_tok):
        node = Node(VDEC, name_tok[1], name_tok[2])
        node.add(type_node)
        if self.peek()[1] == "=":
            self.consume()
            node.add(self.parse_boolean_op())

        return node

    def parse_declaration(self, force_int=False):
        type_node = self.parse_type() if not force_int else Node(TYP, "int", self.peek()[2])
        type_nodes = [type_node]
        while self.peek()[0] in [SEP, TYP]:
            if self.peek()[0] == TYP:
                type_nodes.append(self.parse_type())
            else:
                self.consume()  # ','

        name_tok = self.consume()  # ID
        
        if self.peek()[1] == "(":
            # return self.parse_fun_dec(type_nodes, name_tok)
            node = self.parse_fun_dec(type_nodes, name_tok)
            return node
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

    def __init__(self, kind=None, value=None, line_no=0):
        assert type(kind) != tuple
        self.kind = kind
        self.value = value
        self.line_no = line_no
        self.vid = 0
        self.color = ""
        self.offset = 0  # memory offset
        self.children = []

    def __str__(self):
        return "Node=" + str(tuple([self.kind, self.value]))
    
    def add(self, node):
        assert node is not None
        self.children.append(node)

    def get(self, c_type):
        matchs = []
        for c in self.children:
            if c.kind == c_type:
                matchs.append(c)
        return matchs
    
    def print(self):
        print(self.to_string())
    
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
            text_value = str(code[1])
            if self.kind in [VAR, VDEC] and self.vid != 0:
                text_value = text_value + "{" + RED + str(self.vid) + YELLOW + "}"
            name = BLUE + str(code[0]) + ENDCOLOR + '<' + YELLOW + text_value + ENDCOLOR + '>'
            if len(self.children) > 0:
                name += ':'
            else:
                pipes.pop(-1)
            name += GREEN + "  # " + str(self.line_no) + ENDCOLOR
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
