import math
import os
import sys
import random
from fractions import Fraction
from typing import Tuple

CONTEXTS = [
    {
        "space": r"không gian studio 3D $Oxyz$",
        "A_desc": r"vị trí camera",
        "S_desc": r"quả cầu LED",
        "I_desc": r"tâm điều khiển",
        "plane_desc": r"vách kính màn hình",
        "S_name": r"$(S)$",
        "plane_name": r"$(\alpha)$",
        "a_stmt": r"Vị trí đặt camera $A$ nằm an toàn ngoài quả cầu LED $(S)$.",
        "b_stmt": r"Trục chiếu sáng $IA$ tạo với vách kính $(\alpha)$ một góc",
        "c_stmt": r"Vùng khói hiệu ứng hình nón đỉnh $I$ có đáy là giao của vách kính $(\alpha)$ và quả cầu $(S)$ có thể tích cần bơm là",
        "d_stmt": r"Vách kính $(\alpha)$ cắt quả cầu $(S)$ theo một quỹ đạo tròn $(C)$. Cảm biến lấy nét đặt tại điểm $M(x_1; y_1; z_1)$ thuộc quỹ đạo $(C)$ sao cho khoảng cách từ $M$ đến camera $A$ nhỏ nhất là $m$ và cảm biến đo chiều sâu đặt tại điểm $N(x_2; y_2; z_2)$ thuộc quỹ đạo $(C)$ sao cho khoảng cách từ $N$ đến $A$ lớn nhất là $M$. Khi đó mã hiệu chuẩn tiêu cự phần mềm là $x_1 - 2x_2 + y_1 - 3y_2 + m + M ="
    },
    {
        "space": r"không gian giả lập 3D $Oxyz$ của hệ thống robot phẫu thuật",
        "A_desc": r"vị trí đầu phát tia laser",
        "S_desc": r"khối u",
        "I_desc": r"tâm",
        "plane_desc": r"mặt phẳng mô phân cách",
        "S_name": r"$(S)$",
        "plane_name": r"$(\alpha)$",
        "a_stmt": r"Vị trí đầu phát tia laser $A$ nằm ở khoảng cách an toàn, hoàn toàn bên ngoài khối u $(S)$ (để tránh va chạm vật lý trước khi kích hoạt).",
        "b_stmt": r"Trục chiếu tia laser $IA$ tạo với mặt phẳng mô phân cách $(\alpha)$ một góc",
        "c_stmt": r"Vùng mô cần xử lý nhiệt có dạng khối nón với đỉnh là tâm $I$ và đáy là phần vết cắt giao tuyến của mặt phẳng $(\alpha)$ và khối u $(S)$ có thể tích không gian bằng",
        "d_stmt": r"Mặt phẳng phân cách $(\alpha)$ cắt khối u $(S)$ tạo thành một đường rạch vòng tròn $(C)$. Mũi dao robot được lập trình di chuyển đến điểm $M(x_1; y_1; z_1)$ thuộc đường rạch $(C)$ sao cho khoảng cách truyền tia laser từ $A$ là ngắn nhất (cường độ mạnh nhất, khoảng cách đạt giá trị $m$). Sau đó, mũi dao chuyển đến điểm $N(x_2; y_2; z_2)$ thuộc $(C)$ sao cho khoảng cách từ $A$ là lớn nhất (cường độ yếu nhất, khoảng cách $M$). Khi đó, mã sinh trắc học để hệ thống duyệt lệnh cắt là $x_1 - 2x_2 + y_1 - 3y_2 + m + M ="
    }
]

def fmt_point(p):
    return f"({p[0]}; {p[1]}; {p[2]})"

