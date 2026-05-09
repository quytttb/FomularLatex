import math
import os
import sys
import random
from fractions import Fraction
from typing import Tuple

# Each preset: (A, B, t_total, R)
# All presets verified: integer v, t_H, t_delta, t1, t2, d_sq, P_in, P_out, T_mins
PARAM_SETS = [
    # v=(2,1,0), v_sq=5, d_sq=20, R=5, angle≈53°
    ((-2, -6, 0), (4, -3, 0), 3, 5),
    # v=(2,1,0), v_sq=5, d_sq=5, R=5, angle≈127°
    ((-5, -5, 0), (5, 0, 0), 5, 5),
    # v=(2,2,0), v_sq=8, d_sq=8, R=4, angle=90°
    ((-2, -6, 0), (4, 0, 0), 3, 4),
    # v=(2,2,0), v_sq=8, d_sq=4, R=6, angle≈141°
    ((-6, -6, 2), (4, 4, 2), 5, 6),
    # v=(3,0,0), v_sq=9, d_sq=16, R=5, angle≈74°
    ((-6, -4, 0), (3, -4, 0), 3, 5),
    # v=(4,3,-1), v_sq=26, d_sq=10, R=6, angle≈116°
    ((-8, -5, 5), (4, 4, 2), 3, 6),
    # v=(4,3,-1), v_sq=26, d_sq=40, R=12, angle≈116°
    ((-16, -10, 10), (24, 20, 0), 10, 12),
    # v=(2,1,1), v_sq=6, d_sq=12, R=6, angle≈109°
    ((-8, -1, -1), (2, 4, 4), 5, 6),
    # v=(2,2,0), v_sq=8, d_sq=49, R=9, angle≈78°
    ((-6, -6, 7), (4, 4, 7), 5, 9),
    # v=(-2,-1,0), v_sq=5, d_sq=61, R=9, angle≈60°
    ((2, 6, 0), (-4, 0, 0), 3, 4),
    ((2, 6, 0), (-4, 3, 0), 3, 5),
    ((2, 6, -3), (-4, 0, -3), 3, 5),
    ((6, -4, 0), (-3, -4, 0), 3, 5),
    ((7, 6, 0), (-5, 0, 0), 3, 5),
    ((2, 1, 7), (-4, -2, 4), 3, 6),
    ((5, 5, -4), (-4, 2, -4), 3, 6),
    ((0, 6, 6), (-6, 0, 0), 3, 6),
    ((8, -4, -2), (-4, -4, -2), 3, 6),
    ((8, -1, 5), (-4, -4, 2), 3, 6),
    ((6, 3, -4), (-4, -2, -4), 5, 6),
    ((6, 6, 6), (-6, 0, 0), 3, 6),
    ((8, 8, -2), (-4, -4, -2), 3, 6),
    ((6, 0, 8), (-3, -6, 2), 3, 7),
    ((4, 8, -3), (-6, -2, -3), 5, 7),
    ((2, 10, 0), (-8, 0, 0), 5, 8),
    ((-2, 10, -1), (-8, 4, -1), 3, 9),
    ((3, 9, -4), (-7, 4, -4), 5, 9),
    ((5, 10, -4), (-7, 4, -4), 3, 9),
    ((9, 3, 9), (-6, -3, 6), 3, 9),
    ((5, 7, 7), (-9, 0, 0), 7, 9),
    ((11, 5, 5), (-9, 0, 0), 5, 9),
    ((6, 10, -1), (-8, -4, -1), 7, 9),
    ((2, 11, 0), (-8, 6, 0), 5, 10),
    ((2, 10, -6), (-8, 0, -6), 5, 10),
    ((12, -6, 0), (-8, -6, 0), 5, 10),
    ((11, 7, 0), (-10, 0, 0), 7, 10),
    ((9, -7, -6), (-6, -7, -6), 5, 11),
    ((8, 8, -7), (-6, -6, -7), 7, 11),
    ((11, 8, -6), (-9, -2, -6), 5, 11),
    ((12, 8, -2), (-9, -6, -2), 7, 11),
    ((0, 12, 12), (-12, 0, 0), 3, 12),
    ((2, 14, 0), (-12, 0, 0), 7, 12),
    ((12, 6, -8), (-8, -4, -8), 5, 12),
    ((8, 10, 10), (-12, 0, 0), 5, 12),
    ((2, 14, -5), (-12, 0, -5), 7, 13),
    ((8, 14, -3), (-12, 4, -3), 5, 13),
    ((8, 14, -6), (-12, 4, -6), 5, 14),
    ((7, 14, 7), (-14, 0, 0), 7, 14),
    ((8, 16, 9), (-12, -4, -6), 5, 14),
    ((16, 8, -4), (-12, -6, -4), 7, 14),
    ((9, 17, 0), (-11, 2, -10), 5, 15),
    ((9, 5, 17), (-11, -10, 2), 5, 15),
    ((6, 15, 12), (-14, -5, 2), 5, 15),
    ((13, 14, 0), (-15, 0, 0), 7, 15),
    ((15, 15, -5), (-10, -10, -5), 5, 15),
    ((13, 19, 3), (-12, -1, -12), 5, 17),
    ((16, 16, -1), (-12, -12, -1), 7, 17),
    ((10, 20, 8), (-18, -1, -6), 7, 19),
    ((10, 22, -1), (-18, -6, -1), 7, 19),
]

