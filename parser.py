# parser.py
import re

# --- Lexer definitions ---
KEYWORDS = {"int", "float", "string", "void", "return", "if", "else", "for", "while", "printf"}
OPERATORS = {"+", "-", "*", "/", "=", ">", "<", "==", ">=", "<=", "!=", "++", "--"}
PUNCTUATIONS = {";", ",", "(", ")", "{", "}"}

def lexical_analysis(code):
    token_pattern = (
        r'\".*?\"'                # string literals
        r'|[A-Za-z_][A-Za-z0-9_]*'  # identifiers
        r'|\d+\.\d+'              # float constants
        r'|\d+'                   # integer constants
        r'|==|!=|<=|>=|[+\-*/=<>;,(){}]'  # operators & punctuations
    )
    tokens = re.findall(token_pattern, code)
    ordered_tokens = []
    for token in tokens:
        if token in KEYWORDS:
            ordered_tokens.append(("Keyword", token))
        elif re.match(r'^".*"$', token):
            ordered_tokens.append(("String", token))
        elif re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', token):
            ordered_tokens.append(("Identifier", token))
        elif re.match(r'^\d+\.\d+$', token):
            ordered_tokens.append(("Constant", token))
        elif re.match(r'^\d+$', token):
            ordered_tokens.append(("Constant", token))
        elif token in OPERATORS:
            ordered_tokens.append(("Operator", token))
        elif token in PUNCTUATIONS:
            ordered_tokens.append(("Punctuation", token))
        else:
            ordered_tokens.append(("Unknown", token))
    return ordered_tokens

# --- Node definition ---
class Node:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children if children else []

    def display(self, level=0):
        print(" " * (level * 4) + ("├── " if level > 0 else "") + self.name)
        for child in self.children:
            if isinstance(child, Node):
                child.display(level + 1)
            else:
                print(" " * ((level + 1) * 4) + "└── " + str(child))

