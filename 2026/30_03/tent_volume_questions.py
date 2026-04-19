"""
Sinh đề tự luận: thể tích lều cắm trại đáy chữ nhật và hình vuông.

Tham số đầu vào:
  - sys.argv[1]: Số lượng câu (mặc định 1)
  - sys.argv[2]: Dạng toán {1, 2}. Nếu không truyền, mặc định random
  - sys.argv[3]: Seed (tùy chọn)
"""
import math
import os
import sys
import random

def generate_type1(seed_val=None):
    if seed_val is not None:
        random.seed(seed_val)
    a = random.choice([200, 210, 220, 240, 250, 300, 320])
    b_choices = [150, 180, 195, 200, 250, 280]
    b = random.choice([x for x in b_choices if x != a])
    h = random.choice([120, 150, 180, 200, 240])
    
    V_cm3 = (a * b * h) // 2
    V_m3 = V_cm3 / 1000000
    
    v_str = f"{V_m3:g}"
    if "." in v_str:
        ans_str = f"{v_str.replace('.', ',')} | {v_str}"
        V_m3_tex = v_str.replace('.', ',')
    else:
        ans_str = v_str
        V_m3_tex = v_str
    
    stem = f"Một cái lều cắm trại có đáy là hình chữ nhật kích thước ${a}$ cm $\\times$ ${b}$ cm và chiều cao là ${h}$ cm. Bốn cạnh bên cong được tạo thành từ hai đường parabol nhận đỉnh của lều làm đỉnh của parabol (hình vẽ). Thể tích phần không gian bên trong lều là bao nhiêu mét khối?\n"
    
    tikz = f"""\\begin{{center}}
  \\begin{{tikzpicture}}[line join = round, line cap=round,>=stealth,font=\\footnotesize,scale=1,color=red!75!black, line width=1pt]
   \\path (0,0)coordinate (A)--++(4,-0.25)coordinate (B)
   --++(-0.5,-1.5)coordinate (C)
   --++(-5,0.5) coordinate (D)--cycle;
   \\fill[pink!20](A)--(B)--(C)--(D)--cycle; 
   \\draw[dashed] (A)--(B) (D)--(A);
   \\draw (D)--(C)--(B);
   \\begin{{scope}}[line width=1pt]
    \\draw[dashed] (A) ..controls +(80:1) and +(180:0.5).. ($(A)!1/2!(C)+(0,3.5)$)coordinate (S) ;
    \\draw  (B) ..controls +(100:1) and +(0:1).. (S) ;
    \\draw  (C) ..controls +(100:1) and +(0:1).. (S) ;
    \\draw  (D) ..controls +(80:1) and +(180:1).. (S) ;
   \\end{{scope}}
   \\draw[<->] (S)--($(A)!1/2!(C)$)node[above,pos=0.5,rotate=-90]{{${h}$ cm}};
   \\draw[<->] ([yshift=-5pt]D)--([yshift=-5pt]C)node[below,pos=0.5,sloped]{{${a}$ cm}};
   \\draw[<->] ([xshift=5pt]C)--([xshift=5pt]B)node[below,pos=0.5,sloped]{{${b}$ cm}};
  \\end{{tikzpicture}}
\\end{{center}}"""

    stem += tikz
    
    solution = f"""Chọn hệ tọa độ có gốc trùng với đỉnh của lều, trục $Oz$ hướng thẳng đứng xuống mặt đáy.
Do lều được tạo thành từ hai đường parabol nhận $O$ làm đỉnh, nên khi cắt lều bởi một mặt phẳng nằm ngang cách đỉnh một khoảng $z$ ($0 \\le z \\le {h}$ cm), ta luôn được thiết diện là một hình chữ nhật có chiều dài và chiều rộng tỉ lệ thuận với căn bậc hai của $z$ (cụ thể là $\\sqrt{{z}}$).
Gọi chiều dài và chiều rộng của thiết diện tại độ sâu $z$ lần lượt là $x(z)$ và $y(z)$, ta có liên hệ:
$$x(z) = {a} \\cdot \\sqrt{{\\frac{{z}}{{{h}}}}} \\quad \\text{{và}} \\quad y(z) = {b} \\cdot \\sqrt{{\\frac{{z}}{{{h}}}}}$$
Diện tích thiết diện tại độ cao $z$: 
$$S(z) = x(z) \\cdot y(z) = {a} \\cdot {b} \\cdot \\frac{{z}}{{{h}}} = {a*b} \\cdot \\frac{{z}}{{{h}}} \\quad (\\text{{cm}}^2)$$
Thể tích không gian bên trong lều:
$$V = \\int_0^{{{h}}} S(z) \\, dz = \\int_0^{{{h}}} \\frac{{{a*b}}}{{{h}}} z \\, dz = \\left( \\frac{{{a*b}}}{{{2*h}}} \\cdot z^2 \\right) \\bigg|_0^{{{h}}} = \\frac{{1}}{{2}} \\cdot {a} \\cdot {b} \\cdot {h}$$
Thay các giá trị $a={a}$, $b={b}$, $h={h}$ vào công thức:
$$V = \\frac{{1}}{{2}} \\cdot {a} \\cdot {b} \\cdot {h} = {V_cm3} \\quad (\\text{{cm}}^3)$$
Đổi sang đơn vị mét khối: $V = {V_m3_tex} \\text{{ m}}^3$.

Đáp án: {V_m3_tex}"""

    return stem, solution, ans_str

