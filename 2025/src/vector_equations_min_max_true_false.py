import random
from fractions import Fraction
import sys
import logging
#vector_equations_min_max_true_false
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def gcd(a, b):
    """Compute the greatest common divisor of a and b."""
    while b:
        a, b = b, a % b
    return a

def simplify_fraction(num, denom):
    """Simplify a fraction by dividing numerator and denominator by their GCD."""
    if denom < 0:
        num, denom = -num, -denom
    if num == 0:
        return 0, 1
    g = gcd(abs(num), abs(denom))
    return num // g, denom // g

def format_fraction(num, denom):
    """Format a fraction for LaTeX."""
    num, denom = simplify_fraction(num, denom)
    if num == 0:
        return "0"
    if denom == 1:
        return f"{num}"
    if num < 0:
        return f"-\\frac{{{-num}}}{{{denom}}}"
    return f"\\frac{{{num}}}{{{denom}}}"

def format_point_ABC(x, y, z):
    """Format a point (x, y, z) for LaTeX for A, B, C, without outer parentheses."""
    x_str = format_fraction(int(x.numerator), int(x.denominator)) if isinstance(x, Fraction) else str(x)
    y_str = format_fraction(int(y.numerator), int(y.denominator)) if isinstance(y, Fraction) else str(y)
    z_str = format_fraction(int(z.numerator), int(z.denominator)) if isinstance(z, Fraction) else str(z)
    return f"{x_str};{y_str};{z_str}"

def format_point_M(x, y, z):
    """Format a point (x, y, z) for LaTeX for M, with parentheses."""
    x_str = format_fraction(int(x.numerator), int(x.denominator)) if isinstance(x, Fraction) else str(x)
    y_str = format_fraction(int(y.numerator), int(y.denominator)) if isinstance(y, Fraction) else str(y)
    z_str = format_fraction(int(z.numerator), int(z.denominator)) if isinstance(z, Fraction) else str(z)
    return f"({x_str};{y_str};{z_str})"

def format_coefficient(coeff, first_term=False):
    """Format coefficient for LaTeX: omit 1, use - for -1, include + for positive non-1, show coeff."""
    if coeff == 1:
        return "" if first_term else "+"
    if coeff == -1:
        return "-"
    if coeff > 0:
        return f"+{coeff}" if not first_term else f"{coeff}"
    return f"{coeff}"

def generate_random_points():
    """Generate three distinct random points A, B, C."""
    points = []
    while len(points) < 3:
        x = random.randint(-5, 5)
        y = random.randint(-5, 5)
        z = random.randint(-5, 5)
        point = (x, y, z)
        if point not in points:
            points.append(point)
    return points[0], points[1], points[2]

def solve_vector_equation(coeff_MA, coeff_MB, coeff_MC, A, B, C):
    """Solve coeff_MA*MA + coeff_MB*MB + coeff_MC*MC = (0, 0, 0)."""
    sum_coeff = coeff_MA + coeff_MB + coeff_MC
    if sum_coeff == 0:
        return None
    
    x_M = Fraction(coeff_MA * A[0] + coeff_MB * B[0] + coeff_MC * C[0], sum_coeff)
    y_M = Fraction(coeff_MA * A[1] + coeff_MB * B[1] + coeff_MC * C[1], sum_coeff)
    z_M = Fraction(coeff_MA * A[2] + coeff_MB * B[2] + coeff_MC * C[2], sum_coeff)
    
    if abs(x_M.numerator) > 20 or abs(x_M.denominator) > 20 or abs(y_M.numerator) > 20 or abs(y_M.denominator) > 20 or abs(z_M.numerator) > 20 or abs(z_M.denominator) > 20:
        return None
        
    return (x_M, y_M, z_M)

def compute_vector_MA(M, A):
    """Compute vector MA = (x_A - x_M, y_A - y_M, z_A - z_M)."""
    return (Fraction(A[0]) - M[0], Fraction(A[1]) - M[1], Fraction(A[2]) - M[2])

