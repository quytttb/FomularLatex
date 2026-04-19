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
# SCENARIO 2: KHỐI RỖNG (GIAO 2 ĐƯỜNG)
# ============================================================================

class HollowVolumeQuestion6(BaseVolumeQuestion):
    """
    Câu 6: Đồ thị với hình vẽ (cần phân tích từ mẫu)
    Tạm thời implement dạng đơn giản: y=ln x, x từ 1 đến e
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        return {}
    
    def calculate_answer(self) -> str:
        x = sp.Symbol('x')
        # V = π∫[1,e] (ln x)² dx
        volume_expr = sp.pi * sp.integrate(sp.log(x)**2, (x, 1, sp.E))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        x = sp.Symbol('x')
        wrongs = [
            f"\\(V = {sp.latex(sp.integrate(sp.log(x)**2, (x, 1, sp.E)))}\\)",  # Thiếu π
            f"\\(V = {sp.latex(sp.pi * sp.integrate(sp.log(x), (x, 1, sp.E)))}\\)",  # Thiếu bình phương
            f"\\(V = {sp.latex(sp.pi * (sp.E - 1))}\\)",  # Sai công thức
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        return (
            f"Thể tích của vật thể tròn xoay thu được khi quay hình phẳng xung quanh trục hoành Ox bằng:"
        )
    
    def generate_solution(self) -> str:
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate(sp.log(x)**2, (x, 1, sp.E))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho hình phẳng (D) giới hạn bởi đồ thị hàm số (phần gạch sọc).

Giả sử hình phẳng giới hạn bởi \\(y = \\ln x\\), trục hoành, \\(x = 1\\) và \\(x = e\\).

Ta có: Thể tích khối tròn xoay khi quay (D) quanh trục Ox:

\\(V = \\pi \\int_1^e y^2 \\, dx = \\pi \\int_1^e (\\ln x)^2 dx\\)

Tính nguyên hàm bằng phương pháp tích phân từng phần:

Đặt \\(u = (\\ln x)^2\\), \\(dv = dx\\) suy ra \\(du = \\frac{{2\\ln x}}{{x}}dx\\), \\(v = x\\)

\\(\\int (\\ln x)^2 dx = x(\\ln x)^2 - 2\\int \\ln x \\, dx\\)

Tính \\(\\int \\ln x \\, dx\\): Đặt \\(u = \\ln x\\), \\(dv = dx\\) ta được:

\\(\\int \\ln x \\, dx = x\\ln x - x + C\\)

Do đó:

\\(\\int (\\ln x)^2 dx = x(\\ln x)^2 - 2(x\\ln x - x)\\)

\\(= x(\\ln x)^2 - 2x\\ln x + 2x + C\\)

Áp dụng:

\\(V = \\pi [x(\\ln x)^2 - 2x\\ln x + 2x]_1^e\\)

Thay cận:

Tại \\(x = e\\): \\(e(\\ln e)^2 - 2e\\ln e + 2e = e \\cdot 1 - 2e \\cdot 1 + 2e = e\\)

Tại \\(x = 1\\): \\(1(\\ln 1)^2 - 2 \\cdot 1 \\cdot \\ln 1 + 2 \\cdot 1 = 0 - 0 + 2 = 2\\)

\\(V = \\pi(e - 2)\\)

Kết luận: \\(V = {sp.latex(volume_simplified)}\\)
"""


