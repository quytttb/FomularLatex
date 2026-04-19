import math
import os
import random
import sys
from fractions import Fraction
from typing import Optional

def format_frac_tex(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    if f.numerator < 0:
        return f"-\\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"
    return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"

def format_sqrt(val: int) -> str:
    root = math.isqrt(val)
    if root * root == val:
        return str(root)
    for i in range(root, 1, -1):
        if val % (i * i) == 0:
            rem = val // (i * i)
            return f"{i}\\sqrt{{{rem}}}"
    return f"\\sqrt{{{val}}}"

SEED_DE_MAU = 1

def generate_question(seed: Optional[int] = None):
    if seed is not None:
        random.seed(seed)

    pythagorean_pairs = [
        (15, 20), (20, 15), (30, 40), (40, 30), 
        (24, 10), (10, 24), (12, 16), (16, 12),
        (21, 28), (28, 21), (18, 24), (24, 18)
    ]

    if seed == SEED_DE_MAU:
        h1, h2, h3 = 10, 15, 20
        x2, y3 = 30, 40
    else:
        h1 = random.choice([10, 12, 15, 18, 20])
        h2 = random.choice([15, 18, 20, 24, 25])
        h3 = random.choice([15, 16, 20, 25, 30])
        x2, y3 = random.choice(pythagorean_pairs)

    d12 = x2
    d23 = int(math.hypot(x2, y3))

    xA_frac = Fraction(x2 * h1, h1 + h2)
    xA_val = float(xA_frac)
    
    yB_frac = Fraction(y3 * h1, h1 + h3)
    yB_val = float(yB_frac)

    T1_sq = x2**2 + (h1 + h2)**2
    T2_sq = y3**2 + (h1 + h3)**2
    
    T1 = math.sqrt(T1_sq)
    T2 = math.sqrt(T2_sq)

    T_sum = T1 + T2
    S_val = xA_val + yB_val + T_sum
    ans_rounded = round(S_val)

    # String format
    T1_tex = format_sqrt(T1_sq)
    T2_tex = format_sqrt(T2_sq)
    
    if T1_tex.isdigit() and T2_tex.isdigit():
        T_expr_tex = f"{int(T1_tex) + int(T2_tex)}"
    elif T2_tex.isdigit() and not T1_tex.isdigit():
        T_expr_tex = f"{T2_tex} + {T1_tex}"
    else:
        T_expr_tex = f"{T1_tex} + {T2_tex}"

    xA_tex = format_frac_tex(xA_frac)
    yB_tex = format_frac_tex(yB_frac)
    
    ans_S_tex = f"{S_val:.4f}".replace(".", ",")

    tikz_code = r"""\begin{center}
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.8,color=red!75!black,line width=1pt]
   \draw 
   (0,0) coordinate (O) 
   (6,0) coordinate (y)
   (-3,-3) coordinate (x)  
   (0,4) coordinate (z) 
   ($(O)!0.5!(z)$) coordinate (C1) 
   ($(O)!0.8!(y)$) coordinate (B1) ($(B1)+(0,3)$) coordinate (B11)
   ($(O)!0.5!(B1)$) coordinate (B)
   ($(O)!0.8!(x)$) coordinate (A1) ($(A1)+(0,1.5)$) coordinate (A11)
   ($(O)!0.5!(A1)$) coordinate (A)
   ;
   \draw[dashed] (A11)--(A)--(C1)--(B)--(B11);
   \draw[->] (O)--(x);\draw[->] (O)--(y);\draw[->] (O)--(z);
   \draw[line width=4pt] 
   (A1)--(A11)(B1)--(B11) (O)--(C1)
   ;
   \draw (A11) node[above]{cột 2};
   \draw (B11) node[above]{cột 3};
   \draw (C1) node[above right]{cột 1};
   \foreach \p/\r in {A/-40,B/-90,O/-90,x/90,y/90,z/0}
   \fill (\p) circle (1.2pt) node[shift={(\r:3mm)}]{$\p$};
   
%   \draw (0,1) node[opacity=0.3]{FB: Tan Hoang Trong};
  \end{tikzpicture}
\end{center}"""

    question = rf'''Nhân ngày liên hoan năm học mới, các nhân viên dùng dây thừng có gắn cờ đủ màu sắc để trang trí. Trong không gian $Oxyz$, mỗi đơn vị trên trục tọa độ là mét, mặt phẳng $(Oxy)$ là mặt đất, trục $Oz$ hướng lên trời. Có ba cây cột được cắm trên sân trường. Trong đó:
\begin{{itemize}}
    \item Chân của cột 1 (chiều cao {h1} m) nằm ở gốc tọa độ.
    \item Chân của cột 2 (chiều cao {h2} m) nằm trên trục $Ox$.
    \item Chân của cột 3 (chiều cao {h3} m) nằm trên trục $Oy$ (như hình vẽ).
    \item Khoảng cách từ cột 1 đến cột 2 là {d12} m và khoảng cách từ cột 2 đến cột 3 là {d23} m.
\end{{itemize}}
Để trang trí cho ngày lễ, người ta sẽ:
\begin{{itemize}}
    \item Nối dây từ đỉnh cột 2 xuống mặt đất rồi lại nối lên đỉnh cột 1.
    \item Từ đỉnh cột 1 kéo dây nối xuống mặt đất rồi nối tiếp lên đỉnh cột 3.
\end{{itemize}}
Gọi $A(x, y, z)$ và $B(a, b, c)$ là hai vị trí chạm đất của dây thừng để tổng chiều dài dây ngắn nhất. Gọi $T$ là tổng chiều dài sợi dây ngắn nhất sau khi nối từ đỉnh cột 2 đến đỉnh cột 3. Tính giá trị $x + y + z + a + b + c + T$.
(Không làm tròn các giá trị trung gian, chỉ làm tròn kết quả cuối cùng đến hàng đơn vị).
{tikz_code}'''

    solution = rf'''Theo giả thiết:\\
Chân cột 1 là $O(0;0;0) \Rightarrow$ Đỉnh cột 1 là $M_1(0; 0; {h1})$.\\
Chân cột 2 nằm trên $Ox$, cách cột 1 $d_{{12}} = {d12}$ m nên chân cột 2 là $C_2({d12}; 0; 0)$.\\
$\Rightarrow$ Đỉnh cột 2 là $M_2({d12}; 0; {h2})$.\\
Chân cột 3 nằm trên $Oy$ là $C_3(0; y_3; 0)$. Ta có khoảng cách giữa chân cột 2 và chân cột 3 là ${d23}$ m $\Rightarrow {d12}^2 + y_3^2 = {d23}^2 \Rightarrow y_3^2 = {d23}^2 - {d12}^2 = {y3**2} \Rightarrow y_3 = {y3}$ (dựa vào hình vẽ ta thấy $y_3 > 0$).\\
$\Rightarrow$ Đỉnh cột 3 là $M_3(0; {y3}; {h3})$.\\

Hai điểm chạm đất là $A(x; y; z)$ nằm trong mặt phẳng $(Oxy)$ nên $A(x; y; 0)$ và $B(a; b; c)$ nằm trong $(Oxy)$ nên $B(a; b; 0)$.\\
Tổng chiều dài sợi dây là $L = (M_2A + AM_1) + (M_1B + BM_3)$.\\
Tổng này nhỏ nhất khi cả hai cụm $(M_2A + AM_1)$ và $(M_1B + BM_3)$ đều nhỏ nhất.\\

Xét $(M_2A + AM_1)$ cực tiểu:\\
Điểm $M_1, M_2$ nằm cùng phía so với mặt phẳng $(Oxy)$.\\
Gọi $M_1'$ là điểm đối xứng của $M_1$ qua $(Oxy)$, ta có $M_1'(0; 0; -{h1})$.\\
Ta có $M_2A + AM_1 = M_2A + AM_1' \ge M_2 M_1'$.\\
Dấu bằng xảy ra khi $A = M_2 M_1' \cap (Oxy)$.\\
Ta có $\overrightarrow{{M_2 M_1'}} = (-{d12}; 0; -{h1+h2})$.\\
Phương trình đường thẳng $M_2 M_1'$ là:
$$ \begin{{cases}} X = {d12} - {d12}t \\ Y = 0 \\ Z = {h2} - {h1+h2}t \end{{cases}} $$
Giao điểm $A$ với $(Oxy)$ ứng với $Z=0 \Rightarrow {h2} - {h1+h2}t = 0 \Rightarrow t = \frac{{{h2}}}{{{h1+h2}}}$.\\
Suy ra $x_A = {d12} - {d12}\cdot \frac{{{h2}}}{{{h1+h2}}} = {xA_tex}$, $y_A = 0, z_A = 0 \Rightarrow A\left({xA_tex}; 0; 0\right)$.\\
Lúc này $(M_2A + AM_1)_{{\min}} = M_2 M_1' = \sqrt{{(-{d12})^2 + 0^2 + (-{h1+h2})^2}} = {T1_tex}$.\\

Xét $(M_1B + BM_3)$ cực tiểu:\\
Tương tự, gọi $M_3'$ là điểm đối xứng của $M_3$ qua $(Oxy)$, ta có $M_3'(0; {y3}; -{h3})$.\\
Ta có $M_1B + BM_3 = M_1B + BM_3' \ge M_1 M_3'$.\\
Dấu bằng xảy ra khi $B = M_1 M_3' \cap (Oxy)$.\\
Ta có $\overrightarrow{{M_1 M_3'}} = (0; {y3}; -{h1+h3})$.\\
Phương trình đường thẳng $M_1 M_3'$ là:
$$ \begin{{cases}} X = 0 \\ Y = {y3}t \\ Z = {h1} - {h1+h3}t \end{{cases}} $$
Giao điểm $B$ với $(Oxy)$ ứng với $Z=0 \Rightarrow {h1} - {h1+h3}t = 0 \Rightarrow t = \frac{{{h1}}}{{{h1+h3}}}$.\\
Suy ra $x_B=0, y_B = {y3}\cdot \frac{{{h1}}}{{{h1+h3}}} = {yB_tex}, z_B=0 \Rightarrow B\left(0; {yB_tex}; 0\right)$.\\
Lúc này $(M_1B + BM_3)_{{\min}} = M_1 M_3' = \sqrt{{0^2 + {y3}^2 + (-{h1+h3})^2}} = {T2_tex}$.\\

Tổng chiều dài dây ngắn nhất:\\
$$ T = M_2 M_1' + M_1 M_3' = {T_expr_tex} $$
Khi đó $x = {xA_tex}, y = 0, z = 0, a = 0, b = {yB_tex}, c = 0$.\\
Suy ra $S = x + y + z + a + b + c + T = {xA_tex} + {yB_tex} + {T_expr_tex} \approx {ans_S_tex}$.\\
Vậy kết quả làm tròn đến hàng đơn vị là {ans_rounded}.'''

    return question, solution, str(ans_rounded)

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
    output_file = os.path.join(out_dir, "example_5.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, a in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {a}")

if __name__ == "__main__":
    main()
