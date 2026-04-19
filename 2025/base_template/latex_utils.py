"""
Các hàm tiện ích LaTeX cho hệ thống sinh câu hỏi toán tối ưu hóa
Tổ chức theo 10 nhóm vấn đề chính từ latex_formatting_issues.md

NHÓM 1: Dạng số học và hệ số (format_number_clean, format_coefficient_*)
NHÓM 2: Dấu và biểu thức đại số (simplify_signs, clean_latex_expression)  
NHÓM 3: Phân số và căn bậc hai (format_fraction_*, format_sqrt_*)
NHÓM 4: Biểu thức đa thức (format_polynomial_*, collect_like_terms)
NHÓM 5: Dấu ngoặc (remove_redundant_parentheses, auto_parentheses)
NHÓM 6: Ký hiệu đặc biệt (format_powers, format_derivatives, format_percent_money)
NHÓM 7: Khoảng, tập hợp, logic (format_interval_*, format_set_*, format_logic_*)
NHÓM 8: Biểu thức LaTeX tổng quát (standardize_latex_symbols, clean_whitespace)
NHÓM 9: Trường hợp đặc biệt (format_decimal_to_fraction, unify_notation)
NHÓM 10: Kiểm tra và sửa lỗi LaTeX (validate_latex, fix_latex_syntax)
"""
import math
import re
from fractions import Fraction
from typing import Union, List, Tuple
import sympy
from sympy import simplify, sympify, latex as sympy_latex, collect, expand, factor
from sympy.parsing.latex import parse_latex


# ██████████████████████████████████████████████████████████████████████████████████
# ███████████████████████ NHÓM 3: PHÂN SỐ VÀ CĂN BẬC HAI ███████████████████████████
# ██████████████████████████████████████████████████████████████████████████████████

def format_fraction_latex(num, denom):
    """
    Định dạng phân số thành LaTeX.
    
    Args:
        num: Tử số
        denom: Mẫu số
        
    Returns:
        str: Chuỗi LaTeX của phân số đã được tối giản
        
    Examples:
        >>> format_fraction_latex(2, 4)
        '\\frac{1}{2}'
        >>> format_fraction_latex(3, 1)
        '3'
    """
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
    """
    Định dạng hệ số trong đa thức với xử lý dấu và biến.
    
    Args:
        coeff: Hệ số cần định dạng
        is_first: True nếu là hạng tử đầu tiên
        var: Tên biến (mặc định 'x')  
        power: Bậc của biến (mặc định 1)
        
    Returns:
        str: Chuỗi LaTeX của hạng tử đã định dạng
        
    Examples:
        >>> format_coefficient(2, True, 'x', 2)
        '2x^{2}'
        >>> format_coefficient(-1, False, 'y', 1)
        ' - y'
    """
    if coeff == 0:
        return ""
    if isinstance(coeff, Fraction):
        num, denom = coeff.numerator, coeff.denominator
    else:
        num, denom = int(coeff), 1
    if denom == 1:
        coeff_str = str(abs(num)) if abs(num) != 1 or power == 0 else ""
    else:
        coeff_str = f"\\frac{{{abs(num)}}}{{{denom}}}"
    if power == 0:
        var_str = coeff_str if coeff_str else "1"
    elif power == 1:
        var_str = f"{coeff_str}{var}" if coeff_str else var
    else:
        var_str = f"{coeff_str}{var}^{{{power}}}" if coeff_str else f"{var}^{{{power}}}"
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
    """
    Định dạng đa thức từ danh sách hệ số.
    
    Args:
        coeffs: Danh sách hệ số từ bậc cao xuống bậc thấp
        var: Tên biến (mặc định 'x')
        
    Returns:
        str: Chuỗi LaTeX của đa thức đã định dạng
        
    Examples:
        >>> format_polynomial([1, -2, 1], 'x')
        'x^{2} - 2x + 1'
        >>> format_polynomial([0, 0, 3], 'y')
        '3'
    """
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
    return "".join(terms)


def format_number_clean(value, precision=2):
    """
    Định dạng số với độ chính xác tùy chỉnh, loại bỏ số 0 thừa.
    
    Args:
        value: Giá trị số cần định dạng
        precision: Số chữ số thập phân (mặc định 2)
        
    Returns:
        str: Chuỗi số đã được làm sạch
        
    Examples:
        >>> format_number_clean(4.0)
        '4'
        >>> format_number_clean(3.50)
        '3,5'
    """
    try:
        fval = float(value)
        if abs(fval - round(fval)) < 1e-10:
            return str(int(round(fval)))
        else:
            formatted = f"{fval:.{precision}f}"
            while formatted.endswith('0') and '.' in formatted:
                formatted = formatted[:-1]
            if formatted.endswith('.'):
                formatted = formatted[:-1]
            if '.' in formatted:
                formatted = formatted.replace('.', '{,}')
            return formatted
    except Exception:
        return str(value)


def format_coord_solution(coord):
    """
    Định dạng tọa độ nghiệm dưới dạng phân số hoặc số thập phân.
    
    Args:
        coord: Tọa độ cần định dạng (Fraction hoặc số)
        
    Returns:
        str: Chuỗi LaTeX của tọa độ với \\dfrac
        
    Examples:
        >>> format_coord_solution(Fraction(3, 2))
        '\\dfrac{3}{2}'
        >>> format_coord_solution(2.5)
        '2,5'
    """
    if isinstance(coord, Fraction):
        if coord.denominator == 1:
            return str(coord.numerator)
        else:
            return f"\\dfrac{{{coord.numerator}}}{{{coord.denominator}}}"
    return format_number_clean(coord, precision=10).replace('\\frac', '\\dfrac')


