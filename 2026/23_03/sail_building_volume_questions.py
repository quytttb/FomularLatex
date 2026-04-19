import math
import random
import sys
import os
from fractions import Fraction

def generate_question(seed=None):
    if seed is not None:
        random.seed(seed)
        
    while True:
        # Randomize parameters
        h_total = random.choice([300, 320, 350, 360, 400])
        h_floors = random.choice([200, 240, 250, 280, 300])
        if h_floors >= h_total:
            continue
            
        r_base = random.choice([50, 60, 70, 80])
        r_top = random.choice([30, 40, 45, 50])
        if r_top >= r_base:
            continue
            
        alpha = random.choice([45, 60, 90, 120])
        num_floors = random.choice([50, 56, 60, 65, 70])
        
        c_frac = Fraction(r_base)
        # y = ax² + bx + c qua A(0, r_base), C(h_floors, r_top), S(h_total, 0)
        # Giải hệ: (2) a·h_f² + b·h_f = r_top - c,  (3) a·h_t² + b·h_t = -c
        a_frac = (Fraction(r_top - r_base, h_floors) + Fraction(r_base, h_total)) \
                 / (h_floors - h_total)

        b_frac = Fraction(-r_base, h_total) - a_frac * h_total

        if a_frac == 0:
            continue
        if a_frac.denominator > 2000 or b_frac.denominator > 200:
            continue

        # Verify: parabol đi qua đúng 3 điểm
        assert a_frac * h_floors**2 + b_frac * h_floors + c_frac == r_top
        assert a_frac * h_total**2 + b_frac * h_total + c_frac == 0

        a = float(a_frac)
        b = float(b_frac)
        c = r_base

        # ∫₀^h (ax²+bx+c)² dx, khai triển rồi tích phân từng hạng
        x = Fraction(h_floors)
        integral_val = (a_frac**2 * x**5 / 5
                        + a_frac * b_frac * x**4 / 2
                        + (b_frac**2 + 2 * a_frac * c_frac) * x**3 / 3
                        + b_frac * c_frac * x**2
                        + c_frac**2 * x)

        vol = float(Fraction(alpha, 360) * integral_val) * math.pi
        vol_thousands = vol / 1000
        ans = round(vol_thousands)

        if ans > 0:
            break

    # Format fractions for LaTeX
    def format_frac(f):
        if f.denominator == 1:
            return str(f.numerator)
        if f.numerator < 0:
            return f"-\\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"
        return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"

    a_tex = format_frac(a_frac)
    b_tex = format_frac(b_frac)
    
    # Format polynomial
    poly_terms = []
    if a_frac != 0:
        if a_frac == 1: poly_terms.append("x^2")
        elif a_frac == -1: poly_terms.append("-x^2")
        else: poly_terms.append(f"{a_tex}x^2")
        
    if b_frac != 0:
        if b_frac == 1: poly_terms.append("+ x")
        elif b_frac == -1: poly_terms.append("- x")
        elif b_frac > 0: poly_terms.append(f"+ {b_tex}x")
        else: poly_terms.append(f"- {format_frac(abs(b_frac))}x")
        
    if c != 0:
        if c > 0: poly_terms.append(f"+ {c}")
        else: poly_terms.append(f"- {abs(c)}")
        
    poly_tex = " ".join(poly_terms)
    if poly_tex.startswith("+ "):
        poly_tex = poly_tex[2:]

    alpha_frac = Fraction(alpha, 360)
    alpha_tex = format_frac(alpha_frac)

    question = f"""Một tòa nhà hình cánh buồm được minh họa bởi hình vẽ bên, tòa nhà có chiều cao $SO = {h_total}$ m, gồm {num_floors} tầng có tổng chiều cao là $OI = {h_floors}$ m và phần còn lại phía trên là không gian sân thượng. Mặt trước hình cánh buồm, được căng bởi hai cung parabol $SCA$ và $SDB$ giống hệt nhau có trục đối xứng vuông góc với đường thẳng $SO$, các parabol này nằm trong mỗi mặt bên của tòa nhà. Hai mặt bên $SOA$ và $SOB$ tạo với nhau một góc ${alpha}^\\circ$. Mặt sàn tầng một có dạng hình quạt tròn tâm $O$ với bán kính $OA = {r_base}$ m, mái của tầng {num_floors} có dạng hình quạt tròn tâm $I$ với bán kính $IC = {r_top}$ m. Thiết diện ngang của tòa nhà đi qua một điểm $H$ bất kỳ trên đoạn $OI$ luôn là hình quạt có tâm là $H$. Tính thể tích của tòa nhà (chỉ tính phần chứa {num_floors} tầng) với đơn vị là nghìn mét khối và kết quả làm tròn đến hàng đơn vị.

\\begin{{center}}
\\begin{{tikzpicture}}[scale=1, >=stealth,color=red!75!black, line width=1pt]
   \\coordinate (O) at (0,0);
   \\coordinate (H) at (0,1.8);
   \\coordinate (I) at (0,4.8);
   \\coordinate (S) at (0,6.5);
   \\coordinate (C) at (-1.1,3.8);
   \\coordinate (D) at (-2,4.8);
   \\coordinate (P7) at (-2.6,1.8);
   \\coordinate (P8) at (-1.6,0.2);
   \\coordinate (A) at (-1.4,-1.3);
   \\coordinate (B) at (-2.4,0);
   \\coordinate (P11) at (0.8,4.8);
   \\coordinate (P12) at (0.8,0);
   \\coordinate (P13) at (1.8,6.5);
   \\coordinate (P14) at (1.8,0);
   \\draw (S) .. controls +(-162.8:0.7) and +(67.6:0.8) .. (D) .. controls (-2.3,4.1) and (-2.6,2.8) .. (P7) .. controls +(-91.6:0.8) and +(102.4:0.6) .. (B) .. controls (-2.3,-0.5) and (-2,-1.1) .. (A) .. controls +(114.8:0.5) and +(-92.6:0.5) .. (P8) .. controls (-1.5,1.4) and (-1.4,2.7) .. (C) .. controls +(76.3:1) and +(-118.1:1) .. (S) -- (O) -- (A);
   
   \\draw[pattern=north west lines,opacity=0.3] (P7) .. controls +(-86:0.7) and +(153.2:0.7) .. (P8) -- (H);
   \\draw (D) .. controls +(-85.8:0.5) and +(173.3:0.6) .. (C) -- (I);
   \\draw (I)--(C)node[below,sloped,pos=0.5]{{{r_top} m}};
   \\draw[<->] (P11) -- (P12)node[above,sloped,pos=0.5]{{{h_floors} m}};
   \\draw[<->] (P13) -- (P14) node[above,sloped,pos=0.5]{{{h_total} m}};
   \\draw [dashed] (O) -- (B);
   \\draw [dashed] (H) -- (P7);
   \\draw [dashed] (I) -- (D);
   \\draw [dashed] (P12) -- (O);
   \\draw [dashed] (P12) -- (P14);
   \\draw [dashed] (I) -- (P11);
   \\draw [dashed] (S) -- (P13);
   \\foreach \\p/\\pos/\\lbl in {{
    O/(-45:3mm)/O,
    H/(360:3mm)/H,
    I/(45:3mm)/I,
    S/(90:3mm)/S,
    C/(-145:3mm)/C,
    D/(165:3mm)/D,
    A/(300:3mm)/A,
    B/(180:3mm)/B
   }}{{
    \\fill (\\p) circle (1.2pt) node[shift=\\pos] {{$\\lbl$}};
   }}
   \\draw pic[draw, angle radius=0.5cm, ] {{angle = B--O--A}};
   \\node at (-1,-0.3) {{${alpha}^\\circ$}};
\\end{{tikzpicture}}
\\end{{center}}"""

    solution = f"""Chọn $OS$, $OA$ lần lượt là trục $Ox$, $Oy$ và đơn vị trên trục là mét.
Khi đó Parabol $(P): y = ax^2 + bx + c$ đi qua các điểm $A(0; {r_base})$, $C({h_floors}; {r_top})$, $S({h_total}; 0)$ nên
$$ \\begin{{cases}} 0^2a + 0b + c = {r_base} \\\\ {h_floors}^2a + {h_floors}b + c = {r_top} \\\\ {h_total}^2a + {h_total}b + c = 0 \\end{{cases}} \\Leftrightarrow a = {a_tex}, b = {b_tex}, c = {c}. $$
Suy ra $(P): y = {poly_tex}$.

Mặt cắt vuông góc với trục $Ox$ tại điểm $H$ có hoành độ $x$ ($0 \\le x \\le {h_floors}$) là hình quạt có bán kính $r = {poly_tex}$ và góc ở tâm ${alpha}^\\circ$ nên có diện tích $S(x) = \\frac{{{alpha}}}{{360}} \\cdot \\pi r^2 = {alpha_tex}\\pi \\left({poly_tex}\\right)^2$ m$^2$.

Thể tích tòa nhà là $V = \\int_0^{{{h_floors}}} S(x) dx = \\int_0^{{{h_floors}}} {alpha_tex}\\pi \\left({poly_tex}\\right)^2 dx \\approx {ans}$ ($10^3$ m$^3$).

Cách 2: Vì thiết diện ngang của tòa nhà là quạt tròn và hai mặt bên tòa nhà hợp với nhau một góc ${alpha}^\\circ$ nên thể tích toàn nhà ({num_floors} tầng) bằng ${alpha_tex}$ thể tích khối tròn xoay sinh ra khi quay hình thang cong giới hạn bởi $(P)$, trục hoành, trục tung và đường thẳng $x = {h_floors}$ quanh trục hoành.
Vậy thể tích tòa nhà bằng $V = {alpha_tex}\\pi \\int_0^{{{h_floors}}} \\left({poly_tex}\\right)^2 dx \\approx {ans}$ ($10^3$ m$^3$)."""

    return question, solution, ans

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

    # Wrap in standard LaTeX document for testing if needed, or just output the content
    tex_content = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage[utf8]{{vietnam}}
\\usepackage{{amsmath,amssymb,fancyhdr}}
\\usepackage{{tikz}}
\\usetikzlibrary{{angles,patterns,calc,arrows}}
\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{{geometry}}
\\usepackage[solcolor]{{ex_test}}
\\newcommand{{\\heva}}[1]{{\\left\\{{\\begin{{aligned}}#1\\end{{aligned}}\\right.}}

\\begin{{document}}
{content}
\\end{{document}}
"""

    output_file = os.path.join(os.path.dirname(__file__), "sail_building_volume_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, a in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {a}")

if __name__ == "__main__":
    main()
