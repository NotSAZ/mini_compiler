# lexer.py
import re

KEYWORDS = {"int", "float", "void", "return", "if", "else", "for", "while"}
OPERATORS = {"+", "-", "*", "/", "=", ">", "<", "==", ">=", "<=", "!="}
PUNCTUATIONS = {";", ",", "(", ")", "{", "}"}

def lexical_analysis(code):
    # Tokenize code
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|[0-9]+|==|<=|>=|!=|[-+*/=(){};,<>]", code)
    
    result = {
        "Keyword": set(),
        "Identifier": set(),
        "Operator": set(),
        "Constant": set(),
        "Punctuation": set()
    }
    errors = []
    ordered_tokens = []  # for parser

    for token in tokens:
        if token in KEYWORDS:
            result["Keyword"].add(token)
            ordered_tokens.append(("Keyword", token))
        elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", token):
            result["Identifier"].add(token)
            ordered_tokens.append(("Identifier", token))
        elif token in OPERATORS:
            result["Operator"].add(token)
            ordered_tokens.append(("Operator", token))
        elif re.match(r"^[0-9]+$", token):
            result["Constant"].add(token)
            ordered_tokens.append(("Constant", token))
        elif token in PUNCTUATIONS:
            result["Punctuation"].add(token)
            ordered_tokens.append(("Punctuation", token))
        else:
            errors.append(token)

    # Convert sets to sorted lists for display
    for k in result:
        result[k] = sorted(result[k])

    return result, errors, ordered_tokens


def display_tokens(result, errors):
    print("\n--- Lexical Analysis ---")
    for category, items in result.items():
        if items:
            print(f"{category} ({len(items)}): {', '.join(items)}")
    if errors:
        print(f"\nInvalid Tokens: {', '.join(errors)}")
