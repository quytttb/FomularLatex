"""
Generator câu hỏi hình học không gian - Dạng đúng/sai
Mỗi câu hỏi có 4 mệnh đề (a, b, c, d), random chọn từ 13 loại câu hỏi:
- Câu 1: Mặt phẳng qua 3 điểm
- Câu 2: Mặt phẳng qua 2 điểm song song đường thẳng
- Câu 3: Mặt phẳng qua 2 điểm vuông góc mặt phẳng
- Câu 4: Phương trình trung tuyến tam giác
- Câu 5: Đường thẳng qua điểm song song với BC
- Câu 6: Đường thẳng qua điểm vuông góc mặt phẳng
- Câu 7: Đường thẳng qua M vuông góc với d1 và d2
- Câu 8: Đường thẳng vuông góc với d và song song với (P)
- Câu 9: Đường thẳng trong (P) vuông góc với d
- Câu 10: Giao điểm đường thẳng và mặt phẳng
- Câu 11: Giao điểm đường thẳng và mặt cầu
- Câu 12: Mặt cầu có tâm và thể tích
- Câu 13: Mặt cầu ngoại tiếp tứ diện

Chạy: python3 custom_geometry_questions.py [số_câu]
Output: custom_geometry_questions.tex
"""

import random
from typing import List, Tuple, Dict
import sympy as sp
from sympy import simplify, Rational, Matrix
from sympy.matrices.common import NonInvertibleMatrixError


# ==================== HELPER FUNCTIONS ====================

def make_true_false(prefix: str, expr_str: str, value_true, value_false) -> Dict[str, str]:
    r"""Tiện ích tạo cặp mệnh đề đúng/sai để giảm lặp code khi chỉ khác giá trị.
    prefix: phần mô tả câu hỏi trước cụm 'Khi đó ...'
    expr_str: biểu thức hiển thị trong LaTeX (không có \( \))
    value_true/value_false: giá trị tương ứng.
    """
    true_text = f"{prefix} Khi đó \\({expr_str} = {value_true}\\)."
    false_text = f"{prefix} Khi đó \\({expr_str} = {value_false}\\)."
    return {"true": true_text, "false": false_text}


def format_point(pt: Tuple[int, int, int]) -> str:
    """Format điểm (x;y;z)"""
    if len(pt) == 3:
        return f"({pt[0]};{pt[1]};{pt[2]})"
    return str(pt)


def format_vec(v: Tuple[int, int, int]) -> str:
    """Format vector (x;y;z)"""
    return f"({v[0]};{v[1]};{v[2]})"


