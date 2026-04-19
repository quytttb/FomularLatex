"""
Tập 7 — Bao gồm 4 dạng (độc lập):
- Dạng 25: Mặt phẳng song song (Q) và cách điểm M một khoảng — Ví dụ 26, Câu 25
- Dạng 26: Mặt phẳng song song (Q) và cách (Q) một khoảng — Ví dụ 27, Câu 26–27
- Dạng 27: Mặt phẳng vuông góc với hai mặt phẳng và cách O một khoảng — Ví dụ 28, Câu 28–29
- Dạng 28: Mặt phẳng qua giao tuyến (α),(β) và điều kiện bổ sung — Ví dụ 29, Câu 30–31

Chạy: python3 plane_true_false_part_B_set7.py [số_câu]
Sinh ra: plane_true_false_part_B_set7.tex
"""

import random
import math
from typing import List, Tuple, Dict


# -------------------- Simple formatters --------------------

def format_point(pt: Tuple[int, int, int]) -> str:
    return f"({pt[0]};{pt[1]};{pt[2]})"


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
    if d_base != 0:
        parts.append(f"+ {d_base}" if d_base > 0 else f"- {abs(d_base)}")
    if d_sqrt_coeff != 0:
        sqrt_expr = format_sqrt_expression(abs(d_sqrt_coeff), d_sqrt_under)
        parts.append(("+ " if d_sqrt_coeff > 0 else "- ") + sqrt_expr)
    if not parts:
        parts.append("0")
    return " ".join(parts) + " = 0"


def format_plane_equation(a: int, b: int, c: int, d: int) -> str:
    return format_plane_equation_with_sqrt(a, b, c, d, 0, 1)


# -------------------- Vector helpers --------------------

