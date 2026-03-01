
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