class HollowVolumeQuestion8(BaseVolumeQuestion):
    """
    Câu 8: y=x và y=√(ax-x²)
    V = π∫[giao điểm] (ax-x²-x²) dx = π∫ (ax-2x²) dx
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        a = random.choice((4, 5, 6))
        return {"a": a}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        a = params["a"]
        x = sp.Symbol('x')
        # Giao điểm: x = √(ax-x²) => x² = ax-x² => 2x² = ax => x(2x-a)=0 => x=0 hoặc x=a/2
        # Miền: từ x=0 đến x=a/2
        volume_expr = sp.pi * sp.integrate((a*x - x**2) - x**2, (x, 0, a/2))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        a = params["a"]
        x = sp.Symbol('x')
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * sp.integrate(a*x - x**2, (x, 0, a/2)))}\\)",  # Quên trừ x²
            f"\\(V = {sp.latex(sp.integrate((a*x - x**2) - x**2, (x, 0, a/2)))}\\)",  # Thiếu π
            f"\\(V = {sp.latex(sp.pi * sp.integrate((a*x - x**2)**2 - x**2, (x, 0, a/2)))}\\)",  # Sai công thức
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        a = params["a"]
        return (
            f"Thể tích vật thể tròn xoay khi quay hình phẳng giới hạn bởi đường thẳng \\(y = x\\) "
            f"và đường tròn \\(y = \\sqrt{{{a}x - x^2}}\\) xung quanh trục Ox bằng:"
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        a = params["a"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate((a*x - x**2) - x**2, (x, 0, a/2))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho hình phẳng (D) giới hạn bởi đường thẳng \\(y = x\\) và đường tròn \\(y = \\sqrt{{{a}x - x^2}}\\).

Tìm giao điểm: Giải phương trình \\(x = \\sqrt{{{a}x - x^2}}\\)

Bình phương hai vế (với điều kiện \\(x \\geq 0\\)):

\\(x^2 = {a}x - x^2\\)

\\(2x^2 = {a}x\\)

\\(2x^2 - {a}x = 0\\)

\\(x(2x - {a}) = 0\\)

Suy ra \\(x = 0\\) hoặc \\(x = \\frac{{{a}}}{{2}}\\)

Kiểm tra điều kiện: Với \\(x \\in [0, \\frac{{{a}}}{{2}}]\\), ta có \\({a}x - x^2 = x({a} - x) \\geq 0\\).

Ta có: Thể tích khối tròn xoay (khối rỗng) khi quay (D) quanh trục Ox:

\\(V = \\pi \\int_0^{{\\frac{{{a}}}{{2}}}} (R^2 - r^2) \\, dx\\)

trong đó \\(R = \\sqrt{{{a}x - x^2}}\\) (bán kính ngoài) và \\(r = x\\) (bán kính trong).

\\(V = \\pi \\int_0^{{\\frac{{{a}}}{{2}}}} ((\\sqrt{{{a}x - x^2}})^2 - x^2) dx\\)

\\(= \\pi \\int_0^{{\\frac{{{a}}}{{2}}}} ({a}x - x^2 - x^2) dx\\)

\\(= \\pi \\int_0^{{\\frac{{{a}}}{{2}}}} ({a}x - 2x^2) dx\\)

Tính nguyên hàm:

\\(V = \\pi \\left[ {a} \\cdot \\frac{{x^2}}{{2}} - 2 \\cdot \\frac{{x^3}}{{3}} \\right]_0^{{\\frac{{{a}}}{{2}}}}\\)

\\(= \\pi \\left[ \\frac{{{a}x^2}}{{2}} - \\frac{{2x^3}}{{3}} \\right]_0^{{\\frac{{{a}}}{{2}}}}\\)

Thay cận:

\\(V = \\pi \\left( \\frac{{{a}}}{{2}} \\cdot \\frac{{{a}^2}}{{4}} - \\frac{{2}}{{3}} \\cdot \\frac{{{a}^3}}{{8}} \\right)\\)

\\(= \\pi \\left( \\frac{{{a}^3}}{{8}} - \\frac{{{a}^3}}{{12}} \\right)\\)

\\(= \\pi \\cdot \\frac{{3{a}^3 - 2{a}^3}}{{24}} = \\pi \\cdot \\frac{{{a}^3}}{{24}}\\)

Kết luận: \\(V = {sp.latex(volume_simplified)}\\)
"""


