import re

with open("cau_3.py", "r", encoding="utf-8") as f:
    code = f.read()

def_start = code.find("def generate_question")
def_end = code.find("def main():")

new_generate_question = r'''def generate_question(context_idx=None) -> Tuple[str, str, str]:
    if context_idx is None:
        context = random.choice(CONTEXTS)
    else:
        context = CONTEXTS[context_idx % len(CONTEXTS)]
        
    dx = random.randint(-4, 4)
    dy = random.randint(-4, 4)
    Ax, Ay = 6 + dx, 4 + dy
    Bx, By = 6 + dx, 6 + dy
    Cx, Cy = 4 + dx, 6 + dy
    Dx, Dy = 4 + dx, 4 + dy
    Ox, Oy = 5 + dx, 5 + dy
    
    v1 = random.choice([1.0, 1.5, 2.0, 2.5])
    v2 = random.choice([2.0, 2.5, 3.0, 3.5])
    
    Tx = random.randint(-12, -6)
    Ty = random.randint(-12, -6)
    Ht = random.randint(8, 15)
    
    stem = rf"""Trung tâm TED mới xây một ngôi nhà mới để cho học sinh học tập trải nghiệm có mái nhà là hình chóp tứ giác đều $S.ABCD$ có chiều cao là 2 mét. Trong hệ tọa độ $Oxyz$ (đơn vị đo trên các trục tính bằng mét), với các điểm ở đáy là $A({Ax}; {Ay}; 2)$, $B({Bx}; {By}; 2)$, $C({Cx}; {Cy}; 2)$, $D({Dx}; {Dy}; 2)$ và $S$ là đỉnh của mái nhà. Xét tính đúng/sai của các mệnh đề sau:

\begin{center}
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
   \coordinate (S') at (-1.8,3.9);
   \coordinate (B') at (-3.2,-1.9);
   \coordinate (C') at (-0.7,0.7);
   \coordinate (D_tikz) at (3.2,-0.2);
   \coordinate (P11) at (4.1,-3.0);
   \coordinate (P15) at (7.0,-2.8);
   \coordinate (L) at (7.0,-0.4);
   \coordinate (L1) at (7.0,2);
   \coordinate (O_tikz) at (1,0.0);
   \coordinate (x) at (-2,-3.3);
   \coordinate (y) at (9.5,-0.0);
   \coordinate (z) at (0.1,5.0);
   \coordinate (C_tikz) at ($(L)!0.1!(C')$);
   \coordinate (B_tikz) at ($(L)!0.285!(B')+(0,-1)$);
   \coordinate (S_tikz) at ($(L)!0.374!(S')$);
   \coordinate (A_tikz) at ($(B_tikz) + (D_tikz) - (C_tikz)$);
   \coordinate (D12) at ($(A_tikz) + (P11) - (B_tikz)$);
   \coordinate (D13) at ($(P11) + (C_tikz) - (B_tikz)$);
   \coordinate (D14) at ($(D12) + (D13) - (P11)$);
   \coordinate (O') at ($(A_tikz)!1/2!(C_tikz)$);
   
   \draw[black] (S_tikz) -- (C_tikz) -- (D13) coordinate (C') -- (P11) coordinate (B')-- (D12) coordinate (A')-- (A_tikz) -- (S_tikz);
   %%%%%%%%%%%%%%%%%
   \draw[black] (A_tikz) -- (B_tikz) -- (C_tikz) (S_tikz)--(B_tikz) (B_tikz) -- (P11);
   %%%%%%%%%%%%%%%%%
   \draw[black,dashed] (A_tikz) -- (D_tikz) -- (C_tikz);
   %%%%%%%%%%%%%%%%%
   \draw[black,dashed] (D12) -- (D14) -- (D13);
   %%%%%%%%%%%%%%%%%
   \draw[black,dashed] (D14)coordinate (D') -- (D_tikz) -- (S_tikz);
   %%%%%%%%%%%%%%%%%
   % \draw[black,line width=4pt] (L1) -- (P15);
   %%%%%%%%%%%%%%%%%
   \draw[dashed] (O')--($(O')!0.2!(L1)+(0,0.75)$);
   \draw  
   ($(O')!0.2!(L1)+(0,0.75)$)--(8,2)
   (O') coordinate (I) ;
   \begin{scope}[red,line width=0.6pt]
    \draw[dashed] (I) -- ($(D_tikz)!0.1!(C_tikz)$) coordinate (M)-- ($(D_tikz)!0.6!(A_tikz)$) --($(D')!1/2!(A')$)
    --($(B')!1/2!(A')$)
    ($(B_tikz)!0.2!(A_tikz)$)--($(B_tikz)!0.2!(C_tikz)$)
    ($(B')!1/2!(C')$)--($(D')!0.75!(C')$)
    --($(D_tikz)!0.1!(C_tikz)$)
    ;
    \draw ($(B')!1/2!(A')$)--($(B_tikz)!0.2!(A_tikz)$)
    ($(B_tikz)!0.2!(C_tikz)$)--($(B')!1/2!(C')$)
    ;
   \end{scope}
   \foreach \p/\r in {A_tikz/180,B_tikz/-40,C_tikz/-45,S_tikz/90,D_tikz/140,I/0,M/60}
   {
       \pgfmathsetmacro{\x}{\r}
       \fill (\p) circle (1.2pt);
   }
   \draw (A_tikz) node[shift={(180:3mm)}]{$A$};
   \draw (B_tikz) node[shift={(-40:3mm)}]{$B$};
   \draw (C_tikz) node[shift={(-45:3mm)}]{$C$};
   \draw (S_tikz) node[shift={(90:3mm)}]{$S$};
   \draw (D_tikz) node[shift={(140:3mm)}]{$D$};
   \draw (I) node[shift={(0:3mm)}]{$I$};
   \draw (M) node[shift={(60:3mm)}]{$M$};
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
   \foreach \x in {-2, -1.75, ..., 0} {
    \path (8,1+\x-0.5) pic[scale=0.2]{thong};
   }
   \foreach \h/\pos in {0.8/0.3, 0.5/-0.2, 0.2/0.4, -0.2/-0.4, -0.5/0.5, -0.8/-0.3, 0.0/0.0, -0.9/0.6, 0.4/-0.5} {
    \shade[ball color=red] (8+\pos, 0.25+\h) circle (1.5pt);
    \shade[ball color=yellow!90!black] (8-\pos*0.8, 0.45+\h) circle (1.5pt);
    \shade[ball color=blue] (8+\pos*0.5, -0.2+\h) circle (1.5pt);
   }
   \node[star, star points=5, star point ratio=2.25, fill=yellow, draw=orange, line width=0.5pt, inner sep=3.5pt] 
   at (8, 1.6) {};
   \draw (8,1.6) node[scale=0.5]{\textbf{\color{red}TED}};
\end{tikzpicture}
\end{center}"""
    
    # Mệnh đề A
    a_correct = random.choice([True, False])
    stmt_a_text = context['a_stmt']
    if not a_correct:
        stmt_a_text = stmt_a_text.replace("z - 2 = 0", "z - 4 = 0")
    stmt_a = rf"{'*' if a_correct else ''}a) {stmt_a_text}"
        
    sol_a = rf"""a) {'Đúng' if a_correct else 'Sai'}.
Ta có các điểm ở đáy mái nhà: $A({Ax};{Ay};2)$, $B({Bx};{By};2)$, $C({Cx};{Cy};2)$, $D({Dx};{Dy};2)$.
Nhận thấy tọa độ z của cả bốn điểm đều bằng 2, do đó các điểm $A$, $B$, $C$, $D$ cùng nằm trên mặt phẳng $z=2$ hay $z-2=0$."""
    
    # Mệnh đề B
    b_correct = random.choice([True, False])
    stmt_b_text = context['b_stmt'].replace("S(5; 4; 5)", rf"S({Ox}; {Oy}; 4)")
    if not b_correct:
         stmt_b_text = context['b_stmt'].replace("S(5; 4; 5)", rf"S({Ox}; {Oy+1}; 5)")
    stmt_b = rf"{'*' if b_correct else ''}b) {stmt_b_text}"

    sol_b = rf"""b) {'Đúng' if b_correct else 'Sai'}.
Tâm của hình chữ nhật $ABCD$ là $O(\frac{{{Ax}+{Cx}}}{{2}};\frac{{{Ay}+{Cy}}}{{2}};2)=({Ox};{Oy};2)$.
Do mái nhà là hình chóp có chiều cao bằng 2 và đỉnh $S$ nằm trên đường thẳng vuông góc với mặt phẳng đáy tại $O$, nên tọa độ đỉnh chóp là $S({Ox};{Oy};4)$.
{'Trong khi đó mệnh đề cho tọa độ khác, điều này không đúng.' if not b_correct else 'Điều này khớp với mệnh đề.'}"""
    
    # Mệnh đề C
    v1_f = v1 / 100.0
    v2_f = v2 / 100.0
    b_val = 4 * (v1_f + v2_f) / math.sqrt(2)
    a_val = v1_f**2 + v2_f**2
    t_min = b_val / (2 * a_val)
    min_dist_sq = 8 - (b_val**2) / (4 * a_val)
    min_dist = math.sqrt(min_dist_sq)
    min_dist_round = round(min_dist, 1)
    
    c_correct = random.choice([True, False])
    stmt_c_text = context['c_stmt'].replace("1.5", str(v1)).replace("3", str(v2))
    if c_correct:
        stmt_c_text = stmt_c_text.replace("2m", f"{min_dist_round}m")
    else:
        fake_dist = round(min_dist + 1.2, 1)
        stmt_c_text = stmt_c_text.replace("2m", f"{fake_dist}m")
    stmt_c = rf"{'*' if c_correct else ''}c) {stmt_c_text}"

    sol_c = rf"""c) {'Đúng' if c_correct else 'Sai'}.
Giả sử các bức tường của ngôi nhà vuông góc với mặt đất $z=0$. Lấy các điểm $A^{{\prime}}$, $B^{{\prime}}$, $C^{{\prime}}$, $D^{{\prime}}$ lần lượt là các hình chiếu vuông góc của $A$, $B$, $C$, $D$ xuống mặt phẳng $z=0$.
Ta có $A({Ax};{Ay};2)$, $C({Cx};{Cy};2)$, $D^{{\prime}}({Dx};{Dy};0)$, $B^{{\prime}}({Bx};{By};0)$.
$\overrightarrow{{AD^{{\prime}}}}=(-2;0;-2)$.
$|\overrightarrow{{AD^{{\prime}}}}|=2\sqrt{{2}} \Rightarrow \vec{{u}}_{{1}}=(-\frac{{1}}{{\sqrt{{2}}}};0;-\frac{{1}}{{\sqrt{{2}}}})$.
Vì $AQ={v1_f:g}t$ nên $Q({Ax}-\frac{{{v1_f:g}t}}{{\sqrt{{2}}}};{Ay};2-\frac{{{v1_f:g}t}}{{\sqrt{{2}}}})$.
$\overrightarrow{{CB^{{\prime}}}}=(2;0;-2)$, $|\overrightarrow{{CB^{{\prime}}}}|=2\sqrt{{2}} \Rightarrow \vec{{u}}_{{2}}=(\frac{{1}}{{\sqrt{{2}}}};0;-\frac{{1}}{{\sqrt{{2}}}})$.
$CR={v2_f:g}t$ nên $R({Cx}+\frac{{{v2_f:g}t}}{{\sqrt{{2}}}};{Cy};2-\frac{{{v2_f:g}t}}{{\sqrt{{2}}}})$.
$QR^2 = (-2 + \frac{{{v1_f+v2_f:g}}}{{\sqrt{{2}}}}t)^2 + 2^2 + (\frac{{{v1_f-v2_f:g}}}{{\sqrt{{2}}}}t)^2 = 8 - \frac{{{4*(v1_f+v2_f):g}}}{{\sqrt{{2}}}}t + {v1_f**2+v2_f**2:g}t^2$.
$(QR^2)^{{\prime}} = - \frac{{{4*(v1_f+v2_f):g}}}{{\sqrt{{2}}}} + {2*(v1_f**2+v2_f**2):g}t = 0 \Rightarrow t \approx {t_min:.1f}$ (s).
Khi đó $QR_{{\text{{min}}}} \approx {min_dist_round}$ m.
{'Khoảng cách ngắn nhất tính được khác với mệnh đề nên mệnh đề sai.' if not c_correct else 'Điều kiện khớp với toán học nên mệnh đề đúng.'}"""
    
    # Mệnh đề D
    IT_sq = (Tx - Ox)**2 + (Ty - Oy)**2 + (Ht - 2)**2
    IT = math.sqrt(IT_sq)
    wire_len = 12.503 + IT
    wire_len_round = round(wire_len, 2)
    
    d_correct = random.choice([True, False])
    stmt_d_text = context['d_stmt'].replace("(-8; -8; 0)", rf"({Tx}; {Ty}; 0)").replace("10m", f"{Ht}m")
    if d_correct:
         stmt_d_text = stmt_d_text + rf" là ${wire_len_round}$ m."
    else:
         stmt_d_text = stmt_d_text + rf" là ${round(wire_len + 2.50, 2)}$ m."
    stmt_d = rf"{'*' if d_correct else ''}d) {stmt_d_text}"

    sol_d_text = rf"""Phần dây điện thắp sáng ngôi sao:

Hộp điện đặt tại tâm xà nhà (đáy nhà) $I({Ox};{Oy};2).$

Cây thông ở vị trí $({Tx};{Ty};0)$, cao ${Ht}\,\text{{m}}$ nên đỉnh cây thông là $T({Tx};{Ty};{Ht}).$

Độ dài dây điện cần dùng là $\displaystyle IT = \sqrt{{({Tx}-{Ox})^2+({Ty}-{Oy})^2+({Ht}-2)^2}} \approx {IT:.2f}\,\text{{m}}.$

Phần dây đèn LED:

Phần dây đèn LED chia làm 2 phần: phần 1 là đoạn nối từ hộp điện đến điểm $M$ và phần 2 từ $M$ cuốn quanh các bức tường.

Độ dài phần 1 chính là độ dài $IM$. Do $M$ cách $D$ $0,5m$ và thuộc đoạn $CD$ nên ta có $M({Dx}; {Dy+0.5}; 2).$ 

Suy ra $IM=\sqrt{{({Dx}-{Ox})^2+({Dy+0.5}-{Oy})^2+(2-2)^2}} =\sqrt{{1+0,25}} =\sqrt{{1,25}}\approx 1,118\,\text{{m}}.$

Áp dụng phương pháp trải phẳng hình ta có hình sau, khi đó bài toán trở thành tìm độ dài ngắn nhất nối $M$ và $M'$ nằm trong các ô vuông:
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
\draw (112,272.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{A'}}}};
\draw (182,269.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{B'}}}};
\draw (188.57,349.89) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C'}}}};
\draw (106,341.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D'}}}};
\draw (388,143.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{M}}}};
\draw (108,405.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D}}}};
\draw (369,222.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{A}}}};
\draw (439.71,221.96) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{B}}}};
\draw (187,406.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C}}}};
\draw (441,146.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C}}}};
\draw (371,144.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D}}}};
\draw (308,144.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D'}}}};
\draw (317.14,223.96) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{A'}}}};
\draw (232,216.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{B'}}}};
\draw (234,150.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C'}}}};
\draw (236,269.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{B}}}};
\draw (315,277.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{A}}}};
\draw (244,350.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C}}}};
\draw (309,349.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D}}}};
\draw (131,414.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{M'}}}};
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
\draw (112,272.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{A'}}}};
\draw (182,269.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{B'}}}};
\draw (166.57,332.89) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C'}}}};
\draw (106,341.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D'}}}};
\draw (388,143.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{M}}}};
\draw (108,405.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D}}}};
\draw (369,222.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{A}}}};
\draw (439.71,221.96) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{B}}}};
\draw (187,406.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C}}}};
\draw (441,146.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C}}}};
\draw (371,144.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D}}}};
\draw (308,144.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D'}}}};
\draw (297.14,208.96) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{A'}}}};
\draw (232,216.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{B'}}}};
\draw (234,150.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C'}}}};
\draw (236,269.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{B}}}};
\draw (315,277.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{A}}}};
\draw (244,350.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C}}}};
\draw (309,349.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D}}}};
\draw (131,414.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{M'}}}};
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
\draw (112,272.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{A'}}}};
\draw (182,269.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{B'}}}};
\draw (166.57,332.89) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C'}}}};
\draw (106,341.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D'}}}};
\draw (388,143.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{M}}}};
\draw (108,405.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D}}}};
\draw (369,222.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{A}}}};
\draw (439.71,221.96) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{B}}}};
\draw (187,406.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C}}}};
\draw (441,146.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C}}}};
\draw (371,144.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D}}}};
\draw (308,144.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D'}}}};
\draw (297.14,208.96) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{A'}}}};
\draw (232,216.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{B'}}}};
\draw (234,150.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C'}}}};
\draw (236,269.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{B}}}};
\draw (315,277.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{A}}}};
\draw (244,350.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{C}}}};
\draw (309,349.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{D}}}};
\draw (131,414.57) node [anchor=north west][inner sep=0.75pt]   [align=left] {{\fontfamily{{ptm}}\selectfont \textit{{M'}}}};
\end{tikzpicture}
\end{center}

Bằng định lý Pytago, ta có thể tính được độ dài các đoạn màu xanh xấp xỉ $11,385\,\,m.$

Do đó độ dài đường ngắn nhất của dây đèn LED là $11,385+1,118=12,503$\,m.

Vậy tổng độ dài phần dây điện và phần đèn LED là $12,503+{IT:.2f}={wire_len_round}$\,m.
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
'''

code = code[:def_start] + new_generate_question + "\n\n" + code[def_end:]

with open("cau_3.py", "w", encoding="utf-8") as f:
    f.write(code)

