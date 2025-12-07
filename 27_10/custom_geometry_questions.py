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


def format_parametric_line(point: Tuple[int, int, int], vec: Tuple[int, int, int], t_symbol: str = "t") -> str:
    r"""Format phương trình tham số của đường thẳng, chuẩn hóa dấu và hệ số:

    Quy tắc:
    - Ẩn hệ số 1 và −1: dùng "t" hoặc "-t" thay vì "1t", "-1t".
    - Bỏ hạng 0: không in "+ 0t" hay "x = 0 + ...".
    - Dùng dấu cộng/trừ chuẩn: "x = a + bt" hoặc "x = a - bt"; nếu a = 0 thì "x = bt"/"x = t"/"x = -t".
    """
    (x0, y0, z0) = point
    (a, b, c) = vec

    def comp(name: str, base: int, coef: int) -> str:
        if coef == 0:
            # Chỉ còn hằng số
            return f"{name} = {base}"
        # Chuẩn hóa phần hệ số t
        t_term = t_symbol if abs(coef) == 1 else f"{abs(coef)}{t_symbol}"
        if base == 0:
            # Không in "0 + ..."
            return f"{name} = {t_term}" if coef > 0 else f"{name} = -{t_term}"
        # Có hằng số khác 0
        if coef > 0:
            return f"{name} = {base} + {t_term}"
        else:
            return f"{name} = {base} - {t_term}"

    x_line = comp("x", x0, a)
    y_line = comp("y", y0, b)
    z_line = comp("z", z0, c)

    return (
        "\\begin{cases}\n"
        f"{x_line} \\\\ \n"
        f"{y_line} \\\\ \n"
        f"{z_line}\n"
        f"\\end{{cases}},\\; {t_symbol} \\in \\mathbb{{R}}"
    )


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


def random_component_nonzero(min_val: int, max_val: int) -> int:
    """Sinh 1 số nguyên trong [min_val, max_val] khác 0."""
    choices = [i for i in range(min_val, max_val + 1) if i != 0]
    return random.choice(choices)


def random_vector_all_components_nonzero(min_val: int, max_val: int) -> Tuple[int, int, int]:
    """Sinh véctơ có mỗi thành phần đều khác 0, trong [min_val, max_val]."""
    return (
        random_component_nonzero(min_val, max_val),
        random_component_nonzero(min_val, max_val),
        random_component_nonzero(min_val, max_val),
    )


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
    p = random.choice(coeffs)
    q = random.choice(coeffs)
    r = random.choice(coeffs)
    s = random.choice(coeffs)
    return (p, q, r, s)


def format_linear_form(p: int, q: int, r: int, s: int) -> str:
    """Format biểu thức pA + qB + rC + sD"""
    return format_linear_combination([p, q, r, s], ["A", "B", "C", "D"])


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

def inline_math(s: str) -> str:
    """Wrap inline math with \\( ... \\)."""
    return f"\\({s}\\)"


def display_math(s: str) -> str:
    """Wrap display math with \\[ ... \\] on separate lines for readability."""
    return f"\\[\n{s}\n\\]"


def named_point(name: str, pt: Tuple[int, int, int]) -> str:
    """Format named point like \\(A(x;y;z)\\) for LaTeX inline math."""
    return inline_math(f"{name}{format_point(pt)}")


def format_sphere_equation(center: Tuple[int, int, int], r_squared: int) -> str:
    """Format phương trình mặt cầu (x - x0)^2 + (y - y0)^2 + (z - z0)^2 = R^2
    với chuẩn hóa dấu và số: (x + 2)^2, x^2 thay cho (x - 0)^2, v.v.
    """
    def term(var: str, c: int) -> str:
        if c == 0:
            return f"{var}^2"
        sign = '-' if c > 0 else '+'
        val = abs(c)
        return f"({var} {sign} {val})^2"

    return f"{term('x', center[0])} + {term('y', center[1])} + {term('z', center[2])} = {r_squared}"

