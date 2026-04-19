import argparse
import logging
import math
import random
import sys
from math import gcd
from typing import Any, Dict, List, Tuple


Point = Tuple[int, int, int]
Vector = Tuple[int, int, int]


def dot(u: Vector, v: Vector) -> int:
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


def cross(u: Vector, v: Vector) -> Vector:
    return (
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    )


def add(u: Point, v: Vector) -> Point:
    return u[0] + v[0], u[1] + v[1], u[2] + v[2]


def sub(u: Point, v: Point) -> Vector:
    return u[0] - v[0], u[1] - v[1], u[2] - v[2]


def scale(v: Vector, k: int) -> Vector:
    return v[0] * k, v[1] * k, v[2] * k


def norm_sq(v: Vector) -> int:
    return dot(v, v)


def gcd_multiple(values: Tuple[int, ...]) -> int:
    g = 0
    for value in values:
        if value != 0:
            g = gcd(g, abs(value)) if g else abs(value)
    return g or 1


def simplify_vector(v: Vector) -> Vector:
    g = gcd_multiple(v)
    return v[0] // g, v[1] // g, v[2] // g


def format_point(p: Point) -> str:
    return f"({p[0]};{p[1]};{p[2]})"


def append_linear_term(parts: List[str], coeff: int, text: str) -> None:
    if coeff == 0:
        return
    if not parts:
        if coeff == 1:
            parts.append(text)
        elif coeff == -1:
            parts.append(f"-{text}")
        else:
            parts.append(f"{coeff}{text}")
    else:
        if coeff == 1:
            parts.append(f"+ {text}")
        elif coeff == -1:
            parts.append(f"- {text}")
        elif coeff > 0:
            parts.append(f"+ {coeff}{text}")
        else:
            parts.append(f"- {abs(coeff)}{text}")


def append_constant(parts: List[str], value: int) -> None:
    if value == 0:
        return
    if not parts:
        parts.append(str(value))
    elif value > 0:
        parts.append(f"+ {value}")
    else:
        parts.append(f"- {abs(value)}")


def format_plane_equation(a: int, b: int, c: int, d: int) -> str:
    parts: List[str] = []
    append_linear_term(parts, a, "x")
    append_linear_term(parts, b, "y")
    append_linear_term(parts, c, "z")
    append_constant(parts, d)
    if not parts:
        parts.append("0")
    return " ".join(parts) + " = 0"


def format_square_term(var: str, shift: int) -> str:
    if shift == 0:
        return f"{var}^2"
    if shift > 0:
        return f"({var} - {shift})^2"
    return f"({var} + {abs(shift)})^2"


def format_sphere_center_form(center: Point, radius_sq: int) -> str:
    term_x = format_square_term("x", center[0])
    term_y = format_square_term("y", center[1])
    term_z = format_square_term("z", center[2])
    return f"{term_x} + {term_y} + {term_z} = {radius_sq}"


def format_sphere_expanded(center: Point, radius_sq: int) -> str:
    a, b, c = center
    A = -2 * a
    B = -2 * b
    C = -2 * c
    D = a * a + b * b + c * c - radius_sq
    parts: List[str] = ["x^2 + y^2 + z^2"]
    append_linear_term(parts, A, "x")
    append_linear_term(parts, B, "y")
    append_linear_term(parts, C, "z")
    append_constant(parts, D)
    return " ".join(parts) + " = 0"


def format_param_line(base: Point, direction: Vector) -> str:
    rows: List[str] = []
    for name, b, d in zip(("x", "y", "z"), base, direction):
        if d == 0:
            rows.append(f"{name} = {b}")
        else:
            sign = "+" if d > 0 else "-"
            coeff = abs(d)
            if coeff == 1:
                term = "t"
            else:
                term = f"{coeff}t"
            rows.append(f"{name} = {b} {sign} {term}")
    joined = " \\\\ ".join(rows)
    return "\\begin{cases} " + joined + " \\end{cases}"


def format_canonical_line(base: Point, direction: Vector) -> str:
    parts: List[str] = []
    for name, b, d in zip(("x", "y", "z"), base, direction):
        if d == 0:
            continue
        if b == 0:
            numerator = name
        elif b > 0:
            numerator = f"{name} - {b}"
        else:
            numerator = f"{name} + {abs(b)}"
        if d == 1:
            parts.append(numerator)
        elif d == -1:
            parts.append(f"-({numerator})")
        else:
            parts.append(f"\\dfrac{{{numerator}}}{{{d}}}")
    return " = ".join(parts)


def format_linear_combination(coeffs: Tuple[int, int, int], symbols: Tuple[str, str, str]) -> str:
    parts: List[str] = []
    for coeff, symbol in zip(coeffs, symbols):
        append_linear_term(parts, coeff, symbol)
    return " ".join(parts) if parts else "0"


def format_affine_term(base: int, coefficient: int) -> str:
    if coefficient == 0:
        return str(base)
    if coefficient > 0:
        if coefficient == 1:
            return f"{base} + t"
        return f"{base} + {coefficient}t"
    if coefficient == -1:
        return f"{base} - t"
    return f"{base} - {abs(coefficient)}t"


def format_signed_product(coeff: int, expr: str, first: bool = False) -> str:
    if coeff == 0:
        return ""
    if first:
        if coeff == 1:
            return expr
        if coeff == -1:
            return f"-{expr}"
        return f"{coeff}{expr}"
    if coeff == 1:
        return f"+ {expr}"
    if coeff == -1:
        return f"- {expr}"
    if coeff > 0:
        return f"+ {coeff}{expr}"
    return f"- {abs(coeff)}{expr}"


def random_point(min_val: int = -4, max_val: int = 4) -> Point:
    return (
        random.randint(min_val, max_val),
        random.randint(min_val, max_val),
        random.randint(min_val, max_val),
    )


