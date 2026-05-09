import os
import sys
import random
import math

def format_plane(A, B, C, D):
    terms = []
    if A != 0:
        if A == 1: terms.append("x")
        elif A == -1: terms.append("-x")
        else: terms.append(f"{A}x")
    if B != 0:
        if B == 1: terms.append("+y" if terms else "y")
        elif B == -1: terms.append("-y")
        else: terms.append(f"+{B}y" if terms and B > 0 else f"{B}y")
    if C != 0:
        if C == 1: terms.append("+z" if terms else "z")
        elif C == -1: terms.append("-z")
        else: terms.append(f"+{C}z" if terms and C > 0 else f"{C}z")
    if D != 0:
        terms.append(f"+{D}" if D > 0 and terms else f"{D}")
    return "".join(terms) + "=0"

def generate_params():
    while True:
        A_p = random.randint(-3, 3)
        B_p = random.randint(-3, 3)
        C_p = random.randint(-3, 3)
        if A_p == 0 and B_p == 0 and C_p == 0:
            continue
        
        D_p = random.randint(-10, 10)
        
        xA = random.randint(-5, 5)
        yA = random.randint(-5, 5)
        zA = random.randint(-5, 5)
        
        xB = random.randint(-5, 5)
        yB = random.randint(-5, 5)
        zB = random.randint(-5, 5)
        
        if xA == xB and yA == yB and zA == zB:
            continue
            
        I_x = (xA + xB) / 2
        I_y = (yA + yB) / 2
        I_z = (zA + zB) / 2
        
        R_sq = ((xA - xB)**2 + (yA - yB)**2 + (zA - zB)**2) / 4
        R = math.sqrt(R_sq)
        
        norm_P_sq = A_p**2 + B_p**2 + C_p**2
        norm_P = math.sqrt(norm_P_sq)
        d = abs(A_p * I_x + B_p * I_y + C_p * I_z + D_p) / norm_P
        
        if d >= R - 0.5:
            continue
            
        r_sq = R_sq - d**2
        if r_sq < 0.1:
            continue
            
        t_H = -(A_p * I_x + B_p * I_y + C_p * I_z + D_p) / norm_P_sq
        H_x = I_x + A_p * t_H
        H_y = I_y + B_p * t_H
        H_z = I_z + C_p * t_H
        
        t_K = -(A_p * xA + B_p * yA + C_p * zA + D_p) / norm_P_sq
        K_x = xA + A_p * t_K
        K_y = yA + B_p * t_K
        K_z = zA + C_p * t_K
        
        HK_sq = (K_x - H_x)**2 + (K_y - H_y)**2 + (K_z - H_z)**2
        if HK_sq < 0.001:
            continue
            
        return {"A": (xA, yA, zA), "B": (xB, yB, zB), "P": (A_p, B_p, C_p, D_p)}