def generate_question(context_idx=None) -> Tuple[str, str, str]:
    if context_idx is None:
        context = random.choice(CONTEXTS)
    else:
        context = CONTEXTS[context_idx % len(CONTEXTS)]
        
    A = (6, -10, 3)
    I = (0, 2, -3)
    R_tex = r"2\sqrt{6}"
    
    # Mệnh đề A
    a_correct = random.choice([True, False])
    stmt_a_text = context['a_stmt']
    if not a_correct:
        stmt_a_text = stmt_a_text.replace("ngoài", "trong").replace("bên ngoài", "bên trong")
    stmt_a = rf"{'*' if a_correct else ''}a) {stmt_a_text}"
        
    sol_a = rf"""a) {'Đúng' if a_correct else 'Sai'}.
Ta tính khoảng cách $IA$:
$\overrightarrow{{IA}} = (6; -12; 6) \Rightarrow IA = \sqrt{{6^2 + (-12)^2 + 6^2}} = \sqrt{{216}} = 6\sqrt{{6}}$.
Bán kính mặt cầu là $R = {R_tex} = \sqrt{{24}}$.
Vì $IA > R$ (do $\sqrt{{216}} > \sqrt{{24}}$) nên điểm $A$ nằm hoàn toàn bên ngoài mặt cầu $(S)$."""
    
    # Mệnh đề B
    b_correct = random.choice([True, False])
    stmt_b_text = rf"{context['b_stmt']} $60^\circ$."
    b_is_true = False 
    if b_correct:
        stmt_b_text = rf"{context['b_stmt']} $\arcsin\left(\frac{{1}}{{2\sqrt{{3}}}}\right)$."
        b_is_true = True
    stmt_b = rf"{'*' if b_is_true else ''}b) {stmt_b_text}"

    sol_b = rf"""b) {'Đúng' if b_is_true else 'Sai'}.
Đường thẳng $IA$ có vectơ chỉ phương $\overrightarrow{{IA}} = (6; -12; 6) = 6(1; -2; 1)$, ta chọn $\vec{{u}} = (1; -2; 1)$.
Mặt phẳng $(\alpha): x + y = 0$ có vectơ pháp tuyến $\vec{{n}} = (1; 1; 0)$.
Gọi $\phi$ là góc giữa trục $IA$ và mặt phẳng $(\alpha)$, ta có:
$\sin \phi = \frac{{|\vec{{u}} \cdot \vec{{n}}|}}{{|\vec{{u}}| \cdot |\vec{{n}}|}} = \frac{{|1 \cdot 1 + (-2) \cdot 1 + 1 \cdot 0|}}{{\sqrt{{1^2 + (-2)^2 + 1^2}} \cdot \sqrt{{1^2 + 1^2 + 0^2}}}} = \frac{{1}}{{\sqrt{{6}} \cdot \sqrt{{2}}}} = \frac{{1}}{{2\sqrt{{3}}}}$.
Vậy $\phi = \arcsin\left(\frac{{1}}{{2\sqrt{{3}}}}\right) \approx 16,78^\circ \neq 60^\circ$."""
    
    # Mệnh đề C
    c_correct = random.choice([True, False])
    stmt_c_text = rf"{context['c_stmt']} $5$."
    c_is_true = False 
    if c_correct:
        stmt_c_text = rf"{context['c_stmt']} $\frac{{22\pi\sqrt{{2}}}}{{3}}$."
        c_is_true = True
    stmt_c = rf"{'*' if c_is_true else ''}c) {stmt_c_text}"

    sol_c = rf"""c) {'Đúng' if c_is_true else 'Sai'}.
Chiều cao khối nón là khoảng cách từ tâm $I$ đến mặt phẳng đáy $(\alpha)$:
$h = d(I, \alpha) = \frac{{|0 + 2 + 0|}}{{\sqrt{{1^2 + 1^2}}}} = \frac{{2}}{{\sqrt{{2}}}} = \sqrt{{2}}$.
Bán kính đường tròn đáy nón $r$ được tính theo định lý Pytago:
$r = \sqrt{{R^2 - h^2}} = \sqrt{{24 - 2}} = \sqrt{{22}}$.
Thể tích khối nón là: $V = \frac{{1}}{{3}}\pi r^2 h = \frac{{1}}{{3}}\pi (22) (\sqrt{{2}}) = \frac{{22\pi\sqrt{{2}}}}{{3}}$."""
    
    # Mệnh đề D
    d_correct = random.choice([True, False])
    stmt_d_text = rf"{context['d_stmt']} $5$."
    d_is_true = False
    if d_correct:
        stmt_d_text = rf"{context['d_stmt']} $-4 + 4\sqrt{{6}} + 6\sqrt{{10}}$."
        d_is_true = True
    stmt_d = rf"{'*' if d_is_true else ''}d) {stmt_d_text}"

    sol_d = rf"""d) {'Đúng' if d_is_true else 'Sai'}.
Gọi $K$ là hình chiếu vuông góc của $I(0; 2; -3)$ lên $(\alpha)$.
Đường thẳng qua $I$ vuông góc $(\alpha)$ có dạng $\heva{{x = t \\ y = 2 + t \\ z = -3}}$. Thay vào $(\alpha): t + 2 + t = 0 \Rightarrow t = -1$. Do đó $K(-1; 1; -3)$.
Khoảng cách $K$ là tâm của đường tròn $(C)$, bán kính $(C)$ là $r = \sqrt{{22}}$.
Tương tự, gọi $H$ là hình chiếu của $A(6; -10; 3)$ lên $(\alpha)$.
Thay $\heva{{x = 6 + u \\ y = -10 + u \\ z = 3}}$ vào $(\alpha): 6 + u - 10 + u = 0 \Rightarrow u = 2$. Do đó $H(8; -8; 3)$.
Khoảng cách $AH = |2|\sqrt{{2}} = 2\sqrt{{2}}$.
Lấy điểm tuỳ ý $X \in (C)$, do $AH \perp (\alpha)$ nên tam giác $AHX$ vuông tại $H \Rightarrow AX^2 = AH^2 + HX^2$.
Do $AH$ không đổi, $AX$ lớn nhất/nhỏ nhất khi $HX$ lớn nhất/nhỏ nhất, khoảng cách này đạt GTLN/GTNN khi $X$ là giao điểm của đường thẳng $HK$ với đường tròn $(C)$.
Ta có $\overrightarrow{{HK}} = (-9; 9; -6) \Rightarrow HK = 3\sqrt{{22}}$.
$\Rightarrow HX_{{min}} = |HK - r| = 3\sqrt{{22}} - \sqrt{{22}} = 2\sqrt{{22}}$.
$\Rightarrow HX_{{max}} = HK + r = 3\sqrt{{22}} + \sqrt{{22}} = 4\sqrt{{22}}$.
$\Rightarrow m = \sqrt{{AH^2 + HX_{{min}}^2}} = \sqrt{{8 + 88}} = 4\sqrt{{6}}$ (đạt tại điểm $M$).
$\Rightarrow M = \sqrt{{AH^2 + HX_{{max}}^2}} = \sqrt{{8 + 352}} = 6\sqrt{{10}}$ (đạt tại điểm $N$).
Hai điểm $M$ và $N$ nằm trên đường thẳng $HK$.
$\overrightarrow{{KM}} = \frac{{r}}{{HK}}\overrightarrow{{KH}} = \frac{{\sqrt{{22}}}}{{3\sqrt{{22}}}}(9; -9; 6) = (3; -3; 2) \Rightarrow M = K + (3; -3; 2) = (2; -2; -1)$.
$\overrightarrow{{KN}} = -\frac{{r}}{{HK}}\overrightarrow{{KH}} = (-3; 3; -2) \Rightarrow N = K + (-3; 3; -2) = (-4; 4; -5)$.
Với $M(x_1; y_1; z_1)$ và $N(x_2; y_2; z_2)$, ta có: 
$x_1 - 2x_2 + y_1 - 3y_2 = 2 - 2(-4) + (-2) - 3(4) = -4$.
Vậy mã kiểm tra thu được là $-4 + m + M = -4 + 4\sqrt{{6}} + 6\sqrt{{10}}$."""
    
    stem = rf"Trong {context['space']}, cho {context['A_desc']} $A{fmt_point(A)}$, {context['S_desc']} {context['S_name']} có {context['I_desc']} $I{fmt_point(I)}$, bán kính bằng ${R_tex}$ và {context['plane_desc']} {context['plane_name']} có phương trình $x + y = 0$. Xét tính đúng/sai của các mệnh đề sau:"
    
    question = rf"""{stem}

{stmt_a}

{stmt_b}

{stmt_c}

{stmt_d}"""

    solution = rf"""{sol_a}

{sol_b}

{sol_c}

{sol_d}"""

    key = ", ".join(["Đ" if x else "S" for x in [a_correct, b_is_true, c_is_true, d_is_true]])
    
    return question, solution, key

def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    out_dir = os.path.dirname(os.path.abspath(__file__))
    
    content = ""
    keys = []
    
    for i in range(num_questions):
        q, s, k = generate_question(i % len(CONTEXTS))
        keys.append(k)
        content += rf"""Câu {i+1}: {q}

Lời giải:

{s}

"""

    template = r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath, amsfonts, amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\usepackage{tikz}
\usetikzlibrary{calc,angles,quotes}

\newcommand{\heva}[1]{\left\{\begin{aligned}#1\end{aligned}\right.}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)

    out_path = os.path.join(out_dir, "cau_2_questions.tex")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {out_path}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")

if __name__ == "__main__":
    main()