def format_scientific(num: float, precision: int = 3) -> str:
    """
    Định dạng số dưới dạng khoa học (scientific notation).
    
    Args:
        num: Số cần định dạng
        precision: Số chữ số thập phân (mặc định 3)
        
    Returns:
        str: Chuỗi LaTeX dạng khoa học a \\times 10^{b}
        
    Examples:
        >>> format_scientific(1250.0)
        '1.250 \\times 10^{3}'
        >>> format_scientific(0.00456)
        '4.560 \\times 10^{-3}'
    """
    if abs(num) < 1e-10:
        return "0"
    exponent = int(math.floor(math.log10(abs(num))))
    mantissa = num / (10 ** exponent)
    if exponent == 0:
        return f"{mantissa:.{precision}f}".rstrip('0').rstrip('.')
    else:
        return f"{mantissa:.{precision}f} \\times 10^{{{exponent}}}"


def format_sqrt(number: Union[int, float]) -> str:
    """
    Định dạng căn bậc hai thành LaTeX với tối ưu hóa hiển thị.
    Tự động rút gọn thành dạng a√b nếu có thể.
    
    Args:
        number: Số dưới dấu căn
        
    Returns:
        str: Chuỗi LaTeX của căn bậc hai đã tối ưu
        
    Examples:
        >>> format_sqrt(4)
        '2'
        >>> format_sqrt(12)
        '2\\sqrt{3}'
        >>> format_sqrt(8)
        '2\\sqrt{2}'
    """
    if number == int(number) and int(number) >= 0:
        sqrt_val = math.sqrt(number)
        if sqrt_val == int(sqrt_val):
            return f"{int(sqrt_val)}"
        else:
            # Kiểm tra xem có thể viết dưới dạng a*sqrt(b) không
            for a in range(1, int(sqrt_val) + 1):
                b = number / (a * a)
                if abs(b - round(b)) < 1e-10 and b > 0:
                    b_int = int(round(b))
                    if b_int == 1:
                        return f"{a}"
                    else:
                        return f"{a}\\sqrt{{{b_int}}}"
            # Nếu không thể viết dưới dạng a*sqrt(b), trả về sqrt(number)
            return f"\\sqrt{{{int(number)}}}"
    else:
        # Với số thực, thử tìm dạng a*sqrt(b)
        sqrt_val = math.sqrt(number)
        for a in range(1, int(sqrt_val) + 1):
            b = number / (a * a)
            if abs(b - round(b)) < 1e-10 and b > 0:
                b_int = int(round(b))
                if b_int == 1:
                    return f"{a}"
                else:
                    return f"{a}\\sqrt{{{b_int}}}"
        # Nếu không thể, trả về sqrt(number) với số làm tròn
        return f"\\sqrt{{{format_number_clean(number)}}}"


def format_sqrt_improved(number: Union[int, float]) -> str:
    """
    Phiên bản cải tiến của format_sqrt với xử lý đặc biệt cho các trường hợp phức tạp.
    
    Args:
        number: Số dưới dấu căn
        
    Returns:
        str: Chuỗi LaTeX của căn bậc hai đã tối ưu
        
    Examples:
        >>> format_sqrt_improved(18)
        '3\\sqrt{2}'
        >>> format_sqrt_improved(50)
        '5\\sqrt{2}'
    """
    if number == int(number) and int(number) >= 0:
        sqrt_val = math.sqrt(number)
        if sqrt_val == int(sqrt_val):
            return f"{int(sqrt_val)}"
        else:
            # Kiểm tra xem có thể viết dưới dạng a*sqrt(b) không
            for a in range(1, int(sqrt_val) + 1):
                b = number / (a * a)
                if abs(b - round(b)) < 1e-10 and b > 0:
                    b_int = int(round(b))
                    if b_int == 1:
                        return f"{a}"
                    else:
                        return f"{a}\\sqrt{{{b_int}}}"
            # Nếu không thể viết dưới dạng a*sqrt(b), trả về sqrt(number)
            return f"\\sqrt{{{int(number)}}}"
    else:
        # Với số thực, thử tìm dạng a*sqrt(b)
        sqrt_val = math.sqrt(number)
        for a in range(1, int(sqrt_val) + 1):
            b = number / (a * a)
            if abs(b - round(b)) < 1e-10 and b > 0:
                b_int = int(round(b))
                if b_int == 1:
                    return f"{a}"
                else:
                    return f"{a}\\sqrt{{{b_int}}}"
        # Nếu không thể, trả về sqrt(number) với số làm tròn
        return f"\\sqrt{{{format_number_clean(number)}}}"


def format_dimension(value: float, unit: str = "mét") -> str:
    """
    Định dạng giá trị kích thước với đơn vị.
    
    Args:
        value: Giá trị số
        unit: Đơn vị đo lường (mặc định "mét")
        
    Returns:
        str: Chuỗi kích thước đã định dạng
        
    Examples:
        >>> format_dimension(5.0, "km")
        '5 km'
        >>> format_dimension(3.14, "cm")
        '3.1 cm'
    """
    if abs(value - round(value)) < 1e-10:
        return f"{int(round(value))} {unit}"
    else:
        formatted = f"{value:.1f}"
        if formatted.endswith('.0'):
            formatted = formatted[:-2]
        return f"{formatted} {unit}"


def strip_latex_inline_math(ans: str) -> str:
    """
    Loại bỏ ký hiệu toán học inline khỏi chuỗi LaTeX.
    
    Args:
        ans: Chuỗi có thể chứa \\(...\\) hoặc $...$
        
    Returns:
        str: Chuỗi đã loại bỏ ký hiệu inline math
        
    Examples:
        >>> strip_latex_inline_math("\\(x^2\\)")
        'x^2'
        >>> strip_latex_inline_math("$y + 1$")
        'y + 1'
    """
    if ans.startswith("\\(") and ans.endswith("\\)"):
        return ans[2:-2].strip()
    if ans.startswith("$") and ans.endswith("$"):
        return ans[1:-1].strip()
    return ans


def format_dfrac(num, denom):
    """
    Định dạng phân số sử dụng \\dfrac để hiển thị đẹp hơn.
    
    Args:
        num: Tử số
        denom: Mẫu số
        
    Returns:
        str: Chuỗi LaTeX với \\dfrac thay vì \\frac
        
    Examples:
        >>> format_dfrac(3, 4)
        '\\dfrac{3}{4}'
        >>> format_dfrac(5, 1)
        '5'
    """
    if denom == 0:
        return "undefined"
    frac = Fraction(num, denom)
    if frac.denominator == 1:
        return str(frac.numerator)
    elif frac.numerator == 0:
        return "0"
    else:
        return f"\\dfrac{{{frac.numerator}}}{{{frac.denominator}}}"