def generate_question(seed=None, force_sample=False):
    if seed is not None:
        random.seed(seed)
        
    if force_sample:
        p = {"A": (3, 4, 1), "B": (7, -4, -3), "P": (1, 1, -1, 2)}
    else:
        p = generate_params()
        
    xA, yA, zA = p["A"]
    xB, yB, zB = p["B"]
    A_p, B_p, C_p, D_p = p["P"]
    P_str = format_plane(A_p, B_p, C_p, D_p)
    if P_str.startswith("+"): P_str = P_str[1:]
    
    I_x = (xA + xB) / 2
    I_y = (yA + yB) / 2
    I_z = (zA + zB) / 2
    
    R_sq = ((xA - xB)**2 + (yA - yB)**2 + (zA - zB)**2) / 4
    R = math.sqrt(R_sq)
    
    norm_P_sq = A_p**2 + B_p**2 + C_p**2
    norm_P = math.sqrt(norm_P_sq)
    d = abs(A_p * I_x + B_p * I_y + C_p * I_z + D_p) / norm_P
    
    r_sq = R_sq - d**2
    r = math.sqrt(r_sq)
    
    t_H = -(A_p * I_x + B_p * I_y + C_p * I_z + D_p) / norm_P_sq
    H_x = I_x + A_p * t_H
    H_y = I_y + B_p * t_H
    H_z = I_z + C_p * t_H
    
    t_K = -(A_p * xA + B_p * yA + C_p * zA + D_p) / norm_P_sq
    K_x = xA + A_p * t_K
    K_y = yA + B_p * t_K
    K_z = zA + C_p * t_K
    
    HK_x = K_x - H_x
    HK_y = K_y - H_y
    HK_z = K_z - H_z
    HK = math.sqrt(HK_x**2 + HK_y**2 + HK_z**2)
    
    u_x = HK_x / HK
    u_y = HK_y / HK
    u_z = HK_z / HK
    
    M1_x = H_x + r * u_x
    M1_y = H_y + r * u_y
    M1_z = H_z + r * u_z
    
    M2_x = H_x - r * u_x
    M2_y = H_y - r * u_y
    M2_z = H_z - r * u_z
    
    AK_sq = (xA - K_x)**2 + (yA - K_y)**2 + (zA - K_z)**2
    AK = math.sqrt(AK_sq)
    
    KM1_sq = (K_x - M1_x)**2 + (K_y - M1_y)**2 + (K_z - M1_z)**2
    KM2_sq = (K_x - M2_x)**2 + (K_y - M2_y)**2 + (K_z - M2_z)**2
    
    AM1 = math.sqrt(AK_sq + KM1_sq)
    AM2 = math.sqrt(AK_sq + KM2_sq)
    
    if AM1 > AM2:
        a, b = AM2, AM1
        x1, y1, z1 = M2_x, M2_y, M2_z
        x2, y2, z2 = M1_x, M1_y, M1_z
    else:
        a, b = AM1, AM2
        x1, y1, z1 = M1_x, M1_y, M1_z
        x2, y2, z2 = M2_x, M2_y, M2_z
        
    ans_val = a + 2*b + x1 + y2 - z1 + 3*z2
    ans_str = f"{ans_val:.1f}".replace('.', ',')
    
    stem = rf"Trên một phim trường 3D được thiết lập theo hệ trục tọa độ không gian $Oxyz$ (đơn vị đo được tính bằng mét), người ta đặt một Trạm điều khiển trung tâm cố định tại vị trí $A({xA}; {yA}; {zA})$ và một đèn chiếu sáng phụ tại vị trí $B({xB}; {yB}; {zB})$. Một robot quay phim tự hành (coi như điểm $M$) được thiết lập để di chuyển liên tục trên một mặt sàn sân khấu nghiêng có phương trình $(P): {P_str}$. Để đảm bảo chất lượng hình ảnh không bị lóa sáng do góc chiếu, hệ thống được lập trình sao cho hướng nhìn từ robot $M$ về phía Trạm $A$ và đèn $B$ luôn tạo với nhau một góc vuông (hay tam giác $ABM$ vuông tại $M$). Đội ngũ kỹ thuật cần nối một sợi cáp truyền dữ liệu trực tiếp từ Trạm $A$ đến robot $M$. Đội kỹ thuật cần chuẩn bị sợi cáp có chiều dài tối thiểu $a$ khi robot ở vị trí $(x_1; y_1; z_1)$ và chiều dài tối đa là $b$ khi robot ở vị trí $(x_2; y_2; z_2)$. Khi đó $a+2b+x_1+y_2-z_1+3z_2$ bằng bao nhiêu (làm tròn đến hàng phần mười)."
    
    sol = rf"""Ta có tam giác $ABM$ vuông tại $M$, do đó $\overrightarrow{{MA}} \cdot \overrightarrow{{MB}} = 0$. Suy ra $M$ nằm trên mặt cầu $(S)$ đường kính $AB$.
Tâm $I$ của mặt cầu $(S)$ là trung điểm $AB \Rightarrow I({I_x:g}; {I_y:g}; {I_z:g})$.
Bán kính mặt cầu $R = \frac{{AB}}{{2}} = \frac{{\sqrt{{({xA}-{xB})^2 + ({yA}-{yB})^2 + ({zA}-{zB})^2}}}}{{2}} \approx {R:.3f}$.
Vì robot di chuyển trên $(P)$ nên $M \in (P)$. Quỹ đạo của $M$ là đường tròn giao tuyến $(C) = (S) \cap (P)$.
Khoảng cách từ $I$ đến $(P)$: $d(I, (P)) = \frac{{|{A_p} \cdot {I_x:g} + {B_p} \cdot {I_y:g} + {C_p} \cdot {I_z:g} + {D_p}|}}{{\sqrt{{{A_p}^2 + {B_p}^2 + {C_p}^2}}}} \approx {d:.3f}$.
Bán kính đường tròn giao tuyến $r = \sqrt{{R^2 - d^2}} \approx {r:.3f}$.
Tâm $H$ của đường tròn $(C)$ là hình chiếu của $I$ lên $(P)$. Phương trình đường thẳng qua $I$ vuông góc với $(P)$ có VTCP $\vec{{n_P}}=({A_p}; {B_p}; {C_p})$, cắt $(P)$ tại $H({H_x:.3g}; {H_y:.3g}; {H_z:.3g})$.
Khoảng cách cáp chính là đoạn $AM$, với $A$ là điểm cố định và $M$ di động trên đường tròn $(C)$.
Gọi $K$ là hình chiếu của $A$ lên $(P)$. Tương tự, ta tìm được $K({K_x:.3g}; {K_y:.3g}; {K_z:.3g})$.
Độ dài $AK = d(A, (P)) \approx {AK:.3f}$.
Ta có $AM^2 = AK^2 + KM^2$. Vì $AK$ vuông góc với $(P)$ nên khoảng cách $AM$ đạt min/max khi và chỉ khi đoạn $KM$ đạt min/max trên mặt phẳng $(P)$.
Do $K, H \in (P)$ và $M$ nằm trên đường tròn tâm $H$ bán kính $r$ trong mặt phẳng $(P)$, ta có $K, H, M$ thẳng hàng khi $KM$ đạt cực trị.
Vectơ $\overrightarrow{{HK}} = ({HK_x:.3g}; {HK_y:.3g}; {HK_z:.3g}) \Rightarrow HK \approx {HK:.3f}$.
Vị trí $M$ cho $KM$ min: $M_{{min}}$ nằm trên tia $\overrightarrow{{HK}}$, do đó $\overrightarrow{{HM_{{min}}}} = r \frac{{\overrightarrow{{HK}}}}{{HK}}$, từ đó tính được $M_{{min}} \approx ({x1:.3f}; {y1:.3f}; {z1:.3f})$.
Vị trí $M$ cho $KM$ max: $M_{{max}}$ nằm trên tia đối của $\overrightarrow{{HK}}$, do đó $\overrightarrow{{HM_{{max}}}} = -r \frac{{\overrightarrow{{HK}}}}{{HK}} \Rightarrow M_{{max}} \approx ({x2:.3f}; {y2:.3f}; {z2:.3f})$.
Chiều dài $a = AM_{{min}} \approx {a:.3f}$, đạt được khi $x_1 \approx {x1:.3f}, y_1 \approx {y1:.3f}, z_1 \approx {z1:.3f}$.
Chiều dài $b = AM_{{max}} \approx {b:.3f}$, đạt được khi $x_2 \approx {x2:.3f}, y_2 \approx {y2:.3f}, z_2 \approx {z2:.3f}$.
Tính giá trị biểu thức: $a + 2b + x_1 + y_2 - z_1 + 3z_2 \approx {ans_val:.3f}$.
Làm tròn đến hàng phần mười, ta được kết quả là ${ans_str}$."""

    return stem, sol, ans_str

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
        # Use force_sample=True for the first question if no seed is provided to show the sample matches
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
    out_path = os.path.join(out_dir, "cau_1_questions.tex")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {out_path}")

if __name__ == "__main__":
    main()
