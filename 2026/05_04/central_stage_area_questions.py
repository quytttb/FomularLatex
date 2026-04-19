"""
Sinh đề tự luận: thiết kế sân khấu ngoài trời cắt bởi các parabol.
"""
import sys
import os
import random
from fractions import Fraction
from typing import Tuple

def format_frac_tex_from_fraction(f: Fraction) -> str:
    """Format a Fraction as LaTeX, already simplified."""
    if f.denominator == 1:
        return str(f.numerator)
    if f.numerator < 0:
        return rf"-\frac{{{-f.numerator}}}{{{f.denominator}}}"
    return rf"\frac{{{f.numerator}}}{{{f.denominator}}}"

def format_coeff_x2(num, den) -> str:
    """Format coefficient of x^2 as LaTeX. E.g. 2/1 -> '2', 2/3 -> '\\frac{2}{3}'."""
    f = Fraction(num, den)
    return format_frac_tex_from_fraction(f)

def get_nice_parameters(seed_val=None):
    if seed_val is not None:
        random.seed(seed_val)
        
    # a là nửa cạnh hình vuông
    a_choices = [1, 2, 3, 4, 5, 8, 10]
    a = random.choice(a_choices)
    side_length = 2 * a
    
    # alpha, beta để random câu hỏi Hãy tính T = alpha*p + beta*q
    alpha = random.choice([1, 2, 3])
    beta = random.choice([-2, -1, 1, 2])
    
    # Nếu không có seed và a=1, mặc định giống bài mẫu
    if a == 1 and seed_val is None:
        alpha = 1
        beta = -1

    return a, side_length, alpha, beta

def format_term(coeff, var, is_first=False):
    """Format a term like '2p', '-q', 'p' for expression display."""
    if coeff == 0:
        return ""
    
    if coeff == 1:
        term = var
    elif coeff == -1:
        term = f"-{var}"
    else:
        term = f"{coeff}{var}"
        
    if not is_first and coeff > 0:
        return f"+ {term}"
    elif not is_first and coeff < 0:
        return f"- {str(term)[1:]}"
    return term

