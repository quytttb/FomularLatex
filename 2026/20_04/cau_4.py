import os
import sys
import math
import random
from typing import Tuple
from fractions import Fraction

PARAM_SETS = [
    (141, 153, 20, 30, 211),
    (91, 103, 24, 30, 131),
    (146, 198, 48, 25, 69),
    (135, 167, 21, 5, 140),
    (87, 99, 36, 25, 97),
    (131, 148, 42, 30, 177),
    (113, 132, 34, 25, 137),
    (60, 70, 42, 20, 90),
    (95, 109, 26, 15, 125),
    (71, 88, 23, 15, 190),
    (104, 125, 45, 5, 137),
    (128, 140, 49, 20, 112),
    (130, 153, 46, 30, 171),
    (68, 74, 41, 10, 105),
    (70, 82, 47, 5, 93),
    (95, 129, 40, 15, 83),
    (107, 134, 26, 30, 158),
    (149, 197, 40, 5, 108),
    (128, 179, 27, 10, 150),
    (108, 130, 49, 30, 148),
    (88, 114, 30, 5, 95),
    (64, 79, 32, 15, 76),
    (100, 118, 40, 20, 137),
    (142, 176, 24, 15, 146),
    (91, 119, 37, 25, 90),
    (134, 166, 48, 25, 129),
    (106, 125, 24, 25, 177),
    (71, 77, 47, 5, 93),
    (140, 155, 45, 30, 167),
    (136, 145, 32, 20, 181),
    (119, 157, 28, 25, 72),
    (147, 198, 23, 30, 209),
    (94, 120, 23, 15, 193),
    (80, 99, 20, 30, 205),
    (93, 109, 36, 5, 128),
    (141, 178, 39, 10, 121),
    (107, 122, 37, 25, 102),
    (136, 161, 35, 5, 120),
    (106, 130, 27, 5, 125),
    (132, 142, 22, 30, 228),
    (68, 90, 44, 10, 59),
    (144, 179, 50, 25, 99),
    (93, 125, 50, 10, 110),
    (148, 165, 42, 15, 169),
    (145, 191, 31, 20, 206),
    (117, 129, 27, 10, 142),
    (103, 109, 38, 25, 131),
    (135, 154, 20, 5, 243),
    (140, 148, 27, 5, 218),
    (64, 79, 22, 25, 111),
]

CONTEXTS = [
    {
        "object": "thiết bị bay không người lái (UAV)",
        "station": "trạm radar kiểm soát không lưu",
        "radius_desc": "khả năng quét và kiểm soát các vật thể bay trong bán kính tối đa bằng",
        "movement": "bay thẳng nhanh dần đều"
    }
]

def format_frac(num, den):
    f = Fraction(num, den)
    if f.denominator == 1:
        return str(f.numerator)
    return rf"\frac{{{f.numerator}}}{{{f.denominator}}}"

def format_sqrt2_frac(num, den):
    f = Fraction(num, den)
    if f.denominator == 1:
        if f.numerator == 1:
            return r"\sqrt{2}"
        return rf"{f.numerator}\sqrt{{2}}"
    if f.numerator == 1:
        return rf"\frac{{\sqrt{{2}}}}{{{f.denominator}}}"
    return rf"\frac{{{f.numerator}\sqrt{{2}}}}{{{f.denominator}}}"

