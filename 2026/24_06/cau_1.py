"""
Câu 1: Hình hộp chữ nhật - Vector, khoảng cách, góc (Đúng/Sai)
---------------------------------------------------------------
Cho hình hộp chữ nhật ABCD.A'B'C'D' với AB=a, AD=b, AA'=c.
Trên BC' lấy điểm E sao cho k*BC' = m*BE, lấy điểm F là trọng tâm ΔD'AE.
Xét 4 mệnh đề:
  a) Biểu diễn vec A'F qua BA, BC, BB' (có đảo véc tơ → bẫy)
  b) Khoảng cách d(C; (AEF)) ≈ ? (có đảo điểm và mặt phẳng)
  c) Góc (CF, AE) ≈ ?° (có đảo điểm)
  d) Khoảng cách d(D'; đường thẳng ED) ≈ ?
"""

import math
import os
import random
import sys
from fractions import Fraction
from typing import Tuple

# ---------------------------------------------------------------------------
# Parameter sets: (AB, AD, AA_prime, k, m)
# Constraint: m > k > 0 (so BE = k/m * BC'), nice numbers for computation
# We ensure the final answers are "nice" (clean decimals / small fractions)
# Format: (a, b, c, k, m) where E on BC': BE = (k/m)*BC'
# ---------------------------------------------------------------------------
PARAM_SETS = [
    # (AB, AD, AA', k_num, k_den) where BE/BC' = k_num/k_den
    (4, 4, 6, 2, 5),
    (3, 4, 6, 1, 3),
    (4, 3, 6, 2, 5),
    (3, 3, 6, 1, 3),
    (4, 4, 8, 2, 5),
    (3, 4, 8, 1, 4),
    (4, 3, 8, 1, 3),
    (6, 4, 6, 2, 5),
    (4, 6, 6, 1, 3),
    (6, 3, 6, 2, 5),
    (3, 6, 6, 1, 4),
    (4, 4, 10, 2, 5),
    (6, 6, 6, 2, 5),
    (6, 4, 8, 1, 3),
    (4, 6, 8, 2, 5),
    (5, 4, 6, 2, 5),
    (4, 5, 6, 1, 3),
    (5, 3, 6, 1, 3),
    (3, 5, 6, 2, 5),
    (6, 5, 6, 1, 4),
    (5, 6, 8, 2, 5),
    (6, 6, 8, 1, 3),
    (5, 5, 6, 2, 5),
    (5, 5, 8, 1, 4),
    (4, 4, 12, 1, 4),
    (6, 4, 10, 2, 5),
    (4, 6, 10, 1, 3),
    (3, 4, 10, 2, 5),
    (4, 3, 10, 1, 4),
    (6, 3, 8, 1, 3),
    (3, 6, 8, 2, 5),
    (5, 4, 8, 1, 3),
    (4, 5, 8, 2, 5),
    (6, 5, 8, 1, 4),
    (5, 6, 6, 1, 3),
    (6, 6, 10, 2, 5),
    (5, 5, 10, 1, 3),
    (8, 4, 6, 2, 5),
    (4, 8, 6, 1, 3),
    (8, 6, 6, 2, 5),
    (6, 8, 6, 1, 4),
    (8, 4, 8, 1, 3),
    (4, 8, 8, 2, 5),
    (8, 3, 6, 1, 3),
    (3, 8, 6, 2, 5),
    (8, 6, 8, 1, 4),
    (6, 8, 8, 2, 5),
    (8, 8, 6, 1, 3),
    (8, 8, 8, 2, 5),
    (10, 4, 6, 2, 5),
    (4, 10, 6, 1, 3),
    (10, 6, 6, 2, 5),
    (6, 10, 6, 1, 4),
    (10, 4, 8, 1, 3),
    (10, 6, 8, 2, 5),
    (8, 5, 6, 1, 3),
    (5, 8, 6, 2, 5),
    (10, 3, 6, 1, 4),
    (3, 10, 6, 2, 5),
    (10, 5, 8, 1, 3),
]


def vec_add(u, v):
    return (u[0]+v[0], u[1]+v[1], u[2]+v[2])

