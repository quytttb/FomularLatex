import math
import os
import sys
import random

def generate_question(idx=1):
    w = random.choice([3, 6, 9, 12, 15]) # AB
    d = random.choice([3, 6, 9, 12, 15]) # AD
    h = random.choice([4, 6, 8, 10, 12, 14]) # cạnh bên
    
    # Đảm bảo bài không bị tầm thường (cạnh đáy không nên bằng nhau để dễ phân biệt a,b)
    while w == d:
        d = random.choice([3, 6, 9, 12, 15])
        
    c1 = random.choice([3, 6, 9])
    c2 = random.choice([3, 6, 9])
    
    a_val = d / 3.0
    b_val = w / 3.0
    
    T_sq = (-d)**2 + (w/2.0)**2 + (3*h/2.0)**2
    T = math.sqrt(T_sq)
    
    D_val = c1 * a_val + c2 * b_val + T
    D_round = round(D_val, 1)
    D_round_str_dot = f"{D_round:.1f}"
    D_round_str_comma = D_round_str_dot.replace(".", ",")
    
    def format_val(val):
        if val.is_integer():
            return f"{int(val)}"
        else:
            return f"{val:.2f}".replace('.', ',')
            
    a_str = format_val(a_val)
    b_str = format_val(b_val)
    
    tikz_fig = r"""\begin{center}
\begin{tikzpicture}[line join=round, line cap=round, scale=1,color=red!75!black,line width=1pt]
    % Định nghĩa các tọa độ
    \coordinate (A) at (0,0);
    \coordinate (B) at (3,0.8);
    \coordinate (C) at (7,0.8);
    \coordinate (D) at (4,0);
    
    \coordinate (E) at (0,3);
    \coordinate (F) at (3,3.8);
    \coordinate (G) at (7,3.8);
    \coordinate (H) at (4,3);

    % Tô màu mặt đáy ABCD
    \fill[red!30] (A) -- (B) -- (C) -- (D) -- cycle;

    % Vẽ các cạnh khuất (nét đứt)
    \draw[dashed] (A) -- (B) -- (C);
    \draw[dashed] (B) -- (F);
    \draw[dashed] (A) -- (F) node[midway, left] (M) {};
    
    % Vẽ điểm M trên đoạn AF (trung điểm)
    \fill (1.5, 1.9) circle (1pt) node[left] {$M$};

    % Vẽ các cạnh nhìn thấy
    \draw[thick] (E) -- (F) -- (G) -- (H) -- cycle; % Mặt trên
    \draw[thick] (A) -- (D) -- (C); % Các cạnh đáy trước
    \draw[thick] (A) -- (E); % Cạnh đứng trái
    \draw[thick] (D) -- (H); % Cạnh đứng giữa
    \draw[thick] (C) -- (G); % Cạnh đứng phải

    % Gán nhãn các đỉnh
    \node[left] at (A) {$A$};
    \node[above right] at (B) {$B$};
    \node[right] at (C) {$C$};
    \node[below] at (D) {$D$};
    \node[above] at (E) {$E$};
    \node[above] at (F) {$F$};
    \node[above] at (G) {$G$};
    \node[above] at (H) {$H$};
\end{tikzpicture}
\end{center}"""

    question = rf"""Một bể cá đầy nước có dạng hình hộp chữ nhật $ABCD.EFGH$ với $AB = {w}\text{{ (dm)}}$, $AD = {d}\text{{ (dm)}}$ và cạnh bên bằng ${h}\text{{ (dm)}}$. Một chú cá con bơi theo những đoạn thẳng từ điểm $G$ đến chạm mặt đáy của hồ, rồi từ điểm đó bơi đến vị trí điểm $M$ là trung điểm của $AF$ được mô hình hóa như hình vẽ sau:
{tikz_fig}

Để đường đi ngắn nhất là $T$ thì chú cá bơi đến điểm dưới đáy hồ cách $BA$ và $BC$ những đoạn bằng $a$ và $b$. Khi đó tổng $D = {c1}a + {c2}b + T$ bằng bao nhiêu (làm tròn đến chữ số thập phân thứ nhất)?"""

    solution = rf"""Gắn hệ trục tọa độ $Oxyz$ sao cho gốc $O \equiv B(0;0;0)$. 
Vì đáy $ABCD$ là hình chữ nhật nên tia $BC \perp BA$. Ta chọn tia $BC$ trùng với tia $Ox$, tia $BA$ trùng với tia $Oy$, và tia $BF$ trùng với tia $Oz$.
Khi đó ta có toạ độ các đỉnh là:
$B(0; 0; 0)$
$C({d}; 0; 0)$ (do $AD = BC = {d}$)
$A(0; {w}; 0)$ (do $AB = {w}$)
$F(0; 0; {h})$ (nằm ngay trên $B$)
$G({d}; 0; {h})$ (nằm ngay trên $C$)

Trung điểm $M$ của $AF$ có tọa độ:
$M\left( \dfrac{{0+0}}{{2}}; \dfrac{{{w}+0}}{{2}}; \dfrac{{0+{h}}}{{2}} \right) = \left(0; {w/2:.1f}; {h/2:.1f}\right)$.

Giả sử chú cá bơi từ $G$ đến điểm $K(x; y; 0)$ thuộc mặt đáy $(Oxy)$, rồi từ $K$ đến $M$. 
Tổng quãng đường bơi là $S = GK + KM$.
Lấy điểm $G'$ đối xứng với $G$ qua mặt phẳng $(Oxy)$. Suy ra $G'({d}; 0; -{h})$.
Đường đi là $T = \min(GK + KM) = \min(G'K + KM)$. 
Theo bất đẳng thức tam giác, $G'K + KM \ge G'M$. Dấu bằng xảy ra khi $G', K, M$ thẳng hàng, hay $K$ chính là giao điểm của đường thẳng đoạn $G'M$ với mặt phẳng $(Oxy)$.

Tính véctơ $\overrightarrow{{G'M}} = (0 - {d}; {w/2:.1f} - 0; {h/2:.1f} - (-{h})) = (-{d}; {w/2:.1f}; {3*h/2:.1f})$.
Phương trình tham số của đường thẳng $G'M$ là:
$$ \begin{{cases}} x = {d} - {d}t \\ y = {w/2:.1f}t \\ z = -{h} + {3*h/2:.1f}t \end{{cases}} $$
Giao điểm $K \in (Oxy) \Rightarrow z_K = 0 \Rightarrow -{h} + {3*h/2:.1f}t = 0 \Rightarrow t = \dfrac{{2}}{{3}}$.

Thay giá trị $t = \\dfrac{{2}}{{3}}$ vào phương trình $x, y$ của đường thẳng:\\
$x_K = {d} - {d} \\cdot \\dfrac{{2}}{{3}} = {d/3:.2f}$\\
$y_K = {w/2:.1f} \\cdot \\dfrac{{2}}{{3}} = {w/3:.2f}$
Vậy toạ độ điểm chạm đáy là $K\left( {d/3:.2f}; {w/3:.2f}; 0 \right)$.

Theo cách gắn hệ trục, khoảng cách từ $K$ đến $BA$ (thuộc trục $Oy$) chính là hoành độ $|x_K|$, và khoảng cách từ $K$ đến $BC$ (thuộc trục $Ox$) chính là tung độ $|y_K|$.
Do tọa độ $K$ dương, suy ra $a = x_K = {a_str}$ và $b = y_K = {b_str}$.

Giá trị nhỏ nhất của quãng đường bơi là đoạn $G'M$:
$T = G'M = \sqrt{{(-{d})^2 + ({w/2:.1f})^2 + ({3*h/2:.1f})^2}} = \sqrt{{{d**2} + {w**2/4} + {9*h**2/4}}} = \sqrt{{{T_sq}}}$.

Ta tính tổng $D$:
$D = {c1} \cdot a + {c2} \cdot b + T = {c1} \cdot {a_str} + {c2} \cdot {b_str} + \sqrt{{{T_sq}}} \approx {D_round_str_comma}$.

Vậy giá trị cần tìm là ${D_round_str_comma}$."""

    # We use a standard f-string here so that backslashes in \begin{ex} stay single unless doubled
    return question, solution, D_round_str_comma, D_round_str_dot

def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    content = ""
    answers = []
    for i in range(num_questions):
        q, s, a_comma, a_dot = generate_question(i + 1)
        ans_pair = f"{a_comma} | {a_dot}"
        answers.append(ans_pair)
        content += f"\\begin{{ex}}%Câu {i+1}\n{q}\n\n\\shortans{{{ans_pair}}}\n\\loigiai{{\n{s}\n}}\n\\end{{ex}}\n\n"
    
    tex_content = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage{{amsmath,amssymb,fancyhdr}}
\\usepackage{{tikz}}
\\usetikzlibrary{{angles,patterns,calc,arrows,intersections}}
\\usepackage{{polyglossia}}
\\setdefaultlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{{geometry}}
\\usepackage[solcolor]{{ex_test}}
\\newcommand{{\\heva}}[1]{{\\left\\{{\\begin{{aligned}}#1\\end{{aligned}}\\right.}}
\\begin{{document}}
{content}
\\end{{document}}
"""

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "swimming_fish_path_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)
    
    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, a in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {a}")

if __name__ == "__main__":
    main()
