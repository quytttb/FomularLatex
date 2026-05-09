import sys
import os
import random
import math
from fractions import Fraction
from typing import Tuple

def fmt_frac(v):
    if v.denominator == 1:
        return f"{v.numerator}"
    return rf"\frac{{{v.numerator}}}{{{v.denominator}}}"

def fmt_dec(v: Fraction, precision=4):
    out = f"{float(v):.{precision}f}".rstrip('0').rstrip('.')
    return out.replace('.', ',')

def fmt_point_dec(p):
    return f"({fmt_dec(p[0])}; {fmt_dec(p[1])}; {fmt_dec(p[2])})"

def fmt_point(p):
    return f"({fmt_frac(p[0])}; {fmt_frac(p[1])}; {fmt_frac(p[2])})"

def sqrt_tex(v: Fraction):
    if v.denominator == 1:
        num_str = str(v.numerator)
        root = math.sqrt(v.numerator)
        if root == int(root):
            return str(int(root))
        return rf"\sqrt{{{num_str}}}"
    
    num_str = str(v.numerator)
    den_str = str(v.denominator)
    root_num = math.sqrt(v.numerator)
    root_den = math.sqrt(v.denominator)
    
    if root_num == int(root_num) and root_den == int(root_den):
        return rf"\frac{{{int(root_num)}}}{{{int(root_den)}}}"
    elif root_den == int(root_den):
        return rf"\frac{{\sqrt{{{num_str}}}}}{{{int(root_den)}}}"
    else:
        return rf"\frac{{\sqrt{{{v.numerator * v.denominator}}}}}{{{v.denominator}}}"

def num_tex(v: Fraction):
    if v.denominator == 1:
        return str(v.numerator)
    return f"{float(v):.1f}".replace('.', ',')

def format_sqrt_frac(num, den):
    if num == 0: return "0"
    a, u = 1, num
    for p in [2, 3, 5, 7, 11, 13]:
        while u % (p**2) == 0:
            a *= p; u //= (p**2)
    b, v = 1, den
    for p in [2, 3, 5, 7, 11, 13]:
        while v % (p**2) == 0:
            b *= p; v //= (p**2)
    top_mul = a
    bot = b * v
    top_sqrt = u * v
    f = Fraction(top_mul, bot)
    top_c = f.numerator
    bot_c = f.denominator
    if top_sqrt == 1:
        if bot_c == 1: return str(top_c)
        return rf"\frac{{{top_c}}}{{{bot_c}}}"
    c, w = 1, top_sqrt
    for p in [2, 3, 5, 7, 11, 13]:
        while w % (p**2) == 0:
            c *= p; w //= (p**2)
    top_c *= c
    top_sqrt = w
    f2 = Fraction(top_c, bot_c)
    top_c = f2.numerator
    bot_c = f2.denominator
    if top_c == 1 and top_sqrt == 1:
        if bot_c == 1: return "1"
        return rf"\frac{{1}}{{{bot_c}}}"
    top_str = ""
    if top_c > 1: top_str += str(top_c)
    if top_c < 0 and top_c == -1: top_str += "-"
    if top_sqrt > 1: top_str += rf"\sqrt{{{top_sqrt}}}"
    elif top_c == 1: top_str = "1"
    if bot_c == 1: return top_str
    return rf"\frac{{{top_str}}}{{{bot_c}}}"

def term(var, val):
    if val == 0: return var
    if val > 0: return f"{var} - {val}"
    return f"{var} + {-val}"

def bracket_term(var, val):
    if val == 0: return f"{var}^2"
    if val > 0: return f"({var} - {val})^2"
    return f"({var} + {-val})^2"

def pt(c):
    return f"({c[0]}; {c[1]}; {c[2]})"

def fmt_f(n, d):
    if n < 0: return rf"-\frac{{{-n}}}{{{d}}}"
    return rf"\frac{{{n}}}{{{d}}}"