def random_nonzero_vector(min_val: int = -4, max_val: int = 4) -> Vector:
    for _ in range(200):
        v = random_point(min_val, max_val)
        if v != (0, 0, 0):
            return v
    return (1, 0, 0)


def perpendicular_vector(direction: Vector) -> Vector:
    candidates = [
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
        (1, 1, 0),
        (1, 0, 1),
        (0, 1, 1),
    ]
    for cand in candidates:
        v = cross(direction, cand)
        if v != (0, 0, 0):
            return simplify_vector(v)
    fallback = (direction[1], -direction[0], direction[2] if direction[2] != 0 else 1)
    return simplify_vector(fallback)


def format_line_expression(line_data: Dict[str, Any]) -> str:
    direction = line_data["direction"]
    # Chỉ dùng dạng chính tắc nếu cả 3 thành phần đều khác 0
    if line_data.get("style") == "canonical" and all(d != 0 for d in direction):
        expr = format_canonical_line(line_data["point"], direction)
        if expr:
            return expr
    return format_param_line(line_data["point"], direction)


def format_sphere_expression(sphere_data: Dict[str, Any]) -> str:
    if sphere_data["type"] == "center":
        return format_sphere_center_form(sphere_data["center"], sphere_data["radius_sq"])
    return format_sphere_expanded(sphere_data["center"], sphere_data["radius_sq"])


def pick_wrong_integer(true_value: int) -> int:
    deltas = [i for i in range(-7, 8) if i != 0]
    random.shuffle(deltas)
    for delta in deltas:
        candidate = true_value + delta
        if candidate != true_value:
            return candidate
    return true_value + 5


def sqrt_term(value: int) -> str:
    if value == 1:
        return "1"
    return f"\\sqrt{{{value}}}"


def angle_denominator(norm_u: int, norm_v: int) -> str:
    term_u = sqrt_term(norm_u)
    term_v = sqrt_term(norm_v)
    if term_u == "1" and term_v == "1":
        return "1"
    if term_u == "1":
        return term_v
    if term_v == "1":
        return term_u
    return f"{term_u} \\cdot {term_v}"


def format_angle_expression(kind: str, numerator: int, norm_u: int, norm_v: int) -> str:
    denominator = angle_denominator(norm_u, norm_v)
    if denominator == "1":
        fraction = str(numerator)
    else:
        fraction = f"\\dfrac{{{numerator}}}{{{denominator}}}"
    if kind == "cos":
        return f"\\arccos\\left({fraction}\\right)"
    return f"\\arcsin\\left({fraction}\\right)"


def compute_angle_degree(kind: str, numerator: int, norm_a: int, norm_b: int) -> int:
    # kind: 'cos' or 'sin'; norms are squared lengths
    den = math.sqrt(max(0.0, float(norm_a))) * math.sqrt(max(0.0, float(norm_b)))
    if den == 0:
        return 0
    ratio = max(0.0, min(1.0, float(numerator) / den))
    rad = math.acos(ratio) if kind == "cos" else math.asin(ratio)
    return int(round(math.degrees(rad)))


def adjust_numerator(numerator: int, den_sq: int) -> int:
    limit = max(1, int(math.isqrt(den_sq)))
    candidates = [numerator + d for d in (-2, -1, 1, 2) if 0 <= numerator + d <= limit]
    for cand in candidates:
        if cand != numerator:
            return cand
    if numerator < limit:
        return numerator + 1
    return max(0, numerator - 1)


