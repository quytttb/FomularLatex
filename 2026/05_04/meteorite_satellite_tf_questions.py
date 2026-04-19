"""
Đề đúng/sai: thiên thạch - vệ tinh - trái đất.

Bài toán trong không gian Oxyz:
- Trái đất hình cầu tâm O bán kính R = 6400 km (đơn vị toạ độ: 1000 km → R = 6.4)
- Hệ thống quan sát theo dõi đến độ cao 4600 km (bán kính quan sát = 11)
- Thiên thạch bay thẳng từ M đến N, v₁
- Hai vệ tinh A, B di chuyển trong mặt phẳng trung trực MN

4 mệnh đề a, b, c, d.
"""
import math
import os
import sys
import random
from fractions import Fraction
from typing import Tuple

# ==============================================================================
# Bộ tham số: M(0, m2, m3), N(m3, m2, 0) → OM = ON, I = (m3/2, m2, m3/2)
#   Cần OM = số nguyên, m3 chẵn
# ==============================================================================
PARAM_SETS = [
    # (m2, m3, OM,  bx, by)  -- bx, by cho B(bx, by, bx) nằm trong mp trung trực
    (5, 12, 13, 7, -6),
    (9, 12, 15, 8, -5),
    (15, 8, 17, 6, -7),
    (7, 24, 25, 10, -8),
    (15, 20, 25, 9, -7),
]

R_UNIT = Fraction(32, 5)  # 6400/1000 = 6.4 = 32/5
R_KM = 6400
OBS_ALT_KM = 4600

def fmt_point(p):
    return f"({p[0]}; {p[1]}; {p[2]})"

def sqrt_tex(n):
    """Return LaTeX for √n, simplifying perfect squares."""
    root = int(math.sqrt(n))
    if root * root == n:
        return str(root)
    return rf"\sqrt{{{n}}}"