CONTEXTS = [
    {
        "object": "khinh khí cầu",
        "station": "trạm kiểm soát không lưu",
        "sensor": "anten",
        "movement": "bay thẳng",
        "radius_desc": "kiểm soát được các vật thể cách trạm một khoảng tối đa bằng",
    },
    {
        "object": "thiết bị lặn tự hành (ROV)",
        "station": "trạm định vị thủy âm (Sonar)",
        "sensor": "đầu dò định hướng",
        "movement": "di chuyển thẳng đều",
        "radius_desc": "có khả năng phát hiện và duy trì tín hiệu với các vật thể dưới nước ở khoảng cách tối đa bằng",
    },
    {
        "object": "vệ tinh siêu nhỏ (CubeSat)",
        "station": "Trạm Vũ trụ",
        "sensor": "radar mảng pha điện tử",
        "movement": "trôi dạt theo đường thẳng",
        "radius_desc": "có khả năng quét và theo dõi các vật thể trong bán kính tối đa",
    },
    {
        "object": "robot thám hiểm tự hành",
        "station": "trạm định vị sóng vô tuyến xuyên đá",
        "sensor": "tia định vị",
        "movement": "di chuyển theo một đường thẳng",
        "radius_desc": "có khả năng phát hiện các vật thể di chuyển trong bán kính tối đa là",
    },
    {
        "object": "cabin của hệ thống cáp treo công nghiệp",
        "station": "trạm radar an toàn",
        "sensor": "radar",
        "movement": "trượt trên cáp",
        "radius_desc": "có khả năng quét và cảnh báo va chạm cho các vật thể trong bán kính tối đa là",
    }
]

def fmt_point(p):
    return f"({p[0]}; {p[1]}; {p[2]})"

def sqrt_tex(n):
    """Return LaTeX for √n, simplifying perfect squares."""
    if n < 0: return ""
    root = int(math.sqrt(n))
    if root * root == n:
        return str(root)
    return rf"\sqrt{{{n}}}"

def _fmt_param_line(var, a0, v0):
    """Format one line of parametric equation: var &= a0 + v0*t"""
    if v0 == 0:
        return f"{var} &= {a0}"
    sign = '+' if v0 >= 0 else ''
    return f"{var} &= {a0} {sign}{v0}t"

def _fmt_op_term(a0, v0):
    """Format one term of OP² expansion: (a0 + v0*t)^2 or a0^2"""
    if v0 == 0:
        if a0 < 0:
            return f"({a0})^2"
        return f"{a0}^2"
    sign = '+' if v0 >= 0 else ''
    return f"({a0} {sign}{v0}t)^2"