class HollowVolumeQuestion9(BaseVolumeQuestion):
    """
    Câu 9: y=ax-x² và y=x
    V = π∫[giao điểm] ((ax-x²)² - x²) dx
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        a = random.choice((3, 4, 5))
        return {"a": a}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        a = params["a"]
        x = sp.Symbol('x')
        # Giao điểm: ax-x² = x => x(a-x-1)=0 => x=0 hoặc x=a-1
        volume_expr = sp.pi * sp.integrate((a*x - x**2)**2 - x**2, (x, 0, a-1))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        a = params["a"]
        x = sp.Symbol('x')
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * sp.integrate((a*x - x**2) - x, (x, 0, a-1)))}\\)",  # Quên bình phương
            f"\\(V = {sp.latex(sp.integrate((a*x - x**2)**2 - x**2, (x, 0, a-1)))}\\)",  # Thiếu π
            f"\\(V = {sp.latex(sp.pi * sp.integrate((a*x - x**2)**2, (x, 0, a-1)))}\\)",  # Quên trừ x²
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        a = params["a"]
        return (
            f"Thể tích vật thể tròn xoay khi quay hình phẳng giới hạn bởi parabol \\(y = {a}x - x^2\\) "
            f"và đường thẳng \\(y = x\\) xung quanh trục Ox bằng:"
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        a = params["a"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate((a*x - x**2)**2 - x**2, (x, 0, a-1))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        expanded = sp.expand((a*x - x**2)**2)
        return f"""
Cho hình phẳng (D) giới hạn bởi parabol \\(y = {a}x - x^2\\) và đường thẳng \\(y = x\\).

Tìm giao điểm: Giải phương trình \\({a}x - x^2 = x\\)

\\({a}x - x^2 - x = 0\\)

\\({a-1}x - x^2 = 0\\)

\\(x({a-1} - x) = 0\\)

Suy ra \\(x = 0\\) hoặc \\(x = {a-1}\\)

Ta có: Thể tích khối tròn xoay (khối rỗng) khi quay (D) quanh trục Ox:

\\(V = \\pi \\int_0^{{{a-1}}} (R^2 - r^2) \\, dx\\)

trong đó \\(R = {a}x - x^2\\) (parabol - bán kính ngoài) và \\(r = x\\) (đường thẳng - bán kính trong).

\\(V = \\pi \\int_0^{{{a-1}}} (({a}x - x^2)^2 - x^2) dx\\)

Khai triển \\(({a}x - x^2)^2 = {sp.latex(expanded)}\\)

\\(V = \\pi \\int_0^{{{a-1}}} ({sp.latex(expanded)} - x^2) dx\\)

Tính nguyên hàm và thay cận:

