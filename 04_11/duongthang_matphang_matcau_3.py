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


def format_point_float(p: Tuple[float, float, float]) -> str:
    """Format điểm với tọa độ float, làm tròn nếu cần."""
    def fmt(x: float) -> str:
        if abs(x - round(x)) < 1e-9:
            return str(int(round(x)))
        return f"{x:.2f}"
    return f"({fmt(p[0])};{fmt(p[1])};{fmt(p[2])})"


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
    joined = " \\\\\n".join(rows)
    return "\\begin{cases}\n" + joined + "\n\\end{cases}"


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
    ratio = max(-1.0, min(1.0, float(numerator) / den))
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
    """Tính bình phương khoảng cách giữa 2 điểm nguyên."""
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    dz = p1[2] - p2[2]
    return dx * dx + dy * dy + dz * dz


def distance_sq_float(p1: Tuple[float, float, float], p2: Tuple[float, float, float]) -> float:
    """Tính bình phương khoảng cách giữa 2 điểm float."""
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


def project_point_to_plane(A: Point, n: Vector, d: int) -> Tuple[float, float, float]:
    """Chiếu điểm A lên mặt phẳng n.x + d = 0."""
    # Khoảng cách từ A đến mặt phẳng: |n.A + d| / ||n||
    # Hình chiếu: A - (n.A + d) / ||n||^2 * n
    n_norm_sq = norm_sq(n)
    if n_norm_sq == 0:
        return (float(A[0]), float(A[1]), float(A[2]))
    numerator = dot(n, A) + d
    t = numerator / n_norm_sq
    H = (A[0] - t * n[0], A[1] - t * n[1], A[2] - t * n[2])
    return H


def project_point_to_line(A: Point, P0: Point, u: Vector) -> Tuple[float, float, float]:
    """Chiếu điểm A lên đường thẳng qua P0 với vector chỉ phương u."""
    # Vector từ P0 đến A
    PA = sub(A, P0)
    # Tham số t: t = (PA . u) / ||u||^2
    u_norm_sq = norm_sq(u)
    if u_norm_sq == 0:
        return (float(P0[0]), float(P0[1]), float(P0[2]))
    t = dot(PA, u) / u_norm_sq
    H = (P0[0] + t * u[0], P0[1] + t * u[1], P0[2] + t * u[2])
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


def distance_point_to_line(A: Point, P0: Point, u: Vector) -> float:
    """Tính khoảng cách từ điểm A đến đường thẳng qua P0 với vector chỉ phương u."""
    PA = sub(A, P0)
    cross_prod = cross(PA, u)
    cross_norm = math.sqrt(float(norm_sq(cross_prod)))
    u_norm = math.sqrt(float(norm_sq(u)))
    if u_norm == 0:
        return math.sqrt(float(norm_sq(PA)))
    return cross_norm / u_norm


def distance_between_lines(P1: Point, u1: Vector, P2: Point, u2: Vector) -> Tuple[float, int, int]:
    """
    Tính khoảng cách giữa 2 đường thẳng.
    Trả về: (khoảng cách float, tử số, mẫu số của công thức)
    """
    cross_prod = cross(u1, u2)
    cross_norm_sq = norm_sq(cross_prod)
    
    # Nếu u1 và u2 song song (hoặc trùng phương)
    if cross_norm_sq == 0:
        # Khoảng cách từ P2 đến đường thẳng 1
        d = distance_point_to_line(P2, P1, u1)
        return d, 0, 1
    
    # Công thức: d = |P1P2 . (u1 x u2)| / ||u1 x u2||
    P1P2 = sub(P2, P1)
    numerator = abs(dot(P1P2, cross_prod))
    denominator_sq = cross_norm_sq
    denominator = math.sqrt(float(cross_norm_sq))
    
    return numerator / denominator, numerator, denominator_sq


