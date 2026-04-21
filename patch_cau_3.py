import re

with open("2026/20_04/cau_3.py", "r", encoding="utf-8") as f:
    content = f.read()

stem_text = r"""stem = r'''Trung tâm TED mới xây một ngôi nhà mới để cho học sinh học tập trải nghiệm có mái nhà là hình chóp tứ giác đều $S.ABCD$ có chiều cao là 2 mét. Trong hệ tọa độ $Oxyz$ (đơn vị đo trên các trục tính bằng mét), với các điểm ở đáy là $A(6; 4; 2)$, $B(6; 6; 2)$, $C(4; 6; 2)$, $D(4; 4; 2)$ và $S$ là đỉnh của mái nhà. Xét tính đúng/sai của các mệnh đề sau:

\begin{center}
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.8]
   \coordinate (S') at (-1.8,3.9);
   \coordinate (B') at (-3.2,-1.9);
   \coordinate (C') at (-0.7,0.7);
   \coordinate (P9) at (3.2,-0.2);
   \coordinate (P11) at (4.1,-3.0);
   \coordinate (P15) at (7.0,-2.8);
   \coordinate (L) at (7.0,-0.4);
   \coordinate (O) at (0.0,-0.0);
   \coordinate (x) at (-2.9,-3.3);
   \coordinate (y) at (8.4,-0.0);
   \coordinate (z) at (0.0,5.0);
   \coordinate (G) at ($(L)!0.233!(C')$);
   \coordinate (B) at ($(L)!0.285!(B')$);
   \coordinate (S) at ($(L)!0.374!(S')$);
   \coordinate (A) at ($(B) + (P9) - (G)$);
   \coordinate (D12) at ($(A) + (P11) - (B)$);
   \coordinate (D13) at ($(P11) + (G) - (B)$);
   \coordinate (D14) at ($(D12) + (D13) - (P11)$);
   % --- Vẽ các đối tượng ---
   \draw[blue] (L) -- (B');
   \draw[blue] (L) -- (S');
   \draw[blue,dashed] (L) -- (C');
   %%%%%%%%%%%%%%%%%
   \draw[black] (S) -- (G) -- (D13) -- (P11) -- (D12) -- (A) -- (S);
   %%%%%%%%%%%%%%%%%
   \draw[black] (A) -- (B) -- (G) (S)--(B) (B) -- (P11);
   %%%%%%%%%%%%%%%%%
   \draw[black,dashed] (A) -- (P9) -- (G);
   %%%%%%%%%%%%%%%%%
   \draw[black,dashed] (D12) -- (D14) -- (D13);
   %%%%%%%%%%%%%%%%%
   \draw[black,dashed] (D14) -- (P9) -- (S);
   %%%%%%%%%%%%%%%%%
   \draw[black,pattern=north west lines] (S') -- (B') -- (C') -- (S');
   \draw[black,line width=4pt] (L) -- (P15);
   %%%%%%%%%%%%%%%%%
   \draw[blue,->] (O) -- (x);
   \draw[blue,->,dashed] (O) -- (y);
   \draw[blue,->] (O) -- (z);
   \path (L)--(S) node[pos=0.5,sloped]{\textbf{<<}};
   \path (L)--(B) node[pos=0.5,sloped]{\textbf{<<}};
   \foreach \p/\r in {B'/-120,A/180,B/90,G/-45,L/0,S'/90,C'/40,O/-90,S/90}
   \fill (\p) circle (1.2pt) node[shift={(\r:3mm)}]{$\p$};
   \draw (x) node[shift={(0:3mm)}]{$x$};
   \draw (y) node[shift={(0:3mm)}]{$y$};
   \draw (z) node[shift={(0:3mm)}]{$z$};
\end{tikzpicture}
\end{center}'''"""

content = re.sub(
    r'stem \= rf"Trung tâm TED mới xây một ngôi nhà mới.*?Xét tính đúng/sai của các mệnh đề sau:"',
    stem_text,
    content,
    flags=re.DOTALL
)

sol_d_text = r"""sol_d_text = r'''\textbf{Phần dây điện thắp sáng ngôi sao:}

Hộp điện đặt tại tâm xà nhà (đáy nhà) $I(5;5;2).$

Cây thông ở vị trí $(-8;-8;0)$, cao $10\,\text{m}$ nên đỉnh cây thông là $T(-8;-8;10).$

Độ dài dây điện cần dùng là $\displaystyle IT = \sqrt{(-8-5)^2+(-8-5)^2+(10-2)^2} \approx 20{,}05\,\text{m}.$

\hspace{0,7cm}\textbf{Phần dây đèn LED:}

Phần dây đèn LED chia làm 2 phần: phần 1 là đoạn nối từ hộp điện đến điểm $M$ và phần 2 từ $M$ cuốn quanh các bức tường.

Độ dài phần 1 chính là độ dài $IM$. Do $M$ cách $D$ $0,5m$ và thuộc đoạn $CD$ nên ta có $M(4; 4,5; 2).$ 

Suy ra $IM=\sqrt{(4-5)^2+(4,5-5)^2+(2-2)^2} =\sqrt{1+0,25} =\sqrt{1,25}\approx 1,118\,\text{m}.$

Áp dụng phương pháp trải phẳng hình ta có hình sau, khi đó bài toán trở thành tìm độ dài ngắn nhất nối $M$ và $M'$ nằm trong các ô vuông:
\begin{center}
\tikzset{every picture/.style={line width=0.75pt}}       
\begin{tikzpicture}[x=0.75pt,y=0.75pt,yscale=-1,xscale=1]
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
\tikzset{every picture/.style={line width=0.75pt}}       
\begin{tikzpicture}[x=0.75pt,y=0.75pt,yscale=-1,xscale=1]
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
\tikzset{every picture/.style={line width=0.75pt}}       
\begin{tikzpicture}[x=0.75pt,y=0.75pt,yscale=-1,xscale=1]
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

Bằng định lý Pytago, ta có thể tính được độ dài các đoạn màu xanh xấp xỉ $11,385\,\,m.$

Do đó độ dài đường ngắn nhất của dây đèn LED là $11,385+1,118=12,503$\,m.

Vậy tổng độ dài phân dây điện và phần đèn LED là $12,503+20,05=32,553$\,m.
'''

sol_d_format = f"d) {'Đúng' if d_correct else 'Sai'}.\n{sol_d_text}"
"""

content = re.sub(
    r'sol_d \= rf"""d\) \{\'Đúng\' if d_correct else \'Sai\'\}\..*?Vậy tổng độ dài phần dây điện và phần đèn LED là \$12,503 \+ 20,05 \= 32,553\$ m\."""',
    sol_d_text + '\n    sol_d = f"""d) {{\'Đúng\' if d_correct else \'Sai\'}}.\n{sol_d_text}"""',
    content,
    flags=re.DOTALL
)

content = content.replace(r"\usetikzlibrary{calc,angles,quotes}", r"\usetikzlibrary{calc,angles,quotes,patterns}")

with open("2026/20_04/cau_3.py", "w", encoding="utf-8") as f:
    f.write(content)
print("done")
