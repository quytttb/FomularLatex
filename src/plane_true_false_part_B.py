import random
from typing import List, Tuple, Dict

# Simple formatters

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

# Vector/plane helpers

def cross(u: Tuple[int, int, int], v: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return (u[1]*v[2] - u[2]*v[1], u[2]*v[0] - u[0]*v[2], u[0]*v[1] - u[1]*v[0])


def subtract(p: Tuple[int, int, int], q: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return (p[0]-q[0], p[1]-q[1], p[2]-q[2])

# Propositions (Part B)

# Ví dụ 21 - Câu 16 (phần B): planes through 3 points and (ABC) from projections

def prop_plane_through_three_points() -> Dict[str, str]:
    A = (1, 0, 0)
    B = (0, -2, 0)
    C = (0, 0, 3)
    AB = subtract(B, A)
    AC = subtract(C, A)
    n = cross(AB, AC)
    a, b, c = n
    d = -(a*A[0] + b*A[1] + c*A[2])
    true_text = f"Phương trình mặt phẳng qua A{format_point(A)}, B{format_point(B)}, C{format_point(C)} là $(P): {format_plane_equation(a,b,c,d)}$."
    # false: tweak d by ±1
    false_text = f"Phương trình mặt phẳng qua A{format_point(A)}, B{format_point(B)}, C{format_point(C)} là $(P): {format_plane_equation(a,b,c,d+1)}$."
    return {"true": true_text, "false": false_text}


def prop_plane_from_projections_ABC() -> Dict[str, str]:
    # Given M(1,2,3) -> projections give A(1,0,0), B(0,2,0), C(0,0,3) and plane x/1 + y/2 + z/3 = 1 -> 6x+3y+2z-6=0
    M = (1, 2, 3)
    A, B, C = (M[0], 0, 0), (0, M[1], 0), (0, 0, M[2])
    true_text = "Với điểm M(1;2;3), gọi A, B, C lần lượt là hình chiếu của M trên các trục tọa độ. Khi đó phương trình mặt phẳng (ABC) là $6x+3y+2z-6=0$."
    false_text = "Với điểm M(1;2;3), gọi A, B, C lần lượt là hình chiếu của M trên các trục tọa độ. Khi đó phương trình mặt phẳng (ABC) là $2x+3y+6z-6=0$."
    return {"true": true_text, "false": false_text}

# Ví dụ 22 - Câu 18: parallel with (ABC) from given M

def prop_parallel_to_ABC_from_M() -> Dict[str, str]:
    M = (-3, 2, 4)
    # (ABC): x/|xM| + y/|yM| + z/|zM| = 1 -> 4x - 6y - 3z + 12 = 0 (as in tex)
    true_text = "Cho điểm M(-3;2;4). Mặt phẳng song song với (ABC) (ABC từ hình chiếu của M) có phương trình $4x-6y-3z+12=0$."
    false_text = "Cho điểm M(-3;2;4). Mặt phẳng song song với (ABC) có phương trình $3x-6y-4z+12=0$."
    return {"true": true_text, "false": false_text}

# Ví dụ 25 - Câu 23 - Câu 24: minimal volume and related optimization forms

def prop_min_volume_plane_through_M() -> Dict[str, str]:
    # For M(1,2,3), min volume plane through M cutting axes gives x/1 + y/2 + z/3 = 1 -> 6x+3y+2z-6=0
    M = (1, 2, 3)
    true_text = "Mặt phẳng đi qua M(1;2;3) cắt ba trục tọa độ sao cho thể tích tứ diện OABC nhỏ nhất có phương trình $6x+3y+2z-18=0$."
    false_text = "Mặt phẳng đi qua M(1;2;3) cắt ba trục tọa độ sao cho thể tích tứ diện OABC nhỏ nhất có phương trình $6x+3y+3z-21=0$."
    return {"true": true_text, "false": false_text}


def prop_min_sum_inverse_squares() -> Dict[str, str]:
    # Shape-only statement consistent with tex style
    true_text = "Với M(1;2;3), mặt phẳng (P) để $T=\\dfrac{1}{OA^2}+\\dfrac{1}{OB^2}+\\dfrac{1}{OC^2}$ nhỏ nhất có dạng $x+ay+bz+c=0$."
    false_text = "Với M(1;2;3), mặt phẳng (P) để $T$ nhỏ nhất có dạng $ax+by+cz+d=0$ với $a=b=c=0$."
    return {"true": true_text, "false": false_text}

# Pool/group registry for Part B
PART_B_GROUPS: List[List] = [
    [prop_plane_through_three_points, prop_plane_from_projections_ABC],  # Ví dụ 21 - Câu 16 (phần B)
    [prop_parallel_to_ABC_from_M],                                       # Ví dụ 22 - Câu 18
    [prop_min_volume_plane_through_M, prop_min_sum_inverse_squares],     # Ví dụ 25 - Câu 23 - Câu 24
]


def generate_question(question_number: int) -> str:
    # Chọn 1 nhóm mapping trong phần B, lấy 1 mệnh đề từ nhóm đó
    selected_group = random.choice(PART_B_GROUPS)
    primary_gen = random.choice(selected_group)
    # Pool còn lại là tất cả generator của phần B trừ nhóm đã chọn
    all_gens: List = []
    for grp in PART_B_GROUPS:
        for g in grp:
            all_gens.append(g)
    remaining_pool = [g for g in all_gens if g not in selected_group]
    if len(remaining_pool) >= 3:
        other_gens = random.sample(remaining_pool, 3)
    else:
        other_gens = [random.choice(remaining_pool) for _ in range(3)] if remaining_pool else [primary_gen]*3
    selected_gens = [primary_gen] + other_gens
    propositions: List[Dict[str, str]] = [gen() for gen in selected_gens]
    num_true = random.randint(1, 4)
    true_indices = set(random.sample(range(4), num_true))
    option_labels = ['a', 'b', 'c', 'd']
    content = f"Câu {question_number}: Chọn các mệnh đề đúng.\n\n"
    for i in range(4):
        text = propositions[i]['true'] if i in true_indices else propositions[i]['false']
        marker = '*' if i in true_indices else ''
        content += f"{marker}{option_labels[i]}) {text}\n\n"
    return content


def create_latex_document(questions: List[str], title: str = "Các bài toán về viết phương trình mặt phẳng - Đúng/Sai") -> str:
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
    out = "plane_true_false_part_B.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(questions)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()