def generate_question(seed_val=None) -> Tuple[str, str, str]:
    if seed_val is not None:
        random.seed(seed_val)

    m2, m3, OM, bx, by = random.choice(PARAM_SETS)

    # Toạ độ chính
    M = (0, m2, m3)
    N = (m3, m2, 0)
    k = m3 // 2  # m3 luôn chẵn
    I = (k, m2, k)       # trung điểm MN
    A_sat = (-k, -m2, -k)  # đối xứng I qua O
    B_sat = (bx, by, bx)   # nằm trong mp x=z

    # Khoảng cách
    OM_val = OM  # = √(m2² + m3²) = số nguyên
    OI_sq = 2 * k * k + m2 * m2
    OA_sq = OI_sq  # OA = OI vì A = -I
    OB_sq = 2 * bx * bx + by * by

    MN_sq = 2 * m3 * m3  # |MN|² = m3² + m3² = 2m3²
    MI_len_sq = MN_sq // 4  # MI = |MN|/2, MI² = m3²/2

    # R² trong đơn vị toạ độ
    R_sq = R_UNIT * R_UNIT  # (32/5)² = 1024/25

    # ==================== Câu a ====================
    # Khoảng cách ngắn nhất thiên thạch đến bề mặt Trái Đất
    # OH = √OI_sq (khoảng cách từ O đến đường MN)
    OH_km = math.sqrt(OI_sq) * 1000
    closest_km = round(OH_km - R_KM)
    
    sum_coords = 2 * k + m2
    correct_val_a = sum_coords - closest_km

    a_correct = random.choice([True, False])
    if a_correct:
        val_a = correct_val_a
    else:
        val_a = correct_val_a + random.choice([-100, 100, -200, 200, 50, -50])

    # ==================== Câu b ====================
    # Quãng đường dài nhất nếu thiên thạch đổi hướng lao xuống Trái Đất (tiếp tuyến)
    # MM' = √(OM² - R²) (tiếp tuyến từ M tới mặt cầu)
    # Nhưng quãng đường dài nhất = MM' + cung M'... = sqrt(OM² + R²) nếu xuyên qua
    # Thực tế: nếu lao thẳng qua tâm thì quãng đường = OM + R (xa nhất tới bề mặt xa)
    # Nhưng bài gốc: MM' là tiếp tuyến = √(OM² - R²), đó cũng là quãng đường xa nhất
    # trước khi va chạm (vì nếu hướng lệch tâm hơn thì không chạm)
    tangent_sq_frac = Fraction(OM * OM, 1) - R_sq  # OM² - R²
    tangent_km = math.sqrt(float(tangent_sq_frac)) * 1000
    longest_km = round(tangent_km)

    b_correct = random.choice([True, False])
    if b_correct:
        val_b = longest_km
    else:
        val_b = longest_km + random.choice([-200, 200, -500, 500])

    # ==================== Câu c ====================
    # Khoảng cách xa nhất 2 vệ tinh
    # AB_max = OA + OB (khi O, A, B thẳng hàng)
    OA_val = math.sqrt(OA_sq)
    OB_val = math.sqrt(OB_sq)
    AB_max_km = round((OA_val + OB_val) * 1000)

    # Giá trị sai (bẫy): dùng √(OA² + OB²) thay vì OA + OB
    AB_wrong_km = round(math.sqrt(OA_sq + OB_sq) * 1000)

    c_correct = random.choice([True, False])
    if c_correct:
        val_c = AB_max_km
    else:
        val_c = AB_wrong_km

    # ==================== Câu d ====================
    # Vệ tinh A va chạm thiên thạch tại I
    # t₁ = MI / v₁, t₂ = π·OA / v₂ → chọn v₁, v₂ sao cho t₁ = t₂
    # MI = m3√2 / 2 (đơn vị 1000km)
    # Chọn t (giờ) là số nguyên đẹp
    t_hours = random.choice([2, 3, 4, 5])

    # v₁ = MI / t = (m3√2/2) / t × 10³ km/h
    # Đặt v₁ = (m3√2 / (2t)) × 10³
    v1_coeff = Fraction(m3, 2 * t_hours)  # hệ số trước √2 × 10³

    # v₂ = π·OA / t = π·√OI_sq / t × 10³
    # Đặt v₂ = (π√OI_sq / t) × 10³
    v2_coeff_num = 1  # hệ số trước π√OI_sq
    v2_denom = t_hours

    # Kiểm tra: t₁ = t₂ = t ← đúng theo construction
    d_correct = random.choice([True, False])

    # Format v₁
    v1_tex = f"{v1_coeff.numerator}" if v1_coeff.denominator == 1 else rf"\frac{{{v1_coeff.numerator}}}{{{v1_coeff.denominator}}}"
    v1_full_tex = rf"{v1_tex}\sqrt{{2}} \cdot 10^3"

    # Format v₂
    if v2_denom == 1:
        v2_full_tex = rf"\pi\sqrt{{{OI_sq}}} \cdot 10^3"
    else:
        v2_full_tex = rf"\frac{{\pi\sqrt{{{OI_sq}}}}}{{{v2_denom}}} \cdot 10^3"

    if d_correct:
        v2_display = v2_full_tex
    else:
        # Sai: thay OI_sq bằng giá trị khác
        wrong_sq = OI_sq + random.choice([-4, 4, -8, 8])
        if wrong_sq <= 0:
            wrong_sq = OI_sq + 8
        if v2_denom == 1:
            v2_display = rf"\pi\sqrt{{{wrong_sq}}} \cdot 10^3"
        else:
            v2_display = rf"\frac{{\pi\sqrt{{{wrong_sq}}}}}{{{v2_denom}}} \cdot 10^3"

    # ==================== Đề bài ====================
    tikz_fig = r"""
\begin{center}
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
 
 \draw (0,0) circle(2.8cm);
 \draw (0,0)coordinate (O) circle(5cm);
 \draw 
 (150:3.6) coordinate (A)
 (130:3.5) coordinate (B)
 (0:2.8) coordinate (O1)
 (0:5) coordinate (O2)
 ;
 
 
 \draw (180:2.8) arc(180:360:2.8cm and 0.5cm);
 \draw (180:2.8) arc(-180:-360:2.8cm and 0.5cm);
 
 
 
 \draw (180:5) arc(180:360:5cm and 1cm);
 \draw[dashed] (180:5) arc(-180:-360:5cm and 1cm);
 
 
 \draw[dashed] (100:5)coordinate (P)--(30:4)coordinate (Q) ;
 \draw (P)--($(Q)!1.5!(P)$)coordinate (M)
 (Q)--($(P)!1.5!(Q)$)coordinate (N)
 ;
 \draw[<->] (O)--(O1)node[above,pos=0.5]{6400 km};
 \draw[<->] (O2)--(O1)node[above,pos=0.5]{4600 km};
 
\foreach \p/\r in {M/90,N/0,Q/90,O/-90,P/90,A/120,B/120}
\fill (\p) circle (1.2pt) node[shift={(\r:3mm)}]{$\p$};


\end{tikzpicture}
\end{center}
"""

    stem = f"""Các thiên thạch có đường kính lớn hơn $140\\text{{m}}$ và có thể lại gần Trái Đất ở khoảng cách nhỏ hơn $7500000\\text{{km}}$ được coi là những vật thể có khả năng va chạm gây nguy hiểm cho Trái Đất. Để theo dõi những thiên thạch này, các nhà nghiên cứu của trung tâm Vũ Trụ Nasa đã thiết lập các trạm quan sát các vật thể bay gần Trái Đất. Giả sử có một hệ thống quan sát có khả năng theo dõi các vật thể ở độ cao không vượt quá ${OBS_ALT_KM}\\text{{km}}$ so với mực nước biển. Coi Trái Đất là khối cầu có bán kính ${R_KM}\\text{{km}}$. Chọn hệ trục tọa độ $Oxyz$ trong không gian có gốc $O$ tại tâm Trái Đất và đơn vị độ dài trên mỗi trục tọa độ là $1000\\text{{km}}$. Một thiên thạch \textit{{(coi như một hạt)}} chuyển động với tốc độ $v_1 = {v1_full_tex}\\,(km/h)$ không đổi theo đường thẳng xuất phát từ điểm $M{fmt_point(M)}$ đến $N{fmt_point(N)}$.
{tikz_fig}"""

    stmt_a = f"{'*' if a_correct else ''}a) Khoảng cách thiên thạch gần với trái đất nhất có độ dài bằng $m\\text{{ (km)}}$ \\textit{{(làm tròn đến hàng đơn vị)}} khi thiên thạch ở vị trí $H(a; b; c)$. Khi đó $a+b+c-m$ bằng ${val_a}$."

    stmt_b = f"{'*' if b_correct else ''}b) Các nhà nghiên cứu của trung tâm vũ trụ Nasa đưa ra giả thiết nếu lúc thiên thạch đang ở vị trí $M$ bất ngờ đổi hướng và lao xuống trái đất với phương thẳng thì quãng đường dài nhất nó có thể va chạm với trái đất là ${val_b}\\text{{km}}$ \\textit{{(làm tròn đến hàng đơn vị)}}."

    stmt_c = f"{'*' if c_correct else ''}c) Tại thời điểm thiên thạch đang ở vị trí $M$ thì có $2$ vệ tinh đang ở vị trí $A{fmt_point(A_sat)}$, $B{fmt_point(B_sat)}$ có vận tốc khác nhau di chuyển trong mặt phẳng trung trực của $MN$ và luôn cách trái đất với khoảng cố định. Khoảng cách xa nhất của $2$ vệ tinh có thể đạt là ${val_c}\\text{{km}}$ \\textit{{(làm tròn đến hàng đơn vị)}}."

    stmt_d = f"{'*' if d_correct else ''}d) Nếu vệ tinh $A$ đi với vận tốc $v_2 = {v2_display}\\,(km/h)$ thì sẽ va chạm với thiên thạch."

    # ==================== Lời giải ====================
    MN_vec = (m3, 0, -m3)
    u_vec = (1, 0, -1)

    sol_a = f"""a) {'Đúng' if a_correct else 'Sai'}.

$M{fmt_point(M)}, N{fmt_point(N)}$ nên $\\overrightarrow{{MN}} = {fmt_point(MN_vec)}$.

Chọn $MN$ có VTCP là $\\vec{{u}} = (1; 0; -1)$, qua $M{fmt_point(M)}$ có phương trình $\\begin{{cases}} x = t \\\\ y = {m2} \\\\ z = {m3} - t \\end{{cases}}$.

Gọi $H$ là vị trí thiên thạch gần Trái Đất nhất. Khi đó $OH \\perp MN$ tại $H(t; {m2}; {m3} - t)$.
$\\Rightarrow \\overrightarrow{{OH}}(t; {m2}; {m3} - t) \\perp \\vec{{u}}(1; 0; -1)$
$\\Rightarrow t \\cdot 1 + {m2} \\cdot 0 + ({m3} - t) \\cdot (-1) = 0$
$\\Leftrightarrow t = {k} \\Rightarrow H{fmt_point(I)}$.
$\\Rightarrow OH = \\sqrt{{{k}^2 + {m2}^2 + {k}^2}} = {sqrt_tex(OI_sq)}$

Suy ra khoảng cách ngắn nhất từ tâm trái đất đến $MN$ là ${sqrt_tex(OI_sq)} \\cdot 1000 \\approx {round(math.sqrt(OI_sq)*1000)}\\text{{km}}$.
Khoảng cách thiên thạch gần với trái đất nhất là $m = {round(math.sqrt(OI_sq)*1000)} - {R_KM} = {closest_km}$.
Điểm $H({k}; {m2}; {k}) \\Rightarrow a+b+c = {sum_coords}$.
Vậy $a+b+c-m = {sum_coords} - {closest_km} = {correct_val_a}$."""

    # b) Tiếp tuyến từ M tới mặt cầu
    OM_sq = OM * OM
    R_sq_float = float(R_sq)
    R_dec = float(R_UNIT)

    sol_b = f"""b) {'Đúng' if b_correct else 'Sai'}.

Gọi $M'$ là điểm va chạm của thiên thạch với Trái Đất.
$\\Rightarrow MM'$ lớn nhất khi $MM'$ là tiếp tuyến kẻ từ $M$ tới mặt cầu - là bề mặt trái đất.
$\\Rightarrow MM' = \\sqrt{{OM^2 - OM'^2}} = \\sqrt{{{OM}^2 - {R_dec}^2}}$

Hay quãng đường dài nhất là $\\sqrt{{{OM}^2 - {R_dec}^2}} \\cdot 1000 \\approx {longest_km}\\text{{km}}$."""

    # c) Khoảng cách xa nhất 2 vệ tinh
    sol_c = f"""c) {'Đúng' if c_correct else 'Sai'}.

$A{fmt_point(A_sat)}, B{fmt_point(B_sat)} \\Rightarrow OA = {sqrt_tex(OA_sq)}, OB = {sqrt_tex(OB_sq)}$

$AB \\le OA + OB = {sqrt_tex(OA_sq)} + {sqrt_tex(OB_sq)} \\approx {round(OA_val + OB_val, 4)}$

Vậy $AB$ lớn nhất bằng ${AB_max_km}\\text{{km}}$ khi $O, A, B$ thẳng hàng."""

    # d) Va chạm
    MI_tex = rf"\frac{{{m3}\sqrt{{2}}}}{{2}}" if m3 != 2 else rf"\sqrt{{2}}"
    MI_val = m3 * math.sqrt(2) / 2

    sol_d_intro = f"""d) {'Đúng' if d_correct else 'Sai'}.

$M{fmt_point(M)}, N{fmt_point(N)}$ nên trung điểm $I$ của $MN$ có toạ độ $I{fmt_point(I)}$.
Do $OA = {sqrt_tex(OA_sq)}$ không đổi nên $A$ luôn thuộc mặt cầu có tâm $O$, bán kính $OA = {sqrt_tex(OA_sq)}$.

Để vệ tinh va chạm với thiên thạch thì chỉ có thể va chạm tại $I$ (vì $I$ thuộc mặt phẳng trung trực của $MN$ và nằm trên $MN$).

Khi đó $MI = \\frac{{MN}}{{2}} = \\frac{{{m3}\\sqrt{{2}}}}{{2}}$.

Thời gian để thiên thạch di chuyển từ $M$ đến $I$ là $t_1 = \\frac{{{MI_tex} \\cdot 10^3}}{{{v1_full_tex}}} = {t_hours}$ (giờ).

Nhận thấy $A, I$ đối xứng nhau qua $O$ nên quãng đường để vệ tinh di chuyển từ $A$ đến $I$ là một đường cong có độ dài bằng nửa chu vi đường tròn bán kính $OA$ và bằng $\\pi \\cdot OA = {sqrt_tex(OI_sq)}\\pi$."""

    if d_correct:
        sol_d = sol_d_intro + f"""

Vậy thời gian để vệ tinh đi từ $A$ đến $I$ là $t_2 = \\frac{{{sqrt_tex(OI_sq)}\\pi \\cdot 10^3}}{{{v2_full_tex}}} = {t_hours}$ (giờ).

Vậy $t_1 = t_2 = {t_hours}$ nên vệ tinh và thiên thạch va chạm."""
    else:
        wrong_t2 = t_hours * math.sqrt(OI_sq) / math.sqrt(wrong_sq)
        sol_d = sol_d_intro + f"""

Vậy thời gian để vệ tinh đi từ $A$ đến $I$ là $t_2 = \\frac{{{sqrt_tex(OI_sq)}\\pi \\cdot 10^3}}{{{v2_display}}} = \\frac{{{t_hours}\\sqrt{{{OI_sq}}}}}{{\\sqrt{{{wrong_sq}}}}} \\approx {round(wrong_t2, 2)}$ (giờ).

Vì $t_1 = {t_hours} \\ne t_2 \\approx {round(wrong_t2, 2)}$ nên vệ tinh và thiên thạch không va chạm."""

    # ==================== Kết hợp ====================
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

    seed = None
    if len(sys.argv) > 2:
        seed = int(sys.argv[2])

    content = ""
    keys = []

    for i in range(num_questions):
        q, s, k = generate_question(seed + i if seed is not None else None)
        keys.append(k)
        content += f"\\begin{{ex}}%Câu {i+1}\n{q}\n\n\\loigiai{{\n{s}\n}}\n\\end{{ex}}\n\n"

    template = r"""\documentclass[12pt,a4paper]{article}
\usepackage{amsmath,amssymb,fancyhdr,longtable}
\usepackage{polyglossia}
\setdefaultlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage{tikz}
\usetikzlibrary{angles,patterns,calc,arrows,intersections}
\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}
\usepackage[solcolor]{ex_test}
\newcommand{\heva}[1]{\left\{\begin{aligned}#1\end{aligned}\right.}

\begin{document}
#CONTENT#
\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "meteorite_satellite_tf_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")


if __name__ == "__main__":
    main()
