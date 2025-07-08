import random
import sys
import logging
from fractions import Fraction
import re
import math

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_fraction_latex(num, denom):
    """Format a fraction for LaTeX display."""
    if denom == 0:
        return "undefined"
    
    frac = Fraction(num, denom)
    if frac.denominator == 1:
        return str(frac.numerator)
    elif frac.numerator == 0:
        return "0"
    else:
        return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"

def format_coefficient(coeff, is_first=False, var='x', power=1):
    """Format coefficient with proper signs and variable."""
    if coeff == 0:
        return ""
    
    # Handle Fraction coefficients
    if isinstance(coeff, Fraction):
        num, denom = coeff.numerator, coeff.denominator
    else:
        num, denom = int(coeff), 1
    
    # Format the coefficient part
    if denom == 1:
        coeff_str = str(abs(num)) if abs(num) != 1 or power == 0 else ""
    else:
        coeff_str = f"\\frac{{{abs(num)}}}{{{denom}}}"
    
    # Handle variable and power
    if power == 0:
        var_str = coeff_str if coeff_str else "1"
    elif power == 1:
        var_str = f"{coeff_str}x" if coeff_str else "x"
    else:
        var_str = f"{coeff_str}x^{{{power}}}" if coeff_str else f"x^{{{power}}}"
    
    # Sửa logic dấu đầu tiên
    if is_first:
        if num < 0:
            return f"-{var_str}"
        else:
            return var_str
    else:
        if num < 0:
            return f" - {var_str}"
        else:
            return f" + {var_str}"

def format_polynomial(coeffs, var='x'):
    """Format polynomial coefficients as LaTeX string."""
    if not coeffs or all(c == 0 for c in coeffs):
        return "0"
    
    terms = []
    degree = len(coeffs) - 1
    
    for i, coeff in enumerate(coeffs):
        if coeff == 0:
            continue
        
        power = degree - i
        term = format_coefficient(coeff, len(terms) == 0, var, power)
        if term:
            terms.append(term)
    
    if not terms:
        return "0"
    
    result = "".join(terms)
    # Chuẩn hóa để sửa các lỗi format như x{2} → x^{2}
    return standardize_math_expression(result)

def format_coefficient_clean(coeff, is_first=False, var='x', power=1, var_name=''):
    """Format coefficient with proper signs and variable, clean display (no +0)."""
    if coeff == 0:
        return ""
    
    # Handle Fraction coefficients
    if isinstance(coeff, Fraction):
        num, denom = coeff.numerator, coeff.denominator
    else:
        num, denom = int(coeff), 1
    
    # Format the coefficient part
    if power == 0:  # Constant term
        if denom == 1:
            coeff_str = str(abs(num))
        else:
            coeff_str = f"\\frac{{{abs(num)}}}{{{denom}}}"
        var_str = coeff_str
    else:  # Variable term
        if denom == 1:
            if abs(num) == 1:
                coeff_str = "" if power != 0 else "1"
            else:
                coeff_str = str(abs(num))
        else:
            coeff_str = f"\\frac{{{abs(num)}}}{{{denom}}}"
        
        # Add variable name if provided (like 'm' or 'n')
        if var_name:
            if power == 1:
                var_str = f"{coeff_str}{var_name}" if coeff_str else var_name
            else:
                var_str = f"{coeff_str}{var_name}^{{{power}}}" if coeff_str else f"{var_name}^{{{power}}}"
        else:
            if power == 1:
                var_str = f"{coeff_str}{var}" if coeff_str else var
            else:
                var_str = f"{coeff_str}{var}^{{{power}}}" if coeff_str else f"{var}^{{{power}}}"
    
    # Handle signs - cleaned up
    if is_first:
        if num < 0:
            return f"-{var_str}"
        else:
            return var_str
    else:
        if num < 0:
            return f" - {var_str}"
        else:
            return f" + {var_str}"

def format_polynomial_clean(d, a, b, var='x', var_name='m'):
    """Format polynomial cleanly without + - issues."""
    result_parts = []
    
    # (dm + a)x part
    inner_parts = []
    
    # dm part
    if d != 0:
        if d == 1:
            inner_parts.append(var_name)
        elif d == -1:
            inner_parts.append(f"-{var_name}")
        else:
            inner_parts.append(f"{d}{var_name}")
    
    # a part
    if a != 0:
        if len(inner_parts) == 0:
            inner_parts.append(str(a))
        else:
            if a > 0:
                inner_parts.append(f" + {a}")
            else:
                inner_parts.append(f" - {abs(a)}")
    
    # Build (dm + a)x
    if inner_parts:
        if len(inner_parts) > 1:
            result_parts.append(f"({''.join(inner_parts)}){var}")
        else:
            result_parts.append(f"{''.join(inner_parts)}{var}")
    
    # b part
    if b != 0:
        if len(result_parts) == 0:
            result_parts.append(str(b))
        else:
            if b > 0:
                result_parts.append(f" + {b}")
            else:
                result_parts.append(f" - {abs(b)}")
    
    return "".join(result_parts) if result_parts else "0"

def format_simple_polynomial(coeff, constant, var='x'):
    """Format simple polynomial like ax + b."""
    parts = []
    
    # ax part
    if coeff != 0:
        if coeff == 1:
            parts.append(var)
        elif coeff == -1:
            parts.append(f"-{var}")
        else:
            parts.append(f"{coeff}{var}")
    
    # constant part
    if constant != 0:
        if len(parts) == 0:
            parts.append(str(constant))
        else:
            if constant > 0:
                parts.append(f" + {constant}")
            else:
                parts.append(f" - {abs(constant)}")
    
    return "".join(parts) if parts else "0"

def format_polynomial_expression(d, a, b, var='x', var_name=''):
    """Format polynomial expression like (dm+a)x+b, excluding zero terms."""
    
    # Build the inner expression (dm + a)
    inner_terms = []
    
    # First term: dm (with variable name like 'm')
    if d != 0:
        if d == 1:
            inner_terms.append(var_name)
        elif d == -1:
            inner_terms.append(f"-{var_name}")
        else:
            inner_terms.append(f"{d}{var_name}")
    
    # Second term: a (constant)
    if a != 0:
        if len(inner_terms) == 0:
            inner_terms.append(str(a))
        else:
            if a > 0:
                inner_terms.append(f" + {a}")
            else:
                inner_terms.append(f" - {abs(a)}")
    
    # Build the complete expression
    if len(inner_terms) == 0:
        # If both d and a are 0, the numerator is just b
        if b != 0:
            return str(b)
        else:
            return "0"
    
    # Format the (dm + a)x part
    inner = "".join(inner_terms)
    if len(inner_terms) > 1:
        x_part = f"({inner}){var}"
    else:
        x_part = f"{inner}{var}"
    
    # Add constant term b if non-zero
    if b != 0:
        if b > 0:
            return f"{x_part} + {b}"
        else:
            return f"{x_part} - {abs(b)}"
    else:
        return x_part

def format_coefficient_for_display(coeff, var_name):
    """Format coefficient for display với chuẩn hóa: 1m → m, -1m → -m."""
    if coeff == 0:
        return "0"
    elif coeff == 1:
        return var_name
    elif coeff == -1:
        return f"-{var_name}"
    else:
        result = f"{coeff}{var_name}"
        # Áp dụng chuẩn hóa cho kết quả
        return standardize_math_expression(result)

