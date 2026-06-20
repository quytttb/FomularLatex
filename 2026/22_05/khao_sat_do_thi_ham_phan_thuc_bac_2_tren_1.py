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

def format_rational_func(a, b, c, d, e):
    num = format_equation([a, b, c], ["x^2", "x", ""])
    den = format_equation([d, e], ["x", ""])
    return rf"\frac{{{num}}}{{{den}}}"

def generate_stmt_a():
    # y = x + n + k/(x-x0) = (x^2 + (n-x0)x - nx0 + k) / (x-x0)
    # IM^2 = 2t + k^2/t + 2k = d^2 => 2t^2 + (2k-d^2)t + k^2 = 0
    # We use pre-calculated (k, d^2, t1, t2)
    params = [
        (2, 10, 1, 2),
        (4, 20, 2, 4),
        (6, 34, 2, 9),
        (-2, 6, 1, 2),
        (-4, 12, 2, 4),
        (-6, 22, 2, 9)
    ]
    k, d2, t1, t2 = random.choice(params)
    x0 = random.choice([-2, -1, 1, 2])
    n = random.choice([-2, -1, 0, 1, 2])
    
    a = 1
    b = n - x0
    c = -n*x0 + k
    
    func_str = format_rational_func(a, b, c, 1, -x0)
    
    is_correct = random.choice([True, False])
    num_pts = 4 if is_correct else random.choice([2, 3])
    
    stmt = rf"Có đúng {num_pts} điểm thuộc đồ thị hàm số $y = {func_str}$ cách tâm đối xứng của đồ thị một khoảng bằng ${sqrt_tex(d2)}$."
    
    sol_correct_str = "Đúng" if is_correct else "Sai"
    
    # y = x + n + k/(x-x0)
    y_asymp = format_equation([1, n], ["x", ""])
    
    sol = rf"""+) {sol_correct_str}.

Ta có $y = {func_str} = {y_asymp} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}}$.
Đồ thị có tiệm cận đứng $x = {x0}$ và tiệm cận xiên $y = {y_asymp}$.
Tâm đối xứng của đồ thị là giao điểm của hai tiệm cận: $I({x0}; {x0+n})$.
Gọi $M(x; {y_asymp} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}})$ là điểm thuộc đồ thị ($x \neq {x0}$).
Khoảng cách $IM^2 = (x - {x0})^2 + ({y_asymp} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}} - ({x0+n}))^2 = (x - {x0})^2 + (x - {x0} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}})^2$
$= 2(x - {x0})^2 + \frac{{{k**2}}}{{(x - {x0})^2}} {f'+ {2*k}' if 2*k > 0 else f'- {abs(2*k)}'}$.
Theo giả thiết $IM = {sqrt_tex(d2)} \Leftrightarrow IM^2 = {d2} \Leftrightarrow 2(x - {x0})^2 + \frac{{{k**2}}}{{(x - {x0})^2}} {f'+ {2*k}' if 2*k > 0 else f'- {abs(2*k)}'} = {d2}$.
Đặt $t = (x - {x0})^2 > 0$, ta có phương trình: $2t + \frac{{{k**2}}}{{t}} {f'+ {2*k}' if 2*k > 0 else f'- {abs(2*k)}'} = {d2} \Leftrightarrow 2t^2 - {d2 - 2*k}t + {k**2} = 0$.
Phương trình này có 2 nghiệm phân biệt $t = {t1}$ và $t = {t2}$ (đều thỏa mãn $t > 0$).
Mỗi giá trị $t > 0$ cho 2 giá trị của $x$. Vậy có đúng 4 điểm thỏa mãn.
Mệnh đề này là {sol_correct_str.lower()}."""
    
    return stmt, sol, is_correct

