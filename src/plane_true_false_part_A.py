import math
import random
from typing import List, Tuple, Dict

# Utilities

def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


def simplify_fraction(numer: int, denom: int) -> Tuple[int, int]:
    if denom == 0:
        return (numer, denom)
    g = gcd(numer, denom)
    numer //= g
    denom //= g
    if denom < 0:
        numer = -numer
        denom = -denom
    return numer, denom


def format_signed(value: int) -> str:
    return f"+ {abs(value)}" if value > 0 else (f"- {abs(value)}" if value < 0 else "+ 0")


def format_plane_equation(a: int, b: int, c: int, d: int) -> str:
    parts: List[str] = []
    # ax
    if a == 1:
        parts.append("x")
    elif a == -1:
        parts.append("-x")
    elif a != 0:
        parts.append(f"{a}x")
    # by
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
    # cz
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
        if d > 0 and parts:
            parts.append(f"+ {d}")
        else:
            parts.append(str(d))
    if not parts:
        parts.append("0")
    return " ".join(parts) + " = 0"


def format_point(pt: Tuple[int, int, int]) -> str:
    return f"({pt[0]};{pt[1]};{pt[2]})"


def are_collinear(v: Tuple[int, int, int], w: Tuple[int, int, int]) -> bool:
    x1, y1, z1 = v
    x2, y2, z2 = w
    return (x1 * y2 == y1 * x2) and (x1 * z2 == z1 * x2) and (y1 * z2 == z1 * y2)


def dot(v: Tuple[int, int, int], w: Tuple[int, int, int]) -> int:
    return v[0]*w[0] + v[1]*w[1] + v[2]*w[2]


def cross(u: Tuple[int, int, int], v: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return (
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0]
    )


def point_plane_distance(a: int, b: int, c: int, d: int, P: Tuple[int, int, int]) -> Tuple[int, int]:
    numer = abs(a*P[0] + b*P[1] + c*P[2] + d)
    denom = int(math.isqrt(a*a + b*b + c*c))
    # Keep radical if not perfect square; we will indicate as numerator/sqrt(norm_sq)
    norm_sq = a*a + b*b + c*c
    return numer, norm_sq


def format_distance(numer: int, norm_sq: int) -> str:
    # returns LaTeX like \dfrac{numer}{\sqrt{norm_sq}}
    if norm_sq == 0:
        return "0"
    return f"\\dfrac{{{numer}}}{{\\sqrt{{{norm_sq}}}}}"


# Proposition generators for Part A

# Group: Ví dụ 4,5 (distance point-plane) + Câu 7 (reflection => AB = 2*distance)

def prop_point_plane_distance() -> Dict[str, str]:
    # Generate random plane and point
    a = random.choice([v for v in range(-5, 6) if v != 0])
    b = random.randint(-5, 5)
    c = random.randint(-5, 5)
    if a == 0 and b == 0 and c == 0:
        a = 1
    d = random.randint(-8, 8)
    P = (random.randint(-4, 4), random.randint(-4, 4), random.randint(-4, 4))
    numer, norm_sq = point_plane_distance(a, b, c, d, P)
    true_text = f"Khoảng cách từ điểm A{format_point(P)} đến mặt phẳng (P): {format_plane_equation(a,b,c,d)} bằng $ {format_distance(numer, norm_sq)} $."
    # false: tweak numerator by ±1..3 (ensure different)
    delta = random.choice([1, 2, 3])
    false_numer = numer + delta if numer != 0 else numer + 2
    false_text = f"Khoảng cách từ điểm A{format_point(P)} đến mặt phẳng (P): {format_plane_equation(a,b,c,d)} bằng $ {format_distance(false_numer, norm_sq)} $."
    return {"true": true_text, "false": false_text}


