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
    
    # Handle signs - Thay đổi theo yêu cầu: 2 dấu trừ thành dấu cộng, +- thành -
    if is_first:
        if num < 0:
            return f"+{var_str}"  # 2 dấu trừ thành dấu cộng
        else:
            return var_str
    else:
        if num < 0:
            return f" - {var_str}"  # +- thành -
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
    # x{2} → x^{2}
    expr = re.sub(r'([a-z])\{(\d+)\}', r'\1^{\2}', expr)
    
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
    expr = re.sub(r'\$\+', r'$', expr)                   # $+ → $
    expr = re.sub(r'\\\(\+', r'\\(', expr)               # \(+ → \(
    
    # 7. Chuẩn hóa hệ số 1 trong phân số
    expr = re.sub(r'\\frac{1([a-z])}{', r'\\frac{\1}{', expr)      # \frac{1m}{ → \frac{m}{
    expr = re.sub(r'\\frac{-1([a-z])}{', r'\\frac{-\1}{', expr)    # \frac{-1m}{ → \frac{-m}{
    
    # 8. Chuẩn hóa biểu thức x^{1} → x
    expr = re.sub(r'([a-z])\^{1}(?![0-9])', r'\1', expr)
    
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

def generate_wrong_answers_asymptote_1(correct_result, m_value, n_value, coeff_a, coeff_b, A, B, c, d, a):
    """Generate 3 wrong answers based on common mistakes in asymptote calculations."""
    wrong_answers = []
    
    # Wrong answer 1: Sai dấu trong tính tiệm cận đứng (dùng c/n thay vì -c/n)
    n_wrong1 = Fraction(c, A)  # Quên dấu âm
    m_wrong1 = Fraction(B * n_wrong1 - a, d)
    wrong_result1 = coeff_a * m_wrong1 + coeff_b * n_wrong1
    wrong_answers.append(format_fraction_latex(wrong_result1.numerator, wrong_result1.denominator))
    
    # Wrong answer 2: Sai công thức tiệm cận ngang (dùng dm/n thay vì (dm+a)/n)
    # Tức là quên hằng số a trong tử số
    m_wrong2 = Fraction(B * n_value, d)  # Quên trừ a
    wrong_result2 = coeff_a * m_wrong2 + coeff_b * n_value
    wrong_answers.append(format_fraction_latex(wrong_result2.numerator, wrong_result2.denominator))
    
    # Wrong answer 3: Nhầm dấu trong phép toán cuối (sai dấu của coeff_a hoặc coeff_b)
    wrong_result3 = -coeff_a * m_value + coeff_b * n_value  # Đổi dấu coeff_a
    wrong_answers.append(format_fraction_latex(wrong_result3.numerator, wrong_result3.denominator))
    
    return wrong_answers

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
    correct_result_str = format_fraction_latex(correct_result.numerator, correct_result.denominator)
    
    # Generate wrong answers using professional approach
    wrong_answers = generate_wrong_answers_asymptote_1(correct_result, m_value, n_value, coeff_a, coeff_b, A, B, c, d, a)
    
    # Create all options
    all_options = [correct_result_str] + wrong_answers
    random.shuffle(all_options)
    correct_index = all_options.index(correct_result_str)
    
    # Random choice between correct and wrong for proposition
    is_correct = random.choice([True, False])
    displayed_result = correct_result_str if is_correct else random.choice(wrong_answers)
    
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
        'proposition': f"Hàm số \\(y = \\frac{{{numerator}}}{{{denominator}}}\\) có {chosen_statement} thì \\({coeff_a}m {'+' if coeff_b >= 0 else '-'} {abs(coeff_b)}n = {displayed_result}\\).",
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
            'displayed_result': displayed_result,
            'all_options': all_options,
            'correct_index': correct_index,
            'correct_answer': correct_result_str
        }
    }

