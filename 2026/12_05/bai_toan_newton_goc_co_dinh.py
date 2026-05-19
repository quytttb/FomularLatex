import os
import sys
import random
import argparse
import math
from dataclasses import dataclass

def generate_question(seed=None):
    if seed is not None:
        random.seed(seed)
        
    # Sinh ngẫu nhiên tham số mở rộng để tạo được >50 bộ tỷ lệ đẹp (geom_scale từ 1 đến 50)
    geom_scale = random.randint(1, 50)
    
    # Sinh ngẫu nhiên khối lượng (hàng chục giá trị chẵn)
    m_A = random.randint(5, 50) * 2
    m_B = random.randint(2, 40) * 2
    
    # Bán kính viền (do đặt trên mặt đất Oxy) - tương ứng theo scale
    R_A = 5 * geom_scale
    R_B = 20 * geom_scale
    
    # Vị trí ban đầu
    I_A = (0, 0, R_A)
    # Tọa độ A, B theo tỷ lệ
    IB_x = -30 * geom_scale
    IB_y = -30 * geom_scale # Hệ số của căn 3
    I_B = (IB_x, f"{IB_y}\\sqrt{{3}}", R_B)
    
    # Gia tốc B thiết lập
    aB_x = 11 * geom_scale
    aB_y = 11 * geom_scale # Hệ số của căn 3
    
    # Lực tác dụng lên B
    FB_x_total = m_B * aB_x
    FB_y_total = m_B * aB_y
    
    FB1_x = random.randint(1, FB_x_total - 1)
    FB2_x = FB_x_total - FB1_x
    
    FB1_y = random.randint(1, FB_y_total - 1)
    FB2_y = FB_y_total - FB1_y
    
    # Mục tiêu lực A để quỹ đạo tạo góc 60 độ (a_A = S, S \sqrt{3}, 0)
    FA_x_total = m_A * geom_scale
    FA_y_total = m_A * geom_scale # Hệ số của \sqrt{3}
    
    # Phân tách ngẫu nhiên FA thành tổ hợp tuyến tính k1*FA1 + k2*FA2
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
            
            if x1 != y1 or x2 != y2: # Tăng độ đa dạng, tránh trùng lặp hệ số
                solved = True
                break
                
    if not solved:
        k1, k2 = 1, 1
        x1, x2 = FA_x_total // 2, FA_x_total - (FA_x_total // 2)
        y1, y2 = FA_y_total // 2, FA_y_total - (FA_y_total // 2)
        if x2 == 0: x2 = 1; x1 = FA_x_total - k2*1
        if y2 == 0: y2 = 1; y1 = FA_y_total - k2*1
        
    alpha = random.randint(1, 5)
    beta = random.randint(1, 5)
    S = alpha * k1 + beta * k2
    
    expr_S = ""
    if alpha == 1: expr_S += "k_1"
    else: expr_S += f"{alpha}k_1"
    if beta == 1: expr_S += " + k_2"
    else: expr_S += f" + {beta}k_2"

    question = f"""Trong vật lý, Định luật II Newton phát biểu rằng lực tổng hợp tác dụng lên một vật sẽ truyền cho vật đó một gia tốc cùng hướng với lực: $F = ma$. Áp dụng nguyên lý này vào không gian với hệ trục tọa độ $Oxyz$ (quy ước đơn vị trên mỗi trục là mét và lực được tính theo Newton), cho mặt đất trùng với mặt phẳng $(Oxy)$. Lực tác dụng song song $(Oxy)$.
$\\diamond$ Viên bi $A$ có khối lượng $m_A = {m_A}$ kg, tâm ban đầu $I_A(0; 0; {R_A})$.
$\\diamond$ Viên bi $B$ có khối lượng $m_B = {m_B}$ kg, tâm ban đầu $I_B({IB_x}; {IB_y}\\sqrt{{3}}; {R_B})$.
Cùng một lúc, cả hai viên bi bắt đầu chuyển động từ trạng thái nghỉ. Viên bi $B$ chịu tác dụng đồng thời của hai lực không đổi $\\vec{{F_{{B1}}}} = ({FB1_x}; {FB1_y}\\sqrt{{3}}; 0)$ và $\\vec{{F_{{B2}}}} = ({FB2_x}; {FB2_y}\\sqrt{{3}}; 0)$.
Biết rằng sau đúng $t = 2$ giây kể từ lúc bắt đầu chuyển động, hai viên bi xảy ra va chạm. Để quỹ đạo chuyển động của viên bi $A$ tạo với trục $Ox$ một góc bằng $60^\\circ$, người ta tác dụng đồng thời lên viên bi $A$ hai lực $\\vec{{F_1}}$ và $\\vec{{F_2}}$ lần lượt cùng hướng với hai vector $\\overrightarrow{{F_{{A1}}}} = ({x1}; {y1}\\sqrt{{3}}; 0)$ và $\\overrightarrow{{F_{{A2}}}} = ({x2}; {y2}\\sqrt{{3}}; 0)$ với độ lớn gấp $k_1$ và $k_2$ lần. Tính giá trị biểu thức $S = {expr_S}$."""

    IB_2_x = IB_x + 2 * aB_x
    IB_2_y = IB_y + 2 * aB_y
    IA_2_x = 2 * geom_scale
    IA_2_y = 2 * geom_scale

    solution = f"""Gia tốc của $B$: $\\vec{{a_B}} = \\frac{{\\vec{{F_{{B1}}}} + \\vec{{F_{{B2}}}}}}{{m_B}} = ({aB_x}; {aB_y}\\sqrt{{3}}; 0)$. Tọa độ $I_B(2) = ({IB_2_x}; {IB_2_y}\\sqrt{{3}}; {R_B})$.
Khoảng cách va chạm giữa hai tâm lúc $t=2$: $R_A + R_B = {R_A} + {R_B} = {R_A+R_B}$.
Quỹ đạo $A$ tạo góc $60^\\circ$ nên $I_A(2)$ nằm trên đường $y = x\\sqrt{{3}}$ (với $z={R_A}$).
Từ điều kiện mặt cầu tiếp xúc suy ra $\\vec{{a_A}} = ({geom_scale}; {geom_scale}\\sqrt{{3}}; 0) \\Rightarrow \\vec{{F_A}} = m_A \\vec{{a_A}} = ({FA_x_total}; {FA_y_total}\\sqrt{{3}}; 0)$.
Lực tác dụng lên $A$: $k_1 \\overrightarrow{{F_{{A1}}}} + k_2 \\overrightarrow{{F_{{A2}}}} = \\vec{{F_A}} \\Rightarrow k_1 = {k1}, k_2 = {k2}$.
Vậy $S = {S}$."""

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
    
    with open("bai_toan_newton_goc_co_dinh.tex", "w", encoding="utf-8") as f:
        f.write("\\documentclass{article}\\usepackage[utf8]{inputenc}\\usepackage[vietnamese]{babel}\\usepackage{amsmath}\\begin{document}\n")
        f.write("\\section*{Ví dụ 5 (Đa dạng tham số)}\n")
        for i in range(args.num_questions):
            q, s, a = generate_question()
            f.write(f"\\subsection*{{Câu {i+1}}}\n{q}\nLời giải:\n{s}\nĐáp án: {a}\n\\vspace{{1cm}}\n")
        f.write("\\end{document}\n")

if __name__ == "__main__":
    main()
