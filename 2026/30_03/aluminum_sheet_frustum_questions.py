"""
Generate LaTeX: square aluminum sheet, corner cuts, folded regular square frustum bucket.

Randomises parameters s (sheet side, dm) and t (corner cut AM = AP, dm).
  s_pool : 10 values in [6..15]
  t_pool : [1, 2, 3]
  Constraint: s > 4t  (ensures interior maximum)  AND  p = s-2t >= 2

Output: ex_test format (\\begin{ex} ... \\shortans{} \\loigiai{}).
Same problem type as chau_nuoc.tex.

Usage:
  python3 aluminum_sheet_frustum_questions.py [num_questions] [seed]
"""
import math
import os
import random
import sys
from math import gcd
from typing import Tuple

# ── TikZ figures (schematic, coordinates fixed regardless of s, t) ─────────────

TIKZ_FLAT = r"""
\begin{center}
  \begin{tikzpicture}[scale=0.8, font=\footnotesize]
   % Sơ đồ khai triển tấm nhôm (không đúng tỉ lệ)
   \coordinate (A) at (0,6);
   \coordinate (B) at (0,0);
   \coordinate (C) at (6,0);
   \coordinate (D) at (6,6);
   
   % Tọa độ các đỉnh hình vuông nét đứt bên trong (Đáy nhỏ)
   \coordinate (N) at (1.5,4.5);
   \coordinate (E) at (1.5,1.5);
   \coordinate (Q) at (4.5,1.5);
   \coordinate (U) at (4.5,4.5);
   
   % Các điểm nằm trên các cạnh ngoài để tạo viền cho 4 cánh
   \coordinate (M)  at (0,5.2);
   \coordinate (P)  at (0.8,6);
   
   \coordinate (M1) at (0,0.8);
   \coordinate (P1) at (0.8,0);
   
   \coordinate (Q1) at (5.2,0);
   \coordinate (Q2) at (6,0.8);
   
   \coordinate (U1) at (6,5.2);
   \coordinate (U2) at (5.2,6);
   
   % TÔ MÀU NỀN
   \fill[blue!10] (P) -- (U2) -- (U) -- (U1) -- (Q2) -- (Q) -- (Q1) -- (P1) -- (E) -- (M1) -- (M) -- (N) -- cycle;
   \fill[blue!15] (N) -- (U) -- (Q) -- (E) -- cycle;
   
   % VẼ CÁC PHẦN CẮT BỎ Ở 4 GÓC
   \draw[pattern=north west lines, pattern color=brown] (A) -- (P) -- (N) -- (M) -- cycle;
   \draw[pattern=north west lines, pattern color=brown] (B) -- (M1) -- (E) -- (P1) -- cycle;
   \draw[pattern=north west lines, pattern color=brown] (C) -- (Q1) -- (Q) -- (Q2) -- cycle;
   \draw[pattern=north west lines, pattern color=brown] (D) -- (U1) -- (U) -- (U2) -- cycle;
   
   \draw[thick] (A) -- (B) -- (C) -- (D) -- cycle;
   
   \draw[dashed] (N) -- (U) -- (Q) -- (E) -- cycle;
   \draw[dashed] (N) -- (Q);
   \draw[dashed] (E) -- (U);
   
   \node[above left] at (A) {$A$};
   \node[below left] at (B) {$B$};
   \node[below right] at (C) {$C$};
   \node[above right] at (D) {$D$};
   
   \node[above right=-1pt] at (N) {$N$};
   \node[below right=-1pt] at (E) {$E$};
   \node[below left=-1pt] at (Q) {$Q$};
   \node[above] at (P) {$P$};
   \node[left] at (M) {$M$};
   
   \node[above, text=green!50!black] at (U2) {$I$};
   
  \end{tikzpicture}
\end{center}"""

