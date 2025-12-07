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
# SCENARIO 4: ỨNG DỤNG THỰC TẾ
# ============================================================================

class PracticalVaseQuestion10(BaseVolumeQuestion):
    """
    Câu 10: Cái lọ y=√(x+a)
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        # Đường kính đáy 2 => y(0) = √a = 1 => a = 1
        a = 1
        return {"a": a}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        a = params["a"]
        x = sp.Symbol('x')
        # Đường kính đáy 2 => y(0) = √a = 1 => a = 1
        # Đường kính miệng 4 => y(b) = √(b+a) = 2 => b+a = 4 => b = 3
        b = 3
        volume_expr = sp.pi * sp.integrate(x + a, (x, 0, b))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        a = params["a"]
        x = sp.Symbol('x')
        b = 3
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * sp.integrate(sp.sqrt(x + a), (x, 0, b)))}\\)",  # Quên bình phương
            f"\\(V = {sp.latex(sp.integrate(x + a, (x, 0, b)))}\\)",  # Thiếu π
            f"\\(V = {sp.latex(sp.pi * sp.integrate(x + a, (x, 0, 2*b)))}\\)",  # Sai cận
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        a = params["a"]
        return (
            f"Một bác thợ gốm làm một cái lọ có dạng khối tròn xoay tạo thành khi quay hình phẳng "
            f"giới hạn bởi \\(y = \\sqrt{{x + {a}}}\\) và trục Ox. "
            f"Biết đáy lọ và miệng lọ có đường kính lần lượt là 2 dm và 4 dm. Tính thể tích của lọ."
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        a = params["a"]
        x = sp.Symbol('x')
        b = 3
        volume_expr = sp.pi * sp.integrate(x + a, (x, 0, b))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho cái lọ có dạng khối tròn xoay, đường kính đáy 2 dm, đường kính miệng 4 dm. Lọ được tạo bởi \\(y = \\sqrt{{x + {a}}}\\).

**Xác định tham số:**

Từ đường kính đáy 2 dm, bán kính đáy là \\(r_0 = 1\\) dm.

Tại \\(x = 0\\): \\(y(0) = \\sqrt{{{a}}} = 1 \\Rightarrow {a} = 1\\)

Từ đường kính miệng 4 dm, bán kính miệng là \\(r_1 = 2\\) dm.

Tại \\(x = b\\): \\(y(b) = \\sqrt{{b + {a}}} = 2\\)

\\(b + {a} = 4 \\Rightarrow b = 4 - {a} = {b}\\)

Ta có: Thể tích cái lọ:

\\(V = \\pi \\int_0^{{{b}}} y^2 \\, dx = \\pi \\int_0^{{{b}}} (\\sqrt{{x + {a}}})^2 dx\\)

\\(= \\pi \\int_0^{{{b}}} (x + {a}) dx\\)

Tính nguyên hàm:

\\(V = \\pi \\left[ \\frac{{x^2}}{{2}} + {a}x \\right]_0^{{{b}}}\\)

\\(= \\pi \\left( \\frac{{{b}^2}}{{2}} + {a} \\cdot {b} \\right)\\)

\\(= \\pi \\left( \\frac{{9}}{{2}} + 3 \\right) = \\pi \\cdot \\frac{{15}}{{2}}\\)

Kết luận: \\(V = {sp.latex(volume_simplified)}\\) dm³ (hoặc \\(\\approx {float(volume_simplified.evalf()):.2f}\\) dm³)
"""


