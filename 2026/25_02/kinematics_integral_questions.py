import os
import random
import logging
import math
from fractions import Fraction
from typing import Dict, Any, List, Tuple
from string import Template

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


# ==============================================================================
# UTILS
# ==============================================================================

def frac_str(f: Fraction) -> str:
    r"""Fraction -> LaTeX \dfrac hoặc số nguyên"""
    if f.denominator == 1:
        return str(f.numerator)
    if f.numerator < 0:
        return rf"-\dfrac{{{abs(f.numerator)}}}{{{f.denominator}}}"
    return rf"\dfrac{{{f.numerator}}}{{{f.denominator}}}"


def format_percentage(val: float, decimals: int = 2) -> str:
    perc = val * 100
    if abs(perc - round(perc)) < 1e-9:
        return f"{int(round(perc))}\\%"
    formatted = f"{perc:.{decimals}f}".rstrip('0').rstrip('.')
    return formatted.replace(".", ",") + "\\%"


def format_decimal_vn(val, decimals: int = 4) -> str:
    if isinstance(val, Fraction):
        val = float(val)
    s = f"{val:.{decimals}f}".rstrip('0').rstrip('.')
    if s == "" or s == "-0":
        s = "0"
    return s.replace(".", ",")


def format_coeff_term(coeff: Fraction, var: str, first: bool = False) -> str:
    """Format a coefficient*variable term for display, e.g. -3t, +2"""
    if coeff == 0:
        return ""
    sign = ""
    if coeff > 0 and not first:
        sign = " + "
    elif coeff < 0:
        sign = " - "
        coeff = abs(coeff)
    elif first and coeff > 0:
        sign = ""

    if var == "":
        return f"{sign}{frac_str(coeff)}"

    if coeff == 1:
        return f"{sign}{var}"
    elif coeff == Fraction(1):
        return f"{sign}{var}"
    else:
        return f"{sign}{frac_str(coeff)}{var}"


def format_velocity(a: Fraction, b: Fraction, c: Fraction) -> str:
    """Format v(t) = at^2 + bt + c"""
    parts = []
    # at^2
    if a != 0:
        parts.append(format_coeff_term(a, "t^2", first=(len(parts) == 0)))
    if b != 0:
        parts.append(format_coeff_term(b, "t", first=(len(parts) == 0)))
    if c != 0:
        parts.append(format_coeff_term(c, "", first=(len(parts) == 0)))
    return "".join(parts) if parts else "0"


# ==============================================================================
# TEMPLATE
# ==============================================================================

TEMPLATE_QUESTION = r"""Một chất điểm $X$ chuyển động dọc theo một đường thẳng sao cho vận tốc của nó ở thời điểm $t$ (giây) là: $v(t) = ${v_expr}$ (m/s). Ban đầu, vật ở vị trí điểm $O$ và đi theo hướng về vị trí điểm $A$.

${stmt_a}

${stmt_b}

${stmt_c}

${stmt_d}
"""

