import os
import sys
import random
import math

def generate_params():
    while True:
        # Tọa độ B 
        triples = [
            (3, 4, 5),
            (5, 12, 13),
            (6, 8, 10),
            (8, 15, 17),
            (9, 12, 15),
            (12, 16, 20)
        ]
        x_B, y_B, d = random.choice(triples)
        
        if random.choice([True, False]): x_B, y_B = y_B, x_B
        if random.choice([True, False]): x_B = -x_B
        if random.choice([True, False]): y_B = -y_B
        
        z_B = random.randint(3, 12)
        
        # Bán kính R_M của điểm M trên (Oxy)
        # R_M cần khác d để tránh bị trùng tâm B' với M_min
        R_M = random.randint(2, d - 1) 
        
        # Điểm A(0, 0, z_A)
        z_A = random.randint(5, 20)
        
        # Diện tích tam giác OAM
        # S = 1/2 * OA * OM = 1/2 * z_A * R_M
        S_val = (z_A * R_M) / 2
        if S_val != int(S_val):
            continue # Chỉ lấy S là số nguyên cho đẹp
        
        return {
            "A": (0, 0, z_A),
            "B": (x_B, y_B, z_B),
            "R_M": R_M,
            "S": int(S_val),
            "d": d
        }

def generate_question(seed=None, force_sample=False):
    if seed is not None:
        random.seed(seed)
        
    if force_sample:
        p = {
            "A": (0, 0, 10),
            "B": (3, 4, 6),
            "R_M": 3,
            "S": 15,
            "d": 5
        }
    else:
        p = generate_params()
        
    xA, yA, zA = p["A"]
    xB, yB, zB = p["B"]
    R_M = p["R_M"]
    S = p["S"]
    d = p["d"]
    
    # Tính toán tọa độ min/max
    # M_min nằm giữa O và B'
    x1 = (R_M / d) * xB
    y1 = (R_M / d) * yB
    z1 = 0
    
    # M_max nằm về phía đối diện
    x2 = -(R_M / d) * xB
    y2 = -(R_M / d) * yB
    z2 = 0
    
    BM_min = math.sqrt((d - R_M)**2 + zB**2)
    BM_max = math.sqrt((d + R_M)**2 + zB**2)
    
    a = BM_min
    b = BM_max
    a_sq = (d - R_M)**2 + zB**2
    
    ans_val = x1 + 2*y1 + 3*y2 - 3*z2 + a_sq - 3*b
    ans_str = f"{ans_val:.1f}".replace('.', ',')
    
    stem = rf"Trong một studio, đội ngũ kỹ thuật đang setup mâm xoay chụp ảnh cho chiến dịch ra mắt bộ sản phẩm 'The King of TED'. Mặt bàn trưng bày được xem như mặt phẳng tọa độ $(Oxy)$ với tâm của mâm xoay là gốc tọa độ $O(0;0;0)$. Đơn vị đo đạc trong không gian này được tính bằng decimet (dm). Một đèn đánh sáng chính (Key Light) được treo thẳng đứng trực tiếp phía trên tâm mâm xoay tại vị trí $A(0;0;{zA})$. Cùng với đó, một chiếc máy quay cận cảnh (Macro Camera), được đặt tại điểm $M$, di chuyển liên tục trên mặt bàn. Để tối ưu hóa hiệu ứng đổ bóng cho sản phẩm, kỹ thuật viên lập trình cho máy quay cận cảnh này di chuyển sao cho tam giác $OAM$ (tạo bởi tâm mâm xoay, đèn và máy quay) không bao giờ có góc tù, và diện tích bề mặt tam giác ánh sáng này luôn duy trì ở mức cố định là ${S}\text{{dm}}^2$. Cùng lúc đó, một máy quay toàn cảnh (Main Camera) được cố định tại một góc của studio ở vị trí không gian $B({xB};{yB};{zB})$ để bắt trọn khung hình từ trên cao. Để chuẩn bị độ dài dây cáp kết nối tín hiệu giữa hai máy quay sao cho dây không bị căng đứt hay quá chùng gây vướng víu, ta cần xác định định các vị trí để căn chỉnh độ dài dây cáp kết nối cho phù hợp. Biết rằng khi $M$ ở vị trí $(x_1;y_1;z_1)$ thì dây $BM$ đạt giá trị nhỏ nhất là $a$ và khi $M$ ở vị trí $(x_2;y_2;z_2)$ thì dây $BM$ đạt giá trị lớn nhất là $b$. Giá trị của biểu thức $x_1 + 2y_1 + 3y_2 - 3z_2 + a^2 - 3b$ bằng bao nhiêu (làm tròn đến hàng phần mười)."
    
    sol = rf"""Máy quay di chuyển trên mặt bàn $(Oxy)$ nên $M(x; y; 0)$. Đèn tại $A(0; 0; {zA})$.
Ta xét các góc của tam giác $OAM$:
Ta có $\overrightarrow{{OA}} = (0; 0; {zA})$ và $\overrightarrow{{OM}} = (x; y; 0)$. Suy ra $\overrightarrow{{OA}} \cdot \overrightarrow{{OM}} = 0 \Rightarrow \widehat{{AOM}} = 90^\circ$.
Do đó tam giác $OAM$ luôn vuông tại $O$ (không bao giờ có góc tù).
Diện tích tam giác $OAM$ là: $S_{{OAM}} = \frac{{1}}{{2}} OA \cdot OM = \frac{{1}}{{2}} \cdot {zA} \cdot \sqrt{{x^2+y^2}} = {S}$.
$\Rightarrow OM = \sqrt{{x^2+y^2}} = \frac{{2 \cdot {S}}}{{{zA}}} = {R_M}$.
Vậy quỹ đạo di chuyển của máy quay $M$ là đường tròn $(C)$ tâm $O$, bán kính $R = {R_M}$ nằm trên mặt phẳng $(Oxy)$.

Gọi $H$ là hình chiếu vuông góc của $B({xB}; {yB}; {zB})$ lên mặt phẳng $(Oxy)$ $\Rightarrow H({xB}; {yB}; 0)$.
Khoảng cách $OH = \sqrt{{{xB}^2 + {yB}^2}} = {d}$.
Sợi dây kết nối là đoạn thẳng $BM$. Ta có $BM = \sqrt{{HM^2 + BH^2}} = \sqrt{{HM^2 + {zB}^2}}$.
Do $BH = {zB}$ không đổi nên $BM$ đạt min/max khi và chỉ khi đoạn $HM$ đạt min/max.
Vì $M$ thuộc đường tròn $(C)$ tâm $O$ bán kính $R = {R_M}$ trên $(Oxy)$ và điểm $H$ nằm ngoài đường tròn (do $OH = {d} > R = {R_M}$), ta có:
$HM_{{min}} = |OH - R| = |{d} - {R_M}| = {abs(d - R_M)}$.
$HM_{{max}} = OH + R = {d} + {R_M} = {d + R_M}$.
Khi đó, khoảng cách nhỏ nhất $a = \sqrt{{HM_{{min}}^2 + BH^2}} = \sqrt{{{abs(d - R_M)}^2 + {zB}^2}} \approx {a:.3f}$. Ta có $a^2 = {a_sq}$.
Khoảng cách lớn nhất $b = \sqrt{{HM_{{max}}^2 + BH^2}} = \sqrt{{{d + R_M}^2 + {zB}^2}} \approx {b:.3f}$.

Vị trí của $M$ đạt các cực trị nằm trên đoạn thẳng $OH$. 
Vectơ $\overrightarrow{{OH}} = ({xB}; {yB}; 0)$.
Điểm $M_1$ ứng với $BM_{{min}}$ là giao điểm của đoạn $OH$ với đường tròn $(C)$, có $\overrightarrow{{OM_1}} = \frac{{R}}{{OH}} \overrightarrow{{OH}} = \frac{{{R_M}}}{{{d}}}({xB}; {yB}; 0) = ({x1:g}; {y1:g}; 0) \Rightarrow x_1={x1:g}, y_1={y1:g}, z_1=0$.
Điểm $M_2$ ứng với $BM_{{max}}$ nằm trên tia đối của $\overrightarrow{{OH}}$, có $\overrightarrow{{OM_2}} = -\frac{{R}}{{OH}} \overrightarrow{{OH}} = -\frac{{{R_M}}}{{{d}}}({xB}; {yB}; 0) = ({x2:g}; {y2:g}; 0) \Rightarrow x_2={x2:g}, y_2={y2:g}, z_2=0$.

Giá trị biểu thức: $P = x_1 + 2y_1 + 3y_2 - 3z_2 + a^2 - 3b \approx {ans_val:.3f}$. 
Làm tròn đến hàng phần mười, kết quả là ${ans_str}$."""

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
        force = (i == 0 and seed_val is None)
        q, s, k = generate_question(seed, force_sample=force)
        
        content += rf"""Câu {i+1}: {q}

Lời giải:

{s}

Đáp án: {k}

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
    out_path = os.path.join(out_dir, "cau_3_questions.tex")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {out_path}")

if __name__ == "__main__":
    main()