def generate_stmt_b():
    # y = x + n + k/(x-x0)
    # S = |x-x0| + |k| / (sqrt(2)|x-x0|) = a*sqrt(2)
    k = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    a = random.choice([2, 3, 4])
    while a**2 <= math.sqrt(2) * abs(k):
        a += 1
        
    x0 = random.choice([-2, -1, 1, 2])
    n = random.choice([-2, -1, 0, 1, 2])
    
    a_c = 1
    b_c = n - x0
    c_c = -n*x0 + k
    
    func_str = format_rational_func(a_c, b_c, c_c, 1, -x0)
    
    is_correct = random.choice([True, False])
    num_pts = 4 if is_correct else random.choice([2, 3])
    
    stmt = rf"Có đúng {num_pts} điểm $M$ thuộc đồ thị $(C)$ của hàm số $y = {func_str}$ sao cho tổng khoảng cách từ điểm $M$ đến hai đường tiệm cận của $(C)$ bằng ${a}\sqrt{{2}}$."
    
    sol_correct_str = "Đúng" if is_correct else "Sai"
    
    y_asymp = format_equation([1, n], ["x", ""])
    
    sol = rf"""+) {sol_correct_str}.

Ta có $y = {func_str} = {y_asymp} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}}$.
Đồ thị có tiệm cận đứng $\Delta_1: x - {x0} = 0$ và tiệm cận xiên $\Delta_2: x - y {'+' if n > 0 else '-'} {abs(n) if n != 0 else '0'} = 0$.
Gọi $M(x_0; y_0) \in (C)$.
Khoảng cách từ $M$ đến $\Delta_1$ là $d_1 = |x_0 - {x0}|$.
Khoảng cách từ $M$ đến $\Delta_2$ là $d_2 = \frac{{|x_0 - y_0 {'+' if n > 0 else '-'} {abs(n) if n != 0 else '0'}|}}{{\sqrt{{1^2 + (-1)^2}}}} = \frac{{|x_0 - (x_0 {'+' if n > 0 else '-'} {abs(n)} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{x_0 - {x0}}}) {'+' if n > 0 else '-'} {abs(n) if n != 0 else '0'}|}}{{\sqrt{{2}}}} = \frac{{{abs(k)}}}{{\sqrt{{2}}|x_0 - {x0}|}}$.
Tổng khoảng cách $S = d_1 + d_2 = |x_0 - {x0}| + \frac{{{abs(k)}}}{{\sqrt{{2}}|x_0 - {x0}|}}$.
Theo giả thiết $S = {a}\sqrt{{2}} \Leftrightarrow |x_0 - {x0}| + \frac{{{abs(k)}}}{{\sqrt{{2}}|x_0 - {x0}|}} = {a}\sqrt{{2}}$.
Đặt $u = |x_0 - {x0}| > 0$, ta có: $u + \frac{{{abs(k)}}}{{\sqrt{{2}}u}} = {a}\sqrt{{2}} \Leftrightarrow \sqrt{{2}}u^2 - {2*a}u + {abs(k)} = 0$.
Phương trình bậc hai theo $u$ có $\Delta' = {a**2} - {abs(k)}\sqrt{{2}} > 0$ và $S = {a}\sqrt{{2}} > 0, P = \frac{{{abs(k)}}}{{\sqrt{{2}}}} > 0$.
Do đó phương trình có 2 nghiệm $u$ dương phân biệt.
Mỗi giá trị $u > 0$ cho 2 giá trị của $x_0$. Vậy có đúng 4 điểm $M$ thỏa mãn.
Mệnh đề này là {sol_correct_str.lower()}."""
    
    return stmt, sol, is_correct

def generate_stmt_c():
    # y = (x^2 + bx + c) / (x - x0)
    # Line through extrema: y = 2x + b
    # Area = b^2 / 4
    b = random.choice([-6, -4, -2, 2, 4, 6])
    c = random.choice([-5, -3, -1, 1, 3, 5])
    x0 = random.choice([-2, -1, 1, 2])
    
    func_str = format_rational_func(1, b, c, 1, -x0)
    
    area = (b**2) // 4
    
    is_correct = random.choice([True, False])
    area_val = area if is_correct else area + random.choice([-1, 1, 2])
    if area_val <= 0: area_val = area + 2
    
    stmt = rf"Đường thẳng đi qua hai điểm cực trị của đồ thị hàm số $y = {func_str}$ cắt hai trục tọa độ $Ox, Oy$ tạo thành một tam giác có diện tích bằng ${area_val}$."
    
    sol_correct_str = "Đúng" if is_correct else "Sai"
    
    sol = rf"""+) {sol_correct_str}.

Đường thẳng $\Delta$ đi qua hai điểm cực trị của đồ thị hàm số $y = \frac{{u(x)}}{{v(x)}}$ có phương trình $y = \frac{{u'(x)}}{{v'(x)}}$.
Ta có $u'(x) = 2x {'+' if b > 0 else '-'} {abs(b)}$ và $v'(x) = 1$.
Suy ra phương trình đường thẳng $\Delta$ là $y = 2x {'+' if b > 0 else '-'} {abs(b)}$.
Giao điểm của $\Delta$ với trục $Oy$ là $A(0; {b})$, suy ra $OA = {abs(b)}$.
Giao điểm của $\Delta$ với trục $Ox$ là $B({fmt_frac(-b, 2)}; 0)$, suy ra $OB = {abs(b)//2}$.
Diện tích tam giác vuông $OAB$ là $S = \frac{{1}}{{2}} OA \cdot OB = \frac{{1}}{{2}} \cdot {abs(b)} \cdot {abs(b)//2} = {area}$.
Mệnh đề này là {sol_correct_str.lower()}."""
    
    return stmt, sol, is_correct

