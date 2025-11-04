"""
Tập 2 — Bao gồm 4 dạng (độc lập):
- Dạng 5: Mặt phẳng qua điểm và song song với mặt phẳng tọa độ (Oxy/Oyz/Oxz) — Câu 5
- Dạng 6: Mặt phẳng trung trực của đoạn thẳng — Ví dụ 13, Câu 6
- Dạng 7: Mặt phẳng qua điểm và có hai véctơ chỉ phương — Ví dụ 14, Câu 7
- Dạng 8: Mặt phẳng qua ba điểm bất kỳ — Ví dụ 15, Câu 8

Chạy: python3 plane_true_false_part_B_set2.py [số_câu]
Sinh ra: plane_true_false_part_B_set2.tex
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


# -------------------- Propositions (4 dạng: 5–8) --------------------

# Dạng 5: Qua điểm và song song mp tọa độ (Oxy/Oyz/Oxz)
def prop_plane_parallel_coordinate_plane() -> Dict[str, str]:
    coordinate_planes = [("Oxy", (0, 0, 1)), ("Oyz", (1, 0, 0)), ("Oxz", (0, 1, 0))]
    points = [(random.randint(1, 5), random.randint(1, 5), random.randint(1, 5)) for _ in range(4)]
    plane_name, normal = random.choice(coordinate_planes)
    A = random.choice(points)
    a, b, c = normal
    d = -(a * A[0] + b * A[1] + c * A[2])
    a, b, c, d = normalize_plane_coeffs(a, b, c, d)
    p, q, r, s = choose_linear_form_coeffs()
    expr_str = format_linear_form(p, q, r, s)
    value_true = evaluate_linear_form(p, q, r, s, a, b, c, d)
    value_false = pick_wrong_value(value_true)
    true_text = (
        f"Cho mặt phẳng (P) có dạng Ax+By+Cz+D=0, đi qua A{format_point(A)} và song song với ({plane_name}). "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho mặt phẳng (P) có dạng Ax+By+Cz+D=0, đi qua A{format_point(A)} và song song với ({plane_name}). "
        f"Khi đó {expr_str} = {value_false}."
    )
    return {"true": true_text, "false": false_text}


# Dạng 6: Mặt phẳng trung trực của đoạn AB
def prop_plane_perpendicular_bisector() -> Dict[str, str]:
    point_pairs = [((2, 0, 1), (0, -2, 3)), ((1, 1, 2), (3, -1, 0)), ((0, 2, 1), (2, 0, 3)), ((-1, 1, 2), (1, -1, 0))]
    A, B = random.choice(point_pairs)
    from fractions import Fraction
    Mx = Fraction(A[0] + B[0], 2)
    My = Fraction(A[1] + B[1], 2)
    Mz = Fraction(A[2] + B[2], 2)
    AB = subtract(B, A)
    # Plane: normal || AB, passing through midpoint M
    d_frac = -(AB[0] * Mx + AB[1] * My + AB[2] * Mz)
    L = d_frac.denominator
    a_int, b_int, c_int = AB[0] * L, AB[1] * L, AB[2] * L
    d_int = d_frac.numerator
    a_int, b_int, c_int, d_int = normalize_plane_coeffs(a_int, b_int, c_int, d_int)
    p, q, r, s = choose_linear_form_coeffs()
    expr_str = format_linear_form(p, q, r, s)
    value_true = evaluate_linear_form(p, q, r, s, a_int, b_int, c_int, d_int)
    value_false = pick_wrong_value(value_true)
    true_text = (
        f"Cho mặt phẳng trung trực của đoạn AB với A{format_point(A)}, B{format_point(B)} có dạng Ax+By+Cz+D=0. "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho mặt phẳng trung trực của đoạn AB với A{format_point(A)}, B{format_point(B)} có dạng Ax+By+Cz+D=0. "
        f"Khi đó {expr_str} = {value_false}."
    )
    return {"true": true_text, "false": false_text}


# Dạng 7: Qua điểm M và có hai VTCP a,b
def prop_plane_direction_vectors() -> Dict[str, str]:
    points = [(random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)) for _ in range(4)]
    vector_pairs = [
        ((random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)),
         (random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3))) for _ in range(4)
    ]
    while True:
        M = random.choice(points)
        a_vec, b_vec = random.choice(vector_pairs)
        if not is_zero_vector(a_vec) and not is_zero_vector(b_vec) and cross(a_vec, b_vec) != (0, 0, 0):
            break
    n = cross(a_vec, b_vec)
    a, b, c = n
    d = -(a * M[0] + b * M[1] + c * M[2])
    a, b, c, d = normalize_plane_coeffs(a, b, c, d)
    p, q, r, s = choose_linear_form_coeffs()
    expr_str = format_linear_form(p, q, r, s)
    value_true = evaluate_linear_form(p, q, r, s, a, b, c, d)
    value_false = pick_wrong_value(value_true)
    true_text = (
        f"Cho (P) có dạng Ax+By+Cz+D=0 đi qua M{format_point(M)} và có hai véctơ chỉ phương {format_vec(a_vec)}, {format_vec(b_vec)}. "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho (P) có dạng Ax+By+Cz+D=0 đi qua M{format_point(M)} và có hai véctơ chỉ phương {format_vec(a_vec)}, {format_vec(b_vec)}. "
        f"Khi đó {expr_str} = {value_false}."
    )
    return {"true": true_text, "false": false_text}


# Dạng 8: Qua 3 điểm bất kỳ
def prop_plane_three_points_variant() -> Dict[str, str]:
    points_sets = [((1, 0, 2), (1, 1, 1), (2, 3, 0)), ((3, -1, 2), (4, -1, -1), (2, 0, 2))]
    while True:
        A, B, C = random.choice(points_sets)
        AB = subtract(B, A)
        AC = subtract(C, A)
        n = cross(AB, AC)
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
        f"Cho (P) có dạng Ax+By+Cz+D=0 đi qua ba điểm A{format_point(A)}, B{format_point(B)}, C{format_point(C)}. "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho (P) có dạng Ax+By+Cz+D=0 đi qua ba điểm A{format_point(A)}, B{format_point(B)}, C{format_point(C)}. "
        f"Khi đó {expr_str} = {value_false}."
    )
    return {"true": true_text, "false": false_text}


# -------------------- Document builders --------------------

def generate_question(question_number: int) -> str:
    gens = [
        prop_plane_parallel_coordinate_plane,
        prop_plane_perpendicular_bisector,
        prop_plane_direction_vectors,
        prop_plane_three_points_variant,
    ]
    propositions: List[Dict[str, str]] = [gen() for gen in gens]
    import random as _r
    num_true = _r.randint(1, 4)
    true_indices = set(_r.sample(range(4), num_true))
    option_labels = ['a', 'b', 'c', 'd']
    content = f"Câu {question_number}: Chọn các mệnh đề đúng.\n\n"
    for i in range(4):
        text = propositions[i]['true'] if i in true_indices else propositions[i]['false']
        marker = '*' if i in true_indices else ''
        content += f"{marker}{option_labels[i]}) {text}\n\n"
    return content


def create_latex_document(questions: List[str], title: str = "Các bài toán về viết phương trình mặt phẳng - Đúng/Sai (Tập 2)") -> str:
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
    out = "plane_true_false_part_B_set2.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(questions)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()


