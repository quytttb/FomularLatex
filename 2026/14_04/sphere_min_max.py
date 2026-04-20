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

def simplify_sqrt(n: int) -> str:
    if n == 0: return "0"
    if n < 0: return f"\\sqrt{{{n}}}"
    outside = 1
    inside = n
    for i in range(math.isqrt(n), 1, -1):
        if n % (i*i) == 0:
            outside = i
            inside = n // (i*i)
            break
    if inside == 1:
        return str(outside)
    if outside == 1:
        return f"\\sqrt{{{inside}}}"
    return f"{outside}\\sqrt{{{inside}}}"

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

def generate_type1(seed_val=None) -> Tuple[str, str, str]:
    if seed_val is not None:
        random.seed(seed_val)
        
    while True:
        a = random.randint(-3, 3)
        b = random.randint(-3, 3)
        c = random.randint(-3, 3)
        if a == 0 and b == 0 and c == 0:
            continue
        R2 = a**2 + b**2 + c**2
        
        I = Point3D(random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3))
        
        # Chọn hệ số k ngẫu nhiên (MA + k·MB)
        k = random.choice([2, 3, 4])
        
        # Đặt A sao cho IA = k*R, tức là vec_IA = k*(a,b,c)
        A = Point3D(I.x + k*a, I.y + k*b, I.z + k*c)
        
        vec_IA = A - I
        IA2 = dist_sq(I, A)
        
        # IA' = R²/IA, tức IA'/IA = R²/IA² = 1/k²
        inv_ratio = Fraction(1, k**2)
        vec_IA_prime = Point3D(vec_IA.x * inv_ratio, vec_IA.y * inv_ratio, vec_IA.z * inv_ratio)
        A_prime = I + vec_IA_prime
        
        B = Point3D(random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
        IB2 = dist_sq(I, B)
        if IB2 > R2:
            A_prime_B2 = dist_sq(A_prime, B)
            if A_prime_B2 > 0:
                break

    R_tex = simplify_sqrt(R2)
    IA_tex = simplify_sqrt(IA2.numerator)
    
    def format_term(var, val):
        if val == 0: return rf"{var}^2"
        if val > 0: return rf"({var} - {val})^2"
        return rf"({var} + {-val})^2"
    
    eq_x = format_term('x', I.x.numerator)
    eq_y = format_term('y', I.y.numerator)
    eq_z = format_term('z', I.z.numerator)
    
    k_tex = str(k)
    question = rf"""Trong không gian với hệ tọa độ $Oxyz$, cho mặt cầu $(S) : {eq_x} + {eq_y} + {eq_z} = {R2}$ và hai điểm $A{A.to_tex()}; B{B.to_tex()}$. Xét điểm $M$ thay đổi thuộc mặt cầu $(S)$. Tính giá trị nhỏ nhất của biểu thức $P = MA + {k_tex}MB$. Kết quả làm tròn đến 2 số sau dấu phẩy."""

    N_frac = k**2 * A_prime_B2
    ans_val_exact = math.sqrt(float(N_frac))
    ans_val = round(ans_val_exact, 2)
    # Format: integer if .00, else up to 2 decimal places
    if ans_val == int(ans_val):
        ans_solution = str(int(ans_val))
        ans_display = str(int(ans_val))
    else:
        val_dot = f"{ans_val:.2f}"
        ans_solution = val_dot.replace('.', ',')
        ans_display = f"{ans_solution} | {val_dot}"
    ans_sqrt_tex = simplify_sqrt(int(N_frac)) if N_frac.denominator == 1 else f"\\sqrt{{{format_frac_tex(N_frac)}}}"

    inv_frac_tex = format_frac_tex(Fraction(1, k**2))
    inv_ratio_tex = format_frac_tex(Fraction(1, k))
    
    def format_sq(val):
        if val < 0: return rf"({val})^2"
        return rf"{val}^2"

    solution = rf"""Mặt cầu $(S)$ có tâm $I{I.to_tex()}$ và bán kính $R = \sqrt{{{R2}}} = {R_tex}$.
Ta tính khoảng cách từ tâm $I$ đến điểm $A$:
$$\overrightarrow{{IA}} = ({vec_IA.x}; {vec_IA.y}; {vec_IA.z}) \Rightarrow IA = \sqrt{{{format_sq(vec_IA.x)} + {format_sq(vec_IA.y)} + {format_sq(vec_IA.z)}}} = {IA_tex}.$$
Nhận xét thấy $IA = {k_tex}R$. Biểu thức cần tìm đạt nhỏ nhất là $P = MA + {k_tex}MB = {k_tex}\left(\frac{{1}}{{{k_tex}}}MA + MB\right)$.

Lấy điểm $A'$ nằm trên tia $IA$ sao cho $IA' \cdot IA = R^2 \Rightarrow IA' = \frac{{R^2}}{{IA}} = \frac{{{R2}}}{{{IA_tex}}}$.
Từ đó suy ra $\frac{{IA'}}{{IA}} = {inv_frac_tex} \Rightarrow \overrightarrow{{IA'}} = {inv_frac_tex}\overrightarrow{{IA}}$.
Tọa độ của $A'$ thỏa mãn hệ thức trên là:
$$A'\left({format_frac_tex(I.x)} + {inv_frac_tex}\cdot ({vec_IA.x}); {format_frac_tex(I.y)} + {inv_frac_tex}\cdot ({vec_IA.y}); {format_frac_tex(I.z)} + {inv_frac_tex}\cdot ({vec_IA.z})\right) \Rightarrow A'{A_prime.to_tex()}.$$

Xét hai tam giác $\Delta IMA'$ và $\Delta IAM$, ta có:
Góc $\widehat{{MIA}}$ chung.
Mặt khác, $\frac{{IA'}}{{IM}} = \frac{{R/{k_tex}}}{{R}} = {inv_ratio_tex}$ và $\frac{{IM}}{{IA}} = \frac{{R}}{{{k_tex}R}} = {inv_ratio_tex}$.
Suy ra $\frac{{IA'}}{{IM}} = \frac{{IM}}{{IA}} \Rightarrow \Delta IMA' \sim \Delta IAM$ (c.g.c).
Do đó, ta có tỉ số đồng dạng: $\frac{{MA'}}{{MA}} = \frac{{IM}}{{IA}} = {inv_ratio_tex} \Rightarrow MA = {k_tex}MA'$.

Thay vào biểu thức, ta được:
$$P = MA + {k_tex}MB = {k_tex}MA' + {k_tex}MB = {k_tex}(MA' + MB).$$
Áp dụng bất đẳng thức tam giác cho bộ ba điểm $M, A', B$, ta có: $MA' + MB \ge A'B$.
Dấu "$=$" xảy ra khi và chỉ khi $M$ thuộc đoạn thẳng $A'B$.
Ta kiểm tra vị trí tương đối của $A'$ và $B$ đối với mặt cầu $(S)$:
Khoảng cách $IA' = \frac{{R}}{{{k_tex}}} < R \Rightarrow A'$ nằm trong mặt cầu.
Khoảng cách $IB > R \Rightarrow B$ nằm ngoài mặt cầu (do $(x_B-x_I)^2+(y_B-y_I)^2+(z_B-z_I)^2 = {IB2.numerator} > {R2}$).
Vì vậy, đoạn thẳng $A'B$ luôn cắt mặt cầu $(S)$ tại một điểm, suy ra dấu "$=$" hoàn toàn có thể xảy ra.

Độ dài $A'B$ là:
$$\overrightarrow{{A'B}} = ({format_frac_tex(B.x - A_prime.x)}; {format_frac_tex(B.y - A_prime.y)}; {format_frac_tex(B.z - A_prime.z)}).$$
$$\Rightarrow A'B^2 = \left({format_frac_tex(B.x - A_prime.x)}\right)^2 + \left({format_frac_tex(B.y - A_prime.y)}\right)^2 + \left({format_frac_tex(B.z - A_prime.z)}\right)^2 = {format_frac_tex(A_prime_B2)}.$$
Vậy giá trị nhỏ nhất của biểu thức $P$ là ${k_tex}A'B = \sqrt{{{k**2} \cdot {format_frac_tex(A_prime_B2)}}} = {ans_sqrt_tex} \approx {ans_solution}$."""

    return question, solution, ans_display

def main():
    num_questions = 1
    dang = 1
    
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    if len(sys.argv) > 2:
        dang = int(sys.argv[2])
        
    seed_val = None
    if len(sys.argv) > 3:
        seed_val = int(sys.argv[3])

    questions_content = ""
    answers = []

    for i in range(num_questions):
        if dang == 1:
            q, s, a = generate_type1(seed_val + i if seed_val is not None else None)
        else:
            q, s, a = generate_type1(seed_val + i if seed_val is not None else None)
        answers.append(a)
        ans_str = str(a)
        questions_content += f"Câu {i + 1}: {q}\n\nLời giải:\n\n{s}\n\nĐáp án: {ans_str}\n\n"

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

\title{{Bài tập Mặt cầu Cực trị}}
\author{{Generator}}
\date{{\today}}

\begin{{document}}
\maketitle

{questions_content}

\end{{document}}"""

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "sphere_min_max.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(latex_document)

    print(f"Đã tạo {num_questions} câu dạng {dang} và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, ans in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {ans}")

if __name__ == "__main__":
    main()