# --- Parser ---
def parse(tokens):
    parse_tree = Node("Program", [])
    errors = []
    i = 0
    n = len(tokens)

    def get_val(idx):
        return tokens[idx][1] if idx < n else None

    # Expect: void main ( ) { ... }
    if n < 5 or get_val(0) != "void" or get_val(1) != "main":
        errors.append("Missing or invalid function header (expected 'void main()').")
        return parse_tree, errors

    func_node = Node("Function", [
        Node("Keyword", ["void"]),
        Node("Identifier", ["main"]),
        Node("Punctuation", ["("]),
        Node("Punctuation", [")"]),
    ])

    i = 4
    if get_val(i) != "{":
        errors.append("Missing opening '{'")
        return parse_tree, errors
    i += 1

    body_node = Node("Body", [])

    while i < n and get_val(i) != "}":
        token_type, token_value = tokens[i]

        if token_value in ("int", "float", "string"):
            decl_node = Node("Declaration", [Node("Type", [token_value])])
            i += 1
            while i < n and get_val(i) not in {";", "}"}:
                decl_node.children.append(Node(tokens[i][0], [get_val(i)]))
                i += 1
            if get_val(i) == ";":
                decl_node.children.append(Node("Punctuation", [";"]))
                i += 1
            body_node.children.append(decl_node)
            continue

        elif token_value == "if":
            if_node = Node("IfStatement", [Node("Keyword", ["if"])])
            i += 1
            if get_val(i) == "(":
                cond_node = Node("Condition", [])
                i += 1
                while i < n and get_val(i) != ")":
                    cond_node.children.append(Node(tokens[i][0], [get_val(i)]))
                    i += 1
                if_node.children.append(cond_node)
                if get_val(i) == ")":
                    i += 1
            if get_val(i) == "{":
                body = Node("IfBody", [])
                i += 1
                while i < n and get_val(i) != "}":
                    body.children.append(Node(tokens[i][0], [get_val(i)]))
                    i += 1
                if get_val(i) == "}":
                    i += 1
                if_node.children.append(body)
            if i < n and get_val(i) == "else":
                else_node = Node("ElseStatement", [Node("Keyword", ["else"])])
                i += 1
                if get_val(i) == "{":
                    else_body = Node("ElseBody", [])
                    i += 1
                    while i < n and get_val(i) != "}":
                        else_body.children.append(Node(tokens[i][0], [get_val(i)]))
                        i += 1
                    if get_val(i) == "}":
                        i += 1
                    else_node.children.append(else_body)
                if_node.children.append(else_node)
            body_node.children.append(if_node)
            continue

        elif token_value == "while":
            while_node = Node("WhileLoop", [Node("Keyword", ["while"])])
            i += 1
            if get_val(i) == "(":
                cond = Node("Condition", [])
                i += 1
                while i < n and get_val(i) != ")":
                    cond.children.append(Node(tokens[i][0], [get_val(i)]))
                    i += 1
                if get_val(i) == ")":
                    i += 1
                while_node.children.append(cond)
            if get_val(i) == "{":
                loop_body = Node("LoopBody", [])
                i += 1
                while i < n and get_val(i) != "}":
                    loop_body.children.append(Node(tokens[i][0], [get_val(i)]))
                    i += 1
                if get_val(i) == "}":
                    i += 1
                while_node.children.append(loop_body)
            body_node.children.append(while_node)
            continue

        elif token_value == "for":
            for_node = Node("ForLoop", [Node("Keyword", ["for"])])
            i += 1
            if get_val(i) == "(":
                header = Node("Header", [])
                i += 1
                while i < n and get_val(i) != ")":
                    header.children.append(Node(tokens[i][0], [get_val(i)]))
                    i += 1
                if get_val(i) == ")":
                    i += 1
                for_node.children.append(header)
            if get_val(i) == "{":
                loop_body = Node("LoopBody", [])
                i += 1
                while i < n and get_val(i) != "}":
                    loop_body.children.append(Node(tokens[i][0], [get_val(i)]))
                    i += 1
                if get_val(i) == "}":
                    i += 1
                for_node.children.append(loop_body)
            body_node.children.append(for_node)
            continue

        elif token_value == "printf":
            printf_node = Node("PrintStatement", [Node("Keyword", ["printf"])])
            i += 1
            if get_val(i) == "(":
                args_node = Node("Arguments", [])
                i += 1
                while i < n and get_val(i) != ")":
                    args_node.children.append(Node(tokens[i][0], [get_val(i)]))
                    i += 1
                printf_node.children.append(args_node)
                if get_val(i) == ")":
                    i += 1
            if get_val(i) == ";":
                printf_node.children.append(Node("Punctuation", [";"]))
                i += 1
            body_node.children.append(printf_node)
            continue

        elif token_value == "return":
            ret_node = Node("ReturnStatement", [Node("Keyword", ["return"])])
            i += 1
            while i < n and get_val(i) != ";":
                ret_node.children.append(Node(tokens[i][0], [get_val(i)]))
                i += 1
            if get_val(i) == ";":
                ret_node.children.append(Node("Punctuation", [";"]))
                i += 1
            body_node.children.append(ret_node)
            continue

        else:
            stmt_node = Node("Statement", [Node(token_type, [token_value])])
            i += 1
            while i < n and get_val(i) != ";":
                stmt_node.children.append(Node(tokens[i][0], [get_val(i)]))
                i += 1
            if get_val(i) == ";":
                stmt_node.children.append(Node("Punctuation", [";"]))
                i += 1
            body_node.children.append(stmt_node)

    parse_tree.children.append(func_node)
    func_node.children.append(Node("Punctuation", ["{"]))
    func_node.children.append(body_node)
    func_node.children.append(Node("Punctuation", ["}"]))

    return parse_tree, []

# --- Run parser on a file ---
if __name__ == "__main__":
    file_path = input("Enter the path of the C source file: ").strip()

    try:
        with open(file_path, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        exit(1)

    tokens = lexical_analysis(code)
    parse_tree, errors = parse(tokens)

    print("\n--- Parse Tree ---")
    parse_tree.display()

    if errors:
        print("\nErrors:")
        for e in errors:
            print(" -", e)
