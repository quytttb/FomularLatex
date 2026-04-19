"""
Hệ thống sinh đề toán về thể tích khối tròn xoay
"""

import logging
import os
import random
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, cast
import math
from fractions import Fraction
from typing import Union
from math import gcd
import sympy as sp

"""
Các hàm tiện ích LaTeX cho hệ thống sinh câu hỏi thể tích khối tròn xoay
"""


@dataclass
class GeneratorConfig:
    seed: Optional[int] = None
    exact_mode: bool = True
    # Cấu hình cho các hệ số trong hàm số
    coefficient_choices: Tuple[int, ...] = (1, 2, 3, 4, 5, 6)
    # Cấu hình cho cận tích phân
    integration_bounds: Tuple[int, int] = (0, 5)
    # Cấu hình cho các giá trị đặc biệt (e, π, etc.)
    special_values: Tuple[float, ...] = (sp.E.evalf(), sp.pi.evalf())


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
    elif hasattr(coeff, 'p') and hasattr(coeff, 'q'):  # sympy.Rational
        num, denom = coeff.p, coeff.q
    elif hasattr(coeff, 'numerator') and hasattr(coeff, 'denominator'):  # sympy types
        num, denom = coeff.numerator, coeff.denominator
    else:
        num, denom = coeff, 1
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
    """Định dạng số ở dạng chính xác (phân số/căn) không dùng thập phân."""
    try:
        expr = sp.nsimplify(value)
        if isinstance(expr, sp.Rational):
            if expr.q == 1:
                return str(expr.p)
            return f"{expr.p}/{expr.q}"
        return sp.latex(expr)
    except Exception:
        return str(value)


def format_coord_solution(coord):
    try:
        expr = sp.nsimplify(coord)
        if isinstance(expr, sp.Rational):
            if expr.q == 1:
                return str(expr.p)
            return f"\\dfrac{{{expr.p}}}{{{expr.q}}}"
        return sp.latex(expr)
    except Exception:
        return str(coord)


def format_scientific(num: float, precision: int = 3) -> str:
    """Trả về biểu diễn chính xác (không thập phân)."""
    expr = sp.nsimplify(num)
    return sp.latex(expr)


def format_sqrt(number: Union[int, float]) -> str:
    """Biểu diễn căn bậc hai dạng LaTeX (chính xác)."""
    expr = sp.nsimplify(number)
    return sp.latex(sp.sqrt(expr))


# format_sqrt_improved bị loại bỏ (trùng lặp logic với format_sqrt)


def format_dimension(value: float, unit: str = "mét") -> str:
    """Định dạng độ lớn kèm đơn vị ở dạng chính xác."""
    return f"{format_number_clean(sp.nsimplify(value))} {unit}"


def strip_latex_inline_math(ans: str) -> str:
    if ans.startswith("\\(") and ans.endswith("\\)"):
        return ans[2:-2].strip()
    if ans.startswith("$") and ans.endswith("$"):
        return ans[1:-1].strip()
    return ans


def to_decimal_comma(value: Any) -> str:
    s = str(value)
    return s.replace('.', ',')


def format_dfrac(num, denom):
    """Format fraction using dfrac for better display (chính xác)."""
    if denom == 0:
        return "undefined"
    try:
        frac = sp.Rational(num, denom)
        if frac.q == 1:
            return str(frac.p)
        elif frac.p == 0:
            return "0"
        else:
            return f"\\dfrac{{{frac.p}}}{{{frac.q}}}"
    except Exception:
        return f"\\dfrac{{{num}}}{{{denom}}}"


def format_money(value, unit="triệu đồng"):
    """Format money values cleanly"""
    return f"{format_number_clean(value)} {unit}"


def format_percentage(value):
    """Format percentage values"""
    return f"{format_number_clean(value * 100)}\\%"


def format_expression(expr):
    """Format expression to clean up signs and improve LaTeX display"""
    if isinstance(expr, str):
        # Chuyển + - thành - (có khoảng trắng)
        expr = expr.replace("+ -", "- ")
        # Chuyển +- thành -
        expr = expr.replace("+-", "-")
        # Chuyển -+ thành -
        expr = expr.replace("-+", "-")
        # Loại bỏ khoảng trắng thừa
        expr = expr.strip()
        # Xử lý trường hợp bắt đầu bằng +
        if expr.startswith("+"):
            expr = expr[1:]
        return expr
    return str(expr)


