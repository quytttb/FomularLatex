import os
import sys
import random
import argparse

def format_coord(c):
    return f"({c[0]}; {c[1]}; {c[2]})"

def poly(c0, c2):
    if c2 == 0: return str(c0)
    term2 = f"{c2}t^2" if abs(c2) != 1 else ("t^2" if c2 == 1 else "-t^2")
    if c0 == 0: return term2
    return f"{c0} + {term2}" if c2 > 0 else f"{c0} {term2}"

def lin(c0, c1):
    if c1 == 0: return str(c0)
    term1 = f"{c1}t" if abs(c1) != 1 else ("t" if c1 == 1 else "-t")
    if c0 == 0: return term1
    return f"{c0} + {term1}" if c1 > 0 else f"{c0} {term1}"

def generate_question(seed=None):
    if seed is not None:
        random.seed(seed)
        
    while True:
        # Sinh hệ số scale lớn (từ 1 đến 50) để tạo bộ tham số không giới hạn
        geom_scale = random.randint(1, 40)
        
        t = random.randint(2, 5) # Thời điểm va chạm
        m = random.randint(1, 4) # Khối lượng
        
        # 1. Chọn vector pháp tuyến n dựa trên các bộ số Pytago cơ bản nhân với geom_scale
        base_triplets = [
            (3, 4, 0, 5), (4, 3, 0, 5), (0, 3, 4, 5), (0, 4, 3, 5), (3, 0, 4, 5), (4, 0, 3, 5),
            (5, 12, 0, 13), (12, 5, 0, 13), (0, 5, 12, 13), (0, 12, 5, 13),
            (6, 8, 0, 10), (8, 6, 0, 10), (8, 15, 0, 17), (15, 8, 0, 17),
            (0, 8, 15, 17), (0, 15, 8, 17), (8, 0, 15, 17), (15, 0, 8, 17)
        ]
        bx, by, bz, br = random.choice(base_triplets)
        nx = bx * geom_scale * random.choice([1, -1])
        ny = by * geom_scale * random.choice([1, -1])
        nz = bz * geom_scale * random.choice([1, -1])
        R = br * geom_scale
        n = (nx, ny, nz)
        
        # 2. Chọn vector chỉ phương của thanh MN
        if nz == 0:
            ux, uy = -ny, nx
            uz = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]) * geom_scale
        elif nx == 0:
            uy, uz = -nz, ny
            ux = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]) * geom_scale
        else: # ny == 0
            ux, uz = -nz, nx
            uy = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]) * geom_scale
            
        mn_len_scale = random.choice([2, 4])
        MN = (ux * mn_len_scale, uy * mn_len_scale, uz * mn_len_scale)
        if MN == (0, 0, 0): continue
        
        # 3. Chọn gia tốc và vận tốc
        ax = 2 * random.randint(-5, 5) * geom_scale
        ay = 2 * random.randint(-5, 5) * geom_scale
        az = 2 * random.randint(-5, 5) * geom_scale
        a = (ax, ay, az)
        
        vx = random.randint(-8, 8) * geom_scale
        vy = random.randint(-8, 8) * geom_scale
        vz = random.randint(-8, 8) * geom_scale
        v = (vx, vy, vz)
        
        # Phải đảm bảo đang tiến lại gần (n . dD/dt < 0)
        dot_val = nx*(vx - ax*t) + ny*(vy - ay*t) + nz*(vz - az*t)
        if dot_val >= 0:
            v = (vx - 2*nx, vy - 2*ny, vz - 2*nz)
            dot_val = nx*(vx - ax*t) + ny*(vy - ay*t) + nz*(vz - az*t)
        if dot_val >= 0: continue
            
        # 4. Xác định tọa độ
        I0 = (random.randint(-15, 15)*geom_scale, random.randint(-15, 15)*geom_scale, random.randint(-15, 15)*geom_scale)
        
        It = (I0[0] + (ax * t**2)//2, I0[1] + (ay * t**2)//2, I0[2] + (az * t**2)//2)
        Et = (It[0] + nx, It[1] + ny, It[2] + nz)
        E0 = (Et[0] - vx*t, Et[1] - vy*t, Et[2] - vz*t)
        
        M0 = (E0[0] + MN[0]//2, E0[1] + MN[1]//2, E0[2] + MN[2]//2)
        N0 = (E0[0] - MN[0]//2, E0[1] - MN[1]//2, E0[2] - MN[2]//2)
        
        Fx = m * ax
        Fy = m * ay
        Fz = m * az
        F = (Fx, Fy, Fz)
        
        F1 = (random.randint(-20, 20)*geom_scale, random.randint(-20, 20)*geom_scale, random.randint(-20, 20)*geom_scale)
        F2 = (Fx - F1[0], Fy - F1[1], Fz - F1[2])
        
        break
        
    question = f"""Trong vật lý, định luật II Newton phát biểu rằng lực tổng hợp tác dụng lên một vật sẽ truyền cho vật đó một gia tốc cùng hướng với lực: $\\vec{{F}} = m\\vec{{a}}$. Áp dụng nguyên lý này vào không gian với hệ trục tọa độ $Oxyz$ (quy ước đơn vị chiều dài là mét, thời gian là giây, lực là Newton).
Một mặt cầu $(S)$ có khối lượng $m = {m}\\text{{ kg}}$, bán kính $R = {R}\\text{{ m}}$, ban đầu có tâm nằm tại vị trí $I_0{format_coord(I0)}$ và đang đứng yên. Bắt đầu từ thời điểm $t = 0$, mặt cầu chịu tác dụng đồng thời của hai lực không đổi $\\vec{{F_1}} = {format_coord(F1)}$ và $\\vec{{F_2}} = {format_coord(F2)}$ khiến nó chuyển động tịnh tiến.
Cùng lúc đó, một thanh cứng $MN$ (bỏ qua bề dày) ban đầu có hai đầu mút tại $M_0{format_coord(M0)}$ và $N_0{format_coord(N0)}$ bắt đầu chuyển động tịnh tiến với vận tốc không đổi $\\vec{{v}} = {format_coord(v)}\\text{{ m/s}}$. Giả thiết thanh và mặt cầu không bị biến dạng hay thay đổi hướng trong suốt quá trình di chuyển.

Biết rằng sau $t$ giây thì mặt cầu sẽ va chạm với thanh cứng tại điểm có tọa độ $(x_0; y_0; z_0)$. Khi đó giá trị của biểu thức $T = t + x_0 + y_0 + z_0$ bằng bao nhiêu?"""

    I_poly_x = poly(I0[0], a[0]//2)
    I_poly_y = poly(I0[1], a[1]//2)
    I_poly_z = poly(I0[2], a[2]//2)
    
    M_lin_x = lin(M0[0], v[0])
    M_lin_y = lin(M0[1], v[1])
    M_lin_z = lin(M0[2], v[2])
    
    N_lin_x = lin(N0[0], v[0])
    N_lin_y = lin(N0[1], v[1])
    N_lin_z = lin(N0[2], v[2])
    
    E_lin_x = lin(E0[0], v[0])
    E_lin_y = lin(E0[1], v[1])
    E_lin_z = lin(E0[2], v[2])

    solution = f"""Lực tổng hợp tác dụng lên mặt cầu:
$\\vec{{F}} = \\vec{{F_1}} + \\vec{{F_2}} = {format_coord(F1)} + {format_coord(F2)} = {format_coord(F)}$ (N).
Gia tốc của mặt cầu:
$\\vec{{a}} = \\frac{{\\vec{{F}}}}{{m}} = \\frac{{{format_coord(F)}}}{{{m}}} = {format_coord(a)}$ (m/s$^2$).

Phương trình chuyển động của tâm $I(t)$ do ban đầu đứng yên ($v_{{0S}} = 0$):
$I(t) = I_0 + \\frac{{1}}{{2}}\\vec{{a}}t^2 = ({I_poly_x}; {I_poly_y}; {I_poly_z})$.
    
Vận tốc của thanh $MN$ là $\\vec{{v}} = {format_coord(v)}$. Phương trình chuyển động của một điểm bất kỳ trên thanh:
$X(t) = X(0) + \\vec{{v}}t$. Do đó thanh tịnh tiến đều. Vector chỉ phương của thanh không đổi là $\\overrightarrow{{MN}} = M_0 - N_0 = {format_coord(MN)}$.

Khi mặt cầu va chạm với thanh cứng tại thời điểm $t_0$, khoảng cách từ tâm $I(t_0)$ đến đường thẳng chứa thanh $MN$ bằng chính bán kính $R = {R}$.
Xét tại thời điểm $t = {t}$ (s):
Tọa độ tâm mặt cầu: $I({t}) = {format_coord(It)}$.
Tính hình chiếu vuông góc $H$ của $I({t})$ lên đường thẳng chứa $MN$:
Lấy một điểm $E$ trên đoạn $MN$ tại thời điểm $t$: $E({t}) = {format_coord(Et)}$. 
Ta có vector từ điểm $I({t})$ đến $E({t})$ là $\\overrightarrow{{I({t})E({t})}} = {format_coord(n)}$.
Kiểm tra tính vuông góc: $\\overrightarrow{{I({t})E({t})}} \\cdot \\overrightarrow{{MN}} = {n[0]}\\times({MN[0]}) + {n[1]}\\times({MN[1]}) + {n[2]}\\times({MN[2]}) = 0$.
Suy ra $E({t})$ chính là hình chiếu vuông góc $H$ của $I({t})$ lên đường thẳng $MN$.
Khoảng cách từ $I({t})$ đến đường thẳng $MN$ bằng độ dài $I({t})E({t}) = \\sqrt{{{n[0]}^2 + {n[1]}^2 + {n[2]}^2}} = {R} = R$.
Điều này chứng tỏ tại $t = {t}$ (s), mặt cầu tiếp xúc hoàn hảo với thanh cứng. Đây chính là thời điểm va chạm.

Điểm va chạm $H$ có tọa độ $H({Et[0]}; {Et[1]}; {Et[2]})$.
Do đó $x_0 = {Et[0]}, y_0 = {Et[1]}, z_0 = {Et[2]}$.
Giá trị biểu thức cần tính là: 
$T = t + x_0 + y_0 + z_0 = {t} + {Et[0]} + {Et[1]} + {Et[2]} = {t + Et[0] + Et[1] + Et[2]}$."""

    ans_val = t + Et[0] + Et[1] + Et[2]
    key = f"{ans_val}"
    
    return question, solution, key

def main():
    parser = argparse.ArgumentParser(description="Sinh đề tự động bài toán Newton mặt cầu")
    parser.add_argument("num_questions", type=int, default=1, nargs='?', help="Số lượng câu hỏi cần sinh")
    args = parser.parse_args()
    
    tex_filename = "bai_toan_newton_mat_cau.tex"
    with open(tex_filename, "w", encoding="utf-8") as f:
        f.write("\\documentclass{article}\n")
        f.write("\\usepackage[utf8]{inputenc}\n")
        f.write("\\usepackage[vietnamese]{babel}\n")
        f.write("\\usepackage{amsmath}\n")
        f.write("\\begin{document}\n")
        f.write("\\section*{Bài tập Mặt cầu chuyển động}\n")
        
        for i in range(args.num_questions):
            q, s, a = generate_question()
            f.write(f"\\subsection*{{Câu {i+1}}}\n")
            f.write(f"{q}\n\\vspace{{0.5cm}}\n")
            f.write(f"Lời giải:\n")
            f.write(f"{s}\n\\vspace{{0.5cm}}\n")
            f.write(f"Đáp án: {a}\n")
            f.write("\\vspace{1cm}\n")
            
        f.write("\\end{document}\n")

if __name__ == "__main__":
    main()
