import sys
from src.registers import *
from src.const_names import *
from src.tokenizer import tokenizer
from src.parser import Parser, Tree, Node
from src.semanticanalyzer import SemanticAnalyzer


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

        # for each function, list of the regs it overwrites
        self.clobbers = {}  # [function_name] -> [clobbered regs]
        self.init_clobbers()

        self.push_pop_delta = 0

    def init_clobbers(self):
        self.clobbers["int_to_string"] = [rax, rcx, rdx, r8, r9, r10, r11]
        self.clobbers["init_string"] = [rax]
        self.clobbers["gen_lib_print"] = [rax, rdx, r8, r9, r10, rsi]
        self.clobbers["mult"] = [rax, rdx]
        self.clobbers["div64"] = [rax, rcx, rdx]

        # filter out regs that do not need to be saved by this function
        for k in self.clobbers:
            self.clobbers[k] = filter_caller_saved(self.clobbers[k])

        # closure
        fuse = {}  # functions called by the key function
        fuse["int_to_string"] = ["div64", "mult"]
        fuse["init_string"] = ["int_to_string"]
        fuse["gen_lib_print"] = ["init_string", "div64", "mult"]
        
        changed = True
        while changed:
            changed = False
            for f_name, f_regs in self.clobbers.items():
                if f_name not in fuse:
                    continue
                old_regs_len = len(f_regs)
                for f_used in fuse[f_name]:
                    f_regs += self.clobbers[f_used]
                self.clobbers[f_name] = list(set(f_regs))
                new_regs_len = len(self.clobbers[f_name])
                if old_regs_len != new_regs_len:
                    changed = True

        for k, v in self.clobbers.items():
            print("Function" + YELLOW, k, ENDCOLOR + "clobbers" + GREEN, v, ENDCOLOR)

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

        assert self.push_pop_delta == 0  # if not zero, something has been forgotten

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
        # use [rax, rcx, rdx, r8, r9, r10, r11]
        # fuse [div64, mult]
        # return in rax an address to the generated string

        # known issue:
        # 123 is saved as string "321"

        self.move(rax, r1)

        self.comment("int_to_string()")

        self.push(rax)  # save rax to

        self.move(rdx, r1)  # save orignal value
        self.move(r8, rdx)

        # get length first
        self.move(rcx, 10 ** 8)  # count 8 bytes blocks
        self.pp(self.div64, r8, rcx, [rdx])
        self.add(r8, 1)  # +1 line for the reminder
        self.move(rcx, 8)
        self.pp(self.mult, r8, rcx, [rax, rcx, rdx, r9, r10])
        self.add(r8, 8)  # +1 line for the length

        self.pop(rax)  # get the content of r1 back
        
        self.sub(rsp, r8, "reserve space")
        self.move(r10, rsp)  # mem old rsp pointer

        self.move(r9, 0)
        self.move(r11, rax)

        lid = self.label()  # while rax > 10
        self.move(rcx, 10)  # used for calculations
        self.pp(self.div64, r11, rcx, [rax, rdx, r8, r9, r10])
        self.add(rcx, "48", "convert to char digit")
        self.move("[" + r10 + "+" + r9 + "]", rcx)
        self.inc(r9)
        self.cmp(r11, 0)
        self.jump(lid, "==")  # jump if not zero

        # write string length
        self.move(rax, r10)
        self.add(rax, r8)
        self.sub(rax, 8)
        self.move(self.at(rax), r9)

        return rax

    def init_string(self, node: Node):
        # use [rax]
        # fuse [int_to_string, mult]
        # save a string in memory and return a pointer to it
        self.comment("init string: " + node.kind + "(" + node.value + ")")
        text = ""
        if node.kind == NUM:
            self.move(rax, node.value)
            return self.int_to_string(rax)
        elif node.kind == VAR:
            return self.int_to_string(self.color(node))
        else:
            text = node.value
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
        # use [rax, rdx, r8, r9, r10, rsi]
        # fuse [init_string, div64, mult]
        # print in stdout

        # known issue:
        # does not add '\n' at the end of the string
        # does not handle strings containing '\n'

        child = node.children[0]
        reg = ""
        if child.kind == VAR:
            if self.var_type[child.vid] != "string":
                reg = self.init_string(child)
            else:
                reg = self.color(child)
        else:
            reg = self.init_string(child)
        
        self.move(r8, self.at(reg), "load len in r8")
        self.move(r9, 8)
        self.pp(self.div64, r8, r9, [rax, rdx], "len // 8")
        self.inc(r8)
        self.move(r10, 8)
        self.pp(self.mult, r8, r10, [rax, rdx])
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
        assert r1 != "rip"
        if r1 != r2:  # skip useless move to self
            self.write("mov " + str(r1) + ", " + str(r2) + comment)
        return r1

    def add(self, r1, r2, comment=""):
        comment = self.make_comment(comment)
        self.write("add " + str(r1) + ", " + str(r2) + comment)
        return r1
    
    def mult(self, r1, r2, comment=""):
        # use [rax, rdx]
        # store result in r1
        comment = self.make_comment(comment)

        self.move(rax, r1)
        self.xor(rdx, rdx)
        self.write("mul " + str(r2) + comment)
        self.move(r1, rax)

        return r1
    
    def div64(self, r1, r2, comment=""):
        # use [rax, rcx, rdx]
        # r1 divided by r2 -> quotient in r1 and reminder in r2

        comment = self.make_comment(comment)

        if r1 != rax:
            self.move(rax, r1)
        div_reg = r2
        if r2 == rdx:
            div_reg = self.move(rcx, r2, "move divisor reg from rdx as rdx will be zero-ed")
        self.xor(rdx, rdx)
        self.cmp(div_reg, 0, "check division by zero")
        self.jump("exit", "!=")
        self.write("div " + div_reg + comment)
        if r1 != rax:
            self.move(r1, rax)
        self.move(r2, rdx)
        
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
            if reg in reversed([rbx, r12, r13, r14, r15]):
                self.write("pop " + str(reg) + comment)
                comment = ""

    def push_clobbered(self, regs, f_name, comment=""):
        comment = self.make_comment(comment)
        if type(regs) != list:
            regs = [regs]
        for reg in regs:
            if reg in self.clobbers[f_name]:
                self.push(reg)
                comment = ""
    
    def pop_clobbered(self, regs, f_name, comment=""):
        comment = self.make_comment(comment)
        if type(regs) != list:
            regs = [regs]
        for reg in reversed(regs):
            if reg in self.clobbers[f_name]:
                self.pop(reg)
                comment = ""

    def pp(self, f, r1, r2="", regs=None, comment=""):
        # wraps the function f with pushçclobbered() and pop_cloberred()
        assert f.__name__ in self.clobbers
        f_name = f.__name__
        if regs is not  None:
            self.push_clobbered(regs, f_name)
        if r2 == "":
            ret_reg = f(r1, comment)
        else:
            ret_reg = f(r1, r2, comment)
        if regs is not  None:
            self.pop_clobbered(regs, f_name)
        return ret_reg

    def push(self, v, comment=""):
        comment = self.make_comment(comment)
        if type(v) != list:
            v = [v]
        for reg in v:
            self.push_pop_delta += 1
            self.write("push " + str(reg) + comment)
            comment = ""

    def pop(self, v, comment=""):
        comment = self.make_comment(comment)
        if type(v) != list:
            v = [v]
        for reg in reversed(v):
            self.push_pop_delta -= 1
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