"""
Dạng bài toán: Tìm khoảng đồng biến, nghịch biến của hàm số bậc 2 phân thức
"""

import random
import math
import sys
import logging
import re
from abc import ABC, abstractmethod
from fractions import Fraction
from typing import List, Dict, Any, Union, Type

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ███████████████████████████████████████████████████████████████████████████████
# ██           PHẦN 1: CÁC HÀM TIỆN ÍCH VÀ FORMAT LATEX                        ██
# ███████████████████████████████████████████████████████████████████████████████


# ███████████████████████████████████████████████████████████████████████████████
# ██                         HÀM TIỆN ÍCH TOÁN HỌC                             ██
# ███████████████████████████████████████████████████████████████████████████████

def gcd(a, b):
    """Tính ước chung lớn nhất của a và b."""
    while b:
        a, b = b, a % b
    return a


def simplify_fraction(num, denom):
    """Rút gọn phân số bằng cách chia tử số và mẫu số cho ước chung lớn nhất."""
    if denom < 0:
        num, denom = -num, -denom
    if num == 0:
        return 0, 1
    g = gcd(abs(num), abs(denom))
    return num // g, denom // g


def is_perfect_square(n):
    """Kiểm tra xem n có phải là số chính phương hay không."""
    sqrt_n = int(n ** 0.5)
    return sqrt_n * sqrt_n == n


# ███████████████████████████████████████████████████████████████████████████████
# ██                        HÀM FORMAT SỐ VÀ PHÂN SỐ                           ██
# ███████████████████████████████████████████████████████████████████████████████

def format_number_clean(value, precision=2):
    """Format số sạch - cải tiến cho LaTeX Việt Nam"""
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
            # Chỉ thay dấu chấm bằng dấu phẩy khi vẫn còn dấu chấm
            if '.' in formatted:
                formatted = formatted.replace('.', '{,}')
            return formatted
    except Exception:
        return str(value)


def format_latex_number(value, is_left_endpoint=True):
    """Format số cho LaTeX, ưu tiên số nguyên thay vì phân số."""
    if value == float('-inf'):
        return "-\\infty"
    elif value == float('inf'):
        return "+\\infty"
    if isinstance(value, int):
        return str(value)
    elif isinstance(value, (float, Fraction)):
        # Kiểm tra xem có phải số nguyên không
        if abs(value - round(value)) < 1e-10:
            return str(int(round(value)))
        # Nếu không phải số nguyên, vẫn dùng phân số
        frac = Fraction(value).limit_denominator(100)
        num, denom = simplify_fraction(frac.numerator, frac.denominator)
        if denom == 1:
            return str(num)
        return f"\\frac{{{num}}}{{{denom}}}"
    else:
        logging.warning(f"Kiểu giá trị không mong đợi khi format LaTeX: {value}")
        return str(value)


def format_coord_solution(coord):
    """Format tọa độ chuẩn Việt Nam cho lời giải (TỐI ƯU - tái sử dụng format_number_clean)"""
    if isinstance(coord, Fraction):
        num, denom = simplify_fraction(coord.numerator, coord.denominator)
        if denom == 1:
            return str(num)
        else:
            return f"\\dfrac{{{num}}}{{{denom}}}"

    # Tái sử dụng format_number_clean để tránh trùng lặp
    return format_number_clean(coord, precision=10).replace('\\frac', '\\dfrac')


def format_scientific(num: float, precision: int = 3) -> str:
    """Format số khoa học - từ thuc_te_hinh_hoc.py"""
    if abs(num) < 1e-10:
        return "0"

    exponent = int(math.floor(math.log10(abs(num))))
    mantissa = num / (10 ** exponent)

    if exponent == 0:
        return f"{mantissa:.{precision}f}".rstrip('0').rstrip('.')
    else:
        return f"{mantissa:.{precision}f} \\times 10^{{{exponent}}}"


def format_sqrt(number: Union[int, float]) -> str:
    """Format căn bậc hai - từ thuc_te_hinh_hoc.py"""
    if number == int(number) and int(number) >= 0:
        sqrt_val = math.sqrt(number)
        if sqrt_val == int(sqrt_val):
            return f"{int(sqrt_val)}"
        else:
            return f"\\sqrt{{{int(number)}}}"
    else:
        return f"\\sqrt{{{number}}}"


def format_dimension(value: float, unit: str = "mét") -> str:
    """Format kích thước với đơn vị - từ thuc_te_hinh_hoc.py"""
    if abs(value - round(value)) < 1e-10:
        return f"{int(round(value))} {unit}"
    else:
        formatted = f"{value:.1f}"
        if formatted.endswith('.0'):
            formatted = formatted[:-2]
        return f"{formatted} {unit}"


# ███████████████████████████████████████████████████████████████████████████████
# ██                      HÀM FORMAT ĐA THỨC VÀ BIỂU THỨC                     ██
# ███████████████████████████████████████████████████████████████████████████████

def clean_sign_expression(expr: str) -> str:
    """Chuẩn hóa các biểu thức dấu: loại bỏ +0, -0, nhân/chia với 1, -1, 0, dấu cộng/trừ liên tiếp, v.v."""
    # 1 - -2 -> 1 + 2
    expr = re.sub(r"-\s*-\s*([\d\w\\(])", r"+ \1", expr)
    # 1 + -4 -> 1 - 4
    expr = re.sub(r"\+\s*-\s*([\d\w\\(])", r"- \1", expr)
    # 1 + +4 -> 1 + 4
    expr = re.sub(r"\+\s*\+\s*([\d\w\\(])", r"+ \1", expr)
    # 1 - +4 -> 1 - 4
    expr = re.sub(r"-\s*\+\s*([\d\w\\(])", r"- \1", expr)
    # 3 . -4 -> 3 . (-4)
    expr = re.sub(r"(\.|\*|/)\s*-\s*([\d\w\\(])", r"\1 (-\2)", expr)
    # 3 * 1 -> 3, 1 * x -> x
    expr = re.sub(r"([\d\w\\(\)])\s*([\*\.])\s*1(?![\d\w])", r"\1", expr)
    expr = re.sub(r"1\s*([\*\.])\s*([\d\w\\(\)])", r"\2", expr)
    # 3 * -1 -> -3, -1 * x -> -x
    expr = re.sub(r"([\d\w\\(\)])\s*([\*\.])\s*-1(?![\d\w])", r"-\1", expr)
    expr = re.sub(r"-1\s*([\*\.])\s*([\d\w\\(\)])", r"-\2", expr)
    # x / 1 -> x
    expr = re.sub(r"([\d\w\\(\)])\s*/\s*1(?![\d\w])", r"\1", expr)
    # x / -1 -> -x
    expr = re.sub(r"([\d\w\\(\)])\s*/\s*-1(?![\d\w])", r"-\1", expr)
    # x + 0, x - 0 -> x
    expr = re.sub(r"([\d\w\\)\}])\s*([\+\-])\s*0(?![\d\w])", r"\1", expr)
    # 0 + x -> x, 0 - x -> -x
    expr = re.sub(r"0\s*\+\s*([\d\w\\(])", r"\1", expr)
    expr = re.sub(r"0\s*-\s*([\d\w\\(])", r"-\1", expr)
    # x * 0, 0 * x, x . 0, 0 . x -> 0
    expr = re.sub(r"([\d\w\\(\)])\s*([\*\.])\s*0(?![\d\w])", r"0", expr)
    expr = re.sub(r"0\s*([\*\.])\s*([\d\w\\(\)])", r"0", expr)
    # --4 -> 4, ---4 -> -4
    expr = re.sub(r"--([\d\w\\(])", r"\1", expr)
    expr = re.sub(r"---([\d\w\\(])", r"-\1", expr)
    # +4 ở đầu -> 4
    expr = re.sub(r"^\+\s*([\d\w\\(])", r"\1", expr)
    # +-4, -+4 ở đầu -> -4
    expr = re.sub(r"^[\+\-]\+([\d\w\\(])", r"-\1", expr)
    # Dấu chia với số âm: 3 / -4 -> 3 / (-4)
    expr = re.sub(r"/\s*-\s*([\d\w\\(])", r"/ (-\1)", expr)
    # Loại bỏ dấu + ở đầu nếu có
    expr = re.sub(r"^\+", r"", expr)
    # Loại bỏ khoảng trắng thừa
    expr = re.sub(r"\s+", " ", expr).strip()
    return expr


def format_coefficient(coeff, is_first=False, var='x', power=1):
    """Format hệ số với dấu và biến (TỐI ƯU - tái sử dụng simplify_fraction)"""
    if coeff == 0:
        return ""

    # Tái sử dụng simplify_fraction cho Fraction coefficients
    if isinstance(coeff, Fraction):
        num, denom = simplify_fraction(coeff.numerator, coeff.denominator)
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
        var_str = f"{coeff_str}{var}" if coeff_str else var
    else:
        var_str = f"{coeff_str}{var}^{{{power}}}" if coeff_str else f"{var}^{{{power}}}"

    # Handle signs
    if is_first:
        result = f"-{var_str}" if num < 0 else var_str
    else:
        result = f" - {var_str}" if num < 0 else f" + {var_str}"
    # Chuẩn hóa biểu thức dấu
    return clean_sign_expression(result)


def format_polynomial(coeffs, var='x'):
    """Format đa thức thành LaTeX - từ thuc_te_hinh_hoc.py"""
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
    return clean_sign_expression(result)


def format_rational_for_latex(a, b, c, d, e, var='x'):
    """Format hàm số y = (ax^2 + bx + c)/(dx + e) cho LaTeX với phân số sạch."""
    # Tử số: ax^2 + bx + c
    num_terms = []
    if a != 0:
        if a == 1:
            num_terms.append(f"{var}^2")
        elif a == -1:
            num_terms.append(f"-{var}^2")
        else:
            num_terms.append(f"{a}{var}^2")
    if b != 0:
        if b == 1:
            num_terms.append(f"+{var}")
        elif b == -1:
            num_terms.append(f"-{var}")
        else:
            num_terms.append(f"+{b}{var}" if b > 0 else f"{b}{var}")
    if c != 0:
        num_terms.append(f"+{c}" if c > 0 else f"{c}")
    numerator = "".join(num_terms)
    if numerator.startswith("+"):
        numerator = numerator[1:]
    numerator = numerator or "0"

    # Mẫu số: dx + e
    denom_terms = []
    if d != 0:
        if d == 1:
            denom_terms.append(f"{var}")
        elif d == -1:
            denom_terms.append(f"-{var}")
        else:
            denom_terms.append(f"{d}{var}")
    if e != 0:
        denom_terms.append(f"+{e}" if e > 0 else f"{e}")
    denominator = "".join(denom_terms)
    if denominator.startswith("+"):
        denominator = denominator[1:]

    return f"\\frac{{{clean_sign_expression(numerator)}}}{{{clean_sign_expression(denominator)}}}"


# ███████████████████████████████████████████████████████████████████████████████
# ██                       HÀM TIỆN ÍCH XỬ LÝ CHUỖI                           ██
# ███████████████████████████████████████████████████████████████████████████████

def strip_latex_inline_math(ans: str) -> str:
    r"""Loại bỏ \( ... \) hoặc $...$ khỏi đáp án để tránh lồng môi trường toán học."""
    if ans.startswith("\\(") and ans.endswith("\\)"):
        return ans[2:-2].strip()
    if ans.startswith("$") and ans.endswith("$"):
        return ans[1:-1].strip()
    return ans


