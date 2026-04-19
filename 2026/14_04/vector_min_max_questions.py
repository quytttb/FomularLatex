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
        
def dot_product(p1: Point3D, p2: Point3D) -> Fraction:
    return p1.x * p2.x + p1.y * p2.y + p1.z * p2.z

def cross_product(p1: Point3D, p2: Point3D) -> Point3D:
    return Point3D(
        p1.y * p2.z - p1.z * p2.y,
        p1.z * p2.x - p1.x * p2.z,
        p1.x * p2.y - p1.y * p2.x
    )

def is_coplanar(A: Point3D, B: Point3D, C: Point3D, D: Point3D) -> bool:
    AB = B - A
    AC = C - A
    AD = D - A
    return dot_product(cross_product(AB, AC), AD) == 0

def format_plane_equation(A, B, C, K):
    terms = []
    if A != 0:
        if A == 1: terms.append("x")
        elif A == -1: terms.append("-x")
        else: terms.append(f"{A}x")
    if B != 0:
        if B == 1: terms.append("+y" if terms else "y")
        elif B == -1: terms.append("-y")
        else: terms.append(f"+{B}y" if B > 0 and terms else f"{B}y")
    if C != 0:
        if C == 1: terms.append("+z" if terms else "z")
        elif C == -1: terms.append("-z")
        else: terms.append(f"+{C}z" if C > 0 and terms else f"{C}z")
    if K != 0:
        terms.append(f"+{K}" if K > 0 and terms else f"{K}")
    
    if not terms:
        return "0 = 0"
    return "".join(terms) + " = 0"

def format_vector(p: Point3D):
    return f"({format_frac_tex(p.x)}; {format_frac_tex(p.y)}; {format_frac_tex(p.z)})"

def format_vec_sum(coeffs, vecs):
    terms = []
    for c, v in zip(coeffs, vecs):
        if c == 0: continue
        if c == 1: terms.append(f"+{v}" if terms else f"{v}")
        elif c == -1: terms.append(f"-{v}")
        else: terms.append(f"+{c}{v}" if c > 0 and terms else f"{c}{v}")
    res = "".join(terms)
    if res.startswith("+"): res = res[1:]
    return res if res else "0"