def format_money(value, unit="triệu đồng"):
    """
    Định dạng giá trị tiền tệ một cách sạch sẽ.
    
    Args:
        value: Giá trị tiền
        unit: Đơn vị tiền tệ (mặc định "triệu đồng")
        
    Returns:
        str: Chuỗi tiền tệ đã định dạng
        
    Examples:
        >>> format_money(100)
        '100 triệu đồng'
        >>> format_money(50.5, "nghìn USD")
        '50,5 nghìn USD'
    """
    return f"{format_number_clean(value)} {unit}"


def format_percentage(value):
    """
    Định dạng giá trị phần trăm.
    
    Args:
        value: Giá trị thập phân (0.5 = 50%)
        
    Returns:
        str: Chuỗi phần trăm với ký hiệu \\%
        
    Examples:
        >>> format_percentage(0.25)
        '25\\%'
        >>> format_percentage(1.5)
        '150\\%'
    """
    return f"{format_number_clean(value * 100)}\\%"


def format_function_notation(func_name, var, expression):
    """
    Định dạng ký hiệu hàm số như f(x) = biểu_thức.
    
    Args:
        func_name: Tên hàm
        var: Biến
        expression: Biểu thức của hàm
        
    Returns:
        str: Chuỗi ký hiệu hàm đã định dạng
        
    Examples:
        >>> format_function_notation('f', 'x', 'x^2 + 1')
        'f(x) = x^2 + 1'
    """
    return f"{func_name}({var}) = {expression}"


def clean_latex_expression(expression: str) -> str:
    """
    Làm sạch biểu thức LaTeX:
    - Chuyển +- thành -
    - Loại bỏ khoảng trắng thừa
    - Đơn giản hóa các ký hiệu
    - Tối ưu hiển thị
    """
    if not expression:
        return "0"

    # Chuyển +- thành -
    expression = expression.replace("+ -", "- ")
    expression = expression.replace("+-", "-")

    # Loại bỏ khoảng trắng thừa
    expression = re.sub(r'\s+', ' ', expression.strip())

    # Đơn giản hóa các trường hợp đặc biệt
    expression = re.sub(r'\+ 0(?:\s|$)', '', expression)  # Loại bỏ +0
    expression = re.sub(r'- 0(?:\s|$)', '', expression)  # Loại bỏ -0
    expression = re.sub(r'^\+ ', '', expression)  # Loại bỏ dấu + ở đầu
    expression = re.sub(r'\b1\.0+\b', '1', expression)  # 1.000... -> 1
    expression = re.sub(r'\b0\.0+\b', '0', expression)  # 0.000... -> 0

    # Cải thiện hiển thị hệ số 1 và -1
    expression = re.sub(r'\b1x\b', 'x', expression)  # 1x -> x
    expression = re.sub(r'\b1([a-zA-Z])\b', r'\1', expression)  # 1y -> y
    expression = re.sub(r'- 1x\b', '- x', expression)  # -1x -> -x
    expression = re.sub(r'- 1([a-zA-Z])\b', r'- \1', expression)  # -1y -> -y

    # Loại bỏ khoảng trắng thừa sau khi xử lý
    expression = re.sub(r'\s+', ' ', expression.strip())

    # Nếu biểu thức rỗng hoặc chỉ có khoảng trắng, trả về 0
    if not expression or expression.isspace():
        return "0"

    return expression


def simplify_signs(expression: str) -> str:
    """
    Đơn giản hóa dấu trong biểu thức LaTeX.
    Xử lý các trường hợp: ++, --, +-, -+ và dấu ở đầu.
    
    Args:
        expression: Biểu thức LaTeX cần xử lý
        
    Returns:
        str: Biểu thức đã đơn giản hóa dấu
        
    Examples:
        >>> simplify_signs("x + -y")
        'x - y'
        >>> simplify_signs("--z")
        '+z'
    """
    # Xử lý nhiều dấu liên tiếp
    expression = re.sub(r'\+\s*-', '-', expression)
    expression = re.sub(r'-\s*-', '+', expression)
    expression = re.sub(r'\+\s*\+', '+', expression)

    # Xử lý dấu ở đầu biểu thức
    expression = re.sub(r'^\+\s*', '', expression)

    return expression


def format_coefficient_improved(coeff, is_first=False, var='x', power=1):
    """
    Phiên bản cải tiến của format_coefficient với xử lý tốt hơn cho dấu và hệ số.
    Hỗ trợ Fraction và số thập phân chính xác hơn.
    
    Args:
        coeff: Hệ số (int, float, hoặc Fraction)
        is_first: True nếu là hạng tử đầu tiên
        var: Tên biến (mặc định 'x')
        power: Bậc của biến (mặc định 1)
        
    Returns:
        str: Chuỗi LaTeX của hạng tử đã cải tiến
        
    Examples:
        >>> format_coefficient_improved(Fraction(3, 2), True, 'x', 2)
        '\\frac{3}{2}x^{2}'
        >>> format_coefficient_improved(-0.5, False, 'y', 1)
        ' - \\frac{1}{2}y'
    """
    if coeff == 0:
        return ""

    # Xử lý Fraction
    if isinstance(coeff, Fraction):
        num, denom = coeff.numerator, coeff.denominator
    else:
        try:
            float_coeff = float(coeff)
            if abs(float_coeff - round(float_coeff)) < 1e-10:
                num, denom = int(round(float_coeff)), 1
            else:
                # Chuyển đổi số thực thành phân số để xử lý chính xác
                frac = Fraction(float_coeff).limit_denominator(1000)
                num, denom = frac.numerator, frac.denominator
        except:
            num, denom = int(coeff), 1

    # Xác định dấu
    is_negative = num < 0
    abs_num = abs(num)

    # Tạo chuỗi hệ số
    if denom == 1:
        if power == 0:
            coeff_str = str(abs_num)
        elif abs_num == 1:
            coeff_str = ""
        else:
            coeff_str = str(abs_num)
    else:
        coeff_str = f"\\frac{{{abs_num}}}{{{denom}}}"

    # Tạo chuỗi biến
    if power == 0:
        var_str = coeff_str if coeff_str else "1"
    elif power == 1:
        var_str = f"{coeff_str}{var}" if coeff_str else var
    else:
        var_str = f"{coeff_str}{var}^{{{power}}}" if coeff_str else f"{var}^{{{power}}}"

    # Xử lý dấu
    if is_first:
        return f"-{var_str}" if is_negative else var_str
    else:
        return f" - {var_str}" if is_negative else f" + {var_str}"


