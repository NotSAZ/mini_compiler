# lexer.py
import re
import os

KEYWORDS = {"int", "float", "string", "void", 
            "return", "if", "else", "for", "while", 
            "printf"}

OPERATORS = {"+", "-", "*", "/", "=", ">", "<", 
             "==", ">=", "<=", "!=", "++", "--"}

PUNCTUATIONS = {";", ",", "(", ")", "{", "}"}


def lexical_analysis(code):
    """
    Perform lexical analysis on the given code string.
    Returns:
        result: dict of categorized tokens
        errors: list of unrecognized tokens
        ordered_tokens: list of tokens in order of appearance
    """
    token_pattern = (
        r'\".*?\"'                # string literals
        r'|[A-Za-z_][A-Za-z0-9_]*'  # identifiers
        r'|\d+\.\d+'              # float constants
        r'|\d+'                   # integer constants
        r'|==|!=|<=|>=|[+\-*/=<>;,(){}]'  # operators & punctuations
    )

    tokens = re.findall(token_pattern, code)

    result = {
        "Keyword": set(),
        "Identifier": set(),
        "Operator": set(),
        "Constant": set(),
        "String": set(),
        "Punctuation": set()
    }

    errors = []
    ordered_tokens = []

    for token in tokens:
        if token in KEYWORDS:
            result["Keyword"].add(token)
            ordered_tokens.append(("Keyword", token))
        elif re.match(r'^".*"$', token):
            result["String"].add(token)
            ordered_tokens.append(("String", token))
        elif re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', token):
            result["Identifier"].add(token)
            ordered_tokens.append(("Identifier", token))
        elif re.match(r'^\d+\.\d+$', token):
            result["Constant"].add(token)
            ordered_tokens.append(("Constant", token))
        elif re.match(r'^\d+$', token):
            result["Constant"].add(token)
            ordered_tokens.append(("Constant", token))
        elif token in OPERATORS:
            result["Operator"].add(token)
            ordered_tokens.append(("Operator", token))
        elif token in PUNCTUATIONS:
            result["Punctuation"].add(token)
            ordered_tokens.append(("Punctuation", token))
        else:
            errors.append(token)

    # Convert sets to sorted lists
    for k in result:
        result[k] = sorted(result[k])

    return result, errors, ordered_tokens


def display_tokens(result, errors):
    """Display lexical analysis results"""
    print("\n--- Lexical Analysis ---")
    for category, items in result.items():
        if items:
            print(f"{category} ({len(items)}): {', '.join(items)}")
    if errors:
        print(f"\nInvalid Tokens ({len(errors)}): {', '.join(errors)}")


# --- Run independently from a file ---
if __name__ == "__main__":
    path = input("Enter the path of the code file: ").strip()
    if not os.path.exists(path):
        print(" File not found.")
    else:
        with open(path, "r") as f:
            code = f.read()

        result, errors, ordered_tokens = lexical_analysis(code)
        display_tokens(result, errors)