def standardize_math_expression(expr):
    """Chuẩn hóa biểu thức toán học theo các quy tắc chuyên nghiệp."""
    
    # 0. Sửa lỗi format LaTeX cơ bản trước tiên
    # 2x{2} → 2x^{2}, 3x{3} → 3x^{3}  
    expr = re.sub(r'(\d+[a-z])\{(\d+)\}', r'\1^{\2}', expr)
    # x{2} → x^{2} (but not \frac{} or \sqrt{})
    expr = re.sub(r'(?<!\\fra)(?<!\\sqr)([a-z])\{(\d+)\}', r'\1^{\2}', expr)
    
    # 0.1. Sửa lỗi +x → x ở đầu biểu thức
    expr = re.sub(r'^\+([a-z])', r'\1', expr)      # +x → x ở đầu
    expr = re.sub(r'(\(\+)([a-z])', r'(\2', expr)  # (+x → (x
    expr = re.sub(r'(\{)\+([a-z])', r'\1\2', expr) # {+x → {x
    
    # 1. Chuẩn hóa hệ số 1 và -1 với biến - cải thiện
    # 1m → m, -1m → -m, 1n → n, -1n → -n
    expr = re.sub(r'(?<!\d)1([a-z])', r'\1', expr)  # 1m → m (không có số trước 1)
    expr = re.sub(r'(?<!\d)-1([a-z])', r'-\1', expr)  # -1m → -m
    
    # 1.1. Xử lý hệ số 1 ở đầu biểu thức sau dấu =, (
    expr = re.sub(r'(=\s*)1([a-z])', r'\1\2', expr)      # = 1m → = m
    expr = re.sub(r'(\(\s*)1([a-z])', r'\1\2', expr)     # ( 1m → ( m
    expr = re.sub(r'(^|\s)1([a-z])', r'\1\2', expr)      # ^1m → m hoặc space1m → m
    
    # 2. Chuẩn hóa dấu hiệu trước khi xử lý số 0
    expr = expr.replace("--", "+")      # -- → +
    expr = expr.replace("+ -", " - ")   # + - → -  (với space)
    expr = expr.replace("- -", " + ")   # - - → +  (với space)
    expr = expr.replace("+-", "-")      # +- → -
    
    # 2.1. Xử lý + -number thành - number đặc biệt
    expr = re.sub(r'\+\s*-(\d+)', r' - \1', expr)  # + -5 → - 5
    
    # 3. Loại bỏ phép cộng/trừ với 0
    # 1m + 0 → m, -1m + 0 → -m, expr + 0 → expr, expr - 0 → expr
    expr = re.sub(r'\s*\+\s*0(?![.\d])', '', expr)  # + 0 → ''
    expr = re.sub(r'\s*-\s*0(?![.\d])', '', expr)   # - 0 → ''
    expr = re.sub(r'0\s*\+\s*', '', expr)           # 0 + → ''
    
    # 4. Chuẩn hóa dấu ngoặc cho số âm trong phép nhân
    # -2 * 3 → (-2) * 3, x * -5 → x * (-5)
    expr = re.sub(r'(\s|^|=)(-\d+)(\s*\\cdot|\s*\*)', r'\1(\2)\3', expr)
    expr = re.sub(r'(\\cdot|\*)\s*(-\d+)', r'\1 (\2)', expr)
    
    # 5. Loại bỏ dấu + ở đầu số dương
    expr = re.sub(r'(=\s*)\+(\d+)', r'\1\2', expr)       # = +4 → = 4
    expr = re.sub(r'(\(\s*)\+(\d+)', r'\1\2', expr)      # ( +4 → ( 4
    expr = re.sub(r'(^|\s)\+(\d+)', r'\1\2', expr)       # +4 → 4
    
    # 6. Chuẩn hóa biểu thức trong LaTeX
    expr = re.sub(r'\\frac{\+(\d+)', r'\\frac{\1', expr)  # \frac{+4 → \frac{4
    expr = re.sub(r'\\\(\+', r'\\(', expr)               # \(+ → \(
    
    # 7. Chuẩn hóa hệ số 1 trong phân số
    expr = re.sub(r'\\frac{1([a-z])}{', r'\\frac{\1}{', expr)      # \frac{1m}{ → \frac{m}{
    expr = re.sub(r'\\frac{-1([a-z])}{', r'\\frac{-\1}{', expr)    # \frac{-1m}{ → \frac{-m}{
    
    # 8. Chuẩn hóa biểu thức x^{1} → x (FIXED: added closing })
    expr = re.sub(r'([a-z])\^\{1\}(?![0-9])', r'\1', expr)
    
    # 9. Loại bỏ phép nhân thừa với 1
    expr = re.sub(r'1\s*\\cdot\s*', '', expr)      # 1⋅ → ''
    expr = re.sub(r'\s*\\cdot\s*1(?![0-9])', '', expr)  # ⋅1 → ''
    
    # 10. Chuyển số thập phân thành phân số (NEW)
    # 2.5 → \frac{5}{2}, -1.25 → -\frac{5}{4}
    expr = convert_decimals_to_fractions(expr)
    
    # 11. Loại bỏ dấu chấm cuối dòng (NEW)
    expr = re.sub(r'\.(\s*$)', r'\1', expr)  # Remove trailing dots
    expr = re.sub(r'\.(\s*\\\\)', r'\1', expr)  # Remove dots before line breaks
    expr = re.sub(r'SAI\.', r'SAI', expr)  # Remove dots after SAI
    expr = re.sub(r'ĐÚNG\.', r'ĐÚNG', expr)  # Remove dots after ĐÚNG
    
    # 12. Chuẩn hóa space thừa
    expr = re.sub(r'\s+', ' ', expr)               # Multiple spaces → single space
    expr = expr.strip()                            # Remove leading/trailing spaces
    
    return expr

def convert_decimals_to_fractions(expr):
    """Chuyển đổi số thập phân thành phân số trong biểu thức LaTeX."""
    import re
    from fractions import Fraction
    
    def decimal_to_fraction(match):
        decimal_str = match.group(0)
        try:
            # First try to convert to radical form
            decimal_value = float(decimal_str)
            radical_form = format_radical_latex(decimal_value)
            if radical_form:
                return radical_form
            
            # If not a recognizable radical, convert to fraction
            frac = Fraction(decimal_str).limit_denominator()
            if frac.denominator == 1:
                return str(frac.numerator)
            else:
                if frac.numerator < 0:
                    return f"-\\frac{{{abs(frac.numerator)}}}{{{frac.denominator}}}"
                else:
                    return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
        except:
            return decimal_str
    
    # Match decimal numbers (including negative)
    expr = re.sub(r'-?\d+\.\d+', decimal_to_fraction, expr)
    
    return expr

def format_number_as_fraction(number):
    """Chuyển đổi số thành phân số LaTeX. (Legacy function - use format_number_enhanced instead)"""
    return format_number_enhanced(number)

def clean_negative_signs(expr):
    """Clean up double negative signs in expressions and remove + from standalone positive numbers."""
    # Kiểm tra nếu là multi-line text (có \n) thì chỉ làm sạch từng dòng riêng biệt
    if '\n' in expr:
        lines = expr.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip():  # Chỉ xử lý dòng không rỗng
                cleaned_lines.append(standardize_math_expression(line))
            else:
                cleaned_lines.append(line)  # Giữ nguyên dòng trống
        
        # Áp dụng các quy tắc bổ sung cho toàn bộ text
        result = '\n'.join(cleaned_lines)
        # Remove duplicate fractions like \frac{-1}{2} = \frac{-1}{2}
        result = re.sub(r'(\\frac{[^}]*}{[^}]*}) = \\frac{([^}]*)}{([^}]*)}', r'\1', result)
        # Simplify nested fractions like \frac{\frac{a}{b}}{c} to \frac{a}{b*c}
        result = re.sub(r'\\frac{\\frac{([^}]*)}{([^}]*)}}{([^}]*)}', r'\\frac{\1}{\2 \\cdot \3}', result)
        return result
    else:
        # Sử dụng hàm chuẩn hóa cho single line
        expr = standardize_math_expression(expr)
        
        # Các quy tắc bổ sung từ hàm cũ
        # Remove duplicate fractions like \frac{-1}{2} = \frac{-1}{2}
        expr = re.sub(r'(\\frac{[^}]*}{[^}]*}) = \\frac{([^}]*)}{([^}]*)}', r'\1', expr)
        
        # Simplify nested fractions like \frac{\frac{a}{b}}{c} to \frac{a}{b*c}
        expr = re.sub(r'\\frac{\\frac{([^}]*)}{([^}]*)}}{([^}]*)}', r'\\frac{\1}{\2 \\cdot \3}', expr)
        
        # Áp dụng chuẩn hóa thêm một lần nữa sau khi xử lý
        return standardize_math_expression(expr)