def generate_wrong_answers_asymptote_2(sum_of_squares_correct, m_positive, m_negative, S0, target_numerator, d, a):
    """Generate 3 wrong answers based on common mistakes in area calculations."""
    wrong_answers = []
    
    # Wrong answer 1: Quên dấu trị tuyệt đối (chỉ lấy giá trị dương)
    # Tức là chỉ tính m_positive^2 + 0^2 hoặc tương tự
    wrong_sum1 = m_positive**2  # Chỉ lấy 1 nghiệm
    wrong_answers.append(format_number_enhanced(wrong_sum1))
    
    # Wrong answer 2: Sai công thức diện tích (dùng S = S0 thay vì S = 2*S0) 
    # Dẫn đến |dm + a| = S0*e²/|c| thay vì 2*S0*e²/|c|
    target_wrong2 = target_numerator / 2  # Chia đôi target
    m_positive_wrong2 = safe_divide(target_wrong2 - a, d)
    m_negative_wrong2 = safe_divide(-target_wrong2 - a, d)
    wrong_sum2 = m_positive_wrong2**2 + m_negative_wrong2**2
    wrong_answers.append(format_number_enhanced(wrong_sum2))
    
    # Wrong answer 3: Nhầm công thức tổng bình phương (dùng (m1 + m2)² thay vì m1² + m2²)
    sum_of_values = m_positive + m_negative  # m1 + m2
    wrong_sum3 = sum_of_values**2  # (m1 + m2)²
    wrong_answers.append(format_number_enhanced(wrong_sum3))
    
    return wrong_answers

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
    sum_of_squares_correct_str = format_number_enhanced(sum_of_squares_correct)
    
    # Generate wrong answers using professional approach
    wrong_answers = generate_wrong_answers_asymptote_2(sum_of_squares_correct, m_positive, m_negative, S0, target_numerator, d, a)
    
    # Create all options
    all_options = [sum_of_squares_correct_str] + wrong_answers
    random.shuffle(all_options)
    correct_index = all_options.index(sum_of_squares_correct_str)
    
    # Random choice between correct and wrong for proposition
    is_correct = random.choice([True, False])
    sum_of_squares_displayed = sum_of_squares_correct_str if is_correct else random.choice(wrong_answers)
    
    # Format the function
    numerator = format_polynomial_clean(d, a, b, 'x', 'm')
    denominator = format_simple_polynomial(e, c, 'x')
    
    # Clean up negative signs
    numerator = clean_negative_signs(numerator)
    denominator = clean_negative_signs(denominator)
    
    return {
        'proposition': f"Hàm số \\(y = \\frac{{{numerator}}}{{{denominator}}}\\) có đường tiệm cận đứng và ngang tạo với hai trục tọa độ một hình chữ nhật có diện tích bằng \\({S0}\\) thì tổng bình phương các giá trị của \\(m\\) là \\({sum_of_squares_displayed}\\).",
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
            'sum_of_squares_displayed': sum_of_squares_displayed,
            'all_options': all_options,
            'correct_index': correct_index,
            'correct_answer': sum_of_squares_correct_str
        }
    }

def generate_wrong_answers_asymptote_3(correct_count, valid_m_values, a, b, c, d, constant_term):
    """Generate 3 wrong answers based on common mistakes in counting asymptotes."""
    wrong_answers = []
    
    # Wrong answer 1: Quên điều kiện f(a) ≠ 0 (chỉ tính Δ > 0)
    count_wrong1 = 0
    for m in range(-10, 11):
        delta = (b*m + c)**2 - 4*constant_term
        if delta > 0:  # Chỉ kiểm tra Δ > 0, bỏ qua f(a) ≠ 0
            count_wrong1 += 1
    wrong_answers.append(str(count_wrong1))
    
    # Wrong answer 2: Sai điều kiện Δ (dùng Δ ≥ 0 thay vì Δ > 0)
    count_wrong2 = 0
    for m in range(-10, 11):
        f_a = a*a + (b*m + c)*a + constant_term
        delta = (b*m + c)**2 - 4*constant_term
        if f_a != 0 and delta >= 0:  # Dùng Δ ≥ 0 thay vì Δ > 0
            count_wrong2 += 1
    wrong_answers.append(str(count_wrong2))
    
    # Wrong answer 3: Nhầm khoảng đếm (dùng [-10, 10) thay vì [-10, 10] hoặc nhầm logic)
    # Hoặc tính sai công thức f(a)
    count_wrong3 = 0
    for m in range(-10, 10):  # Thiếu m=10
        f_a = a*a + (b*m + c)*a + constant_term
        delta = (b*m + c)**2 - 4*constant_term
        if f_a != 0 and delta > 0:
            count_wrong3 += 1
    wrong_answers.append(str(count_wrong3))
    
    return wrong_answers

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
    
    # Calculate the CORRECT number of integer values in [-10, 10]
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
    
    # Count valid integer values of m in [-10, 10]
    valid_m_values = []
    for m in range(-10, 11):
        # Check condition 1: f(a) ≠ 0
        f_a = a*a + (b*m + c)*a + constant_term
        condition1_ok = (f_a != 0)
        
        # Check condition 2: Δ > 0
        delta = (b*m + c)**2 - discriminant_const
        condition2_ok = (delta > 0)
        
        if condition1_ok and condition2_ok:
            valid_m_values.append(m)
    
    correct_count = len(valid_m_values)
    correct_count_str = str(correct_count)
    
    # Generate wrong answers using professional approach
    wrong_answers = generate_wrong_answers_asymptote_3(correct_count, valid_m_values, a, b, c, d, constant_term)
    
    # Create all options
    all_options = [correct_count_str] + wrong_answers
    random.shuffle(all_options)
    correct_index = all_options.index(correct_count_str)
    
    # Random choice between correct and wrong for proposition
    is_correct = random.choice([True, False])
    displayed_count = correct_count_str if is_correct else random.choice(wrong_answers)
    
    # Debug: Print the logic to verify correctness
    # print(f"DEBUG: correct_count={correct_count}, displayed_count={displayed_count}, is_correct={is_correct}")
    
    return {
        'proposition': f"Có \\({displayed_count}\\) giá trị nguyên của \\(m\\) trong khoảng \\([-10; 10]\\) để hàm số \\(y = {formula}\\) có {chosen_option}.",
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
            'all_options': all_options,
            'correct_index': correct_index,
            'correct_answer': correct_count_str
        }
    }