def format_function_notation(func_name, var, expression):
    """Format function notation like f(x) = expression"""
    return f"{func_name}({var}) = {expression}"


def simplify_for_latex(expr: sp.Expr) -> sp.Expr:
    """Apply a sequence of simplifications that tend to produce human-friendly LaTeX.
    - avoid algebraic power decompositions
    - rationalize radicals when appropriate
    - keep rationals and sqrt factors in a/times sqrt(b) / c style
    """
    try:
        # together → radsimp → simplify is generally safe and readable
        return sp.simplify(sp.radsimp(sp.together(expr)))
    except Exception:
        return sp.simplify(expr)


def latex_sqrt_sum_of_squares(dx: sp.Expr, dy: sp.Expr, dz: sp.Expr) -> str:
    dx_s = simplify_for_latex(dx)
    dy_s = simplify_for_latex(dy)
    dz_s = simplify_for_latex(dz)
    inner = sp.simplify(sp.Add(dx_s**2, dy_s**2, dz_s**2, evaluate=False))
    return sp.latex(sp.sqrt(inner))


"""
Lớp cơ sở cho các dạng bài toán thể tích khối tròn xoay
"""


class BaseVolumeQuestion(ABC):
    """
    Lớp cơ sở cho tất cả các dạng bài toán thể tích khối tròn xoay
    """

    def __init__(self, config: Optional["GeneratorConfig"] = None):
        self.parameters = {}
        self.correct_answer = None
        self.wrong_answers = []
        self.solution_steps = []
        self.config = config or GeneratorConfig()

    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên cho bài toán"""
        pass

    @abstractmethod
    def calculate_answer(self) -> str:
        """Tính đáp án đúng dựa trên parameters"""
        pass

    @abstractmethod
    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý"""
        pass

    @abstractmethod
    def generate_question_text(self) -> str:
        """Sinh đề bài bằng LaTeX"""
        pass

    @abstractmethod
    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết bằng LaTeX"""
        pass

    def generate_full_question(self, question_number: int = 1) -> str:
        """Tạo câu hỏi hoàn chỉnh với 4 đáp án A/B/C/D"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        self.wrong_answers = self.generate_wrong_answers()
        question_text = self.generate_question_text()
        solution = self.generate_solution()
        all_answers = [self.correct_answer] + self.wrong_answers
        random.shuffle(all_answers)
        correct_index = all_answers.index(self.correct_answer)
        question_content = f"Câu {question_number}: {question_text}\n\n"
        for j, ans in enumerate(all_answers):
            letter = chr(65 + j)
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
    def create_latex_document(questions: List[str], title: str = "Câu hỏi Thể tích Khối tròn xoay") -> str:
        """Tạo document LaTeX hoàn chỉnh"""
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
    def create_latex_document_with_format(questions_data: List, title: str = "Câu hỏi Thể tích Khối tròn xoay", fmt: int = 1) -> str:
        """Tạo document LaTeX với 2 format khác nhau"""
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

        if fmt == 1:
            # Format 1: đáp án ngay sau câu hỏi
            for question_data in questions_data:
                if isinstance(question_data, tuple):
                    latex_content += f"{question_data[0]}\n\n"
                else:
                    latex_content += f"{question_data}\n\n"
        else:
            # Format 2: câu hỏi + lời giải + đáp án ngay sau mỗi câu
            for idx, question_data in enumerate(questions_data, 1):
                if isinstance(question_data, tuple):
                    question_content, correct_answer = question_data
                    latex_content += question_content + "\n\n"
                    
                    # Thêm đáp án ngay sau lời giải
                    ans = correct_answer
                    # Xử lý đáp án có thể có text ngoài math mode (ví dụ: "183,259 đồng")
                    math_part = ""
                    text_part = ""
                    
                    # Kiểm tra xem có math mode không
                    if ans.startswith("\\(") and ans.endswith("\\)"):
                        math_part = ans
                    elif ans.startswith("$") and ans.endswith("$"):
                        math_part = ans
                    else:
                        # Không có math mode, có thể là text thuần (ví dụ: "183,259 đồng")
                        text_part = ans
                    
                    # Nếu có math mode, kiểm tra xem có text sau không
                    if math_part:
                        # Lấy nội dung math để kiểm tra
                        math_content = math_part
                        if math_part.startswith("\\(") and math_part.endswith("\\)"):
                            math_content = math_part[2:-2].strip()
                        elif math_part.startswith("$") and math_part.endswith("$"):
                            math_content = math_part[1:-1].strip()
                        
                        # Kiểm tra số thập phân
                        if ',' in math_content:
                            ans_dot = math_content.replace(',', '.')
                            ans_dot_math = f"\\({ans_dot}\\)"
                            latex_content += f"Đáp án: {math_part} hoặc {ans_dot_math}\n\n"
                        else:
                            latex_content += f"Đáp án: {math_part}\n\n"
                    else:
                        # Chỉ có text, không có math mode
                        latex_content += f"Đáp án: {text_part}\n\n"
                else:
                    # Fallback cho format cũ
                    latex_content += f"{question_data}\n\n"

        latex_content += "\\end{document}"
        return latex_content