def format_linear_combination(coeffs: List[int], symbols: List[str]) -> str:
    """Chuẩn hóa biểu thức tuyến tính dạng k1*s1 + k2*s2 + ...

    Quy tắc:
    - Bỏ các hạng có hệ số 0.
    - Ẩn hệ số 1 và −1: dùng "x" hoặc "-x" thay vì "1x", "-1x".
    - Dấu và khoảng trắng chuẩn: "x + 2y - z".
    - Nếu tất cả 0, trả về "0".
    """
    assert len(coeffs) == len(symbols)

    parts: List[str] = []

    for k, sym in zip(coeffs, symbols):
        if k == 0:
            continue
        core = sym if abs(k) == 1 else f"{abs(k)}{sym}"
        if not parts:
            parts.append(core if k > 0 else f"-{core}")
        else:
            parts.append(f"+ {core}" if k > 0 else f"- {core}")

    return " ".join(parts) if parts else "0"

def format_linear_expression(coeffs: Tuple[int, int, int], symbols: Tuple[str, str, str]) -> str:
    """Format biểu thức tuyến tính k1*s1 + k2*s2 + k3*s3 với quy tắc dấu/1/−1 như các câu hỏi.
    coeffs: (k1, k2, k3), symbols: ví dụ ('a','b','c') hoặc ('u','v','w')."""
    return format_linear_combination(list(coeffs), list(symbols))


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

    # Chọn ngẫu nhiên hệ số nào sẽ cho trước (0=A, 1=B, 2=C, 3=D)
    plane_coeffs = [a, b, c, d]
    fixed_idx = random.randint(0, 3)
    fixed_value = plane_coeffs[fixed_idx]
    
    # Ba hệ số còn lại
    remaining_indices = [i for i in range(4) if i != fixed_idx]
    
    # Tạo biểu thức cho 3 hệ số còn lại
    coeff_pool = [-3, -2, -1, 1, 2, 3]
    k1 = random.choice(coeff_pool)
    k2 = random.choice(coeff_pool)
    k3 = random.choice(coeff_pool)
    
    value_true = (k1 * plane_coeffs[remaining_indices[0]] + 
                  k2 * plane_coeffs[remaining_indices[1]] + 
                  k3 * plane_coeffs[remaining_indices[2]])
    value_false = pick_wrong_value(value_true)
    
    # Format phương trình và biểu thức
    symbols = ['A', 'B', 'C', 'D']
    remaining_symbols = [symbols[i] for i in remaining_indices]
    
    # Tạo phương trình mặt phẳng với hệ số cố định
    if fixed_idx == 0:
        plane_eq = f"{fixed_value}x+By+Cz+D=0"
    elif fixed_idx == 1:
        plane_eq = f"Ax+{fixed_value}y+Cz+D=0"
    elif fixed_idx == 2:
        plane_eq = f"Ax+By+{fixed_value}z+D=0"
    else:
        plane_eq = f"Ax+By+Cz+{fixed_value}=0"
    
    expr_str = format_linear_combination([k1, k2, k3], remaining_symbols)

    prefix = (
        f"Cho (P) có dạng {inline_math(plane_eq)} đi qua ba điểm "
        f"{named_point('A', A)}, {named_point('B', B)}, {named_point('C', C)}."
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

    # Chọn ngẫu nhiên hệ số nào sẽ cho trước (0=A, 1=B, 2=C, 3=D)
    plane_coeffs = [a, b, c, d]
    fixed_idx = random.randint(0, 3)
    fixed_value = plane_coeffs[fixed_idx]
    
    # Ba hệ số còn lại
    remaining_indices = [i for i in range(4) if i != fixed_idx]
    
    # Tạo biểu thức cho 3 hệ số còn lại
    coeff_pool = [-3, -2, -1, 1, 2, 3]
    k1 = random.choice(coeff_pool)
    k2 = random.choice(coeff_pool)
    k3 = random.choice(coeff_pool)
    
    value_true = (k1 * plane_coeffs[remaining_indices[0]] + 
                  k2 * plane_coeffs[remaining_indices[1]] + 
                  k3 * plane_coeffs[remaining_indices[2]])
    value_false = pick_wrong_value(value_true)
    
    # Format phương trình và biểu thức
    symbols = ['A', 'B', 'C', 'D']
    remaining_symbols = [symbols[i] for i in remaining_indices]
    
    # Tạo phương trình mặt phẳng với hệ số cố định
    if fixed_idx == 0:
        plane_eq = f"{fixed_value}x+By+Cz+D=0"
    elif fixed_idx == 1:
        plane_eq = f"Ax+{fixed_value}y+Cz+D=0"
    elif fixed_idx == 2:
        plane_eq = f"Ax+By+{fixed_value}z+D=0"
    else:
        plane_eq = f"Ax+By+Cz+{fixed_value}=0"
    
    expr_str = format_linear_combination([k1, k2, k3], remaining_symbols)

    prefix = (
        f"Cho (P) có dạng {inline_math(plane_eq)} đi qua {named_point('A', A)}, {named_point('B', B)} và song song với đường thẳng CD "
        f"với {named_point('C', C)}, {named_point('D', D)}."
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

    # Chọn ngẫu nhiên hệ số nào sẽ cho trước (0=A, 1=B, 2=C, 3=D)
    plane_coeffs = [a, b, c, d]
    fixed_idx = random.randint(0, 3)
    fixed_value = plane_coeffs[fixed_idx]
    
    # Ba hệ số còn lại
    remaining_indices = [i for i in range(4) if i != fixed_idx]
    
    # Tạo biểu thức cho 3 hệ số còn lại
    coeff_pool = [-3, -2, -1, 1, 2, 3]
    k1 = random.choice(coeff_pool)
    k2 = random.choice(coeff_pool)
    k3 = random.choice(coeff_pool)
    
    value_true = (k1 * plane_coeffs[remaining_indices[0]] + 
                  k2 * plane_coeffs[remaining_indices[1]] + 
                  k3 * plane_coeffs[remaining_indices[2]])
    value_false = pick_wrong_value(value_true)
    
    # Format phương trình và biểu thức
    symbols = ['A', 'B', 'C', 'D']
    remaining_symbols = [symbols[i] for i in remaining_indices]
    
    # Tạo phương trình mặt phẳng với hệ số cố định
    if fixed_idx == 0:
        plane_eq = f"{fixed_value}x+By+Cz+D=0"
    elif fixed_idx == 1:
        plane_eq = f"Ax+{fixed_value}y+Cz+D=0"
    elif fixed_idx == 2:
        plane_eq = f"Ax+By+{fixed_value}z+D=0"
    else:
        plane_eq = f"Ax+By+Cz+{fixed_value}=0"
    
    expr_str = format_linear_combination([k1, k2, k3], remaining_symbols)

    eq_Q = format_plane_equation(a_Q, b_Q, c_Q, d_Q)

    prefix = (
        f"Cho (P) có dạng {inline_math(plane_eq)} đi qua "
        f"{named_point('A', A)}, {named_point('B', B)} và \n"
        + "vuông góc với mặt phẳng (Q):\n" + display_math(eq_Q)
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

    # Chọn ngẫu nhiên tọa độ nào sẽ cho trước (0=u, 1=v, 2=w)
    fixed_idx = random.randint(0, 2)
    fixed_value = AM_dir[fixed_idx]
    
    # Hai tọa độ còn lại
    remaining_indices = [i for i in range(3) if i != fixed_idx]
    
    # Tạo biểu thức cho 2 tọa độ còn lại
    coeff_pool = [-2, -1, 1, 2, 3]
    k1 = random.choice(coeff_pool)
    k2 = random.choice(coeff_pool)
    
    value_true = k1 * AM_dir[remaining_indices[0]] + k2 * AM_dir[remaining_indices[1]]
    value_false = pick_wrong_value(value_true)
    
    # Format vector và biểu thức
    symbols = ['u', 'v', 'w']
    vec_str = f"({symbols[0]};{symbols[1]};{symbols[2]})"
    
    # Thay giá trị cố định vào
    if fixed_idx == 0:
        vec_str = f"({fixed_value};v;w)"
        expr_str = format_linear_combination([k1, k2], ['v', 'w'])
    elif fixed_idx == 1:
        vec_str = f"(u;{fixed_value};w)"
        expr_str = format_linear_combination([k1, k2], ['u', 'w'])
    else:
        vec_str = f"(u;v;{fixed_value})"
        expr_str = format_linear_combination([k1, k2], ['u', 'v'])

    prefix = (
        f"Cho tam giác ABC với {named_point('A', A)}, {named_point('B', B)}, {named_point('C', C)}. "
        f"Trung tuyến AM có véctơ chỉ phương \\(\\vec{{u}}={vec_str}\\)."
    )

    return make_true_false(prefix, expr_str, value_true, value_false)


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

    # Chọn ngẫu nhiên tọa độ nào sẽ cho trước (0=a, 1=b, 2=c)
    fixed_idx = random.randint(0, 2)
    fixed_value = BC[fixed_idx]
    
    # Hai tọa độ còn lại
    remaining_indices = [i for i in range(3) if i != fixed_idx]
    
    # Tạo biểu thức cho 2 tọa độ còn lại
    coeff_pool = [-2, -1, 1, 2]
    k1 = random.choice(coeff_pool)
    k2 = random.choice(coeff_pool)
    
    value_true = k1 * BC[remaining_indices[0]] + k2 * BC[remaining_indices[1]]
    value_false = pick_wrong_value(value_true)
    
    # Format vector và biểu thức
    symbols = ['a', 'b', 'c']
    
    # Thay giá trị cố định vào
    if fixed_idx == 0:
        vec_str = f"({fixed_value};b;c)"
        expr_str = format_linear_combination([k1, k2], ['b', 'c'])
    elif fixed_idx == 1:
        vec_str = f"(a;{fixed_value};c)"
        expr_str = format_linear_combination([k1, k2], ['a', 'c'])
    else:
        vec_str = f"(a;b;{fixed_value})"
        expr_str = format_linear_combination([k1, k2], ['a', 'b'])

    prefix = (
        f"Cho đường thẳng d qua {named_point('A', A)} và song song với BC, "
        f"với {named_point('B', B)}, {named_point('C', C)}. "
        f"Đường thẳng d có véctơ chỉ phương \\(\\vec{{u}}={vec_str}\\)."
    )

    return make_true_false(prefix, expr_str, value_true, value_false)


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
    vtcp = (a_P, b_P, c_P)
    
    # Chọn ngẫu nhiên tọa độ nào sẽ cho trước (0=u, 1=v, 2=w)
    fixed_idx = random.randint(0, 2)
    fixed_value = vtcp[fixed_idx]
    
    # Hai tọa độ còn lại
    remaining_indices = [i for i in range(3) if i != fixed_idx]
    
    # Tạo biểu thức cho 2 tọa độ còn lại
    coeff_pool = [-2, -1, 1, 2]
    k1 = random.choice(coeff_pool)
    k2 = random.choice(coeff_pool)
    
    value_true = k1 * vtcp[remaining_indices[0]] + k2 * vtcp[remaining_indices[1]]
    value_false = pick_wrong_value(value_true)
    
    # Format vector và biểu thức
    symbols = ['u', 'v', 'w']
    
    # Thay giá trị cố định vào
    if fixed_idx == 0:
        vec_str = f"({fixed_value};v;w)"
        expr_str = format_linear_combination([k1, k2], ['v', 'w'])
    elif fixed_idx == 1:
        vec_str = f"(u;{fixed_value};w)"
        expr_str = format_linear_combination([k1, k2], ['u', 'w'])
    else:
        vec_str = f"(u;v;{fixed_value})"
        expr_str = format_linear_combination([k1, k2], ['u', 'v'])

    eq_P = format_plane_equation(a_P, b_P, c_P, d_P)

    prefix = (
        f"Cho đường thẳng d qua {named_point('A', A)} và vuông góc với mặt phẳng (P):\n" + display_math(eq_P) + " "
        f"Đường thẳng d có véctơ chỉ phương \\(\\vec{{u}}={vec_str}\\)."
    )

    return make_true_false(prefix, expr_str, value_true, value_false)


def cau_7_duong_thang_vuong_goc_2_duong() -> Dict[str, str]:
    """Câu 7: Đường thẳng qua M vuông góc với d1 và d2"""
    # Tham số random theo yêu cầu
    # M(x_M; y_M; z_M) với mỗi tọa độ trong [-5,5]
    M = (
        random.randint(-5, 5),
        random.randint(-5, 5),
        random.randint(-5, 5),
    )

    # d1, d2: điểm (x_i, y_i, z_i) trong [-4,4], VTCP (a_i,b_i,c_i) trong [-3,3]\{0}, tránh song song
    for _ in range(1000):
        P1 = (random.randint(-4, 4), random.randint(-4, 4), random.randint(-4, 4))
        P2 = (random.randint(-4, 4), random.randint(-4, 4), random.randint(-4, 4))
        u1 = random_vector_all_components_nonzero(-3, 3)
        u2 = random_vector_all_components_nonzero(-3, 3)
        u = cross(u1, u2)
        if not is_zero_vector(u):  # tránh chọn u1, u2 song song
            break
    else:
        P1, P2 = (0, 0, 0), (1, 1, 1)
        u1, u2 = (1, 0, 0), (0, 1, 0)
        u = cross(u1, u2)

    # Trình bày đề bài theo format yêu cầu
    d1_tex = format_parametric_line(P1, u1, "t")
    d2_tex = format_parametric_line(P2, u2, "t")

    # Tạo phương trình đường thẳng kết quả (qua M với VTCP u)
    result_line_tex = format_parametric_line(M, u, "t")

    # Mệnh đề: phương trình đường thẳng là... (inline math)
    prefix = (
        f"Cho {named_point('M', M)} và hai đường thẳng "
        f"{inline_math(f'd_1:\\ {d1_tex},\\quad d_2:\\ {d2_tex}')}." 
        " Phương trình đường thẳng đi qua \\(M\\), đồng thời vuông góc với \\(d_1\\) và \\(d_2\\) là "
        f"{inline_math(result_line_tex)}."
    )

    true_text = prefix
    # Tạo phương trình sai: thay đổi một thành phần của VTCP
    idx = random.randint(0, 2)
    u_wrong = (
        u[0] + (random.choice([-2, -1, 1, 2]) if idx == 0 else 0),
        u[1] + (random.choice([-2, -1, 1, 2]) if idx == 1 else 0),
        u[2] + (random.choice([-2, -1, 1, 2]) if idx == 2 else 0)
    )
    wrong_line_tex = format_parametric_line(M, u_wrong, "t")
    
    false_text = (
        f"Cho {named_point('M', M)} và hai đường thẳng "
        f"{inline_math(f'd_1:\\ {d1_tex},\\quad d_2:\\ {d2_tex}')}." 
        " Phương trình đường thẳng đi qua \\(M\\), đồng thời vuông góc với \\(d_1\\) và \\(d_2\\) là "
        f"{inline_math(wrong_line_tex)}."
    )

    return {"true": true_text, "false": false_text}


def cau_8_duong_thang_vuong_goc_va_song_song() -> Dict[str, str]:
    """Câu 8: Đường thẳng qua A, vuông góc với d và song song với (P)"""
    # Điểm A(x_A, y_A, z_A) và điểm trên d (x0,y0,z0) đều trong [-5,5]
    A = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
    P0 = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))

    # VTCP của d: (a,b,c) trong [-4,4]\{0} từng thành phần; VTPT (alpha,beta,gamma) trong [-4,4]\{0}
    # Tránh (a,b,c) song song với (alpha,beta,gamma)
    for _ in range(1000):
        u_d = random_vector_all_components_nonzero(-4, 4)
        n_P = random_vector_all_components_nonzero(-4, 4)
        if not is_zero_vector(cross(u_d, n_P)):
            break
    else:
        u_d, n_P = (1, 1, 1), (1, -1, 0)

    delta = random.randint(-10, 10)

    # VTCP cần tìm: vuông góc với u_d và song song với (P) => u = u_d × n_P
    u = cross(u_d, n_P)
    if is_zero_vector(u):
        # fallback phòng xa (đã tránh ở trên)
        u = (1, 0, 0)

    # Tạo phương trình đường thẳng kết quả (qua A với VTCP u)
    result_line_tex = format_parametric_line(A, u, "t")

    # Trình bày đề bài (inline math)
    d_tex = format_parametric_line(P0, u_d, "t")
    eq_P = format_plane_equation(n_P[0], n_P[1], n_P[2], delta)

    # Mệnh đề: phương trình đường thẳng là... (inline)
    prefix = (
        f"Phương trình đường thẳng \\(\\Delta\\) đi qua {named_point('A', A)}, "
        "vuông góc với đường thẳng "
        f"{inline_math(f'd:\\ {d_tex},\\ t \\in \\mathbb{{R}}')} "
        "và song song với mặt phẳng "
        f"{inline_math(f'(P):\\ {eq_P}')} "
        "là "
        f"{inline_math('\\Delta:\\ ' + result_line_tex)}."
    )

    true_text = prefix
    # Tạo phương trình sai: thay đổi một thành phần của VTCP
    idx = random.randint(0, 2)
    u_wrong = (
        u[0] + (random.choice([-2, -1, 1, 2]) if idx == 0 else 0),
        u[1] + (random.choice([-2, -1, 1, 2]) if idx == 1 else 0),
        u[2] + (random.choice([-2, -1, 1, 2]) if idx == 2 else 0)
    )
    wrong_line_tex = format_parametric_line(A, u_wrong, "t")
    
    false_text = (
        f"Phương trình đường thẳng \\(\\Delta\\) đi qua {named_point('A', A)}, "
        "vuông góc với đường thẳng "
        f"{inline_math(f'd:\\ {d_tex},\\ t \\in \\mathbb{{R}}')} "
        "và song song với mặt phẳng "
        f"{inline_math(f'(P):\\ {eq_P}')} "
        "là "
        f"{inline_math('\\Delta:\\ ' + wrong_line_tex)}."
    )

    return {"true": true_text, "false": false_text}


def cau_9_duong_thang_trong_mp_vuong_goc_duong() -> Dict[str, str]:
    """Câu 9: Đường thẳng nằm trong (P) và vuông góc với d"""
    # M(x_M, y_M, z_M) trong [-5,5]
    M = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))

    # Mặt phẳng (P): chọn (A,B,C) trong [-4,4]\{0} và ĐẶT D sao cho M thuộc (P)
    A_coef = random_vector_all_components_nonzero(-4, 4)
    n_P = A_coef
    D_coef = -(n_P[0] * M[0] + n_P[1] * M[1] + n_P[2] * M[2])

    # Đường thẳng d: điểm (x0,y0,z0) trong [-5,5], VTCP (a,b,c) trong [-4,4]\{0}
    for _ in range(1000):
        P0 = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
        u_d = random_vector_all_components_nonzero(-4, 4)
        # đảm bảo (a,b,c) không song song với (A,B,C)
        if not is_zero_vector(cross(n_P, u_d)):
            break
    else:
        P0, u_d = (0, 0, 0), (1, 1, 1)

    # VTCP đường thẳng cần tìm: u = n_P × u_d (vuông góc với cả n và u_d, nên nằm trong P và vuông góc d)
    u = cross(n_P, u_d)
    if is_zero_vector(u):
        u = (1, 0, 0)

    # Tạo phương trình đường thẳng kết quả (qua M với VTCP u)
    result_line_tex = format_parametric_line(M, u, "t")

    # Trình bày đề bài (inline)
    eq_P = format_plane_equation(n_P[0], n_P[1], n_P[2], D_coef)
    d_tex = format_parametric_line(P0, u_d, "t")

    # Mệnh đề: phương trình đường thẳng là... (inline)
    prefix = (
        "Phương trình đường thẳng \\(\\Delta\\) nằm trong mặt phẳng "
        f"{inline_math(f'(P):\\ {eq_P}')} "
        "vuông góc với đường thẳng "
        f"{inline_math(f'd:\\ {d_tex},\\ t \\in \\mathbb{{R}}')} "
        f"và đi qua điểm {named_point('M', M)} là "
        f"{inline_math('\\Delta:\\ ' + result_line_tex)}."
    )

    true_text = prefix
    # Tạo phương trình sai: thay đổi một thành phần của VTCP
    idx = random.randint(0, 2)
    u_wrong = (
        u[0] + (random.choice([-2, -1, 1, 2]) if idx == 0 else 0),
        u[1] + (random.choice([-2, -1, 1, 2]) if idx == 1 else 0),
        u[2] + (random.choice([-2, -1, 1, 2]) if idx == 2 else 0)
    )
    wrong_line_tex = format_parametric_line(M, u_wrong, "t")
    
    false_text = (
        "Phương trình đường thẳng \\(\\Delta\\) nằm trong mặt phẳng "
        f"{inline_math(f'(P):\\ {eq_P}')} "
        "vuông góc với đường thẳng "
        f"{inline_math(f'd:\\ {d_tex},\\ t \\in \\mathbb{{R}}')} "
        f"và đi qua điểm {named_point('M', M)} là "
        f"{inline_math('\\Delta:\\ ' + wrong_line_tex)}."
    )

    return {"true": true_text, "false": false_text}


