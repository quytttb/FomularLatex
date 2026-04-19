import math
import random
import sys
import os
from typing import Dict, Any, List, Tuple

def format_money(amount: float) -> str:
    return str(int(round(amount)))

def format_decimal_vn(val: float, decimals: int = 2) -> str:
    if val == int(val):
        return str(int(val))
    formatted = f"{val:.{decimals}f}".rstrip("0").rstrip(".")
    return formatted.replace(".", "{,}")

def generate_type1() -> Tuple[str, str, int]:
    R = random.randint(4, 20)
    D = random.choice([d for d in range(2, 2*R) if d % 2 == 0])
    C = random.randint(5, 90) * 10000
    
    D_half = D / 2
    
    val_at_D_half = 0.5 * D_half * math.sqrt(R**2 - D_half**2) + 0.5 * R**2 * math.asin(D_half/R)
    S = 4 * val_at_D_half
    total_cost = S * C
    ans_round = round(total_cost)
    
    D_half_draw = 3 * D_half / R
    ycoord_draw = math.sqrt(9 - D_half_draw**2)
    A_deg = math.degrees(math.acos(D_half_draw / 3))
    B_deg = 180 - A_deg
    C_deg = 180 + A_deg
    D_deg = 360 - A_deg
    
    tikz = f"""\\begin{{center}}
\\begin{{tikzpicture}}[scale=0.8,color=red!75!black,line width=1pt]
    \\tikzstyle{{dotstyle}}=[circle, draw=red, fill=white, thick, inner sep=1pt]
    \\def\\ycoord{{{ycoord_draw:.3f}}}
    
    \\draw[thick] (0,0) circle (3);
    \\draw[fill=orange!30,line width=1pt] 
    ({A_deg:.1f}:3) arc({A_deg:.1f}:{B_deg:.1f}:3)--({C_deg:.1f}:3)arc({C_deg:.1f}:{D_deg:.1f}:3)--cycle;
    \\draw[thick] ({D_half_draw:.3f}, \\ycoord) -- ({D_half_draw:.3f}, -\\ycoord);
    \\draw[thick] (-{D_half_draw:.3f}, \\ycoord) -- (-{D_half_draw:.3f}, -\\ycoord);
    \\draw[thick] (-{D_half_draw:.3f}, 0) -- ({D_half_draw:.3f}, 0);
    
    \\node[dotstyle] at (0,0) {{}};
    \\node[dotstyle] at ({D_half_draw:.3f}, \\ycoord) {{}};
    \\node[dotstyle] at ({D_half_draw:.3f}, -\\ycoord) {{}};
    \\node[dotstyle] at (-{D_half_draw:.3f}, \\ycoord) {{}};
    \\node[dotstyle] at (-{D_half_draw:.3f}, -\\ycoord) {{}};
    \\node[dotstyle] at ({D_half_draw:.3f}, 0) {{}};
    \\node[dotstyle] at (-{D_half_draw:.3f}, 0) {{}};
    \\node[below=2pt] at (0,0) {{$O$}};
    \\node[above=2pt] at (0,0) {{{D}\\,m}};
\\end{{tikzpicture}}
\\end{{center}}"""

    question = f"""Một mảnh vườn hình tròn tâm $O$ bán kính {R} m. Người ta cần trồng cây trên dải đất rộng {D} m nhận $O$ làm tâm đối xứng, biết kinh phí trồng cây là {format_money(C)} đồng/m$^2$. Hỏi cần bao nhiêu tiền để trồng cây trên dải đất đó (làm tròn đến hàng đơn vị)?
{tikz}"""

    solution = f"""Ta chọn hệ trục tọa độ $Oxy$ sao cho tâm của mảnh vườn trùng với gốc tọa độ $O$.

Khi đó phương trình đường tròn tâm $O$, bán kính $R = {R}$ là $x^2 + y^2 = {R**2}$.

Suy ra phương trình nửa đường tròn phía trên trục hoành là $y = \\sqrt{{{R**2} - x^2}}$ và nửa phía dưới là $y = -\\sqrt{{{R**2} - x^2}}$.

Dải đất rộng {D} m và nhận $O$ làm tâm đối xứng nên nó được giới hạn bởi hai đường thẳng $x = -{D_half:g}$ và $x = {D_half:g}$.

Diện tích dải đất cần trồng cây là phần hình phẳng giới hạn bởi hai đường thẳng $x = -{D_half:g}$, $x = {D_half:g}$ và đường tròn. Theo ứng dụng của tích phân, diện tích này bằng:
\\[ S = \\int_{{-{D_half:g}}}^{{{D_half:g}}} \\left( \\sqrt{{{R**2} - x^2}} - \\left(-\\sqrt{{{R**2} - x^2}}\\right) \\right) dx = 2 \\int_{{-{D_half:g}}}^{{{D_half:g}}} \\sqrt{{{R**2} - x^2}} dx. \\]
Do tính đối xứng qua trục $Oy$, ta có:
\\[ S = 4 \\int_{{0}}^{{{D_half:g}}} \\sqrt{{{R**2} - x^2}} dx. \\]
Đặt $x = {R} \\sin t \\Rightarrow dx = {R} \\cos t dt$. Đổi cận: với $x = 0 \\Rightarrow t = 0$; với $x = {D_half:g} \\Rightarrow t = \\arcsin\\left(\\frac{{{D_half:g}}}{{{R}}}\\right)$.

Tính tích phân ta được diện tích $S \\approx {format_decimal_vn(S, 3)}$ m$^2$.

Vậy tổng số tiền cần dùng để trồng cây là:
\\[ T = S \\cdot {format_money(C)} \\approx {format_money(ans_round)} \\text{{ (đồng)}}. \\]"""

    return question, solution, ans_round

