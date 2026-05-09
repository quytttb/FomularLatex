import random
import os
import sys

def format_term(coeff, var, is_first=False):
    if coeff == 0:
        return ""
    if coeff == 1:
        return var if is_first else f"+{var}"
    if coeff == -1:
        return f"-{var}"
    if coeff > 0:
        return f"{coeff}{var}" if is_first else f"+{coeff}{var}"
    return f"{coeff}{var}"

def get_x0_str(b, k):
    if b == 1:
        if k == 1: return r"\frac{1}{e}"
        return rf"\frac{{1}}{{e^{k}}}"
    else:
        if k == 1: return rf"\frac{{1}}{{{b}e}}"
        return rf"\frac{{1}}{{{b}e^{k}}}"

def get_x1_str(k):
    if k == 1: return r"\frac{1}{e}"
    return rf"\frac{{1}}{{e^{k}}}"

def get_x2_str(k):
    if k == 1: return "e"
    return rf"e^{k}"

def generate_question(seed=None, force_sample=False):
    if seed is not None:
        random.seed(seed)

    if force_sample:
        b, c, d = 2, 2, 1
    else:
        b = random.randint(1, 5)
        c = random.randint(1, 5)
        d = random.randint(1, 10)
        
    func_str = ""
    # x \ln(bx)
    if b == 1:
        func_str += r"x \ln x"
    else:
        func_str += rf"x \ln({b}x)"
        
    func_str += format_term(c, "x")
    func_str += f"+{d}"
    
    k = c + 1
    x0_str = get_x0_str(b, k)
    x1_str = get_x1_str(k)
    x2_str = get_x2_str(k)
    
    if force_sample:
        choices = [
            (rf"Hàm số đồng biến trên khoảng $\left(0, {x0_str}\right)$.", False),
            (rf"Hàm số nghịch biến trên khoảng $\left(0, {x2_str}\right)$.", False),
            (rf"Hàm số nghịch biến trên khoảng $\left({x1_str}, +\infty\right)$.", False),
            (rf"Hàm số đồng biến trên khoảng $\left({x0_str}, +\infty\right)$.", True)
        ]
    else:
        choices = [
            (rf"Hàm số đồng biến trên khoảng $\left({x0_str}, +\infty\right)$.", True),
            (rf"Hàm số đồng biến trên khoảng $\left(0, {x0_str}\right)$.", False),
            (rf"Hàm số nghịch biến trên khoảng $\left({x1_str}, +\infty\right)$.", False),
            (rf"Hàm số nghịch biến trên khoảng $\left(0, {x2_str}\right)$.", False)
        ]
        random.shuffle(choices)
        
    options_text = "\\choice\n"
    for text, is_correct in choices:
        if is_correct:
            options_text += rf"{{\True {text}}}" + "\n"
        else:
            options_text += rf"{{{text}}}" + "\n"
            
    stem = rf"Cho hàm số $y = {func_str}$. Mệnh đề nào dưới đây đúng?"
    
    if b == 1:
        sol = rf"""Tập xác định: $D = (0, +\infty)$.
Đạo hàm: $y' = \ln x + x \cdot \frac{{1}}{{x}} + {c} = \ln x + {k}$.
Cho $y' = 0 \Leftrightarrow \ln x = -{k} \Leftrightarrow x = {x0_str}$.
Ta có bảng xét dấu $y'$:
$y' < 0$ khi $x \in \left(0, {x0_str}\right) \Rightarrow$ hàm số nghịch biến trên khoảng $\left(0, {x0_str}\right)$.
$y' > 0$ khi $x \in \left({x0_str}, +\infty\right) \Rightarrow$ hàm số đồng biến trên khoảng $\left({x0_str}, +\infty\right)$."""
    else:
        sol = rf"""Tập xác định: $D = (0, +\infty)$.
Đạo hàm: $y' = \ln({b}x) + x \cdot \frac{{{b}}}{{{b}x}} + {c} = \ln({b}x) + {k}$.
Cho $y' = 0 \Leftrightarrow \ln({b}x) = -{k} \Leftrightarrow {b}x = e^{{-{k}}} \Leftrightarrow x = {x0_str}$.
Ta có bảng xét dấu $y'$:
$y' < 0$ khi $x \in \left(0, {x0_str}\right) \Rightarrow$ hàm số nghịch biến trên khoảng $\left(0, {x0_str}\right)$.
$y' > 0$ khi $x \in \left({x0_str}, +\infty\right) \Rightarrow$ hàm số đồng biến trên khoảng $\left({x0_str}, +\infty\right)$."""
    
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
    out_path = os.path.join(out_dir, "don_dieu_logarit_questions.tex")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {out_path}")

if __name__ == "__main__":
    main()
