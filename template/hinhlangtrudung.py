import math
import random
import sys
from typing import List, Tuple, Optional
from math import gcd
import re

# ---------- Common utilities (refactored) ----------
def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

def fmt_decimal(val: float, ndigits: int = 3) -> str:
    if not math.isfinite(val):
        return "0"
    s = f"{val:.{ndigits}f}".rstrip('0').rstrip('.')
    return s if s else '0'

def fmt_angle_one_decimal(deg: float) -> str:
    s = f"{deg:.1f}".rstrip('0').rstrip('.')
    return s

def perturb_choose(rng: random.Random, base: float, deltas, formatter, bounds=None, max_attempts: int = 8):
    """Return a perturbed value whose formatted string differs; else None.
    Adds minimal fallback tweak to reduce bias when standard deltas fail."""
    original_fmt = formatter(base)
    deltas_list = list(deltas)
    for _ in range(max_attempts):
        d = rng.choice(deltas_list)
        cand = base + d
        if bounds:
            lo, hi = bounds
            if cand < lo:
                cand = lo + abs(d)*0.3
            if cand > hi:
                cand = hi - abs(d)*0.3
        if formatter(cand) != original_fmt:
            return cand
    # fallback: try ± half smallest non-zero delta
    nonzero = [abs(x) for x in deltas_list if x != 0]
    if nonzero:
        smallest = min(nonzero)
        for sign in (1, -1):
            cand = base + sign * smallest * 0.5
            if bounds:
                lo, hi = bounds
                cand = clamp(cand, lo, hi)
            if formatter(cand) != original_fmt:
                return cand
    return None


# ---- Vector operations for area and volume formulas ----
def cross_product(u, v):
    """Tính tích có hướng của 2 vector 3D: u × v"""
    return (
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2], 
        u[0]*v[1] - u[1]*v[0]
    )

def vector_magnitude(v):
    """Tính độ dài vector"""
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def dot_product(u, v):
    """Tính tích vô hướng"""
    return u[0]*v[0] + u[1]*v[1] + u[2]*v[2]

def scalar_triple_product(u, v, w):
    """Tính tích hỗn hợp [u, v, w] = u · (v × w)"""
    cross_vw = cross_product(v, w)
    return dot_product(u, cross_vw)

def triangle_area_vector(AB, AC):
    """Tính diện tích tam giác bằng công thức vector: S = 1/2 |AB × AC|"""
    cross = cross_product(AB, AC)
    return 0.5 * vector_magnitude(cross)

def triangle_area_formula2(AB, AC):
    """Tính diện tích tam giác bằng công thức: S = 1/2 √(|AB|²|AC|² - (AB·AC)²)"""
    mag_AB = vector_magnitude(AB)
    mag_AC = vector_magnitude(AC)
    dot_AB_AC = dot_product(AB, AC)
    return 0.5 * math.sqrt(mag_AB**2 * mag_AC**2 - dot_AB_AC**2)

def tetrahedron_volume(AB, AC, AD):
    """Tính thể tích tứ diện: V = 1/6 |[AB, AC, AD]|"""
    return abs(scalar_triple_product(AB, AC, AD)) / 6.0

# ---- Higher-level shared helpers to reduce duplication ----
ANGLE_DELTAS = [-15,-10,-5,5,10,15]
NUMERIC_NOISE = (-0.2,-0.15,-0.1,0.1,0.15,0.2)

def sanitize_angle_from_cos(rng: random.Random, cos_val: float) -> float:
    """Clamp cosine and convert to degrees without artificial shifting.
    (Logic fix) Previously we nudged angles away from 0°/180°, which broke
    consistency between shown angle and dot-product derived cos. Now we keep
    the mathematical angle to avoid logical mismatch in the solution section."""
    safe = clamp(cos_val, -1.0, 1.0)
    return math.degrees(math.acos(safe))

def make_angle_display(rng: random.Random, true_angle_deg: float, correct_prob: float, formatter=fmt_angle_one_decimal) -> Tuple[str, bool]:
    """Return (shown_angle_str, is_correct). Uses perturb_choose for wrong variant."""
    if rng.random() < correct_prob:
        return formatter(true_angle_deg), True
    alt = perturb_choose(rng, true_angle_deg, ANGLE_DELTAS, formatter, bounds=(0.5,179.5))
    if alt is None:
        return formatter(true_angle_deg), True
    return formatter(alt), False

def make_numeric_display(rng: random.Random, true_val: float, correct_prob: float, formatter=fmt_decimal, noises=NUMERIC_NOISE) -> Tuple[str, bool]:
    """Return (shown_value_str, is_correct) for distance-like numeric approximations."""
    if rng.random() < correct_prob:
        return formatter(true_val), True
    for _ in range(6):
        noise = rng.choice(noises)
        cand = true_val + noise
        if cand < 0:
            cand = abs(noise)
        shown = formatter(cand)
        if shown != formatter(true_val):
            return shown, False
    # Fallback if collisions
    return formatter(true_val), True



def reduce_fraction(num: int, den: int) -> Tuple[int, int]:
    """Utility to reduce fraction to lowest terms."""
    if den == 0:
        return num, 1
    g = gcd(abs(num), abs(den))
    return num // g, den // g


def format_fraction_tex(num: int, den: int) -> str:
    """Format reduced fraction as LaTeX string."""
    num, den = reduce_fraction(num, den)
    return f"{num}" if den == 1 else f"\\frac{{{num}}}{{{den}}}"


def mutate_fraction_string(rng: random.Random, frac_tex: str) -> str:
    """Mutate LaTeX fraction/integer to a different reduced form; return original if cannot.
    Supports patterns: -?\\frac{num}{den} or -?digits"""
    m = re.fullmatch(r"(-)?(\\frac\{(\d+)\}\{(\d+)\}|(\d+))", frac_tex)
    if not m:
        return frac_tex
    sign = -1 if m.group(1) else 1
    if m.group(3):
        num = int(m.group(3)); den = int(m.group(4))
    else:
        num = int(m.group(5)); den = 1
    orig = (sign*num, den)
    for _ in range(6):
        if den == 1:
            delta = rng.choice([-1,1])
            new_num = orig[0] + delta
            if abs(new_num) == abs(orig[0]):
                continue
            if abs(orig[0]) > 1 and new_num == 0:
                new_num += 1
            n2,d2 = reduce_fraction(new_num,1)
        else:
            if rng.random() < 0.5:
                delta = rng.choice([-1,1])
                n_raw = orig[0] + delta
                if n_raw == 0:
                    n_raw += 1
                n2,d2 = reduce_fraction(n_raw, den)
            else:
                delta = rng.choice([-1,1])
                d_raw = den + delta
                if d_raw == 0:
                    d_raw = 2
                n2,d2 = reduce_fraction(orig[0], d_raw)
        if (n2,d2) == orig:
            continue
        if d2 == 1:
            return f"{n2}"
        sign_tex = '-' if n2*d2 < 0 else ''
        return f"{sign_tex}\\frac{{{abs(n2)}}}{{{abs(d2)}}}"
    return frac_tex