def generate_asymptote_question_1():
    """Generate question 1: về tiệm cận đứng và ngang với tham số m và n"""
    
    # Generate random parameters
    d = random.choice([-3, -2, -1, 1, 2, 3])
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    n = random.choice([-3, -2, -1, 1, 2, 3])
    c = random.randint(-5, 5)
    A = random.randint(-3, 3)
    B = random.randint(-3, 3)
    
    # Ensure valid conditions
    while A == 0 or B == 0 or c == 0 or n == 0:
        A = random.randint(-3, 3)
        B = random.randint(-3, 3)
        c = random.randint(-5, 5)
        n = random.choice([-3, -2, -1, 1, 2, 3])
    
    # Calculate m and n from conditions  
    # For denominator nx + c: vertical asymptote x = -c/n = A => n = -c/A
    n_value = Fraction(-c, A)
    # For numerator (dm+a)x + b: horizontal asymptote y = (dm+a)/n = B => dm + a = Bn => m = (Bn - a)/d
    m_value = Fraction(B * n_value - a, d)
    
    # Generate random coefficients alpha, beta for alpha*m + beta*n
    coeff_a = random.randint(-5, 5)
    coeff_b = random.randint(-5, 5)
    while coeff_a == 0 or coeff_b == 0:
        coeff_a = random.randint(-5, 5)
        coeff_b = random.randint(-5, 5)
    
    # Calculate correct result: alpha*m + beta*n
    correct_result = coeff_a * m_value + coeff_b * n_value
    
    # Generate wrong result
    wrong_result = correct_result + random.choice([-3, -2, -1, 1, 2, 3])
    
    # Random choice between correct and wrong
    is_correct = random.choice([True, False])
    displayed_result = correct_result if is_correct else wrong_result
    
    # Format the function using new clean format
    numerator = format_polynomial_clean(d, a, b, 'x', 'm')
    
    # Format denominator: nx + c (no coefficient before n)
    denom_terms = []
    
    # nx term (n is parameter, not coefficient)
    denom_terms.append("nx")
    
    # Constant term c
    if c != 0:
        if c > 0:
            denom_terms.append(f" + {c}")
        else:
            denom_terms.append(f" - {abs(c)}")
    
    denominator = "".join(denom_terms)
    
    # Clean up negative signs in the formatted strings
    numerator = clean_negative_signs(numerator)
    denominator = clean_negative_signs(denominator)
    
    # Random choice of one statement from 3 options
    statements = [
        f"Tiệm cận đứng: \\(x = {A}\\); tiệm cận ngang: \\(y = {B}\\)",
        f"Tiệm cận đứng đi qua điểm \\(({A}; 0)\\) và tiệm cận ngang đi qua điểm \\((0; {B})\\)",
        f"Tiệm cận đứng và ngang giao nhau tại điểm \\(({A}; {B})\\)"
    ]
    chosen_statement = random.choice(statements)
    
    return {
        'proposition': f"Hàm số \\(y = \\frac{{{numerator}}}{{{denominator}}}\\) có {chosen_statement} thì \\({coeff_a}m {'+' if coeff_b >= 0 else '-'} {abs(coeff_b)}n = {format_fraction_latex(displayed_result.numerator, displayed_result.denominator)}\\).",
        'is_correct': is_correct,
        'solution_data': {
            'numerator': numerator,
            'denominator': denominator,
            'chosen_statement': chosen_statement,
            'A': A, 'B': B, 'c': c, 'd': d, 'a': a,
            'n_value': n_value,
            'm_value': m_value,
            'coeff_a': coeff_a,
            'coeff_b': coeff_b,
            'correct_result': correct_result,
            'displayed_result': displayed_result
        }
    }

def generate_asymptote_question_2():
    """Generate question 2: về diện tích hình chữ nhật tạo bởi tiệm cận"""
    
    # Generate random parameters
    d = random.choice([-2, -1, 1, 2])
    a = random.randint(-4, 4)
    b = random.randint(-4, 4)
    e = random.choice([-2, -1, 1, 2])
    c = random.randint(-4, 4)
    S0 = random.randint(2, 8)
    
    # Ensure valid conditions
    while c == 0 or e == 0 or d == 0:
        e = random.choice([-2, -1, 1, 2])
        c = random.randint(-4, 4)
        d = random.choice([-2, -1, 1, 2])
    
    # Calculate asymptotes
    vertical_asymptote = Fraction(-c, e)
    # For area calculation: |horizontal_asymptote * vertical_asymptote| = S0
    # horizontal_asymptote = (dm + a)/e
    # So |(dm + a)/e * (-c/e)| = S0
    # |-(dm + a)*c/e²| = S0
    # |(dm + a)*c|/e² = S0
    # |dm + a| = S0*e²/|c|
    
    target_numerator = safe_divide(S0 * e * e, abs(c))
    m_positive = safe_divide(target_numerator - a, d)
    m_negative = safe_divide(-target_numerator - a, d)
    
    # Calculate sum of squares of both solutions
    sum_of_squares_correct = m_positive**2 + m_negative**2
    
    # Generate wrong answer (reasonable deviation from correct sum of squares)
    adjustment = random.choice([-10, -5, -2, -1, 1, 2, 5, 10])
    sum_of_squares_wrong = sum_of_squares_correct + adjustment
    
    # Random choice between correct and wrong
    is_correct = random.choice([True, False])
    sum_of_squares_displayed = sum_of_squares_correct if is_correct else sum_of_squares_wrong
    
    # Format the function
    numerator = format_polynomial_clean(d, a, b, 'x', 'm')
    denominator = format_simple_polynomial(e, c, 'x')
    
    # Clean up negative signs
    numerator = clean_negative_signs(numerator)
    denominator = clean_negative_signs(denominator)
    
    return {
        'proposition': f"Hàm số \\(y = \\frac{{{numerator}}}{{{denominator}}}\\) có đường tiệm cận đứng và ngang tạo với hai trục tọa độ một hình chữ nhật có diện tích bằng \\({S0}\\) thì tổng bình phương các giá trị của \\(m\\) là \\({format_number_enhanced(sum_of_squares_displayed)}\\).",
        'is_correct': is_correct,
        'solution_data': {
            'numerator': numerator,
            'denominator': denominator,
            'S0': S0,
            'd': d, 'a': a, 'e': e, 'c': c,
            'vertical_asymptote': vertical_asymptote,
            'target_numerator': target_numerator,
            'm_positive': m_positive,
            'm_negative': m_negative,
            'sum_of_squares_correct': sum_of_squares_correct,
            'sum_of_squares_displayed': sum_of_squares_displayed
        }
    }