def generate_type2() -> Tuple[str, str, int]:
    R = random.randint(4, 20)
    D = random.choice([d for d in range(2, 2*R) if d % 2 == 0])
    C = random.randint(5, 90) * 10000
    
    D_half = D / 2
    
    y0 = math.sqrt(R**2 - D_half**2)
    val_at_y0 = 0.5 * y0 * D_half + 0.5 * R**2 * math.asin(y0/R)
    S = 4 * (val_at_y0 - D_half * y0)
    total_cost = S * C
    ans_round = round(total_cost)
    
    D_half_draw = 3 * D_half / R
    ycoord_draw = math.sqrt(9 - D_half_draw**2)
    A_deg = math.degrees(math.acos(D_half_draw / 3))
    
    tikz = f"""\\begin{{center}}
\\begin{{tikzpicture}}[scale=0.8,color=red!75!black,line width=1pt]
    \\tikzstyle{{dotstyle}}=[circle, draw=red, fill=white, thick, inner sep=1pt]
    \\def\\ycoord{{{ycoord_draw:.3f}}}
    
    \\draw[thick] (0,0) circle (3);
    
    \\draw[thick] ({D_half_draw:.3f}, \\ycoord) -- ({D_half_draw:.3f}, -\\ycoord);
    \\draw[thick] (-{D_half_draw:.3f}, \\ycoord) -- (-{D_half_draw:.3f}, -\\ycoord);
    \\draw[thick] (-{D_half_draw:.3f}, 0) -- ({D_half_draw:.3f}, 0);
    \\draw[fill=orange!30,line width=1pt] (-{A_deg:.1f}:3) arc(-{A_deg:.1f}:{A_deg:.1f}:3)--cycle;
    \\draw[fill=orange!30,line width=1pt] ({-180+A_deg:.1f}:3) arc({-180+A_deg:.1f}:{-180-A_deg:.1f}:3)--cycle;
    \\node[dotstyle] at (0,0) {{}};
    \\node[dotstyle] at ({D_half_draw:.3f}, \\ycoord) {{}};
    \\node[dotstyle] at ({D_half_draw:.3f}, -\\ycoord) {{}};
    \\node[dotstyle] at (-{D_half_draw:.3f}, \\ycoord) {{}};
    \\node[dotstyle] at (-{D_half_draw:.3f}, -\\ycoord) {{}};
    \\node[dotstyle] at ({D_half_draw:.3f}, 0) {{}};
    \\node[dotstyle] at (-{D_half_draw:.3f}, 0) {{}};
    \\node[below=2pt] at (0,0) {{$O$}};
    \\node[above=2pt] at (0,0) {{{D}\\,m}};
\\end{{tikzpicture}}
\\end{{center}}"""

    question = f"""Một mảnh vườn hình tròn tâm $O$ bán kính {R} m. Người ta cần trồng cây (được tô màu cam) nằm ở phía ngoài của dải đất rộng {D} m nhận $O$ làm tâm đối xứng (như hình vẽ). Biết kinh phí trồng cây là {format_money(C)} đồng/m$^2$. Hỏi cần bao nhiêu tiền để trồng cây trên dải đất đó (làm tròn đến hàng đơn vị)?
{tikz}"""

    solution = f"""Ta chọn hệ trục tọa độ $Oxy$ sao cho tâm của mảnh vườn trùng với gốc tọa độ $O$.
Khi đó phương trình đường tròn là $x^2 + y^2 = {R**2}$.
Dải đất ở giữa rộng {D} m, nên biên của dải đất là hai đường thẳng $x = -{D_half:g}$ và $x = {D_half:g}$. Phần tô màu cam nằm trong khoảng $x \\ge {D_half:g}$ và $x \\le -{D_half:g}$.

Tung độ giao điểm của đường thẳng $x = {D_half:g}$ và đường tròn thỏa mãn:
\\[ y^2 + ({D_half:g})^2 = {R**2} \\Rightarrow y = \\pm \\sqrt{{{R**2} - {D_half**2:g}}} = \\pm {format_decimal_vn(y0, 3)}. \\]
Từ phương trình đường tròn, ta suy ra phương trình cung tròn phía bên phải trục tung ($x > 0$) là $x = \\sqrt{{{R**2} - y^2}}$.

Diện tích phần tô màu cam bên phải trục tung được giới hạn bởi đường cong $x = \\sqrt{{{R**2} - y^2}}$ và đường thẳng $x = {D_half:g}$. Vì phần cần trồng cây gồm hai phần đối xứng nhau qua trục tung, nên tổng diện tích là:
\\[ S = 2 \\int_{{-{format_decimal_vn(y0, 3)}}}^{{{format_decimal_vn(y0, 3)}}} \\left( \\sqrt{{{R**2} - y^2}} - {D_half:g} \\right) dy = 4 \\int_{{0}}^{{{format_decimal_vn(y0, 3)}}} \\left( \\sqrt{{{R**2} - y^2}} - {D_half:g} \\right) dy. \\]
Tính tích phân ta được diện tích $S \\approx {format_decimal_vn(S, 3)}$ m$^2$.

Vậy tổng số tiền cần dùng để trồng cây là:
\\[ T = S \\cdot {format_money(C)} \\approx {format_money(ans_round)} \\text{{ (đồng)}}. \\]"""

    return question, solution, ans_round

