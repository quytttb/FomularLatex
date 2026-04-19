import sys
import os
import random
import math
from fractions import Fraction
from typing import Tuple

def format_frac_tex(f: Fraction) -> str:
    """Format a Fraction as LaTeX, already simplified."""
    if f.denominator == 1:
        return str(f.numerator)
    if f.numerator < 0:
        return rf"-\frac{{{-f.numerator}}}{{{f.denominator}}}"
    return rf"\frac{{{f.numerator}}}{{{f.denominator}}}"

class Point3D:
    def __init__(self, x, y, z):
        self.x = Fraction(x)
        self.y = Fraction(y)
        self.z = Fraction(z)
        
    def __add__(self, other):
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)
        
    def __sub__(self, other):
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)
        
    def __mul__(self, scalar):
        return Point3D(self.x * scalar, self.y * scalar, self.z * scalar)
        
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
        
    def __str__(self):
        return f"({self.x}; {self.y}; {self.z})"
        
    def to_tex(self):
        return f"({format_frac_tex(self.x)}; {format_frac_tex(self.y)}; {format_frac_tex(self.z)})"

def dist_sq(A, B):
    return (A.x - B.x)**2 + (A.y - B.y)**2 + (A.z - B.z)**2

def format_T_term(coeff, var_text, is_first=False):
    if coeff == 0:
        return ""
    if coeff == 1:
        res = var_text
    elif coeff == -1:
        res = "-" + var_text
    elif isinstance(coeff, Fraction) and coeff.denominator != 1:
        if coeff > 0:
            res = rf"\frac{{{coeff.numerator}}}{{{coeff.denominator}}}" + var_text
        else:
            res = rf"-\frac{{{-coeff.numerator}}}{{{coeff.denominator}}}" + var_text
    else:
        c_int = int(coeff)
        if c_int > 0:
            res = f"{c_int}{var_text}"
        else:
            res = f"{c_int}{var_text}"
    if not is_first and coeff > 0:
        return "+" + res
    return res

def format_combo_term(coeff, var, is_first=False):
    if coeff == 1:
        res = var
    elif coeff == -1:
        res = f"-{var}"
    else:
        res = f"{coeff}{var}"
    if not is_first and coeff > 0:
        return f"+{res}"
    return res