def distance(p1: Point, p2: Point) -> float:
    """Tính khoảng cách Euclid giữa 2 điểm."""
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    dz = p1[2] - p2[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def distance_sq(p1: Point, p2: Point) -> int:
    """Tính bình phương khoảng cách giữa 2 điểm."""
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    dz = p1[2] - p2[2]
    return dx * dx + dy * dy + dz * dz


def format_distance(d_sq: int) -> str:
    """Format khoảng cách từ bình phương khoảng cách (giữ căn hoặc số nguyên)."""
    if d_sq == 0:
        return "0"
    # Kiểm tra xem có phải số chính phương không
    root = int(math.isqrt(d_sq))
    if root * root == d_sq:
        return str(root)
    # Kiểm tra có thể rút gọn căn không
    for factor in range(2, int(math.isqrt(d_sq)) + 1):
        factor_sq = factor * factor
        if d_sq % factor_sq == 0:
            remainder = d_sq // factor_sq
            if remainder == 1:
                return str(factor)
            return f"{factor}\\sqrt{{{remainder}}}"
    return f"\\sqrt{{{d_sq}}}"


def project_point_to_plane(A: Point, n: Vector, d: int) -> Point:
    """Chiếu điểm A lên mặt phẳng n.x + d = 0."""
    # Khoảng cách từ A đến mặt phẳng: |n.A + d| / ||n||
    # Hình chiếu: A - (n.A + d) / ||n||^2 * n
    n_norm_sq = norm_sq(n)
    if n_norm_sq == 0:
        return A
    numerator = dot(n, A) + d
    # Để có tọa độ nguyên, ta nhân với n_norm_sq
    # H = A - (numerator / n_norm_sq) * n
    # => H = (n_norm_sq * A - numerator * n) / n_norm_sq
    scaled_A = scale(A, n_norm_sq)
    offset = scale(n, numerator)
    H_num = sub(scaled_A, offset)
    # H_num = (H_x * n_norm_sq, H_y * n_norm_sq, H_z * n_norm_sq)
    # Vì n_norm_sq có thể chia hết, ta sẽ làm tròn
    # Nhưng để đảm bảo nguyên, ta cần chọn n và A phù hợp
    # Tạm thời chia và làm tròn
    H = (H_num[0] // n_norm_sq, H_num[1] // n_norm_sq, H_num[2] // n_norm_sq)
    return H


def project_point_to_line(A: Point, P0: Point, u: Vector) -> Point:
    """Chiếu điểm A lên đường thẳng qua P0 với vector chỉ phương u."""
    # Vector từ P0 đến A
    PA = sub(A, P0)
    # Tham số t: t = (PA . u) / ||u||^2
    u_norm_sq = norm_sq(u)
    if u_norm_sq == 0:
        return P0
    proj_num = dot(PA, u)
    # Để có tọa độ nguyên, ta nhân với u_norm_sq
    # H = P0 + t * u = P0 + (proj_num / u_norm_sq) * u
    # => H = (u_norm_sq * P0 + proj_num * u) / u_norm_sq
    scaled_P0 = scale(P0, u_norm_sq)
    offset = scale(u, proj_num)
    H_num = add(scaled_P0, offset)
    # Chia và làm tròn
    H = (H_num[0] // u_norm_sq, H_num[1] // u_norm_sq, H_num[2] // u_norm_sq)
    return H


def distance_point_to_plane(A: Point, n: Vector, d: int) -> float:
    """Tính khoảng cách từ điểm A đến mặt phẳng n.x + d = 0."""
    n_norm = math.sqrt(float(norm_sq(n)))
    if n_norm == 0:
        return 0.0
    return abs(dot(n, A) + d) / n_norm


def distance_point_to_plane_sq(A: Point, n: Vector, d: int) -> int:
    """Tính bình phương khoảng cách từ điểm A đến mặt phẳng."""
    numerator = dot(n, A) + d
    return numerator * numerator


def distance_point_to_line_sq(A: Point, P0: Point, u: Vector) -> int:
    """Tính bình phương khoảng cách từ điểm A đến đường thẳng qua P0 với vector chỉ phương u."""
    PA = sub(A, P0)
    u_norm_sq = norm_sq(u)
    if u_norm_sq == 0:
        return norm_sq(PA)
    proj_num = dot(PA, u)
    # Khoảng cách = ||PA||^2 - (PA.u)^2 / ||u||^2
    # = (||PA||^2 * ||u||^2 - (PA.u)^2) / ||u||^2
    PA_norm_sq = norm_sq(PA)
    return (PA_norm_sq * u_norm_sq - proj_num * proj_num) // u_norm_sq


class SpatialGeometryQuestion:
    def __init__(self) -> None:
        self.parameters: Dict[str, Any] = {}

    def _make_line(self, label: str) -> Dict[str, Any]:
        point = random_point(-4, 4)
        direction = random_nonzero_vector(-3, 3)
        style = "canonical" if random.random() < 0.5 else "param"
        return {"label": label, "point": point, "direction": direction, "style": style}

    def _normalize_plane(self, normal: Vector, d: int) -> Tuple[Vector, int]:
        g = gcd_multiple((normal[0], normal[1], normal[2], d))
        if g != 0:
            normal = (normal[0] // g, normal[1] // g, normal[2] // g)
            d //= g
        if normal[0] < 0 or (normal[0] == 0 and normal[1] < 0) or (normal[0] == 0 and normal[1] == 0 and normal[2] < 0):
            normal = (-normal[0], -normal[1], -normal[2])
            d = -d
        return normal, d

    def _build_statement_a(self) -> Dict[str, Any]:
        """Mệnh đề a: Cho điểm A và điểm M trên mặt phẳng. AM đạt GTNN là m tại M(x,y,z)."""
        # Chọn normal có norm^2 là số chính phương để m là số nguyên
        perfect_squares = [1, 4, 9, 16, 25]
        candidates = [
            (1, 0, 0), (0, 1, 0), (0, 0, 1),
            (1, 1, 0), (1, 0, 1), (0, 1, 1),
            (2, 0, 0), (0, 2, 0), (0, 0, 2),
            (1, 2, 0), (2, 1, 0), (1, 0, 2), (2, 0, 1), (0, 1, 2), (0, 2, 1),
            (2, 2, 0), (2, 0, 2), (0, 2, 2),
            (1, 1, 1), (2, 1, 1), (1, 2, 1), (1, 1, 2),
            (3, 0, 0), (0, 3, 0), (0, 0, 3),
        ]
        normal = random.choice([c for c in candidates if norm_sq(c) in perfect_squares])
        normal = simplify_vector(normal)
        
        # Chọn M nguyên trên mặt phẳng
        M = random_point(-3, 3)
        # Tính d sao cho M thuộc mặt phẳng: n.M + d = 0 => d = -n.M
        plane_d = -dot(normal, M)
        normal, plane_d = self._normalize_plane(normal, plane_d)
        
        # Điều chỉnh A để hình chiếu của A lên P là M (để có số đẹp)
        # A = M + k*n với k là một số nguyên khác 0
        k = random.choice([-3, -2, -1, 1, 2, 3])
        A = add(M, scale(normal, k))
        
        # Khoảng cách m = |k| * ||n|| (bây giờ là số nguyên vì norm_sq chính phương)
        n_norm_sq = norm_sq(normal)
        n_norm = int(math.isqrt(n_norm_sq))
        m_sq = k * k * n_norm_sq
        m_value = abs(k) * n_norm
        
        # Biểu thức: k1*x + k2*y + k3*z + k4*m
        expr_coeffs = (
            random.choice([-2, -1, 1, 2]),
            random.choice([-2, -1, 1, 2]),
            random.choice([-2, -1, 1, 2]),
            random.choice([-2, -1, 1, 2]),
        )
        while expr_coeffs == (0, 0, 0, 0):
            expr_coeffs = (
                random.choice([-2, -1, 1, 2]),
                random.choice([-2, -1, 1, 2]),
                random.choice([-2, -1, 1, 2]),
                random.choice([-2, -1, 1, 2]),
            )
        value = (
            expr_coeffs[0] * M[0]
            + expr_coeffs[1] * M[1]
            + expr_coeffs[2] * M[2]
            + expr_coeffs[3] * m_value
        )
        wrong = pick_wrong_integer(value)
        plane = {"label": "P", "normal": normal, "d": plane_d}
        return {
            "A": A,
            "M": M,
            "plane": plane,
            "m": m_value,
            "m_sq": m_sq,
            "expr_coeffs": expr_coeffs,
            "value": value,
            "wrong": wrong,
            "k": k,
            "n_norm_sq": n_norm_sq,
        }

    def _build_statement_b(self) -> Dict[str, Any]:
        """Mệnh đề b: Cho điểm A và điểm M trên mặt cầu. AM đạt GTNN là m tại M_min và GTLN là M tại M_max."""
        # Chiến lược: Chọn C, chọn AC_vec có norm chính xác, chọn R và d sao cho chia đẹp
        C = random_point(-3, 3)
        R = random.choice([2, 3, 4, 5])
        R_sq = R * R
        
        # Chọn d và AC_vec sao cho d chia hết cho GCD(d, R) để M_min/M_max có tọa độ nguyên
        # Cách đơn giản: chọn d là bội số nhỏ của R hoặc R là bội số của d
        d_options = [R + 1, R + 2, R + 3, R - 1, R - 2] if R > 2 else [R + 1, R + 2, R + 3]
        d = random.choice([opt for opt in d_options if opt > 0 and opt != R])
        
        # Chọn AC_vec có độ dài = d, đơn giản nhất là dọc theo trục
        axis = random.choice([0, 1, 2])
        if axis == 0:
            AC_vec = (d, 0, 0)
        elif axis == 1:
            AC_vec = (0, d, 0)
        else:
            AC_vec = (0, 0, d)
        
        A = add(C, AC_vec)
        is_inside = d < R
        
        # Tính M_min và M_max với tọa độ nguyên
        # Để đảm bảo nguyên: cần C*d ± AC_vec*R chia hết cho d
        # Vì AC_vec chỉ có 1 thành phần khác 0 = d, và C*d luôn chia hết cho d
        # => (C*d ± d*R) / d = C ± R (luôn nguyên!)
        
        if is_inside:
            # A trong cầu: M_min = C - (R/d)*AC_vec, M_max = C + (R/d)*AC_vec
            M_min_num = sub(scale(C, d), scale(AC_vec, R))
            M_min = (M_min_num[0] // d, M_min_num[1] // d, M_min_num[2] // d)
            m = R - d
            
            M_max_num = add(scale(C, d), scale(AC_vec, R))
            M_max = (M_max_num[0] // d, M_max_num[1] // d, M_max_num[2] // d)
            M_value = R + d
        else:
            # A ngoài cầu: M_min = C + (R/d)*AC_vec, M_max = C - (R/d)*AC_vec
            M_min_num = add(scale(C, d), scale(AC_vec, R))
            M_min = (M_min_num[0] // d, M_min_num[1] // d, M_min_num[2] // d)
            m = d - R
            
            M_max_num = sub(scale(C, d), scale(AC_vec, R))
            M_max = (M_max_num[0] // d, M_max_num[1] // d, M_max_num[2] // d)
            M_value = d + R
        
        # Biểu thức
        expr_coeffs = (
            random.choice([-2, -1, 1, 2]),  # hệ số cho m
            random.choice([-2, -1, 1, 2]),  # hệ số cho M
            random.choice([-2, -1, 1, 2]),  # hệ số cho (a+b+c)
            random.choice([-2, -1, 1, 2]),  # hệ số cho (x+y+z)
        )
        while expr_coeffs == (0, 0, 0, 0):
            expr_coeffs = (
                random.choice([-2, -1, 1, 2]),
                random.choice([-2, -1, 1, 2]),
                random.choice([-2, -1, 1, 2]),
                random.choice([-2, -1, 1, 2]),
            )
        value = (
            expr_coeffs[0] * m
            + expr_coeffs[1] * M_value
            + expr_coeffs[2] * (M_min[0] + M_min[1] + M_min[2])
            + expr_coeffs[3] * (M_max[0] + M_max[1] + M_max[2])
        )
        wrong = pick_wrong_integer(value)
        sphere_type = random.choice(["center", "expanded"])
        sphere = {
            "label": "S",
            "center": C,
            "radius_sq": R_sq,
            "type": sphere_type,
        }
        return {
            "A": A,
            "sphere": sphere,
            "M_min": M_min,
            "M_max": M_max,
            "m": m,
            "M": M_value,
            "expr_coeffs": expr_coeffs,
            "value": value,
            "wrong": wrong,
            "is_inside": is_inside,
            "d": d,
            "R": R,
        }

    def _build_statement_c(self) -> Dict[str, Any]:
        """Mệnh đề c: Cho điểm A và điểm M trên đường thẳng. AM đạt GTNN là m tại M(a,b,c)."""
        # Random đường thẳng d: P0, u
        line = self._make_line("d")
        P0 = line["point"]
        u = line["direction"]
        
        # Chọn M trên đường thẳng
        t = random.randint(-3, 3)
        M = add(P0, scale(u, t))
        
        # Chọn v vuông góc với u có norm^2 chính phương (mở rộng không gian tìm kiếm)
        v_candidates = []
        for search_range in [5, 8, 12]:  # Tăng dần phạm vi tìm kiếm (đủ lớn để bao phủ)
            for i in range(-search_range, search_range + 1):
                for j in range(-search_range, search_range + 1):
                    for k_coord in range(-search_range, search_range + 1):
                        v_cand = (i, j, k_coord)
                        if v_cand != (0, 0, 0) and dot(v_cand, u) == 0:
                            v_norm = norm_sq(v_cand)
                            # Kiểm tra có phải số chính phương
                            v_sqrt = int(math.isqrt(v_norm))
                            if v_sqrt * v_sqrt == v_norm and v_norm > 0:
                                v_candidates.append(v_cand)
            if v_candidates:
                break
        
        if not v_candidates:
            # Fallback an toàn: tạo v từ các trục cơ sở có norm chính phương
            # Tìm trục vuông góc với u
            for base_v in [(1, 0, 0), (0, 1, 0), (0, 0, 1), (2, 0, 0), (0, 2, 0), (0, 0, 2),
                           (3, 0, 0), (0, 3, 0), (0, 0, 3), (4, 0, 0), (0, 4, 0), (0, 0, 4),
                           (5, 0, 0), (0, 5, 0), (0, 0, 5), (1, 1, 0), (1, 0, 1), (0, 1, 1),
                           (2, 2, 0), (2, 0, 2), (0, 2, 2), (3, 4, 0), (4, 3, 0), (3, 0, 4),
                           (4, 0, 3), (0, 3, 4), (0, 4, 3)]:
                if dot(base_v, u) == 0:
                    v_norm_test = norm_sq(base_v)
                    v_sqrt_test = int(math.isqrt(v_norm_test))
                    if v_sqrt_test * v_sqrt_test == v_norm_test:
                        v = base_v
                        break
            else:
                # Fallback cuối cùng: nếu không tìm được, thay đổi biểu thức
                # Dùng v đơn giản và thay đổi biểu thức dùng m^2 thay vì m
                # Nhưng để đơn giản, ta chọn v = (1,0,0) và kiểm tra lại
                # Thực tế case này rất hiếm, ta sẽ dùng vector đơn giản nhất vuông góc
                v = perpendicular_vector(u)
                v = simplify_vector(v)
                # Kiểm tra lại norm, nếu không chính phương thì scale
                v_test_norm = norm_sq(v)
                v_test_sqrt = int(math.isqrt(v_test_norm))
                if v_test_sqrt * v_test_sqrt != v_test_norm:
                    # Không chính phương, ta phải tìm được ít nhất 1 trong danh sách trên
                    # Nếu đến đây là bug logic, ta dùng (1,0,0) làm mặc định
                    v = (1, 0, 0)
        else:
            v = random.choice(v_candidates)
        
        # Tính A sao cho hình chiếu của A lên d là M
        # A = M + k*v với v vuông góc với u
        k = random.choice([-2, -1, 1, 2])
        A = add(M, scale(v, k))
        
        # Khoảng cách m = ||A - M|| = |k| * ||v|| (bây giờ là số nguyên)
        v_norm_sq = norm_sq(v)
        v_norm = int(math.isqrt(v_norm_sq))
        m_sq = k * k * v_norm_sq
        m_value = abs(k) * v_norm
        
        # Biểu thức: m + a + b + c = ...
        value = m_value + M[0] + M[1] + M[2]
        wrong = pick_wrong_integer(value)
        return {
            "A": A,
            "line": line,
            "M": M,
            "m": m_value,
            "m_sq": m_sq,
            "value": value,
            "wrong": wrong,
            "t": t,
            "k": k,
            "v_norm_sq": v_norm_sq,
            "u_norm_sq": norm_sq(u),
            "proj_num": 0,  # Không cần nữa vì đã chọn M trước
        }

    def _build_statement_d(self) -> Dict[str, Any]:
        """Mệnh đề d: Cho hai mặt phẳng song song. Tính khoảng cách giữa chúng."""
        # Chọn normal có norm^2 chính phương để m là số nguyên
        perfect_squares = [1, 4, 9, 16, 25]
        candidates = [
            (1, 0, 0), (0, 1, 0), (0, 0, 1),
            (1, 1, 0), (1, 0, 1), (0, 1, 1),
            (2, 0, 0), (0, 2, 0), (0, 0, 2),
            (1, 2, 0), (2, 1, 0), (1, 0, 2), (2, 0, 1), (0, 1, 2), (0, 2, 1),
            (2, 2, 0), (2, 0, 2), (0, 2, 2),
            (1, 1, 1), (2, 1, 1), (1, 2, 1), (1, 1, 2),
            (3, 0, 0), (0, 3, 0), (0, 0, 3),
        ]
        normal = random.choice([c for c in candidates if norm_sq(c) in perfect_squares])
        normal = simplify_vector(normal)
        n_norm_sq = norm_sq(normal)
        n_norm = int(math.isqrt(n_norm_sq))
        
        # Chọn d_P và d_S khác nhau
        d_P = random.choice([-3, -2, -1, 0, 1, 2, 3])
        d_S_options = [d for d in [-3, -2, -1, 0, 1, 2, 3] if d != d_P]
        d_S = random.choice(d_S_options)
        
        # Lưu normal ban đầu để phát hiện đảo dấu
        old_normal = normal
        normal, d_P = self._normalize_plane(normal, d_P)
        
        # Nếu normal bị đảo dấu, đồng bộ d_S
        if normal == (-old_normal[0], -old_normal[1], -old_normal[2]):
            d_S = -d_S
        
        # Khoảng cách m = |d_P - d_S| / ||n|| (bây giờ là số nguyên)
        m_numerator = abs(d_P - d_S)
        m_value = m_numerator // n_norm if n_norm != 0 else m_numerator
        
        wrong = pick_wrong_integer(m_value)
        plane_P = {"label": "P", "normal": normal, "d": d_P}
        plane_S = {"label": "S", "normal": normal, "d": d_S}
        return {
            "plane_P": plane_P,
            "plane_S": plane_S,
            "m": m_value,
            "m_numerator": m_numerator,
            "value": m_value,
            "wrong": wrong,
            "n_norm_sq": n_norm_sq,
            "n_norm": n_norm,
            "d_P": d_P,
            "d_S": d_S,
        }

    def generate_parameters(self) -> Dict[str, Any]:
        params = {
            "a": self._build_statement_a(),
            "b": self._build_statement_b(),
            "c": self._build_statement_c(),
            "d": self._build_statement_d(),
        }
        self.parameters = params
        return params

    def generate_question(self, question_number: int) -> str:
        params = self.generate_parameters()

        statements_info: List[Dict[str, object]] = []

        # Statement a: Điểm đến mặt phẳng
        data_a = params["a"]
        plane_a_eq = format_plane_equation(
            data_a["plane"]["normal"][0],
            data_a["plane"]["normal"][1],
            data_a["plane"]["normal"][2],
            data_a["plane"]["d"],
        )
        plane_label_a_math = f"\\({data_a['plane']['label']}\\)"
        plane_label_a_phrase = f"({plane_label_a_math})"
        # Biểu thức: k1*x + k2*y + k3*z + k4*m
        expr_parts: List[str] = []
        append_linear_term(expr_parts, data_a["expr_coeffs"][0], "x")
        append_linear_term(expr_parts, data_a["expr_coeffs"][1], "y")
        append_linear_term(expr_parts, data_a["expr_coeffs"][2], "z")
        append_linear_term(expr_parts, data_a["expr_coeffs"][3], "m")
        expr_a = " ".join(expr_parts) if expr_parts else "0"
        true_text_a = (
            f"Cho điểm A{format_point(data_a['A'])} và 1 điểm M bất kì thuộc mặt phẳng {plane_label_a_phrase}: \\({plane_a_eq}\\). "
            f"Khi đó M(x, y, z) thì AM đạt GTNN là m. Khi đó \\({expr_a} = {data_a['value']}\\)."
        )
        false_text_a = true_text_a.replace(f"= {data_a['value']}\\)", f"= {data_a['wrong']}\\)")
        statements_info.append(
            {
                "label": "a",
                "true_text": true_text_a,
                "false_text": false_text_a,
                "display_true": data_a["value"],
                "display_false": data_a["wrong"],
            }
        )

        # Statement b: Điểm đến mặt cầu
        data_b = params["b"]
        sphere_eq = format_sphere_expression(data_b["sphere"])
        sphere_label_b_math = f"\\({data_b['sphere']['label']}\\)"
        sphere_label_b_phrase = f"({sphere_label_b_math})"
        # Biểu thức: k1*m + k2*M + k3*(a+b+c) + k4*(x+y+z)
        expr_b_parts: List[str] = []
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][0], "m")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][1], "M")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][2], "(a + b + c)")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][3], "(x + y + z)")
        expr_b = " ".join(expr_b_parts) if expr_b_parts else "0"
        true_text_b = (
            f"Cho điểm A{format_point(data_b['A'])} và 1 điểm M bất kì thuộc mặt cầu {sphere_label_b_phrase}: \\({sphere_eq}\\). "
            f"Biết rằng AM đạt GTNN là m khi M(a, b, c) và đạt GTLN là M khi M(x, y, z). "
            f"Khi đó \\({expr_b} = {data_b['value']}\\)."
        )
        false_text_b = true_text_b.replace(f"= {data_b['value']}\\)", f"= {data_b['wrong']}\\)")
        statements_info.append(
            {
                "label": "b",
                "true_text": true_text_b,
                "false_text": false_text_b,
                "display_true": data_b["value"],
                "display_false": data_b["wrong"],
            }
        )

        # Statement c: Điểm đến đường thẳng
        data_c = params["c"]
        line_c_expr = format_line_expression(data_c["line"])
        line_label_c_math = f"\\({data_c['line']['label']}\\)"
        true_text_c = (
            f"Cho điểm A{format_point(data_c['A'])} và 1 điểm M bất kì thuộc đường thẳng {line_label_c_math}: \\({line_c_expr}\\). "
            f"Biết rằng AM đạt GTNN là m khi M(a, b, c). "
            f"Khi đó \\(m + a + b + c = {data_c['value']}\\)."
        )
        false_text_c = true_text_c.replace(f"= {data_c['value']}\\)", f"= {data_c['wrong']}\\)")
        statements_info.append(
            {
                "label": "c",
                "true_text": true_text_c,
                "false_text": false_text_c,
                "display_true": data_c["value"],
                "display_false": data_c["wrong"],
            }
        )

        # Statement d: Hai mặt phẳng song song
        data_d = params["d"]
        plane_P_eq = format_plane_equation(
            data_d["plane_P"]["normal"][0],
            data_d["plane_P"]["normal"][1],
            data_d["plane_P"]["normal"][2],
            data_d["plane_P"]["d"],
        )
        plane_S_eq = format_plane_equation(
            data_d["plane_S"]["normal"][0],
            data_d["plane_S"]["normal"][1],
            data_d["plane_S"]["normal"][2],
            data_d["plane_S"]["d"],
        )
        plane_P_label_math = f"\\({data_d['plane_P']['label']}\\)"
        plane_S_label_math = f"\\({data_d['plane_S']['label']}\\)"
        plane_P_label_phrase = f"({plane_P_label_math})"
        plane_S_label_phrase = f"({plane_S_label_math})"
        true_text_d = (
            f"Cho hai mặt phẳng song song {plane_P_label_phrase}: \\({plane_P_eq}\\) và {plane_S_label_phrase}: \\({plane_S_eq}\\). "
            f"Khoảng cách giữa hai mặt phẳng là \\({data_d['value']}\\)."
        )
        false_text_d = true_text_d.replace(f"là \\({data_d['value']}\\)", f"là \\({data_d['wrong']}\\)")
        statements_info.append(
            {
                "label": "d",
                "true_text": true_text_d,
                "false_text": false_text_d,
                "display_true": data_d["value"],
                "display_false": data_d["wrong"],
            }
        )

        num_true = random.randint(1, 4)
        true_indices = set(random.sample(range(4), num_true))

        option_labels = ["a", "b", "c", "d"]
        question_lines: List[str] = []
        solutions: List[str] = ["Lời giải."]
        correct_labels: List[str] = []

        for idx, statement in enumerate(statements_info):
            is_true = idx in true_indices
            text = statement["true_text"] if is_true else statement["false_text"]
            displayed_value = statement["display_true"] if is_true else statement["display_false"]
            prefix = "*" if is_true else ""
            question_lines.append(f"{prefix}{option_labels[idx]}) {text}")
            if is_true:
                correct_labels.append(option_labels[idx])

            label = statement["label"]
            if label == "a":
                data = params["a"]
                expr_parts = []
                append_linear_term(expr_parts, data["expr_coeffs"][0], "x")
                append_linear_term(expr_parts, data["expr_coeffs"][1], "y")
                append_linear_term(expr_parts, data["expr_coeffs"][2], "z")
                append_linear_term(expr_parts, data["expr_coeffs"][3], "m")
                expr = " ".join(expr_parts) if expr_parts else "0"
                status = " \\quad(\\text{đúng})" if is_true else f" \\neq {displayed_value} \\Rightarrow \\text{{sai}}"
                m_formatted = format_distance(data["m_sq"])
                plane_eq = format_plane_equation(
                    data['plane']['normal'][0],
                    data['plane']['normal'][1],
                    data['plane']['normal'][2],
                    data['plane']['d']
                )
                solution_text = (
                    f"a) Mặt phẳng \\((P)\\): \\({plane_eq}\\) có vector pháp tuyến \\(\\vec{{n}} = {format_point(data['plane']['normal'])}\\).\n\n"
                    f"Điểm \\(A{format_point(data['A'])}\\).\n\n"
                    f"Hình chiếu \\(M\\) của \\(A\\) lên mặt phẳng là: \\(M{format_point(data['M'])}\\).\n\n"
                    f"Khoảng cách: \\(m = AM = {m_formatted}\\).\n\n"
                    f"Vậy \\({expr} = {data['value']}{status}\\)"
                )
                solutions.append(solution_text)
            elif label == "b":
                data = params["b"]
                expr_parts = []
                append_linear_term(expr_parts, data["expr_coeffs"][0], "m")
                append_linear_term(expr_parts, data["expr_coeffs"][1], "M")
                append_linear_term(expr_parts, data["expr_coeffs"][2], "(a + b + c)")
                append_linear_term(expr_parts, data["expr_coeffs"][3], "(x + y + z)")
                expr = " ".join(expr_parts) if expr_parts else "0"
                status = " \\quad(\\text{đúng})" if is_true else f" \\neq {displayed_value} \\Rightarrow \\text{{sai}}"
                sphere_eq = format_sphere_expression(data['sphere'])
                if data["is_inside"]:
                    solution_text = (
                        f"b) Mặt cầu \\((S)\\): \\({sphere_eq}\\) có tâm \\(I{format_point(data['sphere']['center'])}\\), bán kính \\(R = {data['R']}\\).\n\n"
                        f"Điểm \\(A{format_point(data['A'])}\\) nằm trong mặt cầu.\n\n"
                        f"Khoảng cách từ \\(A\\) đến tâm: \\(d = IA = {data['d']}\\).\n\n"
                        f"GTNN của \\(AM\\): \\(m = R - d = {data['R']} - {data['d']} = {data['m']}\\), đạt được khi \\(M_{{\\min}}{format_point(data['M_min'])}\\).\n\n"
                        f"GTLN của \\(AM\\): \\(M = R + d = {data['R']} + {data['d']} = {data['M']}\\), đạt được khi \\(M_{{\\max}}{format_point(data['M_max'])}\\).\n\n"
                        f"Vậy \\({expr} = {data['value']}{status}\\)"
                    )
                    solutions.append(solution_text)
                else:
                    solution_text = (
                        f"b) Mặt cầu \\((S)\\): \\({sphere_eq}\\) có tâm \\(I{format_point(data['sphere']['center'])}\\), bán kính \\(R = {data['R']}\\).\n\n"
                        f"Điểm \\(A{format_point(data['A'])}\\) nằm ngoài mặt cầu.\n\n"
                        f"Khoảng cách từ \\(A\\) đến tâm: \\(d = IA = {data['d']}\\).\n\n"
                        f"GTNN của \\(AM\\): \\(m = d - R = {data['d']} - {data['R']} = {data['m']}\\), đạt được khi \\(M_{{\\min}}{format_point(data['M_min'])}\\).\n\n"
                        f"GTLN của \\(AM\\): \\(M = d + R = {data['d']} + {data['R']} = {data['M']}\\), đạt được khi \\(M_{{\\max}}{format_point(data['M_max'])}\\).\n\n"
                        f"Vậy \\({expr} = {data['value']}{status}\\)"
                    )
                    solutions.append(solution_text)
            elif label == "c":
                data = params["c"]
                status = " \\quad(\\text{đúng})" if is_true else f" \\neq {displayed_value} \\Rightarrow \\text{{sai}}"
                m_formatted = format_distance(data["m_sq"])
                solution_text = (
                    f"c) Đường thẳng \\(d\\) có vector chỉ phương \\(\\vec{{u}} = {format_point(data['line']['direction'])}\\).\n\n"
                    f"Điểm \\(A{format_point(data['A'])}\\).\n\n"
                    f"Hình chiếu \\(M\\) của \\(A\\) lên đường thẳng \\(d\\) là: \\(M{format_point(data['M'])}\\).\n\n"
                    f"Khoảng cách: \\(m = AM = {m_formatted}\\).\n\n"
                    f"Vậy \\(m + a + b + c = {data['m']} + {data['M'][0]} + {data['M'][1]} + {data['M'][2]} = {data['value']}{status}\\)"
                )
                solutions.append(solution_text)
            else:
                data = params["d"]
                status = " \\quad(\\text{đúng})" if is_true else f" \\neq {displayed_value} \\Rightarrow \\text{{sai}}"
                plane_P_eq = format_plane_equation(
                    data['plane_P']['normal'][0],
                    data['plane_P']['normal'][1],
                    data['plane_P']['normal'][2],
                    data['plane_P']['d']
                )
                plane_S_eq = format_plane_equation(
                    data['plane_S']['normal'][0],
                    data['plane_S']['normal'][1],
                    data['plane_S']['normal'][2],
                    data['plane_S']['d']
                )
                solution_text = (
                    f"d) Mặt phẳng \\((P)\\): \\({plane_P_eq}\\) và mặt phẳng \\((S)\\): \\({plane_S_eq}\\) song song.\n\n"
                    f"Vector pháp tuyến chung: \\(\\vec{{n}} = {format_point(data['plane_P']['normal'])}\\).\n\n"
                    f"Khoảng cách giữa hai mặt phẳng:\n\n"
                    f"\\(d = \\dfrac{{|d_P - d_S|}}{{\\|\\vec{{n}}\\|}} = \\dfrac{{{data['m_numerator']}}}{{{data['n_norm']}}} = {data['m']}{status}\\)"
                )
                solutions.append(solution_text)

        question_body = "\n\n".join(question_lines)
        solution_text = "\n\n".join(solutions)

        content = (
            f"Câu {question_number}: Chọn các mệnh đề đúng.\n\n"
            f"{question_body}\n\n{solution_text}\n"
        )
        return content