class RightPrismQuestion:
    """Sinh bài toán lăng trụ đứng ABC.A'B'C' vuông tại A.

    Chuyển sang "random thật": mỗi lần chạy giá trị đầu vào có thể khác nhau
    (không còn seed nội bộ cố định). Tham số question_number giữ lại chỉ để
    tương thích chữ ký gọi nhưng không dùng cho random.
    """

    def __init__(self, question_number: int, correct_prob: float = 0.6):  # question_number không dùng cho RNG nữa
        self.rng = random.Random()  # seeded by OS/time -> true randomness
        self.x = self.rng.randint(2, 6)
        self.y = self.rng.randint(2, 6)
        self.z = self.rng.randint(2, 6)
        self.k = self.rng.choice([3, 4, 5])
        self.correct_prob = clamp(correct_prob, 0.0, 1.0)

    def build(self, idx: int) -> Tuple[str, List[bool]]:
        x, y, z, k = self.x, self.y, self.z, self.k
        header = (
            f"Câu {idx}: Cho hình lăng trụ đứng ABC.A'B'C' vuông tại A với AB bằng {x}, AC bằng {y}, AA' bằng {z}. "
            f"Điểm E trên AC' sao cho AC' bằng {k} \\, AE."
        ) + "\n\n"

        # (a) góc giữa hai vectơ
        BE = (-x, y / k, z / k)
        EC = (0, (k - 1) * y / k, -z / k)
        A_prime_E = (0, y / k, -(k - 1) * z / k)
        CE_vec = (0, -(k - 1) * y / k, z / k)
        AA_vec = (0, 0, z)
        def dot(u,v): return u[0]*v[0]+u[1]*v[1]+u[2]*v[2]
        def norm(u): return math.sqrt(dot(u,u))
        cos_tex = [
            ("Góc giữa BE và EC là", "\\frac{(k-1)y^2-z^2}{\\sqrt{k^2x^2+y^2+z^2}\\sqrt{(k-1)^2y^2+z^2}}", dot(BE,EC)/(norm(BE)*norm(EC))),
            ("Góc giữa A'E và BE là", "\\frac{y^2-(k-1)z^2}{\\sqrt{y^2+(k-1)^2z^2}\\sqrt{k^2x^2+y^2+z^2}}", dot(A_prime_E,BE)/(norm(A_prime_E)*norm(BE))),
            ("Góc giữa CE và AA' là", "\\frac{z}{\\sqrt{(k-1)^2y^2+z^2}}", dot(CE_vec,AA_vec)/(norm(CE_vec)*norm(AA_vec)))
        ]
        a_label, _a_tex_ignore, a_cos_val = self.rng.choice(cos_tex)
        a_angle = sanitize_angle_from_cos(self.rng, a_cos_val)
        shown_angle, a_ok = make_angle_display(self.rng, a_angle, self.correct_prob)
        a_text = f"{'*a)' if a_ok else 'a)'} {a_label} \\( \\approx {shown_angle}^\\circ \\)\\\n"

        # (b) tích vô hướng
        dot1_val = (k - 1)*(y*y + z*z)/(k*k)
        dot2_val = z*z
        dot3_val = -(k - 1)*y*y/k
        def frac_s(n,d): return format_fraction_tex(n,d)
        cand_b = [
            ("\\overrightarrow{A'E} \\cdot \\overrightarrow{EC}", frac_s(int((k-1)*(y*y+z*z)), k*k), dot1_val),
            ("\\overrightarrow{BB'} \\cdot \\overrightarrow{AC'}", f"{z*z}", dot2_val),
            ("\\overrightarrow{CE} \\cdot \\overrightarrow{B'C'}", ("-" if dot3_val<0 else "")+frac_s(abs(int((k-1)*y*y)), k), dot3_val)
        ]
        b_label, b_correct_tex, _ = self.rng.choice(cand_b)
        if self.rng.random() < self.correct_prob:
            b_stmt = f"{b_label} = {b_correct_tex}"; b_ok=True
        else:
            mutated = mutate_fraction_string(self.rng, b_correct_tex)
            if mutated == b_correct_tex:
                b_stmt = f"{b_label} = {b_correct_tex}"; b_ok=True
            else:
                b_stmt = f"{b_label} = {mutated}"; b_ok=False
        b_text = f"{'*b)' if b_ok else 'b)'} \\( {b_stmt} \\)\\\n"

        # (c) thể tích
        def vol_part(mult_num, mult_den):
            num,den=reduce_fraction(mult_num*x*y*z, mult_den*k)
            return f"{num}" if den==1 else f"\\frac{{{num}}}{{{den}}}"
        # Dùng công thức vector: V_{E.ABC} = 1/6 |[AB, AC, AE]|
        B_vec = (x,0,0)
        C_vec = (0,y,0)
        E_vec = (0,y/k,z/k)
        AB_vec = (B_vec[0], B_vec[1], B_vec[2])
        AC_vec = (C_vec[0], C_vec[1], C_vec[2])
        AE_vec = (E_vec[0], E_vec[1], E_vec[2])
        v_e_abc_val = tetrahedron_volume(AB_vec, AC_vec, AE_vec)
        v_e_a1_val = (k-1)*v_e_abc_val
        v_e_bc_val = 2*(k-1)*v_e_abc_val
        v1 = ("V_{E.ABC}", vol_part(1,6), v_e_abc_val)
        v2 = ("V_{E.A'B'C'}", vol_part(k-1,6), v_e_a1_val)
        v3 = ("V_{E.B'C'BC}", vol_part(k-1,3), v_e_bc_val)
        c_label, c_tex_correct, _ = self.rng.choice([v1,v2,v3])
        if self.rng.random()<self.correct_prob:
            c_stmt=f"{c_label} = {c_tex_correct}"; c_ok=True
        else:
            mutated = mutate_fraction_string(self.rng, c_tex_correct)
            if mutated == c_tex_correct:
                c_stmt = f"{c_label} = {c_tex_correct}"; c_ok=True
            else:
                c_stmt = f"{c_label} = {mutated}"; c_ok=False
        c_text = f"{'*c)' if c_ok else 'c)'} \\( {c_stmt} \\)\\\n"

        # (d) góc mặt phẳng hoặc khoảng cách
        norm_nEBC = math.sqrt((y*z)**2 + (x*z)**2 + ((k-1)*x*y)**2)
        cos1 = (k-1)*x*y/norm_nEBC; cos1_tex = "\\frac{(k-1)xy}{\\sqrt{y^2z^2+x^2z^2+(k-1)^2x^2y^2}}"
        norm_nEA = math.sqrt((y*z)**2 + ((k-1)*x*z)**2 + (x*y)**2)
        cos2 = y*z/norm_nEA; cos2_tex = "\\frac{yz}{\\sqrt{y^2z^2+(k-1)^2x^2z^2+x^2y^2}}"
        d1 = x*y*z/norm_nEBC; d1_tex = "\\frac{xyz}{\\sqrt{y^2z^2+x^2z^2+(k-1)^2x^2y^2}}"
        d2 = (k-2)*x*y*z/(k*math.sqrt((y*z)**2 + (x*z)**2 + (x*y)**2)); d2_tex = "\\frac{(k-2)xyz}{k\\sqrt{y^2z^2+x^2z^2+x^2y^2}}"
        d_cands = [
            ("Góc giữa (EBC) và (ABC) là", cos1_tex, cos1, 'angle1'),
            ("Góc giữa (EA'B) và (ACC'A') là", cos2_tex, cos2, 'angle2'),
            ("d(A; (EBC))", d1_tex, d1, 'dist1'),
            ("d(E; (A'BC))", d2_tex, d2, 'dist2'),
        ]
        d_label, d_tex_correct, d_val, d_type = self.rng.choice(d_cands)
        d_angle = None
        if d_type.startswith('angle'):
            d_angle = sanitize_angle_from_cos(self.rng, d_val)
            shown_d_val, d_ok = make_angle_display(self.rng, d_angle, self.correct_prob)
            d_text = f"{'*d)' if d_ok else 'd)'} {d_label} \\( \\approx {shown_d_val}^\\circ \\)\\\n"
        else:
            shown_num, d_ok = make_numeric_display(self.rng, d_val, self.correct_prob)
            d_text = f"{'*d)' if d_ok else 'd)'} {d_label} \\( \\approx {shown_num} \\)\\\n"

        # Lời giải
        lines: List[str] = []
        def add(s: str, skip=False):
            # Append plain text lines; force line break with \\ unless already present. If skip=True, add a blank line for spacing.
            if s and not s.rstrip().endswith("\\\\"):
                s = s + " \\\\" 
            lines.append(s)
            if skip:
                lines.append("")
        add("Lời giải:")
        add("Chọn hệ trục Oxyz: gốc tại A, Ox // AB, Oy // AC, Oz // AA'.")
        coords = [
            f"A(0,0,0)", f"B({x},0,0)", f"C(0,{y},0)", f"A'(0,0,{z})",
            f"B'({x},0,{z})", f"C'(0,{y},{z})", f"E(0,\\frac{{{y}}}{{{k}}},\\frac{{{z}}}{{{k}}})"
        ]
        add("Toạ độ:\\\\" + "\\\\".join(f"\\({c}\\)" for c in coords), skip=True)
        add("Phần a):")
        # Vector display
        def frac_tex(n,d): return format_fraction_tex(n,d)
        def comp(num,den):
            if num==0: return '0'
            sign='-' if num<0 else ''
            return sign + frac_tex(abs(num),den)
        ky=comp(y,k); kz=comp(z,k); k1y=comp((k-1)*y,k); k1z=comp((k-1)*z,k)
        BE_d = f"(-{x},{ky},{kz})"; EC_d=f"(0,{k1y},-{kz})"; AEp_d=f"(0,{ky},-{k1z})"; CE_d=f"(0,-{k1y},{kz})"; AA_d=f"(0,0,{z})"
        if 'BE và EC' in a_label:
            add(f"Xét \\( \\overrightarrow{{BE}}={BE_d},\\; \\overrightarrow{{EC}}={EC_d} \\).")
        elif "A'E và BE" in a_label:
            add(f"Xét \\( \\overrightarrow{{A'E}}={AEp_d},\\; \\overrightarrow{{BE}}={BE_d} \\).")
        else:
            add(f"Xét \\( \\overrightarrow{{CE}}={CE_d},\\; \\overrightarrow{{AA'}}={AA_d} \\).")
        # Bổ sung thay số cụ thể cho cos góc (a) - loại bỏ công thức ký hiệu
        if 'BE và EC' in a_label:
            a_dot_val = dot(BE, EC); a_n1 = norm(BE); a_n2 = norm(EC)
        elif "A'E và BE" in a_label:
            a_dot_val = dot(A_prime_E, BE); a_n1 = norm(A_prime_E); a_n2 = norm(BE)
        else:  # CE và AA'
            a_dot_val = dot(CE_vec, AA_vec); a_n1 = norm(CE_vec); a_n2 = norm(AA_vec)
        add(f"Tích vô hướng: {fmt_decimal(a_dot_val)}, độ dài: {fmt_decimal(a_n1)} và {fmt_decimal(a_n2)}.")
        add(f"\\(\\cos\\theta = \\frac{{{fmt_decimal(a_dot_val)}}}{{{fmt_decimal(a_n1)} \\cdot {fmt_decimal(a_n2)}}} = {fmt_decimal(a_cos_val)}\\).")
        add(f"Suy ra \\(\\theta \\approx {fmt_angle_one_decimal(a_angle)}^\\circ\\).")
        add("Phần b):")
        # Chỉ hiển thị 2 vectơ liên quan đến câu hỏi thực tế
        if "A'E" in b_label and "EC" in b_label:
            add(f"Xét \\( \\overrightarrow{{A'E}}={AEp_d},\\; \\overrightarrow{{EC}}={EC_d} \\).")
        elif "BB'" in b_label and "AC'" in b_label:
            add(f"Xét \\( \\overrightarrow{{BB'}}=(0,0,{z}),\\; \\overrightarrow{{AC'}}=(0,{y},{z}) \\).")
        else:  # CE và B'C'
            add(f"Xét \\( \\overrightarrow{{CE}}={CE_d},\\; \\overrightarrow{{B'C'}}=(-{x},{y},0) \\).")
        add(f"Kết quả đúng: \\( {b_label} = {b_correct_tex} \\).")
        add("Phần c):")
        # Bổ sung bước tính các véc tơ dùng cho thể tích
        AB_c = f"({x},0,0)"; AC_c = f"(0,{y},0)"; AE_c = f"(0,{ky},{kz})"
        add(f"Tính các véc tơ: \\( \\overrightarrow{{AB}}={AB_c}, \\overrightarrow{{AC}}={AC_c}, \\overrightarrow{{AE}}={AE_c} \\).")
        # Trình bày theo mục tiêu được hỏi trong c_label
        if c_label == "V_{E.ABC}":
            # Công thức thể tích tứ diện: V = 1/6 |[AB, AC, AE]|
            add(f"Thể tích: \\( V_{{E.ABC}} = \\frac{{1}}{{6}}|[\\overrightarrow{{AB}}, \\overrightarrow{{AC}}] \\cdot \\overrightarrow{{AE}}| = {fmt_decimal(v_e_abc_val)} \\).")
        elif c_label == "V_{E.A'B'C'}":
            add("Ta có quan hệ: \\( V_{E.A'B'C'} = (k-1)\\,V_{E.ABC} \\).")
            add(f"Với \\( V_{{E.ABC}} = {fmt_decimal(v_e_abc_val)} \\) suy ra \\( V_{{E.A'B'C'}} = {fmt_decimal(v_e_a1_val)} \\).")
        else:  # V_{E.B'C'BC}
            add("Ta có quan hệ: \\( V_{E.B'C'BC} = 2(k-1)\\,V_{E.ABC} \\).")
            add(f"Với \\( V_{{E.ABC}} = {fmt_decimal(v_e_abc_val)} \\) suy ra \\( V_{{E.B'C'BC}} = {fmt_decimal(v_e_bc_val)} \\).")
        add(f"Kết quả đúng: \\({c_label} = {c_tex_correct} \\).")
        add("Phần d):")
        if d_type=='angle1':
            nEBC_num = (y*z, x*z, (k-1)*x*y)
            add(f"Tìm pháp tuyến của các mặt phẳng:")
            add(f"- Mặt phẳng (ABC): pháp tuyến \\(\\vec{{n_1}} = (0,0,1)\\)")
            add(f"- Mặt phẳng (EBC): từ 3 điểm E, B, C, tính \\(\\vec{{n_2}} = \\overrightarrow{{EB}} \\times \\overrightarrow{{EC}}\\)")
            add(f"\\(\\vec{{n_2}} = ({nEBC_num[0]},{nEBC_num[1]},{nEBC_num[2]})\\)")
            add(f"Công thức góc: \\(\\cos\\alpha = \\frac{{|\\vec{{n_1}} \\cdot \\vec{{n_2}}|}}{{|\\vec{{n_1}}| \\cdot |\\vec{{n_2}}|}}\\)")
            computed_angle = d_angle if d_angle is not None else math.degrees(math.acos(clamp(d_val,-1.0,1.0)))
            add(f"Góc giữa hai mặt phẳng: \\( \\alpha \\approx {fmt_angle_one_decimal(computed_angle)}^\\circ\\).")
        elif d_type=='angle2':
            nEA1 = (y*z, (k-1)*x*z, x*y)
            add(f"Tìm pháp tuyến của các mặt phẳng:")
            add(f"- Mặt phẳng (ACC'A'): pháp tuyến \\(\\vec{{n_1}} = (1,0,0)\\)")
            add(f"- Mặt phẳng (EA'B): từ 3 điểm E, A', B, tính \\(\\vec{{n_2}} = \\overrightarrow{{EA'}} \\times \\overrightarrow{{EB}}\\)")
            add(f"\\(\\vec{{n_2}} = ({nEA1[0]},{nEA1[1]},{nEA1[2]})\\)")
            add(f"Công thức góc: \\(\\cos\\alpha = \\frac{{|\\vec{{n_1}} \\cdot \\vec{{n_2}}|}}{{|\\vec{{n_1}}| \\cdot |\\vec{{n_2}}|}}\\)")
            computed_angle = d_angle if d_angle is not None else math.degrees(math.acos(clamp(d_val,-1.0,1.0)))
            add(f"Góc giữa hai mặt phẳng: \\( \\alpha \\approx {fmt_angle_one_decimal(computed_angle)}^\\circ\\).")
        elif d_type=='dist1':
            nEBC_num = (y*z, x*z, (k-1)*x*y)
            add(f"Phương trình mặt phẳng (EBC):")
            add(f"Pháp tuyến: \\(\\vec{{n}} = ({nEBC_num[0]},{nEBC_num[1]},{nEBC_num[2]})\\)")
            add(f"Phương trình: \\({nEBC_num[0]}x + {nEBC_num[1]}y + {nEBC_num[2]}z = d_0\\)")
            add(f"Công thức khoảng cách: \\(d(A;(EBC)) = \\frac{{|{nEBC_num[0]} \\cdot 0 + {nEBC_num[1]} \\cdot 0 + {nEBC_num[2]} \\cdot 0 - d_0|}}{{\\sqrt{{{nEBC_num[0]}^2 + {nEBC_num[1]}^2 + {nEBC_num[2]}^2}}}}\\)")
            add(f"Khoảng cách d(A; (EBC)) = {fmt_decimal(d_val)}.")
        else:
            nA1BC = (y*z, x*z, x*y)
            add(f"Phương trình mặt phẳng (A'BC):")
            add(f"Pháp tuyến: \\(\\vec{{n}} = ({nA1BC[0]},{nA1BC[1]},{nA1BC[2]})\\)")
            add(f"Phương trình: \\({nA1BC[0]}x + {nA1BC[1]}y + {nA1BC[2]}z = d_0\\)")
            add(f"Công thức khoảng cách: \\(d(E;(A'BC)) = \\frac{{|{nA1BC[0]} \\cdot E_x + {nA1BC[1]} \\cdot E_y + {nA1BC[2]} \\cdot E_z - d_0|}}{{\\sqrt{{{nA1BC[0]}^2 + {nA1BC[1]}^2 + {nA1BC[2]}^2}}}}\\)")
            add(f"Khoảng cách d(E; (A'BC)) = {fmt_decimal(d_val)}.")
        if d_type.startswith('angle'):
            pass
        
        # (Đã bỏ phần kết luận chung theo yêu cầu)
        parts = a_text + b_text + c_text + d_text
        full = "\n".join([header, parts, "\n".join(lines)])
        return full, [a_ok, b_ok, c_ok, d_ok]