def format_full_asymptote_equation(A, B, C, D, E):
    """Format the full asymptote equation with all three terms like asymptote_mc.py"""
    # Calculate all values
    slope = Fraction(A, D)
    BD = B * D
    AE = A * E
    BD_minus_AE = BD - AE
    D_squared = D * D
    intercept = Fraction(BD_minus_AE, D_squared)
    R_numerator = BD_minus_AE * E
    R = C - Fraction(R_numerator, D_squared)
    
    # Format each component
    slope_display = format_fraction_latex(slope.numerator, slope.denominator)
    intercept_display = format_fraction_latex(intercept.numerator, intercept.denominator)
    R_display = format_fraction_latex(R.numerator, R.denominator)
    denom_str = format_polynomial([D, E])
    
    # Format slope term
    if slope == 0:
        slope_term = ""
    elif slope.numerator == 1 and slope.denominator == 1:
        slope_term = "x"
    elif slope.numerator == -1 and slope.denominator == 1:
        slope_term = "-x"
    else:
        slope_term = f"{slope_display}x"
    
    # Build the equation with proper sign handling
    terms = []
    
    # Add slope term
    if slope != 0:
        terms.append(slope_term)
    
    # Add intercept term (avoid + with negative numbers)
    if intercept != 0:
        if len(terms) > 0:
            if intercept > 0:
                terms.append(f" + {intercept_display}")
            else:
                terms.append(f" - {format_fraction_latex(abs(intercept.numerator), abs(intercept.denominator))}")
        else:
            terms.append(intercept_display)
    
    # Add R term (avoid + with negative numbers)
    if R != 0:
        if len(terms) > 0:
            if R > 0:
                terms.append(f" + \\frac{{{R_display}}}{{{denom_str}}}")
            else:
                terms.append(f" - \\frac{{{format_fraction_latex(abs(R.numerator), abs(R.denominator))}}}{{{denom_str}}}")
        else:
            terms.append(f"\\frac{{{R_display}}}{{{denom_str}}}")
    
    # If all terms are zero
    if not terms:
        return "0"
    
    return "".join(terms)

