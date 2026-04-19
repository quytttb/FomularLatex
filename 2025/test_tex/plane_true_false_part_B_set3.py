"""
Tập 3 — Bao gồm 4 dạng (độc lập):
- Dạng 9: Mặt phẳng chứa một trục (Ox/Oy/Oz) — Ví dụ 16, Câu 9
- Dạng 10: Mặt phẳng qua hai điểm, song song một trục — Ví dụ 17, Câu 10
- Dạng 11: Mặt phẳng qua hai điểm, song song một đường thẳng — Ví dụ 18, Câu 11
- Dạng 12: Mặt phẳng qua hai điểm, vuông góc với một mặt phẳng cho trước — Câu 12

Chạy: python3 plane_true_false_part_B_set3.py [số_câu]
Sinh ra: plane_true_false_part_B_set3.tex
"""

import random
import math
from typing import List, Tuple, Dict


# -------------------- Simple formatters --------------------

def format_point(pt: Tuple[int, int, int]) -> str:
    return f"({pt[0]};{pt[1]};{pt[2]})"


def format_vec(v: Tuple[int, int, int]) -> str:
    return f"({v[0]};{v[1]};{v[2]})"


def format_plane_equation(a: int, b: int, c: int, d: int) -> str:
    parts: List[str] = []
    if a == 1:
        parts.append("x")
    elif a == -1:
        parts.append("-x")
    elif a != 0:
        parts.append(f"{a}x")
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
            parts.append("y" if b == 1 else ("-y" if b == -1 else f"{b}y"))
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
            parts.append("z" if c == 1 else ("-z" if c == -1 else f"{c}z"))
    if d != 0:
        if d > 0:
            parts.append(f"+ {d}")
        else:
            parts.append(f"- {abs(d)}")
    if not parts:
        parts.append("0")
    return " ".join(parts) + " = 0"


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


# -------------------- Propositions (4 dạng: 9–12) --------------------

# Dạng 9: Mặt phẳng chứa trục (Ox/Oy/Oz)
def prop_plane_contains_axis() -> Dict[str, str]:
    axes = [("Ox", (1, 0, 0)), ("Oy", (0, 1, 0)), ("Oz", (0, 0, 1))]
    points = [(random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)) for _ in range(4)]
    M = random.choice(points)
    axis_name, axis_vec = random.choice(axes)
    if axis_name == "Ox":
        a, b, c = 0, M[2], -M[1]
    elif axis_name == "Oy":
        a, b, c = M[2], 0, -M[0]
    else:
        a, b, c = M[1], -M[0], 0
    d = 0
    a, b, c, d = normalize_plane_coeffs(a, b, c, d)
    p, q, r, s = choose_linear_form_coeffs()
    expr_str = format_linear_form(p, q, r, s)
    value_true = evaluate_linear_form(p, q, r, s, a, b, c, d)
    value_false = pick_wrong_value(value_true)
    true_text = (
        f"Cho (P) có dạng Ax+By+Cz+D=0 chứa trục {axis_name} và đi qua M{format_point(M)}. "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho (P) có dạng Ax+By+Cz+D=0 chứa trục {axis_name} và đi qua M{format_point(M)}. "
        f"Khi đó {expr_str} = {value_false}."
    )
    return {"true": true_text, "false": false_text}


# Dạng 10: Qua 2 điểm và song song trục
def prop_plane_parallel_to_axis() -> Dict[str, str]:
    point_pairs = [
        ((1, 0, 1), (-1, 2, 2)),
        ((0, 1, 2), (2, -1, 1)),
        ((2, 0, 1), (0, 2, 3)),
        ((-1, 1, 0), (1, 0, 2))
    ]
    A, B = random.choice(point_pairs)
    axes = [("Ox", (1, 0, 0)), ("Oy", (0, 1, 0)), ("Oz", (0, 0, 1))]
    axis_name, axis_vec = random.choice(axes)
    AB = subtract(B, A)
    while True:
        n = cross(AB, axis_vec)
        if not is_zero_vector(n):
            break
        axis_name, axis_vec = random.choice(axes)
    a, b, c = n
    d = -(a * A[0] + b * A[1] + c * A[2])
    a, b, c, d = normalize_plane_coeffs(a, b, c, d)
    p, q, r, s = choose_linear_form_coeffs()
    expr_str = format_linear_form(p, q, r, s)
    value_true = evaluate_linear_form(p, q, r, s, a, b, c, d)
    value_false = pick_wrong_value(value_true)
    true_text = (
        f"Cho (P) có dạng Ax+By+Cz+D=0 đi qua A{format_point(A)}, B{format_point(B)} và song song trục {axis_name}. "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho (P) có dạng Ax+By+Cz+D=0 đi qua A{format_point(A)}, B{format_point(B)} và song song trục {axis_name}. "
        f"Khi đó {expr_str} = {value_false}."
    )
    return {"true": true_text, "false": false_text}