def format_polynomial_clean(coeffs, var='x'):
    """
    Định dạng đa thức với làm sạch biểu thức tốt hơn.
    Sử dụng format_coefficient_improved và clean_latex_expression.
    
    Args:
        coeffs: Danh sách hệ số từ bậc cao xuống bậc thấp
        var: Tên biến (mặc định 'x')
        
    Returns:
        str: Chuỗi LaTeX của đa thức đã làm sạch
        
    Examples:
        >>> format_polynomial_clean([1, 0, -1], 'x')
        'x^{2} - 1'
        >>> format_polynomial_clean([0, 2, 0], 'y')
        '2y'
    """
    if not coeffs or all(c == 0 for c in coeffs):
        return "0"

    terms = []
    degree = len(coeffs) - 1

    for i, coeff in enumerate(coeffs):
        if coeff == 0:
            continue
        power = degree - i
        term = format_coefficient_improved(coeff, len(terms) == 0, var, power)
        if term:
            terms.append(term)

    if not terms:
        return "0"

    result = "".join(terms)
    return clean_latex_expression(result)


def optimize_latex_fractions(expression: str) -> str:
    """
    Tối ưu hóa phân số trong biểu thức LaTeX.
    Chuyển \\frac thành \\dfrac và đơn giản hóa các trường hợp đặc biệt.
    
    Args:
        expression: Biểu thức LaTeX chứa phân số
        
    Returns:
        str: Biểu thức đã tối ưu phân số
        
    Examples:
        >>> optimize_latex_fractions("\\frac{x}{1}")
        'x'
        >>> optimize_latex_fractions("\\frac{0}{y}")
        '0'
    """
    # Thay thế \\frac thành \\dfrac cho hiển thị ��ẹp hơn
    expression = expression.replace('\\frac', '\\dfrac')

    # Đơn giản hóa phân số có mẫu số 1
    expression = re.sub(r'\\d?frac\{([^}]+)\}\{1\}', r'\1', expression)

    # Đơn giản hóa phân số 0/anything
    expression = re.sub(r'\\d?frac\{0\}\{[^}]+\}', '0', expression)

    return expression


def format_decimal_to_fraction(decimal_value, max_denominator=100):
    """
    Chuyển đổi số thập phân thành phân số LaTeX nếu có thể.
    
    Args:
        decimal_value: Số thập phân cần chuyển đổi
        max_denominator: Mẫu số tối đa cho phép (mặc định 100)
        
    Returns:
        str: Chuỗi LaTeX phân số hoặc số thập phân gốc
        
    Examples:
        >>> format_decimal_to_fraction(0.5)
        '\\dfrac{1}{2}'
        >>> format_decimal_to_fraction(0.333, 10)
        '\\dfrac{1}{3}'
        >>> format_decimal_to_fraction(0.123456)
        '0,123456'
    """
    try:
        frac = Fraction(decimal_value).limit_denominator(max_denominator)
        if frac.denominator == 1:
            return str(frac.numerator)
        elif abs(float(frac) - decimal_value) < 1e-10:
            return f"\\dfrac{{{frac.numerator}}}{{{frac.denominator}}}"
        else:
            return format_number_clean(decimal_value)
    except:
        return format_number_clean(decimal_value)


def remove_redundant_parentheses(expression: str) -> str:
    """
    Loại bỏ dấu ngoặc thừa trong biểu thức LaTeX
    """
    # Loại bỏ ngoặc quanh số đơn lẻ
    expression = re.sub(r'\(([+-]?\d+(?:\.\d+)?)\)', r'\1', expression)

    # Loại bỏ ngoặc quanh biến đơn lẻ
    expression = re.sub(r'\(([a-zA-Z])\)', r'\1', expression)

    return expression


def clean_and_optimize_latex(expression: str) -> str:
    """
    Hàm tổng hợp để làm sạch và tối ưu biểu thức LaTeX
    Áp dụng tất cả các quy tắc làm sạch
    """
    if not expression:
        return "0"

    # Bước 1: Làm sạch cơ bản
    result = clean_latex_expression(expression)

    # Bước 2: Đơn giản hóa dấu
    result = simplify_signs(result)

    # Bước 3: Tối ưu phân số
    result = optimize_latex_fractions(result)

    # Bước 4: Loại bỏ ngoặc thừa
    result = remove_redundant_parentheses(result)

    # Bước 5: Làm sạch lần cuối
    result = clean_latex_expression(result)

    return result


def format_expression_with_variable(expression: str, var: str = 'x') -> str:
    """
    Format biểu thức với biến cụ thể và làm sạch
    """
    if not expression:
        return "0"

    # Thay thế biến nếu cần
    if var != 'x':
        expression = expression.replace('x', var)

    return clean_and_optimize_latex(expression)


def compare_expressions(expr1: str, expr2: str) -> bool:
    """
    So sánh hai biểu thức LaTeX sau khi làm sạch
    """
    clean1 = clean_and_optimize_latex(expr1)
    clean2 = clean_and_optimize_latex(expr2)
    return clean1 == clean2


def format_quadratic_clean(a, b, c, var='x'):
    """
    Format phương trình bậc 2 với làm sạch tối ưu
    """
    coeffs = [a, b, c]
    result = format_polynomial_clean(coeffs, var)
    return clean_and_optimize_latex(result)


