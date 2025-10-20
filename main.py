import os
import re
from lexer import lexical_analysis, display_tokens
from parser import parse
from tac_generator import generate_tac_from_node, display_tac
from ac_generator import generate_assembly, display_assembly
from optimizer import optimize_tac, display_optimization   # <-- added import

def preprocess_code(lines):
    clean_lines = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(("if", "else", "for", "while", "printf", "return", "{", "}")):
            print(f"; Unhandled TAC: ; Control structure detected: {line}")
            continue
        line = re.sub(r'(\w+)\+\+', r'\1 = \1 + 1', line)
        line = re.sub(r'(\w+)\-\-', r'\1 = \1 - 1', line)
        if line.startswith("int ") and "=" not in line:
            continue
        line = line.rstrip(";")
        clean_lines.append(line)
    return clean_lines


def main():
    path = input("Enter the path of the C source file: ").strip()
    if not os.path.exists(path):
        print("File not found!!!")
        return

    with open(path, "r") as f:
        code = f.read()
    print("File loaded successfully.")

    # --- Phase 1: Lexical Analysis ---
    result, errors, ordered_tokens = lexical_analysis(code)
    display_tokens(result, errors)

    # --- Phase 2: Parsing ---
    tree, parse_errors = parse(ordered_tokens)
    print("\n--- Parsing & Parse Tree ---")
    if parse_errors:
        for e in parse_errors:
            print(e)
    else:
        tree.display()

    # --- Phase 3: TAC Generation ---
    print("\n--- Generating Three Address Code (TAC) ---")
    all_tac = generate_tac_from_node(tree)
    display_tac(all_tac)

    # --- Phase 4: Optimization ---
    print("\n--- Optimizing TAC ---")
    optimized_tac = optimize_tac(all_tac)
    display_optimization(all_tac, optimized_tac)

    # --- Phase 5: Assembly Generation ---
    print("\n--- Generating Assembly Code (from Optimized TAC) ---")
    assembly = generate_assembly(optimized_tac)
    display_assembly(assembly)


if __name__ == "__main__":
    main()