def vec_sub(u, v):
    return (u[0]-v[0], u[1]-v[1], u[2]-v[2])

def vec_scale(s, v):
    return (s*v[0], s*v[1], s*v[2])

def dot(u, v):
    return u[0]*v[0] + u[1]*v[1] + u[2]*v[2]

def cross(u, v):
    return (
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0]
    )

def norm(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def fmt_frac(num, den):
    """Return LaTeX fraction string, simplified."""
    f = Fraction(num, den)
    if f.denominator == 1:
        return str(f.numerator)
    sign = "-" if f < 0 else ""
    return rf"{sign}\dfrac{{{abs(f.numerator)}}}{{{f.denominator}}}"

def fmt_coeff(num, den, vec_name, first=False):
    """Format a vector coefficient term for LaTeX output."""
    f = Fraction(num, den)
    if f == 0:
        return ""
    
    abs_f = abs(f)
    if first:
        sign_str = "-" if f < 0 else ""
    else:
        sign_str = "-" if f < 0 else "+"

    if abs_f == 1:
        coeff_str = ""
    elif abs_f.denominator == 1:
        coeff_str = str(abs_f.numerator)
    else:
        coeff_str = rf"\dfrac{{{abs_f.numerator}}}{{{abs_f.denominator}}}"
        
    return rf"{sign_str}{coeff_str}\overrightarrow{{{vec_name}}}"


def build_vec_expr(coeffs_list, vec_names_list):
    """Build LaTeX vector expression, correctly handling zero coefficients."""
    parts = []
    for coeff, vname in zip(coeffs_list, vec_names_list):
        is_first = (len(parts) == 0)
        term = fmt_coeff(coeff.numerator, coeff.denominator, vname, first=is_first)
        if term:
            parts.append(term)
    return "".join(parts) if parts else r"\vec{0}"


def generate_question(seed=None) -> Tuple[str, str, str]:
    if seed is not None:
        random.seed(seed)

    # Randomize dimensions
    a = random.randint(2, 10)
    b = random.randint(2, 10)
    c = random.randint(2, 10)

    # Coordinates: A at origin
    pts_exact = {
        'A': (Fraction(0), Fraction(0), Fraction(0)),
        'B': (Fraction(a), Fraction(0), Fraction(0)),
        'C': (Fraction(a), Fraction(b), Fraction(0)),
        'D': (Fraction(0), Fraction(b), Fraction(0)),
        "A'": (Fraction(0), Fraction(0), Fraction(c)),
        "B'": (Fraction(a), Fraction(0), Fraction(c)),
        "C'": (Fraction(a), Fraction(b), Fraction(c)),
        "D'": (Fraction(0), Fraction(b), Fraction(c))
    }
    vertices = list(pts_exact.keys())

    # Randomize segment for E: E on P1_E P2_E
    P1_E, P2_E = random.sample(vertices, 2)
    k_num = random.randint(1, 4)
    k_den = k_num + random.randint(1, 4)  # Ensure k_num < k_den so E is strictly between
    ratio = Fraction(k_num, k_den)
    
    P1_ex = pts_exact[P1_E]
    P2_ex = pts_exact[P2_E]
    
    Ex = P1_ex[0] + ratio * (P2_ex[0] - P1_ex[0])
    Ey = P1_ex[1] + ratio * (P2_ex[1] - P1_ex[1])
    Ez = P1_ex[2] + ratio * (P2_ex[2] - P1_ex[2])
    pts_exact['E'] = (Ex, Ey, Ez)
    
    # Randomize triangle for F: F is centroid of T1 T2 T3
    F_pts = random.sample(vertices + ['E'], 3)
    T1, T2, T3 = F_pts
    Fx = (pts_exact[T1][0] + pts_exact[T2][0] + pts_exact[T3][0]) / Fraction(3)
    Fy = (pts_exact[T1][1] + pts_exact[T2][1] + pts_exact[T3][1]) / Fraction(3)
    Fz = (pts_exact[T1][2] + pts_exact[T2][2] + pts_exact[T3][2]) / Fraction(3)
    pts_exact['F'] = (Fx, Fy, Fz)

    # --- Statement a: Express a random vector in a random basis ---
    all_pts = list(pts_exact.keys())
    
    # Select basis: A root vertex and its 3 neighbors
    root_vertex_options = {
        'A': ['B', 'D', "A'"],
        'B': ['A', 'C', "B'"],
        'C': ['B', 'D', "C'"],
        'D': ['A', 'C', "D'"],
        "A'": ["B'", "D'", 'A'],
        "B'": ["A'", "C'", 'B'],
        "C'": ["B'", "D'", 'C'],
        "D'": ["A'", "C'", 'D']
    }
    
    best_pair = None
    best_score = -1
    best_root = None
    best_coeffs = None
    
    for r_opt, neighbors_opt in root_vertex_options.items():
        for start in all_pts:
            for end in all_pts:
                if start == end: continue
                target_vec_opt = vec_sub(pts_exact[end], pts_exact[start])
                c_opt = []
                for n_opt in neighbors_opt:
                    u_opt = vec_sub(pts_exact[n_opt], pts_exact[r_opt])
                    dot_val = target_vec_opt[0]*u_opt[0] + target_vec_opt[1]*u_opt[1] + target_vec_opt[2]*u_opt[2]
                    norm_sq = u_opt[0]**2 + u_opt[1]**2 + u_opt[2]**2
                    c_opt.append(dot_val / norm_sq)
                
                score = sum(1 for c in c_opt if abs(c) not in (0, 1))
                if start in ['E', 'F'] or end in ['E', 'F']:
                    score += 0.5
                
                if score > best_score:
                    best_score = score
                    best_pair = (start, end)
                    best_root = r_opt
                    best_coeffs = c_opt
                    
    target_start, target_end = best_pair
    root = best_root
    neighbors = root_vertex_options[root]
    target_vec = vec_sub(pts_exact[target_end], pts_exact[target_start])
    alpha, beta, gamma = best_coeffs

    stmt_a_correct = random.choice([True, False])
    vec_names = [f"{root}{n}" for n in neighbors]
    
    a_alpha, a_beta, a_gamma = alpha, beta, gamma
    if not stmt_a_correct:
        # Generate random fractional coefficients to ensure they are strictly not 0 or 1
        wrong_pool = [Fraction(1,2), Fraction(-1,2), Fraction(1,3), Fraction(-1,3), 
                      Fraction(2,3), Fraction(-2,3), Fraction(3,4), Fraction(-3,4), 
                      Fraction(1,4), Fraction(-1,4), Fraction(1,5), Fraction(-1,5)]
        a_alpha = random.choice(wrong_pool)
        a_beta = random.choice(wrong_pool)
        a_gamma = random.choice(wrong_pool)
        while (a_alpha, a_beta, a_gamma) == (alpha, beta, gamma):
            a_gamma = random.choice(wrong_pool)

    def cross_frac(u, v):
        return (
            u[1]*v[2] - u[2]*v[1],
            u[2]*v[0] - u[0]*v[2],
            u[0]*v[1] - u[1]*v[0]
        )

    # --- Statement b: distance from pt_b to plane (plane_b_pt E F) ---
    while True:
        pt_b = random.choice(all_pts)
        plane_b_pt = random.choice([v for v in all_pts if v not in (pt_b, 'E', 'F')])
        P1_ex_plane = pts_exact[plane_b_pt]
        vec_P1E_ex = vec_sub(pts_exact['E'], P1_ex_plane)
        vec_P1F_ex = vec_sub(pts_exact['F'], P1_ex_plane)
        n_b_ex = cross_frac(vec_P1E_ex, vec_P1F_ex)
        n_b_norm_sq = float(n_b_ex[0]**2 + n_b_ex[1]**2 + n_b_ex[2]**2)
        if n_b_norm_sq < 1e-9:
            continue  # E, F, plane_b_pt are collinear — plane not defined
        pt_b_ex = pts_exact[pt_b]
        n1, n2, n3 = n_b_ex
        P1_ex_plane_tmp = pts_exact[plane_b_pt]
        C_num_tmp = abs(n1*(pt_b_ex[0]-P1_ex_plane_tmp[0]) + n2*(pt_b_ex[1]-P1_ex_plane_tmp[1]) + n3*(pt_b_ex[2]-P1_ex_plane_tmp[2]))
        if float(C_num_tmp) > 1e-9:
            break  # pt_b is not on the plane, distance > 0

    n1, n2, n3 = n_b_ex
    pt_b_ex = pts_exact[pt_b]
    
    C_num = abs(n1 * (pt_b_ex[0] - P1_ex_plane[0]) + n2 * (pt_b_ex[1] - P1_ex_plane[1]) + n3 * (pt_b_ex[2] - P1_ex_plane[2]))
    C_den = math.sqrt(float(n1**2 + n2**2 + n3**2))
    d_C_AEF = float(C_num) / C_den

    b_correct = random.choice([True, False])
    d_C_AEF_rounded = round(d_C_AEF, 2)
    if b_correct:
        d_b_display = d_C_AEF_rounded
    else:
        d_b_display = round(d_C_AEF_rounded + random.choice([-0.5, 0.3, -0.3, 0.5, 0.7, -0.7, 1.0, -1.0]), 2)
        if d_b_display <= 0:
            d_b_display = d_C_AEF_rounded + 0.5
        d_b_display = round(d_b_display, 2)

    # --- Statement c: angle between vectors/lines (pt_c1 F) and (pt_c2 E) ---
    while True:
        pt_c1, pt_c2 = random.sample(all_pts, 2)
        if pt_c1 == 'F' or pt_c2 == 'E':
            continue
        vec_c1F = vec_sub(pts_exact['F'], pts_exact[pt_c1])
        vec_c2E = vec_sub(pts_exact['E'], pts_exact[pt_c2])
        vec_c1F_f = (float(vec_c1F[0]), float(vec_c1F[1]), float(vec_c1F[2]))
        vec_c2E_f = (float(vec_c2E[0]), float(vec_c2E[1]), float(vec_c2E[2]))
        if norm(vec_c1F_f) > 1e-9 and norm(vec_c2E_f) > 1e-9:
            break

    is_vector_angle = random.choice([True, False])

    cos_raw = dot(vec_c1F_f, vec_c2E_f) / (norm(vec_c1F_f) * norm(vec_c2E_f))
    cos_raw = max(-1.0, min(1.0, cos_raw))
    
    if is_vector_angle:
        angle_actual = math.degrees(math.acos(cos_raw))
    else:
        angle_actual = math.degrees(math.acos(abs(cos_raw)))
        
    angle_rounded = round(angle_actual, 1)

    c_correct = random.choice([True, False])
    if c_correct:
        angle_c_display = angle_rounded
    else:
        angle_c_display = round(angle_rounded + random.choice([-10, 10, -15, 15, 20, -20, -5, 5]), 1)
        if angle_c_display < 0:
            angle_c_display = abs(angle_c_display)
        if is_vector_angle and angle_c_display > 180:
            angle_c_display = 180 - (angle_c_display - 180)
        elif not is_vector_angle and angle_c_display > 90:
            angle_c_display = 90 - (angle_c_display - 90)

    # --- Statement d: d(pt_d; line E→target_line_pt), ensure distance > 0 ---
    while True:
        pt_d = random.choice(all_pts)
        target_line_pt = random.choice([v for v in all_pts if v != 'E'])
        if pt_d == 'E' or pt_d == target_line_pt:
            continue
        ED_ex = vec_sub(pts_exact[target_line_pt], pts_exact['E'])
        ED_float = (float(ED_ex[0]), float(ED_ex[1]), float(ED_ex[2]))
        if norm(ED_float) < 1e-9:
            continue  # E == target_line_pt
        vec_E_pt_d = vec_sub(pts_exact[pt_d], pts_exact['E'])
        vec_E_pt_d_float = (float(vec_E_pt_d[0]), float(vec_E_pt_d[1]), float(vec_E_pt_d[2]))
        cross_vecs = cross(vec_E_pt_d_float, ED_float)
        d_Dp_ED = norm(cross_vecs) / norm(ED_float)
        if d_Dp_ED > 1e-9:
            break  # pt_d is not on the line
    
    d_Dp_rounded = round(d_Dp_ED, 2)

    d_correct = random.choice([True, False])
    if d_correct:
        d_d_display = d_Dp_rounded
    else:
        d_d_display = round(d_Dp_rounded + random.choice([-0.5, 0.3, 0.5, -0.3, 0.7, -0.7, 1.0, -1.0]), 2)
        if d_d_display <= 0:
            d_d_display = d_Dp_rounded + 0.5
        d_d_display = round(d_d_display, 2)

    display_expr = build_vec_expr([a_alpha, a_beta, a_gamma], vec_names)
    stmt_a_text = rf"\(\overrightarrow{{{target_start}{target_end}}}={display_expr}\)"

    d_C_AEF_str = f"{d_b_display:.2f}".replace('.', r'.')
    angle_c_str = f"{angle_c_display:.1f}"
    d_d_str = f"{d_d_display:.2f}"

    # Build question stem
    stem = (
        rf"Cho hình hộp chữ nhật $ABCD.A'B'C'D'$ với $AB={a}$, $AD={b}$, $AA'={c}$. "
        rf"Trên đoạn thẳng ${P1_E}{P2_E}$ lấy điểm $E$ sao cho ${k_den} \overrightarrow{{{P1_E}E}} = {k_num} \overrightarrow{{{P1_E}{P2_E}}}$, "
        rf"lấy điểm $F$ là trọng tâm $\Delta {T1}{T2}{T3}$."
    )

    stmt_a = rf"{'*' if stmt_a_correct else ''}a) {stmt_a_text}"
    stmt_b = rf"{'*' if b_correct else ''}b) $d({pt_b};({plane_b_pt}EF))\approx {d_C_AEF_str}$"
    
    if is_vector_angle:
        c_stmt_text = rf"(\overrightarrow{{{pt_c1}F}},\overrightarrow{{{pt_c2}E}})"
    else:
        c_stmt_text = rf"({pt_c1}F,{pt_c2}E)"
        
    stmt_c = rf"{'*' if c_correct else ''}c) ${c_stmt_text}\approx {angle_c_str}^\circ$"
    stmt_d = rf"{'*' if d_correct else ''}d) $d({pt_d};E{target_line_pt})\approx {d_d_str}$"

    # ---- Solutions ----
    def frac_str(f):
        if f.denominator == 1:
            return str(f.numerator)
        return rf"\dfrac{{{f.numerator}}}{{{f.denominator}}}"

    AE_tex = rf"\left({frac_str(Ex)};\ {frac_str(Ey)};\ {frac_str(Ez)}\right)"
    AF_tex = rf"\left({frac_str(Fx)};\ {frac_str(Fy)};\ {frac_str(Fz)}\right)"
    AFvec_tex = rf"\left({frac_str(target_vec[0])};\ {frac_str(target_vec[1])};\ {frac_str(target_vec[2])}\right)"

    sol_a = rf"""a) {'Đúng' if stmt_a_correct else 'Sai'}.

Đặt hệ trục tọa độ: $A=(0;0;0)$, $B=({a};0;0)$, $C=({a};{b};0)$, $D=(0;{b};0)$, $A'=(0;0;{c})$, $B'=({a};0;{c})$, $C'=({a};{b};{c})$, $D'=(0;{b};{c})$.

$E = {P1_E} + \dfrac{{{k_num}}}{{{k_den}}}\overrightarrow{{{P1_E}{P2_E}}} = {AE_tex}$.

$F$ là trọng tâm $\Delta {T1}{T2}{T3} \Rightarrow F = \dfrac{{{T1} + {T2} + {T3}}}{{3}} = {AF_tex}$.

$\overrightarrow{{{target_start}{target_end}}} = {target_end} - {target_start} = {AFvec_tex}$.

Biểu diễn đúng: $\overrightarrow{{{target_start}{target_end}}} = {build_vec_expr([alpha, beta, gamma], vec_names)}$.

Mệnh đề {'Đúng' if stmt_a_correct else 'đã sai hệ số biểu diễn nên Sai'}."""

    n1f = Fraction(n1).limit_denominator(1000)
    n2f = Fraction(n2).limit_denominator(1000)
    n3f = Fraction(n3).limit_denominator(1000)
    
    vec_P1E_tex = rf"\left({frac_str(vec_P1E_ex[0])};\ {frac_str(vec_P1E_ex[1])};\ {frac_str(vec_P1E_ex[2])}\right)"
    vec_P1F_tex = rf"\left({frac_str(vec_P1F_ex[0])};\ {frac_str(vec_P1F_ex[1])};\ {frac_str(vec_P1F_ex[2])}\right)"
    
    vec_P1_pt_b_ex = (pt_b_ex[0] - P1_ex_plane[0], pt_b_ex[1] - P1_ex_plane[1], pt_b_ex[2] - P1_ex_plane[2])
    vec_P1_pt_b_tex = rf"\left({frac_str(vec_P1_pt_b_ex[0])};\ {frac_str(vec_P1_pt_b_ex[1])};\ {frac_str(vec_P1_pt_b_ex[2])}\right)"

    norm_n = math.sqrt(float(n1f)**2 + float(n2f)**2 + float(n3f)**2)
    dot_n_P1_pt_b = n1f * vec_P1_pt_b_ex[0] + n2f * vec_P1_pt_b_ex[1] + n3f * vec_P1_pt_b_ex[2]

    sol_b = rf"""b) {'Đúng' if b_correct else 'Sai'}.

Ta tính khoảng cách $d({pt_b};({plane_b_pt}EF))$ thông qua thể tích khối tứ diện ${pt_b}.{plane_b_pt}EF$:
$d({pt_b};({plane_b_pt}EF)) = \dfrac{{3V_{{{pt_b}.{plane_b_pt}EF}}}}{{S_{{{plane_b_pt}EF}}}}$

Diện tích tam giác ${plane_b_pt}EF$:
$\overrightarrow{{{plane_b_pt}E}} = {vec_P1E_tex}$, $\overrightarrow{{{plane_b_pt}F}} = {vec_P1F_tex}$.
Tích có hướng $[\overrightarrow{{{plane_b_pt}E}}, \overrightarrow{{{plane_b_pt}F}}] = \left({frac_str(n1f)};\ {frac_str(n2f)};\ {frac_str(n3f)}\right)$.
$S_{{{plane_b_pt}EF}} = \dfrac{{1}}{{2}} |[\overrightarrow{{{plane_b_pt}E}}, \overrightarrow{{{plane_b_pt}F}}]| \approx {norm_n/2:.4f}$.

Thể tích tứ diện ${pt_b}.{plane_b_pt}EF$:
Với $\overrightarrow{{{plane_b_pt}{pt_b}}} = {vec_P1_pt_b_tex}$, ta có:
$V_{{{pt_b}.{plane_b_pt}EF}} = \dfrac{{1}}{{6}} |[\overrightarrow{{{plane_b_pt}E}}, \overrightarrow{{{plane_b_pt}F}}] \cdot \overrightarrow{{{plane_b_pt}{pt_b}}}| = {frac_str(abs(dot_n_P1_pt_b)/6)}$.

Khoảng cách:
$d({pt_b};({plane_b_pt}EF)) = \dfrac{{3 \times {frac_str(abs(dot_n_P1_pt_b)/6)}}}{{{norm_n/2:.4f}}} \approx {d_C_AEF:.4f} \approx {d_C_AEF_rounded:.2f}$.

Vậy mệnh đề là {'Đúng' if b_correct else 'Sai'}."""

    vec_c1F_ex = vec_c1F
    vec_c2E_ex = vec_c2E
    
    vec_c1F_tex = rf"\left({frac_str(vec_c1F_ex[0])};\ {frac_str(vec_c1F_ex[1])};\ {frac_str(vec_c1F_ex[2])}\right)"
    vec_c2E_tex = rf"\left({frac_str(vec_c2E_ex[0])};\ {frac_str(vec_c2E_ex[1])};\ {frac_str(vec_c2E_ex[2])}\right)"
    
    if is_vector_angle:
        angle_type_str = rf"Góc giữa hai véc tơ $\overrightarrow{{{pt_c1}F}}$ và $\overrightarrow{{{pt_c2}E}}$"
        cos_expr = rf"\cos\alpha = \dfrac{{\overrightarrow{{{pt_c1}F}} \cdot \overrightarrow{{{pt_c2}E}}}}{{|\overrightarrow{{{pt_c1}F}}||\overrightarrow{{{pt_c2}E}}|}} \approx {cos_raw:.4f}"
    else:
        angle_type_str = rf"Góc giữa hai đường thẳng ${pt_c1}F$ và ${pt_c2}E$"
        cos_expr = rf"\cos\alpha = \dfrac{{|\overrightarrow{{{pt_c1}F}} \cdot \overrightarrow{{{pt_c2}E}}|}}{{|\overrightarrow{{{pt_c1}F}}||\overrightarrow{{{pt_c2}E}}|}} \approx {abs(cos_raw):.4f}"

    sol_c = rf"""c) {'Đúng' if c_correct else 'Sai'}.

$\overrightarrow{{{pt_c1}F}} = F - {pt_c1} = {vec_c1F_tex}$.

$\overrightarrow{{{pt_c2}E}} = E - {pt_c2} = {vec_c2E_tex}$.

{angle_type_str}:
${cos_expr}$.

$\alpha \approx {angle_actual:.1f}^\circ$.

Vậy mệnh đề là {'Đúng' if c_correct else 'Sai'}."""

    vec_ED_tex = rf"\left({frac_str(ED_ex[0])};\ {frac_str(ED_ex[1])};\ {frac_str(ED_ex[2])}\right)"
    vec_E_pt_d_tex = rf"\left({frac_str(vec_E_pt_d[0])};\ {frac_str(vec_E_pt_d[1])};\ {frac_str(vec_E_pt_d[2])}\right)"

    pt_d_coords = rf"({frac_str(pts_exact[pt_d][0])};{frac_str(pts_exact[pt_d][1])};{frac_str(pts_exact[pt_d][2])})"
    D_coords = rf"({frac_str(pts_exact[target_line_pt][0])};{frac_str(pts_exact[target_line_pt][1])};{frac_str(pts_exact[target_line_pt][2])})"

    sol_d = rf"""d) {'Đúng' if d_correct else 'Sai'}.

$E = {AE_tex}$, ${target_line_pt}={D_coords}$, ${pt_d}={pt_d_coords}$.

Véctơ chỉ phương đường thẳng $E{target_line_pt}$: $\overrightarrow{{E{target_line_pt}}} = {target_line_pt} - E = {vec_ED_tex}$.

$\overrightarrow{{E{pt_d}}} = {pt_d} - E = {vec_E_pt_d_tex}$.

$d({pt_d};E{target_line_pt}) = \dfrac{{|\overrightarrow{{E{pt_d}}} \times \overrightarrow{{E{target_line_pt}}}|}}{{|\overrightarrow{{E{target_line_pt}}}|}} \approx {d_Dp_ED:.4f} \approx {d_Dp_rounded:.2f}$.

Vậy mệnh đề là {'Đúng' if d_correct else 'Sai'}."""

    key_arr = ["Đ" if x else "S" for x in (stmt_a_correct, b_correct, c_correct, d_correct)]
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

    seed_val = None
    if len(sys.argv) > 2:
        seed_val = int(sys.argv[2])

    out_dir = os.path.dirname(os.path.abspath(__file__))
    content = ""
    keys = []

    for i in range(num_questions):
        seed = (seed_val + i) if seed_val is not None else None
        q, s, k = generate_question(seed=seed)
        keys.append(k)
        content += rf"""Câu {i+1}: {q}

Lời giải:

{s}

"""

    template = r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath, amsfonts, amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=2cm}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\usepackage{esvect}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)
    output_file = os.path.join(out_dir, "cau_1_questions.tex")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")


if __name__ == "__main__":
    main()
