"""
Tập 1 — Bao gồm 4 dạng (độc lập):
- Dạng 1: Mặt phẳng qua điểm và biết VTPT — Ví dụ 10, Câu 1
- Dạng 2: Mặt phẳng qua điểm và vuông góc một trục tọa độ — Câu 2
- Dạng 3: Mặt phẳng qua điểm và vuông góc với đường thẳng — Ví dụ 11, Câu 3
- Dạng 4: Mặt phẳng qua điểm và song song với một mặt phẳng cho trước — Ví dụ 12, Câu 4

Chạy: python3 plane_true_false_part_B_set1.py [số_câu]
Sinh ra: plane_true_false_part_B_set1.tex
"""

import random
import math
from typing import List, Tuple, Dict


# -------------------- Simple formatters --------------------

def format_point(pt: Tuple[int, int, int]) -> str:
    return f"({pt[0]};{pt[1]};{pt[2]})"


def format_vec(v: Tuple[int, int, int]) -> str:
    return f"({v[0]};{v[1]};{v[2]})"


def format_sqrt_expression(coeff: int, under_sqrt: int) -> str:
    if under_sqrt == 1:
        return str(coeff)
    elif coeff == 1:
        return f"\\sqrt{{{under_sqrt}}}"
    elif coeff == -1:
        return f"-\\sqrt{{{under_sqrt}}}"
    else:
        return f"{coeff}\\sqrt{{{under_sqrt}}}"


def format_plane_equation_with_sqrt(a: int, b: int, c: int, d_base: int, d_sqrt_coeff: int = 0, d_sqrt_under: int = 1) -> str:
    parts: List[str] = []

    # x term
    if a == 1:
        parts.append("x")
    elif a == -1:
        parts.append("-x")
    elif a != 0:
        parts.append(f"{a}x")

    # y term
    if b != 0:
        if parts:
            if b == 1:
                parts.append("+ y")
            elif b == -1:
                parts.append("- y")
            elif b > 0:
                parts.append(f"+ {b}y")
            else:
                parts.append(f"- {abs(b)}y")
        else:
            if b == 1:
                parts.append("y")
            elif b == -1:
                parts.append("-y")
            else:
                parts.append(f"{b}y")

    # z term
    if c != 0:
        if parts:
            if c == 1:
                parts.append("+ z")
            elif c == -1:
                parts.append("- z")
            elif c > 0:
                parts.append(f"+ {c}z")
            else:
                parts.append(f"- {abs(c)}z")
        else:
            if c == 1:
                parts.append("z")
            elif c == -1:
                parts.append("-z")
            else:
                parts.append(f"{c}z")

    # constant d_base
    if d_base != 0:
        if parts:
            if d_base > 0:
                parts.append(f"+ {d_base}")
            else:
                parts.append(f"- {abs(d_base)}")
        else:
            parts.append(str(d_base))

    if d_sqrt_coeff != 0:
        sqrt_expr = format_sqrt_expression(abs(d_sqrt_coeff), d_sqrt_under)
        if parts:
            if d_sqrt_coeff > 0:
                parts.append(f"+ {sqrt_expr}")
            else:
                parts.append(f"- {sqrt_expr}")
        else:
            if d_sqrt_coeff > 0:
                parts.append(sqrt_expr)
            else:
                parts.append(f"-{sqrt_expr}")

    if not parts:
        parts.append("0")

    return " ".join(parts) + " = 0"


def format_plane_equation(a: int, b: int, c: int, d: int) -> str:
    return format_plane_equation_with_sqrt(a, b, c, d, 0, 1)


# -------------------- Vector helpers --------------------

