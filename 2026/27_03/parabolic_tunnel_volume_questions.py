"""
Sinh đề tự luận: thể tích đường hầm parabol.

Format:
  \begin{ex}
  ...
  \shortans{}
  \loigiai{}
  \end{ex}
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
        L = random.choice([20, 30, 40, 50, 60, 80])
        a = random.choice([10, 12, 14, 15, 16, 20])
        b_choices = [x for x in [4, 5, 6, 8, 10] if x < a]
        b = random.choice(b_choices)
        k = random.choice([2, 5, 8])
        
        c = (k + 1) // 3
        
        if (b * L) % (a - b) != 0:
            continue
            
        return L, a, b, k, c

def generate_question(seed_val=None) -> Tuple[str, str, str]:
    L, a, b, k, c = get_nice_parameters(seed_val)
    
    m_frac = Fraction(a - b, L)
    m_tex = rf"\frac{{{m_frac.numerator}}}{{{m_frac.denominator}}}" if m_frac.denominator != 1 else str(m_frac.numerator)
    
    # Try to make decimal like 0,25 if clean, otherwise use latex fraction
    m_dec = f"{float(m_frac):g}".replace('.', ',') if float(m_frac)*100%1==0 else m_tex
    
    CT = (b * L) // (a - b)
    AT = L + CT
    
    V_val = Fraction(c * L * (a**2 + a*b + b**2), 3)
    V_round = round(float(V_val))
    v_val_tex = format_frac_tex(V_val)
    
    # Neu ket qua la so nguyen hoac lam tron len/xuong ma van bang exact result
    approx_str = f" \\approx {V_round}" if V_val.denominator != 1 else ""
    
    m_val_frac = Fraction(2*k - 1, k)
    m_val_tex = format_frac_tex(m_val_frac) if m_val_frac.denominator != 1 else str(m_val_frac.numerator)

    ob_frac = Fraction(k - 1, k)
    ob_tex = format_frac_tex(ob_frac)
    ob_dec = f"{float(ob_frac):g}".replace('.', ',') if float(ob_frac)*10%1==0 else ob_tex

    ratio_val = Fraction(3 * c * (2*k - 1)**2, 4 * k**3)
    ratio_tex = rf"\frac{{{ratio_val.numerator}}}{{{ratio_val.denominator}}}"

    he_be_frac = Fraction(k, 2*k - 1)
    he_be_tex = format_frac_tex(he_be_frac)
    
    s1_coeff_val = Fraction(4*k, 3) * (he_be_frac**2)
    s1_coeff_tex = format_frac_tex(s1_coeff_val)

    be_disp = f"= {c} BE^2" if c != 1 else "= BE^2"
    
    tikz_stem = r"""
\begin{center}
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
 

 % --- Global Definitions ---
 \coordinate (D) at (0,0);
 \coordinate (C) at (2,-1);
 \coordinate (A) at (8.6,1);
 \coordinate (PD4) at ($(D)+(A)-(C)$);
 \coordinate (F) at ($(A)!1.9!(PD4)$);
 \coordinate (T6) at ($(C)+(0,2.75)$);
 \coordinate (PD7) at ($(T6)+(A)-(C)$);
 \coordinate (T8) at ($(A)!2.05!(PD7)$);
 \coordinate (B) at ($(C)!0.58!(A)$);
 \coordinate (G) at ($(T6)!0.58!(T8)$);
 \coordinate (E) at ($(D)!0.58!(F)$);
 \coordinate (P12) at (1.4,2.2);
 \coordinate (P13) at (7.71,7.76);
 \coordinate (T14) at ($(P12)!0.3!(P13)$);
 \coordinate (S) at ($(P12)!0.55!(P13)$);
 \coordinate (T16) at ($(P12)!0.62!(P13)$);
 \coordinate (PD17) at ($(B)+(S)-(G)$);
 \coordinate (H) at (intersection of S--PD17 and E--B);
 % --- Global Paths ---
 \draw (D) -- (C) -- (A) -- (T8) -- (T6) -- (C);
 \draw (B) -- (G) .. controls (5.8,4.8) and (5.42,5.28) .. (S) -- (H);
 \draw (D) .. controls (0.2,1) and (0.6,2.2) .. (P12) .. controls (1.6,2.2) and (1.8,2) .. (T6);
 \draw (T14) .. controls (3.62,4.51) and (4.24,5.28) .. (S);
 \draw (T16) .. controls (6.21,7.21) and (6.67,7.82) .. (P13) .. controls (8.11,7.74) and (8.63,7.1) .. (T8);
 \draw (P12) -- (P13);
 \draw [dashed] (D) -- (F) -- (A);
 \draw [dashed] (E) -- (B);
 \draw [dashed] (E) .. controls (2.8,2.4) and (3,3.2) .. (T14);
 \draw [dashed] (F) .. controls (4.76,3.95) and (4.98,4.82) .. (T16);
 \path [dashed] (S) -- (PD17);
 
 
 
 % --- Intersections ---
 
 % --- Point Dots (Free) ---
 \fill (D) circle (1.2pt) node[shift={(192:3mm)}]{$D$};
 \fill (C) circle (1.2pt) node[shift={(275:3mm)}]{$C$};
 \fill (A) circle (1.2pt) node[shift={(336:3mm)}]{$A$};
 \fill (F) circle (1.2pt) node[shift={(170:3mm)}]{$F$};
 \fill (B) circle (1.2pt) node[shift={(280:3mm)}]{$B$};
 \fill (G) circle (1.2pt) node[shift={(343:3mm)}]{$G$};
 \fill (E) circle (1.2pt) node[shift={(271:3mm)}]{$E$};
 \fill (P13) circle (1.2pt) node[shift={(45:3mm)}]{$P13$};
 \fill (S) circle (1.2pt) node[shift={(91:3mm)}]{$S$};
 \fill (H) circle (1.2pt) node[shift={(240:3mm)}]{$H$};
 
 % --- Angles ---
 \draw pic[draw, angle radius=0.5cm] {right angle = F--A--B};
 \draw pic[draw, angle radius=0.5cm] {right angle = E--B--C};
 \draw pic[draw, angle radius=0.5cm] {right angle = B--C--D};
 
 % --- Texts ---
 \node at (3.2,5) {$(P)$};
 \node at (6.2,3.) {$d$};
