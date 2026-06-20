import random
import sys
import logging
from fractions import Fraction
import sympy as sp
#rational_quaratic_min_max_2
# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def gcd(a, b):
    """Compute GCD."""
    while b:
        a, b = b, a % b
    return a

def simplify_fraction(num, denom):
    """Simplify fraction."""
    if denom < 0:
        num, denom = -num, -denom
    if num == 0:
        return 0, 1
    g = gcd(abs(num), abs(denom))
    return num // g, denom // g

def format_latex_number(value):
    """Format number for LaTeX."""
    if isinstance(value, (int, sp.Integer)):
        return f"{value}"
    elif isinstance(value, Fraction):
        num, denom = simplify_fraction(value.numerator, value.denominator)
        if denom == 1:
            return f"{num}"
        return f"\\frac{{{num}}}{{{denom}}}"
    elif isinstance(value, sp.Rational):
        num, denom = value.p, value.q
        if denom == 1:
            return f"{num}"
        return f"\\frac{{{num}}}{{{denom}}}"
    elif isinstance(value, sp.Expr):
        return sp.latex(value)
    return str(value)

def format_rational_for_latex(a, b, c, d, e):
    """Format the function y = (ax^2 + bx + c)/(dx + e) for LaTeX."""
    num_terms = []
    if a != 0:
        if a == 1:
            num_terms.append("x^2")
        elif a == -1:
            num_terms.append("-x^2")
        else:
            num_terms.append(f"{a}x^2")
    if b != 0:
        if b == 1:
            num_terms.append("+x")
        elif b == -1:
            num_terms.append("-x")
        else:
            num_terms.append(f"+{b}x" if b > 0 else f"{b}x")
    if c != 0:
        num_terms.append(f"+{c}" if c > 0 else f"{c}")
    numerator = "".join(num_terms)
    if numerator.startswith("+"):
        numerator = numerator[1:]
    numerator = numerator or "0"
    
    denom_terms = []
    if d != 0:
        if d == 1:
            denom_terms.append("x")
        elif d == -1:
            denom_terms.append("-x")
        else:
            denom_terms.append(f"{d}x")
    if e != 0:
        denom_terms.append(f"+{e}" if e > 0 else f"{e}")
    denominator = "".join(denom_terms)
    if denominator.startswith("+"):
        denominator = denominator[1:]
    
    return f"\\frac{{{numerator}}}{{{denominator}}}"

def format_coefficient(coeff, var='m'):
    """Format coefficient for LaTeX, omitting 1 and handling -1."""
    if coeff == 1:
        return var
    elif coeff == -1:
        return f"-{var}"
    return f"{coeff}{var}"

def format_expression(a_coeff, b_coeff):
    """Format expression a*m + b*M, handling signs and coefficients."""
    m_term = format_coefficient(a_coeff, 'm')
    M_term = format_coefficient(b_coeff, 'M')
    if b_coeff < 0:
        return f"{m_term} {M_term}"
    return f"{m_term}+{M_term}"

def is_perfect_square(n):
    """Check if n is a perfect square."""
    sqrt_n = int(n ** 0.5)
    return sqrt_n * sqrt_n == n

def evaluate_rational(coeffs, x_val):
    """Evaluate f(x) = (ax^2 + bx + c)/(dx + e)."""
    a, b, c, d, e = coeffs
    x = Fraction(x_val) if isinstance(x_val, (int, Fraction)) else x_val
    num = a * x**2 + b * x + c
    denom = d * x + e
    if denom == 0:
        return None
    result = num / denom
    return Fraction(result).limit_denominator(100) if isinstance(result, Fraction) else result

def get_critical_points(a, b, c, d, e):
    """Compute critical points and discontinuity point."""
    x_p = Fraction(-e, d) if d != 0 else None
    
    A_prime = a * d
    B_prime = 2 * a * e
    C_prime = b * e - c * d
    
    discriminant = B_prime * B_prime - 4 * A_prime * C_prime
    if discriminant < 0 or not is_perfect_square(discriminant):
        return [], x_p
    
    sqrt_disc = int(discriminant ** 0.5)
    x1 = Fraction(-B_prime - sqrt_disc, 2 * A_prime) if A_prime != 0 else None
    x2 = Fraction(-B_prime + sqrt_disc, 2 * A_prime) if A_prime != 0 else None
    if x1 == x2 or x1 is None or x2 is None:
        return [], x_p
    critical_points = [x1, x2]
    critical_points.sort(key=lambda x: float(x))
    
    return critical_points, x_p