def cross(u: Tuple[int, int, int], v: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return (u[1]*v[2] - u[2]*v[1], u[2]*v[0] - u[0]*v[2], u[0]*v[1] - u[1]*v[0])


def is_zero_vector(v: Tuple[int, int, int]) -> bool:
    return v[0] == 0 and v[1] == 0 and v[2] == 0


# -------------------- Propositions (4 dạng: 25–28) --------------------

# Dạng 25: Song song (Q) và cách điểm M một khoảng
def prop_plane_parallel_distance_from_point() -> Dict[str, str]:
    options = [
        ((1, 1, -1, 2), (1, 2, 3), 2),
        ((2, -1, 2, -1), (0, 1, 2), 3),
        ((1, 2, 2, 0), (1, 0, 1), 3),
        ((2, 1, 2, 1), (1, 1, 0), 3),
        ((1, 1, 1, -2), (2, 1, 0), 2),
        ((2, 2, 1, 0), (0, 1, 1), 3),
    ]
    (a, b, c, d_orig), M, k = random.choice(options)
    norm_squared = a * a + b * b + c * c
    norm_int = math.isqrt(norm_squared)
    M_value = a * M[0] + b * M[1] + c * M[2]
    if norm_int * norm_int == norm_squared:
        d1 = -M_value + k * norm_int
        d2 = -M_value - k * norm_int
        chosen_d = random.choice([d1, d2])
        true_text = (
            f"Có hai mặt phẳng song song với (Q): {format_plane_equation(a, b, c, d_orig)} và cách điểm M{format_point(M)} khoảng {k}. "
            f"Một trong hai mặt phẳng đó có phương trình \\({format_plane_equation(a, b, c, chosen_d)}\\)."
        )
        wrong_d = chosen_d + random.choice([-2, -1, 1, 2])
        false_text = (
            f"Mặt phẳng song song với (Q): {format_plane_equation(a, b, c, d_orig)} và cách điểm M{format_point(M)} khoảng {k} "
            f"có phương trình \\({format_plane_equation(a, b, c, wrong_d)}\\)."
        )
    else:
        sign = random.choice([1, -1])
        d_base = -M_value
        d_sqrt_coeff = sign * k
        d_sqrt_under = norm_squared
        true_text = (
            f"Có hai mặt phẳng song song với (Q): {format_plane_equation(a, b, c, d_orig)} và cách điểm M{format_point(M)} khoảng {k}. "
            f"Một trong hai mặt phẳng đó có phương trình \\({format_plane_equation_with_sqrt(a, b, c, d_base, d_sqrt_coeff, d_sqrt_under)}\\)."
        )
        wrong_sqrt_coeff = d_sqrt_coeff + random.choice([-1, 1])
        false_text = (
            f"Mặt phẳng song song với (Q): {format_plane_equation(a, b, c, d_orig)} và cách điểm M{format_point(M)} khoảng {k} "
            f"có phương trình \\({format_plane_equation_with_sqrt(a, b, c, d_base, wrong_sqrt_coeff, d_sqrt_under)}\\)."
        )
    return {"true": true_text, "false": false_text}


# Dạng 26: Song song (Q) và cách (Q) một khoảng
def prop_plane_parallel_distance_between_planes() -> Dict[str, str]:
    options = [
        ((1, 0, 0, 2), 3),
        ((0, 1, 0, -1), 2),
        ((0, 0, 1, 1), 4),
        ((1, 1, 0, 0), 2),
        ((1, 0, 1, -1), 3),
        ((0, 1, 1, 2), 2),
        ((1, 1, 1, 0), 3),
        ((2, 0, 0, 1), 2),
        ((0, 2, 0, -1), 3),
        ((3, 0, 0, 2), 4),
        ((2, 2, 1, 0), 3),
    ]
    (a, b, c, d_orig), dist = random.choice(options)
    norm_squared = a * a + b * b + c * c
    norm_int = math.isqrt(norm_squared)
    if norm_int * norm_int == norm_squared:
        d_shift = dist * norm_int
        d_option1 = d_orig + d_shift
        d_option2 = d_orig - d_shift
        d_correct = random.choice([d_option1, d_option2])
        true_text = f"Mặt phẳng song song với (Q): {format_plane_equation(a, b, c, d_orig)} và cách (Q) khoảng {dist} có phương trình \\({format_plane_equation(a, b, c, d_correct)}\\)."
        wrong_d = d_correct + random.choice([-2, -1, 1, 2])
        false_text = f"Mặt phẳng song song với (Q): {format_plane_equation(a, b, c, d_orig)} và cách (Q) khoảng {dist} có phương trình \\({format_plane_equation(a, b, c, wrong_d)}\\)."
    else:
        sign = random.choice([1, -1])
        d_base = d_orig
        d_sqrt_coeff = sign * dist
        d_sqrt_under = norm_squared
        true_text = f"Mặt phẳng song song với (Q): {format_plane_equation(a, b, c, d_orig)} và cách (Q) khoảng {dist} có phương trình \\({format_plane_equation_with_sqrt(a, b, c, d_base, d_sqrt_coeff, d_sqrt_under)}\\)."
        wrong_sqrt_coeff = d_sqrt_coeff + random.choice([-1, 1])
        false_text = f"Mặt phẳng song song với (Q): {format_plane_equation(a, b, c, d_orig)} và cách (Q) khoảng {dist} có phương trình \\({format_plane_equation_with_sqrt(a, b, c, d_base, wrong_sqrt_coeff, d_sqrt_under)}\\)."
    return {"true": true_text, "false": false_text}


# Dạng 27: Vuông góc 2 mp và cách O một khoảng
def prop_plane_perpendicular_two_planes_distance() -> Dict[str, str]:
    plane1_options = [
        (1, 2, -1, random.randint(-3, 3)),
        (2, -1, 1, random.randint(-3, 3)),
        (1, 1, -2, random.randint(-2, 2)),
        (-1, 3, 1, random.randint(-2, 2))
    ]
    plane2_options = [
        (2, -1, 1, random.randint(-3, 3)),
        (1, -2, 3, random.randint(-2, 2)),
        (3, 1, -1, random.randint(-2, 2)),
        (-2, 1, 2, random.randint(-3, 3))
    ]
    while True:
        a1, b1, c1, d1 = random.choice(plane1_options)
        a2, b2, c2, d2 = random.choice(plane2_options)
        n1 = (a1, b1, c1)
        n2 = (a2, b2, c2)
        if n1 != (0, 0, 0) and n2 != (0, 0, 0) and cross(n1, n2) != (0, 0, 0):
            break
    k = random.randint(2, 4)
    O = (0, 0, 0)
    n = cross((a1, b1, c1), (a2, b2, c2))
    dot_nO = n[0]*O[0] + n[1]*O[1] + n[2]*O[2]
    d_base = -dot_nO
    norm_sq = n[0]**2 + n[1]**2 + n[2]**2
    true_text = (
        f"Mặt phẳng vuông góc với (α): {format_plane_equation(a1, b1, c1, d1)} và (β): {format_plane_equation(a2, b2, c2, d2)}, "
        f"cách điểm O{format_point(O)} một khoảng bằng {k} có dạng \\({n[0]}x + {n[1]}y + {n[2]}z + {d_base} \\pm {k}\\sqrt{{{norm_sq}}} = 0\\)."
    )
    wrong_k = k + random.choice([-2, -1, 1, 2])
    false_text = (
        f"Mặt phẳng vuông góc với (α): {format_plane_equation(a1, b1, c1, d1)} và (β): {format_plane_equation(a2, b2, c2, d2)}, "
        f"cách điểm O{format_point(O)} một khoảng bằng {k} có dạng \\({n[0]}x + {n[1]}y + {n[2]}z + {d_base} \\pm {wrong_k}\\sqrt{{{norm_sq}}} = 0\\)."
    )
    return {"true": true_text, "false": false_text}


# Dạng 28: Qua giao tuyến (α),(β) và thêm điều kiện
def prop_plane_through_intersection_line() -> Dict[str, str]:
    from fractions import Fraction
    M_options = [(random.randint(1, 3), random.randint(-3, -1), random.randint(1, 3)), (random.randint(0, 2), random.randint(-2, 0), random.randint(2, 4)), (random.randint(2, 4), random.randint(-1, 1), random.randint(1, 2))]
    plane1_options = [(1, -1, 1, random.randint(-5, -2)), (2, -1, 0, random.randint(-3, 0)), (1, 0, -1, random.randint(-2, 1)), (3, -2, 1, random.randint(-4, -1))]
    plane2_options = [(3, -1, 1, random.randint(-2, 1)), (2, -1, 2, random.randint(-3, 0)), (1, -1, 3, random.randint(-1, 2)), (4, -3, 0, random.randint(-2, 1))]
    def are_parallel(n1: Tuple[int, int, int], n2: Tuple[int, int, int]) -> bool:
        cr = cross(n1, n2)
        return cr == (0, 0, 0)
    while True:
        M = random.choice(M_options)
        a1, b1, c1, d1 = random.choice(plane1_options)
        a2, b2, c2, d2 = random.choice(plane2_options)
        if are_parallel((a1, b1, c1), (a2, b2, c2)):
            continue
        dist1 = a1 * M[0] + b1 * M[1] + c1 * M[2] + d1
        dist2 = a2 * M[0] + b2 * M[1] + c2 * M[2] + d2
        if dist2 == 0:
            continue
        lam = Fraction(-dist1, dist2)
        a_final = a1 + lam * a2
        b_final = b1 + lam * b2
        c_final = c1 + lam * c2
        d_final = d1 + lam * d2
        if a_final == 0 and b_final == 0 and c_final == 0:
            continue
        break
    coeffs_frac = [Fraction(a_final).limit_denominator(), Fraction(b_final).limit_denominator(), Fraction(c_final).limit_denominator(), Fraction(d_final).limit_denominator()]
    lcm_denom = 1
    for f in coeffs_frac:
        g = math.gcd(lcm_denom, f.denominator)
        lcm_denom = abs(int(Fraction(lcm_denom * f.denominator, g)))
    a_int = int(coeffs_frac[0] * lcm_denom)
    b_int = int(coeffs_frac[1] * lcm_denom)
    c_int = int(coeffs_frac[2] * lcm_denom)
    d_int = int(coeffs_frac[3] * lcm_denom)
    true_text = (
        f"Mặt phẳng qua M{format_point(M)} và qua giao tuyến của (α): {format_plane_equation(a1, b1, c1, d1)} và (β): {format_plane_equation(a2, b2, c2, d2)} "
        f"có phương trình \\({format_plane_equation(a_int, b_int, c_int, d_int)}\\)."
    )
    wrong_a = a_int + random.choice([-2, 2])
    wrong_d = d_int + random.choice([-3, 3])
    false_text = (
        f"Mặt phẳng qua M{format_point(M)} và qua giao tuyến của (α): {format_plane_equation(a1, b1, c1, d1)} và (β): {format_plane_equation(a2, b2, c2, d2)} "
        f"có phương trình \\({format_plane_equation(wrong_a, b_int, c_int, wrong_d)}\\)."
    )
    return {"true": true_text, "false": false_text}


# -------------------- Document builders --------------------

def generate_question(question_number: int) -> str:
    gens = [
        prop_plane_parallel_distance_from_point,
        prop_plane_parallel_distance_between_planes,
        prop_plane_perpendicular_two_planes_distance,
        prop_plane_through_intersection_line,
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


def create_latex_document(questions: List[str], title: str = "Các bài toán về viết phương trình mặt phẳng - Đúng/Sai (Tập 7)") -> str:
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
    out = "plane_true_false_part_B_set7.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(questions)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()


