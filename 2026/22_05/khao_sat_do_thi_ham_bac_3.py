import math
import os
import sys
import random
from fractions import Fraction
from typing import Tuple

def format_equation(coeffs, terms):
    """Format polynomial equation from coeffs and terms."""
    res = ""
    for c, t in zip(coeffs, terms):
        if c == 0:
            continue
        if c == 1 and t != "":
            res += f" + {t}"
        elif c == -1 and t != "":
            res += f" - {t}"
        elif c > 0:
            res += f" + {c}{t}"
        else:
            res += f" - {abs(c)}{t}"
    
    if res.startswith(" + "):
        res = res[3:]
    elif res.startswith(" - "):
        res = "-" + res[3:]
    if res == "":
        return "0"
    return res

def fmt_x_minus_a(a):
    if a < 0:
        return f"x + {abs(a)}"
    elif a > 0:
        return f"x - {a}"
    return "x"

def fmt_frac(num, den):
    if num % den == 0:
        return str(num // den)
    if den < 0:
        num, den = -num, -den
    if num < 0:
        return rf"-\frac{{{abs(num)}}}{{{den}}}"
    return rf"\frac{{{num}}}{{{den}}}"

def sqrt_tex(n):
    if n < 0: return ""
    root = int(math.sqrt(n))
    if root * root == n:
        return str(root)
    return rf"\sqrt{{{n}}}"

def generate_question() -> Tuple[str, str, str]:
    # ---------------------------------------------------------
    # Mệnh đề a
    # ---------------------------------------------------------
    # y = x^3 - 3x_1^2 x + 2x_1^3
    a_params = [
        (1, 1, 4, 13),
        (-1, 1, -4, 14),
        (2, 1, 1, 26),
        (-2, 1, -1, 28),
        (3, 2, 8, 726),
        (-3, 2, -8, 732)
    ]
    x1, m_a, n_a, T_true = random.choice(a_params)
    c_a = -3 * x1**2
    d_a = 2 * x1**3
    func_a = format_equation([1, c_a, d_a], ["x^3", "x", ""])
    
    a_correct = random.choice([True, False])
    T_val = T_true if a_correct else T_true + random.choice([-2, 2, -1, 1, 3, -3])
    
    sign_n_a = "+" if n_a > 0 else "-"
    abs_n_a = abs(n_a)
    T_expr = f"{m_a if m_a != 1 else ''}a {sign_n_a} {abs_n_a if abs_n_a != 1 else ''}b"
    if m_a == 1:
        T_expr = f"a {sign_n_a} {abs_n_a if abs_n_a != 1 else ''}b"
    
    stmt_a = rf"Cho hàm số $y = {func_a}$ có đồ thị $(C)$ cắt trục hoành tại hai điểm $A$ và $B$. Tồn tại duy nhất một điểm $M(a;b) \in (C)$ sao cho tam giác $MAB$ cân tại $M$, khi đó giá trị biểu thức $T = {T_expr}$ bằng ${T_val}$."

    sol_a_correct_str = "Đúng" if a_correct else "Sai"
    sol_a = rf"""a) {sol_a_correct_str}.

Phương trình hoành độ giao điểm của đồ thị $(C)$ và trục hoành là: 
${func_a} = 0 \Leftrightarrow ({fmt_x_minus_a(x1)})^2({fmt_x_minus_a(-2*x1)}) = 0$.
Suy ra đồ thị $(C)$ cắt trục hoành tại hai điểm phân biệt $A({x1}; 0)$ và $B({-2*x1}; 0)$.
Gọi $I$ là trung điểm của đoạn thẳng $AB$, ta có tọa độ $I$ là $x_I = \frac{{{x1} + ({-2*x1})}}{{2}} = {fmt_frac(-x1, 2)}$ và $y_I = 0$. Suy ra $I({fmt_frac(-x1, 2)}; 0)$.
Để tam giác $MAB$ cân tại đỉnh $M$, điểm $M$ phải nằm trên đường trung trực của đoạn thẳng $AB$.
Do $AB$ nằm trên trục hoành, đường trung trực của $AB$ là đường thẳng đi qua $I$ và vuông góc với trục hoành, có phương trình $x = {fmt_frac(-x1, 2)}$.
Do đó, hoành độ của điểm $M$ là $a = x_M = {fmt_frac(-x1, 2)}$.
Vì điểm $M(a; b)$ nằm trên đồ thị $(C)$, thay $x = {fmt_frac(-x1, 2)}$ vào phương trình đồ thị ta được tung độ:
$b = y_M = {fmt_frac(27*(x1**3), 8)}$.
Suy ra, có duy nhất một điểm $M$ thỏa mãn yêu cầu bài toán.
Tính biểu thức $T = {T_expr}$ với $a = {fmt_frac(-x1, 2)}$ và $b = {fmt_frac(27*(x1**3), 8)}$, ta thu được $T = {T_true}$.
Vậy mệnh đề này là {sol_a_correct_str.lower()}."""

    # ---------------------------------------------------------
    # Mệnh đề b
    # ---------------------------------------------------------
    # y = a_2 x^3 + b_2 x + c_2
    b_params = [
        (1, 1, 1, 1, 2),
        (-1, -1, 2, 1, 2),
        (1, 2, -1, 1, 10),
        (-1, -2, 3, 1, 10),
        (1, 3, 1, 1, 17),
        (-1, -3, 3, 1, 17),
        (1, 1, 2, 2, 20),
        (-1, -1, -2, 2, 20)
    ]
    a2, b2, c2, t0, d2 = random.choice(b_params)
    func_b = format_equation([a2, b2, c2], ["x^3", "x", ""])
    
    b_correct = random.choice([True, False])
    k_val = 2 if b_correct else random.choice([3, 4])
    
    stmt_b = rf"Có đúng {k_val} điểm thuộc đồ thị hàm số $y = {func_b}$ cách giao điểm của đồ thị với trục tung một khoảng bằng ${sqrt_tex(d2)}$."

    sol_b_correct_str = "Đúng" if b_correct else "Sai"
    sol_b = rf"""b) {sol_b_correct_str}.

Giao điểm của đồ thị với trục tung là $M(0; {c2})$.
Gọi $N(x; {func_b})$ là điểm thuộc đồ thị.
Khoảng cách $MN = \sqrt{{x^2 + ({format_equation([a2, b2], ["x^3", "x"])})^2}} = \sqrt{{x^2(1 + ({format_equation([a2, b2], ["x^2", ""])})^2)}}$.
Theo giả thiết $MN = {sqrt_tex(d2)} \Leftrightarrow x^2(1 + ({format_equation([a2, b2], ["x^2", ""])})^2) = {d2}$.
Đặt $t = x^2 \ge 0$, ta có phương trình $t(1 + ({format_equation([a2, b2], ["t", ""])})^2) = {d2}$.
Xét hàm số $g(t) = t(1 + ({format_equation([a2, b2], ["t", ""])})^2) = {format_equation([a2**2, 2*a2*b2, b2**2 + 1], ["t^3", "t^2", "t"])}$.
$g'(t) = {format_equation([3*a2**2, 4*a2*b2, b2**2 + 1], ["t^2", "t", ""])}$.
Vì $t \ge 0$ và các hệ số của $g'(t)$ đều dương nên $g'(t) > 0 \forall t \ge 0$, suy ra hàm số $g(t)$ đồng biến trên $[0; +\infty)$.
Mặt khác $g({t0}) = {d2}$ nên phương trình có nghiệm duy nhất $t = {t0}$.
Với $t = {t0} \Rightarrow x^2 = {t0} \Rightarrow x = \pm {sqrt_tex(t0)}$.
Vậy có đúng 2 điểm thỏa mãn. Mệnh đề này là {sol_b_correct_str.lower()}."""

    # ---------------------------------------------------------
    # Mệnh đề c
    # ---------------------------------------------------------
    # y = x^3 + b_3 x^2 + c_3 x + d_3
    r1 = random.choice([-2, -1, 0, 1, 2])
    r2 = random.choice([x for x in [-2, -1, 0, 1, 2, 3] if x != r1])
    m3 = random.choice([-2, -1, 1, 2, 3])
    n3 = random.choice([-3, -2, -1, 0, 1, 2, 3])
    xI = random.choice([-1, 0, 1, 2])
    yI = random.choice([-2, -1, 0, 1, 2])
    
    b3 = -(2*r1 + r2)
    c3 = r1**2 + 2*r1*r2 + m3
    d3 = -(r1**2 * r2) - 2*m3*xI - n3 + 2*yI
    
    func_c = format_equation([1, b3, c3, d3], ["x^3", "x^2", "x", ""])
    line_c = format_equation([m3, n3], ["x", ""])
    
    c_correct = random.choice([True, False])
    k_c = 2 if c_correct else random.choice([1, 3])
    
    stmt_c = rf"Cho hàm số $y = {func_c}$ có đồ thị $(C)$, điểm $I({xI}; {yI})$ và đường thẳng $\Delta : y = {line_c}$. Có đúng {k_c} cặp điểm $A, B$ thỏa mãn $A \in (C), B \in \Delta$ và chúng đối xứng nhau qua $I$."

    xI_expr = f"-x" if xI == 0 else f"{2*xI} - x"
    
    sol_c_correct_str = "Đúng" if c_correct else "Sai"
    sol_c = rf"""c) {sol_c_correct_str}.

Gọi $A(x; {func_c}) \in (C)$.
Vì $A, B$ đối xứng nhau qua $I({xI}; {yI})$ nên $B({xI_expr}; {2*yI} - ({func_c}))$.
Vì $B \in \Delta$ nên tọa độ điểm $B$ thỏa mãn phương trình $\Delta$:
${2*yI} - ({func_c}) = {format_equation([m3, n3], [f"({xI_expr})", ""])}$
$\Leftrightarrow {format_equation([1, b3, c3-m3, d3+2*m3*xI+n3-2*yI], ["x^3", "x^2", "x", ""])} = 0$
$\Leftrightarrow ({fmt_x_minus_a(r1)})^2({fmt_x_minus_a(r2)}) = 0$.
Phương trình này có 2 nghiệm phân biệt $x = {r1}$ và $x = {r2}$.
Mỗi giá trị của $x$ cho ta 1 điểm $A$, tương ứng có 1 điểm $B$.
Vậy có đúng 2 cặp điểm $A, B$ thỏa mãn. Mệnh đề này là {sol_c_correct_str.lower()}."""

    # ---------------------------------------------------------
    # Mệnh đề d
    # ---------------------------------------------------------
    # y = x^3 - 3m x^2 + 4m^3
    m_sq = random.choice([2, 3, 4, 5, 6])
    S_val = 4 * (m_sq**2)
    
    d_correct = random.choice([True, False])
    V_val = m_sq if d_correct else random.choice([m_sq + 1, m_sq - 1, m_sq**2])
    
    stmt_d = rf"Biết đồ thị hàm số $y = x^3 - 3mx^2 + 4m^3$ (với $m > 0$) có hai điểm cực trị $A$ và $B$. Nếu tam giác $OAB$ có diện tích bằng ${S_val}$ thì $m^2 = {V_val}$."

    sol_d_correct_str = "Đúng" if d_correct else "Sai"
    sol_d = rf"""d) {sol_d_correct_str}.

Ta có $y' = 3x^2 - 6mx = 3x(x - 2m)$.
$y' = 0 \Leftrightarrow x = 0$ hoặc $x = 2m$.
Với $x = 0 \Rightarrow y = 4m^3 \Rightarrow A(0; 4m^3)$. Điểm $A$ nằm trên trục tung.
Với $x = 2m \Rightarrow y = 8m^3 - 12m^3 + 4m^3 = 0 \Rightarrow B(2m; 0)$. Điểm $B$ nằm trên trục hoành.
Tam giác $OAB$ vuông tại $O$, có diện tích $S = \frac{{1}}{{2}} OA \cdot OB = \frac{{1}}{{2}} |4m^3| \cdot |2m| = 4m^4$.
Theo giả thiết $S = {S_val} \Leftrightarrow 4m^4 = {S_val} \Leftrightarrow m^4 = {m_sq**2} \Leftrightarrow m^2 = {m_sq}$.
Vậy mệnh đề này là {sol_d_correct_str.lower()}."""

    # ---------------------------------------------------------
    # Tổng hợp
    # ---------------------------------------------------------
    stem = "Xét tính đúng, sai của các phát biểu sau:"
    
    stmt_a_full = rf"{'*' if a_correct else ''}a) {stmt_a}"
    stmt_b_full = rf"{'*' if b_correct else ''}b) {stmt_b}"
    stmt_c_full = rf"{'*' if c_correct else ''}c) {stmt_c}"
    stmt_d_full = rf"{'*' if d_correct else ''}d) {stmt_d}"

    key_arr = ["Đ" if x else "S" for x in (a_correct, b_correct, c_correct, d_correct)]
    key = ", ".join(key_arr)

    question = f"""{stem}

{stmt_a_full}

{stmt_b_full}

{stmt_c_full}

{stmt_d_full}"""

    solution = "\n\n".join([sol_a, sol_b, sol_c, sol_d])

    return question, solution, key

def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])

    content = ""
    keys = []
    
    for i in range(num_questions):
        q, s, k = generate_question()
        keys.append(k)
        content += f"Câu {i+1}: {q}\n\nLời giải:\n\n{s}\n\n"

    template = r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath, amsfonts, amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
% \setmainfont{Times New Roman}
\usepackage{tikz}
\usetikzlibrary{calc,angles,quotes}

\newcommand{\heva}[1]{\left\{\begin{aligned}#1\end{aligned}\right.}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)

    out_dir = os.path.dirname(os.path.abspath(__file__))
    script_base = os.path.splitext(os.path.basename(__file__))[0]
    output_file = os.path.join(out_dir, f"{script_base}_questions.tex")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")

if __name__ == "__main__":
    main()