def format_equation_clean(left_side: str, right_side: str = "0") -> str:
    """
    Format phương trình với vế trái và vế phải
    """
    left_clean = clean_and_optimize_latex(left_side)
    right_clean = clean_and_optimize_latex(right_side)

    # Nếu vế phải là 0, không cần hiển thị
    if right_clean == "0":
        return f"{left_clean} = 0"
    else:
        return f"{left_clean} = {right_clean}"


def format_interval_notation(a, b, include_a=True, include_b=True):
    """
    Format khoảng trong LaTeX
    """
    left_bracket = "[" if include_a else "("
    right_bracket = "]" if include_b else ")"

    a_str = format_decimal_to_fraction(a) if isinstance(a, (int, float)) else str(a)
    b_str = format_decimal_to_fraction(b) if isinstance(b, (int, float)) else str(b)

    return f"{left_bracket}{a_str}; {b_str}{right_bracket}"


def format_derivative_notation(func_expr: str, var: str = 'x', order: int = 1) -> str:
    """
    Format ký hiệu đạo hàm
    """
    clean_expr = clean_and_optimize_latex(func_expr)

    if order == 1:
        return f"f'({var}) = {clean_expr}"
    elif order == 2:
        return f"f''({var}) = {clean_expr}"
    else:
        return f"f^{{({order})}}({var}) = {clean_expr}"


# ██████████████████████████████████████████████████████████████████████████████████
# ███████████████████████ NHÓM 1: DẠNG SỐ HỌC VÀ HỆ SỐ ███████████████████████████
# ██████████████████████████████████████████████████████████████████████████████████

# ==========================================
# NHÓM 1: DẠNG SỐ HỌC VÀ HỆ SỐ  
# ==========================================

def normalize_decimal_numbers(expression: str) -> str:
    """
    Chuyển số thực thành số nguyên nếu có thể: 4.0 -> 4, 1.000 -> 1.
    Loại bỏ phần thập phân .0 không cần thiết.
    
    Args:
        expression: Biểu thức chứa số thập phân
        
    Returns:
        str: Biểu thức đã chuẩn hóa số
        
    Examples:
        >>> normalize_decimal_numbers("4.0 + 3.000")
        '4 + 3'
        >>> normalize_decimal_numbers("2.5 + 1.0")
        '2.5 + 1'
    """
    expression = re.sub(r'\b(\d+)\.0+\b', r'\1', expression)
    return expression

def format_zero_coefficients(expression: str) -> str:
    """
    Loại bỏ các hạng tử có hệ số 0 trong biểu thức.
    Xử lý các trường hợp: 0x, 0y^2, +0z, -0w.
    
    Args:
        expression: Biểu thức chứa hạng tử có hệ số 0
        
    Returns:
        str: Biểu thức đã loại bỏ hạng tử 0
        
    Examples:
        >>> format_zero_coefficients("2x + 0y + 3z")
        '2x +  + 3z'
        >>> format_zero_coefficients("x^2 + 0x + 1")
        'x^2 +  + 1'
    """
    # Loại bỏ 0x, 0y, 0*anything
    expression = re.sub(r'\b0\s*[a-zA-Z]+(?:\^\{?\d+\}?)?', '', expression)
    expression = re.sub(r'[+\-]\s*0\s*[a-zA-Z]+(?:\^\{?\d+\}?)?', '', expression)
    return expression


# ██████████████████████████████████████████████████████████████████████████████████
# ███████████████████████ NHÓM 2: DẤU VÀ BIỂU THỨC ĐẠI SỐ ███████████████████████
# ██████████████████████████████████████████████████████████████████████████████████

# ==========================================
# NHÓM 2: DẤU VÀ BIỂU THỨC ĐẠI SỐ
# ==========================================

def fix_consecutive_signs(expression: str) -> str:
    """
    Sửa các dấu liên tiếp: ++, --, +-, -+.
    Áp dụng quy tắc toán học chuẩn cho phép toán dấu.
    
    Args:
        expression: Biểu thức chứa dấu liên tiếp
        
    Returns:
        str: Biểu thức đã sửa dấu
        
    Examples:
        >>> fix_consecutive_signs("x + +y")
        'x + y'
        >>> fix_consecutive_signs("a - -b")
        'a + b'
        >>> fix_consecutive_signs("c + -d")
        'c - d'
    """
    expression = re.sub(r'\+\s*\+', '+', expression)
    expression = re.sub(r'-\s*-', '+', expression)
    expression = re.sub(r'\+\s*-', '-', expression)
    expression = re.sub(r'-\s*\+', '-', expression)
    return expression

def remove_leading_plus(expression: str) -> str:
    """
    Loại bỏ dấu + ở đầu biểu thức.
    + 2x -> 2x, nhưng giữ nguyên dấu - ở đầu.
    
    Args:
        expression: Biểu thức có thể có dấu + đầu
        
    Returns:
        str: Biểu thức đã loại bỏ dấu + đầu
        
    Examples:
        >>> remove_leading_plus("+ 2x - y")
        '2x - y'
        >>> remove_leading_plus("- 3z + w")
        '- 3z + w'
    """
    return re.sub(r'^\+\s*', '', expression.strip())


# ██████████████████████████████████████████████████████████████████████████████████
# ███████████████████████ NHÓM 4: BIỂU THỨC ĐA THỨC ███████████████████████████████
# ██████████████████████████████████████████████████████████████████████████████████

# ==========================================
# NHÓM 3: PHÂN SỐ VÀ CĂN BẬC HAI (Đã có sẵn)
# ==========================================

# ==========================================
# NHÓM 4: BIỂU THỨC ĐA THỨC
# ==========================================

def collect_like_terms_manual(expression: str) -> str:
    """
    Thu gọn các hạng tử đồng dạng bằng regex đơn giản.
    Ví dụ: x^2 + x^2 -> 2x^2 (cần sympy để xử lý chính xác).
    
    Args:
        expression: Biểu thức chứa hạng tử đồng dạng
        
    Returns:
        str: Biểu thức đã thu gọn (hiện tại trả về nguyên bản)
        
    Note:
        Hàm này cần sympy để thực hiện chính xác.
    """
    # Ví dụ: x^2 + x^2 -> 2x^2 (cần sympy để xử lý chính xác)
    return expression

