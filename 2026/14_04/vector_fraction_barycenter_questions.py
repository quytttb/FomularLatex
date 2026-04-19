import sys
import os
import random
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
    else:
        res = f"{coeff}{var_text}"
        
    if not is_first and coeff > 0:
        return "+" + res
    return res

def generate_type1(seed_val=None) -> Tuple[str, str, str]:
    if seed_val is not None:
        random.seed(seed_val)
        
    while True:
        # Chọn các hệ số a, b, c
        a = random.choice([-3, -2, -1, 1, 2, 3])
        b = random.choice([-3, -2, -1, 1, 2, 3])
        c = random.choice([-3, -2, -1, 1, 2, 3])
        
        k = a + b + c
        if k == 0:
            continue
            
        D = Point3D(random.choice([-4, -3, -2, -1, 1, 2, 3, 4]), random.choice([-4, -3, -2, -1, 1, 2, 3, 4]), random.choice([-4, -3, -2, -1, 1, 2, 3, 4]))
        
        # Để đảm bảo tọa độ nguyên, ta chọn vector DA' = c * u, DB' = c * v
        u = Point3D(random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3))
        v = Point3D(random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3))
        
        if (u.x == 0 and u.y == 0 and u.z == 0) or (v.x == 0 and v.y == 0 and v.z == 0):
            continue
            
        A = D + u * c
        B = D + v * c
        
        # c * DC = -a * DA - b * DB
        # c * DC = -a * (c * u) - b * (c * v)
        # DC = -a * u - b * v
        vec_DC = (u * (-a)) + (v * (-b))
        C = D + vec_DC
        
        # Đảm bảo các điểm phân biệt
        if A.to_tex() == B.to_tex() or B.to_tex() == C.to_tex() or C.to_tex() == A.to_tex():
            continue
        if A.to_tex() == D.to_tex() or B.to_tex() == D.to_tex() or C.to_tex() == D.to_tex():
            continue
            
        DA2 = dist_sq(D, A)
        DB2 = dist_sq(D, B)
        DC2 = dist_sq(D, C)
        
        K = a * DA2 + b * DB2 + c * DC2
        if K != 0:
            break

    # Chọn mặt phẳng ngẫu nhiên
    planes = [
        ("Oxy", "z = 0", lambda p: Point3D(p.x, p.y, 0)),
        ("Oyz", "x = 0", lambda p: Point3D(0, p.y, p.z)),
        ("Oxz", "y = 0", lambda p: Point3D(p.x, 0, p.z))
    ]
    plane_name, plane_eq, proj_func = random.choice(planes)
    
    M = proj_func(D)
    
    # Xác định min/max
    is_max = (K > 0)
    min_max_text = "lớn nhất" if is_max else "nhỏ nhất"
    K_sign_text = ">" if is_max else "<"
    
    # Tính giá trị cực trị m của T
    MD2 = dist_sq(M, D)
    if MD2 == 0:
        # M trùng D (D nằm trên mặt phẳng), không dùng được
        # Bỏ qua, sinh lại
        return generate_type1(seed_val + 1000 if seed_val is not None else None)
    m_val = Fraction(k) + K / MD2
    
    # Tạo hệ số random cho tổ hợp tuyến tính: c_m*m + c_x*xm + c_y*ym + c_z*zm
    coeff_choices = [-2, -1, 1, 2]
    c_m = random.choice(coeff_choices)
    c_x = random.choice(coeff_choices)
    c_y = random.choice(coeff_choices)
    c_z = random.choice(coeff_choices)
    
    combo_val = c_m * m_val + c_x * M.x + c_y * M.y + c_z * M.z
    
    # Format biểu thức tổ hợp tuyến tính
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
    
    combo_expr = format_combo_term(c_m, "m", is_first=True)
    combo_expr += format_combo_term(c_x, "x_M")
    combo_expr += format_combo_term(c_y, "y_M")
    combo_expr += format_combo_term(c_z, "z_M")
    
    ans_val = combo_val
    
    # Format biểu thức T
    termA = format_T_term(a, r"\left(\frac{MA}{MD}\right)^2", is_first=True)
    termB = format_T_term(b, r"\left(\frac{MB}{MD}\right)^2", is_first=False)
    termC = format_T_term(c, r"\left(\frac{MC}{MD}\right)^2", is_first=False)
    T_expr = termA + termB + termC
    
    # Format biểu thức P
    termPa = format_T_term(a, "MA^2", is_first=True)
    termPb = format_T_term(b, "MB^2", is_first=False)
    termPc = format_T_term(c, "MC^2", is_first=False)
    P_expr = termPa + termPb + termPc
    
    # Format phương trình I
    I_eq_A = format_T_term(a, r"\overrightarrow{IA}", is_first=True)
    I_eq_B = format_T_term(b, r"\overrightarrow{IB}", is_first=False)
    I_eq_C = format_T_term(c, r"\overrightarrow{IC}", is_first=False)
    I_eq = I_eq_A + I_eq_B + I_eq_C
    
    # Format phương trình của I cho D
    D_eq_A = format_T_term(a, r"\overrightarrow{DA}", is_first=True)
    D_eq_B = format_T_term(b, r"\overrightarrow{DB}", is_first=False)
    D_eq_C = format_T_term(c, r"\overrightarrow{DC}", is_first=False)
    D_eq = D_eq_A + D_eq_B + D_eq_C
    
    b_sign_P = f"+ {b}" if b > 0 else f"- {-b}"
    c_sign_P = f"+ {c}" if c > 0 else f"- {-c}"

    question = rf"""Trong không gian với hệ tọa độ $Oxyz$, cho các điểm $A{A.to_tex()}; B{B.to_tex()}; C{C.to_tex()}; D{D.to_tex()}$. Xét điểm $M(x_M; y_M; z_M)$ thay đổi trên mặt phẳng $({plane_name})$. Biểu thức $T = {T_expr}$ đạt giá trị {min_max_text} là $m$ khi $M$ ở vị trí xác định. Khi đó ${combo_expr}$ bằng bao nhiêu? Kết quả làm tròn đến 2 số sau dấu phẩy."""

    solution = rf"""Đặt $P = {P_expr}$ (tử số của $T$).
Gọi $I$ là điểm thỏa mãn ${I_eq} = \vec{{0}}$.
Tọa độ điểm $I$ được xác định bởi:
$$ \begin{{cases}} x_I = \frac{{{a}({A.x}) {b_sign_P}({B.x}) {c_sign_P}({C.x})}}{{{k}}} = {format_frac_tex(D.x)} \\ y_I = \frac{{{a}({A.y}) {b_sign_P}({B.y}) {c_sign_P}({C.y})}}{{{k}}} = {format_frac_tex(D.y)} \\ z_I = \frac{{{a}({A.z}) {b_sign_P}({B.z}) {c_sign_P}({C.z})}}{{{k}}} = {format_frac_tex(D.z)} \end{{cases}} \Rightarrow I{D.to_tex()}.$$
Nhận xét: Điểm $I$ trùng với điểm $D$. Do đó $D$ chính là tâm tỉ cự của biểu thức $P$, tức là ta có ${D_eq} = \vec{{0}}$.

Ta có:
\begin{{align*}}
P &= {a}(\overrightarrow{{MD}} + \overrightarrow{{DA}})^2 {b_sign_P}(\overrightarrow{{MD}} + \overrightarrow{{DB}})^2 {c_sign_P}(\overrightarrow{{MD}} + \overrightarrow{{DC}})^2 \\
&= {k}MD^2 + 2\overrightarrow{{MD}}({D_eq}) + {a}DA^2 {b_sign_P}DB^2 {c_sign_P}DC^2 \\
&= {k}MD^2 + {a}DA^2 {b_sign_P}DB^2 {c_sign_P}DC^2 \quad \text{{(vì }} {D_eq} = \vec{{0}} \text{{)}}
\end{{align*}}
Ta tính các bình phương khoảng cách:
$$DA^2 = {format_frac_tex(DA2)}, \quad DB^2 = {format_frac_tex(DB2)}, \quad DC^2 = {format_frac_tex(DC2)}$$
Thay vào biểu thức trên, ta được:
$${a}DA^2 {b_sign_P}DB^2 {c_sign_P}DC^2 = {a}({format_frac_tex(DA2)}) {b_sign_P}({format_frac_tex(DB2)}) {c_sign_P}({format_frac_tex(DC2)}) = {format_frac_tex(K)}.$$
Do đó, $P = {k}MD^2 {"+" if K >= 0 else "-"} {format_frac_tex(abs(K))}$.
Suy ra biểu thức $T = \frac{{P}}{{MD^2}} = \frac{{{k}MD^2 {"+" if K >= 0 else "-"} {format_frac_tex(abs(K))}}}{{MD^2}} = {k} {"+" if K >= 0 else "-"} \frac{{{format_frac_tex(abs(K))}}}{{MD^2}}$.

Vì ${format_frac_tex(K)} \neq 0$, để $T$ đạt giá trị {min_max_text} thì $MD^2$ phải đạt giá trị nhỏ nhất (với điều kiện $MD > 0$).
Mặt khác, $M \in ({plane_name})$ nên khoảng cách $MD$ đạt giá trị nhỏ nhất khi $M$ là hình chiếu vuông góc của $D$ lên mặt phẳng $({plane_name})$.
Tọa độ hình chiếu của điểm $D{D.to_tex()}$ lên mặt phẳng $({plane_name})$ (có phương trình ${plane_eq}$) là điểm $M{M.to_tex()}$.
Vậy khi biểu thức $T$ đạt giá trị {min_max_text}, $M{M.to_tex()}$ và $m = {format_frac_tex(m_val)}$.

Ta tính: ${combo_expr} = {format_frac_tex(ans_val)}$."""

    ans_float = round(float(ans_val), 2)
    if ans_float == int(ans_float):
        ans_display = str(int(ans_float))
    else:
        val_dot = f"{ans_float:.2f}"
        ans_display = f"{val_dot.replace('.', ',')} | {val_dot}"

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

\title{{Bài tập Phân thức Tâm tỉ cự cực trị}}
\author{{Generator}}
\date{{\today}}

\begin{{document}}
\maketitle

{questions_content}

\end{{document}}"""

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "vector_fraction_barycenter_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(latex_document)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, ans in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {ans}")

if __name__ == "__main__":
    main()
