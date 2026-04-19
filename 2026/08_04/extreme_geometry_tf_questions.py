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

# --- Bộ vector đẹp mở rộng ---
NICE_VECTOR_BASES = [
    (2, 3, 6), (1, 4, 8), (2, 6, 9), (3, 4, 12), (6, 10, 15),
    (1, 2, 2), (2, 2, 1), (3, 6, 2), (4, 4, 7), (1, 6, 8),
    (3, 6, 6), (2, 4, 4), (1, 3, 3), (5, 10, 10), (2, 1, 2),
]

def get_nice_vector():
    base = random.choice(NICE_VECTOR_BASES)
    perm = list(base)
    random.shuffle(perm)
    return tuple(p * random.choice([1, -1]) for p in perm)

# --- Random labels ---
PLANE_NAMES = ['P', 'Q', 'R', '\\alpha', '\\beta', '\\gamma', '\\pi']
MIN_LABELS = ['m', 'k', 'p', 'd', 'l', 's']

# Bộ nhãn toạ độ (3 biến cho mỗi điểm, KHÁC NHAU giữa các điểm)
COORD_LABEL_SETS = [
    # (M_labels, N_labels, A_labels)
    (('A', 'B', 'C'), ('X', 'Y', 'Z'), ('I', 'J', 'K')),
    (('a', 'b', 'c'), ('u', 'v', 'w'), ('p', 'q', 'r')),
    (('P', 'Q', 'R'), ('D', 'E', 'F'), ('U', 'V', 'W')),
    (('m_1', 'm_2', 'm_3'), ('n_1', 'n_2', 'n_3'), ('a_1', 'a_2', 'a_3')),
    (('\\alpha', '\\beta', '\\gamma'), ('X', 'Y', 'Z'), ('I', 'J', 'K')),
    (('A', 'B', 'C'), ('D', 'E', 'F'), ('G', 'H', 'K')),
]

PT_NAME_SETS_AB = [
    ('A', 'B'), ('P', 'Q'), ('E', 'F'), ('H', 'K'), ('C', 'D'),
]

def get_random_labels_cd():
    """Trả về (plane_name, min_label, M_labels, N_labels, A_labels)"""
    plane = random.choice(PLANE_NAMES)
    min_lbl = random.choice(MIN_LABELS)
    coord_set = random.choice(COORD_LABEL_SETS)
    return plane, min_lbl, coord_set[0], coord_set[1], coord_set[2]

def get_random_labels_ab():
    """Trả về (plane_name, min_label, M_labels, pt_names)"""
    plane = random.choice(PLANE_NAMES)
    min_lbl = random.choice(MIN_LABELS)
    pts = random.choice(PT_NAME_SETS_AB)
    m_labels = random.choice([('x_M', 'y_M', 'z_M'),
                               ('A', 'B', 'C'),
                               ('a', 'b', 'c'),
                               ('P', 'Q', 'R'),
                               ('u', 'v', 'w')])
    return plane, min_lbl, m_labels, pts

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
    return " ".join(terms) + " = 0"

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

def f_plane(pt, n, D):
    return n[0]*pt[0] + n[1]*pt[1] + n[2]*pt[2] + D

def reflect_pt(pt, n, D, n_sq):
    f_val = f_plane(pt, n, D)
    return (
        pt[0] - 2 * f_val * n[0] / n_sq,
        pt[1] - 2 * f_val * n[1] / n_sq,
        pt[2] - 2 * f_val * n[2] / n_sq
    )