def compute_P_b(M, x, y, z, A, B, C):
    """Compute P = x |MA|^2 + y |MB|^2 + z |MC|^2."""
    MA = compute_vector_MA(M, A)
    MB = compute_vector_MA(M, B)
    MC = compute_vector_MA(M, C)
    MA_sq = MA[0]**2 + MA[1]**2 + MA[2]**2
    MB_sq = MB[0]**2 + MB[1]**2 + MB[2]**2
    MC_sq = MC[0]**2 + MC[1]**2 + MC[2]**2
    result = x * MA_sq + y * MB_sq + z * MC_sq
    return result

def compute_P_c(M, a, b, c, A, B, C):
    """Compute P = a MA·MB + b MB·MC + c MC·MA."""
    MA = compute_vector_MA(M, A)
    MB = compute_vector_MA(M, B)
    MC = compute_vector_MA(M, C)
    dot_MA_MB = MA[0] * MB[0] + MA[1] * MB[1] + MA[2] * MB[2]
    dot_MB_MC = MB[0] * MC[0] + MB[1] * MC[1] + MB[2] * MC[2]
    dot_MC_MA = MC[0] * MA[0] + MC[1] * MA[1] + MC[2] * MA[2]
    result = a * dot_MA_MB + b * dot_MB_MC + c * dot_MC_MA
    return result

def compute_P_d(M, a, b, c, d, e, f, A, B, C):
    """Compute P = a |MA|^2 + b |MB|^2 + c |MC|^2 + d MA·MB + e MB·MC + f MC·MA."""
    MA = compute_vector_MA(M, A)
    MB = compute_vector_MA(M, B)
    MC = compute_vector_MA(M, C)
    MA_sq = MA[0]**2 + MA[1]**2 + MA[2]**2
    MB_sq = MB[0]**2 + MB[1]**2 + MB[2]**2
    MC_sq = MC[0]**2 + MC[1]**2 + MC[2]**2
    dot_MA_MB = MA[0] * MB[0] + MA[1] * MB[1] + MA[2] * MB[2]
    dot_MB_MC = MB[0] * MC[0] + MB[1] * MC[1] + MB[2] * MC[2]
    dot_MC_MA = MC[0] * MA[0] + MC[1] * MA[1] + MC[2] * MA[2]
    result = a * MA_sq + b * MB_sq + c * MC_sq + d * dot_MA_MB + e * dot_MB_MC + f * dot_MC_MA
    return result

