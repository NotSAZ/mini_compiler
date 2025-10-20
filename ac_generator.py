from lexer import lexical_analysis
from parser import parse

label_counter = 1
temp_counter = 1

# --- TAC helpers ---
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

# --- TAC generation functions ---
from tac_generator import generate_tac_from_node  # reuse your existing TAC generator
# generate_expression_tac and display_tac already in tac_generator

# --- Assembly generation ---
def generate_assembly(tac_lines):
    assembly = []
    reg_map = {}
    reg_count = 1

    def get_reg(v):
        nonlocal reg_count
        # Numeric constants
        if v.replace('.', '', 1).isdigit():
            return v
        # String literals
        if v.startswith('"') and v.endswith('"'):
            return v
        # Map variables to registers
        if v not in reg_map:
            reg_map[v] = f"R{reg_count}"
            reg_count += 1
        return reg_map[v]

    for line in tac_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # IF_FALSE ... GOTO
        if line.startswith("IF_FALSE"):
            parts = line.split()
            _, cond_var, _, label = parts
            r = get_reg(cond_var)
            assembly.append(f"CMP {r}, 0")
            assembly.append(f"JE {label}")

        # GOTO label
        elif line.startswith("GOTO"):
            _, label = line.split()
            assembly.append(f"JMP {label}")

        # LABEL label
        elif line.startswith("LABEL"):
            _, label = line.split()
            assembly.append(f"{label}:")

        # Assignment / arithmetic
        elif "=" in line:
            lhs, rhs = [x.strip() for x in line.split("=", 1)]
            dest = get_reg(lhs)
            parts = rhs.split()

            if len(parts) == 3 and parts[1] in {"+", "-", "*", "/"}:
                r1, op, r2 = get_reg(parts[0]), parts[1], get_reg(parts[2])
                if op == "+": assembly.append(f"ADD {dest}, {r1}, {r2}")
                elif op == "-": assembly.append(f"SUB {dest}, {r1}, {r2}")
                elif op == "*": assembly.append(f"MUL {dest}, {r1}, {r2}")
                elif op == "/": assembly.append(f"DIV {dest}, {r1}, {r2}")
            else:
                src = get_reg(rhs)
                assembly.append(f"MOV {dest}, {src}")

        # PRINT statement
        elif line.startswith("PRINT"):
            parts = line[len("PRINT"):].strip()
            items = [p.strip() for p in parts.split(",")]
            asm_line = "PRINT " + " ".join(get_reg(it) for it in items)
            assembly.append(asm_line)

        # RETURN statement
        elif line.startswith("RETURN"):
            parts = line[len("RETURN"):].strip()
            if parts:
                r = get_reg(parts)
                assembly.append(f"MOV R0, {r}")
            assembly.append("RET")

        # Fallback
        else:
            r = get_reg(line)
            assembly.append(f"; standalone {r}")

    return assembly

def display_assembly(assembly):
    print("\n--- Assembly Code ---")
    for line in assembly:
        print(line)

# --- Run independently ---
if __name__ == "__main__":
    file_path = input("Enter the path of the C source file: ").strip()
    try:
        with open(file_path, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        exit(1)

    # Lexical analysis
    _, _, ordered_tokens = lexical_analysis(code)

    # Parsing
    parse_tree, _ = parse(ordered_tokens)

    # Generate TAC
    from tac_generator import generate_tac_from_node
    tac = generate_tac_from_node(parse_tree)

    # Generate assembly
    assembly = generate_assembly(tac)
    display_assembly(assembly)