def generate_menh_de_a():
    plane_name, min_lbl, m_labels, pt_names = get_random_labels_ab()
    ptA_name, ptB_name = pt_names
    
    while True:
        n = get_nice_vector()
        v = get_nice_vector()
        cross = (n[1]*v[2] - n[2]*v[1], n[2]*v[0] - n[0]*v[2], n[0]*v[1] - n[1]*v[0])
        if cross != (0,0,0):
            dot_nv = sum(x*y for x,y in zip(n,v))
            if dot_nv != 0: break
    
    k1 = random.randint(1, 4)
    k2 = random.randint(1, 4)
    A0 = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
    
    A1 = (A0[0] - k1*v[0], A0[1] - k1*v[1], A0[2] - k1*v[2])
    B1 = (A0[0] + k2*v[0], A0[1] + k2*v[1], A0[2] + k2*v[2])
    D = -sum(n[i]*A0[i] for i in range(3))
    
    m_val = (k1 + k2) * math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    vars_dict = {m_labels[0]: A0[0], m_labels[1]: A0[1], m_labels[2]: A0[2], min_lbl: m_val}
    expr_str, val = make_linear_expr(vars_dict)
    
    is_true = random.choice([True, False])
    if not is_true: val += random.choice([-2, -1, 1, 2])
    disp_val = f"{val:.1f}".replace(".", ",")
    
    P_eq = format_plane(n[0], n[1], n[2], D)
    A_str = f"{A1[0]}; {A1[1]}; {A1[2]}"
    B_str = f"{B1[0]}; {B1[1]}; {B1[2]}"
    
    prefix = "*a) " if is_true else "a) "
    stmt = rf'''{prefix}Cho mặt phẳng $({plane_name}): {P_eq}$, điểm ${ptA_name}({A_str})$ và ${ptB_name}({B_str})$. Gọi $M$ là điểm bất kì nằm trên mặt phẳng $({plane_name})$. Khi điểm $M$ có toạ độ $({m_labels[0]}; {m_labels[1]}; {m_labels[2]})$ thì $T = M{ptA_name} + M{ptB_name}$ đạt giá trị nhỏ nhất là ${min_lbl}$. Tính ${expr_str}$ (làm tròn đến hàng phần mười).'''
    
    loigiai = rf'''a) Đặt $f(x, y, z) = {n[0]}x + {n[1]}y + {n[2]}z + {D}$.
Ta có $f({ptA_name}) \cdot f({ptB_name}) = ({-k1 * dot_nv}) \cdot ({k2 * dot_nv}) < 0$. Suy ra ${ptA_name}, {ptB_name}$ nằm khác phía đối với $({plane_name})$.
$T = M{ptA_name} + M{ptB_name} \ge {ptA_name}{ptB_name}$. Dấu bằng xảy ra khi $M = {ptA_name}{ptB_name} \cap ({plane_name})$.
Phương trình tham số đường thẳng ${ptA_name}{ptB_name}$ qua ${ptA_name}$ có véctơ chỉ phương $\overrightarrow{{{ptA_name}{ptB_name}}} \parallel \vec{{v}} = ({v[0]}; {v[1]}; {v[2]})$ là:
$$ \begin{{cases}} x = {A1[0]} + {v[0]}t \\ y = {A1[1]} + {v[1]}t \\ z = {A1[2]} + {v[2]}t \end{{cases}} $$
Thay vào phương trình $({plane_name})$ ta tìm được $t = {k1}$, suy ra toạ độ $M({A0[0]}; {A0[1]}; {A0[2]})$.
Khi đó ${min_lbl} = {ptA_name}{ptB_name} = {int(m_val)}$.
Tính ${expr_str} \approx {val:.1f}$.
Mệnh đề này là {"ĐÚNG" if is_true else "SAI"}.'''
    return stmt, is_true, loigiai

