#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ===================== THÔNG TIN BỘ DẠNG (SET 4) =====================
# Dạng 13: Hai mặt phẳng song song – tìm tham số — gồm Ví dụ 9, Câu 15
# Dạng 14: Hai mặt phẳng cắt nhau – điều kiện tham số — gồm Câu 16
# Dạng 15: Hai mặt phẳng vuông góc – điều kiện tham số — gồm Câu 17
# =====================================================================

import random
from typing import List, Tuple, Dict


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


# ----------------------------- Các mệnh đề (dạng) -----------------------------
def prop_parallel_condition_with_parameter() -> Dict[str, str]:
    a1, b1, c1 = random.choice([1, 2]), random.choice([1, 2]), random.choice([1, -1])
    d1 = random.randint(-3, 3)
    k = random.choice([2, 3, -2])
    a2, b2 = k * a1, k * b1
    d2 = random.randint(-3, 3)
    m_true = k * c1
    while d2 == k * d1:
        d2 = random.randint(-3, 3)
    plane1_eq = format_plane_equation(a1, b1, c1, d1)
    parts = []
    parts.append("x" if a2 == 1 else ("-x" if a2 == -1 else f"{a2}x"))
    if b2 != 0:
        if b2 == 1:
            parts.append("+ y")
        elif b2 == -1:
            parts.append("- y")
        elif b2 > 0:
            parts.append(f"+ {b2}y")
        else:
            parts.append(f"- {abs(b2)}y")
    parts.append("+ mz")
    if d2 > 0:
        parts.append(f"+ {d2}")
    elif d2 < 0:
        parts.append(f"- {abs(d2)}")
    plane2_eq = " ".join(parts) + " = 0"
    true_text = f"Với \\(m = {m_true}\\), hai mặt phẳng \\((P): {plane1_eq}\\) và \\((Q): {plane2_eq}\\) song song."
    m_false = m_true + random.choice([1, -1, 2, -2])
    false_text = f"Với \\(m = {m_false}\\), hai mặt phẳng \\((P): {plane1_eq}\\) và \\((Q): {plane2_eq}\\) song song."
    return {"true": true_text, "false": false_text}


def prop_planes_intersect_condition_m() -> Dict[str, str]:
    m_true = random.randint(-4, 4)
    true_text = (
        f"Hai mặt phẳng \\((P): 2x + 2y - z = 0\\) và \\((Q): x + y + {m_true}z + 1 = 0\\) cắt nhau."
    )
    false_text = (
        "Hai mặt phẳng \\((P): 2x + 2y - z = 0\\) và \\((Q): x + y - \\frac{1}{2}z + 1 = 0\\) cắt nhau."
    )
    return {"true": true_text, "false": false_text}


def prop_planes_perpendicular_condition_m() -> Dict[str, str]:
    m_true = random.choice([2, -2])
    m_sq_true = m_true * m_true
    true_text = (
        f"Hai mặt phẳng \\((\\alpha): {m_sq_true}x - y + {(m_sq_true - 2)}z + 2 = 0\\) và \\((\\beta): 2x + {m_sq_true}y - 2z + 1 = 0\\) vuông góc."
    )
    m_false = random.choice([0, 1, 3, -1, -3])
    m_sq_false = m_false * m_false
    false_text = (
        f"Hai mặt phẳng \\((\\alpha): {m_sq_false}x - y + {(m_sq_false - 2)}z + 2 = 0\\) và \\((\\beta): 2x + {m_sq_false}y - 2z + 1 = 0\\) vuông góc."
    )
    return {"true": true_text, "false": false_text}


# ----------------------------- Gom nhóm DẠNG -----------------------------
PART_GROUPS: List[List] = [
    [prop_parallel_condition_with_parameter],
    [prop_planes_intersect_condition_m],
    [prop_planes_perpendicular_condition_m],
]


# ----------------------------- Sinh câu hỏi + LaTeX -----------------------------
def generate_question(question_number: int) -> str:
    selected_group = random.choice(PART_GROUPS)
    primary_gen = random.choice(selected_group)
    all_gens = [g for grp in PART_GROUPS for g in grp]
    remaining_pool = [g for g in all_gens if g not in selected_group]
    # Vì file cuối chỉ có 3 dạng, vẫn sinh 4 mệnh đề bằng cách cho phép lặp nếu thiếu
    other_gens = []
    while len(other_gens) < 3:
        other_gens.append(random.choice(remaining_pool or all_gens))
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


def create_latex_document(questions: List[str], title: str = "Part A - Set 4 (Dạng 13-15)") -> str:
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
    questions = [generate_question(i + 1) for i in range(num_questions)]
    tex = create_latex_document(questions)
    out = "plane_true_false_part_A_set4.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(questions)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()