def generate_wrong_answers_oblique(correct_slope, correct_intercept):
    """Generate 3 wrong answers based on common mistakes like asymptote_mc.py"""
    wrong_answers = []
    
    # Wrong answer 1: Change slope slightly
    wrong_slope1 = correct_slope + random.choice([Fraction(-1), Fraction(1), Fraction(-1, 2), Fraction(1, 2)])
    wrong_answers.append((wrong_slope1, correct_intercept))
    
    # Wrong answer 2: Change intercept
    wrong_intercept2 = correct_intercept + random.choice([Fraction(-2), Fraction(-1), Fraction(1), Fraction(2)])
    wrong_answers.append((correct_slope, wrong_intercept2))
    
    # Wrong answer 3: Common formula mistake (BD + AE instead of BD - AE)
    # This simulates using (BD + AE)/D² instead of (BD - AE)/D²
    wrong_intercept3 = correct_intercept + Fraction(2 * correct_slope.denominator * correct_intercept.denominator, correct_intercept.denominator)
    if wrong_intercept3 == correct_intercept:
        wrong_intercept3 = correct_intercept + Fraction(3)
    wrong_answers.append((correct_slope, wrong_intercept3))
    
    return wrong_answers

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
    
    # Fix x{2} → x^2 formatting
    num_str = num_str.replace("x{2}", "x^2")
    denom_str = denom_str.replace("x{2}", "x^2")
    
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
    
    # Add R term like in asymptote_mc.py
    if R != 0:
        R_display = format_fraction_latex(R.numerator, R.denominator)
        if R > 0:
            ta_co_parts.append(f" + \\frac{{{R_display}}}{{{denom_str}}}")
        else:
            ta_co_parts.append(f" - \\frac{{{format_fraction_latex(abs(R.numerator), abs(R.denominator))}}}{{{denom_str}}}")
    
    ta_co_equation = "".join(ta_co_parts)
    
    # Create correct answer using standard format 
    correct_answer_parts = []
    
    if slope.numerator == 1 and slope.denominator == 1:
        correct_answer_parts.append("x")
    elif slope.numerator == -1 and slope.denominator == 1:
        correct_answer_parts.append("-x")
    elif slope != 0:
        correct_answer_parts.append(f"{format_fraction_latex(slope.numerator, slope.denominator)}x")
    
    if intercept != 0:
        intercept_display = format_fraction_latex(intercept.numerator, intercept.denominator)
        if len(correct_answer_parts) > 0:
            if intercept > 0:
                correct_answer_parts.append(f" + {intercept_display}")
            else:
                correct_answer_parts.append(f" - {format_fraction_latex(abs(intercept.numerator), abs(intercept.denominator))}")
        else:
            correct_answer_parts.append(intercept_display)
    
    correct_answer = "".join(correct_answer_parts) if correct_answer_parts else "0"
    
    # Generate wrong answers using standard format
    wrong_answers = generate_wrong_answers_oblique(slope, intercept)
    wrong_answer_strs = []
    
    # Generate wrong options using standard format 
    for wrong_slope, wrong_intercept in wrong_answers:
        wrong_parts = []
        
        if wrong_slope.numerator == 1 and wrong_slope.denominator == 1:
            wrong_parts.append("x")
        elif wrong_slope.numerator == -1 and wrong_slope.denominator == 1:
            wrong_parts.append("-x")
        elif wrong_slope != 0:
            wrong_parts.append(f"{format_fraction_latex(wrong_slope.numerator, wrong_slope.denominator)}x")
        
        if wrong_intercept != 0:
            wrong_intercept_display = format_fraction_latex(wrong_intercept.numerator, wrong_intercept.denominator)
            if len(wrong_parts) > 0:
                if wrong_intercept > 0:
                    wrong_parts.append(f" + {wrong_intercept_display}")
                else:
                    wrong_parts.append(f" - {format_fraction_latex(abs(wrong_intercept.numerator), abs(wrong_intercept.denominator))}")
            else:
                wrong_parts.append(wrong_intercept_display)
        
        wrong_answer_strs.append("".join(wrong_parts) if wrong_parts else "0")
    
    # Create all options
    all_options = [correct_answer] + wrong_answer_strs
    random.shuffle(all_options)
    correct_index = all_options.index(correct_answer)
    
    # Randomly choose if this is correct or wrong answer (for the proposition)
    is_correct = random.choice([True, False])
    displayed_answer = correct_answer if is_correct else random.choice(wrong_answer_strs)
    
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
            'all_options': all_options,
            'correct_index': correct_index,
            'correct_answer': correct_answer,
            'slope': slope,
            'intercept': intercept
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

