import random
import os
import sys

def format_poly(a, b, c):
    terms = []
    if a == 1: terms.append("x^2")
    elif a == -1: terms.append("-x^2")
    elif a != 0: terms.append(f"{a}x^2")
    
    if b == 1: terms.append("+x" if terms else "x")
    elif b == -1: terms.append("-x")
    elif b > 0: terms.append(f"+{b}x" if terms else f"{b}x")
    elif b < 0: terms.append(f"{b}x")
    
    if c > 0: terms.append(f"+{c}" if terms else f"{c}")
    elif c < 0: terms.append(f"{c}")
    
    if not terms: return "0"
    return "".join(terms)

def generate_question(seed=None, force_sample=False):
    if seed is not None:
        random.seed(seed)
        
    # Generate parameters for y = (A x^2 + B x + C) e^{D x + E} + F
    # Derivative y' = [ D A x^2 + (2 A + D B) x + (B + D C) ] e^{D x + E}
    # Let y' = a_p (x - x1) (x - x2) e^{D x + E}
    
    if force_sample:
        D = 1
        E = 0
        F = 0
        a_p = 1
        x1 = -1
        x2 = 1
    else:
        D = random.choice([-2, -1, 1, 2])
        E = random.randint(-4, 4)
        F = random.randint(-5, 5)
        
        # y = (Ax^2 + Bx + C) e^{Dx+E} + F
        # y' = (DAx^2 + (2A+DB)x + (B+DC)) e^{Dx+E}
        # We want y' polynomial = a_p(x - x1)(x - x2) = a_p*x^2 - a_p(x1+x2)x + a_p*x1*x2
        # So: a_p = DA, B = (-a_p(x1+x2) - 2A)/D, C = (a_p*x1*x2 - B)/D
        # B is always integer (since 2A/D is integer for D in {-2,-1,1,2}).
        # C requires B % D == 0. B = -A(x1+x2) - 2A/D.
        # For |D|=2: B = -A(x1+x2) ∓ A = -A(x1+x2 ± 1).
        #   B % 2 == 0 iff A*(x1+x2 ± 1) is even, which holds when x1+x2 is odd.
        # For |D|=1: B % 1 == 0 always.
        
        A = random.choice([-2, -1, 1, 2])
        a_p = A * D
        
        x1 = random.randint(-4, 2)
        x2 = random.randint(x1 + 1, 4)
        
        # When |D|=2, ensure x1+x2 is odd so that C is an integer
        if abs(D) == 2 and (x1 + x2) % 2 == 0:
            # Shift x2 by 1 to make sum odd
            if x2 + 1 <= 4:
                x2 += 1
            elif x1 - 1 >= -4 and x1 - 1 < x2:
                x1 -= 1
            else:
                x2 -= 1
                if x1 >= x2:
                    x1 = x2 - 1
        
    # Exact divisions - no truncation allowed
    assert a_p % D == 0, f"a_p={a_p} not divisible by D={D}"
    A = a_p // D
    
    B_num = -a_p * (x1 + x2) - 2 * A
    assert B_num % D == 0, f"B numerator={B_num} not divisible by D={D}"
    B = B_num // D
    
    C_num = a_p * x1 * x2 - B
    assert C_num % D == 0, f"C numerator={C_num} not divisible by D={D} (B={B}, x1={x1}, x2={x2})"
    C = C_num // D
    
    # Verify: recalculate derivative coefficients and check they match intended roots
    A_p = D * A
    B_p = 2 * A + D * B
    C_p = B + D * C
    
    # Verify the derivative polynomial has the correct roots
    assert A_p == a_p, f"A_p mismatch: {A_p} != {a_p}"
    assert B_p == -a_p * (x1 + x2), f"B_p mismatch: {B_p} != {-a_p*(x1+x2)}"
    assert C_p == a_p * x1 * x2, f"C_p mismatch: {C_p} != {a_p*x1*x2}"
    
    poly_str = format_poly(A, B, C)
    exponent_str = ""
    if D == 1:
        exponent_str += "x"
    elif D == -1:
        exponent_str += "-x"
    else:
        exponent_str += f"{D}x"
        
    if E > 0:
        exponent_str += f"+{E}"
    elif E < 0:
        exponent_str += f"{E}"
        
    if not exponent_str:
        exponent_str = "0"
        
    func_str = rf"({poly_str})e^{{{exponent_str}}}"
    if F > 0:
        func_str += f" + {F}"
    elif F < 0:
        func_str += f" - {-F}"
        
    stem = rf"Cho hàm số $y = {func_str}$. Mệnh đề nào dưới đây đúng?"
    
    if A_p > 0:
        choices = [
            (rf"Hàm số đồng biến trên các khoảng $(-\infty, {x1})$ và $({x2}, +\infty)$.", True),
            (rf"Hàm số nghịch biến trên khoảng $(-\infty, {x1})$.", False),
            (rf"Hàm số đồng biến trên khoảng $({x1}, {x2})$.", False),
            (rf"Hàm số nghịch biến trên khoảng $\mathbb{{R}}$.", False)
        ]
    else:
        choices = [
            (rf"Hàm số nghịch biến trên các khoảng $(-\infty, {x1})$ và $({x2}, +\infty)$.", True),
            (rf"Hàm số đồng biến trên khoảng $(-\infty, {x1})$.", False),
            (rf"Hàm số nghịch biến trên khoảng $({x1}, {x2})$.", False),
            (rf"Hàm số đồng biến trên khoảng $\mathbb{{R}}$.", False)
        ]
        
    if force_sample:
        pass # keep order
    else:
        random.shuffle(choices)
        
    options_text = "\\choice\n"
    for text, is_correct in choices:
        if is_correct:
            options_text += rf"{{\True {text}}}" + "\n"
        else:
            options_text += rf"{{{text}}}" + "\n"
            
    # Calculate derivative
    poly_deriv = format_poly(A_p, B_p, C_p)
    deriv_part1 = format_poly(0, 2*A, B)
    # Build the second term of derivative with proper sign handling
    # y' = (2Ax+B)e^{Dx+E} + D(Ax^2+Bx+C)e^{Dx+E}
    if D == 1:
        deriv_connector = " + "
        deriv_part2_coef = ""
    elif D == -1:
        deriv_connector = " - "
        deriv_part2_coef = ""
    elif D > 0:
        deriv_connector = " + "
        deriv_part2_coef = str(D)
    else:  # D < -1
        deriv_connector = " - "
        deriv_part2_coef = str(-D)
    deriv_part2 = rf"{deriv_part2_coef}({poly_str})e^{{{exponent_str}}}"
        
    sign_str = "> 0" if A_p > 0 else "< 0"
    sol = rf"""Tập xác định: $D = \mathbb{{R}}$.
Đạo hàm: $y' = ({deriv_part1})e^{{{exponent_str}}}{deriv_connector}{deriv_part2} = ({poly_deriv})e^{{{exponent_str}}}$.
Cho $y' = 0 \Leftrightarrow {poly_deriv} = 0 \Leftrightarrow \left[ \begin{{array}}{{l}} x = {x1} \\ x = {x2} \end{{array}} \right.$.
Ta có bảng xét dấu $y'$ (dấu của $y'$ phụ thuộc vào tam thức bậc hai $f(x) = {poly_deriv}$ có hệ số $a = {A_p} {sign_str}$):
"""
    if A_p > 0:
        sol += rf"""$y' > 0$ khi $x \in (-\infty, {x1}) \cup ({x2}, +\infty) \Rightarrow$ hàm số đồng biến trên các khoảng $(-\infty, {x1})$ và $({x2}, +\infty)$.
$y' < 0$ khi $x \in ({x1}, {x2}) \Rightarrow$ hàm số nghịch biến trên khoảng $({x1}, {x2})$."""
    else:
        sol += rf"""$y' < 0$ khi $x \in (-\infty, {x1}) \cup ({x2}, +\infty) \Rightarrow$ hàm số nghịch biến trên các khoảng $(-\infty, {x1})$ và $({x2}, +\infty)$.
$y' > 0$ khi $x \in ({x1}, {x2}) \Rightarrow$ hàm số đồng biến trên khoảng $({x1}, {x2})$."""

    return stem, options_text, sol

def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    seed_val = None
    if len(sys.argv) > 2:
        seed_val = int(sys.argv[2])
        
    out_dir = os.path.dirname(os.path.abspath(__file__))
    content = ""
    
    for i in range(num_questions):
        seed = seed_val + i if seed_val is not None else None
        force = (i == 0 and seed_val is None)
        q, opts, s = generate_question(seed, force_sample=force)
        
        content += rf"""\begin{{ex}}
{q}
{opts}
\loigiai{{
{s}
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
    out_path = os.path.join(out_dir, "don_dieu_mu_da_thuc_questions.tex")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {out_path}")

if __name__ == "__main__":
    main()