# ███████████████████████████████████████████████████████████████████████████████
# ██                   THÊM FORMAT LATEX MỚI TẠI ĐÂY                          ██
# ███████████████████████████████████████████████████████████████████████████████
# Ví dụ thêm hàm format mới:
# def format_your_new_function(value):
#     """Mô tả chức năng"""
#     return formatted_value


# ███████████████████████████████████████████████████████████████████████████████
# ██                       PHẦN 2: CÁC HÌNH VẼ TIKZ                            ██
# ███████████████████████████████████████████████████████████████████████████████

class TikZFigureLibrary:
    """Thư viện hình vẽ TikZ"""

    @staticmethod
    def get_bird_fish_3d_coordinate_figure():
        """Hình vẽ chim bói cá lặn xuống bắt cá với hệ trục tọa độ 3D - từ sample_bai1.tex"""
        return """
\\begin{tikzpicture}[line join=round, line cap=round,scale=1,transform shape, >=stealth]
\\definecolor{columbiablue}{rgb}{0.61, 0.87, 1.0}%màu nước
\\definecolor{arsenic}{rgb}{0.23, 0.27, 0.29}%màu mỏ
\\definecolor{antiquewhite}{rgb}{0.98, 0.92, 0.84}%màu trắng
\\definecolor{cadmiumorange}{rgb}{0.93, 0.53, 0.18}%lông cam
\\definecolor{coolblack}{rgb}{0.0, 0.18, 0.39}%cánh đậm
\\definecolor{brandeisblue}{rgb}{0.0, 0.44, 1.0}%màu xanh đầu
\\definecolor{darkcoral}{rgb}{0.8, 0.36, 0.27}%màu chân
\\definecolor{amber}{rgb}{1.0, 0.49, 0.0}%màu vẽ cá

\\tikzset{san/.pic={ 
    \\path
    (-1.3,-1.5) coordinate (O)
    ($(O)+(-142:2)$) coordinate (y)
    ($(O)+(0:4.7)$) coordinate (x)
    ($(O)+(90:3)$) coordinate (z)
    ($(x)+(y)-(O)$) coordinate (t)
    
    (-.8,-2.2)coordinate (A)
    (1.6,0.8) coordinate (C)
    ($(A)!.13!(C)$) coordinate (B)
    ;
    \\fill[columbiablue] (O)--(x)--(t)--(y)--cycle;
    
    \\foreach\\p/\\g/\\t in {x/-90/y, y/-90/x, z/0/z}
    {
        \\node at (\\p) [shift=(\\g:2mm)] {\\tiny $\\t$};
    }
    
    \\foreach\\p/\\g in {A/180,B/0,C/-50,O/-90}
    {
        \\draw[fill=black](\\p) circle (.5pt) +(\\g:2mm)node{\\tiny $\\p$};
    }
    
    \\draw[->] (O)--(x) ;
    \\draw[->] (O)--(y);
    \\draw[->] (O)--(z);
    \\draw[dashed] (A)--(B);
    \\draw (B)--(C);
    %---------nước
    \\draw (-1,-1.7)
    ..controls +(-120:.5) and +(-160:.5) ..(0,-2)
    (-.9,-1.9)
    ..controls +(-70:.2) and +(-160:.2) ..(-.2,-1.9)
    (-.95,-1.8)
    ..controls +(70:.5) and +(30:.5) ..(0,-1.9)
    (.1,-1.6)
    ..controls +(-20:.2) and +(30:.2) ..(.2,-1.9)
    (-.7,-1.75)
    ..controls +(-170:.2) and +(-160:.3) ..(-.5,-1.9)
    ;
}}

\\tikzset{chim_boi_ca/.pic={
    %==============cánh trái
    \\draw[fill=coolblack]
    (-.55,1.4)
    ..controls +(110:.7) and +(100:.3) ..(-.9,1.8)
    ..controls +(135:.3) and +(120:.3) ..(-1.2,1.8)
    ..controls +(145:.25) and +(110:.25) ..(-1.45,1.7)
    ..controls +(165:.15) and +(85:.15) ..(-1.75,1.63)
    ..controls +(-165:.1) and +(85:.1) ..(-1.9,1.5)
    ..controls +(165:.15) and +(85:.1) ..(-2.1,1.3)
    ..controls +(-165:.1) and +(95:.1) ..(-2.2,1.1)
    ..controls +(-160:.1) and +(95:.1) ..(-2.35,1)--(-1,1.1)
    ;
    %======--------------------
    %Tô lông đầu
    \\def\\L{
        (2,.84)
        ..controls +(170:.2) and +(25:.3) ..(1,.65)
        ..controls +(-145:.5) and +(40:.6) ..(.3,.4)
        ..controls +(-140:.3) and +(-60:.3) ..(0,.6)
        ..controls +(120:.3) and +(-50:.7) ..(-1,1.1)
        ..controls +(90:.3) and +(170:.3) ..(-.55,1.4)%1
        ..controls +(-40:.2) and +(140:.1) ..(-.25,1.2)
        ..controls +(-70:.2) and +(-160:.35) ..(.15,.85)
        ..controls +(75:.7) and +(135:.8) ..(1.9,1.3)--(2.1,1)--cycle
        ;
    }
    \\fill[brandeisblue] \\L;
    %==============================
    \\draw[fill=antiquewhite] (2,1.05)
    ..controls +(165:.2) and +(-35:.2)..(1.7,1.15)
    ..controls +(145:.2) and +(65:.2)..(1.2,1.15)
    ..controls +(-60:.1) and +(165:.1)..(1.4,1)
    ..controls +(-15:.2) and +(-145:.3)..cycle
    ;
    \\draw[fill=arsenic] (1.6,1.2)
    ..controls +(155:.18) and +(55:.15)..(1.23,1.17)
    ..controls +(-75:.2) and +(-95:.2)..cycle
    ;
    \\fill (1.44,1.14) circle(1mm);
    
    \\fill[cadmiumorange] (2,1.05)
    ..controls +(165:.2) and +(-35:.2)..(1.7,1.15)
    ..controls +(145:.2) and +(95:.3)..cycle
    ;
    \\fill[cadmiumorange] (2,.84)
    ..controls +(150:.2) and +(-25:.1) ..(1.7,1)
    ..controls +(155:.2) and +(-50:.3) ..(1.2,1.08)
    ..controls +(130:.2) and +(50:.2) ..(.75,1)
    ..controls +(-130:.2) and +(-10:.2) ..(.21,1)
    ..controls +(-120:.1) and +(70:.1) ..(.15,.84)
    ..controls +(-20:.3) and +(-150:.3) ..(.8,.85)
    ..controls +(-10:.3) and +(150:.5) ..(1.7,.85)
    ..controls +(-10:.1) and +(150:.1) ..cycle
    ;
    %==================
    %viền đen đầu
    \\def\\X{
        (0,.6)
        ..controls +(120:.3) and +(-50:.7) ..(-1,1.1)
        
        (-.55,1.4)%1
        ..controls +(-40:.2) and +(140:.1) ..(-.25,1.2)
        ..controls +(-70:.2) and +(-160:.35) ..(.15,.85)
        ..controls +(75:.7) and +(135:.8) ..(1.9,1.3)
        ;
    }
    \\draw[black]\\X;
    %====================
    %Tô mỏ
    \\def\\N{
        (1.9,1.3)
        ..controls +(-35:.4) and +(140:.3) ..(3.4,.78)
        ..controls +(-175:.2) and +(-10:.3) ..(2,.84)
        ..controls +(150:.2) and +(-25:.1) ..(1.7,1)
        ..controls +(20:.2) and +(175:.1) ..(2,1.05)
        ..controls +(-35:.2) and +(155:.1) ..cycle
        ;
    }
    \\fill[arsenic] \\N;
    %Mỏ
    \\def\\M{
        (1.9,1.3)
        ..controls +(-35:.4) and +(140:.3) ..(3.4,.78)
        ..controls +(-175:.2) and +(-10:.3) ..(2,.84)
        ..controls +(170:.2) and +(25:.3) ..(1,.65)
        ;
    }
    \\draw[black]\\M;
    %==============================
    
    %================Cánh phải
    \\draw[fill=coolblack]
    (-.6,-.3)%3
    ..controls +(-130:.5) and +(-10:.2) ..(-1,-.95)
    ..controls +(170:.1) and +(-10:.15) ..(-1.2,-1.02)
    ..controls +(170:.1) and +(-40:.15) ..(-1.45,-.95)
    ..controls +(160:.1) and +(-80:.15) ..(-1.6,-.8)
    ..controls +(140:.1) and +(-70:.15) ..(-1.75,-.65)
    ..controls +(140:.1) and +(-70:.15) ..(-1.9,-.5)
    ..controls +(160:.1) and +(-70:.15) ..(-2.05,-.35)
    ..controls +(150:.1) and +(-70:.15) ..(-2.25,-.2)
    ..controls +(-160:.1) and +(-20:.15) ..(-2.5,-.18)
    ..controls +(160:.1) and +(-30:.15) ..(-2.75,-.16)
    ..controls +(160:.1) and +(-60:.15) ..(-2.95,-.05)
    ..controls +(160:.1) and +(-80:.15) ..(-3.2,.05)
    ..controls +(160:.1) and +(-90:.15) ..(-3.35,.15)
    ..controls +(160:.1) and +(-95:.15) ..(-3.55,.25)
    ..controls +(-160:.2) and +(-145:.2) ..(-3.7,.35)
    ..controls +(-160:.2) and +(-160:.4) ..(-3.7,.53)
    ..controls +(-160:.2) and +(-160:.3) ..(-3.85,.65)
    ..controls +(160:.5) and +(-170:.3) ..(-2.6,.95)
    ..controls +(0:.5) and +(120:.3) ..(-.6,-.3)%3
    ;
    %===================
    \\fill[brandeisblue]
    (-.8,-1.1)%lông đuôi xanh
    ..controls +(-80:.2) and +(140:.2) ..(-.5,-1.5)
    ..controls +(-40:.2) and +(140:.4) ..(-.3,-2.5)
    ..controls +(135:.7) and +(-85:.6) ..cycle
    ;
    \\draw (-.3,-2.5)
    ..controls +(135:.7) and +(-85:.6) ..(-.8,-1.1)%lông đuôi xanh
    ;
    %=============đuôi
    \\draw[fill=brandeisblue] (-.45,-2.3)
    ..controls +(-95:.2) and +(95:.2) ..(-.4,-2.8)
    --(-.32,-2.8)--(-.25,-2.2)
    (-.25,-2.2)--(-.32,-2.78)--(-.27,-2.78)--(-.16,-2.2)
    ;
    %================
    %Tô lông cam
    \\def\\C{
        (2,.84)
        ..controls +(170:.2) and +(25:.3) ..(1,.65)
        ..controls +(-145:.5) and +(40:.6) ..(.3,.4)
        ..controls +(-140:.3) and +(-60:.3) ..(0,.6)
        ..controls +(120:.3) and +(-50:.7) ..(-1,1.1)%2
        ..controls +(130:.2) and +(20:.3) ..(-2.6,.95)
        ..controls +(-160:.2) and +(145:.3) ..(-1.6,.5)
        ..controls +(-35:.2) and +(145:.3) ..(-1,-.5)
        ..controls +(-35:.2) and +(-145:.2) ..(-.6,-.3)%3
        ..controls +(-135:.2) and +(100:.2) ..(-.8,-1.1)%lông đuôi xanh
        ..controls +(-80:.2) and +(140:.2) ..(-.5,-1.5)
        ..controls +(-40:.2) and +(140:.4) ..(-.3,-2.5)%đuôi dưới
        ..controls +(40:.4) and +(-150:.5) ..(.5,-1.1)%chân
        ..controls +(-20:.2) and +(160:.2) ..(.8,-1.15)
        ..controls +(150:.1) and +(-70:.1) ..(.65,-.9)
        ..controls +(110:.2) and +(-95:.8) ..(1.26,.6)
        ..controls +(75:.1) and +(-160:.2) ..cycle
        ;
    }
    
    \\fill[cadmiumorange] \\C;
    \\draw[black]\\C;
    
    \\draw[black] (-1,1.1)
    ..controls +(130:.2) and +(20:.3) ..(-2.6,.95)
    
    (-.6,-.3)%3
    ..controls +(-135:.2) and +(100:.2) ..(-.8,-1.1)
    ;
    
    %======================chân
    \\draw[fill=darkcoral]
    (.5,-1.1)
    ..controls +(-20:.1) and +(170:.1) ..(1.5,-1.1)%chân
    ..controls +(-10:.1) and +(-10:.3) ..(1.2,-1.2)
    ;
    %móng 2
    \\draw (1.47,-1.15)%chân
    ..controls +(-10:.1) and +(120:.1) ..(1.63,-1.25)
    ;
    %---------------------
    \\draw[fill=darkcoral]
    (.7,-1.15)
    ..controls +(40:.1) and +(170:.1) ..(1.3,-1.08)%chân
    ..controls +(-10:.1) and +(-10:.1) ..(1.2,-1.2)
    ..controls +(170:.1) and +(30:.1) ..(1,-1.2)
    ;
    %móng 2
    \\draw (1.27,-1.15)%chân
    ..controls +(-10:.1) and +(120:.1) ..(1.43,-1.25)
    ;
    %------------------------
    \\draw[fill=darkcoral]
    (.25,-1.1)
    ..controls +(-20:.2) and +(-170:.1) ..(.5,-1.1)%chân
    ..controls +(-20:.2) and +(160:.2) ..(.8,-1.15)
    ..controls +(-20:.2) and +(160:.2) ..(1.1,-1.2)%móng 1
    ..controls +(-20:.1) and +(-50:.1) ..(1.03,-1.25)
    ..controls +(130:.05) and +(-10:.05) ..(.8,-1.26)
    ..controls +(170:.05) and +(10:.05) ..(.5,-1.28)
    ..controls +(-150:.1) and +(-160:.15) ..(.3,-1.25)
    ..controls +(160:.1) and +(-80:.1) ..(.1,-1.15)
    ;
    %móng 1
    \\draw (1.1,-1.25)%móng 1
    ..controls +(-20:.1) and +(95:.1) ..(1.2,-1.35)
    ;
}}

%===========Vẽ cá
\\tikzset{ca/.pic={
    %vây
    \\def\\V{
        (-.35,.74)
        ..controls +(120:.12) and +(40:.22) ..(-.7,.72)--cycle
        (-.7,.32)
        ..controls +(-170:.1) and +(10:.1) ..(-.95,.3)
        ..controls +(60:.1) and +(-140:.1) ..(-.85,.45)--(-.65,.4)--cycle
        (-.3,.32)
        ..controls +(-170:.1) and +(10:.1) ..(-.45,.1)
        ..controls +(-40:.1) and +(-110:.1) ..(-.1,.37)--cycle
        ;
    }
    \\fill[amber] \\V;
    \\draw\\V;
    
    %-----------------
    \\def\\C{
        (-1.25,.83)
        ..controls +(-45:.2) and +(130:.2) ..(-1,.58)
        ..controls +(35:.2) and +(130:.52) ..(.05,.52)
        ..controls +(-90:.1) and +(-110:.1) ..(.05,.52)--(.04,.44)
        ..controls +(-150:.5) and +(-40:.2) ..(-1,.53)
        ..controls +(-140:.1) and +(40:.1) ..(-1.3,.42)
        ..controls +(60:.2) and +(-55:.2) ..cycle
        ;
    }
    
    \\fill[amber] \\C;
    \\draw\\C;
    %-----------------
    \\def\\Cn{
        (-1,.57)
        ..controls +(35:.1) and +(130:.4) ..(.01,.52)
        ..controls +(-140:.4) and +(-40:.2) ..cycle
        ;
    }
    \\fill[amber!70] \\Cn;
    \\draw (-.3,.7)
    ..controls +(-120:.1) and +(120:.2) ..(-.3,.34);
    
    \\draw[fill=white] (-.22,.55) circle (.08);
    \\draw[fill=black] (-.22,.55) circle (.048);
    
}}

\\path
(0,0)pic[scale=1]{san}
;

\\path (-1,-2.5)pic[xscale=-.35,yscale=.35]{ca}
(1.6,1)pic[xscale=-.15,yscale=.15,rotate=-40]{chim_boi_ca}; 
\\end{tikzpicture}
"""

    @staticmethod
    def get_airplane_3d_coordinate_figure():
        """Hình vẽ máy bay trong không gian 3D với hệ trục tọa độ - từ sample_bai1.tex"""
        return """
\\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\\footnotesize,scale=1]

\\path 
(0,0) coordinate (O)
(-2,-2) coordinate (A')
(4,0) coordinate (B')
(0,3) coordinate (C')
($(O)!0.3!(C')$) coordinate (C1)
($(O)!0.3!(B')$) coordinate (B1)
($(O)!0.3!(A')$) coordinate (A1)
($(O)!0.8!(C')$) coordinate (C)
($(O)!0.8!(B')$) coordinate (B)
($(O)!0.8!(A')$) coordinate (A)
;

\\foreach \\diem/\\t/\\r in{A'/x/-90,
    B'/y/60,
    C'/z/60,
    A1/\\overrightarrow{i}/-60,
    B1/\\overrightarrow{j}/-90,
    C1/\\overrightarrow{k}/180}	
\\draw[->,line width=1pt] 	(O)--(\\diem)node[shift={(\\r:4mm)},scale=0.8]{$\\t$};

\\draw[dashed] 
(A)--($(A)+(B)-(O)$) coordinate (H) --(B)
(C)--($(C)+(H)-(O)$)coordinate (M) node[above=0.5cm]{$M$}--(H)
(H)--(O)--(M);

\\draw (M) node[scale=0.7]{	
    \\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\\footnotesize,scale=0.15,rotate=30]
        %%%%%%%%%%%%%%	
        \\draw[fill=black] 
        (0,0) .. controls +(20:1) and +(90:1) .. (8,0)
        ..controls +(-90:1) and +(-20:1) .. (0,0)--cycle
        ;
        %%%%%%%%%%%%%%	
        \\draw [fill=black]
        (4,0)--(3,4)--(3.5,4)--(6,0)--cycle
        (4,0)--(3,-4)--(3.5,-4)--(6,0)--cycle
        (0.5,0)--(0,1)--(0.5,1)--(1.3,0)--cycle
        (0.5,0)--(0,-1)--(0.5,-1)--(1.3,0)--cycle
        ;
        %%%%%%%%%%%%%
    \\end{tikzpicture}	
};
\\draw pic[draw,angle radius=4mm] {right angle = O--A--H}; 
\\draw pic[draw,angle radius=4mm] {right angle = O--B--H}; 
\\draw pic[draw,angle radius=4mm] {right angle = O--C--M}; 
\\draw[cyan,line width=2pt,->] (O)--(M);	

\\foreach \\p/\\r in {A/160,B/90,C/180,H/-45}
\\fill (\\p) circle (1.2pt) node[shift={(\\r:3mm)},scale=0.8]{$\\p$};
\\end{tikzpicture}
"""

    @staticmethod
    def get_general_3d_coordinate_figure():
        """Hình vẽ hệ trục tọa độ 3D mở rộng với mặt nước và vật thể - bổ sung cho những context khác của dạng toán Giao điểm đường thẳng với mặt phẳng"""
        return """
\\begin{tikzpicture}[line join=round, line cap=round,scale=1,transform shape, >=stealth]
\\definecolor{columbiablue}{rgb}{0.61, 0.87, 1.0}%màu nước
\\definecolor{arsenic}{rgb}{0.23, 0.27, 0.29}%màu mỏ
\\definecolor{antiquewhite}{rgb}{0.98, 0.92, 0.84}%màu trắng
\\definecolor{cadmiumorange}{rgb}{0.93, 0.53, 0.18}%lông cam
\\definecolor{coolblack}{rgb}{0.0, 0.18, 0.39}%cánh đậm
\\definecolor{brandeisblue}{rgb}{0.0, 0.44, 1.0}%màu xanh đầu
\\definecolor{darkcoral}{rgb}{0.8, 0.36, 0.27}%màu chân
\\definecolor{amber}{rgb}{1.0, 0.49, 0.0}%màu vẽ cá

\\tikzset{san/.pic={ 
    \\path
    (-1.3,-1.5) coordinate (O)
    ($(O)+(-142:2)$) coordinate (y)
    ($(O)+(0:4.7)$) coordinate (x)
    ($(O)+(90:3)$) coordinate (z)
    ($(x)+(y)-(O)$) coordinate (t)
    
    (-.8,-2.2)coordinate (A)
    (1.6,0.8) coordinate (C)
    ($(A)!.13!(C)$) coordinate (B)
    ;
    \\fill[columbiablue] (O)--(x)--(t)--(y)--cycle;
    
    \\foreach\\p/\\g/\\t in {x/-90/y, y/-90/x, z/0/z}
    {
        \\node at (\\p) [shift=(\\g:2mm)] {\\tiny $\\t$};
    }
    
    \\foreach\\p/\\g in {A/180,B/0,C/-50,O/-90}
    {
        \\draw[fill=black](\\p) circle (.5pt) +(\\g:2mm)node{\\tiny $\\p$};
    }
    
    \\draw[->] (O)--(x) ;
    \\draw[->] (O)--(y);
    \\draw[->] (O)--(z);
    \\draw[dashed] (A)--(B);
    \\draw (B)--(C);
    %---------nước
    \\draw (-1,-1.7)
    ..controls +(-120:.5) and +(-160:.5) ..(0,-2)
    (-.9,-1.9)
    ..controls +(-70:.2) and +(-160:.2) ..(-.2,-1.9)
    (-.95,-1.8)
    ..controls +(70:.5) and +(30:.5) ..(0,-1.9)
    (.1,-1.6)
    ..controls +(-20:.2) and +(30:.2) ..(.2,-1.9)
    (-.7,-1.75)
    ..controls +(-170:.2) and +(-160:.3) ..(-.5,-1.9)
    ;
}}

\\path
(0,0)pic[scale=1]{san}
;

\\end{tikzpicture}
"""

    # ===== THÊM TIKZ FIGURES MỚI TẠI ĐÂY =====
    # Ví dụ thêm hình vẽ mới:
    # @staticmethod
    # def get_your_new_figure():
    #     """Mô tả hình vẽ của bạn"""
    #     return """
    #     \\begin{tikzpicture}
    #         % Code TikZ của bạn ở đây
    #     \\end{tikzpicture}
    #     """


