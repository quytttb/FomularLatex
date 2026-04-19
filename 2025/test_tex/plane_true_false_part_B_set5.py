"""
Tập 5 — Bao gồm 4 dạng (độc lập):
- Dạng 17: Mặt phẳng song song với (ABC) dựng từ hình chiếu của điểm M — Ví dụ 22
- Dạng 18: Mặt phẳng với M là trực tâm tam giác ABC — Câu 17, Câu 18
- Dạng 19: Mặt phẳng với G là trọng tâm tam giác ABC — Ví dụ 23, Câu 19
- Dạng 20: Ràng buộc tỉ lệ chặn OM = 2ON (cắt Ox, Oy) — Câu 20

Chạy: python3 plane_true_false_part_B_set5.py [số_câu]
Sinh ra: plane_true_false_part_B_set5.tex
"""

import random
from typing import List, Tuple, Dict


# -------------------- Simple formatters --------------------

def format_point(pt: Tuple[int, int, int]) -> str:
    return f"({pt[0]};{pt[1]};{pt[2]})"


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


# -------------------- Propositions (4 dạng: 17–20) --------------------

# Dạng 17: Song song với (ABC) dựng từ hình chiếu của một điểm M
def prop_parallel_to_ABC_from_M() -> Dict[str, str]:
    M_points = [(random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)) for _ in range(4)]
    while True:
        M = random.choice(M_points)
        a = M[1] * M[2]
        b = M[0] * M[2]
        c = M[0] * M[1]
        d = -M[0] * M[1] * M[2]
        if not is_zero_vector((a, b, c)):
            break
    d_parallel = d + random.choice([-1, 1])
    true_text = f"Cho điểm M{format_point(M)}. Gọi A, B, C lần lượt là hình chiếu của M trên các trục tọa độ. Một mặt phẳng song song với (ABC) có phương trình \\({format_plane_equation(a, b, c, d_parallel)}\\)."
    wrong_a, wrong_c = c, a
    if a == c:
        wrong_a = a + 1
    false_text = f"Cho điểm M{format_point(M)}. Gọi A, B, C lần lượt là hình chiếu của M trên các trục tọa độ. Mặt phẳng song song với (ABC) có phương trình \\({format_plane_equation(wrong_a, b, wrong_c, d)}\\)."
    return {"true": true_text, "false": false_text}


# Dạng 18: M là trực tâm (ABC)
def prop_plane_orthocenter_condition() -> Dict[str, str]:
    M_options = [(random.randint(1, 5), random.randint(1, 5), random.randint(1, 5)) for _ in range(4)]
    M = random.choice(M_options)
    p, q, r = M
    k = p * p + q * q + r * r
    a, b, c, d = p, q, r, -k
    true_text = (
        f"Mặt phẳng đi qua điểm M{format_point(M)} và cắt trục tọa độ Ox, Oy, Oz tại A, B, C sao cho M là trực tâm tam giác ABC "
        f"có phương trình \\({format_plane_equation(a, b, c, d)}\\)."
    )
    wrong_d = d + random.choice([-5, -3, 3, 5])
    false_text = (
        f"Mặt phẳng đi qua điểm M{format_point(M)} và cắt trục tọa độ Ox, Oy, Oz tại A, B, C sao cho M là trực tâm tam giác ABC "
        f"có phương trình \\({format_plane_equation(a, b, c, wrong_d)}\\)."
    )
    return {"true": true_text, "false": false_text}


# Dạng 19: G là trọng tâm (ABC)
def prop_plane_centroid_from_axes() -> Dict[str, str]:
    G_coords = [(random.randint(1, 5), random.randint(1, 5), random.randint(1, 5)) for _ in range(4)]
    G = random.choice(G_coords)
    x0, y0, z0 = G
    a_coeff = y0 * z0
    b_coeff = x0 * z0
    c_coeff = x0 * y0
    d_val = 3 * x0 * y0 * z0
    true_text = f"Mặt phẳng đi qua G{format_point(G)} và cắt các trục tọa độ tại A, B, C sao cho G là trọng tâm tam giác ABC có phương trình \\({format_plane_equation(a_coeff, b_coeff, c_coeff, -d_val)}\\)."
    wrong_d = d_val + random.choice([-6, 6, -9, 9])
    false_text = f"Mặt phẳng đi qua G{format_point(G)} và cắt các trục tọa độ tại A, B, C sao cho G là trọng tâm tam giác ABC có phương trình \\({format_plane_equation(a_coeff, b_coeff, c_coeff, -wrong_d)}\\)."
    return {"true": true_text, "false": false_text}