def generate_question(seed_val=None) -> Tuple[str, str, str]:
    if seed_val is not None:
        random.seed(seed_val)

    while True:
        x_I = random.randint(-8, 8)
        y_I = random.randint(-8, 8)
        z_I = random.randint(-8, 8)
        I = (x_I, y_I, z_I)
        
        u1, u2, u3 = 0, 0, 0
        while u1==0 or u2==0 or u3==0:
            u1 = random.randint(-5, 5)
            u2 = random.randint(-5, 5)
            u3 = random.randint(-5, 5)
        u = (u1, u2, u3)
        u_sq = u1**2 + u2**2 + u3**2
        
        x_d = random.randint(-8, 8)
        y_d = random.randint(-8, 8)
        z_d = random.randint(-8, 8)
        M = (x_d, y_d, z_d)
        
        IM = (M[0]-I[0], M[1]-I[1], M[2]-I[2])
        cross = (IM[1]*u[2] - IM[2]*u[1], IM[2]*u[0] - IM[0]*u[2], IM[0]*u[1] - IM[1]*u[0])
        cross_sq = cross[0]**2 + cross[1]**2 + cross[2]**2
        
        if cross_sq == 0: continue
        
        IK_sq_frac = Fraction(cross_sq, u_sq)
        
        R_sq = random.randint(2, 25)
        if IK_sq_frac <= R_sq: continue
        
        cos_AIB = 2 * Fraction(R_sq) / IK_sq_frac - 1
        if cos_AIB.denominator > 25 or cos_AIB >= 1 or cos_AIB <= -1 or cos_AIB == 0:
            continue
        if cos_AIB.denominator == 1:
            continue
            
        break
        
    v = random.choice([2, 3, 4, 5])
    
    # a
    a_is_true = random.choice([True, False])
    fake_R_sq = R_sq if a_is_true else R_sq + random.choice([1, 2, -1])
    if fake_R_sq <= 0: fake_R_sq = R_sq + 2
    R_str = format_sqrt_frac(fake_R_sq, 1)
    stmt_a = rf"{'*' if a_is_true else ''}a) Quả bóng có tâm $I{pt(I)}$ và bán kính $R = {R_str}$."
    ans_a = "Đúng" if a_is_true else "Sai"
    sol_a = rf"a) {ans_a}. Mặt ngoài quả bóng là mặt cầu $(S)$ có tâm $I{pt(I)}$ và bán kính $R = {format_sqrt_frac(R_sq, 1)}$."
    
    # b
    b_is_true = random.choice([True, False])
    dist_true_str = format_sqrt_frac(cross_sq, u_sq)
    dist_str = dist_true_str if b_is_true else format_sqrt_frac(cross_sq * random.choice([2, 3]), u_sq)
    stmt_b = rf"{'*' if b_is_true else ''}b) Khoảng cách từ tâm quả bóng đến đường thẳng $d$ bằng ${dist_str}$."
    
    ans_b = "Đúng" if b_is_true else "Sai"
    sol_b = rf"""b) {ans_b}.
Đường thẳng $d: \frac{{{term('x', x_d)}}}{{{u1}}} = \frac{{{term('y', y_d)}}}{{{u2}}} = \frac{{{term('z', z_d)}}}{{{u3}}}$ qua $A'{pt(M)}$ và có vectơ chỉ phương $\vec{{u}}_d = {pt(u)}$.

Ta có: $\overrightarrow{{A'I}} = {pt((-IM[0], -IM[1], -IM[2]))}$; $[\vec{{u}}_d, \overrightarrow{{A'I}}] = {pt((cross[0], cross[1], cross[2]))}$.

Do đó $d(I, d) = \frac{{|[\vec{{u}}_d, \overrightarrow{{A'I}}]|}}{{|\vec{{u}}_d|}} = \frac{{\sqrt{{ {cross[0]}^2 + {cross[1]}^2 + {cross[2]}^2 }}}}{{\sqrt{{ {u1}^2 + {u2}^2 + {u3}^2 }}}} = {dist_true_str}$."""

    # c
    a_frac = cos_AIB.numerator
    b_frac = cos_AIB.denominator
    true_val = a_frac**2 + b_frac**2
    c_is_true = random.choice([True, False])
    val = true_val if c_is_true else true_val + random.randint(1, 10)
    frac_str = fmt_f(a_frac, b_frac)
    
    stmt_c = rf"{'*' if c_is_true else ''}c) Nếu $\cos \widehat{{AIB}} = \frac{{a}}{{b}}$ (phân số tối giản) thì giá trị $a^2 + b^2 = {val}$."
    
    ans_c = "Đúng" if c_is_true else "Sai"
    sol_c = rf"""c) {ans_c}.
Gọi $K$ là hình chiếu của $I$ trên $d$ thì $KI = {dist_true_str}$ và $KA \perp IA$; suy ra $\cos \widehat{{AIK}} = \frac{{IA}}{{IK}} = {format_sqrt_frac(R_sq * u_sq, cross_sq)}$.

Do vậy $\cos \widehat{{AIB}} = 2\cos^2 \widehat{{AIK}} - 1 = 2\left({format_sqrt_frac(R_sq * u_sq, cross_sq)}\right)^2 - 1 = {frac_str} \Rightarrow a = {a_frac}, b = {b_frac} \Rightarrow a^2 + b^2 = {true_val}$."""

    # d
    arc_len = math.sqrt(R_sq) * math.acos(float(cos_AIB)) # dm
    t_seconds_exact = (arc_len * 10) / v
    t_seconds = round(t_seconds_exact)
    
    d_is_true = random.choice([True, False])
    t_val = t_seconds if d_is_true else t_seconds + random.choice([-3, -2, 2, 3])
    
    arc_len_rounded = f"{arc_len:.2f}".replace('.', ',')
        
    stmt_d = rf"{'*' if d_is_true else ''}d) Một con kiến bò từ vị trí $A$ đến vị trí $B$ trên quả bóng với tốc độ ${v}$ cm/s; thời gian ngắn nhất cho chuyến đi này là ${t_val}$ giây (làm tròn đến hàng đơn vị)."
    
    ans_d = "Đúng" if d_is_true else "Sai"
    sol_d = rf"""d) {ans_d}.
Độ dài cung tròn bé nhất mà con kiến có thể đi: $l_{{AB}} = R \times \widehat{{AIB}} = {format_sqrt_frac(R_sq, 1)} \times \arccos\left({frac_str}\right) \approx {arc_len_rounded}$ dm.

Thời gian tối thiểu để kiến đến nơi là $\frac{{l_{{AB}} \times 10}}{{{v}}} \approx {t_seconds}$ giây."""

    stem = rf"""Bài toán 7: Xét một hệ trục tọa độ $Oxyz$ được cho sẵn, đơn vị trên mỗi trục là $dm$, mặt ngoài của một quả bóng được mô hình hóa bởi phương trình mặt cầu ${bracket_term('x', x_I)} + {bracket_term('y', y_I)} + {bracket_term('z', z_I)} = {R_sq}$, quả bóng nằm yên trên sàn nhà. Người ta nhìn thấy một tấm ván ngã xuống đè lên quả bóng, phần giao của tấm ván và sàn nhà là đường thẳng $d$ có phương trình $\frac{{{term('x', x_d)}}}{{{u1}}} = \frac{{{term('y', y_d)}}}{{{u2}}} = \frac{{{term('z', z_d)}}}{{{u3}}}$. Gọi $A, B$ lần lượt là hai tiếp điểm của tấm ván, sàn nhà với quả bóng và $I$ là tâm quả bóng."""
    
    question = rf"""{stem}

{stmt_a}

{stmt_b}

{stmt_c}

{stmt_d}"""
    
    sol_stem = r"""\begin{center}
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
  \def\R{1.2}
  \path 
  (0,2) coordinate (A1)
  ($(A1)+(6,0)$) coordinate (B1)
  ($(B1)+(1.5,-2)$) coordinate (C)
  ($(C)+(-6,0)$) coordinate (D)
  ($(A1)! 1/2 !(D)$) coordinate (K)
  ($(D)! 1/2 !(C)+(-0.5,1)$) coordinate (B)
  ($(B)+(0,1.2)$) coordinate (I)
  ($(I)+(-0.35,0.85)$) coordinate (A)
  (intersection of K--I and A--B) coordinate (H)
  ;
  \draw (I) circle (\R);
  \draw[dashed] ($(I)+(-1.2,0)$) arc (180:0:1.2cm and 0.5cm) ($(I)+(-1.2,0)$) arc (180:360:1.2cm and 0.5cm) ($(I)+(0,1.2)$) arc (90:-90:0.5cm and 1.2cm) ($(I)+(0,1.2)$) arc (90:270:0.5cm and 1.2cm);
  \draw ($(A1)!-0.2!(D)$) -- ($(D)!-0.2!(A1)$) node[pos=1, right] {$d$};
  \draw (D)--(C)--(B1)--++(-1,0) coordinate (E) (K)--(A)--(I) (A1)--++(4,3) coordinate (A2) (D)--++(4,3)coordinate (A3)--(A2);
  \draw[dashed] (E)--(A1) (I)--(K) (A)--(B) (K)--(B);
  \draw pic[draw,angle radius=1.5mm] {right angle = I--H--A};
  \foreach \p/\r in {A/0,K/180,I/45,H/180,B/-90}
  \fill (\p) circle (1.2pt) node[shift={(\r:3mm)}]{$\p$};
  \draw[dashed] (I)--(B); 
  \pic[draw,angle radius=6mm]{angle = B1--C--D};
  \draw ($(C)+(150:4.5mm)$) node[]{$Q$};
  
  \pic[draw,angle radius=6mm]{angle = A1--A2--A3};
  \draw ($(A2)+(-90:4mm)$) node[]{$P$};
 \end{tikzpicture}
\end{center}"""
    
    solution = rf"""{sol_stem}

{sol_a}

{sol_b}

{sol_c}

{sol_d}"""

    solution = solution.strip()

    key = ", ".join(["Đ" if x else "S" for x in [a_is_true, b_is_true, c_is_true, d_is_true]])
    
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
        seed = seed_val + i if seed_val is not None else None
        q, s, k = generate_question(seed)
        keys.append(k)
        content += rf"""Câu {i+1}: {q}

Lời giải:

{s}

"""

    template = r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath, amsfonts, amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\usepackage{tikz}
\usetikzlibrary{calc,angles,quotes,decorations.markings,intersections,patterns,shapes.geometric}

\newcommand{\heva}[1]{\left\{\begin{aligned}#1\end{aligned}\right.}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)

    out_path = os.path.join(out_dir, "cau_7_questions.tex")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {out_path}")
    print("\n=== ĐÁP ÁN ===")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: Đáp án: {k}")

if __name__ == "__main__":
    main()
