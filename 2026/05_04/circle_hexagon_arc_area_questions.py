"""
Sinh đề tự luận: Diện tích phần bao bởi 6 cung tròn (parabol) nội tiếp đường tròn.

Bài toán:
  Cho đường tròn tâm O bán kính R, lấy 6 điểm chia đều A,B,C,D,E,F.
  Vẽ cung tròn C_i tiếp xúc với hai đoạn thẳng liên tiếp, đi qua hai điểm kề.
  Tính diện tích phần được bao bởi 6 cung tròn C₁ đến C₆.

Toán học:
  Parabol C₁ đối xứng qua Oy: y = ax² + b
  Đi qua A(R/2, R√3/2):  a·R²/4 + b = R√3/2          ...(1)
  Tiếp xúc OA (y=√3x) tại A:  y'(R/2) = aR = √3       ...(2)
  => a = √3/R,  b = R√3/4
  S₁ = 2∫₀^{R/2} [(√3/R)x² − √3x + R√3/4] dx = √3R²/12
  S = 6S₁ = √3R²/2

Đáp án tổng quát: S = (√3 / 2) × R²
"""
import sys
import os
import random
import math
from fractions import Fraction
from typing import Tuple


# ============================================================
#  Helpers: format LaTeX fractions / coefficients
# ============================================================

def frac_tex(num: int, den: int) -> str:
    """Return simplified LaTeX fraction. E.g. frac_tex(6,4) -> '\\frac{3}{2}'."""
    f = Fraction(num, den)
    if f.denominator == 1:
        return str(f.numerator)
    sign = "-" if f < 0 else ""
    return rf"{sign}\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"


def coeff_sqrt3_tex(num: int, den: int) -> str:
    """
    Format (num/den)√3 as LaTeX.
    E.g. (1,1) -> '\\sqrt{3}', (1,2) -> '\\frac{\\sqrt{3}}{2}',
         (3,2) -> '\\frac{3\\sqrt{3}}{2}', (2,1) -> '2\\sqrt{3}'.
    """
    f = Fraction(num, den)
    n, d = abs(f.numerator), f.denominator
    sign = "-" if f < 0 else ""
    if d == 1:
        if n == 1:
            return rf"{sign}\sqrt{{3}}"
        return rf"{sign}{n}\sqrt{{3}}"
    if n == 1:
        return rf"{sign}\frac{{\sqrt{{3}}}}{{{d}}}"
    return rf"{sign}\frac{{{n}\sqrt{{3}}}}{{{d}}}"


def point_tex(x_num, x_den, y_num, y_den) -> str:
    """Format point (p ; q√3) for LaTeX, e.g. (1;\\sqrt{3})."""
    x = frac_tex(x_num, x_den)
    y = coeff_sqrt3_tex(y_num, y_den)
    return rf"({x};{y})"


# ============================================================
#  TikZ blocks (parametrised by R)
# ============================================================

def _tikz_coeffs(R: int):
    """Return TikZ expression strings for parabola y = (√3/R)x² + R√3/4."""
    # Coefficient a = √3/R
    if R == 1:
        a_str = "sqrt(3)"           # √3
    else:
        a_str = f"sqrt(3)/{R}"      # √3/R
    # Constant b = R√3/4
    f_b = Fraction(R, 4)
    if f_b == 1:
        b_str = "sqrt(3)"
    elif f_b.denominator == 1:
        if f_b.numerator == 1:
            b_str = "sqrt(3)"
        else:
            b_str = f"{f_b.numerator}*sqrt(3)"
    else:
        if f_b.numerator == 1:
            b_str = f"sqrt(3)/{f_b.denominator}"
        else:
            b_str = f"{f_b.numerator}*sqrt(3)/{f_b.denominator}"
    return a_str, b_str