\end{tikzpicture}
\end{center}"""

    stem = f'''Một đường hầm hiện đại được thiết kế với mặt đáy là hình thang $ACDF$ vuông tại $A$ và $C$ ($AF \\parallel CD$). 
Xét một thiết diện bất kì của đường hầm vuông góc với $AC$ là một hình phẳng giới hạn bởi đường cong $(P)$, đoạn $BE$ và đoạn $BG$ như hình vẽ ($G$ thuộc $(P)$). Giả sử $(P)$ là một nhánh của parabol có đỉnh $S$ và hình chiếu của $S$ trên mặt nền là $H$, $E$ là chân của parabol ($E$ thuộc $(P)$ và mặt đáy) thì $SH = {k}EH$. 
Một mặt bên đường hầm có dạng mặt phẳng vuông góc với mặt đáy chứa đường thẳng $AC$, gọi $B$ là hình chiếu vuông góc của $G$ xuống mặt phẳng đáy thì $BE = BG$ và $B$ thuộc đoạn $AC$. 
Biết $AC = {L}$ mét, $AF = {a}$ m, $CD = {b}$ m. Tìm thể tích đường hầm trên và làm tròn đến hàng đơn vị của m$^3$.
{tikz_stem}'''

    solution = f'''Nhận xét: $S_{{\\text{{parabol}}}} = \\frac{{4}}{{3}} B.h$

Đây là bài toán tính $V$ thông qua diện tích thiết diện 1 phần Parabol $S(x)$.

+) Bước 1: Đặt trục toạ độ

Đặt $AB = x$, ta sẽ rút $BE$ theo $x$.
$$\\frac{{CD}}{{BE}} = \\frac{{CT}}{{BT}} = \\frac{{{CT}}}{{{AT}-x}}$$
$$\\Rightarrow {b}({AT}-x) = {CT} \\cdot BE$$
$$\\Leftrightarrow BE = {a} - {m_dec}x$$

Diện tích $(P)$ đầy đủ:
$$S_1 = \\frac{{4}}{{3}} HE \\cdot SH = \\frac{{{4 * k}}}{{3}} HE^2 \\quad $$

+) Bước 2: Vì $S(x) = k \\cdot S_1$ nên ta sẽ so sánh $S(x)$ và $S_1$ thông qua mô hình sau:

Giả sử ta chọn: $\\begin{{cases}} SH={k} \\\\ HE=1 \\end{{cases}}$
$\\Rightarrow (P): y = a(x^2 - 1)$ qua $S(0; {k})$

$\\Rightarrow y = -{k}x^2 + {k}$

Theo bài $BG = BE$, đặt $G(m-1; m)$

Vì $G \\in (P)$ nên: $m^2 = a((m-1)^2 - 1) \\Rightarrow m = {m_val_tex} \\Rightarrow OB = {ob_dec}$ 

$\\Rightarrow \\frac{{S(x)}}{{S_1}} = \\frac{{\\int_{{-1}}^{{{ob_tex}}} (-{k}x^2 + {k}) dx}}{{\\frac{{4}}{{3}} \\cdot 1 \\cdot {k}}} = {ratio_tex}$

Ta có: $HE = {he_be_tex} BE \\Rightarrow S_1 = {s1_coeff_tex} BE^2$

Do đó: $S(x) {be_disp}$.

Vậy: $V = \\int_{{0}}^{{{L}}} S(x) dx = {v_val_tex}{approx_str}$

Đáp án: {V_round}'''

    return stem, solution, str(V_round)

def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    seed = None
    if len(sys.argv) > 2:
        seed = int(sys.argv[2])

    content = ""
    answers = []

    for i in range(num_questions):
        q, s, a = generate_question(seed + i if seed is not None else None)
        answers.append(a)
        content += f"\\begin{{ex}}%Câu {i+1}\n{q}\n\n\\shortans{{{a}}}\n\\loigiai{{\n{s}\n}}\n\\end{{ex}}\n\n"

    tex_content = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage{{amsmath,amssymb,fancyhdr}}
\\usepackage{{polyglossia}}
\\setdefaultlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage{{tikz}}
\\usetikzlibrary{{angles,quotes,calc}}
\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{{geometry}}
\\usepackage[solcolor]{{ex_test}}
\\newcommand{{\\heva}}[1]{{\\left\\{{\\begin{{aligned}}#1\\end{{aligned}}\\right.}}

\\begin{{document}}
{content}
\\end{{document}}
"""

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "parabolic_tunnel_volume_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, a in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {a}")

if __name__ == "__main__":
    main()
