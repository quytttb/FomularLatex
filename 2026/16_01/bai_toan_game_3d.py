import random
import sys
import os
import math
from string import Template
from fractions import Fraction
from typing import Tuple, List, Dict, Any

# ==================== CONFIGURATION & HELPERS ====================

# Type aliases
Point = Tuple[float, float, float]
Vector = Tuple[float, float, float]


def dot(u: Vector, v: Vector) -> float:
    """Dot product of two vectors"""
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


def cross(u: Vector, v: Vector) -> Vector:
    """Cross product of two vectors"""
    return (
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0]
    )


def norm_sq(v: Vector) -> float:
    """Squared norm of a vector"""
    return v[0] ** 2 + v[1] ** 2 + v[2] ** 2


def norm(v: Vector) -> float:
    """Norm of a vector"""
    return math.sqrt(norm_sq(v))


def sub_vec(a: Point, b: Point) -> Vector:
    """Vector from point b to point a: a - b"""
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def simplify_sqrt(n: int) -> Tuple[int, int]:
    """Simplify sqrt(n) to a*sqrt(b) where b is square-free. Returns (a, b)."""
    if n <= 0:
        return (0, 0)
    a = 1
    b = n
    for p in [2, 3, 5, 7, 11, 13]:
        while b % (p * p) == 0:
            a *= p
            b //= (p * p)
    return (a, b)


def format_sqrt(n: int) -> str:
    """Format sqrt(n) in LaTeX, simplifying if possible."""
    if n == 0:
        return "0"
    if n == 1:
        return "1"
    a, b = simplify_sqrt(n)
    if b == 1:
        return str(a)
    if a == 1:
        return f"\\sqrt{{{b}}}"
    return f"{a}\\sqrt{{{b}}}"


def format_frac_sqrt(num_coef: int, num_sqrt: int, denom: int) -> str:
    """Format (num_coef * sqrt(num_sqrt)) / denom in LaTeX."""
    from math import gcd
    
    # Simplify the sqrt first
    a, b = simplify_sqrt(num_sqrt)
    num_coef *= a
    
    # Simplify the fraction
    g = gcd(abs(num_coef), denom)
    num_coef //= g
    denom //= g
    
    if denom == 1:
        if b == 1:
            return str(num_coef)
        if num_coef == 1:
            return f"\\sqrt{{{b}}}"
        if num_coef == -1:
            return f"-\\sqrt{{{b}}}"
        return f"{num_coef}\\sqrt{{{b}}}"
    
    if b == 1:
        return f"\\dfrac{{{num_coef}}}{{{denom}}}"
    
    if num_coef == 1:
        return f"\\dfrac{{\\sqrt{{{b}}}}}{{{denom}}}"
    if num_coef == -1:
        return f"-\\dfrac{{\\sqrt{{{b}}}}}{{{denom}}}"
    return f"\\dfrac{{{num_coef}\\sqrt{{{b}}}}}{{{denom}}}"


def format_fraction(value: float) -> str:
    """Format a float as a LaTeX fraction if it's a simple fraction."""
    from fractions import Fraction
    
    # Handle special cases
    if value == 0:
        return "0"
    if value == int(value):
        return str(int(value))
    
    # Try to convert to a simple fraction with higher limit
    frac = Fraction(value).limit_denominator(1000)
    
    # Check if it's a reasonably good approximation (tolerance 0.001)
    if abs(float(frac) - value) < 0.001:
        if frac.denominator == 1:
            return str(frac.numerator)
        if frac.numerator < 0:
            return f"-\\dfrac{{{abs(frac.numerator)}}}{{{frac.denominator}}}"
        return f"\\dfrac{{{frac.numerator}}}{{{frac.denominator}}}"
    
    # Fallback to decimal
    return f"{value:.4f}".rstrip('0').rstrip('.')


def format_chord_value(chord: float, R: float, sin_phi: float) -> str:
    """Format chord = 2*R*sin(phi) as a nice LaTeX expression."""
    # chord = 2 * R * sin_phi
    # Try to express as fraction or sqrt
    
    chord_sq = chord * chord
    
    # Check if chord^2 is a nice integer
    if abs(chord_sq - round(chord_sq)) < 0.0001:
        return format_sqrt(int(round(chord_sq)))
    
    # Check if chord = 2*sqrt(n) form
    if abs(chord_sq / 4 - round(chord_sq / 4)) < 0.0001:
        inner = int(round(chord_sq / 4))
        if inner == 1:
            return "2"
        return f"2\\sqrt{{{inner}}}"
    
    # Try fraction form
    return format_fraction(chord)


def format_term(coef: int, var: str, first: bool = False) -> str:
    """Format a term like 2x, -3y, +z, etc."""
    if coef == 0:
        return ""
    
    sign = "" if first else ("+" if coef > 0 else "")
    
    if abs(coef) == 1:
        if coef == 1:
            return f"{sign}{var}" if not first else var
        else:
            return f"-{var}"
    
    return f"{sign}{coef}{var}"


