import math
import random
from typing import List, Tuple, Dict

# ================================================================
# Phần C — Tương giao mặt phẳng và mặt cầu (Các dạng 1 → 4)
# - Dạng 1 — Tiếp xúc mặt cầu tại điểm cho trước (Ví dụ 30; Câu 1)
# - Dạng 2 — Mặt phẳng song song với mặt phẳng cho trước và tiếp xúc với mặt cầu (Ví dụ 31; Câu 2; Câu 3)
# - Dạng 3 — Mặt phẳng song song và cách đều hai mặt phẳng song song (Ví dụ 32)
# - Dạng 4 — Mặt phẳng song song với mặt phẳng cho trước, cắt mặt cầu theo đường tròn có chu vi cho trước (Câu 4)
# ================================================================

# Bộ hàm định dạng (giữ nguyên dạng số/căn bậc hai)

def format_plane_equation(a: int, b: int, c: int, d: int) -> str:
    parts: List[str] = []
    # x
    if a == 1:
        parts.append("x")
    elif a == -1:
        parts.append("-x")
    elif a != 0:
        parts.append(f"{a}x")
    # y
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
    # z
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
    # d
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


# Dạng 1 — Tiếp xúc mặt cầu tại điểm cho trước (Ví dụ 30; Câu 1)
def prop_tangent_plane_at_point() -> Dict[str, str]:
    # Sinh tâm và bán kính; lấy điểm M trên mặt cầu bằng cách tịnh tiến theo trục x
    center = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
    r = random.choice([3, 4, 5])
    # Lấy điểm thuộc mặt cầu bằng cách cộng bán kính theo x
    M = (center[0] + r, center[1], center[2])
    # Pháp tuyến mặt phẳng tiếp xúc là vector CM
    a, b, c = (M[0]-center[0], M[1]-center[1], M[2]-center[2])
    d = -(a*M[0] + b*M[1] + c*M[2])
    true_text = f"Mặt phẳng tiếp xúc với mặt cầu tâm I{format_point(center)} bán kính {r} tại M{format_point(M)} có phương trình \\((P): {format_plane_equation(a,b,c,d)}\\)."
    false_text = f"Mặt phẳng tiếp xúc với mặt cầu tâm I{format_point(center)} bán kính {r} tại M{format_point(M)} có phương trình \\((P): {format_plane_equation(a,b,c,d+1)}\\)."
    return {"true": true_text, "false": false_text}


# Dạng 2 — Song song (Q) và tiếp xúc với mặt cầu (Ví dụ 31; Câu 2; Câu 3)
def prop_plane_parallel_tangent_to_sphere() -> Dict[str, str]:
    # Mặt cầu tổng quát: x^2+y^2+z^2+2ux+2vy+2wz + D = 0 (chọn để bán kính nguyên)
    u, v, w = random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)
    r_sq_choice = random.choice([1, 4, 9, 16])
    D = u*u + v*v + w*w - r_sq_choice
    center = (-u, -v, -w)
    r_int = math.isqrt(r_sq_choice)
    # Mặt phẳng đã cho (Q): ax+by+cz+d0=0; (P) // (Q) ⇒ cùng (a,b,c)
    normals = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (3, 4, 0), (4, 3, 0), (3, 0, 4), (0, 3, 4)]
    a, b, c = random.choice(normals)
    d0 = random.randint(-10, 10)
    norm_int = math.isqrt(a*a + b*b + c*c)
    base = a*center[0] + b*center[1] + c*center[2]
    d_true = -base + r_int * norm_int
    d_false = d_true + random.choice([1, -1, 2, -2])
    true_text = (
        f"Tồn tại mặt phẳng \\((P)\\) song song với \\((Q): {format_plane_equation(a,b,c,d0)}\\) và tiếp xúc với mặt cầu "
        f"\\(x^2+y^2+z^2+{2*u}x+{2*v}y+{2*w}z+{D}=0\\) có dạng \\((P): {format_plane_equation(a,b,c,d_true)}\\)."
    )
    false_text = (
        f"Mặt phẳng \\((P): {format_plane_equation(a,b,c,d_false)}\\) song song với \\((Q): {format_plane_equation(a,b,c,d0)}\\) "
        f"và tiếp xúc với mặt cầu \\(x^2+y^2+z^2+{2*u}x+{2*v}y+{2*w}z+{D}=0\\)."
    )
    return {"true": true_text, "false": false_text}