def generate_question(context_idx=None) -> Tuple[str, str, str]:
    if context_idx is None:
        context = random.choice(CONTEXTS)
    else:
        context = CONTEXTS[context_idx % len(CONTEXTS)]
        
    preset = random.choice(PARAM_SETS)
    a, R, c, t_before, t_explode = preset
    k = random.randint(3, 7)
    a_dec = random.randint(3, 8)
    
    # 1. Base equations: IM^2(s) = s^2 - 2as + 2a^2
    # Roots when entering/exiting R: s^2 - 2as + 2a^2 - R^2 = 0 -> s = a ± sqrt(R^2 - a^2)
    delta_s = math.sqrt(R**2 - a**2)
    s_in = a - delta_s
    s_out = a + delta_s
    
    # Original theoretical entering time
    t_in_orig = math.sqrt(2 * s_in / c)
    
    # Phase 1: Normal acceleration
    t_A = t_in_orig - t_before / 60
    s_A = (c / 2) * (t_A**2)
    v_A = c * t_A
    dA = math.sqrt(s_A**2 - 2*a*s_A + 2*a**2)
    
    # Phase 2: Boosted acceleration
    a2 = c + k * 10
    def solve_tau(target_s):
        A_coef = 0.5 * a2
        B_coef = v_A
        C_coef = s_A - target_s
        return (-B_coef + math.sqrt(B_coef**2 - 4*A_coef*C_coef)) / (2*A_coef)
        
    tau_in = solve_tau(s_in)
    tau_out = solve_tau(s_out)
    
    t_in_new = t_A + tau_in
    t_out_new = t_A + tau_out
    
    t_in_mins = t_in_new * 60
    t_out_mins = t_out_new * 60
    T_mins = t_out_mins - t_in_mins
    
    # Answer B
    ans_b = a + 2 * T_mins
    
    # Answer C
    xM = s_out / 2
    zM = s_out * math.sqrt(2) / 2
    part_C = xM + 3 * math.sqrt(2) * xM
    ans_c = t_in_mins + part_C + t_out_mins
    
    # Phase 3: Explosion
    v_out = v_A + a2 * tau_out
    a3 = -a_dec * 12960
    te = t_explode / 3600
    s_explos = v_out * te + 0.5 * a3 * (te**2)
    s_E = s_out + s_explos
    dE = math.sqrt(s_E**2 - 2*a*s_E + 2*a**2)
    
    # Generate Statements
    a_correct = random.choice([True, False])
    dA_text = round(dA, 1) if a_correct else round(dA + random.choice([-2.5, -1.8, 1.8, 2.5]), 1)
        
    b_correct = random.choice([True, False])
    ans_b_text = round(ans_b, 1) if b_correct else round(ans_b + random.choice([-5.5, -3.2, 3.2, 5.5]), 1)
        
    c_correct = random.choice([True, False])
    ans_c_text = round(ans_c, 1) if c_correct else round(ans_c + random.choice([-15.5, -10.2, 10.2, 15.5]), 1)
        
    d_correct = random.choice([True, False])
    dE_text = round(dE, 1) if d_correct else round(dE + random.choice([-2.2, -1.5, 1.5, 2.2]), 1)
    
    obj_name = "UAV"
    
    stem = rf"Trong không gian với hệ trục tọa độ $Oxyz$ (đơn vị đo trên các trục là km), một trạm radar kiểm soát không lưu được đặt tại vị trí $I({a} ; {a} ; 0)$ có khả năng quét và kiểm soát các vật thể bay trong bán kính tối đa bằng {R} km."
    stem += "\n\n"
    stem += rf"Một thiết bị bay không người lái (UAV) xuất phát từ điểm gốc tọa độ $O(0 ; 0 ; 0)$ và bắt đầu bay thẳng nhanh dần đều với vận tốc $v_1(t)={c}t(\mathrm{{\sim km}} / \mathrm{{h}})$, với $t$ tính bằng giờ kể từ thời điểm xuất phát. Hướng bay của thiết bị cùng hướng với véc-tơ đơn vị $\vec{{u}}$, biết góc giữa véc-tơ $\vec{{u}}$ lần lượt với các hướng $\vec{{i}}, \vec{{j}}, \vec{{k}}$ trên các trục $O x, O y, O z$ có số đo tương ứng bằng $60^\circ, 60^\circ, 45^\circ$."
    stem += "\n"
    stem += rf"Trong dự định, UAV sẽ luôn bay với $v_1$ trong suốt hành trình nhưng tin tình báo cho biết phía trước có một vùng kiểm soát nên trước khi tiếp cận vùng kiểm soát {t_before} phút, UAV bắt đầu chuyển động với gia tốc tăng thêm $\dfrac{{{k}}}{{1296}}m/s^2$ và duy trì việc tăng tốc cho đến khi thoát khỏi vùng kiểm soát của rada sau đó chuyển động chậm dần đều với gia tốc $-{a_dec}m/s^2$ được {t_explode} giây thì phát nổ."
    
    stmt_a = rf"{'*' if a_correct else ''}a) Khoảng cách từ rada đến vị trí lúc UAV bắt đầu tăng tốc khoảng ${dA_text}km$"
    stmt_b = rf"{'*' if b_correct else ''}b) Trong suốt quá trình bay, khoảng cách ngắn nhất từ UAV đến trạm kiểm soát $I$ là $d$ km và thời gian kể từ khi trạm kiểm soát phát hiện ra UAV đến khi UAV ra khỏi vùng kiểm soát là $T$ phút. Khi đó: $d+2T\approx{ans_b_text}$"
    stmt_c = rf"{'*' if c_correct else ''}c) Khoảng thời gian từ lúc UAV bắt đầu chuyển động cho đến khi vào vùng kiểm soát là $t_1$ phút và vị trí khi ra khỏi vùng kiểm soát là $M(x_M,y_M,z_M)$ tại thời điểm $t_2$. Khi đó: $t_1+2x_M-y_M+3z_M+t_2\approx{ans_c_text}$"
    stmt_d = rf"{'*' if d_correct else ''}d) UAV phát nổ tại vị trí cách rada khoảng ${dE_text}km$"
    
    question = f"{stem}\n\n{stmt_a}\n\n{stmt_b}\n\n{stmt_c}\n\n{stmt_d}"

    sol_a = rf"""a) {'Đúng' if a_correct else 'Sai'}.

Gọi $F$ là hình chiếu vuông góc của $I({a}; {a}; 0)$ lên đường bay của UAV. 
Vec-tơ chỉ phương của đường bay: $\vec{{u}} = (\cos 60^\circ; \cos 60^\circ; \cos 45^\circ) = \left(\frac{{1}}{{2}}; \frac{{1}}{{2}}; \frac{{\sqrt{{2}}}}{{2}}\right)$.
Ta có đoạn $OF = \vec{{OI}} \cdot \vec{{u}} = {a} \times \frac{{1}}{{2}} + {a} \times \frac{{1}}{{2}} + 0 = {a}$ (km).
Khoảng cách từ $I$ đến đường bay: $IF = \sqrt{{OI^2 - OF^2}} = \sqrt{{2 \times {a}^2 - {a}^2}} = {a}$ (km).
Gọi $E$ là vị trí UAV bắt đầu vào vùng kiểm soát (bán kính $R = {R}$), suy ra $IE = {R}$ (km).
Xét tam giác vuông $IFE$, $EF = \sqrt{{IE^2 - IF^2}} = \sqrt{{{R}^2 - {a}^2}} \approx {delta_s:.3f}$ (km).
Quãng đường từ $O$ đến điểm $E$ (bắt đầu vào vùng kiểm soát) là $s_{{vào}} = OF - EF = {a} - \sqrt{{{R}^2 - {a}^2}} \approx {s_in:.3f}$ (km).
Hàm quãng đường ban đầu: $s_1(t) = \int_0^t v_1(x) dx = \int_0^t {c}x dx = \frac{{{c}}}{{2}}t^2$.
Thời gian dự kiến bay đến $E$: $t_E = \sqrt{{\frac{{2 \times OE}}{{{c}}}}} \approx {t_in_orig:.4f}$ (giờ).
Gọi $T$ là vị trí UAV bắt đầu tăng tốc. Thời gian bay đến $T$: $t_T = t_E - \frac{{{t_before}}}{{60}} \approx {t_A:.4f}$ (giờ).
Quãng đường tương ứng $OT = \frac{{{c}}}{{2}}t_T^2 \approx {s_A:.3f}$ (km).
Khoảng cách từ radar đến UAV lúc này là $IT = \sqrt{{IF^2 + TF^2}} = \sqrt{{IF^2 + (OF - OT)^2}} \approx {dA:.1f}$ (km)."""
    
    sol_b = rf"""b) {'Đúng' if b_correct else 'Sai'}.

Tại mốc $t_A$, UAV có vận tốc $v_A = {c} \times t_A \approx {v_A:.3f}$ (km/h).
Gia tốc tăng thêm $\frac{{{k}}}{{1296}}$ m/s$^2 = {k*10}$ km/h$^2$. Gia tốc mới $a_2 = {c} + {k*10} = {a2}$ (km/h$^2$).
Hàm quãng đường đi được tính từ lúc bắt đầu tăng tốc (gọi $t$ là thời gian chuyển động trong giai đoạn này):
$s_2(t) = s_A + v_A t + \frac{{1}}{{2}}a_2 t^2 = {s_A:.3f} + {v_A:.3f} t + {(a2/2):.1f} t^2$.
Thiết bị bắt đầu vào vùng radar tại quãng đường $s_{{vào}} \approx {s_in:.3f}$ (km).
Ta có PT: ${(a2/2):.1f} t_{{vào}}^2 + {v_A:.3f} t_{{vào}} + ({s_A - s_in:.4f}) = 0 \Rightarrow t_{{vào}} \approx {tau_in:.4f}$ (giờ).
Thời gian chính thức vào vùng đo tính từ lúc cất cánh: $t_1 = t_A + t_{{vào}} \approx {t_in_new:.4f}$ (giờ) = ${t_in_mins:.2f}$ (phút).
Tương tự, thiết bị bay ra khỏi vùng radar khi quãng đường đạt $s_{{ra}} = {a} + \sqrt{{{delta_s**2}}} \approx {s_out:.3f}$ (km). 
Cần giải PT: ${(a2/2):.1f} t_{{ra}}^2 + {v_A:.3f} t_{{ra}} + ({s_A - s_out:.4f}) = 0 \Rightarrow t_{{ra}} \approx {tau_out:.4f}$ (giờ).
Thời gian bay ra khỏi vùng tính từ lúc cất cánh: $t_2 = t_A + t_{{ra}} \approx {t_out_new:.4f}$ (giờ) = ${t_out_mins:.2f}$ (phút).
Khoảng cách ngắn nhất xảy ra khi $s = {a} \Rightarrow d_{{min}} = \sqrt{{{a}^2 - 2{a}({a}) + 2{a}^2}} = {a}$ km.
Thời gian tiếp cận vùng: $T = t_2 - t_1 \approx {T_mins:.2f}$ phút. Khi đó: $d + 2T \approx {ans_b:.1f}$."""
    
    sol_c = rf"""c) {'Đúng' if c_correct else 'Sai'}.

Thời điểm vào vùng: $t_1 = {t_in_mins:.2f}$ phút; Thời điểm ra vùng: $t_2 = {t_out_mins:.2f}$ phút.
Tọa độ khi ra khỏi vùng (ứng với quãng đường di chuyển bằng $s_{{ra}} \approx {s_out:.3f}$ km):
$x_M = y_M = \frac{{s_{{ra}}}}{{2}} \approx {xM:.2f}$ và $z_M = \frac{{s_{{ra}}\sqrt{{2}}}}{{2}} \approx {xM * math.sqrt(2):.2f}$.
Có $2x_M - y_M + 3z_M = x_M + 3\sqrt{{2}}x_M \approx {part_C:.2f}$.
Lắp ráp lại ta được tổng $t_1 + 2x_M - y_M + 3z_M + t_2 \approx {t_in_mins:.2f} + {part_C:.2f} + {t_out_mins:.2f} \approx {ans_c:.1f}$."""
    
    sol_d = rf"""d) {'Đúng' if d_correct else 'Sai'}.

Qua điểm thoát vùng theo phương trình của mốc 2, UAV có vận tốc $v_{{ra}} = v_A + a_2 t_{{ra}} \approx {v_out:.3f}$ (km/h).
Giai đoạn chậm dần đều bắt đầu với gia tốc $a_3 = -{a_dec}$ m/s$^2 = {-a_dec*12960}$ (km/h$^2$), duy trì được $t_e = {t_explode}$ (giây) = ${te:.5f}$ (giờ).
Tổng chiều dài quãng đường tại thời điểm điểm bay bị nổ:
$s_E = s_{{ra}} + (v_{{ra}} t_e + \frac{{1}}{{2}}a_3 t_e^2) \approx {s_out:.3f} + ({s_explos:.3f}) = {s_E:.3f}$ (km).
Thế lại vào hàm hình học vị trí:
$d_E = \sqrt{{s_E^2 - 2 \times {a} \times s_E + 2 \times {a**2}}} \approx {dE:.1f}$ km."""
    
    solution = "\n\n".join([sol_a, sol_b, sol_c, sol_d])
    key = ", ".join(["Đ" if x else "S" for x in (a_correct, b_correct, c_correct, d_correct)])
    
    return question, solution, key

def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])

    context_idx = None
    if len(sys.argv) > 2:
        context_idx = int(sys.argv[2])

    content = ""
    keys = []
    
    # Generate questions
    for i in range(num_questions):
        q, s, k = generate_question(context_idx)
        keys.append(k)
        content += f"Câu {i+1}: {q}\n\nLời giải:\n\n{s}\n\n"

    # LaTeX template
    template = r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath, amsfonts, amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
% \setmainfont{Times New Roman}
\usepackage{tikz}
\usetikzlibrary{calc,angles,quotes}

\newcommand{\heva}[1]{\left\{\begin{aligned}#1\end{aligned}\right.}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "cau_4_questions.tex")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")

if __name__ == "__main__":
    main()