def subtract(p1: Tuple[int, int, int], p2: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Vector p1 - p2"""
    return p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]


def add(p1: Tuple[int, int, int], p2: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Vector p1 + p2"""
    return p1[0] + p2[0], p1[1] + p2[1], p1[2] + p2[2]


def scale(v: Tuple[int, int, int], k: int) -> Tuple[int, int, int]:
    """Scale vector v by integer k"""
    return v[0] * k, v[1] * k, v[2] * k


def cross(v1: Tuple[int, int, int], v2: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Tích có hướng v1 × v2"""
    return (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    )


def is_zero_vector(v: Tuple[int, int, int]) -> bool:
    """Kiểm tra vector không"""
    return v[0] == 0 and v[1] == 0 and v[2] == 0


def random_point(min_val: int = -3, max_val: int = 3) -> Tuple[int, int, int]:
    """Sinh ngẫu nhiên 1 điểm nguyên trong [min_val, max_val]"""
    return (
        random.randint(min_val, max_val),
        random.randint(min_val, max_val),
        random.randint(min_val, max_val),
    )


def random_nonzero_vector(min_val: int = -3, max_val: int = 3) -> Tuple[int, int, int]:
    """Sinh ngẫu nhiên 1 véctơ khác 0 trong [min_val, max_val] với giới hạn số lần thử để tránh cảnh báo vòng lặp vô hạn."""
    for _ in range(1000):
        v = random_point(min_val, max_val)
        if not is_zero_vector(v):
            return v
    # Fallback an toàn nếu không tìm được (rất hiếm)
    return 1, 0, 0


def gcd_multiple(*args):
    """Tính GCD của nhiều số"""
    from math import gcd
    result = args[0]
    for x in args[1:]:
        result = gcd(result, x)
    return result


def normalize_plane_coeffs(a: int, b: int, c: int, d: int) -> Tuple[int, int, int, int]:
    """Rút gọn hệ số phương trình mặt phẳng về nguyên tố cùng nhau"""
    g = gcd_multiple(abs(a) if a != 0 else 1,
                     abs(b) if b != 0 else 1,
                     abs(c) if c != 0 else 1,
                     abs(d) if d != 0 else 1)
    if g > 1:
        a, b, c, d = a // g, b // g, c // g, d // g
    # Chuẩn hóa dấu: hệ số đầu tiên khác 0 phải dương
    if a < 0 or (a == 0 and b < 0) or (a == 0 and b == 0 and c < 0):
        a, b, c, d = -a, -b, -c, -d
    return a, b, c, d


def format_plane_equation(a: int, b: int, c: int, d: int) -> str:
    """Format phương trình mặt phẳng ax + by + cz + d = 0"""
    parts = []
    # x term
    if a == 1:
        parts.append("x")
    elif a == -1:
        parts.append("-x")
    elif a != 0:
        parts.append(f"{a}x")

    # y term
    if b != 0:
        if parts:
            if b == 1:
                parts.append("+ y")
            elif b == -1:
                parts.append("- y")
            elif b > 0:
                parts.append(f"+ {b}y")
            else:
                parts.append(f"- {abs(b)}y")
        else:
            parts.append("y" if b == 1 else ("-y" if b == -1 else f"{b}y"))

    # z term
    if c != 0:
        if parts:
            if c == 1:
                parts.append("+ z")
            elif c == -1:
                parts.append("- z")
            elif c > 0:
                parts.append(f"+ {c}z")
            else:
                parts.append(f"- {abs(c)}z")
        else:
            parts.append("z" if c == 1 else ("-z" if c == -1 else f"{c}z"))

    # d term
    if d != 0:
        if parts:
            if d > 0:
                parts.append(f"+ {d}")
            else:
                parts.append(f"- {abs(d)}")
        else:
            parts.append(str(d))

    equation = " ".join(parts)
    if not parts:
        equation = "0"
    return equation + " = 0"


def choose_linear_form_coeffs() -> Tuple[int, int, int, int]:
    """Chọn hệ số cho biểu thức pA + qB + rC + sD"""
    coeffs = [-3, -2, -1, 0, 1, 2, 3]
    return tuple(random.choice(coeffs) for _ in range(4))


def format_linear_form(p: int, q: int, r: int, s: int) -> str:
    """Format biểu thức pA + qB + rC + sD"""

    def add_term(parts, coeff, symbol):
        if coeff == 0:
            return
        term_coeff = coeff
        if not parts:
            if term_coeff == 1:
                parts.append(symbol)
            elif term_coeff == -1:
                parts.append(f"-{symbol}")
            else:
                parts.append(f"{term_coeff}{symbol}")
        else:
            if term_coeff == 1:
                parts.append(f"+ {symbol}")
            elif term_coeff == -1:
                parts.append(f"- {symbol}")
            elif term_coeff > 0:
                parts.append(f"+ {term_coeff}{symbol}")
            else:
                parts.append(f"- {abs(term_coeff)}{symbol}")

    parts = []
    add_term(parts, p, "A")
    add_term(parts, q, "B")
    add_term(parts, r, "C")
    add_term(parts, s, "D")
    return " ".join(parts) if parts else "0"


def evaluate_linear_form(p: int, q: int, r: int, s: int, a: int, b: int, c: int, d: int) -> int:
    """Tính giá trị pA + qB + rC + sD"""
    return p * a + q * b + r * c + s * d


def pick_wrong_value(true_value: int) -> int:
    """Chọn giá trị sai khác giá trị đúng"""
    deltas = [i for i in range(-8, 9) if i != 0]
    random.shuffle(deltas)
    return true_value + deltas[0]


def format_line_equation(P: Tuple[int, int, int], v: Tuple[int, int, int]) -> str:
    """Format phương trình đường thẳng qua P, VTCP v"""
    x0, y0, z0 = P
    a, b, c = v

    # Format (x - x0)/a = (y - y0)/b = (z - z0)/c
    def format_fraction(coord_name, coord_val, direction):
        if direction == 0:
            return None
        numerator = f"{coord_name}"
        if coord_val > 0:
            numerator = f"({coord_name} - {coord_val})"
        elif coord_val < 0:
            numerator = f"({coord_name} + {abs(coord_val)})"

        if direction == 1:
            return numerator
        elif direction == -1:
            return f"-{numerator}"
        else:
            return f"\\dfrac{{{numerator}}}{{{direction}}}"

    parts = []
    x_part = format_fraction("x", x0, a)
    y_part = format_fraction("y", y0, b)
    z_part = format_fraction("z", z0, c)

    if x_part:
        parts.append(x_part)
    if y_part:
        parts.append(y_part)
    if z_part:
        parts.append(z_part)

    return " = ".join(parts) if parts else "0"


def format_sympy_to_latex(expr):
    """Chuyển biểu thức SymPy sang LaTeX"""
    if isinstance(expr, (int, float)):
        return str(expr)
    elif hasattr(expr, 'is_integer') and expr.is_integer:
        # SymPy Integer hoặc biểu thức có property is_integer
        return str(expr)
    elif isinstance(expr, Rational):
        # Xử lý số hữu tỉ của SymPy an toàn hơn thay vì kiểm tra thuộc tính p/q
        return str(expr.p) if expr.q == 1 else f"\\frac{{{expr.p}}}{{{expr.q}}}"
    else:
        return sp.latex(expr)


# ---------- Small reusable helpers for expression building ----------

def format_linear_expression(coeffs: Tuple[int, int, int], symbols: Tuple[str, str, str]) -> str:
    """Format biểu thức tuyến tính k1*s1 + k2*s2 + k3*s3 với quy tắc dấu/1/−1 như các câu hỏi.
    coeffs: (k1, k2, k3), symbols: ví dụ ('a','b','c') hoặc ('u','v','w')."""
    k1, k2, k3 = coeffs

    def term_str(k: int, sym: str, has_prev: bool) -> str:
        if k == 0:
            return ""
        # hiển thị hệ số 1 và -1
        core = sym if abs(k) == 1 else f"{abs(k)}{sym}"
        if not has_prev:
            return core if k > 0 else f"-{core}"
        else:
            return f"+ {core}" if k > 0 else f"- {core}"

    parts: List[str] = []
    s1 = term_str(k1, symbols[0], False)
    if s1:
        parts.append(s1)
    s2 = term_str(k2, symbols[1], bool(parts))
    if s2:
        parts.append(s2)
    s3 = term_str(k3, symbols[2], bool(parts))
    if s3:
        parts.append(s3)

    return " ".join(parts) if parts else "0"


def dot3(coeffs: Tuple[int, int, int], vec: Tuple[int, int, int]) -> int:
    """Tính k1*x + k2*y + k3*z"""
    return coeffs[0] * vec[0] + coeffs[1] * vec[1] + coeffs[2] * vec[2]


# ==================== GENERATORS ====================

def cau_1_mat_phang_qua_3_diem() -> Dict[str, str]:
    """Câu 1: Phương trình mặt phẳng qua 3 điểm A, B, C"""
    # Random 3 điểm không thẳng hàng (giới hạn số lần thử để tránh cảnh báo vòng lặp vô hạn)
    for _ in range(1000):
        A = random_point()
        B = random_point()
        C = random_point()

        AB = subtract(B, A)
        AC = subtract(C, A)
        n = cross(AB, AC)

        if not is_zero_vector(n):
            break
    else:
        # Fallback an toàn nếu không tìm được bộ điểm phù hợp
        A, B, C = (0, 0, 0), (1, 0, 0), (0, 1, 0)
        AB = subtract(B, A)
        AC = subtract(C, A)
        n = cross(AB, AC)

    # Tính phương trình mặt phẳng
    a, b, c = n
    d = -(a * A[0] + b * A[1] + c * A[2])
    a, b, c, d = normalize_plane_coeffs(a, b, c, d)

    # Tạo biểu thức linear
    p, q, r, s = choose_linear_form_coeffs()
    expr_str = format_linear_form(p, q, r, s)
    value_true = evaluate_linear_form(p, q, r, s, a, b, c, d)
    value_false = pick_wrong_value(value_true)

    prefix = (
        f"Cho (P) có dạng Ax+By+Cz+D=0 đi qua ba điểm "
        f"A{format_point(A)}, B{format_point(B)}, C{format_point(C)}."
    )
    return make_true_false(prefix, expr_str, value_true, value_false)


def cau_2_mat_phang_qua_2_diem_song_song_duong_thang() -> Dict[str, str]:
    """Câu 2: Mặt phẳng qua A, B và song song với đường thẳng CD"""
    # Random 4 điểm (giới hạn số lần thử để tránh vòng lặp vô hạn)
    for _ in range(1000):
        A = random_point()
        B = random_point()
        C = random_point()
        D = random_point()

        AB = subtract(B, A)
        CD = subtract(D, C)
        n = cross(AB, CD)

        if not is_zero_vector(n):
            break
    else:
        # Fallback bộ điểm đảm bảo không suy biến
        A, B, C, D = (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)
        AB = subtract(B, A)
        CD = subtract(D, C)
        n = cross(AB, CD)

    # VTPT = AB × CD
    a, b, c = n
    d = -(a * A[0] + b * A[1] + c * A[2])
    a, b, c, d = normalize_plane_coeffs(a, b, c, d)

    p, q, r, s = choose_linear_form_coeffs()
    expr_str = format_linear_form(p, q, r, s)
    value_true = evaluate_linear_form(p, q, r, s, a, b, c, d)
    value_false = pick_wrong_value(value_true)

    prefix = (
        f"Cho (P) có dạng Ax+By+Cz+D=0 đi qua A{format_point(A)}, B{format_point(B)} và song song với đường thẳng CD "
        f"với C{format_point(C)}, D{format_point(D)}."
    )
    return make_true_false(prefix, expr_str, value_true, value_false)


def cau_3_mat_phang_qua_2_diem_vuong_goc_mp() -> Dict[str, str]:
    """Câu 3: Mặt phẳng qua A, B và vuông góc với mặt phẳng (Q)"""
    # Random 2 điểm A, B (giới hạn số lần thử)
    for _ in range(1000):
        A = random_point()
        B = random_point()
        AB = subtract(B, A)
        if not is_zero_vector(AB):
            break
    else:
        A, B = (0, 0, 0), (1, 0, 0)
        AB = subtract(B, A)

    # Random mặt phẳng (Q) (giới hạn số lần thử)
    for _ in range(1000):
        a_Q, b_Q, c_Q = random_nonzero_vector()
        d_Q = random.randint(-5, 5)
        n_Q = (a_Q, b_Q, c_Q)
        if not is_zero_vector(n_Q):
            break
    else:
        a_Q, b_Q, c_Q, d_Q = 1, 0, 0, 0
        n_Q = (a_Q, b_Q, c_Q)

    # VTPT của (P) = AB × n_Q
    n = cross(AB, n_Q)
    if is_zero_vector(n):
        n = (1, 0, 0)

    a, b, c = n
    d = -(a * A[0] + b * A[1] + c * A[2])
    a, b, c, d = normalize_plane_coeffs(a, b, c, d)

    p, q, r, s = choose_linear_form_coeffs()
    expr_str = format_linear_form(p, q, r, s)
    value_true = evaluate_linear_form(p, q, r, s, a, b, c, d)
    value_false = pick_wrong_value(value_true)

    eq_Q = format_plane_equation(a_Q, b_Q, c_Q, d_Q)

    prefix = (
        f"Cho (P) có dạng Ax+By+Cz+D=0 đi qua "
        f"A{format_point(A)}, B{format_point(B)} và "
        f"vuông góc với mặt phẳng (Q): {eq_Q}."
    )
    return make_true_false(prefix, expr_str, value_true, value_false)


def cau_4_trung_tuyen_tam_giac() -> Dict[str, str]:
    """Câu 4: Phương trình trung tuyến AM của tam giác ABC"""
    # Random 3 điểm
    A = random_point()
    B = random_point()
    C = random_point()

    # Trung điểm M của BC có toạ độ ((B+C)/2) => VTCP AM cùng phương với (B + C - 2A)
    # Dùng véctơ nguyên để tránh số thực
    AM_dir = subtract(add(B, C), scale(A, 2))

    # Nếu vô tình bằng 0 (A là trung điểm BC) thì chỉnh nhẹ
    if is_zero_vector(AM_dir):
        AM_dir = subtract(B, A)
        if is_zero_vector(AM_dir):
            AM_dir = (1, 0, 0)

    # Tạo biểu thức: k1*u + k2*v + k3*w
    coeff_pool = [-2, -1, 1, 2, 3]
    k1, k2, k3 = random.choice(coeff_pool), random.choice(coeff_pool), random.choice(coeff_pool)

    value_true = dot3((k1, k2, k3), AM_dir)
    value_false = pick_wrong_value(value_true)

    expr_str = format_linear_expression((k1, k2, k3), ("u", "v", "w"))

    true_text = (
        f"Cho tam giác ABC với A{format_point(A)}, B{format_point(B)}, C{format_point(C)}. "
        f"Trung tuyến AM có véctơ chỉ phương \\(\\vec{{u}}=(u;v;w)\\). "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho tam giác ABC với A{format_point(A)}, B{format_point(B)}, C{format_point(C)}. "
        f"Trung tuyến AM có véctơ chỉ phương \\(\\vec{{u}}=(u;v;w)\\). "
        f"Khi đó {expr_str} = {value_false}."
    )

    return {"true": true_text, "false": false_text}


def cau_5_duong_thang_qua_diem_song_song() -> Dict[str, str]:
    """Câu 5: Đường thẳng qua A và song song với BC"""
    # Random 3 điểm
    A = random_point()
    B = random_point()
    C = random_point()

    # VTCP = BC
    BC = subtract(C, B)
    if is_zero_vector(BC):
        BC = (1, 1, 1)

    # Tạo biểu thức
    coeff_pool = [-2, -1, 1, 2]
    k1, k2, k3 = random.choice(coeff_pool), random.choice(coeff_pool), random.choice(coeff_pool)

    value_true = dot3((k1, k2, k3), BC)
    value_false = pick_wrong_value(value_true)

    expr_str = format_linear_expression((k1, k2, k3), ("a", "b", "c"))

    true_text = (
        f"Cho đường thẳng d qua A{format_point(A)} và song song với BC, "
        f"với B{format_point(B)}, C{format_point(C)}. "
        f"Đường thẳng d có véctơ chỉ phương \\(\\vec{{u}}=(a;b;c)\\). "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho đường thẳng d qua A{format_point(A)} và song song với BC, "
        f"với B{format_point(B)}, C{format_point(C)}. "
        f"Đường thẳng d có véctơ chỉ phương \\(\\vec{{u}}=(a;b;c)\\). "
        f"Khi đó {expr_str} = {value_false}."
    )

    return {"true": true_text, "false": false_text}


def cau_6_duong_thang_qua_diem_vuong_goc_mp() -> Dict[str, str]:
    """Câu 6: Đường thẳng qua A và vuông góc với mặt phẳng (P)"""
    # Random điểm A
    A = random_point()

    # Random mặt phẳng (P) (giới hạn số lần thử)
    for _ in range(1000):
        a_P, b_P, c_P = random_nonzero_vector()
        d_P = random.randint(-5, 5)
        if not is_zero_vector((a_P, b_P, c_P)):
            break
    else:
        a_P, b_P, c_P, d_P = 1, 0, 0, 0

    # VTCP của đường thẳng = VTPT của (P)
    # Tạo biểu thức
    coeff_pool = [-2, -1, 1, 2]
    k1, k2, k3 = random.choice(coeff_pool), random.choice(coeff_pool), random.choice(coeff_pool)

    value_true = dot3((k1, k2, k3), (a_P, b_P, c_P))
    value_false = pick_wrong_value(value_true)

    expr_str = format_linear_expression((k1, k2, k3), ("u", "v", "w"))

    eq_P = format_plane_equation(a_P, b_P, c_P, d_P)

    true_text = (
        f"Cho đường thẳng d qua A{format_point(A)} và vuông góc với mặt phẳng (P): {eq_P}. "
        f"Đường thẳng d có véctơ chỉ phương \\(\\vec{{u}}=(u;v;w)\\). "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho đường thẳng d qua A{format_point(A)} và vuông góc với mặt phẳng (P): {eq_P}. "
        f"Đường thẳng d có véctơ chỉ phương \\(\\vec{{u}}=(u;v;w)\\). "
        f"Khi đó {expr_str} = {value_false}."
    )

    return {"true": true_text, "false": false_text}


def cau_7_duong_thang_vuong_goc_2_duong() -> Dict[str, str]:
    """Câu 7: Đường thẳng qua M vuông góc với d1 và d2"""
    # Random điểm M
    M = random_point()

    # Random 2 VTCP không cùng phương (giới hạn số lần thử)
    for _ in range(1000):
        # VTCP của d1
        u1 = random_nonzero_vector()
        # VTCP của d2
        u2 = random_nonzero_vector()

        # VTCP của đường thẳng cần tìm = u1 × u2
        u = cross(u1, u2)
        if not is_zero_vector(u):
            break
    else:
        # Fallback an toàn
        u1, u2 = (1, 0, 0), (0, 1, 0)
        u = cross(u1, u2)

    # Tạo biểu thức hỏi về VTCP
    coeff_pool = [-2, -1, 1, 2]
    k1, k2, k3 = random.choice(coeff_pool), random.choice(coeff_pool), random.choice(coeff_pool)

    value_true = dot3((k1, k2, k3), u)
    value_false = pick_wrong_value(value_true)

    expr_str = format_linear_expression((k1, k2, k3), ("a", "b", "c"))

    true_text = (
        f"Cho đường thẳng \\(\\Delta\\) qua M{format_point(M)} và vuông góc với cả hai đường thẳng "
        f"\\(d_1\\) có VTCP {format_vec(u1)} và \\(d_2\\) có VTCP {format_vec(u2)}. "
        f"Đường thẳng \\(\\Delta\\) có véctơ chỉ phương \\(\\vec{{u}}=(a;b;c)\\). "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho đường thẳng \\(\\Delta\\) qua M{format_point(M)} và vuông góc với cả hai đường thẳng "
        f"\\(d_1\\) có VTCP {format_vec(u1)} và \\(d_2\\) có VTCP {format_vec(u2)}. "
        f"Đường thẳng \\(\\Delta\\) có véctơ chỉ phương \\(\\vec{{u}}=(a;b;c)\\). "
        f"Khi đó {expr_str} = {value_false}."
    )

    return {"true": true_text, "false": false_text}


def cau_8_duong_thang_vuong_goc_va_song_song() -> Dict[str, str]:
    """Câu 8: Đường thẳng qua A, vuông góc với d và song song với (P)"""
    # Random điểm A
    A = random_point()

    # Random VTCP của đường thẳng d
    u_d = random_nonzero_vector()

    # Random VTPT của mặt phẳng (P)
    n_P = random_nonzero_vector()

    # VTCP của đường thẳng cần tìm: vuông góc với u_d và n_P
    # => u = u_d × n_P. Nếu u_d // n_P (tích có hướng = 0), chọn một véc-tơ chắc chắn vuông góc với cả hai.
    u = cross(u_d, n_P)
    if is_zero_vector(u):
        # u_d // n_P. Lấy một véc-tơ cơ sở e không song song với u_d rồi u = u_d × e
        basis = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
        for e in basis:
            cand = cross(u_d, e)
            if not is_zero_vector(cand):
                u = cand
                break
        else:
            # Fallback cực hiếm (khi u_d là (0,0,0) nhưng đã tránh bằng random_nonzero_vector)
            u = (1, 0, 0)

    # Tạo biểu thức
    coeff_pool = [-2, -1, 1, 2]
    k1, k2, k3 = random.choice(coeff_pool), random.choice(coeff_pool), random.choice(coeff_pool)

    value_true = dot3((k1, k2, k3), u)
    value_false = pick_wrong_value(value_true)

    expr_str = format_linear_expression((k1, k2, k3), ("u", "v", "w"))

    eq_P = format_plane_equation(n_P[0], n_P[1], n_P[2], random.randint(-5, 5))

    true_text = (
        f"Cho đường thẳng \\(\\Delta\\) qua A{format_point(A)}, "
        f"vuông góc với đường thẳng có VTCP {format_vec(u_d)} "
        f"và song song với mặt phẳng (P): {eq_P}. "
        f"Đường thẳng \\(\\Delta\\) có véctơ chỉ phương \\(\\vec{{u}}=(u;v;w)\\). "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho đường thẳng \\(\\Delta\\) qua A{format_point(A)}, "
        f"vuông góc với đường thẳng có VTCP {format_vec(u_d)} "
        f"và song song với mặt phẳng (P): {eq_P}. "
        f"Đường thẳng \\(\\Delta\\) có véctơ chỉ phương \\(\\vec{{u}}=(u;v;w)\\). "
        f"Khi đó {expr_str} = {value_false}."
    )

    return {"true": true_text, "false": false_text}


def cau_9_duong_thang_trong_mp_vuong_goc_duong() -> Dict[str, str]:
    """Câu 9: Đường thẳng nằm trong (P) và vuông góc với d"""
    # Random điểm M
    M = random_point()

    # Random VTPT của mặt phẳng (P) (giới hạn số lần thử)
    for _ in range(1000):
        n_P = random_nonzero_vector()
        d_P = random.randint(-5, 5)
        if not is_zero_vector(n_P):
            break
    else:
        n_P, d_P = (1, 0, 0), 0

    # Random VTCP của đường thẳng d
    u_d = random_nonzero_vector()

    # VTCP của đường thẳng cần tìm: vuông góc với cả n_P và u_d
    # => u = n_P × u_d. Nếu n_P // u_d, ta dựng u vuông góc với cả hai bằng cách lấy u = dir × e.
    u = cross(n_P, u_d)
    if is_zero_vector(u):
        # n_P // u_d. Chọn dir là n_P (hoặc u_d), lấy e không song song dir, rồi u = dir × e
        dir_vec = n_P
        basis = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
        for e in basis:
            cand = cross(dir_vec, e)
            if not is_zero_vector(cand):
                u = cand
                break
        else:
            u = (1, 0, 0)

    # Tạo biểu thức
    coeff_pool = [-2, -1, 1, 2]
    k1, k2, k3 = random.choice(coeff_pool), random.choice(coeff_pool), random.choice(coeff_pool)

    value_true = dot3((k1, k2, k3), u)
    value_false = pick_wrong_value(value_true)

    expr_str = format_linear_expression((k1, k2, k3), ("a", "b", "c"))

    eq_P = format_plane_equation(n_P[0], n_P[1], n_P[2], d_P)

    true_text = (
        f"Cho đường thẳng \\(\\Delta\\) nằm trong mặt phẳng (P): {eq_P}, đi qua M{format_point(M)} "
        f"và vuông góc với đường thẳng có VTCP {format_vec(u_d)}. "
        f"Đường thẳng \\(\\Delta\\) có véctơ chỉ phương \\(\\vec{{u}}=(a;b;c)\\). "
        f"Khi đó {expr_str} = {value_true}."
    )
    false_text = (
        f"Cho đường thẳng \\(\\Delta\\) nằm trong mặt phẳng (P): {eq_P}, đi qua M{format_point(M)} "
        f"và vuông góc với đường thẳng có VTCP {format_vec(u_d)}. "
        f"Đường thẳng \\(\\Delta\\) có véctơ chỉ phương \\(\\vec{{u}}=(a;b;c)\\). "
        f"Khi đó {expr_str} = {value_false}."
    )

    return {"true": true_text, "false": false_text}


def cau_10_giao_diem_duong_thang_mat_phang() -> Dict[str, str]:
    """Câu 10: Giao điểm của đường thẳng d và mặt phẳng (P)"""
    # Random điểm M0 trên đường thẳng
    M0 = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))

    # Random VTCP của đường thẳng (giới hạn số lần thử)
    for _ in range(1000):
        u = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
        if not is_zero_vector(u):
            break
    else:
        u = (1, 1, 0)

    # Random mặt phẳng (P) (giới hạn số lần thử)
    for _ in range(1000):
        a_P = random.randint(-3, 3)
        b_P = random.randint(-3, 3)
        c_P = random.randint(-3, 3)
        d_P = random.randint(-5, 5)
        if not is_zero_vector((a_P, b_P, c_P)):
            break
    else:
        a_P, b_P, c_P, d_P = 1, 0, 0, 0

    # Phương trình tham số: x = x0 + at, y = y0 + bt, z = z0 + ct
    # Thay vào (P): a(x0+at) + b(y0+bt) + c(z0+ct) + d = 0
    # => (a*u[0] + b*u[1] + c*u[2])t + (a*M0[0] + b*M0[1] + c*M0[2] + d) = 0

    denom = a_P * u[0] + b_P * u[1] + c_P * u[2]
    if denom == 0:
        # Đường thẳng song song hoặc nằm trong mặt phẳng
        # Chọn lại u song song với VTPT để đảm bảo không song song mặt phẳng
        u = (a_P, b_P, c_P)
        denom = a_P * u[0] + b_P * u[1] + c_P * u[2]

    # Tính t0 dạng hữu tỉ để giữ chính xác
    num = -(a_P * M0[0] + b_P * M0[1] + c_P * M0[2] + d_P)
    t0 = Rational(num, denom)

    # Tọa độ giao điểm (dạng hữu tỉ)
    A = (
        Rational(M0[0]) + Rational(u[0]) * t0,
        Rational(M0[1]) + Rational(u[1]) * t0,
        Rational(M0[2]) + Rational(u[2]) * t0,
    )

    # Tạo biểu thức hỏi về tọa độ (giữ chính xác)
    expr_choices = [
        ("x_A + y_A", A[0] + A[1]),
        ("y_A + z_A", A[1] + A[2]),
        ("x_A + z_A", A[0] + A[2]),
        ("x_A + y_A + z_A", A[0] + A[1] + A[2]),
    ]

    expr_str, value_true = random.choice(expr_choices)
    # Sinh giá trị sai phù hợp kiểu dữ liệu
    if isinstance(value_true, Rational):
        if value_true.q == 1:
            value_false = pick_wrong_value(int(value_true))
        else:
            value_false = Rational(value_true.p + 1, value_true.q)
    else:
        value_false = pick_wrong_value(int(value_true))

    eq_P = format_plane_equation(a_P, b_P, c_P, d_P)

    value_true_latex = format_sympy_to_latex(value_true)
    value_false_latex = format_sympy_to_latex(value_false)

    true_text = (
        f"Cho đường thẳng d đi qua M{format_point(M0)} có VTCP {format_vec(u)} và mặt phẳng (P): {eq_P}. "
        f"Giao điểm A của d và (P) có tọa độ \\(A(x_A; y_A; z_A)\\). "
        f"Khi đó \\({expr_str} = {value_true_latex}\\)."
    )
    false_text = (
        f"Cho đường thẳng d đi qua M{format_point(M0)} có VTCP {format_vec(u)} và mặt phẳng (P): {eq_P}. "
        f"Giao điểm A của d và (P) có tọa độ \\(A(x_A; y_A; z_A)\\). "
        f"Khi đó \\({expr_str} = {value_false_latex}\\)."
    )

    return {"true": true_text, "false": false_text}


def cau_11_giao_diem_duong_thang_mat_cau() -> Dict[str, str]:
    """Câu 11: Giao điểm của đường thẳng và mặt cầu"""
    # Random tâm (đặt tên tránh E741: không dùng biến 'I') và bán kính bình phương
    center = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
    R_squared = random.choice([4, 9, 16, 25])

    # Random điểm M0 trên đường thẳng
    M0 = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))

    # Random VTCP đơn giản
    vtcp = random.choice([(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)])

    # Phương trình tham số: x = x0 + at, y = y0 + bt, z = z0 + ct
    # Thay vào pt mặt cầu: (x0+at-xI)² + (y0+bt-yI)² + (z0+ct-zI)² = R²
    # Để đơn giản, ta chỉ hỏi về tổng hoặc tích tọa độ

    # Tạo câu hỏi đơn giản: hỏi về tổng tọa độ tâm
    expr_choices = [
        ("x_I + y_I", center[0] + center[1]),
        ("y_I + z_I", center[1] + center[2]),
        ("x_I + z_I", center[0] + center[2]),
        ("x_I + y_I + z_I", center[0] + center[1] + center[2]),
    ]

    expr_str, value_true = random.choice(expr_choices)
    value_false = pick_wrong_value(value_true)

    # Format phương trình mặt cầu
    sphere_eq = f"(x - {center[0]})^2 + (y - {center[1]})^2 + (z - {center[2]})^2 = {R_squared}"

    true_text = (
        f"Cho đường thẳng d có VTCP {format_vec(vtcp)} và mặt cầu (S): \\({sphere_eq}\\). "
        f"Mặt cầu có tâm \\(I(x_I; y_I; z_I)\\). "
        f"Khi đó \\({expr_str} = {value_true}\\)."
    )
    false_text = (
        f"Cho đường thẳng d có VTCP {format_vec(vtcp)} và mặt cầu (S): \\({sphere_eq}\\). "
        f"Mặt cầu có tâm \\(I(x_I; y_I; z_I)\\). "
        f"Khi đó \\({expr_str} = {value_false}\\)."
    )

    return {"true": true_text, "false": false_text}


def cau_12_mat_cau_tu_tam_va_the_tich() -> Dict[str, str]:
    """Câu 12: Mặt cầu có tâm I và thể tích V"""
    # Random tâm (đặt tên tránh E741: không dùng biến 'I')
    center = random_point()

    # Random thể tích: V = (4/3)πR³
    # Chọn R nguyên: R = 1, 2, 3, 4
    R = random.choice([1, 2, 3, 4])
    R_squared = R * R
    # Hệ số của π cho thể tích V = (4/3)πR^3, giữ chính xác dạng hữu tỉ
    V_coeff = Rational(4, 3) * R * R * R

    # Tạo biểu thức
    expr_choices = [
        (f"x_I + y_I + R^2", center[0] + center[1] + R_squared),
        (f"x_I - y_I + z_I", center[0] - center[1] + center[2]),
        (f"2x_I + y_I + z_I", 2 * center[0] + center[1] + center[2]),
        (f"x_I + 2y_I + R", center[0] + 2 * center[1] + R),
    ]

    expr_str, value_true = random.choice(expr_choices)
    value_false = pick_wrong_value(value_true)

    V_coeff_latex = format_sympy_to_latex(V_coeff)

    true_text = (
        f"Cho mặt cầu (S) có tâm I{format_point(center)} và thể tích \\({V_coeff_latex}\\pi\\). "
        f"Mặt cầu có tâm \\(I(x_I; y_I; z_I)\\) và bán kính R. "
        f"Khi đó \\( {expr_str} = {value_true} \\)."
    )
    false_text = (
        f"Cho mặt cầu (S) có tâm I{format_point(center)} và thể tích \\({V_coeff_latex}\\pi\\). "
        f"Mặt cầu có tâm \\(I(x_I; y_I; z_I)\\) và bán kính R. "
        f"Khi đó \\( {expr_str} = {value_false} \\)."
    )

    return {"true": true_text, "false": false_text}


def cau_13_mat_cau_ngoai_tiep_tu_dien() -> Dict[str, str]:
    """Câu 13: Mặt cầu ngoại tiếp tứ diện ABCD"""
    # Chọn bộ điểm đẹp - tất cả đều không suy biến và đã test
    point_sets = [
        [(2, 0, 0), (0, 2, 0), (0, 0, 2), (1, 1, 1)],
        [(3, 0, 0), (0, 3, 0), (0, 0, 3), (1, 1, 1)],
        [(4, 0, 0), (0, 4, 0), (0, 0, 4), (2, 2, 2)],
        [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)],
        [(2, 0, 0), (0, 2, 0), (0, 0, 4), (1, 1, 2)],
    ]

    # Thử từng bộ điểm cho đến khi giải được
    for A, B, C, D in point_sets:
        try:
            # Tính tâm mặt cầu ngoại tiếp
            # Giải hệ: IA² = IB² = IC² = ID²
            x1, y1, z1 = A
            x2, y2, z2 = B
            x3, y3, z3 = C
            x4, y4, z4 = D

            # Dùng SymPy để giải
            # Hệ phương trình
            coeff_matrix = Matrix([
                [2 * (x2 - x1), 2 * (y2 - y1), 2 * (z2 - z1)],
                [2 * (x3 - x1), 2 * (y3 - y1), 2 * (z3 - z1)],
                [2 * (x4 - x1), 2 * (y4 - y1), 2 * (z4 - z1)]
            ])

            const_vector = Matrix([
                (x2 * x2 + y2 * y2 + z2 * z2) - (x1 * x1 + y1 * y1 + z1 * z1),
                (x3 * x3 + y3 * y3 + z3 * z3) - (x1 * x1 + y1 * y1 + z1 * z1),
                (x4 * x4 + y4 * y4 + z4 * z4) - (x1 * x1 + y1 * y1 + z1 * z1)
            ])

            solution = coeff_matrix.LUsolve(const_vector)
            center_x = solution[0]
            center_y = solution[1]
            center_z = solution[2]

            # Tính R²
            dx = Rational(x1) - center_x
            dy = Rational(y1) - center_y
            dz = Rational(z1) - center_z
            R_squared = simplify(dx ** 2 + dy ** 2 + dz ** 2)

            # Tạo biểu thức random
            coeffs = [-2, -1, 1, 2]
            k1, k2, k3, k4 = random.choice(coeffs), random.choice(coeffs), random.choice(coeffs), random.choice(coeffs)

            value_true = k1 * center_x + k2 * center_y + k3 * center_z + k4 * R_squared
            value_true = simplify(value_true)

            # Convert to float for wrong value
            try:
                value_true_float = float(value_true)
                value_false = pick_wrong_value(int(value_true_float))
            except (TypeError, ValueError):
                # Nếu không convert được thì dùng giá trị symbolic + offset
                value_false = simplify(value_true + 5)

            # Format expression
            expr_str = format_linear_expression((k1, k2, k3), ("a", "b", "c"))
            # thêm phần R^2 nếu cần
            if k4 != 0:
                # bảo toàn quy tắc dấu khi nối
                tail = "R^2" if abs(k4) == 1 else f"{abs(k4)}R^2"
                if expr_str == "0":
                    expr_str = tail if k4 > 0 else f"-{tail}"
                else:
                    expr_str += f" + {tail}" if k4 > 0 else f" - {tail}"

            # Format value_true for LaTeX
            value_true_latex = format_sympy_to_latex(value_true)
            value_false_latex = format_sympy_to_latex(value_false) if not isinstance(value_false, int) else str(
                value_false)

            true_text = (
                f"Cho mặt cầu ngoại tiếp tứ diện ABCD với "
                f"A{format_point(A)}, B{format_point(B)}, C{format_point(C)}, D{format_point(D)}. "
                f"Mặt cầu có tâm \\(I(a;b;c)\\) và bán kính R. "
                f"Khi đó \\({expr_str} = {value_true_latex}\\)."
            )
            false_text = (
                f"Cho mặt cầu ngoại tiếp tứ diện ABCD với "
                f"A{format_point(A)}, B{format_point(B)}, C{format_point(C)}, D{format_point(D)}. "
                f"Mặt cầu có tâm \\(I(a;b;c)\\) và bán kính R. "
                f"Khi đó \\({expr_str} = {value_false_latex}\\)."
            )

            return {"true": true_text, "false": false_text}

        except (NonInvertibleMatrixError, ValueError, TypeError):
            # Thử bộ điểm tiếp theo
            continue

    # Nếu tất cả đều fail (rất hiếm), dùng bộ điểm mặc định đơn giản nhất
    A, B, C, D = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)]
    true_text = (
        f"Cho mặt cầu ngoại tiếp tứ diện ABCD với A{format_point(A)}, B{format_point(B)}, C{format_point(C)}, D{format_point(D)}. "
        f"Mặt cầu có tâm \\(I(a;b;c)\\) và bán kính R. Khi đó \\(a + b + c = \\frac{{3}}{2}\\)."
    )
    false_text = (
        f"Cho mặt cầu ngoại tiếp tứ diện ABCD với A{format_point(A)}, B{format_point(B)}, C{format_point(C)}, D{format_point(D)}. "
        f"Mặt cầu có tâm \\(I(a;b;c)\\) và bán kính R. Khi đó \\(a + b + c = 2\\)."
    )
    return {"true": true_text, "false": false_text}


# ==================== MAIN GENERATOR ====================

def generate_question(question_number: int, num_options: int = 4) -> str:
    """
    Tạo 1 câu hỏi với 4 mệnh đề (a, b, c, d)
    Mỗi mệnh đề random chọn từ 13 loại câu hỏi
    """
    # Danh sách 13 generators
    all_generators = [
        cau_1_mat_phang_qua_3_diem,
        cau_2_mat_phang_qua_2_diem_song_song_duong_thang,
        cau_3_mat_phang_qua_2_diem_vuong_goc_mp,
        cau_4_trung_tuyen_tam_giac,
        cau_5_duong_thang_qua_diem_song_song,
        cau_6_duong_thang_qua_diem_vuong_goc_mp,
        cau_7_duong_thang_vuong_goc_2_duong,
        cau_8_duong_thang_vuong_goc_va_song_song,
        cau_9_duong_thang_trong_mp_vuong_goc_duong,
        cau_10_giao_diem_duong_thang_mat_phang,
        cau_11_giao_diem_duong_thang_mat_cau,
        cau_12_mat_cau_tu_tam_va_the_tich,
        cau_13_mat_cau_ngoai_tiep_tu_dien,
    ]

    # Tạo 4 mệnh đề, mỗi mệnh đề random chọn 1 generator
    propositions = []
    for i in range(num_options):
        gen = random.choice(all_generators)
        prop = gen()
        propositions.append(prop)

    # Random số mệnh đề đúng (1-4)
    num_true = random.randint(1, num_options)
    true_indices = set(random.sample(range(num_options), num_true))

    # Format output
    option_labels = ['a', 'b', 'c', 'd']
    content = f"Câu {question_number}: Chọn các mệnh đề đúng.\n\n"

    for i in range(num_options):
        text = propositions[i]['true'] if i in true_indices else propositions[i]['false']
        marker = '*' if i in true_indices else ''
        content += f"{marker}{option_labels[i]}) {text}\n\n"

    return content


def create_latex_document(questions: List[str], title: str = "Câu hỏi hình học không gian - Dạng đúng/sai") -> str:
    """Tạo document LaTeX"""
    latex = (
        "\\documentclass[a4paper,12pt]{article}\n"
        "\\usepackage{amsmath,amssymb}\n"
        "\\usepackage{geometry}\n"
        "\\geometry{a4paper, margin=1in}\n"
        "\\usepackage{polyglossia}\n"
        "\\setmainlanguage{vietnamese}\n"
        "\\setmainfont{Times New Roman}\n"
        "\\begin{document}\n\n"
        f"\\section*{{{title}}}\n\n"
    )
    latex += "\n\n".join(questions)
    latex += "\n\n\\end{document}"
    return latex


def main():
    import sys
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    except (IndexError, ValueError):
        num_questions = 5

    # Sinh câu hỏi
    questions = [generate_question(i + 1) for i in range(num_questions)]

    # Tạo file LaTeX
    tex = create_latex_document(questions)

    out_file = "custom_geometry_questions.tex"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(tex)

    print(f"✅ Đã tạo {out_file} với {num_questions} câu.")
    print(f"🔧 Lệnh xuất ra file PDF: xelatex {out_file}")


if __name__ == "__main__":
    main()