# Dạng 3 — Song song và cách đều (Ví dụ 32)
def prop_plane_parallel_equidistant_two_planes() -> Dict[str, str]:
    # Hai mặt phẳng song song: ax+by+cz+d1=0 và ax+by+cz+d2=0
    a, b, c = random.choice([1, 2, 3]), random.choice([-1, 1]), random.choice([2, 4])
    d1 = random.choice([-6, -4, -2, 2, 4])
    k = random.choice([1, 2, 3, 4])
    d2 = d1 + 2*k
    d_middle = d1 + k
    true_text = (
        f"Cho hai mặt phẳng \\((\\alpha): {format_plane_equation(a,b,c,d1)}\\) và \\((\\beta): {format_plane_equation(a,b,c,d2)}\\). "
        f"Mặt phẳng \\((P)\\) song song và cách đều hai mặt phẳng \\((\\alpha)\\) và \\((\\beta)\\) có phương trình \\((P): {format_plane_equation(a,b,c,d_middle)}\\)."
    )
    false_text = (
        f"Cho hai mặt phẳng \\((\\alpha): {format_plane_equation(a,b,c,d1)}\\) và \\((\\beta): {format_plane_equation(a,b,c,d2)}\\). "
        f"Mặt phẳng \\((P): {format_plane_equation(a,b,c,d_middle+1)}\\) song song và cách đều hai mặt phẳng \\((\\alpha)\\) và \\((\\beta)\\)."
    )
    return {"true": true_text, "false": false_text}


# Dạng 4 — (P) // (Q) và cắt cầu theo đường tròn có chu vi 6π (Câu 4)
def prop_plane_sphere_intersection_circumference() -> Dict[str, str]:
    # Mặt cầu dạng chuẩn: (x-h)^2+(y-k)^2+(z-l)^2=R^2
    center = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
    d0 = random.randint(-10, 10)
    r_circle = 3  # 6π ⇒ r=3
    R = 5         # để khoảng cách = 4
    dist_center_plane = 4
    # Chọn pháp tuyến có chuẩn đẹp
    a, b, c = random.choice([(3, 4, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)])
    norm_int = math.isqrt(a*a + b*b + c*c)
    base = a*center[0] + b*center[1] + c*center[2]
    d_true = -base + dist_center_plane * norm_int
    d_false = -base + (dist_center_plane + 1) * norm_int
    # Định dạng phương trình mặt cầu
    cx_term = f"(x{-center[0]:+})" if center[0] != 0 else "x"
    cy_term = f"(y{-center[1]:+})" if center[1] != 0 else "y"
    cz_term = f"(z{-center[2]:+})" if center[2] != 0 else "z"
    sphere_eq = f"{cx_term}^2+{cy_term}^2+{cz_term}^2={R*R}"
    true_text = (
        f"Mặt phẳng \\((P)\\) song song với \\((Q): {format_plane_equation(a,b,c,d0)}\\) và cắt mặt cầu \\((S): {sphere_eq}\\) "
        f"theo giao tuyến là đường tròn có chu vi \\(6\\pi\\) có phương trình \\((P): {format_plane_equation(a,b,c,d_true)}\\)."
    )
    false_text = (
        f"Mặt phẳng \\((P): {format_plane_equation(a,b,c,d_false)}\\) song song với \\((Q): {format_plane_equation(a,b,c,d0)}\\) "
        f"và cắt mặt cầu \\((S): {sphere_eq}\\) theo giao tuyến là đường tròn có chu vi \\(6\\pi\\)."
    )
    return {"true": true_text, "false": false_text}


PART_GROUPS: List = [
    prop_tangent_plane_at_point,
    prop_plane_parallel_tangent_to_sphere,
    prop_plane_parallel_equidistant_two_planes,
    prop_plane_sphere_intersection_circumference,
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
    tex = create_latex_document(qs, title="Tương giao mặt phẳng và mặt cầu — Dạng 1 đến 4")
    out = "plane_sphere_part_C_types_1_4.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(qs)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()