def generate_question(question_number):
    logging.info(f"Generating question {question_number}")
    
    def nonzero_int():
        return random.choice([n for n in range(-5, 6) if n != 0])
    
    options = {}
    
    # Decide which options are correct upfront to avoid 'ensure at least one' bug
    correct_flags = [random.choice([True, False]) for _ in range(4)]
    if not any(correct_flags):
        correct_flags[random.randint(0, 3)] = True
    is_correct_a, is_correct_b, is_correct_c, is_correct_d = correct_flags
    
    # Option a: P = |x·MA + y·MB + z·MC| = |sum|·MI khi chèn I → min = 0 tại M=I
    # Điều kiện: sum = x+y+z > 0 đảm bảo P ≥ 0 và min tồn tại
    while True:
        A_a, B_a, C_a = generate_random_points()
        x_a, y_a, z_a = [nonzero_int() for _ in range(3)]
        if x_a + y_a + z_a > 0:
            M_a = solve_vector_equation(x_a, y_a, z_a, A_a, B_a, C_a)
            if M_a is not None:
                break
            
    if is_correct_a:
        options['a'] = (
            f"*a) Với các điểm \\( A({format_point_ABC(*A_a)}), B({format_point_ABC(*B_a)}), C({format_point_ABC(*C_a)}) \\), "
            f"biểu thức \\( P=|{format_coefficient(x_a, True)}\\overrightarrow{{MA}}{format_coefficient(y_a)}\\overrightarrow{{MB}}{format_coefficient(z_a)}\\overrightarrow{{MC}}| \\) "
            f"đạt giá trị nhỏ nhất khi \\( M{format_point_M(*M_a)} \\)."
        )
    else:
        x_false = M_a[0] + random.choice([-1, 1, 2, -2])
        y_false = M_a[1] + random.choice([-1, 1, 2, -2])
        z_false = M_a[2] + random.choice([-1, 1, 2, -2])
        options['a'] = (
            f"a) Với các điểm \\( A({format_point_ABC(*A_a)}), B({format_point_ABC(*B_a)}), C({format_point_ABC(*C_a)}) \\), "
            f"biểu thức \\( P=|{format_coefficient(x_a, True)}\\overrightarrow{{MA}}{format_coefficient(y_a)}\\overrightarrow{{MB}}{format_coefficient(z_a)}\\overrightarrow{{MC}}| \\) "
            f"đạt giá trị nhỏ nhất khi \\( M{format_point_M(x_false, y_false, z_false)} \\)."
        )
    
    # Option b: P = x·MA² + y·MB² + z·MC² = (x+y+z)·MI² + const
    # Điều kiện: x+y+z > 0 đảm bảo paraboloid mở lên → P đạt min tại M=I
    while True:
        A_b, B_b, C_b = generate_random_points()
        x_b, y_b, z_b = [nonzero_int() for _ in range(3)]
        if x_b + y_b + z_b > 0:
            M_b = solve_vector_equation(x_b, y_b, z_b, A_b, B_b, C_b)
            if M_b is not None:
                break
    P_b = compute_P_b(M_b, x_b, y_b, z_b, A_b, B_b, C_b)
    
    form_b = random.choice([1, 2])
    if is_correct_b:
        if form_b == 1:
            options['b'] = (
                f"*b) Với \\( A({format_point_ABC(*A_b)}), B({format_point_ABC(*B_b)}), C({format_point_ABC(*C_b)}) \\), "
                f"biểu thức \\( P={format_coefficient(x_b, True)}MA^2{format_coefficient(y_b)}MB^2{format_coefficient(z_b)}MC^2 \\) "
                f"đạt giá trị nhỏ nhất khi \\( M{format_point_M(*M_b)} \\)."
            )
        else:
            P_b_str = format_fraction(P_b.numerator, P_b.denominator)
            options['b'] = (
                f"*b) Với \\( A({format_point_ABC(*A_b)}), B({format_point_ABC(*B_b)}), C({format_point_ABC(*C_b)}) \\), "
                f"biểu thức \\( P={format_coefficient(x_b, True)}MA^2{format_coefficient(y_b)}MB^2{format_coefficient(z_b)}MC^2 \\) "
                f"đạt giá trị nhỏ nhất bằng \\( {P_b_str} \\)."
            )
    else:
        if form_b == 1:
            x_false = M_b[0] + random.choice([-1, 1, 2, -2])
            y_false = M_b[1] + random.choice([-1, 1, 2, -2])
            z_false = M_b[2] + random.choice([-1, 1, 2, -2])
            options['b'] = (
                f"b) Với \\( A({format_point_ABC(*A_b)}), B({format_point_ABC(*B_b)}), C({format_point_ABC(*C_b)}) \\), "
                f"biểu thức \\( P={format_coefficient(x_b, True)}MA^2{format_coefficient(y_b)}MB^2{format_coefficient(z_b)}MC^2 \\) "
                f"đạt giá trị nhỏ nhất khi \\( M{format_point_M(x_false, y_false, z_false)} \\)."
            )
        else:
            P_false = P_b + Fraction(random.choice([-10, -5, 5, 10]))
            P_false_str = format_fraction(P_false.numerator, P_false.denominator)
            options['b'] = (
                f"b) Với \\( A({format_point_ABC(*A_b)}), B({format_point_ABC(*B_b)}), C({format_point_ABC(*C_b)}) \\), "
                f"biểu thức \\( P={format_coefficient(x_b, True)}MA^2{format_coefficient(y_b)}MB^2{format_coefficient(z_b)}MC^2 \\) "
                f"đạt giá trị nhỏ nhất bằng \\( {P_false_str} \\)."
            )
    
    # Option c: P = a·MA·MB + b·MB·MC + c·MC·MA = (a+b+c)·MI² + const
    # Trọng số tỉ cự: w_A=a+c, w_B=a+b, w_C=b+c; tổng = 2(a+b+c)
    # Điều kiện: a+b+c > 0 đảm bảo cả hệ số MI² > 0 lẫn tổng trọng số > 0
    while True:
        A_c, B_c, C_c = generate_random_points()
        a_c, b_c, c_c = [nonzero_int() for _ in range(3)]
        sum_abc = a_c + b_c + c_c
        if sum_abc > 0:
            wa = a_c + c_c
            wb = a_c + b_c
            wc = b_c + c_c
            # Tổng trọng số = 2*sum_abc > 0, luôn thỏa
            M_c = solve_vector_equation(wa, wb, wc, A_c, B_c, C_c)
            if M_c is not None:
                break
    P_c = compute_P_c(M_c, a_c, b_c, c_c, A_c, B_c, C_c)
    
    form_c = random.choice([1, 2])
    if is_correct_c:
        if form_c == 1:
            options['c'] = (
                f"*c) Với \\( A({format_point_ABC(*A_c)}), B({format_point_ABC(*B_c)}), C({format_point_ABC(*C_c)}) \\), "
                f"biểu thức \\( P={format_coefficient(a_c, True)}\\overrightarrow{{MA}}\\cdot\\overrightarrow{{MB}}{format_coefficient(b_c)}\\overrightarrow{{MB}}\\cdot\\overrightarrow{{MC}}{format_coefficient(c_c)}\\overrightarrow{{MC}}\\cdot\\overrightarrow{{MA}} \\) "
                f"đạt giá trị nhỏ nhất khi \\( M{format_point_M(*M_c)} \\)."
            )
        else:
            P_c_str = format_fraction(P_c.numerator, P_c.denominator)
            options['c'] = (
                f"*c) Với \\( A({format_point_ABC(*A_c)}), B({format_point_ABC(*B_c)}), C({format_point_ABC(*C_c)}) \\), "
                f"biểu thức \\( P={format_coefficient(a_c, True)}\\overrightarrow{{MA}}\\cdot\\overrightarrow{{MB}}{format_coefficient(b_c)}\\overrightarrow{{MB}}\\cdot\\overrightarrow{{MC}}{format_coefficient(c_c)}\\overrightarrow{{MC}}\\cdot\\overrightarrow{{MA}} \\) "
                f"đạt giá trị nhỏ nhất bằng \\( {P_c_str} \\)."
            )
    else:
        if form_c == 1:
            x_false = M_c[0] + random.choice([-1, 1, 2, -2])
            y_false = M_c[1] + random.choice([-1, 1, 2, -2])
            z_false = M_c[2] + random.choice([-1, 1, 2, -2])
            options['c'] = (
                f"c) Với \\( A({format_point_ABC(*A_c)}), B({format_point_ABC(*B_c)}), C({format_point_ABC(*C_c)}) \\), "
                f"biểu thức \\( P={format_coefficient(a_c, True)}\\overrightarrow{{MA}}\\cdot\\overrightarrow{{MB}}{format_coefficient(b_c)}\\overrightarrow{{MB}}\\cdot\\overrightarrow{{MC}}{format_coefficient(c_c)}\\overrightarrow{{MC}}\\cdot\\overrightarrow{{MA}} \\) "
                f"đạt giá trị nhỏ nhất khi \\( M{format_point_M(x_false, y_false, z_false)} \\)."
            )
        else:
            P_false = P_c + Fraction(random.choice([-10, -5, 5, 10]))
            P_false_str = format_fraction(P_false.numerator, P_false.denominator)
            options['c'] = (
                f"c) Với \\( A({format_point_ABC(*A_c)}), B({format_point_ABC(*B_c)}), C({format_point_ABC(*C_c)}) \\), "
                f"biểu thức \\( P={format_coefficient(a_c, True)}\\overrightarrow{{MA}}\\cdot\\overrightarrow{{MB}}{format_coefficient(b_c)}\\overrightarrow{{MB}}\\cdot\\overrightarrow{{MC}}{format_coefficient(c_c)}\\overrightarrow{{MC}}\\cdot\\overrightarrow{{MA}} \\) "
                f"đạt giá trị nhỏ nhất bằng \\( {P_false_str} \\)."
            )
    
    # Option d: P = a·MA² + b·MB² + c·MC² + d·MA·MB + e·MB·MC + f·MC·MA
    #         = (a+b+c+d+e+f)·MI² + const
    # Trọng số tỉ cự: w_A=2a+d+f, w_B=2b+d+e, w_C=2c+e+f; tổng = 2(a+b+c+d+e+f)
    # Điều kiện: a+b+c+d+e+f > 0 đảm bảo hệ số MI² > 0 và tổng trọng số > 0
    while True:
        A_d, B_d, C_d = generate_random_points()
        a_d, b_d, c_d, d_d, e_d, f_d = [nonzero_int() for _ in range(6)]
        sum_abcdef = a_d + b_d + c_d + d_d + e_d + f_d
        if sum_abcdef > 0:
            wa = d_d + f_d + 2*a_d
            wb = d_d + e_d + 2*b_d
            wc = e_d + f_d + 2*c_d
            # Tổng trọng số = 2*sum_abcdef > 0, luôn thỏa
            M_d = solve_vector_equation(wa, wb, wc, A_d, B_d, C_d)
            if M_d is not None:
                break
    P_d = compute_P_d(M_d, a_d, b_d, c_d, d_d, e_d, f_d, A_d, B_d, C_d)
    
    form_d = random.choice([1, 2])
    if is_correct_d:
        if form_d == 1:
            options['d'] = (
                f"*d) Với \\( A({format_point_ABC(*A_d)}), B({format_point_ABC(*B_d)}), C({format_point_ABC(*C_d)}) \\), "
                f"biểu thức \\( P={format_coefficient(a_d, True)}MA^2{format_coefficient(b_d)}MB^2{format_coefficient(c_d)}MC^2"
                f"{format_coefficient(d_d)}\\overrightarrow{{MA}}\\cdot\\overrightarrow{{MB}}{format_coefficient(e_d)}\\overrightarrow{{MB}}\\cdot\\overrightarrow{{MC}}{format_coefficient(f_d)}\\overrightarrow{{MC}}\\cdot\\overrightarrow{{MA}} \\) "
                f"đạt giá trị nhỏ nhất khi \\( M{format_point_M(*M_d)} \\)."
            )
        else:
            P_d_str = format_fraction(P_d.numerator, P_d.denominator)
            options['d'] = (
                f"*d) Với \\( A({format_point_ABC(*A_d)}), B({format_point_ABC(*B_d)}), C({format_point_ABC(*C_d)}) \\), "
                f"biểu thức \\( P={format_coefficient(a_d, True)}MA^2{format_coefficient(b_d)}MB^2{format_coefficient(c_d)}MC^2"
                f"{format_coefficient(d_d)}\\overrightarrow{{MA}}\\cdot\\overrightarrow{{MB}}{format_coefficient(e_d)}\\overrightarrow{{MB}}\\cdot\\overrightarrow{{MC}}{format_coefficient(f_d)}\\overrightarrow{{MC}}\\cdot\\overrightarrow{{MA}} \\) "
                f"đạt giá trị nhỏ nhất bằng \\( {P_d_str} \\)."
            )
    else:
        if form_d == 1:
            x_false = M_d[0] + random.choice([-1, 1, 2, -2])
            y_false = M_d[1] + random.choice([-1, 1, 2, -2])
            z_false = M_d[2] + random.choice([-1, 1, 2, -2])
            options['d'] = (
                f"d) Với \\( A({format_point_ABC(*A_d)}), B({format_point_ABC(*B_d)}), C({format_point_ABC(*C_d)}) \\), "
                f"biểu thức \\( P={format_coefficient(a_d, True)}MA^2{format_coefficient(b_d)}MB^2{format_coefficient(c_d)}MC^2"
                f"{format_coefficient(d_d)}\\overrightarrow{{MA}}\\cdot\\overrightarrow{{MB}}{format_coefficient(e_d)}\\overrightarrow{{MB}}\\cdot\\overrightarrow{{MC}}{format_coefficient(f_d)}\\overrightarrow{{MC}}\\cdot\\overrightarrow{{MA}} \\) "
                f"đạt giá trị nhỏ nhất khi \\( M{format_point_M(x_false, y_false, z_false)} \\)."
            )
        else:
            P_false = P_d + Fraction(random.choice([-10, -5, 5, 10]))
            P_false_str = format_fraction(P_false.numerator, P_false.denominator)
            options['d'] = (
                f"d) Với \\( A({format_point_ABC(*A_d)}), B({format_point_ABC(*B_d)}), C({format_point_ABC(*C_d)}) \\), "
                f"biểu thức \\( P={format_coefficient(a_d, True)}MA^2{format_coefficient(b_d)}MB^2{format_coefficient(c_d)}MC^2"
                f"{format_coefficient(d_d)}\\overrightarrow{{MA}}\\cdot\\overrightarrow{{MB}}{format_coefficient(e_d)}\\overrightarrow{{MB}}\\cdot\\overrightarrow{{MC}}{format_coefficient(f_d)}\\overrightarrow{{MC}}\\cdot\\overrightarrow{{MA}} \\) "
                f"đạt giá trị nhỏ nhất bằng \\( {P_false_str} \\)."
            )
    
    # Format question with blank lines
    stem = f"Trong không gian $Oxyz$, xét bài toán tìm tọa độ điểm $M$ để biểu thức đạt giá trị nhỏ nhất sau:"
    question = f"{stem}\n\n{options['a']}\n\n{options['b']}\n\n{options['c']}\n\n{options['d']}"

    def truth_str(t): return "Đúng" if t else "Sai"

    sum_w_a = x_a + y_a + z_a
    I_a = format_point_M(*M_a)
    loigiai_a = (
        f"a) Chèn điểm $I$ bất kì vào biểu thức: $\\overrightarrow{{MA}} = \\overrightarrow{{MI}} + \\overrightarrow{{IA}}$... Tương tự cho $B, C$.\\\\\n"
        f"Thu được: $P = |({sum_w_a})\\overrightarrow{{MI}} {format_coefficient(x_a)}\\overrightarrow{{IA}} {format_coefficient(y_a)}\\overrightarrow{{IB}} {format_coefficient(z_a)}\\overrightarrow{{IC}}|$.\\\\\n"
        f"Chọn điểm $I$ thỏa mãn ${format_coefficient(x_a, True)}\\overrightarrow{{IA}} {format_coefficient(y_a)}\\overrightarrow{{IB}} {format_coefficient(z_a)}\\overrightarrow{{IC}} = \\vec{{0}}$.\\\\\n"
        f"Suy ra toạ độ $I$ thỏa mãn $x_I = \\frac{{{x_a} x_A {format_coefficient(y_a)} x_B {format_coefficient(z_a)} x_C}}{{{sum_w_a}}}$. Tương tự cho $y_I, z_I$.\\\\\n"
        f"Ta tìm được $I{I_a}$. "
        f"Lúc này $P = |{sum_w_a}| \\cdot MI$. Vì $|{sum_w_a}| > 0$ nên $P$ nhỏ nhất khi $M \\equiv I{I_a}$.\\\\\n"
        f"So sánh với đề bài, mệnh đề này là {truth_str(is_correct_a)}."
    )

    sum_w_b = x_b + y_b + z_b
    I_b = format_point_M(*M_b)
    P_b_str = format_fraction(P_b.numerator, P_b.denominator)
    loigiai_b = (
        f"b) Chèn điểm $I$ bất kì: $MA^2 = (\\overrightarrow{{MI}} + \\overrightarrow{{IA}})^2 = MI^2 + IA^2 + 2\\overrightarrow{{MI}}\\cdot\\overrightarrow{{IA}}$.\\\\\n"
        f"Khai triển tương tự, ta có $P = ({sum_w_b})MI^2 + {x_b}IA^2 {format_coefficient(y_b)}IB^2 {format_coefficient(z_b)}IC^2 + 2\\overrightarrow{{MI}}\\cdot( {format_coefficient(x_b, True)}\\overrightarrow{{IA}} {format_coefficient(y_b)}\\overrightarrow{{IB}} {format_coefficient(z_b)}\\overrightarrow{{IC}})$.\\\\\n"
        f"Chọn $I$ sao cho ${format_coefficient(x_b, True)}\\overrightarrow{{IA}} {format_coefficient(y_b)}\\overrightarrow{{IB}} {format_coefficient(z_b)}\\overrightarrow{{IC}} = \\vec{{0}}$. Bằng công thức tâm tỉ cự, ta tính được tọa độ $I{I_b}$.\\\\\n"
        f"Vì ${sum_w_b} > 0$ nên $P$ đạt cực tiểu bằng ${P_b_str}$ khi $M \\equiv I{I_b}$.\\\\\n"
        f"Do đó, mệnh đề là {truth_str(is_correct_b)}."
    )

    wa_c, wb_c, wc_c = a_c + c_c, a_c + b_c, b_c + c_c
    I_c = format_point_M(*M_c)
    P_c_str = format_fraction(P_c.numerator, P_c.denominator)
    loigiai_c = (
        f"c) Xét tích vô hướng: $\\overrightarrow{{MA}}\\cdot\\overrightarrow{{MB}} = (\\overrightarrow{{MI}} + \\overrightarrow{{IA}})\\cdot(\\overrightarrow{{MI}} + \\overrightarrow{{IB}}) = MI^2 + \\overrightarrow{{MI}}\\cdot(\\overrightarrow{{IA}} + \\overrightarrow{{IB}}) + \\overrightarrow{{IA}}\\cdot\\overrightarrow{{IB}}$.\\\\\n"
        f"Thay vào $P$, ta thu gọn được hệ số của $MI^2$ là ${a_c} + {b_c} + {c_c} = {a_c+b_c+c_c}$.\\\\\n"
        f"Phần chứa $\\overrightarrow{{MI}}$ là $\\overrightarrow{{MI}}\\cdot\\left( {format_coefficient(wa_c, True)}\\overrightarrow{{IA}} {format_coefficient(wb_c)}\\overrightarrow{{IB}} {format_coefficient(wc_c)}\\overrightarrow{{IC}} \\right) = \\vec{{0}}$.\\\\\n"
        f"Chọn tâm tỉ cự $I$ thỏa mãn ${format_coefficient(wa_c, True)}\\overrightarrow{{IA}} {format_coefficient(wb_c)}\\overrightarrow{{IB}} {format_coefficient(wc_c)}\\overrightarrow{{IC}} = \\vec{{0}}$.\\\\\n"
        f"Sử dụng công thức tọa độ tương ứng với trọng số ${wa_c}, {wb_c}, {wc_c}$, ta có $I{I_c}$. "
        f"Với ${a_c+b_c+c_c} > 0$, paraboloid quay lên, $P$ đạt nhỏ nhất bằng ${P_c_str}$ khi $M \\equiv I{I_c}$.\\\\\n"
        f"Mệnh đề này là {truth_str(is_correct_c)}."
    )

    wa_d, wb_d, wc_d = d_d+f_d+2*a_d, d_d+e_d+2*b_d, e_d+f_d+2*c_d
    I_d = format_point_M(*M_d)
    P_d_str = format_fraction(P_d.numerator, P_d.denominator)
    loigiai_d = (
        f"d) Tương tự các phương pháp trên, chèn điểm $I$ cho tất cả các bình phương và tích vô hướng.\\\\\n"
        f"Hệ số của $MI^2$ sau khai triển là $({a_d} + {b_d} + {c_d} + {d_d} + {e_d} + {f_d}) = {a_d+b_d+c_d+d_d+e_d+f_d}$.\\\\\n"
        f"Tổng phần dư chứa $\\overrightarrow{{MI}}$ có dạng rút gọn $\\overrightarrow{{MI}}\\cdot\\left( {format_coefficient(wa_d, True)}\\overrightarrow{{IA}} {format_coefficient(wb_d)}\\overrightarrow{{IB}} {format_coefficient(wc_d)}\\overrightarrow{{IC}} \\right)$.\\\\\n"
        f"Xác định tâm tỉ cự $I$ thỏa mãn phương trình: ${format_coefficient(wa_d, True)}\\overrightarrow{{IA}} {format_coefficient(wb_d)}\\overrightarrow{{IB}} {format_coefficient(wc_d)}\\overrightarrow{{IC}} = \\vec{{0}}$.\\\\\n"
        f"Tính toán qua tọa độ theo trọng số tỉ cự tâm, ta xác nhận được tọa độ điểm $I{I_d}$.\\\\\n"
        f"Vì tổng hệ số $MI^2$ là ${a_d+b_d+c_d+d_d+e_d+f_d} > 0$, $P$ đạt giá trị nhỏ nhất ${P_d_str}$ khi và chỉ khi $M \\equiv I{I_d}$.\\\\\n"
        f"Kết luận mệnh đề {truth_str(is_correct_d)}."
    )

    conclusion = f"Vậy a) {truth_str(is_correct_a)}; b) {truth_str(is_correct_b)}; c) {truth_str(is_correct_c)} và d) {truth_str(is_correct_d)}."
    
    solution = f"{loigiai_a}\n\n{loigiai_b}\n\n{loigiai_c}\n\n{loigiai_d}\n\n{conclusion}"
    
    content_tex = f"\\begin{{ex}}%Câu {question_number}\n{question}\n\n\\loigiai{{\n{solution}\n}}\n\\end{{ex}}\n"
    
    return content_tex

def generate_latex_file(num_questions, filename="true_false_questions.tex"):
    content = ""
    for i in range(1, num_questions + 1):
        content += generate_question(i) + "\n"
    
    tex_content = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage{{amsmath,amssymb,fancyhdr}}
\\usepackage{{polyglossia}}
\\setdefaultlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{{geometry}}
\\usepackage[solcolor]{{ex_test}}
\\begin{{document}}
{content}\\end{{document}}
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(tex_content)
    print(f"LaTeX file '{filename}' with {num_questions} true/false questions has been generated. Compile with XeLaTeX.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python true_false_questions.py <number-questions>")
        sys.exit(1)
    
    try:
        num_questions = int(sys.argv[1])
        if num_questions <= 0:
            print("Number of questions must be positive.")
            sys.exit(1)
    except ValueError:
        print("Number of questions must be an integer.")
        sys.exit(1)
    
    generate_latex_file(num_questions)

if __name__ == "__main__":
    main()