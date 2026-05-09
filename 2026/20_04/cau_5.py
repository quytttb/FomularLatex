import sys
import os
import random
import math
from typing import Tuple

def generate_question(seed_val=None) -> Tuple[str, str, str]:
    if seed_val is not None:
        random.seed(seed_val)
        
    while True:
        # A, B, C random coordinates, limited up to roughly 50 possible values per axis to fit "50 values" requirement, e.g. -25 to 25.
        if random.random() < 0.5:  # 50% chance to create a "nice" configuration with one vertex as the center of the circle
            px, py, pz = random.randint(-15, 15), random.randint(-15, 15), random.randint(-15, 15)
            dx, dy, dz = random.randint(-10, 10), random.randint(-10, 10), random.randint(-10, 10)
            v1 = [dx, dy, dz]
            v2 = [dx, dy, dz]
            random.shuffle(v2)
            v2 = [v2[0]*random.choice([1, -1]), v2[1]*random.choice([1, -1]), v2[2]*random.choice([1, -1])]
            
            peak_choice = random.choice(['A', 'B', 'C'])
            if peak_choice == 'A':
                A = (px, py, pz)
                B = (px+v1[0], py+v1[1], pz+v1[2])
                C = (px+v2[0], py+v2[1], pz+v2[2])
            elif peak_choice == 'B':
                B = (px, py, pz)
                A = (px+v1[0], py+v1[1], pz+v1[2])
                C = (px+v2[0], py+v2[1], pz+v2[2])
            else:
                C = (px, py, pz)
                A = (px+v1[0], py+v1[1], pz+v1[2])
                B = (px+v2[0], py+v2[1], pz+v2[2])
        else:
            A = (random.randint(-20, 25), random.randint(-20, 25), random.randint(-20, 25))
            B = (random.randint(-20, 25), random.randint(-20, 25), random.randint(-20, 25))
            C = (random.randint(-20, 25), random.randint(-20, 25), random.randint(-20, 25))
        
        def dist2(p1, p2):
            return (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2
            
        AB2 = dist2(A, B)
        AC2 = dist2(A, C)
        BC2 = dist2(B, C)
        
        # Ensure not identical or collinear (triangle inequality strictly gt)
        if AB2 == 0 or AC2 == 0 or BC2 == 0:
            continue
            
        AB = math.sqrt(AB2)
        AC = math.sqrt(AC2)
        BC = math.sqrt(BC2)
        
        if AB + BC <= AC + 0.01 or AB + AC <= BC + 0.01 or AC + BC <= AB + 0.01:
            continue
            
        # cos B
        cosB = (AB2 + BC2 - AC2) / (2 * AB * BC)
        
        # Avoid Floating point precision issues with math.acos
        if cosB <= -1.0 or cosB >= 1.0:
            continue
            
        alpha = math.acos(cosB)
        
        # Area
        sinB = math.sqrt(1 - cosB**2)
        S = 0.5 * AB * BC * sinB
        if S < 0.1:
            continue
            
        break
        
    # R
    R = (AB * BC * AC) / (4 * S)
    
    beta = 2*math.pi - 2*alpha
    length = beta * R
    
    ans_val = round(length)
    
    can_text = ""
    if AB2 == AC2 and AB2 != BC2:
        can_text = r", suy ra tam giác $ABC$ cân tại $A$"
    elif AB2 == BC2 and AB2 != AC2:
        can_text = r", suy ra tam giác $ABC$ cân tại $B$"
    elif AC2 == BC2 and AC2 != AB2:
        can_text = r", suy ra tam giác $ABC$ cân tại $C$"
    elif AB2 == AC2 and AB2 == BC2:
        can_text = r", suy ra tam giác $ABC$ đều"
    
    stem = rf"""Trong công viên nước, người ta xây dựng một máng trượt nước dạng một cung tròn. Mô hình hóa trong hệ trục $Oxyz$ (đơn vị trên mỗi trục là 1 mét) với điểm đầu máng trượt là $A({A[0]}; {A[1]}; {A[2]})$, cung tròn đi qua điểm $B({B[0]}; {B[1]}; {B[2]})$ và kết thúc ở điểm $C({C[0]}; {C[1]}; {C[2]})$.

  \begin{{tikzpicture}}[scale=0.8]
   \definecolor{{deepskyblue}}{{rgb}}{{0.0, 0.75, 1.0}}
   \definecolor{{carnationpink}}{{rgb}}{{1.0, 0.65, 0.79}}
   \definecolor{{darkpastelgreen}}{{rgb}}{{0.01, 0.75, 0.24}}
   \definecolor{{brinkpink}}{{rgb}}{{0.98, 0.38, 0.5}}
   \definecolor{{brightmaroon}}{{rgb}}{{0.76, 0.13, 0.28}}
   \definecolor{{canaryyellow}}{{rgb}}{{1.0, 0.94, 0.0}}
   \definecolor{{beige}}{{rgb}}{{0.96, 0.96, 0.86}}
   \fill[green!90!white] (-4,-5)rectangle(4,0.5);
   \fill[top color=deepskyblue,middle color=white] (-4,0.5) rectangle (4,6);
   \tikzset{{thang/.pic={{\draw[line width=2pt] (1.05,0.9)--(1.05,-1.5);
     \draw[line width=2pt] (1.4,0.7)--(1.4,-2.3);
     \draw[line width=2pt] (2.1,1)--(2.1,-1.95);
     \draw[line width=1.3pt] (2.15,1.05)--(3.5,-1.55)foreach \i in{{0,1,2,...,4}}{{coordinate[pos=\i/4](A\i)}};
     \draw[line width=1.3pt] (2.1,0.7)--(3.5,-2.15)foreach \i in{{0,1,2,...,4}}{{coordinate[pos=\i/4](B\i)}};
     \foreach \i in{{0,1,...,4}}
     \draw[line width=1.3pt] (A\i)--(B\i);
     \draw[line width=1.3pt] (1.9,1)--(3.5,-2.2)foreach \i in{{0,1,2,...,13}}{{coordinate[pos=\i/13](C\i)}};
     \draw[line width=1.3pt] (1.45,0.8)--(3.1,-2.45)foreach \i in{{0,1,2,...,13}}{{coordinate[pos=\i/13](D\i)}};
     \foreach \i in{{0,1,...,13}}
     \draw[line width=2pt] (C\i)--(D\i);
     \draw[fill=gray!60]  (0,1)--(1.2,1.6)--(2.2,1.05)--(1.4,0.7)--(1.05,0.9)--(0.6,0.7)--cycle;
     \draw[fill=gray] (1.05,0.9)--(1.4,0.7)--(2.2,1.05)--(2.2,0.95)--(1.4,0.6)--(1.05,0.8);
     \draw[fill=cyan!20,line width=1.3pt] (0,1)--(0,1.7)--(1.2,2.3)--(1.2,1.6)(1.2,2.3)--(2.2,1.75)--(2.2,1.05)--(1.2,1.6)(1.4,0.7)--(1.4,1.4)--(1.05,1.6)--(1.05,0.9)--(1.05,1.6)--(1.05,0.9)(0.6,0.7)--(0.6,1.4)--(1.05,1.6)--(1.05,0.9);}}}}
 \tikzset{{mangtruot/.pic={{
   \draw[line width=0.1pt,fill=cyan!50] (0.9,-2.65)..controls++(110:0.75)and++(-100:1.5)..(-1.78,0)--(-1.8,0)..controls++(-120:1.5)and++(130:0.75)..(0.85,-2.8);
   \draw[line width=0.1pt,fill=cyan!50!black] (0.5,-3)..controls++(120:0.65)and++(-100:1.5)..(-2.3,0)..controls++(-120:1.5)and++(130:0.75)..(0.5,-3.2);
   \draw[line width=0.1pt,fill=cyan!50] (-2.3,0)..controls++(70:1.15)and++(170:1)..(0.15,0.97)..controls++(180:1)and++(90:1.25)..(-2.19,-0.75)..controls++(110:0.25)and++(-110:0.2)..(-2.3,0);
   \draw[line width=0.1pt,fill=cyan!50] (2.4,0)..controls++(-100:0.5)and++(10:0.5)..(1.5,-0.78)..controls++(-10:0.5)and++(-50:1)..(2.3,0.3);
   \draw[line width=0.1pt,fill=cyan!90!brown] (-1.3,0.95)..controls++(40:0.7)and++(50:2.5)..(2.5,-0.47)..controls++(60:1.1)and++(0:1.3)..(0.15,0.97);
   \draw[line width=0.1pt,fill=cyan!70!brown] (2.82,0.3)..controls++(-90:1.7)and++(-85:1)..(-0.82,0.15)..controls++(-120:1.7)and++(-60:2.3)..(2.82,0.3);
   \draw[line width=0.1pt,fill=cyan!50] (-0.39,0.11)..controls++(-110:0.15)and++(163:0.5)..(0.15,-0.63)..controls++(170:0.9)and++(-145:0.15)..(-0.4,0.11);
   \draw[line width=0.1pt,fill=cyan!50!black] (-1.8,0)..controls++(70:1.65)and++(90:1)..(2.4,0)..controls++(90:0.9)and++(70:1.3)..(-1.78,0);
   \draw[line width=0.1pt,fill=cyan!50!black] (-0.4,0.1)..controls++(70:0.15)and++(-115:1.3)..(1.7,2.3)--(1.9,2.3)..controls++(-110:1.3)and++(70:0.13)..(-0.38,0.1);
   \draw[line width=0.1pt,fill=cyan!50] (-0.82,0.15)..controls++(120:0.1)and++(-130:0.4)..(1.25,2.5)..controls++(-90:0.5)and++(110:0.3)..(-0.77,-0.05);
   \fill[white](1.25,2.5)..controls++(-90:0.5)and++(110:0.3)..(-0.75,0)..controls++(-70:0.3)and++(140:0.1)..(-0.5,-0.3)..controls++(100:0.3)and++(-120:0.1)..(-0.4,0.1)..controls++(70:0.15)and++(-115:1.3)..(1.7,2.3);
   \fill[white](0.85,-2.8)..controls++(130:0.75)and++(-120:1.5)..(-1.8,0)..controls++(80:0.25)and++(-165:0.4)..(-1,0.75)..controls++(180:0.4)and++(90:0.83)..(-2.19,-0.75)..controls++(-75:0.8)and++(130:0.75)..(0.5,-3);
   \fill[white](1,0.9)..controls++(0:1)and++(40:0.9)..(2.4,-0.5)..controls++(60:0.9)and++(-12:0.7)..(1,0.9);
 }}}}
 \tikzset{{Cay/.pic={{ \draw[fill=green!70!black] (-1.45,-3.4)..controls++(-110:1.5) and++(-80:1.5)..(-5.1,-3.6)..controls++(-160:2)and++(-150:1.5)..(-7.9,-1)..controls++(120:0.5)and++(-110:0.5)..(-7.9,0.5)..controls++(120:1)and++(-110:1.5)..(-8,3)..controls++(150:2.5)and++(150:2)..(-6,6)..controls++(140:1.5)and++(180:1)..(-5,7.8)..controls++(120:2.5)and++(130:2)..(-1.5,9.3)..controls++(90:2)and++(150:1.5)..(1,10.3)..controls++(50:1.3)and++(120:1.8)..(4,9)..controls++(30:2)and++(50:1.5)..(6,7)..controls++(-20:2)and++(30:1.5)..(6,4.7)..controls++(20:2)and++(70:1)..(7,3)..controls++(-70:0.5)and++(70:0.5)..(7,2)..controls++(-30:2.5)and++(10:2.5)..(6,-1)..controls++(-80:2)and++(-30:2)..(2.6,-2)..controls++(-45:2)and++(-50:2.5)..(-1.45,-3.4);
   \draw[fill=brown!70!black] (-5,-11)..controls++(20:4) and++(-40:1.5)..(-1.5,-3.4)..controls++(140:0.5)and++(-90:1.5)..(-4,-1)..controls++(-40:0.7)and++(150:0.3)..(-3,-1.7)..controls++(110:0.8)and++(-120:0.5)..(-3,0)..controls++(-100:0.5)and++(160:1)..(-1.5,-2)..controls++(6:0.5)and++(-80:0.5)..(-1,-0.5)..controls++(0:2)and++(-90:0.7)..(0.3,0.9)..controls++(20:1)and++(-50:0.7)..(1,2.8)..controls++(60:1)and++(-70:1)..(1.5,4)..controls++(-20:2)and++(120:1)..(1.5,-0.5)..controls++(20:1.5)and++(-110:1)..(3.5,2.3)..controls++(-70:0.3)and++(70:0.5)..(3.5,1)..controls++(-90:0.3)and++(-90:0.3)..(5,1)..controls++(-90:0.7)and++(90:0.4)..(1.5,-2.3)..controls++(-100:0.5)and++(150:2.5)..(2,-9.7)..controls++(-30:0.5)and++(180:0.3)..(4.5,-10.5)..controls++(-150:0.7)and++(-70:0.7)..(0.3,-10.5) ..controls++(-80:0.8)and++(70:0.5)..(0,-12)..controls++(130:2)and++(0:3)..(-5,-11);
 }}}}
 \tikzset{{hoadao/.pic={{\draw[fill=darkpastelgreen!60] (1.8,-0.87)..controls++(-80:1.5)and++(-170:1)..(4.9,-2)..controls++(-10:0.55)and++(180:1.4)..(6.9,-2.3)..controls++(120:0.5)and++(-60:0.7)..(5.9,-0.7)..controls++(-160:0.4)and++(-60:0.4)..(4.55,-0.45)..controls++(-130:1.3)and++(-20:1)..(1.8,-0.85);
   \draw[fill=darkpastelgreen!60](1.45,-0.5)..controls++(-150:0.9)and++(-60:0.5)..(-0.5,-0.3)..controls++(130:1.3)and++(-90:1)..(-1.4,2.5)..controls++(-20:0.3)and++(90:2.2)..(1.45,-0.5);
   \draw[fill=carnationpink] (1.2,0.8)..controls++(-110:1.7) and++(-130:2)..(4.55,-0.45)..controls++(-40:2.5)and++(-10:2.3)..(6.5,3.1)..controls++(50:2)and++(50:2.3)..(4.5,5.75)..controls++(110:3)and++(130:2.3)..(0.5,4.5)..controls++(180:2)and++(180:2.3)..(1.2,0.8);
   \draw [fill=brinkpink] (2.6,2.5)..controls++(-70:0.3) and++(160:0.3)..(3.1,2)..controls++(-110:1.3)and++(170:0.8)..(3.3,0.15)..controls++(10:0.8) and++(-80:1.3)..(3.8,2)..controls++(20:0.3)and++(-150:0.3)..(4.1,2.15)..controls++(-60:1)and++(-140:0.5)..(5.8,1.5)..controls++(40:0.5)and++(-10:1)..(4.4,2.9)..controls++(80:0.3)and++(-70:0.3)..(4.35,3.3)..controls++(20:1.3)and++(-70:0.5)..(5.5,4.5)..controls++(130:0.5)and++(55:1)..(4,3.8)..controls++(160:0.3)and++(20:0.3)..(3.3,3.83)..controls++(80:0.7)and++(10:0.35)..(2.4,5.1)..controls++(-150:1)and++(115:1.3)..(2.8,3.6)..controls++(-120:0.3)and++(90:0.3)..(2.55,3.1)..controls++(175:1)and++(90:0.65)..(1,2.6)..controls++(-80:0.8)and++(-170:1)..(2.6,2.5);
   \draw [fill=brightmaroon] (3.2,2.6)..controls++(-80:0.1)and++(-100:0.1)..(3.6,2.45)..controls++(70:0.3)and++(-90:1)..(4.27,5)..controls++(-165:0.1)and++(-10:0.1)..(3.5,4.9)..controls+(-80:1)and++(70:0.3)..(3.2,2.6);
   \draw[fill=canaryyellow] (3.05,6.5)..controls++(70:0.5)and++(110:0.5)..(4.35,6.6)..controls++(-80:0.3)and++(100:0.3)..(4.5,5.29)..controls++(-100:0.4)and++(-50:0.44)..(3.2,5.1)..controls++(100:0.3)and++(-80:0.3)..(3.05,6.5);}}}}
 \path (-1.07,1.5)pic[scale=0.2]{{Cay}};
 \path (1.07,1.5)pic[scale=0.12]{{Cay}};
 \path (2.7,1)pic[scale=0.12]{{Cay}};
 \path (-2.5,0)pic[scale=0.05]{{hoadao}};
 \path (-2,0.3)pic[scale=0.05]{{hoadao}};
 \path (0,0)pic[scale=0.85]{{thang}};
 \path (-1.07,-1.3)pic[scale=0.85]{{mangtruot}};
 \end{{tikzpicture}}


 \begin{{tikzpicture}}[scale=0.7, font=\normalsize, line join=round, line cap=round, >=stealth,color=red!70!black,line width=1pt]
  \path 
  (0,0) coordinate (O)
  (-3,-3) coordinate (x)
  (5,0) coordinate (y)
  (0,5) coordinate (z)
  (0,3) coordinate (A)
  (3,-2) coordinate (B)
  (-2,-1) coordinate (C)
  ;
  \draw[thick,->] (O)--(x);\draw[thick,->] (O)--(y);\draw[thick,->] (O)--(z);
  \draw[very thick] (A)..controls +(170:1)and +(120:2)..(C);
  
  \draw[very thick] (C)..controls +(-60:3)and +(-120:1)..  (B);
  \foreach \x/\g in{{A/0, B/-45, C/210}}
  \fill[black](\x)circle(2pt)($(\x)+(\g:4mm)$)node{{$\x$}};
  \foreach \x/\g in{{x/-120, y/0, z/90}}
  \fill[black](\x)circle(.2pt)($(\x)+(\g:3mm)$)node{{$\x$}};
 \end{{tikzpicture}}

Tính độ dài máng trượt đó (kết quả làm tròn đến hàng đơn vị)."""

    sol = rf"""Ta có $AB = \sqrt{{{AB2}}}$, $AC = \sqrt{{{AC2}}}$, $BC = \sqrt{{{BC2}}}${can_text}.

Diện tích $S_{{ABC}} \approx {S:.5f}$.

Bán kính đường tròn ngoại tiếp của tam giác $ABC$ là $R = \frac{{AB \cdot BC \cdot CA}}{{4S_{{ABC}}}} \approx {R:.5f}$.

Theo định lý cosin, ta có $\cos B = \frac{{AB^2 + BC^2 - AC^2}}{{2 \cdot AB \cdot BC}} \approx {cosB:.5f} \Rightarrow \alpha = \widehat{{ABC}} \approx {alpha:.5f} \text{{ rad.}}$

Góc $\alpha$ là góc nội tiếp chắn cung $AC$ (không qua $B$) của đường tròn ngoại tiếp $ABC$.
Suy ra số đo của góc chắn cung $ABC$ là $\beta = 2\pi - 2\alpha$.

Độ dài cung $ABC$ là $l = \beta R = (2\pi - 2\alpha) \cdot R \approx {length:.3f} \approx {ans_val}$."""

    return stem, sol, str(ans_val)

def main():
    num_questions = 1
    
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    seed_val = None
    if len(sys.argv) > 2:
        seed_val = int(sys.argv[2])

    questions_content = ""
    answers = []

    for i in range(num_questions):
        seed = seed_val + i if seed_val is not None else None
        q, s, a = generate_question(seed)
        answers.append(a)
        ans_str = str(a)
        questions_content += f"Câu {i + 1}: {q}\n\nLời giải:\n\n{s}\n\nĐáp án: {ans_str}\n\n"

    latex_document = rf"""\documentclass[a4paper,12pt]{{article}}
\usepackage{{amsmath, amsfonts, amssymb}}
\usepackage{{geometry}}
\geometry{{a4paper, margin=1in}}
\usepackage{{fontspec}}
\usepackage{{polyglossia}}
\setmainlanguage{{vietnamese}}
\usepackage{{tikz}}
\usetikzlibrary{{calc,angles,quotes,patterns,shapes.geometric}}

\begin{{document}}

{questions_content}

\end{{document}}"""

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "cau_5_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(latex_document)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, ans in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {ans}")

if __name__ == "__main__":
    main()
