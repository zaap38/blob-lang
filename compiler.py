import sys
import string
from registers import *


INT_MAX = 2**32-1
INT_MIN = -2**32

# base tokens
ID = "ID"  # identifier
OP = "OP"  # operator
NUM = "NUM"  # number
STRING = "STR"
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
SBS = "SUB-SCRIPT"
NUL = "NULL"

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
GREEN = "\033[92m"
RED = "\033[91m"
ENDCOLOR = "\033[0m"


STDLIB = [
    "print",
]


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


class SemanticAnalyzer:

    def __init__(self, lookup_table = {}):
        self.scopes = [{}]  # stack of variable scopes
        self.functions = {}  # function_name -> {"params": [...], "ret": str}
        self.current_return_types = None

    def analyze(self, ast):
        self.analyze_node(ast.root)
        print(GREEN + "Type-checking done!" + ENDCOLOR)

    def analyze_node(self, node):
        # New scope for functions or blocks
        if node.kind == BLOCK:
            self.push_scope()
            for c in node.children:
                self.analyze_node(c)
            self.pop_scope()
            return

        # Function declaration
        if node.kind == FDEC:
            # Return type
            rtypes = node.get(RTYP) if node.get(RTYP) else None
            ret_type = None
            if rtypes is not None:
                ret_type = []
                for rtype in rtypes:
                    ret_type.append(rtype.value)

            # Parameter types
            params = node.get("PARAMS")[0].children if node.get("PARAMS") else []
            param_types = [p.get(TYP)[0].value for p in params]

            # Save function signature
            self.functions[node.value] = {"params": param_types, "ret": ret_type}

            # New scope for function body
            self.push_scope()

            # Register parameters
            for p, t in zip(params, param_types):
                self.scopes[-1][p.value] = t

            # Track current function return type
            old_return = self.current_return_types
            self.current_return_types = ret_type

            for c in node.children:
                if c.kind not in (RTYP, "PARAMS"):
                    self.analyze_node(c)

            self.current_return_types = old_return
            self.pop_scope()
            return
        
        if node.kind == FOR:
            head = node.get("HEAD")[0]

            # Loop variable is declared automatically as int
            init_node = head.get("INIT")[0]
            if init_node.kind == BOP and init_node.value == "=" and init_node.children[0].kind == VAR:
                loop_var = init_node.children[0].value
                self.scopes[-1][loop_var] = "int"  # declare loop variable as int

            # Analyze the rest of the loop in a new scope
            self.push_scope()
            for c in node.children:
                self.analyze_node(c)
            self.pop_scope()
            return 

        # Variable declaration
        if node.kind == VDEC:
            var_type = node.get(TYP)[0].value
            self.scopes[-1][node.value] = var_type

        # Recursively analyze children first
        for c in node.children:
            self.analyze_node(c)

        # Verify operations
        self.verify(node)

    def verify(self, node):

        # Type-check binary operations
        if node.kind == BOP:
            child_types = [self.get_type(c) for c in node.children]
            if len(child_types) >= 2:
                base_type = child_types[0]
                ltype = child_types[0]
                rtype = child_types[1]
                force_ok = False
                if ltype == "float" and rtype == "int":
                    force_ok = True
                if node.value == "=" and rtype == "null":
                    force_ok = True
                if not force_ok and ltype != rtype:
                    raise Exception(
                        self.msg_error(node, f"TypeError: Invalid '{node.value}' with types '{child_types}'")
                    )

        if node.kind == VDEC:
            child_type = self.get_type(node.children[-1])
            base_type = node.children[0].value
            force_ok = False
            if base_type == "float" and child_type == "int":
                force_ok = True
            if child_type != base_type and child_type is not None and \
                    child_type != "null" and not force_ok:
                raise Exception(
                    self.msg_error(node,
                        f"TypeError: Invalid initialization for '{base_type}' with type '{child_type}'")
                )

        if node.kind == "GET":
            child = node.children[-1]
            child_type = self.get_type(child)
            if child_type != "int":
                raise Exception(
                    self.msg_error(node,
                        f"Getter expects 'int', got '{child_type}'")
                )

        # Function call argument type check
        if node.kind == CALL:
            if node.value in STDLIB:
                return
            if node.value not in self.functions:
                raise Exception(self.msg_error(node, f"Call to undefined function '{node.value}'"))
            sig = self.functions[node.value]
            expected_params = sig["params"]
            actual_args = node.children
            if len(expected_params) != len(actual_args):
                raise Exception(
                    self.msg_error(node,
                        f"Function '{node.value}' expects {len(expected_params)} args, got {len(actual_args)}")
                )
            for i, (expected, arg_node) in enumerate(zip(expected_params, actual_args)):
                arg_type = self.get_type(arg_node)
                if arg_type != expected:
                    raise Exception(
                        self.msg_error(node,
                            f"TypeError: Function '{node.value}' expects {expected} for argument #{i+1}, got {arg_type}")
                    )
        
        if node.kind == RETURN:
            if self.current_return_types is None:
                raise Exception(self.msg_error(node, "Return outside of function"))

            if len(node.children) == 0:
                if self.current_return_types != ["void"]:
                    raise Exception(
                        self.msg_error(node,
                            f"TypeError: Function must return '{self.current_return_types}', got void")
                    )
            else:
                if len(self.current_return_types) != len(node.children):
                    raise Exception(
                        self.msg_error(node,
                            f"InvalidArgCount: Function returns {len(self.current_return_types)} values, got {len(node.children)}")
                    )
                else:
                    for i in range(len(self.current_return_types)):
                        ret_type = self.get_type(node.children[i])
                        if ret_type != self.current_return_types[i]:
                            raise Exception(
                                self.msg_error(node,
                                    f"TypeError: Function returns '{self.current_return_types}', got '{ret_type}' at #{i+1}")
                            )
    
    def lookup_variable_type(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None  # not found
    
    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def msg_error(self, node, msg):
        return RED + "At line" + YELLOW + " " + str(node.line_no) + RED + " " + \
                                msg + ENDCOLOR

    def get_type(self, node):
        if node.kind == NUM:
            return "float" if '.' in node.value else "int"
        
        elif node.kind == NUL:
            return "null"
        
        elif node.kind == STRING:
            return "string"
        
        elif node.kind == VAR:
            var_type = self.lookup_variable_type(node.value)
            if var_type is None:
                raise Exception(self.msg_error(node, f": Undeclared variable '{node.value}'"))
            return var_type
        
        elif node.kind == UOP:
            return self.get_type(node.children[0])
        
        elif node.kind == BOP:
            if node.value == "//":
                return "int"
            elif node.value == "/":
                return "float"
            else:
                return self.get_type(node.children[0])
        
        elif node.kind == CALL:
            if node.value in self.functions:
                rtypes = self.functions[node.value]["ret"]
                if len(rtypes) == 1:
                    rtypes = rtypes[0]
                return rtypes
            else:
                raise Exception(self.msg_error(node, f": Call to unknown function '{node.value}'"))
            
        return None


class CodeGen:

    def __init__(self):
        self.vid = 0
        self.var_offset = 0
        self.label_id = 0
        self.scopes = []
        self.fun_local_count = {}  # [function name] -> count of local vars
        self.local_of = {}  # [vid] -> function name
        self.var_type = {}  # [vid] -> var type

        self.vid_to_offset = {}
        self.vid_to_node = {}

        self.colors = {}  # [vid] -> register
        self.first_use = {}
        self.last_use = {}

        self.current_regs = {}  # [reg] -> vid

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def declare_var(self, name):
        vid = "v" + str(self.vid)
        self.vid += 1
        self.scopes[-1][name] = vid
        return vid

    def lookup_var(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Undeclared variable '{name}'")

    def identify_scope(self, node: Node):
        # enter new scope for blocks and functions
        if node.kind in (BLOCK, FDEC):
            self.push_scope()

            # if function: declare parameters
            if node.kind == FDEC:
                self.var_offset = 0
                self.fun_local_count[node.value] = 0
                params: list[Node] = node.get("PARAMS")
                if params:
                    for p in params[0].children:
                        name = p.value
                        vid = self.declare_var(name)
                        p.vid = vid   # tag parameter node
                        self.vid_to_node[vid] = p
                        self.var_type[vid] = p.get(TYP)

        # variable declaration (int a = 5)
        if node.kind == VDEC:
            name = node.value
            vid = self.declare_var(name)
            self.var_offset += 8
            node.vid = vid
            node.offset = self.var_offset
            self.vid_to_offset[vid] = node.offset
            self.vid_to_node[vid] = node
            self.var_type[vid] = node.get(TYP)[0].value
            self.local_of[vid] = list(self.fun_local_count.keys())[-1]  # parent function
            self.fun_local_count[self.local_of[vid]] += 1

        # variable usage (a = a + 1)
        if node.kind == VAR:
            vid = self.lookup_var(node.value)
            node.vid = vid

        # recurse
        for c in node.children:
            self.identify_scope(c)

        # leave scope
        if node.kind in (BLOCK, FDEC):
            self.pop_scope()

    def coloring(self, node: Node):
        # get variable lifetime
        self.compute_lifetime(node, 0, self.first_use, self.last_use)

        # print(self.first_use)
        # print(self.last_use)

        # buld overlap graph
        graph = {}  # [node] -> [neighbors list]
        for vid in list(self.first_use.keys()):
            fuse = self.first_use[vid]
            luse = self.last_use[vid]
            if vid not in graph:
                graph[vid] = []
            for vid2 in list(self.first_use.keys()):
                if vid == vid2:
                    continue
                fuse2 = self.first_use[vid2]
                luse2 = self.last_use[vid2]
                if fuse2 >= fuse and fuse2 <= luse or \
                        luse2 >= fuse and luse2 <= luse:
                    graph[vid].append(vid2)
                    if vid2 not in graph:
                        graph[vid2] = []
                    graph[vid2].append(vid)
            
        # coloring
        reg_list = ["rbx", "rcx", "rdx", "rsi", "rdi", "r8", "r9", \
                    "r10", "r11", "r12", "r13", "r14", "r15"]  # excluded rax to use for const
        float_regs = ["xmm0","xmm1","xmm2","xmm3","xmm4","xmm5","xmm6","xmm7"]
        for r in reg_list + float_regs:  # init current regs to no value
            self.current_regs[r] = None
        self.colors = self.color_graph(graph, reg_list, float_regs)
        for vid, color in self.colors.items():
            self.vid_to_node[vid].color = color

        # print(self.colors)
                    
    def color_graph(self, interference, registers, float_registers):
        # returns: allocation: dict vid -> register or None (if spilled)
        allocation = {}  # vid -> register or None (spilled)
        
        # Order variables by degree (largest first can reduce spills)
        var_order = sorted(interference.keys(), key=lambda v: -len(interference[v]))
        
        for vid in var_order:
            # find registers used by neighbors
            neighbor_regs = {allocation[n] for n in interference[vid] if 
                             n in allocation and allocation[n] is not None}
            # pick first free register
            assigned = None
            regs = registers if self.var_type[vid] != "float" else float_registers
            for reg in regs:
                if reg not in neighbor_regs:
                    assigned = reg
                    break
            allocation[vid] = assigned  # None if all registers are taken (needs spill)
        
        return allocation

    def compute_lifetime(self, node: Node, time=0, first_use={}, last_use={}):
        time += 1
        if node.kind == VDEC:
            first_use[node.vid] = time
            last_use[node.vid] = time
        elif node.kind == VAR:
            last_use[node.vid] = time
        for c in node.children:
            time = self.compute_lifetime(c, time, first_use, last_use)
        return time

    def color(self, node: Node):
        return self.colors[node.vid]

    def gen(self, ast: Tree):
        node = ast.root
        self.out = []
        self.identify_scope(node)
        self.coloring(node)
        self.gen_node(node)
        return self.out
    
    def gen_node(self, node: Node):

        # print(node)

        if node.kind == ITE:
            pass

        elif node.kind == FDEC:
            self.label(node.value)

            # rbp: stack base pointer
            # rsp: stack pointer
            self.comment("declaring function " + node.value)
            # self.push(rbp, "load space for local var")
            self.move(rbp, rsp)
            # self.sub(rsp, 8 * self.fun_local_count[node.value], "reserve space for local variables")

            for c in node.children:
                self.gen_node(c)

            self.move(rsp, rbp, "free stack memory")
            self.ret(node)

        elif node.kind == VDEC:
            if len(node.children) > 1:
                rax_val = self.gen_node(node.children[1])
                self.move(self.get_target(node, True), rax_val, "init with value")
            else:
                self.move(self.get_target(node), "0", "zero-ing")

        elif node.kind == BOP:
            return self.gen_bop(node)

        elif node.kind == CALL:
            
            if node.value == "print":
                self.gen_lib_print(node)
            else:
                pass

        elif node.kind == ITE:
            pass

        elif node.kind == FOR:
            pass

        elif node.kind == RETURN:
            pass

        elif node.kind == VAR:
            return self.colors[node.vid]
        
        elif node.kind == NUM:
            return node.value

        elif node.kind == STRING:
            return self.init_string(node)

        elif node.kind == BLOCK:
            for c in node.children:
                self.gen_node(c)

        elif node.kind == "ROOT":
            self.write("bits 64", "")
            self.write("default rel", "")
            self.write("global _start", "")
            self.write("")
            self.label("_start")
            self.write("call main")
            self.jump("exit")
            
            for c in node.children:
                self.gen_node(c)

            # return 0
            self.label("exit")
            self.move(rax, 60)
            self.xor(rdi, rdi)
            self.syscall()

    def int_to_string(self, r1):
        # return in rax an address to the generated string

        self.move(rax, r1)
        used_regs = [rbx]

        self.comment("int_to_string()")

        self.push(used_regs)
        self.push(rax)  # save rax to

        self.move(rdx, r1)  # save orignal value
        self.move(r8, rdx)

        # get length first
        self.move(rcx, 10 ** 8)  # count 8 bytes blocks
        self.div64(r8, rcx)
        self.add(r8, 1)  # +1 line for the reminder
        self.move(rcx, 8)
        self.mult(r8, rcx)  # lines for the generated string
        self.add(r8, 8)  # +1 line for the length

        self.pop(rax)  # get the content of r1 back

        self.pop(used_regs)
        
        self.sub(rsp, r8, "reserve space")
        self.move(r10, rsp)  # mem old rsp pointer

        self.push(used_regs)

        self.move(r9, 0)
        self.move(rbx, rax)

        lid = self.label()  # while rax > 10
        self.move(rcx, 10)  # used for calculations
        self.div64(rbx, rcx)
        self.add(rcx, "48", "convert to char digit")
        self.move("[" + r10 + "+" + r9 + "]", rcx)
        self.inc(r9)
        self.cmp(rbx, 0)
        self.jump(lid, "==")  # jump if not zero

        # write string length
        self.move(rax, r10)
        self.add(rax, r8)
        self.sub(rax, 8)
        self.move(self.at(rax), r9)

        self.move(rax, rsp, "move result address in rax")
        self.add(rax, r8)
        
        self.pop(used_regs)

    def init_string(self, node):
        # save a string in memory and return a pointer to it
        self.comment("init string: " + node.kind + "(" + node.value + ")")
        text = ""
        if node.kind == NUM:
            self.move(rax, node.value)
            self.int_to_string(rax)
            return rax
        elif node.kind == VAR:
            # TODO
            return self.color(node)
        else:
            text = node.value
        # self.move(rsp, rbp)
        padding = 8 - (len(text)) % 8
        self.sub(rsp, 8 + len(text) + padding)
        self.move("[" + rbp + "-8]", len(text), "string size")
        for i in range(len(text)):
            self.move(self.rbp(padding + i + 1 + 8), "'" + text[-(i + 1)] + "'")
        self.move(rax, rbp)
        self.sub(rax, 8)
        return rax

    def rbp(self, node):
        head = "[" + rbp + "-"
        if type(node) == int:
            return head + str(node) + "]"
        return head + str(node.offset) + "]"
    
    def at(self, reg, node=None):
        head = "[" + reg
        if node is not None:
            head += "-"
            if type(node) == int:
                return head + str(node) + "]"
            return head + str(node.offset) + "]"
        return head + "]"


    def get_target(self, node: Node, is_init: bool = False):
        reg = self.colors[node.vid]
        if node.vid not in self.colors:  # if var is spilled
            return self.rbp(node)
        if (True or self.current_regs[reg] != node.vid) and not is_init:  # load var into reg
            old_vid = self.current_regs[reg]
            if old_vid is not None:
                self.move(self.rbp(self.vid_to_offset[old_vid]), reg)
            self.current_regs[reg] = node.vid
            self.move(reg, self.rbp(node), "loading " + str(node.value))
        return reg

    def gen_lib_print(self, node: Node):
        child = node.children[0]
        reg = ""
        if child.kind == VAR:
            if self.var_type[child.vid] != "string":
                # reg = self.color(child)
                pass
            else:
                # TODO
                reg = self.color(child)
        else:
            reg = self.init_string(child)
        
        self.move(r8, self.at(reg), "load len in r8")
        self.move(r9, 8)
        self.div64(r8, r9, "len // 8")
        self.inc(r8)
        self.move(r10, 8)
        self.mult(r8, r10)
        self.move(r9, reg)
        self.move(rax, 1, "syscall: write")
        self.move(rdi, 1, "std out")
        self.move(rdx, self.at(r9), "length of the string")
        self.sub(r9, r8)
        self.move(rsi, r9, "address of the string")
        self.syscall()

    def gen_statement(self, node: Node):
        pass

    def gen_expr(self, node: Node):
        pass

    def gen_affectation(self, node: Node):
        pass

    def gen_bop(self, node: Node):
        self.comment("binop '" + node.value + "'")
        left = node.children[0]
        right = node.children[1]
        
        r1 = self.gen_node(left)
        r2 = self.gen_node(right)
        
        if node.value == "=":
            rax_val = self.gen_node(right)
            target = self.get_target(left)
            self.move(target, rax_val, "affectation")
            return target

        elif node.value == "+":
            return self.add(r1, r2)

        elif node.value == "-":
            return self.sub(r1, r2)
        
        elif node.value == "/":
            pass
        
        elif node.value == "//":
            pass
        
        elif node.value == "*":
            pass
        
        elif node.value == "^":
            pass

    def syscall(self):
        self.write("syscall")

    def inst(self, inst_addr):
        self.write("int " + str(inst_addr))

    def call(self, node: Node):
        self.write("call " + node.value)

    def ite(self, node: Node):
        pass

    def forloop(self, node: Node):
        pass

    def ret(self, node: Node):
        self.write("ret")

    def inc(self, reg, comment=""):
        comment = self.make_comment(comment)
        self.write("inc " + reg)

    def label(self, name=""):
        if name == "":
            self.label_id += 1
            name = "label_" + str(self.label_id)
        self.write(name + ":", "")
        return name

    def move(self, r1, r2, comment=""):
        comment = self.make_comment(comment)
        self.write("mov " + str(r1) + ", " + str(r2) + comment)
        return r1

    def add(self, r1, r2, comment=""):
        comment = self.make_comment(comment)
        self.write("add " + str(r1) + ", " + str(r2) + comment)
        return r1
    
    def mult(self, r1, r2, comment=""):
        comment = self.make_comment(comment)

        self.push([rax, rdx])

        self.move(rax, r1)
        self.xor(rdx, rdx)
        self.write("mul " + str(r2) + comment)
        self.move(r1, rax)
        
        self.pop([rax, rdx])

        return r1
    
    def div64(self, r1, r2, comment=""):
        comment = self.make_comment(comment)
        self.push([rax, rdx])

        self.move(rax, r1)
        self.xor(rdx, rdx)
        self.cmp(r2, 0, "check division by zero")
        self.jump("exit", "!=")
        self.write("div " + r2 + comment)
        self.move(r1, rax)
        self.move(r2, rdx)
        
        self.pop([rax, rdx])
        return r1, r2
    
    def xor(self, r1, r2, comment=""):
        comment = self.make_comment(comment)
        self.write("xor " + str(r1) + ", " + str(r2) + comment)
        return r1

    def sub(self, r1, r2, comment=""):
        comment = self.make_comment(comment)
        self.write("sub " + str(r1) + ", " + str(r2) + comment)
        return r1
    
    def push_callee_saved(self, v):
        comment = self.make_comment(comment)
        if type(v) != list:
            v = [v]
        for reg in v:
            if reg in [rbx, r12, r13, r14, r15]:
                self.write("push " + str(reg) + comment)
                comment = ""

    def pop_callee_saved(self, v):
        comment = self.make_comment(comment)
        if type(v) != list:
            v = [v]
        for reg in v:
            if reg in [rbx, r12, r13, r14, r15]:
                self.write("pop " + str(reg) + comment)
                comment = ""

    def push(self, v, comment=""):
        comment = self.make_comment(comment)
        if type(v) != list:
            v = [v]
        for reg in v:
            self.write("push " + str(reg) + comment)
            comment = ""

    def pop(self, v, comment=""):
        comment = self.make_comment(comment)
        if type(v) != list:
            v = [v]
        for reg in reversed(v):
            self.write("pop " + str(reg) + comment)
            comment = ""

    def pusha(self, comment=""):
        comment = self.make_comment(comment)
        self.write("pusha" + comment)

    def popa(self, comment=""):
        comment = self.make_comment(comment)
        self.write("popa" + comment)

    def jump(self, label, t=None):
        # "jump if false" setup
        commands = {
            "<": "jge",
            ">": "jle",
            "<=": "jg",
            ">=": "jl",
            "==": "jne",
            "!=": "je",
            None: "jmp"
        }
        self.write(commands[t] + " " + str(label))

    def cmp(self, r1, r2, comment=""):
        if comment != "":
            comment = "        ;; " + comment
        self.write("cmp " + str(r1) + ", " + str(r2) + comment)
        return r1
    
    def make_comment(self, comment):
        if comment != "":
            return "        ;; " + comment
        return ""
    
    def comment(self, text):
        self.write(";; " + text)

    def write(self, line, indent="\t"):
        self.out.append(indent + line)


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
    print("".join([BLUE + code[0] + ENDCOLOR + " '" + YELLOW + code[1].replace("\n", "\\n")
                                                  .replace("\t", "\\t") + ENDCOLOR + \
                                                    "' (" + GREEN + str(code[2]) +  ENDCOLOR + ")| "
                   for code in codes]))

    print("==========AST==========")
    ast = Parser().parse(codes)
    ast.print()

    print("==========TYPE-CHECKING==========")
    SemanticAnalyzer().analyze(ast)

    print("==========ASM-GEN==========")
    asm_code = CodeGen().gen(ast)
    # print(asm_code)
    with open("./output.asm", "w") as of:
        of.write("\n".join(asm_code))
    print("ASM Generated")
    # ast.print()  # ast with var IDs