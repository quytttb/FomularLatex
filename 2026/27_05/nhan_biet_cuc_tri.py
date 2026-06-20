import os
import sys
import random
from typing import Tuple, List


# ─────────────────────────────────────────────────────────────────────────────
# Formatting helpers
# ─────────────────────────────────────────────────────────────────────────────

def format_poly(coeffs: List[int], powers: List[str]) -> str:
    """Format polynomial expression from coefficients and power symbols."""
    res = ""
    for c, p in zip(coeffs, powers):
        if c == 0:
            continue
        sign = " + " if c > 0 else " - "
        val = abs(c)
        val_str = "" if (val == 1 and p != "") else str(val)
        res += f"{sign}{val_str}{p}"

    if res.startswith(" + "):
        res = res[3:]
    elif res.startswith(" - "):
        res = "-" + res[3:]
    return res if res else "0"


def format_rational(a: int, b: int, c: int, d: int, e: int) -> str:
    """Format (ax²+bx+c)/(dx+e) as a LaTeX fraction."""
    num = format_poly([a, b, c], ["x^2", "x", ""])
    den = format_poly([d, e], ["x", ""])
    return rf"\frac{{{num}}}{{{den}}}"


# ─────────────────────────────────────────────────────────────────────────────
# Function generators
# ─────────────────────────────────────────────────────────────────────────────

def generate_cubic() -> Tuple[str, str, str, str, str]:
    """
    Generate y = ax³ + bx² + cx + d with two distinct extrema at integer x.
    Returns (func_str, x_CT, y_CT, x_CD, y_CD) as strings.
    If a > 0: local max at x1, local min at x2  (x1 < x2)
    If a < 0: local min at x1, local max at x2
    """
    while True:
        a = random.choice([-2, -1, 1, 2])
        x1 = random.randint(-3, 2)
        x2 = random.randint(x1 + 1, 3)

        # y' = 3ax² + 2bx + c has roots x1, x2
        # ⟹ b = -3a(x1+x2)/2  (must be integer)
        if abs(a) == 1 and (x1 + x2) % 2 != 0:
            continue

        b = int(-1.5 * a * (x1 + x2))
        c = int(3 * a * x1 * x2)
        d = random.randint(-5, 5)

        y1 = a * x1**3 + b * x1**2 + c * x1 + d
        y2 = a * x2**3 + b * x2**2 + c * x2 + d

        # Require distinct y-values, and non-zero x-values (nicer distractors)
        if y1 != y2 and x1 != 0 and x2 != 0:
            break

    # a > 0: x1 is local max (CĐ), x2 is local min (CT)
    if a > 0:
        x_CD, y_CD = x1, y1
        x_CT, y_CT = x2, y2
    else:
        x_CT, y_CT = x1, y1
        x_CD, y_CD = x2, y2

    func_str = format_poly([a, b, c, d], ["x^3", "x^2", "x", ""])
    return func_str, str(x_CT), str(y_CT), str(x_CD), str(y_CD)


def generate_quartic():
    """
    Generate y = ax⁴ + bx² + c  (even function with three extrema).

    The single extremum at x=0 is what we ask about in the question.
    The two symmetric extrema at x=±k are used as SEPARATE distractors
    to avoid the ± notation in answer choices.

    Returns:
        func_str   – LaTeX of the function
        x_single   – "0"  (hoành độ of the lone extremum)
        y_single   – str  (tung độ of the lone extremum)
        y_sym      – str  (tung độ of the symmetric extrema at ±k)
        k_pos      – str  (positive k, e.g. "2")
        k_neg      – str  (negative k, e.g. "-2")
        is_single_cd – bool: True if x=0 is a local max (CĐ)
    """
    a = random.choice([-2, -1, 1, 2])
    k = random.choice([1, 2, 3])
    b = -2 * a * k**2         # makes y'=0 at x=0 and x=±k
    c = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])

    y_0 = c                                   # y at x=0
    y_k = a * k**4 + b * k**2 + c            # y at x=±k

    func_str = format_poly([a, b, c], ["x^4", "x^2", ""])
    # a > 0 → x=0 is local max (CĐ); a < 0 → x=0 is local min (CT)
    is_single_cd = (a > 0)

    return func_str, "0", str(y_0), str(y_k), str(k), str(-k), is_single_cd


