import os
import sys
import random
import fcntl
import argparse
from math import pi, sin, cos, sqrt

def generate_question():
    # Sinh ngẫu nhiên các tham số đa dạng, lấy từ tập hàng chục các bộ số đẹp (hơn 50 tham số)
    
    # 54 bộ Pytago cho width, height để đảm bảo đường chéo AC là số nguyên đẹp
    DIMENSIONS = [
        (20, 15), (24, 18), (28, 21), (32, 24), (36, 27), (40, 30), 
        (44, 33), (48, 36), (52, 39), (56, 42), (60, 45), (64, 48), 
        (68, 51), (72, 54), (76, 57), (80, 60), (24, 10), (36, 15), 
        (48, 20), (60, 25), (72, 30), (84, 35), (30, 16), (45, 24), 
        (60, 32), (75, 40), (90, 48), (48, 14), (72, 21), (96, 28), 
        (40, 9), (80, 18), (35, 12), (70, 24), (63, 16), (21, 20), 
        (42, 40), (63, 60), (15, 20), (18, 24), (21, 28), (24, 32), 
        (27, 36), (30, 40), (33, 44), (36, 48), (39, 52), (42, 56), 
        (45, 60), (48, 64), (51, 68), (54, 72), (10, 24), (16, 30)
    ]
    w_val, h_val = random.choice(DIMENSIONS)
    width = float(w_val) if w_val % 1 != 0 else int(w_val)
    height = float(h_val) if h_val % 1 != 0 else int(h_val)
    
    # Hơn 60 giá trị đường kính hồ bán nguyệt đẹp (bước nhảy 0.5)
    max_d_int = int(min(60.0, width - 2.0) * 2)
    min_d_int = min(10, max_d_int - 2)
    valid_diameters = [d / 2.0 for d in range(min_d_int, max_d_int + 1)]
    if not valid_diameters:
        valid_diameters = [max_d_int / 2.0]
    d_val = random.choice(valid_diameters)
    diameter = int(d_val) if d_val == int(d_val) else d_val
    
    # Tập hợp hơn 80 bộ vận tốc bơi và đi bộ đẹp
    # Chọn sao cho tỉ lệ v_swim/v_walk tạo thành số cos(t/2) đẹp: 0.5, 0.6, 0.8
    VELOCITIES = []
    for v_s in range(15, 66): 
        VELOCITIES.append((v_s / 10.0, (v_s * 2) / 10.0))       # Ratio 0.5
    for v_s in range(15, 66, 3): 
        VELOCITIES.append((v_s / 10.0, (v_s * 5 / 3) / 10.0))   # Ratio 0.6
    for v_s in range(16, 65, 4): 
        VELOCITIES.append((v_s / 10.0, (v_s * 5 / 4) / 10.0))   # Ratio 0.8
        
    vs_val, vw_val = random.choice(VELOCITIES)
    v_swim = int(vs_val) if vs_val == int(vs_val) else vs_val
    v_walk = int(vw_val) if vw_val == int(vw_val) else vw_val
    
    # Đổi đơn vị sang m/phút
    v_swim_mpm = v_swim * 1000 / 60
    v_walk_mpm = v_walk * 1000 / 60
    
    radius = diameter / 2
    
    # Tính quãng đường AC
    # C(0, height), A(width, 0)
    AC = sqrt(width**2 + height**2)
    
    # Tính thời gian bơi AC
    t_AC = AC / v_swim_mpm
    
    # Tham số hóa đường tròn tâm I(radius, height), bán kính R = radius
    # Góc t đi từ 0 (tại C) đến pi (tại D)
    # M(radius - radius*cos(t), height + radius*sin(t))
    # Quãng đường bơi CM
    # Vector CM = (radius - radius*cos(t)) - 0, (height + radius*sin(t)) - height
    # CM = sqrt(radius^2(1-cos(t))^2 + radius^2*sin^2(t)) = radius * sqrt(2 - 2cos(t)) = 2*radius*sin(t/2) = diameter * sin(t/2)
    # Thời gian bơi CM: t_CM = diameter * sin(t/2) / v_swim_mpm
    
    # Quãng đường đi bộ từ M qua D(diameter, height) rồi về A(width, 0)
    # Cung MD tương ứng với góc (pi - t)
    # Độ dài cung MD = radius * (pi - t)
    # Quãng đường bò thẳng từ D đến góc trên bên phải E(width, height): width - diameter
    # Quãng đường từ E thẳng xuống A(width, 0): height
    # Tổng quãng đường đi bộ S_walk = radius * (pi - t) + (width - diameter) + height
    # Thời gian đi bộ: t_walk = S_walk / v_walk_mpm
    
    # Tổng thời gian T(t) = t_AC + (diameter/v_swim_mpm)*sin(t/2) + (radius*(pi - t) + width - diameter + height)/v_walk_mpm
    # Đạo hàm T'(t) = (diameter / (2*v_swim_mpm)) * cos(t/2) - radius / v_walk_mpm
    # T'(t) = 0 => cos(t/2) = (radius * 2 * v_swim_mpm) / (v_walk_mpm * diameter) = v_swim_mpm / v_walk_mpm
    
    ratio = v_swim_mpm / v_walk_mpm
    # Với đề mẫu v_swim = 2.7, v_walk = 5.4 => ratio = 0.5
    # cos(t/2) = 0.5 => t/2 = pi/3 => t = 2pi/3
    
    from math import acos
    t_half = acos(ratio)
    t_opt = 2 * t_half
    
    # Tính giá trị lớn nhất
    max_t_CM = (diameter * sin(t_opt/2)) / v_swim_mpm
    max_t_walk = (radius * (pi - t_opt) + (width - diameter) + height) / v_walk_mpm
    total_time = t_AC + max_t_CM + max_t_walk
    
    # Làm tròn đến 2 chữ số thập phân
    ans_val = round(total_time, 2)
    if isinstance(ans_val, int) or (isinstance(ans_val, float) and ans_val.is_integer()):
        key = str(int(ans_val))
    else:
        ans_dot = str(ans_val)
        ans_comma = ans_dot.replace('.', ',')
        key = f"{ans_dot} | {ans_comma}"
    
    width_str = str(width).replace('.', ',')
    height_str = str(height).replace('.', ',')
    diameter_str = str(diameter).replace('.', ',')
    v_swim_str = str(v_swim).replace('.', ',')
    v_walk_str = str(v_walk).replace('.', ',')
    
    question = f"""Bạn Nam thường đi bơi ở hồ bơi Sky Garden cạnh nhà, hồ bơi có thiết kế là một hình chữ nhật với chiều dài ${width_str}m$, chiều rộng ${height_str}m$ và bên cạnh đó có một hồ bán nguyệt đường kính ${diameter_str}m$ (như hình vẽ). Trong một lần bể bơi vắng người nên Nam đã thực hiện một chu trình là bơi theo đoạn thẳng $AC$ rồi bơi tiếp theo đoạn thẳng $CM$, với $M$ là một vị trí bất kì trên hình bán nguyệt. Ngay sau đó bạn đi bộ theo một hướng qua điểm $D$ dọc bờ của hồ bơi để quay lại vị trí $A$ và kết thúc chu trình.

Biết rằng vận tốc bơi của Nam là ${v_swim_str} \\text{{ km/h}}$, vận tốc đi bộ là ${v_walk_str} \\text{{ km/h}}$ và tốc độ bơi, vận tốc đi bộ không thay đổi trong một chu trình. Hỏi thời gian chậm nhất để Nam thực hiện xong chu trình trên là bao nhiêu phút? (kết quả làm tròn đến hàng phần trăm)"""

    solution = f"""Gắn hệ trục tọa độ $Oxy$ với $B(0;0)$ là góc dưới bên trái của hình chữ nhật, $A({width_str}; 0)$.
Điểm $C$ có tọa độ $(0; {height_str})$. Đường thẳng $CD$ nằm trên đường $y={height_str}$, bán nguyệt có đường kính $CD = {diameter_str} \\Rightarrow$ Bán kính $R = {radius}$.
Tâm của bán nguyệt là $I({radius}; {height_str})$.
Tham số hóa tọa độ điểm $M$ trên bán nguyệt: $M({radius} - {radius}\\cos t; {height_str} + {radius}\\sin t)$ với $t \\in [0; \\pi]$.
Khi đó $C$ ứng với $t=0$ và $D$ ứng với $t=\\pi$.

Thời gian bơi đoạn $AC$:
$AC = \\sqrt{{ {width_str}^2 + {height_str}^2 }} = {AC:.2f}$ (m).
Đổi vận tốc bơi: $v_b = {v_swim_str} \\text{{ km/h}} = {v_swim_mpm:.2f} \\text{{ m/phút}}$, vận tốc đi bộ $v_d = {v_walk_str} \\text{{ km/h}} = {v_walk_mpm:.2f} \\text{{ m/phút}}$.
$t_{{AC}} = \\frac{{AC}}{{v_b}} = \\frac{{{AC:.2f}}}{{{v_swim_mpm:.2f}}} \\approx {t_AC:.2f}$ (phút).

Quãng đường bơi $CM$:
Ta có $\\overrightarrow{{CM}} = ({radius} - {radius}\\cos t; {radius}\\sin t) \\Rightarrow CM = \\sqrt{{{radius}^2(1-\\cos t)^2 + {radius}^2\\sin^2 t}} = {diameter} \\sin\\left(\\frac{{t}}{{2}}\\right)$.
Thời gian bơi $CM$: $t_{{CM}} = \\frac{{{diameter}\\sin(t/2)}}{{v_b}}$.

Quãng đường đi bộ từ $M$ về $A$:
Gồm đoạm cung $MD$, đoạn thẳng $DE$ ($E$ là góc trên bên phải) và $EA$.
Cung $MD = R(\\pi - t) = {radius}(\\pi - t)$.
$DE = {width} - {diameter} = {width - diameter}$.
$EA = {height}$.
Tổng quãng đường đi bộ: $S_d = {radius}(\\pi - t) + {width - diameter} + {height}$.
Thời gian đi bộ: $t_d = \\frac{{{radius}(\\pi - t) + {width - diameter + height}}}{{v_d}}$.

Tổng thời gian thực hiện:
$f(t) = t_{{AC}} + t_{{CM}} + t_d = {t_AC:.4f} + \\frac{{{diameter}}}{{{v_swim_mpm:.2f}}} \\sin\\left(\\frac{{t}}{{2}}\\right) + \\frac{{{radius}(\\pi - t) + {width - diameter + height}}}{{{v_walk_mpm:.2f}}}$.
Xét hàm $f(t)$ trên đoạn $[0; \\pi]$:
$f'(t) = \\frac{{{radius}}}{{{v_swim_mpm:.2f}}} \\cos\\left(\\frac{{t}}{{2}}\\right) - \\frac{{{radius}}}{{{v_walk_mpm:.2f}}} = 0$
$\\Leftrightarrow \\cos\\left(\\frac{{t}}{{2}}\\right) = \\frac{{{v_swim_mpm:.2f}}}{{{v_walk_mpm:.2f}}} = {ratio:.2f} \\Rightarrow \\frac{{t}}{{2}} \\approx {t_half:.4f} \\Rightarrow t \\approx {t_opt:.4f} \\text{{ (rad)}}$.

Lập bảng biến thiên, $f(t)$ đạt GTLN tại $t \\approx {t_opt:.4f}$.
Tính được giá trị lớn nhất của thời gian là $T_{{max}} \\approx {ans_val}$ phút.
"""
    return question, solution, key

def main():
    parser = argparse.ArgumentParser(description="Sinh đề tự động bài toán tối ưu hồ bơi")
    parser.add_argument("num_questions", type=int, help="Số lượng câu hỏi cần sinh")
    args = parser.parse_args()
    
    tex_filename = "bai_toan_ho_boi.tex"
    with open(tex_filename, "w", encoding="utf-8") as f:
        f.write("\\documentclass{article}\n")
        f.write("\\usepackage[utf8]{inputenc}\n")
        f.write("\\usepackage[vietnamese]{babel}\n")
        f.write("\\usepackage{amsmath}\n")
        f.write("\\begin{document}\n")
        f.write("\\section*{Bài tập Tối ưu Hồ bơi}\n")
        
        for i in range(args.num_questions):
            q, s, a = generate_question()
            f.write(f"\\subsection*{{Câu {i+1}}}\n")
            f.write(f"{q}\n")
            f.write(f"Lời giải:\n")
            f.write(f"{s}\n")
            f.write(f"Đáp án: {a}\n")
            f.write("\\vspace{1cm}\n")
            
        f.write("\\end{document}\n")
        
    print(f"Đã sinh {args.num_questions} câu hỏi vào {tex_filename}")

if __name__ == "__main__":    
    main()