class EquilateralPrismQuestion:
    r"""Lăng trụ đứng với đáy tam giác đều cạnh 2a.

    Toạ độ chọn:
        B(-a,0,0), C(a,0,0), A(0,a\sqrt{3},0) và các điểm đỉnh trên thêm z.
    E trên AC' sao cho AC' = k AE (k>1). Nội bộ dùng biến a,z,k.
    """

    def __init__(self, question_number: int, correct_prob: float = 0.6):  # question_number giữ tương thích
        self.rng = random.Random()
        self.a = self.rng.randint(2, 6)
        self.z = self.rng.randint(2, 6)
        self.k = self.rng.choice([3, 4, 5])
        self.correct_prob = max(0.0, min(1.0, correct_prob))

    def build(self, idx: int) -> Tuple[str, List[bool]]:
        a, z, k = self.a, self.z, self.k
        side = 2 * a
        header = (
            f"Câu {idx}: Cho lăng trụ đứng A'B'C'ABC có đáy ABC là tam giác đều với các cạnh bằng {side} và AA' bằng {z}. "
            f"Điểm E trên AC' sao cho AC' bằng {k} \\, AE."
        ) + "\n\n"

        # Vectơ & điểm
        sqrt3 = math.sqrt(3)
        BE = (a + a/k, a*sqrt3*(k-1)/k, z/k)
        EC = (a*(k-1)/k, -a*sqrt3*(k-1)/k, -z/k)
        A_prime_E = (a/k, -a*sqrt3/k, -z*(k-1)/k)
        CE = (-a*(k-1)/k, a*sqrt3*(k-1)/k, z/k)
        AA_prime_vec = (0, 0, z)

        def dot(u, v):
            return u[0]*v[0] + u[1]*v[1] + u[2]*v[2]

        def norm(u):
            return math.sqrt(dot(u, u))

        cos1_val = dot(BE, EC)/(norm(BE)*norm(EC))
        cos2_val = dot(A_prime_E, BE)/(norm(A_prime_E)*norm(BE))
        cos3_val = dot(CE, AA_prime_vec)/(norm(CE)*norm(AA_prime_vec))
        # Công thức hiển thị cos góc (đã hiệu chỉnh mẫu số tránh lặp a^2a^2 và thiếu hệ số 3)
        cos1_tex = r"\frac{-(2a^2(k-1)(k-2)+z^2)}{\sqrt{4a^2(k^2-k+1)+z^2}\sqrt{4a^2(k-1)^2+z^2}}"
        cos2_tex = r"\frac{-(2a^2(k-2)+z^2(k-1))}{\sqrt{4a^2+z^2(k-1)^2}\sqrt{4a^2(k^2-k+1)+z^2}}"
        cos3_tex = r"\frac{z}{\sqrt{4a^2(k-1)^2+z^2}}"
        angle_candidates = [
            ("Góc giữa BE và EC là", cos1_tex, cos1_val),
            ("Góc giữa A'E và BE là", cos2_tex, cos2_val),
            ("Góc giữa CE và AA' là", cos3_tex, cos3_val),
        ]
        label_a, _tex_ignore, val_a = self.rng.choice(angle_candidates)
        angle_deg2 = sanitize_angle_from_cos(self.rng, val_a)
        shown_a, a_ok = make_angle_display(self.rng, angle_deg2, self.correct_prob)
        a_text = f"{'*a)' if a_ok else 'a)'} {label_a} \\( \\approx {shown_a}^\\circ \\)\\\n"

        # (b) dot products
        dot1_val = (k-1)*(4*a*a + z*z)/(k*k)
        dot2_val = z*z
        dot3_val = -2*a*a*(k-1)/k
        def frac(num:int, den:int)->str: return format_fraction_tex(num,den)
        dot1_tex = frac(int((k-1)*(4*a*a + z*z)), k*k)
        dot2_tex = f"{z*z}"
        dot3_tex = "-" + frac(int(2*a*a*(k-1)), k)
        dot_candidates = [
            (r"\overrightarrow{A'E} \cdot \overrightarrow{EC}", dot1_tex, dot1_val),
            (r"\overrightarrow{BB'} \cdot \overrightarrow{AC'}", dot2_tex, dot2_val),
            (r"\overrightarrow{CE} \cdot \overrightarrow{B'C'}", dot3_tex, dot3_val),
        ]
        label_b, tex_b_correct, _ = self.rng.choice(dot_candidates)
        if self.rng.random() < self.correct_prob:
            b_stmt = f"{label_b} = {tex_b_correct}"; b_ok=True
        else:
            mutated = mutate_fraction_string(self.rng, tex_b_correct)
            if mutated == tex_b_correct:
                b_stmt = f"{label_b} = {tex_b_correct}"; b_ok=True
            else:
                b_stmt = f"{label_b} = {mutated}"; b_ok=False
        b_text = f"{'*b)' if b_ok else 'b)'} \\( {b_stmt} \\)\\\n"

        # (c) thể tích
        def vol_part(mult_num, mult_den):
            # Thể tích có nhân tử a^2 z \ sqrt{3}; biểu diễn phần hữu tỉ * \ sqrt{3}
            num, den = reduce_fraction(2 * mult_num * a * a * z, mult_den * k)
            if num == 0:
                return "0"
            if den == 1:
                return ("\\sqrt{3}" if num == 1 else f"{num}\\sqrt{{3}}")
            return f"\\frac{{{num}}}{{{den}}}\\sqrt{{3}}"
        # Dùng công thức vector: V_{E.ABC} = 1/6 |[AB, AC, AE]|
        A_vec = (0,0,0)
        B_vec = (a,0,0)
        C_vec = (0,a*sqrt3,0)
        # E = A + (1/k) AC' = (a/k, a\sqrt{3}(k-1)/k, z/k)
        E_vec = (a/k, a*sqrt3*(k-1)/k, z/k)
        AB_vec = (B_vec[0], B_vec[1], B_vec[2])
        AC_vec = (C_vec[0], C_vec[1], C_vec[2])
        AE_vec = (E_vec[0], E_vec[1], E_vec[2])
        v_e_abc_val = tetrahedron_volume(AB_vec, AC_vec, AE_vec)
        v_e_a1_val = (k-1)*v_e_abc_val
        v_e_bc_val = 2*(k-1)*v_e_abc_val
        v1 = ("V_{E.ABC}", vol_part(1,6), v_e_abc_val)
        v2 = ("V_{E.A'B'C'}", vol_part(k-1,6), v_e_a1_val)
        v3 = ("V_{E.B'C'BC}", vol_part(k-1,3), v_e_bc_val)
        c_label, c_tex_correct, _ = self.rng.choice([v1,v2,v3])
        if self.rng.random()<self.correct_prob:
            c_stmt=f"{c_label} = {c_tex_correct}"; c_ok=True
        else:
            mutated = mutate_fraction_string(self.rng, c_tex_correct)
            if mutated == c_tex_correct:
                c_stmt = f"{c_label} = {c_tex_correct}"; c_ok=True
            else:
                c_stmt = f"{c_label} = {mutated}"; c_ok=False
        c_text = f"{'*c)' if c_ok else 'c)'} \\( {c_stmt} \\)\\\n"

        # (d) góc mặt phẳng hoặc khoảng cách
        norm_nEBC = math.sqrt((a*sqrt3*z)**2 + (a*z)**2 + ((k-1)*a*a*sqrt3)**2)
        # |n_{EBC}|^2 = 3a^2z^2 + a^2z^2 + 3(k-1)^2 a^4 = 4a^2z^2 + 3(k-1)^2 a^4
        cos1 = (k-1)*a*a*sqrt3/norm_nEBC; cos1_tex = "\\frac{(k-1)a^2\\sqrt{3}}{\\sqrt{4a^2z^2+3(k-1)^2a^4}}"
        norm_nEA = math.sqrt((a*sqrt3*z)**2 + ((k-1)*a*z)**2 + (a*a*sqrt3)**2)
        # n1 (ACC'A') ∥ (√3, 1, 0), n2 (EA'B) ∥ (a√3 z, (k-1) a z, a^2 √3)
        # n1·n2 = (k+2) a z, |n1| = 2, |n2| = norm_nEA
        cos2 = (k+2)*a*z/(2*norm_nEA); cos2_tex = "\\frac{(k+2)az}{2\\sqrt{a^2z^2((k-1)^2+3)+3a^4}}"
        d1 = a*a*z/norm_nEBC; d1_tex = "\\frac{a^2z}{\\sqrt{4a^2z^2+3(k-1)^2a^4}}"
        # n(A'BC) ∥ (0, -2 a z, 2 a^2 √3) => |n| = 2 √(a^2 z^2 + 3 a^4)
        # d(E; (A'BC)) = |n·E| / |n| = (k-2) a^2 √3 z / (k √(a^2 z^2 + 3 a^4))
        d2 = (k-2)*a*a*sqrt3*z/(k*math.sqrt(a*a*z*z + 3*a*a*a*a))
        d2_tex = "\\frac{(k-2)a^2\\sqrt{3}z}{k\\sqrt{a^2z^2+3a^4}}"
        d_cands = [
            ("Góc giữa (EBC) và (ABC) là", cos1_tex, cos1, 'angle1'),
            ("Góc giữa (EA'B) và (ACC'A') là", cos2_tex, cos2, 'angle2'),
            ("d(A; (EBC))", d1_tex, d1, 'dist1'),
            ("d(E; (A'BC))", d2_tex, d2, 'dist2'),
        ]
        d_label, d_tex_correct, d_val, d_type = self.rng.choice(d_cands)
        d_angle = None
        if d_type.startswith('angle'):
            d_angle = sanitize_angle_from_cos(self.rng, d_val)
            shown_d_val, d_ok = make_angle_display(self.rng, d_angle, self.correct_prob)
            d_text = f"{'*d)' if d_ok else 'd)'} {d_label} \\( \\approx {shown_d_val}^\\circ \\)\\\n"
        else:
            shown_num, d_ok = make_numeric_display(self.rng, d_val, self.correct_prob)
            d_text = f"{'*d)' if d_ok else 'd)'} {d_label} \\( \\approx {shown_num} \\)\\\n"

        # --- Lời giải chi tiết ---
        lines_detail: List[str] = []
        def addd(s: str, skip=False):
            # Plain text lines; force line break with \\ unless already present. If skip=True, insert a blank line.
            if s and not s.rstrip().endswith("\\\\"):
                s = s + " \\\\" 
            lines_detail.append(s)
            if skip:
                lines_detail.append("")
        addd("Lời giải:")
        addd("Chọn hệ trục Oxyz: gốc O tại trung điểm BC, Ox trùng BC, Oy hướng về phía A, Oz thẳng đứng.")
        def frac_tex(n,d): return format_fraction_tex(n,d)
        xE = frac_tex(a, k); yE_frac = frac_tex(a*(k-1), k); yE = ("" if yE_frac=="1" else yE_frac) + "\\sqrt{3}"; zE = frac_tex(z,k)
        coord_list = [f"B(-{a},0,0)", f"C({a},0,0)", f"A(0,{a}\\sqrt{{3}},0)", f"A'(0,{a}\\sqrt{{3}},{z})", f"B'(-{a},0,{z})", f"C'({a},0,{z})", f"E({xE},{yE},{zE})"]
        addd("Toạ độ:\\\\" + "\\\\".join(f"\\({c}\\)" for c in coord_list), skip=True)
        # a
        addd("Phần a):")
        # --- Hiển thị vectơ với giá trị số (loại bỏ ký hiệu k) ---
        def frac_num(num:int, den:int) -> str:
            n,d = reduce_fraction(num, den)
            if d == 1:
                return f"{n}"
            return f"\\frac{{{n}}}{{{d}}}"
        def comp_plain(num:int, den:int) -> str:
            sign = '-' if num < 0 else ''
            num = abs(num)
            return sign + frac_num(num, den)
        def comp_sqrt3(num:int, den:int) -> str:
            """Rational * sqrt(3) component."""
            sign = '-' if num < 0 else ''
            num = abs(num)
            n,d = reduce_fraction(num, den)
            if n == 0:
                return '0'
            if n == 1 and d == 1:
                return sign + "\\sqrt{3}"
            if d == 1:
                return sign + f"{n}\\sqrt{{3}}"
            return sign + f"\\frac{{{n}}}{{{d}}}\\sqrt{{3}}"
        # Thành phần vectơ sau khi thế số (k đã có giá trị):
        # BE = (a + a/k, a*sqrt3*(k-1)/k, z/k)
        BE_d = "(" + \
                comp_plain(a*(k+1), k) + ", " + \
                comp_sqrt3(a*(k-1), k) + ", " + \
                comp_plain(z, k) + ")"
        # EC = (a*(k-1)/k, -a*sqrt3*(k-1)/k, -z/k)
        EC_d = "(" + \
                comp_plain(a*(k-1), k) + ", -" + comp_sqrt3(a*(k-1), k).lstrip('-') + ", -" + comp_plain(z, k).lstrip('-') + ")"
        # A'E = (a/k, -a*sqrt3/k, -z*(k-1)/k)
        AEp_d = "(" + comp_plain(a, k) + ", -" + comp_sqrt3(a, k).lstrip('-') + ", -" + comp_plain(z*(k-1), k).lstrip('-') + ")"
        # CE = (-a*(k-1)/k, a*sqrt3*(k-1)/k, z/k)
        CE_d = "(-" + comp_plain(a*(k-1), k).lstrip('-') + ", " + comp_sqrt3(a*(k-1), k) + ", " + comp_plain(z, k) + ")"
        AA_d = f"(0,0,{z})"
        if 'BE và EC' in label_a:
            addd(f"Xét \\( \\overrightarrow{{BE}}={BE_d},\\; \\overrightarrow{{EC}}={EC_d} \\)." ); v1a,v2a=BE,EC
        elif "A'E và BE" in label_a:
            addd(f"Xét \\( \\overrightarrow{{A'E}}={AEp_d},\\; \\overrightarrow{{BE}}={BE_d} \\)." ); v1a,v2a=A_prime_E,BE
        else:
            addd(f"Xét \\( \\overrightarrow{{CE}}={CE_d},\\; \\overrightarrow{{AA'}}={AA_d} \\)." ); v1a,v2a=CE,AA_prime_vec
        a_dot_val=dot(v1a,v2a); a_n1=norm(v1a); a_n2=norm(v2a)
        addd(f"Tích vô hướng: {fmt_decimal(a_dot_val)}, độ dài: {fmt_decimal(a_n1)} và {fmt_decimal(a_n2)}.")
        addd(f"\\(\\cos\\theta = \\frac{{{fmt_decimal(a_dot_val)}}}{{{fmt_decimal(a_n1)} \\cdot {fmt_decimal(a_n2)}}} = {fmt_decimal(val_a)}\\).")
        addd(f"Suy ra \\(\\theta \\approx {fmt_angle_one_decimal(angle_deg2)}^\\circ\\).")
        # b
        addd("Phần b):")
        if "A'E" in label_b and "EC" in label_b:
            addd(f"Xét \\( \\overrightarrow{{A'E}}={AEp_d},\\; \\overrightarrow{{EC}}={EC_d} \\).")
        elif "BB'" in label_b and "AC'" in label_b:
            addd(f"Xét \\( \\overrightarrow{{BB'}}=(0,0,{z}),\\; \\overrightarrow{{AC'}}=(a,-a\\sqrt{{3}},{z}) \\).")
        else:
            addd(f"Xét \\( \\overrightarrow{{CE}}={CE_d},\\; \\overrightarrow{{B'C'}}=(2a,0,0) \\).")
        addd(f"Kết quả đúng: \\( {label_b} = {tex_b_correct} \\).")
        # c
        addd("Phần c):")
        # Bổ sung bước tính các véc tơ dùng cho thể tích
        AB_c = f"(-{a},-{a}\\sqrt{{3}},0)"; AC_c = f"({a},-{a}\\sqrt{{3}},0)"
        AE_c = "(" + comp_plain(a, k) + ", " + comp_sqrt3(a*(k-1), k) + ", " + comp_plain(z, k) + ")"
        addd(f"Tính các véc tơ: \\( \\overrightarrow{{AB}}={AB_c}, \\overrightarrow{{AC}}={AC_c}, \\overrightarrow{{AE}}={AE_c} \\).")
        ABv=(-a,-a*math.sqrt(3),0); ACv=(a,-a*math.sqrt(3),0); AEv=(a/k,a*math.sqrt(3)*(k-1)/k,z/k)
        v_e_abc_val=tetrahedron_volume(ABv,ACv,AEv)
        v_e_a1_val=(k-1)*v_e_abc_val
        v_e_bc_val=2*(k-1)*v_e_abc_val
        if c_label == "V_{E.ABC}":
            addd(f"Thể tích: \\( V_{{E.ABC}} = \\tfrac{{1}}{{6}}|[ \\overrightarrow{{AB}}, \\overrightarrow{{AC}} ] \\cdot \\overrightarrow{{AE}} | = {fmt_decimal(v_e_abc_val)} \\).")
        elif c_label == "V_{E.A'B'C'}":
            addd("Ta có quan hệ: \\( V_{E.A'B'C'} = (k-1)\\,V_{E.ABC} \\).")
            addd(f"Với \\( V_{{E.ABC}} = {fmt_decimal(v_e_abc_val)} \\) suy ra \\( V_{{E.A'B'C'}} = {fmt_decimal(v_e_a1_val)} \\).")
        else:
            addd("Ta có quan hệ: \\( V_{E.B'C'BC} = 2(k-1)\\,V_{E.ABC} \\).")
            addd(f"Với \\( V_{{E.ABC}} = {fmt_decimal(v_e_abc_val)} \\) suy ra \\( V_{{E.B'C'BC}} = {fmt_decimal(v_e_bc_val)} \\).")
        addd(f"Kết quả đúng: \\({c_label} = {c_tex_correct} \\).")
        # d
        addd("Phần d):")
        # Tạo biểu thức symbolic cho pháp tuyến (không qua số thập phân)
        def format_symbolic_term(coeff, var=""):
            """Format một thành phần dạng coeff*var."""
            if coeff == 0:
                return "0"
            elif coeff == 1:
                return var if var else "1"
            elif coeff == -1:
                return f"-{var}" if var else "-1"
            else:
                return f"{coeff}{var}" if var else str(coeff)
        
        if d_type=='angle1':
            # nEBC = (a*sqrt(3)*z, a*z, (k-1)*a*a*sqrt(3))
            n2_x = format_symbolic_term(a*z, "\\sqrt{3}")      # az√3
            n2_y = format_symbolic_term(a*z)                   # az  
            n2_z = format_symbolic_term((k-1)*a*a, "\\sqrt{3}") # (k-1)a²√3
            addd(f"Tìm pháp tuyến của các mặt phẳng:")
            addd(f"- Mặt phẳng (ABC): pháp tuyến \\(\\vec{{n_1}} = (0,0,1)\\)")
            addd(f"- Mặt phẳng (EBC): từ 3 điểm E, B, C, tính \\(\\vec{{n_2}} = \\overrightarrow{{EB}} \\times \\overrightarrow{{EC}}\\)")
            addd(f"\\(\\vec{{n_2}} = ({n2_x},{n2_y},{n2_z})\\)")
            addd(f"Công thức góc: \\(\\cos\\alpha = \\frac{{|\\vec{{n_1}} \\cdot \\vec{{n_2}}|}}{{|\\vec{{n_1}}| \\cdot |\\vec{{n_2}}|}}\\)")
            computed_angle = d_angle if d_angle is not None else math.degrees(math.acos(clamp(d_val,-1.0,1.0)))
            addd(f"Góc giữa hai mặt phẳng: \\( \\alpha \\approx {fmt_angle_one_decimal(computed_angle)}^\\circ\\).")
        elif d_type=='angle2':
            # nEA1 = (a*sqrt(3)*z, (k-1)*a*z, a*a*sqrt(3))
            n2_x = format_symbolic_term(a*z, "\\sqrt{3}")        # az√3
            n2_y = format_symbolic_term((k-1)*a*z)               # (k-1)az
            n2_z = format_symbolic_term(a*a, "\\sqrt{3}")        # a²√3
            addd(f"Tìm pháp tuyến của các mặt phẳng:")
            addd(f"- Mặt phẳng (ACC'A'): pháp tuyến \\(\\vec{{n_1}} = (\\sqrt{3},1,0)\\)")
            addd(f"- Mặt phẳng (EA'B): từ 3 điểm E, A', B, tính \\(\\vec{{n_2}} = \\overrightarrow{{EA'}} \\times \\overrightarrow{{EB}}\\)")
            addd(f"\\(\\vec{{n_2}} = ({n2_x},{n2_y},{n2_z})\\)")
            addd(f"Công thức góc: \\(\\cos\\alpha = \\frac{{|\\vec{{n_1}} \\cdot \\vec{{n_2}}|}}{{|\\vec{{n_1}}| \\cdot |\\vec{{n_2}}|}}\\)")
            computed_angle = d_angle if d_angle is not None else math.degrees(math.acos(clamp(d_val,-1.0,1.0)))
            addd(f"Góc giữa hai mặt phẳng: \\( \\alpha \\approx {fmt_angle_one_decimal(computed_angle)}^\\circ\\).")
        elif d_type=='dist1':
            n_x = format_symbolic_term(a*z, "\\sqrt{3}")
            n_y = format_symbolic_term(a*z)
            n_z = format_symbolic_term((k-1)*a*a, "\\sqrt{3}")
            addd(f"Tìm phương trình mặt phẳng (EBC):")
            addd(f"Bước 1: Tính pháp tuyến từ tích có hướng \\(\\overrightarrow{{EB}} \\times \\overrightarrow{{EC}}\\)")
            addd(f"Pháp tuyến: \\(\\vec{{n}} = ({n_x},{n_y},{n_z})\\)")
            addd(f"Bước 2: Thế điểm E vào phương trình để tìm hệ số tự do d₀")
            addd(f"Bước 3: Áp dụng công thức khoảng cách từ điểm đến mặt phẳng:")
            addd(f"\\(d(A;(EBC)) = \\frac{{|\\vec{{n}} \\cdot \\overrightarrow{{AE}} + d_0|}}{{|\\vec{{n}}|}}\\)")
            addd(f"Khoảng cách d(A; (EBC)) = {fmt_decimal(d_val)}.")
        else:
            # nA1BC = (a*sqrt(3)*z, a*z, a*a*sqrt(3))
            n_x = format_symbolic_term(a*z, "\\sqrt{3}")
            n_y = format_symbolic_term(a*z)
            n_z = format_symbolic_term(a*a, "\\sqrt{3}")
            addd(f"Tìm phương trình mặt phẳng (A'BC):")
            addd(f"Bước 1: Tính pháp tuyến từ tích có hướng \\(\\overrightarrow{{A'B}} \\times \\overrightarrow{{A'C}}\\)")
            addd(f"Pháp tuyến: \\(\\vec{{n}} = ({n_x},{n_y},{n_z})\\)")
            addd(f"Bước 2: Thế điểm A' vào phương trình để tìm hệ số tự do d₀")
            addd(f"Bước 3: Áp dụng công thức khoảng cách từ điểm đến mặt phẳng:")
            addd(f"\\(d(E;(A'BC)) = \\frac{{|\\vec{{n}} \\cdot \\overrightarrow{{A'E}} + d_0|}}{{|\\vec{{n}}|}}\\)")
            addd(f"Khoảng cách d(E; (A'BC)) = {fmt_decimal(d_val)}.")
        parts = a_text + b_text + c_text + d_text
        full = "\n".join([header, parts, "\n".join(lines_detail)])
        return full, [a_ok, b_ok, c_ok, d_ok]