def generate_detailed_solution_asymptote_1(sol):
    """Generate detailed solution for asymptote question 1."""
    solution_content = ""
    
    # Add equivalence explanation at the beginning if statement 2 or 3 was chosen
    if "đi qua điểm" in sol['chosen_statement'] or "giao nhau tại điểm" in sol['chosen_statement']:
        # Copy the original statement first
        solution_content += f"Hàm số \\(y = \\frac{{{sol['numerator']}}}{{{sol['denominator']}}}\\) có {sol['chosen_statement']}\n\n"
        # Then add the equivalence
        solution_content += f"\\(\\Leftrightarrow\\) Hàm số \\(y = \\frac{{{sol['numerator']}}}{{{sol['denominator']}}}\\) có tiệm cận đứng: \\(x = {sol['A']}\\); tiệm cận ngang: \\(y = {sol['B']}\\)\n\n"
    else:
        solution_content += f"Hàm số \\(y = \\frac{{{sol['numerator']}}}{{{sol['denominator']}}}\\) có:\n\n"
    
    # Format all LaTeX expressions to clean up double negatives
    tiemcan_dung = clean_negative_signs(f"\\frac{{-{sol['c']}}}{{n}} = {sol['A']}")
    n_value_calc = clean_negative_signs(f"\\frac{{-{sol['c']}}}{{{sol['A']}}} = {format_fraction_latex(sol['n_value'].numerator, sol['n_value'].denominator)}")
    if sol['a'] >= 0:
        tiemcan_ngang_expr = f"{format_coefficient_for_display(sol['d'], 'm')} + {sol['a']}"
    else:
        tiemcan_ngang_expr = f"{format_coefficient_for_display(sol['d'], 'm')} - {abs(sol['a'])}"
    tiemcan_ngang_expr = standardize_math_expression(tiemcan_ngang_expr)
    tiemcan_ngang = clean_negative_signs(f"\\frac{{{tiemcan_ngang_expr}}}{{n}} = {sol['B']}")
    
    solution_content += f"\\begin{{itemize}}\n"
    solution_content += f"    \\item Tiệm cận đứng: \n"
    solution_content += f"    \\(x = {tiemcan_dung} \\Rightarrow n = {n_value_calc}\\)\n"
    solution_content += f"    \\item Tiệm cận ngang:\n"
    solution_content += f"    \\(y = {tiemcan_ngang}\\)\n"
    solution_content += f"\\end{{itemize}}\n\n"
    
    # Format with parentheses for negative numbers in multiplication
    B_display = f"({sol['B']})" if sol['B'] < 0 else str(sol['B'])
    n_value_display = f"({format_fraction_latex(sol['n_value'].numerator, sol['n_value'].denominator)})" if sol['n_value'].numerator * sol['n_value'].denominator < 0 else format_fraction_latex(sol['n_value'].numerator, sol['n_value'].denominator)
    
    # Calculate B * n_value
    B_times_n = sol['B'] * sol['n_value']
    B_times_n_display = format_fraction_latex(B_times_n.numerator, B_times_n.denominator)
    
    solution_content += f"\\(\\Leftrightarrow {standardize_math_expression(f'{sol['d']}m + {sol['a']}')} = {B_display} \\cdot {n_value_display} = {B_times_n_display}\\)\n\n"
    
    # Calculate the result of B * n_value - a
    B_times_n_minus_a = B_times_n - sol['a']
    B_times_n_minus_a_display = format_fraction_latex(B_times_n_minus_a.numerator, B_times_n_minus_a.denominator)
    
    solution_content += f"\\(\\Rightarrow {standardize_math_expression(f'{sol['d']}m')} = {B_times_n_display} {'-' if sol['a'] > 0 else '+'} {abs(sol['a'])} = {B_times_n_minus_a_display}\\)\n\n"
    solution_content += f"\\(\\Rightarrow m = {format_fraction_latex(sol['m_value'].numerator, sol['m_value'].denominator)}\\)\n\n"
    
    # Format the final calculation
    coeff_a_display = f"({sol['coeff_a']})" if sol['coeff_a'] < 0 else str(sol['coeff_a'])
    coeff_b_display = f"({sol['coeff_b']})" if sol['coeff_b'] < 0 else str(sol['coeff_b'])
    m_value_display = f"({format_fraction_latex(sol['m_value'].numerator, sol['m_value'].denominator)})" if sol['m_value'].numerator * sol['m_value'].denominator < 0 else format_fraction_latex(sol['m_value'].numerator, sol['m_value'].denominator)
    n_value_display = f"({format_fraction_latex(sol['n_value'].numerator, sol['n_value'].denominator)})" if sol['n_value'].numerator * sol['n_value'].denominator < 0 else format_fraction_latex(sol['n_value'].numerator, sol['n_value'].denominator)
    
    final_calc = f"{coeff_a_display} \\cdot {m_value_display} {'+' if sol['coeff_b'] >= 0 else '-'} {abs(sol['coeff_b'])} \\cdot {n_value_display}"
    final_result = format_fraction_latex(sol['correct_result'].numerator, sol['correct_result'].denominator)
    
    solution_content += f"Vậy \\({sol['coeff_a']}m {'+' if sol['coeff_b'] >= 0 else '-'} {abs(sol['coeff_b'])}n = {final_calc} = {final_result}\\)\n\n"
    
    return solution_content

