import math
import os
import sys
import random
from fractions import Fraction
from typing import Tuple

PARAM_SETS = [
    # (A, B, time_total, R)
    ((-16, -10, 10), (24, 20, 0), 10, 12)
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
    
    A, B, t_total, R = PARAM_SETS[0]
    
    # Tính toán vector vận tốc
    AB = (B[0]-A[0], B[1]-A[1], B[2]-A[2])
    v_vec = (AB[0]/t_total, AB[1]/t_total, AB[2]/t_total)
    v_sq = v_vec[0]**2 + v_vec[1]**2 + v_vec[2]**2
    v_val = math.sqrt(v_sq)

    # Điểm vuông góc H từ O đến chuyển động
    t_H = - (A[0]*v_vec[0] + A[1]*v_vec[1] + A[2]*v_vec[2]) / v_sq
    H = (A[0] + v_vec[0]*t_H, A[1] + v_vec[1]*t_H, A[2] + v_vec[2]*t_H)
    d_sq = H[0]**2 + H[1]**2 + H[2]**2
    d_val = math.sqrt(d_sq)
    
    # Thời gian trong vùng kiểm soát
    t_delta = math.sqrt((R**2 - d_sq) / v_sq)
    t1 = t_H - t_delta
    t2 = t_H + t_delta
    
    T_hours = t2 - t1
    T_mins = T_hours * 60
    
    # Vị trí đi vào và ra
    P_in = (A[0] + v_vec[0]*t1, A[1] + v_vec[1]*t1, A[2] + v_vec[2]*t1)
    P_out = (A[0] + v_vec[0]*t2, A[1] + v_vec[1]*t2, A[2] + v_vec[2]*t2)
    
    # Mệnh đề A
    a_correct = random.choice([True, False])
    v_display = int(v_sq) if a_correct else random.choice([24, 28, 30])
    val_a = sqrt_tex(v_display)
    
    # Mệnh đề B
    b_correct = random.choice([True, False])
    if b_correct:
        stmt_b_eq = f"d^2 + T = {int(d_sq + T_mins)}"
    else:
        d_fake = int(d_val) if d_val.is_integer() else 6
        stmt_b_eq = f"d + 2T = {d_fake + 2*int(T_mins)}"
    
    # Mệnh đề C
    c_correct = random.choice([True, False])
    correct_val_c = t1 + 2*P_out[0] - P_out[1] + 3*P_out[2]
    val_c = int(correct_val_c) if c_correct else int(correct_val_c) + random.choice([-10, -18, 10, 18, 5])
    
    # Mệnh đề D
    d_correct = random.choice([True, False])
    cos_theta = (P_in[0]*P_out[0] + P_in[1]*P_out[1] + P_in[2]*P_out[2]) / (R**2)
    angle_rad = math.acos(cos_theta)
    angle_deg = round(math.degrees(angle_rad))
    # Bẫy góc (góc kề bù)
    wrong_angle = 180 - angle_deg
    val_d = angle_deg if d_correct else wrong_angle
    if val_d == angle_deg and not d_correct:
        val_d = 64 # để tránh trùng
        
    stem = rf"""Trong không gian với hệ trục tọa độ $Oxyz$ (với đơn vị đo trên các trục tọa độ là ki-lômét). Một {obj} từ vị trí điểm $A{fmt_point(A)}$ {mov} đến vị trí điểm $B{fmt_point(B)}$ hết {t_total} giờ. Biết {sta} đặt ở vị trí gốc tọa độ $O$ {rad_desc} {R} km.

Xét tính đúng, sai của các phát biểu sau:"""
    
    stmt_a = rf"{'*' if a_correct else ''}a) Vận tốc di chuyển của {obj} trên quỹ đạo $AB$ là ${val_a} \mathrm{{~km/h}}$."
    stmt_b = rf"{'*' if b_correct else ''}b) Trong suốt quá trình di chuyển từ $A$ đến $B$, khoảng cách ngắn nhất từ {obj} đến {sta} $O$ là $d$ (km) và thời gian kể từ khi {sta} bắt đầu phát hiện được đến khi {obj} ra khỏi vùng kiểm soát là $T$ (phút). Khi đó ta có hệ thức: ${stmt_b_eq}$."
    stmt_c = rf"{'*' if c_correct else ''}c) Khoảng thời gian từ lúc {obj} xuất phát ở $A$ cho đến khi lọt vào vùng kiểm soát là $t_1$ (giờ) và vị trí ngay khi ra khỏi vùng kiểm soát là điểm $M(x_M; y_M; z_M)$. Khi đó: $t_1 + 2x_M - y_M + 3z_M = {val_c}$."
    stmt_d = rf"{'*' if d_correct else ''}d) {sta.capitalize()} tại $O$ sử dụng một hệ thống {sensor} để bám sát mục tiêu. Góc quét không gian của {sensor} (góc tạo bởi hướng tia của {sensor} lúc bắt đầu phát hiện và lúc {obj} vượt ra ngoài tầm kiểm soát) xấp xỉ ${val_d}^{{\circ}}$ (làm tròn đến số nguyên gần nhất)."

    # Lời giải chi tiết
    sol_a = rf"""a) {'Đúng' if a_correct else 'Sai'}.

Ta có $\overrightarrow{{AB}} = {fmt_point((int(AB[0]), int(AB[1]), int(AB[2])))} $. Thời gian di chuyển là $t = {t_total}$ giờ.
Vận tốc di chuyển là vector $\vec{{v}} = \frac{{1}}{{{t_total}}} \overrightarrow{{AB}} = {fmt_point((int(v_vec[0]), int(v_vec[1]), int(v_vec[2])))} \text{{ (km/h)}}$.
Độ lớn vận tốc: $v = |\vec{{v}}| = \sqrt{{{int(v_vec[0])}^2 + {int(v_vec[1])}^2 + ({int(v_vec[2])})^2}} = \sqrt{{{int(v_sq)}}} \text{{ (km/h)}}$."""

    sol_b = rf"""b) {'Đúng' if b_correct else 'Sai'}.

Phương trình quỹ đạo chuyển động của {obj}: $\heva{{x &= {A[0]} + {int(v_vec[0])}t \\ y &= {A[1]} + {int(v_vec[1])}t \\ z &= {A[2]} + {int(v_vec[2])}t}} \quad (t \ge 0)$ (với $t$ là số giờ).
Bình phương khoảng cách từ $O$ đến {obj} tại thời điểm $t$ là $OP^2$:
$$OP^2 = ({A[0]} + {int(v_vec[0])}t)^2 + ({A[1]} + {int(v_vec[1])}t)^2 + ({A[2]} + {int(v_vec[2])}t)^2$$
$$= {int(v_sq)}t^2 - {int(2 * v_sq * t_H)}t + {A[0]**2 + A[1]**2 + A[2]**2} = {int(v_sq)}(t - {int(t_H)})^2 + {int(d_sq)}$$
Khoảng cách ngắn nhất là $d(O, AB) = \sqrt{{{int(d_sq)}}}$ km (khi $t = {int(t_H)}$ giờ).
{obj} nằm trong vùng kiểm soát khi $OP^2 \le {R}^2 \iff {int(v_sq)}(t - {int(t_H)})^2 + {int(d_sq)} \le {R**2}$
$\iff {int(v_sq)}(t - {int(t_H)})^2 \le {int(R**2 - d_sq)} \iff (t - {int(t_H)})^2 \le {int((R**2 - d_sq)/v_sq)} \iff {int(t1)} \le t \le {int(t2)}$.
Suy ra thời gian nằm trong vùng kiểm soát bằng ${int(t2)} - {int(t1)} = {int(T_hours)}$ (giờ), đổi ra $T = {int(T_hours)} \times 60 = {int(T_mins)}$ (phút).
Và khoảng cách cực tiểu $d = \sqrt{{{int(d_sq)}}}$.
Ta có  $d^2 + T = {int(d_sq)} + {int(T_mins)} = {int(d_sq + T_mins)}$."""

    sol_c = rf"""c) {'Đúng' if c_correct else 'Sai'}.

Theo phân tích trên, thời điểm bắt đầu vào vùng kiểm soát là $t_1 = {int(t1)}$ (giờ).
Thời điểm ra khỏi vùng kiểm soát là $t_2 = {int(t2)}$ (giờ).
Vị trí ngay khi ra khỏi vùng kiểm soát là điểm $M$: thay $t_2 = {int(t2)}$ vào phương trình quỹ đạo ta được $M({int(P_out[0])}; {int(P_out[1])}; {int(P_out[2])})$.
Thay số vào biểu thức: $t_1 + 2x_M - y_M + 3z_M = {int(t1)} + 2({int(P_out[0])}) - {int(P_out[1])} + 3({int(P_out[2])}) = {int(t1)} + {2*int(P_out[0])} - {int(P_out[1])} + {3*int(P_out[2])} = {int(correct_val_c)}$."""

    cos_val_frac = Fraction(int(P_in[0]*P_out[0] + P_in[1]*P_out[1] + P_in[2]*P_out[2]), R**2)

    sol_d = rf"""d) {'Đúng' if d_correct else 'Sai'}.

Vị trí bắt đầu phát hiện là $P({int(P_in[0])}; {int(P_in[1])}; {int(P_in[2])})$, tọa độ vector $\overrightarrow{{OP}} = {fmt_point((int(P_in[0]), int(P_in[1]), int(P_in[2])))}$.
Vị trí lúc mất tín hiệu là $M({int(P_out[0])}; {int(P_out[1])}; {int(P_out[2])})$, tọa độ vector $\overrightarrow{{OM}} = {fmt_point((int(P_out[0]), int(P_out[1]), int(P_out[2])))}$.
Góc quét không gian $\alpha = (\overrightarrow{{OP}}, \overrightarrow{{OM}})$. Ta có $\cos \alpha = \frac{{\overrightarrow{{OP}} \cdot \overrightarrow{{OM}}}}{{|\overrightarrow{{OP}}| \cdot |\overrightarrow{{OM}}|}}$
Do $OP = OM = R = {R}$, nên $|\overrightarrow{{OP}}| \cdot |\overrightarrow{{OM}}| = {R}^2 = {R**2}$.
$\overrightarrow{{OP}} \cdot \overrightarrow{{OM}} = ({int(P_in[0])})({int(P_out[0])}) + ({int(P_in[1])})({int(P_out[1])}) + ({int(P_in[2])})({int(P_out[2])}) = {int(P_in[0]*P_out[0] + P_in[1]*P_out[1] + P_in[2]*P_out[2])}$.
Suy ra $\cos \alpha = \frac{{{int(P_in[0]*P_out[0] + P_in[1]*P_out[1] + P_in[2]*P_out[2])}}}{{{R**2}}} = {cos_val_frac.numerator if cos_val_frac.denominator==1 else rf"\frac{{{cos_val_frac.numerator}}}{{{cos_val_frac.denominator}}}"}$.
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
    output_file = os.path.join(out_dir, "flight_path_tf_questions.tex")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")

if __name__ == "__main__":
    main()