class QuestionManager:
    def __init__(self) -> None:
        self.failed_count = 0

    def generate_questions(self, num_questions: int, verbose: bool = False) -> List[str]:
        if num_questions <= 0:
            raise ValueError("Số câu hỏi phải lớn hơn 0")
        questions: List[str] = []
        for idx in range(1, num_questions + 1):
            try:
                question = SpatialGeometryQuestion().generate_question(idx)
                questions.append(question)
                if verbose:
                    print(f"✅ Đã tạo xong câu {idx}")
            except Exception as exc:  # pragma: no cover - chỉ để debug runtime
                self.failed_count += 1
                print(f"❌ Lỗi khi tạo câu {idx}: {exc}")
        if not questions:
            raise ValueError("Không thể tạo được câu hỏi nào")
        if self.failed_count > 0:
            print(f"⚠️ Có {self.failed_count} câu không tạo được")
        return questions


class LaTeXTemplate:
    DOCUMENT_HEADER = r"""\documentclass[a4paper,12pt]{{article}}
\usepackage{{amsmath}}
\usepackage{{amsfonts}}
\usepackage{{amssymb}}
\usepackage{{geometry}}
\geometry{{a4paper, margin=1in}}
\usepackage{{polyglossia}}
\setmainlanguage{{vietnamese}}
\setmainfont{{Times New Roman}}
\usepackage{{tikz}}
\begin{{document}}
\title{{{title}}}
\author{{{author}}}
\maketitle

"""

    DOCUMENT_FOOTER = r"""
\end{document}"""


