import math
import random
from typing import List, Tuple, Dict

# ================================================================
# Phần C — Tương giao mặt phẳng và mặt cầu (Các dạng 5 → 8)
# - Dạng 5 — Mặt phẳng qua 2 điểm và có khoảng cách đến 2 điểm khác bằng nhau (Câu 5)
# - Dạng 6 — Hình cầu tiếp xúc với mặt phẳng (tính bán kính từ khoảng cách tâm đến mặt phẳng) (Ví dụ 33; Câu 6)
# - Dạng 7 — Bài toán tham số m về vị trí tương đối mặt phẳng–mặt cầu (không giao/tiếp xúc/cắt) (Ví dụ 34; Câu 7; Câu 8)
# - Dạng 8 — Viết phương trình mặt cầu tâm cho trước cắt mặt phẳng theo đường tròn bán kính r (Câu 10)
# ================================================================

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
            if b == 1:
                parts.append("y")
            elif b == -1:
                parts.append("-y")
            else:
                parts.append(f"{b}y")
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
    if d != 0:
        if parts:
            if d > 0:
                parts.append(f"+ {d}")
            else:
                parts.append(f"- {abs(d)}")
        else:
            parts.append(str(d))
    if not parts:
        parts.append("0")
    return " ".join(parts) + " = 0"


def format_point(pt: Tuple[int, int, int]) -> str:
    return f"({pt[0]};{pt[1]};{pt[2]})"


# Dạng 5 — (Câu 5)
def prop_plane_through_points_equidistant() -> Dict[str, str]:
    O = (0, 0, 0)
    A = (random.choice([1, 2]), random.choice([1, 2]), 0)
    B = (0, random.choice([3, 4]), 0)
    C = (0, 0, random.choice([2, 3]))
    from fractions import Fraction
    ax, ay = A[0], A[1]
    By, Cz = B[1], C[2]
    frac = Fraction(ax * By, Cz)
    coeff_z_str = f"{frac.numerator}" if frac.denominator == 1 else f"\\dfrac{{{frac.numerator}}}{{{frac.denominator}}}"

    def fmt_xy(ay_val: int, ax_val: int) -> str:
        parts: List[str] = []
        if ay_val != 0:
            if ay_val == 1:
                parts.append("x")
            elif ay_val == -1:
                parts.append("-x")
            else:
                parts.append(f"{ay_val}x")
        neg_ax = -ax_val
        if parts:
            if neg_ax > 0:
                parts.append("+ y" if neg_ax == 1 else f"+ {neg_ax}y")
            elif neg_ax < 0:
                parts.append("- y" if neg_ax == -1 else f"- {abs(neg_ax)}y")
        else:
            if neg_ax == 1:
                parts.append("y")
            elif neg_ax == -1:
                parts.append("-y")
            elif neg_ax != 0:
                parts.append(f"{neg_ax}y")
        return " ".join(parts) if parts else "0"

    xy_part = fmt_xy(ay, ax)
    true_text = (
        f"Mặt phẳng \\((P)\\) đi qua hai điểm \\(O{format_point(O)}\\), \\(A{format_point(A)}\\) và cách đều hai điểm \\(B{format_point(B)}\\), \\(C{format_point(C)}\\) "
        f"có dạng \\({xy_part} \\pm {coeff_z_str}z = 0\\)."
    )
    false_text = (
        f"Mặt phẳng đi qua hai điểm \\(O{format_point(O)}\\), \\(A{format_point(A)}\\) và cách đều hai điểm \\(B{format_point(B)}\\), \\(C{format_point(C)}\\) có duy nhất một nghiệm."
    )
    return {"true": true_text, "false": false_text}


# Dạng 6 — (Ví dụ 33; Câu 6)
def prop_radius_from_center_plane_distance() -> Dict[str, str]:
    triple_choices = [(3, 4, 0, 5), (5, 12, 0, 13), (1, 0, 0, 1), (0, 1, 0, 1)]
    a, b, c, norm = random.choice(triple_choices)
    d = random.choice([1, 2, 3])
    I = (random.choice([0, 1, -1]), random.choice([-2, -1, 1]), random.choice([0, 1, 2]))
    numer = abs(a*I[0] + b*I[1] + c*I[2] + d)
    if numer == 0:
        d = d + 1
        numer = abs(a*I[0] + b*I[1] + c*I[2] + d)
    if norm == 1:
        true_text = f"Hình cầu tâm I{format_point(I)} tiếp xúc với mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) có bán kính \\({numer}\\)."
        false_text = f"Hình cầu tâm I{format_point(I)} tiếp xúc với mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) có bán kính \\({numer+1}\\)."
    else:
        true_text = f"Hình cầu tâm I{format_point(I)} tiếp xúc với mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) có bán kính \\(\\dfrac{{{numer}}}{{{norm}}}\\)."
        false_text = f"Hình cầu tâm I{format_point(I)} tiếp xúc với mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) có bán kính \\(\\dfrac{{{numer+1}}}{{{norm}}}\\)."
    return {"true": true_text, "false": false_text}