TEMPLATE_SOLUTION = r"""
Lời giải

Ta có $v(t) = ${v_expr}$. Nghiệm $v(t) = 0$: $t = ${root1}$ và $t = ${root2}$.

a) ${ans_a}. Quãng đường vật đi được sau $${t1}$ giây là:
$S = \int_{0}^{${t1}} |v(t)| \, dt$

Trên $[0; ${root1}]$: $v(t) \ge 0$ nên $|v(t)| = v(t)$.
Trên $[${root1}; ${t1}]$: $v(t) \le 0$ nên $|v(t)| = -v(t)$.

$S = \int_{0}^{${root1}} v(t) \, dt - \int_{${root1}}^{${t1}} v(t) \, dt$

$S = \left[ ${antideriv_expr} \right]_{0}^{${root1}} - \left[ ${antideriv_expr} \right]_{${root1}}^{${t1}}$

$S = ${S1_val} - (${S2_val}) = ${S_total}$ (m).

b) ${ans_b}. Khoảng cách từ vật tới vị trí ban đầu sau $${t2}$ giây:
$x(${t2}) = \int_{0}^{${t2}} v(t) \, dt = \left[ ${antideriv_expr} \right]_{0}^{${t2}} = ${disp_val}$ (m).

Khoảng cách từ vật tới vị trí ban đầu là $|x(${t2})| = ${disp_abs}$ (m).

c) ${ans_c}. Chất điểm $Y$ xuất phát tại $O$ cùng lúc với $X$, đi theo hướng về $A$ với vận tốc không đổi $v_Y = ${v_Y}$ (m/s).
Vị trí $X$ tại thời điểm $t$: $x_X(t) = \int_{0}^{t} v(s) \, ds = ${antideriv_t_expr}$.
Vị trí $Y$: $x_Y(t) = ${v_Y} \cdot t$.
Hai chất điểm gặp nhau khi $x_X(t) = x_Y(t)$:
$${antideriv_t_expr} = ${v_Y} t$
$\Leftrightarrow t \left( ${quad_meet_expr} \right) = 0$
Bỏ $t = 0$ (vị trí xuất phát), ta giải: $${quad_meet_expr} = 0$.
$\Delta = ${delta_meet}$. ${meet_conclusion}

d) ${ans_d}. Chất điểm $Z$ xuất phát tại $O$, đi theo hướng về $A$ với vận tốc không đổi $v_Z = ${v_Z}$ (m/s), xuất phát muộn hơn $X$ một khoảng $a$ giây.
Vị trí $Z$ tại thời điểm $t$ ($t \ge a$): $x_Z(t) = ${v_Z}(t - a)$.
Gặp nhau đúng 1 lần: $x_X(t) = x_Z(t)$ có đúng 1 nghiệm $t > a$.
$${antideriv_t_expr} = ${v_Z}(t - a)$
$\Leftrightarrow ${cubic_eq} = 0$

Để phương trình có đúng 1 nghiệm trên $(a; +\infty)$, ta tìm điều kiện tiếp xúc.
Đặt $f(t) = x_X(t) - ${v_Z} \cdot t$. Khi đó $f(t) = ${f_expr}$.
$f'(t) = v(t) - ${v_Z} = ${fprime_expr}$
$f'(t) = 0 \Leftrightarrow ${fprime_expr} = 0 \Leftrightarrow t = ${t_touch}$.

Tại $t = ${t_touch}$: $f(${t_touch}) = ${f_at_touch}$.
$x_Z(${t_touch}) = x_X(${t_touch})$ khi $${v_Z}(${t_touch} - a) = ${f_at_touch} + ${v_Z} \cdot ${t_touch}$
$\Rightarrow a = ${t_touch} - \dfrac{${f_at_touch}}{${v_Z}} = ${a_val_exact}$ $\approx ${a_val_round}$ (giây).
"""


# ==============================================================================
# GENERATOR
# ==============================================================================