def generate_type2(seed_val=None):
    if seed_val is not None:
        random.seed(seed_val)
    x = random.randint(2, 6) # So edge is x \sqrt{2}
    h = random.choice([2, 3, 4, 5, 6])
    
    V = (x**2) * h
    
    stem = f"Một lều cắm trại có dạng như hình vẽ dưới, khung lều được tạo thành từ hai parabol giống nhau có chung đỉnh $O$ và thuộc hai mặt phẳng vuông góc nhau (một parabol đi qua $A, O, C$ và một parabol đi qua $B, D, O$), bốn chân tạo thành hình vuông $ABCD$ có cạnh là ${x}\\sqrt{{2}}$ m, chiều cao tính từ đỉnh lều là ${h}$ m. Biết mặt cắt của lều khi cắt bởi một mặt phẳng song song với mặt phẳng $(ABCD)$ luôn là một hình vuông. Tính thể tích của lều (đơn vị là m$^3$).\n"
    
    tikz = f"""\\begin{{center}}
  \\begin{{tikzpicture}}[line join = round, line cap=round,>=stealth,font=\\footnotesize,scale=1,color=red!75!black, line width=1pt]
   \\path (0,0)coordinate (A)--++(4,-0.25)coordinate (B)
   --++(-0.5,-1.5)coordinate (C)
   --++(-5,0.5) coordinate (D)--cycle;
   \\fill[pink!20](A)--(B)--(C)--(D)--cycle; 
   \\draw[dashed] (A)--(B) (D)--(A);
   \\draw (D)--(C)--(B);
   \\begin{{scope}}[line width=1pt]
    \\draw[dashed] (A) ..controls +(80:1) and +(180:0.5).. ($(A)!1/2!(C)+(0,3.5)$)coordinate (S) ;
    \\draw  (B) ..controls +(100:1) and +(0:1).. (S) ;
    \\draw  (C) ..controls +(100:1) and +(0:1).. (S) ;
    \\draw  (D) ..controls +(80:1) and +(180:1).. (S) ;
   \\end{{scope}}
   \\foreach \\p in {{A,B,C,D,S}} \\fill[red] (\\p) circle(1.5pt);
   \\draw (S) node[above]{{$O$}};
   \\draw (A) node[above left]{{$C$}};
   \\draw (B) node[below right]{{$B$}};
   \\draw (C) node[below right]{{$A$}};
   \\draw (D) node[below left]{{$D$}};
  \\end{{tikzpicture}}
\\end{{center}}"""

    stem += tikz
    
    solution = f"""Chọn hệ trục tọa độ sao cho gốc tọa độ tại đỉnh lều $O$, chiều dương trục $Oz$ hướng thẳng đứng xuống dưới. Lều có chiều cao $h = {h}$ m.
Do khung lều làm từ hai parabol giống nhau đi qua $A, C$ và $B, D$ (các đường chéo của đáy), các parabol này nằm trong mặt phẳng chứa các đường chéo của đáy.
Tại mặt ngang cắt ở độ sâu $z$ ($0 \\le z \\le {h}$), thiết diện luôn nhận hình dạng vuông theo đề bài.
Gọi $r(z)$ là một nửa đường chéo của thiết diện tại độ sâu $z$. Vì đường cong khung lều là đường parabol $(P): z = k \\cdot x^2$ với đỉnh $O$, ta có:
$$z = k \\cdot r(z)^2 \\Rightarrow r(z) = \\sqrt{{\\frac{{z}}{{k}}}}$$
Khi $z = {h}$ thì thiết diện chính là mặt đáy $ABCD$. Đáy là hình vuông cạnh $a = {x}\\sqrt{{2}}$ m, suy ra đường chéo của mặt đáy $d = \\sqrt{{2}} \\cdot {x}\\sqrt{{2}} = {2*x}$ m.
Một nửa đường chéo đáy bằng ${x}$ m. Thay vào phương trình parabol ta được tham số $k$: 
$${h} = k \\cdot ({x})^2 \\Rightarrow k = \\frac{{{h}}}{{{x**2}}}$$
Suy ra ở mức độ sâu $z$ bất kỳ, nửa đường chéo của thiết diện là $r(z) = \\sqrt{{\\frac{{{x**2}}}{{{h}}} z}}$.
Do thiết diện là hình vuông, diện tích thiết diện $S(z)$ được tính theo nửa đường chéo $r(z)$:
$$S(z) = \\frac{{1}}{{2}} \\cdot (2 r(z))^2 = 2 \\cdot r(z)^2 = 2 \\cdot \\frac{{{x**2}}}{{{h}}} z$$
Thể tích của chiếc lều (đơn vị m$^3$) là:
$$V = \\int_0^{{{h}}} S(z) \\, dz = \\int_0^{{{h}}} 2 \\frac{{{x**2}}}{{{h}}} z \\, dz = \\left( \\frac{{{x**2}}}{{{h}}} z^2 \\right) \\bigg|_0^{{{h}}} = {x**2} \\cdot {h}$$
Thay số $x={x}, h={h}$:
$$V = {x**2} \\cdot {h} = {V} \\quad (\\text{{m}}^3)$$

Đáp án: {V}"""
    
    return stem, solution, str(V)