def generate_question(seed_val=None) -> Tuple[str, str, str]:
    a, side_length, alpha, beta = get_nice_parameters(seed_val)
    
    p = 8 * a**2
    q = -7 * a**2
    answer = alpha * p + beta * q
    
    a_half = Fraction(a, 2)
    a_half_tex = format_frac_tex_from_fraction(a_half)

    # Biểu thức T = alpha*p + beta*q
    expr_T = ""
    expr_T += format_term(alpha, "p", is_first=True)
    if expr_T:
        expr_T += " " + format_term(beta, "q", is_first=False)
    else:
        expr_T += format_term(beta, "q", is_first=True)

    # ---- TikZ Hình 1 (đề bài, không label toạ độ) ----
    tikz_stem1 = r"""
\begin{center}
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1.5,samples=100]
  \def\xtrai{-2}\def\xphai{2}
  \def\yduoi{-2}\def\ytren{2}
  %\path[] (0,\yduoi)--(0,\ytren) node[below left]{$y$};
  \draw plot[domain=-1:1] (\x,{2*(\x)^2-1});
  \draw plot[domain=-1:1] (\x,{-2*(\x)^2+1});
  \draw[rotate=90] plot[domain=-1:1] (\x,{2*(\x)^2-1});
  \draw[rotate=-90] plot[domain=-1:1] (\x,{2*(\x)^2-1});
  \draw (-1,-1) rectangle (1,1);
  \pgfmathsetmacro{\can}{sqrt(2)}
  
  \draw[fill=red,opacity=0.5] 
  plot[domain=-\can/2:-1/2] (\x,{(-2*(\x)^2+1)})--
  plot[domain=-1/2:-\can/2,rotate=-90] (\x,{(2*(\x)^2-1)})
  --
  plot[domain=-\can/2:-1/2,rotate=-90] (\x,{(-2*(\x)^2+1)})
  -- plot[domain=1/2:\can/2] (\x,{(-2*(\x)^2+1)})
  --
  plot[domain=\can/2:1/2] (\x,{(2*(\x)^2-1)})
  -- plot[domain=-1/2:-\can/2,rotate=90] (\x,{(2*(\x)^2-1)})
  --
  plot[domain=-\can/2:-1/2,rotate=90] (\x,{(-2*(\x)^2+1)})
  --
  plot[domain=-1/2:-\can/2] (\x,{(2*(\x)^2-1)})
  ; 
  \fill (1,0) circle(0.5pt) node[below right]{$G$};
  \fill (0,-1) circle(0.5pt) node[below]{$F$};
  \fill (-1,0) circle(0.5pt) node[below left]{$E$};
  \fill (0,1) circle(0.5pt) node[above]{$H$};
  \fill (-1,1) circle(0.5pt) node[above left]{$A$};
  \fill (-1,-1) circle(0.5pt) node[below left]{$B$};
  \fill (1,-1) circle(0.5pt) node[below right]{$C$};
  \fill (1,1) circle(0.5pt) node[above right]{$D$};
\end{tikzpicture}
\end{center}"""

    # ---- TikZ Hình 2 (lời giải, có label toạ độ) ----
    tikz_stem2 = r"""
\begin{center}
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1.5,samples=100]
 \def\xtrai{-2}\def\xphai{2}
 \def\yduoi{-2}\def\ytren{2}
 \draw[->] (\xtrai,0)--(\xphai,0) node[below left]{$x$};
 \draw[->] (0,\yduoi)--(0,\ytren) node[below left]{$y$};
 \fill(0,0) circle(0.5pt) node[shift=(-156:5mm)]{$O$};
 \draw plot[domain=-1:1] (\x,{2*(\x)^2-1});
 \draw plot[domain=-1:1] (\x,{-2*(\x)^2+1});
 \draw[rotate=90] plot[domain=-1:1] (\x,{2*(\x)^2-1});
 \draw[rotate=-90] plot[domain=-1:1] (\x,{2*(\x)^2-1});
 \draw (-1,-1) rectangle (1,1);
 \draw 
 (-1,1)--(1,-1)
 (-1,-1)--(1,1)
 ;
\pgfmathsetmacro{\can}{sqrt(2)}

\draw[fill=red,opacity=0.5] 
plot[domain=-\can/2:-1/2] (\x,{(-2*(\x)^2+1)})--
plot[domain=-1/2:-\can/2,rotate=-90] (\x,{(2*(\x)^2-1)})
--
plot[domain=-\can/2:-1/2,rotate=-90] (\x,{(-2*(\x)^2+1)})
-- plot[domain=1/2:\can/2] (\x,{(-2*(\x)^2+1)})
--
plot[domain=\can/2:1/2] (\x,{(2*(\x)^2-1)})
-- plot[domain=-1/2:-\can/2,rotate=90] (\x,{(2*(\x)^2-1)})
--
plot[domain=-\can/2:-1/2,rotate=90] (\x,{(-2*(\x)^2+1)})
--
plot[domain=-1/2:-\can/2] (\x,{(2*(\x)^2-1)})
; 
\fill (1,1) circle(0.5pt) node[above right]{$D$};
\fill (1,-1) circle(0.5pt) node[below right]{$C$};
\fill (1,0) circle(0.5pt) node[below right]{$G$};
\fill (0,-1) circle(0.5pt) node[below right]{$F$};
\fill (-1,-1) circle(0.5pt) node[below left]{$B$};
\fill (-1,0) circle(0.5pt) node[below left]{$E$};
\fill (-1,1) circle(0.5pt) node[above left]{$A$};
\fill (0,1) circle(0.5pt) node[above left]{$H$};
\fill (1/2,-1/2) circle(0.5pt) node[below=3pt]{$N$};
\fill (1/2,0) circle(0.5pt) node[above]{#A_HALF#};
\draw[dashed] (1/2,-1/2)--(1/2,0) ;

\fill[orange,opacity=0.6] (0,0)--(1/2,0)--(1/2,-1/2)--cycle;
\fill[green,opacity=0.6] (1/2,0)--(1/2,-1/2)--(\can/2,0)--cycle;
\end{tikzpicture}
\end{center}"""
    
    tikz_stem2 = tikz_stem2.replace("#A_HALF#", f"${a_half_tex}$")
    
    # ---- Đề bài ----
    stem = f"""Hình 1 là một tác phẩm dự thi của nhà thiết kế sân khấu trong một cuộc thi thiết kế sân khấu ngoài trời tổ chức tại một quảng trường. Khi mở rộng sân khấu trung tâm ta được Hình 2. Quá trình thiết kế sân khấu trung tâm được mô tả như sau:
{tikz_stem1}
Bước 1. Vẽ hình vuông $ABCD$ có độ dài cạnh bằng ${side_length}$, và lấy trung điểm của bốn cạnh lần lượt là $E, F, G, H$.

Bước 2. Vẽ đồ thị của các hàm bậc hai đi qua ba điểm $B, C, H$ và hàm bậc hai đi qua ba điểm $F, D, A$.

Bước 3. Tương tự như Bước 2, vẽ đồ thị của các hàm bậc hai đi qua ba điểm $A, B, G$ và ba điểm $C, D, E$.

Biết rằng: Diện tích phần tô màu trong Hình 2 được cho bởi công thức $\\frac{{p\\sqrt{{2}} + q}}{{3}}$.

Hãy tính giá trị của biểu thức $T = {expr_T}$. (Với $p,q$ là các số nguyên)."""

    # ---- Tính toán các giá trị trung gian cho lời giải ----
    a2 = a**2
    
    # Hệ số m = 2/a của parabol
    m_frac = Fraction(2, a)
    m_tex = format_frac_tex_from_fraction(m_frac)
    
    # Parabol: y = (2/a)x^2 - a. Cần format hệ số 2/a trước x^2
    if m_frac == 2:
        parab_tex = f"2x^2 - {a}"
    elif m_frac == 1:
        parab_tex = f"x^2 - {a}"
    else:
        parab_tex = f"{m_tex}x^2 - {a}"
    
    # Hệ số tích phân: 2/(3a)
    coeff_int = Fraction(2, 3 * a)
    coeff_int_tex = format_frac_tex_from_fraction(coeff_int)
    
    # S1 = (a^2/3)*sqrt(2) - 5a^2/12
    s1_sqrt2_coeff = Fraction(a2, 3)
    s1_sqrt2_tex = format_frac_tex_from_fraction(s1_sqrt2_coeff)
    
    s1_const = Fraction(5 * a2, 12)
    s1_const_tex = format_frac_tex_from_fraction(s1_const)
    
    # Giá trị tại cận trên: a^2/sqrt2 = a^2*sqrt2/2 và a^2/(3*sqrt2) = a^2*sqrt2/6
    # (a^2/sqrt2 - a^2/(3*sqrt2)) = a^2*sqrt2*(1/2 - 1/6) = a^2*sqrt2*(2/6) = a^2*sqrt2/3
    # Giá trị tại cận dưới: a*(a/2) - (2/(3a))*(a/2)^3 = a^2/2 - (2/(3a))*(a^3/8) = a^2/2 - a^2/12 = 5a^2/12
    
    val_upper_1 = Fraction(a2, 1)  # a^2/sqrt2 (hệ số trước sqrt2 ở tử)
    val_upper_2 = Fraction(a2, 3)  # a^2/(3*sqrt2) (hệ số)
    
    val_lower_1 = Fraction(a2, 2)
    val_lower_1_tex = format_frac_tex_from_fraction(val_lower_1)
    val_lower_2 = Fraction(a2, 12)
    val_lower_2_tex = format_frac_tex_from_fraction(val_lower_2)
    
    # S2 = (1/2)*(a/2)*(a/2) = a^2/8
    s2_val = Fraction(a2, 8)
    s2_tex = format_frac_tex_from_fraction(s2_val)
    
    # -5a^2/12 + a^2/8 = (-10a^2 + 3a^2)/24 = -7a^2/24
    combined_const = Fraction(7 * a2, 24)
    combined_const_tex = format_frac_tex_from_fraction(combined_const)
    
    # 2*a
    two_a = 2 * a
    
    # a^2
    a_sq = a**2
    # Display helpers: avoid '1x' or '1^2' when a=1
    a_coeff = '' if a == 1 else str(a)  # coefficient before x: 'x' vs '3x'
    a_sq_tex = '1' if a == 1 else f'{a}^2'  # '1' vs '3^2' for (a)^2
    a_sq_val_tex = str(a_sq)  # numeric value of a^2
    
    # Kết quả cuối: S = (8a^2*sqrt2 - 7a^2)/3
    neg_q = -q  # = 7*a^2, giá trị dương
    
    # ---- Lời giải ----
    solution = f"""Chọn hệ trục tọa độ $Oxy$ như hình vẽ.
{tikz_stem2}
Gốc tọa độ $O$ là giao điểm của hai đường chéo $AC$ và $BD$.
Trục $Ox \\equiv EG; Oy \\equiv HF$.

Khi đó ta dễ suy ra được phương trình đường thẳng $AC: y = -x$.
Hàm số bậc hai có đồ thị đi qua $F, D, A$ có đỉnh là parabol $F(0; -{a})$. Giả sử hàm số có dạng $y=mx^2 - {a}$.
Đồ thị đi qua điểm $D({a}; {a})$ nên ta có:
$$ {a} = m \\cdot {a_sq_tex} - {a} \\Leftrightarrow {two_a} = m \\cdot {a_sq_val_tex} \\Leftrightarrow m = {m_tex}.$$
Vậy đồ thị hàm số bậc hai đi qua $F,D,A$ là: $y = {parab_tex}$.

Xét phương trình hoành độ giao điểm của đường thẳng $AC$ ($y=-x$) và đồ thị hàm số $y = {parab_tex}$:
$$ {parab_tex} = -x \\Leftrightarrow {m_tex} x^2 + x - {a} = 0 \\Leftrightarrow \\left[ \\begin{{array}}{{l}} x = -{a} \\\\ x = {a_half_tex} \\end{{array}} \\right. $$
Với $x>0$, ta có giao điểm $N({a_half_tex}; -{a_half_tex})$.
Giao điểm của đồ thị parabol với tia $Ox$: 
$$ y=0 \\Rightarrow {parab_tex} = 0 \\Rightarrow x^2 = {val_lower_1_tex} \\Rightarrow x = \\frac{{{a}}}{{\\sqrt{{2}}}}.$$

Gọi $S_1$ là diện tích vùng được tô màu xanh như hình trên, khi đó vùng này giới hạn bởi trục $Ox$, đường $x = {a_half_tex}$ và parabol $y = {parab_tex}$. Do parabol nằm dưới trục $Ox$ nên:
$$S_1 = \\int_{{{a_half_tex}}}^{{\\frac{{{a}}}{{\\sqrt{{2}}}}}} \\left({a} - {m_tex} x^2\\right) dx$$
$$S_1 = \\left( {a_coeff}x - {coeff_int_tex} x^3 \\right) \\bigg|_{{{a_half_tex}}}^{{\\frac{{{a}}}{{\\sqrt{{2}}}}}} = \\left( \\frac{{{a_sq_val_tex}}}{{\\sqrt{{2}}}} - \\frac{{{a_sq_val_tex}}}{{3\\sqrt{{2}}}} \\right) - \\left( {val_lower_1_tex} - {val_lower_2_tex} \\right) = {s1_sqrt2_tex}\\sqrt{{2}} - {s1_const_tex}.$$

Gọi $S_2$ là diện tích phần tô màu cam trong hình trên (tam giác vuông có hai cạnh góc vuông bằng ${a_half_tex}$):
$$S_2 = \\frac{{1}}{{2}} \\cdot {a_half_tex} \\cdot {a_half_tex} = {s2_tex}.$$

Diện tích phần tô màu đỏ của toàn bộ trung tâm sân khấu như hình 2 gồm 8 vùng đối xứng (mỗi vùng tương đương $S_1 + S_2$), do đó $S = 8(S_1 + S_2)$:
$$S = 8 \\left( {s1_sqrt2_tex}\\sqrt{{2}} - {s1_const_tex} + {s2_tex} \\right) = 8 \\left( {s1_sqrt2_tex}\\sqrt{{2}} - {combined_const_tex} \\right) = \\frac{{{p}\\sqrt{{2}} - {neg_q}}}{{3}}.$$

Đối chiếu với công thức $\\frac{{p\\sqrt{{2}} + q}}{{3}}$ ta có $p = {p}$ và $q = {q}$.
Vậy giá trị của biểu thức là:
$$T = {expr_T} = {alpha} \\cdot ({p}) + ({beta}) \\cdot ({q}) = {answer}.$$"""

    return stem, solution, str(answer)

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

    template = r"""\documentclass[12pt,a4paper]{article}
\usepackage{amsmath,amssymb,fancyhdr}
\usepackage{polyglossia}
\setdefaultlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage{tikz}
\usetikzlibrary{angles,quotes,calc}
\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}
\usepackage[solcolor]{ex_test}
\newcommand{\heva}[1]{\left\{\begin{aligned}#1\end{aligned}\right.}

\begin{document}
#CONTENT#
\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "central_stage_area_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, ans in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {ans}")

if __name__ == "__main__":
    main()