def tikz_stem(R: int) -> str:
    """TikZ hình đề bài (không có hệ trục)."""
    sc = round(2.0 / R, 3) if R > 2 else 1.0
    a_str, b_str = _tikz_coeffs(R)
    dom = R          # domain for parabola plot
    ldom = R + 0.5   # domain for tangent lines
    fill_val = float(Fraction(R, 2))

    return rf"""\begin{{center}}
\begin{{tikzpicture}}[line join=round, line cap=round,scale={sc}]
  \foreach \x/\y in {{6/A,1/B,2/C,3/D,4/E,5/F}}{{
    \begin{{scope}}[rotate=\x*60-60]
      \draw plot[domain=-{dom}:{dom}, samples=200]
            (\x, {{{a_str}*(\x)^2 + {b_str}}});
      \draw[thick,domain=0:{ldom}] plot (\x, {{sqrt(3)*\x}});
      \draw[thick,domain=-{ldom}:0] plot (\x, {{-sqrt(3)*\x}});
      \draw ({R*0.625},{R*2}) node[scale=1.5]{{$C_\x$}};
      \draw (-{R*0.35},{R*1.1}) node[scale=1.5]{{$\y$}};
      \fill[black,opacity=0.5]
        plot[domain=-{fill_val}:{fill_val}, samples=200]
             (\x, {{{a_str}*(\x)^2 + {b_str}}})
        -- plot[domain={fill_val}:0] (\x, {{sqrt(3)*\x}}) -- cycle;
    \end{{scope}}
  }}
  \fill[white] (0,0) circle(1.5pt)
        node[shift=(150:5mm)]{{$\color{{white}} O$}};
  \draw (0,0) circle({R});
\end{{tikzpicture}}
\end{{center}}"""


def tikz_stem_axes(R: int) -> str:
    """TikZ hình đề bài có hệ trục và góc π/3."""
    sc = round(2.0 / R, 3) if R > 2 else 1.0
    a_str, b_str = _tikz_coeffs(R)
    dom = R
    ldom = R + 0.5
    fill_val = float(Fraction(R, 2))
    axis_len = R + 1

    return rf"""\begin{{center}}
\begin{{tikzpicture}}[line join=round, line cap=round,scale={sc}]
  % Hệ trục
  \draw[->,blue,thick] (-{axis_len},0)--({axis_len},0) node[right]{{$x$}};
  \draw[->,blue,thick] (0,-{axis_len})--(0,{axis_len}) node[above]{{$y$}};
  % Góc pi/3
  \draw[blue,thick] (0,0)--({R},0);
  \draw[blue,thick] (0,0)--({{{R}*cos(60)}},{{{R}*sin(60)}});
  \draw[blue] (0.7,0) arc(0:60:0.7);
  \node[blue] at (0.9,0.4) {{$\frac{{\pi}}{{3}}$}};
  % Đoạn sqrt(3)
  \draw[blue,thick] ({{{R}*cos(60)}},{{{R}*sin(60)}}) -- ({{{R}*cos(60)}},0);
  \node[blue] at ({{{R}*cos(60)+0.3}},{{sin(60)}}) {{$\sqrt{{3}}$}};
  % 6 hình xoay
  \foreach \x/\y in {{6/A,1/B,2/C,3/D,4/E,5/F}}{{
    \begin{{scope}}[rotate=\x*60-60]
      \draw plot[domain=-{dom}:{dom}, samples=200]
            (\x, {{{a_str}*(\x)^2 + {b_str}}});
      \draw[thick,domain=0:{ldom}] plot (\x, {{sqrt(3)*\x}});
      \draw[thick,domain=-{ldom}:0] plot (\x, {{-sqrt(3)*\x}});
      \draw ({R*0.625},{R*2}) node[scale=1.5]{{$C_\x$}};
      \draw (-{R*0.35},{R*1.1}) node[scale=1.5]{{$\y$}};
      \fill[black,opacity=0.5]
        plot[domain=-{fill_val}:{fill_val}, samples=200]
             (\x, {{{a_str}*(\x)^2 + {b_str}}})
        -- plot[domain={fill_val}:0] (\x, {{sqrt(3)*\x}}) -- cycle;
    \end{{scope}}
  }}
  % Tâm và đường tròn
  \fill (0,0) circle(1.5pt) node[below left]{{$O$}};
  \draw (0,0) circle({R});
\end{{tikzpicture}}
\end{{center}}"""


