"""
Ví dụ 12: Tiệm cận xiên chứa tham số m (Trắc nghiệm 1 đáp án)
---------------------------------------------------------------
Biết tiệm cận xiên của đồ thị hàm số
    y = (num_ax^2 + num_bx + num_c) / (x + den_d)
đi qua điểm A(x_A; y_A). Giá trị của tham số m bằng?

Tham số m xuất hiện ở một trong ba vị trí (ngẫu nhiên):
  - Hệ số x^2 ở tử: A = c_a*m + k_a
  - Hệ số x  ở tử: B = c_b*m + k_b
  - Hằng số   ở mẫu: D = c_d*m + k_d

Tiệm cận xiên: y = A * x + (B - A*D)  (chia đa thức bậc 2 cho (x+D))
Điều kiện: A(x_A; y_A) nằm trên TCX → y_A = A*x_A + (B - A*D)
"""

import math
import os
import random
import sys
from fractions import Fraction
from typing import Tuple

# ---------------------------------------------------------------------------
# Parameter sets: (a, b, c, d, c_coeff, k_coeff, pos, x_A)
#   a, b, c  : hệ số tử số khi m = m_true (A, B, C hằng số)
#   d        : hằng số mẫu khi m = m_true
#   c_coeff  : hệ số của m trong biểu thức chứa m
#   pos      : vị trí m — 'A' (hệ số x^2), 'B' (hệ số x), 'D' (hằng số mẫu)
#   x_A      : hoành độ điểm đã cho
#   m_true   : giá trị m đúng
# Constraint: a != 0, x_A != -d, (a,b,c,d) cho TCX "đẹp"
# ---------------------------------------------------------------------------
PARAM_SETS = [
    # (a, b, c, d, c_coeff, pos, x_A, m_true)
    (1,  2, -3,  1, 1, 'A',  2,  1),
    (2,  3, -5, -1, 1, 'A',  3,  2),
    (1, -4,  2,  2, 2, 'A',  1, -1),
    (3,  1, -2, -2, 1, 'A',  2,  3),
    (2, -1,  4,  1, 2, 'A', -1, -2),
    (-1, 3,  1,  2, 1, 'A',  1, -1),
    (1,  5, -2,  3, 2, 'A',  0,  1),
    (2,  0,  3, -1, 1, 'A',  2,  2),
    (3, -2,  1,  2, 2, 'A', -1,  3),
    (1,  4,  0, -3, 1, 'A',  1,  1),
    (-2, 1,  3,  1, 1, 'A',  2, -2),
    (1, -3,  5,  2, 2, 'A', -1,  1),
    (2,  2, -4, -2, 1, 'A',  3,  2),
    (1,  1,  2,  1, 1, 'A',  2,  1),
    (3,  0, -3,  3, 1, 'A',  1,  3),
    (1,  2, -3,  1, 1, 'B',  2,  2),
    (2,  5,  1, -1, 1, 'B',  3,  5),
    (1, -2,  4,  2, 2, 'B',  1, -2),
    (2,  3, -1, -2, 1, 'B',  2,  3),
    (3,  1,  2,  1, 2, 'B', -1,  1),
    (-1, 4, -3,  2, 1, 'B',  1,  4),
    (1,  0,  5,  3, 1, 'B',  0,  0),
    (2, -4,  1, -1, 2, 'B',  2, -4),
    (1,  6, -2,  2, 1, 'B', -1,  6),
    (3, -1,  0,  1, 1, 'B',  2, -1),
    (-2, 2,  3, -1, 2, 'B',  1,  2),
    (1,  3,  1,  2, 1, 'B',  3,  3),
    (2, -3,  4, -2, 1, 'B',  1, -3),
    (1,  1, -5,  1, 2, 'B', -1,  1),
    (3,  2,  2,  2, 1, 'B',  2,  2),
    (1,  2,  3,  2, 1, 'D',  1,  2),
    (2,  3, -1,  0, 1, 'D',  2,  0),
    (1, -1,  2, -3, 2, 'D',  1, -3),
    (2,  1,  4,  1, 1, 'D',  3,  1),
    (3,  2, -2,  2, 2, 'D', -1,  2),
    (-1, 3,  1,  1, 1, 'D',  2,  1),
    (1,  4, -3, -2, 1, 'D',  1, -2),
    (2, -2,  1,  3, 1, 'D',  2,  3),
    (1,  1,  0, -1, 2, 'D',  0, -1),
    (3, -3,  5,  2, 1, 'D',  1,  2),
    (2,  0, -4,  1, 2, 'D',  2,  1),
    (1,  2,  2, -3, 1, 'D', -1, -3),
    (-2, 1, -1,  2, 2, 'D',  1,  2),
    (1,  3,  4,  0, 1, 'D',  2,  0),
    (2,  1,  3, -2, 1, 'D',  3, -2),
    (1, -4,  2,  3, 2, 'D', -1,  3),
    (3,  2,  1, -1, 1, 'D',  2, -1),
    (2,  5, -3,  2, 1, 'D',  1,  2),
    (1,  0,  5,  1, 2, 'D',  2,  1),
    (3, -1, -2, -3, 1, 'D',  1, -3),
    (1,  2, -1,  2, 2, 'A', -1, -2),
    (2,  3,  0,  1, 1, 'B',  1,  3),
    (1, -5,  3, -2, 2, 'A',  2, -5),
    (3,  4, -1,  1, 1, 'D',  2,  1),
    (2, -3,  2,  3, 2, 'B',  1, -3),
    (1,  1, -4, -1, 1, 'A',  3,  1),
    (4,  2,  1,  2, 1, 'D',  1,  2),
    (2,  1, -2, -1, 2, 'A',  2,  2),
    (1,  3,  3,  3, 1, 'B',  1,  3),
    (3, -2,  5,  2, 2, 'D', -1,  2),
]


