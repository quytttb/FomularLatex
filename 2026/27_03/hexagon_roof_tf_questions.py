"""
Đề đúng/sai: mái chòi lục giác cong (parabol).

Format Azota (xem SAMPLE LATEX FILE/README.md và mẫu De_mau_azota_latex_v1.tex):
  \\choiceTFt
  {{* mệnh đề đúng}}
  {{mệnh đề sai (không dấu *)}}
  ...
Trong nội dung không lặp nhãn a), b), c), d) — ex_test đánh số cột TT.
"""
import math
import os
import sys
import random
from fractions import Fraction
from typing import Tuple

def format_frac_tex(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    if f.numerator < 0:
        return rf"-\frac{{{-f.numerator}}}{{{f.denominator}}}"
    return rf"\frac{{{f.numerator}}}{{{f.denominator}}}"

def get_nice_parameters(seed_val=None):
    if seed_val is not None:
        random.seed(seed_val)
        
    while True:
        r0 = random.randint(3, 8)
        sm = random.randint(1, r0 - 1)
        H = random.choice([6, 8, 10, 12, 14, 16])
        
        # We need a, b so that:
        # a * r0^2 + b * r0 + H = 0  => b = -H/r0 - a*r0
        # a * sm^2 + b * sm + H/2 = 0
        
        # a*sm^2 + (-H/r0 - a*r0)*sm + H/2 = 0
        # a(sm^2 - r0*sm) = H*sm/r0 - H/2
        
        # a = (H*sm/r0 - H/2) / (sm^2 - r0*sm)
        num_a = H * sm - H * r0 / 2
        den_a = r0 * sm * (sm - r0)
        
        a_frac = Fraction(int(num_a * 2), int(den_a * 2))
        if a_frac == 0:
            continue
            
        b_frac = Fraction(-H, r0) - a_frac * r0
        
        if a_frac > 0 and b_frac < 0:
            # check discriminant format inside root for x:
            # y = a x^2 + b x + H
            # a x^2 + b x + (H - y) = 0
            
            lcd = math.lcm(a_frac.denominator, b_frac.denominator)
            A = a_frac.numerator * (lcd // a_frac.denominator)
            B = b_frac.numerator * (lcd // b_frac.denominator)
            C_const = H * lcd
            
            # Equation: A x^2 + B x + C_const - lcd * y = 0
            # Delta = B^2 - 4*A*(C_const - lcd * y)
            # Delta = B^2 - 4*A*C_const + 4*A*lcd * y
            D_const = B**2 - 4*A*C_const
            D_y = 4*A*lcd
            
            if D_const >= 0 and D_y > 0:
                gcd_delta = math.gcd(abs(D_const), D_y)
                sq_factor = 1
                for i in range(2, 20):
                    while gcd_delta % (i*i) == 0:
                        sq_factor *= i
                        gcd_delta //= (i*i)
                
                return r0, sm, H, a_frac, b_frac, A, B, C_const, lcd, D_const, D_y, sq_factor

def generate_question(seed_val=None) -> Tuple[str, str, str]:
    r0, sm, H, a_frac, b_frac, A, B, C_const, lcd, D_const, D_y, sq_factor = get_nice_parameters(seed_val)
    
    alpha_tex = format_frac_tex(a_frac)
    beta_tex = format_frac_tex(b_frac)
    
    def x_of_y_val(y):
        D = D_const + D_y * y
        return (-B - math.sqrt(D)) / (2 * A)
        
    n = 400_000
    dy = H / n
    total = 0.0
    for i in range(n + 1):
        y = i * dy
        x = x_of_y_val(y)
        a = (3.0 * math.sqrt(3) / 2.0) * x * x
        w = 1.0 if i in (0, n) else 2.0
        total += w * a
    V = total * dy / 2.0
    v_round = round(V, 1)
    v_comma = f"{v_round:.1f}".replace(".", ",")
    
    # Area mid
    area_mid_coef = Fraction(6 * sm**2, 4)
    if area_mid_coef.denominator == 1:
        if area_mid_coef.numerator == 1:
            area_mid_tex = r"\sqrt{3}"
        else:
            area_mid_tex = rf"{area_mid_coef.numerator}\sqrt{{3}}"
    else:
        area_mid_tex = rf"\frac{{{area_mid_coef.numerator}\sqrt{{3}}}}{{{area_mid_coef.denominator}}}"

    area_mid_full_tex = rf"\frac{{6\sqrt{{3}} \cdot {sm}^2}}{{4}} = {area_mid_tex}"
    
    # roots form
    num_part1 = -B
    
    D_const_in = D_const // (sq_factor**2)
    D_y_in = D_y // (sq_factor**2)
    
    delta_in_sqrt = f"{D_const_in} + {D_y_in}t" if D_const_in != 0 else f"{D_y_in}t"
    if D_const_in == 0 and D_y_in == 1:
        delta_in_sqrt = "t"
        
    if sq_factor == 1:
        delta_latex_t = rf"\sqrt{{{delta_in_sqrt}}}"
    else:
        delta_latex_t = rf"{sq_factor}\sqrt{{{delta_in_sqrt}}}"
        
    denom = 2 * A
    
    # For option C, we output x = (num_part1 - delta_latex_t) / denom
    # Try to simplify the fraction if possible
    gcd_all = math.gcd(math.gcd(abs(num_part1), sq_factor), denom)
    
    np1 = num_part1 // gcd_all
    sqf = sq_factor // gcd_all
    den = denom // gcd_all
    
    if sqf == 1:
        delta_l_t = rf"\sqrt{{{delta_in_sqrt}}}"
    else:
        delta_l_t = rf"{sqf}\sqrt{{{delta_in_sqrt}}}"
        
    if den == 1:
        x_eq_t = rf"{np1} - {delta_l_t}"
        x_eq_y = x_eq_t.replace("t", "y").replace("sqry", "sqrt")
    else:
        x_eq_t = rf"\frac{{{np1} - {delta_l_t}}}{{{den}}}"
        x_eq_y = rf"\frac{{{np1} - {delta_l_t.replace('t', 'y').replace('sqry', 'sqrt')}}}{{{den}}}"
        
    # generate a WRONG eq for statement c
    sqf_wrong = sqf
    dy_wrong = D_y_in // 2 if D_y_in % 2 == 0 and D_y_in > 2 else D_y_in + 1
    
    delta_in_wrong = f"{D_const_in} + {dy_wrong}t" if D_const_in != 0 else f"{dy_wrong}t"
    if sqf_wrong == 1:
        dl_wrong = rf"\sqrt{{{delta_in_wrong}}}"
    else:
        dl_wrong = rf"{sqf_wrong}\sqrt{{{delta_in_wrong}}}"
        
    if den == 1:
        x_wrong_t = rf"{np1} - {dl_wrong}"
    else:
        x_wrong_t = rf"\frac{{{np1} - {dl_wrong}}}{{{den}}}"

    tikz_code = r"""
\begin{center}
\begin{tikzpicture}[scale=1, font=\footnotesize, line join=round, line cap=round, >=stealth,color=red!75!black, line width=1pt]
   \coordinate (A) at (0,0);
   \coordinate (B) at (1.5,1.3);
   \coordinate (C) at (4,1);
   \coordinate (O) at ($(A)+(C)-(B)$);
   \coordinate (D) at ($(A)!2!(O)$);\coordinate (E) at ($(B)!2!(O)$);
   \coordinate (F) at ($(C)!2!(O)$);
   \coordinate (S) at ($(O)+(0,5)$);\coordinate (M) at ($(S)!0.5!(O)$);
   \draw(C)--(D) (A)--(F)--(E)--(E)--(D);
   \draw[dashed,thin](A)--(B)--(C)--(D) (A)--(D) (S)--(O) (B)--(E) (C)--(F);
   \draw (1,1) node [left] {$c_1$};\draw (2,0) node [left] {$c_2$};\draw (3.3,0) node [left] {$c_3$};
   \draw (4,0) node [left] {$c_4$};\draw (3.8,2) node [left] {$c_5$};\draw (2.2,1.8) node [left] {$c_6$};
   \foreach \i/\g in {S/90,O/-90}{\draw[fill=black](\i) circle (1pt) ($(\i)+(\g:3mm)$) node[scale=1]{$\i$};}
   \begin{scope}
    \clip (-2,-2) rectangle (5,5);
    \draw[name path=(C)] plot[smooth,tension=0.7] coordinates{(S)(1.2,1.5)(A)};
    \draw[name path=(C)] plot[smooth,tension=0.7] coordinates{(S)(2,1.5)(F)};
    \draw[name path=(C)] plot[smooth,tension=0.7] coordinates{(S)(2.7,0.5)(E)};
    \draw[name path=(C)] plot[smooth,tension=0.7] coordinates{(S)(3.6,0.5)(D)};
    \draw[name path=(C)] plot[smooth,tension=0.7] coordinates{(S)(3.5,1.8)(C)};
    \draw[name path=(C),dashed] plot[smooth,tension=0.7] coordinates{(S)(2,2.5)(B)};
   \end{scope}
\end{tikzpicture}
\end{center}"""

    y_eq_str = f"y = {alpha_tex}x^2"
    if b_frac > 0:
        y_eq_str += f" + {beta_tex}x"
    elif b_frac < 0:
        y_eq_str += f" - {format_frac_tex(-b_frac)}x"
        
    if H > 0:
        y_eq_str += f" + {H}"

    stem = f'''Phần mái $(H)$ của một cái chòi có dạng hình "chóp lục giác cong đều" như hình vẽ. Đáy của $(H)$ là một lục giác đều tâm $O$ độ dài cạnh ${r0}\\text{{ m}}$, chiều cao $SO = {H}\\text{{ m}}$ (vuông góc với mặt phẳng đáy). Các cạnh bên của $(H)$ là các sợi dây $c_1, c_2, c_3, c_4, c_5, c_6$ nằm trên các đường parabol có trục đối xứng song song với $SO$. Giả sử giao tuyến nếu có của $(H)$ và mặt phẳng $(\\alpha)$ vuông góc với $SO$ là một lục giác đều. Biết rằng khi $(\\alpha)$ đi qua trung điểm của $SO$ thì lục giác đều có cạnh ${sm}\\text{{ m}}$.{tikz_code}'''

    # Dùng bảng thủ công (longtable)
    stmt_a = f"*a) Diện tích hình lục giác đều nói trên khi $(\\alpha)$ đi qua trung điểm của $SO$ là ${area_mid_tex}\\text{{ m}}^2$."
    stmt_b = f"*b) Chọn hệ trục tọa độ $Oxy$ sao cho gốc tọa độ là điểm $O$ trên hình vẽ, $S$ thuộc tia $Oy$ và đỉnh $A$ của lục giác đều thuộc tia $Ox$ (đơn vị trên mỗi trục tọa độ là mét) thì $c_4$ nằm trên đường parabol có phương trình ${y_eq_str}$."
    stmt_c = f"c) Nếu $(\\alpha)$ cắt $SO$ và $c_4$ lần lượt tại $M$ và $B$ mà $t = OM\\ (0 \\le t \\le {H})$ thì độ dài đoạn $BM$ là ${x_wrong_t}$."
    stmt_d = f"*d) Thể tích phần không gian nằm bên trong mái chòi $(H)$ là ${v_comma}\\text{{ m}}^3$."

    eq1_str = rf"{A}a + {abs(B)}b + c = 0" if B < 0 else rf"{A}a - {abs(B)}b + c = 0" # simplified representation
    
    solution = f'''a) Diện tích hình lục giác đều độ dài cạnh ${sm}\\text{{ m}}$ khi $(\\alpha)$ đi qua trung điểm của $SO$ là ${area_mid_full_tex}\\text{{ m}}^2$.

b) Parabol $c_4 : y = ax^2 + bx + c$ đi qua các điểm $S(0; {H})$, $E({sm}; {H//2})$, $A({r0}; 0)$
$$ \\Rightarrow \\begin{{cases}} c = {H} \\\\ {sm**2}a + {sm}b + c = {H//2} \\\\ {r0**2}a + {r0}b + c = 0 \\end{{cases}} \\Leftrightarrow \\begin{{cases}} a = {alpha_tex} \\\\ b = {beta_tex} \\\\ c = {H} \\end{{cases}} \\Rightarrow c_4 : {y_eq_str}. $$

c) Khi $t = OM\\ (0 \\le t \\le {H}) \\Rightarrow y_B = t \\Rightarrow t = {alpha_tex}x^2 {('+' + beta_tex) if b_frac>0 else ('-' + format_frac_tex(-b_frac))}x + {H}$
$$ \\Leftrightarrow {A}x^2 {('+' + str(B)) if B>0 else ('-' + str(-B))}x + {C_const} - {lcd}t = 0 $$
$$ \\Leftrightarrow x = {x_eq_t} \\Rightarrow x = {x_eq_t} = BM \\text{{ do }} 0 < x = BM < {r0}. $$

d) Mặt cắt vuông góc với trục $Oy$ tại điểm có tung độ $y\\ (0 \\le y \\le {H})$ là lục giác đều có độ dài cạnh $x = {x_eq_y}$ và có diện tích $S(y) = \\frac{{3\\sqrt{{3}}}}{{2}}\\left({x_eq_y}\\right)^2\\text{{ m}}^2$.

Thể tích phần không gian nằm bên trong mái chòi $(H)$ là 
$$ V = \\int_0^{{{H}}} S(y)\\,dy = \\int_0^{{{H}}} \\frac{{3\\sqrt{{3}}}}{{2}}\\left({x_eq_y}\\right)^2\\,dy \\approx {v_comma}\\text{{ m}}^3. $$

Vậy a) đúng; b) đúng; c) sai và d) đúng.'''

    question = f"""{stem}

{stmt_a}

{stmt_b}

{stmt_c}

{stmt_d}"""
    key = "Đ, Đ, S, Đ"
    return question, solution, key

def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    seed = None
    if len(sys.argv) > 2:
        seed = int(sys.argv[2])

    content = ""
    keys = []

    for i in range(num_questions):
        q, s, k = generate_question(seed + i if seed is not None else None)
        keys.append(k)
        content += f"\\begin{{ex}}%Câu {i+1}\n{q}\n\n\\loigiai{{\n{s}\n}}\n\\end{{ex}}\n\n"

    tex_content = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage{{amsmath,amssymb,fancyhdr,longtable}}
\\usepackage{{polyglossia}}
\\setdefaultlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage{{tikz}}
\\usetikzlibrary{{angles,patterns,calc,arrows,intersections}}
\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{{geometry}}
\\usepackage[solcolor]{{ex_test}}
\\newcommand{{\\heva}}[1]{{\\left\\{{\\begin{{aligned}}#1\\end{{aligned}}\\right.}}

\\begin{{document}}
{content}
\\end{{document}}
"""

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "hexagon_roof_tf_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")

if __name__ == "__main__":
    main()