class PracticalGlassQuestion17(BaseVolumeQuestion):
    """
    Câu 17: Cái ly parabol
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        return {"diameter": 4, "height": 6}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        h = params["height"]
        r = params["diameter"] / 2
        x = sp.Symbol('x')
        # Parabol: y = ax² đi qua (h, r) => r = a*h² => a = r/h²
        # y = (r/h²)x²
        a_coeff = r / (h**2)
        volume_expr = sp.pi * sp.integrate((a_coeff * x**2)**2, (x, 0, h))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        h = params["height"]
        r = params["diameter"] / 2
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * r**2 * h / 3)}\\)",  # Công thức hình nón
            f"\\(V = {sp.latex(sp.pi * r**2 * h)}\\)",  # Công thức hình trụ
            f"\\(V = {sp.latex(sp.pi * r * h)}\\)",  # Sai công thức
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        d = params["diameter"]
        h = params["height"]
        return (
            f"Một cái ly hình tròn xoay, đường kính miệng {d} cm, chiều cao {h} cm. "
            f"Thiết diện qua trục là một parabol. Tính thể tích cái ly."
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        h = params["height"]
        r = params["diameter"] / 2
        x = sp.Symbol('x')
        a_coeff = r / (h**2)
        volume_expr = sp.pi * sp.integrate((a_coeff * x**2)**2, (x, 0, h))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho cái ly hình tròn xoay, đường kính miệng {d} cm, chiều cao {h} cm. Thiết diện qua trục là parabol.

**Thiết lập hệ tọa độ và tìm phương trình parabol:**

Đặt hệ tọa độ Oxy với O tại đáy ly, trục Ox hướng lên theo chiều cao.

Thiết diện là parabol có dạng \\(y = ax^2\\), đi qua điểm \\(({h}, {r})\\) (với \\(r = {d}/2 = {r}\\) cm).

Thay vào: \\({r} = a \\cdot {h}^2\\)

\\(a = \\frac{{{r}}}{{{h}^2}} = \\frac{{{r}}}{{{h**2}}}\\)

Phương trình: \\(y = \\frac{{{r}}}{{{h}^2}}x^2\\)

Ta có: Thể tích cái ly:

\\(V = \\pi \\int_0^{{{h}}} y^2 \\, dx = \\pi \\int_0^{{{h}}} \\left(\\frac{{{r}}}{{{h}^2}}x^2\\right)^2 dx\\)

\\(= \\pi \\int_0^{{{h}}} \\frac{{{r}^2}}{{{h}^4}}x^4 \\, dx\\)

\\(= \\pi \\cdot \\frac{{{r}^2}}{{{h}^4}} \\int_0^{{{h}}} x^4 \\, dx\\)

Tính nguyên hàm:

\\(= \\pi \\cdot \\frac{{{r}^2}}{{{h}^4}} \\left[ \\frac{{x^5}}{{5}} \\right]_0^{{{h}}}\\)

\\(= \\pi \\cdot \\frac{{{r}^2}}{{{h}^4}} \\cdot \\frac{{{h}^5}}{{5}}\\)

\\(= \\pi \\cdot \\frac{{{r}^2 \\cdot {h}}}{{5}}\\)

Kết luận: \\(V = {sp.latex(volume_simplified)}\\) cm³
"""


class PracticalWatermelonQuestion18(BaseVolumeQuestion):
    """
    Câu 18: Dưa hấu elip
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        major_axis = 28
        minor_axis = 25
        price_per_1000cm3 = 20000
        return {"major": major_axis, "minor": minor_axis, "price": price_per_1000cm3}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        a = params["major"] / 2
        b = params["minor"] / 2
        # Thể tích elip: V = (4/3)πab² (quay quanh trục lớn)
        volume = (4/3) * sp.pi * a * b**2
        price_per_cm3 = params["price"] / 1000
        total_price = volume * price_per_cm3
        return f"{int(total_price):,} đồng"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        a = params["major"] / 2
        b = params["minor"] / 2
        price_per_cm3 = params["price"] / 1000
        wrongs = [
            f"{int((4/3) * sp.pi * a**2 * b * price_per_cm3):,} đồng",  # Sai công thức
            f"{int(sp.pi * a * b**2 * price_per_cm3):,} đồng",  # Thiếu 4/3
            f"{int((4/3) * sp.pi * a * b * price_per_cm3):,} đồng",  # Thiếu b²
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        major = params["major"]
        minor = params["minor"]
        price = params["price"]
        return (
            f"Quả dưa hấu thiết diện là elip có trục lớn {major} cm, trục nhỏ {minor} cm. "
            f"Cứ 1000 cm³ dưa làm được cốc sinh tố giá {price:,} đồng. Tính tiền thu được (vỏ không đáng kể)."
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        a = params["major"] / 2
        b = params["minor"] / 2
        price_per_cm3 = params["price"] / 1000
        volume = (4/3) * sp.pi * a * b**2
        total_price = volume * price_per_cm3
        return f"""
