import math
import random
from typing import List, Tuple, Dict

# Formatters

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
        if d > 0 and parts:
            parts.append(f"+ {d}")
        else:
            parts.append(str(d))
    if not parts:
        parts.append("0")
    return " ".join(parts) + " = 0"


def format_point(pt: Tuple[int, int, int]) -> str:
    return f"({pt[0]};{pt[1]};{pt[2]})"

# Helpers

def point_plane_distance_numer_normsq(a: int, b: int, c: int, d: int, P: Tuple[int, int, int]) -> Tuple[int, int]:
    numer = abs(a*P[0] + b*P[1] + c*P[2] + d)
    norm_sq = a*a + b*b + c*c
    return numer, norm_sq


def sphere_center_radius_from_eq(A: int, B: int, C: int, D: int) -> Tuple[Tuple[float, float, float], float]:
    # x^2 + y^2 + z^2 + 2ux + 2vy + 2wz + D = 0 => center (-u, -v, -w), r^2 = u^2+v^2+w^2 - D
    u, v, w = A/2.0, B/2.0, C/2.0
    cx, cy, cz = -u, -v, -w
    r_sq = u*u + v*v + w*w - D
    r = math.sqrt(abs(r_sq))
    return (cx, cy, cz), r

# Propositions for Part C

# Tangent plane at a point on sphere

def prop_tangent_plane_at_point() -> Dict[str, str]:
    # Sphere: (x-1)^2 + (y+1)^2 + (z-3)^2 = 9; point M(2,1,1) genericized
    center = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
    r = random.choice([3, 4, 5])
    # pick a point on sphere by offsetting along x
    M = (center[0] + r, center[1], center[2])
    # Tangent plane normal is vector CM
    a, b, c = (M[0]-center[0], M[1]-center[1], M[2]-center[2])
    d = -(a*M[0] + b*M[1] + c*M[2])
    true_text = f"Mặt phẳng tiếp xúc với mặt cầu tâm I{format_point(center)} bán kính {r} tại M{format_point(M)} có phương trình $(P): {format_plane_equation(a,b,c,d)}$."
    false_text = f"Mặt phẳng tiếp xúc với mặt cầu tâm I{format_point(center)} bán kính {r} tại M{format_point(M)} có phương trình $(P): {format_plane_equation(a,b,c,d+1)}$."
    return {"true": true_text, "false": false_text}

# Plane parallel to given plane and tangent to sphere

def prop_plane_parallel_tangent_to_sphere() -> Dict[str, str]:
    # Sphere general: x^2+y^2+z^2+2ux+2vy+2wz + D = 0
    u, v, w = random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)
    D = random.randint(-10, 5)
    center = (-u, -v, -w)
    r = math.sqrt(max(0.0, u*u + v*v + w*w - D))
    # Given plane: ax+by+cz+d0=0, parallel planes: same (a,b,c) with different d
    a, b, c = random.choice([1, 2, 3]), random.choice([1, 2]), random.choice([-2, -1, 1, 2])
    d0 = random.randint(-10, 10)
    # Distance from center to plane equals radius at tangency: |a*cx+b*cy+c*cz + d| / sqrt(a^2+b^2+c^2) = r
    numer_c = abs(a*center[0] + b*center[1] + c*center[2])
    norm = math.sqrt(a*a + b*b + c*c)
    # d_true candidates: d = ±(r*norm) - (a*cx+b*cy+c*cz)
    offset = r*norm
    d_true = - (a*center[0] + b*center[1] + c*center[2]) + offset
    d_false = d_true + random.choice([1, -1, 2, -2])
    true_text = f"Tồn tại mặt phẳng $(Q)$ song song với $(P): {format_plane_equation(a,b,c,int(d0))}$ và tiếp xúc với mặt cầu $x^2+y^2+z^2+{2*u}x+{2*v}y+{2*w}z+{D}=0$ có dạng $(Q): {format_plane_equation(a,b,c,int(round(d_true)))}$."
    false_text = f"$(Q): {format_plane_equation(a,b,c,int(round(d_false)))}$ cũng là mặt phẳng tiếp xúc như trên."
    return {"true": true_text, "false": false_text}