def generate_menh_de_b():
    plane_name, min_lbl, m_labels, pt_names = get_random_labels_ab()
    ptA_name, ptB_name = pt_names
    
    while True:
        n = get_nice_vector()
        v = get_nice_vector()
        cross = (n[1]*v[2] - n[2]*v[1], n[2]*v[0] - n[0]*v[2], n[0]*v[1] - n[1]*v[0])
        if cross != (0,0,0):
            dot_nv = sum(x*y for x,y in zip(n,v))
            if dot_nv != 0:
                n_sq = sum(x*x for x in n)
                req = n_sq // math.gcd(2 * abs(dot_nv), n_sq)
                if req <= 15:
                    k1 = req * random.randint(1, 2)
                    break
                    
    k2 = random.randint(1, 4)
    A0 = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
    D = -sum(n[i]*A0[i] for i in range(3))
    n_sq = sum(x*x for x in n)
    
    A_prime = (A0[0] - k1*v[0], A0[1] - k1*v[1], A0[2] - k1*v[2])
    B1 = (A0[0] + k2*v[0], A0[1] + k2*v[1], A0[2] + k2*v[2])
    
    A1 = (
        int(A_prime[0] - 2 * f_plane(A_prime, n, D) * n[0] / n_sq),
        int(A_prime[1] - 2 * f_plane(A_prime, n, D) * n[1] / n_sq),
        int(A_prime[2] - 2 * f_plane(A_prime, n, D) * n[2] / n_sq)
    )
    
    m_val = (k1 + k2) * math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    vars_dict = {m_labels[0]: A0[0], m_labels[1]: A0[1], m_labels[2]: A0[2], min_lbl: m_val}
    expr_str, val = make_linear_expr(vars_dict)
    
    is_true = random.choice([True, False])
    if not is_true: val += random.choice([-2, -1, 1, 2])
    disp_val = f"{val:.1f}".replace(".", ",")
    
    P_eq = format_plane(n[0], n[1], n[2], D)
    A_str = f"{A1[0]}; {A1[1]}; {A1[2]}"
    B_str = f"{B1[0]}; {B1[1]}; {B1[2]}"
    
    prefix = "*b) " if is_true else "b) "
    stmt = rf'''{prefix}Cho mặt phẳng $({plane_name}): {P_eq}$, điểm ${ptA_name}({A_str})$ và ${ptB_name}({B_str})$. Gọi $M$ là điểm bất kì nằm trên mặt phẳng $({plane_name})$. Khi điểm $M$ có toạ độ $({m_labels[0]}; {m_labels[1]}; {m_labels[2]})$ thì $T = M{ptA_name} + M{ptB_name}$ đạt giá trị nhỏ nhất là ${min_lbl}$. Tính ${expr_str}$ (làm tròn đến hàng phần mười).'''

    loigiai = rf'''b) Đặt $f(x, y, z) = {n[0]}x + {n[1]}y + {n[2]}z + {D}$.
Tính thấy $f({ptA_name}) \cdot f({ptB_name}) > 0$. Suy ra ${ptA_name}, {ptB_name}$ cùng phía đối với $({plane_name})$.
Lấy ${ptA_name}'$ đối xứng với ${ptA_name}$ qua $({plane_name})$, tìm được ${ptA_name}'({A_prime[0]}; {A_prime[1]}; {A_prime[2]})$.
Ta có $T = M{ptA_name} + M{ptB_name} = M{ptA_name}' + M{ptB_name} \ge {ptA_name}'{ptB_name}$. Dấu bằng khi $M = {ptA_name}'{ptB_name} \cap ({plane_name})$.
Tương tự mệnh đề trước, đường thẳng ${ptA_name}'{ptB_name}$ giao $({plane_name})$ tại điểm $M({A0[0]}; {A0[1]}; {A0[2]})$.
Và có ${min_lbl} = {ptA_name}'{ptB_name} = {int(m_val)}$.
Tính ${expr_str} \approx {val:.1f}$.
Mệnh đề này là {"ĐÚNG" if is_true else "SAI"}.'''
    return stmt, is_true, loigiai