def prop_reflection_segment_length() -> Dict[str, str]:
    # AB length for reflection across plane equals 2 * distance(A, plane)
    a = random.choice([v for v in range(-4, 5) if v != 0])
    b = random.randint(-4, 4)
    c = random.randint(-4, 4)
    if a == 0 and b == 0 and c == 0:
        b = 1
    d = random.randint(-6, 6)
    A = (random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3))
    numer, norm_sq = point_plane_distance(a, b, c, d, A)
    # AB = 2 * numer / sqrt(norm_sq)
    true_text = f"Gọi B là điểm đối xứng của A{format_point(A)} qua mặt phẳng (P): {format_plane_equation(a,b,c,d)}. Khi đó độ dài $AB$ bằng $ {format_distance(2*numer, norm_sq)} $."
    # false: tweak numerator
    delta = random.choice([1, 2])
    false_text = f"Gọi B là điểm đối xứng của A{format_point(A)} qua mặt phẳng (P): {format_plane_equation(a,b,c,d)}. Khi đó độ dài $AB$ bằng $ {format_distance(2*numer + delta, norm_sq)} $."
    return {"true": true_text, "false": false_text}

# Group: Ví dụ 3 (point on plane) - Câu 4 (m-parameter point on plane)

def prop_point_on_plane_membership() -> Dict[str, str]:
    a = random.choice([v for v in range(-4, 5) if v != 0])
    b = random.randint(-4, 4)
    c = random.randint(-4, 4)
    d = random.randint(-6, 6)
    # Create a point on plane
    # Choose x,y then solve for z if c != 0, else adjust differently
    x = random.randint(-3, 3)
    y = random.randint(-3, 3)
    if c == 0:
        # ensure a*x + b*y + d = 0
        z = random.randint(-3, 3)
        d = -(a*x + b*y + c*z)
    else:
        rhs = -(a*x + b*y + d)
        # ensure divisible for integer z sometimes; otherwise accept fractional but we keep integer
        z = rhs // c
        d = -(a*x + b*y + c*z)
    P = (x, y, z)
    true_text = f"Điểm M{format_point(P)} thuộc mặt phẳng (P): {format_plane_equation(a,b,c,d)}."
    # false: modify one coordinate
    Pf = (P[0] + random.choice([-1, 1]), P[1], P[2])
    false_text = f"Điểm M{format_point(Pf)} thuộc mặt phẳng (P): {format_plane_equation(a,b,c,d)}."
    return {"true": true_text, "false": false_text}


def prop_point_with_m_on_plane() -> Dict[str, str]:
    # Point A(m; m-1; 1+2m) in plane ax+by+cz+d=0 -> find m value. We convert to T/F: with given m value, statement true/false
    a = random.choice([v for v in range(-3, 4) if v != 0])
    b = random.randint(-3, 3)
    c = random.randint(-3, 3)
    d = random.randint(-6, 6)
    # Define point pattern like in tex
    # Compute m solving a*m + b*(m-1) + c*(1+2m) + d = 0
    coeff_m = a + b + 2*c
    const_term = -b + c + d
    # Ensure solvable (coeff_m != 0)
    if coeff_m == 0:
        coeff_m = 1
    m_true = -const_term / coeff_m
    # Prefer integer m
    if abs(m_true - round(m_true)) < 1e-9:
        m_display = str(int(round(m_true)))
    else:
        # format as fraction p/q
        from fractions import Fraction
        frac = Fraction(-const_term, coeff_m)
        m_display = f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
    true_text = f"Với $m = {m_display}$, điểm $A(m;\, m-1;\, 1+2m)$ thuộc mặt phẳng (P): {format_plane_equation(a,b,c,d)}."
    # false: tweak m by +1
    if isinstance(m_true, float) and abs(m_true - round(m_true)) < 1e-9:
        m_false_display = str(int(round(m_true)) + random.choice([1, -1]))
    else:
        m_false_display = "0" if m_display != "0" else "1"
    false_text = f"Với $m = {m_false_display}$, điểm $A(m;\, m-1;\, 1+2m)$ thuộc mặt phẳng (P): {format_plane_equation(a,b,c,d)}."
    return {"true": true_text, "false": false_text}