def generate_type3() -> Tuple[str, str, int]:
    W = random.choice([w for w in range(2, 21) if w % 2 == 0])
    H = random.choice([h for h in range(2, 21) if h % 2 == 0])
    h_col = random.choice([h/2 for h in range(1, 2*H)])
    C = random.randint(5, 90) * 10000
    
    a = W / 2
    b = H / 2
    
    term1 = (h_col - b) * math.sqrt(2*b*h_col - h_col**2)
    term2 = b**2 * math.asin(h_col/b - 1)
    term3 = (math.pi / 2) * b**2
    S = (a / b) * (term1 + term2 + term3)
    
    total_cost = S * C
    ans_round = round(total_cost)
    
    tikz = f"""\\begin{{center}}
\\begin{{tikzpicture}}[line join = round, line cap=round,>=stealth,font=\\footnotesize,scale=1,color=red!75!black,line width=1pt]
    \\draw (160:3cm and 1.8cm)coordinate (A) arc(160:380:3cm and 1.8cm)coordinate (B) arc(380:540:3cm and 1.8cm);
    \\draw[fill=orange!30] (A)arc(160:380:3cm and 1.8cm)--cycle;
    %%%%%%%
    \\draw[red,dashed,line width=1pt] (90:3cm and 1.8cm)--++(4,0)coordinate (A');
    
    \\draw[red,dashed,line width=1pt] ($(A)!1/2!(B)$)--++(5,0)coordinate (B');
    \\draw[red,dashed,line width=1pt] (-90:3cm and 1.8cm)--++(5,0)coordinate (C');
    \\draw[red,dashed,line width=1pt] (0:3cm and 1.8cm)--++(0,-2.5)coordinate (T);
    \\draw[red,dashed,line width=1pt] (180:3cm and 1.8cm)--++(0,-2.5)coordinate (P);
    \\draw[red,<->,line width=1pt] (T)--(P)node[pos=0.5,below]{{$\\color{{red}} {format_decimal_vn(W)}$ m}};
    \\draw[red,<->,line width=1pt] (B')--(C')node[pos=0.5,sloped,above]{{$\\color{{red}} {format_decimal_vn(h_col)}$ m}};
    
    \\draw[red,<->,line width=1pt] (A')++(0,0)--++(0,-3.6) node[pos=0.5,sloped,above]{{$\\color{{red}} {format_decimal_vn(H)}$ m}};
\\end{{tikzpicture}}
\\end{{center}}"""

    question = f"""Một sân chơi hình elip có kích thước như hình vẽ. Người ta muốn sơn một phần sân chơi thành màu hồng nhạt để làm sàn cho khu vui chơi. Biết kinh phí để sơn là {format_money(C)} đồng trên một đơn vị diện tích (m$^2$). Hỏi cần bao nhiêu tiền để sơn phần sân chơi đó (làm tròn đến hàng đơn vị)?
{tikz}"""

    solution = f"""Ta chọn hệ trục tọa độ $Oxy$ sao cho tâm Elip trùng với gốc tọa độ $O$.
Dựa vào hình vẽ, ta có độ dài trục lớn là $2a = {W} \\Rightarrow a = {a:g}$ và độ dài trục nhỏ là $2b = {H} \\Rightarrow b = {b:g}$.
Suy ra phương trình chính tắc của Elip là $\\frac{{x^2}}{{{a**2:g}}} + \\frac{{y^2}}{{{b**2:g}}} = 1$.

Điểm thấp nhất của Elip nằm trên đường thẳng $y = -{b:g}$. Đường giới hạn phía trên của phần tô màu cao ${format_decimal_vn(h_col)}$ m tính từ đáy, nên tung độ của đường này là $y = -{b:g} + {format_decimal_vn(h_col)} = {format_decimal_vn(-b + h_col)}$.

Từ phương trình Elip, ta suy ra phương trình cung Elip phía bên phải trục tung ($x > 0$) là:
\\[ x = {a:g}\\sqrt{{1 - \\frac{{y^2}}{{{b**2:g}}}}}. \\]
Vì phần tô màu đối xứng qua trục $Oy$, nên diện tích phần cần sơn được tính bằng:
\\[ S = \\int_{{-{b:g}}}^{{{format_decimal_vn(-b + h_col)}}} 2x\\, dy = 2 \\int_{{-{b:g}}}^{{{format_decimal_vn(-b + h_col)}}} {a:g}\\sqrt{{1 - \\frac{{y^2}}{{{b**2:g}}}}}\\, dy. \\]
Tính giá trị tích phân ta được $S \\approx {format_decimal_vn(S, 3)}$ m$^2$.

Vậy tổng số tiền cần dùng để sơn phần sân chơi đó là:
\\[ T = S \\cdot {format_money(C)} \\approx {format_money(ans_round)} \\text{{ (đồng)}}. \\]"""

    return question, solution, ans_round

