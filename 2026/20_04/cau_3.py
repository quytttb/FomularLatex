import math
import os
import sys
import random
from fractions import Fraction
from typing import Tuple

CONTEXTS = [
    {
        "space": r"Trung tâm TED",
        "A_desc": r"học sinh học tập",
        "S_desc": r"mái nhà",
        "I_desc": r"hộp điện",
        "plane_desc": r"mặt phẳng",
        "a_stmt": r"Đáy của mái nhà nằm trên mặt phẳng $z - 2 = 0$.",
        "b_stmt": r"Tọa độ đỉnh chóp của mái nhà là $S(5; 4; 5)$.",
        "c_stmt": r"Ông Tâm muốn một mắc hai dây đèn led một dây LED xanh nối từ $A$ đến $D^\prime$ một dây nối đỏ từ $C$ đến $B^\prime$. Trong cùng một dây hai dây đèn từ $A$ đến $D^\prime$ và từ $C$ đến $B^\prime$ phát ra hai tia sáng với tốc độ lần lượt là $1.5cm/s$ và $3cm/s$. Khi đó, khoảng cách ngắn nhất giữa hai tia sáng là $2m$ (làm tròn đến hàng phần chục).",
        "d_stmt": r"Ông Tâm có mua một cây thông cao $10m$ và trồng ở vị trí $(-8; -8; 0)$ để trang trí cho trung tâm trong dịp giáng sinh sắp tới. Biết rằng để kéo điện thắp sáng ngôi sao trên đỉnh có chữ TED (rất đẹp), ông Tâm phải đục một lỗ nhỏ trên mái nhà và kéo điện từ hộp điện nằm ở tâm của xà nhà lên đỉnh của ngôi sao đó. Ngoài ra để cho không khí thêm ấm cúng, ông Tâm mua một dây LED cắm từ hộp điện đến một điểm $M$ cách $D$ $0.5m$ rồi từ đó cuốn quanh tất cả các bức tường và lại quay trở lại $M$. Độ dài tối thiểu của dây điện và dây đèn cần dùng là làm tròn đến hàng phần trăm"
    }
]

def fmt_point(p):
    return f"({p[0]}; {p[1]}; {p[2]})"

