#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ===================== THÔNG TIN BỘ DẠNG (SET 3) =====================
# Dạng 9: Điểm trên trục Oz với ràng buộc khoảng cách tới mặt phẳng (tổng các giá trị m) — gồm Câu 11
# Dạng 10: Điểm trên trục Oz sao cho d(M,(P)) = d(M,A) — gồm Câu 12
# Dạng 11: Góc giữa hai mặt phẳng — gồm Ví dụ 8, Câu 13
# Dạng 12: Góc giữa mặt phẳng và mặt phẳng toạ độ — gồm Câu 14
# =====================================================================

import math
import random
from typing import List, Tuple, Dict
from dataclasses import dataclass


# --------------------- Hằng số cấu hình sinh dữ liệu ---------------------
SMALL_COORD_RANGE = (-3, 4)


# ----------------------------- Kiểu dữ liệu ------------------------------
@dataclass
class PlaneParams:
    a: int
    b: int
    c: int
    d: int


# ----------------------------- Tiện ích/Định dạng -----------------------------
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


def format_distance(numer: int, norm_sq: int) -> str:
    if norm_sq == 0:
        return "0"
    return f"\\dfrac{{{numer}}}{{\\sqrt{{{norm_sq}}}}}"


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


# ----------------------------- Các mệnh đề (dạng) -----------------------------
def prop_point_on_axis_distance_condition() -> Dict[str, str]:
    a = random.choice([v for v in range(-3, 4) if v != 0])
    b = random.choice([v for v in range(-3, 4) if v != 0])
    c = random.choice([v for v in range(-3, 4) if v != 0])
    d = random.randint(-6, 6)
    target_distance = random.choice([1, 2, 3])
    N2 = a * a + b * b + c * c
    # Tổng m1+m2 = -2d/c
    from fractions import Fraction
    frac = Fraction(-2 * d, c)
    sum_display = str(frac.numerator) if frac.denominator == 1 else f"\\dfrac{{{frac.numerator}}}{{{frac.denominator}}}"
    plane_eq = format_plane_equation(a, b, c, d)
    true_text = (
        f"Cho điểm \\(M(0;0;m) \\in Oz\\) và mặt phẳng \\((P): {plane_eq}\\) thỏa mãn \\(d(M,(P)) = {target_distance}\\). "
        f"Tổng các giá trị \\(m\\) bằng \\({sum_display}\\)."
    )
    false_options = [0, 1, -1, 2, -2, 3, -3] if sum_display != "0" else [1, 2, -1, -2]
    false_sum = random.choice(false_options)
    false_text = (
        f"Cho điểm \\(M(0;0;m) \\in Oz\\) và mặt phẳng \\((P): {plane_eq}\\) thỏa mãn \\(d(M,(P)) = {target_distance}\\). "
        f"Tổng các giá trị \\(m\\) bằng \\({false_sum}\\)."
    )
    return {"true": true_text, "false": false_text}


def prop_equal_distance_to_plane_and_point_on_Oz() -> Dict[str, str]:
    a, b, c, d = 0, 0, 1, 0
    A = (0, 0, 2)
    k_true = 1
    plane_eq = format_plane_equation(a, b, c, d)
    true_text = (
        f"Tồn tại điểm \\(M(0;0;{k_true})\\) sao cho \\(d(M,(P)) = d(M,A)\\) với \\(A{A}\\) và \\((P): {plane_eq}\\)."
    )
    k_false = -1
    false_text = (
        f"Tồn tại điểm \\(M(0;0;{k_false})\\) sao cho \\(d(M,(P)) = d(M,A)\\) với \\(A{A}\\) và \\((P): {plane_eq}\\)."
    )
    return {"true": true_text, "false": false_text}