def cross(u: Tuple[int, int, int], v: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return (u[1]*v[2] - u[2]*v[1], u[2]*v[0] - u[0]*v[2], u[0]*v[1] - u[1]*v[0])


def subtract(p: Tuple[int, int, int], q: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return (p[0]-q[0], p[1]-q[1], p[2]-q[2])


def is_zero_vector(v: Tuple[int, int, int]) -> bool:
    return v[0] == 0 and v[1] == 0 and v[2] == 0


def are_parallel(u: Tuple[int, int, int], v: Tuple[int, int, int]) -> bool:
    return cross(u, v) == (0, 0, 0)


def flip_one_nonzero_component(n: Tuple[int, int, int]) -> Tuple[int, int, int]:
    a, b, c = n
    nonzero = [(a != 0), (b != 0), (c != 0)]
    if sum(nonzero) >= 2:
        if a != 0:
            return (-a, b, c)
        if b != 0:
            return (a, -b, c)
        return (a, b, -c)
    if sum(nonzero) == 1:
        if a != 0:
            return (a, 1, 0)
        if b != 0:
            return (1, b, 0)
        return (1, 0, c)
    return (1, 0, 0)


# -------------------- Plane normalization & linear form helpers --------------------

def _gcd_two(x: int, y: int) -> int:
    return math.gcd(abs(x), abs(y))


def gcd_list(values: Tuple[int, int, int, int]) -> int:
    g = 0
    for v in values:
        g = _gcd_two(g, v)
    return g if g != 0 else 1


def normalize_plane_coeffs(a: int, b: int, c: int, d: int) -> Tuple[int, int, int, int]:
    g = gcd_list((a, b, c, d))
    a //= g
    b //= g
    c //= g
    d //= g
    # Fix the overall sign to make representation unique
    if a < 0 or (a == 0 and b < 0) or (a == 0 and b == 0 and c < 0):
        a, b, c, d = -a, -b, -c, -d
    return a, b, c, d


def choose_linear_form_coeffs() -> Tuple[int, int, int, int]:
    while True:
        p = random.randint(-3, 3)
        q = random.randint(-3, 3)
        r = random.randint(-3, 3)
        s = random.randint(-3, 3)
        if not (p == 0 and q == 0 and r == 0 and s == 0):
            return p, q, r, s


def format_linear_form(p: int, q: int, r: int, s: int) -> str:
    parts: List[str] = []
    def add(term_coeff: int, symbol: str):
        if term_coeff == 0:
            return
        if not parts:
            if term_coeff == 1:
                parts.append(symbol)
            elif term_coeff == -1:
                parts.append(f"-{symbol}")
            else:
                parts.append(f"{term_coeff}{symbol}")
        else:
            if term_coeff == 1:
                parts.append(f"+ {symbol}")
            elif term_coeff == -1:
                parts.append(f"- {symbol}")
            elif term_coeff > 0:
                parts.append(f"+ {term_coeff}{symbol}")
            else:
                parts.append(f"- {abs(term_coeff)}{symbol}")
    add(p, "A")
    add(q, "B")
    add(r, "C")
    add(s, "D")
    return " ".join(parts) if parts else "0"


def evaluate_linear_form(p: int, q: int, r: int, s: int, a: int, b: int, c: int, d: int) -> int:
    return p * a + q * b + r * c + s * d


def pick_wrong_value(true_value: int) -> int:
    deltas = [i for i in range(-6, 7) if i != 0]
    random.shuffle(deltas)
    for delta in deltas:
        if true_value + delta != true_value:
            return true_value + delta
    return true_value + 1


# -------------------- Propositions (4 dạng) --------------------

# Dạng 1: Qua điểm và biết VTPT (Ví dụ 10, Câu 1)
def prop_plane_point_normal() -> Dict[str, str]:
    points = [(random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)) for _ in range(3)]
    # Random nonzero normals
    normals = []
    for _ in range(3):
        while True:
            n = (random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3))
            if n[0] != 0 or n[1] != 0 or n[2] != 0:
                normals.append(n)
                break
    pt = random.choice(points)
    n = random.choice(normals)
    a, b, c = n
    d = -(a * pt[0] + b * pt[1] + c * pt[2])
    a, b, c, d = normalize_plane_coeffs(a, b, c, d)
    p, q, r, s = choose_linear_form_coeffs()
    expr_str = format_linear_form(p, q, r, s)
    value_true = evaluate_linear_form(p, q, r, s, a, b, c, d)
    value_false = pick_wrong_value(value_true)
    base = (
        f"Cho mặt phẳng (P) có dạng Ax+By+Cz+D=0, đi qua M{format_point(pt)} và có véctơ pháp tuyến song song với "
        f"\\(\\vec n={format_vec(n)}\\). Khi đó {expr_str} = {value_true}."
    )
    base_false = (
        f"Cho mặt phẳng (P) có dạng Ax+By+Cz+D=0, đi qua M{format_point(pt)} và có véctơ pháp tuyến song song với "
        f"\\(\\vec n={format_vec(n)}\\). Khi đó {expr_str} = {value_false}."
    )
    return {"true": base, "false": base_false}


# Dạng 2: Qua điểm và vuông góc một trục (Câu 2)
def prop_plane_perpendicular_axis() -> Dict[str, str]:
    axes = [("Ox", (1, 0, 0), 0), ("Oy", (0, 1, 0), 1), ("Oz", (0, 0, 1), 2)]
    points = [(random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)) for _ in range(4)]
    axis_name, normal, coord_idx = random.choice(axes)
    point = random.choice(points)
    a, b, c = normal
    d = -(a * point[0] + b * point[1] + c * point[2])
    a, b, c, d = normalize_plane_coeffs(a, b, c, d)
    p, q, r, s = choose_linear_form_coeffs()
    expr_str = format_linear_form(p, q, r, s)
    value_true = evaluate_linear_form(p, q, r, s, a, b, c, d)
    value_false = pick_wrong_value(value_true)
    true_text = (
        f"Cho mặt phẳng (P) có dạng Ax+By+Cz+D=0, đi qua M{format_point(point)} và vuông góc với trục {axis_name}. "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho mặt phẳng (P) có dạng Ax+By+Cz+D=0, đi qua M{format_point(point)} và vuông góc với trục {axis_name}. "
        f"Khi đó {expr_str} = {value_false}."
    )
    return {"true": true_text, "false": false_text}


