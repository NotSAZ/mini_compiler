# parser.py

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


def parse(tokens):
    parse_tree = Node("Program", [])
    errors = []
    i = 0
    n = len(tokens)

    def get_val(idx):
        return tokens[idx][1] if idx < n else None

    # Expect: void main ( ) { ... }
    if n < 5 or get_val(0) != "void" or get_val(1) != "main":
        errors.append("❌ Missing or invalid function header (expected 'void main()').")
        return parse_tree, errors

    func_node = Node("Function", [
        Node("Keyword", ["void"]),
        Node("Identifier", ["main"]),
        Node("Punctuation", ["("]),
        Node("Punctuation", [")"]),
    ])

    i = 4
    if get_val(i) != "{":
        errors.append("❌ Missing opening '{'")
        return parse_tree, errors
    i += 1

    body_node = Node("Body", [])

    while i < n and get_val(i) != "}":
        token_type, token_value = tokens[i]

        # ✅ Handle declarations
        if token_value in ("int", "float"):
            decl_node = Node("Declaration", [])
            decl_node.children.append(Node("Type", [token_value]))
            i += 1
            while i < n and get_val(i) not in {";", "}"}:
                decl_node.children.append(Node(tokens[i][0], [get_val(i)]))
                i += 1
            body_node.children.append(decl_node)
            if get_val(i) == ";":
                i += 1
            continue

        # ✅ Handle if statement
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
                i += 1
            if get_val(i) == "{":
                body = Node("IfBody", [])
                i += 1
                while i < n and get_val(i) != "}":
                    body.children.append(Node(tokens[i][0], [get_val(i)]))
                    i += 1
                i += 1
                if_node.children.append(body)

            # Check for else
            if i < n and get_val(i) == "else":
                else_node = Node("ElseStatement", [Node("Keyword", ["else"])])
                i += 1
                if get_val(i) == "{":
                    else_body = Node("ElseBody", [])
                    i += 1
                    while i < n and get_val(i) != "}":
                        else_body.children.append(Node(tokens[i][0], [get_val(i)]))
                        i += 1
                    else_node.children.append(else_body)
                    i += 1
                if_node.children.append(else_node)
            body_node.children.append(if_node)
            continue

        # ✅ Handle while loop
        elif token_value == "while":
            while_node = Node("WhileLoop", [Node("Keyword", ["while"])])
            i += 1
            if get_val(i) == "(":
                cond = Node("Condition", [])
                i += 1
                while i < n and get_val(i) != ")":
                    cond.children.append(Node(tokens[i][0], [get_val(i)]))
                    i += 1
                while_node.children.append(cond)
                i += 1
            if get_val(i) == "{":
                loop_body = Node("LoopBody", [])
                i += 1
                while i < n and get_val(i) != "}":
                    loop_body.children.append(Node(tokens[i][0], [get_val(i)]))
                    i += 1
                while_node.children.append(loop_body)
                i += 1
            body_node.children.append(while_node)
            continue

        # ✅ Handle for loop
        elif token_value == "for":
            for_node = Node("ForLoop", [Node("Keyword", ["for"])])
            i += 1
            if get_val(i) == "(":
                header = Node("Header", [])
                i += 1
                while i < n and get_val(i) != ")":
                    header.children.append(Node(tokens[i][0], [get_val(i)]))
                    i += 1
                for_node.children.append(header)
                i += 1
            if get_val(i) == "{":
                loop_body = Node("LoopBody", [])
                i += 1
                while i < n and get_val(i) != "}":
                    loop_body.children.append(Node(tokens[i][0], [get_val(i)]))
                    i += 1
                for_node.children.append(loop_body)
                i += 1
            body_node.children.append(for_node)
            continue

        else:
            # Generic statement (assignment or return)
            stmt_node = Node("Statement", [Node(token_type, [token_value])])
            i += 1
            while i < n and get_val(i) != ";":
                stmt_node.children.append(Node(tokens[i][0], [get_val(i)]))
                i += 1
            if get_val(i) == ";":
                i += 1
            body_node.children.append(stmt_node)

    parse_tree.children.append(func_node)
    func_node.children.append(Node("Punctuation", ["{"]))
    func_node.children.append(body_node)
    func_node.children.append(Node("Punctuation", ["}"]))

    return parse_tree, errors
