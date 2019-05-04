#
# (B)ASM - Elliot Bewey
# 2019      MIT License
#

# Imports
from datetime import datetime

# --------------------
# Constants
# --------------------

# Constant Null/Empty States
NULL = 0
EMPTY = ""

# Limits
MAX_MEMORY = 2048
MAX_ARGS = 16

# ASM Return States
RET_EXIT = -3
RET_ERR = -2
RET_OK = -1

# ASM Comparision Flags
ASM_FLAG_ERR = RET_ERR
ASM_FLAG_LT = -1
ASM_FLAG_EQ = 0
ASM_FLAG_GT = 1

# --------------------
# Functions for Operations
# --------------------


KW_OUT_S = "OUT"


# OUTPUT Operation KW
# Argument 0: Content
def kw_out(*argv):
    asm_print(get_arg_val(argv[0]))
    return RET_OK


KW_MOV_S = "MOV"


# MOVE Operation KW
# Argument 0: Destination
# Argument 1: Source
def kw_mov(*argv):
    if check_arg(KW_MOV_S, len(argv), 2):
        return RET_ERR
    asm_memory[argv[0]] = get_arg_val(argv[1])
    return RET_OK


KW_ADD_S = "ADD"


# ADD Operation KW
# Argument 0: Destination
# Argument 1: Source
def kw_add(*argv):
    if check_arg(KW_ADD_S, len(argv), 2):
        return RET_ERR
    asm_memory[argv[0]] = int(asm_memory[argv[0]]) + int(get_arg_val(argv[1]))
    return RET_OK


KW_CMP_S = "CMP"


# COMPARE Operation KW
# Argument 0: Value A
# Argument 1: Value B
def kw_cmp(*argv):
    if check_arg(KW_CMP_S, len(argv), 2):
        return RET_ERR
    
    global asm_flag
    val_a = int(get_arg_val(argv[0]))
    val_b = int(get_arg_val(argv[1]))
    asm_flag = ASM_FLAG_ERR
    
    if val_a > val_b:
        asm_flag = ASM_FLAG_GT
    elif val_a < val_b:
        asm_flag = ASM_FLAG_LT
    else:
        asm_flag = ASM_FLAG_EQ        
    return RET_OK


KW_JMP_S = "JMP"


# JUMP Operation KW
# Argument 0: Destination (Line)
def kw_jmp(*argv):
    return int(argv[0])


KW_JG_S = "JG"


# JUMP GREATER Operation KW
# Argument 0: Destination (Line)
def kw_jg(*argv):
    if check_arg(KW_JG_S, len(argv), 1):
        return RET_ERR
   
    global asm_flag
    if asm_flag == ASM_FLAG_GT:
        return int(argv[0])
    return RET_OK


KW_JL_S = "JL"


# JUMP LESSER Operation KW
# Argument 0: Destination (Line)
def kw_jl(*argv):
    if check_arg(KW_JL_S, len(argv), 1):
        return RET_ERR
    
    global asm_flag
    if asm_flag == ASM_FLAG_LT:
        return int(argv[0])
    return RET_OK


KW_INP_S = "INP"


# INPUT Operation KW
# Argument 0: Destination
def kw_inp(*argv):
    if check_arg(KW_INP_S, len(argv), 1):
        return RET_ERR
    
    asm_print("Input: ", end='')
    asm_memory[argv[0]] = input()
    return RET_OK


KW_RET_S = "RET"


# RETURN Operation KW
# Argument 0 (Optional) Return Code
def kw_ret(*argv):   
    
    ret_code = 0
    if argv[0]:
        ret_code = int(argv[0])
    asm_print("Program ended with code " + str(ret_code))
    return RET_EXIT


# Ensures args are within limits
def check_arg(kw, amt, req_amt):
    if amt > MAX_ARGS:
        asm_print("Too many args, max is " + str(MAX_ARGS))
    if amt != req_amt:
        raise Exception(str(kw) + " takes " + str(req_amt) +
                        " arguments, but you only gave " + str(amt))


# --------------------
# Registers and Memory
# --------------------


kw_functions = {KW_OUT_S: kw_out, KW_MOV_S: kw_mov, KW_ADD_S: kw_add,
                KW_JMP_S: kw_jmp, KW_CMP_S: kw_cmp, KW_JL_S: kw_jl,
                KW_JG_S: kw_jg, KW_INP_S: kw_inp, KW_RET_S: kw_ret}
asm_memory = {}
asm_flag = ASM_FLAG_EQ


# --------------------
# Lexer / IO
# --------------------


def asm_print(value, end='\n'):
    time = datetime.now().strftime("%H:%M:%S")
    print("[" + time + "][ASM] " + value, end=end) 


# Returns the value of the address, or the coded value
def get_arg_val(arg):
    def is_address(s):
        return s.startswith("0x")

    if is_address(arg):
        return asm_memory[arg]
    else:
        return arg


# Set all of 'asm_memory' to be NULL (0)
def empty_memory():
    for i in range(0, MAX_MEMORY):
        asm_memory[hex(i)] = NULL


# Prints the memory locations that aren't NULL (0)
def print_memory():
    for i in range(0, MAX_MEMORY):
        val = asm_memory[hex(i)]
        if val != NULL:
            asm_print(str(hex(i)) + " = " + str(val))


# Tokenize each line into a keyword and series of arguments
def tokenize(s):
    if s == EMPTY:
        return EMPTY
    built_s = EMPTY
    for char in s:
        if char == ';':
            break
        built_s += char
    token_parts = built_s.split()
    token_kw = token_parts[0]
    token_args = EMPTY
    token_parts[0] = EMPTY
    token_kw = token_kw.upper()
    for token in token_parts:
        if not token:
            continue
        token_args += token.strip()
    token_args = token_args.split(',')
    new_dict = {"kw": token_kw,
                "args": token_args}
    return new_dict


# Open Destination File (d) in Read-Mode
def get_file_lines(d):
    f = open(d, "r")
    if f.mode == "r":
        contents = f.read()
        contents = contents.splitlines()
        return contents


# Runs the given code_lines through the tokenizer and kw functions
def run_program(code_lines):
    code_line = 0
    while code_line < len(code_lines):
        code = code_lines[code_line]
        if not code:
            code_line = code_line + 1
            continue
        code = tokenize(code)
        next_line = kw_functions[code["kw"]](*code["args"])
        if next_line < 0:
            if next_line == RET_EXIT:
                return
            code_line = code_line + 1
        else:
            code_line = next_line


# Ran at program start, runs lines of code into the run_program subroutine
def main():
    empty_memory()
    asm_print("Enter directory of code file: ", end='')
    d = input()
    code_lines = get_file_lines(d)
    
    asm_print("--- START PROGRAM ---")
    run_program(code_lines)
    asm_print("--- END PROGRAM ---")


# Runs the main functions
if __name__ == "__main__":
    main()
    asm_print("--- DEBUG INFO ---")
    print_memory()