# Dạng 7 — (Ví dụ 34; Câu 7; Câu 8)
def prop_plane_sphere_no_intersection_param() -> Dict[str, str]:
    center = (-1, 2, 3)
    r = 5
    a, b, c = 2, 1, -2
    base = a*center[0] + b*center[1] + c*center[2]
    norm_int = math.isqrt(a*a + b*b + c*c)
    threshold = r*norm_int
    true_text = f"Với \\((P): 2x+y-2z+m=0\\) và mặt cầu \\((S): (x+1)^2+(y-2)^2+(z-3)^2=25\\), nếu \\(|{base}+m|>{threshold}\\) thì \\((P)\\) và \\((S)\\) không có điểm chung."
    false_text = f"Với mặt phẳng \\((P): 2x+y-2z+m=0\\) và mặt cầu \\((S): (x+1)^2+(y-2)^2+(z-3)^2=25\\), luôn tồn tại giao tuyến là đường tròn với mọi \\(m\\)."
    return {"true": true_text, "false": false_text}


def prop_param_plane_tangent_sphere() -> Dict[str, str]:
    u, v, w = random.choice([-1, 1]), random.choice([-1, 1]), random.choice([-1, 1])
    r_sq_candidates = [1, 4, 9, 16]
    r_sq = random.choice(r_sq_candidates)
    D = u*u + v*v + w*w - r_sq
    r = int(math.sqrt(r_sq))
    normal_choices = [(1, 0, 0), (0, 1, 0), (3, 4, 0)]
    a, b, c = random.choice(normal_choices)
    norm = math.isqrt(a*a + b*b + c*c)
    base = -a*u - b*v - c*w
    m1 = -base + r * norm
    m2 = -base - r * norm
    # Mặt cầu và (P)
    sphere_terms = ["x^2+y^2+z^2"]
    if u != 0:
        sphere_terms.append(f"{2*u:+}x")
    if v != 0:
        sphere_terms.append(f"{2*v:+}y")
    if w != 0:
        sphere_terms.append(f"{2*w:+}z")
    if D != 0:
        sphere_terms.append(f"{D:+}")
    sphere_eq = "".join(sphere_terms) + "=0"
    plane_base = []
    if a != 0:
        plane_base.append("x" if a == 1 else ("-x" if a == -1 else f"{a}x"))
    if b != 0:
        if plane_base:
            plane_base.append("+ y" if b == 1 else ("- y" if b == -1 else (f"+ {b}y" if b > 0 else f"- {abs(b)}y")))
        else:
            plane_base.append("y" if b == 1 else ("-y" if b == -1 else f"{b}y"))
    if c != 0:
        if plane_base:
            plane_base.append("+ z" if c == 1 else ("- z" if c == -1 else (f"+ {c}z" if c > 0 else f"- {abs(c)}z")))
        else:
            plane_base.append("z" if c == 1 else ("-z" if c == -1 else f"{c}z"))
    plane_base_str = " ".join(plane_base)
    true_text = f"Cho mặt cầu \\((S): {sphere_eq}\\) và mặt phẳng \\((P): {plane_base_str}+m=0\\). Để \\((P)\\) tiếp xúc với \\((S)\\), ta có \\(m={m1}\\) hoặc \\(m={m2}\\)."
    false_text = f"Cho mặt cầu \\((S): {sphere_eq}\\) và mặt phẳng \\((P): {plane_base_str}+m=0\\). Chỉ có duy nhất giá trị \\(m={m1}\\) để \\((P)\\) tiếp xúc với \\((S)\\)."
    return {"true": true_text, "false": false_text}