def tikz_solution(R: int) -> str:
    """TikZ lời giải: parabol + tiếp tuyến + vùng tô màu."""
    sc = round(2.0 / R, 3) if R > 2 else 1.0
    a_str, b_str = _tikz_coeffs(R)
    plot_dom = R * 0.75
    line_ext = R * 0.9
    R_half = float(Fraction(R, 2))

    a_x = frac_tex(R, 2)
    a_y = coeff_sqrt3_tex(R, 2)

    return rf"""\begin{{center}}
\begin{{tikzpicture}}[scale={sc}]
  % Trục
  \draw[->] (-{R},0)--({R},0) node[right]{{$x$}};
  \draw[->] (0,-0.5)--(0,{R*1.5}) node[above]{{$y$}};
  % Parabol
  \draw[thick,domain=-{plot_dom}:{plot_dom},samples=200]
       plot (\x, {{{a_str}*(\x)^2 + {b_str}}});
  % Tiếp tuyến tại x={R_half}: y = sqrt(3)x
  \draw[thick] (-{line_ext*0.3},{{-{line_ext*0.3}*sqrt(3)}})
               -- ({line_ext},{{sqrt(3)*{line_ext}}});
  % Tiếp tuyến tại x=-{R_half}: y = -sqrt(3)x
  \draw[thick] ({line_ext*0.3},{{-{line_ext*0.3}*sqrt(3)}})
               -- (-{line_ext},{{sqrt(3)*{line_ext}}});
  % Điểm
  \fill[blue] ({R_half},{{{R_half}*sqrt(3)}}) circle (2pt)
        node[right]{{$A({a_x};{a_y})$}};
  \fill[blue] (-{R_half},{{{R_half}*sqrt(3)}}) circle (2pt)
        node[left]{{$B(-{a_x};{a_y})$}};
  \fill[blue] (0,{{{b_str}}}) circle (2pt) node[above left]{{$I$}};
  \fill (0,0) circle (2pt) node[below right]{{$O$}};
  % Vùng tô màu
  \fill[green,opacity=0.4]
    plot[domain=0:{R_half}] (\x, {{{a_str}*(\x)^2 + {b_str}}})
    -- (0,0) -- cycle;
\end{{tikzpicture}}
\end{{center}}"""


# ============================================================
#  Core: generate question + solution
# ============================================================