def generate_stmt_d():
    # y = (ax^2 + bx + c) / (x - x0), d: y = mx + n
    # Intersection: (m-a)x^2 + (n-mx0-b)x - (nx0+c) = 0
    # A = m-a, B = n-mx0-b, C = -(nx0+c)
    # We want A != 0, Delta > 0
    while True:
        a = random.choice([-1, 1])
        m = random.choice([-2, -1, 1, 2])
        if a == m: continue
        x0 = random.choice([-2, -1, 1, 2])
        n = random.choice([-2, -1, 1, 2])
        b = random.choice([-3, -2, -1, 0, 1, 2, 3])
        c = random.choice([-3, -2, -1, 0, 1, 2, 3])
        
        A = m - a
        B = n - m*x0 - b
        C = -(n*x0 + c)
        
        delta = B**2 - 4*A*C
        if delta > 0 and delta % (A**2) == 0:
            # S = |n| * sqrt(delta) / (2|A|)
            num = abs(n) * int(math.sqrt(delta))
            den = 2 * abs(A)
            break
        elif delta > 0:
            # S = |n| * sqrt(delta) / (2|A|)
            break

    func_str = format_rational_func(a, b, c, 1, -x0)
    line_str = format_equation([m, n], ["x", ""])
    
    S_num = abs(n)
    S_den = 2 * abs(A)
    # Simplify S_num / S_den
    gcd = math.gcd(S_num, S_den)
    S_num //= gcd
    S_den //= gcd
    
    if S_num == 1 and S_den == 1:
        S_str = rf"\sqrt{{{delta}}}"
    elif S_den == 1:
        S_str = rf"{S_num}\sqrt{{{delta}}}"
    elif S_num == 1:
        S_str = rf"\frac{{\sqrt{{{delta}}}}}{{{S_den}}}"
    else:
        S_str = rf"\frac{{{S_num}\sqrt{{{delta}}}}}{{{S_den}}}"

    is_correct = random.choice([True, False])
    if is_correct:
        S_val = S_str
    else:
        fake_num = S_num + random.choice([1, 2])
        if fake_num == 1 and S_den == 1:
            S_val = rf"\sqrt{{{delta}}}"
        elif S_den == 1:
            S_val = rf"{fake_num}\sqrt{{{delta}}}"
        elif fake_num == 1:
            S_val = rf"\frac{{\sqrt{{{delta}}}}}{{{S_den}}}"
        else:
            S_val = rf"\frac{{{fake_num}\sqrt{{{delta}}}}}{{{S_den}}}"
            
    stmt = rf"Đường thẳng $d: y = {line_str}$ cắt đồ thị hàm số $y = {func_str}$ tại hai điểm phân biệt $A$ và $B$. Khi đó diện tích tam giác $OAB$ (với $O$ là gốc tọa độ) bằng ${S_val}$."
    
    sol_correct_str = "Đúng" if is_correct else "Sai"
    
    sol = rf"""+) {sol_correct_str}.

Phương trình hoành độ giao điểm: $\frac{{{format_equation([a, b, c], ['x^2', 'x', ''])}}}{{{fmt_x_minus_a(x0)}}} = {line_str}$
$\Rightarrow {format_equation([a, b, c], ['x^2', 'x', ''])} = ({line_str})({fmt_x_minus_a(x0)})$
$\Leftrightarrow {format_equation([A, B, C], ['x^2', 'x', ''])} = 0 \quad (1)$
Phương trình (1) có $\Delta = {B**2} - 4({A})({C}) = {delta} > 0$ và $x = {x0}$ không là nghiệm, nên $d$ luôn cắt đồ thị tại hai điểm phân biệt $A, B$.
Gọi $x_A, x_B$ là nghiệm của (1), ta có $|x_A - x_B| = \frac{{\sqrt{{\Delta}}}}{{|a|}} = \frac{{\sqrt{{{delta}}}}}{{{abs(A)}}}$.
Độ dài đoạn $AB = \sqrt{{1 + {m}^2}} |x_A - x_B| = \sqrt{{{1+m**2}}} \frac{{\sqrt{{{delta}}}}}{{{abs(A)}}}$.
Khoảng cách từ $O$ đến $d: {m}x - y {'+' if n > 0 else '-'} {abs(n)} = 0$ là $h = \frac{{|{n}|}}{{\sqrt{{{m}^2 + (-1)^2}}}} = \frac{{{abs(n)}}}{{\sqrt{{{1+m**2}}}}}$.
Diện tích tam giác $OAB$ là $S = \frac{{1}}{{2}} AB \cdot h = \frac{{1}}{{2}} \sqrt{{{1+m**2}}} \frac{{\sqrt{{{delta}}}}}{{{abs(A)}}} \frac{{{abs(n)}}}{{\sqrt{{{1+m**2}}}}} = \frac{{{abs(n)}\sqrt{{{delta}}}}}{{{2*abs(A)}}} = {S_str}$.
Mệnh đề này là {sol_correct_str.lower()}."""
    
    return stmt, sol, is_correct

