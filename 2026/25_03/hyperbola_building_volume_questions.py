import math
import random
import sys
import os
from fractions import Fraction

def format_frac_tex(f):
    if f.denominator == 1:
        return str(f.numerator)
    if f.numerator < 0:
        return f"-\\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"
    return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"

def get_volume(a, b, L_y, H_mid, H_end):
    k_p = (H_end - H_mid) / (L_y**2)
    tan_T = L_y / b
    sec_T = math.sqrt(1 + tan_T**2)
    
    term1 = 0.5 * (sec_T * tan_T + math.log(sec_T + tan_T))
    term2 = 0.25 * (sec_T**3) * tan_T - 0.25 * term1
    
    I = k_p * (b**2) * term2 + H_mid * term1
    V = (8 * a * b / 3) * I
    return V

def generate_question(seed=None):
    if seed is not None:
        random.seed(seed)
        
    while True:
        L_y = random.choice([20, 30, 40, 50])
        a = random.choice([10, 20, 30])
        k = random.choice([1, 2, 3, 0.5, 1.5])
        
        b = L_y / k
        if b != int(b):
            continue
        b = int(b)
        
        H_mid = random.choice([40, 50, 60, 70, 80])
        H_end = H_mid + random.choice([10, 20, 30, 40])
        
        if k == 1:
            MN_str = f"{2*a}\\sqrt{{2}}"
            W_str = f"{a}\\sqrt{{2}}"
            W_sq = 2 * a**2
        elif k == 2:
            MN_str = f"{2*a}\\sqrt{{5}}"
            W_str = f"{a}\\sqrt{{5}}"
            W_sq = 5 * a**2
        elif k == 3:
            MN_str = f"{2*a}\\sqrt{{10}}"
            W_str = f"{a}\\sqrt{{10}}"
            W_sq = 10 * a**2
        elif k == 0.5:
            MN_str = f"{a}\\sqrt{{5}}"
            W_str = f"{a//2}\\sqrt{{5}}"
            W_sq = 5 * (a//2)**2
        elif k == 1.5:
            MN_str = f"{a}\\sqrt{{13}}"
            W_str = f"{a//2}\\sqrt{{13}}"
            W_sq = 13 * (a//2)**2
            
        V = get_volume(a, b, L_y, H_mid, H_end)
        V_1000 = V / 1000
        ans = round(V_1000, 1)
        
        if ans > 0:
            break

    ans_dot = f"{ans:.1f}"
    ans_comma = ans_dot.replace(".", ",")
    ans_str = f"{ans_comma} | {ans_dot}"
    
    k_p_frac = Fraction(H_end - H_mid, L_y**2)
    k_p_str = format_frac_tex(k_p_frac)
    
    frac_4a_3 = format_frac_tex(Fraction(4*a, 3))
    
    V_exact_str = f"{V:.3f}".replace(".", ",")
    
    question = f"""Một tòa nhà trong không gian $Oxyz$ có mặt sàn nằm trong mặt phẳng $(Oxy)$ là hình hypebol có chiều dài $AB = {2*L_y}$ m, chỗ hẹp nhất $CD = {2*a}$ m và chỗ rộng nhất $MN = PQ = {MN_str}$ m. Các điểm trên đỉnh tòa nhà là $E, F$ và $S$ nằm trên tia $Oz$, $AE = BF = {H_end}$ m, $OS = {H_mid}$ m. Thiết diện của tòa nhà khi cắt bởi mặt phẳng vuông góc với $AB$ là hình parabol. Đường cong $ESF$ là một phần của parabol. Tính thể tích của tòa nhà theo đơn vị $1000 \\text{{ m}}^3$, làm tròn kết quả đến hàng phần chục.

\\begin{{center}}
\\begin{{tikzpicture}}[line join = round, line cap=round,>=stealth,font=\\footnotesize,scale=1,color=red!75!black, line width=1pt]
   \\foreach \\p/\\x/\\y in {{
    M/-1.8/-0.5,
    N/-0.4/-1.9,
    Q/1.9/0.4,
    A/-1.2/-1.1,
    B/1.2/1.1,
    P/0.5/1.8,
    D/0.4/-0.4,
    O/0/0,
    C/-0.4/0.4,
    E/-1.1/3.1,
    S/0/3.2,
    F/1.2/5.4,
    P13/0.8/4.5,
    Z/0/5.9,
    y/-1.7/-1.5,
    x/1.7/-1.7
   }}{{
    \\coordinate (\\p) at (\\x,\\y);
   }}
   
   \\draw (M) -- (N) .. controls +(78.69:0.51) and +(-135:0.707) .. (D) .. controls (0.8,-0) and (1.3,0.2) .. (Q) .. controls +(93.01:1.903) and +(-45:0.2) .. (F) .. controls (1,5.6) and (0.9,5.1) .. (P13) .. controls +(-116.57:0.447) and +(45:0.566) .. (S) .. controls (0.2,3.2) and (0.3,0.8) .. (D);
   \\draw (M) .. controls +(85.91:1.404) and +(135:0.5) .. (E) .. controls (-0.9,2.9) and (-0.6,-0.2) .. (N);
   \\draw (E) .. controls +(-36.87:0.5) and +(-135:0.566) .. (S);
   \\draw (P13) -- (F);
   \\draw [dashed] (Q) -- (P) .. controls +(-111.8:0.539) and +(45:0.566) .. (C) .. controls (-0.776,0.024) and (-1.3,-0.3) .. (M);
   \\draw [dashed] (O) -- (A);
   \\draw [dashed] (O) -- (C) .. controls +(84.29:1.005) and +(180:0.2) .. (S);
   \\draw [dashed] (O) -- (D);
   \\draw [dashed] (P) .. controls +(84.29:1.005) and +(-99.46:0.906) .. (P13);
   \\draw [dashed] (B) -- (F);
   \\draw [dashed] (O) -- (B);
   \\draw [->] (S) -- (Z)node[left]{{$z$}};
   \\draw [->] (A) -- (y)node[left]{{$y$}};
   \\draw [->] (D) -- (x)node[right]{{$x$}};
   \\foreach \\p/\\pos/\\lbl in {{
    M/(180:3mm)/M,
    N/(285:3mm)/N,
    Q/(315:3mm)/Q,
    A/(255:3mm)/A,
    B/(25:3mm)/B,
    P/(25:3mm)/P,
    D/(7:3mm)/D,
    O/(-95:3mm)/O,
    C/(120:3mm)/C,
    E/(125:3mm)/E,
    S/(125:3mm)/S,
    F/(45:3mm)/F
   }}{{
    \\fill (\\p) circle (1.2pt) node[shift=\\pos] {{$\\lbl$}};
   }}
\\end{{tikzpicture}}
\\end{{center}}"""

    solution = f"""Chọn hệ trục tọa độ $Oxyz$ như hình vẽ, với gốc $O$ là trung điểm của $CD$, trục $Oy$ dọc theo $AB$, trục $Ox$ dọc theo $CD$, trục $Oz$ hướng lên trên.

Phương trình đường hypebol trên mặt phẳng $(Oxy)$ có dạng $\\frac{{x^2}}{{a^2}} - \\frac{{y^2}}{{b^2}} = 1$.
Ta có $CD = {2*a} \\Rightarrow 2a = {2*a} \\Rightarrow a = {a}$.
Chiều dài $AB = {2*L_y} \\Rightarrow$ tung độ của $M, N, P, Q$ là $y = \\pm {L_y}$.
Tại $y = {L_y}$, độ rộng $MN = {MN_str} \\Rightarrow 2x = {MN_str} \\Rightarrow x = {W_str}$.
Thay vào phương trình hypebol: 
$$ \\frac{{\\left({W_str}\\right)^2}}{{{a}^2}} - \\frac{{{L_y}^2}}{{b^2}} = 1 \\Rightarrow \\frac{{{W_sq}}}{{{a**2}}} - \\frac{{{L_y**2}}}{{b^2}} = 1 \\Rightarrow b^2 = {b**2} \\Rightarrow b = {b} $$
Vậy phương trình hypebol là: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1 \\Rightarrow x = {a}\\sqrt{{1 + \\frac{{y^2}}{{{b**2}}}}}$.
Độ rộng của mặt sàn tại vị trí $y$ là $2x = {2*a}\\sqrt{{1 + \\frac{{y^2}}{{{b**2}}}}}$.

Phương trình đường parabol $ESF$ trên mặt phẳng $(Oyz)$ có dạng $z = ky^2 + c$.
Đỉnh $S$ có $OS = {H_mid} \\Rightarrow c = {H_mid}$.
Tại $y = {L_y}$, $z = AE = {H_end} \\Rightarrow k \\cdot {L_y}^2 + {H_mid} = {H_end} \\Rightarrow {L_y**2}k = {H_end - H_mid} \\Rightarrow k = {k_p_str}$.
Vậy phương trình parabol là: $z = {k_p_str}y^2 + {H_mid}$.

Thiết diện của tòa nhà khi cắt bởi mặt phẳng vuông góc với trục $Oy$ tại điểm có tung độ $y$ ($-{L_y} \\le y \\le {L_y}$) là một hình parabol có đáy là $2x$ và chiều cao là $z$.
Diện tích thiết diện này là: $S(y) = \\frac{{2}}{{3}} \\cdot \\text{{đáy}} \\cdot \\text{{chiều cao}} = \\frac{{2}}{{3}} \\cdot (2x) \\cdot z = \\frac{{4}}{{3}} x z$.
$$ S(y) = {frac_4a_3} \\sqrt{{1 + \\frac{{y^2}}{{{b**2}}}}} \\cdot \\left({k_p_str}y^2 + {H_mid}\\right) $$

Thể tích tòa nhà là:
$$ V = \\int_{{-{L_y}}}^{{{L_y}}} S(y) dy = 2 \\int_{{0}}^{{{L_y}}} {frac_4a_3} \\sqrt{{1 + \\frac{{y^2}}{{{b**2}}}}} \\left({k_p_str}y^2 + {H_mid}\\right) dy $$
Bấm máy tính ta được $V \\approx {V_exact_str} \\text{{ m}}^3$.
Đổi ra đơn vị $1000 \\text{{ m}}^3$, ta có $V \\approx \\text{{{ans_str}}}$.
"""
    return question, solution, ans_str

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
        q, s, a = generate_question(seed + i if seed else None)
        answers.append(a)
        content += f"\\begin{{ex}}%Câu {i+1}\n{q}\n\n\\shortans{{{a}}}\n\\loigiai{{\n{s}\n}}\n\\end{{ex}}\n\n"

    tex_content = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage[utf8]{{vietnam}}
\\usepackage{{amsmath,amssymb,fancyhdr}}
\\usepackage{{tikz}}
\\usetikzlibrary{{angles,patterns,calc,arrows,intersections}}
\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{{geometry}}
\\usepackage[solcolor]{{ex_test}}
\\newcommand{{\\heva}}[1]{{\\left\\{{\\begin{{aligned}}#1\\end{{aligned}}\\right.}}

\\begin{{document}}
{content}
\\end{{document}}
"""

    output_file = os.path.join(os.path.dirname(__file__), "hyperbola_building_volume_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, a in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {a}")

if __name__ == "__main__":
    main()
