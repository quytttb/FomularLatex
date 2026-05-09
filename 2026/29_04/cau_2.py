import os
import sys
import random
import math

def generate_params():
    triples = [
        (3, 4, 5),
        (5, 12, 13),
        (6, 8, 10),
        (8, 15, 17),
        (9, 12, 15),
        (12, 16, 20)
    ]
    m, n, k = random.choice(triples)
    c = k**2
    r = n**2 - m**2
    d = 2*m*n
    
    axis = random.choice(['x', 'y'])
    if random.choice([True, False]):
        C1, C2 = m, n
    else:
        C1, C2 = n, m
        
    return m, n, k, c, r, d, axis, C1, C2

def generate_question(seed=None, force_sample=False):
    if seed is not None:
        random.seed(seed)
        
    if force_sample:
        m, n, k = 3, 4, 5
        c = 25
        r = 7
        d = 24
        axis = 'x'
        C1, C2 = 3, 4
    else:
        m, n, k, c, r, d, axis, C1, C2 = generate_params()
        
    if axis == 'x':
        xA, yA, zA = c, 0, d
        xB, yB, zB = -c, 0, d
        var = 'x'
        other_var = 'y'
    else:
        xA, yA, zA = 0, c, d
        xB, yB, zB = 0, -c, d
        var = 'y'
        other_var = 'x'
        
    MA_expr = f"{2*c**2} - {2*c}{var}"
    MB_expr = f"{2*c**2} + {2*c}{var}"
    MA_inter = rf"\sqrt{{{var}^2 - {2*c}{var} + {c**2} + {other_var}^2 + {d**2}}} = \sqrt{{({var}^2 + {other_var}^2) - {2*c}{var} + {c**2 + d**2}}} = \sqrt{{{r**2} - {2*c}{var} + {c**2 + d**2}}}"
    MB_inter = rf"\sqrt{{{var}^2 + {2*c}{var} + {c**2} + {other_var}^2 + {d**2}}} = \sqrt{{({var}^2 + {other_var}^2) + {2*c}{var} + {c**2 + d**2}}} = \sqrt{{{r**2} + {2*c}{var} + {c**2 + d**2}}}"
    
    if C1 == m and C2 == n:
        opt_var = r
        if axis == 'x':
            M1_x, M1_y, M1_z = -r, 0, 0
            M2_x, M2_y, M2_z = r, 0, 0
        else:
            M1_x, M1_y, M1_z = 0, -r, 0
            M2_x, M2_y, M2_z = 0, r, 0
    else:
        opt_var = -r
        if axis == 'x':
            M1_x, M1_y, M1_z = r, 0, 0
            M2_x, M2_y, M2_z = -r, 0, 0
        else:
            M1_x, M1_y, M1_z = 0, r, 0
            M2_x, M2_y, M2_z = 0, -r, 0
            
    a = 4*m*n*k
    b = 2*c*k
    x1, y1, z1 = M1_x, M1_y, M1_z
    x2, y2, z2 = M2_x, M2_y, M2_z
    
    ans_val = a - x1 + 3*x2 - y1 + z2 - 3*b
    
    stem = rf"Trong không gian với hệ tọa độ $Oxyz$ (đơn vị: mét), mặt phẳng $(Oxy)$ có phương trình $z=0$ được mô phỏng là mặt đất bằng phẳng. Một trạm điều khiển flycam di động $M(x ; y ; 0)$ hoạt động trên mặt đất. Trên không trung, có hai tháp phát sóng tín hiệu cố định được đặt tại các vị trí $A({xA} ; {yA} ; {zA})$ và $B({xB} ; {yB} ; {zB})$. Để flycam có thể nhận tín hiệu phân cực vuông góc chuẩn xác từ cả hai tháp cùng lúc, trạm điều khiển $M$ phải luôn di chuyển sao cho góc nhìn từ $M$ lên hai đỉnh tháp duy trì đúng $90^{{\circ}}$ (tức là $\widehat{{AMB}}=90^{{\circ}}$). Hệ thống tính toán cho biết, chi phí năng lượng đồng bộ tín hiệu của trạm $M$ phụ thuộc vào khoảng cách từ trạm đến hai tháp và được tính theo công thức $S={C1} MA+{C2} MB$. Khi $M$ có tọa độ $(x_1;y_1;z_1)$ thì $S$ có giá trị nhỏ nhất là $a$, khi $M$ có tọa độ $(x_2;y_2;z_2)$ thì $S$ có giá trị lớn nhất là $b$. Biểu thức $a-x_1+3x_2-y_1+z_2-3b$ có giá trị bằng bao nhiêu (làm tròn đến hàng phần mười)."
    
    S_deriv = rf"S'({var}) = {C1} \cdot \frac{{-{2*c}}}{{2\sqrt{{{MA_expr}}}}} + {C2} \cdot \frac{{{2*c}}}{{2\sqrt{{{MB_expr}}}}} = \frac{{-{C1 * c}}}{{\sqrt{{{MA_expr}}}}} + \frac{{{C2 * c}}}{{\sqrt{{{MB_expr}}}}}"
    eq_step = rf"\frac{{{C1 * c}}}{{\sqrt{{{MA_expr}}}}} = \frac{{{C2 * c}}}{{\sqrt{{{MB_expr}}}}} \Leftrightarrow {C1}\sqrt{{{MB_expr}}} = {C2}\sqrt{{{MA_expr}}}"
    eq_sq = rf"{C1**2}({MB_expr}) = {C2**2}({MA_expr}) \Leftrightarrow {C1**2 * 2 * c**2} + {C1**2 * 2 * c}{var} = {C2**2 * 2 * c**2} - {C2**2 * 2 * c}{var}"
    eq_solve = rf"{2*c*(C1**2 + C2**2)}{var} = {2*c**2 * (C2**2 - C1**2)} \Leftrightarrow {var} = {opt_var}"
    
    val_MA_minus = int(math.sqrt(2*c**2 - 2*c*(-r)))
    val_MB_minus = int(math.sqrt(2*c**2 + 2*c*(-r)))
    S_minus_r = rf"{C1}\sqrt{{{2*c**2 - 2*c*(-r)}}} + {C2}\sqrt{{{2*c**2 + 2*c*(-r)}}} = {C1}({val_MA_minus}) + {C2}({val_MB_minus}) = {C1*val_MA_minus + C2*val_MB_minus}"
    
    val_MA_plus = int(math.sqrt(2*c**2 - 2*c*(r)))
    val_MB_plus = int(math.sqrt(2*c**2 + 2*c*(r)))
    S_plus_r = rf"{C1}\sqrt{{{2*c**2 - 2*c*(r)}}} + {C2}\sqrt{{{2*c**2 + 2*c*(r)}}} = {C1}({val_MA_plus}) + {C2}({val_MB_plus}) = {C1*val_MA_plus + C2*val_MB_plus}"
    
    sol = rf"""Ta có $\widehat{{AMB}} = 90^{{\circ}}$ nên $M$ thuộc mặt cầu $(S)$ đường kính $AB$. 
Tâm $I$ của mặt cầu là trung điểm của đoạn thẳng $AB \Rightarrow I\left(\frac{{{xA} + ({xB})}}{{2}}; \frac{{{yA} + ({yB})}}{{2}}; \frac{{{zA} + ({zB})}}{{2}}\right)$ hay $I(0; 0; {zA})$.
Bán kính mặt cầu là $R = \frac{{AB}}{{2}} = \frac{{\sqrt{{({xB - xA})^2 + ({yB - yA})^2 + 0^2}}}}{{2}} = \frac{{{2*c}}}{{2}} = {c}$.
Mặt khác, $M(x; y; 0)$ nằm trên mặt đất bằng phẳng, tức là $M \in (Oxy)$ với phương trình $z = 0$.
Suy ra $M$ thuộc đường tròn giao tuyến $(C)$ của mặt phẳng $(Oxy)$ và mặt cầu $(S)$.
Đường tròn $(C)$ có tâm $H$ là hình chiếu vuông góc của tâm $I(0; 0; {zA})$ lên mặt phẳng $(Oxy) \Rightarrow H(0; 0; 0)$.
Bán kính của đường tròn $(C)$ là $r_{{(C)}} = \sqrt{{R^2 - d^2(I, (Oxy))}} = \sqrt{{{c}^2 - {d}^2}} = {r}$.
Vậy $M(x; y; 0)$ luôn di động trên đường tròn có tâm gốc tọa độ $O(0;0;0)$, bán kính $r = {r}$. Từ đó ta có điều kiện $x^2 + y^2 = {r**2}$.
Gọi $A', B'$ lần lượt là hình chiếu vuông góc của $A({xA}; {yA}; {zA})$ và $B({xB}; {yB}; {zB})$ lên mặt phẳng $(Oxy)$.
Ta có $A'({xA}; {yA}; 0)$ với khoảng cách $AA' = d(A, (Oxy)) = {zA}$ và $B'({xB}; {yB}; 0)$ với khoảng cách $BB' = d(B, (Oxy)) = {zB}$.
Áp dụng định lý Pytago, ta tính được $MA$ và $MB$:
$MA = \sqrt{{MA'^2 + AA'^2}} = \sqrt{{({var} - {c})^2 + {other_var}^2 + {d}^2}}$.
Thay $x^2 + y^2 = {r**2}$ vào, ta được $MA = {MA_inter} = \sqrt{{{MA_expr}}}$.
Tương tự, $MB = \sqrt{{MB'^2 + BB'^2}} = \sqrt{{({var} + {c})^2 + {other_var}^2 + {d}^2}}$.
Thay $x^2 + y^2 = {r**2}$ vào, ta được $MB = {MB_inter} = \sqrt{{{MB_expr}}}$.
Hàm chi phí năng lượng cần tối ưu là $S = {C1}MA + {C2}MB = {C1}\sqrt{{{MA_expr}}} + {C2}\sqrt{{{MB_expr}}}$.
Với điều kiện $M$ thuộc đường tròn bán kính {r}, ta có ${var} \in [-{r}; {r}]$. Đạo hàm của $S({var})$:
$${S_deriv}$$
Đặt $S'({var}) = 0 \Rightarrow {eq_step}$.
Bình phương hai vế ta được:
$${eq_sq} \Leftrightarrow {eq_solve}$$
Ta kiểm tra các giá trị tại điểm biên và điểm cực trị:
Tại ${var} = -{r} \Rightarrow {other_var} = 0$: $S(-{r}) = {S_minus_r}$.
Tại ${var} = {r} \Rightarrow {other_var} = 0$: $S({r}) = {S_plus_r}$.
Từ các kết quả trên, ta xác định được:
Giá trị nhỏ nhất $a = {a}$ tại tọa độ $M_1({x1}; {y1}; {z1}) \Rightarrow x_1 = {x1}, y_1 = {y1}, z_1 = {z1}$.
Giá trị lớn nhất $b = {b}$ tại tọa độ $M_2({x2}; {y2}; {z2}) \Rightarrow x_2 = {x2}, y_2 = {y2}, z_2 = {z2}$.
Biểu thức cần tính: $P = a - x_1 + 3x_2 - y_1 + z_2 - 3b = {a} - ({x1}) + 3({x2}) - ({y1}) + ({z2}) - 3({b}) = {ans_val}$."""

    return stem, sol, str(ans_val)

def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    seed_val = None
    if len(sys.argv) > 2:
        seed_val = int(sys.argv[2])
        
    out_dir = os.path.dirname(os.path.abspath(__file__))
    content = ""
    
    for i in range(num_questions):
        seed = seed_val + i if seed_val is not None else None
        force = (i == 0 and seed_val is None)
        q, s, k = generate_question(seed, force_sample=force)
        
        content += rf"""Câu {i+1}: {q}

\textbf{{Lời giải:}}

{s}

\textbf{{Đáp án: {k}}}

"""

    template = r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath, amsfonts, amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)
    out_path = os.path.join(out_dir, "cau_2_questions.tex")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {out_path}")

if __name__ == "__main__":
    main()