def generate_menh_de_c():
    plane_name, min_lbl, M_labels, N_labels, A_labels = get_random_labels_cd()
    
    while True:
        n = get_nice_vector()
        v = get_nice_vector()
        cross = (n[1]*v[2] - n[2]*v[1], n[2]*v[0] - n[0]*v[2], n[0]*v[1] - n[1]*v[0])
        if cross != (0,0,0):
            dot_nv = sum(x*y for x,y in zip(n,v))
            if dot_nv != 0: break
            
    A0 = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
    D = -sum(n[i]*A0[i] for i in range(3))
    n_mag = math.sqrt(sum(x*x for x in n))
    
    while True:
        k1 = random.randint(2, 8)
        k2 = random.randint(2, 8)
        I1 = (A0[0] - k1*v[0], A0[1] - k1*v[1], A0[2] - k1*v[2])
        I2 = (A0[0] + k2*v[0], A0[1] + k2*v[1], A0[2] + k2*v[2])
        d1 = abs(f_plane(I1, n, D)) / n_mag
        d2 = abs(f_plane(I2, n, D)) / n_mag
        if d1 > 2.001 and d2 > 2.001:
            R1 = random.randint(1, max(1, int(d1 - 0.001)))
            R2 = random.randint(1, max(1, int(d2 - 0.001)))
            break
            
    v_mag = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    # Tính điểm M trên (S1) gần (P) nhất theo hướng v
    u = (v[0]/v_mag, v[1]/v_mag, v[2]/v_mag)
    M_min = (I1[0] + R1 * u[0], I1[1] + R1 * u[1], I1[2] + R1 * u[2])
    # Tính điểm N trên (S2) gần (P) nhất theo hướng -v
    N_min = (I2[0] - R2 * u[0], I2[1] - R2 * u[1], I2[2] - R2 * u[2])
    
    m_val = (k1 + k2) * v_mag - R1 - R2
    
    vars_dict = {
        M_labels[0]: M_min[0], M_labels[1]: M_min[1], M_labels[2]: M_min[2],
        N_labels[0]: N_min[0], N_labels[1]: N_min[1], N_labels[2]: N_min[2],
        A_labels[0]: A0[0], A_labels[1]: A0[1], A_labels[2]: A0[2],
        min_lbl: m_val
    }
    expr_str, val = make_linear_expr(vars_dict)
    
    is_true = random.choice([True, False])
    if not is_true: val += random.choice([-2, -1, 1, 2])
    disp_val = f"{val:.1f}".replace(".", ",")
    
    S1_eq = format_sphere(I1[0], I1[1], I1[2], R1)
    S2_eq = format_sphere(I2[0], I2[1], I2[2], R2)
    P_eq = format_plane(n[0], n[1], n[2], D)
    
    prefix = "*c) " if is_true else "c) "
    stmt = rf'''{prefix}Cho $M$ thuộc mặt cầu $(S_1): {S1_eq}$ và $N$ thuộc mặt cầu $(S_2): {S2_eq}$ và điểm $A$ thuộc mặt phẳng $({plane_name}): {P_eq}$. Khi điểm $M$ có toạ độ $({M_labels[0]},{M_labels[1]},{M_labels[2]})$, điểm $N$ có toạ độ $({N_labels[0]},{N_labels[1]},{N_labels[2]})$ và $A$ có toạ độ $({A_labels[0]};{A_labels[1]};{A_labels[2]})$ thì $T = MA + NA$ đạt giá trị nhỏ nhất là ${min_lbl}$. Tính ${expr_str}$ (làm tròn đến hàng phần mười).'''
    
    loigiai = rf'''c) Mặt cầu $(S_1)$ có tâm $I_1({I1[0]}; {I1[1]}; {I1[2]})$ và bán kính $R_1={R1}$.
Mặt cầu $(S_2)$ có tâm $I_2({I2[0]}; {I2[1]}; {I2[2]})$ và bán kính $R_2={R2}$.
Khoảng cách $d(I_1, ({plane_name})) > R_1$ và $d(I_2, ({plane_name})) > R_2$. Đồng thời 2 tâm nằm khác phía đối với $({plane_name})$ do $f(I_1) \cdot f(I_2) < 0$. Do đó $(S_1), (S_2)$ cùng nằm khác phía và không cắt $({plane_name})$.
Độ dài nhỏ nhất ${min_lbl} = T_{{min}} = I_1 I_2 - R_1 - R_2 = {int(m_val)}$ (các điểm thẳng hàng: $I_1 - M - A - N - I_2$). 
Điểm $M$ đạt $T_{{min}}$ tại toạ độ $({M_labels[0]}; {M_labels[1]}; {M_labels[2]})$ là $({M_min[0]:.1f}; {M_min[1]:.1f}; {M_min[2]:.1f})$.
Điểm $N$ đạt $T_{{min}}$ tại toạ độ $({N_labels[0]}; {N_labels[1]}; {N_labels[2]})$ là $({N_min[0]:.1f}; {N_min[1]:.1f}; {N_min[2]:.1f})$.
$A = I_1I_2 \cap ({plane_name})$ là $A({A0[0]}; {A0[1]}; {A0[2]})$.
Tính ${expr_str} \approx {val:.1f}$.
Mệnh đề này là {"ĐÚNG" if is_true else "SAI"}.'''
    return stmt, is_true, loigiai

