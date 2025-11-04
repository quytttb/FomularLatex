"""
Dạng toán tối ưu: Hai mặt cầu và một mặt phẳng — tối thiểu MA + NA

Bài toán: Cho hai mặt cầu S1, S2 và mặt phẳng (P). Lấy M ∈ S1, N ∈ S2, A ∈ (P).
Tối thiểu T = MA + NA. Sinh tham số ngẫu nhiên và hỗ trợ target_point ∈ {A,M,N}.
"""

import logging
import os
import random
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from fractions import Fraction
from typing import Union
import sympy as sp
import math
import re

"""
Các hàm tiện ích LaTeX cho hệ thống sinh câu hỏi toán tối ưu hóa
"""


# ==== Helpers to format plane equation nicely (clean signs, hide coefficient 1) ====
def clean_latex_expression(expression: str) -> str:
    """Simple cleanup: fix '+ -', '+-' and trim redundant spaces; hide leading '+'."""
    if not expression:
        return "0"
    expr = expression.replace("+ -", "- ")
    expr = expr.replace("+-", "-")
    expr = expr.replace("-+", "-")
    # collapse whitespace
    expr = re.sub(r"\s+", " ", expr.strip())
    # drop leading plus
    if expr.startswith('+'):
        expr = expr[1:].lstrip()
    # tidy 1x -> x, - 1x -> - x
    expr = re.sub(r"\b1x\b", "x", expr)
    expr = re.sub(r"\b1y\b", "y", expr)
    expr = re.sub(r"\b1z\b", "z", expr)
    expr = re.sub(r"- 1x\b", "- x", expr)
    expr = re.sub(r"- 1y\b", "- y", expr)
    expr = re.sub(r"- 1z\b", "- z", expr)
    return expr


def _format_coeff_term(coeff: int, is_first: bool, var: str, power: int = 1) -> str:
    """Format a single term a*var^power with proper sign and omitted 1 when needed."""
    if coeff == 0:
        return ""
    sign = "" if is_first else (" - " if coeff < 0 else " + ")
    abs_coeff = abs(int(coeff))
    if power == 0:
        # constant term — ensure leading minus shown when first and negative
        if is_first:
            return f"-{abs_coeff}" if coeff < 0 else f"{abs_coeff}"
        return f"{sign}{abs_coeff}"
    # decide coefficient string (hide 1)
    coeff_str = "" if abs_coeff == 1 else str(abs_coeff)
    if power == 1:
        term_core = f"{coeff_str}{var}" if coeff_str else var
    else:
        term_core = f"{coeff_str}{var}^{{{power}}}" if coeff_str else f"{var}^{{{power}}}"
    if is_first and coeff < 0:
        return f"-{term_core}"
    return f"{sign}{term_core}"


def format_plane_equation_latex(A: int, B: int, C: int, D: int) -> str:
    """Return cleaned string for Ax + By + Cz + D using human-friendly signs and 1 omission."""
    parts = []
    tx = _format_coeff_term(A, is_first=len(parts) == 0, var='x', power=1)
    if tx:
        parts.append(tx)
    ty = _format_coeff_term(B, is_first=len(parts) == 0, var='y', power=1)
    if ty:
        parts.append(ty)
    tz = _format_coeff_term(C, is_first=len(parts) == 0, var='z', power=1)
    if tz:
        parts.append(tz)
    td = _format_coeff_term(D, is_first=len(parts) == 0, var='', power=0)
    if td:
        parts.append(td)
    return clean_latex_expression("".join(parts))


@dataclass
class GeneratorConfig:
    seed: Optional[int] = None
    exact_mode: bool = True
    coord_min: int = -2
    coord_max: int = 5
    vector_max_component: int = 3
    time_choices: Tuple[int, ...] = (3, 4, 5, 6, 7, 8)
    pretty: bool = False


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
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        # Không dùng nsimplify, giữ nguyên symbolic expression
        if isinstance(value, (sp.Basic, sp.Expr)):
            expr = value
        elif isinstance(value, (int, sp.Integer)):
            expr = sp.Integer(value)
        elif hasattr(value, 'numerator') and hasattr(value, 'denominator'):
            expr = sp.Rational(value.numerator, value.denominator)
        else:
            expr = sp.sympify(value)
        
        if isinstance(expr, sp.Rational):
            if expr.q == 1:
                return str(expr.p)
            return f"{expr.p}/{expr.q}"
        return sp.latex(expr)
    except Exception:
        return str(value)


def format_coord_solution(coord):
    try:
        # Không dùng nsimplify, giữ nguyên symbolic expression
        if isinstance(coord, (sp.Basic, sp.Expr)):
            expr = coord
        elif isinstance(coord, (int, sp.Integer)):
            expr = sp.Integer(coord)
        elif hasattr(coord, 'numerator') and hasattr(coord, 'denominator'):
            expr = sp.Rational(coord.numerator, coord.denominator)
        else:
            expr = sp.sympify(coord)
            
        if isinstance(expr, sp.Rational):
            if expr.q == 1:
                return str(expr.p)
            return f"\\dfrac{{{expr.p}}}{{{expr.q}}}"
        return sp.latex(expr)
    except Exception:
        return str(coord)


def format_scientific(num: Union[int, float, sp.Basic], precision: int = 3) -> str:
    """Trả về biểu diễn chính xác (không thập phân)."""
    if isinstance(num, (sp.Basic, sp.Expr)):
        expr = num
    elif isinstance(num, (int, sp.Integer)):
        expr = sp.Integer(num)
    elif isinstance(num, Fraction):
        expr = sp.Rational(num.numerator, num.denominator)
    else:
        expr = sp.sympify(num)
    return sp.latex(expr)


def format_sqrt(number: Union[int, float, sp.Basic]) -> str:
    """Biểu diễn căn bậc hai dạng LaTeX (chính xác)."""
    if isinstance(number, (sp.Basic, sp.Expr)):
        expr = number
    elif isinstance(number, (int, sp.Integer)):
        expr = sp.Integer(number)
    elif isinstance(number, Fraction):
        expr = sp.Rational(number.numerator, number.denominator)
    else:
        expr = sp.sympify(number)
    return sp.latex(sp.sqrt(expr))


# format_sqrt_improved bị loại bỏ (trùng lặp logic với format_sqrt)


def format_dimension(value: Union[float, sp.Basic], unit: str = "mét") -> str:
    """Định dạng độ lớn kèm đơn vị ở dạng chính xác."""
    return f"{format_number_clean(value)} {unit}"


def strip_latex_inline_math(ans: str) -> str:
    if ans.startswith("\\(") and ans.endswith("\\)"):
        return ans[2:-2].strip()
    if ans.startswith("$") and ans.endswith("$"):
        return ans[1:-1].strip()
    return ans