Kết luận: \\(V = {sp.latex(volume_simplified)}\\)
"""


class HollowVolumeQuestion11(BaseVolumeQuestion):
    """
    Câu 11: y=a-x² và y=b (phần gạch sọc)
    V = π∫[giao điểm] ((a-x²)² - b²) dx
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        a = random.choice((4, 5, 6))
        b = random.choice((2, 3))
        return {"a": a, "b": b}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        a = params["a"]
        b = params["b"]
        x = sp.Symbol('x')
        # Giao điểm: a-x² = b => x² = a-b => x = ±√(a-b)
        sqrt_val = sp.sqrt(a - b)
        volume_expr = sp.pi * sp.integrate((a - x**2)**2 - b**2, (x, -sqrt_val, sqrt_val))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        a = params["a"]
        b = params["b"]
        x = sp.Symbol('x')
        sqrt_val = sp.sqrt(a - b)
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * sp.integrate((a - x**2) - b, (x, -sqrt_val, sqrt_val)))}\\)",  # Quên bình phương
            f"\\(V = {sp.latex(sp.integrate((a - x**2)**2 - b**2, (x, -sqrt_val, sqrt_val)))}\\)",  # Thiếu π
            f"\\(V = {sp.latex(sp.pi * sp.integrate((a - x**2)**2, (x, -sqrt_val, sqrt_val)))}\\)",  # Quên trừ b²
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        a = params["a"]
        b = params["b"]
        return (
            f"Thể tích vật thể tròn xoay khi quay hình phẳng giới hạn bởi \\(y = {a} - x^2\\) "
            f"và đường thẳng \\(y = {b}\\) (phần gạch sọc) quanh trục Ox:"
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        a = params["a"]
        b = params["b"]
        x = sp.Symbol('x')
        sqrt_val = sp.sqrt(a - b)
        volume_expr = sp.pi * sp.integrate((a - x**2)**2 - b**2, (x, -sqrt_val, sqrt_val))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho hình phẳng (D) giới hạn bởi parabol \\(y = {a} - x^2\\) và đường thẳng \\(y = {b}\\).

Tìm giao điểm: Giải phương trình \\({a} - x^2 = {b}\\)

\\(x^2 = {a} - {b}\\)

\\(x^2 = {a-b}\\)

\\(x = \\pm \\sqrt{{{a-b}}}\\)

Ta có: Thể tích khối tròn xoay (khối rỗng) khi quay (D) quanh trục Ox:

\\(V = \\pi \\int_{{-\\sqrt{{{a-b}}}}}^{{\\sqrt{{{a-b}}}}} (R^2 - r^2) \\, dx\\)

trong đó \\(R = {a} - x^2\\) (parabol - bán kính ngoài) và \\(r = {b}\\) (bán kính trong).

\\(V = \\pi \\int_{{-\\sqrt{{{a-b}}}}}^{{\\sqrt{{{a-b}}}}} (({a} - x^2)^2 - {b}^2) dx\\)

Do hàm số dưới dấu tích phân là hàm chẵn, ta có thể tính:

\\(V = 2\\pi \\int_0^{{\\sqrt{{{a-b}}}}} (({a} - x^2)^2 - {b}^2) dx\\)

Khai triển: \\(({a} - x^2)^2 = {a}^2 - 2 \\cdot {a}x^2 + x^4\\)

\\(V = 2\\pi \\int_0^{{\\sqrt{{{a-b}}}}} ({a}^2 - {2*a}x^2 + x^4 - {b}^2) dx\\)

\\(= 2\\pi \\int_0^{{\\sqrt{{{a-b}}}}} ({a**2 - b**2} - {2*a}x^2 + x^4) dx\\)

Tính nguyên hàm:

\\(= 2\\pi \\left[ {a**2 - b**2} \\cdot x - {2*a} \\cdot \\frac{{x^3}}{{3}} + \\frac{{x^5}}{{5}} \\right]_0^{{\\sqrt{{{a-b}}}}}\\)

Thay cận và rút gọn:

Kết luận: \\(V = {sp.latex(volume_simplified)}\\)
"""


class HollowVolumeQuestion12(BaseVolumeQuestion):
    """
    Câu 12: y=√(x+a) và y=b-x
    V = π∫[giao điểm] ((b-x)² - (x+a)) dx
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        a = random.choice((1, 2, 3))
        b = random.choice((3, 4, 5))
        return {"a": a, "b": b}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        a = params["a"]
        b = params["b"]
        x = sp.Symbol('x', real=True)
        # Giao điểm: √(x+a) = b-x => x+a = (b-x)²
        # Giải phương trình: x+a = b²-2bx+x² => x² - (2b+1)x + (b²-a) = 0
        eq = sp.Eq((b - x)**2, x + a)
        solutions = sp.solve(eq, x)
        # Lấy hai nghiệm thực
        real_sols = [sol.evalf() for sol in solutions if sol.is_real or abs(sp.im(sol)) < 1e-10]
        if len(real_sols) < 2:
            # Fallback nếu không có 2 nghiệm
            x1 = 0
            x2 = min(b, b - a)
        else:
            x1 = min(real_sols)
            x2 = max(real_sols)
            # Đảm bảo (b-x) >= 0 và x+a >= 0
            x2 = min(x2, b)
            x1 = max(x1, -a)
        volume_expr = sp.pi * sp.integrate((b - x)**2 - (x + a), (x, x1, x2))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        a = params["a"]
        b = params["b"]
        x = sp.Symbol('x', real=True)
        # Dùng giao điểm thật để tạo đáp án sai
        eq = sp.Eq((b - x)**2, x + a)
        solutions = sp.solve(eq, x)
        real_sols = [sol.evalf() for sol in solutions if sol.is_real or abs(sp.im(sol)) < 1e-10]
        if len(real_sols) < 2:
            x1 = 0
            x2 = max(b - a - 1, 1)
        else:
            x1 = min(real_sols)
            x2 = min(max(real_sols), b)
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * sp.integrate((b - x) - sp.sqrt(x + a), (x, x1, x2)))}\\)",  # Quên bình phương
            f"\\(V = {sp.latex(sp.integrate((b - x)**2 - (x + a), (x, x1, x2)))}\\)",  # Thiếu π
            f"\\(V = {sp.latex(sp.pi * sp.integrate((b - x)**2, (x, x1, x2)))}\\)",  # Quên trừ (x+a)
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        a = params["a"]
        b = params["b"]
        return (
            f"Thể tích vật thể tròn xoay khi quay hình phẳng giới hạn bởi \\(y = \\sqrt{{x + {a}}}\\) "
            f"và \\(y = {b} - x\\) quanh trục Ox:"
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        a = params["a"]
        b = params["b"]
        x = sp.Symbol('x', real=True)
        # Tính giao điểm thật
        eq = sp.Eq((b - x)**2, x + a)
        solutions = sp.solve(eq, x)
        real_sols = [sol.evalf() for sol in solutions if sol.is_real or abs(sp.im(sol)) < 1e-10]
        if len(real_sols) < 2:
            x1 = 0
            x2 = max(b - a - 1, 1)
        else:
            x1 = min(real_sols)
            x2 = min(max(real_sols), b)
        volume_expr = sp.pi * sp.integrate((b - x)**2 - (x + a), (x, x1, x2))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho hình phẳng (D) giới hạn bởi \\(y = \\sqrt{{x + {a}}}\\) và \\(y = {b} - x\\).

Tìm giao điểm: Giải phương trình \\(\\sqrt{{x + {a}}} = {b} - x\\)

Điều kiện: \\(x + {a} \\geq 0\\) và \\({b} - x \\geq 0\\), tức là \\(x \\geq -{a}\\) và \\(x \\leq {b}\\).

Bình phương hai vế:

\\(x + {a} = ({b} - x)^2\\)

\\(x + {a} = {b}^2 - 2 \\cdot {b}x + x^2\\)

\\(x^2 - (2 \\cdot {b} + 1)x + ({b}^2 - {a}) = 0\\)

Giải phương trình bậc 2 này để tìm \\(x_1\\) và \\(x_2\\).

Ta có: Thể tích khối tròn xoay (khối rỗng) khi quay (D) quanh trục Ox:

\\(V = \\pi \\int_{{x_1}}^{{x_2}} (R^2 - r^2) \\, dx\\)

trong đó \\(R = {b} - x\\) (đường thẳng - bán kính ngoài) và \\(r = \\sqrt{{x + {a}}}\\) (bán kính trong).

\\(V = \\pi \\int_{{x_1}}^{{x_2}} (({b} - x)^2 - (\\sqrt{{x + {a}}})^2) dx\\)

\\(= \\pi \\int_{{x_1}}^{{x_2}} (({b} - x)^2 - (x + {a})) dx\\)

Khai triển: \\(({b} - x)^2 = {b}^2 - 2 \\cdot {b}x + x^2\\)

\\(V = \\pi \\int_{{x_1}}^{{x_2}} ({b}^2 - 2 \\cdot {b}x + x^2 - x - {a}) dx\\)

Tính nguyên hàm và thay cận:

Kết luận: \\(V = {sp.latex(volume_simplified)}\\)
"""


class HollowVolumeQuestion13(BaseVolumeQuestion):
    """
    Câu 13: y=x², y=a, y=b-cx (tam giác cong)
    Chia miền thành 2 phần tích phân
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        b = random.choice((8, 9, 10))
        c = random.choice((2, 3))
        return {"a": 1, "b": b, "c": c}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        a = params["a"]
        b = params["b"]
        c = params["c"]
        x = sp.Symbol('x')
        # Giao điểm phức tạp, đơn giản hóa: từ x=0 đến x=1 (y=x² và y=1)
        # và từ x=1 đến x=(b-a)/c (y=1 và y=b-cx)
        # Chuyển cận thành phân số để tránh số thập phân
        upper_bound = sp.Rational(b - a, c)
        volume_expr = sp.pi * (sp.integrate(1 - x**4, (x, 0, 1)) + 
                               sp.integrate((b - c*x)**2 - 1, (x, 1, upper_bound)))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        a = params["a"]
        b = params["b"]
        c = params["c"]
        x = sp.Symbol('x')
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * sp.integrate(1 - x**2, (x, 0, 1)))}\\)",  # Chỉ lấy phần đầu
            f"\\(V = {sp.latex(sp.integrate(1 - x**4, (x, 0, 1)))}\\)",  # Thiếu π
            f"\\(V = {sp.latex(sp.pi * sp.integrate(1, (x, 0, (b-a)/c)))}\\)",  # Sai công thức
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        a = params["a"]
        b = params["b"]
        c = params["c"]
        return (
            f"Thể tích vật thể tròn xoay giới hạn bởi parabol \\(y = x^2\\), đường thẳng \\(y = {a}\\) "
            f"và \\(y = {b} - {c}x\\) (hình tam giác cong) quay quanh Ox:"
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        a = params["a"]
        b = params["b"]
        c = params["c"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * (sp.integrate(1 - x**4, (x, 0, 1)) + 
                               sp.integrate((b - c*x)**2 - 1, (x, 1, (b-a)/c)))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho hình phẳng (D) (tam giác cong) giới hạn bởi \\(y = x^2\\), \\(y = {a}\\) và \\(y = {b} - {c}x\\).

Tìm giao điểm:
- \\(x^2 = {a} \\Rightarrow x = \\pm 1\\), chọn \\(x = 1\\) (miền dương)
- \\({a} = {b} - {c}x \\Rightarrow x = \\frac{{{b - a}}}{{{c}}}\\)

Miền D được chia thành 2 phần:

**Phần 1:** Từ \\(x = 0\\) đến \\(x = 1\\), giữa \\(y = x^2\\) (dưới) và \\(y = {a}\\) (trên).

**Phần 2:** Từ \\(x = 1\\) đến \\(x = \\frac{{{b-a}}}{{{c}}}\\), giữa \\(y = {a}\\) (dưới) và \\(y = {b} - {c}x\\) (trên).

Ta có: Thể tích khối tròn xoay khi quay (D) quanh trục Ox:

\\(V = V_1 + V_2\\)

**Tính \\(V_1\\):** (khối rỗng)

\\(V_1 = \\pi \\int_0^1 ({a}^2 - (x^2)^2) dx = \\pi \\int_0^1 (1 - x^4) dx\\)

\\(= \\pi \\left[ x - \\frac{{x^5}}{{5}} \\right]_0^1 = \\pi \\left(1 - \\frac{{1}}{{5}}\\right) = \\frac{{4\\pi}}{{5}}\\)

**Tính \\(V_2\\):** (khối rỗng)

\\(V_2 = \\pi \\int_1^{{\\frac{{{b-a}}}{{{c}}}}} (({b} - {c}x)^2 - {a}^2) dx\\)

Khai triển và tính nguyên hàm:

\\(V = V_1 + V_2\\)

Kết luận: \\(V = {sp.latex(volume_simplified)}\\)
"""


class HollowVolumeQuestion15(BaseVolumeQuestion):
    """
    Câu 15: Tam giác cong với y=x+a
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        a = random.choice((1, 2, 3))
        return {"a": a}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        a = params["a"]
        x = sp.Symbol('x')
        # Đơn giản hóa: miền từ x=0 đến x=2, giữa y=x+a và y=0
        volume_expr = sp.pi * sp.integrate((x + a)**2, (x, 0, 2))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        a = params["a"]
        x = sp.Symbol('x')
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * sp.integrate(x + a, (x, 0, 2)))}\\)",  # Quên bình phương
            f"\\(V = {sp.latex(sp.integrate((x + a)**2, (x, 0, 2)))}\\)",  # Thiếu π
            f"\\(V = {sp.latex(sp.pi * sp.integrate((x + a)**2, (x, 0, 1)))}\\)",  # Sai cận
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        a = params["a"]
        return (
            f"Thể tích vật thể tròn xoay quay quanh Ox (phần gạch sọc tam giác cong giới hạn bởi \\(y = x + {a}\\)...):"
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        a = params["a"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate((x + a)**2, (x, 0, 2))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho hình phẳng (D) (tam giác cong) giới hạn bởi \\(y = x + {a}\\) và các đường khác.

Ta có: Thể tích khối tròn xoay khi quay (D) quanh trục Ox:

\\(V = \\pi \\int_0^2 y^2 \\, dx = \\pi \\int_0^2 (x + {a})^2 dx\\)

Khai triển: \\((x + {a})^2 = x^2 + {2*a}x + {a**2}\\)

\\(V = \\pi \\int_0^2 (x^2 + {2*a}x + {a**2}) dx\\)

Tính nguyên hàm:

\\(V = \\pi \\left[ \\frac{{x^3}}{{3}} + {a}x^2 + {a**2}x \\right]_0^2\\)

Thay cận:

\\(V = \\pi \\left( \\frac{{8}}{{3}} + {a} \\cdot 4 + {a**2} \\cdot 2 \\right)\\)

\\(= \\pi \\left( \\frac{{8}}{{3}} + {4*a} + {2*a**2} \\right)\\)

Kết luận: \\(V = {sp.latex(volume_simplified)}\\)
"""


class HollowVolumeQuestion16(BaseVolumeQuestion):
    """
    Câu 16: y=√(x-a), y=b-x, x=c
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        b = random.choice((1, 2))
        c = random.choice((3, 4, 5))
        return {"a": 1, "b": b, "c": c}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        a = params["a"]
        b = params["b"]
        c = params["c"]
        x = sp.Symbol('x', real=True)
        # Giao điểm: √(x-a) = b-x => x-a = (b-x)²
        # Giải phương trình: x² - (2b+1)x + (b²+a) = 0
        eq = sp.Eq((b - x)**2, x - a)
        solutions = sp.solve(eq, x)
        # Lấy nghiệm thực
        real_sols = [sol.evalf() for sol in solutions if sol.is_real or abs(sp.im(sol)) < 1e-10]
        if len(real_sols) < 2:
            # Fallback: dùng cận từ a đến min(c, b)
            x1 = a
            x2 = min(c, b)
        else:
            x1 = max(min(real_sols), a)  # Đảm bảo x >= a (để √(x-a) xác định)
            x2 = min(max(real_sols), c, b)  # Đảm bảo x <= min(c, b)
        volume_expr = sp.pi * sp.integrate((b - x)**2 - (x - a), (x, x1, x2))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        a = params["a"]
        b = params["b"]
        c = params["c"]
        x = sp.Symbol('x', real=True)
        # Dùng giao điểm thật
        eq = sp.Eq((b - x)**2, x - a)
        solutions = sp.solve(eq, x)
        real_sols = [sol.evalf() for sol in solutions if sol.is_real or abs(sp.im(sol)) < 1e-10]
        if len(real_sols) < 2:
            x1 = a
            x2 = min(c, b)
        else:
            x1 = max(min(real_sols), a)
            x2 = min(max(real_sols), c, b)
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * sp.integrate((b - x) - sp.sqrt(x - a), (x, x1, x2)))}\\)",  # Quên bình phương
            f"\\(V = {sp.latex(sp.integrate((b - x)**2 - (x - a), (x, x1, x2)))}\\)",  # Thiếu π
            f"\\(V = {sp.latex(sp.pi * sp.integrate((b - x)**2, (x, x1, x2)))}\\)",  # Quên trừ (x-a)
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        a = params["a"]
        b = params["b"]
        c = params["c"]
        return (
            f"Thể tích vật thể tròn xoay khi quay hình phẳng giới hạn bởi \\(y = \\sqrt{{x - {a}}}\\), "
            f"\\(y = {b} - x\\) và \\(x = {c}\\) quanh trục Ox:"
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        a = params["a"]
        b = params["b"]
        c = params["c"]
        x = sp.Symbol('x', real=True)
        # Tính giao điểm thật
        eq = sp.Eq((b - x)**2, x - a)
        solutions = sp.solve(eq, x)
        real_sols = [sol.evalf() for sol in solutions if sol.is_real or abs(sp.im(sol)) < 1e-10]
        if len(real_sols) < 2:
            x1 = a
            x2 = min(c, b)
        else:
            x1 = max(min(real_sols), a)
            x2 = min(max(real_sols), c, b)
        volume_expr = sp.pi * sp.integrate((b - x)**2 - (x - a), (x, x1, x2))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho hình phẳng (D) giới hạn bởi \\(y = \\sqrt{{x - {a}}}\\), \\(y = {b} - x\\) và \\(x = {c}\\).

Tìm giao điểm: Giải phương trình \\(\\sqrt{{x - {a}}} = {b} - x\\)

Điều kiện: \\(x \\geq {a}\\) và \\({b} - x \\geq 0\\), tức là \\({a} \\leq x \\leq {b}\\).

Bình phương hai vế:

\\(x - {a} = ({b} - x)^2\\)

\\(x - {a} = {b}^2 - 2 \\cdot {b}x + x^2\\)

\\(x^2 - (2 \\cdot {b} + 1)x + ({b}^2 + {a}) = 0\\)

Giải phương trình bậc 2 để tìm \\(x_1\\) và \\(x_2\\), đảm bảo \\(x_1 \\geq {a}\\) và \\(x_2 \\leq \\min({b}, {c})\\).

Ta có: Thể tích khối tròn xoay (khối rỗng) khi quay (D) quanh trục Ox:

\\(V = \\pi \\int_{{x_1}}^{{x_2}} (R^2 - r^2) \\, dx\\)

trong đó \\(R = {b} - x\\) (đường thẳng - bán kính ngoài) và \\(r = \\sqrt{{x - {a}}}\\) (bán kính trong).

\\(V = \\pi \\int_{{x_1}}^{{x_2}} (({b} - x)^2 - (\\sqrt{{x - {a}}})^2) dx\\)

\\(= \\pi \\int_{{x_1}}^{{x_2}} (({b} - x)^2 - (x - {a})) dx\\)

Khai triển và tính nguyên hàm:

Kết luận: \\(V = {sp.latex(volume_simplified)}\\)
"""


# ============================================================================


def get_available_question_types():
    return [
        HollowVolumeQuestion6,
        HollowVolumeQuestion8,
        HollowVolumeQuestion9,
        HollowVolumeQuestion11,
        HollowVolumeQuestion12,
        HollowVolumeQuestion13,
        HollowVolumeQuestion15,
        HollowVolumeQuestion16
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

    return BaseVolumeQuestion.create_latex_document(questions, "Câu hỏi Khối Rỗng")


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
            latex_content = BaseVolumeQuestion.create_latex_document(questions_data, "Câu hỏi Khối Rỗng")
        else:
            latex_content = BaseVolumeQuestion.create_latex_document_with_format(questions_data, "Câu hỏi Khối Rỗng", fmt)

        filename = "hollow_questions.tex"
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