def generate_stmt_e():
    # y = x + n + k/(x-x0)
    # Integer points = divisors of k
    k_vals = {
        1: 2, -1: 2,
        2: 4, -2: 4,
        3: 4, -3: 4,
        4: 6, -4: 6,
        5: 4, -5: 4,
        6: 8, -6: 8
    }
    k = random.choice(list(k_vals.keys()))
    num_pts = k_vals[k]
    
    x0 = random.choice([-2, -1, 1, 2])
    n = random.choice([-2, -1, 0, 1, 2])
    
    a = 1
    b = n - x0
    c = -n*x0 + k
    
    func_str = format_rational_func(a, b, c, 1, -x0)
    
    is_correct = random.choice([True, False])
    pts_val = num_pts if is_correct else num_pts + random.choice([-2, 2])
    if pts_val <= 0: pts_val = num_pts + 2
    
    stmt = rf"Cho hàm số $y = {func_str}$ có đồ thị $(C)$. Trên đồ thị $(C)$ có {pts_val} điểm mà cả hoành độ và tung độ đều là các số nguyên."
    
    sol_correct_str = "Đúng" if is_correct else "Sai"
    
    y_asymp = format_equation([1, n], ["x", ""])
    
    sol = rf"""+) {sol_correct_str}.

Ta có $y = {func_str} = {y_asymp} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}}$.
Để điểm thuộc đồ thị có tọa độ nguyên thì $x$ và $y$ đều phải là số nguyên.
Vì $x \in \mathbb{{Z}}$ nên ${y_asymp} \in \mathbb{{Z}}$. Do đó $y \in \mathbb{{Z}} \Leftrightarrow \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}} \in \mathbb{{Z}}$.
Suy ra $x - {x0}$ phải là ước của ${abs(k)}$.
Các ước của ${abs(k)}$ là: {', '.join(map(str, [i for i in range(-abs(k), abs(k)+1) if i != 0 and abs(k) % i == 0]))}.
Có tất cả {num_pts} ước, tương ứng với {num_pts} giá trị nguyên của $x$ (đều khác ${x0}$).
Vậy trên đồ thị có đúng {num_pts} điểm có tọa độ nguyên.
Mệnh đề này là {sol_correct_str.lower()}."""
    
    return stmt, sol, is_correct

def generate_question() -> Tuple[str, str, str]:
    generators = [generate_stmt_a, generate_stmt_b, generate_stmt_c, generate_stmt_d, generate_stmt_e]
    selected_gens = random.sample(generators, 4)
    
    stmts = []
    sols = []
    is_corrects = []
    
    labels = ['a', 'b', 'c', 'd']
    
    for i, gen in enumerate(selected_gens):
        stmt, sol, is_correct = gen()
        # Replace "+)" with "a)", "b)", etc.
        sol = sol.replace("+)", f"{labels[i]})", 1)
        
        stmts.append(rf"{'*' if is_correct else ''}{labels[i]}) {stmt}")
        sols.append(sol)
        is_corrects.append(is_correct)
        
    stem = "Xét tính đúng, sai của các phát biểu sau:"
    
    question = f"{stem}\n\n" + "\n\n".join(stmts)
    solution = "\n\n".join(sols)
    
    key_arr = ["Đ" if x else "S" for x in is_corrects]
    key = ", ".join(key_arr)
    
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