def format_dfrac(num, denom):
    """Format fraction using dfrac for better display (chính xác)."""
    if denom == 0:
        return "undefined"
    try:
        # Chuyển về integer nếu có thể, nếu không giữ nguyên symbolic
        if hasattr(num, 'is_integer') and num.is_integer and hasattr(denom, 'is_integer') and denom.is_integer:
            frac = sp.Rational(int(num), int(denom))
        elif isinstance(num, (int, sp.Integer)) and isinstance(denom, (int, sp.Integer)):
            frac = sp.Rational(int(num), int(denom))
        else:
            # Giữ nguyên dạng symbolic
            return f"\\dfrac{{{sp.latex(num)}}}{{{sp.latex(denom)}}}"
        
        if isinstance(frac, sp.Rational):
            if frac.q == 1:
                return str(frac.p)
            elif frac.p == 0:
                return "0"
            else:
                return f"\\dfrac{{{frac.p}}}{{{frac.q}}}"
        else:
            return f"\\dfrac{{{sp.latex(num)}}}{{{sp.latex(denom)}}}"
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


def to_decimal_comma(value: Any) -> str:
    s = str(value)
    return s.replace('.', ',')

def format_time_hours_or_minutes(hours_value: float, decimal_places: int = 1) -> str:
    """
    Định dạng thời gian theo giờ: nếu < 1 giờ thì hiển thị theo phút.
    Loại bỏ phần .0 khi không cần.
    """
    epsilon = 1e-12
    if hours_value < 1.0 - 1e-9:
        minutes = round(hours_value * 60.0 + epsilon, decimal_places)
        minutes_str = f"{minutes:.{decimal_places}f}"
        if decimal_places > 0 and minutes_str.endswith("." + "0" * decimal_places):
            minutes_str = minutes_str.split(".")[0]
        return f"{minutes_str}\\,\\text{{phút}}"
    hours_rounded = round(hours_value + epsilon, decimal_places)
    hours_str = f"{hours_rounded:.{decimal_places}f}"
    if decimal_places > 0 and hours_str.endswith("." + "0" * decimal_places):
        hours_str = hours_str.split(".")[0]
    return f"{hours_str}\\,\\text{{giờ}}"

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
Lớp cơ sở cho các dạng bài toán tối ưu hóa
"""


class BaseOptimizationQuestion(ABC):
    """
    Lớp cơ sở cho tất cả các dạng bài toán tối ưu hóa
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
    def create_latex_document(questions: List[str], title: str = "Câu hỏi Tối ưu hóa") -> str:
        """Tạo document LaTeX hoàn chỉnh"""
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{polyglossia}}
\\setmainlanguage{{vietnamese}}
\\setmainfont{{Latin Modern Roman}}
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
    def create_latex_document_with_format(questions_data: List[Union[str, Tuple[str, str]]], title: str = "Câu hỏi Tối ưu hóa", fmt: int = 1) -> str:
        """Tạo document LaTeX với 2 format khác nhau"""
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{polyglossia}}
\\setmainlanguage{{vietnamese}}
\\setmainfont{{Latin Modern Roman}}
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
            # Format 2: câu hỏi + lời giải, đáp án ngay sau từng câu
            for idx, question_data in enumerate(questions_data, 1):
                if isinstance(question_data, tuple):
                    question_content, correct_answer = question_data
                    latex_content += question_content + "\n\n"
                    # In đáp án ngay sau lời giải của câu hiện tại
                    ans = correct_answer
                    if ans.startswith("\\(") and ans.endswith("\\)"):
                        ans = ans[2:-2].strip()
                    if ans.startswith("$") and ans.endswith("$"):
                        ans = ans[1:-1].strip()
                    ans_comma = ans.replace('.', ',')
                    latex_content += f"Đáp án: \\({ans}\\) | \\({ans_comma}\\)\n\n"
                else:
                    # Fallback cho format cũ
                    latex_content += f"{question_data}\n\n"

        latex_content += "\\end{document}"
        return latex_content


    """Khoảng cách nhỏ nhất giữa hai khinh khí cầu chuyển động vuông góc trong không gian với độ cao không đổi.
    """

# ======================
# Dạng toán nâng cao: Hai mặt cầu và một mặt phẳng — tối thiểu MA + NA
# ======================