def generate_question(seed_val=None) -> Tuple[str, str, str]:
    if seed_val is not None:
        random.seed(seed_val)

    R = random.choice([1, 2, 3, 4, 5, 6])

    # ---------- Đáp án ----------
    # S = (√3/2) R²
    S_value = math.sqrt(3) / 2 * R * R
    ans_dot = f"{S_value:.2f}"
    ans_comma = ans_dot.replace(".", ",")
    answer = f"{ans_dot} | {ans_comma}"

    # ---------- Các biểu thức LaTeX trung gian ----------
    R_half_tex = frac_tex(R, 2)                     # R/2
    R_sqrt3_half_tex = coeff_sqrt3_tex(R, 2)        # R√3/2
    a_tex = coeff_sqrt3_tex(1, R)                    # √3/R  (hệ số a)
    b_tex = coeff_sqrt3_tex(R, 4)                    # R√3/4 (hệ số b)
    A_pt = point_tex(R, 2, R, 2)                     # A(R/2 ; R√3/2)

    # Parabol: y = a·x² + b  (thay số)
    parab_tex = rf"{a_tex} x^2 + {b_tex}"

    # Tích phân cận: 0 → R/2
    # Biểu thức dưới dấu tích phân: (√3/R)x² − √3x + R√3/4
    integrand_tex = rf"{a_tex} x^2 - \sqrt{{3}} x + {b_tex}"

    # Kết quả S dạng chính xác
    S_sq = Fraction(R * R, 2)
    if S_sq.denominator == 1:
        S_exact_tex = rf"{S_sq.numerator}\sqrt{{3}}"
    else:
        S_exact_tex = coeff_sqrt3_tex(R * R, 2)

    # Hệ phương trình:
    #   a·(R/2)² + b = R√3/2  tức  a·R²/4 + b = R√3/2
    #   y'(R/2) = 2a·(R/2) = aR = √3
    # Viết dạng LaTeX cho hệ phương trình:
    R_sq_4 = Fraction(R*R, 4)
    R_sq_4_tex = frac_tex(R*R, 4)
    if R == 1:
        eq1_lhs = rf"\frac{{1}}{{4}} a + b"
        eq2_lhs = "a"
    elif R == 2:
        eq1_lhs = "a + b"
        eq2_lhs = "2a"
    else:
        eq1_lhs = rf"{R_sq_4_tex} a + b"
        eq2_lhs = rf"{R}a"

    # ---------- Đề bài ----------
    stem = rf"""Cho đường tròn tâm $O$, bán kính bằng ${R}$. Trên đường tròn, lấy $6$ điểm chia đều đường tròn, lần lượt là $A, B, C, D, E, F$.

Vẽ cung tròn $C_1$ tiếp xúc với hai đoạn thẳng $OA$ và $OB$, đi qua hai điểm $A$ và $B$. Tương tự, vẽ cung tròn $C_2$ tiếp xúc với hai đoạn thẳng $OB$ và $OC$, đi qua $B$ và $C$. Tiếp tục bằng cách tương tự, ta vẽ các cung tròn $C_3, C_4, C_5, C_6$ tiếp xúc với các cặp đoạn thẳng liên tiếp tạo bởi các điểm trên.
{tikz_stem(R)}
Hỏi: Diện tích phần được bao bởi $6$ cung tròn $C_1$ đến $C_6$ là bao nhiêu? (làm tròn kết quả đến hàng phần trăm)"""

    # ---------- Lời giải ----------
    solution = rf"""Gắn hệ trục tọa độ như hình vẽ.
{tikz_stem_axes(R)}
Ta dễ có được góc $\widehat{{AOF}} = \dfrac{{\pi}}{{3}}$ suy ra đường thẳng $OA: y = \sqrt{{3}}\,x$, do đó điểm $A{A_pt}$.

Dễ thấy được đường cong $C_1$ là đồ thị hàm số parabol đối xứng qua trục $Oy$. Do đó hàm số parabol đó có dạng: $y = ax^2 + b$ và đồ thị hàm số này đi qua điểm $A, B$.

Ta có:
$$\heva{{{eq1_lhs} = {R_sqrt3_half_tex} \\ {eq2_lhs} = \sqrt{{3}} }}
\Rightarrow
\heva{{a = {a_tex} \\ b = {b_tex} }}$$

Vậy $(C_1): y = {parab_tex}$.
{tikz_solution(R)}
Để tiện tính toán: Ta xét riêng diện tích tô đậm được tạo bởi cung tròn $C_1$ với hai đoạn thẳng $OA, OB$.

Khi đó diện tích tô đậm được tạo bởi cung tròn $C_1$ với hai đoạn thẳng $OA, OB$ là:
$$S_1 = 2\int_0^{{{R_half_tex}}} \left({integrand_tex}\right) dx$$

Suy ra diện tích phần được bao bởi $6$ cung tròn $C_1$ đến $C_6$ là:
$$S = 6 S_1 = 12 \int_0^{{{R_half_tex}}} \left({integrand_tex}\right) dx = {S_exact_tex} \approx {answer}$$"""

    return stem, solution, answer


# ============================================================
#  Main: CLI entry point
# ============================================================

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
        content += (
            f"\\begin{{ex}}%Câu {i+1}\n{q}\n\n"
            f"\\shortans{{{a}}}\n"
            f"\\loigiai{{\n{s}\n}}\n"
            f"\\end{{ex}}\n\n"
        )

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
    output_file = os.path.join(out_dir, "circle_hexagon_arc_area_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, ans in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {ans}")


if __name__ == "__main__":
    main()