def generate_asymptote_question_3():
    """Generate question 3: về số lượng tiệm cận với mệnh đề đúng/sai"""
    
    # Generate random parameters
    a = random.randint(1, 3)
    b = random.choice([-2, -1, 1, 2])
    c = random.randint(-3, 3)
    d = random.choice([-2, -1, 1, 2])
    
    # Ensure valid conditions
    while c == 0 or d == 0 or b == 0:  # Prevent division by zero in m != calculation
        c = random.randint(-3, 3)
        d = random.choice([-2, -1, 1, 2])
        b = random.choice([-2, -1, 1, 2])
    
    # Generate random interval with integer endpoints
    interval_start = random.randint(-20, -5)
    interval_length = random.randint(15, 25)
    interval_end = interval_start + interval_length
    
    # Random choice between two options
    options = [
        "2 tiệm cận đứng",
        "3 tiệm cận"
    ]
    chosen_option = random.choice(options)
    
    # Calculate d * b * a as concrete number
    constant_term = d * b * a
    
    # Clean up formula - calculate constant term directly
    formula = clean_negative_signs(f"\\frac{{x - {a}}}{{x^2 + ({b}m + {c})x + {constant_term}}}")
    
    # Calculate the CORRECT number of integer values in [interval_start, interval_end]
    # For function y = (x-a)/(x² + (bm+c)x + constant_term)
    # Conditions: f(a) ≠ 0 AND Δ > 0
    
    # Condition 1: f(a) ≠ 0 means denominator at x=a is not zero
    # f(a) = a² + (bm+c)a + constant_term ≠ 0
    # = a² + ba*m + ca + constant_term
    # = a² + a(c + db) + a*b*m ≠ 0
    # Since a ≠ 0, we need: c + db + b*m ≠ 0
    # => b*m ≠ -(c + db)
    # => m ≠ -(c + db)/b
    
    condition1_value = -(c + d*b) // b if (c + d*b) % b == 0 else None
    
    # Condition 2: Δ > 0 for quadratic x² + (bm+c)x + constant_term
    # Δ = (bm+c)² - 4*1*constant_term = (bm+c)² - 4*constant_term
    # Since this involves m², we need to solve: (bm+c)² > 4*constant_term
    # Let's analyze this case by case based on the sign of 4*constant_term
    
    discriminant_const = 4 * constant_term
    
    # Count valid integer values of m in [interval_start, interval_end]
    valid_m_values = []
    for m in range(interval_start, interval_end + 1):
        # Check condition 1: f(a) ≠ 0
        f_a = a*a + (b*m + c)*a + constant_term
        condition1_ok = (f_a != 0)
        
        # Check condition 2: Δ > 0
        delta = (b*m + c)**2 - discriminant_const
        condition2_ok = (delta > 0)
        
        if condition1_ok and condition2_ok:
            valid_m_values.append(m)
    
    correct_count = len(valid_m_values)
    
    # Generate wrong count (reasonable deviation)
    if correct_count <= 5:
        adjustment = random.choice([-2, -1, 1, 2, 3])
    else:
        adjustment = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    
    wrong_count = max(0, min(21, correct_count + adjustment))  # Ensure 0 <= wrong_count <= 21
    
    # Random choice between correct and wrong
    is_correct = random.choice([True, False])
    displayed_count = correct_count if is_correct else wrong_count
    
    # Debug: Print the logic to verify correctness
    # print(f"DEBUG: correct_count={correct_count}, displayed_count={displayed_count}, is_correct={is_correct}")
    
    return {
        'proposition': f"Có \\({displayed_count}\\) giá trị nguyên của \\(m\\) trong khoảng \\([{interval_start}; {interval_end}]\\) để hàm số \\(y = {formula}\\) có {chosen_option}.",
        'is_correct': is_correct,
        'solution_data': {
            'formula': formula,
            'chosen_option': chosen_option,
            'a': a, 'b': b, 'c': c, 'd': d,
            'constant_term': constant_term,
            'correct_count': correct_count,
            'displayed_count': displayed_count,
            'valid_m_values': valid_m_values,
            'condition1_value': condition1_value,
            'interval_start': interval_start,
            'interval_end': interval_end
        }
    }

def generate_detailed_solution_oblique(A, B, C, D, E, slope, intercept):
    """Generate detailed solution following the LaTeX base file format exactly."""
    
    # Format the original function
    num_str = format_polynomial([A, B, C])
    denom_str = format_polynomial([D, E])
    
    # Calculate R using the formula from LaTeX base
    BD = B * D
    AE = A * E
    BD_minus_AE = BD - AE
    D_squared = D * D
    R_numerator = BD_minus_AE * E
    R = C - Fraction(R_numerator, D_squared)
    
    # Format values for display
    R_display = format_fraction_latex(R.numerator, R.denominator)
    slope_display = format_fraction_latex(slope.numerator, slope.denominator)
    intercept_display = format_fraction_latex(intercept.numerator, intercept.denominator)
    
    # Format slope coefficient for "Ta có:" line - avoid "1 · x" 
    if slope.numerator == 1 and slope.denominator == 1:
        slope_ta_co = "x"
    elif slope.numerator == -1 and slope.denominator == 1:
        slope_ta_co = "-x"
    else:
        slope_ta_co = f"{slope_display}x"
    
    # Build "Ta có:" equation dynamically - skip intercept if it's 0
    ta_co_parts = [slope_ta_co]
    
    # Add intercept term only if not zero
    if intercept != 0:
        if intercept > 0:
            ta_co_parts.append(f" + {intercept_display}")
        else:
            ta_co_parts.append(f" - {format_fraction_latex(abs(intercept.numerator), abs(intercept.denominator))}")
    
    # Add R term
    if R != 0:
        if R > 0:
            ta_co_parts.append(f" + \\frac{{{R_display}}}{{{denom_str}}}")
        else:
            ta_co_parts.append(f" - \\frac{{{format_fraction_latex(abs(R.numerator), abs(R.denominator))}}}{{{denom_str}}}")
    
    ta_co_equation = "".join(ta_co_parts)
    
    # Build the final equation for tiệm cận xiên (chỉ có 2 hệ số)
    final_parts = []
    
    # Add slope term
    if slope.numerator == 1 and slope.denominator == 1:
        final_parts.append("x")
    elif slope.numerator == -1 and slope.denominator == 1:
        final_parts.append("-x")
    elif slope != 0:
        final_parts.append(f"{slope_display}x")
    
    # Add intercept term (handle sign properly)
    if intercept != 0:
        if len(final_parts) > 0:
            if intercept > 0:
                final_parts.append(f" + {intercept_display}")
            else:
                final_parts.append(f" - {format_fraction_latex(abs(intercept.numerator), abs(intercept.denominator))}")
        else:
            final_parts.append(intercept_display)
    
    final_equation = "".join(final_parts) if final_parts else "0"
    
    solution = f"""Giải:

Ta có: \\(y = \\frac{{{num_str}}}{{{denom_str}}} = {ta_co_equation}\\)

\\(\\Rightarrow \\displaystyle\\lim_{{x \\to +\\infty}} \\left(\\left(\\frac{{{num_str}}}{{{denom_str}}}\\right) - \\left({ta_co_equation}\\right)\\right) = \\displaystyle\\lim_{{x \\to +\\infty}} \\frac{{{R_display}}}{{{denom_str}}} = \\displaystyle\\lim_{{x \\to +\\infty}} \\frac{{\\frac{{{R_display}}}{{x}}}}{{{D} + \\frac{{{E}}}{{x}}}} = 0\\)

\\(\\Rightarrow\\) Tiệm cận xiên: \\(y = {final_equation}\\)"""
    
    return solution

