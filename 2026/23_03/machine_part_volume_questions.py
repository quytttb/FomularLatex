import math
import random
import sys
import os
from fractions import Fraction

def generate_question(seed=None):
    if seed is not None:
        random.seed(seed)
        
    while True:
        a_val = random.choice([2, 2.5, 3, 3.5, 4, 4.5, 5])
        a = Fraction(a_val)
        
        b_val = a_val + random.choice([1, 1.5, 2, 2.5, 3])
        b = Fraction(b_val)
        
        d1_val = a_val + random.choice([0.5, 1, 1.5, 2])
        if d1_val >= b_val:
            continue
        d1 = Fraction(d1_val)
        
        d2_val = random.choice([0.5, 1, 1.5, 2, 2.5, 3])
        if d2_val >= a_val:
            continue
        d2 = Fraction(d2_val)
        
        rhs1 = Fraction(-a, b - a)
        rhs2 = Fraction(d2 - a, d1 - a)
        
        if b == d1:
            continue
            
        c1 = (rhs1 - rhs2) / (b - d1)
        if c1 == 0:
            continue
            
        c2 = rhs1 - (b + a) * c1
        c3 = - c1 * b**2 - c2 * b
        
        if c1.denominator > 100 or c2.denominator > 100 or c3.denominator > 100:
            continue

        assert c1 * a**2 + c2 * a + c3 == a, "Parabol không qua G"
        assert c1 * b**2 + c2 * b + c3 == 0, "Parabol không qua F"
        assert c1 * d1**2 + c2 * d1 + c3 == d2, "Parabol không qua I"

        # Đảm bảo parabol không âm trên [a, b]
        vertex_x = -c2 / (2 * c1)
        if a < vertex_x < b:
            vertex_y = c1 * vertex_x**2 + c2 * vertex_x + c3
            if vertex_y < 0:
                continue

        def integral(x):
            return c1 * x**3 / 3 + c2 * x**2 / 2 + c3 * x
            
        area_parabola = integral(b) - integral(a)
        if area_parabola <= 0:
            continue
            
        area_square = a**2
        area_semicircle = Fraction(1, 2) * math.pi * float(a / 2)**2
        
        total_area = float(area_square) - area_semicircle + float(area_parabola)
        vol = total_area * float(a)
        ans = round(vol, 1)
        
        if ans > 0:
            break

    def format_number(num):
        if isinstance(num, Fraction):
            if num.denominator == 1:
                return str(num.numerator)
            return str(float(num)).replace('.', ',')
        if num == int(num):
            return str(int(num))
        return str(num).replace('.', ',')

    def format_frac_tex(f):
        if f.denominator == 1:
            return str(f.numerator)
        if f.numerator < 0:
            return f"-\\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"
        return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"

    a_str = format_number(a)
    b_str = format_number(b)
    d1_str = format_number(d1)
    d2_str = format_number(d2)
    r_str = format_number(a / 2)
    ans_dot = f"{ans:.1f}"
    ans_comma = ans_dot.replace(".", ",")
    ans_str = f"{ans_comma} | {ans_dot}"

    a_tex = format_frac_tex(a)
    b_tex = format_frac_tex(b)
    d1_tex = format_frac_tex(d1)
    d2_tex = format_frac_tex(d2)
    r_tex = format_frac_tex(a / 2)

    poly_terms = []
    if c1 != 0:
        if c1 == 1: poly_terms.append("x^2")
        elif c1 == -1: poly_terms.append("-x^2")
        else: poly_terms.append(f"{format_frac_tex(c1)}x^2")
        
    if c2 != 0:
        if c2 == 1: poly_terms.append("+ x")
        elif c2 == -1: poly_terms.append("- x")
        elif c2 > 0: poly_terms.append(f"+ {format_frac_tex(c2)}x")
        else: poly_terms.append(f"- {format_frac_tex(abs(c2))}x")
        
    if c3 != 0:
        if c3 > 0: poly_terms.append(f"+ {format_frac_tex(c3)}")
        else: poly_terms.append(f"- {format_frac_tex(abs(c3))}")
        
    poly_tex = " ".join(poly_terms)
    if poly_tex.startswith("+ "):
        poly_tex = poly_tex[2:]

    def eq_line(x_frac, y_tex):
        x2 = x_frac ** 2
        x2_tex = format_frac_tex(x2)
        x_tex = format_frac_tex(x_frac)
        if x_frac.denominator != 1:
            return f"\\left({x_tex}\\right)^2 a + {x_tex} b + c = {y_tex}"
        return f"{x2_tex} a + {x_tex} b + c = {y_tex}"

    eq1 = eq_line(a, a_tex)
    eq2 = eq_line(b, "0")
    eq3 = eq_line(d1, d2_tex)

    question = f"""Một chi tiết máy được thiết kế như hình vẽ. Các tứ giác $ABCD$, $CDGH$ là các hình vuông có cạnh ${a_str}$ cm nằm trong hai mặt phẳng vuông góc với nhau. Tứ giác $ABEF$ là hình chữ nhật có cạnh $AF = {b_str}$ cm nằm trong mặt phẳng song song với mặt phẳng $(CDGH)$. Mặt cong $GHEF$ được mài nhẵn theo đường parabol $FG$ (có trục đối xứng song song với đường thẳng $AD$) đi qua điểm $I$ với $I$ lần lượt cách mặt phẳng $(ABCD)$ và $(ABEF)$ một khoảng bằng ${d1_str}$ cm và ${d2_str}$ cm. Còn mặt cong $ABCD$ được mài nhẵn theo nửa đường tròn đường kính $AD$. Thể tích của chi tiết máy bằng bao nhiêu? (đơn vị cm$^3$) (làm tròn kết quả đến hàng phần mười).

\\begin{{center}}
\\begin{{tikzpicture}}[scale=.8,>=stealth, font=\\footnotesize, line join=round, line cap=round,color=red!75!black, line width=1pt]
   \\tikzset{{every node/.style={{scale=1}}}}
   \\def\\ya{{7}}
   \\path
   (0,0) coordinate (F) 
   (0:\\ya) coordinate (A)
   (30:3) coordinate (E)
   ($(A)+(E)-(F)$) coordinate (B)
   (2,3.5) coordinate (G)
   (\\ya,3.5) coordinate (D)
   ($(D)+(B)-(A)$) coordinate (C)
   ($(G)+(C)-(D)$) coordinate (H)
   ($(1.5,2)$) coordinate (I)
   ;
   \\draw[name path=c1,samples=200,domain=0:2,smooth,variable=\\x] plot (\\x,{{5/6*((\\x)^2)+1/12*(\\x)}});
   \\draw (\\ya,3.5) arc[start angle=90, end angle=270, radius=1.75cm];
   \\path[name path=fe] (F)--(E);
   \\path[name intersections={{of=c1 and fe}}] (intersection-1) coordinate (K')  (intersection-2) coordinate (K);
   \\draw[dashed] (C) arc[start angle=90, end angle=150, radius=1.75cm];
   \\draw (B) arc[start angle=-90, end angle=-210, radius=1.75cm];
   \\draw[samples=200,domain=0:2,smooth,variable=\\x] plot (\\x,{{5/6*((\\x)^2)+1/12*(\\x)}});
   \\draw [dashed] (E) parabola (H);
   \\draw (F)--(A)--(B) (G)--(D)--(C)--(H)--cycle (F)--(K)
   ;
   \\draw[dashed] (K)--(E)--(B);
   \\foreach \\x/\\g in
   {{A/-90,B/0,F/180,E/-90,G/180,D/-90,C/90,H/90,I/180}}
   \\fill[black](\\x) circle (1pt)
   ($(\\x)+(\\g:5mm)$) node{{$\\x$}};
\\end{{tikzpicture}}
\\end{{center}}"""

    solution = f"""Khi cắt chi tiết máy bởi mặt phẳng vuông góc với $AB$ thu được thiết diện có diện tích không đổi là diện tích hình thang cong $ADGF$.
Do đó thể tích của chi tiết máy là $V = S_{{\\text{{hình thang cong }} ADGF}} \\cdot AB$.

Chọn hệ trục tọa độ $Oxy$ với $A(0;0)$, tia $Ox$ chứa $AF$, tia $Oy$ chứa $AD$, đơn vị trên mỗi trục tọa độ là cm.
Tọa độ các điểm là $A(0; 0)$, $D(0; {a_str})$, $G({a_str}; {a_str})$, $F({b_str}; 0)$, $I({d1_str}; {d2_str})$.

Đường tròn đường kính $AD$ có bán kính $r = \\frac{{AD}}{{2}} = {r_tex}$.

Parabol $y = ax^2 + bx + c$ đi qua các điểm $G({a_str}; {a_str})$, $F({b_str}; 0)$, $I({d1_str}; {d2_str})$.
$$ \\begin{{cases}} {eq1} \\\\ {eq2} \\\\ {eq3} \\end{{cases}} \\Leftrightarrow \\begin{{cases}} a = {format_frac_tex(c1)} \\\\ b = {format_frac_tex(c2)} \\\\ c = {format_frac_tex(c3)} \\end{{cases}} \\Rightarrow y = {poly_tex} $$

$\\Rightarrow V = \\left[ \\left({a_tex}\\right)^2 - \\frac{{1}}{{2}}\\pi\\left({r_tex}\\right)^2 + \\int_{{{a_str}}}^{{{b_str}}} \\left( {poly_tex} \\right) dx \\right] \\cdot {a_str} \\approx \\text{{{ans_str}}} \\text{{ cm}}^3$."""

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

    output_file = os.path.join(os.path.dirname(__file__), "machine_part_volume_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, a in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {a}")

if __name__ == "__main__":
    main()