def prop_param_plane_intersect_sphere_circle() -> Dict[str, str]:
    u, v, w = random.choice([-2, -1, 1, 2]), random.choice([-2, -1, 1, 2]), random.choice([-2, -1, 1, 2])
    r_sq_choice = random.choice([1, 4, 9, 16])
    D = u*u + v*v + w*w - r_sq_choice
    center = (-u, -v, -w)
    A, B, C = 2*u, 2*v, 2*w
    r = math.isqrt(r_sq_choice)
    a, b = random.choice([(3, 4), (5, 12), (1, 0), (0, 1)])
    norm = math.isqrt(a*a + b*b)
    base = a*center[0] + b*center[1]
    threshold = r * norm
    m_min = -threshold - base
    m_max = threshold - base
    true_text = f"Cho mặt cầu \\((S): x^2+y^2+z^2{A:+}x{B:+}y{C:+}z{D:+}=0\\) và mặt phẳng \\((P): {a}x{b:+}y+m=0\\). Để \\((P)\\) cắt \\((S)\\) theo giao tuyến là đường tròn, cần \\({m_min}<m<{m_max}\\)."
    false_text = f"Cho mặt cầu \\((S): x^2+y^2+z^2{A:+}x{B:+}y{C:+}z{D:+}=0\\) và mặt phẳng \\((P): {a}x{b:+}y+m=0\\). Điều kiện để \\((P)\\) cắt \\((S)\\) theo giao tuyến là đường tròn là \\(m<{m_min}\\) hoặc \\(m>{m_max}\\)."
    return {"true": true_text, "false": false_text}


# Dạng 8 — (Câu 10)
def prop_sphere_plane_intersection_given_radius() -> Dict[str, str]:
    center = (random.choice([1, 2]), random.choice([1, 2]), random.choice([1, 2]))
    r_circle = random.choice([3, 4])
    a, b, c, expected_norm = random.choice([(3, 4, 0, 5), (1, 0, 0, 1), (0, 1, 0, 1), (5, 12, 0, 13)])
    base = a*center[0] + b*center[1] + c*center[2]
    dist_integer = random.choice([1, 2, 3])
    d = -base + dist_integer * expected_norm
    R_sq = dist_integer*dist_integer + r_circle*r_circle
    cx_term = f"(x{-center[0]:+})" if center[0] != 0 else "x"
    cy_term = f"(y{-center[1]:+})" if center[1] != 0 else "y"
    cz_term = f"(z{-center[2]:+})" if center[2] != 0 else "z"
    sphere_eq = f"{cx_term}^2+{cy_term}^2+{cz_term}^2={R_sq}"
    true_text = f"Mặt cầu \\((S)\\) có tâm \\(I{format_point(center)}\\) và cắt mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) theo đường tròn có bán kính \\(r={r_circle}\\) có phương trình \\((S): {sphere_eq}\\)."
    false_text = (
        f"Để mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) cắt mặt cầu \\((S)\\) có tâm \\(I{format_point(center)}\\) "
        f"theo đường tròn có bán kính \\(r={r_circle}\\), mặt cầu cần có bán kính \\(R={r_circle}\\)."
    )
    return {"true": true_text, "false": false_text}


def prop_param_m_mixed() -> Dict[str, str]:
    """Dạng 7 (tham số m): chọn ngẫu nhiên một trong ba biến thể (không giao / tiếp xúc / cắt)."""
    return random.choice([
        prop_plane_sphere_no_intersection_param,
        prop_param_plane_tangent_sphere,
        prop_param_plane_intersect_sphere_circle,
    ])()


PART_GROUPS: List = [
    prop_plane_through_points_equidistant,      # Dạng 5
    prop_radius_from_center_plane_distance,     # Dạng 6
    prop_param_m_mixed,                         # Dạng 7 (gộp 3 biến thể)
    prop_sphere_plane_intersection_given_radius # Dạng 8
]


def generate_question(question_number: int) -> str:
    gens = random.sample(PART_GROUPS, k=4)
    props: List[Dict[str, str]] = [g() for g in gens]
    num_true = random.randint(1, 4)
    true_indices = set(random.sample(range(4), num_true))
    labels = ['a', 'b', 'c', 'd']
    content = f"Câu {question_number}: Chọn các mệnh đề đúng.\n\n"
    for i in range(4):
        txt = props[i]['true'] if i in true_indices else props[i]['false']
        mark = '*' if i in true_indices else ''
        content += f"{mark}{labels[i]}) {txt}\n\n"
    return content


def create_latex_document(questions: List[str], title: str) -> str:
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
    qs = [generate_question(i+1) for i in range(num_questions)]
    tex = create_latex_document(qs, title="Tương giao mặt phẳng và mặt cầu — Dạng 5 đến 8")
    out = "plane_sphere_part_C_types_5_8.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(qs)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()


