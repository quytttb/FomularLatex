import re

with open("cau_3.py", "r", encoding="utf-8") as f:
    c = f.read()

new_tikz = r"""\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
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
   
   
\end{tikzpicture}"""

c = re.sub(r"\\begin\{tikzpicture\}\[line join = round.*?\\end\{tikzpicture\}", new_tikz, c, count=1, flags=re.DOTALL)

if "shapes.geometric" not in c:
    c = c.replace(r"\usetikzlibrary{calc,angles,quotes,patterns}", r"\usetikzlibrary{calc,angles,quotes,patterns,shapes.geometric}")

with open("cau_3.py", "w", encoding="utf-8") as f:
    f.write(c)