Cho quả dưa hấu có thiết diện là elip với trục lớn {major} cm, trục nhỏ {minor} cm.

**Tính thể tích dưa hấu:**

Khi quay elip quanh trục lớn, ta được khối elip tròn xoay (ellipsoid) với công thức:

\\(V = \\frac{{4}}{{3}}\\pi a b^2\\)

trong đó \\(a\\) là nửa trục lớn, \\(b\\) là nửa trục nhỏ.

Ta có: \\(a = \\frac{{{major}}}{{2}} = {a}\\) cm, \\(b = \\frac{{{minor}}}{{2}} = {b}\\) cm

\\(V = \\frac{{4}}{{3}}\\pi \\cdot {a} \\cdot {b}^2\\)

\\(= \\frac{{4}}{{3}}\\pi \\cdot {a} \\cdot {b**2}\\)

\\(\\approx {float(volume.evalf()):.2f}\\) cm³

**Tính tiền thu được:**

Giá: {price:,} đồng / 1000 cm³

Tiền thu được = \\(V \\times \\frac{{{price}}}{{1000}}\\)

\\(= {float(volume.evalf()):.2f} \\times \\frac{{{price}}}{{1000}}\\)

\\(\\approx {int(total_price):,}\\) đồng

Kết luận: {int(total_price):,} đồng
"""


class PracticalSquareParabolaQuestion19(BaseVolumeQuestion):
    """
    Câu 19: Hình vuông & parabol
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        side = 20
        return {"side": side}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        side = params["side"]
        x = sp.Symbol('x')
        # Diện tích hình phẳng H = 800/3
        # Thể tích khối tròn xoay tính từ parabol
        volume_expr = sp.pi * sp.integrate((side/2 - x**2/side)**2, (x, -side/2, side/2))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        side = params["side"]
        x = sp.Symbol('x')
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * side**3)}\\)",  # Sai công thức
            f"\\(V = {sp.latex(sp.pi * side**2)}\\)",  # Sai công thức
            f"\\(V = {sp.latex(sp.pi * side)}\\)",  # Sai công thức
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        side = params["side"]
        return (
            f"Hình vuông ABCD cạnh {side} cm, đường cong BIC là một phần parabol đỉnh I. "
            f"Diện tích hình phẳng (H) bằng \\(\\frac{{800}}{{3}}\\). Tính thể tích khối tròn xoay."
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        side = params["side"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate((side/2 - x**2/side)**2, (x, -side/2, side/2))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho hình vuông ABCD cạnh {side} cm, đường cong BIC là một phần parabol đỉnh I. Diện tích hình phẳng (H) bằng \\(\\frac{{800}}{{3}}\\) cm².

**Thiết lập hệ tọa độ:**

Đặt hệ tọa độ với I ở gốc, trục Ox ngang, trục Oy thẳng đứng.

Parabol có dạng \\(y = ax^2\\) với đỉnh I tại gốc.

Điểm B và C ở vị trí \\(x = \\pm {side//2}\\), và \\(y = {side//2}\\).

Thay vào: \\({side//2} = a \\cdot {(side//2)**2}\\)

\\(a = \\frac{{{side//2}}}{{{(side//2)**2}}} = \\frac{{1}}{{{side//2}}}\\)

**Kiểm tra diện tích:**

Diện tích hình phẳng (H): \\(S = \\int_{{-{side//2}}}^{{{side//2}}} ({side//2} - \\frac{{x^2}}{{{side//2}}}) dx = \\frac{{800}}{{3}}\\)

Ta có: Thể tích khối tròn xoay khi quay (H) quanh trục Ox:

\\(V = \\pi \\int_{{-{side//2}}}^{{{side//2}}} ({side//2} - \\frac{{x^2}}{{{side//2}}})^2 dx\\)

Do hàm chẵn:

\\(V = 2\\pi \\int_0^{{{side//2}}} ({side//2} - \\frac{{x^2}}{{{side//2}}})^2 dx\\)

Tính nguyên hàm và thay cận:

Kết luận: \\(V = {sp.latex(volume_simplified)}\\) cm³
"""


class PracticalHatQuestion20(BaseVolumeQuestion):
    """
    Câu 20: Mũ Noel parabol
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        return {"OO_prime": 5, "OA": 10, "OB": 20}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        oo_prime = params["OO_prime"]
        oa = params["OA"]
        ob = params["OB"]
        x = sp.Symbol('x')
        # Parabol đi qua các điểm, tính thể tích
        volume_expr = sp.pi * sp.integrate((oa - (oa/ob**2)*x**2)**2, (x, -ob, ob))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"\\(V = {sp.latex(volume_simplified)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        oa = params["OA"]
        ob = params["OB"]
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * oa**2 * ob)}\\)",  # Công thức hình trụ
            f"\\(V = {sp.latex(sp.pi * oa**2 * ob / 3)}\\)",  # Công thức hình nón
            f"\\(V = {sp.latex(sp.pi * oa * ob)}\\)",  # Sai công thức
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        oo_prime = params["OO_prime"]
        oa = params["OA"]
        ob = params["OB"]
        return (
            f"Mũ ông già Noel hình tròn xoay. Mặt cắt là một phần parabol đỉnh A. "
            f"Biết \\(OO' = {oo_prime}\\) cm, \\(OA = {oa}\\) cm, \\(OB = {ob}\\) cm. Tính thể tích chiếc mũ."
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        oa = params["OA"]
        ob = params["OB"]
        x = sp.Symbol('x')
        volume_expr = sp.pi * sp.integrate((oa - (oa/ob**2)*x**2)**2, (x, -ob, ob))
        volume_simplified = sp.nsimplify(sp.simplify(volume_expr))
        return f"""
Cho mũ ông già Noel hình tròn xoay. Mặt cắt qua trục là parabol đỉnh A. Biết \\(OO' = {oo_prime}\\) cm, \\(OA = {oa}\\) cm, \\(OB = {ob}\\) cm.

**Thiết lập hệ tọa độ:**

Đặt hệ tọa độ với A tại \\((0, {oa})\\), O tại gốc tọa độ.

Parabol có dạng \\(y = {oa} - ax^2\\) với đỉnh A ở \\((0, {oa})\\).

Điểm B ở vị trí \\(({ob}, 0)\\), thay vào:

\\(0 = {oa} - a \\cdot {ob}^2\\)

\\(a = \\frac{{{oa}}}{{{ob}^2}} = \\frac{{{oa}}}{{{ob**2}}}\\)

Phương trình: \\(y = {oa} - \\frac{{{oa}}}{{{ob}^2}}x^2\\)

Ta có: Thể tích chiếc mũ (từ O' đến B, nhưng đơn giản hóa từ -OB đến OB):

\\(V = \\pi \\int_{{-{ob}}}^{{{ob}}} y^2 \\, dx = \\pi \\int_{{-{ob}}}^{{{ob}}} ({oa} - \\frac{{{oa}}}{{{ob}^2}}x^2)^2 dx\\)

Do hàm chẵn:

\\(V = 2\\pi \\int_0^{{{ob}}} ({oa} - \\frac{{{oa}}}{{{ob}^2}}x^2)^2 dx\\)

Tính nguyên hàm và thay cận:

Kết luận: \\(V = {sp.latex(volume_simplified)}\\) cm³
"""


class PracticalDrumQuestion21(BaseVolumeQuestion):
    """
    Câu 21: Cái trống mặt cầu
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        R = 0.5
        h = 0.8
        return {"R": R, "h": h}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        R = params["R"]
        h = params["h"]
        # Thể tích lát cầu đối xứng qua tâm: V = πh(R² - h²/12)
        # hoặc: V = πh(12R² - h²)/12
        # Chuyển sang phân số để có kết quả đẹp
        R_frac = sp.Rational(R)
        h_frac = sp.Rational(h)
        volume = sp.pi * h_frac * (R_frac**2 - h_frac**2 / 12)
        volume_simplified = sp.nsimplify(sp.simplify(volume))
        return f"\\(V = {sp.latex(volume_simplified)}\\) m³"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        R = params["R"]
        h = params["h"]
        wrongs = [
            f"\\(V = {sp.latex(sp.pi * R**2 * h)}\\) m³",  # Công thức hình trụ
            f"\\(V = {sp.latex(4/3 * sp.pi * R**3)}\\) m³",  # Thể tích cầu đầy
            f"\\(V = {sp.latex(sp.pi * h**2 * R)}\\) m³",  # Sai công thức
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        R = params["R"]
        h = params["h"]
        return (
            f"Cái trống trường giới hạn bởi mặt cầu bán kính \\(R = {R}\\) m và hai mặt phẳng song song cách đều tâm. "
            f"Chiều cao trống \\(h = {h}\\) m. Tính thể tích."
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        R = params["R"]
        h = params["h"]
        R_frac = sp.Rational(R)
        h_frac = sp.Rational(h)
        volume = sp.pi * h_frac * (R_frac**2 - h_frac**2 / 12)
        volume_simplified = sp.nsimplify(sp.simplify(volume))
        return f"""
Cho cái trống trường được tạo bởi mặt cầu bán kính \\(R = {R}\\) m, giới hạn bởi hai mặt phẳng song song cách đều tâm O, chiều cao trống \\(h = {h}\\) m.

**Công thức thể tích lát cầu đối xứng:**

Khi hai mặt phẳng song song cách đều tâm mặt cầu (mỗi mặt cách tâm \\(h/2\\)), thể tích phần giữa (lát cầu) được tính bởi:

\\(V = \\pi h \\left(R^2 - \\frac{{h^2}}{{12}}\\right)\\)

Hoặc viết dưới dạng: \\(V = \\frac{{\\pi h(12R^2 - h^2)}}{{12}}\\)

**Áp dụng:**

Với \\(R = {R}\\) m, \\(h = {h}\\) m:

\\(V = \\pi \\cdot {h} \\left({R}^2 - \\frac{{{h}^2}}{{12}}\\right)\\)

\\(= \\pi \\cdot {h} \\left({R**2} - \\frac{{{h**2}}}{{12}}\\right)\\)

\\(= \\pi \\cdot {h} \\left({R**2} - {h**2/12}\\right)\\)

Rút gọn:

\\(V = {sp.latex(volume_simplified)}\\) m³

\\(\\approx {float(volume_simplified.evalf()):.4f}\\) m³

Kết luận: \\(V = {sp.latex(volume_simplified)}\\) m³
"""




def get_available_question_types():
    return [
        PracticalVaseQuestion10,
        PracticalGlassQuestion17,
        PracticalWatermelonQuestion18,
        PracticalSquareParabolaQuestion19,
        PracticalHatQuestion20,
        PracticalDrumQuestion21
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

    return BaseVolumeQuestion.create_latex_document(questions, "Câu hỏi Ứng Dụng Thực Tế")


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
            latex_content = BaseVolumeQuestion.create_latex_document(questions_data, "Câu hỏi Ứng Dụng Thực Tế")
        else:
            latex_content = BaseVolumeQuestion.create_latex_document_with_format(questions_data, "Câu hỏi Ứng Dụng Thực Tế", fmt)

        filename = "practical_questions.tex"
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
