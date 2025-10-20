import re

def optimize_tac(tac_lines):
    optimized = []
    consts = {}  

    # Pass 1: Constant folding + propagation
    for line in tac_lines:
        line = line.strip()
        if not line:
            continue

        # Match arithmetic operations: t1 = 3 + 4
        m = re.match(r"(t\d+)\s*=\s*([0-9.]+)\s*([\+\-\*/])\s*([0-9.]+)", line)
        if m:
            var, a, op, b = m.groups()
            try:
                val = eval(f"{a}{op}{b}")
            except Exception:
                val = f"{a}{op}{b}"
            consts[var] = str(val)
            optimized.append(f"{var} = {val}")
            continue

        # Replace known constants in expressions
        for c, v in consts.items():
            line = re.sub(rf"\b{c}\b", v, line)

        # Propagate direct assignments (e.g., t2 = 5)
        assign_match = re.match(r"(t\d+)\s*=\s*([0-9.]+)$", line)
        if assign_match:
            consts[assign_match.group(1)] = assign_match.group(2)

        optimized.append(line)

    # Pass 2: Dead code elimination (remove temps never used)
    used = set()
    for line in optimized:
        # Find all temps used in expressions or conditions
        for t in re.findall(r"\bt\d+\b", line):
            used.add(t)

    final = []
    for line in optimized:
        assign_match = re.match(r"(t\d+)\s*=", line)
        if assign_match:
            lhs = assign_match.group(1)
            if lhs not in used:
                continue  # remove unused temp
        final.append(line)

    # Pass 3: Remove unused labels
    labels = set(re.findall(r"\bL\d+\b", " ".join(final)))
    cleaned = []
    for line in final:
        label_match = re.match(r"LABEL\s+(L\d+)", line)
        if label_match and label_match.group(1) not in labels:
            continue
        cleaned.append(line)

    # Pass 4: Remove redundant jumps (GOTO immediately before its label)
    compacted = []
    skip_next_label = None
    for i, line in enumerate(cleaned):
        if line.startswith("GOTO"):
            target = re.findall(r"L\d+", line)
            if target and i + 1 < len(cleaned):
                next_line = cleaned[i + 1]
                if next_line.strip() == f"LABEL {target[0]}":
                    # redundant jump
                    continue
        compacted.append(line)

    return compacted


def display_optimization(before, after):
    print("\n===== OPTIMIZATION =====")
    print("Before:")
    for i, line in enumerate(before, 1):
        print(f"({i}) {line}")
    print("\nAfter:")
    for i, line in enumerate(after, 1):
        print(f"({i}) {line}")
    print("========================\n")


if __name__ == "__main__":
    import os
    from tac_generator import generate_tac_from_node, display_tac
    from parser import parse
    from lexer import lexical_analysis

    file_path = input("Enter the path of the C source file: ").strip()
    if not os.path.exists(file_path):
        print(f"File '{file_path}' not found!")
        exit(1)

    with open(file_path, "r") as f:
        code = f.read()

    _, _, tokens = lexical_analysis(code)
    parse_tree, _ = parse(tokens)
    tac = generate_tac_from_node(parse_tree)

    optimized_tac = optimize_tac(tac)
    display_optimization(tac, optimized_tac)