class KinematicsIntegralQuestion:

    def generate_parameters(self) -> Dict[str, Any]:
        """Generate v(t) = a*t^2 + b*t + c with two positive roots."""
        attempts = 0
        while attempts < 2000:
            attempts += 1

            # Pick two distinct positive rational roots for v(t) = 0
            # roots: r1, r2 with 0 < r1 < r2
            r1_num = random.randint(1, 4)
            r1_den = random.choice([1, 2, 3])
            r2_num = random.randint(r1_num + 1, 6)
            r2_den = random.choice([1, 2, 3])

            r1 = Fraction(r1_num, r1_den)
            r2 = Fraction(r2_num, r2_den)

            if r1 >= r2 or r1 <= 0:
                continue

            # v(t) = a_coeff * (t - r1)(t - r2) = a_coeff * [t^2 - (r1+r2)t + r1*r2]
            a_coeff = Fraction(random.choice([1, 2]))

            a = a_coeff
            b = -a_coeff * (r1 + r2)
            c = a_coeff * r1 * r2

            # c must be > 0 so particle starts moving toward A
            if c <= 0:
                continue

            # Choose t1 between r1 and r2 (so v changes sign)
            # t1 should be nice
            t1_candidates = [r1 + Fraction(k, 6) for k in range(1, 12)]
            t1_candidates = [t for t in t1_candidates if r1 < t <= r2 + Fraction(1, 2) and t > r1]
            if not t1_candidates:
                continue
            t1 = random.choice(t1_candidates)

            # t2 should be >= r2 so displacement involves sign change
            t2_candidates = [r2, r2 + Fraction(1, 2), r2 + 1]
            t2_candidates = [t for t in t2_candidates if t > r1]
            if not t2_candidates:
                continue
            t2 = random.choice(t2_candidates)

            # Antiderivative: F(t) = a/3 t^3 + b/2 t^2 + c*t
            def F(t):
                return a * t**3 / 3 + b * t**2 / 2 + c * t

            # a) Distance = integral |v| from 0 to t1
            # v >= 0 on [0, r1], v <= 0 on [r1, r2], v >= 0 on [r2, ...]
            if t1 <= r1:
                S_total = F(t1) - F(0)
            elif t1 <= r2:
                S_total = (F(r1) - F(0)) - (F(t1) - F(r1))
            else:
                S_total = (F(r1) - F(0)) - (F(r2) - F(r1)) + (F(t1) - F(r2))

            if S_total <= 0:
                continue

            # b) Displacement at t2
            disp = F(t2) - F(0)
            disp_abs = abs(disp)

            # c) Meet with Y: x_X(t) = v_Y * t
            # x_X(t) = F(t) = a/3 t^3 + b/2 t^2 + c*t
            # F(t) = v_Y * t => t * (a/3 t^2 + b/2 t + (c - v_Y)) = 0
            # Need quadratic a/3 t^2 + b/2 t + (c - v_Y) = 0 to have 2 positive roots
            # Sum of roots = -b/2 / (a/3) = -3b/(2a) > 0 => b < 0 (usually true)
            # Product of roots = (c - v_Y) / (a/3) = 3(c - v_Y)/a > 0 => v_Y < c
            # Discriminant > 0

            # Choose v_Y so that the quadratic has exactly 2 positive roots
            # Quadratic: a/3 t^2 + b/2 t + (c - v_Y) = 0
            A_q = a / 3
            B_q = b / 2

            # For 2 positive roots: discriminant > 0, sum > 0, product > 0
            # sum = -B_q / A_q = -(b/2)/(a/3) = -3b/(2a)
            sum_roots = -B_q / A_q
            if sum_roots <= 0:
                continue

            # Product > 0 => c - v_Y > 0 => v_Y < c
            # Discriminant = B_q^2 - 4*A_q*(c - v_Y) > 0
            # => v_Y > c - B_q^2 / (4*A_q)
            disc_threshold = c - B_q**2 / (4 * A_q)

            # Pick v_Y as a nice fraction between disc_threshold and c
            v_Y_candidates = [Fraction(k, 6) for k in range(1, 20)]
            v_Y_candidates = [v for v in v_Y_candidates if disc_threshold < v < c]
            if not v_Y_candidates:
                continue

            v_Y = random.choice(v_Y_candidates)
            C_q = c - v_Y
            delta_meet = B_q**2 - 4 * A_q * C_q

            if delta_meet <= 0:
                continue

            # Verify 2 positive roots
            sqrt_delta = float(delta_meet) ** 0.5
            root_m1 = float(-B_q - sqrt_delta) / float(2 * A_q)
            root_m2 = float(-B_q + sqrt_delta) / float(2 * A_q)
            if root_m1 <= 0 or root_m2 <= 0:
                continue

            # Number of meetings (excluding t=0): 2
            num_meetings = 2

            # d) Z starts a seconds late with speed v_Z, meets X exactly 1 time
            # x_X(t) = F(t), x_Z(t) = v_Z(t - a_delay)
            # Meet: F(t) = v_Z(t - a_delay)
            # => F(t) - v_Z*t = -v_Z * a_delay
            # Let f(t) = F(t) - v_Z*t = a/3 t^3 + b/2 t^2 + (c - v_Z)*t
            # f'(t) = v(t) - v_Z = a*t^2 + b*t + (c - v_Z)
            # For tangent: f'(t_0) = 0 and f(t_0) = -v_Z * a_delay
            # => a_delay = (v_Z * t_0 - F(t_0)) / v_Z = t_0 - F(t_0)/v_Z

            # Pick v_Z
            v_Z_candidates = [Fraction(k, 4) for k in range(1, 12)]
            valid_vZ = []
            for vz in v_Z_candidates:
                # f'(t) = a*t^2 + b*t + (c - vz) = 0
                disc_z = b**2 - 4 * a * (c - vz)
                if disc_z <= 0:
                    continue
                sqrt_dz = Fraction(disc_z)
                # Check if perfect square (for nice answer)
                sq_test = float(disc_z) ** 0.5
                # We allow non-perfect-square, just need t_touch > 0
                t_touch_1 = (-b - Fraction(int(round(sq_test * 1000)), 1000)) / (2 * a)
                t_touch_2 = (-b + Fraction(int(round(sq_test * 1000)), 1000)) / (2 * a)
                # Use exact float
                t_t1_f = (float(-b) - float(disc_z)**0.5) / float(2*a)
                t_t2_f = (float(-b) + float(disc_z)**0.5) / float(2*a)

                for t_touch_f in [t_t1_f, t_t2_f]:
                    if t_touch_f <= 0:
                        continue
                    # a_delay = t_touch - F(t_touch) / vz
                    F_touch = float(a)/3 * t_touch_f**3 + float(b)/2 * t_touch_f**2 + float(c) * t_touch_f
                    a_delay = t_touch_f - F_touch / float(vz)
                    if a_delay > 0 and a_delay < t_touch_f:
                        valid_vZ.append((vz, t_touch_f, a_delay))

            if not valid_vZ:
                continue

            v_Z, t_touch_f, a_delay = random.choice(valid_vZ)

            # Round a_delay to 2 decimal places
            a_delay_round = round(a_delay, 2)

            return {
                "a": a, "b": b, "c": c,
                "r1": r1, "r2": r2,
                "t1": t1, "t2": t2,
                "S_total": S_total,
                "disp": disp, "disp_abs": disp_abs,
                "v_Y": v_Y, "delta_meet": delta_meet,
                "num_meetings": num_meetings,
                "A_q": A_q, "B_q": B_q, "C_q": C_q,
                "v_Z": v_Z, "t_touch": t_touch_f, "a_delay": a_delay,
                "a_delay_round": a_delay_round,
            }
        raise ValueError("Could not find valid parameters after 2000 attempts")

    def generate(self, q_num: int) -> Tuple[str, str]:
        p = self.generate_parameters()
        TF = [random.choice([True, False]) for _ in range(4)]

        a, b, c = p['a'], p['b'], p['c']
        v_expr = format_velocity(a, b, c)

        # a) Distance after t1
        val_a = p['S_total']
        if not TF[0]:
            offsets = [Fraction(1, 6), Fraction(-1, 6), Fraction(1, 3), Fraction(-1, 3)]
            val_a = p['S_total'] + random.choice(offsets)
        stmt_a_text = f"a) Sau ${frac_str(p['t1'])}$ giây, vật di chuyển được quãng đường là ${frac_str(val_a)}$ (m)."
        stmt_a = ("*" if TF[0] else "") + stmt_a_text

        # b) Distance from origin after t2
        val_b = p['disp_abs']
        if not TF[1]:
            offsets = [Fraction(1, 3), Fraction(-1, 3), Fraction(1, 2), Fraction(-1, 2)]
            val_b = p['disp_abs'] + random.choice(offsets)
            if val_b < 0:
                val_b = abs(val_b)
        stmt_b_text = f"b) Sau ${frac_str(p['t2'])}$ giây, khoảng cách từ vật tới vị trí ban đầu bằng ${frac_str(val_b)}$ m."
        stmt_b = ("*" if TF[1] else "") + stmt_b_text

        # c) Meetings with Y
        val_c_meetings = p['num_meetings']
        if not TF[2]:
            val_c_meetings = random.choice([1, 3])
        stmt_c_text = (
            f"c) Một chất điểm $Y$ khác xuất phát tại $O$ cùng lúc với chất điểm $X$, "
            f"đi theo hướng về $A$ với vận tốc không đổi bằng ${frac_str(p['v_Y'])}$ (m/s). "
            f"Khi đó hai chất điểm gặp nhau đúng {val_c_meetings} lần (không tính tại vị trí xuất phát điểm $O$)."
        )
        stmt_c = ("*" if TF[2] else "") + stmt_c_text

        # d) Delayed meeting with Z
        val_d = p['a_delay_round']
        if not TF[3]:
            val_d = round(p['a_delay_round'] + random.choice([-0.15, 0.15, -0.25, 0.25]), 2)
        val_d_str = str(val_d).replace(".", ",")
        stmt_d_text = (
            f"d) Một chất điểm $Z$ xuất phát tại $O$, đi theo hướng về $A$ với vận tốc không đổi "
            f"${format_decimal_vn(float(p['v_Z']), 2)}$ m/s. "
            f"Biết chất điểm $Z$ xuất phát muộn hơn chất điểm $X$ một khoảng thời gian là $a$ giây "
            f"và $Z$ gặp $X$ đúng 1 lần trên đường di chuyển. "
            f"Giá trị của $a$ là ${val_d_str}$ (giây), làm tròn đến hàng phần trăm."
        )
        stmt_d = ("*" if TF[3] else "") + stmt_d_text

        replacements_q = {
            "v_expr": v_expr,
            "stmt_a": stmt_a,
            "stmt_b": stmt_b,
            "stmt_c": stmt_c,
            "stmt_d": stmt_d,
        }
        question_text = TEMPLATE_QUESTION
        for k, v in replacements_q.items():
            question_text = question_text.replace(f"${{{k}}}", str(v))

        # --- Solution ---
        ans_labels = ["Đúng" if tf else "Sai" for tf in TF]

        def F_expr():
            """Antiderivative string"""
            parts = []
            # a/3 t^3
            coeff3 = a / 3
            parts.append(format_coeff_term(coeff3, "t^3", first=True))
            # b/2 t^2
            coeff2 = b / 2
            parts.append(format_coeff_term(coeff2, "t^2", first=False))
            # c*t
            parts.append(format_coeff_term(c, "t", first=False))
            return "".join(parts)

        antideriv_expr = F_expr()

        def F(t):
            return a * t**3 / 3 + b * t**2 / 2 + c * t

        S1_val = F(p['r1']) - F(0)
        if p['t1'] <= p['r1']:
            S2_val = Fraction(0)
        else:
            S2_val = F(p['t1']) - F(p['r1'])

        # Meet quadratic
        A_q, B_q, C_q = p['A_q'], p['B_q'], p['C_q']
        quad_meet_expr = format_velocity(A_q, B_q, C_q)

        delta_meet_frac = p['delta_meet']
        if delta_meet_frac > 0:
            meet_conclusion = f"Vì $\\Delta = {frac_str(delta_meet_frac)} > 0$ nên phương trình có 2 nghiệm dương phân biệt, tức hai chất điểm gặp nhau đúng 2 lần."
        else:
            meet_conclusion = "Phương trình vô nghiệm dương."

        # antideriv as function of t
        antideriv_t = format_velocity(a/3, b/2, c)

        # f(t) = F(t) - v_Z*t
        f_a3 = a / 3
        f_b2 = b / 2
        f_c_vz = c - p['v_Z']
        f_expr = format_velocity(f_a3, f_b2, f_c_vz)

        # f'(t) = v(t) - v_Z
        fprime_c = c - p['v_Z']
        fprime_expr = format_velocity(a, b, fprime_c)

        # t_touch
        t_touch_f = p['t_touch']
        t_touch_str = format_decimal_vn(t_touch_f, 4)

        # f(t_touch)
        f_at_touch = float(f_a3) * t_touch_f**3 + float(f_b2) * t_touch_f**2 + float(f_c_vz) * t_touch_f
        f_at_touch_str = format_decimal_vn(f_at_touch, 4)

        # a_delay exact
        a_val_exact = format_decimal_vn(p['a_delay'], 4)
        a_val_round = str(p['a_delay_round']).replace(".", ",")

        # cubic equation display
        cubic_eq = f"{format_velocity(a/3, b/2, c - p['v_Z'])} + {frac_str(p['v_Z'])} \\cdot a"

        replacements_sol = {
            "v_expr": v_expr,
            "root1": frac_str(p['r1']),
            "root2": frac_str(p['r2']),
            "ans_a": ans_labels[0],
            "ans_b": ans_labels[1],
            "ans_c": ans_labels[2],
            "ans_d": ans_labels[3],
            "t1": frac_str(p['t1']),
            "t2": frac_str(p['t2']),
            "antideriv_expr": antideriv_expr,
            "S1_val": frac_str(S1_val),
            "S2_val": frac_str(S2_val),
            "S_total": frac_str(p['S_total']),
            "disp_val": frac_str(p['disp']),
            "disp_abs": frac_str(p['disp_abs']),
            "v_Y": frac_str(p['v_Y']),
            "antideriv_t_expr": antideriv_t,
            "quad_meet_expr": quad_meet_expr,
            "delta_meet": frac_str(delta_meet_frac),
            "meet_conclusion": meet_conclusion,
            "v_Z": format_decimal_vn(float(p['v_Z']), 2),
            "cubic_eq": cubic_eq,
            "f_expr": f_expr,
            "fprime_expr": fprime_expr,
            "t_touch": t_touch_str,
            "f_at_touch": f_at_touch_str,
            "a_val_exact": a_val_exact,
            "a_val_round": a_val_round,
        }
        solution_text = TEMPLATE_SOLUTION
        for k, v in replacements_sol.items():
            solution_text = solution_text.replace(f"${{{k}}}", str(v))

        final_str = (
            f"\\begin{{ex}}%Câu {q_num}\n"
            + question_text.strip()
            + "\n\n\\loigiai{\n"
            + solution_text.strip()
            + "\n}\n\\end{ex}"
        )
        return final_str, ""


def create_document(questions: List[Tuple[str, str]]) -> str:
    content = "\n\n".join(q for q, _ in questions)
    doc = r"""\documentclass[12pt,a4paper]{article}
\usepackage{amsmath,amssymb}
\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}
\usepackage[solcolor]{ex_test}

\begin{document}

""" + content + r"""

\end{document}
"""
    return doc


if __name__ == "__main__":
    import sys
    num_q = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else random.randint(1, 10000)
    random.seed(seed)
    logging.info(f"Generating {num_q} questions with seed {seed}")

    gen = KinematicsIntegralQuestion()
    qs = []
    for i in range(num_q):
        qs.append(gen.generate(i + 1))

    latex_content = create_document(qs)
    out_file = os.path.join(os.path.dirname(__file__), "kinematics_integral_questions.tex")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(latex_content)
    logging.info(f"Saved to {out_file}")