def generate_question(context_idx=None) -> Tuple[str, str, str]:
    if context_idx is None:
        context = random.choice(CONTEXTS)
    else:
        context = CONTEXTS[context_idx % len(CONTEXTS)]
        
    obj = context["object"]
    sta = context["station"]
    sensor = context["sensor"]
    mov = context["movement"]
    rad_desc = context["radius_desc"]
    
    # Random chọn bộ tham số
    A, B, t_total, R = random.choice(PARAM_SETS)
    
    # Tính toán vector vận tốc
    AB = (B[0]-A[0], B[1]-A[1], B[2]-A[2])
    v_vec = (AB[0]//t_total, AB[1]//t_total, AB[2]//t_total)
    v_sq = v_vec[0]**2 + v_vec[1]**2 + v_vec[2]**2
    v_val = math.sqrt(v_sq)

    # Điểm vuông góc H từ O đến chuyển động
    t_H = - (A[0]*v_vec[0] + A[1]*v_vec[1] + A[2]*v_vec[2]) // v_sq
    H = (A[0] + v_vec[0]*t_H, A[1] + v_vec[1]*t_H, A[2] + v_vec[2]*t_H)
    d_sq = H[0]**2 + H[1]**2 + H[2]**2
    d_val = math.sqrt(d_sq)
    
    # Thời gian trong vùng kiểm soát
    t_delta_sq = (R**2 - d_sq) // v_sq
    t_delta = int(math.isqrt(t_delta_sq))
    t1 = t_H - t_delta
    t2 = t_H + t_delta
    
    T_hours = t2 - t1
    T_mins = T_hours * 60
    
    # Vị trí đi vào và ra
    P_in = (A[0] + v_vec[0]*t1, A[1] + v_vec[1]*t1, A[2] + v_vec[2]*t1)
    P_out = (A[0] + v_vec[0]*t2, A[1] + v_vec[1]*t2, A[2] + v_vec[2]*t2)
    
    # Mệnh đề A
    a_correct = random.choice([True, False])
    v_display = v_sq if a_correct else v_sq + random.choice([-2, 2, 4, -1])
    if v_display <= 0:
        v_display = v_sq + 4
    val_a = sqrt_tex(v_display)
    
    # Mệnh đề B
    b_correct = random.choice([True, False])
    if b_correct:
        stmt_b_eq = f"d^2 + T = {d_sq + T_mins}"
    else:
        d_fake = int(d_val) if d_val == int(d_val) else int(d_val) + 1
        stmt_b_eq = f"d + 2T = {d_fake + 2*T_mins}"
    
    # Mệnh đề C
    c_correct = random.choice([True, False])
    correct_val_c = t1 + 2*P_out[0] - P_out[1] + 3*P_out[2]
    val_c = int(correct_val_c) if c_correct else int(correct_val_c) + random.choice([-10, -18, 10, 18, 5])
    
    # Mệnh đề D
    d_correct = random.choice([True, False])
    cos_theta = (P_in[0]*P_out[0] + P_in[1]*P_out[1] + P_in[2]*P_out[2]) / (R**2)
    angle_rad = math.acos(max(-1, min(1, cos_theta)))
    angle_deg = round(math.degrees(angle_rad))
    # Bẫy góc (góc kề bù)
    wrong_angle = 180 - angle_deg
    val_d = angle_deg if d_correct else wrong_angle
    if val_d == angle_deg and not d_correct:
        val_d = angle_deg + random.choice([10, -10, 15])
        
    stem = rf"""Trong không gian với hệ trục tọa độ $Oxyz$ (với đơn vị đo trên các trục tọa độ là ki-lômét). Một {obj} từ vị trí điểm $A{fmt_point(A)}$ {mov} đến vị trí điểm $B{fmt_point(B)}$ hết {t_total} giờ. Biết {sta} đặt ở vị trí gốc tọa độ $O$ {rad_desc} {R} km.

Xét tính đúng, sai của các phát biểu sau:"""
    
    # Format velocity components for display
    def fmt_v(val):
        """Wrap negative values in parens for squared display."""
        if val >= 0:
            return str(val)
        return f"({val})"
    
    stmt_a = rf"{'*' if a_correct else ''}a) Vận tốc di chuyển của {obj} trên quỹ đạo $AB$ là ${val_a} \mathrm{{~km/h}}$."
    stmt_b = rf"{'*' if b_correct else ''}b) Trong suốt quá trình di chuyển từ $A$ đến $B$, khoảng cách ngắn nhất từ {obj} đến {sta} $O$ là $d$ (km) và thời gian kể từ khi {sta} bắt đầu phát hiện được đến khi {obj} ra khỏi vùng kiểm soát là $T$ (phút). Khi đó ta có hệ thức: ${stmt_b_eq}$."
    stmt_c = rf"{'*' if c_correct else ''}c) Khoảng thời gian từ lúc {obj} xuất phát ở $A$ cho đến khi lọt vào vùng kiểm soát là $t_1$ (giờ) và vị trí ngay khi ra khỏi vùng kiểm soát là điểm $M(x_M; y_M; z_M)$. Khi đó: $t_1 + 2x_M - y_M + 3z_M = {val_c}$."
    stmt_d = rf"{'*' if d_correct else ''}d) {sta.capitalize()} tại $O$ sử dụng một hệ thống {sensor} để bám sát mục tiêu. Góc quét không gian của {sensor} (góc tạo bởi hướng tia của {sensor} lúc bắt đầu phát hiện và lúc {obj} vượt ra ngoài tầm kiểm soát) xấp xỉ ${val_d}^{{\circ}}$ (làm tròn đến số nguyên gần nhất)."

    # Hệ số khai triển OP²
    # OP² = (Ax+vx*t)² + (Ay+vy*t)² + (Az+vz*t)²
    # = v_sq*t² + 2*(Ax*vx+Ay*vy+Az*vz)*t + (Ax²+Ay²+Az²)
    # = v_sq*t² - 2*v_sq*t_H*t + |A|²
    # = v_sq*(t - t_H)² + d_sq
    A_sq = A[0]**2 + A[1]**2 + A[2]**2
    coef_linear = 2 * (A[0]*v_vec[0] + A[1]*v_vec[1] + A[2]*v_vec[2])

    # Lời giải chi tiết
    sol_a = rf"""a) {'Đúng' if a_correct else 'Sai'}.

Ta có $\overrightarrow{{AB}} = {fmt_point((AB[0], AB[1], AB[2]))} $. Thời gian di chuyển là $t = {t_total}$ giờ.
Vận tốc di chuyển là vector $\vec{{v}} = \frac{{1}}{{{t_total}}} \overrightarrow{{AB}} = {fmt_point(v_vec)} \text{{ (km/h)}}$.
Độ lớn vận tốc: $v = |\vec{{v}}| = \sqrt{{{v_vec[0]}^2 + {fmt_v(v_vec[1])}^2 + {fmt_v(v_vec[2])}^2}} = \sqrt{{{v_sq}}} \text{{ (km/h)}}$."""

    sol_b = rf"""b) {'Đúng' if b_correct else 'Sai'}.

Phương trình quỹ đạo chuyển động của {obj}: $\heva{{{_fmt_param_line('x', A[0], v_vec[0])} \\ {_fmt_param_line('y', A[1], v_vec[1])} \\ {_fmt_param_line('z', A[2], v_vec[2])}}} \quad (t \ge 0)$ (với $t$ là số giờ).
Bình phương khoảng cách từ $O$ đến {obj} tại thời điểm $t$ là $OP^2$:
$$OP^2 = {_fmt_op_term(A[0], v_vec[0])} + {_fmt_op_term(A[1], v_vec[1])} + {_fmt_op_term(A[2], v_vec[2])}$$
$$= {v_sq}t^2 {'+' if coef_linear >= 0 else ''}{coef_linear}t + {A_sq} = {v_sq}(t - {t_H})^2 + {d_sq}$$
Khoảng cách ngắn nhất là $d(O, AB) = \sqrt{{{d_sq}}}$ km (khi $t = {t_H}$ giờ).
{obj} nằm trong vùng kiểm soát khi $OP^2 \le {R}^2 \iff {v_sq}(t - {t_H})^2 + {d_sq} \le {R**2}$
$\iff {v_sq}(t - {t_H})^2 \le {R**2 - d_sq} \iff (t - {t_H})^2 \le {t_delta_sq} \iff {t1} \le t \le {t2}$.
Suy ra thời gian nằm trong vùng kiểm soát bằng ${t2} - {t1} = {T_hours}$ (giờ), đổi ra $T = {T_hours} \times 60 = {T_mins}$ (phút).
Và khoảng cách cực tiểu $d = \sqrt{{{d_sq}}}$.
Ta có  $d^2 + T = {d_sq} + {T_mins} = {d_sq + T_mins}$."""

    sol_c = rf"""c) {'Đúng' if c_correct else 'Sai'}.

Theo phân tích trên, thời điểm bắt đầu vào vùng kiểm soát là $t_1 = {t1}$ (giờ).
Thời điểm ra khỏi vùng kiểm soát là $t_2 = {t2}$ (giờ).
Vị trí ngay khi ra khỏi vùng kiểm soát là điểm $M$: thay $t_2 = {t2}$ vào phương trình quỹ đạo ta được $M({P_out[0]}; {P_out[1]}; {P_out[2]})$.
Thay số vào biểu thức: $t_1 + 2x_M - y_M + 3z_M = {t1} + 2({P_out[0]}) - {P_out[1]} + 3({P_out[2]}) = {t1} + {2*P_out[0]} - {P_out[1]} + {3*P_out[2]} = {int(correct_val_c)}$."""

    dot_pp = P_in[0]*P_out[0] + P_in[1]*P_out[1] + P_in[2]*P_out[2]
    cos_val_frac = Fraction(dot_pp, R**2)

    sol_d = rf"""d) {'Đúng' if d_correct else 'Sai'}.

Vị trí bắt đầu phát hiện là $P({P_in[0]}; {P_in[1]}; {P_in[2]})$, tọa độ vector $\overrightarrow{{OP}} = {fmt_point(P_in)}$.
Vị trí lúc mất tín hiệu là $M({P_out[0]}; {P_out[1]}; {P_out[2]})$, tọa độ vector $\overrightarrow{{OM}} = {fmt_point(P_out)}$.
Góc quét không gian $\alpha = (\overrightarrow{{OP}}, \overrightarrow{{OM}})$. Ta có $\cos \alpha = \frac{{\overrightarrow{{OP}} \cdot \overrightarrow{{OM}}}}{{|\overrightarrow{{OP}}| \cdot |\overrightarrow{{OM}}|}}$
Do $OP = OM = R = {R}$, nên $|\overrightarrow{{OP}}| \cdot |\overrightarrow{{OM}}| = {R}^2 = {R**2}$.
$\overrightarrow{{OP}} \cdot \overrightarrow{{OM}} = ({P_in[0]})({P_out[0]}) + ({P_in[1]})({P_out[1]}) + ({P_in[2]})({P_out[2]}) = {dot_pp}$.
Suy ra $\cos \alpha = \frac{{{dot_pp}}}{{{R**2}}} = {cos_val_frac.numerator if cos_val_frac.denominator==1 else rf"\frac{{{cos_val_frac.numerator}}}{{{cos_val_frac.denominator}}}"}$.
Vậy $\alpha \approx {angle_deg}^{{\circ}}$."""

    key_arr = ["Đ" if x else "S" for x in (a_correct, b_correct, c_correct, d_correct)]
    key = ", ".join(key_arr)

    question = f"""{stem}

{stmt_a}

{stmt_b}

{stmt_c}

{stmt_d}"""

    solution = "\n\n".join([sol_a, sol_b, sol_c, sol_d])

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
    output_file = os.path.join(out_dir, "cau_1_questions.tex")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")

if __name__ == "__main__":
    main()