def generate_question(context_idx=None) -> Tuple[str, str, str]:
    if context_idx is None:
        context = random.choice(CONTEXTS)
    else:
        context = CONTEXTS[context_idx % len(CONTEXTS)]
        
    A = (6, 4, 2)
    B = (6, 6, 2)
    C = (4, 6, 2)
    D = (4, 4, 2)
    
    stem = rf"Trung tâm TED mới xây một ngôi nhà mới để cho học sinh học tập trải nghiệm có mái nhà là hình chóp tứ giác đều $S.ABCD$ có chiều cao là 2 mét. Trong hệ tọa độ $Oxyz$ (đơn vị đo trên các trục tính bằng mét), với các điểm ở đáy là $A(6; 4; 2)$, $B(6; 6; 2)$, $C(4; 6; 2)$, $D(4; 4; 2)$ và $S$ là đỉnh của mái nhà. Xét tính đúng/sai của các mệnh đề sau:"
    
    # Mệnh đề A
    a_correct = random.choice([True, False])
    stmt_a_text = context['a_stmt']
    if not a_correct:
        stmt_a_text = stmt_a_text.replace("z - 2 = 0", "z - 4 = 0")
    stmt_a = rf"{'*' if a_correct else ''}a) {stmt_a_text}"
        
    sol_a = rf"""a) {'Đúng' if a_correct else 'Sai'}.
Ta có các điểm ở đáy mái nhà: $A(6;4;2)$, $B(6;6;2)$, $C(4;6;2)$, $D(4;4;2)$.
Nhận thấy tọa độ z của cả bốn điểm đều bằng 2, do đó các điểm $A$, $B$, $C$, $D$ cùng nằm trên mặt phẳng $z=2$ hay $z-2=0$."""
    
    # Mệnh đề B
    b_correct = random.choice([True, False])
    stmt_b_text = context['b_stmt']
    if b_correct:
         stmt_b_text = stmt_b_text.replace("S(5; 4; 5)", "S(5; 5; 4)")
    stmt_b = rf"{'*' if b_correct else ''}b) {stmt_b_text}"

    sol_b = rf"""b) {'Đúng' if b_correct else 'Sai'}.
Tâm của hình chữ nhật $ABCD$ là $O(\frac{{6+4}}{{2}};\frac{{4+6}}{{2}};2)=(5;5;2)$.
Do mái nhà là hình chóp có chiều cao bằng 2 và đỉnh $S$ nằm trên đường thẳng vuông góc với mặt phẳng đáy tại $O$, nên tọa độ đỉnh chóp là $S(5;5;4)$.
{'Trong khi đó mệnh đề cho rằng $S(5;4;5)$ là tọa độ đỉnh chóp, điều này không đúng.' if not b_correct else 'Điều này khớp với mệnh đề.'}"""
    
    # Mệnh đề C
    c_correct = random.choice([True, False])
    stmt_c_text = context['c_stmt']
    if c_correct:
        stmt_c_text = stmt_c_text.replace("2m", "2.8m")
    stmt_c = rf"{'*' if c_correct else ''}c) {stmt_c_text}"

    sol_c = rf"""c) {'Đúng' if c_correct else 'Sai'}.
Giả sử các bức tường của ngôi nhà vuông góc với mặt đất $z=0$. Lấy các điểm $A^{{\prime}}$, $B^{{\prime}}$, $C^{{\prime}}$, $D^{{\prime}}$ lần lượt là các hình chiếu vuông góc của $A$, $B$, $C$, $D$ xuống mặt phẳng $z=0$.
Ta có $A(6;4;2)$, $C(4;6;2)$, $D^{{\prime}}(4;4;0)$, $B^{{\prime}}(6;6;0)$.
$\overrightarrow{{AD^{{\prime}}}}=(-2;0;-2)$.
$|\overrightarrow{{AD^{{\prime}}}}|=2\sqrt{{2}} \Rightarrow \vec{{u}}_{{1}}=(-\frac{{1}}{{\sqrt{{2}}}};0;-\frac{{1}}{{\sqrt{{2}}}})$.
Vì $AQ=0,015t$ nên $Q(6-\frac{{0,015t}}{{\sqrt{{2}}}};4;2-\frac{{0,015t}}{{\sqrt{{2}}}})$.
$\overrightarrow{{CB^{{\prime}}}}=(2;0;-2)$, $|\overrightarrow{{CB^{{\prime}}}}|=2\sqrt{{2}} \Rightarrow \vec{{u}}_{{2}}=(\frac{{1}}{{\sqrt{{2}}}};0;-\frac{{1}}{{\sqrt{{2}}}})$.
$CR=0,03t$ nên $R(4+\frac{{0,03t}}{{\sqrt{{2}}}};6;2-\frac{{0,03t}}{{\sqrt{{2}}}})$.
$QR^2=(-2-\frac{{0,045t}}{{\sqrt{{2}}}})^2+(-2)^2+(\frac{{0,015t}}{{\sqrt{{2}}}})^2=8+\frac{{0,18}}{{\sqrt{{2}}}}t+0,001125t^2$.
$(QR^2)^{{\prime}}=\frac{{0,18}}{{\sqrt{{2}}}}+0,00225t>0 \ (t\ge0) \Rightarrow QR_{{\text{{min}}}}=QR(0)=\sqrt{{8}}=2\sqrt{{2}}\approx 2,8$ m.
{'Khoảng cách ngắn nhất khác 2m nên mệnh đề sai.' if not c_correct else 'Khoảng cách xấp xỉ 2,8m nên mệnh đề đúng.'}"""
    
    # Mệnh đề D
    d_correct = random.choice([True, False])
    stmt_d_text = context['d_stmt']
    if d_correct:
         stmt_d_text = stmt_d_text + " là $32,55$ m."
    else:
         stmt_d_text = stmt_d_text + " là $30,00$ m."
    stmt_d = rf"{'*' if d_correct else ''}d) {stmt_d_text}"

    sol_d = rf"""d) {'Đúng' if d_correct else 'Sai'}.
Phần dây điện thắp sáng ngôi sao:
Hộp điện đặt tại tâm xà nhà (đáy nhà) $I(5;5;2)$.
Cây thông ở vị trí $(-8;-8;0)$, cao 10 m nên đỉnh cây thông là $T(-8;-8;10)$.
Độ dài dây điện cần dùng là $IT=\sqrt{{(-8-5)^2+(-8-5)^2+(10-2)^2}}\approx 20,05$ m.

Phần dây đèn LED:
Phần dây đèn LED chia làm 2 phần: phần 1 là đoạn nối từ hộp điện đến điểm $M$ và phần 2 từ $M$ cuốn quanh các bức tường.
Độ dài phần 1 chính là độ dài $IM$. Do $M$ cách $D$ 0,5m và thuộc đoạn $CD$ nên ta có $M(4;4,5;2)$.
Suy ra $IM = \sqrt{{(4-5)^2 + (4,5-5)^2 + (2-2)^2}} = \sqrt{{1 + 0,25}} = \sqrt{{1,25}} \approx 1,118$ m.
Bằng định lý Pytago (phương pháp trải phẳng), ta có thể tính được độ dài đường ngắn nhất cuốn quanh tường xấp xỉ $11,385$ m.
Do đó độ dài đường ngắn nhất của dây đèn LED là $11,385+1,118=12,503$ m.
Vậy tổng độ dài phần dây điện và phần đèn LED là $12,503 + 20,05 = 32,553$ m."""
    
    question = rf"""{stem}

{stmt_a}

{stmt_b}

{stmt_c}

{stmt_d}"""

    solution = rf"""{sol_a}

{sol_b}

{sol_c}

{sol_d}"""

    key = ", ".join(["Đ" if x else "S" for x in [a_correct, b_correct, c_correct, d_correct]])
    
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

    out_path = os.path.join(out_dir, "cau_3_questions.tex")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {out_path}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")

if __name__ == "__main__":
    main()