# ███████████████████████████████████████████████████████████████████████████████
# ██                     PHẦN 3: LỚP CƠ SỞ CHO CÂU HỎI                         ██
# ███████████████████████████████████████████████████████████████████████████████

class BaseOptimizationQuestion(ABC):
    """
    Lớp cơ sở cho tất cả các dạng bài toán tối ưu hóa

    Mỗi dạng toán con cần implement:
    1. generate_parameters() - Sinh tham số ngẫu nhiên
    2. calculate_answer() - Tính đáp án đúng
    3. generate_wrong_answers() - Sinh đáp án sai
    4. generate_question_text() - Sinh đề bài
    5. generate_solution() - Sinh lời giải
    """

    def __init__(self):
        """Khởi tạo các thuộc tính cơ bản"""
        self.parameters = {}  # Tham số của bài toán
        self.correct_answer = None  # Đáp án đúng
        self.wrong_answers = []  # Danh sách đáp án sai
        self.solution_steps = []  # Các bước giải (nếu cần)

    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        """
        Sinh tham số ngẫu nhiên cho bài toán

        Returns:
            Dict chứa các tham số cần thiết

        Ví dụ:
            return {
                'length': 10,
                'width': 5,
                'cost': 100000
            }
        """
        pass

    @abstractmethod
    def calculate_answer(self) -> str:
        """
        Tính đáp án đúng dựa trên parameters

        Returns:
            Chuỗi LaTeX chứa đáp án (ví dụ: "\\(5\\) mét")
        """
        pass

    @abstractmethod
    def generate_wrong_answers(self) -> List[str]:
        """
        Sinh 3 đáp án sai hợp lý

        Returns:
            List chứa 3 chuỗi LaTeX đáp án sai
        """
        pass

    @abstractmethod
    def generate_question_text(self) -> str:
        """
        Sinh đề bài bằng LaTeX

        Returns:
            Chuỗi LaTeX chứa đề bài hoàn chỉnh (có thể có hình vẽ)
        """
        pass

    @abstractmethod
    def generate_solution(self) -> str:
        """
        Sinh lời giải chi tiết bằng LaTeX

        Returns:
            Chuỗi LaTeX chứa lời giải từng bước
        """
        pass

    def generate_full_question(self, question_number: int = 1) -> str:
        """
        Tạo câu hỏi hoàn chỉnh với 4 đáp án A/B/C/D

        Args:
            question_number: Số thứ tự câu hỏi

        Returns:
            Chuỗi chứa câu hỏi hoàn chỉnh với đáp án và lời giải
        """
        logging.info(f"Đang tạo câu hỏi {question_number}")

        # Bước 1: Sinh tham số và tính toán
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        self.wrong_answers = self.generate_wrong_answers()

        # Bước 2: Tạo nội dung câu hỏi
        question_text = self.generate_question_text()
        solution = self.generate_solution()

        # Bước 3: Trộn đáp án và đánh dấu đáp án đúng
        all_answers = [self.correct_answer] + self.wrong_answers
        random.shuffle(all_answers)
        correct_index = all_answers.index(self.correct_answer)

        # Bước 4: Format câu hỏi
        question_content = f"Câu {question_number}: {question_text}\n\n"

        for j, ans in enumerate(all_answers):
            letter = chr(65 + j)  # A, B, C, D
            marker = "*" if j == correct_index else ""
            question_content += f"{marker}{letter}. {ans}\n\n"

        question_content += f"Lời giải:\n\n{solution}\n\n"

        return question_content

    def generate_question_only(self, question_number: int = 1) -> tuple:
        """Tạo câu hỏi chỉ có đề bài và lời giải"""
        logging.info(f"Đang tạo câu hỏi {question_number}")

        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()

        question_text = self.generate_question_text()
        solution = self.generate_solution()

        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += f"Lời giải:\n\n{solution}\n\n"

        return question_content, self.correct_answer

    @staticmethod
    def create_latex_document(questions: List[str], title: str = "Câu hỏi Tối ưu hóa") -> str:
        """
        Tạo document LaTeX hoàn chỉnh (tối ưu cho xelatex)

        Args:
            questions: Danh sách câu hỏi
            title: Tiêu đề document

        Returns:
            Chuỗi LaTeX hoàn chỉnh
        """
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{polyglossia}}
\\setmainlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage{{tikz}}
\\usepackage{{tkz-tab}}
\\usepackage{{tkz-euclide}}
\\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\\begin{{document}}
\\title{{{title}}}
\\maketitle

