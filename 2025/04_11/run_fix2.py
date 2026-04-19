import sys

def fix():
    filepath = "/home/haiquy/PycharmProjects/FomularLatex/2025/04_11/duongthang_matphang_matcau_3.py"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace M(...) calls
    content = content.replace("m khi M(a, b, c) và N(x, y, z)", "m khi \\(M(a, b, c)\\) và \\(N(x, y, z)\\)")
    content = content.replace("M khi M(p, q, r) và N(k, l, e)", "M khi \\(M(p, q, r)\\) và \\(N(k, l, e)\\)")

    idx_start = content.find("def format_param_line(")
    idx_end = content.find("def format_canonical_line(", idx_start)

    old_func = content[idx_start:idx_end]
    new_func = '''def format_param_line(base: Point, direction: Vector) -> str:
    rows: List[str] = []
    for name, b, d in zip(("x", "y", "z"), base, direction):
        if d == 0:
            rows.append(f"{name} = {b}")
        else:
            sign = "+" if d > 0 else "-"
            coeff = abs(d)
            if coeff == 1:
                term = "t"
            else:
                term = f"{coeff}t"
            rows.append(f"{name} = {b} {sign} {term}")
    joined = "; ".join(rows)
    return "\\\\{ " + joined + " \\\\}"

'''
    content = content.replace(old_func, new_func)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed!")

fix()