# Group: Ví dụ 7 (distance constraint) - Câu 12 (equal distances)

def prop_equal_distance_to_plane_and_point_on_Oz() -> Dict[str, str]:
    # Given plane ax+by+cz+d=0, point A(xa,ya,za). Find M on Oz: (0,0,k) such that d(M,plane) = d(M,A)
    a = random.choice([v for v in range(-4, 5) if v != 0])
    b = random.randint(-4, 4)
    c = random.choice([v for v in range(-4, 5) if v != 0])
    d = random.randint(-6, 6)
    A = (random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3))
    # Distance to plane: |a*0 + b*0 + c*k + d| / sqrt(norm_sq) = |c*k + d| / sqrt(norm_sq)
    # Distance to A: sqrt((0-xa)^2 + (0-ya)^2 + (k-za)^2)
    # Equate squares: (c*k + d)^2 / (a^2 + b^2 + c^2) = xa^2 + ya^2 + (k - za)^2
    norm_sq = a*a + b*b + c*c
    xa2 = A[0]*A[0]
    ya2 = A[1]*A[1]
    za = A[2]
    # (c*k + d)^2 = norm_sq*(xa^2 + ya^2 + (k - za)^2)
    # Expand: c^2 k^2 + 2cd k + d^2 = norm_sq*(xa^2 + ya^2 + k^2 - 2za k + za^2)
    # Bring to one side: (c^2 - norm_sq)k^2 + (2cd + 2 norm_sq za)k + (d^2 - norm_sq*(xa^2 + ya^2 + za^2)) = 0
    A2 = c*c - norm_sq
    B2 = 2*c*d + 2*norm_sq*za
    C2 = d*d - norm_sq*(xa2 + ya2 + za*za)
    # Solve quadratic; pick an integer-ish root if possible
    disc = B2*B2 - 4*A2*C2
    k_true: float
    if A2 == 0:
        # Linear case
        if B2 == 0:
            k_true = 0.0
        else:
            k_true = -C2 / B2
    else:
        if disc < 0:
            k_true = 0.0
        else:
            sqrt_disc = math.sqrt(disc)
            k1 = (-B2 + sqrt_disc) / (2*A2)
            k2 = (-B2 - sqrt_disc) / (2*A2)
            k_true = k1 if abs(k1) <= abs(k2) else k2
    # Format
    k_disp = f"{k_true:.2f}" if abs(k_true - round(k_true)) > 1e-9 else str(int(round(k_true)))
    true_text = f"Tồn tại điểm $M(0;0;{k_disp})$ sao cho $d(M,(P)) = d(M,A)$ với $A{format_point(A)}$ và $(P): {format_plane_equation(a,b,c,d)}$."
    k_false = (float(k_true) + random.choice([-1.0, 1.0, 2.0])) if isinstance(k_true, float) else (k_true + 1)
    k_false_disp = f"{k_false:.2f}" if abs(k_false - round(k_false)) > 1e-9 else str(int(round(k_false)))
    false_text = f"Tồn tại điểm $M(0;0;{k_false_disp})$ sao cho $d(M,(P)) = d(M,A)$ với $A{format_point(A)}$ và $(P): {format_plane_equation(a,b,c,d)}$."
    return {"true": true_text, "false": false_text}

# Group: Ví dụ 8 (angle between planes) - Câu 14 (angle with Oxy)

