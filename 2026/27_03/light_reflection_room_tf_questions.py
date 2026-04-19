"""
True/false question: light reflection in a rectangular room (Oxyz).
"""
import os
import sys
import math
import random
from fractions import Fraction
from typing import Tuple

def fmt(v):
    if isinstance(v, float):
        return str(int(v)) if v.is_integer() else str(v).replace('.', '{,}')
    return str(v)

def fmt_frac(f):
    if isinstance(f, Fraction):
        if f.denominator == 1: return str(f.numerator)
        return f"\\dfrac{{{f.numerator}}}{{{f.denominator}}}"
    return str(f)

# Hai hình: (trái) nguyên lí phản xạ 2D; (phải) phòng Oxyz theo đề — chiếu song song.
TIKZ_FIGURES = r"""
\begin{center}
\setlength{\tabcolsep}{8pt}
\begin{tabular}{@{}c@{\hspace{0.6cm}}c@{}}
\begin{tikzpicture}[scale=1.02, font=\footnotesize, line join=round, line cap=round,
  >=stealth, line width=0.75pt]
  \coordinate (Ii) at (0,0);
  \coordinate (Ss) at (-1.48,1.42);
  \coordinate (Rr) at (1.42,1.38);
  \coordinate (Nn) at (0,1.22);
  \fill[pattern=north east lines, pattern color=black!32] (-2.55,-0.42) rectangle (2.55,0);
  \draw[thick] (-2.55,0) -- (2.55,0);
  \draw[densely dashed] (Ii) -- (Nn) node[above=1pt] {$N$};
  \draw[->, thick] (Ss) -- (Ii);
  \node[above left=0pt, inner sep=1pt] at (Ss) {$S$};
  \draw[->, thick] (Ii) -- (Rr);
  \node[above right=0pt, inner sep=1pt] at (Rr) {$R$};
  \fill (Ii) circle (1.3pt) node[below=2pt] {$I$};
  \draw[thin] (Ii) ++(136:0.5) arc (136:90:0.5);
  \node[font=\scriptsize, inner sep=0.5pt] at (-0.28,0.28) {$i$};
  \draw[thin] (Ii) ++(90:0.42) arc (90:44:0.42);
  \node[font=\scriptsize, inner sep=0.5pt] at (0.28,0.28) {$i'$};
\end{tikzpicture}
&
\begin{tikzpicture}[scale=0.6, >=stealth, line join=round, line cap=round,
  x={(-0.5cm,-0.4cm)}, y={(0.8cm,0cm)}, z={(0cm,0.8cm)},
  font=\footnotesize, line width=0.7pt]
  \coordinate (O) at (0,0,0);
  \coordinate (C) at (5,0,0);
  \coordinate (D) at (0,6,0);
  \coordinate (F) at (0,0,4);
  \coordinate (N) at (5,6,0);
  \coordinate (G) at (5,0,4);
  \coordinate (K) at (0,6,4);
  \coordinate (A) at (5,1,0); 
  \coordinate (M) at (2.2,0,0);
  \coordinate (E) at (2.2,0,1.5);
  \coordinate (B) at (0,2.2,2.4);
  \coordinate (H) at (0,2.2,0);

  % Axes
  \draw[->] (O) -- (7,0,0) node[below] {$x$};
  \draw[->] (O) -- (0,8,0) node[above] {$y$};
  \draw[->] (O) -- (0,0,5.5) node[right] {$z$};

  % Walls
  \draw (C) -- (G) -- (F);
  \draw (F) -- (K) -- (D);
  \draw (C) -- (N) -- (D);

  % Mirror (ellipse rotated 25 degrees to match perspective of the xOz wall)
  \fill[black!20, rotate around={25:(E)}] (E) ellipse [x radius=0.6cm, y radius=0.3cm];
  \draw[black!70, rotate around={25:(E)}] (E) ellipse [x radius=0.6cm, y radius=0.3cm];

  % Lines and Rays
  \draw (A) -- (E) -- (B); 
  \draw (M) -- (E); % Projection on left wall
  \draw (B) -- (H); % Projection on right wall

  % Points
  \foreach \p in {O,C,D,F,N,G,K,A,M,E,B,H} {
    \fill (\p) circle (1.2pt);
  }
  
  % Labels with exact positioning matching the original figure
  \node[anchor=north west, inner sep=2pt] at (O) {$O$};
  \node[anchor=east, inner sep=2pt] at (C) {$C$}; 
  \node[anchor=north, inner sep=2pt] at (D) {$D$}; 
  \node[anchor=north west, inner sep=2pt] at (F) {$F$};
  \node[anchor=north, inner sep=2pt] at (N) {$N$};
  \node[anchor=east, inner sep=2pt] at (G) {$G$};
  \node[anchor=south west, inner sep=2pt] at (K) {$K$};
  \node[anchor=north, inner sep=2pt] at (A) {$A$};
  \node[anchor=north west, inner sep=2pt, xshift=-2pt] at (M) {$M$};
  \node[anchor=south east, inner sep=2pt] at (E) {$E$};
  \node[anchor=south west, inner sep=2pt] at (B) {$B$};
  \node[anchor=north, inner sep=2pt] at (H) {$H$};
\end{tikzpicture}
\end{tabular}
\end{center}
"""