def generate_rational_func() -> Tuple[str, str, str, str, str]:
    """
    Generate y = (Ax²+bx+c)/(x−x0).
    Returns (func_str, x_CT, y_CT, x_CD, y_CD) as strings.
    """
    while True:
        A  = random.choice([-1, 1])
        x0 = random.choice([-3, -2, -1, 1, 2, 3])
        k  = random.choice([1, 2])
        m  = random.choice([-4, -3, -2, -1, 0, 1, 2, 3, 4])

        b = m - 2 * A * x0
        c = A * k**2 - m * x0 + A * x0**2
        e = -x0      # denominator: x + e = x - x0

        # Critical points at x = x0 ± k
        if A > 0:
            x_CT, y_CT = x0 + k, m + 2 * A * k
            x_CD, y_CD = x0 - k, m - 2 * A * k
        else:
            x_CD, y_CD = x0 + k, m + 2 * A * k
            x_CT, y_CT = x0 - k, m - 2 * A * k

        if x_CT != 0 and x_CD != 0 and y_CT != 0 and y_CD != 0:
            break

    func_str = format_rational(A, b, c, 1, e)
    return func_str, str(x_CT), str(y_CT), str(x_CD), str(y_CD)


# ─────────────────────────────────────────────────────────────────────────────
# Question generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_question(option_index: int) -> Tuple[str, str, str]:
    """
    Build one multiple-choice question.
      option_index 0 → cubic
      option_index 1 → quartic
      option_index 2 → rational
    Returns (stem, options_text, correct_letter).
    """

    # ── 1. Generate the function ──────────────────────────────────────────
    if option_index == 0:
        func_str, x_CT, y_CT, x_CD, y_CD = generate_cubic()
        is_quartic = False
    elif option_index == 1:
        func_str, x_single, y_single, y_sym, k_pos, k_neg, is_single_cd = generate_quartic()
        is_quartic = True
    else:
        func_str, x_CT, y_CT, x_CD, y_CD = generate_rational_func()
        is_quartic = False

    # ── 2a. Quartic: only ask about the unique extremum at x = 0 ─────────
    if is_quartic:
        extremum_type = "cd" if is_single_cd else "ct"

        quartic_pool = {
            "cd": [
                ("cd_tai",  "Hàm số đạt cực đại tại:"),
                ("gt_cd",   "Giá trị cực đại của hàm số là:"),
                ("cd_la",   "Cực đại của hàm số là:"),
                ("diem_cd", "Điểm cực đại của đồ thị hàm số là:"),
            ],
            "ct": [
                ("ct_tai",  "Hàm số đạt cực tiểu tại:"),
                ("gt_ct",   "Giá trị cực tiểu của hàm số là:"),
                ("ct_la",   "Cực tiểu của hàm số là:"),
                ("diem_ct", "Điểm cực tiểu của đồ thị hàm số là:"),
            ],
        }
        q_type, q_text = random.choice(quartic_pool[extremum_type])

        if q_type in ["cd_tai", "ct_tai"]:
            correct_option = r"\(x = 0\)"
            distractors = [
                rf"\(x = {k_pos}\)",
                rf"\(x = {k_neg}\)",
                rf"\(y = {y_single}\)",
            ]
        elif q_type in ["gt_cd", "gt_ct", "cd_la", "ct_la"]:
            correct_option = rf"\(y = {y_single}\)"
            distractors = [
                rf"\(y = {y_sym}\)",
                r"\(x = 0\)",
                rf"\(x = {k_pos}\)",
            ]
        else:  # diem_cd / diem_ct
            correct_option = rf"\(\left(0; {y_single}\right)\)"
            distractors = [
                rf"\(\left({k_pos}; {y_sym}\right)\)",
                rf"\(\left({k_neg}; {y_sym}\right)\)",
                rf"\(\left({y_single}; 0\right)\)",
            ]

    # ── 2b. Cubic / Rational: ask about either extremum ───────────────────
    else:
        pool = [
            ("ct_tai",  "Hàm số đạt cực tiểu tại:"),
            ("gt_ct",   "Giá trị cực tiểu của hàm số là:"),
            ("ct_la",   "Cực tiểu của hàm số là:"),
            ("diem_ct", "Điểm cực tiểu của đồ thị hàm số là:"),
            ("cd_tai",  "Hàm số đạt cực đại tại:"),
            ("gt_cd",   "Giá trị cực đại của hàm số là:"),
            ("cd_la",   "Cực đại của hàm số là:"),
            ("diem_cd", "Điểm cực đại của đồ thị hàm số là:"),
        ]
        q_type, q_text = random.choice(pool)

        if q_type == "ct_tai":
            correct_option = rf"\(x = {x_CT}\)"
            distractors = [rf"\(x = {x_CD}\)", rf"\(y = {y_CT}\)", rf"\(y = {y_CD}\)"]
        elif q_type == "cd_tai":
            correct_option = rf"\(x = {x_CD}\)"
            distractors = [rf"\(x = {x_CT}\)", rf"\(y = {y_CD}\)", rf"\(y = {y_CT}\)"]
        elif q_type in ["gt_ct", "ct_la"]:
            correct_option = rf"\(y = {y_CT}\)"
            distractors = [rf"\(y = {y_CD}\)", rf"\(x = {x_CT}\)", rf"\(x = {x_CD}\)"]
        elif q_type in ["gt_cd", "cd_la"]:
            correct_option = rf"\(y = {y_CD}\)"
            distractors = [rf"\(y = {y_CT}\)", rf"\(x = {x_CD}\)", rf"\(x = {x_CT}\)"]
        elif q_type == "diem_ct":
            correct_option = rf"\(\left({x_CT}; {y_CT}\right)\)"
            distractors = [
                rf"\(\left({x_CD}; {y_CD}\right)\)",
                rf"\(\left({y_CT}; {x_CT}\right)\)",
                rf"\(\left({y_CD}; {x_CD}\right)\)",
            ]
        else:  # diem_cd
            correct_option = rf"\(\left({x_CD}; {y_CD}\right)\)"
            distractors = [
                rf"\(\left({x_CT}; {y_CT}\right)\)",
                rf"\(\left({y_CD}; {x_CD}\right)\)",
                rf"\(\left({y_CT}; {x_CT}\right)\)",
            ]

    stem = rf"Cho hàm số \(y = {func_str}\). {q_text}"

    # ── 3. Deduplicate, fill dummies, shuffle ─────────────────────────────
    unique_distractors: List[str] = []
    for d in distractors:
        if d != correct_option and d not in unique_distractors:
            unique_distractors.append(d)

    dummy_count = 1
    while len(unique_distractors) < 3:
        if q_type in ["diem_ct", "diem_cd"]:
            dummy = rf"\(\left({99 + dummy_count}; {-99 - dummy_count}\right)\)"
        elif q_type in ["gt_ct", "ct_la", "gt_cd", "cd_la"]:
            dummy = rf"\(y = {99 + dummy_count}\)"
        else:
            dummy = rf"\(x = {99 + dummy_count}\)"
        if dummy not in unique_distractors and dummy != correct_option:
            unique_distractors.append(dummy)
        dummy_count += 1

    choices = [(correct_option, True)] + [(d, False) for d in unique_distractors[:3]]
    random.shuffle(choices)

    options_text = "\\choice\n"
    correct_letter = "A"
    for idx, (text, is_correct) in enumerate(choices):
        letter = chr(65 + idx)
        if is_correct:
            correct_letter = letter
            options_text += rf"{{\True {text}}}" + "\n"
        else:
            options_text += rf"{{{text}}}" + "\n"

    return stem, options_text, correct_letter


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    """
    Cách dùng:
        python3 nhan_biet_cuc_tri.py <số_câu> [option]

    option:
        1 → hàm bậc ba  y = ax³ + bx² + cx + d (mặc định)
        2 → hàm bậc bốn y = ax⁴ + bx² + c
        3 → hàm phân thức y = (ax²+bx+c)/(dx+e)

    Ví dụ:
        python3 nhan_biet_cuc_tri.py 10 1   # 10 câu bậc ba
        python3 nhan_biet_cuc_tri.py 5 2    # 5 câu bậc bốn
        python3 nhan_biet_cuc_tri.py 8 3    # 8 câu phân thức
        python3 nhan_biet_cuc_tri.py 10     # 10 câu bậc ba (mặc định option 1)
    """
    OPTION_NAMES = {
        1: ("bậc ba",    "bac_3"),
        2: ("bậc bốn",   "bac_4"),
        3: ("phân thức", "phan_thuc"),
    }

    if len(sys.argv) < 2:
        print("Lỗi: cần chỉ định số câu (num_questions).")
        print(__doc__ or main.__doc__)
        sys.exit(1)

    try:
        num_questions = int(sys.argv[1])
        if num_questions <= 0:
            raise ValueError
    except ValueError:
        print("Lỗi: số câu phải là một số nguyên dương.")
        sys.exit(1)

    option = 1
    if len(sys.argv) > 2:
        try:
            option = int(sys.argv[2])
        except ValueError:
            print("Lỗi: option phải là số nguyên (1, 2 hoặc 3).")
            sys.exit(1)

    if option not in OPTION_NAMES:
        print(f"Lỗi: option phải là 1, 2 hoặc 3 (nhận được: {option}).")
        sys.exit(1)

    option_index = option - 1   # 0-based index used by generate_question()
    label, suffix = OPTION_NAMES[option]

    content = ""
    answers = []

    for _ in range(num_questions):
        q, opts, ans = generate_question(option_index)
        answers.append(ans)
        content += rf"""\begin{{ex}}
{q}
{opts}\loigiai{{
}}
\end{{ex}}

"""

    template = r"""\documentclass[12pt,a4paper]{article}
\usepackage{amsmath,amssymb}
\usepackage{polyglossia}
\setdefaultlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}
\usepackage[solcolor]{ex_test}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, f"nhan_biet_cuc_tri_{suffix}_questions.tex")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"[Option {option} – hàm {label}] Đã tạo {num_questions} câu → {out_path}")
    print("Đáp án đúng:")
    for idx, ans in enumerate(answers):
        print(f"  Câu {idx+1}: {ans}")


if __name__ == "__main__":
    main()