def generate_menh_de_d():
    plane_name, min_lbl, M_labels, N_labels, A_labels = get_random_labels_cd()
    
    while True:
        n = get_nice_vector()
        v = get_nice_vector()
        cross = (n[1]*v[2] - n[2]*v[1], n[2]*v[0] - n[0]*v[2], n[0]*v[1] - n[1]*v[0])
        if cross != (0,0,0):
            dot_nv = sum(x*y for x,y in zip(n,v))
            if dot_nv != 0:
                n_sq = sum(x*x for x in n)
                req = n_sq // math.gcd(2 * abs(dot_nv), n_sq)
                if req <= 15:
                    k2 = req * random.randint(1, 2)
                    break
                    
    A0 = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
    D = -sum(n[i]*A0[i] for i in range(3))
    n_mag = math.sqrt(sum(x*x for x in n))
    
    while True:
        k1 = random.randint(2, 8)
        I1 = (A0[0] - k1*v[0], A0[1] - k1*v[1], A0[2] - k1*v[2])
        I2_prime = (A0[0] + k2*v[0], A0[1] + k2*v[1], A0[2] + k2*v[2])
        
        f_I2p = f_plane(I2_prime, n, D)
        I2 = (
            int(I2_prime[0] - 2 * f_I2p * n[0] / n_sq),
            int(I2_prime[1] - 2 * f_I2p * n[1] / n_sq),
            int(I2_prime[2] - 2 * f_I2p * n[2] / n_sq)
        )
        
        d1 = abs(f_plane(I1, n, D)) / n_mag
        d2 = abs(f_plane(I2, n, D)) / n_mag
        if d1 > 2.001 and d2 > 2.001:
            R1 = random.randint(1, max(1, int(d1 - 0.001)))
            R2 = random.randint(1, max(1, int(d2 - 0.001)))
            break
            
    v_mag = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    u = (v[0]/v_mag, v[1]/v_mag, v[2]/v_mag)
    
    M_min = (I1[0] + R1 * u[0], I1[1] + R1 * u[1], I1[2] + R1 * u[2])
    # N_min trên (S2') — phản xạ qua (P) để lấy N thực tế trên (S2)
    N_min_prime = (I2_prime[0] - R2 * u[0], I2_prime[1] - R2 * u[1], I2_prime[2] - R2 * u[2])
    N_min = reflect_pt(N_min_prime, n, D, n_sq)
    
    m_val = (k1 + k2) * v_mag - R1 - R2
    
    vars_dict = {
        M_labels[0]: M_min[0], M_labels[1]: M_min[1], M_labels[2]: M_min[2],
        N_labels[0]: N_min[0], N_labels[1]: N_min[1], N_labels[2]: N_min[2],
        A_labels[0]: A0[0], A_labels[1]: A0[1], A_labels[2]: A0[2],
        min_lbl: m_val
    }
    expr_str, val = make_linear_expr(vars_dict)
    
    is_true = random.choice([True, False])
    if not is_true: val += random.choice([-2, -1, 1, 2])
    disp_val = f"{val:.1f}".replace(".", ",")
    
    S1_eq = format_sphere(I1[0], I1[1], I1[2], R1)
    S2_eq = format_sphere(I2[0], I2[1], I2[2], R2)
    P_eq = format_plane(n[0], n[1], n[2], D)
    
    prefix = "*d) " if is_true else "d) "
    stmt = rf'''{prefix}Cho $M$ thuộc mặt cầu $(S_1): {S1_eq}$ và $N$ thuộc mặt cầu $(S_2): {S2_eq}$ và điểm $A$ thuộc mặt phẳng $({plane_name}): {P_eq}$. Khi điểm $M$ có toạ độ $({M_labels[0]},{M_labels[1]},{M_labels[2]})$, điểm $N$ có toạ độ $({N_labels[0]},{N_labels[1]},{N_labels[2]})$ và $A$ có toạ độ $({A_labels[0]};{A_labels[1]};{A_labels[2]})$ thì $T = MA + NA$ đạt giá trị nhỏ nhất là ${min_lbl}$. Tính ${expr_str}$ (làm tròn đến hàng phần mười).'''
    
    loigiai = rf'''d) Mặt cầu $(S_1)$ tâm $I_1({I1[0]}; {I1[1]}; {I1[2]})$, $(S_2)$ tâm $I_2({I2[0]}; {I2[1]}; {I2[2]})$.
Ta thấy $f(I_1) \cdot f(I_2) > 0$, chứng tỏ $(S_1), (S_2)$ nằm CÙNG PHÍA đối với $({plane_name})$.
Gọi $(S_2')$ là mặt cầu đối xứng với $(S_2)$ qua $({plane_name})$. Tâm $I_2'$ đối xứng của $I_2$ qua $({plane_name})$ có toạ độ $({I2_prime[0]}; {I2_prime[1]}; {I2_prime[2]})$.
Khi đó $T = MA + NA = MA + N'A$ (với $N' \in (S_2')$ đối xứng với $N$).
Tương tự mệnh đề trước, khoảng cách nhỏ nhất ${min_lbl} = T_{{min}} = I_1 I'_2 - R_1 - R_2 = {int(m_val)}$.
Điểm $M$ đạt GTNN là $M_{{min}}({M_min[0]:.1f}; {M_min[1]:.1f}; {M_min[2]:.1f})$.
Điểm $N$ đạt GTNN tại $({N_min[0]:.1f}; {N_min[1]:.1f}; {N_min[2]:.1f})$ (phản xạ $N'$ qua $({plane_name})$).
$A = I_1I'_2 \cap ({plane_name})$ có toạ độ $A({A0[0]}; {A0[1]}; {A0[2]})$.
Tính ${expr_str} \approx {val:.1f}$.
Mệnh đề này là {"ĐÚNG" if is_true else "SAI"}.'''
    return stmt, is_true, loigiai