def generate_question(seed_val=None) -> Tuple[str, str, str]:
    if seed_val is not None:
        random.seed(seed_val)
        
    while True:
        # Chọn nghiệm dương R (bán kính mặt cầu) và nghiệm âm R2
        R = random.choice([2, 3, 4, 5, 6])
        R2 = random.choice([-1, -2, -3])
        
        # Hệ số đa thức: f(t) = t^4 + b_coeff*t^3 + k*t^2 + C0
        # f'(t) = 4t(t-R)(t-R2) => 3*b_coeff = -4(R+R2), 2*k = 4*R*R2
        b_coeff = Fraction(-4 * (R + R2), 3)  # hệ số của MD^3
        k = 2 * R * R2                         # tổng hệ số tỉ cự (âm)
        
        # k < 0, chia thành 3 hệ số âm: kA + kB + kC = k
        abs_k = -k  # abs_k >= 4
        if abs_k < 3:
            continue
        p1 = random.randint(1, abs_k - 2)
        p2 = random.randint(1, abs_k - p1 - 1)
        p3 = abs_k - p1 - p2
        parts = [-p1, -p2, -p3]
        random.shuffle(parts)
        kA, kB, kC = parts
        
        # Sinh điểm D
        D = Point3D(
            random.choice([-4, -3, -2, -1, 1, 2, 3, 4]),
            random.choice([-4, -3, -2, -1, 1, 2, 3, 4]),
            random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        )
        
        # Sinh A, B, C sao cho D là tâm tỉ cự: kA*DA + kB*DB + kC*DC = 0
        # Dùng kỹ thuật: DA = kC*u, DB = kC*v => DC = -kA*u - kB*v
        # Giới hạn u, v theo |kC| để tọa độ không quá lớn
        max_uv = max(1, min(3, 8 // max(abs(kA), abs(kB), abs(kC))))
        u = Point3D(random.randint(-max_uv, max_uv), random.randint(-max_uv, max_uv), random.randint(-max_uv, max_uv))
        v = Point3D(random.randint(-max_uv, max_uv), random.randint(-max_uv, max_uv), random.randint(-max_uv, max_uv))
        
        if (u.x == 0 and u.y == 0 and u.z == 0) or (v.x == 0 and v.y == 0 and v.z == 0):
            continue
            
        A = D + u * kC
        B = D + v * kC
        vec_DC = (u * (-kA)) + (v * (-kB))
        C = D + vec_DC
        
        # Đảm bảo các điểm phân biệt
        pts = [A, B, C, D]
        texs = [p.to_tex() for p in pts]
        if len(set(texs)) < 4:
            continue
            
        DA2 = dist_sq(D, A)
        DB2 = dist_sq(D, B)
        DC2 = dist_sq(D, C)
        
        C0 = kA * DA2 + kB * DB2 + kC * DC2
        
        # Sinh hệ số tổ hợp tuyến tính cho câu hỏi cuối
        coeff_choices = [-3, -2, -1, 1, 2, 3]
        c1 = random.choice(coeff_choices)
        c2 = random.choice(coeff_choices)
        c3 = random.choice(coeff_choices)
        
        # Chọn max hoặc min
        is_max = random.choice([True, False])
        
        base_val = float(c1 * D.x + c2 * D.y + c3 * D.z)
        sphere_part = R * math.sqrt(c1**2 + c2**2 + c3**2)
        
        if is_max:
            ans_float = base_val + sphere_part
        else:
            ans_float = base_val - sphere_part
            
        break
    
    # === FORMAT ĐỀ BÀI ===
    min_max_text = "lớn nhất" if is_max else "nhỏ nhất"
    
    # Biểu thức P
    term_MD4 = "MD^4"
    term_MD3 = format_T_term(b_coeff, "MD^3", is_first=False)
    term_MA2 = format_T_term(Fraction(kA), "MA^2", is_first=False)
    term_MB2 = format_T_term(Fraction(kB), "MB^2", is_first=False)
    term_MC2 = format_T_term(Fraction(kC), "MC^2", is_first=False)
    P_expr = f"{term_MD4}{term_MD3}{term_MA2}{term_MB2}{term_MC2}"
    
    # Biểu thức tổ hợp tuyến tính
    combo_expr = format_combo_term(c1, "a", is_first=True)
    combo_expr += format_combo_term(c2, "b")
    combo_expr += format_combo_term(c3, "c")
    
    question = rf"""Trong không gian với hệ tọa độ $Oxyz$, cho các điểm $A{A.to_tex()}; B{B.to_tex()}; C{C.to_tex()}; D{D.to_tex()}$. Điểm $M(a; b; c)$ thỏa mãn biểu thức $P = {P_expr}$ đạt giá trị nhỏ nhất ($P_{{\min}}$). Tìm giá trị {min_max_text} của ${combo_expr}$. Kết quả làm tròn đến 2 số sau dấu phẩy."""
    
    # === FORMAT LỜI GIẢI ===
    # Phần I: Biểu thức P dưới dạng tâm tỉ cự
    I_eq_terms = format_T_term(Fraction(kA), r"\overrightarrow{IA}", is_first=True)
    I_eq_terms += format_T_term(Fraction(kB), r"\overrightarrow{IB}", is_first=False)
    I_eq_terms += format_T_term(Fraction(kC), r"\overrightarrow{IC}", is_first=False)
    
    D_eq_terms = format_T_term(Fraction(kA), r"\overrightarrow{DA}", is_first=True)
    D_eq_terms += format_T_term(Fraction(kB), r"\overrightarrow{DB}", is_first=False)
    D_eq_terms += format_T_term(Fraction(kC), r"\overrightarrow{DC}", is_first=False)
    
    P_sq_terms = format_T_term(Fraction(kA), "MA^2", is_first=True)
    P_sq_terms += format_T_term(Fraction(kB), "MB^2", is_first=False)
    P_sq_terms += format_T_term(Fraction(kC), "MC^2", is_first=False)

    kB_sign = f"+ {kB}" if kB > 0 else f"- {-kB}"
    kC_sign = f"+ {kC}" if kC > 0 else f"- {-kC}"
    
    # P_min value
    P_min_val = Fraction(R**4) + b_coeff * Fraction(R**3) + Fraction(k) * Fraction(R**2) + C0
    
    # Giá trị base và norm cho Cauchy-Schwarz
    base_frac = c1 * D.x + c2 * D.y + c3 * D.z
    norm_sq = c1**2 + c2**2 + c3**2
    
    # Format đáp án chính xác dạng symbolic
    sign_R = "+" if is_max else "-"
    
    solution = rf"""Đặt $Q = {P_sq_terms}$ (phần chứa $MA, MB, MC$).
Gọi $I$ là điểm thỏa mãn ${I_eq_terms} = \vec{{0}}$.
Tọa độ điểm $I$ được xác định bởi:
$$ \begin{{cases}} x_I = \frac{{{kA}({format_frac_tex(A.x)}) {kB_sign}({format_frac_tex(B.x)}) {kC_sign}({format_frac_tex(C.x)})}}{{{k}}} = {format_frac_tex(D.x)} \\ y_I = \frac{{{kA}({format_frac_tex(A.y)}) {kB_sign}({format_frac_tex(B.y)}) {kC_sign}({format_frac_tex(C.y)})}}{{{k}}} = {format_frac_tex(D.y)} \\ z_I = \frac{{{kA}({format_frac_tex(A.z)}) {kB_sign}({format_frac_tex(B.z)}) {kC_sign}({format_frac_tex(C.z)})}}{{{k}}} = {format_frac_tex(D.z)} \end{{cases}} \Rightarrow I{D.to_tex()}.$$
Nhận xét: Điểm $I$ trùng với điểm $D$. Do đó ${D_eq_terms} = \vec{{0}}$.

Ta biến đổi:
\begin{{align*}}
Q &= {kA}(\overrightarrow{{MD}} + \overrightarrow{{DA}})^2 {kB_sign}(\overrightarrow{{MD}} + \overrightarrow{{DB}})^2 {kC_sign}(\overrightarrow{{MD}} + \overrightarrow{{DC}})^2 \\
&= {k} \cdot MD^2 + 2\overrightarrow{{MD}} \cdot ({D_eq_terms}) + {kA} \cdot DA^2 {kB_sign} DB^2 {kC_sign} DC^2 \\
&= {k} \cdot MD^2 + C_0 \quad \text{{(vì }} {D_eq_terms} = \vec{{0}} \text{{)}}
\end{{align*}}
trong đó $C_0 = {kA}({format_frac_tex(DA2)}) {kB_sign}({format_frac_tex(DB2)}) {kC_sign}({format_frac_tex(DC2)}) = {format_frac_tex(C0)}$.

Thay vào biểu thức $P$, đặt $t = MD \ge 0$:
$$P = f(t) = t^4 {format_T_term(b_coeff, "t^3")} + ({k})t^2 + C_0$$
Đạo hàm:
$$f'(t) = 4t^3 + {format_frac_tex(3*b_coeff)}t^2 + {2*k}t = t\left(4t^2 + {format_frac_tex(3*b_coeff)}t + {2*k}\right)$$
Giải $f'(t) = 0$ với $t \ge 0$:
$$4t^2 + {format_frac_tex(3*b_coeff)}t + {2*k} = 0 \Leftrightarrow 4(t - {R})(t - ({R2})) = 0$$
Suy ra $t = {R}$ (nhận, vì $t \ge 0$) hoặc $t = {R2}$ (loại).

Xét dấu $f'(t)$ trên $[0; +\infty)$:
\begin{{itemize}}
\item Với $0 < t < {R}$: $f'(t) < 0$ (hàm giảm).
\item Với $t > {R}$: $f'(t) > 0$ (hàm tăng).
\end{{itemize}}
Vậy $f(t)$ đạt giá trị nhỏ nhất tại $t = {R}$, tức $MD = {R}$.

Khi đó điểm $M(a; b; c)$ nằm trên mặt cầu tâm $D{D.to_tex()}$, bán kính $R = {R}$:
$$(a - {format_frac_tex(D.x)})^2 + (b - {format_frac_tex(D.y)})^2 + (c - {format_frac_tex(D.z)})^2 = {R**2}$$

Áp dụng bất đẳng thức Bunyakovsky (Cauchy-Schwarz):
$$({c1}^2 + {c2}^2 + {c3}^2)\left[(a - {format_frac_tex(D.x)})^2 + (b - {format_frac_tex(D.y)})^2 + (c - {format_frac_tex(D.z)})^2\right] \ge \left[{combo_expr} - ({format_frac_tex(base_frac)})\right]^2$$
$$\Rightarrow \left[{combo_expr} - ({format_frac_tex(base_frac)})\right]^2 \le {norm_sq} \cdot {R**2} = {norm_sq * R**2}$$
$$\Rightarrow -{math.sqrt(norm_sq * R**2):.4g} \le {combo_expr} - ({format_frac_tex(base_frac)}) \le {math.sqrt(norm_sq * R**2):.4g}$$
$$\Rightarrow {combo_expr} \in \left[{float(base_frac) - math.sqrt(norm_sq * R**2):.4g};\; {float(base_frac) + math.sqrt(norm_sq * R**2):.4g}\right]$$

Vậy giá trị {min_max_text} của ${combo_expr}$ bằng ${ans_float:.4g}$."""

    ans_rounded = round(ans_float, 2)
    if ans_rounded == int(ans_rounded):
        ans_display = str(int(ans_rounded))
    else:
        val_dot = f"{ans_rounded:.2f}"
        ans_display = f"{val_dot.replace('.', ',')} | {val_dot}"
    
    return question, solution, ans_display

def main():
    num_questions = 1
    
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    seed_val = None
    if len(sys.argv) > 2:
        seed_val = int(sys.argv[2])

    content = ""
    answers = []

    for i in range(num_questions):
        q, s, a = generate_question(seed_val + i if seed_val is not None else None)
        answers.append(a)
        content += f"Câu {i + 1}: {q}\n\nLời giải:\n\n{s}\n\nĐáp án: {a}\n\n"

    latex_document = rf"""\documentclass[a4paper,12pt]{{article}}
\usepackage{{amsmath, amsfonts, amssymb}}
\usepackage{{geometry}}
\geometry{{a4paper, margin=1in}}
\usepackage{{fontspec}}
\usepackage{{polyglossia}}
\setmainlanguage{{vietnamese}}
% \setmainfont{{Times New Roman}}
\usepackage{{tikz}}
\usetikzlibrary{{calc,angles,quotes}}

\title{{Bài tập Đa thức - Mặt cầu - Tâm tỉ cự}}
\author{{Generator}}
\date{{\today}}

\begin{{document}}
\maketitle

{content}

\end{{document}}"""

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "polynomial_sphere_extreme.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(latex_document)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, ans in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {ans}")

if __name__ == "__main__":
    main()
