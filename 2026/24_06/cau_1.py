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
    sign_str = ""
    if not first:
        sign_str = "+" if f > 0 else "-"
        abs_f = Fraction(abs(f.numerator), f.denominator)
    else:
        sign_str = "" if f > 0 else "-"
        abs_f = Fraction(abs(f.numerator), f.denominator)
    if abs_f == 1:
        coeff_str = ""
    elif abs_f.denominator == 1:
        coeff_str = str(abs_f.numerator)
    else:
        coeff_str = rf"\dfrac{{{abs_f.numerator}}}{{{abs_f.denominator}}}"
    return rf"{sign_str}{coeff_str}\overrightarrow{{{vec_name}}}"


def generate_question(seed=None) -> Tuple[str, str, str]:
    if seed is not None:
        random.seed(seed)

    a, b, c, k_num, k_den = random.choice(PARAM_SETS)

    # Coordinates: A at origin
    # A=(0,0,0), B=(a,0,0), C=(a,b,0), D=(0,b,0)
    # A'=(0,0,c), B'=(a,0,c), C'=(a,b,c), D'=(0,b,c)
    A  = (0, 0, 0)
    B  = (a, 0, 0)
    C  = (a, b, 0)
    D  = (0, b, 0)
    Ap = (0, 0, c)
    Bp = (a, 0, c)
    Cp = (a, b, c)
    Dp = (0, b, c)

    # E on BC': BE = (k_num/k_den) * BC'
    # BC' = C' - B = (0, b, c)
    ratio = Fraction(k_num, k_den)
    E = (a + 0*ratio, 0 + b*ratio, 0 + c*ratio)  # B + ratio*(C'-B)
    # Use exact fractions for E
    Ex = Fraction(a)
    Ey = Fraction(b * k_num, k_den)
    Ez = Fraction(c * k_num, k_den)

    # F = centroid of D'AE
    # D'=(0,b,c), A=(0,0,0), E=(a, Ey, Ez)
    Fx = Fraction(0 + 0 + a, 3)
    Fy = Fraction(b + 0 + b*k_num//1, 3) if False else (Fraction(b) + Fraction(0) + Ey) / 3
    Fz = (Fraction(c) + Fraction(0) + Ez) / 3

    # A'F = F - A' = (Fx-0, Fy-0, Fz-c)
    AFx = Fx - 0
    AFy = Fy - 0
    AFz = Fz - c

    # Express A'F in terms of BA, BC, BB'
    # BA = A - B = (-a, 0, 0) → x-component: AFx = α*(-a) → α = -AFx/a
    # BC = C - B = (0, b, 0)  → y-component: AFy = β*b      → β = AFy/b
    # BB' = B'-B = (0, 0, c)  → z-component: AFz = γ*c      → γ = AFz/c
    alpha = -AFx / a   # coefficient of BA
    beta  =  AFy / b   # coefficient of BC
    gamma =  AFz / c   # coefficient of BB'

    # Correct decomposition: A'F = alpha*BA + beta*BC + gamma*BB'
    # The bẫy: statement swaps BA and BC
    # So stated: A'F = alpha_wrong*BC + beta_wrong*BA + gamma*BB'
    # where alpha_wrong=alpha, beta_wrong=beta (just labels swapped)
    # The statement uses alpha as coeff of BC and beta as coeff of BA → WRONG
    stmt_a_correct = False  # The statement with swapped vectors is always FALSE

    # --- Statement b: d(C; plane AEF) ---
    # Vectors in plane AEF:
    AE = (Ex - 0, Ey - 0, Ez - 0)       # exact fractions
    AF_vec = (AFx + 0, AFy, AFz + c - c) # A'F isn't needed; we want AF from A
    # Actually AF = F - A = (Fx, Fy, Fz)
    AF = (Fx, Fy, Fz)

    # Normal to plane AEF = AE × AF
    n = cross(AE, AF)   # (n1, n2, n3) as fractions
    n1, n2, n3 = n

    # Plane AEF passes through A=(0,0,0): equation n1*x + n2*y + n3*z = 0
    # d(C; (AEF)) = |n1*a + n2*b + n3*0| / sqrt(n1²+n2²+n3²)
    C_num = abs(n1 * a + n2 * b + n3 * 0)
    C_den = math.sqrt(float(n1**2 + n2**2 + n3**2))
    d_C_AEF = float(C_num) / C_den

    # Randomize statement b
    b_correct = random.choice([True, False])
    d_C_AEF_rounded = round(d_C_AEF, 2)
    if b_correct:
        d_b_display = d_C_AEF_rounded
    else:
        # Wrong answer: perturb
        d_b_display = round(d_C_AEF_rounded + random.choice([-0.5, 0.3, -0.3, 0.5, 0.7, -0.7, 1.0, -1.0]), 2)
        if d_b_display <= 0:
            d_b_display = d_C_AEF_rounded + 0.5
        d_b_display = round(d_b_display, 2)

    # --- Statement c: angle between vectors CF and AE (can be obtuse, no abs) ---
    CF = vec_sub((float(Fx), float(Fy), float(Fz)), C)
    AE_float = (float(Ex), float(Ey), float(Ez))
    cos_angle = dot(CF, AE_float) / (norm(CF) * norm(AE_float))
    cos_angle = max(-1.0, min(1.0, cos_angle))
    angle_deg = math.degrees(math.acos(cos_angle))  # actual angle between vectors (0-180°)
    angle_rounded = round(angle_deg, 1)

    c_correct = random.choice([True, False])
    if c_correct:
        angle_c_display = angle_rounded
    else:
        angle_c_display = round(angle_rounded + random.choice([-10, 10, -15, 15, 20, -20, -5, 5]), 1)
        if angle_c_display < 0 or angle_c_display > 180:
            angle_c_display = round(angle_rounded + random.choice([5, -5]), 1)

    # --- Statement d: d(D'; line ED) ---
    # Line ED: through E, direction ED = D - E
    ED = vec_sub(D, (float(Ex), float(Ey), float(Ez)))
    # d(D'; line ED) = |ED × ED'| / |ED|
    # where ED' = D' - E
    EDp = vec_sub(Dp, (float(Ex), float(Ey), float(Ez)))
    cross_vecs = cross(EDp, ED)
    d_Dp_ED = norm(cross_vecs) / norm(ED)
    d_Dp_rounded = round(d_Dp_ED, 2)  # round to 1 decimal per sample problem style

    d_correct = random.choice([True, False])
    if d_correct:
        d_d_display = d_Dp_rounded
    else:
        d_d_display = round(d_Dp_rounded + random.choice([-0.5, 0.3, 0.5, -0.3, 0.7, -0.7, 1.0, -1.0]), 2)
        if d_d_display <= 0:
            d_d_display = d_Dp_rounded + 0.5
        d_d_display = round(d_d_display, 2)

    # Format coefficients for statement a display
    # Correct: A'F = alpha*BA + beta*BC + gamma*BB'
    # Statement (swapped): A'F = alpha*BC + beta*BA + gamma*BB'  (always wrong)
    def fmt_signed_frac(f, first=False):
        """Format Fraction f with sign for LaTeX."""
        sign = "+" if (f >= 0 and not first) else ("-" if f < 0 else "")
        abs_f = Fraction(abs(f.numerator), f.denominator)
        if abs_f.denominator == 1:
            coeff = str(abs_f.numerator)
        else:
            coeff = rf"\dfrac{{{abs_f.numerator}}}{{{abs_f.denominator}}}"
        return sign, coeff

    def frac_to_tex(f, first=False):
        if f == 0:
            return ""
        sign = "" if (f > 0 and first) else ("+" if f > 0 else "-")
        abs_f = abs(f)
        if abs_f.denominator == 1:
            num_str = str(abs_f.numerator)
        else:
            num_str = rf"\dfrac{{{abs_f.numerator}}}{{{abs_f.denominator}}}"
        return sign + num_str

    alpha_tex = frac_to_tex(alpha, first=True)
    beta_tex  = frac_to_tex(beta)
    gamma_tex = frac_to_tex(gamma)

    # Statement a: swapped BA ↔ BC
    stmt_a_text = (
        rf"\(\overrightarrow{{A'F}}={alpha_tex}\overrightarrow{{BC}}{beta_tex}\overrightarrow{{BA}}{gamma_tex}\overrightarrow{{BB'}}\)"
        r"   (có đảo các véc tơ thành phần)"
    )

    # Condition string for E
    # 2BC'=5BE → k_den*BC' = k_num... wait: original is "2BC'=5BE" meaning k_den:k_num=5:2
    # Actually the condition given is: `2BC' = 5BE` means BE = 2/5 BC'
    # So numerically: k_num=2, k_den=5 in original. Let's generalize:
    # "k_den * BC' = (1/ratio_num * k_den / k_num) ... "
    # Actually we need to write the condition as: p*BC' = q*BE so BE = (p/q)*BC'
    # We have ratio = k_num/k_den so p=k_num, q=k_den gives BE = p/q * BC'... wait
    # ratio = k_num/k_den = BE/BC'
    # So: k_den * BE = k_num * BC'
    # Present as: k_den·BE = k_num·BC' ← nope, the sample has "2BC'=5BE" meaning 2/5 = BE/BC'
    # So 2*BC'... hmm. Let me re-read: "2BC' = 5BE" → BC'/BE = 5/2 → BE = (2/5)BC'
    # So if ratio=k_num/k_den, we write: k_den·BC' = (k_den/k_num * k_den) ...
    # Simpler: write "k_den BC' = (k_den²/k_num) BE"?? No.
    # Actually: if BE = (k_num/k_den)*BC', then BC'/BE = k_den/k_num
    # So k_num*BC' = k_den*BE ← that's the relation (cross multiply)
    cond_num = k_num  # k_num*BC' = k_den*BE
    cond_den = k_den

    d_C_AEF_str = f"{d_b_display:.2f}".replace('.', r'.')
    angle_c_str = f"{angle_c_display:.1f}"
    d_d_str = f"{d_d_display:.2f}"

    # Build question stem
    stem = (
        rf"Cho hình hộp chữ nhật $ABCD.A'B'C'D'$ với $AB={a}$, $AD={b}$, $AA'={c}$. "
        rf"Trên $BC'$ lấy điểm $E$ sao cho ${cond_num}BC'={cond_den}BE$, "
        rf"lấy điểm $F$ là trọng tâm $\Delta D'AE$."
    )

    stmt_a = rf"{'*' if stmt_a_correct else ''}a) {stmt_a_text}"
    stmt_b = (
        rf"{'*' if b_correct else ''}b) $d(C;(AEF))\approx {d_C_AEF_str}$ "
        r"(Có đảo điểm và mặt phẳng)"
    )
    stmt_c = (
        rf"{'*' if c_correct else ''}c) $(\overrightarrow{{CF}},\overrightarrow{{AE}})\approx {angle_c_str}^\circ$ "
        r"(hoặc $(CF,AE)$, có đảo điểm)"
    )
    stmt_d = (
        rf"{'*' if d_correct else ''}d) $d(D';ED)\approx {d_d_str}$"
    )

    # ---- Solutions ----
    # Coordinate display helpers
    def frac_str(f):
        if f.denominator == 1:
            return str(f.numerator)
        return rf"\dfrac{{{f.numerator}}}{{{f.denominator}}}"

    AE_tex = rf"\left({frac_str(Fraction(int(Ex)))};\ {frac_str(Ey)};\ {frac_str(Ez)}\right)"
    AF_tex = rf"\left({frac_str(Fx)};\ {frac_str(Fy)};\ {frac_str(Fz)}\right)"
    Ap_tex = rf"(0;\ 0;\ {c})"
    AFvec_tex = rf"\left({frac_str(AFx)};\ {frac_str(AFy)};\ {frac_str(AFz)}\right)"

    n1f = Fraction(n1).limit_denominator(1000)
    n2f = Fraction(n2).limit_denominator(1000)
    n3f = Fraction(n3).limit_denominator(1000)

    sol_a = rf"""a) Sai.

Đặt hệ trục tọa độ: $A=(0;0;0)$, $B=({a};0;0)$, $C=({a};{b};0)$, $D=(0;{b};0)$, $A'=(0;0;{c})$, $B'=({a};0;{c})$, $C'=({a};{b};{c})$, $D'=(0;{b};{c})$.

$\overrightarrow{{BC'}} = ({a};{b};{c}) - ({a};0;0) = (0;{b};{c})$.

$E = B + \dfrac{{{k_num}}}{{{k_den}}}\overrightarrow{{BC'}} = \left({a};\ {frac_str(Ey)};\ {frac_str(Ez)}\right)$.

$F$ là trọng tâm $\Delta D'AE \Rightarrow F = \dfrac{{D' + A + E}}{{3}} = \left({frac_str(Fx)};\ {frac_str(Fy)};\ {frac_str(Fz)}\right)$.

$\overrightarrow{{A'F}} = F - A' = {AFvec_tex}$.

Mặt khác $\overrightarrow{{BA}} = (-{a};0;0)$, $\overrightarrow{{BC}} = (0;{b};0)$, $\overrightarrow{{BB'}} = (0;0;{c})$.

Biểu diễn đúng: $\overrightarrow{{A'F}} = {frac_to_tex(alpha, first=True)}\overrightarrow{{BA}} {frac_to_tex(beta)}\overrightarrow{{BC}} {frac_to_tex(gamma)}\overrightarrow{{BB'}}$.

Mệnh đề đã đảo vai trò của $\overrightarrow{{BA}}$ và $\overrightarrow{{BC}}$ nên Sai."""

    # Normal vector for plane AEF
    n1_val = float(n1)
    n2_val = float(n2)
    n3_val = float(n3)
    norm_n = math.sqrt(n1_val**2 + n2_val**2 + n3_val**2)
    d_num_exact = abs(n1_val * a + n2_val * b)
    d_C_exact = d_num_exact / norm_n

    dot_n_AC = n1f * a + n2f * b

    sol_b = rf"""b) {'Đúng' if b_correct else 'Sai'}.

Ta tính khoảng cách $d(C;(AEF))$ thông qua thể tích khối tứ diện $C.AEF$:
$d(C;(AEF)) = \dfrac{{3V_{{C.AEF}}}}{{S_{{AEF}}}}$

Diện tích tam giác $AEF$:
$\overrightarrow{{AE}} = {AE_tex}$, $\overrightarrow{{AF}} = {AF_tex}$.
Tích có hướng $[\overrightarrow{{AE}}, \overrightarrow{{AF}}] = \left({frac_str(n1f)};\ {frac_str(n2f)};\ {frac_str(n3f)}\right)$.
$S_{{AEF}} = \dfrac{{1}}{{2}} |[\overrightarrow{{AE}}, \overrightarrow{{AF}}]| = \dfrac{{1}}{{2}} \sqrt{{\left({frac_str(n1f)}\right)^2 + \left({frac_str(n2f)}\right)^2 + \left({frac_str(n3f)}\right)^2}} \approx {norm_n/2:.4f}$.

Thể tích tứ diện $C.AEF$:
Với $\overrightarrow{{AC}} = ({a}; {b}; 0)$, ta có:
$V_{{C.AEF}} = \dfrac{{1}}{{6}} |[\overrightarrow{{AE}}, \overrightarrow{{AF}}] \cdot \overrightarrow{{AC}}| = \dfrac{{1}}{{6}} |{frac_str(n1f)}({a}) + {frac_str(n2f)}({b}) + {frac_str(n3f)}(0)| = {frac_str(abs(dot_n_AC)/6)}$.

Khoảng cách:
$d(C;(AEF)) = \dfrac{{3 \times {frac_str(abs(dot_n_AC)/6)}}}{{{norm_n/2:.4f}}} \approx {d_C_AEF:.4f} \approx {d_C_AEF_rounded:.2f}$.

Vậy mệnh đề là {'Đúng' if b_correct else 'Sai'}."""

    CF_float = (float(Fx) - a, float(Fy) - b, float(Fz) - 0)
    cos_raw = dot(CF_float, AE_float) / (norm(CF_float) * norm(AE_float))
    angle_actual = math.degrees(math.acos(max(-1.0, min(1.0, cos_raw))))

    sol_c = rf"""c) {'Đúng' if c_correct else 'Sai'}.

$\overrightarrow{{CF}} = F - C = \left({frac_str(Fx - a)};\ {frac_str(Fy - b)};\ {frac_str(Fz)}\right)$.

$\overrightarrow{{AE}} = {AE_tex}$.

Góc giữa hai véc tơ $\overrightarrow{{CF}}$ và $\overrightarrow{{AE}}$:
$\cos\alpha = \dfrac{{\overrightarrow{{CF}} \cdot \overrightarrow{{AE}}}}{{|\overrightarrow{{CF}}||\overrightarrow{{AE}}|}} \approx {cos_raw:.4f}$.

$\alpha \approx {angle_actual:.1f}^\circ$.

Vậy mệnh đề là {'Đúng' if c_correct else 'Sai'}."""

    # d(D'; line ED) solution
    E_float = (float(Ex), float(Ey), float(Ez))
    ED_float = vec_sub(D, E_float)
    EDp_float = vec_sub(Dp, E_float)
    cross_EDp_ED = cross(EDp_float, ED_float)
    d_actual = norm(cross_EDp_ED) / norm(ED_float)

    sol_d = rf"""d) {'Đúng' if d_correct else 'Sai'}.

$E = \left({frac_str(Ex)};\ {frac_str(Ey)};\ {frac_str(Ez)}\right)$, $D=(0;{b};0)$, $D'=(0;{b};{c})$.

Véctơ chỉ phương đường thẳng $ED$: $\overrightarrow{{ED}} = D - E = \left({frac_str(Fraction(0)-Ex)};\ {frac_str(Fraction(b)-Ey)};\ {frac_str(-Ez)}\right)$.

$\overrightarrow{{ED'}} = D' - E = \left({frac_str(Fraction(0)-Ex)};\ {frac_str(Fraction(b)-Ey)};\ {frac_str(Fraction(c)-Ez)}\right)$.

$d(D';ED) = \dfrac{{|\overrightarrow{{ED'}} \times \overrightarrow{{ED}}|}}{{|\overrightarrow{{ED}}|}} \approx {d_actual:.4f} \approx {d_Dp_rounded:.2f}$.

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