def generate_oblique_asymptote_question():
    """Generate oblique asymptote question using asymptote_mc.py format."""
    
    # Generate coefficients for oblique asymptote
    A = random.choice([-2, -1, 1, 2])
    B = random.randint(-4, 4)
    C = random.randint(-4, 4)
    D = random.choice([-2, -1, 1, 2])
    E = random.randint(-4, 4)
    
    # Ensure valid conditions: D ≠ 0, E ≠ 0, and A ≠ 0 (for oblique asymptote)
    while D == 0 or E == 0 or A == 0:
        A = random.choice([-2, -1, 1, 2])
        D = random.choice([-2, -1, 1, 2])
        E = random.randint(-4, 4)
    
    # Thêm log để kiểm tra hệ số
    logging.info(f"[OBLIQUE] Sinh hệ số: A={A}, B={B}, C={C}, D={D}, E={E}")
    print(f"[OBLIQUE] Sinh hệ số: A={A}, B={B}, C={C}, D={D}, E={E}")
    
    # Calculate oblique asymptote using exact formula from asymptote_mc.py
    slope = Fraction(A, D)
    BD = B * D
    AE = A * E
    BD_minus_AE = BD - AE
    D_squared = D * D
    intercept = Fraction(BD_minus_AE, D_squared)
    
    # Calculate remainder R
    R_numerator = BD_minus_AE * E
    R = C - Fraction(R_numerator, D_squared)
    
    # Format polynomial strings with proper exponents
    num_str = format_polynomial([A, B, C])
    denom_str = format_polynomial([D, E])

    print(f"[DEBUG] format_polynomial input: {[A, B, C]}, output: {num_str}")
    print(f"[DEBUG] format_polynomial input: {[D, E]}, output: {denom_str}")
    
    # Fix x{2} → x^{2} formatting  
    num_str = num_str.replace("x{2}", "x^{2}")
    denom_str = denom_str.replace("x{2}", "x^{2}")
    
    # Format slope coefficient for "Ta có:" line - avoid "1 · x" 
    if slope.numerator == 1 and slope.denominator == 1:
        slope_ta_co = "x"
    elif slope.numerator == -1 and slope.denominator == 1:
        slope_ta_co = "-x"
    else:
        slope_display = format_fraction_latex(slope.numerator, slope.denominator)
        slope_ta_co = f"{slope_display}x"
    
    # Build "Ta có:" equation dynamically - skip intercept if it's 0
    ta_co_parts = [slope_ta_co]
    
    # Add intercept term only if not zero
    if intercept != 0:
        intercept_display = format_fraction_latex(intercept.numerator, intercept.denominator)
        if intercept > 0:
            ta_co_parts.append(f" + {intercept_display}")
        else:
            ta_co_parts.append(f" - {format_fraction_latex(abs(intercept.numerator), abs(intercept.denominator))}")
    
    ta_co_equation = "".join(ta_co_parts)
    
    # Generate wrong answer using standard format
    A_wrong = A + random.choice([-1, 1])
    slope_wrong = Fraction(A_wrong, D)
    BD_wrong = B * D
    AE_wrong = A_wrong * E
    BD_minus_AE_wrong = BD_wrong - AE_wrong
    D_squared = D * D
    intercept_wrong = Fraction(BD_minus_AE_wrong, D_squared)
    
    # Format wrong equation using standard format
    wrong_parts = []
    
    if slope_wrong.numerator == 1 and slope_wrong.denominator == 1:
        wrong_parts.append("x")
    elif slope_wrong.numerator == -1 and slope_wrong.denominator == 1:
        wrong_parts.append("-x")
    elif slope_wrong != 0:
        slope_wrong_display = format_fraction_latex(slope_wrong.numerator, slope_wrong.denominator)
        wrong_parts.append(f"{slope_wrong_display}x")
    
    if intercept_wrong != 0:
        intercept_wrong_display = format_fraction_latex(intercept_wrong.numerator, intercept_wrong.denominator)
        if len(wrong_parts) > 0:
            if intercept_wrong > 0:
                wrong_parts.append(f" + {intercept_wrong_display}")
            else:
                wrong_parts.append(f" - {format_fraction_latex(abs(intercept_wrong.numerator), abs(intercept_wrong.denominator))}")
        else:
            wrong_parts.append(intercept_wrong_display)
    
    wrong_equation = "".join(wrong_parts) if wrong_parts else "0"
    
    # Randomly choose if this is correct or wrong answer
    is_correct = random.choice([True, False])
    displayed_answer = ta_co_equation if is_correct else wrong_equation
    
    # Clean up expressions
    ta_co_equation = clean_negative_signs(ta_co_equation)
    num_str = clean_negative_signs(num_str)
    denom_str = clean_negative_signs(denom_str)
    displayed_answer = clean_negative_signs(displayed_answer)
    
    return {
        'proposition': f"Hàm số \\(y = \\frac{{{num_str}}}{{{denom_str}}}\\) có phương trình đường tiệm cận xiên là: \\(y = {displayed_answer}\\).",
        'is_correct': is_correct,
        'solution_data': {
            'num_str': num_str,
            'denom_str': denom_str,
            'ta_co_equation': ta_co_equation,
            'R': R,
            'A': A, 'B': B, 'C': C, 'D': D, 'E': E,
            'displayed_answer': displayed_answer,
            'slope': slope,
            'intercept': intercept
        }
    }