def sort_polynomial_terms(expression: str) -> str:
    """
    Sắp xếp các hạng tử theo bậc giảm dần.
    x + x^2 -> x^2 + x.
    
    Args:
        expression: Biểu thức đa thức
        
    Returns:
        str: Đa thức đã sắp xếp (hiện tại trả về nguyên bản)
        
    Note:
        Hàm này cần sympy để thực hiện chính xác.
    """
    # Cần sympy để xử lý chính xác
    return expression


# ██████████████████████████████████████████████████████████████████████████████████
# ███████████████████████ NHÓM 5: DẤU NGOẶC ███████████████████████████████████████
# ██████████████████████████████████████████████████████████████████████████████████

# ==========================================
# NHÓM 5: DẤU NGOẶC
# ==========================================

def auto_parentheses_for_fractions(expression: str) -> str:
    """
    Tự động thêm \\left( \\right) cho phân số phức tạp.
    Chuyển ( \\frac{a}{b} ) thành \\left( \\frac{a}{b} \\right).
    
    Args:
        expression: Biểu thức chứa phân số trong ngoặc
        
    Returns:
        str: Biểu thức với ngoặc tự động điều chỉnh kích thước
        
    Examples:
        >>> auto_parentheses_for_fractions("( \\dfrac{1}{2} )")
        '\\left(\\dfrac{1}{2}\\right)'
    """
    # Thay thế ( frac ) thành \\left( frac \\right)
    pattern = r'\(\s*(\\d?frac\{[^}]+\}\{[^}]+\})\s*\)'
    replacement = r'\\left(\1\\right)'
    return re.sub(pattern, replacement, expression)


# ██████████████████████████████████████████████████████████████████████████████████
# ███████████████████████ NHÓM 6: KÝ HIỆU ĐẶC BIỆT ███████████████████████████████
# ██████████████████████████████████████████████████████████████████████████████████

# ==========================================
# NHÓM 6: KÝ HIỆU ĐẶC BIỆT VÀ CHUẨN HÓA
# ==========================================

def format_powers_clean(expression: str) -> str:
    """
    Làm sạch lũy thừa: x^1 -> x, x^0 -> 1.
    Loại bỏ các lũy thừa không cần thiết trong biểu thức.
    
    Args:
        expression: Biểu thức chứa lũy thừa
        
    Returns:
        str: Biểu thức đã làm sạch lũy thừa
        
    Examples:
        >>> format_powers_clean("x^1 + y^0")
        'x + 1'
        >>> format_powers_clean("z^{1} * w^{0}")
        'z * 1'
    """
    expression = re.sub(r'([a-zA-Z])\^\{?1\}?(?![0-9])', r'\1', expression)
    expression = re.sub(r'([a-zA-Z])\^\{?0\}?', '1', expression)
    return expression

def standardize_function_notation(expression: str) -> str:
    """
    Chuẩn hóa ký hiệu hàm số.
    f(x)=... -> f(x) = ... (thêm khoảng trắng quanh dấu =).
    
    Args:
        expression: Biểu thức chứa ký hiệu hàm
        
    Returns:
        str: Biểu thức với ký hiệu hàm đã chuẩn hóa
        
    Examples:
        >>> standardize_function_notation("f(x)=x^2")
        'f(x) = x^2'
        >>> standardize_function_notation("g(t)=2t+1")
        'g(t) = 2t+1'
    """
    # f(x)=... -> f(x) = ...
    expression = re.sub(r'([a-zA-Z]+\([^)]+\))\s*=\s*', r'\1 = ', expression)
    return expression


# ██████████████████████████████████████████████████████████████████████████████████
# ███████████████████████ NHÓM 7: KHOẢNG, TẬP HỢP, LOGIC ███████████████████████████
# ██████████████████████████████████████████████████████████████████████████████████

# ==========================================
# NHÓM 7: KHOẢNG, TẬP HỢP, LOGIC
# ==========================================

def format_logic_symbols(expression: str) -> str:
    """Chuẩn hóa các ký hiệu logic trong LaTeX: and/or -> \\land/\\lor"""
    expression = re.sub(r'\\band\\b', r'\\\\land', expression)
    expression = re.sub(r'\\bor\\b', r'\\\\lor', expression)
    return expression

def format_set_notation(expression: str) -> str:
    """Chuẩn hóa ký hiệu tập hợp: {x | x > 0} -> \\{x \\mid x > 0\\}"""
    expression = re.sub(r'\\{([^|]+)\\|([^}]+)\\}', r'\\\\{\\1 \\\\mid \\2\\\\}', expression)
    return expression

def format_interval_notation_clean(expression: str) -> str:
    """Chuẩn hóa ký hiệu khoảng: [a, b] hoặc (a, b) -> [a; b] hoặc (a; b)"""
    expression = re.sub(r'([\\[\\(])\\s*([^,;]+)[,;]\\s*([^\\]\\)]+)([\\]\\)])', r'\\1\\2; \\3\\4', expression)
    return expression


# ██████████████████████████████████████████████████████████████████████████████████
# ███████████████████████ NHÓM 8: BIỂU THỨC LATEX TỔNG QUÁT ███████████████████████
# ██████████████████████████████████████████████████████████████████████████████████

# ==========================================
# NHÓM 8: BIỂU THỨC LATEX TỔNG QUÁT
# ==========================================

def standardize_latex_symbols(expression: str) -> str:
    """Chuẩn hóa các ký hiệu LaTeX"""
    replacements = {
        '<=': '\\\\leq',
        '>=': '\\\\geq', 
        '!=': '\\\\neq',
        '->': '\\\\to',
        '...': '\\\\dots'
    }
    for old, new in replacements.items():
        expression = expression.replace(old, new)
    return expression