class LaTeXDocumentBuilder:
    def __init__(self) -> None:
        self.template = LaTeXTemplate()

    def build_document(self, questions: List[str], title: str, author: str = "dev") -> str:
        if not questions:
            raise ValueError("Danh sách câu hỏi không được rỗng")
        header = self.template.DOCUMENT_HEADER.format(title=title, author=author)
        body = "\n\n".join(questions)
        return header + body + self.template.DOCUMENT_FOOTER


DEFAULT_NUM_QUESTIONS = 3
DEFAULT_FILENAME = "geometry_questions.tex"
DEFAULT_TITLE = "Câu hỏi đường thẳng, mặt phẳng và mặt cầu"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generator câu hỏi hình học không gian dạng đúng/sai",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
    python3 duongthang_matphang_matcau.py            # Tạo 3 câu
    python3 duongthang_matphang_matcau.py 5          # Tạo 5 câu
    python3 duongthang_matphang_matcau.py -n 10      # Tạo 10 câu
""",
    )
    parser.add_argument(
        "num_questions",
        nargs="?",
        type=int,
        default=DEFAULT_NUM_QUESTIONS,
        help=f"Số câu cần tạo (mặc định: {DEFAULT_NUM_QUESTIONS})",
    )
    parser.add_argument(
        "-n",
        "--num-questions",
        type=int,
        dest="num_questions_override",
        help="Ghi đè số câu cần tạo",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=DEFAULT_FILENAME,
        help=f"Tên file LaTeX (mặc định: {DEFAULT_FILENAME})",
    )
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        default=DEFAULT_TITLE,
        help=f"Tiêu đề tài liệu (mặc định: '{DEFAULT_TITLE}')",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Hiển thị chi tiết quá trình tạo",
    )
    args = parser.parse_args()
    if args.num_questions_override is not None:
        args.num_questions = args.num_questions_override
    if args.num_questions <= 0:
        parser.error("Số câu phải dương")
    return args


def generate_questions(num_questions: int, verbose: bool = False) -> List[str]:
    manager = QuestionManager()
    return manager.generate_questions(num_questions, verbose)


def create_latex_file(questions: List[str], filename: str, title: str) -> None:
    builder = LaTeXDocumentBuilder()
    content = builder.build_document(questions, title)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> None:
    try:
        args = parse_arguments()
        if args.verbose:
            logging.basicConfig(level=logging.INFO)
        questions = generate_questions(args.num_questions, args.verbose)
        create_latex_file(questions, args.output, args.title)
        print(f"✅ Đã tạo {args.output} với {len(questions)} câu.")
        print(f"📄 Biên dịch bằng: xelatex {args.output}")
    except Exception as exc:
        print(f"❌ Lỗi: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()