def generate_detailed_solution_asymptote_2(sol):
    """Generate detailed solution for asymptote question 2."""
    solution_content = ""
    
    solution_content += f"Hàm số \\(y = \\frac{{{sol['numerator']}}}{{{sol['denominator']}}}\\) có:\n\n"
    
    # Clean up expressions for display
    tiemcan_ngang = clean_negative_signs(f"\\frac{{{sol['d']}m + {sol['a']}}}{{{sol['e']}}}")
    tiemcan_dung = clean_negative_signs(f"\\frac{{-{sol['c']}}}{{{sol['e']}}} = {format_fraction_latex(sol['vertical_asymptote'].numerator, sol['vertical_asymptote'].denominator)}")
    
    solution_content += f"\\begin{{itemize}}\n"
    solution_content += f"    \\item Tiệm cận ngang: \\(y = {tiemcan_ngang}\\)\n"
    solution_content += f"    \\item Tiệm cận đứng: \\(x = {tiemcan_dung}\\)\n"
    solution_content += f"\\end{{itemize}}\n\n"
    
    # Calculate the actual values for display
    vertical_asymptote_value = format_fraction_latex(sol['vertical_asymptote'].numerator, sol['vertical_asymptote'].denominator)
    
    solution_content += f"Diện tích hình chữ nhật tạo bởi hai đường tiệm cận và hai trục tọa độ:\n\n"
    solution_content += f"\\(S = \\left| {tiemcan_ngang} \\cdot {vertical_asymptote_value} \\right| = \\left| \\frac{{{sol['d']}m + {sol['a']}}}{{{sol['e']}}} \\cdot {vertical_asymptote_value} \\right| = \\frac{{|{sol['d']}m + {sol['a']}| \\cdot |{sol['c']}|}}{{{sol['e']**2}}}\\)\n\n"
    solution_content += f"Theo đề bài: \\(S = {sol['S0']}\\)\n\n"
    solution_content += f"\\(\\Rightarrow \\frac{{|{sol['d']}m + {sol['a']}| \\cdot {abs(sol['c'])}}}{{{sol['e']**2}}} = {sol['S0']}\\)\n\n"
    solution_content += f"\\(\\Leftrightarrow |{sol['d']}m + {sol['a']}| = \\frac{{{sol['S0']} \\cdot {sol['e']**2}}}{{{abs(sol['c'])}}} = {format_number_enhanced(sol['target_numerator'])}\\)\n\n"
    solution_content += f"\\(\\Leftrightarrow {sol['d']}m + {sol['a']} = \\pm {format_number_enhanced(sol['target_numerator'])}\\)\n\n"
    solution_content += f"Trường hợp 1: \\({sol['d']}m + {sol['a']} = {format_number_enhanced(sol['target_numerator'])} \\Rightarrow m = {format_number_enhanced(sol['m_positive'])}\\)\n\n"
    solution_content += f"Trường hợp 2: \\({sol['d']}m + {sol['a']} = {format_number_enhanced(-sol['target_numerator'])} \\Rightarrow m = {format_number_enhanced(sol['m_negative'])}\\)\n\n"
    solution_content += f"Tổng bình phương các giá trị: \\(({format_number_enhanced(sol['m_positive'])})^2 + ({format_number_enhanced(sol['m_negative'])})^2 = {format_number_enhanced(sol['sum_of_squares_correct'])}\\)\n\n"
    
    return solution_content