def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    t_type = None
    if len(sys.argv) > 2:
        try:
            t = int(sys.argv[2])
            if t in [1, 2]:
                t_type = t
        except ValueError:
            pass

    seed = None
    if len(sys.argv) > 3:
        seed = int(sys.argv[3])

    content = ""
    answers = []

    for i in range(num_questions):
        current_seed = seed + i if seed is not None else None
        
        # Determine the type specifically for this question
        if t_type is not None:
            chosen_type = t_type
        else:
            # Provide different seeds for random choice if global seed is set
            if current_seed is not None:
                random.seed(current_seed + 1000)
            chosen_type = random.choice([1, 2])
            
        if chosen_type == 1:
            q, s, a = generate_type1(current_seed)
        else:
            q, s, a = generate_type2(current_seed)
            
        answers.append(a)
        content += f"\\begin{{ex}}%Câu {i+1}\n{q}\n\n\\shortans{{{a}}}\n\\loigiai{{\n{s}\n}}\n\\end{{ex}}\n\n"

    tex_content = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage{{amsmath,amssymb,fancyhdr}}
\\usepackage{{polyglossia}}
\\setdefaultlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage{{tikz}}
\\usetikzlibrary{{calc,patterns}}
\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{{geometry}}
\\usepackage[solcolor]{{ex_test}}
\\newcommand{{\\heva}}[1]{{\\left\\{{\\begin{{aligned}}#1\\end{{aligned}}\\right.}}

\\begin{{document}}
{content}
\\end{{document}}
"""

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "tent_volume_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, a in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {a}")

if __name__ == "__main__":
    main()
