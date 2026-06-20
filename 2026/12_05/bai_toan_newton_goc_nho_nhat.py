import os
import sys
import random
import argparse
import math
from dataclasses import dataclass

def generate_question(seed=None):
    if seed is not None:
        random.seed(seed)
        
    # Sinh hệ số scale lớn để có nhiều tham số đa dạng, đảm bảo lực là số nguyên
    geom_scale = random.randint(1, 20) * 5
    S_5 = geom_scale // 5
    
    m_A = random.randint(3, 30)
    m_B = random.randint(2, 20)
    
    # Bán kính và vị trí ban đầu
    R_A = 4 * geom_scale
    R_B = 9 * geom_scale
    
    I_A = (0, 0, R_A)
    I_B_x = 8 * geom_scale
    I_B_y = 14 * geom_scale
    I_B = (I_B_x, I_B_y, R_B)
    
    # Gia tốc và lực tác dụng lên B
    # a_B = (6 S, 8 S, 0)
    aB_x = 6 * geom_scale
    aB_y = 8 * geom_scale
    
    FB_x_total = m_B * aB_x
    FB_y_total = m_B * aB_y
    
    FB1_x = random.randint(1, FB_x_total - 1)
    FB2_x = FB_x_total - FB1_x
    FB1_y = random.randint(1, FB_y_total - 1)
    FB2_y = FB_y_total - FB1_y
    
    # Gia tốc A mấu chốt để đạt góc nhỏ nhất là a_A_x = 68 * S_5, a_A_y = 51 * S_5
    FA_x_total = m_A * 68 * S_5
    FA_y_total = m_A * 51 * S_5
    
    solved = False
    for _ in range(500):
        k1 = random.randint(1, 15)
        k2 = random.randint(1, 15)
        x1_cands = [x for x in range(1, FA_x_total//k1 + 1) if (FA_x_total - k1*x) % k2 == 0 and (FA_x_total - k1*x) > 0]
        y1_cands = [y for y in range(1, FA_y_total//k1 + 1) if (FA_y_total - k1*y) % k2 == 0 and (FA_y_total - k1*y) > 0]
        
        if x1_cands and y1_cands:
            x1 = random.choice(x1_cands)
            x2 = (FA_x_total - k1*x1) // k2
            y1 = random.choice(y1_cands)
            y2 = (FA_y_total - k1*y1) // k2
            
            if x1 != y1 or x2 != y2:
                solved = True
                break
                
    if not solved:
        k1, k2 = 1, 1
        x1, x2 = FA_x_total // 2, FA_x_total - (FA_x_total // 2)
        y1, y2 = FA_y_total // 2, FA_y_total - (FA_y_total // 2)
        
    alpha = random.randint(1, 5)
    beta = random.randint(1, 5)
    S = alpha * k1 + beta * k2
    
    expr_S = ""
    if alpha == 1: expr_S += "k_1"
    else: expr_S += f"{alpha}k_1"
    if beta == 1: expr_S += " + k_2"
    else: expr_S += f" + {beta}k_2"

    question = f"""Trong vật lý, Định luật II Newton phát biểu rằng lực tổng hợp tác dụng lên một vật sẽ truyền cho vật đó một gia tốc cùng hướng với lực: $F = ma$. Đặt hệ tọa độ $Oxyz$ với mặt đất $(Oxy)$. Lực tác dụng song song $(Oxy)$.
$\\diamond$ Viên bi $A$ có khối lượng $m_A = {m_A}$ kg, tâm $I_A(0; 0; {R_A})$.
$\\diamond$ Viên bi $B$ có khối lượng $m_B = {m_B}$ kg, tâm $I_B({I_B_x}; {I_B_y}; {R_B})$.
Cả hai viên bi bắt đầu chuyển động từ trạng thái nghỉ. Viên bi $B$ chịu tác dụng hai lực $\\vec{{F_{{B1}}}} = ({FB1_x}; {FB1_y}; 0)$ và $\\vec{{F_{{B2}}}} = ({FB2_x}; {FB2_y}; 0)$.
Sau $t = 2$ giây, hai viên bi xảy ra va chạm. Để quỹ đạo viên bi $A$ tạo với tia $Ox$ một góc nhỏ nhất, người ta tác dụng lên bi $A$ hai lực $\\vec{{F_1}}$ và $\\vec{{F_2}}$ lần lượt cùng hướng $\\overrightarrow{{F_{{A1}}}} = ({x1}; {y1}; 0)$ và $\\overrightarrow{{F_{{A2}}}} = ({x2}; {y2}; 0)$ với độ lớn gấp $k_1$ và $k_2$ lần. Tính biểu thức $S = {expr_S}$."""

    IB_2_x = I_B_x + 2 * aB_x
    IB_2_y = I_B_y + 2 * aB_y

    solution = f"""Gia tốc của $B$ được xác định bởi:
$\\vec{{a_B}} = \\frac{{\\vec{{F_{{B1}}}} + \\vec{{F_{{B2}}}}}}{{m_B}} = \\frac{{({FB1_x + FB2_x}; {(FB1_y + FB2_y)}; 0)}}{{{m_B}}} = ({aB_x}; {aB_y}; 0)$ (m/s$^2$).
Vì $B$ bắt đầu từ trạng thái nghỉ, tọa độ tâm $B$ sau $2$s là:
$I_B(2) = I_B(0) + \\frac{{1}}{{2}}\\vec{{a_B}} \\cdot 2^2 = ({I_B_x} + 2({aB_x}); {I_B_y} + 2({aB_y}); {R_B}) = ({IB_2_x}; {IB_2_y}; {R_B})$.

Khi hai bi va chạm tại $t=2$ s, khoảng cách giữa hai tâm là $I_A(2) I_B(2) = R_A+R_B={13*geom_scale}$. 
Vì $A$ lăn trên mặt $Oxy$ với bán kính $R_A={R_A}$, tâm $I_A(2)$ nằm trên mặt phẳng $z={R_A}$. Khi chiếu vị trí $2$ tâm xuống mặt phẳng này, khoảng cách hình chiếu $d$ là:
$d = \\sqrt{{(I_A(2) I_B(2))^2 - ({R_B} - {R_A})^2}} = \\sqrt{{({13*geom_scale})^2 - ({R_B - R_A})^2}} = {12*geom_scale}$.
Theo hình học phẳng, quỹ đạo của $I_A$ (bắt đầu từ gốc $O$ đến $I_A(2)$) là một đường thẳng đi qua gốc tọa độ. Để khoảng cách từ $I_A(2)$ đến điểm cố định $I_B'(2)({IB_2_x}; {IB_2_y})$ bằng $d$, $I_A(2)$ phải nằm trên đường tròn bán kính $d={12*geom_scale}$ có tâm $I_B'(2)$. 
Góc do quỹ đạo $A$ tạo với trục $Ox$ nhỏ nhất khi đường thẳng chứa quỹ đạo của $A$ chính là tiếp tuyến vẽ từ gốc $O$ đến đường tròn tâm $I_B'(2)$. Qua đó tính được hệ số góc là $\\frac{{3}}{{4}}$, suy ra gia tốc của $A$: $\\vec{{a_A}} = ({68*S_5}; {51*S_5}; 0)$.

Lực tổng hợp tác dụng lên $A$ là $\\vec{{F_A}} = m_A \\vec{{a_A}} = ({FA_x_total}; {FA_y_total}; 0)$ (N).
Lại có: $k_1 \\overrightarrow{{F_{{A1}}}} + k_2 \\overrightarrow{{F_{{A2}}}} = \\vec{{F_A}}$, ta có hệ phương trình:
\\begin{{cases}}
{x1}k_1 + {x2}k_2 = {FA_x_total} \\\\
{y1}k_1 + {y2}k_2 = {FA_y_total}
\\end{{cases}}
Giải hệ trên ta thu được $k_1 = {k1}, k_2 = {k2}$.
Vậy giá trị biểu thức là $S = {expr_S} = {S}$."""

    ans_val = S
    if isinstance(ans_val, int) or (isinstance(ans_val, float) and ans_val.is_integer()):
        key = str(int(ans_val))
    else:
        ans_dot = str(round(ans_val, 2))
        ans_comma = ans_dot.replace('.', ',')
        key = f"{ans_dot} | {ans_comma}"

    return question, solution, key

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("num_questions", type=int, default=1, nargs='?')
    args = parser.parse_args()
    
    with open("bai_toan_newton_goc_nho_nhat.tex", "w", encoding="utf-8") as f:
        f.write("\\documentclass{article}\\usepackage[utf8]{inputenc}\\usepackage[vietnamese]{babel}\\usepackage{amsmath}\\begin{document}\n")
        f.write("\\section*{Ví dụ 6 (Đa dạng tham số)}\n")
        for i in range(args.num_questions):
            q, s, a = generate_question()
            f.write(f"\\subsection*{{Câu {i+1}}}\n{q}\nLời giải:\n{s}\nĐáp án: {a}\n\\vspace{{1cm}}\n")
        f.write("\\end{document}\n")

if __name__ == "__main__":
    main()