def gcd(a, b): return math.gcd(a, b)

def generate_question() -> Tuple[str, str, str]:
    # 1. Random values ensuring nice numerical output later
    dx = random.choice([1, 2, 4])
    OM = random.randint(2, 5)
    OC = OM + dx
    CA = random.randint(1, 4)
    EM_val = int(random.choice([1, 2, 3, 4]))
    
    y0_frac = Fraction(OM * CA, dx)
    z0_frac = Fraction(OC * EM_val, dx)

    H_room = max(4, int(math.ceil(float(y0_frac))) + random.randint(1, 3), 
                 int(math.ceil(float(z0_frac))) + random.randint(1, 3))
    OD = OF = H_room

    is_a_true = random.choice([True, False])
    is_b_true = random.choice([True, False])
    is_c_true = random.choice([True, False])
    is_d_true = random.choice([True, False])

    # Prefix marks
    pref_a = "*a)" if is_a_true else "a)"
    pref_b = "*b)" if is_b_true else "b)"
    pref_c = "*c)" if is_c_true else "c)"
    pref_d = "*d)" if is_d_true else "d)"

    # Statement a: Plane ACE
    n_x, n_y, n_z = CA * EM_val, 0, CA * dx
    A_p, C_p = n_x, n_z
    D_p = -(n_x * OC)
    
    g_p = gcd(gcd(abs(A_p), abs(C_p)), abs(D_p))
    A_p //= g_p; C_p //= g_p; D_p //= g_p

    D_p_disp = D_p if is_a_true else D_p + random.choice([-2, 2, 4])
    if not is_a_true and D_p_disp == D_p: D_p_disp += 1

    sign_c_str = "+" if C_p > 0 else "-"
    c_abs = abs(C_p)
    term_c_disp = f"{sign_c_str} {c_abs}z" if (C_p != 0 and c_abs != 1) else (f"{sign_c_str} z" if C_p != 0 else "")
    
    plane_eq_stmt = f"{A_p}x {term_c_disp}"
    if D_p_disp != 0: plane_eq_stmt += f" {'+' if D_p_disp > 0 else '-'} {abs(D_p_disp)}"
    plane_eq_stmt += " = 0"

    plane_eq_real = f"{A_p}x {term_c_disp}"
    if D_p != 0: plane_eq_real += f" {'+' if D_p > 0 else '-'} {abs(D_p)}"
    plane_eq_real += " = 0"

    # Statement b: Point J on AE
    u_x, u_y, u_z = -dx, -CA, EM_val
    g_u = gcd(gcd(abs(u_x), abs(u_y)), abs(u_z))
    u_x //= g_u; u_y //= g_u; u_z //= g_u
    if u_x > 0:
        u_x, u_y, u_z = -u_x, -u_y, -u_z

    t = random.choice([1, 2])
    Jx = OC + t * u_x
    Jy = CA + t * u_y
    Jz = t * u_z
    if not is_b_true:
        Jx += random.choice([1, -1])
        Jy += random.choice([1, -1])

    # Statement c: Angle
    sum_sq = dx**2 + CA**2 + EM_val**2
    sin_val = CA / math.sqrt(sum_sq)
    angle = math.degrees(math.asin(sin_val))
    angle_round = round(angle)
    disp_angle = angle_round if is_c_true else angle_round + random.choice([5, -5, 10])

    # Statement d: Intersection B
    found = False
    for c1 in range(1, 6):
        for c2 in range(1, 6):
            if (c1 * y0_frac + c2 * z0_frac).denominator == 1:
                coeff1, coeff2 = c1, c2
                found = True
                break
        if found: break
    if not found:
        coeff1, coeff2 = dx, 2 * dx
    
    true_V = int(coeff1 * y0_frac + coeff2 * z0_frac)
    disp_V = true_V if is_d_true else true_V + random.choice([2, -2, 3])

    c1_str = f"{coeff1}" if coeff1 > 1 else ""
    c2_str = f"{coeff2}" if coeff2 > 1 else ""
    d_expr = f"{c1_str}y_0 + {c2_str}z_0"

    # Assemble Stem
    EM_fmt = fmt(EM_val)
    stem = (
        f"Nguyên lí phản xạ ánh sáng: Khi ánh sáng bị phản xạ, tia phản xạ nằm trong mặt phẳng chứa tia tới và pháp tuyến của gương tại điểm tới; góc phản xạ bằng góc tới ($i=i'$) (hình bên trái).\n\n"
        f"Chú ý: Đối xứng tia $SI$ qua gương thì tia $IS'$ là tia đối của tia $IR$.\n\n"
        f"Trong căn phòng dạng hình hộp chữ nhật, có gương phẳng tròn tâm $E$ (độ dày không đáng kể), treo trên tường mặt phẳng $(FOC)$. "
        f"Biết $OCGF$, $OCND$, $OFKD$ là các hình chữ nhật; $OC = {OC}\\text{{ m}}$; $OD = OF = {OD}\\text{{ m}}$; "
        f"$OM = {OM}\\text{{ m}}$; $EM = {EM_fmt}\\text{{ m}}$; $CA = {CA}\\text{{ m}}$. Một tia sáng chiếu từ $A$ tới $E$, phản xạ trên gương tới điểm $B$ trên tường (tham khảo hình bên phải). Chọn hệ trục $Oxyz$ như hình, mỗi đơn vị dài $1\\text{{ m}}$.\n"
        + TIKZ_FIGURES
    )

    stmt_a = f"{pref_a} Phương trình mặt phẳng $(ACE)$ là ${plane_eq_stmt}$."
    stmt_b = f"{pref_b} Đường thẳng $AE$ đi qua điểm $J({Jx}; {Jy}; {Jz})$."
    stmt_c = f"{pref_c} Gọi $(d)$ là đường thẳng đối xứng với đường thẳng $AE$ qua mặt phẳng $(OCGF)$. Góc giữa đường thẳng $(d)$ và mặt phẳng $(OCGF)$ là ${disp_angle}^\\circ$ (kết quả làm tròn đến hàng đơn vị)."
    stmt_d = f"{pref_d} Gọi tọa độ điểm $B$ là $B(x_0; y_0; z_0)$ thì ${d_expr} = {disp_V}$."

    question = f"{stem}\n\n{stmt_a}\n\n{stmt_b}\n\n{stmt_c}\n\n{stmt_d}"

    # Solution Generation
    c_a_res = 'Đúng' if is_a_true else 'Sai'
    c_b_res = 'Đúng' if is_b_true else 'Sai'
    c_c_res = 'Đúng' if is_c_true else 'Sai'
    c_d_res = 'Đúng' if is_d_true else 'Sai'
    
    # Format A'E vector identically to u_x,u_y,u_z
    v_ap_x, v_ap_y, v_ap_z = -dx, CA, EM_val
    g_ap = gcd(gcd(abs(v_ap_x), abs(v_ap_y)), abs(v_ap_z))
    v_ap_x //= g_ap; v_ap_y //= g_ap; v_ap_z //= g_ap
    if v_ap_x > 0:
        v_ap_x, v_ap_y, v_ap_z = -v_ap_x, -v_ap_y, -v_ap_z

    solution = f"""Ta có $O(0;0;0)$, $A({OC};{CA};0)$, $C({OC};0;0)$, $D(0;{OD};0)$, $E({OM};0;{EM_fmt})$, $F(0;0;{OF})$, $M({OM};0;0)$.

$\\overrightarrow{{CA}} = (0;{CA};0)$, $\\overrightarrow{{CE}} = ({-dx};0;{EM_fmt})$, $[\\overrightarrow{{CA}},\\overrightarrow{{CE}}] = ({fmt(n_x)};0;{fmt(n_z)})$.

Phương trình mặt phẳng $(ACE)$: ${plane_eq_real}$. Vậy ý a) {c_a_res}.

$\\overrightarrow{{AE}} = ({-dx};{-CA};{EM_fmt})$ là một vectơ chỉ phương của đường thẳng $AE$. Phương trình đường thẳng $AE$: $\\dfrac{{x-{OC}}}{{{u_x}}} = \\dfrac{{y-{CA}}}{{{u_y}}} = \\dfrac{{z}}{{{u_z}}}$. Thay tọa độ điểm $J({Jx};{Jy};{Jz})$ vào phương trình lúc nãy {'ta thấy thỏa mãn' if is_b_true else 'kiểm tra không thỏa mãn'}. Vậy ý b) {c_b_res}.

Do đường thẳng $(d)$ đối xứng với đường thẳng $AE$ qua mặt phẳng $(OCGF)$ nên góc giữa $(d)$ và $(OCGF)$ bằng góc giữa $AE$ và $(OCGF)$.
Pháp tuyến của mặt phẳng $y=0$ là $\\vec{{n}} = (0;1;0)$, $\\overrightarrow{{AE}} = ({-dx};{-CA};{EM_fmt})$,
$$\\sin\\left(AE,(OCGF)\\right) = \\dfrac{{|\\vec{{n}} \\cdot \\overrightarrow{{AE}}|}}{{|\\vec{{n}}|\\,|\\overrightarrow{{AE}}|}} = \\dfrac{{{CA}}}{{\\sqrt{{{int(sum_sq)}}}}} \\Rightarrow \\left(AE,(OCGF)\\right) \\approx {angle_round}^\\circ.$$
Vậy ý c) {c_c_res}.

Tia $AE$ nằm trong mặt phẳng $(ACE)$ vuông góc với mặt phẳng chứa gương. Khi đó tia $EB$ thuộc mặt phẳng $(ACE)$.
Gọi $A'$ là điểm đối xứng với $A$ qua $C$, ta có $A'$ thuộc đường thẳng $EB$, đồng thời có tọa độ $A'({OC};{-CA};0)$.
Khi đó $\\overrightarrow{{A'E}} = ({-dx};{CA};{EM_fmt})$. Phương trình đường thẳng $A'E$: $\\dfrac{{x-{OC}}}{{{v_ap_x}}} = \\dfrac{{y+{CA}}}{{{v_ap_y}}} = \\dfrac{{z}}{{{v_ap_z}}}$.

Do $B$ là giao điểm của $A'E$ và mặt phẳng $(Oyz)$ ($x=0$) nên toạ độ điểm $B\\left(0; {fmt_frac(y0_frac)}; {fmt_frac(z0_frac)}\\right)$.
Vậy ta có ${d_expr} = {true_V}$. Vậy ý d) {c_d_res}.
"""

    key = f"{c_a_res[0]}, {c_b_res[0]}, {c_c_res[0]}, {c_d_res[0]}"
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
        content += f"\\begin{{ex}}%Câu {i+1}\n{q}\n\\loigiai{{\n{s}\n}}\n\\end{{ex}}\n\n"

    tex_content = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage{{amsmath,amssymb,fancyhdr}}
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
    output_file = os.path.join(out_dir, "light_reflection_room_tf_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")

if __name__ == "__main__":
    random.seed()
    main()