def generate_single_question(question_number):
    """Generate a single question with a), b), c), d) format following true_false style."""
    
    # Generate each type of question data
    question_a_data = generate_asymptote_question_1()
    question_b_data = generate_asymptote_question_2()
    question_c_data = generate_asymptote_question_3()
    question_d_data = generate_oblique_asymptote_question()
    
    # Collect all data
    all_data = [question_a_data, question_b_data, question_c_data, question_d_data]
    option_labels = ['a', 'b', 'c', 'd']
    
    # Build question content
    question_content = f"Câu {question_number}: Chọn các mệnh đề đúng:\n\n"
    
    # Add propositions with correct marking style (like true_false format)
    for i, (label, data) in enumerate(zip(option_labels, all_data)):
        marker = '*' if data['is_correct'] else ''
        proposition_text = data['proposition']
        
        # Ensure consistent single-line format without line breaks or tabs
        proposition_text = proposition_text.replace('\\\\\\quad', ' ')
        proposition_text = proposition_text.replace('\\\\', ' ')
        
        question_content += f"{marker}{label}) {proposition_text}\n\n"
    
    # Add solutions section
    question_content += "Lời giải:\n\n"
    
    # Solution for proposition a)
    sol_a = question_a_data['solution_data']
    question_content += "Lời giải cho mệnh đề a):\n\n"
    
    # Add equivalence explanation at the beginning if statement 2 or 3 was chosen
    if "đi qua điểm" in sol_a['chosen_statement'] or "giao nhau tại điểm" in sol_a['chosen_statement']:
        # Copy the original statement first
        question_content += f"Hàm số \\(y = \\frac{{{sol_a['numerator']}}}{{{sol_a['denominator']}}}\\) có {sol_a['chosen_statement']}\n\n"
        # Then add the equivalence
        question_content += f"\\(\\Leftrightarrow\\) Hàm số \\(y = \\frac{{{sol_a['numerator']}}}{{{sol_a['denominator']}}}\\) có tiệm cận đứng: \\(x = {sol_a['A']}\\); tiệm cận ngang: \\(y = {sol_a['B']}\\)\n\n"
    else:
        question_content += f"Hàm số \\(y = \\frac{{{sol_a['numerator']}}}{{{sol_a['denominator']}}}\\) có:\n\n"
    
    # Format all LaTeX expressions to clean up double negatives
    tiemcan_dung = clean_negative_signs(f"\\frac{{-{sol_a['c']}}}{{n}} = {sol_a['A']}")
    n_value_calc = clean_negative_signs(f"\\frac{{-{sol_a['c']}}}{{{sol_a['A']}}} = {format_fraction_latex(sol_a['n_value'].numerator, sol_a['n_value'].denominator)}")
    if sol_a['a'] >= 0:
        tiemcan_ngang_expr = f"{format_coefficient_for_display(sol_a['d'], 'm')} + {sol_a['a']}"
    else:
        tiemcan_ngang_expr = f"{format_coefficient_for_display(sol_a['d'], 'm')} - {abs(sol_a['a'])}"
    tiemcan_ngang_expr = standardize_math_expression(tiemcan_ngang_expr)
    tiemcan_ngang = clean_negative_signs(f"\\frac{{{tiemcan_ngang_expr}}}{{n}} = {sol_a['B']}")
    
    question_content += f"Tiệm cận đứng: \\(x = {tiemcan_dung} \\Rightarrow n = {n_value_calc}\\)\n\n"
    question_content += f"Tiệm cận ngang: \\(y = {tiemcan_ngang}\\)\n\n"
    
    # Format with parentheses for negative numbers in multiplication
    B_display = f"({sol_a['B']})" if sol_a['B'] < 0 else str(sol_a['B'])
    n_value_display = f"({format_fraction_latex(sol_a['n_value'].numerator, sol_a['n_value'].denominator)})" if sol_a['n_value'].numerator * sol_a['n_value'].denominator < 0 else format_fraction_latex(sol_a['n_value'].numerator, sol_a['n_value'].denominator)
    
    # Calculate B * n_value
    B_times_n = sol_a['B'] * sol_a['n_value']
    B_times_n_display = format_fraction_latex(B_times_n.numerator, B_times_n.denominator)
    
    question_content += f"\\(\\Leftrightarrow {standardize_math_expression(f'{sol_a['d']}m + {sol_a['a']}')} = {B_display} \\cdot {n_value_display} = {B_times_n_display}\\)\n\n"
    
    # Calculate the result of B * n_value - a
    B_times_n_minus_a = B_times_n - sol_a['a']
    B_times_n_minus_a_display = format_fraction_latex(B_times_n_minus_a.numerator, B_times_n_minus_a.denominator)
    
    question_content += f"\\(\\Rightarrow {standardize_math_expression(f'{sol_a['d']}m')} = {B_times_n_display} {'-' if sol_a['a'] > 0 else '+'} {abs(sol_a['a'])} = {B_times_n_minus_a_display}\\)\n\n"
    question_content += f"\\(\\Rightarrow m = {format_fraction_latex(sol_a['m_value'].numerator, sol_a['m_value'].denominator)}\\)\n\n"
    
    # Format the final calculation
    coeff_a_display = f"({sol_a['coeff_a']})" if sol_a['coeff_a'] < 0 else str(sol_a['coeff_a'])
    coeff_b_display = f"({sol_a['coeff_b']})" if sol_a['coeff_b'] < 0 else str(sol_a['coeff_b'])
    m_value_display = f"({format_fraction_latex(sol_a['m_value'].numerator, sol_a['m_value'].denominator)})" if sol_a['m_value'].numerator * sol_a['m_value'].denominator < 0 else format_fraction_latex(sol_a['m_value'].numerator, sol_a['m_value'].denominator)
    n_value_display = f"({format_fraction_latex(sol_a['n_value'].numerator, sol_a['n_value'].denominator)})" if sol_a['n_value'].numerator * sol_a['n_value'].denominator < 0 else format_fraction_latex(sol_a['n_value'].numerator, sol_a['n_value'].denominator)
    
    final_calc = f"{coeff_a_display} \\cdot {m_value_display} {'+' if sol_a['coeff_b'] >= 0 else '-'} {abs(sol_a['coeff_b'])} \\cdot {n_value_display}"
    final_result = format_fraction_latex(sol_a['correct_result'].numerator, sol_a['correct_result'].denominator)
    
    question_content += f"Vậy \\({sol_a['coeff_a']}m {'+' if sol_a['coeff_b'] >= 0 else '-'} {abs(sol_a['coeff_b'])}n = {final_calc} = {final_result}\\)\n\n"
    
    # Add conclusion for proposition a)
    displayed_result_a = format_fraction_latex(sol_a['displayed_result'].numerator, sol_a['displayed_result'].denominator)
    if sol_a['displayed_result'] == sol_a['correct_result']:
        question_content += f"Kết luận: Mệnh đề a) ĐÚNG.\n\n"
    else:
        question_content += f"Kết luận: Mệnh đề a) SAI.\n\n"
    
    # Solution for proposition b)
    sol_b = question_b_data['solution_data']
    question_content += "Lời giải cho mệnh đề b):\n\n"
    question_content += f"Hàm số \\(y = \\frac{{{sol_b['numerator']}}}{{{sol_b['denominator']}}}\\) có:\n\n"
    
    # Clean up expressions for display
    tiemcan_ngang = clean_negative_signs(f"\\frac{{{sol_b['d']}m + {sol_b['a']}}}{{{sol_b['e']}}}")
    tiemcan_dung = clean_negative_signs(f"\\frac{{-{sol_b['c']}}}{{{sol_b['e']}}} = {format_fraction_latex(sol_b['vertical_asymptote'].numerator, sol_b['vertical_asymptote'].denominator)}")
    
    question_content += f"Tiệm cận ngang: \\(y = {tiemcan_ngang}\\)\n\n"
    question_content += f"Tiệm cận đứng: \\(x = {tiemcan_dung}\\)\n\n"
    
    # Calculate the actual values for display
    vertical_asymptote_value = format_fraction_latex(sol_b['vertical_asymptote'].numerator, sol_b['vertical_asymptote'].denominator)
    
    question_content += f"Diện tích hình chữ nhật tạo bởi hai đường tiệm cận và hai trục tọa độ:\n\n"
    question_content += f"\\(S = \\left| {tiemcan_ngang} \\cdot {vertical_asymptote_value} \\right| = \\left| \\frac{{{sol_b['d']}m + {sol_b['a']}}}{{{sol_b['e']}}} \\cdot {vertical_asymptote_value} \\right| = \\frac{{|{sol_b['d']}m + {sol_b['a']}| \\cdot |{sol_b['c']}|}}{{{sol_b['e']**2}}}\\)\n\n"
    question_content += f"Theo đề bài: \\(S = {sol_b['S0']}\\)\n\n"
    question_content += f"\\(\\Rightarrow \\frac{{|{sol_b['d']}m + {sol_b['a']}| \\cdot {abs(sol_b['c'])}}}{{{sol_b['e']**2}}} = {sol_b['S0']}\\)\n\n"
    question_content += f"\\(\\Leftrightarrow |{sol_b['d']}m + {sol_b['a']}| = \\frac{{{sol_b['S0']} \\cdot {sol_b['e']**2}}}{{{abs(sol_b['c'])}}} = {format_number_enhanced(sol_b['target_numerator'])}\\)\n\n"
    question_content += f"\\(\\Leftrightarrow {sol_b['d']}m + {sol_b['a']} = \\pm {format_number_enhanced(sol_b['target_numerator'])}\\)\n\n"
    question_content += f"Trường hợp 1: \\({sol_b['d']}m + {sol_b['a']} = {format_number_enhanced(sol_b['target_numerator'])} \\Rightarrow m = {format_number_enhanced(sol_b['m_positive'])}\\)\n\n"
    question_content += f"Trường hợp 2: \\({sol_b['d']}m + {sol_b['a']} = {format_number_enhanced(-sol_b['target_numerator'])} \\Rightarrow m = {format_number_enhanced(sol_b['m_negative'])}\\)\n\n"
    question_content += f"Tổng bình phương các giá trị: \\(({format_number_enhanced(sol_b['m_positive'])})^2 + ({format_number_enhanced(sol_b['m_negative'])})^2 = {format_number_enhanced(sol_b['sum_of_squares_correct'])}\\)\n\n"
    
    # Add conclusion for proposition b)
    displayed_sum_b = format_number_enhanced(sol_b['sum_of_squares_displayed'])
    correct_sum_b = format_number_enhanced(sol_b['sum_of_squares_correct'])
    if sol_b['sum_of_squares_displayed'] == sol_b['sum_of_squares_correct']:
        question_content += f"Kết luận: Mệnh đề b) ĐÚNG.\n\n"
    else:
        question_content += f"Kết luận: Mệnh đề b) SAI.\n\n"
    
    # Solution for proposition c)
    sol_c = question_c_data['solution_data']
    question_content += "Lời giải cho mệnh đề c):\n\n"
    
    # Calculate specific values using CORRECT logic
    # For f(a) ≠ 0 where f(a) = a² + (bm+c)a + constant_term
    # f(a) = a² + ba*m + ca + constant_term = (a² + ca + constant_term) + ba*m
    f_a_const = sol_c['a']**2 + sol_c['a']*sol_c['c'] + sol_c['constant_term']  # Constant part of f(a)
    f_a_coeff = sol_c['a']*sol_c['b']  # Coefficient of m in f(a)
    m_excluded = safe_divide(-f_a_const, f_a_coeff)  # Value of m where f(a) = 0
    
    if sol_c['chosen_option'] == "2 tiệm cận đứng":
        question_content += f"Để có 2 tiệm cận đứng:\n\n"
        question_content += f"Điều kiện: \\(f({sol_c['a']}) \\neq 0\\) và mẫu số có 2 nghiệm phân biệt\n\n"
    else:
        question_content += f"Để có 3 tiệm cận:\n\n"
        question_content += f"- Dễ thấy hàm số chỉ có 1 tiệm cận ngang \\(y = 0\\) (vì bậc tử < bậc mẫu)\n\n"
        question_content += f"- Để hàm số có 3 tiệm cận \\(\\Rightarrow\\) hàm số có 2 tiệm cận đứng\n\n"
    
    # Start the system of inequalities approach with continuous equivalences
    question_content += f"\\(\\Leftrightarrow \\begin{{cases}} \nf({sol_c['a']}) \\neq 0 \\\\\n\\Delta > 0\n\\end{{cases}}\\)\n\n"
    
    # Calculate specific values for direct substitution
    delta_const = sol_c['c']**2 - 4*sol_c['constant_term']  # Constant part of Delta
    
    # Continue with equivalences, substituting calculated values directly
    question_content += f"\\(\\Leftrightarrow \\begin{{cases}} \nm \\neq {format_number_enhanced(m_excluded)} \\\\\n{sol_c['b']**2}m^2 + {2*sol_c['b']*sol_c['c']}m + {delta_const} > 0\n\\end{{cases}}\\)\n\n"
    
    # Calculate discriminant of the quadratic inequality to determine final result
    quad_discriminant = (2*sol_c['b']*sol_c['c'])**2 - 4*(sol_c['b']**2)*delta_const
    
    if quad_discriminant < 0:
        # Quadratic is always positive
        if sol_c['b']**2 > 0:  # Coefficient of m² is positive
            question_content += f"\\(\\Leftrightarrow m \\in \\mathbb{{R}} \\setminus \\{{{format_number_enhanced(m_excluded)}\\}}\\)\n\n"
        else:
            question_content += f"\\(\\Leftrightarrow \\text{{Vô nghiệm}}\\)\n\n"
    elif quad_discriminant == 0:
        # Quadratic has one repeated root
        quad_root = -(2*sol_c['b']*sol_c['c'])/(2*sol_c['b']**2)
        if sol_c['b']**2 > 0:
            question_content += f"\\(\\Leftrightarrow m \\in \\mathbb{{R}} \\setminus \\{{{format_number_enhanced(m_excluded)}, {format_number_enhanced(quad_root)}\\}}\\)\n\n"
    else:
        # Quadratic has two distinct roots
        import math
        
        # For quadratic am² + bm + c > 0, the discriminant and roots are:
        # Here we have: (sol_c['b']²)m² + (2*sol_c['b']*sol_c['c'])m + delta_const > 0
        a_coeff = sol_c['b']**2
        b_coeff = 2*sol_c['b']*sol_c['c']
        c_coeff = delta_const
        
        # Calculate discriminant and roots properly
        discriminant = b_coeff**2 - 4*a_coeff*c_coeff
        sqrt_disc = math.sqrt(discriminant)
        
        root1 = (-b_coeff - sqrt_disc) / (2*a_coeff)
        root2 = (-b_coeff + sqrt_disc) / (2*a_coeff)
        
        # Try to format roots as exact expressions with radicals
        def format_quadratic_root_simple(discriminant, b_coeff, a_coeff, is_positive_sqrt=True):
            """Format quadratic root in LaTeX with radicals when possible"""
            sqrt_disc = math.sqrt(discriminant)
            
            # Check if discriminant can be written as k²×n where n is square-free
            # Try to find the largest perfect square factor
            sqrt_disc_rounded = round(sqrt_disc)
            
            # Check if sqrt_disc is close to an integer times sqrt of a small integer
            for k in range(1, 20):
                for n in range(2, 50):
                    if abs(discriminant - k*k*n) < 1e-10:
                        # Found discriminant = k²n, so √discriminant = k√n
                        # Simplify √n if possible (e.g., √8 = 2√2)
                        simplified_n = n
                        simplified_k = k
                        
                        # Check if n has perfect square factors
                        for factor in [4, 9, 16, 25, 36, 49]:
                            if n % factor == 0:
                                simplified_k *= int(math.sqrt(factor))
                                simplified_n = n // factor
                                break
                        
                        sqrt_part = f"{simplified_k}\\sqrt{{{simplified_n}}}" if simplified_k > 1 else f"\\sqrt{{{simplified_n}}}"
                        
                        # Calculate the root: (-b ± k√n) / (2a)
                        sign = "+" if is_positive_sqrt else "-"
                        
                        # Simplify the expression
                        if 2*a_coeff == 2:  # denominator is 2
                            constant_part = -b_coeff // 2 if b_coeff % 2 == 0 else None
                            if constant_part is not None and constant_part != 0:
                                return f"{constant_part} {sign} {sqrt_part}"
                            elif constant_part == 0:
                                return f"{sign if is_positive_sqrt else '-'}{sqrt_part}"
                            else:
                                return f"\\frac{{{-b_coeff} {sign} {sqrt_part}}}{{2}}"
                        else:
                            return f"\\frac{{{-b_coeff} {sign} {sqrt_part}}}{{{2*a_coeff}}}"
                        
            # Fallback to decimal approximation
            root_value = (-b_coeff + (sqrt_disc if is_positive_sqrt else -sqrt_disc)) / (2*a_coeff)
            return format_number_enhanced(root_value)
        
        # Format the roots using the simplified function
        root1_formatted = format_quadratic_root_simple(discriminant, b_coeff, a_coeff, False)
        root2_formatted = format_quadratic_root_simple(discriminant, b_coeff, a_coeff, True)
        
        if a_coeff > 0:  # Parabola opens upward
            # Final result considering the exclusion
            if m_excluded < min(root1, root2) or m_excluded > max(root1, root2):
                question_content += f"\\(\\Leftrightarrow m \\in (-\\infty, {root1_formatted}) \\cup ({root2_formatted}, +\\infty) \\setminus \\{{{format_number_enhanced(m_excluded)}\\}}\\)\n\n"
            else:
                question_content += f"\\(\\Leftrightarrow m \\in (-\\infty, {root1_formatted}) \\cup ({root2_formatted}, +\\infty)\\)\n\n"
    
    # Show the specific excluded value and count correctly
    question_content += f"Kết quả: Có \\({sol_c['correct_count']}\\) giá trị nguyên thỏa mãn\n\n"
    
    # Add conclusion for proposition c)
    if sol_c['displayed_count'] == sol_c['correct_count']:
        question_content += f"Kết luận: Mệnh đề c) ĐÚNG.\n\n"
    else:
        question_content += f"Kết luận: Mệnh đề c) SAI.\n\n"
    
    # Solution for proposition d)
    sol_d = question_d_data['solution_data']
    question_content += "Lời giải cho mệnh đề d):\n\n"
    
    # Generate detailed solution using the exact same function as asymptote_mc.py
    detailed_solution = generate_detailed_solution_oblique(
        sol_d['A'], sol_d['B'], sol_d['C'], sol_d['D'], sol_d['E'], 
        sol_d['slope'], sol_d['intercept']
    )
    
    question_content += f"{detailed_solution}\n\n"
    
    # Add conclusion for proposition d)
    displayed_answer_d = sol_d['displayed_answer']
    correct_answer_d = sol_d['ta_co_equation']
    if sol_d['displayed_answer'] == sol_d['ta_co_equation']:
        question_content += f"Kết luận: Mệnh đề d) ĐÚNG.\n\n"
    else:
        question_content += f"Kết luận: Mệnh đề d) SAI.\n\n"
    
    # Apply clean_negative_signs to the final content
    return clean_negative_signs(question_content)

