"""
Tập 6 — Bao gồm 4 dạng (độc lập):
- Dạng 21: Mặt phẳng thỏa 4OA = 2OB = OC — Ví dụ 24
- Dạng 22: Mặt phẳng qua C, M và chắn bằng nhau trên Ox, Oy — Câu 21
- Dạng 23: Tối ưu thể tích tứ diện OABC (giá trị nhỏ nhất) — Câu 23
- Dạng 24: Tối ưu T = 1/OA^2 + 1/OB^2 + 1/OC^2 — Câu 24

Chạy: python3 plane_true_false_part_B_set6.py [số_câu]
Sinh ra: plane_true_false_part_B_set6.tex
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


# -------------------- Propositions (4 dạng: 21–24) --------------------

# Dạng 21: 4OA = 2OB = OC
def prop_plane_special_ratio_4OA_2OB_OC() -> Dict[str, str]:
    coords = [(x, y, z) for x in range(-3, 4) for y in range(-3, 4) for z in range(-3, 4) if 4 * x + 2 * y + z > 0]
    if not coords:
        coords = [(x, y, z) for x in range(-5, 6) for y in range(-5, 6) for z in range(-5, 6) if 4 * x + 2 * y + z > 0]
    M = random.choice(coords)
    k = 4 * M[0] + 2 * M[1] + M[2]
    true_text = f"Mặt phẳng qua M{format_point(M)} và cắt các tia Ox, Oy, Oz tại A, B, C sao cho 4OA = 2OB = OC có phương trình \\(4x + 2y + z - {k} = 0\\)."
    wrong_k = k + random.choice([-3, -5, 3, 5])
    false_text = f"Mặt phẳng qua M{format_point(M)} và cắt các tia Ox, Oy, Oz tại A, B, C sao cho 4OA = 2OB = OC có phương trình \\(4x + 2y + z - {wrong_k} = 0\\)."
    return {"true": true_text, "false": false_text}


# Dạng 22: Chặn bằng nhau trên Ox, Oy (qua C, M)
def prop_plane_equal_segments() -> Dict[str, str]:
    from fractions import Fraction
    def build_valid_example():
        C_candidates = [(0, 0, random.randint(1, 4)), (0, 0, random.randint(2, 5)), (0, 0, random.randint(1, 3))]
        M_candidates = [(random.randint(1, 3), random.randint(1, 3), random.randint(0, 2)), (random.randint(2, 4), random.randint(1, 2), random.randint(1, 3)), (random.randint(1, 2), random.randint(2, 4), random.randint(0, 1))]
        from math import gcd as _gcd
        for _ in range(200):
            C = random.choice(C_candidates)
            M = random.choice(M_candidates)
            zC = C[2]
            x0, y0, z0 = M
            if zC == z0:
                continue
            denom = zC - z0
            a_frac = Fraction((x0 + y0) * zC, denom)
            if a_frac <= 0:
                continue
            coeff_x_f = a_frac * zC
            coeff_y_f = a_frac * zC
            coeff_z_f = a_frac * a_frac
            coeff_const_f = a_frac * a_frac * zC
            denoms = [coeff_x_f.denominator, coeff_y_f.denominator, coeff_z_f.denominator, coeff_const_f.denominator]
            L = 1
            for d in denoms:
                L = L * d // _gcd(L, d)
            coeff_x = int(coeff_x_f * L)
            coeff_y = int(coeff_y_f * L)
            coeff_z = int(coeff_z_f * L)
            coeff_const = int(coeff_const_f * L)
            g = 0
            for v in (coeff_x, coeff_y, coeff_z, coeff_const):
                g = _gcd(g, abs(v)) if g else abs(v)
            if g > 1:
                coeff_x //= g
                coeff_y //= g
                coeff_z //= g
                coeff_const //= g
            if coeff_x == 0 or coeff_y == 0 or coeff_const == 0:
                continue
            if (coeff_x * C[0] + coeff_y * C[1] + coeff_z * C[2] - coeff_const) != 0:
                continue
            if (coeff_x * x0 + coeff_y * y0 + coeff_z * z0 - coeff_const) != 0:
                continue
            return C, M, (coeff_x, coeff_y, coeff_z, coeff_const)
        zC = random.randint(2, 5)
        C = (0, 0, zC)
        a0, b0, c0 = 2, 1, zC
        coeff_x, coeff_y, coeff_z, coeff_const = b0 * c0, a0 * c0, a0 * b0, a0 * b0 * c0
        M = (1, 1, 0)
        return C, M, (coeff_x, coeff_y, coeff_z, coeff_const)
    C, M, (cx, cy, cz, cst) = build_valid_example()
    true_text = f"Cho hai điểm C{format_point(C)} và M{format_point(M)}. Mặt phẳng qua C, M đồng thời chắn trên các nửa trục dương Ox, Oy các đoạn thẳng bằng nhau có phương trình \\({format_plane_equation_with_sqrt(cx, cy, cz, -cst)}\\)."
    wrong_cy = cy + random.choice([-2, -1, 1, 2])
    if wrong_cy == cx:
        wrong_cy += 1
    false_text = f"Cho hai điểm C{format_point(C)} và M{format_point(M)}. Mặt phẳng qua C, M đồng thời chắn trên các nửa trục dương Ox, Oy các đoạn thẳng bằng nhau có phương trình \\({format_plane_equation_with_sqrt(cx, wrong_cy, cz, -cst)}\\)."
    return {"true": true_text, "false": false_text}


# Dạng 23: Tối ưu thể tích OABC (giá trị min)
def prop_min_volume_with_value() -> Dict[str, str]:
    from fractions import Fraction
    M = (random.randint(1, 4), random.randint(1, 4), random.randint(1, 4))
    x, y, z = M
    volume_frac = Fraction(9, 2) * x * y * z
    if volume_frac.denominator == 1:
        volume_str = f"{volume_frac.numerator}"
    else:
        volume_str = f"\\dfrac{{{volume_frac.numerator}}}{{{volume_frac.denominator}}}"
    true_text = f"Mặt phẳng đi qua M{format_point(M)} cắt ba trục tọa độ sao cho tứ diện OABC có thể tích nhỏ nhất. Thể tích nhỏ nhất đó bằng \\({volume_str}\\)."
    wrong_frac = volume_frac + Fraction(1, 2)
    if wrong_frac.denominator == 1:
        wrong_str = f"{wrong_frac.numerator}"
    else:
        wrong_str = f"\\dfrac{{{wrong_frac.numerator}}}{{{wrong_frac.denominator}}}"
    false_text = f"Mặt phẳng đi qua M{format_point(M)} cắt ba trục tọa độ sao cho tứ diện OABC có thể tích nhỏ nhất. Thể tích nhỏ nhất đó bằng \\({wrong_str}\\)."
    return {"true": true_text, "false": false_text}


# Dạng 24: Tối ưu T = 1/OA^2 + 1/OB^2 + 1/OC^2
def prop_min_sum_inverse_squares() -> Dict[str, str]:
    M = (random.randint(1, 4), random.randint(1, 4), random.randint(1, 4))
    x0, y0, z0 = M
    k = x0*x0 + y0*y0 + z0*z0
    true_text = f"Với M{format_point(M)}, mặt phẳng (P) để T nhỏ nhất là \\({x0}x + {y0}y + {z0}z - {k} = 0\\)."
    wrong_k = k + random.choice([-5, -3, 3, 5])
    false_text = f"Với M{format_point(M)}, mặt phẳng (P) để T nhỏ nhất là \\({x0}x + {y0}y + {z0}z - {wrong_k} = 0\\)."
    return {"true": true_text, "false": false_text}


# -------------------- Document builders --------------------

def generate_question(question_number: int) -> str:
    gens = [
        prop_plane_special_ratio_4OA_2OB_OC,
        prop_plane_equal_segments,
        prop_min_volume_with_value,
        prop_min_sum_inverse_squares,
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


def create_latex_document(questions: List[str], title: str = "Các bài toán về viết phương trình mặt phẳng - Đúng/Sai (Tập 6)") -> str:
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
    out = "plane_true_false_part_B_set6.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(questions)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()