def get_monotonicity_intervals(a, d, critical_points, x_p):
    """Determine increasing and decreasing intervals."""
    if not critical_points:
        if a * d > 0:
            return [(Fraction(-1000), x_p), (x_p, Fraction(1000))], []
        else:
            return [], [(Fraction(-1000), x_p), (x_p, Fraction(1000))]
    
    x1, x2 = critical_points
    if a * d > 0:
        increasing = [(Fraction(-1000), min(x1, x_p)), (max(x2, x_p), Fraction(1000))]
        decreasing = []
        if x1 < x_p < x2:
            decreasing = [(x1, x_p), (x_p, x2)]
        elif x_p < x1 or x_p > x2:
            decreasing = [(x1, x2)]
    else:
        decreasing = [(Fraction(-1000), min(x1, x_p)), (max(x2, x_p), Fraction(1000))]
        increasing = []
        if x1 < x_p < x2:
            increasing = [(x1, x_p), (x_p, x2)]
        elif x_p < x1 or x_p > x2:
            increasing = [(x1, x2)]
    
    increasing = [i for i in increasing if i[0] < i[1]]
    decreasing = [d for d in decreasing if d[0] < d[1]]
    
    return increasing, decreasing

def get_valid_coefficients(nice_numbers, coeff_range=(-5, 5)):
    """Generate valid coefficients ensuring derivative has two distinct roots."""
    valid_configs = []
    a_choices = [a for a in range(coeff_range[0], coeff_range[1] + 1) if a != 0]
    b_choices = [b for b in range(coeff_range[0], coeff_range[1] + 1) if b != 0]
    c_choices = [c for c in range(coeff_range[0], coeff_range[1] + 1) if c != 0]
    d_choices = [d for d in range(coeff_range[0], coeff_range[1] + 1) if d != 0]
    e_choices = [e for e in range(coeff_range[0], coeff_range[1] + 1) if e != 0]
    
    for a in a_choices:
        for b in b_choices:
            for c in c_choices:
                for d in d_choices:
                    for e in e_choices:
                        critical_points, x_p = get_critical_points(a, b, c, d, e)
                        if not critical_points:
                            continue
                        x1, x2 = critical_points
                        if x1 not in nice_numbers or x2 not in nice_numbers:
                            continue
                        if abs(x2 - x1) < 1:
                            continue
                        valid_configs.append((a, b, c, d, e))
    
    logging.debug(f"Found {len(valid_configs)} valid coefficient sets")
    return valid_configs

def generate_rational_with_nice_roots(coeff_range=(-5, 5)):
    """Generate rational function with nice critical points."""
    nice_numbers = [
        -5, -4, -3, -2, -1, 0,
        Fraction(-3, 4), Fraction(-1, 2), Fraction(-1, 4),
        Fraction(1, 4), Fraction(1, 2), Fraction(3, 4),
        1, 2, 3, 4, 5
    ]
    valid_configs = get_valid_coefficients(nice_numbers, coeff_range)
    
    max_attempts = 200
    for attempt in range(max_attempts):
        logging.info(f"Attempt {attempt + 1}: Generating function")
        if not valid_configs:
            raise RuntimeError("No valid coefficient sets found.")
        
        a, b, c, d, e = random.choice(valid_configs)
        critical_points, x_p = get_critical_points(a, b, c, d, e)
        if not critical_points:
            continue
        critical_points.sort(key=lambda x: float(x))
        
        coeffs = [a, b, c, d, e]
        logging.info(f"Generated function: Coefficients={coeffs}, Critical points={critical_points}, Discontinuity={x_p}")
        return coeffs, critical_points, x_p
    
    raise RuntimeError("Failed to generate valid function")