def prop_angle_between_planes() -> Dict[str, str]:
    # Sinh 2 mặt phẳng ngẫu nhiên có hệ số nhỏ để hiển thị gọn
    a1, b1, c1 = [random.randint(-2, 2) for _ in range(3)]
    a2, b2, c2 = [random.randint(-2, 2) for _ in range(3)]
    # Tránh cả hai pháp tuyến cùng 0
    if a1 == b1 == c1 == 0:
        a1 = 1
    if a2 == b2 == c2 == 0:
        a2 = -1
    d1 = random.randint(-3, 3)
    d2 = random.randint(-3, 3)
    numer = abs(a1 * a2 + b1 * b2 + c1 * c2)
    den_sq = (a1 * a1 + b1 * b1 + c1 * c1) * (a2 * a2 + b2 * b2 + c2 * c2)
    plane1_eq = format_plane_equation(a1, b1, c1, d1)
    plane2_eq = format_plane_equation(a2, b2, c2, d2)
    true_text = (
        f"Góc giữa hai mặt phẳng \\((P): {plane1_eq}\\) và \\((Q): {plane2_eq}\\) có cos bằng "
        f"\\(\\dfrac{{{numer}}}{{\\sqrt{{{den_sq}}}}}\\)."
    )
    wrong_numer = numer + random.choice([1, 2])
    false_text = (
        f"Góc giữa hai mặt phẳng \\((P): {plane1_eq}\\) và \\((Q): {plane2_eq}\\) có cos bằng "
        f"\\(\\dfrac{{{wrong_numer}}}{{\\sqrt{{{den_sq}}}}}\\)."
    )
    return {"true": true_text, "false": false_text}


def prop_angle_plane_with_coordinate_plane() -> Dict[str, str]:
    a, b, c = [random.randint(-3, 3) for _ in range(3)]
    if a == b == c == 0:
        a = 1
    d = random.randint(-6, 6)
    norm_sq = a * a + b * b + c * c
    coord_plane = random.choice(["Oxy", "Oyz", "Oxz"])
    if coord_plane == "Oxy":
        numer = abs(c)
        plane_name = "Oxy"
    elif coord_plane == "Oyz":
        numer = abs(a)
        plane_name = "Oyz"
    else:
        numer = abs(b)
        plane_name = "Oxz"
    plane_eq = format_plane_equation(a, b, c, d)
    true_text = (
        f"Góc giữa mặt phẳng \\((P): {plane_eq}\\) và mặt phẳng \\(({plane_name})\\) có cos bằng "
        f"\\(\\dfrac{{{numer}}}{{\\sqrt{{{norm_sq}}}}}\\)."
    )
    wrong_numer = numer + random.choice([1, 2])
    false_text = (
        f"Góc giữa mặt phẳng \\((P): {plane_eq}\\) và mặt phẳng \\(({plane_name})\\) có cos bằng "
        f"\\(\\dfrac{{{wrong_numer}}}{{\\sqrt{{{norm_sq}}}}}\\)."
    )
    return {"true": true_text, "false": false_text}


# ----------------------------- Gom nhóm DẠNG -----------------------------
PART_GROUPS: List[List] = [
    [prop_point_on_axis_distance_condition],
    [prop_equal_distance_to_plane_and_point_on_Oz],
    [prop_angle_between_planes],
    [prop_angle_plane_with_coordinate_plane],
]


# ----------------------------- Sinh câu hỏi + LaTeX -----------------------------
def generate_question(question_number: int) -> str:
    selected_group = random.choice(PART_GROUPS)
    primary_gen = random.choice(selected_group)
    all_gens = [g for grp in PART_GROUPS for g in grp]
    remaining_pool = [g for g in all_gens if g not in selected_group]
    if len(remaining_pool) >= 3:
        other_gens = random.sample(remaining_pool, 3)
    else:
        other_gens = [random.choice(remaining_pool) for _ in range(3)] if remaining_pool else [primary_gen] * 3
    selected_gens = [primary_gen] + other_gens
    propositions: List[Dict[str, str]] = [gen() for gen in selected_gens]
    num_true = random.randint(1, 4)
    true_indices = set(random.sample(range(4), num_true))
    option_labels = ['a', 'b', 'c', 'd']
    content = f"Câu {question_number}: Chọn các mệnh đề đúng.\n\n"
    for i in range(4):
        if i in true_indices:
            text = propositions[i]['true']
            marker = '*'
        else:
            text = propositions[i]['false']
            marker = ''
        content += f"{marker}{option_labels[i]}) {text}\n\n"
    return content


def create_latex_document(questions: List[str], title: str = "Part A - Set 3 (Dạng 9-12)") -> str:
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
    questions = [generate_question(i + 1) for i in range(num_questions)]
    tex = create_latex_document(questions)
    out = "plane_true_false_part_A_set3.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(questions)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()