def frac_str(f):
    """Format Fraction as LaTeX (no sign in denominator)."""
    f = Fraction(f).limit_denominator(10000)
    if f.denominator == 1:
        return str(f.numerator)
    sign = "-" if f < 0 else ""
    return rf"{sign}\dfrac{{{abs(f.numerator)}}}{{{f.denominator}}}"


def coeff_tex(val, var, first=False):
    """Format coefficient * variable as LaTeX term with sign."""
    if val == 0:
        return ""
    if not first:
        sign = "+" if val > 0 else "-"
        abs_val = abs(val)
    else:
        sign = "" if val > 0 else "-"
        abs_val = abs(val)
    if abs_val == 1:
        num_str = ""
    else:
        num_str = str(abs_val)
    if first:
        return f"{sign}{num_str}{var}"
    return f" {sign} {num_str}{var}".replace("  ", " ")


def poly_tex(a, b, c):
    """Format ax^2 + bx + c as LaTeX string."""
    parts = []
    # x^2 term
    if a != 0:
        if a == 1:
            parts.append("x^2")
        elif a == -1:
            parts.append("-x^2")
        else:
            parts.append(f"{a}x^2")
    # x term
    if b != 0:
        if not parts:
            if b == 1: parts.append("x")
            elif b == -1: parts.append("-x")
            else: parts.append(f"{b}x")
        else:
            if b > 0:
                parts.append(f"+ {b}x" if b != 1 else "+ x")
            else:
                parts.append(f"- {abs(b)}x" if b != -1 else "- x")
    # constant
    if c != 0:
        if not parts:
            parts.append(str(c))
        else:
            parts.append(f"+ {c}" if c > 0 else f"- {abs(c)}")
    return " ".join(parts) if parts else "0"


def build_poly_m_tex(c_a, k_a, c_b, k_b, c_c, k_c):
    def m_expr_str(c, k):
        if c == 0:
            return str(k)
        if k == 0:
            return f"{c}m" if c not in (1, -1) else ("m" if c == 1 else "-m")
        if c == 1:
            return f"m + {k}" if k > 0 else f"m - {abs(k)}"
        if c == -1:
            return f"-m + {k}" if k > 0 else f"-m - {abs(k)}"
        return f"{c}m + {k}" if k > 0 else f"{c}m - {abs(k)}"

    def needs_parens(expr_str):
        if '+' in expr_str: return True
        if '-' in expr_str[1:]: return True
        return False

    parts = []
    # A term
    expr_a = m_expr_str(c_a, k_a)
    if expr_a != "0":
        if needs_parens(expr_a):
            parts.append(f"({expr_a})x^2")
        else:
            if expr_a == "1": parts.append("x^2")
            elif expr_a == "-1": parts.append("-x^2")
            else: parts.append(f"{expr_a}x^2")
            
    # B term
    expr_b = m_expr_str(c_b, k_b)
    if expr_b != "0":
        if not parts:
            if needs_parens(expr_b):
                parts.append(f"({expr_b})x")
            else:
                if expr_b == "1": parts.append("x")
                elif expr_b == "-1": parts.append("-x")
                else: parts.append(f"{expr_b}x")
        else:
            if needs_parens(expr_b):
                parts.append(f"+ ({expr_b})x")
            else:
                if expr_b.startswith('-'):
                    if expr_b == "-1": parts.append("- x")
                    else: parts.append(f"- {expr_b[1:]}x")
                else:
                    if expr_b == "1": parts.append("+ x")
                    else: parts.append(f"+ {expr_b}x")
                    
    # C term
    expr_c = m_expr_str(c_c, k_c)
    if expr_c != "0":
        if not parts:
            if needs_parens(expr_c):
                parts.append(f"({expr_c})")
            else:
                parts.append(expr_c)
        else:
            if needs_parens(expr_c):
                parts.append(f"+ ({expr_c})")
            else:
                if expr_c.startswith('-'):
                    parts.append(f"- {expr_c[1:]}")
                else:
                    parts.append(f"+ {expr_c}")
                    
    if not parts:
        return "0"
    return " ".join(parts)