def prop_angle_between_planes() -> Dict[str, str]:
    # Angle between planes P: a1x+b1y+c1z+d1=0 and Q: a2x+b2y+c2z+d2=0
    a1, b1, c1 = random.choice([v for v in range(-3, 4) if v != 0]), random.randint(-3, 3), random.randint(-3, 3)
    a2, b2, c2 = random.choice([v for v in range(-3, 4) if v != 0]), random.randint(-3, 3), random.randint(-3, 3)
    d1, d2 = random.randint(-6, 6), random.randint(-6, 6)
    n1 = (a1, b1, c1)
    n2 = (a2, b2, c2)
    num = abs(dot(n1, n2))
    den = math.sqrt((a1*a1 + b1*b1 + c1*c1) * (a2*a2 + b2*b2 + c2*c2))
    cos_val = min(1.0, max(0.0, num / den if den != 0 else 0.0))
    angle_deg = math.degrees(math.acos(cos_val))
    angle_disp = f"{angle_deg:.0f}^\\circ"
    true_text = f"Góc giữa hai mặt phẳng $(P): {format_plane_equation(a1,b1,c1,d1)}$ và $(Q): {format_plane_equation(a2,b2,c2,d2)}$ bằng $ {angle_disp} $."
    # false: tweak by 15 degrees
    false_angle = max(0, int(round(angle_deg)) + random.choice([-30, -15, 15, 30]))
    false_text = f"Góc giữa hai mặt phẳng $(P): {format_plane_equation(a1,b1,c1,d1)}$ và $(Q): {format_plane_equation(a2,b2,c2,d2)}$ bằng $ {false_angle}^\\circ $."
    return {"true": true_text, "false": false_text}


def prop_angle_plane_with_Oxy() -> Dict[str, str]:
    # Angle between plane P and Oxy is angle between normals and (0,0,1)
    a, b = random.randint(-3, 3), random.randint(-3, 3)
    c = random.choice([v for v in range(-3, 4) if v != 0])
    d = random.randint(-6, 6)
    n = (a, b, c)
    num = abs(c)
    den = math.sqrt(a*a + b*b + c*c)
    cos_val = min(1.0, max(0.0, num / den if den != 0 else 0.0))
    angle_deg = math.degrees(math.acos(cos_val))
    angle_disp = f"{angle_deg:.0f}^\\circ"
    true_text = f"Góc giữa mặt phẳng $(P): {format_plane_equation(a,b,c,d)}$ và mặt phẳng $(Oxy)$ bằng $ {angle_disp} $."
    false_angle = max(0, int(round(angle_deg)) + random.choice([-30, -15, 15, 30]))
    false_text = f"Góc giữa mặt phẳng $(P): {format_plane_equation(a,b,c,d)}$ và mặt phẳng $(Oxy)$ bằng $ {false_angle}^\\circ $."
    return {"true": true_text, "false": false_text}

# Group: Ví dụ 9 (parallel planes), Câu 16 (intersect), Câu 17 (perpendicular)

def prop_planes_parallel_with_params_sum() -> Dict[str, str]:
    # Build two planes with normals proportional: (2,1,m) and (1,n,2) like in tex style
    t = random.choice([1, 2, 3])
    m = 2 * t  # ensure integer
    n = 1 * t
    # Planes (P): 2x + y + m z + p = 0 and (Q): x + n y + 2z + q = 0 (constants irrelevant)
    p, q = random.randint(-5, 5), random.randint(-5, 5)
    true_sum = m + n
    true_text = f"Cho $(P): 2x + y + {m}z {format_signed(p)} = 0$ và $(Q): x + {n}y + 2z {format_signed(q)} = 0$ song song nhau. Khi đó $m + n = {true_sum}$."
    false_text = f"Cho $(P): 2x + y + {m}z {format_signed(p)} = 0$ và $(Q): x + {n}y + 2z {format_signed(q)} = 0$ song song nhau. Khi đó $m + n = {true_sum + random.choice([-2,-1,1,2])}$."
    return {"true": true_text, "false": false_text}


def prop_planes_intersect_condition_m() -> Dict[str, str]:
    # (P): 2x+2y - z = 0 and (Q): x + y + m z + 1 = 0 intersect iff normals not parallel
    m_true = random.choice([v for v in range(-4, 5) if v != -0.5])
    true_text = f"Hai mặt phẳng $(P): 2x + 2y - z = 0$ và $(Q): x + y + {m_true}z + 1 = 0$ cắt nhau."
    false_text = f"Hai mặt phẳng $(P): 2x + 2y - z = 0$ và $(Q): x + y - \frac{1}{2}z + 1 = 0$ cắt nhau."
    return {"true": true_text, "false": false_text}


