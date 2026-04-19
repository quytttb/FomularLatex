import math
import os
import sys
import random
from fractions import Fraction
from typing import Tuple

def format_frac_tex(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    if f.numerator < 0:
        return rf"-\frac{{{-f.numerator}}}{{{f.denominator}}}"
    return rf"\frac{{{f.numerator}}}{{{f.denominator}}}"

def get_nice_vector():
    base = random.choice([(2,3,6), (1,4,8), (2,6,9), (3,4,12), (6,10,15), (4,4,2), (3,4,0)])
    perm = list(base)
    random.shuffle(perm)
    return tuple(p * random.choice([1, -1]) for p in perm)

def format_plane(A, B, C, D):
    terms = []
    for coeff, var in [(A, 'x'), (B, 'y'), (C, 'z')]:
        if coeff == 0: continue
        if coeff == 1: terms.append(var if not terms else f"+ {var}")
        elif coeff == -1: terms.append(f"- {var}")
        else:
            if not terms: terms.append(f"{coeff}{var}")
            else:
                if coeff > 0: terms.append(f"+ {coeff}{var}")
                else: terms.append(f"- {abs(coeff)}{var}")
    if D > 0: terms.append(f"+ {D}")
    elif D < 0: terms.append(f"- {abs(D)}")
    res = " ".join(terms) + " = 0"
    if res.startswith("+ "): res = res[2:]
    return res

def format_line(P0, u):
    terms = []
    if P0[0] == 0: tx = "x"
    else: tx = f"x {-P0[0]:+}" if P0[0] < 0 else f"x - {P0[0]}"
    terms.append(rf"\frac{{{tx}}}{{{u[0]}}}")
    
    if P0[1] == 0: ty = "y"
    else: ty = f"y {-P0[1]:+}" if P0[1] < 0 else f"y - {P0[1]}"
    terms.append(rf"\frac{{{ty}}}{{{u[1]}}}")
    
    if P0[2] == 0: tz = "z"
    else: tz = f"z {-P0[2]:+}" if P0[2] < 0 else f"z - {P0[2]}"
    terms.append(rf"\frac{{{tz}}}{{{u[2]}}}")
    
    return " = ".join(terms)

def format_sphere(Ix, Iy, Iz, R):
    terms = []
    for val, var in [(Ix, 'x'), (Iy, 'y'), (Iz, 'z')]:
        if val == 0: terms.append(f"{var}^2")
        else:
            op = "-" if val > 0 else "+"
            terms.append(f"({var} {op} {abs(val)})^2")
    return " + ".join(terms) + f" = {R**2}"

def make_linear_expr(vars_dict):
    keys = list(vars_dict.keys())
    random.shuffle(keys)
    chosen_keys = keys[:random.randint(4, min(len(keys), 7))]
    
    expr_str_parts = []
    val = 0
    for i, k in enumerate(chosen_keys):
        c = random.choice([-3, -2, -1, 1, 2, 3])
        val += c * vars_dict[k]
        
        if i == 0:
            if c == 1: expr_str_parts.append(k)
            elif c == -1: expr_str_parts.append(f"-{k}")
            else: expr_str_parts.append(f"{c}{k}")
        else:
            if c == 1: expr_str_parts.append(f"+ {k}")
            elif c == -1: expr_str_parts.append(f"- {k}")
            elif c > 0: expr_str_parts.append(f"+ {c}{k}")
            else: expr_str_parts.append(f"- {abs(c)}{k}")
            
    return " ".join(expr_str_parts), float(val)

def generate_base_params():
    K = random.choice([2, 3, 4])
    while True:
        ka = random.choice([-3, -2, -1, 1, 2, 3])
        kb = random.choice([-3, -2, -1, 1, 2, 3])
        kc = K - ka - kb
        if kc not in [0] and abs(kc) <= 5: 
            break
            
    while True:
        I = (random.randint(-4, 4), random.randint(-4, 4), random.randint(-4, 4))
        if I[0] != 0 and I[1] != 0 and I[2] != 0:
            break
    
    while True:
        A = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
        B = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
        if A == I or B == I or A == B: continue
        
        cx = I[0] - (ka*(A[0]-I[0]) + kb*(B[0]-I[0])) / kc
        cy = I[1] - (ka*(A[1]-I[1]) + kb*(B[1]-I[1])) / kc
        cz = I[2] - (ka*(A[2]-I[2]) + kb*(B[2]-I[2])) / kc
        
        if cx.is_integer() and cy.is_integer() and cz.is_integer():
            C = (int(cx), int(cy), int(cz))
            if C != A and C != B and C != I:
                break
                
    def dist_sq(P1, P2): return sum((P1[i]-P2[i])**2 for i in range(3))
    
    C0 = ka * dist_sq(I, A) + kb * dist_sq(I, B) + kc * dist_sq(I, C)
    
    return K, ka, kb, kc, I, A, B, C, C0

def format_vector_term(coeff, vec_name):
    if coeff == 1: return rf"\overrightarrow{{{vec_name}}}"
    elif coeff == -1: return rf"-\overrightarrow{{{vec_name}}}"
    elif coeff > 0: return rf"{coeff}\overrightarrow{{{vec_name}}}"
    else: return rf"{-coeff}\overrightarrow{{{vec_name}}}"

def format_vector_eq(ka, kb, kc):
    parts = []
    parts.append(format_vector_term(ka, "IA"))
    if kb > 0: parts.append(rf"+ {format_vector_term(kb, 'IB')}")
    else: parts.append(rf"- {format_vector_term(abs(kb), 'IB')}")
    if kc > 0: parts.append(rf"+ {format_vector_term(kc, 'IC')}")
    else: parts.append(rf"- {format_vector_term(abs(kc), 'IC')}")
    return " ".join(parts)

def format_vector_sum(ka, kb, kc):
    parts = []
    parts.append(format_vector_term(ka, "MA"))
    
    if kb > 0: parts.append(rf"+ {format_vector_term(kb, 'MB')}")
    else: parts.append(rf"- {format_vector_term(abs(kb), 'MB')}")
    
    if kc > 0: parts.append(rf"+ {format_vector_term(kc, 'MC')}")
    else: parts.append(rf"- {format_vector_term(abs(kc), 'MC')}")
    
    return " ".join(parts)

def generate_menh_de_a(prob_type, params):
    K, ka, kb, kc, I, A, B, C, C0 = params
    is_true = random.choice([True, False])
    
    opt = random.choice([1, 2])
    if opt == 1:
        plane_name = random.choice(["Oxy", "Oyz", "Oxz"])
        if plane_name == "Oxy":
            M = (I[0], I[1], 0)
            dist_sq = I[2]**2
            dist = abs(I[2])
            P_str = "(Oxy)"
        elif plane_name == "Oyz":
            M = (0, I[1], I[2])
            dist_sq = I[0]**2
            dist = abs(I[0])
            P_str = "(Oyz)"
        else:
            M = (I[0], 0, I[2])
            dist_sq = I[1]**2
            dist = abs(I[1])
            P_str = "(Oxz)"
    else:
        M = (random.randint(-4, 4), random.randint(-4, 4), random.randint(-4, 4))
        while M == I:
            M = (random.randint(-4, 4), random.randint(-4, 4), random.randint(-4, 4))
        
        n_raw = (I[0]-M[0], I[1]-M[1], I[2]-M[2])
        gcd = math.gcd(abs(n_raw[0]), math.gcd(abs(n_raw[1]), abs(n_raw[2])))
        n = (n_raw[0]//gcd, n_raw[1]//gcd, n_raw[2]//gcd)
        
        D = -(n[0]*M[0] + n[1]*M[1] + n[2]*M[2])
        P_eq = format_plane(n[0], n[1], n[2], D)
        P_str = rf"(\alpha): {P_eq}"
        dist_sq = sum((I[i]-M[i])**2 for i in range(3))
        dist = math.sqrt(dist_sq)

    if prob_type == 1:
        m_val = K * dist
    else:
        m_val = K * dist_sq + C0
        
    vars_dict = {'x_M': M[0], 'y_M': M[1], 'z_M': M[2], 'm': m_val}
    expr_str, true_val = make_linear_expr(vars_dict)
    val = true_val
    if not is_true: 
        val += random.choice([-2, -1, 1, 2])
    disp_val = f"{val:.1f}".replace(".", ",")
    
    prefix = "*a) " if is_true else "a) "
    stmt = rf'''{prefix}Khi điểm $M$ có toạ độ $(x_M; y_M; z_M)$ thuộc mặt phẳng ${P_str}$ thì biểu thức $P$ đạt giá trị nhỏ nhất là $m$. Giá trị biểu thức $S = {expr_str}$ (làm tròn đến hàng phần mười) bằng ${disp_val}$.'''
    
    vec_eq = format_vector_eq(ka, kb, kc)
    loigiai = rf'''a) Xét hệ thức $\overrightarrow{{v}} = {vec_eq} = \overrightarrow{{0}}$. 
Suy ra tâm tỉ cự $I({I[0]}; {I[1]}; {I[2]})$. {f"Và lượng hằng số $C_0 = {ka} IA^2 {kb:+} IB^2 {kc:+} IC^2 = {C0}$." if prob_type == 2 else ""}
Cho mặt phẳng $(P)$ là ${P_str}$. Điểm $M$ thuộc $(P)$ để $P$ đạt GTNN khi $M$ là hình chiếu vuông góc của $I$ lên $(P)$. 
Tính toán hình chiếu ta được toạ độ $M({M[0]}; {M[1]}; {M[2]})$.
Khi đó $\min P = m = {int(m_val) if isinstance(m_val, int) or isinstance(m_val, float) and m_val.is_integer() else f"{K}\sqrt{{{dist_sq}}}"}$.
Với toạ độ $M(x_M; y_M; z_M)$, ta tính được $S = {expr_str} = {true_val:.1f}$.'''
    return stmt, is_true, loigiai

def generate_menh_de_b(prob_type, params):
    K, ka, kb, kc, I, A, B, C, C0 = params
    is_true = random.choice([True, False])
    
    M = (random.randint(-4, 4), random.randint(-4, 4), random.randint(-4, 4))
    while M == I:
        M = (random.randint(-4, 4), random.randint(-4, 4), random.randint(-4, 4))
        
    v_IM = (M[0]-I[0], M[1]-I[1], M[2]-I[2])
    choices = []
    if v_IM[2] != 0:
        choices.append((1, 0, -v_IM[0]/v_IM[2]))
        choices.append((0, 1, -v_IM[1]/v_IM[2]))
    if v_IM[0] != 0:
        choices.append((-v_IM[1]/v_IM[0], 1, 0))
    if v_IM[1] != 0:
        choices.append((1, -v_IM[0]/v_IM[1], 0))
    
    u = None
    for c in choices:
        denoms = [Fraction(x).limit_denominator().denominator for x in c]
        lcm = math.lcm(*denoms)
        tu = (int(c[0]*lcm), int(c[1]*lcm), int(c[2]*lcm))
        gcd = math.gcd(abs(tu[0]), math.gcd(abs(tu[1]), abs(tu[2])))
        if gcd != 0:
            u_cand = (tu[0]//gcd, tu[1]//gcd, tu[2]//gcd)
            if u_cand != (0,0,0): 
                u = u_cand
                break
        
    if u is None: u = (1, 1, 1)

    t = random.choice([-2, -1, 1, 2])
    P0 = (M[0] + t*u[0], M[1] + t*u[1], M[2] + t*u[2])
    
    line_eq = format_line(P0, u)
    dist_sq = sum(x**2 for x in v_IM)
    dist = math.sqrt(dist_sq)
    
    if prob_type == 1:
        m_val = K * dist
    else:
        m_val = K * dist_sq + C0
        
    vars_dict = {'x_M': M[0], 'y_M': M[1], 'z_M': M[2], 'm': m_val}
    expr_str, true_val = make_linear_expr(vars_dict)
    val = true_val
    if not is_true: 
        val += random.choice([-2, -1, 1, 2])
    disp_val = f"{val:.1f}".replace(".", ",")
    
    prefix = "*b) " if is_true else "b) "
    stmt = rf'''{prefix}Tìm toạ độ điểm $M(x_M; y_M; z_M)$ thuộc đường thẳng $d: {line_eq}$ để biểu thức $P$ đạt giá trị nhỏ nhất là $m$. Giá trị biểu thức $S = {expr_str}$ (làm tròn đến hàng phần mười) bằng ${disp_val}$.'''
    
    loigiai = rf'''b) Đường thẳng $d$ đi qua điểm $D({P0[0]}; {P0[1]}; {P0[2]})$ có VTCP $\overrightarrow{{u}} = ({u[0]}; {u[1]}; {u[2]})$.
Điểm $M \in d$ để $P$ đạt GTNN khi $M$ là hình chiếu vuông góc của $I$ lên $d$.
Tính toán hình chiếu ta được toạ độ $M({M[0]}; {M[1]}; {M[2]})$.
Khoảng cách $IM = \sqrt{{{dist_sq}}}$.
Khi đó $m = {int(m_val) if type(m_val)!=float or m_val.is_integer() else f"{K}\sqrt{{{dist_sq}}}" }$.
Với toạ độ $x_M, y_M, z_M$, ta tính được $S = {expr_str} = {true_val:.1f}$.'''
    return stmt, is_true, loigiai

def generate_menh_de_c_d(prob_type, params, is_inside):
    K, ka, kb, kc, I, A, B, C, C0 = params
    is_true = random.choice([True, False])
    
    v = get_nice_vector()
    L = int(math.sqrt(v[0]**2 + v[1]**2 + v[2]**2))
    J = (I[0] + v[0], I[1] + v[1], I[2] + v[2])
    
    if is_inside:
        R = random.randint(L + 1, L + 5)
    else:
        R = random.randint(1, L - 1)
        
    d_min = abs(L - R)
    d_max = L + R
    
    if prob_type == 1:
        m_val = K * d_min
        M_val = K * d_max
    else:
        m_val = K * (d_min**2) + C0
        M_val = K * (d_max**2) + C0
        
    s_eq = format_sphere(J[0], J[1], J[2], R)
    
    M1 = (J[0] + R * v[0] / L, J[1] + R * v[1] / L, J[2] + R * v[2] / L)
    M2 = (J[0] - R * v[0] / L, J[1] - R * v[1] / L, J[2] - R * v[2] / L)
    
    dist1 = sum((M1[i] - I[i])**2 for i in range(3))
    dist2 = sum((M2[i] - I[i])**2 for i in range(3))
    if dist1 < dist2:
        M_min_pt, M_max_pt = M1, M2
    else:
        M_min_pt, M_max_pt = M2, M1
        
    vars_dict = {
        'x_M': M_min_pt[0], 'y_M': M_min_pt[1], 'z_M': M_min_pt[2],
        'x_N': M_max_pt[0], 'y_N': M_max_pt[1], 'z_N': M_max_pt[2],
        'm': m_val, 'M': M_val
    }
    expr_str, true_val = make_linear_expr({k: vars_dict[k] for k in vars_dict if k != 'M'})
    val = true_val
    expr_str_display = expr_str
    
    if not is_true: 
        val += random.choice([-2, -1, 1, 2])
    disp_val = f"{val:.1f}".replace(".", ",")
    
    letter = "d" if is_inside else "c"
    prefix = f"*{letter}) " if is_true else f"{letter}) "
    
    lbl = "(S_2)" if is_inside else "(S_1)"
    stmt = rf'''{prefix}Tìm toạ độ điểm $M$ thuộc mặt cầu ${lbl}: {s_eq}$ để biểu thức $P$ đạt giá trị nhỏ nhất là $m$ tại toạ độ $(x_M; y_M; z_M)$ hoặc lớn nhất là $M'$ tại toạ độ $(x_N; y_N; z_N)$. Giá trị biểu thức $S = {expr_str_display}$ (làm tròn đến hàng phần mười) bằng ${disp_val}$.'''
    
    pos_str = "TRONG" if is_inside else "NGOÀI"
    loigiai = rf'''{letter}) Mặt cầu ${lbl}$ có tâm $J({J[0]}; {J[1]}; {J[2]})$ và bán kính $R={R}$.
Độ dài $IJ = {L}$. Ta thấy $IJ {'<' if is_inside else '>'} R$, do đó điểm $I$ nằm {pos_str} mặt cầu.
Đường thẳng $IJ$ đi qua $I$ và $J$, cắt mặt cầu tại 2 điểm $M_1, M_2$.
Khoảng cách nhỏ nhất từ $I$ đến mặt cầu là $\min = |IJ - R| = {d_min}$.
Khoảng cách lớn nhất từ $I$ đến mặt cầu là $\max = IJ + R = {d_max}$.
=> GTNN $m = {int(m_val)}$, GTLN $M' = {int(M_val)}$.
Với toạ độ 2 điểm cực trị: điểm đạt GTNN là $({M_min_pt[0]:.1f}; {M_min_pt[1]:.1f}; {M_min_pt[2]:.1f})$ và GTLN là $({M_max_pt[0]:.1f}; {M_max_pt[1]:.1f}; {M_max_pt[2]:.1f})$.
Từ đó ta tính được $S = {expr_str_display} = {true_val:.1f}$.'''
    return stmt, is_true, loigiai

def generate_questions(idx=1):
    prob_type = 2

    params = generate_base_params()
    K, ka, kb, kc, I, A, B, C, C0 = params
    
    A_str = f"{A[0]}; {A[1]}; {A[2]}"
    B_str = f"{B[0]}; {B[1]}; {B[2]}"
    C_str = f"{C[0]}; {C[1]}; {C[2]}"
    
    if prob_type == 1:
        P_expr = rf"\left| {format_vector_sum(ka, kb, kc)} \right|"
        type_str = "Dạng 1: Cực trị tổng độ dài vector (Bậc 1)"
    else:
        parts = []
        if ka == 1: parts.append("MA^2")
        elif ka == -1: parts.append("- MA^2")
        else: parts.append(f"{ka} MA^2")
        
        if kb == 1: parts.append("+ MB^2")
        elif kb == -1: parts.append("- MB^2")
        elif kb > 0: parts.append(f"+ {kb} MB^2")
        else: parts.append(f"- {abs(kb)} MB^2")
        
        if kc == 1: parts.append("+ MC^2")
        elif kc == -1: parts.append("- MC^2")
        elif kc > 0: parts.append(f"+ {kc} MC^2")
        else: parts.append(f"- {abs(kc)} MC^2")
        
        P_expr = " ".join(parts)
        if P_expr.startswith("+ "): P_expr = P_expr[2:]
        type_str = "Dạng 2: Cực trị tổng bình phương khoảng cách (Bậc 2)"
        
    stem = rf"Trong không gian $Oxyz$, cho biểu thức $P = {P_expr}$ với $A({A_str})$, $B({B_str})$, $C({C_str})$. Xét các bài toán cực trị khoảng cách sau:"
    
    s_a, t_a, l_a = generate_menh_de_a(prob_type, params)
    s_b, t_b, l_b = generate_menh_de_b(prob_type, params)
    s_c, t_c, l_c = generate_menh_de_c_d(prob_type, params, is_inside=False)
    s_d, t_d, l_d = generate_menh_de_c_d(prob_type, params, is_inside=True)
    
    def truth_str(t): return "đúng" if t else "sai"
    conclusion = f"Vậy a) {truth_str(t_a)}; b) {truth_str(t_b)}; c) {truth_str(t_c)} và d) {truth_str(t_d)}."
        
    question = f"""{stem}

{s_a}

{s_b}

{s_c}

{s_d}"""

    solution = f"""({type_str})
{l_a}

{l_b}

{l_c}

{l_d}

{conclusion}"""
    
    content = f"\\begin{{ex}}%Câu {idx}\n{question}\n\n\\loigiai{{\n{solution}\n}}\n\\end{{ex}}\n\n"
    
    return content

def main():
    num_questions = 1
    
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    content = ""
    for i in range(num_questions):
        content += generate_questions(i + 1)
    
    tex_content = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage{{amsmath,amssymb,fancyhdr}}
\\usepackage{{polyglossia}}
\\setdefaultlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{{geometry}}
\\usepackage[solcolor]{{ex_test}}
\\begin{{document}}
{content}
\\end{{document}}
"""

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "vector_extreme_2_tf_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)
    
    print(f"Đã tạo {num_questions} câu hỏi Dạng 2 và lưu: {output_file}")

if __name__ == "__main__":
    main()