def generate_detailed_solution_asymptote_3(sol):
    """Generate detailed solution for asymptote question 3."""
    solution_content = ""
    
    # Calculate specific values using CORRECT logic
    # For f(a) ≠ 0 where f(a) = a² + (bm+c)a + constant_term
    # f(a) = a² + ba*m + ca + constant_term = (a² + ca + constant_term) + ba*m
    f_a_const = sol['a']**2 + sol['a']*sol['c'] + sol['constant_term']  # Constant part of f(a)
    f_a_coeff = sol['a']*sol['b']  # Coefficient of m in f(a)
    m_excluded = safe_divide(-f_a_const, f_a_coeff)  # Value of m where f(a) = 0
    
    if sol['chosen_option'] == "2 tiệm cận đứng":
        solution_content += f"Để có 2 tiệm cận đứng:\n\n"
        solution_content += f"Điều kiện: \\(f({sol['a']}) \\neq 0\\) và mẫu số có 2 nghiệm phân biệt\n\n"
    else:
        solution_content += f"Để có 3 tiệm cận:\n\n"
        solution_content += f"- Dễ thấy hàm số chỉ có 1 tiệm cận ngang \\(y = 0\\) (vì bậc tử < bậc mẫu)\n\n"
        solution_content += f"- Để hàm số có 3 tiệm cận \\(\\Rightarrow\\) hàm số có 2 tiệm cận đứng\n\n"
    
    # Start the system of inequalities approach with continuous equivalences
    solution_content += f"\\(\\Leftrightarrow \\begin{{cases}} \nf({sol['a']}) \\neq 0 \\\\\n\\Delta > 0\n\\end{{cases}}\\)\n\n"
    
    # Calculate specific values for direct substitution
    delta_const = sol['c']**2 - 4*sol['constant_term']  # Constant part of Delta
    
    # Continue with equivalences, substituting calculated values directly
    solution_content += f"\\(\\Leftrightarrow \\begin{{cases}} \nm \\neq {format_number_enhanced(m_excluded)} \\\\\n{sol['b']**2}m^2 + {2*sol['b']*sol['c']}m + {delta_const} > 0\n\\end{{cases}}\\)\n\n"
    
    # Calculate discriminant of the quadratic inequality to determine final result
    quad_discriminant = (2*sol['b']*sol['c'])**2 - 4*(sol['b']**2)*delta_const
    
    if quad_discriminant < 0:
        # Quadratic is always positive
        if sol['b']**2 > 0:  # Coefficient of m² is positive
            solution_content += f"\\(\\Leftrightarrow m \\in \\mathbb{{R}} \\setminus \\{{{format_number_enhanced(m_excluded)}\\}}\\)\n\n"
        else:
            solution_content += f"\\(\\Leftrightarrow \\text{{Vô nghiệm}}\\)\n\n"
    elif quad_discriminant == 0:
        # Quadratic has one repeated root
        quad_root = -(2*sol['b']*sol['c'])/(2*sol['b']**2)
        if sol['b']**2 > 0:
            solution_content += f"\\(\\Leftrightarrow m \\in \\mathbb{{R}} \\setminus \\{{{format_number_enhanced(m_excluded)}, {format_number_enhanced(quad_root)}\\}}\\)\n\n"
    else:
        # Quadratic has two distinct roots
        import math
        
        # For quadratic am² + bm + c > 0, the discriminant and roots are:
        # Here we have: (sol['b']²)m² + (2*sol['b']*sol['c'])m + delta_const > 0
        a_coeff = sol['b']**2
        b_coeff = 2*sol['b']*sol['c']
        c_coeff = delta_const
        
        # Calculate discriminant and roots properly
        discriminant = b_coeff**2 - 4*a_coeff*c_coeff
        sqrt_disc = math.sqrt(discriminant)
        
        root1 = (-b_coeff - sqrt_disc) / (2*a_coeff)
        root2 = (-b_coeff + sqrt_disc) / (2*a_coeff)
        
        # Format the roots using the simplified function
        root1_formatted = format_number_enhanced(root1)
        root2_formatted = format_number_enhanced(root2)
        
        if a_coeff > 0:  # Parabola opens upward
            # Final result considering the exclusion
            if m_excluded < min(root1, root2) or m_excluded > max(root1, root2):
                solution_content += f"\\(\\Leftrightarrow m \\in (-\\infty, {root1_formatted}) \\cup ({root2_formatted}, +\\infty) \\setminus \\{{{format_number_enhanced(m_excluded)}\\}}\\)\n\n"
            else:
                solution_content += f"\\(\\Leftrightarrow m \\in (-\\infty, {root1_formatted}) \\cup ({root2_formatted}, +\\infty)\\)\n\n"
    
    # Show the specific excluded value and count correctly
    solution_content += f"Kết quả: Có \\({sol['correct_count']}\\) giá trị nguyên thỏa mãn\n\n"
    
    return solution_content