# ============================================================================
# SCENARIO 1: KHỐI ĐẶC ĐƠN GIẢN
# ============================================================================

class SolidVolumeQuestion1(BaseVolumeQuestion):
    """
    Câu 1: y=√(a+sin x), x∈[0,π]
    V = π∫[0,π] (a+sin x) dx = π[ax - cos x]₀^π = π(aπ + 2)
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        cfg = getattr(self, 'config', GeneratorConfig())
        a = random.choice((1, 2, 3, 4))
        return {"a": a}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        a = params["a"]
        x = sp.Symbol('x')
        integrand = a + sp.sin(x)
        volume_expr = sp.pi * sp.integrate(integrand, (x, 0, sp.pi))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        a = params["a"]
        correct_val = sp.pi * (a * sp.pi + 2)
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * (a * sp.pi + 1))}\\)",  # Thiếu +2
            f"\\(V = {sp.latex(2 * sp.pi * (a * sp.pi + 2))}\\)",  # Nhân 2
            f"\\(V = {sp.latex(a * sp.pi + 2)}\\)",  # Thiếu π
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        a = params["a"]
        return (
            f"Cho hình phẳng (D) giới hạn bởi đường cong \\(y = \\sqrt{{{a} + \\sin x}}\\), "
            f"trục hoành và các đường thẳng \\(x = 0\\), \\(x = \\pi\\). "
            f"Khối tròn xoay tạo thành khi quay (D) quanh trục hoành có thể tích (V) bằng bao nhiêu?"
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        a = params["a"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate(a + sp.sin(x), (x, 0, sp.pi))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho hình phẳng (D) giới hạn bởi \\(y = \\sqrt{{{a} + \\sin x}}\\), trục hoành, \\(x = 0\\) và \\(x = \\pi\\).

Xét hàm số \\(y = \\sqrt{{{a} + \\sin x}}\\) trên \\([0, \\pi]\\). Do \\(-1 \\leq \\sin x \\leq 1\\) nên \\({a} - 1 \\leq {a} + \\sin x \\leq {a} + 1\\), hàm số xác định với \\(x \\in [0, \\pi]\\).

Ta có: Thể tích khối tròn xoay khi quay (D) quanh trục Ox:

\\(V = \\pi \\int_0^{{\\pi}} y^2 \\, dx = \\pi \\int_0^{{\\pi}} (\\sqrt{{{a} + \\sin x}})^2 dx\\)

Bình phương để bỏ căn:

\\(V = \\pi \\int_0^{{\\pi}} ({a} + \\sin x) \\, dx\\)

Tính nguyên hàm:
- \\(\\int {a} \\, dx = {a}x\\)
- \\(\\int \\sin x \\, dx = -\\cos x\\)

Do đó:

\\(V = \\pi \\left[ {a}x - \\cos x \\right]_0^{{\\pi}}\\)

Thay cận:

\\(V = \\pi \\left( {a} \\cdot \\pi - \\cos \\pi - ({a} \\cdot 0 - \\cos 0) \\right)\\)

\\(= \\pi \\left( {a}\\pi - (-1) - 0 + 1 \\right)\\)

\\(= \\pi({a}\\pi + 2)\\)

Kết luận: \\(V = {sp.latex(volume_simplified)}\\)
"""


