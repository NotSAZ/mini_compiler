from parser import parse, Node
from lexer import lexical_analysis

label_counter = 1
temp_counter = 1

def new_label():
    global label_counter
    lbl = f"L{label_counter}"
    label_counter += 1
    return lbl

def new_temp():
    global temp_counter
    tmp = f"t{temp_counter}"
    temp_counter += 1
    return tmp

def generate_tac_from_node(node, tac=None):
    """Recursively traverse parse tree node to generate TAC."""
    if tac is None:
        tac = []

    # --- Declaration ---
    if node.name == "Declaration":
        if len(node.children) > 1:
            lhs_node = node.children[0]
            lhs = lhs_node.children[0] if hasattr(lhs_node, "children") else lhs_node

            # handle initializer if exists
            if len(node.children) > 1:
                rhs_node = Node("Expr", [node.children[1]])
                rhs_temp = generate_expression_tac(rhs_node, tac)
                tac.append(f"{lhs} = {rhs_temp}")

    # --- Assignment / Statement ---
    elif node.name == "Statement":
        if len(node.children) >= 3:
            lhs = node.children[0].children[0]
            op = node.children[1].children[0]
            rhs_node = Node("Expr", [node.children[2]])
            rhs_temp = generate_expression_tac(rhs_node, tac)
            if op == "=":
                tac.append(f"{lhs} = {rhs_temp}")

    # --- Return ---
    elif node.name == "ReturnStatement":
        ret_val = ""
        if node.children[1:]:
            rhs_node = Node("Expr", node.children[1:])
            ret_val = generate_expression_tac(rhs_node, tac)
        tac.append(f"RETURN {ret_val if ret_val else 0}")

    # --- Print ---
    elif node.name == "PrintStatement":
        args = []
        for c in node.children:
            if c.name == "Arguments":
                args = [ch.children[0] for ch in c.children]
        tac.append(f"PRINT {', '.join(args)}")

    # --- If / Else ---
    elif node.name == "IfStatement":
        cond_node = next((c for c in node.children if c.name == "Condition"), None)
        if_body = next((c for c in node.children if c.name == "IfBody"), None)
        else_node = next((c for c in node.children if c.name == "ElseStatement"), None)

        cond_temp = generate_expression_tac(cond_node, tac) if cond_node else ""

        lbl_false = new_label()
        lbl_end = new_label()

        tac.append(f"IF_FALSE {cond_temp} GOTO {lbl_false}")
        if if_body:
            for stmt in if_body.children:
                generate_tac_from_node(stmt, tac)
        tac.append(f"GOTO {lbl_end}")
        tac.append(f"LABEL {lbl_false}")

        if else_node:
            for stmt in else_node.children:
                if stmt.name.endswith("Body"):
                    for s in stmt.children:
                        generate_tac_from_node(s, tac)
        tac.append(f"LABEL {lbl_end}")

    # --- While Loop ---
    elif node.name == "WhileLoop":
        cond_node = next((c for c in node.children if c.name == "Condition"), None)
        body_node = next((c for c in node.children if c.name == "LoopBody"), None)

        lbl_start = new_label()
        lbl_end = new_label()
        tac.append(f"LABEL {lbl_start}")

        if cond_node:
            cond_temp = generate_expression_tac(cond_node, tac)
            tac.append(f"IF_FALSE {cond_temp} GOTO {lbl_end}")

        if body_node:
            for stmt in body_node.children:
                generate_tac_from_node(stmt, tac)

        tac.append(f"GOTO {lbl_start}")
        tac.append(f"LABEL {lbl_end}")

    # --- For Loop ---
    elif node.name == "ForLoop":
        header_node = next((c for c in node.children if c.name == "Header"), None)
        body_node = next((c for c in node.children if c.name == "LoopBody"), None)

        # Init
        if header_node:
            for i in range(len(header_node.children) - 2):
                ch1, ch2, ch3 = header_node.children[i:i+3]
                lhs, op, rhs = ch1.children[0], ch2.children[0], ch3.children[0]
                if op == "=":
                    rhs_node = Node("Expr", [ch3])
                    rhs_temp = generate_expression_tac(rhs_node, tac)
                    tac.append(f"{lhs} = {rhs_temp}")
                    break

        lbl_start = new_label()
        lbl_end = new_label()
        tac.append(f"LABEL {lbl_start}")

        # Condition
        if header_node:
            for i in range(1, len(header_node.children) - 1):
                ch2 = header_node.children[i]
                if hasattr(ch2, "children") and ch2.children[0] in ("<", "<=", ">", ">=", "==", "!="):
                    lhs = header_node.children[i-1].children[0]
                    op = ch2.children[0]
                    rhs = header_node.children[i+1].children[0]
                    cond_temp = new_temp()
                    tac.append(f"{cond_temp} = {lhs} {op} {rhs}")
                    tac.append(f"IF_FALSE {cond_temp} GOTO {lbl_end}")
                    break

        # Body
        if body_node:
            for stmt in body_node.children:
                generate_tac_from_node(stmt, tac)

        # Increment
        if header_node:
            for i in range(1, len(header_node.children)):
                ch = header_node.children[i]
                if hasattr(ch, "children") and ch.children[0] in ("++", "--"):
                    var = header_node.children[i-1].children[0]
                    tac.append(f"{var} = {var} + 1" if ch.children[0] == "++" else f"{var} = {var} - 1")

        tac.append(f"GOTO {lbl_start}")
        tac.append(f"LABEL {lbl_end}")

    else:
        # Recursive call for other nodes
        for child in node.children:
            if isinstance(child, Node):
                generate_tac_from_node(child, tac)

    return tac


def generate_expression_tac(node, tac):
    """Convert expression node to a temporary variable."""
    expr_parts = []
    for c in node.children:
        if hasattr(c, "children"):
            expr_parts.append(str(c.children[0]))
    temp = new_temp()
    tac.append(f"{temp} = {' '.join(expr_parts)}")
    return temp


def display_tac(tac):
    print("\n--- Three Address Code (TAC) ---")
    for line in tac:
        print(line)


# --- Run independently ---
if __name__ == "__main__":
    import os
    file_path = input("Enter the path of the C source file: ").strip()
    if not os.path.exists(file_path):
        print(f"File '{file_path}' not found!")
        exit(1)

    with open(file_path, "r") as f:
        code = f.read()

    # Lexical analysis
    _, _, ordered_tokens = lexical_analysis(code)

    # Parse
    parse_tree, _ = parse(ordered_tokens)

    # Generate TAC
    tac = generate_tac_from_node(parse_tree)
    display_tac(tac)