def prop_planes_perpendicular_condition_m() -> Dict[str, str]:
    # (alpha): m^2 x - y + (m^2 - 2) z + 2 = 0 and (beta): 2x + m^2 y - 2z + 1 = 0 perpendicular when dot(n1,n2)=0
    m = random.choice([1, 2, 3])
    n1 = (m*m, -1, m*m - 2)
    n2 = (2, m*m, -2)
    is_perp = (dot(n1, n2) == 0)
    # Build true by picking m that satisfies
    if not is_perp:
        # pick m=1 or 2 which usually works for the tex examples
        m = 1
    true_text = f"Hai mặt phẳng $(\alpha): {m*m}x - y + {(m*m - 2)}z + 2 = 0$ và $(\beta): 2x + {m*m}y - 2z + 1 = 0$ vuông góc."
    # false with m+1
    mf = m + 1
    false_text = f"Hai mặt phẳng $(\alpha): {mf*mf}x - y + {(mf*mf - 2)}z + 2 = 0$ và $(\beta): 2x + {mf*mf}y - 2z + 1 = 0$ vuông góc."
    return {"true": true_text, "false": false_text}


# Registry of proposition groups for Part A
PART_A_GROUPS: List[List] = [
    # Ví dụ 4,5 + Câu 7
    [prop_point_plane_distance, prop_reflection_segment_length],
    # Ví dụ 3 - Câu 4
    [prop_point_on_plane_membership, prop_point_with_m_on_plane],
    # Ví dụ 7 - Câu 12
    [prop_equal_distance_to_plane_and_point_on_Oz],
    # Ví dụ 8 - Câu 14
    [prop_angle_between_planes, prop_angle_plane_with_Oxy],
    # Ví dụ 9 - Câu 16 - Câu 17
    [prop_planes_parallel_with_params_sum, prop_planes_intersect_condition_m, prop_planes_perpendicular_condition_m],
]


def generate_question(question_number: int) -> str:
    # Chọn 1 nhóm mapping trong phần A, lấy 1 mệnh đề từ nhóm đó
    selected_group = random.choice(PART_A_GROUPS)
    primary_gen = random.choice(selected_group)
    # Tạo pool còn lại: tất cả generator của phần A trừ nhóm đã chọn
    all_gens: List = []
    for grp in PART_A_GROUPS:
        for g in grp:
            all_gens.append(g)
    # Loại bỏ các generator thuộc nhóm đã chọn
    remaining_pool = [g for g in all_gens if g not in selected_group]
    # Lấy 3 generator khác nhau từ remaining_pool (nếu thiếu thì cho phép lặp)
    if len(remaining_pool) >= 3:
        other_gens = random.sample(remaining_pool, 3)
    else:
        other_gens = [random.choice(remaining_pool) for _ in range(3)] if remaining_pool else [primary_gen]*3
    selected_gens = [primary_gen] + other_gens
    # Sinh 4 mệnh đề
    propositions: List[Dict[str, str]] = [gen() for gen in selected_gens]
    # Gán ngẫu nhiên mệnh đề đúng
    num_true = random.randint(1, 4)
    true_indices = set(random.sample(range(4), num_true))
    option_labels = ['a', 'b', 'c', 'd']
    content = f"Câu {question_number}: Chọn các mệnh đề đúng.\n\n"
    for i in range(4):
        text = propositions[i]['true'] if i in true_indices else propositions[i]['false']
        marker = '*' if i in true_indices else ''
        content += f"{marker}{option_labels[i]}) {text}\n\n"
    return content


def create_latex_document(questions: List[str], title: str = "Các bài toán về các thông số liên quan - Đúng/Sai") -> str:
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
    random.seed()
    questions = [generate_question(i+1) for i in range(num_questions)]
    tex = create_latex_document(questions)
    out = "plane_true_false_part_A.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(questions)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()