def generate_type1(seed_val=None) -> Tuple[str, str, str]:
    if seed_val is not None:
        random.seed(seed_val)
        
    while True:
        c_a = random.choice([-3, -2, -1, 1, 2, 3])
        c_b = random.choice([-3, -2, -1, 1, 2, 3])
        c_c = random.choice([-3, -2, -1, 1, 2, 3])
        k = c_a + c_b + c_c
        if k == 0:
            continue

        I = Point3D(random.randint(-5, 5), random.randint(-5, 5), random.choice([-3,-2,-1,1,2,3]))
        D = Point3D(random.randint(-5, 5), random.randint(-5, 5), random.choice([-3,-2,-1,1,2,3]))
        if I.z.numerator * D.z.numerator < 0:
            u = Point3D(random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
            v = Point3D(random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
            if (u.x==0 and u.y==0 and u.z==0) or (v.x==0 and v.y==0 and v.z==0): continue
            
            A = I + u * c_c
            B = I + v * c_c
            C = I - u * c_a - v * c_b
            if not is_coplanar(A, B, C, D):
                if A.to_tex() != B.to_tex() and B.to_tex() != C.to_tex() and C.to_tex() != A.to_tex() and \
                   A.to_tex() != D.to_tex() and B.to_tex() != D.to_tex() and C.to_tex() != D.to_tex():
                    break
                
    vec_ID = D - I
    t_val = -I.z / vec_ID.z
    M = I + vec_ID * t_val
    
    alpha = random.choice([1, 2, 3])
    beta = random.choice([-2, -1, 1, 2])
    gamma = random.choice([-3, -2, 2, 3])
    T_val = alpha * M.x + beta * M.y + gamma * M.z
    
    terms_T = []
    for coeff, var in [(alpha, "a"), (beta, "b"), (gamma, "c")]:
        if coeff == 1:
            terms_T.append(f"+{var}" if terms_T else var)
        elif coeff == -1:
            terms_T.append(f"-{var}")
        else:
            terms_T.append(f"+{coeff}{var}" if coeff > 0 and terms_T else f"{coeff}{var}")
    expr_T = "".join(terms_T)
    if expr_T.startswith("+"): expr_T = expr_T[1:]
    
    vec_terms = format_vec_sum([c_a, c_b, c_c], [r"\overrightarrow{MA}", r"\overrightarrow{MB}", r"\overrightarrow{MC}"])
    I_eq = format_vec_sum([c_a, c_b, c_c], [r"\overrightarrow{IA}", r"\overrightarrow{IB}", r"\overrightarrow{IC}"])
    MD_term_disp = rf"|\overrightarrow{{MD}}|" if abs(k) == 1 else rf"{abs(k)}|\overrightarrow{{MD}}|"
    
    question = rf"""Trong không gian với hệ tọa độ $Oxyz$, cho tứ diện $ABCD$ có $A{A.to_tex()}; B{B.to_tex()}; C{C.to_tex()}; D{D.to_tex()}$. Xét điểm $M$ thay đổi trên mặt phẳng $(Oxy)$. Khi $f = |{vec_terms}| + {MD_term_disp}$ đạt giá trị nhỏ nhất thì điểm $M$ có tọa độ $(a; b; c)$. Giá trị của biểu thức $T = {expr_T}$ bằng bao nhiêu? Kết quả làm tròn đến 2 số sau dấu phẩy."""

    b_sign_P = f"+ {c_b}" if c_b > 0 else f"- {-c_b}"
    c_sign_P = f"+ {c_c}" if c_c > 0 else f"- {-c_c}"
    abs_k = abs(k)
    k_disp = "" if abs_k == 1 else f"{abs_k}"

    solution = rf"""Gọi $I$ là điểm thỏa mãn ${I_eq} = \vec{{0}}$.
Tọa độ điểm $I$ được xác định bởi:
$$ \begin{{cases}} x_I = \frac{{{c_a}({A.x}) {b_sign_P}({B.x}) {c_sign_P}({C.x})}}{{{k}}} = {format_frac_tex(I.x)} \\ y_I = \frac{{{c_a}({A.y}) {b_sign_P}({B.y}) {c_sign_P}({C.y})}}{{{k}}} = {format_frac_tex(I.y)} \\ z_I = \frac{{{c_a}({A.z}) {b_sign_P}({B.z}) {c_sign_P}({C.z})}}{{{k}}} = {format_frac_tex(I.z)} \end{{cases}} \Rightarrow I{I.to_tex()}.$$
Ta có: ${vec_terms} = {k}\overrightarrow{{MI}} + ({I_eq}) = {k}\overrightarrow{{MI}}$.
Khi đó $f = |{k}\overrightarrow{{MI}}| + {MD_term_disp} = {k_disp}(MI + MD)$.
Để $f$ đạt giá trị nhỏ nhất thì $MI + MD$ nhỏ nhất.

Mặt phẳng $(Oxy)$ có phương trình $z = 0$.
Ta có $z_I = {I.z.numerator}$ và $z_D = {D.z.numerator}$.
Vì $z_I \cdot z_D = {I.z.numerator * D.z.numerator} < 0$ nên $I$ và $D$ nằm về hai phía so với mặt phẳng $(Oxy)$.
Do đó $MI + MD$ nhỏ nhất khi $M, I, D$ thẳng hàng và $M$ nằm giữa $I$ và $D$, hay $M$ là giao điểm của đường thẳng $ID$ và mặt phẳng $(Oxy)$.

Ta có $\overrightarrow{{ID}} = {format_vector(vec_ID)}$. Đường thẳng $ID$ có phương trình tham số là:
$$ \begin{{cases}} x = {format_frac_tex(I.x)} + ({format_frac_tex(vec_ID.x)})t \\ y = {format_frac_tex(I.y)} + ({format_frac_tex(vec_ID.y)})t \\ z = {format_frac_tex(I.z)} + ({format_frac_tex(vec_ID.z)})t \end{{cases}} $$
Vì $M \in (Oxy)$ nên $z_M = 0 \Rightarrow {format_frac_tex(I.z)} + ({format_frac_tex(vec_ID.z)})t = 0 \Rightarrow t = {format_frac_tex(t_val)}$.
Suy ra $x_M = {format_frac_tex(M.x)}$ và $y_M = {format_frac_tex(M.y)}$. Vậy $M{M.to_tex()}$.

Ta có $a = {format_frac_tex(M.x)}, b = {format_frac_tex(M.y)}, c = {format_frac_tex(M.z)}$.
Giá trị của biểu thức $T = {expr_T} = {format_frac_tex(T_val)}$."""

    ans_float = round(float(T_val), 2)
    if ans_float == int(ans_float):
        ans_display = str(int(ans_float))
    else:
        val_dot = f"{ans_float:.2f}"
        ans_display = f"{val_dot.replace('.', ',')} | {val_dot}"

    return question, solution, ans_display


def generate_type2(seed_val=None) -> Tuple[str, str, str]:
    if seed_val is not None:
        random.seed(seed_val)
        
    while True:
        c_a = random.choice([-3, -2, -1, 1, 2, 3])
        c_b = random.choice([-3, -2, -1, 1, 2, 3])
        c_c = random.choice([-3, -2, -1, 1, 2, 3])
        k = c_a + c_b + c_c
        if k == 0:
            continue
            
        A_p = random.choice([-2, -1, 1, 2])
        B_p = random.choice([-2, -1, 1, 2])
        C_p = random.choice([-3, -2, -1, 1, 2, 3])
        K_p = random.randint(-5, 5)
        
        I = Point3D(random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
        D = Point3D(random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
        
        eval_I = A_p*I.x + B_p*I.y + C_p*I.z + Fraction(K_p)
        eval_D = A_p*D.x + B_p*D.y + C_p*D.z + Fraction(K_p)
        
        if eval_I * eval_D > 0 and eval_I != 0 and eval_D != 0:
            u = Point3D(random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
            v = Point3D(random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
            if (u.x==0 and u.y==0 and u.z==0) or (v.x==0 and v.y==0 and v.z==0): continue
            
            A = I + u * c_c
            B = I + v * c_c
            C = I - u * c_a - v * c_b
            if not is_coplanar(A, B, C, D):
                if A.to_tex() != B.to_tex() and B.to_tex() != C.to_tex() and C.to_tex() != A.to_tex() and \
                   A.to_tex() != D.to_tex() and B.to_tex() != D.to_tex() and C.to_tex() != D.to_tex():
                    break
                
    S = A_p**2 + B_p**2 + C_p**2
    t_H = -eval_D / Fraction(S)
    n_vec = Point3D(A_p, B_p, C_p)
    D_prime = D + n_vec * (2 * t_H)
    
    vec_IDp = D_prime - I
    eval_vec = A_p*vec_IDp.x + B_p*vec_IDp.y + C_p*vec_IDp.z
    t_M = -eval_I / Fraction(eval_vec)
    M = I + vec_IDp * t_M
    
    alpha = random.choice([1, 2, 3])
    beta = random.choice([-2, -1, 1, 2])
    gamma = random.choice([-3, -2, 2, 3])
    T_val = alpha * M.x + beta * M.y + gamma * M.z
    
    terms_T = []
    for coeff, var in [(alpha, "a"), (beta, "b"), (gamma, "c")]:
        if coeff == 1:
            terms_T.append(f"+{var}" if terms_T else var)
        elif coeff == -1:
            terms_T.append(f"-{var}")
        else:
            terms_T.append(f"+{coeff}{var}" if coeff > 0 and terms_T else f"{coeff}{var}")
    expr_T = "".join(terms_T)
    if expr_T.startswith("+"): expr_T = expr_T[1:]
    
    plane_eq = format_plane_equation(A_p, B_p, C_p, K_p)
    
    vec_terms = format_vec_sum([c_a, c_b, c_c], [r"\overrightarrow{MA}", r"\overrightarrow{MB}", r"\overrightarrow{MC}"])
    I_eq = format_vec_sum([c_a, c_b, c_c], [r"\overrightarrow{IA}", r"\overrightarrow{IB}", r"\overrightarrow{IC}"])
    MD_term_disp = rf"|\overrightarrow{{MD}}|" if abs(k) == 1 else rf"{abs(k)}|\overrightarrow{{MD}}|"
    
    question = rf"""Trong không gian với hệ tọa độ $Oxyz$, cho tứ diện $ABCD$ có $A{A.to_tex()}; B{B.to_tex()}; C{C.to_tex()}; D{D.to_tex()}$. Xét điểm $M$ thay đổi trên mặt phẳng $(P): {plane_eq}$. Khi $f = |{vec_terms}| + {MD_term_disp}$ đạt giá trị nhỏ nhất thì điểm $M$ có tọa độ $(a; b; c)$. Giá trị của biểu thức $T = {expr_T}$ bằng bao nhiêu? Kết quả làm tròn đến 2 số sau dấu phẩy."""

    b_sign_P = f"+ {c_b}" if c_b > 0 else f"- {-c_b}"
    c_sign_P = f"+ {c_c}" if c_c > 0 else f"- {-c_c}"
    abs_k = abs(k)
    k_disp = "" if abs_k == 1 else f"{abs_k}"

    solution = rf"""Gọi $I$ là điểm thỏa mãn ${I_eq} = \vec{{0}}$.
Tọa độ điểm $I$ được xác định bởi:
$$ \begin{{cases}} x_I = \frac{{{c_a}({A.x}) {b_sign_P}({B.x}) {c_sign_P}({C.x})}}{{{k}}} = {format_frac_tex(I.x)} \\ y_I = \frac{{{c_a}({A.y}) {b_sign_P}({B.y}) {c_sign_P}({C.y})}}{{{k}}} = {format_frac_tex(I.y)} \\ z_I = \frac{{{c_a}({A.z}) {b_sign_P}({B.z}) {c_sign_P}({C.z})}}{{{k}}} = {format_frac_tex(I.z)} \end{{cases}} \Rightarrow I{I.to_tex()}.$$
Ta có: ${vec_terms} = {k}\overrightarrow{{MI}} + ({I_eq}) = {k}\overrightarrow{{MI}}$.
Khi đó $f = |{k}\overrightarrow{{MI}}| + {MD_term_disp} = {k_disp}(MI + MD)$.
Để $f$ đạt giá trị nhỏ nhất thì $MI + MD$ nhỏ nhất.

Đặt $g(x,y,z) = {plane_eq.replace(" = 0", "")}$.
Thay tọa độ $I, D$ vào $g(x,y,z)$ ta được:
$$g(I) = {format_frac_tex(eval_I)}$$
$$g(D) = {format_frac_tex(eval_D)}$$
Vì $g(I) \cdot g(D) > 0$ nên $I$ và $D$ nằm cùng phía so với mặt phẳng $(P)$.
Gọi $D'$ là điểm đối xứng của $D$ qua mặt phẳng $(P)$. Khi đó $MD = MD'$.
Suy ra $MI + MD = MI + MD' \ge ID'$.
Dấu "=" xảy ra khi $M, I, D'$ thẳng hàng và $M$ nằm giữa $I, D'$, hay $M$ là giao điểm của đường thẳng $ID'$ và mặt phẳng $(P)$.

Gọi $H$ là hình chiếu của $D$ lên $(P)$. Đường thẳng đi qua $D$ vuông góc với $(P)$ có véctơ chỉ phương $\vec{{n_{{P}}}} = {format_vector(n_vec)}$.
Phương trình tham số của đường thẳng $DH$:
$$ \begin{{cases}} x = {format_frac_tex(D.x)} + ({A_p})t \\ y = {format_frac_tex(D.y)} + ({B_p})t \\ z = {format_frac_tex(D.z)} + ({C_p})t \end{{cases}} $$
Vì $H \in (P)$ nên thay tọa độ tham số vào phương trình $(P)$ ta tìm được $t = {format_frac_tex(t_H)}$.
Suy ra $D'$ là điểm đối xứng của $D$ qua $H$ ứng với tham số $k' = 2t = {format_frac_tex(2*t_H)}$.
Tọa độ điểm $D'{D_prime.to_tex()}$.

Ta có $\overrightarrow{{ID'}} = {format_vector(vec_IDp)}$. Phương trình đường thẳng $ID'$:
$$ \begin{{cases}} x = {format_frac_tex(I.x)} + ({format_frac_tex(vec_IDp.x)})t' \\ y = {format_frac_tex(I.y)} + ({format_frac_tex(vec_IDp.y)})t' \\ z = {format_frac_tex(I.z)} + ({format_frac_tex(vec_IDp.z)})t' \end{{cases}} $$
Vì $M \in (P)$ nên thay tọa độ tham số vào phương trình $(P)$ ta được $t' = {format_frac_tex(t_M)}$.
Suy ra $x_M = {format_frac_tex(M.x)}, y_M = {format_frac_tex(M.y)}, z_M = {format_frac_tex(M.z)}$. Vậy $M{M.to_tex()}$.

Ta có $a = {format_frac_tex(M.x)}, b = {format_frac_tex(M.y)}, c = {format_frac_tex(M.z)}$.
Giá trị của biểu thức $T = {expr_T} = {format_frac_tex(T_val)}$."""

    ans_float = round(float(T_val), 2)
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

    content = ""
    answers = []

    for i in range(num_questions):
        if dang == 1:
            q, s, a = generate_type1(seed_val + i if seed_val is not None else None)
        else:
            q, s, a = generate_type2(seed_val + i if seed_val is not None else None)
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

\title{{Bài tập Vectơ và Tọa độ trong không gian}}
\author{{Generator}}
\date{{\today}}

\begin{{document}}
\maketitle

{content}

\end{{document}}"""
    tex_content = latex_document

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "vector_min_max_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu dạng {dang} và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, ans in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {ans}")

if __name__ == "__main__":
    main()
