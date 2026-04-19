import sys

def format_replacements(content):
    content = content.replace("M(a, b, c)", "\\(M(a, b, c)\\)")
    content = content.replace("N(x, y, z)", "\\(N(x, y, z)\\)")
    content = content.replace("M(p, q, r)", "\\(M(p, q, r)\\)")
    content = content.replace("N(k, l, e)", "\\(N(k, l, e)\\)")

    fn_old = '''def format_param_line(base: Point, direction: Vector) -> str:
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
    joined = " \\\\\\\\\\n".join(rows)
    return "\\\\heva{\\n" + joined + "\\n}"'''

    fn_new = '''def format_param_line(base: Point, direction: Vector) -> str:
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
    return "\\\\{ " + joined + " \\\\}"'''

    return content.replace(fn_old, fn_new)

filepath = "/home/haiquy/PycharmProjects/FomularLatex/2025/04_11/duongthang_matphang_matcau_3.py"
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

text = format_replacements(text)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)

print("done")