def generate_all_questions(num_questions=5):
    """Generate specified number of questions, each with a), b), c), d) format."""
    
    questions = []
    
    # Generate specified number of questions
    for i in range(1, num_questions + 1):
        question = generate_single_question(i)
        questions.append(question)
    
    return questions

def format_radical_latex(number):
    """Convert common irrational numbers to radical form in LaTeX."""
    if isinstance(number, (int, float)):
        # Handle simple integers first
        if abs(number - round(number)) < 1e-10:
            return None  # Let it be handled as integer
            
        # Handle common square roots
        sqrt_values = {
            2: "\\sqrt{2}",
            3: "\\sqrt{3}",
            5: "\\sqrt{5}",
            6: "\\sqrt{6}",
            7: "\\sqrt{7}",
            8: "2\\sqrt{2}",
            10: "\\sqrt{10}",
            11: "\\sqrt{11}",
            12: "2\\sqrt{3}",
            13: "\\sqrt{13}",
            14: "\\sqrt{14}",
            15: "\\sqrt{15}",
            17: "\\sqrt{17}",
            18: "3\\sqrt{2}",
            19: "\\sqrt{19}",
            20: "2\\sqrt{5}",
            24: "2\\sqrt{6}",
            27: "3\\sqrt{3}",
            28: "2\\sqrt{7}",
            32: "4\\sqrt{2}",
            45: "3\\sqrt{5}",
            50: "5\\sqrt{2}",
            72: "6\\sqrt{2}",
            75: "5\\sqrt{3}",
            98: "7\\sqrt{2}",
            125: "5\\sqrt{5}"
        }
        
        for val, latex in sqrt_values.items():
            if abs(number - math.sqrt(val)) < 1e-10:
                return latex
            elif abs(number + math.sqrt(val)) < 1e-10:
                return f"-{latex}"
                
        # Handle fractions of square roots
        fraction_sqrt_values = [
            (math.sqrt(2)/2, "\\frac{\\sqrt{2}}{2}"),
            (math.sqrt(3)/2, "\\frac{\\sqrt{3}}{2}"),
            (math.sqrt(3)/3, "\\frac{\\sqrt{3}}{3}"),
            (math.sqrt(6)/3, "\\frac{\\sqrt{6}}{3}"),
            (math.sqrt(6)/6, "\\frac{\\sqrt{6}}{6}"),
            (math.sqrt(2)/3, "\\frac{\\sqrt{2}}{3}"),
            (math.sqrt(5)/5, "\\frac{\\sqrt{5}}{5}"),
            (math.sqrt(10)/10, "\\frac{\\sqrt{10}}{10}"),
            (2*math.sqrt(2)/3, "\\frac{2\\sqrt{2}}{3}"),
            (2*math.sqrt(3)/3, "\\frac{2\\sqrt{3}}{3}"),
        ]
        
        for val, latex in fraction_sqrt_values:
            if abs(number - val) < 1e-10:
                return latex
            elif abs(number + val) < 1e-10:
                return f"-{latex}"
                
        # Handle pi-related values
        pi_values = [
            (math.pi, "\\pi"),
            (math.pi/2, "\\frac{\\pi}{2}"),
            (math.pi/3, "\\frac{\\pi}{3}"),
            (math.pi/4, "\\frac{\\pi}{4}"),
            (math.pi/6, "\\frac{\\pi}{6}"),
            (2*math.pi, "2\\pi"),
            (3*math.pi/2, "\\frac{3\\pi}{2}"),
            (2*math.pi/3, "\\frac{2\\pi}{3}"),
            (3*math.pi/4, "\\frac{3\\pi}{4}"),
            (5*math.pi/6, "\\frac{5\\pi}{6}")
        ]
        
        for val, latex in pi_values:
            if abs(number - val) < 1e-10:
                return latex
            elif abs(number + val) < 1e-10:
                return f"-{latex}"
                
        # Handle e-related values
        e_values = [
            (math.e, "e"),
            (math.e/2, "\\frac{e}{2}"),
            (2*math.e, "2e"),
            (math.e/3, "\\frac{e}{3}"),
            (3*math.e, "3e")
        ]
        
        for val, latex in e_values:
            if abs(number - val) < 1e-10:
                return latex
            elif abs(number + val) < 1e-10:
                return f"-{latex}"
    
    return None