def build_den_m_tex(c_d, k_d):
    def m_expr_str(c, k):
        if c == 0:
            return str(k)
        if k == 0:
            return f"{c}m" if c not in (1, -1) else ("m" if c == 1 else "-m")
        if c == 1:
            return f"m + {k}" if k > 0 else f"m - {abs(k)}"
        if c == -1:
            return f"-m + {k}" if k > 0 else f"-m - {abs(k)}"
        return f"{c}m + {k}" if k > 0 else f"{c}m - {abs(k)}"

    expr_d = m_expr_str(c_d, k_d)
    if expr_d == "0":
        return "x"
    if expr_d.startswith('-'):
        return f"x - {expr_d[1:]}"
    return f"x + {expr_d}"


def generate_question(seed=None) -> Tuple[str, str, str]:
    if seed is not None:
        random.seed(seed)

    a, b, c, d, c_coeff, pos, x_A, m_true = random.choice(PARAM_SETS)

    attempts_coeffs = 0
    while True:
        attempts_coeffs += 1
        c_a = random.choice([0, 1, 2, -1, -2])
        c_b = random.choice([0, 1, 2, -1, -2])
        c_c = random.choice([0, 1, 2, -1, -2])
        c_d = random.choice([0, 1, 2, -1, -2])
        
        non_zeros = sum(1 for x in [c_a, c_b, c_c, c_d] if x != 0)
        if non_zeros < 2:
            continue
            
        if c_a * c_d != 0:
            continue # avoid quadratic in m
            
        # coefficient of m in y_A = A(m)x_A + B(m) - A(m)D(m)
        m_coeff = c_a * x_A + c_b - a * c_d - d * c_a
        if m_coeff == 0:
            continue
            
        break

    k_a = a - c_a * m_true
    k_b = b - c_b * m_true
    k_c = c - c_c * m_true
    k_d = d - c_d * m_true

    # Oblique asymptote: y = a*x + (b - a*d)
    slope = a
    intercept = b - a * d
    y_A = slope * x_A + intercept

    # Build LaTeX for function
    num_tex = build_poly_m_tex(c_a, k_a, c_b, k_b, c_c, k_c)
    den_tex = build_den_m_tex(c_d, k_d)
    func_tex = rf"y = \dfrac{{{num_tex}}}{{{den_tex}}}"

    # Build 4 answer options (A, B, C, D)
    options = [m_true]
    attempts = 0
    while len(options) < 4 and attempts < 200:
        attempts += 1
        delta = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        cand = m_true + delta
        if cand not in options:
            options.append(cand)
    random.shuffle(options)

    labels = ['A', 'B', 'C', 'D']
    correct_idx = options.index(m_true)
    correct_label = labels[correct_idx]

    opts_str = "\n".join(
        [rf"{'*' if i == correct_idx else ''}{labels[i]}. $m = {options[i]}$." for i in range(4)]
    )

    stem = (
        rf"Biết tiệm cận xiên của đồ thị hàm số ${func_tex}$ đi qua điểm "
        rf"$A({x_A};\ {y_A})$. Giá trị của tham số $m$ bằng:"
    )

    question = f"{stem}\n\n{opts_str}"
    solution = correct_label
    key = correct_label

    return question, solution, key


def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])

    seed_val = None
    if len(sys.argv) > 2:
        seed_val = int(sys.argv[2])

    out_dir = os.path.dirname(os.path.abspath(__file__))
    content = ""
    keys = []

    for i in range(num_questions):
        seed = (seed_val + i) if seed_val is not None else None
        q, s, k = generate_question(seed=seed)
        keys.append(k)
        content += rf"Câu {i+1}: {q}" + "\n\n"

    template = r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath, amsfonts, amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=2cm}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)
    output_file = os.path.join(out_dir, "vi_du_12_questions.tex")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")


if __name__ == "__main__":
    main()