class SolidVolumeQuestion2(BaseVolumeQuestion):
    """
    Câu 2: y=e^(kx), x∈[0,1]
    V = π∫[0,1] e^(2kx) dx = π(e^(2k)-1)/(2k)
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        k = random.choice((1, 2))
        return {"k": k}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        k = params["k"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate(sp.exp(2*k*x), (x, 0, 1))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        k = params["k"]
        x = sp.Symbol('x')
        correct_val = sp.pi * sp.integrate(sp.exp(2*k*x), (x, 0, 1))
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * (sp.exp(2*k) - 1) / k)}\\)",  # Thiếu /2
            f"\\(V = {sp.latex((sp.exp(2*k) - 1) / (2*k))}\\)",  # Thiếu π
            f"\\(V = {sp.latex(sp.pi * sp.exp(2*k) / (2*k))}\\)",  # Thiếu -1
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        k = params["k"]
        return (
            f"Cho hình phẳng (D) giới hạn bởi đường cong \\(y = e^{{{k}x}}\\), "
            f"trục hoành và các đường thẳng \\(x = 0\\), \\(x = 1\\). "
            f"Khối tròn xoay tạo thành khi quay (D) quanh trục hoành có thể tích (V) bằng bao nhiêu?"
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        k = params["k"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate(sp.exp(2*k*x), (x, 0, 1))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho hình phẳng (D) giới hạn bởi \\(y = e^{{{k}x}}\\), trục hoành, \\(x = 0\\) và \\(x = 1\\).

Hàm số \\(y = e^{{{k}x}}\\) xác định và dương với mọi \\(x \\in [0, 1]\\).

Ta có: Thể tích khối tròn xoay khi quay (D) quanh trục Ox:

\\(V = \\pi \\int_0^1 y^2 \\, dx = \\pi \\int_0^1 (e^{{{k}x}})^2 dx\\)

Sử dụng tính chất lũy thừa: \\((e^{{{k}x}})^2 = e^{{{2*k}x}}\\)

\\(V = \\pi \\int_0^1 e^{{{2*k}x}} \\, dx\\)

Tính nguyên hàm: Áp dụng công thức \\(\\int e^{{ax}} dx = \\frac{{1}}{{a}} e^{{ax}} + C\\)

Với \\(a = {2*k}\\), ta có:

\\(\\int e^{{{2*k}x}} dx = \\frac{{1}}{{{2*k}}} e^{{{2*k}x}} + C\\)

Do đó:

\\(V = \\pi \\left[ \\frac{{e^{{{2*k}x}}}}{{{2*k}}} \\right]_0^1\\)

Thay cận:

\\(V = \\pi \\left( \\frac{{e^{{{2*k} \\cdot 1}}}}{{{2*k}}} - \\frac{{e^{{{2*k} \\cdot 0}}}}{{{2*k}}} \\right)\\)

\\(= \\pi \\left( \\frac{{e^{{{2*k}}}}}{{{2*k}}} - \\frac{{1}}{{{2*k}}} \\right)\\)

\\(= \\pi \\cdot \\frac{{e^{{{2*k}}} - 1}}{{{2*k}}}\\)

Kết luận: \\(V = {sp.latex(volume_simplified)}\\)
"""


