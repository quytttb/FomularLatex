"""
Tập 4 — Bao gồm 4 dạng (độc lập):
- Dạng 13: Mặt phẳng chứa một trục và vuông góc với mặt phẳng (Q) — Câu 13
- Dạng 14: Mặt phẳng qua điểm và vuông góc với hai mặt phẳng cho trước — Ví dụ 20, Câu 14
- Dạng 15: Mặt phẳng qua ba điểm nằm trên các trục — Ví dụ 21, Câu 15
- Dạng 16: Mặt phẳng (ABC) từ hình chiếu của M lên các trục — Câu 16

Chạy: python3 plane_true_false_part_B_set4.py [số_câu]
Sinh ra: plane_true_false_part_B_set4.tex
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


# -------------------- Propositions (4 dạng: 13–16) --------------------

# Dạng 13: Chứa trục và vuông góc mặt phẳng (Q)
def prop_plane_contains_axis_perpendicular_given_plane() -> Dict[str, str]:
    plane_coeffs = [(random.randint(-2, 2), random.randint(-2, 2), random.randint(-3, 3), random.randint(-7, 7)) for _ in range(3)]
    axes = [("Ox", (1, 0, 0)), ("Oy", (0, 1, 0)), ("Oz", (0, 0, 1))]
    while True:
        axis_name, axis_vec = random.choice(axes)
        a, b, c, d = random.choice(plane_coeffs)
        plane_normal = (a, b, c)
        if not is_zero_vector(plane_normal):
            n = cross(axis_vec, plane_normal)
            if not is_zero_vector(n):
                break
    d_final = 0
    true_text = f"Mặt phẳng chứa trục {axis_name} và vuông góc với (Q): {format_plane_equation(a, b, c, d)} có phương trình \\({format_plane_equation(n[0], n[1], n[2], d_final)}\\)."
    alt_n = (n[0]+1, n[1], n[2]) if n[0] != -1 else (n[0], n[1]+1, n[2])
    false_text = f"Mặt phẳng chứa trục {axis_name} và vuông góc với (Q): {format_plane_equation(a, b, c, d)} có phương trình \\({format_plane_equation(alt_n[0], alt_n[1], alt_n[2], d_final)}\\)."
    return {"true": true_text, "false": false_text}


# Dạng 14: Qua điểm và vuông góc với 2 mặt phẳng
def prop_plane_perpendicular_two_given_planes() -> Dict[str, str]:
    plane_pairs = []
    for _ in range(4):
        p1 = (random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3))
        p2 = (random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3))
        d1 = random.randint(-5, 5)
        d2 = random.randint(-5, 5)
        desc1 = f"{p1[0]}x+{p1[1]}y+{p1[2]}z+{d1}=0"
        desc2 = f"{p2[0]}x+{p2[1]}y+{p2[2]}z+{d2}=0"
        plane_pairs.append(((p1, desc1), (p2, desc2)))
    points = [(random.randint(0, 3), random.randint(0, 3), random.randint(0, 3)) for _ in range(4)]
    def are_parallel(n1: Tuple[int, int, int], n2: Tuple[int, int, int]) -> bool:
        cr = cross(n1, n2)
        return cr == (0, 0, 0)
    while True:
        (P1_normal, P1_desc), (P2_normal, P2_desc) = random.choice(plane_pairs)
        if (P1_normal != (0, 0, 0)) and (P2_normal != (0, 0, 0)) and not are_parallel(P1_normal, P2_normal):
            break
    A = random.choice(points)
    n = cross(P1_normal, P2_normal)
    d = -(n[0]*A[0] + n[1]*A[1] + n[2]*A[2])
    true_text = f"Cho các mặt phẳng (P\\(_1\\)): {P1_desc} và (P\\(_2\\)): {P2_desc}. Mặt phẳng đi qua điểm A{format_point(A)} và vuông góc với cả hai mặt phẳng trên có phương trình \\({format_plane_equation(n[0], n[1], n[2], d)}\\)."
    wrong_n = flip_one_nonzero_component(n)
    wrong_d = -(wrong_n[0]*A[0] + wrong_n[1]*A[1] + wrong_n[2]*A[2])
    false_text = f"Cho các mặt phẳng (P\\(_1\\)): {P1_desc} và (P\\(_2\\)): {P2_desc}. Mặt phẳng đi qua điểm A{format_point(A)} và vuông góc với cả hai mặt phẳng trên có phương trình \\({format_plane_equation(wrong_n[0], wrong_n[1], wrong_n[2], wrong_d)}\\)."
    return {"true": true_text, "false": false_text}


# Dạng 15: Qua 3 điểm trên các trục (kiểu Ví dụ 21)
def prop_plane_through_three_points() -> Dict[str, str]:
    point_sets = [
        ((1, 0, 0), (0, -2, 0), (0, 0, 3)),
        ((2, 0, 0), (0, 3, 0), (0, 0, -1)),
        ((1, 0, 0), (0, 1, 0), (0, 0, 2)),
        ((3, 0, 0), (0, -1, 0), (0, 0, 4))
    ]
    while True:
        A, B, C = random.choice(point_sets)
        AB = subtract(B, A)
        AC = subtract(C, A)
        n = cross(AB, AC)
        if not is_zero_vector(n):
            break
    a, b, c = n
    d = -(a*A[0] + b*A[1] + c*A[2])
    true_text = f"Phương trình mặt phẳng qua A{format_point(A)}, B{format_point(B)}, C{format_point(C)} là \\((P): {format_plane_equation(a,b,c,d)}\\)."
    false_text = f"Phương trình mặt phẳng qua A{format_point(A)}, B{format_point(B)}, C{format_point(C)} là \\((P): {format_plane_equation(a,b,c,d+1)}\\)."
    return {"true": true_text, "false": false_text}


# Dạng 16: (ABC) từ hình chiếu của M trên các trục
def prop_plane_from_projections_ABC() -> Dict[str, str]:
    M_points = [(random.randint(1, 5), random.randint(1, 5), random.randint(1, 5)) for _ in range(4)]
    M = random.choice(M_points)
    a = M[1] * M[2]
    b = M[0] * M[2]
    c = M[0] * M[1]
    d = -M[0] * M[1] * M[2]
    true_text = f"Với điểm M{format_point(M)}, gọi A, B, C lần lượt là hình chiếu của M trên các trục tọa độ. Khi đó phương trình mặt phẳng (ABC) là \\({format_plane_equation(a, b, c, d)}\\)."
    wrong_a, wrong_b = b, a
    if a == b:
        wrong_a = a + 1
    false_text = f"Với điểm M{format_point(M)}, gọi A, B, C lần lượt là hình chiếu của M trên các trục tọa độ. Khi đó phương trình mặt phẳng (ABC) là \\({format_plane_equation(wrong_a, wrong_b, c, d)}\\)."
    return {"true": true_text, "false": false_text}


# -------------------- Document builders --------------------

def generate_question(question_number: int) -> str:
    gens = [
        prop_plane_contains_axis_perpendicular_given_plane,
        prop_plane_perpendicular_two_given_planes,
        prop_plane_through_three_points,
        prop_plane_from_projections_ABC,
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


def create_latex_document(questions: List[str], title: str = "Các bài toán về viết phương trình mặt phẳng - Đúng/Sai (Tập 4)") -> str:
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
    out = "plane_true_false_part_B_set4.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(questions)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()