"""
        latex_content += "\n\n".join(questions)
        latex_content += "\n\\end{document}"
        return latex_content

    @staticmethod
    def create_latex_document_with_format(questions_data: List, title: str = "Câu hỏi Tối ưu hóa", fmt: int = 1) -> str:
        """Tạo document LaTeX với 2 format khác nhau"""
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{fontspec}}
\\usepackage{{tikz}}
\\usepackage{{tkz-tab}}
\\usepackage{{tkz-euclide}}
\\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\\begin{{document}}
\\title{{{title}}}
\\maketitle

"""

        if fmt == 1:
            # Format 1: đáp án ngay sau câu hỏi
            latex_content += "\n\n".join(questions_data)
        else:
            # Format 2: câu hỏi + lời giải, đáp án ở cuối
            correct_answers = []
            for question_content, correct_answer in questions_data:
                latex_content += question_content + "\n\n"
                correct_answers.append(correct_answer)

            latex_content += "Đáp án\n\n"
            for idx, answer in enumerate(correct_answers, 1):
                latex_content += f"{idx}. {answer}\n\n"

        latex_content += "\\end{document}"
        return latex_content


# ███████████████████████████████████████████████████████████████████████████████
# ██                        PHẦN 4: DẠNG TOÁN                              ██
# ███████████████████████████████████████████████████████████████████████████████


# ███████████████████████████████████████████████████████████████████████████████
# ██                  DẠNG TOÁN: Đồng/nghịch biến hàm số                       ██
# ███████████████████████████████████████████████████████████████████████████████

