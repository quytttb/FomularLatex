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
# SCENARIO 3: BÀI TOÁN NGƯỢC (TÌM THAM SỐ)
# ============================================================================

class InverseVolumeQuestion14(BaseVolumeQuestion):
    """
    Câu 14: y=√x, y=0, x=b; tìm a sao cho V=2V₁
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        b = random.choice((3, 4, 5))
        return {"b": b, "k": 2}
    
    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        b = params["b"]
        k = params["k"]
        # V_total = π∫[0,b] x dx = πb²/2
        # V_partial(a) = π∫[0,a] x dx = πa²/2
        # V_total = k * V_partial => b²/2 = k * a²/2 => b² = k*a² => a² = b²/k => a = b/√k
        a_val = b / sp.sqrt(k)
        return f"\\(a = {sp.latex(sp.simplify(a_val))}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        b = params["b"]
        k = params["k"]
        correct_a = b / sp.sqrt(k)
        wrongs = [
            f"\\(a = {sp.latex(b * sp.sqrt(k))}\\)",  # Nhân √k thay vì chia
            f"\\(a = {sp.latex(b * k)}\\)",  # Nhân k thay vì chia √k
            f"\\(a = {sp.latex(b)}\\)",  # Bằng b
        ]
        return wrongs[:3]
    
    def generate_question_text(self) -> str:
        params = self.parameters
        b = params["b"]
        k = params["k"]
        return (
            f"Gọi (V) là thể tích khối tròn xoay tạo bởi \\(y = \\sqrt{{x}}\\), \\(y = 0\\), \\(x = {b}\\). "
            f"Đường thẳng \\(x = a\\) (\\(0 < a < {b}\\)) cắt đồ thị tại M. "
            f"Gọi \\(V_1\\) là thể tích khi quay tam giác OMH quanh Ox. Biết \\(V = {k}V_1\\). Tính \\(a\\)."
        )
    
    def generate_solution(self) -> str:
        params = self.parameters
        b = params["b"]
        k = params["k"]
        x = sp.Symbol('x')
        a_val = b / sp.sqrt(k)
        return f"""
Cho hàm số \\(y = \\sqrt{{x}}\\), trục hoành và đường thẳng \\(x = {b}\\). Đường thẳng \\(x = a\\) (với \\(0 < a < {b}\\)) cắt đồ thị tại M.

**Bài toán ngược:** Tìm \\(a\\) sao cho thể tích toàn phần V gấp {k} lần thể tích \\(V_1\\) (tam giác OMH quay quanh Ox).

Ta có: **Tính thể tích toàn phần V:**

\\(V = \\pi \\int_0^{{{b}}} y^2 \\, dx = \\pi \\int_0^{{{b}}} (\\sqrt{{x}})^2 dx\\)

\\(= \\pi \\int_0^{{{b}}} x \\, dx = \\pi \\left[ \\frac{{x^2}}{{2}} \\right]_0^{{{b}}}\\)

\\(= \\pi \\cdot \\frac{{{b}^2}}{{2}}\\)

**Tính thể tích \\(V_1\\):**

\\(V_1 = \\pi \\int_0^{{a}} x \\, dx = \\pi \\left[ \\frac{{x^2}}{{2}} \\right]_0^{{a}}\\)

\\(= \\pi \\cdot \\frac{{a^2}}{{2}}\\)

**Thiết lập phương trình:**

Theo đề bài: \\(V = {k}V_1\\)

\\(\\pi \\cdot \\frac{{{b}^2}}{{2}} = {k} \\cdot \\pi \\cdot \\frac{{a^2}}{{2}}\\)

Rút gọn:

\\({b}^2 = {k}a^2\\)

\\(a^2 = \\frac{{{b}^2}}{{{k}}}\\)

\\(a = \\frac{{{b}}}{{\\sqrt{{{k}}}}}\\)

Rút gọn căn:

\\(a = {sp.latex(sp.simplify(a_val))}\\)

Kết luận: \\(a = {sp.latex(sp.simplify(a_val))}\\)
"""


# ============================================================================


def get_available_question_types():
    return [
        InverseVolumeQuestion14
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

    return BaseVolumeQuestion.create_latex_document(questions, "Câu hỏi Bài Toán Ngược")


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
            latex_content = BaseVolumeQuestion.create_latex_document(questions_data, "Câu hỏi Bài Toán Ngược")
        else:
            latex_content = BaseVolumeQuestion.create_latex_document_with_format(questions_data, "Câu hỏi Bài Toán Ngược", fmt)

        filename = "inverse_questions.tex"
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