# Dạng 20: Ràng buộc OM = 2ON (qua A, B cho trước)
def prop_plane_special_ratio_condition() -> Dict[str, str]:
    from fractions import Fraction
    from math import gcd
    from functools import reduce
    A_options = [(random.randint(2, 5), 0, 0), (random.randint(1, 4), 0, random.randint(1, 3)), (random.randint(3, 6), 0, random.randint(2, 4))]
    B_options = [(random.randint(1, 3), 0, random.randint(1, 4)), (random.randint(2, 4), 0, random.randint(2, 3)), (random.randint(1, 2), 0, random.randint(3, 5))]
    max_attempts = 500
    found = False
    coeff_x = coeff_y = coeff_z = coeff_const = 0
    A = (0, 0, 0)
    B = (0, 0, 0)
    for _ in range(max_attempts):
        A = random.choice(A_options)
        B = random.choice(B_options)
        xA, yA, zA = A
        xB, yB, zB = B
        if yA != 0 or yB != 0:
            continue
        xA_f, zA_f = Fraction(xA), Fraction(zA)
        xB_f, zB_f = Fraction(xB), Fraction(zB)
        delta_x = xA_f - xB_f
        delta_z = zA_f - zB_f
        if delta_x == 0 or delta_z == 0:
            continue
        b = Fraction(1, 2) * (xA_f - zA_f * delta_x / delta_z)
        if b == 0:
            continue
        c = -2 * b * delta_z / delta_x
        a = 2 * b
        coeff_x_f = b * c
        coeff_y_f = a * c
        coeff_z_f = a * b
        coeff_const_f = a * b * c
        def lcm(u, v):
            return u * v // gcd(u, v)
        denoms = [coeff_x_f.denominator, coeff_y_f.denominator, coeff_z_f.denominator, coeff_const_f.denominator]
        L = reduce(lcm, denoms, 1)
        ints = [(coeff_x_f * L).numerator, (coeff_y_f * L).numerator, (coeff_z_f * L).numerator, (coeff_const_f * L).numerator]
        g = 0
        for v in ints:
            g = gcd(g, abs(v)) if g else abs(v)
        if g > 1:
            ints = [v // g for v in ints]
        coeff_x, coeff_y, coeff_z, coeff_const = ints
        if coeff_x == 0 or coeff_y == 0 or coeff_const == 0:
            continue
        if (coeff_x * xA + coeff_y * yA + coeff_z * zA - coeff_const) != 0:
            continue
        if (coeff_x * xB + coeff_y * yB + coeff_z * zB - coeff_const) != 0:
            continue
        if coeff_y != 2 * coeff_x:
            continue
        found = True
        break
    if not found:
        b0 = random.randint(1, 3)
        a0 = 2 * b0
        c0 = random.randint(1, 3)
        coeff_x = b0 * c0
        coeff_y = a0 * c0
        coeff_z = a0 * b0
        coeff_const = a0 * b0 * c0
        A = (a0, 0, 0)
        B = (0, b0, 0)
    true_text = f"Mặt phẳng đi qua điểm A{format_point(A)} và B{format_point(B)} đồng thời cắt Ox, Oy tại M,N sao cho OM=2ON có phương trình \\({format_plane_equation(coeff_x, coeff_y, coeff_z, -coeff_const)}\\)."
    wrong_const = coeff_const + random.choice([-2, 2, -3, 3])
    false_text = f"Mặt phẳng đi qua điểm A{format_point(A)} và B{format_point(B)} đồng thời cắt Ox, Oy tại M,N sao cho OM=2ON có phương trình \\({format_plane_equation(coeff_x, coeff_y, coeff_z, -wrong_const)}\\)."
    return {"true": true_text, "false": false_text}


# -------------------- Document builders --------------------

def generate_question(question_number: int) -> str:
    gens = [
        prop_parallel_to_ABC_from_M,
        prop_plane_orthocenter_condition,
        prop_plane_centroid_from_axes,
        prop_plane_special_ratio_condition,
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


def create_latex_document(questions: List[str], title: str = "Các bài toán về viết phương trình mặt phẳng - Đúng/Sai (Tập 5)") -> str:
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
    out = "plane_true_false_part_B_set5.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(questions)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()