def format_full_asymptote_equation(A, B, C, D, E):
    """Format the asymptote equation y = mx + b for LaTeX, excluding remainder term."""
    slope = Fraction(A, D)
    BD = B * D
    AE = A * E
    BD_minus_AE = BD - AE
    D_squared = D * D
    intercept = Fraction(BD_minus_AE, D_squared)
    
    slope_display = format_latex_number(slope)
    intercept_display = format_latex_number(intercept)
    
    terms = []
    if slope == 0:
        slope_term = ""
    elif slope == 1:
        slope_term = "x"
    elif slope == -1:
        slope_term = "-x"
    else:
        slope_term = f"{slope_display}x"
    
    if slope != 0:
        terms.append(slope_term)
    
    if intercept != 0:
        if len(terms) > 0 and intercept < 0:
            terms.append(f"-{format_latex_number(abs(intercept))}")
        else:
            terms.append(f"+{intercept_display}" if intercept > 0 else f"{intercept_display}")
    
    if not terms:
        return "0"
    result = "".join(terms)
    if result.startswith("+"):
        result = result[1:]
    return result

def generate_question(question_number, coeff_range=(-5, 5)):
    """Generate true/false question."""
    coeffs, critical_points, x_p = generate_rational_with_nice_roots(coeff_range)
    x1, x2 = critical_points  # x1 < x2
    a, b, c, d, e = coeffs
    logging.info(f"Critical points: x1={x1}, x2={x2}, Discontinuity: x_p={x_p}")

    f_x1 = evaluate_rational(coeffs, x1)
    f_x2 = evaluate_rational(coeffs, x2)
    A = a
    D = d
    A_prime = a * d  # Coefficient of x^2 in numerator of derivative
    function_latex = format_rational_for_latex(a, b, c, d, e)
    question = f"Câu {question_number}: Cho hàm số \\(y = {function_latex}\\). Chọn mệnh đề đúng:"

    increasing_intervals, decreasing_intervals = get_monotonicity_intervals(a, d, critical_points, x_p)
    interval = (x1, x2) if x1 < x_p < x2 else None
    length = x2 - x1 if interval else None

    statements = []
    is_true = [random.choice([True, False]) for _ in range(4)]
    if not any(is_true):
        is_true[random.randint(0, 3)] = True

    # Option a, c, d logic helper
    nice_numbers = [-5, -4, -3, -2, -1, 0, Fraction(-3, 4), Fraction(-1, 2), Fraction(-1, 4),
                    Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), 1, 2, 3, 4, 5]

    def get_min_max_statement(is_true_desired):
        a_coeff = random.choice([i for i in range(-5, 6) if i != 0])
        b_coeff = random.choice([i for i in range(-5, 6) if i != 0])
        expression = format_expression(a_coeff, b_coeff)
        
        if is_true_desired:
            d_type = random.choice(["no_min_max", "min_max_no_discontinuity", "min_or_max"])
        else:
            d_type = random.choice(["min_max_with_discontinuity", "min_max_no_discontinuity", "min_or_max"])
            
        if d_type == "no_min_max":
            x_cands = [n for n in nice_numbers if n < x_p]
            x = random.choice(x_cands) if x_cands else x_p - 1
            y_cands = [n for n in nice_numbers if n > x_p and float(n) - float(x) >= 1]
            y = random.choice(y_cands) if y_cands else x_p + 1
            interval_type = random.choice(["open", "half_open_right", "closed"])
            interval_str = f"({format_latex_number(x)}, {format_latex_number(y)})" if interval_type == "open" else \
                           f"({format_latex_number(x)}, {format_latex_number(y)}]" if interval_type == "half_open_right" else \
                           f"[{format_latex_number(x)}, {format_latex_number(y)}]"
            return f"Hàm số không có giá trị lớn nhất và nhỏ nhất trên đoạn \\( {interval_str} \\)"
            
        elif d_type == "min_max_with_discontinuity":
            x_cands = [n for n in nice_numbers if n < x_p]
            x = random.choice(x_cands) if x_cands else x_p - 1
            y_cands = [n for n in nice_numbers if n > x_p and float(n) - float(x) >= 1]
            y = random.choice(y_cands) if y_cands else x_p + 1
            interval_type = random.choice(["open", "half_open_right", "closed"])
            interval_str = f"({format_latex_number(x)}, {format_latex_number(y)})" if interval_type == "open" else \
                           f"({format_latex_number(x)}, {format_latex_number(y)}]" if interval_type == "half_open_right" else \
                           f"[{format_latex_number(x)}, {format_latex_number(y)}]"
            val_x = evaluate_rational(coeffs, x)
            val_y = evaluate_rational(coeffs, y)
            if val_x is None: val_x = evaluate_rational(coeffs, x + Fraction(1, 4))
            if val_y is None: val_y = evaluate_rational(coeffs, y - Fraction(1, 4))
            incorrect_value = a_coeff * val_x + b_coeff * val_y
            return f"Gọi M là giá trị lớn nhất và m là giá trị nhỏ nhất của hàm số trên đoạn \\( {interval_str} \\). Giá trị của \\( {expression} \\) là \\( {format_latex_number(incorrect_value + random.choice([-2, -1, 1, 2]))} \\)"
            
        elif d_type == "min_max_no_discontinuity":
            x_cands = [n for n in nice_numbers if n < x_p - 1 or n > x_p + 1]
            x = random.choice(x_cands) if x_cands else x_p - 2
            if x < x_p:
                y_cands = [n for n in nice_numbers if x < n < x_p and float(n) - float(x) >= 1]
            else:
                y_cands = [n for n in nice_numbers if n > x and float(n) - float(x) >= 1]
            y = random.choice(y_cands) if y_cands else x + 1
            
            values = [evaluate_rational(coeffs, x), evaluate_rational(coeffs, y)]
            for crit_point in critical_points:
                if x <= crit_point <= y:
                    values.append(evaluate_rational(coeffs, crit_point))
            valid_values = [v for v in values if v is not None]
            max_val = max(valid_values) if valid_values else 0
            min_val = min(valid_values) if valid_values else 0
            correct_value = a_coeff * min_val + b_coeff * max_val
            
            if is_true_desired:
                return f"Gọi M là giá trị lớn nhất và m là giá trị nhỏ nhất của hàm số trên đoạn \\( [{format_latex_number(x)}, {format_latex_number(y)}] \\). Giá trị của \\( {expression} \\) là \\( {format_latex_number(correct_value)} \\)"
            else:
                incorrect_options = [
                    a_coeff * max_val + b_coeff * min_val,
                    -a_coeff * min_val + b_coeff * max_val,
                    a_coeff * min_val - b_coeff * max_val,
                    correct_value + random.choice([-2, -1, 1, 2])
                ]
                incorrect_val = random.choice([opt for opt in incorrect_options if opt != correct_value])
                return f"Gọi M là giá trị lớn nhất và m là giá trị nhỏ nhất của hàm số trên đoạn \\( [{format_latex_number(x)}, {format_latex_number(y)}] \\). Giá trị của \\( {expression} \\) là \\( {format_latex_number(incorrect_val)} \\)"
                
        else:  # min_or_max
            interval_left = random.choice([True, False])
            x_cands = [n for n in nice_numbers if n < x_p]
            y_cands = [n for n in nice_numbers if n > x_p]
            x = random.choice(x_cands) if x_cands else x_p - 2
            y = random.choice(y_cands) if y_cands else x_p + 2
            
            if interval_left:
                interval_str = f"({format_latex_number(x_p)}, {format_latex_number(y)}]"
                extremum = "nhỏ nhất" if A_prime > 0 else "lớn nhất"
                pts = [y]
                for cp in critical_points:
                    if x_p < cp <= y:
                        pts.append(cp)
                vals = [evaluate_rational(coeffs, p) for p in pts]
                vals = [v for v in vals if v is not None]
                correct_value = min(vals) if extremum == "nhỏ nhất" and vals else max(vals) if vals else 0
                incorrect_value = evaluate_rational(coeffs, max(y, x2))
                if incorrect_value is None or incorrect_value == correct_value:
                    incorrect_value = correct_value + random.choice([-2, -1, 1, 2])
            else:
                interval_str = f"[{format_latex_number(x)}, {format_latex_number(x_p)})"
                extremum = "lớn nhất" if A_prime > 0 else "nhỏ nhất"
                pts = [x]
                for cp in critical_points:
                    if x <= cp < x_p:
                        pts.append(cp)
                vals = [evaluate_rational(coeffs, p) for p in pts]
                vals = [v for v in vals if v is not None]
                correct_value = max(vals) if extremum == "lớn nhất" and vals else min(vals) if vals else 0
                incorrect_value = evaluate_rational(coeffs, min(x, x1))
                if incorrect_value is None or incorrect_value == correct_value:
                    incorrect_value = correct_value + random.choice([-2, -1, 1, 2])
                    
            reversed_extremum = "nhỏ nhất" if extremum == 'lớn nhất' else "lớn nhất"
            
            if is_true_desired:
                return f"Giá trị {extremum} của hàm số trên đoạn \\( {interval_str} \\) là \\( {format_latex_number(correct_value)}\\) và hàm số không có giá trị {reversed_extremum}"
            else:
                return f"Giá trị {extremum} của hàm số trên đoạn \\( {interval_str} \\) là \\( {format_latex_number(incorrect_value)}\\) và hàm số không có giá trị {reversed_extremum}"

    # Option a: Combine extrema location, value_max, value_min, point_max, point_min
    option_a_types = ["extremum_loc", "value_max", "value_min", "point_max", "point_min"]
    a_type = random.choice(option_a_types)
    if a_type == "extremum_loc":
        extremum_type = random.choice(["cực đại", "cực tiểu"])
        if extremum_type == "cực đại":
            correct_x = x1 if A * D > 0 else x2
            incorrect_options = [x2 if A * D > 0 else x1, f_x1, f_x2]
        else:  # cực tiểu
            correct_x = x2 if A * D > 0 else x1
            incorrect_options = [x1 if A * D > 0 else x2, f_x1, f_x2]
        statement_a = f"Hàm số đạt {extremum_type} tại \\( x = {format_latex_number(correct_x)} \\)" if is_true[0] else \
                      f"Hàm số đạt {extremum_type} tại \\( x = {format_latex_number(random.choice(incorrect_options))} \\)"
    elif a_type == "value_max":
        correct_y = f_x1 if A * D > 0 else f_x2
        incorrect_options = [x1, x2, f_x2 if A * D > 0 else f_x1]
        statement_a = f"Giá trị cực đại của hàm số là \\( y = {format_latex_number(correct_y)} \\)" if is_true[0] else \
                      f"Giá trị cực đại của hàm số là \\( y = {format_latex_number(random.choice(incorrect_options))} \\)"
    elif a_type == "value_min":
        correct_y = f_x2 if A * D > 0 else f_x1
        incorrect_options = [x1, x2, f_x1 if A * D > 0 else f_x2]
        statement_a = f"Giá trị cực tiểu của hàm số là \\( y = {format_latex_number(correct_y)} \\)" if is_true[0] else \
                      f"Giá trị cực tiểu của hàm số là \\( y = {format_latex_number(random.choice(incorrect_options))} \\)"
    elif a_type == "point_max":
        correct_point = f"({format_latex_number(x1)}, {format_latex_number(f_x1)})" if A * D > 0 else f"({format_latex_number(x2)}, {format_latex_number(f_x2)})"
        incorrect_point = f"({format_latex_number(x2)}, {format_latex_number(f_x2)})" if A * D > 0 else f"({format_latex_number(x1)}, {format_latex_number(f_x1)})"
        statement_a = f"Điểm cực đại của đồ thị hàm số là \\( {correct_point} \\)" if is_true[0] else \
                      f"Điểm cực đại của đồ thị hàm số là \\( {incorrect_point} \\)"
    else:  # point_min
        correct_point = f"({format_latex_number(x2)}, {format_latex_number(f_x2)})" if A * D > 0 else f"({format_latex_number(x1)}, {format_latex_number(f_x1)})"
        incorrect_point = f"({format_latex_number(x1)}, {format_latex_number(f_x1)})" if A * D > 0 else f"({format_latex_number(x2)}, {format_latex_number(f_x2)})"
        statement_a = f"Điểm cực tiểu của đồ thị hàm số là \\( {correct_point} \\)" if is_true[0] else \
                      f"Điểm cực tiểu của đồ thị hàm số là \\( {incorrect_point} \\)"
    statements.append(f"{'*' if is_true[0] else ''}a) {statement_a}")
    logging.debug(f"Option a: {'True' if is_true[0] else 'False'}, {statement_a}")

    # Option b: Combine monotonicity or distance/area
    b_type = random.choice(["monotonicity", "distance", "area"])
    if b_type == "monotonicity":
        correct_mono = "nghịch biến" if A * D > 0 and interval else "đồng biến" if A * D < 0 and interval else None
        incorrect_mono = "đồng biến" if correct_mono == "nghịch biến" else "nghịch biến"
        if interval and correct_mono:
            statement_b = f"Hàm số {correct_mono} trên khoảng có độ dài \\( {format_latex_number(length)} \\)" if is_true[1] else \
                          f"Hàm số {incorrect_mono} trên khoảng có độ dài \\( {format_latex_number(length)} \\)"
        else:
            statement_b = f"Hàm số {'đồng biến' if A * D > 0 else 'nghịch biến'} trên khoảng \\( ({format_latex_number(-1000)}, {format_latex_number(x_p)}) \\)" if is_true[1] else \
                          f"Hàm số {'nghịch biến' if A * D > 0 else 'đồng biến'} trên khoảng \\( ({format_latex_number(-1000)}, {format_latex_number(x_p)}) \\)"
    elif b_type == "distance":
        correct_dist = sp.sqrt((x2 - x1)**2 + (f_x2 - f_x1)**2)
        incorrect_dist = (x2 - x1)**2 + (f_x2 - f_x1)**2
        statement_b = f"Khoảng cách giữa hai điểm cực trị là \\( {format_latex_number(correct_dist)} \\)" if is_true[1] else \
                      f"Khoảng cách giữa hai điểm cực trị là \\( {format_latex_number(incorrect_dist)} \\)"
    else:  # area
        correct_area = Fraction(abs(x1 * f_x2 - x2 * f_x1), 2)
        incorrect_area = abs(x1 * f_x2 - x2 * f_x1)
        if incorrect_area == correct_area:
            incorrect_area += 1
        statement_b = f"Gọi hai điểm cực trị là A và B, khi đó diện tích \\( \\triangle OAB \\) là \\( {format_latex_number(correct_area)} \\)" if is_true[1] else \
                      f"Gọi hai điểm cực trị là A và B, khi đó diện tích \\( \\triangle OAB \\) là \\( {format_latex_number(incorrect_area)} \\)"
    statements.append(f"{'*' if is_true[1] else ''}b) {statement_b}")
    logging.debug(f"Option b: {'True' if is_true[1] else 'False'}, {statement_b}")

    # Option c
    statement_c = get_min_max_statement(is_true[2])
    statements.append(f"{'*' if is_true[2] else ''}c) {statement_c}")
    logging.debug(f"Option c: {'True' if is_true[2] else 'False'}, {statement_c}")

    # Option d
    statement_d = get_min_max_statement(is_true[3])
    statements.append(f"{'*' if is_true[3] else ''}d) {statement_d}")
    logging.debug(f"Option d: {'True' if is_true[3] else 'False'}, {statement_d}")


    content = [question, ""]
    for stmt in statements:
        content.extend([stmt, ""])
    return "\n".join(content)

def generate_latex_file(num_questions, filename="rational_extrema_questions.tex"):
    """Generate LaTeX file."""
    latex_content = [
        "\\documentclass[12pt]{article}",
        "\\usepackage{amsmath, amssymb}",
        "\\usepackage{geometry}",
        "\\geometry{a4paper, margin=1in}",
        "\\usepackage{polyglossia}",
        "\\setmainlanguage{vietnamese}",
        "\\usepackage{fontspec}",
        "\\setmainfont{Times New Roman}",
        "\\usepackage{unicode-math}",
        "\\setmathfont{XITS Math}",
        "\\setmathfont{Times New Roman}[range=up/latin]",
        "\\begin{document}",
        "\\section*{Danh sách câu hỏi}",
        ""
    ]

    for i in range(1, num_questions + 1):
        content = generate_question(i)
        latex_content.append(content)

    latex_content.append("\\end{document}")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content))
    print(f"LaTeX file '{filename}' with {num_questions} true/false questions has been generated. Compile with XeLaTeX.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python rational_quaratic_min_max.py <number-questions>")
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