TIKZ_3D = r"""
\begin{center}
  \begin{tikzpicture}[scale=0.8, font=\footnotesize]
   % Hình chóp cụt sau khi gấp
   \coordinate (A) at (-0.5, 4);
   \coordinate (B) at (5.5, 4);
   \coordinate (C) at (7.5, 6);
   \coordinate (D) at (1.5, 6);
   \coordinate (A1) at (1.5, 0);
   \coordinate (B1) at (4.5, 0);
   \coordinate (C1) at (5.5, 1);
   \coordinate (D1) at (2.5, 1);
   
   % TÔ MÀU
   \fill[blue!15] (A) -- (B) -- (C) -- (D) -- cycle;
   \fill[blue!5] (A) -- (B) -- (B1) -- (A1) -- cycle;
   \fill[blue!10] (B) -- (C) -- (C1) -- (B1) -- cycle;
   
   % VẼ CÁC CẠNH KHUẤT
   \draw[dashed] (D) -- (D1);
   \draw[dashed] (A1) -- (D1) -- (C1);
   
   % VẼ CÁC CẠNH THẤY
   \draw[thick] (A) -- (B) -- (C) -- (D) -- cycle;
   \draw[thick] (A1) -- (B1) -- (C1);
   \draw[thick] (A) -- (A1);
   \draw[thick] (B) -- (B1);
   \draw[thick] (C) -- (C1);
   
   \node[left] at (A) {$A'$};
   \node[right] at (B) {$B'$};
   \node[above right] at (C) {$C'$};
   \node[above left] at (D) {$D'$};
   
   \node[below left] at (A1) {$N$};
   \node[below right] at (B1) {$E$};
   \node[right] at (C1) {$Q$};
   \node[above left] at (D1) {$U$};
   
   % VẼ TRỤC ĐƯỜNG CAO OO'
   \coordinate (O) at (3.5, 5);
   \coordinate (O1) at (3.5, 0.5);
   
   \draw[dashed, gray] (A) -- (C);
   \draw[dashed, gray] (B) -- (D);
   
   \draw[dashed, red, thick] (O) -- (O1);
   \fill[red] (O) circle (1.5pt);
   \node[above, text=red] at (O) {$O$};
   
   \fill[red] (O1) circle (1.5pt);
   \node[below, text=red] at (O1) {$O'$};
   
  \end{tikzpicture}
\end{center}"""

# ── Math helpers ───────────────────────────────────────────────────────────────

def simplify_sqrt(n: int) -> Tuple[int, int]:
    """Return (coeff, rad) such that sqrt(n) = coeff * sqrt(rad), rad square-free."""
    coeff, rad = 1, n
    i = 2
    while i * i <= rad:
        while rad % (i * i) == 0:
            coeff *= i
            rad //= i * i
        i += 1
    return coeff, rad


