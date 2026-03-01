from src.const_names import *
import string


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