def main():
    if len(sys.argv) < 2:
        print("Usage: python integration_area_questions.py <num_questions> [type] [seed]")
        sys.exit(1)
        
    num_questions = int(sys.argv[1])
    
    q_type = None
    if len(sys.argv) > 2:
        try:
            q_type = int(sys.argv[2])
            if q_type not in [1, 2, 3]:
                q_type = None
        except ValueError:
            q_type = None
            
    seed = None
    if len(sys.argv) > 3:
        try:
            seed = int(sys.argv[3])
        except ValueError:
            pass
            
    if seed is not None:
        random.seed(seed)
        
    questions_data = []
    
    for i in range(num_questions):
        t = q_type if q_type is not None else random.choice([1, 2, 3])
        if t == 1:
            q, s, ans = generate_type1()
        elif t == 2:
            q, s, ans = generate_type2()
        else:
            q, s, ans = generate_type3()
            
        ans_str = f"{ans}"
        
        content = f"\\begin{{ex}}%Câu {i+1}\n{q}\n\n\\shortans{{{ans_str}}}\n\\loigiai{{\n{s}\n}}\n\\end{{ex}}"
        questions_data.append((content, ans_str))
        
    latex_content = r"""\documentclass[12pt,a4paper]{article}
\usepackage{amsmath,amssymb,fancyhdr}
\usepackage{graphicx}
\usepackage{tikz}
\usetikzlibrary{calc,arrows}
\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}
\usepackage[solcolor]{ex_test}
\newcommand{\heva}[1]{\left\{\begin{aligned}#1\end{aligned}\right.}

\begin{document}

""" + "\n\n".join(q for q, _ in questions_data) + "\n\\end{document}"

    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, "integration_area_questions.tex")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(latex_content)
        
    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, (_, a) in enumerate(questions_data):
        print(f"Câu {i + 1}: Đáp án: {a}")

if __name__ == "__main__":
    main()
