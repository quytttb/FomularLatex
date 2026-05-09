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
        # Avoid complex fractions under sqrt
        return rf"\frac{{\sqrt{{{v.numerator * v.denominator}}}}}{{{v.denominator}}}"

def num_tex(v: Fraction):
    if v.denominator == 1:
        return str(v.numerator)
    return f"{float(v):.1f}".replace('.', ',')

def generate_question(seed_val=None) -> Tuple[str, str, str]:
    if seed_val is not None:
        random.seed(seed_val)

    while True:
        z_A = random.randint(3, 20)
        A = (Fraction(0), Fraction(0), Fraction(z_A))
        
        x_B = random.randint(2, 20)
        z_B = random.randint(3, 20)
        B = (Fraction(x_B), Fraction(0), Fraction(z_B))
        
        if z_A == z_B or x_B == 0:
            continue
            
        if abs(z_A - z_B) < 2 or x_B < 3:
            if random.random() > 0.2:
                continue

        alpha_deg = random.choice([120, 135, 150])
        beta_deg = 180 - alpha_deg
        gamma_deg = 2 * beta_deg
            
        dx = B[0] - A[0]
        dz = B[2] - A[2]
        
        AB2 = dx**2 + dz**2
        AB = math.sqrt(float(AB2))

        if alpha_deg == 135:
            R_sq = Fraction(AB2, 2)
            r_form = rf"\frac{{AB}}{{\sqrt{{2}}}} = \frac{{{sqrt_tex(AB2)}}}{{\sqrt{{2}}}}"
            canh_factor = "1"
        elif alpha_deg == 120:
            R_sq = Fraction(AB2, 3)
            r_form = rf"\frac{{AB}}{{\sqrt{{3}}}} = \frac{{{sqrt_tex(AB2)}}}{{\sqrt{{3}}}}"
            canh_factor = "1/sqrt(3)"
        elif alpha_deg == 150:
            R_sq = Fraction(AB2, 1)
            r_form = rf"AB = {sqrt_tex(AB2)}"
            canh_factor = "sqrt(3)"
            
        R = math.sqrt(float(R_sq))
        
        c1 = Fraction(z_A - z_B, x_B)
        c2 = Fraction(x_B**2 - z_A**2 + z_B**2, 2 * x_B)
        
        A_q = c1**2 + 1
        B_q = 2*c1*c2 - 2*z_A
        C_q = c2**2 + z_A**2 - R_sq
        
        delta = B_q**2 - 4*A_q*C_q
        if delta < 0:
            continue
            
        c_i_vals = []
        if delta == 0:
            c_i_vals.append(-B_q / (2*A_q))
        else:
            c_i_vals.append((-B_q - Fraction.from_float(math.sqrt(float(delta))).limit_denominator(100)) / (2*A_q))
            c_i_vals.append((-B_q + Fraction.from_float(math.sqrt(float(delta))).limit_denominator(100)) / (2*A_q))
            
        c_i_vals_valid = [c for c in c_i_vals if c > 0]
        if not c_i_vals_valid:
            continue
        
        c_I = max(c_i_vals_valid)
        a_I = c1 * c_I + c2
        I = (a_I, Fraction(0), c_I)
        
        a_is_true = random.choice([True, False])
        if a_is_true:
            stmt_a_plane = "y = 0"
        else:
            fake_planes = ["x = 0", "x + y = 0", "x - y = 0", "z = 0"]
            stmt_a_plane = random.choice(fake_planes)
            
        stmt_a = rf"{'*' if a_is_true else ''}a) Quỹ đạo bay của chim bói cá thuộc mặt phẳng ${stmt_a_plane}$."
        sol_a = rf"""a) {'Đúng' if a_is_true else 'Sai'}. Mặt phẳng chứa quỹ đạo bay của chim vuông góc với $(Oxy)$ và đi qua $A""" + f"({A[0]}; {A[1]}; {A[2]})$" + r", $B" + f"({B[0]}; {B[1]}; {B[2]})$\n\n" + \
                r"""Mặt phẳng này nhận vecto $\vec{k}(0;0;1)$ và $\overrightarrow{AB}""" + f"{fmt_point((dx, Fraction(0), dz))}$ làm cặp vecto chỉ phương.\n\n" + \
                r"""Véctơ pháp tuyến $\vec{n}_P = [\vec{k}, \overrightarrow{AB}] = (0;""" + f"{x_B}" + r""";0)$, suy ra phương trình mặt phẳng là $y = 0$."""
        
        b_is_true = random.choice([True, False])
        if b_is_true:
            b_point_str = fmt_point_dec(I)
        else:
            fake_a_I = a_I + Fraction(random.choice([-1, 1]))
            fake_c_I = c_I + Fraction(random.choice([-1, 1]))
            b_point_str = fmt_point_dec((fake_a_I, Fraction(0), fake_c_I))
            
        stmt_b = rf"{'*' if b_is_true else ''}b) Đường tròn chứa quỹ đạo bay của chim bói cá có tâm $I{b_point_str}$."
        sol_b = rf"""b) {'Đúng' if b_is_true else 'Sai'}.
Vì tứ giác $AMBN$ nội tiếp nên $\widehat{{ANB}} = 180^\circ - {alpha_deg}^\circ = {beta_deg}^\circ$, dẫn đến góc ở tâm $\widehat{{AIB}} = {gamma_deg}^\circ$ với $I$ là tâm đường tròn.

Bán kính $R = IA = {r_form} = {sqrt_tex(R_sq)}$.

Giả sử $I(a; 0; c)$. Ta có $\heva{{IA^2 &= R^2 \\ IB^2 &= R^2}}$
$\Leftrightarrow \heva{{a^2 + ({z_A}-c)^2 &= {fmt_frac(R_sq)} \\ ({x_B}-a)^2 + ({z_B}-c)^2 &= {fmt_frac(R_sq)}}} \Rightarrow \heva{{a &= {fmt_dec(a_I)} \\ c &= {fmt_dec(c_I)}}}$ (Thỏa mãn do điểm $M(x;0;0)$ nằm dưới $I$, cao độ tâm $I$ phải dương).

Khi đó phương trình đường tròn trong mặt phẳng $(Oxz)$ (với $y=0$) có tâm $I{fmt_point_dec(I)}$, $R = {sqrt_tex(R_sq)}$."""

        KH = float(c_I) - float(R)
        KH_rounded = round(KH, 2)
        KH_str = f"{KH_rounded:.2f}".replace('.', ',')
        
        c_is_true = random.choice([True, False])
        if c_is_true:
            stmt_c_val = KH_str
        else:
            stmt_c_val = f"{round(KH + random.uniform(0.5, 2.0), 2):.2f}".replace('.', ',')
            
        stmt_c = rf"{'*' if c_is_true else ''}c) Khoảng cách ngắn nhất mà chim bói cá bay xuống sát với mặt nước nhất là ${stmt_c_val}$ m (làm tròn đến hàng phần trăm)."
        sol_c = rf"c) {'Đúng' if c_is_true else 'Sai'}. Khoảng cách ngắn nhất đến mặt nước là $KH = d(I, Oxy) - R = {num_tex(c_I)} - {sqrt_tex(R_sq)} \approx {KH_str}$ m."

        vec_IA = (-float(a_I), 0, float(z_A) - float(c_I))
        vec_IK = (0, 0, -float(R))
        
        dot_product = vec_IA[0]*vec_IK[0] + vec_IA[1]*vec_IK[1] + vec_IA[2]*vec_IK[2]
        len_IA = float(R)
        len_IK = float(R)
        
        cos_AIK = dot_product / (len_IA * len_IK)
        
        if cos_AIK > 1 or cos_AIK < -1:
            continue
            
        angle_AIK = math.acos(cos_AIK)
        arc_AK = float(R) * angle_AIK
        
        v = 2.0
        time = arc_AK / v
        time_rounded = round(time, 1)
        time_str = f"{time_rounded:.1f}".replace('.', ',')
        
        d_is_true = random.choice([True, False])
        if d_is_true:
            stmt_d_val = time_str
        else:
            stmt_d_val = f"{round(time + random.uniform(0.5, 1.5), 1):.1f}".replace('.', ',')
        
        stmt_d = rf"{'*' if d_is_true else ''}d) Biết rằng vận tốc của con chim bói cá là $2$ m/s thì thời gian chim bói cá bay từ điểm $A{fmt_point(A)}$ tới điểm gần mặt nước nhất mất ${stmt_d_val}$ s (làm tròn đến hàng phần chục)."
        
        sol_d = rf"""d) {'Đúng' if d_is_true else 'Sai'}. Điểm gần mặt nước nhất là $K$, là điểm thấp nhất của đường tròn cung quỹ đạo rớt thẳng từ tâm $I$ xuống (hoành độ $x = {num_tex(a_I)}$).
Ta có $\cos \widehat{{AIK}} = \frac{{\overrightarrow{{IA}} \cdot \overrightarrow{{IK}}}}{{|IA| \cdot |IK|}} \approx {cos_AIK:.5f} \Rightarrow \widehat{{AIK}} = \arccos ({cos_AIK:.5f})$.

Độ dài quãng đường chim bói cá bay từ $A$ tới $K$ là độ dài cung: $l_{{AK}} = R \cdot \widehat{{AIK}} = {sqrt_tex(R_sq)} \cdot \arccos ({cos_AIK:.5f})$.

Thời gian bay là $t = \frac{{l_{{AK}}}}{{v}} = \frac{{{sqrt_tex(R_sq)} \cdot \arccos ({cos_AIK:.5f})}}{{2}} \approx {time_str}$ s."""

        stem = rf"""Trong không gian $Oxyz$ cho trước với mặt nước phẳng lặng trùng với mặt phẳng $(Oxy)$, đơn vị trên mỗi trục là mét. Một chú chim bói cá đang đậu trên một cành cây ở vị trí $A({A[0]}; {A[1]}; {A[2]})$ tiến hành bay xuống để thám thính ngang qua trên mặt hồ nước đến đậu trên một cành cây khác tại vị trí $B({B[0]}; {B[1]}; {B[2]})$ theo quỹ đạo là một cung tròn hoàn hảo nằm trong mặt phẳng vuông góc với mặt nước đi qua điểm $M$ thỏa mãn $\widehat{{AMB}} = {alpha_deg}^\circ$.

\begin{{center}}
\begin{{tikzpicture}}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
   \def\chim {{(0.12,0.33) .. controls +(-38.25:0.51) and +(-146.6:0.89) .. (1.92,0.64) .. controls +(33.29:1.99) and +(-160.94:2.27) .. (6.96,3.95) .. controls +(17.86:0.24) and +(-167.55:0.25) .. (7.67,3.85) .. controls +(-126.92:0.92) and +(112.06:1.1) .. (8.29,1.44) .. controls +(-146.08:0.16) and +(48.88:0.19) .. (7.24,1.09) .. controls +(7.46:0.48) and +(175.26:0.45) .. (8.57,1.21) .. controls +(-5.93:0.42) and +(169.63:0.51) .. (9.87,1.14) .. controls +(138.43:0.27) and +(-48.66:0.45) .. (8.53,1.64) .. controls +(118.11:0.56) and +(-149.8:0.95) .. (8.35,3.67) .. controls +(-19.29:0.28) and +(173.92:0.36) .. (9.32,3.65) .. controls +(-80.07:1.02) and +(129.41:0.93) .. (11.05,1.54) .. controls +(-105.4:0.25) and +(48.29:0.25) .. (10.18,1.16) .. controls +(14.48:0.43) and +(-169.08:0.29) .. (11.28,1.24) .. controls +(4.61:0.4) and +(172.68:0.69) .. (12.76,1.16) .. controls +(120.55:0.28) and +(-60.73:0.3) .. (11.35,1.59) .. controls +(123.05:0.82) and +(-56.95:0.84) .. (10,3.67) .. controls +(3.37:1.71) and +(-90:2.31) .. (13.31,7.51) .. controls +(68.96:0.7) and +(-173.02:1.24) .. (15.67,8.76) .. controls +(159.67:0.48) and +(-20.32:0.49) .. (14.31,9.26) .. controls +(130.69:1.65) and +(53.89:1.97) .. (10.59,8.35) .. controls +(-173.81:2.21) and +(44.04:3.24) .. (4.31,4.32) .. controls +(0.41:0.33) and +(-167.56:0.24) .. (4.91,4.22) .. controls +(-138.51:1.99) and +(39.26:2.28) .. (0.12,0.33);}}
   \def\ca{{(0.78,6.15) .. controls +(-158.78:1.32) and +(172.67:1.47) .. (0.92,4.67) .. controls +(-18.16:0.63) and +(128.83:0.76) .. (2.73,4.08) .. controls +(-119.54:1) and +(137.55:0.92) .. (2.67,1.42) .. controls +(54.61:0.67) and +(-150.71:0.68) .. (3.83,3.15) .. controls +(21.04:0.4) and +(-117.98:0.52) .. (4.87,3.99) .. controls +(-78.11:0.28) and +(120.95:0.25) .. (5.26,3.27) .. controls +(-166.22:0.79) and +(-169.54:0.96) .. (4.49,2.02) .. controls +(-93.47:2.39) and +(-157.98:1.39) .. (6.36,2.7) .. controls +(-4.66:0.18) and +(175.38:0.18) .. (6.9,2.66) .. controls +(-93.58:0.23) and +(120.06:0.32) .. (6.69,2.01) .. controls +(-3.94:0.42) and +(-99.21:0.54) .. (7.72,2.78) .. controls +(5.81:0.86) and +(-108.43:1.14) .. (10.21,4.27) .. controls +(91.25:0.67) and +(-6.74:1.35) .. (7.47,6.49) .. controls +(96.48:0.64) and +(-2.05:0.81) .. (5.58,8.3) .. controls +(-161.55:0.23) and +(90:0.45) .. (5.45,6.88) .. controls +(-113.2:0.44) and +(68.5:0.51) .. (4.48,5.96) .. controls +(-109.29:0.31) and +(127.87:0.33) .. (4.64,5.1) .. controls +(-139.39:0.27) and +(-45:0.92) .. (2.93,5.78) .. controls +(146.56:0.92) and +(12.53:1.33) .. (-0.06,6.99) .. controls +(-96.33:0.26) and +(147.99:0.41) .. (0.78,6.15);}}
   
   \draw[dashed,color=red!70!black,line width=1pt] (0,0)coordinate (A_plane)--++(3,3)coordinate (B_plane);
   \draw[dashed,color=red!70!black,line width=1pt] (4,0)coordinate (D_plane)--++(3,3)coordinate (C_plane);
   \draw[color=red!70!black,line width=1pt] ($(A_plane)!0.3!(B_plane)$) --++(0,4)coordinate (X);
   \draw[color=red!70!black,line width=1pt] ($(D_plane)!0.5!(C_plane)$) --++(0,2)coordinate (Y);
   \draw[dashed,color=red!70!black,line width=1pt,
   postaction={{
    decorate,
    decoration={{
     markings,
     mark=at position 0.3 with {{\coordinate (M_point);}}
    }}
   }}
   ] (X) .. controls +(-70:3) and +(-140:2) .. (Y);
   
   \fill (M_point) circle(1.5pt)node[below]{{$M$}};
   \draw[xshift=-0.5cm,yshift=5cm,fill=black,scale=0.1] \chim;
   \draw[xscale=-1,xshift=-6.5cm,yshift=3.5cm,fill=black,scale=0.1] \chim;
   \draw[xshift=2cm,yshift=1cm,fill=cyan,scale=0.1] \ca;
   \draw[xshift=4.5cm,yshift=1cm,fill=cyan,xscale=-1,scale=0.1] \ca;

  \draw ($(A_plane)!0.3!(B_plane)$)coordinate (X') --++(0,4)coordinate (X);
  \draw ($(D_plane)!0.5!(C_plane)$)coordinate (Y') --++(0,2)coordinate (Y);
 
\path let \p1 = (X), \p2 = (Y) in \pgfextra{{\pgfmathparse{{veclen(\x1-\x2,\y1-\y2)/28.45274}}\xdef\dodai{{\pgfmathresult}}}};
\pgfmathparse{{\dodai}}\let\dodaiNum\pgfmathresult

\pgfmathsetmacro{{\canh}}{{\dodai/2}}
\draw ($(X)!0.5!(Y)$) coordinate (tam) ($(tam)!\canh cm!-90:(X)$) coordinate (tamvuong);

\pgfmathsetmacro{{\r}}{{sqrt(\dodaiNum*\dodaiNum/4 + \canh*\canh)}}

\path 
(X) coordinate (A_v)
(Y) coordinate (B_v)
($(100:\r)+(tamvuong)$)coordinate (N_v)
($(-120:\r)+(tamvuong)$)coordinate (M_v)
(tamvuong) coordinate (I_v)
;

\foreach \p/\r in {{A_v/-140,B_v/-40}}
\fill (\p) circle (1.2pt) node[shift={{(\r:3mm)}}]{{$\p$}};
\draw (X')--(Y');
\end{{tikzpicture}}
\end{{center}}"""

        question = f"{stem}\n\n{stmt_a}\n\n{stmt_b}\n\n{stmt_c}\n\n{stmt_d}"
        
        sol_stem = rf"""\begin{{center}}
\begin{{tikzpicture}}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
  \def\chim {{(0.12,0.33) .. controls +(-38.25:0.51) and +(-146.6:0.89) .. (1.92,0.64) .. controls +(33.29:1.99) and +(-160.94:2.27) .. (6.96,3.95) .. controls +(17.86:0.24) and +(-167.55:0.25) .. (7.67,3.85) .. controls +(-126.92:0.92) and +(112.06:1.1) .. (8.29,1.44) .. controls +(-146.08:0.16) and +(48.88:0.19) .. (7.24,1.09) .. controls +(7.46:0.48) and +(175.26:0.45) .. (8.57,1.21) .. controls +(-5.93:0.42) and +(169.63:0.51) .. (9.87,1.14) .. controls +(138.43:0.27) and +(-48.66:0.45) .. (8.53,1.64) .. controls +(118.11:0.56) and +(-149.8:0.95) .. (8.35,3.67) .. controls +(-19.29:0.28) and +(173.92:0.36) .. (9.32,3.65) .. controls +(-80.07:1.02) and +(129.41:0.93) .. (11.05,1.54) .. controls +(-105.4:0.25) and +(48.29:0.25) .. (10.18,1.16) .. controls +(14.48:0.43) and +(-169.08:0.29) .. (11.28,1.24) .. controls +(4.61:0.4) and +(172.68:0.69) .. (12.76,1.16) .. controls +(120.55:0.28) and +(-60.73:0.3) .. (11.35,1.59) .. controls +(123.05:0.82) and +(-56.95:0.84) .. (10,3.67) .. controls +(3.37:1.71) and +(-90:2.31) .. (13.31,7.51) .. controls +(68.96:0.7) and +(-173.02:1.24) .. (15.67,8.76) .. controls +(159.67:0.48) and +(-20.32:0.49) .. (14.31,9.26) .. controls +(130.69:1.65) and +(53.89:1.97) .. (10.59,8.35) .. controls +(-173.81:2.21) and +(44.04:3.24) .. (4.31,4.32) .. controls +(0.41:0.33) and +(-167.56:0.24) .. (4.91,4.22) .. controls +(-138.51:1.99) and +(39.26:2.28) .. (0.12,0.33);}}
  \def\ca{{(0.78,6.15) .. controls +(-158.78:1.32) and +(172.67:1.47) .. (0.92,4.67) .. controls +(-18.16:0.63) and +(128.83:0.76) .. (2.73,4.08) .. controls +(-119.54:1) and +(137.55:0.92) .. (2.67,1.42) .. controls +(54.61:0.67) and +(-150.71:0.68) .. (3.83,3.15) .. controls +(21.04:0.4) and +(-117.98:0.52) .. (4.87,3.99) .. controls +(-78.11:0.28) and +(120.95:0.25) .. (5.26,3.27) .. controls +(-166.22:0.79) and +(-169.54:0.96) .. (4.49,2.02) .. controls +(-93.47:2.39) and +(-157.98:1.39) .. (6.36,2.7) .. controls +(-4.66:0.18) and +(175.38:0.18) .. (6.9,2.66) .. controls +(-93.58:0.23) and +(120.06:0.32) .. (6.69,2.01) .. controls +(-3.94:0.42) and +(-99.21:0.54) .. (7.72,2.78) .. controls +(5.81:0.86) and +(-108.43:1.14) .. (10.21,4.27) .. controls +(91.25:0.67) and +(-6.74:1.35) .. (7.47,6.49) .. controls +(96.48:0.64) and +(-2.05:0.81) .. (5.58,8.3) .. controls +(-161.55:0.23) and +(90:0.45) .. (5.45,6.88) .. controls +(-113.2:0.44) and +(68.5:0.51) .. (4.48,5.96) .. controls +(-109.29:0.31) and +(127.87:0.33) .. (4.64,5.1) .. controls +(-139.39:0.27) and +(-45:0.92) .. (2.93,5.78) .. controls +(146.56:0.92) and +(12.53:1.33) .. (-0.06,6.99) .. controls +(-96.33:0.26) and +(147.99:0.41) .. (0.78,6.15);}}
  
  \draw[dashed,color=red!70!black,line width=1pt] (0,0)coordinate (A_plane)--++(3,3)coordinate (B_plane);
  \draw[dashed,color=red!70!black,line width=1pt] (4,0)coordinate (D_plane)--++(3,3)coordinate (C_plane);
  \draw ($(A_plane)!0.3!(B_plane)$)coordinate (X') --++(0,4)coordinate (X);
  \draw ($(D_plane)!0.5!(C_plane)$)coordinate (Y') --++(0,2)coordinate (Y);
 
\path let \p1 = (X), \p2 = (Y) in \pgfextra{{\pgfmathparse{{veclen(\x1-\x2,\y1-\y2)/28.45274}}\xdef\dodai{{\pgfmathresult}}}};
\pgfmathparse{{\dodai}}\let\dodaiNum\pgfmathresult

\pgfmathsetmacro{{\canh}}{{\dodai/2}}
\draw ($(X)!0.5!(Y)$) coordinate (tam) ($(tam)!\canh cm!-90:(X)$) coordinate (tamvuong);
\draw (X)--(tamvuong)--(Y);

\pgfmathsetmacro{{\r}}{{sqrt(\dodaiNum*\dodaiNum/4 + \canh*\canh)}}

\path (X) coordinate (A_v) (Y) coordinate (B_v) ($(100:\r)+(tamvuong)$)coordinate (N_v) ($(-120:\r)+(tamvuong)$)coordinate (M_v) (tamvuong) coordinate (I_v) ($(I_v)+(X')-(A_v)$)coordinate (I') (intersection of I_v--I' and X'--Y') coordinate (H_v);

\draw[name path=duongmot,dashed] (tamvuong) circle(\r);
\draw[name path=duonghai] (I_v)--(H_v);
\draw[name intersections={{of=duongmot and duonghai,by=K_v}}];

\draw pic[draw,angle radius=5mm] {{angle = B_v--M_v--A_v}}; 
\draw ($(M_v)+(75:8mm)$) node[]{{${alpha_deg}^\circ$}};
\draw pic[draw,angle radius=5mm] {{angle = A_v--N_v--B_v}}; 
\draw ($(N_v)+(-95:5mm)$) node[below]{{${beta_deg}^\circ$}};

\foreach \p/\r in {{A_v/-140,B_v/-40,N_v/90,M_v/-120,I_v/90,H_v/-90,K_v/40}}
\fill (\p) circle (1.2pt) node[shift={{(\r:3mm)}}]{{$\p$}};
\draw (N_v)--(A_v)--(M_v)--(B_v)--(N_v) (X')--(Y') (I_v)--(H_v);

  \draw[xshift=-0.5cm,yshift=5cm,fill=black,scale=0.1,] \chim;
  \draw[xscale=-1,xshift=-6.5cm,yshift=3.5cm,fill=black,scale=0.08,] \chim;
  \draw[xshift=2cm,yshift=1.1cm,fill=cyan,scale=0.1] \ca;
  \draw[xshift=5cm,yshift=1.5cm,fill=cyan,xscale=-1,scale=0.1] \ca;
\end{{tikzpicture}}
\end{{center}}"""

        solution = f"{sol_stem}\n\n{sol_a}\n\n{sol_b}\n\n{sol_c}\n\n{sol_d}"

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
\usetikzlibrary{calc,angles,quotes,decorations.markings,intersections}

\newcommand{\heva}[1]{\left\{\begin{aligned}#1\end{aligned}\right.}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)
    # Fix the missing decoration error
    tex_content = tex_content.replace("\\usetikzlibrary{calc,angles,quotes,decorations.markings,intersections}", "\\usetikzlibrary{calc,angles,quotes,decorations.markings,intersections,patterns,shapes.geometric}")
    
    # Due to naming issues A vs A_v
    tex_content = tex_content.replace(r"A_v/-140", "A/-140").replace(r"B_v/-40", "B/-40").replace(r"N_v/90", "N/90").replace(r"M_v/-120", "M/-120").replace(r"I_v/90", "I/90").replace(r"H_v/-90", "H/-90").replace(r"K_v/40", "K/40")
    tex_content = tex_content.replace("M_v", "M").replace("A_v", "A").replace("B_v", "B").replace("N_v", "N").replace("I_v", "I").replace("H_v", "H").replace("K_v", "K")

    out_path = os.path.join(out_dir, "cau_6_questions.tex")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {out_path}")
    print("\n=== ĐÁP ÁN ===")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: Đáp án: {k}")

if __name__ == "__main__":
    main()