def format_number_enhanced(number):
    """Enhanced number formatting: tries radical form first, then fraction form."""
    if isinstance(number, (int, float)):
        # First try to convert to radical form
        radical_form = format_radical_latex(number)
        if radical_form:
            return radical_form
        
        # If not a recognizable radical, convert to fraction
        frac = Fraction(number).limit_denominator()
        if frac.denominator == 1:
            return str(frac.numerator)
        else:
            if frac.numerator < 0:
                return f"-\\frac{{{abs(frac.numerator)}}}{{{frac.denominator}}}"
            else:
                return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
    elif isinstance(number, Fraction):
        return format_fraction_latex(number.numerator, number.denominator)
    else:
        return str(number)

def safe_divide(numerator, denominator):
    """Safe division that returns a Fraction instead of float."""
    return Fraction(numerator, denominator)

if __name__ == "__main__":
    try:
        # Check command line arguments for number of questions
        import sys
        num_questions = 5  # Default
        if len(sys.argv) > 1:
            try:
                num_questions = int(sys.argv[1])
            except ValueError:
                print("Lỗi: Tham số phải là số nguyên. Sử dụng mặc định 5 câu.")
                num_questions = 5
        
        logging.info(f"Generating {num_questions} asymptotic advanced questions")
        
        # Generate all questions
        all_questions = generate_all_questions(num_questions)
        
        # Create LaTeX document
        latex_content = """\\documentclass{article}
\\usepackage{fontspec} % For XeLaTeX font support
\\usepackage{amsmath} % For advanced math environments
\\usepackage{amsfonts}
\\usepackage{amssymb}
\\usepackage{geometry} % For page layout
\\geometry{a4paper, margin=1in} % Set page margins
\\usepackage{polyglossia}
\\setmainlanguage{vietnamese}
\\setmainfont{Times New Roman}

\\begin{document}

"""
        
        # Add all questions with proper spacing
        for i, question in enumerate(all_questions):
            latex_content += question
            if i < len(all_questions) - 1:  # Add spacing between questions except the last one
                latex_content += "\n\n"
            else:
                latex_content += "\n\n"
        
        latex_content += "\\end{document}"
        
        # Write to file
        filename = "asymptotic_advanced_questions_generated.tex"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        logging.info("Successfully wrote LaTeX content to %s", filename)
        print(f"Đã tạo thành công file {filename}. Hãy compile bằng XeLaTeX để tạo PDF.")
        
    except Exception as e:
        logging.error("Error in main: %s", e)
        print(f"Lỗi: {e}")
        sys.exit(1)