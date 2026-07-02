"""
Câu 2: Lăng trụ đứng ABC.A'B'C' vuông tại A - Vector, dot product, thể tích, khoảng cách (Đúng/Sai)
------------------------------------------------------------------------------------------------------
Cho hình lăng trụ đứng ABC.A'B'C' với tam giác đáy ABC vuông tại A.
AB = p, AC = q, AA' = h.
E trên AC' sao cho AC' = k*AE  (tức AE = AC'/k = (1/k)*AC')
G là trọng tâm tam giác ABC'.

Xét 4 mệnh đề:
  a) Góc giữa A'G và BE ≈ ?°  (có đảo)
  b) vec(A'E) · vec(EC) = ?  (có đảo)
  c) V_{E.B'C'BC} = ?  (thể tích khối chóp E.B'C'BC hoặc tương đương)
  d) d(E; (A'BC)) ≈ ?  (có đảo điểm và mặt phẳng)
"""

import math
import os
import random
import sys
from fractions import Fraction
from typing import Tuple

# ---------------------------------------------------------------------------
# Parameter sets: (AB=p, AC=q, AA'=h, k) where E on AC': AE = AC'/k
# Triangle ABC right-angled at A.
# Coordinates: A=(0,0,0), B=(p,0,0), C=(0,q,0)
#              A'=(0,0,h), B'=(p,0,h), C'=(0,q,h)
# E = A + (1/k)*(C'-A) = (0, q/k, h/k)
# G = centroid(A,B,C') = ((0+p+0)/3, (0+0+q)/3, (0+0+h)/3) = (p/3, q/3, h/3)
# ---------------------------------------------------------------------------
PARAM_SETS = [
    # (AB, AC, AA', k) — k integer ≥ 2 so E is strictly between A and C'
    (2, 4, 5, 3),
    (3, 4, 5, 3),
    (2, 6, 5, 3),
    (4, 6, 5, 3),
    (2, 4, 6, 3),
    (3, 6, 6, 3),
    (4, 6, 6, 3),
    (2, 4, 8, 4),
    (3, 4, 8, 4),
    (4, 6, 8, 4),
    (2, 6, 8, 4),
    (3, 6, 8, 3),
    (4, 4, 5, 2),
    (6, 4, 5, 2),
    (4, 6, 5, 2),
    (6, 6, 5, 3),
    (4, 4, 6, 2),
    (6, 4, 6, 3),
    (4, 6, 6, 2),
    (6, 6, 6, 3),
    (2, 4, 10, 5),
    (3, 6, 10, 5),
    (4, 6, 10, 5),
    (2, 6, 10, 5),
    (4, 4, 8, 2),
    (6, 4, 8, 4),
    (6, 6, 8, 4),
    (2, 4, 6, 2),
    (3, 4, 6, 2),
    (2, 6, 6, 2),
    (4, 4, 10, 4),
    (6, 4, 10, 5),
    (6, 6, 10, 5),
    (3, 4, 10, 5),
    (2, 4, 12, 4),
    (3, 6, 12, 4),
    (4, 6, 12, 4),
    (6, 6, 12, 4),
    (4, 4, 12, 3),
    (6, 4, 12, 3),
    (2, 8, 5, 4),
    (4, 8, 5, 4),
    (6, 8, 5, 4),
    (8, 4, 5, 2),
    (8, 6, 5, 3),
    (2, 8, 6, 4),
    (4, 8, 6, 4),
    (8, 4, 6, 2),
    (8, 6, 6, 3),
    (8, 8, 6, 4),
    (2, 8, 8, 4),
    (4, 8, 8, 4),
    (8, 4, 8, 4),
    (8, 6, 8, 4),
    (8, 8, 8, 4),
    (6, 8, 8, 4),
    (3, 8, 6, 4),
    (8, 3, 6, 3),
    (5, 4, 6, 2),
    (4, 5, 6, 5),
]


def dot(u, v):
    return u[0]*v[0] + u[1]*v[1] + u[2]*v[2]

def cross(u, v):
    return (
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0],
    )