class RightPrismGenerator:
    @classmethod
    def generate_single_question(cls, question_number: int = 1, correct_prob: float = 0.6, prism_type: Optional[int] = None) -> Tuple[str, List[bool]]:
        # prism_type: 1 = lăng trụ đáy tam giác vuông, 2 = đáy tam giác đều, None = random thật mỗi câu
        if prism_type == 1:
            return RightPrismQuestion(question_number=question_number, correct_prob=correct_prob).build(question_number)
        if prism_type == 2:
            return EquilateralPrismQuestion(question_number=question_number, correct_prob=correct_prob).build(question_number)
        # random thật khi không cố định loại
        if random.random() < 0.5:
            return RightPrismQuestion(question_number=question_number, correct_prob=correct_prob).build(question_number)
        return EquilateralPrismQuestion(question_number=question_number, correct_prob=correct_prob).build(question_number)

    @classmethod
    def generate_multiple_questions(cls, num_questions: int = 5, correct_prob: float = 0.6, prism_type: Optional[int] = None) -> List[str]:
        return [cls.generate_single_question(i, correct_prob=correct_prob, prism_type=prism_type)[0] for i in range(1, num_questions+1)]

    @staticmethod
    def create_latex_document(questions_data, title: str = "Bài tập Lăng trụ đứng") -> str:
        header = (
            "\\documentclass[a4paper,12pt]{article}\n"
            "\\usepackage{amsmath,amssymb,mathtools}\n"
            "\\usepackage{geometry}\n"
            "\\usepackage{microtype}\n"
            "\\geometry{a4paper, margin=1in}\n"
            "\\usepackage{polyglossia}\n"
            "\\setmainlanguage{vietnamese}\n"
            "\\setmainfont{TeX Gyre Termes}\n"
            "\\setlength{\\emergencystretch}{2em}\n"
            f"\\title{{{title}}}\n"
            "\\begin{document}\n"
            "\\maketitle\n"
        )
        footer = "\n\\end{document}\n"
        body = "\n\n".join(questions_data)
        return header + body + footer

    @classmethod
    def create_latex_file(cls, questions_data, filename: str = "hinhlangtrudung_questions.tex", title: str = "Bài tập Lăng trụ đứng") -> str:
        latex_content = cls.create_latex_document(questions_data, title)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        print(f"Đã tạo file: {filename}")
        return filename