def generate_questions(seed_val=None, idx=1):
    if seed_val is not None:
        random.seed(seed_val)
        
    s_a, t_a, l_a = generate_menh_de_a()
    s_b, t_b, l_b = generate_menh_de_b()
    s_c, t_c, l_c = generate_menh_de_c()
    s_d, t_d, l_d = generate_menh_de_d()
    
    stem = "Trong không gian $Oxyz$, xét các bài toán cực trị khoảng cách sau:"
    
    def truth_str(t): return "đúng" if t else "sai"
    conclusion = f"Vậy a) {truth_str(t_a)}; b) {truth_str(t_b)}; c) {truth_str(t_c)} và d) {truth_str(t_d)}."
        
    question = f"""{stem}

{s_a}

{s_b}

{s_c}

{s_d}"""

    solution = f"""{l_a}

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
        
    seed = None
    if len(sys.argv) > 2:
        seed = int(sys.argv[2])
        
    content = ""
    for i in range(num_questions):
        seed_iter = seed + i if seed is not None else None
        content += generate_questions(seed_iter, i + 1)
    
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
    output_file = os.path.join(out_dir, "extreme_geometry_tf_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)
    
    print(f"Đã tạo {num_questions} câu hỏi và lưu: {output_file}")

if __name__ == "__main__":
    main()