class RationalQuadraticMonotonicity(BaseOptimizationQuestion):
    r"""
    Dạng toán đa dạng về đồng biến, nghịch biến của hàm số với các ngữ cảnh thực tế.
    
    Bao gồm:
    - Hàm phân thức bậc hai/bậc nhất: y = (ax² + bx + c)/(dx + e)
    - Hàm đa thức bậc ba: y = ax³ + bx² + cx + d
    - Hàm đa thức bậc bốn: y = ax⁴ + bx³ + cx² + dx + e
    
    Ngữ cảnh thực tế: vận tốc, quãng đường, vi khuẩn, dân số, kinh tế, etc.
    """

    def get_critical_points(self, a, b, c, d, e):
        """Tính điểm tới hạn và điểm gián đoạn cho f(x) = (ax^2 + bx + c)/(dx + e) - chỉ trả về số nguyên."""
        x_p = round(-e / d) if d != 0 else 0  # Làm tròn gần nhất về số nguyên

        A = a * d
        B = 2 * a * e
        C = b * e - c * d

        discriminant = B * B - 4 * A * C
        if discriminant < 0 or not is_perfect_square(discriminant):
            return [], x_p

        sqrt_disc = discriminant ** 0.5
        x1 = (-B - sqrt_disc) / (2 * A)
        x2 = (-B + sqrt_disc) / (2 * A)
        critical_points = [x1, x2]
        critical_points.sort()

        return critical_points, x_p

    def get_monotonicity_intervals(self, a, d, critical_points, x_p):
        """Xác định khoảng tăng và khoảng giảm."""
        if not critical_points:
            if a * d > 0:
                return [(float('-inf'), x_p), (x_p, float('inf'))], []
            else:
                return [], [(float('-inf'), x_p), (x_p, float('inf'))]

        x1, x2 = critical_points
        if a * d > 0:
            increasing = [(float('-inf'), min(x1, x_p)), (max(x2, x_p), float('inf'))]
            decreasing = []
            if x1 < x_p < x2:
                decreasing = [(x1, x_p), (x_p, x2)]
            elif x_p < x1:
                decreasing = [(x1, x2)]
            elif x_p > x2:
                decreasing = [(x1, x2)]
        else:
            decreasing = [(float('-inf'), min(x1, x_p)), (max(x2, x_p), float('inf'))]
            increasing = []
            if x1 < x_p < x2:
                increasing = [(x1, x_p), (x_p, x2)]
            elif x_p < x1:
                increasing = [(x1, x2)]
            elif x_p > x2:
                increasing = [(x1, x2)]

        increasing = [i for i in increasing if i[0] < i[1]]
        decreasing = [d for d in decreasing if d[0] < d[1]]

        return increasing, decreasing

    def get_valid_coefficients(self, nice_numbers, coeff_range=(-5, 5), domain_min=-5):
        """Sinh hệ số hợp lệ đảm bảo điểm tới hạn thực trong nice_numbers."""
        valid_configs = []
        a_choices = [a for a in range(coeff_range[0], coeff_range[1] + 1) if a != 0]
        d_choices = [d for d in range(coeff_range[0], coeff_range[1] + 1) if d != 0]

        for a in a_choices:
            for b in range(coeff_range[0], coeff_range[1] + 1):
                for c in range(coeff_range[0], coeff_range[1] + 1):
                    for d in d_choices:
                        for e in range(coeff_range[0], coeff_range[1] + 1):
                            critical_points, x_p = self.get_critical_points(a, b, c, d, e)
                            if not critical_points:
                                continue
                            x1, x2 = critical_points
                            if x1 not in nice_numbers or x2 not in nice_numbers:
                                continue
                            if abs(x2 - x1) < 1:
                                continue
                            
                            # Kiểm tra ràng buộc domain cho ngữ cảnh thời gian
                            if domain_min >= 0:  # Ngữ cảnh thời gian (t >= 0)
                                # Loại bỏ nếu có điểm tới hạn âm
                                if x1 < domain_min or x2 < domain_min:
                                    continue
                                # Loại bỏ nếu điểm gián đoạn âm
                                if x_p < domain_min:
                                    continue
                            
                            valid_configs.append((a, b, c, d, e))

        logging.debug(f"Đã tìm thấy {len(valid_configs)} bộ hệ số hợp lệ")
        return valid_configs

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán với ngữ cảnh thực tế đa dạng và ràng buộc hợp lý."""

        # Các ngữ cảnh thực tế đa dạng với ràng buộc cụ thể
        contexts = [
            {
                "name": "velocity",
                "function_type": "rational",  # phân thức
                "subject": "vận tốc của xe",
                "unit": "m/s",
                "time_unit": "giây",
                "question_type": "velocity_change",
                "description": "Một chiếc xe chuyển động với vận tốc được mô tả bởi hàm số",
                "ask_format": "tăng" if random.choice([True, False]) else "giảm",
                "constraints": {
                    "domain_min": 0,  # Thời gian không âm
                    "domain_max": 20,  # Giảm từ 100 xuống 20 giây
                    "value_min": 0,  # Vận tốc không âm
                    "value_max": 100,  # Tăng từ 50 lên 100 m/s
                    "must_be_positive": False,  # Tạm thời không yêu cầu dương
                    "physical_meaning": "Thời gian t $\\geq$ 0"
                }
            },
            {
                "name": "bacteria",
                "function_type": "polynomial_3",  # bậc 3
                "subject": "tốc độ phát triển vi khuẩn",
                "unit": "nghìn con/giờ",
                "time_unit": "giờ",
                "question_type": "growth_rate",
                "description": "Tốc độ phát triển của một quần thể vi khuẩn được mô tả bởi hàm số",
                "ask_format": "tăng" if random.choice([True, False]) else "giảm",
                "constraints": {
                    "domain_min": 0,  # Thời gian không âm
                    "domain_max": 10,  # Giảm từ 48 xuống 10 giờ
                    "value_min": -100,  # Cho phép giá trị âm
                    "value_max": 1000,  # Tốc độ tối đa hợp lý
                    "must_be_positive": False,  # Tạm thời không yêu cầu dương
                    "physical_meaning": "Thời gian t $\\geq$ 0"
                }
            },
            {
                "name": "distance",
                "function_type": "polynomial_4",  # bậc 4
                "subject": "quãng đường",
                "unit": "mét",
                "time_unit": "giây",
                "question_type": "velocity_from_distance",
                "description": "Quãng đường di chuyển của một vật được cho bởi hàm số",
                "ask_format": "tăng" if random.choice([True, False]) else "giảm",
                "constraints": {
                    "domain_min": 0,  # Thời gian không âm
                    "domain_max": 10,  # Giảm từ 60 xuống 10 giây
                    "value_min": -100,  # Cho phép giá trị âm
                    "value_max": 1000,  # Quãng đường tối đa hợp lý
                    "must_be_positive": False,  # Tạm thời không yêu cầu dương
                    "physical_meaning": "Thời gian t $\\geq$ 0"
                }
            },
            {
                "name": "population",
                "function_type": "polynomial_3",  # bậc 3
                "subject": "tốc độ tăng dân số",
                "unit": "người/năm",
                "time_unit": "năm",
                "question_type": "population_growth",
                "description": "Tốc độ tăng dân số của một thành phố được mô tả bởi hàm số",
                "ask_format": "tăng" if random.choice([True, False]) else "giảm",
                "constraints": {
                    "domain_min": 0,  # Thời gian không âm (năm 0 là mốc)
                    "domain_max": 10,  # Giảm từ 50 xuống 10 năm
                    "value_min": -10000,  # Cho phép giảm dân số
                    "value_max": 50000,  # Tốc độ tăng tối đa hợp lý
                    "must_be_positive": False,  # Dân số có thể giảm
                    "physical_meaning": "Thời gian t $\\geq$ 0"
                }
            },
            {
                "name": "economy",
                "function_type": "rational",  # phân thức
                "subject": "tốc độ tăng trưởng kinh tế",
                "unit": "%/năm",
                "time_unit": "năm",
                "question_type": "economic_growth",
                "description": "Tốc độ tăng trưởng kinh tế của một quốc gia được mô tả bởi hàm số",
                "ask_format": "tăng" if random.choice([True, False]) else "giảm",
                "constraints": {
                    "domain_min": 0,  # Thời gian không âm
                    "domain_max": 10,  # Giảm từ 30 xuống 10 năm
                    "value_min": -20,  # Cho phép suy thoái (-20%)
                    "value_max": 20,  # Tăng trưởng tối đa hợp lý (20%)
                    "must_be_positive": False,  # Kinh tế có thể suy thoái
                    "physical_meaning": "Thời gian t $\\geq$ 0"
                }
            }
        ]

        # Chọn ngữ cảnh ngẫu nhiên
        context = random.choice(contexts)
        
        # Random biến cho hàm số (nhất quán trong toàn bộ câu hỏi)
        # Với ràng buộc vật lý, thường dùng 't' cho thời gian
        if context["name"] in ["velocity", "bacteria", "distance", "population", "economy"]:
            context['variable'] = 't'  # Thời gian
        else:
            variables = ['x', 't', 'u', 'v', 'z']
            context['variable'] = random.choice(variables)

        # Sinh hàm số dựa trên loại với ràng buộc
        if context["function_type"] == "rational":
            return self._generate_rational_function(context)
        elif context["function_type"] == "polynomial_3":
            return self._generate_polynomial_3(context)
        elif context["function_type"] == "polynomial_4":
            return self._generate_polynomial_4(context)
        else:
            return self._generate_rational_function(context)

    def _generate_rational_function(self, context):
        """Sinh hàm phân thức bậc hai/bậc nhất với ràng buộc theo ngữ cảnh"""
        max_attempts = 200
        constraints = context.get("constraints", {})
        
        # Điều chỉnh nice_numbers theo ràng buộc domain
        domain_min = constraints.get("domain_min", -5)
        domain_max = constraints.get("domain_max", 5)
        
        # Tạo nice_numbers theo ràng buộc domain - chỉ sử dụng số nguyên
        if domain_min >= 0:  # Ngữ cảnh thời gian (t >= 0)
            nice_numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        else:
            nice_numbers = [-10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Thêm các điểm trong domain
        for i in range(max(0, int(domain_min)), int(domain_max) + 1):
            if i not in nice_numbers:
                nice_numbers.append(i)
        
        # Thêm thêm một số điểm nguyên trong khoảng
        for i in range(max(1, int(domain_min)), int(domain_max) + 1):
            nice_numbers.extend([i + 5, i + 10])  # Thêm các số nguyên lớn hơn
        
        # Lọc bỏ các số âm nếu domain_min >= 0
        if domain_min >= 0:
            nice_numbers = [n for n in nice_numbers if n >= domain_min]
        
        nice_numbers = list(set(nice_numbers))  # Remove duplicates
        nice_numbers.sort()
        
        coeff_range = (-5, 5)
        valid_configs = self.get_valid_coefficients(nice_numbers, coeff_range, domain_min)
        if not valid_configs:
            # Nếu không có config hợp lệ, thử với range lớn hơn
            coeff_range = (-10, 10)
            valid_configs = self.get_valid_coefficients(nice_numbers, coeff_range, domain_min)
            if not valid_configs:
                raise RuntimeError("Không tìm thấy bộ hệ số hợp lệ.")

        for attempt in range(max_attempts):
            a, b, c, d, e = random.choice(valid_configs)
            critical_points, x_p = self.get_critical_points(a, b, c, d, e)
            if not critical_points:
                continue
            x1, x2 = critical_points
            
            # Kiểm tra ràng buộc domain nghiêm ngặt cho ngữ cảnh thời gian
            if domain_min >= 0:  # Ngữ cảnh thời gian (t >= 0)
                # Loại bỏ nếu có điểm tới hạn âm
                if x1 < domain_min or x2 < domain_min:
                    continue
                # Loại bỏ nếu điểm gián đoạn âm hoặc quá gần biên
                if x_p < domain_min or abs(x_p - domain_min) < 0.1:
                    continue
            else:
                # Nới lỏng ràng buộc domain - chỉ yêu cầu 1 điểm trong domain
                if not (domain_min <= x1 <= domain_max or domain_min <= x2 <= domain_max):
                    continue
                # Nới lỏng ràng buộc điểm gián đoạn - chỉ loại bỏ nếu quá gần
                if abs(x_p - domain_min) < 0.1 or abs(x_p - domain_max) < 0.1:
                    continue
            
            increasing_intervals, decreasing_intervals = self.get_monotonicity_intervals(a, d, critical_points, x_p)
            
            # Lọc các khoảng theo domain constraints
            increasing_intervals = self._filter_intervals_by_domain(increasing_intervals, domain_min, domain_max)
            decreasing_intervals = self._filter_intervals_by_domain(decreasing_intervals, domain_min, domain_max)

            monotonicity = context["ask_format"]

            if monotonicity == "tăng" and not increasing_intervals:
                continue
            if monotonicity == "giảm" and not decreasing_intervals:
                continue

            # Bỏ qua kiểm tra ràng buộc giá trị để tăng tỷ lệ thành công

            return {
                'context': context,
                'function_type': 'rational',
                'a': a, 'b': b, 'c': c, 'd': d, 'e': e,
                'critical_points': critical_points,
                'x_p': x_p,
                'increasing_intervals': increasing_intervals,
                'decreasing_intervals': decreasing_intervals,
                'monotonicity': monotonicity
            }

        raise RuntimeError("Không thể sinh câu hỏi hợp lệ sau số lần thử tối đa.")

    def _generate_polynomial_3(self, context):
        """Sinh hàm bậc 3: y = ax³ + bx² + cx + d với ràng buộc theo ngữ cảnh"""
        max_attempts = 100
        constraints = context.get("constraints", {})
        
        # Điều chỉnh domain theo ràng buộc
        domain_min = constraints.get("domain_min", -5)
        domain_max = constraints.get("domain_max", 5)

        for attempt in range(max_attempts):
            # Sinh hệ số cho hàm bậc 3
            a = random.choice([1, -1, 2, -2])  # a ≠ 0
            b = random.randint(-3, 3)
            c = random.randint(-5, 5)
            d = random.randint(-5, 5)

            # Tính đạo hàm: y' = 3ax² + 2bx + c
            # Tìm nghiệm của y' = 0
            discriminant = (2 * b) ** 2 - 4 * (3 * a) * c
            if discriminant <= 0:
                continue

            sqrt_disc = math.sqrt(discriminant)
            x1 = (-2 * b - sqrt_disc) / (2 * 3 * a)
            x2 = (-2 * b + sqrt_disc) / (2 * 3 * a)

            if x1 > x2:
                x1, x2 = x2, x1

            # Đảm bảo x1 != x2 (tránh nghiệm kép)
            if x1 == x2:
                continue

            # Áp dụng ràng buộc domain
            if x1 < domain_min or x1 > domain_max or x2 < domain_min or x2 > domain_max:
                continue

            critical_points = [x1, x2]

            # Xác định khoảng đồng biến, nghịch biến
            if a > 0:
                increasing_intervals = [(domain_min, x1), (x2, domain_max)]
                decreasing_intervals = [(x1, x2)]
            else:
                decreasing_intervals = [(domain_min, x1), (x2, domain_max)]
                increasing_intervals = [(x1, x2)]

            # Lọc khoảng theo domain
            increasing_intervals = self._filter_intervals_by_domain(increasing_intervals, domain_min, domain_max)
            decreasing_intervals = self._filter_intervals_by_domain(decreasing_intervals, domain_min, domain_max)

            monotonicity = context["ask_format"]

            if monotonicity == "tăng" and not increasing_intervals:
                continue
            if monotonicity == "giảm" and not decreasing_intervals:
                continue

            # Kiểm tra ràng buộc giá trị (chỉ kiểm tra nếu có ràng buộc nghiêm ngặt)
            if constraints.get("must_be_positive", False):
                coeffs = [d, c, b, a]  # Thứ tự từ bậc 0 đến bậc 3
                if not self._check_polynomial_constraints(coeffs, domain_min, domain_max, constraints):
                    continue

            return {
                'context': context,
                'function_type': 'polynomial_3',
                'a': a, 'b': b, 'c': c, 'd': d,
                'critical_points': critical_points,
                'increasing_intervals': increasing_intervals,
                'decreasing_intervals': decreasing_intervals,
                'monotonicity': monotonicity
            }

        raise RuntimeError("Không thể sinh hàm bậc 3 hợp lệ.")

    def _generate_polynomial_4(self, context):
        """Sinh hàm bậc 4 dạng đơn giản: y = ax⁴ + bx² + c với ràng buộc theo ngữ cảnh"""
        max_attempts = 100
        constraints = context.get("constraints", {})
        
        # Điều chỉnh domain theo ràng buộc
        domain_min = constraints.get("domain_min", -5)
        domain_max = constraints.get("domain_max", 5)

        for attempt in range(max_attempts):
            # Sinh hệ số cho hàm bậc 4 dạng đơn giản
            a = random.choice([1, -1])  # a ≠ 0
            b = random.randint(-5, 5)
            c = random.randint(-5, 5)

            # Hàm y = ax⁴ + bx² + c
            # Đạo hàm: y' = 4ax³ + 2bx = 2x(2ax² + b)
            # Nghiệm: x = 0 và x² = -b/(2a) (nếu -b/(2a) > 0)

            critical_points = [0]
            if -b / (2 * a) > 0:
                sqrt_val = math.sqrt(-b / (2 * a))
                if sqrt_val > 0:  # Đảm bảo không có nghiệm kép tại 0
                    critical_points = [-sqrt_val, 0, sqrt_val]

            # Áp dụng ràng buộc domain
            critical_points = [x for x in critical_points if domain_min <= x <= domain_max]
            
            # Loại bỏ các điểm trùng lặp
            critical_points = sorted(list(set(critical_points)))
            
            if not critical_points:
                continue

            # Xác định khoảng đồng biến, nghịch biến cho trường hợp đơn giản
            if len(critical_points) == 1:  # Chỉ có x = 0
                if a > 0:
                    increasing_intervals = [(0, domain_max)]
                    decreasing_intervals = [(domain_min, 0)]
                else:
                    decreasing_intervals = [(0, domain_max)]
                    increasing_intervals = [(domain_min, 0)]
            elif len(critical_points) == 3:  # Có 3 điểm tới hạn
                x1, x2, x3 = sorted(critical_points)
                if a > 0:
                    increasing_intervals = [(domain_min, x1), (x2, x3)]
                    decreasing_intervals = [(x1, x2), (x3, domain_max)]
                else:
                    decreasing_intervals = [(domain_min, x1), (x2, x3)]
                    increasing_intervals = [(x1, x2), (x3, domain_max)]
            else:
                # Trường hợp khác (có thể chỉ có 2 điểm do lọc domain)
                critical_points_sorted = sorted(critical_points)
                if len(critical_points_sorted) == 2:
                    x1, x2 = critical_points_sorted
                    if a > 0:
                        increasing_intervals = [(domain_min, x1), (x2, domain_max)]
                        decreasing_intervals = [(x1, x2)]
                    else:
                        decreasing_intervals = [(domain_min, x1), (x2, domain_max)]
                        increasing_intervals = [(x1, x2)]
                else:
                    continue

            # Lọc khoảng theo domain
            increasing_intervals = self._filter_intervals_by_domain(increasing_intervals, domain_min, domain_max)
            decreasing_intervals = self._filter_intervals_by_domain(decreasing_intervals, domain_min, domain_max)

            monotonicity = context["ask_format"]

            if monotonicity == "tăng" and not increasing_intervals:
                continue
            if monotonicity == "giảm" and not decreasing_intervals:
                continue

            # Kiểm tra ràng buộc giá trị (chỉ kiểm tra nếu có ràng buộc nghiêm ngặt)
            if constraints.get("must_be_positive", False):
                coeffs = [c, 0, b, 0, a]  # Thứ tự từ bậc 0 đến bậc 4
                if not self._check_polynomial_constraints(coeffs, domain_min, domain_max, constraints):
                    continue

            return {
                'context': context,
                'function_type': 'polynomial_4',
                'a': a, 'b': b, 'c': c,
                'critical_points': critical_points,
                'increasing_intervals': increasing_intervals,
                'decreasing_intervals': decreasing_intervals,
                'monotonicity': monotonicity
            }

        raise RuntimeError("Không thể sinh hàm bậc 4 hợp lệ.")

    def calculate_answer(self) -> str:
        """Tính đáp án đúng dựa trên loại hàm và ngữ cảnh với ràng buộc."""
        context = self.parameters['context']
        monotonicity = self.parameters['monotonicity']
        increasing_intervals = self.parameters['increasing_intervals']
        decreasing_intervals = self.parameters['decreasing_intervals']
        constraints = context.get('constraints', {})

        # Chọn khoảng dựa trên monotonicity
        if monotonicity == "tăng":
            target_intervals = increasing_intervals
        else:
            target_intervals = decreasing_intervals

        # Format khoảng thời gian với ràng buộc domain
        domain_min = constraints.get('domain_min', float('-inf'))
        domain_max = constraints.get('domain_max', float('inf'))
        
        # Không thêm thông tin ràng buộc vào câu trả lời để tránh lặp lại
        # constraint_info chỉ xuất hiện trong lời giải chi tiết

        # Chỉ lấy khoảng đầu tiên để phù hợp với format trắc nghiệm A/B/C/D
        if target_intervals:
            interval = target_intervals[0]  # Lấy khoảng đầu tiên
            start, end = interval
            
            # Đảm bảo khoảng nằm trong domain hợp lệ và là số nguyên
            actual_start = max(round(start), domain_min) if start != float('-inf') else domain_min
            actual_end = min(round(end), domain_max) if end != float('inf') else domain_max
            
            # Kiểm tra tính hợp lệ của khoảng
            if actual_start >= domain_min and actual_end <= domain_max and actual_start < actual_end:
                return f"từ {context['time_unit']} thứ {actual_start} đến {actual_end}"
            else:
                return "không có khoảng thời gian nào"
        else:
            return "không có khoảng thời gian nào"

    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý dựa trên ngữ cảnh."""
        context = self.parameters['context']
        monotonicity = self.parameters['monotonicity']
        increasing_intervals = self.parameters['increasing_intervals']
        decreasing_intervals = self.parameters['decreasing_intervals']
        constraints = context.get('constraints', {})
        
        # Lấy ràng buộc domain
        domain_min = constraints.get('domain_min', float('-inf'))
        domain_max = constraints.get('domain_max', float('inf'))

        # Lấy đáp án đúng
        correct_intervals = increasing_intervals if monotonicity == "tăng" else decreasing_intervals
        wrong_intervals = decreasing_intervals if monotonicity == "tăng" else increasing_intervals

        wrong_answers = []

        # Đáp án sai 1: Ngược lại với đáp án đúng (lấy khoảng đầu tiên)
        if wrong_intervals:
            interval = wrong_intervals[0]  # Lấy khoảng đầu tiên
            start, end = interval
            
            # Đảm bảo khoảng nằm trong domain hợp lệ và là số nguyên
            actual_start = max(round(start), domain_min) if start != float('-inf') else domain_min
            actual_end = min(round(end), domain_max) if end != float('inf') else domain_max
            
            if actual_start < actual_end and actual_start >= domain_min:
                wrong_answers.append(f"từ {context['time_unit']} thứ {actual_start} đến {actual_end}")

        # Đáp án sai 2 & 3: Khoảng sai lệch từ đáp án đúng
        if correct_intervals:
            interval = correct_intervals[0]  # Lấy khoảng đầu tiên
            start, end = interval

            # Sai lệch khoảng thời gian nhưng đảm bảo >= domain_min và là số nguyên
            if start != float('-inf') and end != float('inf'):
                wrong_start = max(round(start) + 1, domain_min)
                wrong_end = round(end) - 1
                if wrong_start < wrong_end and wrong_start >= domain_min:
                    wrong_answers.append(
                        f"từ {context['time_unit']} thứ {wrong_start} đến {wrong_end}")

                # Mở rộng khoảng nhưng đảm bảo >= domain_min và là số nguyên
                extended_start = max(round(start) - 2, domain_min)
                extended_end = min(round(end) + 2, domain_max)
                if extended_start < extended_end and extended_start >= domain_min:
                    wrong_answers.append(
                        f"từ {context['time_unit']} thứ {extended_start} đến {extended_end}")

        # Đảm bảo có đủ 3 đáp án sai bằng cách tạo thêm đáp án hợp lý
        while len(wrong_answers) < 3:
            # Tạo đáp án sai ngẫu nhiên trong domain với số nguyên
            if domain_min >= 0:  # Ngữ cảnh thời gian
                # Tạo khoảng ngẫu nhiên từ 0 đến domain_max với số nguyên
                start_options = [0, 1, 2, 3, 4, 5]
                end_options = [domain_max//2, domain_max-1, domain_max, domain_max+1, domain_max+2]
                
                # Lọc để đảm bảo start < end và trong domain hợp lý
                valid_starts = [int(s) for s in start_options if s >= domain_min and s <= domain_max-1]
                valid_ends = [int(e) for e in end_options if e >= domain_min+1 and e <= domain_max]
                
                if valid_starts and valid_ends:
                    start = random.choice(valid_starts)
                    end = random.choice([e for e in valid_ends if e > start])
                    candidate = f"từ {context['time_unit']} thứ {start} đến {end}"
                    
                    # Đảm bảo không trùng với các đáp án đã có
                    if candidate not in wrong_answers and candidate != self.correct_answer:
                        wrong_answers.append(candidate)
                    else:
                        # Nếu trùng, tạo khoảng khác
                        start = random.randint(domain_min, domain_max-1)
                        end = random.randint(start+1, domain_max)
                        wrong_answers.append(f"từ {context['time_unit']} thứ {start} đến {end}")
                else:
                    # Fallback nếu không tạo được khoảng hợp lý
                    wrong_answers.append(f"từ {context['time_unit']} thứ 0 đến {domain_max//2}")
            else:
                # Trường hợp domain không có ràng buộc thời gian
                wrong_answers.append(f"không có {context['time_unit']} nào")

        return wrong_answers[:3]

    def generate_question_text(self) -> str:
        """Sinh đề bài với ngữ cảnh thực tế đa dạng."""
        context = self.parameters['context']
        function_type = self.parameters['function_type']
        monotonicity = self.parameters['monotonicity']
        var = context['variable']  # Sử dụng biến đã được random
        constraints = context.get('constraints', {})
        
        # Lấy giới hạn thời gian từ constraints
        domain_max = constraints.get('domain_max', 20)
        time_limit_text = f"trong {domain_max} {context['time_unit']} đầu"

        # Tạo biểu thức hàm số
        if function_type == 'rational':
            a, b, c, d, e = self.parameters['a'], self.parameters['b'], self.parameters['c'], self.parameters['d'], \
            self.parameters['e']
            function_latex = format_rational_for_latex(a, b, c, d, e, var)
        elif function_type == 'polynomial_3':
            a, b, c, d = self.parameters['a'], self.parameters['b'], self.parameters['c'], self.parameters['d']
            function_latex = format_polynomial([a, b, c, d], var)
        elif function_type == 'polynomial_4':
            a, b, c = self.parameters['a'], self.parameters['b'], self.parameters['c']
            function_latex = format_polynomial([a, 0, b, 0, c], var)

        # Tạo câu hỏi dựa trên loại với giới hạn thời gian rõ ràng
        if context['question_type'] == 'velocity_from_distance':
            question_text = f"""{context['description']} \\(s({var}) = {function_latex}\\) ({context['unit']}) sau \\({var}\\) {context['time_unit']}. 
            Vận tốc tức thời của vật tại thời điểm \\({var}\\) là \\(v({var}) = s'({var})\\). 
            Hỏi vận tốc của vật {monotonicity} trong khoảng thời gian nào {time_limit_text}?"""
        else:
            question_text = f"""{context['description']} \\(f({var}) = {function_latex}\\) ({context['unit']}) sau \\({var}\\) {context['time_unit']}. 
            Hỏi {context['subject']} {monotonicity} trong khoảng thời gian nào {time_limit_text}?"""

        return question_text

    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết dựa trên ngữ cảnh với template tối ưu."""
        context = self.parameters['context']
        function_type = self.parameters['function_type']
        monotonicity = self.parameters['monotonicity']
        var = context['variable']
        constraints = context.get('constraints', {})
        
        # Tạo các thành phần solution theo context
        function_description = self._get_function_description(context)
        domain_constraint_text = self._get_domain_constraint_text(context, constraints)
        physical_interpretation = self._get_physical_interpretation(context, monotonicity)
        conclusion = self._get_conclusion(context, monotonicity)
        
        # Tạo biểu thức hàm số và tính đạo hàm
        if function_type == 'rational':
            return self._generate_rational_solution(context, function_description, domain_constraint_text, 
                                                   physical_interpretation, conclusion, var)
        elif function_type == 'polynomial_3':
            return self._generate_polynomial_3_solution(context, function_description, domain_constraint_text,
                                                       physical_interpretation, conclusion, var)
        elif function_type == 'polynomial_4':
            return self._generate_polynomial_4_solution(context, function_description, domain_constraint_text,
                                                       physical_interpretation, conclusion, var)
        
        return ""

    def _get_function_description(self, context) -> str:
        """Lấy mô tả hàm số theo context."""
        context_descriptions = {
            'velocity': 'vận tốc của xe',
            'bacteria': 'tốc độ phát triển của quần thể vi khuẩn',
            'distance': 'quãng đường di chuyển của vật',
            'population': 'tốc độ tăng dân số của thành phố',
            'economy': 'tốc độ tăng trưởng kinh tế của quốc gia'
        }
        return context_descriptions.get(context['name']) or context.get('subject') or 'hàm số'

    def _get_domain_constraint_text(self, context, constraints) -> str:
        """Lấy text giải thích ràng buộc domain."""
        physical_meaning = constraints.get('physical_meaning', '')
        if physical_meaning:
            if context['name'] in ['velocity', 'bacteria', 'distance', 'population', 'economy']:
                return f"Với điều kiện {physical_meaning} (theo ngữ cảnh thực tế)."
            else:
                return f"Với điều kiện {physical_meaning}."
        return ""

    def _get_physical_interpretation(self, context, monotonicity) -> str:
        """Lấy giải thích ý nghĩa vật lý theo context."""
        interpretations = {
            'velocity': {
                'tăng': 'Khi đạo hàm f\'(t) > 0, gia tốc dương có nghĩa là xe tăng tốc.',
                'giảm': 'Khi đạo hàm f\'(t) < 0, gia tốc âm có nghĩa là xe giảm tốc.'
            },
            'bacteria': {
                'tăng': 'Khi đạo hàm f\'(t) > 0, tốc độ phát triển tăng có nghĩa là quần thể phát triển nhanh hơn.',
                'giảm': 'Khi đạo hàm f\'(t) < 0, tốc độ phát triển giảm có nghĩa là quần thể phát triển chậm lại.'
            },
            'distance': {
                'tăng': 'Khi đạo hàm v\'(t) > 0, gia tốc dương có nghĩa là vật tăng tốc.',
                'giảm': 'Khi đạo hàm v\'(t) < 0, gia tốc âm có nghĩa là vật giảm tốc.'
            },
            'population': {
                'tăng': 'Khi đạo hàm f\'(t) > 0, tốc độ tăng dân số tăng có nghĩa là dân số gia tăng nhanh hơn.',
                'giảm': 'Khi đạo hàm f\'(t) < 0, tốc độ tăng dân số giảm có nghĩa là dân số gia tăng chậm lại.'
            },
            'economy': {
                'tăng': 'Khi đạo hàm f\'(t) > 0, tốc độ tăng trưởng kinh tế tăng có nghĩa là nền kinh tế phát triển nhanh hơn.',
                'giảm': 'Khi đạo hàm f\'(t) < 0, tốc độ tăng trưởng kinh tế giảm có nghĩa là nền kinh tế phát triển chậm lại.'
            }
        }
        return interpretations.get(context['name'], {}).get(monotonicity, '')

    def _get_conclusion(self, context, monotonicity) -> str:
        """Lấy kết luận theo context."""
        return f"Vậy {context['subject']} {monotonicity} trong khoảng {context['time_unit']} được chỉ ra ở đáp án."

    def _generate_solution_by_function_type(self, context, function_description, domain_constraint_text,
                                          physical_interpretation, conclusion, var) -> str:
        """Sinh lời giải thống nhất cho tất cả các loại hàm số."""
        function_type = self.parameters['function_type']
        
        # Bước 1: Khởi tạo hàm số và thông tin cơ bản
        function_info = self._get_function_and_derivative_info(function_type, var)
        
        # Bước 2: Template chung cho tất cả loại hàm
        solution_template = """Ta có {function_intro}: \\({function_symbol}({var}) = {function_latex}\\) ({unit}).

{domain_info}
{domain_constraint_text}

{derivative_section}

{critical_points_section}

{discontinuity_section}

{physical_interpretation}

Lập bảng xét dấu cho \\({derivative_symbol}'({var})\\) và kết luận: {conclusion}"""

        # Bước 3: Điền thông tin vào template
        solution = solution_template.format(
            function_intro=function_info['function_intro'],
            function_symbol=function_info['function_symbol'], 
            var=var,
            function_latex=function_info['function_latex'],
            unit=context['unit'],
            domain_info=function_info['domain_info'],
            domain_constraint_text=domain_constraint_text,
            derivative_section=function_info['derivative_section'],
            critical_points_section=function_info['critical_points_section'],
            discontinuity_section=function_info['discontinuity_section'],
            physical_interpretation=physical_interpretation,
            derivative_symbol=function_info['derivative_symbol'],
            conclusion=conclusion
        )
        
        return solution

    def _get_function_and_derivative_info(self, function_type, var) -> dict:
        """Lấy thông tin chi tiết về hàm số và đạo hàm theo từng loại."""
        context = self.parameters['context']
        
        if function_type == 'rational':
            return self._get_rational_function_info(var)
        elif function_type == 'polynomial_3':
            return self._get_polynomial_3_info(var)
        elif function_type == 'polynomial_4':
            return self._get_polynomial_4_info(var)
        else:
            raise ValueError(f"Unsupported function type: {function_type}")

    def _get_rational_function_info(self, var) -> dict:
        """Thông tin chi tiết cho hàm phân thức."""
        context = self.parameters['context']
        a, b, c, d, e = self.parameters['a'], self.parameters['b'], self.parameters['c'], self.parameters['d'], self.parameters['e']
        function_latex = format_rational_for_latex(a, b, c, d, e, var)
        x_p = self.parameters['x_p']
        x1, x2 = self.parameters['critical_points']

        # Tính đạo hàm
        A_prime = a * d
        B_prime = 2 * a * e
        C_prime = b * e - c * d
        
        # Format tử số của đạo hàm
        derivative_num_terms = []
        if A_prime != 0:
            if A_prime == 1:
                derivative_num_terms.append(f"{var}^2")
            elif A_prime == -1:
                derivative_num_terms.append(f"-{var}^2")
            else:
                derivative_num_terms.append(f"{A_prime}{var}^2")
        
        if B_prime != 0:
            if B_prime == 1:
                derivative_num_terms.append(f"+{var}")
            elif B_prime == -1:
                derivative_num_terms.append(f"-{var}")
            else:
                derivative_num_terms.append(f"+{B_prime}{var}" if B_prime > 0 else f"{B_prime}{var}")
        
        if C_prime != 0:
            derivative_num_terms.append(f"+{C_prime}" if C_prime > 0 else f"{C_prime}")
        
        derivative_numerator = "".join(derivative_num_terms)
        if derivative_numerator.startswith("+"):
            derivative_numerator = derivative_numerator[1:]
        derivative_numerator = derivative_numerator or "0"
        
        # Format mẫu số của đạo hàm
        denom_terms = []
        if d != 0:
            if d == 1:
                denom_terms.append(f"{var}")
            elif d == -1:
                denom_terms.append(f"-{var}")
            else:
                denom_terms.append(f"{d}{var}")
        if e != 0:
            denom_terms.append(f"+{e}" if e > 0 else f"{e}")
        derivative_denominator = "".join(denom_terms)
        if derivative_denominator.startswith("+"):
            derivative_denominator = derivative_denominator[1:]
        
        derivative_latex = f"\\frac{{{clean_sign_expression(derivative_numerator)}}}{{\\left({clean_sign_expression(derivative_denominator)}\\right)^2}}"

        return {
            'function_intro': self._get_function_description(context),
            'function_symbol': 'f',
            'function_latex': function_latex,
            'domain_info': f"Tập xác định: \\(D = \\mathbb{{R}} \\setminus \\{{{x_p}\\}}\\).",
            'derivative_section': f"Tính đạo hàm:\n\\(f'({var}) = \\frac{{d}}{{d{var}}}\\left({function_latex}\\right) = {derivative_latex}\\)",
            'critical_points_section': f"\\(f'({var}) = 0 \\Leftrightarrow {clean_sign_expression(derivative_numerator)} = 0\\)\n\n\\(\\Leftrightarrow {var}_1 = {x1}, {var}_2 = {x2}\\).",
            'discontinuity_section': f"Điểm gián đoạn: \\({var} = {x_p}\\).",
            'derivative_symbol': 'f'
        }

    def _get_polynomial_3_info(self, var) -> dict:
        """Thông tin chi tiết cho hàm bậc 3."""
        context = self.parameters['context']
        a, b, c, d = self.parameters['a'], self.parameters['b'], self.parameters['c'], self.parameters['d']
        function_latex = format_polynomial([a, b, c, d], var)
        critical_points = self.parameters['critical_points']

        derivative_latex = format_polynomial([3 * a, 2 * b, c], var)

        return {
            'function_intro': self._get_function_description(context),
            'function_symbol': 'f',
            'function_latex': function_latex,
            'domain_info': "Tập xác định: \\(D = \\mathbb{R}\\).",
            'derivative_section': f"Tính đạo hàm:\n\\(f'({var}) = {derivative_latex}\\)",
            'critical_points_section': f"Giải phương trình \\(f'({var}) = 0\\), ta được các điểm tới hạn:\n\\({var}_1 = {critical_points[0]}, {var}_2 = {critical_points[1]}\\).",
            'discontinuity_section': "",  # Không có điểm gián đoạn
            'derivative_symbol': 'f'
        }

    def _get_polynomial_4_info(self, var) -> dict:
        """Thông tin chi tiết cho hàm bậc 4."""
        context = self.parameters['context']
        a, b, c = self.parameters['a'], self.parameters['b'], self.parameters['c']
        function_latex = format_polynomial([a, 0, b, 0, c], var)
        critical_points = self.parameters['critical_points']

        if context['question_type'] == 'velocity_from_distance':
            # Trường hợp đặc biệt: quãng đường → vận tốc → gia tốc
            velocity_latex = format_polynomial([4 * a, 0, 2 * b, 0], var)
            acceleration_latex = format_polynomial([12 * a, 0, 2 * b], var)
            
            return {
                'function_intro': "quãng đường",
                'function_symbol': 's',
                'function_latex': function_latex,
                'domain_info': "",  # Sẽ được thêm vào domain_constraint_text
                'derivative_section': f"Vận tốc tức thời: \\(v({var}) = s'({var}) = {velocity_latex}\\) (m/s).\n\nTính đạo hàm của vận tốc (gia tốc):\n\\(v'({var}) = {acceleration_latex}\\)",
                'critical_points_section': f"Giải phương trình \\(v'({var}) = 0\\), ta được các điểm tới hạn của vận tốc.",
                'discontinuity_section': "",  # Không có điểm gián đoạn
                'derivative_symbol': 'v'
            }
        else:
            # Trường hợp thông thường
            derivative_latex = format_polynomial([4 * a, 0, 2 * b, 0], var)
            
            return {
                'function_intro': self._get_function_description(context),
                'function_symbol': 'f',
                'function_latex': function_latex,
                'domain_info': "Tập xác định: \\(D = \\mathbb{R}\\).",
                'derivative_section': f"Tính đạo hàm:\n\\(f'({var}) = {derivative_latex}\\)",
                'critical_points_section': f"Giải phương trình \\(f'({var}) = 0\\), ta được các điểm tới hạn.",
                'discontinuity_section': "",  # Không có điểm gián đoạn
                'derivative_symbol': 'f'
            }

    def _generate_rational_solution(self, context, function_description, domain_constraint_text,
                                   physical_interpretation, conclusion, var) -> str:
        """Wrapper cho compatibility - sử dụng hàm thống nhất."""
        return self._generate_solution_by_function_type(context, function_description, domain_constraint_text,
                                                       physical_interpretation, conclusion, var)

    def _generate_polynomial_3_solution(self, context, function_description, domain_constraint_text,
                                       physical_interpretation, conclusion, var) -> str:
        """Wrapper cho compatibility - sử dụng hàm thống nhất."""
        return self._generate_solution_by_function_type(context, function_description, domain_constraint_text,
                                                       physical_interpretation, conclusion, var)

    def _generate_polynomial_4_solution(self, context, function_description, domain_constraint_text,
                                       physical_interpretation, conclusion, var) -> str:
        """Wrapper cho compatibility - sử dụng hàm thống nhất."""
        return self._generate_solution_by_function_type(context, function_description, domain_constraint_text,
                                                       physical_interpretation, conclusion, var)

    def _filter_intervals_by_domain(self, intervals, domain_min, domain_max):
        """Lọc các khoảng theo giới hạn domain và trả về số nguyên."""
        filtered_intervals = []
        for start, end in intervals:
            # Điều chỉnh khoảng theo domain constraints và làm tròn gần nhất về số nguyên
            actual_start = max(round(start), domain_min) if start != float('-inf') else domain_min
            actual_end = min(round(end), domain_max) if end != float('inf') else domain_max
            
            # Chỉ giữ khoảng nếu có độ dài dương và nằm trong domain hợp lệ
            if actual_start < actual_end and actual_start >= domain_min and actual_end <= domain_max:
                filtered_intervals.append((actual_start, actual_end))
        
        return filtered_intervals

    def _check_function_positivity(self, a, b, c, d, e, domain_min, domain_max):
        """Kiểm tra tính dương của hàm phân thức f(x) = (ax² + bx + c)/(dx + e) trên domain."""
        # Kiểm tra một số điểm mẫu trong domain
        test_points = [domain_min, domain_max]
        
        # Thêm điểm giữa domain
        mid_point = (domain_min + domain_max) / 2
        test_points.append(mid_point)
        
        # Thêm thêm điểm để kiểm tra kỹ hơn
        step = (domain_max - domain_min) / 10
        for i in range(1, 10):
            test_points.append(domain_min + i * step)
        
        # Kiểm tra tính dương tại các điểm test
        for x in test_points:
            if domain_min <= x <= domain_max:
                try:
                    denominator = d * x + e
                    if abs(denominator) < 1e-10:  # Tránh chia cho 0
                        continue
                    numerator = a * x * x + b * x + c
                    function_value = numerator / denominator
                    if function_value <= 0:
                        return False
                except:
                    continue
        
        return True

    def _evaluate_polynomial(self, coeffs, x):
        """Tính giá trị của đa thức tại x."""
        result = 0
        for i, coeff in enumerate(coeffs):
            result += coeff * (x ** i)
        return result

    def _check_polynomial_constraints(self, coeffs, domain_min, domain_max, constraints):
        """Kiểm tra ràng buộc cho đa thức."""
        # Kiểm tra một số điểm mẫu trong domain
        test_points = [domain_min, domain_max]
        
        # Thêm điểm giữa domain
        mid_point = (domain_min + domain_max) / 2
        test_points.append(mid_point)
        
        # Thêm thêm điểm để kiểm tra kỹ hơn
        step = (domain_max - domain_min) / 10
        for i in range(1, 10):
            test_points.append(domain_min + i * step)
        
        value_min = constraints.get("value_min", float('-inf'))
        value_max = constraints.get("value_max", float('inf'))
        must_be_positive = constraints.get("must_be_positive", False)
        
        # Kiểm tra tại các điểm test
        for x in test_points:
            if domain_min <= x <= domain_max:
                try:
                    function_value = self._evaluate_polynomial(coeffs, x)
                    
                    # Kiểm tra ràng buộc giá trị
                    if function_value < value_min or function_value > value_max:
                        return False
                    
                    # Kiểm tra ràng buộc tính dương
                    if must_be_positive and function_value <= 0:
                        return False
                        
                except:
                    continue
        
        return True

    def get_context_description(self) -> str:
        """Lấy mô tả ngữ cảnh với ràng buộc vật lý."""
        context = self.parameters['context']
        constraints = context.get('constraints', {})
        
        description = context['description']
        
        # Thêm thông tin ràng buộc vật lý vào mô tả
        if constraints.get('physical_meaning'):
            description += f" (với điều kiện: {constraints['physical_meaning']})"
        
        return description
# ███████████████████████████████████████████████████████████████████████████████
# ██                        PHẦN 6: GENERATOR CHÍNH                            ██
# ███████████████████████████████████████████████████████████████████████████████

class OptimizationGenerator:
    """
    Generator chính để tạo câu hỏi tối ưu hóa
    Quản lý tất cả các dạng toán và tạo document LaTeX
    """

    # Danh sách các dạng toán có sẵn
    QUESTION_TYPES = [
        RationalQuadraticMonotonicity,
        # ===== THÊM DẠNG TOÁN MỚI VÀO DANH SÁCH NÀY =====
    ]

    @classmethod
    def generate_question(cls, question_number: int,
                          question_type=None) -> str:
        """
           Tạo một câu hỏi cụ thể

           Args:
               question_number: Số thứ tự câu hỏi
               question_type: Loại câu hỏi (None = ngẫu nhiên)

           Returns:
               Chuỗi chứa câu hỏi hoàn chỉnh
           """
        if question_type is None:
            question_type = random.choice(cls.QUESTION_TYPES)

        try:
            question_instance = question_type()
            return question_instance.generate_full_question(question_number)
        except Exception as e:
            logging.error(f"Lỗi tạo câu hỏi {question_number}: {e}")
            raise

    @classmethod
    def generate_multiple_questions(cls, num_questions: int = 5) -> List[str]:
        """
        Tạo nhiều câu hỏi

        Args:
            num_questions: Số lượng câu hỏi cần tạo

        Returns:
            Danh sách câu hỏi
        """
        questions = []
        for i in range(1, num_questions + 1):
            try:
                question = cls.generate_question(i)
                questions.append(question)
                logging.info(f"Đã tạo thành công câu hỏi {i}")
            except Exception as e:
                logging.error(f"Lỗi tạo câu hỏi {i}: {e}")
                continue

        return questions

    @classmethod
    def generate_multiple_questions_with_format(cls, num_questions: int = 5, fmt: int = 1):
        """Tạo nhiều câu hỏi với format cụ thể"""
        if fmt == 1:
            return cls.generate_multiple_questions(num_questions)
        else:
            questions_data = []
            for i in range(1, num_questions + 1):
                try:
                    question_type = random.choice(cls.QUESTION_TYPES)
                    question_instance = question_type()
                    question_content, correct_answer = question_instance.generate_question_only(i)
                    questions_data.append((question_content, correct_answer))
                    logging.info(f"Đã tạo thành công câu hỏi {i}")
                except Exception as e:
                    logging.error(f"Lỗi tạo câu hỏi {i}: {e}")
                    continue
            return questions_data

    @classmethod
    def create_latex_file(cls, questions: List[str],
                          filename: str = "questions.tex",
                          title: str = "Câu hỏi") -> str:
        """
        Tạo file LaTeX hoàn chỉnh

        Args:
            questions: Danh sách câu hỏi
            filename: Tên file xuất ra
            title: Tiêu đề document

        Returns:
            Tên file đã tạo
        """
        latex_content = BaseOptimizationQuestion.create_latex_document(questions, title)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(latex_content)
            logging.info(f"Đã tạo file LaTeX: {filename}")
            return filename
        except Exception as e:
            logging.error(f"Lỗi ghi file {filename}: {e}")
            raise

    @classmethod
    def create_latex_file_with_format(cls, questions_data,
                                      filename: str = "questions.tex",
                                      title: str = "Câu hỏi", fmt: int = 1) -> str:
        """
        Tạo file LaTeX với format cụ thể

        Args:
            questions: Danh sách câu hỏi
            filename: Tên file xuất ra
            title: Tiêu đề document
            fmt: Format của câu hỏi (1 là ABCD hoặc 2 là câu hỏi + lời giải, đáp án ở cuối)

        Returns:
            Tên file đã tạo
        """
        latex_content = BaseOptimizationQuestion.create_latex_document_with_format(questions_data, title, fmt)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(latex_content)
            logging.info(f"Đã tạo file LaTeX: {filename}")
            return filename
        except Exception as e:
            logging.error(f"Lỗi ghi file {filename}: {e}")
            raise


# ███████████████████████████████████████████████████████████████████████████████
# ██                             PHẦN 7: HÀM MAIN                              ██
# ███████████████████████████████████████████████████████████████████████████████

def main():
    """
    Hàm main để chạy generator với hỗ trợ 2 format
    Cách sử dụng:
    python math_optimization_template.py [số_câu] [format]
    """
    try:
        # Lấy tham số từ command line
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        fmt = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] in ['1', '2'] else 1

        # Tạo generator và sinh câu hỏi
        generator = OptimizationGenerator()
        questions_data = generator.generate_multiple_questions_with_format(num_questions, fmt)

        if not questions_data:
            print("Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)

        # Tạo file LaTeX
        filename = generator.create_latex_file_with_format(questions_data, fmt=fmt)

        print(f"✅ Đã tạo thành công {filename} với {len(questions_data)} câu hỏi")
        print(f"📄 Biên dịch bằng: xelatex {filename}")
        print(f"📋 Format: {fmt} ({'đáp án ngay sau câu hỏi' if fmt == 1 else 'đáp án ở cuối'})")

    except ValueError:
        print("❌ Lỗi: Vui lòng nhập số câu hỏi hợp lệ hợp lệ")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


"""
🚀 HƯỚNG DẪN THÊM DẠNG TOÁN MỚI:

1. Tạo class mới kế thừa BaseOptimizationQuestion
2. Implement 5 method bắt buộc:
   - generate_parameters(): Sinh tham số
   - calculate_answer(): Tính đáp án đúng  
   - generate_wrong_answers(): Sinh đáp án sai
   - generate_question_text(): Sinh đề bài
   - generate_solution(): Sinh lời giải

3. Thêm class vào OptimizationGenerator.QUESTION_TYPES

🎨 HƯỚNG DẪN THÊM HÌNH VẼ MỚI:

1. Thêm static method vào TikZFigureLibrary
2. Return chuỗi TikZ code
3. Sử dụng trong generate_question_text()

📝 HƯỚNG DẪN THÊM FORMAT MỚI:

1. Thêm hàm format vào phần "THÊM FORMAT LATEX MỚI"
2. Sử dụng trong các method generate_*

💡 MẸO HAY:
- Test từng dạng toán riêng biệt trước khi thêm vào danh sách chính
- Sử dụng logging để debug
- Tham khảo PoolOptimization và LineIntersectionOptimization như ví dụ mẫu
"""