def generate_single_question(question_number):
    """Sinh một câu hỏi random 1 trong 4 loại, kèm lời giải chi tiết đúng với loại đó."""
    question_type = random.randint(0, 3)
    if question_type == 0:
        data = generate_asymptote_question_1()
        sol = data['solution_data']
        numerator = sol['numerator']
        denominator = sol['denominator']
        question_content = f"Câu {question_number}: "
        func_expr = f"\\frac{{{numerator}}}{{{denominator}}}"
        condition = sol['chosen_statement']
        all_options = sol['all_options']
        correct_index = sol['correct_index']
        question_content += f"Cho hàm số \\(y = {func_expr}\\) có {condition} thì giá trị của biểu thức là:\n\n"
        for j, option in enumerate(all_options):
            marker = '*' if j == correct_index else ''
            question_content += f"{marker}{chr(65+j)}. \\({option}\\)\n\n"
        # Lời giải chi tiết
        question_content += "Lời giải:\n\n"
        question_content += generate_detailed_solution_asymptote_1(sol)
        return clean_negative_signs(question_content)
    elif question_type == 1:
        data = generate_asymptote_question_2()
        sol = data['solution_data']
        numerator = sol['numerator']
        denominator = sol['denominator']
        question_content = f"Câu {question_number}: "
        func_expr = f"\\frac{{{numerator}}}{{{denominator}}}"
        all_options = sol['all_options']
        correct_index = sol['correct_index']
        question_content += f"Cho hàm số \\(y = {func_expr}\\) có đường tiệm cận tạo hình chữ nhật diện tích {sol['S0']}. Tính tổng bình phương của các giá trị \\(m\\):\n\n"
        for j, option in enumerate(all_options):
            marker = '*' if j == correct_index else ''
            question_content += f"{marker}{chr(65+j)}. \\({option}\\)\n\n"
        # Lời giải chi tiết
        question_content += "Lời giải:\n\n"
        question_content += generate_detailed_solution_asymptote_2(sol)
        return clean_negative_signs(question_content)
    elif question_type == 2:
        data = generate_asymptote_question_3()
        sol = data['solution_data']
        question_content = f"Câu {question_number}: "
        func_expr = sol['formula']
        all_options = sol['all_options']
        correct_index = sol['correct_index']
        question_content += f"Số giá trị nguyên \\(m\\) trong \\([-10; 10]\\) để hàm số \\(y = {func_expr}\\) có {sol['chosen_option']}:\n\n"
        for j, option in enumerate(all_options):
            marker = '*' if j == correct_index else ''
            question_content += f"{marker}{chr(65+j)}. {option}\n\n"
        # Lời giải chi tiết
        question_content += "Lời giải:\n\n"
        question_content += generate_detailed_solution_asymptote_3(sol)
        return clean_negative_signs(question_content)
    else:
        data = generate_oblique_asymptote_question()
        sol = data['solution_data']
        question_content = f"Câu {question_number}: "
        func_expr = f"\\frac{{{sol['num_str']}}}{{{sol['denom_str']}}}"
        all_options = sol['all_options']
        correct_index = sol['correct_index']
        question_content += f"Cho hàm số \\(y = {func_expr}\\). Phương trình đường tiệm cận xiên của đồ thị hàm số này là:\n\n"
        for j, option in enumerate(all_options):
            marker = '*' if j == correct_index else ''
            question_content += f"{marker}{chr(65+j)}. \\({option}\\)\n\n"
        # Lời giải chi tiết chỉ cho loại oblique
        question_content += "Lời giải:\n\n"
        question_content += generate_detailed_solution_oblique(sol['A'], sol['B'], sol['C'], sol['D'], sol['E'], sol['slope'], sol['intercept'])
        question_content += "\n\n"
        return clean_negative_signs(question_content)

def generate_all_questions(num_questions=5):
    """Sinh num_questions câu hỏi, mỗi câu là 1 ý random, có lời giải chi tiết."""
    questions = []
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
        num_questions = 5  # Default
        
        if len(sys.argv) > 1:
            try:
                num_questions = int(sys.argv[1])
            except ValueError:
                print("Lỗi: Tham số đầu tiên phải là số nguyên. Sử dụng mặc định 5 câu.")
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