class MinSumTwoSpheresToPlaneQuestion(BaseOptimizationQuestion):
    """
    Cho hai mặt cầu S1, S2 và mặt phẳng (P). Lấy M ∈ S1, N ∈ S2, A ∈ (P).
    Tối thiểu T = MA + NA.

    Ý tưởng: Với A cố định, khoảng cách tối thiểu từ A đến mặt cầu S bán kính r, tâm C là d(A, S) = | |AC| - r |.
    Do đó min_{M,N}(MA+NA) = min_{A∈(P)} [ | |AC1| - r1 | + | |AC2| - r2 | ].

    Trường hợp điển hình:
    - Nếu f(C1)·f(C2) < 0 (hai tâm khác phía): A_min = C1C2 ∩ (P) và |AC1|+|AC2| đạt min = |C1C2|.
      Khi đó T_min ứng viên = max(0, |C1C2| - (r1 + r2)).
    - Nếu f(C1)·f(C2) > 0 (hai tâm cùng phía): phản chiếu C2 thành C2' qua (P),
      A_min = C1C2' ∩ (P), |AC1|+|AC2| = |AC1|+|AC2'| đạt min = |C1C2'| ⇒ T_min ứng viên = max(0, |C1C2'| - (r1 + r2)).
    Cần kiểm tra thêm điều kiện hình học (A_min nằm giữa các điểm, A_min ngoài hai cầu...).
    """

    # Danh sách tên điểm có thể random (loại trừ M, N, A vì đã dùng trong đề bài)
    POINT_NAMES = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    def __init__(self, config: Optional["GeneratorConfig"] = None):
        super().__init__(config)
        # Giữ nguyên việc khởi tạo rỗng; tham số sẽ được sinh tại các hàm generate_*

    def _random_nonzero_vector(self, low: int, high: int) -> Tuple[int, int, int]:
        """Sinh véctơ pháp tuyến khác (0,0,0)."""
        while True:
            a = random.randint(low, high)
            b = random.randint(low, high)
            c = random.randint(low, high)
            if not (a == 0 and b == 0 and c == 0):
                return a, b, c

    def _random_point(self, low: int, high: int) -> Tuple[int, int, int]:
        return (
            random.randint(low, high),
            random.randint(low, high),
            random.randint(low, high),
        )

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh (a,b,c,d) mặt phẳng; tâm C1, C2; bán kính r1, r2."""
        cfg = self.config
        low, high = cfg.coord_min, cfg.coord_max

        # Chế độ sinh số "đẹp": chọn mặt phẳng trùng trục và hai tâm thẳng hàng theo trục đó
        if getattr(cfg, 'pretty', False):
            axis = random.choice(['x', 'y', 'z'])
            k = random.choice([-2, -1, 0, 1, 2])
            if axis == 'x':
                a, b, c, d = 1, 0, 0, -k
                y0 = random.choice([-1, 0, 1])
                z0 = random.choice([-1, 0, 1])
                L = random.choice([4, 5, 6])
                s1 = random.randint(1, L - 1)
                s2 = L - s1
                x1, y1, z1 = k - s1, y0, z0
                x2, y2, z2 = k + s2, y0, z0
            elif axis == 'y':
                a, b, c, d = 0, 1, 0, -k
                x0 = random.choice([-1, 0, 1])
                z0 = random.choice([-1, 0, 1])
                L = random.choice([4, 5, 6])
                s1 = random.randint(1, L - 1)
                s2 = L - s1
                x1, y1, z1 = x0, k - s1, z0
                x2, y2, z2 = x0, k + s2, z0
            else:  # axis == 'z'
                a, b, c, d = 0, 0, 1, -k
                x0 = random.choice([-1, 0, 1])
                y0 = random.choice([-1, 0, 1])
                L = random.choice([4, 5, 6])
                s1 = random.randint(1, L - 1)
                s2 = L - s1
                x1, y1, z1 = x0, y0, k - s1
                x2, y2, z2 = x0, y0, k + s2

            # Đảm bảo hệ số mặt phẳng đều khác 0 như yêu cầu: A, B, C, D ≠ 0
            if a == 0 or b == 0 or c == 0 or d == 0:
                def _rnz(lo: int, hi: int) -> int:
                    while True:
                        vv = random.randint(lo, hi)
                        if vv != 0:
                            return vv
                a = _rnz(low, high)
                b = _rnz(low, high)
                c = _rnz(low, high)
                d = _rnz(low - 2, high + 2)

            # Bán kính nhỏ, đảm bảo L - (r1+r2) >= 1 để T nguyên dương
            possible_r = [1, 2, 3]
            r1 = random.choice(possible_r)
            remaining = max(1, L - r1 - 1)
            candidates_r2 = [r for r in possible_r if r <= remaining]
            r2 = random.choice(candidates_r2) if candidates_r2 else 1

            point_names = random.sample(self.POINT_NAMES, 2)
            center1_name, center2_name = point_names[0], point_names[1]
            target_point = random.choice(["A", "M", "N"])

            return {
                "a": a, "b": b, "c": c, "d": d,
                "x1": x1, "y1": y1, "z1": z1, "r1": r1,
                "x2": x2, "y2": y2, "z2": z2, "r2": r2,
                "center1_name": center1_name,
                "center2_name": center2_name,
                "target_point": target_point,
            }

        def _rand_nonzero(lo: int, hi: int) -> int:
            while True:
                v = random.randint(lo, hi)
                if v != 0:
                    return v

        a = _rand_nonzero(low, high)
        b = _rand_nonzero(low, high)
        c = _rand_nonzero(low, high)
        d = _rand_nonzero(low - 2, high + 2)

        x1, y1, z1 = self._random_point(low, high)
        x2, y2, z2 = self._random_point(low, high)
        while (x2, y2, z2) == (x1, y1, z1):
            x2, y2, z2 = self._random_point(low, high)

        # Bán kính dương nhỏ gọn để tránh chồng lấn quá nhiều
        r1 = random.randint(1, max(2, (high - low)//2))
        r2 = random.randint(1, max(2, (high - low)//2))

        # Random tên điểm cho tâm hai mặt cầu (chọn 2 tên khác nhau)
        point_names = random.sample(self.POINT_NAMES, 2)
        center1_name, center2_name = point_names[0], point_names[1]

        # Random chọn target point để hỏi
        target_point = random.choice(["A", "M", "N"])

        return {
            "a": a, "b": b, "c": c, "d": d,
            "x1": x1, "y1": y1, "z1": z1, "r1": r1,
            "x2": x2, "y2": y2, "z2": z2, "r2": r2,
            "center1_name": center1_name,
            "center2_name": center2_name,
            "target_point": target_point,
        }

    @staticmethod
    def _dot_plane(a: int, b: int, c: int, d: int, x: int, y: int, z: int) -> sp.Expr:
        return sp.Add(sp.Integer(a)*x, sp.Integer(b)*y, sp.Integer(c)*z, sp.Integer(d))

    @staticmethod
    def _norm(vec: Tuple[sp.Expr, sp.Expr, sp.Expr]) -> sp.Expr:
        vx, vy, vz = vec
        return sp.sqrt(sp.Add(vx**2, vy**2, vz**2))

    def _compute_core(self) -> Dict[str, Any]:
        """Tính các đại lượng: f(C_i), phản chiếu, điểm A_min ứng viên, T_min ứng viên."""
        p = self.parameters
        a, b, c, d = p["a"], p["b"], p["c"], p["d"]
        x1, y1, z1, r1 = p["x1"], p["y1"], p["z1"], p["r1"]
        x2, y2, z2, r2 = p["x2"], p["y2"], p["z2"], p["r2"]

        # Hàm f(X) của (P)
        def f_point(x, y, z):
            return sp.Add(sp.Integer(a)*x, sp.Integer(b)*y, sp.Integer(c)*z, sp.Integer(d))

        fC1 = f_point(x1, y1, z1)
        fC2 = f_point(x2, y2, z2)
        n2 = sp.Add(sp.Integer(a)**2, sp.Integer(b)**2, sp.Integer(c)**2)
        n_norm = sp.sqrt(n2)

        # Vectơ, độ dài giữa tâm
        C1C2_vec = (sp.Integer(x2 - x1), sp.Integer(y2 - y1), sp.Integer(z2 - z1))
        C1C2_len = self._norm(C1C2_vec)

        # Phản chiếu C2 qua (P)
        C2_ref = (
            x2 - sp.Rational(2)*fC2*a/n2,
            y2 - sp.Rational(2)*fC2*b/n2,
            z2 - sp.Rational(2)*fC2*c/n2,
        )

        # Chọn đường thẳng tối ưu hóa tổng khoảng cách (kiểm tra cùng phía, tránh ép kiểu sign(symbolic))
        s1 = int(fC1)
        s2 = int(fC2)
        same_side = (s1 != 0 and s2 != 0 and s1 * s2 > 0)
        if same_side:
            Ux, Uy, Uz = C2_ref
        else:
            Ux, Uy, Uz = x2, y2, z2

        # Giao của đường C1U với (P): C1 + t*(U - C1)
        denom_t = sp.Add(sp.Integer(a)*(Ux - x1), sp.Integer(b)*(Uy - y1), sp.Integer(c)*(Uz - z1))
        t_star = None
        A_star = None
        denom_t_s = sp.simplify(denom_t)
        if denom_t_s.is_zero is not True:
            t_star = sp.simplify(-fC1 / denom_t_s)
            A_star = (
                sp.simplify(x1 + t_star*(Ux - x1)),
                sp.simplify(y1 + t_star*(Uy - y1)),
                sp.simplify(z1 + t_star*(Uz - z1)),
            )
        else:
            # Nếu đường C1U nằm trong (P) (tức f(C1)=0 và phương song song với (P)), thêm ứng viên trên đường này
            if sp.simplify(fC1).is_zero is True:
                L_len = self._norm((Ux - x1, Uy - y1, Uz - z1))
                # Ứng viên T_min theo lý thuyết: |L - (r1 + r2)|
                T_line_expr = sp.Abs(L_len - (r1 + r2))
                # Chọn A trên đường C1U: nếu L>0, lấy t = r1/L (điểm cách C1 một đoạn r1)
                L_len_s = sp.simplify(L_len)
                if L_len_s.is_zero is not True:
                    t_line = sp.simplify(sp.Rational(r1, 1) / L_len_s)
                else:
                    t_line = sp.Integer(0)
                A_line = (
                    sp.simplify(x1 + t_line*(Ux - x1)),
                    sp.simplify(y1 + t_line*(Uy - y1)),
                    sp.simplify(z1 + t_line*(Uz - z1)),
                )
            else:
                T_line_expr = None
                A_line = None

        # Khoảng cách |A_min*C1| và |A_min*C2|
        AC1 = None
        AC2 = None
        if A_star is not None:
            AC1 = self._norm((A_star[0] - x1, A_star[1] - y1, A_star[2] - z1))
            AC2 = self._norm((A_star[0] - x2, A_star[1] - y2, A_star[2] - z2))

        # Ứng viên tổng khoảng cách tâm: |C1U|
        if same_side:
            C1U_len = self._norm((Ux - x1, Uy - y1, Uz - z1))
            centers_sum_min = C1U_len
        else:
            centers_sum_min = C1C2_len

        # Ứng viên T_min: |d1 - r1| + |d2 - r2|
        T_candidate = None
        if AC1 is not None and AC2 is not None:
            T_candidate = sp.Add(sp.Abs(AC1 - r1), sp.Abs(AC2 - r2))
        # Các dữ kiện trên (P): hình chiếu tâm và "đĩa" giao (nếu có)
        A1_proj = (
            x1 - fC1*a/n2,
            y1 - fC1*b/n2,
            z1 - fC1*c/n2,
        )
        A2_proj = (
            x2 - fC2*a/n2,
            y2 - fC2*b/n2,
            z2 - fC2*c/n2,
        )
        dist1_plane = sp.Mul(sp.Abs(fC1), sp.Pow(n_norm, -1), evaluate=False)
        dist2_plane = sp.Mul(sp.Abs(fC2), sp.Pow(n_norm, -1), evaluate=False)
        r1_on_plane = sp.sqrt(
            sp.Max(
                sp.Integer(0),
                sp.Add(
                    sp.Integer(r1)**2,
                    -sp.Mul(fC1**2, sp.Pow(n2, -1), evaluate=False),
                    evaluate=False,
                ),
            )
        )
        r2_on_plane = sp.sqrt(
            sp.Max(
                sp.Integer(0),
                sp.Add(
                    sp.Integer(r2)**2,
                    -sp.Mul(fC2**2, sp.Pow(n2, -1), evaluate=False),
                    evaluate=False,
                ),
            )
        )
        A1A2_vec = (A1_proj[0] - A2_proj[0], A1_proj[1] - A2_proj[1], A1_proj[2] - A2_proj[2])
        A1A2_len = self._norm(A1A2_vec)

        def _to_float(expr: sp.Expr) -> float:
            try:
                return float(sp.N(expr))
            except Exception:
                return float(expr)

        # Ứng viên (T, A, nhãn)
        candidates: List[Tuple[sp.Expr, Tuple[sp.Expr, sp.Expr, sp.Expr], str]] = []

        # 1) A1: chân chiếu I1
        A1I2_len = self._norm((A1_proj[0] - x2, A1_proj[1] - y2, A1_proj[2] - z2))
        T1_expr = sp.Add(sp.Abs(dist1_plane - r1), sp.Abs(A1I2_len - r2))
        candidates.append((sp.simplify(T1_expr), A1_proj, "A1"))

        # 2) A2: chân chiếu I2
        A2I1_len = self._norm((A2_proj[0] - x1, A2_proj[1] - y1, A2_proj[2] - z1))
        T2_expr = sp.Add(sp.Abs(dist2_plane - r2), sp.Abs(A2I1_len - r1))
        candidates.append((sp.simplify(T2_expr), A2_proj, "A2"))

        # 3) A_sum: giao C1U với (P) (nếu có) hoặc đường C1U nằm trong (P)
        if A_star is not None and T_candidate is not None:
            candidates.append((sp.simplify(T_candidate), A_star, "line"))
        elif 'T_line_expr' in locals() and T_line_expr is not None and A_line is not None:
            candidates.append((sp.simplify(T_line_expr), A_line, "line_in_plane"))

        def _score(expr: sp.Expr) -> float:
            try:
                return float(sp.N(expr))
            except Exception:
                return float(expr)

        # Chọn ứng viên có T nhỏ nhất trên toàn bộ candidates (không loại T=0)
        def _num_val(expr: sp.Expr) -> float:
            try:
                return float(sp.N(expr))
            except Exception:
                return float('inf')

        best_T, best_A, best_label = min(candidates, key=lambda item: _num_val(item[0]))

        # Tính M_opt và N_opt từ A_opt
        Ax, Ay, Az = best_A
        
        # Tính M_opt: điểm trên S1 gần A_opt nhất
        AC1_dist = self._norm((Ax - x1, Ay - y1, Az - z1))
        AC1_zero = sp.simplify(AC1_dist).is_zero
        if AC1_zero is True:
            # A trùng tâm C1: chọn điểm trên S1 theo hướng pháp tuyến mặt phẳng để nằm trên mặt cầu
            M_opt = (
                sp.simplify(x1 + r1 * a / n_norm),
                sp.simplify(y1 + r1 * b / n_norm),
                sp.simplify(z1 + r1 * c / n_norm),
            )
        else:
            # M = C1 + r1 * (A-C1)/|A-C1|
            unit_vec1 = ((Ax - x1)/AC1_dist, (Ay - y1)/AC1_dist, (Az - z1)/AC1_dist)
            M_opt = (
                sp.simplify(x1 + r1 * unit_vec1[0]),
                sp.simplify(y1 + r1 * unit_vec1[1]), 
                sp.simplify(z1 + r1 * unit_vec1[2])
            )
        
        # Tính N_opt: điểm trên S2 gần A_opt nhất
        AC2_dist = self._norm((Ax - x2, Ay - y2, Az - z2))
        AC2_zero = sp.simplify(AC2_dist).is_zero
        if AC2_zero is True:
            # A trùng tâm C2: chọn điểm trên S2 theo hướng pháp tuyến mặt phẳng để nằm trên mặt cầu
            N_opt = (
                sp.simplify(x2 + r2 * a / n_norm),
                sp.simplify(y2 + r2 * b / n_norm),
                sp.simplify(z2 + r2 * c / n_norm),
            )
        else:
            # N = C2 + r2 * (A-C2)/|A-C2|
            unit_vec2 = ((Ax - x2)/AC2_dist, (Ay - y2)/AC2_dist, (Az - z2)/AC2_dist)
            N_opt = (
                sp.simplify(x2 + r2 * unit_vec2[0]),
                sp.simplify(y2 + r2 * unit_vec2[1]),
                sp.simplify(z2 + r2 * unit_vec2[2])
            )

        return {
            "a": a, "b": b, "c": c, "d": d,
            "C1": (x1, y1, z1), "r1": r1, "C2": (x2, y2, z2), "r2": r2,
            "fC1": fC1, "fC2": fC2, "n2": n2, "n_norm": n_norm,
            "same_side": same_side,
            "C2_ref": C2_ref,
            "t_star": t_star, "A_star": A_star,
            "AC1": AC1, "AC2": AC2,
            "centers_sum_min": centers_sum_min,
            "C1C2_len": C1C2_len,
            "T_candidate": T_candidate,
            "A1_proj": A1_proj, "A2_proj": A2_proj,
            "dist1_plane": dist1_plane, "dist2_plane": dist2_plane,
            "r1_on_plane": r1_on_plane, "r2_on_plane": r2_on_plane,
            "A1A2_len": A1A2_len,
            "A_opt": best_A, "T_min_expr": best_T, "case_label": best_label,
            "M_opt": M_opt, "N_opt": N_opt,
        }

    def calculate_answer(self) -> str:
        core = self._compute_core()
        p = self.parameters
        target_point = p["target_point"]
        T_min = core["T_min_expr"]
        
        if target_point == "A":
            Ax, Ay, Az = core["A_opt"]
            expr = sp.simplify(sp.Add(Ax, Ay, Az, T_min))
        elif target_point == "M":
            Mx, My, Mz = core["M_opt"] 
            expr = sp.simplify(sp.Add(Mx, My, Mz, T_min))
        else:  # target_point == "N"
            Nx, Ny, Nz = core["N_opt"]
            expr = sp.simplify(sp.Add(Nx, Ny, Nz, T_min))
            
        # Trả về chỉ giá trị làm tròn 2 chữ số (không hiển thị dạng chuẩn và dấu ≈)
        approx_val = float(sp.N(expr, 8))
        approx_str = f"{approx_val:.2f}"
        return f"\\( {approx_str} \\)"

    def generate_wrong_answers(self) -> List[str]:
        core = self._compute_core()
        p = self.parameters
        target_point = p["target_point"]
        wrongs: List[str] = []

        (x1, y1, z1), (x2, y2, z2) = core["C1"], core["C2"]
        rsum = core["r1"] + core["r2"]
        T_min_expr = core["T_min_expr"]
        centers_sum_min = core["centers_sum_min"]

        # Tính sum dựa trên target_point
        if target_point == "A":
            Ax, Ay, Az = core["A_opt"]
            sumTarget = sp.Add(Ax, Ay, Az)
            # Sai: thay A_opt bằng tâm I1 hoặc I2 nhưng T đúng
            sumC1 = sp.Integer(x1) + sp.Integer(y1) + sp.Integer(z1)
            sumC2 = sp.Integer(x2) + sp.Integer(y2) + sp.Integer(z2)
            exprC1 = sp.simplify(sp.Add(sumC1, T_min_expr))
            exprC2 = sp.simplify(sp.Add(sumC2, T_min_expr))
            wrongs.extend([
                f"\\( {float(sp.N(exprC1, 8)):.2f} \\)",
                f"\\( {float(sp.N(exprC2, 8)):.2f} \\)"
            ])
        elif target_point == "M":
            Mx, My, Mz = core["M_opt"]
            sumTarget = sp.Add(Mx, My, Mz)
            # Sai: thay M_opt bằng tâm C1 hoặc A_opt
            sumC1 = sp.Integer(x1) + sp.Integer(y1) + sp.Integer(z1)
            Ax, Ay, Az = core["A_opt"]
            sumA = sp.Add(Ax, Ay, Az)
            exprC1M = sp.simplify(sp.Add(sumC1, T_min_expr))
            exprAM = sp.simplify(sp.Add(sumA, T_min_expr))
            wrongs.extend([
                f"\\( {float(sp.N(exprC1M, 8)):.2f} \\)",
                f"\\( {float(sp.N(exprAM, 8)):.2f} \\)"
            ])
        else:  # target_point == "N"
            Nx, Ny, Nz = core["N_opt"]
            sumTarget = sp.Add(Nx, Ny, Nz)
            # Sai: thay N_opt bằng tâm C2 hoặc A_opt
            sumC2 = sp.Integer(x2) + sp.Integer(y2) + sp.Integer(z2)
            Ax, Ay, Az = core["A_opt"]
            sumA = sp.Add(Ax, Ay, Az)
            exprC2N = sp.simplify(sp.Add(sumC2, T_min_expr))
            exprAN = sp.simplify(sp.Add(sumA, T_min_expr))
            wrongs.extend([
                f"\\( {float(sp.N(exprC2N, 8)):.2f} \\)",
                f"\\( {float(sp.N(exprAN, 8)):.2f} \\)"
            ])

        # 1) Sai: bỏ r1,r2 → dùng tổng khoảng cách tâm tối thiểu
        expr1 = sp.simplify(sp.Add(sumTarget, centers_sum_min))
        approx1 = float(sp.N(expr1, 8))
        wrongs.append(f"\\( {approx1:.2f} \\)")
        # 2) Sai: cộng r1+r2 thay vì trừ
        expr2 = sp.simplify(sp.Add(sumTarget, centers_sum_min, rsum))
        approx2 = float(sp.N(expr2, 8))
        wrongs.append(f"\\( {approx2:.2f} \\)")

        unique_wrongs: List[str] = []
        ans = self.calculate_answer()
        for w in wrongs:
            if w != ans and w not in unique_wrongs:
                unique_wrongs.append(w)
            if len(unique_wrongs) >= 3:
                break
        if len(unique_wrongs) < 3:
            dist1_to_plane = sp.Abs(core['fC1'])/core['n_norm']
            dist2_to_plane = sp.Abs(core['fC2'])/core['n_norm']
            sum_centers_to_plane = sp.Add(dist1_to_plane, dist2_to_plane)
            expr3 = sp.simplify(sp.Add(sumTarget, sum_centers_to_plane))
            cand = f"\\( {float(sp.N(expr3, 8)):.2f} \\)"
            if cand != ans and cand not in unique_wrongs:
                unique_wrongs.append(cand)
        return unique_wrongs[:3]

    def generate_question_text(self) -> str:
        p = self.parameters
        a, b, c, d = p["a"], p["b"], p["c"], p["d"]
        x1, y1, z1, r1 = p["x1"], p["y1"], p["z1"], p["r1"]
        x2, y2, z2, r2 = p["x2"], p["y2"], p["z2"], p["r2"]
        center1_name = p["center1_name"]
        center2_name = p["center2_name"]
        target_point = p["target_point"]

        def shift(var: str, center: int) -> str:
            return f"{var} - {abs(center)}" if center >= 0 else f"{var} + {abs(center)}"

        def squared(var: str, center: int) -> str:
            if center == 0:
                return f"{var}^2"
            return f"( {shift(var, center)} )^2"

        # Bán kính ở vế phải in dạng chuẩn là kết quả bình phương (không dùng ^2)
        r1_sq = r1 * r1
        r2_sq = r2 * r2
        S1_tex = f"S_1:\\ {squared('x', x1)} + {squared('y', y1)} + {squared('z', z1)} = {r1_sq}"
        S2_tex = f"S_2:\\ {squared('x', x2)} + {squared('y', y2)} + {squared('z', z2)} = {r2_sq}"
        plane_expr = format_plane_equation_latex(a, b, c, d)
        plane_tex = f"(P): {plane_expr} = 0"

        # Tạo câu hỏi theo target_point
        if target_point == "A":
            point_desc = "điểm \\(A(a;b;c)\\) thuộc \\((P)\\)"
            question_expr = "\\(a + b + c + T\\)"
        elif target_point == "M":
            point_desc = "điểm \\(M(m;n;p)\\) thuộc \\((S_1)\\)"
            question_expr = "\\(m + n + p + T\\)"
        else:  # target_point == "N" 
            point_desc = "điểm \\(N(u;v;w)\\) thuộc \\((S_2)\\)"
            question_expr = "\\(u + v + w + T\\)"

        text = (
            "Cho hai mặt cầu \n"
            f"\\[{S1_tex},\\]\n"
            f"\\[{S2_tex},\\]\n"
            f"với \\(r_1,r_2>0\\). Cho mặt phẳng "
            f"\\({plane_tex}.\\)\n"
            "Trên hai mặt cầu \\((S_1), (S_2)\\) lần lượt lấy hai điểm \\(M, N\\). "
            "Trên mặt phẳng \\((P)\\) lấy điểm \\(A\\). "
            f"Chọn {point_desc} sao cho \\(T = MA + NA\\) đạt giá trị nhỏ nhất. "
            f"Khi đó biểu thức {question_expr} bằng? (Kết quả làm tròn đến chữ số thập phân thứ 2)"
        )
        return text

    def generate_solution(self) -> str:
        core = self._compute_core()

        # Lấy tên điểm từ parameters
        p = self.parameters
        center1_name = p["center1_name"]
        center2_name = p["center2_name"]

        a, b, c, d = core["a"], core["b"], core["c"], core["d"]
        (x1, y1, z1), r1 = core["C1"], core["r1"]
        (x2, y2, z2), r2 = core["C2"], core["r2"]

        plane_tex = format_plane_equation_latex(a, b, c, d)

        parts: List[str] = []
        # Giới thiệu tâm các mặt cầu theo yêu cầu trình bày
        parts.append(
            f"Gọi \\({center1_name}({x1};{y1};{z1})\\) là tâm của \\((S_1)\\), "
            f"\\({center2_name}({x2};{y2};{z2})\\) là tâm của \\((S_2)\\)."
        )
        parts.append(f"Xét \\(f(x,y,z) = {plane_tex}\\).")
        parts.append(f"\\(f({center1_name}) = {sp.latex(core['fC1'])}\\), \\(f({center2_name}) = {sp.latex(core['fC2'])}\\).")

        # Phân tích hai trường hợp hình học
        if not core["same_side"]:
            parts.append(f"Vì \\(f({center1_name})\\cdot f({center2_name})<0\\) nên đoạn thẳng nối hai tâm cắt mặt phẳng.")
            parts.append("Dùng bất đẳng thức tam giác thẳng hàng: với \\(M \\in S_1\\), \\(N \\in S_2\\), \\(A \\in (P)\\) bất kì ta có \\(MA+NA \\ge MN\\).")
            parts.append(f"Dấu bằng đạt được khi \\({center1_name}, M, A, N, {center2_name}\\) thẳng hàng.")
            parts.append(f"Gọi \\(A = {center1_name}{center2_name}\\cap (P), \\; M = {center1_name}{center2_name}\\cap (S_1), \\; N = {center1_name}{center2_name}\\cap (S_2)\\). Khi đó \\(MA+NA = MN\\).")
            if core["A_star"] is not None:
                Ax_p, Ay_p, Az_p = core["A_star"]
                dx, dy, dz = (x2 - x1), (y2 - y1), (z2 - z1)
                def lin_coord(c0: int, d: int) -> str:
                    if d == 0:
                        return f"{c0}"
                    sign = "+" if d > 0 else "-"
                    coef = abs(d)
                    if c0 == 0:
                        return f"{coef if coef != 1 else ''}t" if sign == "+" else f"-{coef if coef != 1 else ''}t"
                    return f"{c0} {sign} {'' if coef == 1 else coef}t"
                Alin_x = lin_coord(x1, dx)
                Alin_y = lin_coord(y1, dy)
                Alin_z = lin_coord(z1, dz)
                plane_expr_tmpl = format_plane_equation_latex(a, b, c, d)
                expr_at_A = (plane_expr_tmpl.replace("x", f"({Alin_x})").replace("y", f"({Alin_y})").replace("z", f"({Alin_z})"))
                denom_t = sp.Add(sp.Integer(a)*dx, sp.Integer(b)*dy, sp.Integer(c)*dz)
                if denom_t != 0:
                    t_val = -core['fC1'] / denom_t
                    # Add intermediate steps and equivalences
                    parts.append(f"Đặt \\(A = {center1_name} + t\\,\\overrightarrow{{{center1_name}{center2_name}}}\\). Điều kiện \\(A \\in (P)\\) cho:")
                    parts.append(f"\\({expr_at_A} = 0\\)")
                    parts.append(f"\\(\\Leftrightarrow {sp.latex(core['fC1'])} + t \\cdot ({sp.latex(denom_t)}) = 0\\)")
                    neg_fC1 = sp.simplify(-core['fC1'])
                    parts.append(f"\\(\\Leftrightarrow t \\cdot ({sp.latex(denom_t)}) = {sp.latex(neg_fC1)}\\)")
                    parts.append(f"\\(\\Leftrightarrow t = \\dfrac{{{sp.latex(neg_fC1)}}}{{{sp.latex(denom_t)}}} = {sp.latex(t_val)}\\).")
        else:
            parts.append(f"Vì \\(f({center1_name})\\cdot f({center2_name})>0\\) nên phản chiếu \\({center2_name}\\) qua (P) được \\({center2_name}'\\).")
            Ux, Uy, Uz = core["C2_ref"]
            Ux_tex, Uy_tex, Uz_tex = format_coord_solution(Ux), format_coord_solution(Uy), format_coord_solution(Uz)
            parts.append(f"\\({center2_name}' = ({Ux_tex}; {Uy_tex}; {Uz_tex})\\). Khi đó \\(MA+NA = M'A + N'A = M'A + A N' \\ge M'N'\\) với \\(M' \\in S_1\\), \\(N' \\in S_2\\).")
            parts.append(f"Dấu bằng khi \\({center1_name}, M, A, N, {center2_name}'\\) thẳng hàng.")
            parts.append(f"Khi đó \\(A\\) nằm trên đường thẳng \\({center1_name}{center2_name}'\\) và \\(A = {center1_name}{center2_name}'\\cap (P)\\).")
            if core["A_star"] is not None:
                Ax_p, Ay_p, Az_p = core["A_star"]
                dx2, dy2, dz2 = (Ux - x1), (Uy - y1), (Uz - z1)
                def format_linear_coord(c0: int, d: sp.Expr) -> str:
                    if d == 0:
                        return str(c0)
                    d_str = sp.latex(d)
                    if d_str.startswith('-'):
                        return f"{c0} - {d_str[1:]}t"
                    return f"{c0} + {d_str}t"
                A2lin_x = format_linear_coord(x1, dx2)
                A2lin_y = format_linear_coord(y1, dy2)
                A2lin_z = format_linear_coord(z1, dz2)
                plane_expr_tmpl2 = format_plane_equation_latex(a, b, c, d)
                expr_at_A2 = (plane_expr_tmpl2.replace("x", f"({A2lin_x})").replace("y", f"({A2lin_y})").replace("z", f"({A2lin_z})"))
                denom_t2 = sp.Add(a*dx2, b*dy2, c*dz2)
                if denom_t2 != 0:
                    t2_val = -core['fC1'] / denom_t2
                    # Add intermediate steps and equivalences for the second case
                    parts.append(f"Đặt \\(A = {center1_name} + t\\,\\overrightarrow{{{center1_name}{center2_name}'}}\\). Điều kiện \\(A \\in (P)\\) cho:")
                    parts.append(f"\\({expr_at_A2} = 0\\)")
                    parts.append(f"\\(\\Leftrightarrow {sp.latex(core['fC1'])} + t \\cdot ({sp.latex(denom_t2)}) = 0\\)")
                    neg_fC1_2 = sp.simplify(-core['fC1'])
                    parts.append(f"\\(\\Leftrightarrow t \\cdot ({sp.latex(denom_t2)}) = {sp.latex(neg_fC1_2)}\\)")
                    parts.append(f"\\(\\Leftrightarrow t = \\dfrac{{{sp.latex(neg_fC1_2)}}}{{{sp.latex(denom_t2)}}} = {sp.latex(t2_val)}\\).")

        T_min_expr = core["T_min_expr"]
        target_point = self.parameters.get("target_point", "A")
        Ax, Ay, Az = core["A_opt"]

        if target_point == "A":
            sumA = sp.Add(Ax, Ay, Az)
            parts.append(f"Suy ra \\(T_{{\\min}} = {sp.latex(T_min_expr)}\\) đạt tại \\(A = ({sp.latex(Ax)}; {sp.latex(Ay)}; {sp.latex(Az)})\\).")
            exactA = sp.simplify(sp.Add(sumA, T_min_expr))
            approxA = float(sp.N(exactA, 8))
            parts.append(f"Vậy \\(a+b+c+T = {sp.latex(exactA)} \\approx {approxA:.2f}\\).")
        elif target_point == "M":
            Mx, My, Mz = core["M_opt"]
            sumM = sp.Add(Mx, My, Mz)
            parts.append(f"Suy ra \\(T_{{\\min}} = {sp.latex(T_min_expr)}\\) đạt tại \\(A = ({sp.latex(Ax)}; {sp.latex(Ay)}; {sp.latex(Az)})\\).")
            AC1_len = core.get("AC1")
            n_norm = core.get("n_norm")
            r1_tex = sp.latex(r1)
            if sp.simplify(AC1_len).is_zero is True:
                parts.append("Vì \\(A\\) trùng \\(" + center1_name + "\\), chọn \\(M = " + center1_name + " + \\dfrac{" + r1_tex + "}{\\|\\vec n\\|}\\,\\vec n\\) với \\(\\vec n=(a,b,c)\\), \\(\\|\\vec n\\| = " + sp.latex(n_norm) + ") để \\(|" + center1_name + "M|=" + r1_tex + "\\).")
            else:
                parts.append("Đặt \\(M = " + center1_name + " + k\\,\\overrightarrow{" + center1_name + "A}\\). \\(M \\in (S_1) \\Leftrightarrow |" + center1_name + "M| = " + r1_tex + "\\)")
                parts.append("\\(\\Leftrightarrow |k|\\,|A" + center1_name + "| = " + r1_tex + " \\Leftrightarrow k = \\dfrac{" + r1_tex + "}{|A" + center1_name + "|}\\) (chọn \\(|k|>0\\) cùng hướng \\((\\overrightarrow{" + center1_name + "A})\\)).")
                dx1 = sp.latex(sp.simplify(Ax - x1))
                dy1 = sp.latex(sp.simplify(Ay - y1))
                dz1 = sp.latex(sp.simplify(Az - z1))
                len1 = latex_sqrt_sum_of_squares(sp.simplify(Ax - x1), sp.simplify(Ay - y1), sp.simplify(Az - z1))
                parts.append("\\(\\overrightarrow{" + center1_name + "A} = (" + dx1 + "; " + dy1 + "; " + dz1 + ")\\).")
                parts.append("\\(|A" + center1_name + "| = " + len1 + "\\).")
                parts.append("Suy ra \\(M = (" + str(x1) + " + k(" + sp.latex(Ax) + " - " + str(x1) + "); " + str(y1) + " + k(" + sp.latex(Ay) + " - " + str(y1) + "); " + str(z1) + " + k(" + sp.latex(Az) + " - " + str(z1) + ") )\\).")
                parts.append("Suy ra \\(M = " + center1_name + " + \\dfrac{" + r1_tex + "}{|A" + center1_name + "|}\\,\\overrightarrow{" + center1_name + "A}\\) \\(= (" + sp.latex(Mx) + "; " + sp.latex(My) + "; " + sp.latex(Mz) + ")\\).")
            parts.append(f"Suy ra điểm \\(M = ({sp.latex(Mx)}; {sp.latex(My)}; {sp.latex(Mz)})\\) trên \\((S_1)\\).")
            exactM = sp.simplify(sp.Add(sumM, T_min_expr))
            approxM = float(sp.N(exactM, 8))
            parts.append(f"Vậy \\(m+n+p+T = {sp.latex(exactM)} \\approx {approxM:.2f}\\).")
        else:  # target_point == 'N'
            Nx, Ny, Nz = core["N_opt"]
            sumN = sp.Add(Nx, Ny, Nz)
            parts.append(f"Suy ra \\(T_{{\\min}} = {sp.latex(T_min_expr)}\\) đạt tại \\(A = ({sp.latex(Ax)}; {sp.latex(Ay)}; {sp.latex(Az)})\\).")
            AC2_len = core.get("AC2")
            n_norm = core.get("n_norm")
            r2_tex = sp.latex(r2)
            if sp.simplify(AC2_len).is_zero is True:
                parts.append("Vì \\(A\\) trùng \\(" + center2_name + "\\), chọn \\(N = " + center2_name + " + \\dfrac{" + r2_tex + "}{\\|\\vec n\\|}\\,\\vec n\\) với \\(\\vec n=(a,b,c)\\), \\(\\|\\vec n\\| = " + sp.latex(n_norm) + ") để \\(|" + center2_name + "N|=" + r2_tex + "\\).")
            else:
                parts.append("Đặt \\(N = " + center2_name + " + k\\,\\overrightarrow{" + center2_name + "A}\\). \\(N \\in (S_2) \\Leftrightarrow |" + center2_name + "N| = " + r2_tex + "\\)")
                parts.append("\\(\\Leftrightarrow |k|\\,|A" + center2_name + "| = " + r2_tex + " \\Leftrightarrow k = \\dfrac{" + r2_tex + "}{|A" + center2_name + "|}\\) (chọn \\(|k|>0\\) cùng hướng \\((\\overrightarrow{" + center2_name + "A})\\)).")
                dx2 = sp.latex(sp.simplify(Ax - x2))
                dy2 = sp.latex(sp.simplify(Ay - y2))
                dz2 = sp.latex(sp.simplify(Az - z2))
                len2 = latex_sqrt_sum_of_squares(sp.simplify(Ax - x2), sp.simplify(Ay - y2), sp.simplify(Az - z2))
                parts.append("\\(\\overrightarrow{" + center2_name + "A} = (" + dx2 + "; " + dy2 + "; " + dz2 + ")\\).")
                parts.append("\\(|A" + center2_name + "| = " + len2 + "\\).")
                parts.append("Suy ra \\(N = (" + str(x2) + " + k(" + sp.latex(Ax) + " - " + str(x2) + "); " + str(y2) + " + k(" + sp.latex(Ay) + " - " + str(y2) + "); " + str(z2) + " + k(" + sp.latex(Az) + " - " + str(z2) + ") )\\).")
                parts.append("Suy ra \\(N = " + center2_name + " + \\dfrac{" + r2_tex + "}{|A" + center2_name + "|}\\,\\overrightarrow{" + center2_name + "A}\\) \\(= (" + sp.latex(Nx) + "; " + sp.latex(Ny) + "; " + sp.latex(Nz) + ")\\).")
            parts.append(f"Suy ra điểm \\(N = ({sp.latex(Nx)}; {sp.latex(Ny)}; {sp.latex(Nz)})\\) trên \\((S_2)\\).")
            exactN = sp.simplify(sp.Add(sumN, T_min_expr))
            approxN = float(sp.N(exactN, 8))
            parts.append(f"Vậy \\(u+v+w+T = {sp.latex(exactN)} \\approx {approxN:.2f}\\).")

        return "\n\n".join(parts)
# Cập nhật hàm trả về dạng toán để bao gồm lớp mới
def get_available_question_types():  # type: ignore[override]
    return [
        MinSumTwoSpheresToPlaneQuestion,
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

    return BaseOptimizationQuestion.create_latex_document(questions, "Tổng hợp Câu hỏi Tối ưu hóa từ bai2.tex")


def main():
    """
    Hàm main để chạy generator với hỗ trợ 2 format
    Cách sử dụng:
    python main_runner.py [số_câu] [format]
    """
    try:
        # Lấy tham số từ command line
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        fmt = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] in ['1', '2'] else 1
        # seed tùy chọn: arg3 hoặc biến môi trường OPT_SEED
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

        # Tạo câu hỏi
        question_types = get_available_question_types()
        questions_data = []

        for i in range(1, num_questions + 1):
            try:
                question_type = random.choice(question_types)
                # Seed một lần tổng; để đa dạng theo câu, có thể thay đổi seed dựa trên i nếu cần
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

        # Tạo file LaTeX
        if fmt == 1:
            latex_content = BaseOptimizationQuestion.create_latex_document(questions_data, "Câu hỏi Tối ưu hóa")
        else:
            latex_content = BaseOptimizationQuestion.create_latex_document_with_format(questions_data,
                                                                                       "Câu hỏi Tối ưu hóa", fmt)

        filename = "optimization_questions.tex"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)

        print(f"✅ Đã tạo thành công {filename} với {len(questions_data)} câu hỏi")
        print(f"📄 Biên dịch bằng: xelatex {filename}")
        print(f"📋 Format: {fmt} ({'đáp án ngay sau câu hỏi' if fmt == 1 else 'đáp án ở cuối'})")

    except ValueError:
        print("❌ Lỗi: Vui lòng nhập số câu hỏi hợp lệ")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