# Distance from center to plane equals radius

def prop_radius_from_center_plane_distance() -> Dict[str, str]:
    a, b, c = 4, 3, -2
    d = 1
    I = (0, -2, 1)
    numer, norm_sq = point_plane_distance_numer_normsq(a, b, c, d, I)
    true_text = f"Hình cầu tâm I{format_point(I)} tiếp xúc với mặt phẳng $(P): {format_plane_equation(a,b,c,d)}$ có bán kính $\\dfrac{{{numer}}}{{\\sqrt{{{norm_sq}}}}}$."
    false_text = f"Hình cầu tâm I{format_point(I)} tiếp xúc với mặt phẳng $(P): {format_plane_equation(a,b,c,d)}$ có bán kính $\\dfrac{{{numer+1}}}{{\\sqrt{{{norm_sq}}}}}$."
    return {"true": true_text, "false": false_text}

# Non-intersection (no common point) condition between plane and sphere parameter m

def prop_plane_sphere_no_intersection_param() -> Dict[str, str]:
    # Sphere: (x+1)^2+(y-2)^2+(z-3)^2 = 25 -> x^2+y^2+z^2+2x-4y-6z-11=0
    # Plane: 2x+y-2z+m=0; no intersection if distance from center > radius
    center = (-1, 2, 3)
    r = 5
    a, b, c = 2, 1, -2
    # distance |a*cx+b*cy+c*cz + m| / sqrt(a^2+b^2+c^2) > r => |a*cx+b*cy+c*cz + m| > r*norm
    base = a*center[0] + b*center[1] + c*center[2]
    norm = math.sqrt(a*a + b*b + c*c)
    threshold = r*norm
    # Choose m so that |base + m| > threshold
    m_true = int(math.copysign(math.ceil(threshold) + random.randint(0, 3), random.choice([-1, 1]))) - base
    true_text = f"Với $(P): 2x+y-2z+m=0$ và mặt cầu $(S): (x+1)^2+(y-2)^2+(z-3)^2=25$, khi $m$ đủ lớn về trị tuyệt đối thì $(P)$ và $(S)$ không có điểm chung."
    false_text = f"Với $(P): 2x+y-2z+m=0$ và $(S)$ như trên, luôn tồn tại giao tuyến là đường tròn với mọi $m$."
    return {"true": true_text, "false": false_text}

PART_C_GROUPS: List[List] = [
    [prop_tangent_plane_at_point],
    [prop_plane_parallel_tangent_to_sphere],
    [prop_radius_from_center_plane_distance],
    [prop_plane_sphere_no_intersection_param],
]


def generate_question(question_number: int) -> str:
    # Chọn 1 nhóm mapping trong phần C, lấy 1 mệnh đề từ nhóm đó
    selected_group = random.choice(PART_C_GROUPS)
    primary_gen = random.choice(selected_group)
    # Pool còn lại: tất cả generator của phần C trừ nhóm đã chọn
    all_gens: List = []
    for grp in PART_C_GROUPS:
        for g in grp:
            all_gens.append(g)
    remaining_pool = [g for g in all_gens if g not in selected_group]
    if len(remaining_pool) >= 3:
        other_gens = random.sample(remaining_pool, 3)
    else:
        other_gens = [random.choice(remaining_pool) for _ in range(3)] if remaining_pool else [primary_gen]*3
    selected_gens = [primary_gen] + other_gens
    props: List[Dict[str, str]] = [gen() for gen in selected_gens]
    num_true = random.randint(1, 4)
    true_indices = set(random.sample(range(4), num_true))
    labels = ['a', 'b', 'c', 'd']
    content = f"Câu {question_number}: Chọn các mệnh đề đúng.\n\n"
    for i in range(4):
        txt = props[i]['true'] if i in true_indices else props[i]['false']
        mark = '*' if i in true_indices else ''
        content += f"{mark}{labels[i]}) {txt}\n\n"
    return content


def create_latex_document(questions: List[str], title: str = "Tương giao mặt phẳng và mặt cầu - Đúng/Sai") -> str:
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
    tex = create_latex_document(qs)
    out = "plane_true_false_part_C.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(qs)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()