"""
Các hàm tiện ích LaTeX cho hệ thống sinh câu hỏi toán tối ưu hóa
Tách từ math_template.py - PHẦN 1
"""
import math
from fractions import Fraction
from typing import Union

def format_fraction_latex(num, denom):
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
    if isinstance(coord, Fraction):
        if coord.denominator == 1:
            return str(coord.numerator)
        else:
            return f"\\dfrac{{{coord.numerator}}}{{{coord.denominator}}}"
    return format_number_clean(coord, precision=10).replace('\\frac', '\\dfrac')

def format_scientific(num: float, precision: int = 3) -> str:
    if abs(num) < 1e-10:
        return "0"
    exponent = int(math.floor(math.log10(abs(num))))
    mantissa = num / (10 ** exponent)
    if exponent == 0:
        return f"{mantissa:.{precision}f}".rstrip('0').rstrip('.')
    else:
        return f"{mantissa:.{precision}f} \\times 10^{{{exponent}}}"

def format_sqrt(number: Union[int, float]) -> str:
    """Format căn bậc hai thành LaTeX - cải thiện để hiển thị đẹp hơn"""
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
    """Format căn bậc hai thành LaTeX - phiên bản cải tiến cho các trường hợp đặc biệt"""
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
    if abs(value - round(value)) < 1e-10:
        return f"{int(round(value))} {unit}"
    else:
        formatted = f"{value:.1f}"
        if formatted.endswith('.0'):
            formatted = formatted[:-2]
        return f"{formatted} {unit}"

def strip_latex_inline_math(ans: str) -> str:
    if ans.startswith("\\(") and ans.endswith("\\)"):
        return ans[2:-2].strip()
    if ans.startswith("$") and ans.endswith("$"):
        return ans[1:-1].strip()
    return ans

def format_dfrac(num, denom):
    """Format fraction using dfrac for better display"""
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
    """Format money values cleanly"""
    return f"{format_number_clean(value)} {unit}"

def format_percentage(value):
    """Format percentage values"""
    return f"{format_number_clean(value * 100)}\\%"

def format_function_notation(func_name, var, expression):
    """Format function notation like f(x) = expression"""
    return f"{func_name}({var}) = {expression}"