class SolidVolumeQuestion3(BaseVolumeQuestion):
    """
    Câu 3: y=√(x²+a), x∈[0,1]
    V = π∫[0,1] (x²+a) dx = π(1/3 + a)
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        a = random.choice((1, 2, 3))
        return {"a": a}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        a = params["a"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate(x**2 + a, (x, 0, 1))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        a = params["a"]
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * (1/2 + a))}\\)",  # Sai: 1/2 thay vì 1/3
            f"\\(V = {sp.latex(1/3 + a)}\\)",  # Thiếu π
            f"\\(V = {sp.latex(sp.pi * (1/3 + 2*a))}\\)",  # Nhân 2a
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        a = params["a"]
        return (
            f"Cho hình phẳng (D) giới hạn bởi đường cong \\(y = \\sqrt{{x^2 + {a}}}\\), "
            f"trục hoành và các đường thẳng \\(x = 0\\), \\(x = 1\\). "
            f"Khối tròn xoay tạo thành khi quay (D) quanh trục hoành có thể tích (V) bằng bao nhiêu?"
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        a = params["a"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate(x**2 + a, (x, 0, 1))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho hình phẳng (D) giới hạn bởi \\(y = \\sqrt{{x^2 + {a}}}\\), trục hoành, \\(x = 0\\) và \\(x = 1\\).

Hàm số \\(y = \\sqrt{{x^2 + {a}}}\\) xác định với mọi \\(x \\in [0, 1]\\) vì \\(x^2 + {a} > 0\\).

Ta có: Thể tích khối tròn xoay khi quay (D) quanh trục Ox:

\\(V = \\pi \\int_0^1 y^2 \\, dx = \\pi \\int_0^1 (\\sqrt{{x^2 + {a}}})^2 dx\\)

Bình phương để bỏ căn:

\\(V = \\pi \\int_0^1 (x^2 + {a}) \\, dx\\)

Tính nguyên hàm từng số hạng:
- \\(\\int x^2 \\, dx = \\frac{{x^3}}{{3}} + C\\)
- \\(\\int {a} \\, dx = {a}x + C\\)

Do đó:

\\(V = \\pi \\left[ \\frac{{x^3}}{{3}} + {a}x \\right]_0^1\\)

Thay cận:

\\(V = \\pi \\left( \\frac{{1^3}}{{3}} + {a} \\cdot 1 - \\frac{{0^3}}{{3}} - {a} \\cdot 0 \\right)\\)

\\(= \\pi \\left( \\frac{{1}}{{3}} + {a} \\right)\\)

Kết luận: \\(V = {sp.latex(volume_simplified)}\\)
"""


class SolidVolumeQuestion4(BaseVolumeQuestion):
    """
    Câu 4: y=x²-kx, x∈[0,1]
    V = π∫[0,1] (x²-kx)² dx
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        k = random.choice((1, 2, 3))
        return {"k": k}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        k = params["k"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate((x**2 - k*x)**2, (x, 0, 1))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        k = params["k"]
        x = sp.Symbol('x')
        correct_val = sp.pi * sp.integrate((x**2 - k*x)**2, (x, 0, 1))
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * sp.integrate(x**2 - k*x, (x, 0, 1)))}\\)",  # Quên bình phương
            f"\\(V = {sp.latex(sp.integrate((x**2 - k*x)**2, (x, 0, 1)))}\\)",  # Thiếu π
            f"\\(V = {sp.latex(sp.pi * sp.integrate((x**2 - k*x)**2, (x, 0, 2)))}\\)",  # Sai cận
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        k = params["k"]
        return (
            f"Tính thể tích (V) của khối tròn xoay tạo thành khi quay quanh trục hoành "
            f"hình phẳng giới hạn bởi các đường \\(y = x^2 - {k}x\\), \\(y = 0\\), \\(x = 0\\) và \\(x = 1\\)."
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        k = params["k"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate((x**2 - k*x)**2, (x, 0, 1))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        expanded = sp.expand((x**2 - k*x)**2)
        antiderivative = sp.integrate(expanded, x)
        return f"""
Cho hình phẳng (D) giới hạn bởi \\(y = x^2 - {k}x\\), \\(y = 0\\), \\(x = 0\\) và \\(x = 1\\).

Hàm số \\(y = x^2 - {k}x\\) xác định trên \\([0, 1]\\).

Ta có: Thể tích khối tròn xoay khi quay (D) quanh trục Ox:

\\(V = \\pi \\int_0^1 y^2 \\, dx = \\pi \\int_0^1 (x^2 - {k}x)^2 dx\\)

Khai triển biểu thức bình phương:

\\((x^2 - {k}x)^2 = x^4 - {2*k}x^3 + {k**2}x^2\\)