def norm(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def vec_sub(u, v):
    return (u[0]-v[0], u[1]-v[1], u[2]-v[2])

def frac_str(f):
    """Format Fraction as LaTeX."""
    f = Fraction(f).limit_denominator(10000)
    if f.denominator == 1:
        return str(f.numerator)
    sign = "-" if f < 0 else ""
    return rf"{sign}\dfrac{{{abs(f.numerator)}}}{{{f.denominator}}}"


def generate_question(seed=None) -> Tuple[str, str, str]:
    if seed is not None:
        random.seed(seed)

    p = random.randint(2, 10)
    q = random.randint(2, 10)
    h = random.randint(2, 10)

    # Coordinates
    A  = (0, 0, 0)
    B  = (p, 0, 0)
    C  = (0, q, 0)
    Ap = (0, 0, h)
    Bp = (p, 0, h)
    Cp = (0, q, h)

    pts_exact = {
        'A': (Fraction(0), Fraction(0), Fraction(0)),
        'B': (Fraction(p), Fraction(0), Fraction(0)),
        'C': (Fraction(0), Fraction(q), Fraction(0)),
        "A'": (Fraction(0), Fraction(0), Fraction(h)),
        "B'": (Fraction(p), Fraction(0), Fraction(h)),
        "C'": (Fraction(0), Fraction(q), Fraction(h))
    }
    base_vertices = list(pts_exact.keys())

    # Randomize segment for E: E on P1_E P2_E
    P1_E, P2_E = random.sample(base_vertices, 2)
    k_num = random.randint(1, 4)
    k_den = k_num + random.randint(1, 4)
    ratio = Fraction(k_num, k_den)
    
    P1_ex = pts_exact[P1_E]
    P2_ex = pts_exact[P2_E]
    
    Ex = P1_ex[0] + ratio * (P2_ex[0] - P1_ex[0])
    Ey = P1_ex[1] + ratio * (P2_ex[1] - P1_ex[1])
    Ez = P1_ex[2] + ratio * (P2_ex[2] - P1_ex[2])
    pts_exact['E'] = (Ex, Ey, Ez)

    # G = centroid of a random triangle
    G_pts = random.sample(base_vertices + ['E'], 3)
    T1, T2, T3 = G_pts
    Gx = (pts_exact[T1][0] + pts_exact[T2][0] + pts_exact[T3][0]) / Fraction(3)
    Gy = (pts_exact[T1][1] + pts_exact[T2][1] + pts_exact[T3][1]) / Fraction(3)
    Gz = (pts_exact[T1][2] + pts_exact[T2][2] + pts_exact[T3][2]) / Fraction(3)
    pts_exact['G'] = (Gx, Gy, Gz)

    pts_labels = list(pts_exact.keys())
    
    def cross_frac(u, v):
        return (
            u[1]*v[2] - u[2]*v[1],
            u[2]*v[0] - u[0]*v[2],
            u[0]*v[1] - u[1]*v[0],
        )

    def dot_frac(u, v):
        return u[0]*v[0] + u[1]*v[1] + u[2]*v[2]

    def sub_frac(u, v):
        return (u[0]-v[0], u[1]-v[1], u[2]-v[2])

    def norm_float(u):
        return math.sqrt(float(u[0])**2 + float(u[1])**2 + float(u[2])**2)

    # ---- Statement a: angle between two vectors/lines ----
    while True:
        pool = [pt for pt in pts_labels if pt not in ['E', 'G']]
        rem = random.sample(pool, 2)
        
        pair1 = ['E', rem[0]]
        pair2 = ['G', rem[1]]
        random.shuffle(pair1)
        random.shuffle(pair2)
        
        if random.choice([True, False]):
            pt_a1, pt_a2, pt_a3, pt_a4 = pair1[0], pair1[1], pair2[0], pair2[1]
        else:
            pt_a1, pt_a2, pt_a3, pt_a4 = pair2[0], pair2[1], pair1[0], pair1[1]
            
        v1 = sub_frac(pts_exact[pt_a2], pts_exact[pt_a1])
        v2 = sub_frac(pts_exact[pt_a4], pts_exact[pt_a3])
        if norm_float(v1) > 1e-9 and norm_float(v2) > 1e-9:
            break

    is_vector_angle = random.choice([True, False])
    v1_f = (float(v1[0]), float(v1[1]), float(v1[2]))
    v2_f = (float(v2[0]), float(v2[1]), float(v2[2]))
    cos_a_raw = dot(v1_f, v2_f) / (norm(v1_f) * norm(v2_f))
    cos_a_raw = max(-1.0, min(1.0, cos_a_raw))
    
    if is_vector_angle:
        angle_a_deg = math.degrees(math.acos(cos_a_raw))
    else:
        angle_a_deg = math.degrees(math.acos(abs(cos_a_raw)))

    angle_a_rounded = round(angle_a_deg, 1)

    a_correct = random.choice([True, False])
    if a_correct:
        angle_a_display = angle_a_rounded
    else:
        perturb = random.choice([-10, 10, -15, 15, -20, 20, -5, 5, -25, 25])
        angle_a_display = round(angle_a_rounded + perturb, 1)
        if angle_a_display < 0 or (is_vector_angle and angle_a_display > 180) or (not is_vector_angle and angle_a_display > 90):
            angle_a_display = round(angle_a_rounded + (5 if angle_a_rounded < 45 else -5), 1)

    # ---- Statement b: dot product ----
    while True:
        pool = [pt for pt in pts_labels if pt not in ['E']]
        rem = random.sample(pool, 3)
        pair1 = ['E', rem[0]]
        pair2 = [rem[1], rem[2]]
        random.shuffle(pair1)
        random.shuffle(pair2)
        if random.choice([True, False]):
            pt_b1, pt_b2, pt_b3, pt_b4 = pair1[0], pair1[1], pair2[0], pair2[1]
        else:
            pt_b1, pt_b2, pt_b3, pt_b4 = pair2[0], pair2[1], pair1[0], pair1[1]

        vb1 = sub_frac(pts_exact[pt_b2], pts_exact[pt_b1])
        vb2 = sub_frac(pts_exact[pt_b4], pts_exact[pt_b3])
        dot_exact_frac = dot_frac(vb1, vb2)
        if dot_exact_frac != 0:
            break

    b_correct = random.choice([True, False])
    if b_correct:
        dot_display = dot_exact_frac
    else:
        perturb_opts = [Fraction(1), Fraction(-1), Fraction(1, 2), Fraction(-1, 2),
                        Fraction(3, 2), Fraction(-3, 2), Fraction(2), Fraction(-2),
                        Fraction(3), Fraction(-3), Fraction(5, 2), Fraction(-5, 2)]
        dot_display = dot_exact_frac + random.choice(perturb_opts)

    # ---- Statement c: Volume of a tetrahedron ----
    while True:
        v_pts = ['E'] + random.sample([p for p in pts_labels if p != 'E'], 3)
        random.shuffle(v_pts)
        v1_c = sub_frac(pts_exact[v_pts[1]], pts_exact[v_pts[0]])
        v2_c = sub_frac(pts_exact[v_pts[2]], pts_exact[v_pts[0]])
        v3_c = sub_frac(pts_exact[v_pts[3]], pts_exact[v_pts[0]])
        cr = cross_frac(v1_c, v2_c)
        vol_exact = abs(dot_frac(cr, v3_c)) / Fraction(6)
        if vol_exact > 0:
            break
            
    c_correct = random.choice([True, False])
    if c_correct:
        vol_display = vol_exact
    else:
        perturb_v = random.choice([Fraction(1), Fraction(-1), Fraction(2), Fraction(-2), Fraction(1,2), Fraction(-1,2)])
        vol_display = vol_exact + perturb_v
        if vol_display <= 0:
            vol_display = vol_exact + abs(perturb_v) + Fraction(1)

    # ---- Statement d: Distance from a point to a plane ----
    while True:
        pt_d = random.choice(['E', 'G'])
        plane_pts = random.sample([v for v in pts_labels if v != pt_d], 3)
        v1_d = sub_frac(pts_exact[plane_pts[1]], pts_exact[plane_pts[0]])
        v2_d = sub_frac(pts_exact[plane_pts[2]], pts_exact[plane_pts[0]])
        n_d = cross_frac(v1_d, v2_d)
        if norm_float(n_d) > 1e-9:
            break
            
    v_d = sub_frac(pts_exact[pt_d], pts_exact[plane_pts[0]])
    d_exact_num = abs(dot_frac(n_d, v_d))
    d_exact_den = norm_float(n_d)
    d_actual = float(d_exact_num) / d_exact_den
    d_rounded = round(d_actual, 2)

    d_correct = random.choice([True, False])
    if d_correct:
        d_display = d_rounded
    else:
        perturb_d = random.choice([-0.1, 0.1, -0.2, 0.2, -0.3, 0.3, -0.5, 0.5])
        d_wrong = round(d_rounded + perturb_d, 2)
        if d_wrong <= 0:
            d_wrong = d_rounded + 0.1
        d_display = round(d_wrong, 2)

    # ---- Build question text ----
    if is_vector_angle:
        a_stmt_text = rf"Góc giữa hai véc tơ $\overrightarrow{{{pt_a1}{pt_a2}}}$ và $\overrightarrow{{{pt_a3}{pt_a4}}}$"
    else:
        a_stmt_text = rf"Góc giữa hai đường thẳng ${pt_a1}{pt_a2}$ và ${pt_a3}{pt_a4}$"
        
    dot_display_str = frac_str(dot_display)
    if isinstance(vol_display, Fraction):
        vol_display_str = frac_str(vol_display)
    else:
        vol_display_str = str(vol_display)
    d_display_str = f"{d_display:.2f}".replace('.', ',')

    stem = (
        rf"Cho hình lăng trụ đứng $ABC.A'B'C'$ có tam giác đáy $ABC$ vuông tại $A$ "
        rf"với $AB={p}$, $AC={q}$, $AA'={h}$. "
        rf"Trên đoạn thẳng ${P1_E}{P2_E}$ lấy điểm $E$ sao cho ${k_den} \overrightarrow{{{P1_E}E}} = {k_num} \overrightarrow{{{P1_E}{P2_E}}}$, "
        rf"$G$ là trọng tâm $\Delta {T1}{T2}{T3}$."
    )

    stmt_a = rf"{'*' if a_correct else ''}a) {a_stmt_text} là $\approx {angle_a_display:.1f}^\circ$"
    stmt_b = rf"{'*' if b_correct else ''}b) $\overrightarrow{{{pt_b1}{pt_b2}}} \cdot \overrightarrow{{{pt_b3}{pt_b4}}} = {dot_display_str}$"
    stmt_c = rf"{'*' if c_correct else ''}c) Thể tích khối tứ diện ${v_pts[0]}.{v_pts[1]}{v_pts[2]}{v_pts[3]}$ là ${vol_display_str}$"
    stmt_d = rf"{'*' if d_correct else ''}d) Khoảng cách từ ${pt_d}$ đến mặt phẳng $({plane_pts[0]}{plane_pts[1]}{plane_pts[2]})$ là $\approx {d_display_str}$"

    # ---- Solutions ----
    sol_a = rf"""a) {'Đúng' if a_correct else 'Sai'}.

Đặt hệ trục tọa độ: $A=(0;0;0)$, $B=({p};0;0)$, $C=(0;{q};0)$, $A'=(0;0;{h})$, $B'=({p};0;{h})$, $C'=(0;{q};{h})$.

$E = {P1_E} + \dfrac{{{k_num}}}{{{k_den}}}\overrightarrow{{{P1_E}{P2_E}}} = \left({frac_str(Ex)};\ {frac_str(Ey)};\ {frac_str(Ez)}\right)$.

$G = \dfrac{{{T1} + {T2} + {T3}}}{{3}} = \left({frac_str(Gx)};\ {frac_str(Gy)};\ {frac_str(Gz)}\right)$.

$\overrightarrow{{{pt_a1}{pt_a2}}} = \left({frac_str(v1[0])};\ {frac_str(v1[1])};\ {frac_str(v1[2])}\right)$.

$\overrightarrow{{{pt_a3}{pt_a4}}} = \left({frac_str(v2[0])};\ {frac_str(v2[1])};\ {frac_str(v2[2])}\right)$.

{a_stmt_text}:
$\cos\alpha = \dfrac{{|\overrightarrow{{{pt_a1}{pt_a2}}} \cdot \overrightarrow{{{pt_a3}{pt_a4}}}|}}{{|\overrightarrow{{{pt_a1}{pt_a2}}}||\overrightarrow{{{pt_a3}{pt_a4}}}|}}$ (nếu góc giữa hai đường thẳng thì lấy trị tuyệt đối).
$\approx {abs(cos_a_raw) if not is_vector_angle else cos_a_raw:.4f}$.

$\alpha \approx {angle_a_deg:.1f}^\circ$.

Vậy mệnh đề là {'Đúng' if a_correct else 'Sai'}."""

    sol_b = rf"""b) {'Đúng' if b_correct else 'Sai'}.

$\overrightarrow{{{pt_b1}{pt_b2}}} = \left({frac_str(vb1[0])};\ {frac_str(vb1[1])};\ {frac_str(vb1[2])}\right)$.

$\overrightarrow{{{pt_b3}{pt_b4}}} = \left({frac_str(vb2[0])};\ {frac_str(vb2[1])};\ {frac_str(vb2[2])}\right)$.

$\overrightarrow{{{pt_b1}{pt_b2}}} \cdot \overrightarrow{{{pt_b3}{pt_b4}}} = {frac_str(vb1[0])} \cdot {frac_str(vb2[0])} + {frac_str(vb1[1])} \cdot {frac_str(vb2[1])} + {frac_str(vb1[2])} \cdot {frac_str(vb2[2])} = {frac_str(dot_exact_frac)}$.

Vậy mệnh đề là {'Đúng' if b_correct else 'Sai'}."""

    sol_c = rf"""c) {'Đúng' if c_correct else 'Sai'}.

Ta có các véc tơ:
$\overrightarrow{{{v_pts[0]}{v_pts[1]}}} = \left({frac_str(v1_c[0])};\ {frac_str(v1_c[1])};\ {frac_str(v1_c[2])}\right)$
$\overrightarrow{{{v_pts[0]}{v_pts[2]}}} = \left({frac_str(v2_c[0])};\ {frac_str(v2_c[1])};\ {frac_str(v2_c[2])}\right)$
$\overrightarrow{{{v_pts[0]}{v_pts[3]}}} = \left({frac_str(v3_c[0])};\ {frac_str(v3_c[1])};\ {frac_str(v3_c[2])}\right)$

Tích có hướng $[\overrightarrow{{{v_pts[0]}{v_pts[1]}}}, \overrightarrow{{{v_pts[0]}{v_pts[2]}}}] = \left({frac_str(cr[0])};\ {frac_str(cr[1])};\ {frac_str(cr[2])}\right)$.

Thể tích khối tứ diện:
$V = \dfrac{{1}}{{6}} \left|[\overrightarrow{{{v_pts[0]}{v_pts[1]}}}, \overrightarrow{{{v_pts[0]}{v_pts[2]}}}] \cdot \overrightarrow{{{v_pts[0]}{v_pts[3]}}}\right| = \dfrac{{1}}{{6}} \left|{frac_str(dot_frac(cr, v3_c))}\right| = {frac_str(vol_exact)}$.

Vậy mệnh đề là {'Đúng' if c_correct else 'Sai'}."""

    d_exact_num_frac_str = frac_str(abs(dot_frac(n_d, v_d)) / Fraction(6))
    
    sol_d = rf"""d) {'Đúng' if d_correct else 'Sai'}.

Ta tính khoảng cách từ ${pt_d}$ đến mặt phẳng $({plane_pts[0]}{plane_pts[1]}{plane_pts[2]})$ thông qua thể tích khối tứ diện ${pt_d}.{plane_pts[0]}{plane_pts[1]}{plane_pts[2]}$:
$d({pt_d};({plane_pts[0]}{plane_pts[1]}{plane_pts[2]})) = \dfrac{{3V_{{{pt_d}.{plane_pts[0]}{plane_pts[1]}{plane_pts[2]}}}}}{{S_{{{plane_pts[0]}{plane_pts[1]}{plane_pts[2]}}}}}$

Diện tích tam giác ${plane_pts[0]}{plane_pts[1]}{plane_pts[2]}$:
$\overrightarrow{{{plane_pts[0]}{plane_pts[1]}}} = \left({frac_str(v1_d[0])};\ {frac_str(v1_d[1])};\ {frac_str(v1_d[2])}\right)$
$\overrightarrow{{{plane_pts[0]}{plane_pts[2]}}} = \left({frac_str(v2_d[0])};\ {frac_str(v2_d[1])};\ {frac_str(v2_d[2])}\right)$
Tích có hướng $[\overrightarrow{{{plane_pts[0]}{plane_pts[1]}}}, \overrightarrow{{{plane_pts[0]}{plane_pts[2]}}}] = \left({frac_str(n_d[0])};\ {frac_str(n_d[1])};\ {frac_str(n_d[2])}\right)$.
$S_{{{plane_pts[0]}{plane_pts[1]}{plane_pts[2]}}} = \dfrac{{1}}{{2}} |[\overrightarrow{{{plane_pts[0]}{plane_pts[1]}}}, \overrightarrow{{{plane_pts[0]}{plane_pts[2]}}}]| \approx {d_exact_den/2:.4f}$.

Thể tích tứ diện ${pt_d}.{plane_pts[0]}{plane_pts[1]}{plane_pts[2]}$:
Với $\overrightarrow{{{plane_pts[0]}{pt_d}}} = \left({frac_str(v_d[0])};\ {frac_str(v_d[1])};\ {frac_str(v_d[2])}\right)$, ta có:
$V_{{{pt_d}.{plane_pts[0]}{plane_pts[1]}{plane_pts[2]}}} = \dfrac{{1}}{{6}} |[\overrightarrow{{{plane_pts[0]}{plane_pts[1]}}}, \overrightarrow{{{plane_pts[0]}{plane_pts[2]}}}] \cdot \overrightarrow{{{plane_pts[0]}{pt_d}}}| = {d_exact_num_frac_str}$.

Khoảng cách:
$d = \dfrac{{3 \times {d_exact_num_frac_str}}}{{{d_exact_den/2:.4f}}} \approx {d_actual:.4f} \approx {d_rounded:.2f}$.

Vậy mệnh đề là {'Đúng' if d_correct else 'Sai'}."""

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
    output_file = os.path.join(out_dir, "cau_2_questions.tex")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")


if __name__ == "__main__":
    main()
