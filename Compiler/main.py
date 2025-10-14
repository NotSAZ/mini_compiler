# main.py
from lexer import lexical_analysis, display_tokens
from parser import parse
from tac_generator import generate_tac, display_tac
import os

def main():
    print("Choose input method:")
    print("1. Console input")
    print("2. File input (.txt)")
    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        print("\nEnter your code (end with an empty line):")
        lines = []
        while True:
            line = input()
            if not line.strip():
                break
            lines.append(line)
        code = "\n".join(lines)
    else:
        path = input("\nEnter .txt file path: ").strip()
        if not os.path.exists(path):
            print("❌ File not found.")
            return
        with open(path, "r") as f:
            lines = f.readlines()
        code = "".join(lines)
        print("✅ File loaded successfully.")

    result, errors, ordered_tokens = lexical_analysis(code)
    display_tokens(result, errors)

    tree, parse_errors = parse(ordered_tokens)
    print("\n--- Parsing & Parse Tree ---")
    if parse_errors:
        for e in parse_errors:
            print(e)
    else:
        tree.display()

    print("\n--- Generating Three Address Code (TAC) ---")
    for line in lines:
        if "=" in line and not any(k in line for k in ("if", "while", "for")):
            tac = generate_tac(line)
            display_tac(tac)


if __name__ == "__main__":
    main()
