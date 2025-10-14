import re

def generate_tac(expression):
    expression = expression.replace(";", "").strip()
    expression = expression.replace("x", "*").replace("–", "-")

    if "=" not in expression:
        return ["Error: No assignment operator found."]

    # Handle chained assignments like a = b = c + 5
    lhs_list = [var.strip() for var in expression.split("=")[:-1]]
    rhs = expression.split("=")[-1].strip()

    # Convert unary minus to '0 - x'
    rhs = re.sub(r'(?<=\()-(?=\w)', '0 - ', rhs)
    rhs = re.sub(r'^-(?=\w)', '0 - ', rhs)

    # Tokenize RHS
    tokens = []
    cur = ""
    for ch in rhs:
        if ch in "+-*/()":
            if cur:
                tokens.append(cur.strip())
                cur = ""
            tokens.append(ch)
        elif ch != " ":
            cur += ch
    if cur:
        tokens.append(cur.strip())
    if cur:
        tokens.append(cur.strip())

    operand_stack = []
    operator_stack = []
    tac = []
    t = 1

    # Operator precedence
    def prec(op):
        return 2 if op in ("*", "/") else 1 if op in ("+", "-") else 0

    # Apply operator strictly step by step
    def apply_op(op):
        nonlocal t
        if len(operand_stack) < 2:
            raise ValueError(f"Not enough operands to apply operator '{op}'")
        r = operand_stack.pop()
        l = operand_stack.pop()
        temp = f"t{t}"
        tac.append(f"{temp} = {l} {op} {r}")
        operand_stack.append(temp)
        t += 1

    # Process tokens
    for token in tokens:
        if token.isalnum():
            operand_stack.append(token)
        elif token == "(":
            operator_stack.append(token)
        elif token == ")":
            while operator_stack and operator_stack[-1] != "(":
                apply_op(operator_stack.pop())
            if operator_stack:
                operator_stack.pop()  # Remove '('
            else:
                raise ValueError("Mismatched parentheses")
        else:  # operator
            while operator_stack and operator_stack[-1] != "(" and prec(operator_stack[-1]) >= prec(token):
                apply_op(operator_stack.pop())
            operator_stack.append(token)

    while operator_stack:
        apply_op(operator_stack.pop())

    # Assign final result to all LHS variables (handle chained assignments)
    final_result = operand_stack[-1]
    for lhs in reversed(lhs_list):
        tac.append(f"{lhs} = {final_result}")
        final_result = lhs

    return tac


def display_tac(tac):
    print("\n--- Three Address Code (TAC) ---")
    for line in tac:
        print(line)