def line_plane_intersection(P0: Point, u: Vector, n: Vector, d: int) -> Tuple[Tuple[float, float, float], bool]:
    """
    Tìm giao điểm giữa đường thẳng (qua P0 với vtcp u) và mặt phẳng (normal n, hằng số d).
    Phương trình mặt phẳng: n.x + d = 0
    Phương trình đường thẳng: X = P0 + t*u
    Trả về: (điểm giao, có giao điểm hay không)
    """
    # Thay vào phương trình: n.(P0 + t*u) + d = 0
    # => n.P0 + t*(n.u) + d = 0
    # => t = -(n.P0 + d) / (n.u)
    
    denominator = dot(n, u)
    
    # Nếu đường thẳng song song với mặt phẳng
    if denominator == 0:
        return (float(P0[0]), float(P0[1]), float(P0[2])), False
    
    t = -(dot(n, P0) + d) / denominator
    I = (P0[0] + t * u[0], P0[1] + t * u[1], P0[2] + t * u[2])
    
    return I, True


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
        """Mệnh đề a: Điểm M trên mặt cầu (S) và N trên đường thẳng d. Tìm GTNN của MN."""
        # Tạo mặt cầu (S) với tâm C và bán kính R
        C = random_point(-3, 3)
        R = random.choice([2, 3, 4, 5])
        R_sq = R * R
        sphere_type = random.choice(["center", "expanded"])
        
        # Tạo đường thẳng d
        line = self._make_line("d")
        P0 = line["point"]
        u = line["direction"]
        
        # Tính khoảng cách từ tâm C đến đường thẳng d
        H = project_point_to_line(C, P0, u)  # Hình chiếu C lên d
        d_sq_float = distance_sq_float((float(C[0]), float(C[1]), float(C[2])), H)
        d_value = math.sqrt(d_sq_float)
        
        # GTNN của MN
        # - Nếu d >= R: m = d - R (C nằm ngoài hoặc tiếp xúc), M nằm trên CH, N = H
        # - Nếu d < R: m = 0 (đường thẳng cắt mặt cầu), M = N tại giao điểm
        if d_value >= R - 1e-9:
            m = d_value - R
            m_sq = int((m * m) + 0.5)
            # M là điểm trên cầu gần H nhất: M = C + R * (H-C) / ||H-C||
            if d_value > 1e-9:
                # M = C + R * (H-C) / d_value
                M = (
                    C[0] + R * (H[0] - C[0]) / d_value,
                    C[1] + R * (H[1] - C[1]) / d_value,
                    C[2] + R * (H[2] - C[2]) / d_value,
                )
            else:
                M = (float(C[0]) + R, float(C[1]), float(C[2]))
            N = H
        else:
            # Đường thẳng cắt mặt cầu: tính giao điểm
            # Phương trình: ||P0 + t*u - C||^2 = R^2
            # (P0 - C + t*u).(P0 - C + t*u) = R^2
            # ||P0-C||^2 + 2t*(P0-C).u + t^2*||u||^2 = R^2
            PC = (P0[0] - C[0], P0[1] - C[1], P0[2] - C[2])
            a_coeff = norm_sq(u)
            b_coeff = 2 * dot(PC, u)
            c_coeff = dot(PC, PC) - R_sq
            discriminant = b_coeff * b_coeff - 4 * a_coeff * c_coeff
            if discriminant >= 0 and a_coeff != 0:
                t_intersect = (-b_coeff - math.sqrt(discriminant)) / (2 * a_coeff)
                M = (P0[0] + t_intersect * u[0], P0[1] + t_intersect * u[1], P0[2] + t_intersect * u[2])
                N = M
            else:
                # Fallback nếu không có giao (không nên xảy ra)
                M = (float(C[0]) + R, float(C[1]), float(C[2]))
                N = H
            m = 0
            m_sq = 0
        
        # Biểu thức: k1*m + k2*a + k3*b + k4*c + k5*x + k6*y + k7*z
        expr_coeffs = tuple(random.choice([-2, -1, 1, 2]) for _ in range(7))
        while all(c == 0 for c in expr_coeffs):
            expr_coeffs = tuple(random.choice([-2, -1, 1, 2]) for _ in range(7))
        
        value = (
            expr_coeffs[0] * m
            + expr_coeffs[1] * M[0]
            + expr_coeffs[2] * M[1]
            + expr_coeffs[3] * M[2]
            + expr_coeffs[4] * N[0]
            + expr_coeffs[5] * N[1]
            + expr_coeffs[6] * N[2]
        )
        value_int = int(round(value))
        wrong = pick_wrong_integer(value_int)
        
        sphere = {"label": "S", "center": C, "radius_sq": R_sq, "type": sphere_type}
        
        return {
            "sphere": sphere,
            "line": line,
            "M": M,
            "N": N,
            "m": m,
            "m_sq": m_sq,
            "expr_coeffs": expr_coeffs,
            "value": value_int,
            "wrong": wrong,
            "C": C,
            "R": R,
            "d_value": d_value,
        }

    def _build_statement_b(self) -> Dict[str, Any]:
        """Mệnh đề b: Điểm M trên mặt cầu (S1) và N trên mặt cầu (S2). Tìm GTNN và GTLN."""
        # Tạo 2 mặt cầu
        C1 = random_point(-3, 3)
        C2 = random_point(-3, 3)
        R1 = random.choice([2, 3, 4])
        R2 = random.choice([2, 3, 4])
        
        # Đảm bảo C1 và C2 khác nhau
        while C1 == C2:
            C2 = random_point(-3, 3)
        
        # Tính khoảng cách giữa 2 tâm
        C1C2_vec = sub(C2, C1)
        d_sq = norm_sq(C1C2_vec)
        d = math.sqrt(float(d_sq))
        
        # GTNN: m = max(0, d - R1 - R2)
        # GTLN: M = d + R1 + R2
        m = max(0, d - R1 - R2)
        M_value = d + R1 + R2
        
        # Tìm điểm M_min trên S1 và N_min trên S2 đạt GTNN
        if d > 0:
            # M_min = C1 + R1 * (C2-C1) / d
            M_min_num = add(scale(C1, int(d)), scale(C1C2_vec, R1))
            M_min = (int(M_min_num[0] / d), int(M_min_num[1] / d), int(M_min_num[2] / d))
            
            # N_min = C2 - R2 * (C2-C1) / d
            N_min_num = sub(scale(C2, int(d)), scale(C1C2_vec, R2))
            N_min = (int(N_min_num[0] / d), int(N_min_num[1] / d), int(N_min_num[2] / d))
            
            # M_max = C1 - R1 * (C2-C1) / d
            M_max_num = sub(scale(C1, int(d)), scale(C1C2_vec, R1))
            M_max = (int(M_max_num[0] / d), int(M_max_num[1] / d), int(M_max_num[2] / d))
            
            # N_max = C2 + R2 * (C2-C1) / d
            N_max_num = add(scale(C2, int(d)), scale(C1C2_vec, R2))
            N_max = (int(N_max_num[0] / d), int(N_max_num[1] / d), int(N_max_num[2] / d))
        else:
            # Trường hợp đặc biệt: 2 cầu cùng tâm
            M_min = add(C1, (R1, 0, 0))
            N_min = add(C2, (R2, 0, 0))
            M_max = add(C1, (-R1, 0, 0))
            N_max = add(C2, (-R2, 0, 0))
        
        # Biểu thức phức tạp với 14 biến: m, M, a, b, c, x, y, z, p, q, r, k, l, e
        expr_coeffs = tuple(random.choice([-2, -1, 1, 2]) for _ in range(14))
        while all(c == 0 for c in expr_coeffs):
            expr_coeffs = tuple(random.choice([-2, -1, 1, 2]) for _ in range(14))
        
        value = (
            expr_coeffs[0] * int(m)
            + expr_coeffs[1] * int(M_value)
            + expr_coeffs[2] * M_min[0]
            + expr_coeffs[3] * M_min[1]
            + expr_coeffs[4] * M_min[2]
            + expr_coeffs[5] * N_min[0]
            + expr_coeffs[6] * N_min[1]
            + expr_coeffs[7] * N_min[2]
            + expr_coeffs[8] * M_max[0]
            + expr_coeffs[9] * M_max[1]
            + expr_coeffs[10] * M_max[2]
            + expr_coeffs[11] * N_max[0]
            + expr_coeffs[12] * N_max[1]
            + expr_coeffs[13] * N_max[2]
        )
        wrong = pick_wrong_integer(value)
        
        sphere1_type = random.choice(["center", "expanded"])
        sphere2_type = random.choice(["center", "expanded"])
        
        sphere1 = {"label": "S_1", "center": C1, "radius_sq": R1 * R1, "type": sphere1_type}
        sphere2 = {"label": "S_2", "center": C2, "radius_sq": R2 * R2, "type": sphere2_type}
        
        return {
            "sphere1": sphere1,
            "sphere2": sphere2,
            "M_min": M_min,
            "N_min": N_min,
            "M_max": M_max,
            "N_max": N_max,
            "m": int(m),
            "M": int(M_value),
            "expr_coeffs": expr_coeffs,
            "value": value,
            "wrong": wrong,
            "d": d,
            "R1": R1,
            "R2": R2,
        }

    def _build_statement_c(self) -> Dict[str, Any]:
        """Mệnh đề c: Điểm M trên đường thẳng d1 và N trên đường thẳng d2. Tìm GTNN."""
        # Tạo 2 đường thẳng
        line1 = self._make_line("d_1")
        line2 = self._make_line("d_2")
        
        P1 = line1["point"]
        u1 = line1["direction"]
        P2 = line2["point"]
        u2 = line2["direction"]
        
        # Đảm bảo 2 đường thẳng không song song
        cross_prod = cross(u1, u2)
        attempts = 0
        while norm_sq(cross_prod) == 0 and attempts < 10:
            line2 = self._make_line("d_2")
            P2 = line2["point"]
            u2 = line2["direction"]
            cross_prod = cross(u1, u2)
            attempts += 1
        
        # Tính khoảng cách giữa 2 đường thẳng
        m, m_numerator, m_denominator_sq = distance_between_lines(P1, u1, P2, u2)
        
        # Tìm điểm M trên d1 và N trên d2 đạt khoảng cách nhỏ nhất
        # Sử dụng công thức: M = P1 + t1*u1, N = P2 + t2*u2
        # với t1, t2 thỏa mãn hệ phương trình
        
        cross_norm_sq = norm_sq(cross_prod)
        if cross_norm_sq > 0:
            # Công thức tìm t1, t2
            P1P2 = sub(P2, P1)
            u1_dot_u1 = norm_sq(u1)
            u2_dot_u2 = norm_sq(u2)
            u1_dot_u2 = dot(u1, u2)
            u1_dot_P1P2 = dot(u1, P1P2)
            u2_dot_P1P2 = dot(u2, P1P2)
            
            denom = u1_dot_u1 * u2_dot_u2 - u1_dot_u2 * u1_dot_u2
            if denom != 0:
                t1 = (u1_dot_P1P2 * u2_dot_u2 - u2_dot_P1P2 * u1_dot_u2) / denom
                t2 = (u1_dot_P1P2 * u1_dot_u2 - u2_dot_P1P2 * u1_dot_u1) / denom
            else:
                t1 = 0.0
                t2 = 0.0
        else:
            # Đường thẳng song song, chọn M và N bất kỳ
            t1 = 0.0
            t2 = 0.0
        
        M = (P1[0] + t1 * u1[0], P1[1] + t1 * u1[1], P1[2] + t1 * u1[2])
        N = (P2[0] + t2 * u2[0], P2[1] + t2 * u2[1], P2[2] + t2 * u2[2])
        
        # Biểu thức: k1*m + k2*a + k3*b + k4*c + k5*x + k6*y + k7*z
        expr_coeffs = tuple(random.choice([-2, -1, 1, 2]) for _ in range(7))
        while all(c == 0 for c in expr_coeffs):
            expr_coeffs = tuple(random.choice([-2, -1, 1, 2]) for _ in range(7))
        
        value = (
            expr_coeffs[0] * m
            + expr_coeffs[1] * M[0]
            + expr_coeffs[2] * M[1]
            + expr_coeffs[3] * M[2]
            + expr_coeffs[4] * N[0]
            + expr_coeffs[5] * N[1]
            + expr_coeffs[6] * N[2]
        )
        value_int = int(round(value))
        wrong = pick_wrong_integer(value_int)
        
        return {
            "line1": line1,
            "line2": line2,
            "M": M,
            "N": N,
            "m": m,
            "m_numerator": m_numerator,
            "m_denominator_sq": m_denominator_sq,
            "expr_coeffs": expr_coeffs,
            "value": value_int,
            "wrong": wrong,
        }

    def _build_statement_d(self) -> Dict[str, Any]:
        """Mệnh đề d: Tìm đường thẳng d nằm trong (P), cắt và vuông góc với delta."""
        # Tạo đường thẳng delta
        delta = self._make_line("\\delta")
        P0_delta = delta["point"]
        u_delta = delta["direction"]
        
        # Tạo mặt phẳng (P)
        normal = random_nonzero_vector(-3, 3)
        normal = simplify_vector(normal)
        
        # Đảm bảo delta không song song với (P)
        # (delta cắt P khi u_delta . n != 0)
        attempts = 0
        while dot(u_delta, normal) == 0 and attempts < 10:
            normal = random_nonzero_vector(-3, 3)
            normal = simplify_vector(normal)
            attempts += 1
        
        # Chọn d của mặt phẳng
        plane_d = random.choice([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5])
        normal, plane_d = self._normalize_plane(normal, plane_d)
        
        # Tìm giao điểm I của delta và (P)
        I, has_intersection = line_plane_intersection(P0_delta, u_delta, normal, plane_d)
        
        if not has_intersection:
            # Fallback: điều chỉnh plane_d để có giao điểm
            plane_d = -dot(normal, P0_delta)
            I = P0_delta
        
        # Vector chỉ phương của d: u_d = n x u_delta
        u_d = cross(normal, u_delta)
        u_d = simplify_vector(u_d)
        
        # Xử lý trường hợp u_d = (0,0,0) (u_delta song song với normal)
        if u_d == (0, 0, 0):
            # Chọn vector vuông góc với u_delta và nằm trong mặt phẳng
            u_d = perpendicular_vector(u_delta)
            # Đảm bảo u_d vuông góc với normal (nằm trong mặt phẳng)
            # Nếu không, tìm u_d = normal x (u_delta x normal)
            cross_temp = cross(u_delta, normal)
            if cross_temp != (0, 0, 0):
                u_d = simplify_vector(cross(normal, cross_temp))
        
        # Đường thẳng d qua I với vtcp u_d
        line_d_style = random.choice(["canonical", "param"])
        I_point = (int(round(I[0])), int(round(I[1])), int(round(I[2])))
        line_d = {"label": "d", "point": I_point, "direction": u_d, "style": line_d_style}
        
        plane = {"label": "P", "normal": normal, "d": plane_d}
        
        # Tạo các phương án sai
        # Option 1: Sai vector chỉ phương (không vuông góc với u_delta)
        wrong_u1 = (u_d[0] + random.choice([1, 2]), u_d[1] + random.choice([1, -1]), u_d[2])
        if wrong_u1 == (0, 0, 0) or wrong_u1 == u_d:
            wrong_u1 = (u_d[0] + 1, u_d[1], u_d[2] + 1)
        wrong_line1 = {"label": "d", "point": I_point, "direction": wrong_u1, "style": line_d_style}
        
        # Option 2: Sai điểm đi qua
        wrong_point = (I_point[0] + random.randint(1, 3), I_point[1] + random.randint(1, 3), I_point[2] + random.randint(1, 3))
        wrong_line2 = {"label": "d", "point": wrong_point, "direction": u_d, "style": line_d_style}
        
        # Option 3: Sai cả hai
        wrong_line3 = {"label": "d", "point": wrong_point, "direction": wrong_u1, "style": line_d_style}
        
        return {
            "delta": delta,
            "plane": plane,
            "line_d": line_d,
            "wrong_line1": wrong_line1,
            "wrong_line2": wrong_line2,
            "wrong_line3": wrong_line3,
            "I": I_point,
            "u_d": u_d,
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

        # Statement a: Mặt cầu và đường thẳng
        data_a = params["a"]
        sphere_eq_a = format_sphere_expression(data_a["sphere"])
        line_expr_a = format_line_expression(data_a["line"])
        sphere_label_a = f"\\({data_a['sphere']['label']}\\)"
        line_label_a = f"\\({data_a['line']['label']}\\)"
        
        # Biểu thức: k1*m + k2*a + k3*b + k4*c + k5*x + k6*y + k7*z
        expr_a_parts: List[str] = []
        append_linear_term(expr_a_parts, data_a["expr_coeffs"][0], "m")
        append_linear_term(expr_a_parts, data_a["expr_coeffs"][1], "a")
        append_linear_term(expr_a_parts, data_a["expr_coeffs"][2], "b")
        append_linear_term(expr_a_parts, data_a["expr_coeffs"][3], "c")
        append_linear_term(expr_a_parts, data_a["expr_coeffs"][4], "x")
        append_linear_term(expr_a_parts, data_a["expr_coeffs"][5], "y")
        append_linear_term(expr_a_parts, data_a["expr_coeffs"][6], "z")
        expr_a = " ".join(expr_a_parts) if expr_a_parts else "0"
        
        true_text_a = (
            f"Cho điểm M bất kì thuộc mặt cầu ({sphere_label_a}): \\({sphere_eq_a}\\) "
            f"và N bất kì thuộc đường thẳng {line_label_a}: \\({line_expr_a}\\). "
            f"Biết MN đạt GTNN là m khi M(a, b, c) và N(x, y, z). "
            f"Khi đó \\({expr_a} = {data_a['value']}\\)."
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

        # Statement b: 2 mặt cầu
        data_b = params["b"]
        sphere1_eq = format_sphere_expression(data_b["sphere1"])
        sphere2_eq = format_sphere_expression(data_b["sphere2"])
        sphere1_label = f"\\({data_b['sphere1']['label']}\\)"
        sphere2_label = f"\\({data_b['sphere2']['label']}\\)"
        
        # Biểu thức với 14 biến
        expr_b_parts: List[str] = []
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][0], "m")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][1], "M")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][2], "a")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][3], "b")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][4], "c")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][5], "x")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][6], "y")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][7], "z")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][8], "p")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][9], "q")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][10], "r")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][11], "k")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][12], "l")
        append_linear_term(expr_b_parts, data_b["expr_coeffs"][13], "e")
        expr_b = " ".join(expr_b_parts) if expr_b_parts else "0"
        
        true_text_b = (
            f"Cho điểm M bất kì thuộc mặt cầu ({sphere1_label}): \\({sphere1_eq}\\) "
            f"và N bất kì thuộc mặt cầu ({sphere2_label}): \\({sphere2_eq}\\).\n"
            f"Biết MN đạt GTNN là m khi M(a, b, c) và N(x, y, z). "
            f"MN đạt GTLN là M khi M(p, q, r) và N(k, l, e).\n"
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

        # Statement c: 2 đường thẳng
        data_c = params["c"]
        line1_expr_c = format_line_expression(data_c["line1"])
        line2_expr_c = format_line_expression(data_c["line2"])
        line1_label = f"\\({data_c['line1']['label']}\\)"
        line2_label = f"\\({data_c['line2']['label']}\\)"
        
        # Biểu thức: k1*m + k2*a + k3*b + k4*c + k5*x + k6*y + k7*z
        expr_c_parts: List[str] = []
        append_linear_term(expr_c_parts, data_c["expr_coeffs"][0], "m")
        append_linear_term(expr_c_parts, data_c["expr_coeffs"][1], "a")
        append_linear_term(expr_c_parts, data_c["expr_coeffs"][2], "b")
        append_linear_term(expr_c_parts, data_c["expr_coeffs"][3], "c")
        append_linear_term(expr_c_parts, data_c["expr_coeffs"][4], "x")
        append_linear_term(expr_c_parts, data_c["expr_coeffs"][5], "y")
        append_linear_term(expr_c_parts, data_c["expr_coeffs"][6], "z")
        expr_c = " ".join(expr_c_parts) if expr_c_parts else "0"
        
        true_text_c = (
            f"Cho điểm M bất kì thuộc đường thẳng {line1_label}: \\({line1_expr_c}\\) "
            f"và N bất kì thuộc đường thẳng {line2_label}: \\({line2_expr_c}\\). "
            f"Biết MN đạt GTNN là m khi M(a, b, c) và N(x, y, z). "
            f"Khi đó \\({expr_c} = {data_c['value']}\\)."
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

        # Statement d: Giao tuyến vuông góc
        data_d = params["d"]
        delta_expr = format_line_expression(data_d["delta"])
        plane_eq = format_plane_equation(
            data_d["plane"]["normal"][0],
            data_d["plane"]["normal"][1],
            data_d["plane"]["normal"][2],
            data_d["plane"]["d"],
        )
        delta_label = f"\\({data_d['delta']['label']}\\)"
        plane_label = f"\\({data_d['plane']['label']}\\)"
        
        # Tạo 4 phương án (1 đúng, 3 sai)
        correct_line_expr = format_line_expression(data_d["line_d"])
        wrong1_expr = format_line_expression(data_d["wrong_line1"])
        wrong2_expr = format_line_expression(data_d["wrong_line2"])
        wrong3_expr = format_line_expression(data_d["wrong_line3"])
        
        options = [correct_line_expr, wrong1_expr, wrong2_expr, wrong3_expr]
        random.shuffle(options)
        correct_index = options.index(correct_line_expr)
        
        true_text_d = (
            f"Cho đường thẳng {delta_label}: \\({delta_expr}\\) "
            f"và mặt phẳng ({plane_label}): \\({plane_eq}\\). "
            f"Phương trình đường thẳng \\(d\\) nằm trong ({plane_label}) sao cho \\(d\\) cắt và vuông góc với {delta_label} là: "
            f"\\({correct_line_expr}\\)."
        )
        false_text_d = true_text_d.replace(correct_line_expr, options[(correct_index + 1) % 4])
        
        statements_info.append(
            {
                "label": "d",
                "true_text": true_text_d,
                "false_text": false_text_d,
                "display_true": "đúng",
                "display_false": "sai",
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
                append_linear_term(expr_parts, data["expr_coeffs"][0], "m")
                append_linear_term(expr_parts, data["expr_coeffs"][1], "a")
                append_linear_term(expr_parts, data["expr_coeffs"][2], "b")
                append_linear_term(expr_parts, data["expr_coeffs"][3], "c")
                append_linear_term(expr_parts, data["expr_coeffs"][4], "x")
                append_linear_term(expr_parts, data["expr_coeffs"][5], "y")
                append_linear_term(expr_parts, data["expr_coeffs"][6], "z")
                expr = " ".join(expr_parts) if expr_parts else "0"
                status = " \\quad(\\text{đúng})" if is_true else f" \\neq {displayed_value} \\Rightarrow \\text{{sai}}"
                m_val = data['m']
                m_formatted = f"{m_val:.2f}" if m_val > 0 else "0"
                solution_text = (
                    f"a) Khoảng cách từ tâm mặt cầu đến đường thẳng: \\(d \\approx {data['d_value']:.2f}\\).\n\n"
                    f"Bán kính mặt cầu: \\(R = {data['R']}\\).\n\n"
                    f"GTNN của MN là: \\(m \\approx {m_formatted}\\) đạt tại \\(M{format_point_float(data['M'])}\\) và \\(N{format_point_float(data['N'])}\\).\n\n"
                    f"Vậy \\({expr} = {data['value']}{status}\\)"
                )
                solutions.append(solution_text)
            elif label == "b":
                data = params["b"]
                expr_parts = []
                for i in range(14):
                    syms = ["m", "M", "a", "b", "c", "x", "y", "z", "p", "q", "r", "k", "l", "e"]
                    append_linear_term(expr_parts, data["expr_coeffs"][i], syms[i])
                expr = " ".join(expr_parts) if expr_parts else "0"
                status = " \\quad(\\text{đúng})" if is_true else f" \\neq {displayed_value} \\Rightarrow \\text{{sai}}"
                solution_text = (
                    f"b) Khoảng cách giữa hai tâm mặt cầu: \\(d \\approx {data['d']:.2f}\\).\n\n"
                    f"Bán kính: \\(R_1 = {data['R1']}\\), \\(R_2 = {data['R2']}\\).\n\n"
                    f"GTNN: \\(m = {data['m']}\\) đạt tại \\(M_{{\\min}}{format_point(data['M_min'])}\\) và \\(N_{{\\min}}{format_point(data['N_min'])}\\).\n\n"
                    f"GTLN: \\(M = {data['M']}\\) đạt tại \\(M_{{\\max}}{format_point(data['M_max'])}\\) và \\(N_{{\\max}}{format_point(data['N_max'])}\\).\n\n"
                    f"Vậy \\({expr} = {data['value']}{status}\\)"
                )
                solutions.append(solution_text)
            elif label == "c":
                data = params["c"]
                expr_parts = []
                append_linear_term(expr_parts, data["expr_coeffs"][0], "m")
                append_linear_term(expr_parts, data["expr_coeffs"][1], "a")
                append_linear_term(expr_parts, data["expr_coeffs"][2], "b")
                append_linear_term(expr_parts, data["expr_coeffs"][3], "c")
                append_linear_term(expr_parts, data["expr_coeffs"][4], "x")
                append_linear_term(expr_parts, data["expr_coeffs"][5], "y")
                append_linear_term(expr_parts, data["expr_coeffs"][6], "z")
                expr = " ".join(expr_parts) if expr_parts else "0"
                status = " \\quad(\\text{đúng})" if is_true else f" \\neq {displayed_value} \\Rightarrow \\text{{sai}}"
                
                # Format khoảng cách với tử và mẫu
                if data["m_denominator_sq"] == 1 or data["m_numerator"] == 0:
                    m_formatted = format_distance(data["m_numerator"] * data["m_numerator"]) if data["m_numerator"] > 0 else "0"
                else:
                    # m = numerator / sqrt(denominator_sq)
                    denom_sqrt = format_distance(data["m_denominator_sq"])
                    if data["m_numerator"] == 0:
                        m_formatted = "0"
                    else:
                        m_formatted = f"\\dfrac{{{data['m_numerator']}}}{{{denom_sqrt}}}"
                
                solution_text = (
                    f"c) Khoảng cách giữa hai đường thẳng: \\(m = {m_formatted}\\).\n\n"
                    f"Điểm \\(M{format_point_float(data['M'])}\\) trên \\(d_1\\) và \\(N{format_point_float(data['N'])}\\) trên \\(d_2\\) sao cho \\(MN \\perp d_1, MN \\perp d_2\\).\n\n"
                    f"Vậy \\({expr} = {data['value']}{status}\\)"
                )
                solutions.append(solution_text)
            else:
                data = params["d"]
                correct_expr = format_line_expression(data["line_d"])
                status = " \\quad(\\text{đúng})" if is_true else " \\quad(\\text{sai})"
                delta_expr = format_line_expression(data['delta'])
                plane_eq = format_plane_equation(
                    data['plane']['normal'][0],
                    data['plane']['normal'][1],
                    data['plane']['normal'][2],
                    data['plane']['d']
                )
                solution_text = (
                    f"d) Đường thẳng \\(d\\) nằm trong mặt phẳng \\((P)\\): \\({plane_eq}\\), cắt và vuông góc với \\(\\delta\\).\n\n"
                    f"Giao điểm của \\(\\delta\\) và \\((P)\\) là: \\(I{format_point(data['I'])}\\).\n\n"
                    f"Vector chỉ phương của \\(d\\): \\(\\vec{{u}}_d = \\vec{{n}}_P \\times \\vec{{u}}_{{\\delta}} = {format_point(data['u_d'])}\\).\n\n"
                    f"Vậy phương trình đường thẳng \\(d\\) đi qua \\(I\\) với vector chỉ phương \\(\\vec{{u}}_d\\).{status}"
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