def main():
    """CLI (random thật, không seed):
    Cách dùng:
        python hinhlangtrudung.py num_questions [prism_type] [correct_prob]
            prism_type: 1 = đáy tam giác vuông tại A, 2 = đáy tam giác đều, bỏ trống = random mỗi câu
            correct_prob: (0..1, mặc định 0.6)

    Seed đã loại bỏ và không còn cơ chế cố định nội bộ => mỗi lần chạy sinh dữ liệu khác.
    """
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 5
        prism_type: Optional[int] = None
        correct_prob: float = 0.6

        if len(sys.argv) > 2:
            arg2 = sys.argv[2]
            if arg2 in ('1','2'):
                prism_type = int(arg2)
            else:
                # nếu người dùng vẫn đưa một số (tưởng là seed cũ) -> coi như correct_prob
                try:
                    correct_prob = float(arg2)
                except ValueError:
                    pass
        if len(sys.argv) > 3:
            # tham số thứ ba nếu tồn tại là correct_prob
            try:
                correct_prob = float(sys.argv[3])
            except ValueError:
                pass

        correct_prob = clamp(correct_prob, 0.0, 1.0)
        gen = RightPrismGenerator()
        questions_data = gen.generate_multiple_questions(num_questions, correct_prob=correct_prob, prism_type=prism_type)
        if not questions_data:
            print("Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)
        title = ("Lăng trụ đứng (tam giác vuông)" if prism_type==1 else ("Lăng trụ đứng (tam giác đều)" if prism_type==2 else "Bài tập Lăng trụ đứng"))
        filename = gen.create_latex_file(questions_data, title=title)
        print(f"📄 Biên dịch bằng: xelatex {filename}")
        meta = []
        if prism_type in (1,2): meta.append(f"type={prism_type}")
        meta.append(f"correct_prob={correct_prob}")
        print("(" + ", ".join(meta) + ")")
        if prism_type not in (1,2):
            print("(Trạng thái: random cho loại lăng trụ. Dùng prism_type=1 hoặc 2 để cố định.)")
    except ValueError:
        print("❌ Lỗi: Tham số không hợp lệ (cần số / float)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