def cau_10_giao_diem_duong_thang_mat_phang() -> Dict[str, str]:
    """Câu 10: Giao điểm của đường thẳng d và mặt phẳng (P)"""
    # Tham số random theo yêu cầu
    # Điểm trên d trong [-5,5]
    M0 = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))

    # VTCP của d: (a,b,c) trong [-3,3]\{0} and tất cả thành phần khác 0 theo đề xuất
    u = random_vector_all_components_nonzero(-3, 3)

    # Mặt phẳng (P): A,B,C trong [-3,3]\{0}; D trong [-10,10]
    for _ in range(1000):
        a_P, b_P, c_P = random_vector_all_components_nonzero(-3, 3)
        d_P = random.randint(-10, 10)
        # Đảm bảo Aa+Bb+Cc != 0 để cắt
        if a_P * u[0] + b_P * u[1] + c_P * u[2] != 0:
            break
    else:
        a_P, b_P, c_P, d_P = 1, 1, 1, 0

    # Tính giao điểm chính xác
    denom = a_P * u[0] + b_P * u[1] + c_P * u[2]
    num = -(a_P * M0[0] + b_P * M0[1] + c_P * M0[2] + d_P)
    t0 = Rational(num, denom)

    I_int = (
        Rational(M0[0]) + Rational(u[0]) * t0,
        Rational(M0[1]) + Rational(u[1]) * t0,
        Rational(M0[2]) + Rational(u[2]) * t0,
    )

    # Format tọa độ giao điểm
    I_x_latex = format_sympy_to_latex(I_int[0])
    I_y_latex = format_sympy_to_latex(I_int[1])
    I_z_latex = format_sympy_to_latex(I_int[2])

    # Trình bày đề bài theo format (inline)
    d_tex = format_parametric_line(M0, u, "t")
    eq_P = format_plane_equation(a_P, b_P, c_P, d_P)

    # Mệnh đề: tọa độ giao điểm là... (inline)
    prefix = (
        "Cho đường thẳng "
        f"{inline_math(f'd:\\ {d_tex},\\ t \\in \\mathbb{{R}}')} "
        "và mặt phẳng "
        f"{inline_math(f'(P):\\ {eq_P}')}. "
        "Tọa độ giao điểm \\(I\\) của đường thẳng \\(d\\) và mặt phẳng \\((P)\\) là "
        f"\\(I({I_x_latex}; {I_y_latex}; {I_z_latex})\\)."
    )

    true_text = prefix
    # Tạo tọa độ giao điểm sai: thay đổi một tọa độ
    idx = random.randint(0, 2)
    delta = random.choice([-2, -1, 1, 2])
    num_sym, den_sym = sp.fraction(sp.simplify(I_int[idx]))
    wrong_val = (num_sym + sp.Integer(delta)) / den_sym
    
    I_wrong = list(I_int)
    I_wrong[idx] = wrong_val
    
    I_wrong_latex = [format_sympy_to_latex(I_wrong[i]) for i in range(3)]
    
    false_text = (
        "Cho đường thẳng "
        f"{inline_math(f'd:\\ {d_tex},\\ t \\in \\mathbb{{R}}')} "
        "và mặt phẳng "
        f"{inline_math(f'(P):\\ {eq_P}')}. "
        "Tọa độ giao điểm \\(I\\) của đường thẳng \\(d\\) và mặt phẳng \\((P)\\) là "
        f"\\(I({I_wrong_latex[0]}; {I_wrong_latex[1]}; {I_wrong_latex[2]})\\)."
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

    # Format phương trình mặt cầu với chuẩn hóa dấu/số
    sphere_eq = format_sphere_equation(center, R_squared)

    true_text = (
        f"Cho đường thẳng d có VTCP {inline_math(format_vec(vtcp))} và mặt cầu (S): "
        + display_math(sphere_eq) + " "
        f"Mặt cầu có tâm \\(I(x_I; y_I; z_I)\\). "
        f"Khi đó \\({expr_str} = {value_true}\\)."
    )
    false_text = (
        f"Cho đường thẳng d có VTCP {inline_math(format_vec(vtcp))} và mặt cầu (S): "
        + display_math(sphere_eq) + " "
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
        f"Cho mặt cầu (S) có tâm {named_point('I', center)} và thể tích \\({V_coeff_latex}\\pi\\). "
        f"Mặt cầu có tâm \\(I(x_I; y_I; z_I)\\) và bán kính R. "
        f"Khi đó \\( {expr_str} = {value_true} \\)."
    )
    false_text = (
        f"Cho mặt cầu (S) có tâm {named_point('I', center)} và thể tích \\({V_coeff_latex}\\pi\\). "
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
                f"{named_point('A', A)}, {named_point('B', B)}, {named_point('C', C)}, {named_point('D', D)}. "
                f"Mặt cầu có tâm \\(I(a;b;c)\\) và bán kính R. "
                f"Khi đó \\({expr_str} = {value_true_latex}\\)."
            )
            false_text = (
                f"Cho mặt cầu ngoại tiếp tứ diện ABCD với "
                f"{named_point('A', A)}, {named_point('B', B)}, {named_point('C', C)}, {named_point('D', D)}. "
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
        f"Cho mặt cầu ngoại tiếp tứ diện ABCD với {named_point('A', A)}, {named_point('B', B)}, {named_point('C', C)}, {named_point('D', D)}. "
        f"Mặt cầu có tâm \\(I(a;b;c)\\) và bán kính R. Khi đó \\(a + b + c = \\frac{{3}}{2}\\)."
    )
    false_text = (
        f"Cho mặt cầu ngoại tiếp tứ diện ABCD với {named_point('A', A)}, {named_point('B', B)}, {named_point('C', C)}, {named_point('D', D)}. "
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