def format_plane_eq(a: int, b: int, c: int, d: int) -> str:
    """Format plane equation ax + by + cz + d = 0"""
    terms = []
    
    # x term
    if a != 0:
        if a == 1:
            terms.append("x")
        elif a == -1:
            terms.append("-x")
        else:
            terms.append(f"{a}x")
    
    # y term
    if b != 0:
        if not terms:
            if b == 1:
                terms.append("y")
            elif b == -1:
                terms.append("-y")
            else:
                terms.append(f"{b}y")
        else:
            if b == 1:
                terms.append("+y")
            elif b == -1:
                terms.append("-y")
            elif b > 0:
                terms.append(f"+{b}y")
            else:
                terms.append(f"{b}y")
    
    # z term
    if c != 0:
        if not terms:
            if c == 1:
                terms.append("z")
            elif c == -1:
                terms.append("-z")
            else:
                terms.append(f"{c}z")
        else:
            if c == 1:
                terms.append("+z")
            elif c == -1:
                terms.append("-z")
            elif c > 0:
                terms.append(f"+{c}z")
            else:
                terms.append(f"{c}z")
    
    # constant term
    if d != 0:
        if d > 0:
            terms.append(f"+{d}")
        else:
            terms.append(f"{d}")
    
    return "".join(terms) + "=0"


def format_sphere_eq(cx: int, cy: int, cz: int, r_sq: int) -> str:
    """
    Format sphere equation in expanded form: x^2 + y^2 + z^2 + Dx + Ey + Fz + G = 0
    where center is (cx, cy, cz) and r^2 = r_sq
    D = -2cx, E = -2cy, F = -2cz, G = cx^2 + cy^2 + cz^2 - r_sq
    """
    D = -2 * cx
    E = -2 * cy
    F = -2 * cz
    G = cx * cx + cy * cy + cz * cz - r_sq
    
    result = "x^2+y^2+z^2"
    
    if D != 0:
        if D > 0:
            result += f"+{D}x"
        else:
            result += f"{D}x"
    
    if E != 0:
        if E > 0:
            result += f"+{E}y"
        else:
            result += f"{E}y"
    
    if F != 0:
        if F > 0:
            result += f"+{F}z"
        else:
            result += f"{F}z"
    
    if G != 0:
        if G > 0:
            result += f"+{G}"
        else:
            result += f"{G}"
    
    return result + "=0"


def format_vector(v: Vector) -> str:
    """Format vector as (a; b; c)"""
    return f"({v[0]}; {v[1]}; {v[2]})"


def format_point(p: Point) -> str:
    """Format point as (a; b; c)"""
    return f"({p[0]}; {p[1]}; {p[2]})"


def create_latex_document(content: str) -> str:
    return r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage{enumitem}