def format_multiplication_symbols(expression: str) -> str:
    """Chuyển * thành \\cdot nếu là phép nhân"""
    # Chỉ thay thế * giữa các số hoặc biến
    expression = re.sub(r'(\\d+|[a-zA-Z])\\s*\\*\\s*(\\d+|[a-zA-Z])', r'\\1 \\\\cdot \\2', expression)
    return expression

def clean_whitespace_latex(expression: str) -> str:
    """Loại bỏ khoảng trắng thừa: x   +   y -> x + y"""
    expression = re.sub(r'\\s+', ' ', expression.strip())
    return expression


# ██████████████████████████████████████████████████████████████████████████████████
# ███████████████████████ NHÓM 9: TRƯỜNG HỢP ĐẶC BIỆT ██████████████████████████████
# ██████████████████████████████████████████████████████████████████████████████████

# ==========================================
# NHÓM 9: TRƯỜNG HỢP ĐẶC BIỆT
# ==========================================

def unify_fraction_notation(expression: str) -> str:
    """Đồng nhất hóa \\frac thành \\dfrac"""
    return expression.replace('\\\\frac', '\\\\dfrac')

def handle_empty_expressions(expression: str) -> str:
    """Xử lý biểu thức rỗng -> 0"""
    if not expression or expression.isspace():
        return "0"
    return expression


# ██████████████████████████████████████████████████████████████████████████████████
# ███████████████████████ NHÓM 10: KIỂM TRA VÀ SỬA LỖI ████████████████████████████
# ██████████████████████████████████████████████████████████████████████████████████

# ==========================================
# NHÓM 10: KIỂM TRA VÀ SỬA LỖI LATEX
# ==========================================

def validate_latex_brackets(expression: str) -> bool:
    """
    Kiểm tra dấu ngoặc có khớp không trong biểu thức LaTeX.
    Xử lý các loại ngoặc: (), [], {}.
    
    Args:
        expression: Biểu thức cần kiểm tra
        
    Returns:
        bool: True nếu tất cả ngoặc đều khớp, False nếu có lỗi
        
    Examples:
        >>> validate_latex_brackets("(x + y)")
        True
        >>> validate_latex_brackets("(x + y")
        False
        >>> validate_latex_brackets("{a[b(c)d]e}")
        True
    """
    brackets = {'(': ')', '[': ']', '{': '}'}
    stack = []
    for char in expression:
        if char in brackets:
            stack.append(char)
        elif char in brackets.values():
            if not stack:
                return False
            if brackets[stack[-1]] != char:
                return False
            stack.pop()
    return len(stack) == 0

def fix_latex_syntax_errors(expression: str) -> str:
    """
    Sửa các lỗi cú pháp LaTeX phổ biến.
    - \\frc -> \\frac
    - x^2 -> x^{2} 
    - x_i -> x_{i}
    
    Args:
        expression: Biểu thức có thể chứa lỗi cú pháp
        
    Returns:
        str: Biểu thức đã sửa lỗi cú pháp
        
    Examples:
        >>> fix_latex_syntax_errors("\\frc{1}{2}")
        '\\frac{1}{2}'
        >>> fix_latex_syntax_errors("x^2 + y_i")
        'x^{2} + y_{i}'
    """
    # Sửa \\frc thành \\frac
    expression = re.sub(r'\\\\frc\\b', r'\\\\frac', expression)
    
    # Thêm {} cho ^
    expression = re.sub(r'\\^([a-zA-Z0-9])', r'^{\\1}', expression)
    
    # Thêm {} cho _
    expression = re.sub(r'\\_([a-zA-Z0-9])', r'_{\\1}', expression)
    
    return expression

def check_latex_command_spelling(expression: str) -> List[str]:
    """
    Kiểm tra chính tả các lệnh LaTeX và trả về danh sách lỗi.
    
    Args:
        expression: Biểu thức cần kiểm tra chính tả
        
    Returns:
        List[str]: Danh sách các lỗi chính tả được tìm thấy
        
    Examples:
        >>> check_latex_command_spelling("\\frc{1}{2} + \\sqt{4}")
        ["Found '\\\\frc\\\\b', should be '\\\\frac'", "Found '\\\\sqt\\\\b', should be '\\\\sqrt'"]
    """
    common_errors = [
        (r'\\\\frc\\b', '\\\\frac'),
        (r'\\\\sqt\\b', '\\\\sqrt'),
        (r'\\\\inf\\b', '\\\\infty'),
    ]
    
    errors_found = []
    for error_pattern, correct in common_errors:
        if re.search(error_pattern, expression):
            errors_found.append(f"Found '{error_pattern}', should be '{correct}'")
    
    return errors_found


# ██████████████████████████████████████████████████████████████████████████████████
# ███████████████████████ SYMPY-BASED FORMATTING FUNCTIONS ████████████████████████
# ██████████████████████████████████████████████████████████████████████████████████

# ==========================================
# SYMPY-BASED FORMATTING FUNCTIONS
# ==========================================

def sympy_simplify_latex(expr_latex: str) -> str:
    """Sử dụng sympy để rút gọn biểu thức LaTeX (phân số, đa thức, căn, ...)"""
    try:
        expr = parse_latex(expr_latex)
        simplified = simplify(expr)
        return sympy_latex(simplified)
    except Exception:
        return expr_latex

def sympy_collect_terms(expr_latex: str, var: str = 'x') -> str:
    """Thu gọn các hạng tử đồng dạng bằng sympy"""
    try:
        expr = parse_latex(expr_latex)
        collected = collect(expr, sympy.Symbol(var))
        return sympy_latex(collected)
    except Exception:
        return expr_latex

def sympy_decimal_to_fraction(expr_latex: str) -> str:
    """Chuyển số thập phân thành phân số bằng sympy"""
    try:
        expr = parse_latex(expr_latex)
        if expr is not None and hasattr(expr, 'is_Float') and expr.is_Float:
            frac = sympy.Rational(expr).limit_denominator(100)
            return sympy_latex(frac)
        return sympy_latex(expr)
    except Exception:
        return expr_latex

