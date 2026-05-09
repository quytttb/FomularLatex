import math
import os
import sys
import random
from fractions import Fraction
from typing import Tuple

CONTEXTS = [
    {
        "space": r"Trung tâm TED",
        "A_desc": r"học sinh học tập",
        "S_desc": r"mái nhà",
        "I_desc": r"hộp điện",
        "plane_desc": r"mặt phẳng",
    }
]

def fmt_point(p):
    p0 = int(p[0]) if isinstance(p[0], (int, float)) and float(p[0]).is_integer() else p[0]
    p1 = int(p[1]) if isinstance(p[1], (int, float)) and float(p[1]).is_integer() else p[1]
    p2 = int(p[2]) if isinstance(p[2], (int, float)) and float(p[2]).is_integer() else p[2]
    return f"({p0}; {p1}; {p2})"

def generate_question(context_idx=None) -> Tuple[str, str, str]:
    if context_idx is None:
        context = random.choice(CONTEXTS)
    else:
        context = CONTEXTS[context_idx % len(CONTEXTS)]
        
    z0 = random.choice([2, 4])
    a = random.choice([2, 4, 6])
    x0 = random.choice([4, 6, 8])
    y0 = random.choice([4, 6, 8])
    
    A = (x0, y0, z0)
    B = (x0, y0 + a, z0)
    C = (x0 - a, y0 + a, z0)
    D = (x0 - a, y0, z0)
    
    h = random.choice([2, 3, 4])
    Ox, Oy = x0 - a/2, y0 + a/2
    S_correct_pt = (Ox, Oy, z0 + h)
    
    Tx = random.choice([-8, -6, -4])
    Ty = random.choice([-8, -6, -4])
    Th = random.choice([8, 10, 12])
    
    v1 = random.choice([1.5, 2.0, 2.5])
    v2 = random.choice([3.0, 4.0, 4.5])
    M_dist = 0.5
    
    stem = rf'''Trung tâm TED mới xây một ngôi nhà mới để cho học sinh học tập trải nghiệm có mái nhà là hình chóp tứ giác đều $S.ABCD$ có chiều cao là {h} mét. Trong hệ tọa độ $Oxyz$ (đơn vị đo trên các trục tính bằng mét), với các điểm ở đáy là $A{fmt_point(A)}$, $B{fmt_point(B)}$, $C{fmt_point(C)}$, $D{fmt_point(D)}$ và $S$ là đỉnh của mái nhà. Xét tính đúng/sai của các mệnh đề sau:''' + r'''

\begin{center}
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
   \coordinate (S') at (-1.8,3.9);
   \coordinate (B') at (-3.2,-1.9);
   \coordinate (C') at (-0.7,0.7);
   \coordinate (D) at (3.2,-0.2);
   \coordinate (P11) at (4.1,-3.0);
   \coordinate (P15) at (7.0,-2.8);
   \coordinate (L) at (7.0,-0.4);
   \coordinate (L1) at (7.0,2);
   \coordinate (O) at (1,0.0);
   \coordinate (x) at (-2,-3.3);
   \coordinate (y) at (9.5,-0.0);
   \coordinate (z) at (01,5.0);
   \coordinate (C) at ($(L)!0.1!(C')$);
   \coordinate (B) at ($(L)!0.285!(B')+(0,-1)$);
   \coordinate (S) at ($(L)!0.374!(S')$);
   \coordinate (A) at ($(B) + (D) - (C)$);
   \coordinate (D12) at ($(A) + (P11) - (B)$);
   \coordinate (D13) at ($(P11) + (C) - (B)$);
   \coordinate (D14) at ($(D12) + (D13) - (P11)$);
   \coordinate (O') at ($(A)!1/2!(C)$);
   
   \draw[black] (S) -- (C) -- (D13) coordinate (C') -- (P11) coordinate (B')-- (D12) coordinate (A')-- (A) -- (S);
   %%%%%%%%%%%%%%%%%
   \draw[black] (A) -- (B) -- (C) (S)--(B) (B) -- (P11);
   %%%%%%%%%%%%%%%%%
   \draw[black,dashed] (A) -- (D) -- (C);
   %%%%%%%%%%%%%%%%%
   \draw[black,dashed] (D12) -- (D14) -- (D13);
   %%%%%%%%%%%%%%%%%
   \draw[black,dashed] (D14)coordinate (D') -- (D) -- (S);
   %%%%%%%%%%%%%%%%%
   % \draw[black,line width=4pt] (L1) -- (P15);
   %%%%%%%%%%%%%%%%%
   \draw[dashed] (O')--($(O')!0.2!(L1)+(0,0.75)$);
   \draw  
   ($(O')!0.2!(L1)+(0,0.75)$)--(8,2)
   (O') coordinate (I) ;
   \begin{scope}[red,line width=0.6pt]
    \draw[dashed] (I) -- ($(D)!0.1!(C)$) coordinate (M)-- ($(D)!0.6!(A)$) --($(D')!1/2!(A')$)
    --($(B')!1/2!(A')$)
    ($(B)!0.2!(A)$)--($(B)!0.2!(C)$)
    ($(B')!1/2!(C')$)--($(D')!0.75!(C')$)
    --($(D)!0.1!(C)$)
    ;
    \draw ($(B')!1/2!(A')$)--($(B)!0.2!(A)$)
    ($(B)!0.2!(C)$)--($(B')!1/2!(C')$)
    ;
   \end{scope}
   \foreach \p/\r in {A/180,B/-40,C/-45,S/90,D/140,I/0,M/60}
   \fill (\p) circle (1.2pt) node[shift={(\r:3mm)}]{$\p$};
   \tikzset{
    thong/.pic={ 
     \begin{scope}[transparency group, opacity=0.1]
      \fill[black, shift={(0.1,-0.1)}] (1,-2)--(-1,-2)--(-1.2,-1)--(-0.8,-1)--(-0.8,-0.2) to [bend left =30] (-3.1,-0.5)--(-2.6,-0.2) to [bend left =15] (-4,0) to [bend right =20] (-2.25,1.25) to [bend left =10] (-3.5,1.4) to [bend right =20] (-1.3,3) to [bend left =15] (-2,2.8)to [bend right =10] (0,5) to [bend right =10] (2,2.2) to [bend left =15] (1.3,3) to [bend right =20] (3.5,1.4) to [bend left =10] (2.25,1.25) to [bend right =20] (4,0) to [bend left =15] (2.6,-0.2) --(3.1,-0.5) to [bend left =30] (0.8,-0.2)--(0.8,-1)--(1.2,-1)--(1,-2);
     \end{scope}
     \shade[left color=green!40!black, right color=green!40!black, middle color=green!60!yellow]
     (1,-2)--(-1,-2)--(-1.2,-1)--(-0.8,-1)--(-0.8,-0.2) to [bend left =30] (-3.1,-0.5)--(-2.6,-0.2) to [bend left =15] (-4,0) to [bend right =20] (-2.25,1.25) to [bend left =10] (-3.5,1.4) to [bend right =20] (-1.3,3) to [bend left =15] (-2,2.8)to [bend right =10] (0,5) to [bend right =10] (2,2.2) to [bend left =15] (1.3,3) to [bend right =20] (3.5,1.4) to [bend left =10] (2.25,1.25) to [bend right =20] (4,0) to [bend left =15] (2.6,-0.2) --(3.1,-0.5) to [bend left =30] (0.8,-0.2)--(0.8,-1)--(1.2,-1)--(1,-2);
    }
   }
   \shade[left color=brown!40!black, right color=brown!40!black, middle color=brown!80!orange] 
   (7.9,-1) -- (8.1,-1) -- (8.3,-3) -- (7.7,-3) -- cycle;
   % --- VẼ CÁC TẦNG LÁ ---
   % Vẽ từ dưới lên trên (x từ -2 đến 0) để lớp trên đè lên lớp dưới
   \foreach \x in {-2, -1.75, ..., 0} {
    \path (8,1+\x-0.5) pic[scale=0.2]{thong};
   }
   
   % 2. Các quả châu (Balls) - Rải ngẫu nhiên màu sắc
   \foreach \h/\pos in {0.8/0.3, 0.5/-0.2, 0.2/0.4, -0.2/-0.4, -0.5/0.5, -0.8/-0.3, 0.0/0.0, -0.9/0.6, 0.4/-0.5} {
    \shade[ball color=red] (8+\pos, 0.25+\h) circle (1.5pt);
    \shade[ball color=yellow!90!black] (8-\pos*0.8, 0.45+\h) circle (1.5pt);
    \shade[ball color=blue] (8+\pos*0.5, -0.2+\h) circle (1.5pt);
   }
   \node[star, star points=5, star point ratio=2.25, fill=yellow, draw=orange, line width=0.5pt, inner sep=3.5pt] 
   at (8, 1.6) {};
   \draw (8,1.6) node[scale=0.5]{\textbf{\color{red}TED}};
   
   
\end{tikzpicture}
\end{center}'''
    
    # Mệnh đề A
    a_correct = random.choice([True, False])
    a_correct_text = rf"z - {z0} = 0"
    a_wrong_text = rf"z - {z0 + random.choice([1, 2])} = 0"
    stmt_a_text = rf"Đáy của mái nhà nằm trên mặt phẳng ${a_correct_text if a_correct else a_wrong_text}$."
    stmt_a = rf"{'*' if a_correct else ''}a) {stmt_a_text}"
        
    sol_a = rf"""a) {'Đúng' if a_correct else 'Sai'}.
Ta có các điểm ở đáy mái nhà: $A{fmt_point(A)}$, $B{fmt_point(B)}$, $C{fmt_point(C)}$, $D{fmt_point(D)}$.
Nhận thấy tọa độ z của cả bốn điểm đều bằng {z0}, do đó các điểm $A$, $B$, $C$, $D$ cùng nằm trên mặt phẳng $z={z0}$ hay $z-{z0}=0$."""
    
    # Mệnh đề B
    b_correct = random.choice([True, False])
    S_wrong_pt = (Ox, Oy, S_correct_pt[2] + random.choice([-1, 1]))
    b_correct_text = rf"S{fmt_point(S_correct_pt)}"
    b_wrong_text = rf"S{fmt_point(S_wrong_pt)}"
    stmt_b_text = rf"Tọa độ đỉnh chóp của mái nhà là ${b_correct_text if b_correct else b_wrong_text}$."
    stmt_b = rf"{'*' if b_correct else ''}b) {stmt_b_text}"

    sol_b = rf"""b) {'Đúng' if b_correct else 'Sai'}.
Tâm của hình vuông $ABCD$ là $O(\frac{{{A[0]}+{C[0]}}}{{2}};\frac{{{A[1]}+{C[1]}}}{{2}};{z0})={fmt_point((Ox, Oy, z0))}$.
Do mái nhà là hình chóp có chiều cao bằng {h} và đỉnh $S$ nằm trên đường thẳng vuông góc với mặt phẳng đáy tại $O$, nên tọa độ đỉnh chóp là $S{fmt_point(S_correct_pt)}$.
{'Trong khi đó mệnh đề cho rằng $' + b_wrong_text + '$ là tọa độ đỉnh chóp, điều này không đúng.' if not b_correct else 'Điều này khớp với mệnh đề.'}"""
    
    # Mệnh đề C
    c_correct = random.choice([True, False])
    L1 = math.sqrt(a**2 + z0**2)
    c_A = ((v1+v2)*a/L1)**2 + ((v1-v2)*z0/L1)**2
    c_B = -2*a*(v1+v2)*a/L1
    c_C = 2*(a**2)
    min_dist_sq = c_C - (c_B**2)/(4*c_A)
    min_dist = math.sqrt(abs(min_dist_sq))
    d_round = round(min_dist, 1)
    d_wrong = round(min_dist + random.choice([0.5, 1.0]), 1)
    d_value = d_round if c_correct else d_wrong
    stmt_c_text = rf"Ông Tâm muốn một mắc hai dây đèn led một dây LED xanh nối từ $A$ đến $D^\prime$ một dây nối đỏ từ $C$ đến $B^\prime$. Trong cùng một dây hai dây đèn từ $A$ đến $D^\prime$ và từ $C$ đến $B^\prime$ phát ra hai tia sáng với tốc độ lần lượt là ${v1}cm/s$ và ${v2}cm/s$. Khi đó, khoảng cách ngắn nhất giữa hai tia sáng là ${d_value}m$ (làm tròn đến hàng phần chục)."
    stmt_c = rf"{'*' if c_correct else ''}c) {stmt_c_text}"

    sol_c = rf"""c) {'Đúng' if c_correct else 'Sai'}.
Giả sử các bức tường của ngôi nhà vuông góc với mặt đất $z=0$. Lấy các điểm $A^{{\prime}}$, $B^{{\prime}}$, $C^{{\prime}}$, $D^{{\prime}}$ lần lượt là các hình chiếu vuông góc của $A$, $B$, $C$, $D$ xuống mặt phẳng $z=0$.
Ta có $A{fmt_point(A)}$, $C{fmt_point(C)}$, $D^{{\prime}}({A[0]-a}; {A[1]}; 0)$.
$\overrightarrow{{AD^{{\prime}}}}=(-{a}; 0; -{z0})$.
Với $v_1={v1}$ cm/s, $v_2={v2}$ cm/s, khoảng cách ngắn nhất đạt được là $d \approx {d_round}$ m.
{'Khoảng cách ngắn nhất khác nên mệnh đề sai.' if not c_correct else f'Khoảng cách xấp xỉ {d_round}m nên mệnh đề đúng.'}"""
    
    # Mệnh đề D
    d_correct = random.choice([True, False])
    # Wire goes I -> S (through roof hole) -> T (tree top)
    IS_dist = h  # I is directly below S, vertical distance = h
    S_pt = S_correct_pt  # S = (Ox, Oy, z0 + h)
    ST_dist = math.sqrt((Tx - S_pt[0])**2 + (Ty - S_pt[1])**2 + (Th - S_pt[2])**2)
    IT_dist = IS_dist + ST_dist
    Mx, My = x0 - a, y0 + M_dist
    IM_dist = math.sqrt((Mx - Ox)**2 + (My - Oy)**2)
    unfolded_dist = math.sqrt((4*a)**2 + (2*z0 - 2*M_dist)**2)
    total_wire = IT_dist + IM_dist + unfolded_dist
    d_total_round = round(total_wire, 2)
    d_total_wrong = round(total_wire + random.choice([2.0, 3.0]), 2)
    d_total_value = d_total_round if d_correct else d_total_wrong

    stmt_d_text = rf"Ông Tâm có mua một cây thông cao ${Th}m$ và trồng ở vị trí $({Tx}; {Ty}; 0)$ để trang trí cho trung tâm trong dịp giáng sinh sắp tới. Biết rằng để kéo điện thắp sáng ngôi sao trên đỉnh có chữ TED (rất đẹp), ông Tâm phải đục một lỗ nhỏ trên mái nhà và kéo điện từ hộp điện nằm ở tâm của xà nhà lên đỉnh của ngôi sao đó. Ngoài ra để cho không khí thêm ấm cúng, ông Tâm mua một dây LED cắm từ hộp điện đến một điểm $M$ cách $D$ ${M_dist}m$ rồi từ đó cuốn quanh tất cả các bức tường và lại quay trở lại $M$. Độ dài tối thiểu của dây điện và dây đèn cần dùng là làm tròn đến hàng phần trăm là ${d_total_value}$ m."
    stmt_d = rf"{'*' if d_correct else ''}d) {stmt_d_text}"

    sol_d_text = rf"""Phần dây điện thắp sáng ngôi sao:

Hộp điện đặt tại tâm xà nhà (đáy nhà) $I({Ox}; {Oy}; {z0}).$

Đỉnh mái nhà là $S{fmt_point(S_pt)}$, nằm ngay phía trên $I$.

Cây thông ở vị trí $({Tx}; {Ty}; 0)$, cao ${Th}\,\text{{m}}$ nên đỉnh cây thông là $T({Tx}; {Ty}; {Th}).$

Dây điện đi từ $I$ xuyên qua lỗ trên mái nhà tại $S$ rồi đến $T$:

$IS = {h}\,\text{{m}}$ (khoảng cách từ tâm xà nhà lên đỉnh mái).

$ST = \sqrt{{({Tx}-{S_pt[0]})^2+({Ty}-{S_pt[1]})^2+({Th}-{S_pt[2]})^2}} \approx {ST_dist:.2f}\,\text{{m}}.$

Độ dài dây điện cần dùng là $IS + ST = {h} + {ST_dist:.2f} \approx {IT_dist:.2f}\,\text{{m}}.$

Phần dây đèn LED:

Phần dây đèn LED chia làm 2 phần: phần 1 là đoạn nối từ hộp điện đến điểm $M$ và phần 2 từ $M$ cuốn quanh các bức tường.

Độ dài phần 1 chính là độ dài $IM$. Do $M$ cách $D$ $0,5m$ và thuộc đoạn $CD$ nên ta có $M({Mx}; {My}; {z0}).$ 

Suy ra $IM \approx {IM_dist:.2f}\,\text{{m}}.$

Áp dụng phương pháp trải phẳng hình ta có hình sau, khi đó bài toán trở thành tìm độ dài ngắn nhất nối $M$ và $M'$ nằm trong các ô vuông:""" + r"""
\begin{center}
\begin{tikzpicture}[x=0.75pt,y=0.75pt,yscale=-1,xscale=1,line width=0.75pt]
\draw   (313.14,161) -- (376.43,161) -- (376.43,223.96) -- (313.14,223.96) -- cycle ;
\draw   (376.43,161) -- (439.71,161) -- (439.71,223.96) -- (376.43,223.96) -- cycle ;
\draw   (249.86,161) -- (313.14,161) -- (313.14,223.96) -- (249.86,223.96) -- cycle ;
\draw   (249.86,223.96) -- (313.14,223.96) -- (313.14,286.93) -- (249.86,286.93) -- cycle ;
\draw   (249.86,286.93) -- (313.14,286.93) -- (313.14,349.89) -- (249.86,349.89) -- cycle ;
\draw   (186.57,286.93) -- (249.86,286.93) -- (249.86,349.89) -- (186.57,349.89) -- cycle ;
\draw   (123.29,286.93) -- (186.57,286.93) -- (186.57,349.89) -- (123.29,349.89) -- cycle ;
\draw   (123.29,349.89) -- (186.57,349.89) -- (186.57,412.86) -- (123.29,412.86) -- cycle ;
\draw    (394.29,157.86) -- (394.29,164.86) ;
\draw    (139.29,409.86) -- (139.29,416.86) ;
\draw (112,272.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{A'}}};
\draw (182,269.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{B'}}};
\draw (188.57,349.89) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C'}}};
\draw (106,341.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D'}}};
\draw (388,143.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{M}}};
\draw (108,405.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D}}};
\draw (369,222.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{A}}};
\draw (439.71,221.96) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{B}}};
\draw (187,406.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C}}};
\draw (441,146.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C}}};
\draw (371,144.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D}}};
\draw (308,144.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D'}}};
\draw (317.14,223.96) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{A'}}};
\draw (232,216.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{B'}}};
\draw (234,150.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C'}}};
\draw (236,269.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{B}}};
\draw (315,277.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{A}}};
\draw (244,350.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C}}};
\draw (309,349.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D}}};
\draw (131,414.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{M'}}};
\end{tikzpicture}
\end{center}

Ta nối M và M' bằng đường màu đỏ, được hình sau:
\begin{center}
\begin{tikzpicture}[x=0.75pt,y=0.75pt,yscale=-1,xscale=1,line width=0.75pt]
\draw   (313.14,161) -- (376.43,161) -- (376.43,223.96) -- (313.14,223.96) -- cycle ;
\draw   (376.43,161) -- (439.71,161) -- (439.71,223.96) -- (376.43,223.96) -- cycle ;
\draw   (249.86,161) -- (313.14,161) -- (313.14,223.96) -- (249.86,223.96) -- cycle ;
\draw   (249.86,223.96) -- (313.14,223.96) -- (313.14,286.93) -- (249.86,286.93) -- cycle ;
\draw   (249.86,286.93) -- (313.14,286.93) -- (313.14,349.89) -- (249.86,349.89) -- cycle ;
\draw   (186.57,286.93) -- (249.86,286.93) -- (249.86,349.89) -- (186.57,349.89) -- cycle ;
\draw   (123.29,286.93) -- (186.57,286.93) -- (186.57,349.89) -- (123.29,349.89) -- cycle ;
\draw   (123.29,349.89) -- (186.57,349.89) -- (186.57,412.86) -- (123.29,412.86) -- cycle ;
\draw    (394.29,157.86) -- (394.29,164.86) ;
\draw    (139.29,409.86) -- (139.29,416.86) ;
\draw[red]    (394.29,160.86) -- (139.29,413.86) ;
\draw (112,272.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{A'}}};
\draw (182,269.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{B'}}};
\draw (166.57,332.89) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C'}}};
\draw (106,341.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D'}}};
\draw (388,143.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{M}}};
\draw (108,405.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D}}};
\draw (369,222.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{A}}};
\draw (439.71,221.96) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{B}}};
\draw (187,406.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C}}};
\draw (441,146.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C}}};
\draw (371,144.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D}}};
\draw (308,144.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D'}}};
\draw (297.14,208.96) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{A'}}};
\draw (232,216.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{B'}}};
\draw (234,150.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C'}}};
\draw (236,269.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{B}}};
\draw (315,277.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{A}}};
\draw (244,350.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C}}};
\draw (309,349.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D}}};
\draw (131,414.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{M'}}};
\end{tikzpicture}
\end{center}

Ta có thể quan sát được đường màu đỏ là đường ngắn nhất nối $M$ và $M'$, tuy nhiên đường màu đỏ đi ra ngoài phạm vi các ô vuông. Từ đó, ta có thể tìm các đường nối $M$ và $M'$ gần với đường màu đỏ nhất. Ta dễ dàng xác định được đường màu xanh thỏa như sau:

\begin{center}
\begin{tikzpicture}[x=0.75pt,y=0.75pt,yscale=-1,xscale=1,line width=0.75pt]
\draw   (313.14,161) -- (376.43,161) -- (376.43,223.96) -- (313.14,223.96) -- cycle ;
\draw   (376.43,161) -- (439.71,161) -- (439.71,223.96) -- (376.43,223.96) -- cycle ;
\draw   (249.86,161) -- (313.14,161) -- (313.14,223.96) -- (249.86,223.96) -- cycle ;
\draw   (249.86,223.96) -- (313.14,223.96) -- (313.14,286.93) -- (249.86,286.93) -- cycle ;
\draw   (249.86,286.93) -- (313.14,286.93) -- (313.14,349.89) -- (249.86,349.89) -- cycle ;
\draw   (186.57,286.93) -- (249.86,286.93) -- (249.86,349.89) -- (186.57,349.89) -- cycle ;
\draw   (123.29,286.93) -- (186.57,286.93) -- (186.57,349.89) -- (123.29,349.89) -- cycle ;
\draw   (123.29,349.89) -- (186.57,349.89) -- (186.57,412.86) -- (123.29,412.86) -- cycle ;
\draw    (394.29,157.86) -- (394.29,164.86) ;
\draw    (139.29,409.86) -- (139.29,416.86) ;
\draw[red]    (394.29,160.86) -- (139.29,413.86) ;
\draw[blue] (394.29,160.86) -- (313,224) -- (187,350) -- (139.29,413.86) ;
\draw (112,272.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{A'}}};
\draw (182,269.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{B'}}};
\draw (166.57,332.89) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C'}}};
\draw (106,341.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D'}}};
\draw (388,143.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{M}}};
\draw (108,405.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D}}};
\draw (369,222.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{A}}};
\draw (439.71,221.96) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{B}}};
\draw (187,406.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C}}};
\draw (441,146.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C}}};
\draw (371,144.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D}}};
\draw (308,144.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D'}}};
\draw (297.14,208.96) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{A'}}};
\draw (232,216.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{B'}}};
\draw (234,150.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C'}}};
\draw (236,269.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{B}}};
\draw (315,277.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{A}}};
\draw (244,350.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{C}}};
\draw (309,349.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{D}}};
\draw (131,414.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{ptm}\selectfont \textit{M'}}};
\end{tikzpicture}
\end{center}
""" + rf"""
Bằng định lý Pytago trải thẳng, ta có thể tính được độ dài các đoạn màu xanh xấp xỉ ${unfolded_dist:.3f}\,\,m.$

Do đó độ dài đường ngắn nhất của dây đèn LED là ${unfolded_dist:.3f}+{IM_dist:.3f}={unfolded_dist+IM_dist:.3f}\,\,m.$

Vậy tổng độ dài phần dây điện và phần đèn LED là ${unfolded_dist+IM_dist:.3f}+{IT_dist:.2f}={total_wire:.3f}\,\,m.$
"""
    sol_d = f"d) {'Đúng' if d_correct else 'Sai'}.\n{sol_d_text}"

    question = rf"""{stem}

{stmt_a}

{stmt_b}

{stmt_c}

{stmt_d}"""

    solution = rf"""{sol_a}

{sol_b}

{sol_c}

{sol_d}"""

    key = ", ".join(["Đ" if x else "S" for x in [a_correct, b_correct, c_correct, d_correct]])
    
    return question, solution, key

def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    out_dir = os.path.dirname(os.path.abspath(__file__))
    
    content = ""
    keys = []
    
    for i in range(num_questions):
        q, s, k = generate_question(i % len(CONTEXTS))
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
\usetikzlibrary{calc,angles,quotes,patterns,shapes.geometric}

\newcommand{\heva}[1]{\left\{\begin{aligned}#1\end{aligned}\right.}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)

    out_path = os.path.join(out_dir, "cau_3_questions.tex")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {out_path}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")

if __name__ == "__main__":
    main()