\usepackage{tikz}
\usetikzlibrary{calc,angles,quotes,intersections}
\begin{document}
""" + content + r"\end{document}"


# ==================== PRESETS ====================
# Each preset contains validated parameters that produce nice numbers
# All presets are validated to ensure:
# - d(I, P) > R (sphere doesn't intersect plane)
# - Nice integer or simple fraction values
# Format: {
#   'plane': (a, b, c, d),  # ax + by + cz + d = 0
#   'sphere_center': (cx, cy, cz),
#   'sphere_radius_sq': r^2,
#   'direction': (ux, uy, uz),
#   'context': 'game context description'
# }

# Preset 1: d(I,P) = |-1+4+2-3|/3 = 2/3... need better
# Using I=(-1,2,1), P: x-2y+2z-3=0 => d = |-1-4+2-3|/3 = 6/3 = 2 > R=1 ✓
PRESET_1 = {
    'plane': (1, -2, 2, -3),
    'sphere_center': (-1, 2, 1),
    'sphere_radius_sq': 1,
    'direction': (1, 0, 1),
    'context': 'bắn súng nhắm vào mục tiêu di động'
}

# Preset 2: I=(3,4,2), P: 2x+y-2z-6=0 => d=|6+4-4-6|/3 = 0... bad
# Try I=(3,2,0), P: 2x+2y+z-18=0 => d=|6+4+0-18|/3 = 8/3 > R=1 ✓
PRESET_2 = {
    'plane': (2, 2, 1, -18),
    'sphere_center': (3, 2, 0),
    'sphere_radius_sq': 1,
    'direction': (1, 1, 0),
    'context': 'thu thập vật phẩm trên quỹ đạo'
}

# Preset 3: I=(2,1,1), P: x+2y+2z-9=0 => d=|2+2+2-9|/3 = 3/3 = 1 = R... tangent
# Try P: x+2y+2z-12=0 => d=|2+2+2-12|/3 = 6/3 = 2 > R=1 ✓
# Check dot(u, n): u=(2,-1,0), n=(1,2,2) => 2-2+0 = 0... bad! Change u
# New u=(1,1,1): dot = 1+2+2 = 5 ≠ 0 ✓
PRESET_3 = {
    'plane': (1, 2, 2, -12),
    'sphere_center': (2, 1, 1),
    'sphere_radius_sq': 1,
    'direction': (1, 1, 1),
    'context': 'điều khiển drone bay qua chướng ngại vật'
}

# Preset 4: I=(1,0,1), P: 2x-y+2z-4=0 => d=|2-0+2-4|/3 = 0... bad
# Try P: 2x-y+2z-10=0 => d=|2-0+2-10|/3 = 6/3 = 2 > R=1 ✓
PRESET_4 = {
    'plane': (2, -1, 2, -10),
    'sphere_center': (1, 0, 1),
    'sphere_radius_sq': 1,
    'direction': (1, 2, 0),
    'context': 'bắn tia laser vào khiên năng lượng'
}

# Preset 5: I=(1,1,1), P: x+y+z-6=0 => d=|1+1+1-6|/√3 = 3/√3 = √3 ≈ 1.73 > R=1 ✓
PRESET_5 = {
    'plane': (1, 1, 1, -6),
    'sphere_center': (1, 1, 1),
    'sphere_radius_sq': 1,
    'direction': (1, -1, 0),
    'context': 'phóng tên lửa vào mục tiêu'
}

# Preset 6: I=(2,1,0), P: 2x+2y+z-8=0 => d=|4+2+0-8|/3 = 2/3 < R=1... bad
# Try P: 2x+2y+z-14=0 => d=|4+2+0-14|/3 = 8/3 ≈ 2.67 > R=1 ✓
PRESET_6 = {
    'plane': (2, 2, 1, -14),
    'sphere_center': (2, 1, 0),
    'sphere_radius_sq': 1,
    'direction': (1, 0, 2),
    'context': 'điều khiển robot né tránh bom'
}

# Preset 7: I=(0,1,1), P: x-y+2z-2=0 => d=|0-1+2-2|/√6 = 1/√6 ≈ 0.41 < R=1... bad
# Try P: x-y+2z-8=0 => d=|0-1+2-8|/√6 = 7/√6 ≈ 2.86 > R=1 ✓
PRESET_7 = {
    'plane': (1, -1, 2, -8),
    'sphere_center': (0, 1, 1),
    'sphere_radius_sq': 1,
    'direction': (2, 1, 1),
    'context': 'bắn cung vào mục tiêu bay'
}

# Preset 8: I=(1,1,1), P: 3x-2y+z-6=0 => d=|3-2+1-6|/√14 = 4/√14 ≈ 1.07 > R=1 ✓
PRESET_8 = {
    'plane': (3, -2, 1, -6),
    'sphere_center': (1, 1, 1),
    'sphere_radius_sq': 1,
    'direction': (1, 1, 1),
    'context': 'phóng phi tiêu vào bia di động'
}

# Preset 9: I=(1,0,2), P: x+2y-2z-3=0 => d=|1+0-4-3|/3 = 6/3 = 2 > R=1 ✓
PRESET_9 = {
    'plane': (1, 2, -2, -3),
    'sphere_center': (1, 0, 2),
    'sphere_radius_sq': 1,
    'direction': (2, 0, 1),
    'context': 'bắn pháo sáng vào vùng tối'
}

# Preset 10: I=(1,2,2), P: 2x+y+2z-10=0 => d=|2+2+4-10|/3 = 2/3 < R=1... bad
# Try P: 2x+y+2z-16=0 => d=|2+2+4-16|/3 = 8/3 ≈ 2.67 > R=1 ✓
PRESET_10 = {
    'plane': (2, 1, 2, -16),
    'sphere_center': (1, 2, 2),
    'sphere_radius_sq': 1,
    'direction': (1, -1, 1),
    'context': 'điều khiển vệ tinh thu tín hiệu'
}

# Preset 11: I=(0,-1,1), P: x-2y-2z+3=0 => d=|0+2-2+3|/3 = 3/3 = 1 = R... tangent
# Try P: x-2y-2z+9=0 => d=|0+2-2+9|/3 = 9/3 = 3 > R=1 ✓
PRESET_11 = {
    'plane': (1, -2, -2, 9),
    'sphere_center': (0, -1, 1),
    'sphere_radius_sq': 1,
    'direction': (0, 1, 1),
    'context': 'bắn đạn vào quái vật'
}

# Preset 12: I=(1,0,1), P: 2x-2y+z-5=0 => d=|2-0+1-5|/3 = 2/3 < R=1... bad
# Try P: 2x-2y+z-9=0 => d=|2-0+1-9|/3 = 6/3 = 2 > R=1 ✓
PRESET_12 = {
    'plane': (2, -2, 1, -9),
    'sphere_center': (1, 0, 1),
    'sphere_radius_sq': 1,
    'direction': (1, 1, 2),
    'context': 'phóng lưới bắt địch'
}

# Preset 13: I=(1,1,0), P: x+y-2z-2=0 => d=|1+1-0-2|/√6 = 0... bad
# Try P: x+y-2z-8=0 => d=|1+1-0-8|/√6 = 6/√6 = √6 ≈ 2.45 > R=1 ✓
PRESET_13 = {
    'plane': (1, 1, -2, -8),
    'sphere_center': (1, 1, 0),
    'sphere_radius_sq': 1,
    'direction': (1, -1, 1),
    'context': 'bắn súng điện vào robot'
}

# Preset 14: I=(1,1,1), P: 2x+y+z-6=0 => d=|2+1+1-6|/√6 = 2/√6 ≈ 0.82 < R=1... bad
# Try P: 2x+y+z-10=0 => d=|2+1+1-10|/√6 = 6/√6 = √6 ≈ 2.45 > R=1 ✓
PRESET_14 = {
    'plane': (2, 1, 1, -10),
    'sphere_center': (1, 1, 1),
    'sphere_radius_sq': 1,
    'direction': (0, 1, -1),
    'context': 'phóng tia đông lạnh'
}

# Preset 15: I=(0,0,1), P: x-y-z+1=0 => d=|0-0-1+1|/√3 = 0... bad
# Try P: x-y-z+7=0 => d=|0-0-1+7|/√3 = 6/√3 = 2√3 ≈ 3.46 > R=1 ✓
PRESET_15 = {
    'plane': (1, -1, -1, 7),
    'sphere_center': (0, 0, 1),
    'sphere_radius_sq': 1,
    'direction': (1, 1, 0),
    'context': 'bắn pháo hoa vào bầu trời'
}

# Preset 16: I=(1,1,0), P: 2x+2y-z-6=0 => d=|2+2-0-6|/3 = 2/3 < R=1... bad
# Try P: 2x+2y-z-12=0 => d=|2+2-0-12|/3 = 8/3 ≈ 2.67 > R=1 ✓
PRESET_16 = {
    'plane': (2, 2, -1, -12),
    'sphere_center': (1, 1, 0),
    'sphere_radius_sq': 1,
    'direction': (1, 0, 1),
    'context': 'điều khiển máy bay không người lái'
}

# Preset 17: I=(1,1,2), P: x+2y+z-6=0 => d=|1+2+2-6|/√6 = 1/√6 ≈ 0.41 < R=1... bad
# Try P: x+2y+z-12=0 => d=|1+2+2-12|/√6 = 7/√6 ≈ 2.86 > R=1 ✓
PRESET_17 = {
    'plane': (1, 2, 1, -12),
    'sphere_center': (1, 1, 2),
    'sphere_radius_sq': 1,
    'direction': (2, -1, 1),
    'context': 'bắn súng bắn tỉa'
}

# Preset 18: I=(0,1,-1), P: 2x-y-2z+2=0 => d=|0-1+2+2|/3 = 3/3 = 1 = R... tangent
# Try P: 2x-y-2z+8=0 => d=|0-1+2+8|/3 = 9/3 = 3 > R=1 ✓
PRESET_18 = {
    'plane': (2, -1, -2, 8),
    'sphere_center': (0, 1, -1),
    'sphere_radius_sq': 1,
    'direction': (1, 2, 1),
    'context': 'phóng móc câu vào tường'
}

# Preset 19: I=(2,2,1), P: x+y+2z-8=0 => d=|2+2+2-8|/√6 = 2/√6 ≈ 0.82 < R=1... bad
# Try P: x+y+2z-14=0 => d=|2+2+2-14|/√6 = 8/√6 ≈ 3.27 > R=1 ✓
PRESET_19 = {
    'plane': (1, 1, 2, -14),
    'sphere_center': (2, 2, 1),
    'sphere_radius_sq': 1,
    'direction': (1, -1, 0),
    'context': 'bắn đạn xuyên giáp'
}

# Preset 20: I=(1,1,-1), P: 2x+y-z-4=0 => d=|2+1+1-4|/√6 = 0... bad
# Try P: 2x+y-z-10=0 => d=|2+1+1-10|/√6 = 6/√6 = √6 ≈ 2.45 > R=1 ✓
PRESET_20 = {
    'plane': (2, 1, -1, -10),
    'sphere_center': (1, 1, -1),
    'sphere_radius_sq': 1,
    'direction': (1, 0, 2),
    'context': 'phóng lựu đạn vào boongke'
}

ALL_PRESETS = [
    PRESET_1, PRESET_2, PRESET_3, PRESET_4, PRESET_5,
    PRESET_6, PRESET_7, PRESET_8, PRESET_9, PRESET_10,
    PRESET_11, PRESET_12, PRESET_13, PRESET_14, PRESET_15,
    PRESET_16, PRESET_17, PRESET_18, PRESET_19, PRESET_20
]


# ==================== TEMPLATES ====================

TEMPLATE_Q = Template(
    r"""
