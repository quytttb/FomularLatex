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
        
    if force_sample:
        a = 1
        x1 = -1
        x2 = 1
    else:
        a = random.choice([-2, -1, 1, 2])
        x1 = random.randint(-4, 2)
        x2 = random.randint(x1 + 1, 4)
        
    b = -a * (x1 + x2 + 2)
    c = a * (x1 * x2 + x1 + x2 + 2)
    
    poly_str = format_poly(a, b, c)
    stem = rf"Cho hàm số $y = ({poly_str})e^x$. Mệnh đề nào dưới đây đúng?"
    
    if a > 0:
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
    A_p = a
    B_p = 2*a + b
    C_p = b + c
    poly_deriv = format_poly(A_p, B_p, C_p)
    deriv_part1 = format_poly(0, 2*a, b)
    
    sign_str = "> 0" if a > 0 else "< 0"
    sol = rf"""Tập xác định: $D = \mathbb{{R}}$.
Đạo hàm: $y' = ({deriv_part1})e^x + ({poly_str})e^x = ({poly_deriv})e^x$.
Cho $y' = 0 \Leftrightarrow {poly_deriv} = 0 \Leftrightarrow \left[ \begin{{array}}{{l}} x = {x1} \\ x = {x2} \end{{array}} \right.$.
Ta có bảng xét dấu $y'$ (dấu của $y'$ phụ thuộc vào tam thức bậc hai $f(x) = {poly_deriv}$ có hệ số $a = {A_p} {sign_str}$):
"""
    if a > 0:
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