Do đó:

\\(V = \\pi \\int_0^1 (x^4 - {2*k}x^3 + {k**2}x^2) \\, dx\\)

Tính nguyên hàm từng số hạng:
- \\(\\int x^4 \\, dx = \\frac{{x^5}}{{5}}\\)
- \\(\\int x^3 \\, dx = \\frac{{x^4}}{{4}}\\)
- \\(\\int x^2 \\, dx = \\frac{{x^3}}{{3}}\\)

Do đó:

\\(V = \\pi \\left[ \\frac{{x^5}}{{5}} - {2*k} \\cdot \\frac{{x^4}}{{4}} + {k**2} \\cdot \\frac{{x^3}}{{3}} \\right]_0^1\\)

\\(= \\pi \\left[ \\frac{{x^5}}{{5}} - \\frac{{{2*k}x^4}}{{4}} + \\frac{{{k**2}x^3}}{{3}} \\right]_0^1\\)

Thay cận:

\\(V = \\pi \\left( \\frac{{1}}{{5}} - \\frac{{{2*k}}}{{4}} + \\frac{{{k**2}}}{{3}} - 0 \\right)\\)

\\(= \\pi \\left( \\frac{{1}}{{5}} - \\frac{{{k}}}{{2}} + \\frac{{{k**2}}}{{3}} \\right)\\)