Câu ${idx}: Trong một mô hình game 3D, với hệ trục tọa độ thích hợp, người chơi cùng với khẩu súng của anh ta được mô phỏng như một chất điểm di chuyển trên mặt phẳng \((P): ${plane_eq}\) và nhắm ${context} trên mặt cầu \((S)\) có phương trình \(${sphere_eq}\). Người chơi vẫn có thể bắn trúng mục tiêu nếu nó di chuyển trên bán cầu khuất phía sau tầm nhìn. Sau khi trò chơi bắt đầu, anh ta quyết định nhắm bắn theo phương vectơ \(\vec{u}=${direction_vec}\).

Các mệnh đề sau đúng hay sai?

${label_a}) Mặt phẳng \((P)\) và mặt cầu \((S)\) không có điểm chung.

${label_b}) Người chơi đứng ở vị trí giao điểm của \((P)\) và \(Ox\), khoảng cách từ tâm quả cầu đến đường bay viên đạn bằng \(${prop_b_val}\).

${label_c}) Khoảng cách nhỏ nhất từ vị trí người bắn đến mục tiêu bằng \(${prop_c_val}\).

${label_d}) Khi người chơi bắn vào điểm xa nhất của mặt cầu thì đường đạn sẽ cắt mặt cầu theo một dây cung có độ dài là \(${prop_d_val}\).
"""
)

TEMPLATE_SOL = Template(
    r"""
Lời giải:

a) Mệnh đề ${ans_a}.

Ta có \(d(I,(P))=\dfrac{|${dist_numerator}|}{${dist_denom}}=${dist_IP}\); ${dist_compare_text}; do đó \((P)\) và mặt cầu \((S)\) ${intersection_text}.

b) Mệnh đề ${ans_b}.

Giao điểm của \((P)\) và \(Ox\) là điểm \(M_0${player_pos}\) \(\Rightarrow \overrightarrow{IM_0}=${vec_IM}\); \([\overrightarrow{IM_0}, \vec{u}]=${cross_product}\).

Khoảng cách từ \(I\) đến đường bay viên đạn là \(d=\dfrac{|[\overrightarrow{IM_0}, \vec{u}]|}{|\vec{u}|}=\dfrac{${cross_norm}}{${u_norm}}=${dist_I_to_line_true}\).

c) Mệnh đề ${ans_c}.

Gọi \(M\) thuộc \((P)\), \(N\) thuộc \((S)\) theo thứ tự là vị trí người chơi và vị trí mục tiêu đang bắn; \(H\) là hình chiếu của điểm \(N\) trên \((P)\).

