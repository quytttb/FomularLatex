"""
Dạng bài toán: Tìm khoảng đồng biến, nghịch biến của hàm số
"""

import random
import sys
import logging  
import re
from abc import ABC, abstractmethod
from fractions import Fraction
from typing import List, Dict, Any, Union
from math import gcd as math_gcd, sqrt, floor, log10

# Constants
DEFAULT_DOMAIN_MIN = -5
DEFAULT_DOMAIN_MAX = 5
MAX_ATTEMPTS = 200

# Context configurations for different problem types
CONTEXTS_CONFIG = [
    {
        "name": "bacteria",
        "function_type": "polynomial_3",  # bậc 3
        "subject": "tốc độ phát triển vi khuẩn",
        "unit": "nghìn con/giờ",
        "time_unit": "giờ",
        "question_type": "growth_rate",
        "description": "Tốc độ phát triển của một quần thể vi khuẩn được mô tả bởi hàm số",
        "constraints": {
            "domain_min": 0,  # Thời gian không âm
            "domain_max": 10,  # Giảm từ 48 xuống 10 giờ
            "value_min": -100,  # Cho phép giá trị âm
            "value_max": 1000,  # Tốc độ tối đa hợp lý
            "must_be_positive": False,  # Tạm thời không yêu cầu dương
            "physical_meaning": "Thời gian t \\(\\geq\\) 0"
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
        "constraints": {
            "domain_min": 0,  # Thời gian không âm (năm 0 là mốc)
            "domain_max": 10,  # Giảm từ 50 xuống 10 năm
            "value_min": -10000,  # Cho phép giảm dân số
            "value_max": 50000,  # Tốc độ tăng tối đa hợp lý
            "must_be_positive": False,  # Dân số có thể giảm
            "physical_meaning": "Thời gian t \\(\\geq\\) 0"
        }
    },
    {
        "name": "velocity",
        "function_type": "polynomial_3",  # bậc 3
        "subject": "vận tốc của vật thể",
        "unit": "m/s",
        "time_unit": "giây",
        "question_type": "velocity_analysis",
        "description": "Vận tốc của một vật thể chuyển động được mô tả bởi hàm số",
        "constraints": {
            "domain_min": 0,  # Thời gian không âm
            "domain_max": 20,  # Trong 20 giây đầu
            "value_min": -50,  # Cho phép vận tốc âm (chuyển động ngược)
            "value_max": 100,  # Vận tốc tối đa hợp lý
            "must_be_positive": False,  # Vận tốc có thể âm
            "physical_meaning": "Thời gian t \\(\\geq\\) 0"
        }
    },
    {
        "name": "distance",
        "function_type": "polynomial_3",  # bậc 3
        "subject": "tốc độ thay đổi quãng đường",
        "unit": "km/h",
        "time_unit": "giờ",
        "question_type": "distance_rate",
        "description": "Tốc độ thay đổi quãng đường của một xe được mô tả bởi hàm số",
        "constraints": {
            "domain_min": 0,  # Thời gian không âm
            "domain_max": 12,  # Trong 12 giờ đầu
            "value_min": -20,  # Cho phép giảm tốc
            "value_max": 80,  # Tốc độ tối đa hợp lý
            "must_be_positive": False,  # Tốc độ có thể giảm
            "physical_meaning": "Thời gian t \\(\\geq\\) 0"
        }
    },
    {
        "name": "economy",
        "function_type": "polynomial_3",  # bậc 3
        "subject": "tốc độ tăng trưởng kinh tế",
        "unit": "%/năm",
        "time_unit": "năm",
        "question_type": "economic_growth",
        "description": "Tốc độ tăng trưởng kinh tế của một quốc gia được mô tả bởi hàm số",
        "constraints": {
            "domain_min": 0,  # Năm 0 là mốc
            "domain_max": 15,  # Trong 15 năm đầu
            "value_min": -10,  # Cho phép suy thoái
            "value_max": 20,  # Tăng trưởng tối đa hợp lý
            "must_be_positive": False,  # Kinh tế có thể suy thoái
            "physical_meaning": "Thời gian t \\(\\geq\\) 0"
        }
    }
]

# Context helper mappings for solution generation
CONTEXT_DESCRIPTIONS = {
    'bacteria': 'tốc độ phát triển của quần thể vi khuẩn',
    'population': 'tốc độ tăng dân số của thành phố',
    'velocity': 'vận tốc của vật thể',
    'distance': 'tốc độ thay đổi quãng đường của xe',
    'economy': 'tốc độ tăng trưởng kinh tế của quốc gia'
}

PHYSICAL_INTERPRETATIONS = {
    'bacteria': {
        'tăng': 'Khi đạo hàm f\'(t) > 0, tốc độ phát triển tăng có nghĩa là quần thể phát triển nhanh hơn.',
        'giảm': 'Khi đạo hàm f\'(t) < 0, tốc độ phát triển giảm có nghĩa là quần thể phát triển chậm lại.'
    },
    'population': {
        'tăng': 'Khi đạo hàm f\'(t) > 0, tốc độ tăng dân số tăng có nghĩa là dân số gia tăng nhanh hơn.',
        'giảm': 'Khi đạo hàm f\'(t) < 0, tốc độ tăng dân số giảm có nghĩa là dân số gia tăng chậm lại.'
    },
    'velocity': {
        'tăng': 'Khi đạo hàm f\'(t) > 0, vận tốc tăng có nghĩa là vật thể chuyển động nhanh dần.',
        'giảm': 'Khi đạo hàm f\'(t) < 0, vận tốc giảm có nghĩa là vật thể chuyển động chậm dần.'
    },
    'distance': {
        'tăng': 'Khi đạo hàm f\'(t) > 0, tốc độ thay đổi quãng đường tăng có nghĩa là xe chạy nhanh dần.',
        'giảm': 'Khi đạo hàm f\'(t) < 0, tốc độ thay đổi quãng đường giảm có nghĩa là xe chạy chậm dần.'
    },
    'economy': {
        'tăng': 'Khi đạo hàm f\'(t) > 0, tốc độ tăng trưởng kinh tế tăng có nghĩa là nền kinh tế phát triển nhanh hơn.',
        'giảm': 'Khi đạo hàm f\'(t) < 0, tốc độ tăng trưởng kinh tế giảm có nghĩa là nền kinh tế phát triển chậm lại.'
    }
}


# PHẦN 1: CÁC HÀM TIỆN ÍCH VÀ FORMAT LATEX

# HÀM TIỆN ÍCH TOÁN HỌC

def gcd_custom(a, b):
    """Tính ước chung lớn nhất của a và b - sử dụng math.gcd."""
    return math_gcd(abs(a), abs(b))


def simplify_fraction(num, denom):
    """Rút gọn phân số bằng cách chia tử số và mẫu số cho ước chung lớn nhất."""
    if denom < 0:
        num, denom = -num, -denom
    if num == 0:
        return 0, 1
    g = gcd_custom(num, denom)
    return num // g, denom // g


def is_perfect_square(n):
    """Kiểm tra xem n có phải là số chính phương hay không."""
    sqrt_n = int(n ** 0.5)
    return sqrt_n * sqrt_n == n


# HÀM FORMAT SỐ VÀ PHÂN SỐ

def format_number_clean(value, precision=2, format_type="normal", unit=""):
    """Format số sạch với nhiều loại format - gộp các hàm format"""
    try:
        fval = float(value)
        
        # Format khoa học
        if format_type == "scientific":
            if abs(fval) < 1e-10:
                return "0"
            exponent = int(floor(log10(abs(fval))))
            mantissa = fval / (10 ** exponent)
            if exponent == 0:
                return f"{mantissa:.{precision}f}".rstrip('0').rstrip('.')
            else:
                return f"{mantissa:.{precision}f} \\times 10^{{{exponent}}}"
        
        # Format căn bậc hai
        elif format_type == "sqrt":
            if fval == int(fval) and int(fval) >= 0:
                sqrt_val = sqrt(fval)
                if sqrt_val == int(sqrt_val):
                    return f"{int(sqrt_val)}"
                else:
                    return f"\\sqrt{{{int(fval)}}}"
            else:
                return f"\\sqrt{{{fval}}}"
        
        # Format với đơn vị
        elif format_type == "dimension" and unit:
            if abs(fval - round(fval)) < 1e-10:
                return f"{int(round(fval))} {unit}"
            else:
                formatted = f"{fval:.1f}"
                if formatted.endswith('.0'):
                    formatted = formatted[:-2]
                return f"{formatted} {unit}"
        
        # Format thông thường
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
    """Format tọa độ chuẩn cho lời giải với phân số LaTeX đẹp"""
    if isinstance(coord, Fraction):
        num, denom = simplify_fraction(coord.numerator, coord.denominator)
        if denom == 1:
            return str(num)
        else:
            # Sử dụng \frac thay vì \dfrac cho consistency
            return f"\\frac{{{num}}}{{{denom}}}"

    # Xử lý số thập phân - chuyển sang phân số nếu có thể
    if isinstance(coord, (int, float)):
        # Kiểm tra số nguyên trước
        if abs(coord - round(coord)) < 1e-10:
            return str(int(round(coord)))
            
        # Kiểm tra một số phân số phổ biến với độ chính xác cao
        common_fractions = {
            1/3: "\\frac{1}{3}",
            2/3: "\\frac{2}{3}",
            1/2: "\\frac{1}{2}",
            3/2: "\\frac{3}{2}",
            1/4: "\\frac{1}{4}",
            3/4: "\\frac{3}{4}",
            1/6: "\\frac{1}{6}",
            5/6: "\\frac{5}{6}",
            -1/3: "\\frac{-1}{3}",
            -2/3: "\\frac{-2}{3}",
            -1/2: "\\frac{-1}{2}",
            -3/2: "\\frac{-3}{2}",
            -1/4: "\\frac{-1}{4}",
            -3/4: "\\frac{-3}{4}"
        }
        
        for value, latex in common_fractions.items():
            if abs(coord - value) < 1e-10:
                return latex
        
        # Thử chuyển thành phân số với mẫu số nhỏ
        try:
            frac = Fraction(coord).limit_denominator(100)
            if abs(float(frac) - coord) < 1e-10:
                if frac.denominator == 1:
                    return str(frac.numerator)
                else:
                    return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
        except:
            pass

    # Fallback - format thành số thập phân
    return format_number_clean(coord, precision=4)



# HÀM FORMAT ĐA THỨC VÀ BIỂU THỨC

# Compiled regex patterns for better performance
REGEX_PATTERNS = {
    'double_minus': re.compile(r"-\s*-\s*([\d\w\\(])"),
    'plus_minus': re.compile(r"\+\s*-\s*([\d\w\\(])"),
    'double_plus': re.compile(r"\+\s*\+\s*([\d\w\\(])"),
    'minus_plus': re.compile(r"-\s*\+\s*([\d\w\\(])"),
    'mult_one': re.compile(r"([\d\w\\(\)])\s*([\*\.])\s*1(?![\d\w])"),
    'one_mult': re.compile(r"1\s*([\*\.])\s*([\d\w\\(\)])"),
    'mult_neg_one': re.compile(r"([\d\w\\(\)])\s*([\*\.])\s*-1(?![\d\w])"),
    'neg_one_mult': re.compile(r"-1\s*([\*\.])\s*([\d\w\\(\)])"),
    'div_one': re.compile(r"([\d\w\\(\)])\s*/\s*1(?![\d\w])"),
    'div_neg_one': re.compile(r"([\d\w\\(\)])\s*/\s*-1(?![\d\w])"),
    'plus_zero': re.compile(r"([\d\w\\)\}])\s*([\+\-])\s*0(?![\d\w])"),
    'zero_plus': re.compile(r"0\s*\+\s*([\d\w\\(])"),
    'zero_minus': re.compile(r"0\s*-\s*([\d\w\\(])"),
    'mult_zero': re.compile(r"([\d\w\\(\)])\s*([\*\.])\s*0(?![\d\w])"),
    'zero_mult': re.compile(r"0\s*([\*\.])\s*([\d\w\\(\)])"),
    'triple_minus': re.compile(r"--([\d\w\\(])"),
    'quad_minus': re.compile(r"---([\d\w\\(])"),
    'leading_plus': re.compile(r"^\+\s*([\d\w\\(])"),
    'leading_plus_minus': re.compile(r"^[\+\-]\+([\d\w\\(])"),
    'div_minus': re.compile(r"/\s*-\s*([\d\w\\(])"),
    'whitespace': re.compile(r"\s+")
}


def clean_sign_expression(expr: str) -> str:
    """Chuẩn hóa các biểu thức dấu với compiled regex patterns."""
    # Apply transformations using compiled patterns
    expr = REGEX_PATTERNS['double_minus'].sub(r"+ \1", expr)
    expr = REGEX_PATTERNS['plus_minus'].sub(r"- \1", expr)
    expr = REGEX_PATTERNS['double_plus'].sub(r"+ \1", expr)
    expr = REGEX_PATTERNS['minus_plus'].sub(r"- \1", expr)

    # Multiplication with 1 and -1
    expr = REGEX_PATTERNS['mult_one'].sub(r"\1", expr)
    expr = REGEX_PATTERNS['one_mult'].sub(r"\2", expr)
    expr = REGEX_PATTERNS['mult_neg_one'].sub(r"-\1", expr)
    expr = REGEX_PATTERNS['neg_one_mult'].sub(r"-\2", expr)

    # Division
    expr = REGEX_PATTERNS['div_one'].sub(r"\1", expr)
    expr = REGEX_PATTERNS['div_neg_one'].sub(r"-\1", expr)

    # Addition/subtraction with zero
    expr = REGEX_PATTERNS['plus_zero'].sub(r"\1", expr)
    expr = REGEX_PATTERNS['zero_plus'].sub(r"\1", expr)
    expr = REGEX_PATTERNS['zero_minus'].sub(r"-\1", expr)

    # Multiplication with zero
    expr = REGEX_PATTERNS['mult_zero'].sub(r"0", expr)
    expr = REGEX_PATTERNS['zero_mult'].sub(r"0", expr)

    # Multiple minus signs
    expr = REGEX_PATTERNS['triple_minus'].sub(r"\1", expr)
    expr = REGEX_PATTERNS['quad_minus'].sub(r"-\1", expr)

    # Leading signs
    expr = REGEX_PATTERNS['leading_plus'].sub(r"\1", expr)
    expr = REGEX_PATTERNS['leading_plus_minus'].sub(r"-\1", expr)

    # Division with negative
    expr = REGEX_PATTERNS['div_minus'].sub(r"/ (-\1)", expr)

    # Clean whitespace
    expr = REGEX_PATTERNS['whitespace'].sub(" ", expr).strip()

    return expr


def format_coefficient(coeff, is_first=False, var='x', power=1):
    """Format hệ số với dấu và biến (TỐI ƯU - tái sử dụng simplify_fraction)"""
    if abs(coeff) < 1e-10:  # Use tolerance instead of exact zero
        return ""

    # Tái sử dụng simplify_fraction cho Fraction coefficients
    if isinstance(coeff, Fraction):
        num, denom = simplify_fraction(coeff.numerator, coeff.denominator)
    else:
        # For float coefficients, round to reasonable precision and convert to fraction if needed
        rounded_coeff = round(coeff, 6)  # Keep 6 decimal places
        if abs(rounded_coeff) < 1e-10:  # Use tolerance for zero check
            return ""
        
        # Convert to fraction if it's a simple fraction
        frac = Fraction(rounded_coeff).limit_denominator(1000)
        if frac.denominator <= 10:  # Use fraction for simple denominators
            num, denom = frac.numerator, frac.denominator
        else:
            # Use decimal format for complex fractions
            num, denom = rounded_coeff, 1

    # Additional safety check: if coefficient is 0, skip it
    if (isinstance(num, (int, float)) and abs(num) < 1e-10) or num == 0:
        return ""

    # Format the coefficient part
    if denom == 1:
        if isinstance(num, float):
            coeff_str = str(abs(num)) if abs(num) != 1 or power == 0 else ""
        else:
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
    if not coeffs or all(abs(c) < 1e-10 for c in coeffs):
        return "0"

    terms = []
    degree = len(coeffs) - 1

    for i, coeff in enumerate(coeffs):
        if abs(coeff) < 1e-10:  # Use tolerance instead of exact zero comparison
            continue

        power = degree - i
        term = format_coefficient(coeff, len(terms) == 0, var, power)
        if term:
            terms.append(term)

    if not terms:
        return "0"

    result = "".join(terms)
    return clean_sign_expression(result)


# HÀM TIỆN ÍCH XỬ LÝ CHUỖI

# LỚP CƠ SỞ CHO CÂU HỎI

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
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()

        question_text = self.generate_question_text()
        solution = self.generate_solution()

        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += f"Lời giải:\n\n{solution}\n\n"

        return question_content, self.correct_answer

    @staticmethod
    def create_latex_document(questions: List[str], title: str = "Câu hỏi") -> str:
        """
        Tạo document LaTeX hoàn chỉnh (tối ưu cho xelatex)

        Args:
            questions: Danh sách câu hỏi
            title: Tiêu đề document

        Returns:
            Chuỗi LaTeX hoàn chỉnh
        """
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath, amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
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
    def create_latex_document_with_format(questions_data: List, title: str = "Câu hỏi", fmt: int = 1) -> str:
        """Tạo document LaTeX với 2 format khác nhau"""
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath, amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
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


# PHẦN 4: DẠNG TOÁN

# DẠNG TOÁN: Đồng/nghịch biến hàm số (Chỉ đa thức bậc 3)

class PolynomialCubicMonotonicity(BaseOptimizationQuestion):
    def _get_poly3_coefficients(self, nice_numbers, coeff_range, domain_min, domain_max):
        """Generate coefficients for polynomial degree 3 using new form: k*x³/3 + k(b-a)*x²/2 - kabx + C.
        
        Derivative: f'(x) = k(x-a)(x+b) with critical points at x=a and x=-b.
        Ensure all terms (cubic, quadratic, linear) are present and C ≠ 0.
        """
        valid_configs = []
        
        # Parameter ranges from -5 to 5 (excluding 0 for k, a, b; C must be non-zero)
        k_choices = [k for k in range(-5, 6) if k != 0]
        a_choices = [a for a in range(-5, 6) if a != 0]  
        b_choices = [b for b in range(-5, 6) if b != 0]
        C_choices = [C for C in range(-5, 6) if C != 0]  # C must be non-zero

        for k in k_choices:
            for a in a_choices:
                for b in b_choices:
                    if a == -b:  # Avoid case where critical points are the same
                        continue
                        
                    # Check that critical points a and -b are within domain
                    if not (domain_min <= a <= domain_max and domain_min <= -b <= domain_max):
                        continue
                    
                    # Calculate standard form coefficients to ensure all terms present
                    # From: k*x³/3 + k(b-a)*x²/2 - kabx + C
                    coeff_cubic = k / 3      # Must be non-zero (k ≠ 0)
                    coeff_quad = k * (b - a) / 2  # Will be non-zero if b ≠ a
                    coeff_linear = -k * a * b     # Will be non-zero (k,a,b all ≠ 0)
                    
                    # Ensure quadratic term is non-zero (b ≠ a already checked via a ≠ -b)
                    if coeff_quad == 0:
                        continue
                        
                    for C in C_choices:
                        coeff_const = C  # Already ensured C ≠ 0
                        valid_configs.append((k, a, b, C))
                        
        return valid_configs

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán với ngữ cảnh thực tế đa dạng và ràng buộc hợp lý."""

        # Chọn ngữ cảnh ngẫu nhiên từ constants
        context = random.choice(CONTEXTS_CONFIG).copy()  # Copy để tránh modify original

        # Random ask_format cho context được chọn
        context["ask_format"] = "tăng" if random.choice([True, False]) else "giảm"

        # Random biến cho hàm số (nhất quán trong toàn bộ câu hỏi)
        # Với ràng buộc vật lý, thường dùng 't' cho thời gian
        if context["name"] in ["bacteria", "population", "velocity", "distance", "economy"]:
            context['variable'] = 't'  # Thời gian
        else:
            variables = ['x', 't', 'u', 'v', 'z']
            context['variable'] = random.choice(variables)

        # Sinh hàm số dựa trên loại với ràng buộc
        if context["function_type"] == "polynomial_3":
            return self._generate_polynomial_3(context)
        else:
            raise ValueError(f"Unsupported function_type: {context['function_type']}")

    def _generate_polynomial_3(self, context):
        """Sinh hàm bậc 3 với dạng mới: k*x³/3 + k(b-a)*x²/2 - kabx + C.
        
        Đạo hàm: f'(x) = k(x-a)(x+b) với nghiệm tại x=a và x=-b.
        Đảm bảo có đủ 3 biến bậc 3, 2, 1 và C ≠ 0.
        """
        max_attempts = 100
        constraints = context.get("constraints", {})
        domain_min = constraints.get("domain_min", DEFAULT_DOMAIN_MIN)
        domain_max = constraints.get("domain_max", DEFAULT_DOMAIN_MAX)

        # Simplified: direct parameter generation 
        valid_configs = self._get_poly3_coefficients(None, None, domain_min, domain_max)
        if not valid_configs:
            raise RuntimeError("Không tìm thấy bộ hệ số bậc 3 nghiệm đẹp.")

        for attempt in range(max_attempts):
            k, param_a, param_b, C = random.choice(valid_configs)

            # Critical points from new form: x = a and x = -b
            x1 = param_a      # First critical point
            x2 = -param_b     # Second critical point
            
            # Sort critical points
            if x1 > x2:
                x1, x2 = x2, x1
            if x1 == x2:  # Tránh nghiệm kép
                continue

            # Kiểm tra nghiệm trong domain
            if x1 < domain_min or x1 > domain_max or x2 < domain_min or x2 > domain_max:
                continue

            critical_points = [x1, x2]

            # Xác định khoảng đồng biến, nghịch biến
            # With f'(x) = k(x-a)(x+b), behavior depends on k
            if k > 0:
                # f'(x) > 0 when (x-a)(x+b) > 0, i.e., x < -b or x > a
                # f'(x) < 0 when -b < x < a
                increasing_intervals = [(domain_min, x1), (x2, domain_max)]
                decreasing_intervals = [(x1, x2)]
            else:
                # f'(x) > 0 when (x-a)(x+b) < 0, i.e., -b < x < a  
                # f'(x) < 0 when x < -b or x > a
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

            # Convert to standard polynomial form for compatibility
            # From: k*x³/3 + k(b-a)*x²/2 - kabx + C
            # To: ax³ + bx² + cx + d (ensuring all terms are non-zero)
            a_std = k / 3                    # Cubic coefficient (≠ 0)
            b_std = k * (param_b - param_a) / 2  # Quadratic coefficient (≠ 0)
            c_std = -k * param_a * param_b   # Linear coefficient (≠ 0)
            d_std = C                        # Constant term (≠ 0)

            # DEBUG: Print original form vs standard form
            # print(f"DEBUG: k={k}, a={param_a}, b={param_b}, C={C}")
            # print(f"Original: {k}*x³/3 + {k*(param_b-param_a)}*x²/2 + {-k*param_a*param_b}*x + {C}")
            # print(f"Standard: {a_std}*x³ + {b_std}*x² + {c_std}*x + {d_std}")

            # STRICT validation: ensure this is truly a cubic polynomial
            if abs(a_std) < 1e-10:
                continue  # Skip - not a valid cubic polynomial
            if abs(b_std) < 1e-10:
                continue  # Skip - missing quadratic term
            if abs(c_std) < 1e-10:
                continue  # Skip - missing linear term  
            if abs(d_std) < 1e-10:
                continue  # Skip - missing constant term

            # Kiểm tra ràng buộc nếu cần
            if constraints.get("must_be_positive", False):
                coeffs = [d_std, c_std, b_std, a_std]
                if not self._check_polynomial_constraints(coeffs, domain_min, domain_max, constraints):
                    continue

            return {
                'context': context,
                'function_type': 'polynomial_3',
                # Standard form coefficients for compatibility
                'a': a_std, 'b': b_std, 'c': c_std, 'd': d_std,
                # New form parameters
                'k': k, 'param_a': param_a, 'param_b': param_b, 'C': C,
                'critical_points': critical_points,
                'increasing_intervals': increasing_intervals,
                'decreasing_intervals': decreasing_intervals,
                'monotonicity': monotonicity
            }

        raise RuntimeError("Không thể sinh hàm bậc 3 nghiệm đẹp.")

    def calculate_answer(self) -> str:
        """Tính đáp án đúng và chuẩn bị toàn bộ dữ liệu cho lời giải."""
        context = self.parameters['context']
        monotonicity = self.parameters['monotonicity']
        increasing_intervals = self.parameters['increasing_intervals']
        decreasing_intervals = self.parameters['decreasing_intervals']
        constraints = context.get('constraints', {})
        function_type = self.parameters['function_type']
        var = context['variable']

        # Tính toán toàn bộ components cho LaTeX solution
        # Truyền target_intervals để đảm bảo consistency
        target_intervals = decreasing_intervals if monotonicity == "giảm" else increasing_intervals

        self.solution_data = self._calculate_all_solution_components(
            context, function_type, var, constraints, monotonicity,
            increasing_intervals, decreasing_intervals, target_intervals
        )

        # Chọn khoảng dựa trên monotonicity để tính đáp án cuối
        if monotonicity == "tăng":
            target_intervals = increasing_intervals
        else:
            target_intervals = decreasing_intervals

        # Format khoảng thời gian với ràng buộc domain
        domain_min = constraints.get('domain_min', float('-inf'))
        domain_max = constraints.get('domain_max', float('inf'))

        # Xử lý nhiều khoảng thời gian có thể có
        if target_intervals:
            valid_intervals = []
            
            for interval in target_intervals:
                start, end = interval
                
                # Đảm bảo khoảng nằm trong domain hợp lệ và là số nguyên
                actual_start = max(round(start), domain_min) if start != float('-inf') else domain_min
                actual_end = min(round(end), domain_max) if end != float('inf') else domain_max
                
                # Kiểm tra tính hợp lệ và độ dài của khoảng
                if actual_start >= domain_min and actual_end <= domain_max and actual_start < actual_end:
                    # Kiểm tra khoảng có đủ dài để có ý nghĩa thực tế không
                    # VD: khoảng (2/3, 1) có độ dài 1/3 < 1, quá hẹp cho ứng dụng thực tế
                    interval_length = actual_end - actual_start
                    if interval_length >= 1:  # Khoảng ít nhất 1 đơn vị thời gian
                        valid_intervals.append((actual_start, actual_end))
                    else:
                        # Khoảng quá hẹp - ghi nhận để giải thích
                        self.narrow_interval_explanation = f"Khoảng ({format_coord_solution(start)}, {format_coord_solution(end)}) quá hẹp để có ý nghĩa thực tế"
            
            if valid_intervals:
                # Nếu có nhiều khoảng, format chúng
                if len(valid_intervals) == 1:
                    start, end = valid_intervals[0]
                    correct_answer = f"từ {context['time_unit']} thứ {start} đến {end}"
                else:
                    # Có nhiều khoảng - format chi tiết cho solution
                    interval_strings = []
                    for start, end in valid_intervals:
                        interval_strings.append(f"từ {context['time_unit']} thứ {start} đến {end}")
                    correct_answer = " và ".join(interval_strings)
            else:
                correct_answer = "không có khoảng thời gian nào"
                # Thêm giải thích nếu có khoảng hẹp
                if hasattr(self, 'narrow_interval_explanation'):
                    correct_answer += f" (có khoảng hẹp nhưng không đáng kể)"
        else:
            correct_answer = "không có khoảng thời gian nào"

        # Cập nhật conclusion với correct_answer đã tính
        conclusion_text = f"Vậy {context['subject']} {monotonicity} trong khoảng {correct_answer}"
        
        # Thêm giải thích chi tiết cho trường hợp "không có khoảng nào"
        if "không có khoảng thời gian nào" in correct_answer:
            if hasattr(self, 'narrow_interval_explanation'):
                conclusion_text += f". Giải thích chi tiết: Mặc dù có khoảng {monotonicity} về mặt toán học, nhưng khoảng quá hẹp (độ dài < 1 đơn vị thời gian) nên không đủ rõ ràng để có ý nghĩa thực tế đáng kể"
        
        conclusion_text += " \\(\\rightarrow\\) Chọn đáp án tương ứng."
        self.solution_data['conclusion'] = conclusion_text

        return correct_answer

    def _calculate_all_solution_components(self, context, function_type, var, constraints,
                                         monotonicity, increasing_intervals, decreasing_intervals, target_intervals=None) -> dict:
        """Tính toán toàn bộ components cần thiết cho solution LaTeX - Single Source of Truth."""

        # Thành phần chung
        function_description = CONTEXT_DESCRIPTIONS.get(context['name']) or context.get('subject') or 'hàm số'

        # Domain constraint text
        physical_meaning = constraints.get('physical_meaning', '')
        if physical_meaning:
            if context['name'] in ['bacteria', 'population']:
                domain_constraint_text = f"Với điều kiện {physical_meaning} (theo ngữ cảnh thực tế)."
            else:
                domain_constraint_text = f"Với điều kiện {physical_meaning}."
        else:
            domain_constraint_text = ""

        physical_interpretation = PHYSICAL_INTERPRETATIONS.get(context['name'], {}).get(monotonicity, '')

        # Tính function và derivative info thống nhất
        function_info = self._get_unified_function_info(function_type, var, context)

        # Thêm thông tin xét dấu cụ thể với trường hợp đặc biệt
        if physical_interpretation:
            # SỬ DỤNG CHÍNH CÁC THAM SỐ TRUYỀN VÀO (đã được xử lý)
            # THAY VÌ LẤY LẠI TỪ self.parameters

            # Kiểm tra trường hợp đặc biệt: nghiệm kép tại điểm gián đoạn
            critical_points_from_params = self.parameters.get('critical_points', [])
            x1, x2 = critical_points_from_params if len(critical_points_from_params) >= 2 else [None, None]
            x_p_from_params = self.parameters.get('x_p', None)
            is_special_case = False
            
            if x1 is not None and x2 is not None and x_p_from_params is not None:
                if abs(x1 - x2) < 1e-10 and abs(x1 - x_p_from_params) < 1e-10:
                    is_special_case = True

            sign_analysis = f"Xét dấu của \\({function_info['derivative_symbol']}'({var})\\):\n\n"

            if is_special_case:
                sign_analysis += f"Trường hợp đặc biệt: \\({function_info['derivative_symbol']}'({format_number_clean(x_p_from_params)}) = 0\\) (nghiệm kép) và hàm không xác định tại \\({var} = {format_number_clean(x_p_from_params)}\\)\n\n"
                sign_analysis += f"\\(\\rightarrow\\) Cần xét dấu đạo hàm trên từng khoảng riêng biệt, bỏ qua điểm gián đoạn.\n\n"

            if increasing_intervals:
                formatted_increasing = [f"\\(({format_coord_solution(start)}, {format_coord_solution(end)})\\)"
                                       for start, end in increasing_intervals]
                sign_analysis += f"\\({function_info['derivative_symbol']}'({var}) > 0\\) trên các khoảng: {', '.join(formatted_increasing)}\n"
                sign_analysis += f"  \\(\\Rightarrow\\) {context['subject']} tăng trên các khoảng này\n"
                
                # Kiểm tra khoảng hẹp và thêm giải thích chi tiết
                for start, end in increasing_intervals:
                    if isinstance(start, (int, float)) and isinstance(end, (int, float)):
                        interval_length = abs(end - start)
                        if interval_length < 1:
                            sign_analysis += f"  Nhận xét quan trọng: Khoảng \\(({format_coord_solution(start)}, {format_coord_solution(end)})\\) có độ dài \\({format_coord_solution(interval_length)}\\), quá hẹp để có ý nghĩa thực tế đáng kể.\n"
                            sign_analysis += f"  \\(\\Rightarrow\\) Trong thực tế, khoảng này không đủ rõ ràng để kết luận {context['subject']} {monotonicity} trên một khoảng thời gian có ý nghĩa.\n"
                sign_analysis += "\n"

            if decreasing_intervals:
                formatted_decreasing = [f"\\(({format_coord_solution(start)}, {format_coord_solution(end)})\\)"
                                      for start, end in decreasing_intervals]
                sign_analysis += f"\\({function_info['derivative_symbol']}'({var}) < 0\\) trên các khoảng: {', '.join(formatted_decreasing)}\n"
                sign_analysis += f"  \\(\\Rightarrow\\) {context['subject']} giảm trên các khoảng này\n"
                
                # Kiểm tra khoảng hẹp và thêm giải thích chi tiết
                for start, end in decreasing_intervals:
                    if isinstance(start, (int, float)) and isinstance(end, (int, float)):
                        interval_length = abs(end - start)
                        if interval_length < 1:
                            sign_analysis += f"  Nhận xét quan trọng: Khoảng \\(({format_coord_solution(start)}, {format_coord_solution(end)})\\) có độ dài \\({format_coord_solution(interval_length)}\\), quá hẹp để có ý nghĩa thực tế đáng kể.\n"
                            sign_analysis += f"  \\(\\Rightarrow\\) Trong thực tế, khoảng này không đủ rõ ràng để kết luận {context['subject']} {monotonicity} trên một khoảng thời gian có ý nghĩa.\n"
                sign_analysis += "\n"

            if is_special_case:
                sign_analysis += f"Lưu ý: Mặc dù \\({function_info['derivative_symbol']}'({var}) = 0\\) tại \\({var} = {format_number_clean(x_p_from_params)}\\), nhưng hàm không liên tục tại điểm này nên dấu đạo hàm không đổi trên từng khoảng.\n\n"

            physical_interpretation = sign_analysis + physical_interpretation

        # Tạo kết luận sẽ được cập nhật sau trong calculate_answer()
        conclusion = f"Vậy {context['subject']} {monotonicity} trong khoảng [sẽ được cập nhật] \\(\\rightarrow\\) Chọn đáp án tương ứng."

        return {
            'function_description': function_description,
            'domain_constraint_text': domain_constraint_text,
            'physical_interpretation': physical_interpretation,
            'conclusion': conclusion,
            'var': var,
            'context': context,
            'function_info': function_info
        }

    def _get_unified_function_info(self, function_type, var, context) -> dict:
        """Thống nhất cách tính function và derivative info cho tất cả loại hàm."""

        if function_type == 'polynomial_3':
            return self._calculate_polynomial_3_info(var, context)
        else:
            raise ValueError(f"Unsupported function type: {function_type}")

    def _calculate_polynomial_3_info(self, var, context) -> dict:
        """Tính toán thông tin cho hàm bậc 3 - thống nhất với generate_parameters."""
        a, b, c, d = self.parameters['a'], self.parameters['b'], self.parameters['c'], self.parameters['d']
        function_latex = format_polynomial([a, b, c, d], var)
        critical_points = self.parameters['critical_points']

        derivative_latex = format_polynomial([3 * a, 2 * b, c], var)

        return {
            'function_intro': CONTEXT_DESCRIPTIONS.get(context['name']) or context.get('subject') or 'hàm số',
            'function_symbol': 'f',
            'function_latex': function_latex,
            'domain_info': "Tập xác định: \\(D = \\mathbb{R}\\)",
            'derivative_section': f"\\[\nf'({var}) = {derivative_latex}\n\\]",
            'critical_points_section': f"\\[\nf'({var}) = 0 \\Rightarrow {var} = {format_coord_solution(critical_points[0])}; \\quad {var} = {format_coord_solution(critical_points[1])}\n\\]",
            'discontinuity_section': "",  # Không có điểm gián đoạn
            'derivative_symbol': 'f'
        }

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

        # Luôn có đáp án "không có khoảng thời gian nào" làm một option
        wrong_answers.append("không có khoảng thời gian nào")

        # Đáp án sai 1: Ngược lại với đáp án đúng (lấy khoảng đầu tiên nếu có)
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
                end_options = [domain_max // 2, domain_max - 1, domain_max, domain_max + 1, domain_max + 2]

                # Lọc để đảm bảo start < end và trong domain hợp lý
                valid_starts = [int(s) for s in start_options if s >= domain_min and s <= domain_max - 1]
                valid_ends = [int(e) for e in end_options if e >= domain_min + 1 and e <= domain_max]

                if valid_starts and valid_ends:
                    start = random.choice(valid_starts)
                    end = random.choice([e for e in valid_ends if e > start])
                    candidate = f"từ {context['time_unit']} thứ {start} đến {end}"

                    # Đảm bảo không trùng với các đáp án đã có
                    if candidate not in wrong_answers and candidate != self.correct_answer:
                        wrong_answers.append(candidate)
                    else:
                        # Nếu trùng, tạo khoảng khác
                        start = random.randint(domain_min, domain_max - 1)
                        end = random.randint(start + 1, domain_max)
                        wrong_answers.append(f"từ {context['time_unit']} thứ {start} đến {end}")
                else:
                    # Fallback nếu không tạo được khoảng hợp lý
                    wrong_answers.append(f"từ {context['time_unit']} thứ 0 đến {domain_max // 2}")
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
        if function_type == 'polynomial_3':
            a, b, c, d = self.parameters['a'], self.parameters['b'], self.parameters['c'], self.parameters['d']
            function_latex = format_polynomial([a, b, c, d], var)
        else:
            raise ValueError(f"Unsupported function_type: {function_type}")

        # Tạo câu hỏi dựa trên loại với giới hạn thời gian rõ ràng
        question_text = f"""{context['description']} \\(f({var}) = {function_latex}\\) ({context['unit']}) sau \\({var}\\) {context['time_unit']}. 
        Hỏi {context['subject']} {monotonicity} trong khoảng thời gian nào {time_limit_text}?"""

        return question_text

    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết từ dữ liệu đã được tính toán trong calculate_answer."""
        # Đảm bảo solution_data đã được tính toán
        if not hasattr(self, 'solution_data') or not self.solution_data:
            raise RuntimeError("solution_data chưa được tính toán. Cần gọi calculate_answer() trước.")

        # Lấy dữ liệu đã tính toán
        data = self.solution_data
        function_info = data['function_info']
        context = data['context']
        var = data['var']

        # Template thống nhất cho tất cả loại hàm với format cải thiện
        solution_template = """Đề bài: {function_intro}: \\({function_symbol}({var}) = {function_latex}\\) ({unit}).

{domain_info}
{domain_constraint_text}

Bước 1: Tính đạo hàm
{derivative_section}

Bước 2: Giải phương trình đạo hàm
{critical_points_section}

{discontinuity_section}

Bước 3: Xét dấu của đạo hàm
{physical_interpretation}

Kết luận: {conclusion}"""

        # Format solution từ dữ liệu đã tính toán
        solution = solution_template.format(
            function_intro=function_info['function_intro'],
            function_symbol=function_info['function_symbol'],
            var=var,
            function_latex=function_info['function_latex'],
            unit=context['unit'],
            domain_info=function_info['domain_info'],
            domain_constraint_text=data['domain_constraint_text'],
            derivative_section=function_info['derivative_section'],
            critical_points_section=function_info['critical_points_section'],
            discontinuity_section=function_info['discontinuity_section'],
            physical_interpretation=data['physical_interpretation'],
            derivative_symbol=function_info['derivative_symbol'],
            conclusion=data['conclusion']
        )

        return solution

    def _filter_intervals_by_domain(self, intervals, domain_min, domain_max):
        """Lọc các khoảng theo giới hạn domain."""
        filtered_intervals = []
        for start, end in intervals:
            # Giữ nguyên giá trị Fraction, không làm tròn
            actual_start = max(start, domain_min) if start != float('-inf') else domain_min
            actual_end = min(end, domain_max) if end != float('inf') else domain_max

            # Chỉ giữ khoảng nếu có độ dài dương và nằm trong domain hợp lệ
            if actual_start < actual_end and actual_start >= domain_min and actual_end <= domain_max:
                filtered_intervals.append((actual_start, actual_end))

        return filtered_intervals

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


# PHẦN 6: GENERATOR CHÍNH

class OptimizationGenerator:
    """
    Generator chính để tạo câu hỏi tối ưu hóa
    Quản lý tất cả các dạng toán và tạo document LaTeX
    """

    # Danh sách các dạng toán có sẵn
    QUESTION_TYPES = [
        PolynomialCubicMonotonicity,
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
                except Exception as e:
                    logging.error(f"Lỗi tạo câu hỏi {i}: {e}")
                    continue
            return questions_data

    @classmethod
    def create_latex_file(cls, questions: List[str],
                          filename: str = "questions.tex",
                          title: str = "Câu hỏi về khoảng đồng biến, nghịch biến của hàm số") -> str:
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
            return filename
        except Exception as e:
            logging.error(f"Lỗi ghi file {filename}: {e}")
            raise

    @classmethod
    def create_latex_file_with_format(cls, questions_data,
                                      filename: str = "questions.tex",
                                      title: str = "Câu hỏi về khoảng đồng biến, nghịch biến của hàm số", fmt: int = 1) -> str:
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
            return filename
        except Exception as e:
            logging.error(f"Lỗi ghi file {filename}: {e}")
            raise


# PHẦN 7: HÀM MAIN

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