# Dạng 11: Qua 2 điểm và song song đường thẳng CD
def prop_plane_through_points_parallel_line() -> Dict[str, str]:
    AB_sets = [((1, 1, 0), (0, 2, 1)), ((2, 0, 1), (1, 3, 2)), ((0, 1, 2), (2, 0, 1)), ((1, 2, 0), (0, 1, 3))]
    CD_sets = [((1, 0, 2), (1, 1, 1)), ((2, 1, 0), (2, 2, -1)), ((0, 2, 1), (0, 3, 0)), ((3, 0, 1), (3, 1, 0))]
    A, B = random.choice(AB_sets)
    C, Dp = random.choice(CD_sets)
    while True:
        AB = subtract(B, A)
        CD = subtract(Dp, C)
        n = cross(AB, CD)
        if not is_zero_vector(n):
            break
    a, b, c = n
    d = -(a * A[0] + b * A[1] + c * A[2])
    a, b, c, d = normalize_plane_coeffs(a, b, c, d)
    p, q, r, s = choose_linear_form_coeffs()
    expr_str = format_linear_form(p, q, r, s)
    value_true = evaluate_linear_form(p, q, r, s, a, b, c, d)
    value_false = pick_wrong_value(value_true)
    true_text = (
        f"Cho A{format_point(A)}, B{format_point(B)}, C{format_point(C)}, D{format_point(Dp)}. (P) có dạng Ax+By+Cz+D=0 đi qua A, B và song song CD. "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho A{format_point(A)}, B{format_point(B)}, C{format_point(C)}, D{format_point(Dp)}. (P) có dạng Ax+By+Cz+D=0 đi qua A, B và song song CD. "
        f"Khi đó {expr_str} = {value_false}."
    )
    return {"true": true_text, "false": false_text}


# Dạng 12: Qua 2 điểm và vuông góc với một mặt phẳng (mới)
def prop_plane_two_points_perpendicular_plane() -> Dict[str, str]:
    # Chọn hai điểm A, B và một mặt phẳng Q: a x + b y + c z + d = 0
    points = [
        (random.randint(-2, 3), random.randint(-2, 3), random.randint(-2, 3))
        for _ in range(6)
    ]
    planes = [
        (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2), random.randint(-5, 5))
        for _ in range(6)
    ]
    while True:
        A = random.choice(points)
        B = random.choice(points)
        if A == B:
            continue
        aQ, bQ, cQ, dQ = random.choice(planes)
        nQ = (aQ, bQ, cQ)
        if is_zero_vector(nQ):
            continue
        AB = subtract(B, A)
        nP = cross(AB, nQ)
        if not is_zero_vector(nP):
            break
    a, b, c = nP
    d = -(a * A[0] + b * A[1] + c * A[2])
    a, b, c, d = normalize_plane_coeffs(a, b, c, d)
    p, q, r, s = choose_linear_form_coeffs()
    expr_str = format_linear_form(p, q, r, s)
    value_true = evaluate_linear_form(p, q, r, s, a, b, c, d)
    value_false = pick_wrong_value(value_true)
    Q_desc = f"{aQ}x+{bQ}y+{cQ}z+{dQ}=0"
    true_text = (
        f"Cho A{format_point(A)}, B{format_point(B)} và (Q): {Q_desc}. (P) có dạng Ax+By+Cz+D=0 đi qua A, B và vuông góc (Q). "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho A{format_point(A)}, B{format_point(B)} và (Q): {Q_desc}. (P) có dạng Ax+By+Cz+D=0 đi qua A, B và vuông góc (Q). "
        f"Khi đó {expr_str} = {value_false}."
    )
    return {"true": true_text, "false": false_text}


# -------------------- Document builders --------------------

def generate_question(question_number: int) -> str:
    gens = [
        prop_plane_contains_axis,
        prop_plane_parallel_to_axis,
        prop_plane_through_points_parallel_line,
        prop_plane_two_points_perpendicular_plane,
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


def create_latex_document(questions: List[str], title: str = "Các bài toán về viết phương trình mặt phẳng - Đúng/Sai (Tập 3)") -> str:
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
    out = "plane_true_false_part_B_set3.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(questions)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()