\(MN\) hợp với \((P)\) một góc \(\varphi\) thỏa mãn \(\sin \varphi=\dfrac{|\vec{u} \cdot \vec{n}_P|}{|\vec{u}| \cdot |\vec{n}_P|}=\dfrac{|${dot_u_n}|}{${u_norm} \cdot ${n_norm}}=${sin_phi}\).

Xét tam giác \(MNH\) vuông tại \(H\), ta có \(\sin \varphi=\dfrac{NH}{MN} \Rightarrow MN=\dfrac{NH}{\sin \varphi}\) hay \(MN=${mn_formula} \cdot NH\).

Dễ thấy \(MN\) nhỏ nhất khi và chỉ khi \(NH\) nhỏ nhất; mà \(NH \leq d(I,(P))-R=${nh_min_calc}\).

Do đó \(MN\) nhỏ nhất bằng \(${min_dist_true}\); khi đó \(N, I, H\) nằm trên đường thẳng vuông góc với \((P)\).

d) Mệnh đề ${ans_d}.

Gọi giao điểm của \(MN\) với mặt cầu là \(P'\) và \(E\) là trung điểm của \(NP'\).

Ta có: \(\sin\varphi = \cos \widehat{HNM}=\dfrac{NE}{NI}\Rightarrow NE=NI \cdot \cos \widehat{HNM}=${ne_calc}\Rightarrow NP'=${chord_true}\).

\begin{center}
\begin{tikzpicture}[line join=round, line cap=round, >=stealth]
	% --- Định nghĩa các thông số ---
	\def\r{1.5} % Bán kính hình tròn (S)
	\def\h{1.5} % Khoảng cách từ đáy hình tròn đến mặt phẳng
	
	% --- Tọa độ các điểm chính ---
	\coordinate (H) at (0,0);
	\coordinate (I) at (0, {\h + \r});
	\coordinate (N) at (0, {\h + 2*\r});
	\coordinate (M) at (3.5, 0);
	
	% --- Vẽ mặt phẳng (P) ---
	\draw[fill=gray!10] (-1.5,-0.5) -- (4.5,-0.5) -- (5.5,1) -- (-0.5,1) -- cycle;
	\node at (-1.1, -0.2) {$$(P)$$};
	
	% --- Vẽ đường thẳng đứng (N-H) ---
	\draw[dashed] (N) -- (I);
	\draw[dashed] (I) -- (0, \h);
	\draw (0, \h) -- (H);
	
	% --- Vẽ đường nối N-M và H-M ---
	\draw[name path=lineNM] (N) -- (M);
	\draw (H) -- (M);
	
	% --- Vẽ hình tròn (S) ---
	\draw[thick, name path=circleS] (I) circle (\r);
	\node at (-1.1, {\h + \r}) {$$(S)$$};
	
	% --- Tìm giao điểm P của MN và đường tròn (S) ---
	\path [name intersections={of=lineNM and circleS, by={N_dummy, P}}];
	
	% --- Tìm trung điểm E của NP ---
	\coordinate (E) at ($$(N)!0.5!(P)$$);
	
	% --- Vẽ các đoạn thẳng yêu cầu ---
	\draw[dashed] (I) -- (E);
	\draw[dashed] (P) -- (I);
	
	% --- Vẽ các điểm và nhãn ---
	\fill (H) circle (1.5pt) node[left] {$$H$$};
	\fill (I) circle (1.5pt) node[left] {$$I$$};
	\fill (N) circle (1.5pt) node[above] {$$N$$};
	\fill (M) circle (1.5pt) node[below] {$$M$$};
	\fill (P) circle (1.5pt) node[right, xshift=2pt] {$$P'$$};
	\fill (E) circle (1.5pt) node[above right] {$$E$$};
	
	% --- Ký hiệu góc vuông ---
	\draw (0, 0.2) -- (0.2, 0.2) -- (0.2, 0);
	
	% Ký hiệu góc vuông tại E
	\pic [draw, angle radius=0.2cm] {right angle = I--E--N};
	
	% --- Ký hiệu góc phi tại M ---
	\pic [draw, "$$\varphi$$", angle radius=0.6cm, angle eccentricity=1.5] {angle = N--M--H};
	
	% --- Các nhãn số trên trục ---
	\node[left] at (0, {\h + 1.5*\r}) {$$R$$};
	\node[left] at (0, {\h + 0.5*\r}) {$$R$$};
	\node[left] at (0, {\h/2}) {$$d-R$$};
	
\end{tikzpicture}
\end{center}

Vậy a) ${ans_a}; b) ${ans_b}; c) ${ans_c} và d) ${ans_d}.
"""
)


# ==================== MAIN CLASS ====================

class Game3DQuestion:
    def __init__(self):
        # Plane (P): ax + by + cz + d = 0
        self.plane = (0, 0, 0, 0)  # (a, b, c, d)
        
        # Sphere (S): center I and radius R
        self.sphere_center = (0, 0, 0)  # I = (cx, cy, cz)
        self.sphere_radius_sq = 1  # R^2
        
        # Direction vector u
        self.direction = (0, 0, 0)
        
        # Player position M0 (intersection of P and Ox)
        self.player_pos = (0, 0, 0)
        
        # Game context
        self.context = ""
        
        # Results for 4 statements
        self.res_a = True
        self.res_b = True
        self.res_c = True
        self.res_d = True
        
        # Display values for propositions (may be true or distorted)
        self.prop_b_val = ""
        self.prop_c_val = ""
        self.prop_d_val = ""
        
        # True computed values
        self.true_values = {}
        
        # Selected preset
        self.preset = None

    def generate_parameters(self):
        """Generate parameters from a random preset."""
        self.preset = random.choice(ALL_PRESETS)
        
        self.plane = self.preset['plane']
        self.sphere_center = self.preset['sphere_center']
        self.sphere_radius_sq = self.preset['sphere_radius_sq']
        self.direction = self.preset['direction']
        self.context = self.preset['context']
        
        # Calculate player position: intersection of plane P and Ox axis
        # On Ox: y = 0, z = 0, so ax + d = 0 => x = -d/a
        a, b, c, d = self.plane
        if a != 0:
            x0 = -d / a
            self.player_pos = (x0, 0, 0)
        else:
            # If a = 0, plane doesn't intersect Ox properly, use default
            self.player_pos = (0, 0, 0)

    def solve(self) -> Dict[str, Any]:
        """Calculate all true values for the 4 statements."""
        a, b, c, d = self.plane
        I = self.sphere_center
        R_sq = self.sphere_radius_sq
        R = math.sqrt(R_sq)
        u = self.direction
        M0 = self.player_pos
        
        # Normal vector of plane
        n_P = (a, b, c)
        n_norm_sq = norm_sq(n_P)
        n_norm = math.sqrt(n_norm_sq)
        
        # a) Distance from I to plane P
        # d(I, P) = |a*Ix + b*Iy + c*Iz + d| / sqrt(a^2 + b^2 + c^2)
        numerator = a * I[0] + b * I[1] + c * I[2] + d
        dist_I_P = abs(numerator) / n_norm
        
        # Statement a is true if dist_I_P > R (no intersection)
        no_intersection = dist_I_P > R
        
        # b) Distance from I to line through M0 with direction u
        # d = |IM0 × u| / |u|
        vec_IM = sub_vec(M0, I)  # M0 - I
        cross_IM_u = cross(vec_IM, u)
        cross_norm_sq = norm_sq(cross_IM_u)
        u_norm_sq = norm_sq(u)
        u_norm = math.sqrt(u_norm_sq)
        
        dist_I_to_line = math.sqrt(cross_norm_sq) / u_norm
        
        # c) Minimum distance from player to target
        # Angle phi between line MN and plane P: sin(phi) = |u · n| / (|u| * |n|)
        dot_u_n = dot(u, n_P)
        sin_phi = abs(dot_u_n) / (u_norm * n_norm)
        
        # MN = NH / sin(phi), and NH_min = d(I, P) - R
        NH_min = dist_I_P - R
        if sin_phi > 0:
            MN_min = NH_min / sin_phi
        else:
            MN_min = float('inf')
        
        # d) Chord length when bullet hits the farthest point
        # NE = NI * cos(phi) = R * sin(phi) (since angle at N)
        # Actually: sin(phi) = cos(angle HNM), and NE = NI * cos(HNM) where NI = R
        # NE = R * sin(phi), so chord NP' = 2 * NE = 2 * R * sin(phi)
        NE = R * sin_phi
        chord_length = 2 * NE
        
        self.true_values = {
            'dist_I_P': dist_I_P,
            'no_intersection': no_intersection,
            'vec_IM': vec_IM,
            'cross_IM_u': cross_IM_u,
            'cross_norm_sq': cross_norm_sq,
            'u_norm_sq': u_norm_sq,
            'dist_I_to_line': dist_I_to_line,
            'dot_u_n': dot_u_n,
            'sin_phi': sin_phi,
            'NH_min': NH_min,
            'MN_min': MN_min,
            'NE': NE,
            'chord_length': chord_length,
            'R': R,
            'n_norm_sq': n_norm_sq,
            'numerator': numerator,
        }
        
        return self.true_values

    def distort_and_set_props(self):
        """Set proposition values, with 50% chance of distortion for each."""
        tv = self.true_values
        R = tv['R']
        
        # A: No intersection - this is boolean, distort by negating statement
        if random.random() < 0.5:
            self.res_a = tv['no_intersection']
        else:
            self.res_a = not tv['no_intersection']
        
        # B: Distance from I to line
        dist_true = tv['dist_I_to_line']
        cross_norm_sq = tv['cross_norm_sq']
        u_norm_sq = tv['u_norm_sq']
        
        # True value as simplified sqrt fraction
        # dist = sqrt(cross_norm_sq) / sqrt(u_norm_sq) = sqrt(cross_norm_sq / u_norm_sq)
        # = sqrt(cross_norm_sq) / sqrt(u_norm_sq)
        
        if random.random() < 0.5:
            self.res_b = True
            # Format true value
            self.prop_b_val = format_frac_sqrt(1, int(cross_norm_sq), int(math.sqrt(u_norm_sq))) if u_norm_sq in [1, 4, 9] else format_frac_sqrt(1, int(cross_norm_sq * u_norm_sq), int(u_norm_sq))
            # Simplify: sqrt(cross_norm_sq) / sqrt(u_norm_sq)
            a_coef, a_sqrt = simplify_sqrt(int(cross_norm_sq))
            b_coef = int(math.sqrt(u_norm_sq)) if math.sqrt(u_norm_sq) == int(math.sqrt(u_norm_sq)) else 1
            if b_coef > 0:
                from math import gcd
                g = gcd(a_coef, b_coef)
                self.prop_b_val = format_frac_sqrt(a_coef // g, a_sqrt, b_coef // g)
            else:
                self.prop_b_val = format_sqrt(int(cross_norm_sq))
        else:
            self.res_b = False
            # Distort by changing numerator or denominator
            fake_cross_sq = int(cross_norm_sq) + random.choice([1, -1, 2, -2, 4])
            if fake_cross_sq <= 0:
                fake_cross_sq = int(cross_norm_sq) + 4
            a_coef, a_sqrt = simplify_sqrt(fake_cross_sq)
            b_coef = int(math.sqrt(u_norm_sq)) if math.sqrt(u_norm_sq) == int(math.sqrt(u_norm_sq)) else 1
            if b_coef > 0:
                self.prop_b_val = format_frac_sqrt(a_coef, a_sqrt, b_coef)
            else:
                self.prop_b_val = format_sqrt(fake_cross_sq)
        
        # C: Minimum distance MN
        MN_min = tv['MN_min']
        sin_phi = tv['sin_phi']
        NH_min = tv['NH_min']
        
        # Handle edge case where sin_phi is 0 or MN_min is infinity
        if MN_min == float('inf') or sin_phi == 0:
            self.res_c = True
            self.prop_c_val = "\\infty"
        elif random.random() < 0.5:
            self.res_c = True
            # Calculate exact form: NH_min / sin_phi
            # sin_phi = |dot_u_n| / (|u| * |n|)
            # MN_min = NH_min * |u| * |n| / |dot_u_n|
            dot_val = abs(tv['dot_u_n'])
            u_n = math.sqrt(tv['u_norm_sq'])
            n_n = math.sqrt(tv['n_norm_sq'])
            
            # MN_min = NH_min / sin_phi = NH_min * u_n * n_n / dot_val
            if MN_min < 10:
                # Try to get a nice form
                mn_sq = MN_min * MN_min
                if abs(mn_sq - round(mn_sq)) < 0.0001:
                    self.prop_c_val = format_sqrt(int(round(mn_sq)))
                else:
                    self.prop_c_val = f"{MN_min:.4f}".rstrip('0').rstrip('.')
            else:
                self.prop_c_val = f"{MN_min:.2f}"
        else:
            self.res_c = False
            # Distort
            fake_MN = MN_min * random.choice([1.5, 2, 0.5, 3])
            fake_sq = fake_MN * fake_MN
            if fake_sq < 10000 and abs(fake_sq - round(fake_sq)) < 0.1:
                self.prop_c_val = format_sqrt(int(round(fake_sq)))
            else:
                self.prop_c_val = f"{fake_MN:.2f}"
        
        # D: Chord length
        chord = tv['chord_length']
        R = tv['R']
        
        if random.random() < 0.5:
            self.res_d = True
            self.prop_d_val = format_chord_value(chord, R, sin_phi)
        else:
            self.res_d = False
            fake_chord = chord * random.choice([1.5, 2, 0.5])
            self.prop_d_val = format_chord_value(fake_chord, R, sin_phi)

    @staticmethod
    def label_with_star(letter: str, is_true: bool) -> str:
        return f"*{letter}" if is_true else f"{letter}"

    def generate_question(self, idx: int) -> str:
        """Generate complete question with solution."""
        self.generate_parameters()
        self.solve()
        self.distort_and_set_props()
        
        tv = self.true_values
        a, b, c, d = self.plane
        I = self.sphere_center
        R = tv['R']
        u = self.direction
        M0 = self.player_pos
        
        # Format plane equation
        plane_eq = format_plane_eq(a, b, c, d)
        
        # Format sphere equation
        sphere_eq = format_sphere_eq(int(I[0]), int(I[1]), int(I[2]), self.sphere_radius_sq)
        
        # Format direction vector
        direction_vec = format_vector(u)
        
        # Calculate intermediate values for solution
        vec_IM = tv['vec_IM']
        cross_IM_u = tv['cross_IM_u']
        
        # Distance calculation details
        numerator = tv['numerator']
        n_norm_sq = tv['n_norm_sq']
        dist_I_P = tv['dist_I_P']
        
        # Format distance from I to P
        dist_denom = format_sqrt(int(n_norm_sq))
        if dist_I_P == int(dist_I_P):
            dist_IP_str = str(int(dist_I_P))
        else:
            dist_IP_str = f"{dist_I_P:.4f}".rstrip('0').rstrip('.')
        
        # Comparison with R
        if dist_I_P > R:
            dist_compare = f"{dist_IP_str} > R = {int(R) if R == int(R) else R}"
            intersection_text = "không có điểm chung"
        elif dist_I_P == R:
            dist_compare = f"{dist_IP_str} = R"
            intersection_text = "tiếp xúc nhau"
        else:
            dist_compare = f"{dist_IP_str} < R = {int(R) if R == int(R) else R}"
            intersection_text = "cắt nhau"
        
        # Format cross product and norms for solution
        cross_norm_sq = tv['cross_norm_sq']
        u_norm_sq = tv['u_norm_sq']
        
        cross_norm_str = format_sqrt(int(cross_norm_sq))
        u_norm_str = format_sqrt(int(u_norm_sq))
        
        # True distance from I to line
        a_coef, a_sqrt = simplify_sqrt(int(cross_norm_sq))
        b_coef = int(math.sqrt(u_norm_sq)) if math.sqrt(u_norm_sq) == int(math.sqrt(u_norm_sq)) else 1
        if b_coef > 0:
            from math import gcd
            g = gcd(a_coef, b_coef)
            dist_I_to_line_true = format_frac_sqrt(a_coef // g, a_sqrt, b_coef // g)
        else:
            dist_I_to_line_true = format_sqrt(int(cross_norm_sq))
        
        # Sin phi calculation
        dot_u_n = tv['dot_u_n']
        sin_phi = tv['sin_phi']
        
        # Format sin_phi
        # sin_phi = |dot_u_n| / (sqrt(u_norm_sq) * sqrt(n_norm_sq))
        sin_num = abs(int(dot_u_n))
        sin_denom_sq = int(u_norm_sq * n_norm_sq)
        sin_denom_a, sin_denom_b = simplify_sqrt(sin_denom_sq)
        
        if sin_denom_b == 1:
            sin_phi_str = f"\\dfrac{{{sin_num}}}{{{sin_denom_a}}}"
        else:
            sin_phi_str = f"\\dfrac{{{sin_num}}}{{{sin_denom_a}\\sqrt{{{sin_denom_b}}}}}" if sin_denom_a > 1 else f"\\dfrac{{{sin_num}}}{{\\sqrt{{{sin_denom_b}}}}}"
        
        # Simplify if possible
        if sin_phi == 0.5:
            sin_phi_str = "\\dfrac{1}{2}"
        elif abs(sin_phi - math.sqrt(2)/2) < 0.0001:
            sin_phi_str = "\\dfrac{\\sqrt{2}}{2}"
        elif abs(sin_phi - math.sqrt(3)/2) < 0.0001:
            sin_phi_str = "\\dfrac{\\sqrt{3}}{2}"
        
        # MN formula coefficient
        # MN = NH / sin_phi, so coefficient is 1/sin_phi
        if abs(sin_phi - math.sqrt(2)/2) < 0.0001:
            mn_formula = "\\sqrt{2}"
        elif sin_phi == 0.5:
            mn_formula = "2"
        else:
            mn_formula = f"\\dfrac{{1}}{{{sin_phi_str}}}"
        
        # NH_min calculation
        NH_min = tv['NH_min']
        nh_min_str = f"{dist_IP_str} - {int(R) if R == int(R) else R} = {NH_min:.4f}".rstrip('0').rstrip('.')
        
        # Min distance true value
        MN_min = tv['MN_min']
        if MN_min == float('inf') or MN_min > 10000:
            min_dist_true = "\\infty"
        else:
            mn_sq = MN_min * MN_min
            if abs(mn_sq - round(mn_sq)) < 0.0001:
                min_dist_true = format_sqrt(int(round(mn_sq)))
            else:
                min_dist_true = f"{MN_min:.4f}".rstrip('0').rstrip('.')
        
        # NE and chord calculations
        NE = tv['NE']
        chord = tv['chord_length']
        
        # Format NE as fraction
        ne_str = format_fraction(NE)
        
        # Format chord as fraction or sqrt
        chord_true = format_chord_value(chord, R, tv['sin_phi'])
        
        params = {
            'idx': idx,
            'plane_eq': plane_eq,
            'sphere_eq': sphere_eq,
            'direction_vec': direction_vec,
            'context': self.context,
            
            'label_a': self.label_with_star('a', self.res_a == tv['no_intersection']),
            'label_b': self.label_with_star('b', self.res_b),
            'label_c': self.label_with_star('c', self.res_c),
            'label_d': self.label_with_star('d', self.res_d),
            
            'prop_b_val': self.prop_b_val,
            'prop_c_val': self.prop_c_val,
            'prop_d_val': self.prop_d_val,
            
            # Solution params
            'ans_a': "đúng" if self.res_a == tv['no_intersection'] else "sai",
            'ans_b': "đúng" if self.res_b else "sai",
            'ans_c': "đúng" if self.res_c else "sai",
            'ans_d': "đúng" if self.res_d else "sai",
            
            'dist_numerator': f"{int(a)}\\cdot({int(I[0])}){'+' if b >= 0 else ''}{int(b)}\\cdot({int(I[1])}){'+' if c >= 0 else ''}{int(c)}\\cdot({int(I[2])}){'+' if d >= 0 else ''}{int(d)}",
            'dist_denom': dist_denom,
            'dist_IP': dist_IP_str,
            'dist_compare_text': dist_compare,
            'intersection_text': intersection_text,
            
            'player_pos': format_point((int(M0[0]) if M0[0] == int(M0[0]) else M0[0], int(M0[1]), int(M0[2]))),
            'vec_IM': format_vector((int(vec_IM[0]) if vec_IM[0] == int(vec_IM[0]) else vec_IM[0], int(vec_IM[1]), int(vec_IM[2]))),
            'cross_product': format_vector((int(cross_IM_u[0]), int(cross_IM_u[1]), int(cross_IM_u[2]))),
            'cross_norm': cross_norm_str,
            'u_norm': u_norm_str,
            'dist_I_to_line_true': dist_I_to_line_true,
            
            'dot_u_n': int(dot_u_n),
            'n_norm': format_sqrt(int(n_norm_sq)),
            'sin_phi': sin_phi_str,
            'mn_formula': mn_formula,
            'nh_min_calc': nh_min_str,
            'min_dist_true': min_dist_true,
            
            'ne_calc': ne_str,
            'chord_true': chord_true,
        }
        
        question = TEMPLATE_Q.substitute(params)
        solution = TEMPLATE_SOL.substitute(params)
        
        return f"{question}\n{solution}"


# ==================== MAIN ====================

def main():
    num_questions = 5
    if len(sys.argv) > 1:
        try:
            num_questions = max(1, int(sys.argv[1]))
        except ValueError:
            print("Tham số không hợp lệ, sử dụng mặc định 5 câu hỏi.")
    
    questions = []
    for i in range(num_questions):
        q = Game3DQuestion()
        questions.append(q.generate_question(i + 1))
        
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "bai_toan_game_3d.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong bai_toan_game_3d.tex")


if __name__ == "__main__":
    main()