def format_x_opt_tex(p: int, t: int) -> str:
    """Format x_opt = [(p+4t) + sqrt(disc)] / 10 as simplified LaTeX radical."""
    numer = p + 4 * t
    disc = 21 * p * p + 48 * p * t + 16 * t * t
    sc, sr = simplify_sqrt(disc)
    g = gcd(gcd(numer, sc), 10)
    A, B, D = numer // g, sc // g, 10 // g
    if sr == 1:
        total = A + B
        g2 = gcd(total, D)
        return str(total // g2) if D // g2 == 1 else rf"\frac{{{total // g2}}}{{{D // g2}}}"
    sqrt_tex = rf"\sqrt{{{sr}}}" if B == 1 else rf"{B}\sqrt{{{sr}}}"
    if D == 1:
        return (f"{A}+" if A else "") + sqrt_tex
    if A == 0:
        return rf"\frac{{{sqrt_tex}}}{{{D}}}"
    return rf"\frac{{{A}+{sqrt_tex}}}{{{D}}}"


def format_half(p: int) -> str:
    """Format p/2 for MH' = (p/2)√2 display."""
    return str(p // 2) if p % 2 == 0 else rf"\frac{{{p}}}{{2}}"


def compute_V_max(s: int, t: int) -> Tuple[float, float]:
    """Return (x_opt, V_max) using the closed-form quadratic root."""
    p = s - 2 * t
    # 5x² − (p+4t)x − p(p+2t) = 0
    qb = -(p + 4 * t)
    qc = -p * (p + 2 * t)
    disc = qb * qb - 4 * 5 * qc
    x_opt = (-qb + math.sqrt(disc)) / 10.0
    st = s - t
    h = math.sqrt(t * (st - x_opt))
    V = h / 3.0 * (x_opt ** 2 + p ** 2 + p * x_opt)
    return x_opt, V

# ── Parameter selection ────────────────────────────────────────────────────────

S_POOL = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]   # 10 values
T_POOL = [1, 2, 3]                                 # 3 values


def get_params(seed_val=None) -> Tuple[int, int]:
    if seed_val is not None:
        random.seed(seed_val)
    while True:
        s = random.choice(S_POOL)
        t = random.choice(T_POOL)
        p = s - 2 * t
        # p >= 2: meaningful x range;  s > 4t: interior maximum exists
        if p >= 2 and s > 4 * t:
            return s, t

# ── Question generator ─────────────────────────────────────────────────────────

def generate_question(s: int, t: int) -> Tuple[str, str, str]:
    p   = s - 2 * t
    p2  = p * p
    sp  = s + p
    s2p2 = s * s + p * p
    st  = s - t           # appears in h = √(t(st − x))

    _, V_max = compute_V_max(s, t)
    V_round  = round(V_max)

    x_opt_tex = format_x_opt_tex(p, t)
    half_p    = format_half(p)

    # h formula: √(t(st−x)) — drop coefficient 1 when t=1
    h_tex = rf"\sqrt{{{st}-x}}" if t == 1 else rf"\sqrt{{{t}({st}-x)}}"

    # ── Stem ────────────────────────────────────────────────────────────────
    stem = (
        rf"Từ một tấm nhôm hình vuông có cạnh bằng ${s}$ dm, người ta cắt bỏ bốn tứ giác bằng nhau "
        rf"(cùng bằng tứ giác $AMNP$) ở bốn góc tấm nhôm đó, biết $AM = AP = {t}$ dm và điểm $N$ thuộc "
        rf"đường chéo $AC$. Với phần còn lại của tấm nhôm sau khi đã bỏ đi 4 tứ giác nói trên, người ta đã "
        rf"gập các đoạn $MN$ trùng với $PN$ rồi dán kỹ bằng keo, làm tương tự cho 3 cặp đoạn còn lại, "
        rf"người ta thu được chậu nước hình chóp cụt tứ giác đều. Sức chứa lớn nhất của chậu nước hình chóp "
        rf"cụt tứ giác đều này là bao nhiêu lít (làm tròn đến hàng đơn vị, bỏ qua độ dày tấm nhôm)?"
        + "\n" + TIKZ_FLAT
    )

    # ── Solution (same structure as chau_nuoc.tex, numbers parameterised) ───
    solution = (
        rf"""\textbf{{Lời giải:}}

Ta có: 
$\begin{{cases}} 
NE = x;\; x \in (0;\; {p}) \\ 
PI = {p} 
\end{{cases}} 
\Rightarrow 
\begin{{cases}} 
S_1 = x^2 \\ 
S_2 = {p}^2 = {p2}
\end{{cases}}$

$\Rightarrow NH = \frac{{{s}-x}}{{2}};\; AH = NH$

$\Rightarrow MH = AH - {t} = \frac{{{s}-x}}{{2}} - {t} = \frac{{{p}-x}}{{2}}$

$\Rightarrow MN = \sqrt{{NH^2 + MH^2}} = \frac{{\sqrt{{2x^2 - {2*sp}x + {s2p2}}}}}{{2}}$

$MH' = MO - NO' = {half_p}\sqrt{{2}} - \frac{{x\sqrt{{2}}}}{{2}}$

$\Rightarrow NH' = \sqrt{{MN^2 - MH'^2}} = {h_tex} = h$

Do đó: $V = \frac{{1}}{{3}} \cdot {h_tex} (x^2 + {p2} + {p}x);\quad x \in (0;\; {p})$"""
        + TIKZ_3D
        + rf"""
Cách 1: Casio $\frac{{d}}{{dx}} \approx {V_round}$

Cách 2: KS lập BBT $\Rightarrow V_{{\max}} = V\!\left({x_opt_tex}\right) \approx {V_round}$

Đáp số: $\boxed{{{V_round}}}$ lít."""
    )

    return stem, solution, str(V_round)

# ── Main ───────────────────────────────────────────────────────────────────────

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
        s_val, t_val = get_params(seed + i if seed is not None else None)
        stem, solution, ans = generate_question(s_val, t_val)
        answers.append((s_val, t_val, ans))
        content += (
            f"\\begin{{ex}}%Câu {i+1} (s={s_val}, t={t_val})\n"
            f"{stem}\n\n"
            f"\\shortans{{{ans}}}\n"
            f"\\loigiai{{\n{solution}\n}}\n"
            f"\\end{{ex}}\n\n"
        )

    preamble = (
        r"\documentclass[12pt,a4paper]{article}" + "\n"
        r"\usepackage{amsmath,amssymb,fancyhdr}" + "\n"
        r"\usepackage{polyglossia}" + "\n"
        r"\setdefaultlanguage{vietnamese}" + "\n"
        r"\setmainfont{Times New Roman}" + "\n"
        r"\usepackage{tikz}" + "\n"
        r"\usetikzlibrary{angles,quotes,calc,patterns}" + "\n"
        r"\usepackage{xcolor}" + "\n"
        r"\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}" + "\n"
        r"\usepackage[solcolor]{ex_test}" + "\n"
        r"\newcommand{\heva}[1]{\left\{\begin{aligned}#1\end{aligned}\right.}" + "\n"
    )
    tex_content = preamble + "\n\\begin{document}\n" + content + "\\end{document}\n"

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "aluminum_sheet_frustum_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Generated {num_questions} question(s): {output_file}")
    print("\n=== ANSWERS ===")
    for i, (sv, tv, a) in enumerate(answers):
        print(f"Q{i+1}: s={sv} dm, t={tv} dm  →  {a} lít")


if __name__ == "__main__":
    main()
