import sys
import os
import random
import math
from fractions import Fraction
from typing import Tuple

def fmt_frac(v):
    if hasattr(v, 'denominator') and v.denominator == 1:
        return f"{v.numerator}"
    return rf"\frac{{{v.numerator}}}{{{v.denominator}}}"

def fmt_dec(v, precision=4):
    out = f"{float(v):.{precision}f}".rstrip('0').rstrip('.')
    return out.replace('.', ',')

def bracket_term(var, val):
    if val == 0: return f"{var}^2"
    if val > 0: return f"({var} - {val})^2"
    return f"({var} + {-val})^2"

def generate_question(seed_val=None) -> Tuple[str, str, str]:
    if seed_val is not None:
        random.seed(seed_val)

    while True:
        R = random.randint(10, 25)
        h = random.choice([1, 2, 3])
        R_dl = R + h
        
        u1 = random.choice([1, 2, 3])
        u2 = random.choice([1, 2, 3, 4])
        if u1 == u2 and u1 != 1: continue
        u3 = 0
        
        S_factor = u1**2 + u2**2 + u3**2
        
        # Test delta for b
        delta = (R_dl**2)*S_factor - R**2*(u2**2 + u3**2)
        if delta <= 0: continue
        
        break
        
    km_per_unit = 400
    
    # a
    a_is_true = random.choice([True, False])
    fake_R_dl = R_dl if a_is_true else R_dl + random.choice([1, -1])
    stmt_a = rf"{'*' if a_is_true else ''}a) Tầng điện ly là một mặt cầu có tâm $O$ và bán kính ${fake_R_dl}$"
    ans_a = "Đúng" if a_is_true else "Sai"
    sol_a = rf"a) {ans_a}. Ta có tầng điện li luôn cách bề mặt Trái Đất ${h * km_per_unit}$ km tương ứng với ${h}$ đơn vị độ dài trong hệ trục tọa độ $Oxyz$ nên khi đó:" + "\n" + rf"Tầng điện li là một mặt cầu tâm $O$ và bán kính bằng $R = {R} + {h} = {R_dl}$." + "\n" + rf"Khi ấy ta có phương trình mặt cầu tầng điện li $(S'): x^2 + y^2 + z^2 = {R_dl**2}$."

    # b
    b_is_true = random.choice([True, False])
    if b_is_true:
        stmt_b_eq = rf"\heva{{x &= {R} + {u1 if u1 != 1 else ''}t \\ y &= {u2 if u2 != 1 else ''}t \quad (t \in \mathbb{{R}}) \\ z &= 0}}"
    else:
        fake_u1 = u1 + random.choice([1, -1])
        if fake_u1 == 0: fake_u1 = 2
        stmt_b_eq = rf"\heva{{x &= {R} + {fake_u1 if fake_u1 != 1 else ''}t \\ y &= {u2 if u2 != 1 else ''}t \quad (t \in \mathbb{{R}}) \\ z &= 0}}"
    
    stmt_b = rf"{'*' if b_is_true else ''}b) Phương trình tham số của đường thẳng $AB$ là: ${stmt_b_eq}$"
    ans_b = "Đúng" if b_is_true else "Sai"
    sol_b = rf"b) {ans_b}. Đường thẳng $AB$ đi qua $A({R};0;0)$ với vectơ chỉ phương là $\vec{{u}}=({u1};{u2};{u3})$ nên ta suy ra phương trình tham số của đường thẳng tương ứng là $\heva{{x &= {R} + {u1 if u1 != 1 else ''}t \\ y &= {u2 if u2 != 1 else ''}t \quad (t \in \mathbb{{R}}) \\ z &= 0}}$."

    # c
    c_is_true = random.choice([True, False])
    true_T = delta
    fake_T = true_T if c_is_true else true_T + random.choice([-10, 10, -5, 5])
    
    u1_str = f"{u1}a" if u1 != 1 else "a"
    u2_str = f"{u2}b" if u2 != 1 else "b"
    u3_str = "c"
    
    stmt_c = rf"{'*' if c_is_true else ''}c) Nếu tọa độ điểm $B$ là $(a; b; c)$ thì ta có $({u1_str} + {u2_str} + {u3_str})^2 = {fake_T}$"
    ans_c = "Đúng" if c_is_true else "Sai"
    
    term_x = f"({R} + {u1 if u1 != 1 else ''}t)"
    term_y = f"({u2 if u2 != 1 else ''}t)"
    
    B_coef = 2 * R * u1
    C_coef = R**2 - R_dl**2
    sqrt_delta = rf"\sqrt{{{delta}}}" if int(math.sqrt(delta))**2 != delta else str(int(math.sqrt(delta)))
    
    num_t0 = f"{-B_coef} + {sqrt_delta}"
    t0_str = rf"\frac{{{num_t0}}}{{{S_factor}}}" if S_factor != 1 else f"{num_t0}"
    
    sol_c = rf"""c) {ans_c}. Ta có $B = AB \cap (S')$, tọa độ $B({R} + {u1 if u1!=1 else ''}t; {u2 if u2!=1 else ''}t; 0)$, từ đó ta có phương trình:
${term_x}^2 + {term_y}^2 + 0^2 = {R_dl}^2 \Leftrightarrow {S_factor}t^2 + {B_coef}t + {C_coef} = 0 \Leftrightarrow t = \frac{{{-B_coef} - {sqrt_delta}}}{{{2*S_factor}}} \text{{ hoặc }} t = \frac{{{-B_coef} + {sqrt_delta}}}{{{2*S_factor}}}$
Do $\overrightarrow{{AB}} = k\vec{{u}}$ nên $y_B - y_A = k > 0 \Rightarrow y_B = {u2 if u2!=1 else ''}t > 0 \Rightarrow t > 0$ tức ta nhận $t = t_0 = {t0_str}$.
Suy ra $T = ({u1_str} + {u2_str} + {u3_str})^2 = ({u1}x_B + {u2}y_B + z_B)^2 = ({u1}({R} + {u1 if u1!=1 else ''}t) + {u2}({u2 if u2!=1 else ''}t))^2 = ({S_factor}t + {R*u1})^2$, thế vào ta được $T = {true_T}$."""

    # d
    d_is_true = random.choice([True, False])
    
    t0_val = (-B_coef + math.sqrt(delta)) / (2 * S_factor)
    t0_val = (-B_coef + math.sqrt(delta)) / (2 * S_factor) if S_factor==1 else (-B_coef + math.sqrt(delta)) / (2 * S_factor*0.5) # Wait, my quadratic equation is S_factor*t^2 + B_coef*t + C_coef = 0. Roots are (-B_coef +- sqrt(B_coef^2 - 4*S_factor*C_coef)) / (2*S_factor).
    # Recompute t0_val correctly
    roots = [(-B_coef + math.sqrt(B_coef**2 - 4*S_factor*C_coef))/(2*S_factor), (-B_coef - math.sqrt(B_coef**2 - 4*S_factor*C_coef))/(2*S_factor)]
    t0_val = max(roots)

    xA, yA, zA = R, 0, 0
    xB, yB, zB = R + u1*t0_val, u2*t0_val, 0
    OA_OB = xA*xB + yA*yB + zA*zB
    OA_len = R
    OB_len = R_dl
    
    cos_alpha = OA_OB / (OA_len * OB_len)
    alpha_rad = math.acos(cos_alpha)
    AOC_rad = 2 * alpha_rad
    
    chu_vi = 2 * math.pi * R
    l_nho = AOC_rad * R
    L_lon = chu_vi - l_nho
    
    S_thuc_te = L_lon * km_per_unit
    S_rounded = round(S_thuc_te)
    
    fake_S = S_rounded if d_is_true else S_rounded + random.choice([-100, 100, -50, 50])
    
    stmt_d = rf"{'*' if d_is_true else ''}d) Tính theo đơn vị km (Kết quả làm tròn đến hàng đơn vị) thì quãng đường thực tế lớn nhất đi được giữa $A$ và $C$ ở bề mặt Trái Đất khoảng ${fake_S}$ km."
    ans_d = "Đúng" if d_is_true else "Sai"
    
    num_acos = f"{int(u1*S_factor)}t_0 + {R*u1}" if S_factor != 1 else f"{u1}t_0 + {R*u1}"
    acos_inner_str = rf"\frac{{{num_t0} + {R*u1}}}{{{R * R_dl}}}" # Need careful formatting here. For now let's just use numerical value approximation in sol or correct symbolic.
    oa_ob_str = rf"{R}({R} + {u1 if u1!=1 else ''}t_0)" if u1!=1 else rf"{R}({R} + t_0)"
    
    sol_d = rf"""d) {ans_d}. Trước hết từ hình vẽ dưới, ta có:
$\cos \alpha = \cos \widehat{{AOB}} = \frac{{\overrightarrow{{OA}}.\overrightarrow{{OB}}}}{{OA.OB}} = \frac{{{oa_ob_str}}}{{{R} \times {R_dl}}} \Rightarrow \widehat{{AOC}} = 2\widehat{{AOB}} = 2\arccos\left(\frac{{{oa_ob_str}}}{{{R} \times {R_dl}}}\right) \text{{(radian)}}$
Gọi $(C)$ là đường tròn giao tuyến tạo bởi mặt phẳng $(OABC)$ cắt mặt cầu $(S)$ tức Trái Đất.
Khi ấy quãng đường lớn nhất giữa hai điểm $A$ và $C$ chính là cung lớn $AC$ (kí hiệu là $L$) thuộc đường tròn $(C)$.
Ta có chu vi đường tròn $(C)$ là $C = 2\pi R_{{tđ}} = {2*R}\pi$.
Độ dài cung nhỏ $AC$ là $l = \widehat{{AOC}}.R_{{tđ}} = 2 \times {R} \times \arccos\left(\frac{{{oa_ob_str}}}{{{R} \times {R_dl}}}\right)$.
Suy ra quãng đường cần tìm là $L = C - l$.
Với $t_0 \approx {t0_val:.4f}$ và $1$ đơn vị dài = ${km_per_unit}$ km thực tế, ta suy ra quãng đường thực tế lớn nhất cần tìm bằng $L_{{tt}} = {km_per_unit} L \approx {S_rounded}$ km."""

    stem_text = rf"""Bài toán 8: Trong không gian với hệ trục tọa độ $Oxyz$, coi Trái Đất là một hình cầu có tâm là gốc tọa độ và có bán kính bằng ${R}$ (đơn vị dài trên mỗi hệ trục tọa độ là ${km_per_unit}$ km). Coi tầng điện ly luôn cách bề mặt Trái Đất ${h * km_per_unit}$ km, tức là tầng điện li là một mặt cầu có tâm là gốc tọa độ $O$. Từ một đài phát $A$ đặt tại điểm $A({R};0;0)$ có phát một sóng điện từ với tần số $10$ MHz lên trên cao (với tốc độ không đổi bằng $3.10^8$ m/s) hướng theo vector $\vec{{u}}=({u1};{u2};{u3})$, sóng điện từ này gặp tầng điện ly tại điểm $B$, sau đó bị phản xạ và truyền trở lại gặp bề mặt Trái Đất tại điểm $C$. Biết rằng tính chất phản xạ cho ta kết quả là: bốn điểm $O, A, B, C$ thẳng hàng phẳng và $\widehat{{ABO}} = \widehat{{OBC}}, \widehat{{AOB}} = \widehat{{BOC}}$."""
    
    stem_tikz = r"""\begin{center}
  \begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
  \path (0,0) coordinate (O);
  \draw[fill=gray,opacity=0.5] (O) circle(2cm);
  \fill (O) circle(1pt);
  \draw (120:1) node[above]{Trái Đất};
  \draw (120:3.5) node[above]{Tầng Điện Li};
  \draw[] (O) circle(3cm);
  \draw (O)--(20:2cm) coordinate (A)--(40:3cm)coordinate (B)--(60:2cm) coordinate (C);
  \foreach \p/\r in {A/-40,B/40,C/90,O/-90}
  \fill (\p) circle (1.2pt) node[shift={(\r:3mm)}]{$\p$};
 \end{tikzpicture}
\end{center}"""

    stem = f"{stem_text}\n{stem_tikz}"

    question = f"{stem}\n\n{stmt_a}\n\n{stmt_b}\n\n{stmt_c}\n\n{stmt_d}"
    
    sol_stem = r"""\begin{center}
 \begin{tikzpicture}[line join = round, line cap=round, >=stealth, font=\footnotesize, scale=1]
  
  % 1. Vẽ Trái Đất với hiệu ứng gradient
  \shade[ball color=green!60, opacity=0.4] (0,0) circle(2cm);
  \draw[thick] (0,0) circle(2cm);
  \fill (0,0) circle(1.5pt) node[below left]{$O$};
  
  % 2. Vẽ Tầng điện li (nét đứt hoặc nét vẽ mỹ thuật)
  \draw[dashed, color=blue!60, thick] (0,0) circle(3cm);
  \draw[line width=1.2pt, color=blue!30, opacity=0.5] (0,0) circle(3.1cm);
  
  % 3. Đường truyền sóng (tô đậm và thêm mũi tên)
  \draw[red, thick, ->] (20:2) -- (40:3); % Sóng đi lên
  \draw[red, thick, ->] (40:3) -- (60:2); % Sóng phản xạ xuống
  
  % Vẽ bán kính để xác định góc (nét đứt mảnh)
  \draw[gray, dash dot] (0,0) -- (40:3);
  \draw[gray, dash dot] (0,0) -- (20:2);
  \draw[gray, dash dot] (0,0) -- (60:2);
  
  % 4. Các điểm nút
  \foreach \p/\pos in {(20:2)/A, (40:3)/B, (60:2)/C} {
   \fill[white] \p circle (2pt); % Tạo viền trắng cho điểm
   \draw[fill=black] \p circle (1.2pt);
  }
  
  % Gán nhãn cho các điểm
  \node[right] at (20:2) {$A$};
  \node[above] at (40:3) {$B$};
  \node[left] at (60:2) {$C$};
  
  % 5. Chú thích chữ
  \node[align=center, inner sep=1pt] at (120:1.2) {\textbf{Trái Đất}};
  \node[blue!70!black, align=center,rotate=30] at (120:3.5) {\textbf{Tầng Điện Li}};
  
  % 6. Thêm hiệu ứng sóng tại điểm phát A
  \foreach \r in {0.2, 0.4, 0.6}
  \draw[red, opacity={1-\r}] (20:2) ++(40:\r) arc (40:0:\r);
  
 \end{tikzpicture}
\end{center}"""
    
    solution = f"{sol_stem}\n\n{sol_a}\n\n{sol_b}\n\n{sol_c}\n\n{sol_d}".strip()

    key = ", ".join(["Đ" if x else "S" for x in [a_is_true, b_is_true, c_is_true, d_is_true]])
    
    return question, solution, key


def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    seed_val = None
    if len(sys.argv) > 2:
        seed_val = int(sys.argv[2])
        
    out_dir = os.path.dirname(os.path.abspath(__file__))
    
    content = ""
    keys = []
    
    for i in range(num_questions):
        seed = seed_val + i if seed_val is not None else None
        try:
            q, s, k = generate_question(seed)
        except Exception as e:
            q, s, k = "Lỗi tạo câu hỏi", str(e), "S, S, S, S"
        keys.append(k)
        content += rf"""Câu {i+1}: {q}

Lời giải:

{s}

"""

    template = r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath, amsfonts, amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\usepackage{tikz}
\usetikzlibrary{calc,angles,quotes,decorations.markings,intersections,patterns,shapes.geometric}

\newcommand{\heva}[1]{\left\{\begin{aligned}#1\end{aligned}\right.}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)

    out_path = os.path.join(out_dir, "cau_8_questions.tex")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {out_path}")
    print("\n=== ĐÁP ÁN ===")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: Đáp án: {k}")

if __name__ == "__main__":
    main()