def sympy_sort_polynomial(expr_latex: str, var: str = 'x') -> str:
    """Sắp xếp đa thức theo bậc giảm dần bằng sympy"""
    try:
        expr = parse_latex(expr_latex)
        expanded = expand(expr)
        return sympy_latex(expanded)
    except Exception:
        return expr_latex

def sympy_check_equiv(expr1_latex: str, expr2_latex: str) -> bool:
    """Kiểm tra hai biểu thức LaTeX có tương đương toán học không"""
    try:
        e1 = simplify(parse_latex(expr1_latex))
        e2 = simplify(parse_latex(expr2_latex))
        return sympy.simplify(e1 - e2) == 0
    except Exception:
        return False

def sympy_clean_latex(expr_latex: str) -> str:
    """Chuẩn hóa, làm sạch và tối ưu biểu thức LaTeX bằng sympy"""
    try:
        expr = parse_latex(expr_latex)
        expr = simplify(expr)
        return sympy_latex(expr)
    except Exception:
        return expr_latex


# ██████████████████████████████████████████████████████████████████████████████████
# ███████████████████████ PIPELINE FUNCTIONS ██████████████████████████████████████
# ██████████████████████████████████████████████████████████████████████████████████

# ==========================================
# PIPELINE FUNCTIONS
# ==========================================

def format_percent_money(expression: str) -> str:
    """Chuẩn hóa phần trăm, tiền tệ: 0.5% -> 50%, 1.000.000 đồng -> 1 triệu đồng"""
    # Phần trăm
    def percent_replacer(match):
        val = float(match.group(1))
        if val < 1:
            return str(val * 100).rstrip('0').rstrip('.') + '\\\\%'
        return match.group(0)
    
    expression = re.sub(r'(\\d*\\.?\\d+)\\\\%', percent_replacer, expression)
    
    # Tiền tệ
    expression = re.sub(r'1\\.000\\.000 ?(đồng|VND)', '1 triệu đồng', expression)
    return expression

def format_latex_pipeline_manual(expression: str) -> str:
    """
    Pipeline làm sạch LaTeX bằng các hàm thủ công (không dùng sympy).
    Áp dụng tuần tự các nhóm xử lý từ 1-10.
    
    Args:
        expression: Biểu thức LaTeX cần làm sạch
        
    Returns:
        str: Biểu thức đã được làm sạch hoàn toàn
        
    Examples:
        >>> format_latex_pipeline_manual("1x^2 + 0x + 1")
        'x^{2} + 1'
        >>> format_latex_pipeline_manual("3 + -2")
        '3 - 2'
    """
    if not expression:
        return "0"
    
    # Áp dụng từng nhóm xử lý
    expr = expression.strip()
    
    # Nhóm 1: Số học và hệ số
    expr = normalize_decimal_numbers(expr)
    expr = format_zero_coefficients(expr)
    
    # Nhóm 2: Dấu và biểu thức đại số
    expr = fix_consecutive_signs(expr)
    expr = remove_leading_plus(expr)
    expr = simplify_signs(expr)
    
    # Nhóm 3: Phân số và căn (dùng hàm có sẵn)
    expr = optimize_latex_fractions(expr)
    
    # Nhóm 4: Đa thức (cần sympy để xử lý chính xác)
    
    # Nhóm 5: Ngoặc
    expr = remove_redundant_parentheses(expr)
    expr = auto_parentheses_for_fractions(expr)
    
    # Nhóm 6: Ký hiệu đặc biệt
    expr = format_powers_clean(expr)
    expr = standardize_function_notation(expr)
    
    # Nhóm 7: Khoảng, tập hợp, logic
    expr = format_logic_symbols(expr)
    expr = format_set_notation(expr)
    expr = format_interval_notation_clean(expr)
    
    # Nhóm 8: LaTeX tổng quát
    expr = standardize_latex_symbols(expr)
    expr = format_multiplication_symbols(expr)
    expr = clean_whitespace_latex(expr)
    
    # Nhóm 9: Trường hợp đặc biệt
    expr = unify_fraction_notation(expr)
    expr = handle_empty_expressions(expr)
    expr = format_percent_money(expr)
    
    # Nhóm 10: Kiểm tra và sửa lỗi
    expr = fix_latex_syntax_errors(expr)
    
    # Làm sạch cuối cùng
    expr = clean_latex_expression(expr)
    
    return expr

def format_latex_pipeline_sympy(expression: str) -> str:
    """
    Pipeline làm sạch LaTeX bằng sympy (ưu tiên sympy).
    Sử dụng sympy để xử lý chính xác, fallback về manual nếu lỗi.
    
    Args:
        expression: Biểu thức LaTeX cần làm sạch
        
    Returns:
        str: Biểu thức đã được xử lý bởi sympy
        
    Examples:
        >>> format_latex_pipeline_sympy("x^2 + x^2")
        '2*x^2'
        >>> format_latex_pipeline_sympy("\\frac{2}{4}")
        '\\frac{1}{2}'
    """
    if not expression:
        return "0"
    
    try:
        # Sử dụng sympy để xử lý chính xác
        expr = sympy_clean_latex(expression)
        
        # Bổ sung các xử lý mà sympy không làm được
        expr = format_percent_money(expr)
        expr = standardize_latex_symbols(expr)
        expr = fix_latex_syntax_errors(expr)
        
        return expr
    except Exception:
        # Fallback về phương pháp thủ công
        return format_latex_pipeline_manual(expression)

def format_latex_pipeline(expression: str, use_sympy: bool = False) -> str:
    """
    Pipeline tổng hợp: chuẩn hóa, làm sạch, tối ưu biểu thức LaTeX.
    
    Args:
        expression: Biểu thức LaTeX cần xử lý
        use_sympy: True để ưu tiên sympy, False để dùng các hàm thủ công
        
    Returns:
        str: Biểu thức LaTeX đã được làm sạch và tối ưu
        
    Examples:
        >>> format_latex_pipeline("1x + 0y", False)
        'x'
        >>> format_latex_pipeline("x^2 + x^2", True) 
        '2*x^2'
    """
    if use_sympy:
        return format_latex_pipeline_sympy(expression)
    else:
        return format_latex_pipeline_manual(expression)