Kết luận: \\(V = {sp.latex(volume_simplified)}\\)
"""


class SolidVolumeQuestion5(BaseVolumeQuestion):
    """
    Câu 5: y=√(ln x), x=b
    V = π∫[1,b] ln x dx
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        b = random.choice((2, 3, 4))
        return {"b": b}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        b = params["b"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate(sp.log(x), (x, 1, b))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        b = params["b"]
        x = sp.Symbol('x')
        correct_val = sp.pi * sp.integrate(sp.log(x), (x, 1, b))
        wrongs = [
            f"\\(V = {sp.latex(sp.integrate(sp.log(x), (x, 1, b)))}\\)",  # Thiếu π
            f"\\(V = {sp.latex(sp.pi * sp.integrate(sp.log(x), (x, 0, b)))}\\)",  # Sai cận dưới
            f"\\(V = {sp.latex(sp.pi * b * sp.log(b))}\\)",  # Sai công thức
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        b = params["b"]
        return (
            f"Thể tích của vật thể tròn xoay thu được khi quay hình phẳng "
            f"(phần gạch sọc, giới hạn bởi \\(y = \\sqrt{{\\ln x}}\\) và \\(x = {b}\\)) "
            f"xung quanh trục hoành Ox bằng:"
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        b = params["b"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate(sp.log(x), (x, 1, b))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho hình phẳng (D) giới hạn bởi \\(y = \\sqrt{{\\ln x}}\\), trục hoành và \\(x = {b}\\).

Hàm số \\(y = \\sqrt{{\\ln x}}\\) xác định khi \\(\\ln x \\geq 0 \\Leftrightarrow x \\geq 1\\). Do đó cận dưới là \\(x = 1\\).

Ta có: Thể tích khối tròn xoay khi quay (D) quanh trục Ox:

\\(V = \\pi \\int_1^{{{b}}} y^2 \\, dx = \\pi \\int_1^{{{b}}} (\\sqrt{{\\ln x}})^2 dx\\)

Bình phương để bỏ căn:

\\(V = \\pi \\int_1^{{{b}}} \\ln x \\, dx\\)

Tính nguyên hàm bằng phương pháp tích phân từng phần:

Đặt \\(\\begin{{cases}} u = \\ln x \\\\ dv = dx \\end{{cases}}\\) suy ra \\(\\begin{{cases}} du = \\frac{{1}}{{x}}dx \\\\ v = x \\end{{cases}}\\)

Áp dụng công thức: \\(\\int u \\, dv = uv - \\int v \\, du\\)

\\(\\int \\ln x \\, dx = x\\ln x - \\int x \\cdot \\frac{{1}}{{x}} dx\\)

\\(= x\\ln x - \\int 1 \\, dx\\)

\\(= x\\ln x - x + C\\)

Do đó:

\\(V = \\pi \\left[ x\\ln x - x \\right]_1^{{{b}}}\\)

Thay cận:

\\(V = \\pi \\left( {b}\\ln {b} - {b} - (1 \\cdot \\ln 1 - 1) \\right)\\)

\\(= \\pi \\left( {b}\\ln {b} - {b} - 0 + 1 \\right)\\)

\\(= \\pi({b}\\ln {b} - {b} + 1)\\)

Kết luận: \\(V = {sp.latex(volume_simplified)}\\)
"""


class SolidVolumeQuestion7(BaseVolumeQuestion):
    """
    Câu 7: y=ln x, y=a, trục tung và trục hoành
    V = π∫[1,e^a] (a² - (ln x)²) dx
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        a = random.choice((1, 2))
        return {"a": a}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        a = params["a"]
        x = sp.Symbol('x')
        # Miền D: từ x=1 đến x=e^a, giới hạn bởi y=ln x (dưới) và y=a (trên)
        # Quay quanh Ox: V = π∫[1,e^a] (a² - (ln x)²) dx
        volume_expr = sp.pi * sp.integrate(a**2 - sp.log(x)**2, (x, 1, sp.exp(a)))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        a = params["a"]
        x = sp.Symbol('x')
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * sp.integrate(sp.log(x)**2, (x, 1, sp.exp(a))))}\\)",  # Chỉ lấy phần dưới
            f"\\(V = {sp.latex(sp.integrate(a**2 - sp.log(x)**2, (x, 1, sp.exp(a))))}\\)",  # Thiếu π
            f"\\(V = {sp.latex(sp.pi * a * sp.exp(a))}\\)",  # Sai công thức
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        a = params["a"]
        return (
            f"Thể tích của vật thể tròn xoay thu được khi quay hình phẳng giới hạn bởi "
            f"\\(y = {a}\\), \\(y = \\ln x\\), trục tung và trục hoành (phần gạch sọc) "
            f"xung quanh trục hoành Ox bằng:"
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        a = params["a"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate(a**2 - sp.log(x)**2, (x, 1, sp.exp(a)))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho hình phẳng (D) giới hạn bởi \\(y = {a}\\), \\(y = \\ln x\\), trục tung và trục hoành.

Tìm cận tích phân:
- Giao điểm của \\(y = \\ln x\\) và trục hoành (\\(y = 0\\)): \\(\\ln x = 0 \\Rightarrow x = 1\\)
- Giao điểm của \\(y = \\ln x\\) và \\(y = {a}\\): \\(\\ln x = {a} \\Rightarrow x = e^{{{a}}}\\)

Miền D nằm giữa \\(x = 1\\) và \\(x = e^{{{a}}}\\), giới hạn trên bởi \\(y = {a}\\) và giới hạn dưới bởi \\(y = \\ln x\\).

Ta có: Thể tích khối tròn xoay (khối rỗng) khi quay (D) quanh trục Ox:

\\(V = \\pi \\int_1^{{e^{{{a}}}}} (R^2 - r^2) \\, dx\\)

trong đó \\(R = {a}\\) (bán kính ngoài) và \\(r = \\ln x\\) (bán kính trong).

\\(V = \\pi \\int_1^{{e^{{{a}}}}} ({a}^2 - (\\ln x)^2) \\, dx\\)

\\(= \\pi \\int_1^{{e^{{{a}}}}} {a}^2 \\, dx - \\pi \\int_1^{{e^{{{a}}}}} (\\ln x)^2 \\, dx\\)

Tính tích phân thứ nhất:

\\(\\int_1^{{e^{{{a}}}}} {a}^2 \\, dx = {a}^2 [x]_1^{{e^{{{a}}}}} = {a}^2(e^{{{a}}} - 1)\\)

Tính tích phân thứ hai bằng phương pháp tích phân từng phần hai lần:

Đặt \\(u = (\\ln x)^2\\), \\(dv = dx\\) suy ra \\(du = \\frac{{2\\ln x}}{{x}}dx\\), \\(v = x\\)

\\(\\int (\\ln x)^2 dx = x(\\ln x)^2 - 2\\int \\ln x \\, dx\\)

Từ câu trước ta có: \\(\\int \\ln x \\, dx = x\\ln x - x\\)

Do đó: \\(\\int (\\ln x)^2 dx = x(\\ln x)^2 - 2(x\\ln x - x) = x(\\ln x)^2 - 2x\\ln x + 2x\\)

Áp dụng:

\\(\\int_1^{{e^{{{a}}}}} (\\ln x)^2 dx = [x(\\ln x)^2 - 2x\\ln x + 2x]_1^{{e^{{{a}}}}}\\)

\\(= e^{{{a}}} \\cdot {a}^2 - 2e^{{{a}}} \\cdot {a} + 2e^{{{a}}} - (1 \\cdot 0 - 2 \\cdot 1 \\cdot 0 + 2 \\cdot 1)\\)

\\(= e^{{{a}}}({a}^2 - 2{a} + 2) - 2\\)

Vậy:

\\(V = \\pi[{a}^2(e^{{{a}}} - 1) - (e^{{{a}}}({a}^2 - 2{a} + 2) - 2)]\\)

\\(= \\pi[{a}^2 e^{{{a}}} - {a}^2 - {a}^2 e^{{{a}}} + 2{a}e^{{{a}}} - 2e^{{{a}}} + 2]\\)

\\(= \\pi[2{a}e^{{{a}}} - 2e^{{{a}}} - {a}^2 + 2]\\)

Kết luận: \\(V = {sp.latex(volume_simplified)}\\)
"""


# ============================================================================


def get_available_question_types():
    return [
        SolidVolumeQuestion1,
        SolidVolumeQuestion2,
        SolidVolumeQuestion3,
        SolidVolumeQuestion4,
        SolidVolumeQuestion5,
        SolidVolumeQuestion7
    ]


def generate_mixed_questions(num_questions: int = 9) -> str:
    """Sinh nhiều câu hỏi từ các dạng toán khác nhau"""
    question_types = get_available_question_types()
    questions = []

    for i in range(num_questions):
        question_type = random.choice(question_types)
        question_generator = question_type()
        question_content, _ = question_generator.generate_question_only(i + 1)
        questions.append(question_content)

    return BaseVolumeQuestion.create_latex_document(questions, "Câu hỏi Khối Đặc")


def main():
    """
    Hàm main để chạy generator
    """
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        fmt = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] in ['1', '2'] else 1
        seed: Optional[int] = None
        if len(sys.argv) > 3:
            try:
                seed = int(sys.argv[3])
            except Exception:
                seed = None
        if seed is None:
            env_seed = os.environ.get("OPT_SEED")
            if env_seed is not None:
                try:
                    seed = int(env_seed)
                except Exception:
                    seed = None
        if seed is not None:
            random.seed(seed)

        question_types = get_available_question_types()
        questions_data = []

        for i in range(1, num_questions + 1):
            try:
                question_type = random.choice(question_types)
                question_instance = question_type(GeneratorConfig(seed=None))
                if fmt == 1:
                    question = question_instance.generate_full_question(i)
                    questions_data.append(question)
                else:
                    question_content, correct_answer = question_instance.generate_question_only(i)
                    questions_data.append((question_content, correct_answer))
                logging.info(f"Đã tạo thành công câu hỏi {i}")
            except Exception as e:
                logging.error(f"Lỗi tạo câu hỏi {i}: {e}")
                continue

        if not questions_data:
            print("Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)

        if fmt == 1:
            latex_content = BaseVolumeQuestion.create_latex_document(questions_data, "Câu hỏi Khối Đặc")
        else:
            latex_content = BaseVolumeQuestion.create_latex_document_with_format(questions_data, "Câu hỏi Khối Đặc", fmt)

        filename = "solid_questions.tex"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)

        print(f"✅ Đã tạo thành công {filename} với {len(questions_data)} câu hỏi")
        print(f"📄 Biên dịch bằng: xelatex {filename}")
        print(f"📋 Format: {fmt} {'đáp án ngay sau câu hỏi' if fmt == 1 else 'đáp án ở cuối'}")

    except ValueError:
        print("❌ Lỗi: Vui lòng nhập số câu hỏi hợp lệ")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