# Dạng 3: Qua điểm và vuông góc đường thẳng (Ví dụ 11, Câu 3)
def prop_plane_perpendicular_line() -> Dict[str, str]:
    A_coords = [(random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)) for _ in range(4)]
    B_coords = [(random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)) for _ in range(4)]
    while True:
        A = random.choice(A_coords)
        B = random.choice(B_coords)
        AB = subtract(B, A)
        if not is_zero_vector(AB):
            break
    a, b, c = AB
    d = -(a * A[0] + b * A[1] + c * A[2])
    a, b, c, d = normalize_plane_coeffs(a, b, c, d)
    p, q, r, s = choose_linear_form_coeffs()
    expr_str = format_linear_form(p, q, r, s)
    value_true = evaluate_linear_form(p, q, r, s, a, b, c, d)
    value_false = pick_wrong_value(value_true)
    true_text = (
        f"Cho (P) có dạng Ax+By+Cz+D=0 đi qua A{format_point(A)} và vuông góc với đường thẳng AB, với B{format_point(B)}. "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho (P) có dạng Ax+By+Cz+D=0 đi qua A{format_point(A)} và vuông góc với đường thẳng AB, với B{format_point(B)}. "
        f"Khi đó {expr_str} = {value_false}."
    )
    return {"true": true_text, "false": false_text}


# Dạng 4: Qua điểm và song song mặt phẳng (Ví dụ 12, Câu 4)
def prop_plane_parallel_to_plane() -> Dict[str, str]:
    points = [(random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)) for _ in range(4)]
    plane_coeffs = [(random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)) for _ in range(3)]
    A = random.choice(points)
    while True:
        a0, b0, c0, d_orig = random.choice(plane_coeffs)
        normal = (a0, b0, c0)
        if not is_zero_vector(normal):
            break
    a, b, c = normal
    d = -(a * A[0] + b * A[1] + c * A[2])
    a, b, c, d = normalize_plane_coeffs(a, b, c, d)
    p, q, r, s = choose_linear_form_coeffs()
    expr_str = format_linear_form(p, q, r, s)
    value_true = evaluate_linear_form(p, q, r, s, a, b, c, d)
    value_false = pick_wrong_value(value_true)
    true_text = (
        f"Cho (Q): {format_plane_equation(a0, b0, c0, d_orig)}. Mặt phẳng (P) có dạng Ax+By+Cz+D=0 đi qua A{format_point(A)} và song song với (Q). "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho (Q): {format_plane_equation(a0, b0, c0, d_orig)}. Mặt phẳng (P) có dạng Ax+By+Cz+D=0 đi qua A{format_point(A)} và song song với (Q). "
        f"Khi đó {expr_str} = {value_false}."
    )
    return {"true": true_text, "false": false_text}


# -------------------- Document builders --------------------

def generate_question(question_number: int) -> str:
    gens = [
        prop_plane_point_normal,
        prop_plane_perpendicular_axis,
        prop_plane_perpendicular_line,
        prop_plane_parallel_to_plane,
    ]
    propositions: List[Dict[str, str]] = [gen() for gen in gens]
    num_true = random.randint(1, 4)
    true_indices = set(random.sample(range(4), num_true))
    option_labels = ['a', 'b', 'c', 'd']
    content = f"Câu {question_number}: Chọn các mệnh đề đúng.\n\n"
    for i in range(4):
        text = propositions[i]['true'] if i in true_indices else propositions[i]['false']
        marker = '*' if i in true_indices else ''
        content += f"{marker}{option_labels[i]}) {text}\n\n"
    return content


def create_latex_document(questions: List[str], title: str = "Các bài toán về viết phương trình mặt phẳng - Đúng/Sai (Tập 1)") -> str:
    latex = (
        "\\documentclass[a4paper,12pt]{article}\n"
        "\\usepackage{amsmath,amssymb}\n"
        "\\usepackage{geometry}\n"
        "\\geometry{a4paper, margin=1in}\n"
        "\\usepackage{polyglossia}\n"
        "\\setmainlanguage{vietnamese}\n"
        "\\setmainfont{Times New Roman}\n"
        "\\begin{document}\n\n"
        f"\\section*{{{title}}}\n\n"
    )
    latex += "\n\n".join(questions)
    latex += "\n\n\\end{document}"
    return latex


def main():
    import sys
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    except Exception:
        num_questions = 5
    questions = [generate_question(i+1) for i in range(num_questions)]
    tex = create_latex_document(questions)
    out = "plane_true_false_part_B_set1.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(questions)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()


