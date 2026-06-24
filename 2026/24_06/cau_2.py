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

    p, q, h, k = random.choice(PARAM_SETS)

    # Coordinates (exact fractions for E)
    A  = (0, 0, 0)
    B  = (p, 0, 0)
    C  = (0, q, 0)
    Ap = (0, 0, h)
    Bp = (p, 0, h)
    Cp = (0, q, h)

    # E on AC': AE = (1/k)*AC', so AC' = k*AE
    # AC' vector = C' - A = (0, q, h)
    Ex = Fraction(0)
    Ey = Fraction(q, k)
    Ez = Fraction(h, k)

    # G = centroid(A, B, C') = ((0+p+0)/3, (0+0+q)/3, (0+0+h)/3)
    Gx = Fraction(p, 3)
    Gy = Fraction(q, 3)
    Gz = Fraction(h, 3)

    # ---- Statement a: angle between A'G and BE ----
    ApG = (float(Gx - 0), float(Gy - 0), float(Gz - h))  # G - A'
    BE  = (float(Ex - p), float(Ey - 0), float(Ez - 0))   # E - B

    cos_a = dot(ApG, BE) / (norm(ApG) * norm(BE))
    cos_a = max(-1.0, min(1.0, cos_a))
    # Angle between lines (always acute or right)
    angle_a_deg = math.degrees(math.acos(abs(cos_a)))
    angle_a_rounded = round(angle_a_deg, 1)

    a_correct = random.choice([True, False])
    if a_correct:
        angle_a_display = angle_a_rounded
    else:
        perturb = random.choice([-10, 10, -15, 15, -20, 20, -5, 5, -25, 25])
        angle_a_display = round(angle_a_rounded + perturb, 1)
        if angle_a_display < 0 or angle_a_display > 90:
            angle_a_display = round(angle_a_rounded + (5 if angle_a_rounded < 45 else -5), 1)

    # ---- Statement b: vec(A'E) · vec(EC) ----
    # A'E = E - A' = (Ex-0, Ey-0, Ez-h)
    # EC  = C - E  = (0-Ex, q-Ey, 0-Ez)
    ApE = (float(Ex - 0), float(Ey - 0), float(Ez - h))
    EC  = (float(0 - Ex), float(q - Ey), float(0 - Ez))

    dot_prod = dot(ApE, EC)
    dot_frac = Fraction(dot_prod).limit_denominator(1000)

    b_correct = random.choice([True, False])
    if b_correct:
        dot_display = dot_frac
    else:
        # Perturb by adding a fraction
        perturb_opts = [Fraction(1), Fraction(-1), Fraction(1, 2), Fraction(-1, 2),
                        Fraction(3, 2), Fraction(-3, 2), Fraction(2), Fraction(-2),
                        Fraction(3), Fraction(-3), Fraction(5, 2), Fraction(-5, 2)]
        dot_display = dot_frac + random.choice(perturb_opts)

    # ---- Statement c: V_{E.B'C'BC} ----
    # The solid E.B'C'BC is a pyramid with base B'C'BC (a rectangle) and apex E.
    # Base B'C'BC: B=(p,0,0), C=(0,q,0), C'=(0,q,h), B'=(p,0,h) - this is a rectangle
    # Area of base B'C'BC:
    #   BC = C - B = (-p, q, 0), BB' = B' - B = (0, 0, h)
    #   No wait - the base is quadrilateral B'C'BC which is a rectangle with sides BC and BB'
    #   Area = BC * h (since BB' is perpendicular to base plane... actually BC is not perp to h)
    #   Let's compute properly: B'C'BC is rectangle with sides BC and BB'
    #   BC vector: C-B = (-p, q, 0), |BC| = sqrt(p²+q²)
    #   BB' vector: B'-B = (0,0,h), |BB'| = h
    #   Since BC ⊥ BB', area = |BC|*|BB'| = h*sqrt(p²+q²)
    #
    # For pyramid E.B'C'BC:
    # Volume = (1/3) * Area_base * height from E to plane(B'C'BC)
    # Plane B'C'BC: contains B, normal = BC × BB' = (-p,q,0)×(0,0,h) = (qh, ph, 0)
    #   simplified normal: (q, p, 0)
    # Equation: q(x-p) + p(y-0) + 0*(z-0) = 0 → qx + py = qp
    # d(E; plane B'C'BC) = |q*Ex + p*Ey - qp| / sqrt(q²+p²)
    #   = |q*0 + p*(q/k) - qp| / sqrt(p²+q²)
    #   = |pq/k - pq| / sqrt(p²+q²)
    #   = pq|1/k - 1| / sqrt(p²+q²)
    #   = pq*(k-1)/k / sqrt(p²+q²)

    area_base = h * math.sqrt(p**2 + q**2)
    d_E_to_BCCB = abs(float(Fraction(q*0) + Fraction(p*q, k) - q*p)) / math.sqrt(p**2 + q**2)
    # = p*q*(k-1)/k / sqrt(p²+q²)
    vol_E_BCBC = (1/3) * area_base * d_E_to_BCCB

    # Simpler alternative: use the fact that the prism ABC.A'B'C' has volume (1/2)*p*q*h
    # E.B'C'BC is one part of the prism. 
    # Actually, let's compute using coordinates directly.
    # Split B'C'BC into two triangles or use the formula for a general pyramid.
    # V = (1/3)|det([B-E, B'-E, C-E])| for tetrahedron E,B,B',C ... then add E,B',C',C

    def tetra_vol(P1, P2, P3, P4):
        """Volume of tetrahedron with vertices P1,P2,P3,P4."""
        v1 = (P2[0]-P1[0], P2[1]-P1[1], P2[2]-P1[2])
        v2 = (P3[0]-P1[0], P3[1]-P1[1], P3[2]-P1[2])
        v3 = (P4[0]-P1[0], P4[1]-P1[1], P4[2]-P1[2])
        cr = cross(v2, v3)
        return abs(dot(v1, cr)) / 6.0

    E_f = (float(Ex), float(Ey), float(Ez))
    # Pyramid E.B'C'BC = tetra(E,B,C,B') + tetra(E,B',C,C')
    vol1 = tetra_vol(E_f, B, C, Bp)
    vol2 = tetra_vol(E_f, Bp, C, Cp)
    vol_total = vol1 + vol2

    # Check with exact computation:
    # V_prism(ABC.A'B'C') = (1/2)*p*q*h
    # E divides AC' in ratio 1:(k-1), so the pyramid E.ABC part etc.
    vol_exact = vol_total
    vol_rounded = round(vol_exact, 2)
    # Check if integer
    vol_int = int(round(vol_exact))
    if abs(vol_exact - vol_int) < 0.001:
        vol_display_str = str(vol_int)
        vol_exact_nice = vol_int
    else:
        vol_display_str = f"{vol_rounded:.2f}".replace('.', ',')
        vol_exact_nice = vol_rounded

    c_correct = random.choice([True, False])
    if c_correct:
        vol_display = vol_exact_nice
        vol_display_str_stmt = str(vol_display) if isinstance(vol_display, int) else f"{vol_display:.2f}".replace('.', ',')
    else:
        perturb_v = random.choice([1, -1, 2, -2, 3, -3, 0.5, -0.5])
        vol_wrong = vol_exact_nice + perturb_v
        if vol_wrong <= 0:
            vol_wrong = vol_exact_nice + abs(perturb_v) + 1
        vol_display = vol_wrong
        if isinstance(vol_wrong, int) or (isinstance(vol_wrong, float) and vol_wrong == int(vol_wrong)):
            vol_display_str_stmt = str(int(vol_wrong))
        else:
            vol_display_str_stmt = f"{vol_wrong:.1f}".replace('.', ',')

    # ---- Statement d: d(E; plane A'BC) ----
    # Plane A'BC contains A'=(0,0,h), B=(p,0,0), C=(0,q,0)
    # A'B = B - A' = (p,0,-h)
    # A'C = C - A' = (0,q,-h)
    # Normal = A'B × A'C
    ApB = (p, 0, -h)
    ApC = (0, q, -h)
    n_ApBC = cross(ApB, ApC)  # = (0*(-h)-(-h)*q, (-h)*0-p*(-h), p*q-0*0) = (qh, ph, pq)
    # n = (qh, ph, pq)
    # Plane through A'=(0,0,h): qh*(x-0) + ph*(y-0) + pq*(z-h) = 0
    # → qhx + phy + pqz = pqh

    # d(E; plane A'BC) = |qh*Ex + ph*Ey + pq*Ez - pqh| / sqrt((qh)²+(ph)²+(pq)²)
    num_d = abs(q*h*float(Ex) + p*h*float(Ey) + p*q*float(Ez) - p*q*h)
    den_d = math.sqrt((q*h)**2 + (p*h)**2 + (p*q)**2)
    d_E_ApBC = num_d / den_d
    d_E_rounded = round(d_E_ApBC, 3)

    d_correct = random.choice([True, False])
    if d_correct:
        d_display = d_E_rounded
    else:
        perturb_d = random.choice([-0.1, 0.1, -0.2, 0.2, -0.3, 0.3, -0.5, 0.5])
        d_wrong = round(d_E_rounded + perturb_d, 3)
        if d_wrong <= 0:
            d_wrong = d_E_rounded + 0.1
        d_display = round(d_wrong, 3)

    # ---- Build question text ----
    # Condition: AC' = k*AE
    dot_display_str = frac_str(dot_display)

    if isinstance(d_display, float):
        d_display_str = f"{d_display:.3f}"
    else:
        d_display_str = str(d_display)

    stem = (
        rf"Cho hình lăng trụ đứng $ABC.A'B'C'$ có tam giác đáy $ABC$ vuông tại $A$ "
        rf"với $AB={p}$, $AC={q}$, $AA'={h}$. "
        rf"Điểm $E$ trên $AC'$ sao cho $AC'={k}AE$, "
        rf"$G$ là trọng tâm $\Delta ABC'$."
    )

    stmt_a = (
        rf"{'*' if a_correct else ''}a) "
        rf"Góc giữa $A'G$ và $BE$ là $\approx {angle_a_display:.1f}^\circ$"
        r"   (có đảo điểm)"
    )
    stmt_b = (
        rf"{'*' if b_correct else ''}b) "
        rf"$\overrightarrow{{A'E}} \cdot \overrightarrow{{EC}} = {dot_display_str}$"
        r"       (có đảo điểm)"
    )
    stmt_c = (
        rf"{'*' if c_correct else ''}c) "
        rf"$V_{{E.B'C'BC}} = {vol_display_str_stmt}$"
        r"       (có đảo đỉnh)"
    )
    stmt_d = (
        rf"{'*' if d_correct else ''}d) "
        rf"$d(E; (A'BC)) \approx {d_display_str}$"
        r"       (có đảo điểm và mặt phẳng)"
    )

    # ---- Solutions ----
    sol_a = rf"""a) {'Đúng' if a_correct else 'Sai'}.

Đặt hệ trục tọa độ: $A=(0;0;0)$, $B=({p};0;0)$, $C=(0;{q};0)$,
$A'=(0;0;{h})$, $B'=({p};0;{h})$, $C'=(0;{q};{h})$.

$E$ trên $AC'$ với $AC'={k}AE \Rightarrow AE = \dfrac{{1}}{{{k}}}AC'$:
$E = A + \dfrac{{1}}{{{k}}}\overrightarrow{{AC'}} = \left(0;\ {frac_str(Ey)};\ {frac_str(Ez)}\right)$.

$G = $ trọng tâm $\Delta ABC' = \left(\dfrac{{0+{p}+0}}{{3}};\ \dfrac{{0+0+{q}}}{{3}};\ \dfrac{{0+0+{h}}}{{3}}\right) = \left({frac_str(Gx)};\ {frac_str(Gy)};\ {frac_str(Gz)}\right)$.

$\overrightarrow{{A'G}} = G - A' = \left({frac_str(Gx)};\ {frac_str(Gy)};\ {frac_str(Gz - h)}\right)$.

$\overrightarrow{{BE}} = E - B = \left({frac_str(-p)};\ {frac_str(Ey)};\ {frac_str(Ez)}\right)$.

$\cos\alpha = \dfrac{{|\overrightarrow{{A'G}} \cdot \overrightarrow{{BE}}|}}{{|\overrightarrow{{A'G}}||\overrightarrow{{BE}}|}} \approx {abs(cos_a):.4f}$.

$\alpha \approx {angle_a_deg:.1f}^\circ$.

Vậy mệnh đề là {'Đúng' if a_correct else 'Sai'}."""

    # Exact dot product computation
    ApE_frac = (Ex - 0, Ey - 0, Ez - Fraction(h))
    EC_frac  = (Fraction(0) - Ex, Fraction(q) - Ey, Fraction(0) - Ez)
    dot_exact = ApE_frac[0]*EC_frac[0] + ApE_frac[1]*EC_frac[1] + ApE_frac[2]*EC_frac[2]

    sol_b = rf"""b) {'Đúng' if b_correct else 'Sai'}.

$\overrightarrow{{A'E}} = E - A' = \left(0;\ {frac_str(Ey)};\ {frac_str(Ez - h)}\right)$.

$\overrightarrow{{EC}} = C - E = \left(0;\ {frac_str(Fraction(q) - Ey)};\ {frac_str(-Ez)}\right)$.

$\overrightarrow{{A'E}} \cdot \overrightarrow{{EC}} = 0 \cdot 0 + {frac_str(Ey)} \cdot {frac_str(Fraction(q)-Ey)} + {frac_str(Ez-h)} \cdot {frac_str(-Ez)}$

$= {frac_str(Ey * (Fraction(q) - Ey))} + {frac_str((Ez - h)*(-Ez))} = {frac_str(dot_exact)}$.

Vậy mệnh đề là {'Đúng' if b_correct else 'Sai'}."""

    # Volume solution
    # V_prism = (1/2)*p*q*h
    v_prism = Fraction(p*q*h, 2)
    # E.B'C'BC: use the complement method if possible, or direct formula
    # V_{E.B'C'BC}: Let's split into E.BB'C' + E.BCC'
    # Tetra E,B,B',C': volume = (1/6)|det[EB, EB', EC']|
    # EB = B-E = (p, -q/k, -h/k)
    # EB' = B'-E = (p, -q/k, h-h/k) = (p, -q/k, h(k-1)/k)
    # EC' = C'-E = (0, q-q/k, h-h/k) = (0, q(k-1)/k, h(k-1)/k)
    EB_f = (Fraction(p), -Ey, -Ez)
    EBp_f = (Fraction(p), -Ey, Fraction(h) - Ez)
    ECp_f = (Fraction(0), Fraction(q) - Ey, Fraction(h) - Ez)
    EC_f = (Fraction(0), Fraction(q) - Ey, -Ez)

    def det3(a, b, c):
        return (a[0]*(b[1]*c[2]-b[2]*c[1])
                - a[1]*(b[0]*c[2]-b[2]*c[0])
                + a[2]*(b[0]*c[1]-b[1]*c[0]))

    vol1_f = abs(det3(EB_f, EBp_f, ECp_f)) / 6
    vol2_f = abs(det3(EB_f, EC_f, ECp_f)) / 6
    vol_exact_f = vol1_f + vol2_f

    sol_c = rf"""c) {'Đúng' if c_correct else 'Sai'}.

Thể tích lăng trụ $ABC.A'B'C'$: $V_{{ABC.A'B'C'}} = \dfrac{{1}}{{2}} \cdot AB \cdot AC \cdot AA' = \dfrac{{1}}{{2}} \cdot {p} \cdot {q} \cdot {h} = {frac_str(v_prism)}$.

Tách khối $E.B'C'BC$ thành hai tứ diện:
$V_{{E.BB'C'}} = \dfrac{{1}}{{6}} |\det(\overrightarrow{{EB}}, \overrightarrow{{EB'}}, \overrightarrow{{EC'}})| = {frac_str(vol1_f)}$.

$V_{{E.BCC'}} = \dfrac{{1}}{{6}} |\det(\overrightarrow{{EB}}, \overrightarrow{{EC}}, \overrightarrow{{EC'}})| = {frac_str(vol2_f)}$.

$V_{{E.B'C'BC}} = {frac_str(vol1_f)} + {frac_str(vol2_f)} = {frac_str(vol_exact_f)}$.

Vậy mệnh đề là {'Đúng' if c_correct else 'Sai'}."""

    # d(E; plane A'BC)
    # Normal to A'BC: n = A'B × A'C = (qh, ph, pq)
    # Plane eq: qhx + phy + pqz = pqh
    num_d_f = abs(Fraction(q*h)*Ex + Fraction(p*h)*Ey + Fraction(p*q)*Ez - Fraction(p*q*h))

    sol_d = rf"""d) {'Đúng' if d_correct else 'Sai'}.

Mặt phẳng $(A'BC)$ chứa $A'=(0;0;{h})$, $B=({p};0;0)$, $C=(0;{q};0)$.

$\overrightarrow{{A'B}} = ({p};0;{-h})$, $\overrightarrow{{A'C}} = (0;{q};{-h})$.

Véctơ pháp tuyến $\vec{{n}} = \overrightarrow{{A'B}} \times \overrightarrow{{A'C}} = ({q*h};\ {p*h};\ {p*q})$.

Phương trình $(A'BC)$: ${q*h}x + {p*h}y + {p*q}z = {p*q*h}$.

$d(E;(A'BC)) = \dfrac{{|{q*h} \cdot 0 + {p*h} \cdot {frac_str(Ey)} + {p*q} \cdot {frac_str(Ez)} - {p*q*h}|}}{{\sqrt{{{q*h}^2 + {p*h}^2 + {p*q}^2}}}}$

$= \dfrac{{{frac_str(num_d_f)}}}{{\sqrt{{{(q*h)**2+(p*h)**2+(p*q)**2}}}}} \approx {d_E_ApBC:.3f}$.

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
