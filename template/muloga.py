"""
Dạng toán tối ưu hóa chuyển động
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
Các hàm tiện ích LaTeX cho hệ thống sinh câu hỏi toán tối ưu hóa
"""


@dataclass
class GeneratorConfig:
    seed: Optional[int] = None
    exact_mode: bool = True
    coord_min: int = -2
    coord_max: int = 5
    vector_max_component: int = 3
    time_choices: Tuple[int, ...] = (3, 4, 5, 6, 7, 8)
    # Cấu hình cho dạng exp-quadratic extremum
    expq_k_choices: Tuple[int, ...] = (1, 2)
    # Nếu None: tự chọn theo k để đảm bảo đơn điệu; nếu chỉ định: dùng tập này
    expq_m_choices: Optional[Tuple[int, ...]] = None
    # Nếu chỉ định: chọn ngẫu nhiên trong danh sách các đoạn (L,R)
    expq_interval_choices: Optional[Tuple[Tuple[int, int], ...]] = None
    # Nếu không chỉ định interval_choices: sinh ngẫu nhiên L,R trong khoảng âm dưới đây
    expq_interval_range: Tuple[int, int] = (-10, -1)
    # Ép tìm cực trị: 'min' hoặc 'max'; None thì random hoặc theo ENV
    expq_force_extreme: Optional[str] = None


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
            # Format 2: câu hỏi + lời giải, đáp án ở cuối
            correct_answers = []
            for question_data in questions_data:
                if isinstance(question_data, tuple):
                    question_content, correct_answer = question_data
                    latex_content += question_content + "\n\n"
                    correct_answers.append(correct_answer)
                else:
                    # Fallback cho format cũ
                    latex_content += f"{question_data}\n\n"

            # Thêm phần đáp án ở cuối
            if correct_answers:
                latex_content += "Đáp án\n\n"
                for idx, answer in enumerate(correct_answers, 1):
                    # Loại bỏ ký hiệu LaTeX để hiển thị đáp án sạch
                    ans = answer
                    if ans.startswith("\\(") and ans.endswith("\\)"):
                        ans = ans[2:-2].strip()
                    if ans.startswith("$") and ans.endswith("$"):
                        ans = ans[1:-1].strip()

                    # Nếu là số thập phân (có dấu phẩy), in thêm dạng dấu chấm
                    if ',' in ans:
                        ans_dot = ans.replace(',', '.')
                        latex_content += f"Câu {idx}: {ans}|{ans_dot}\n\n"
                    else:
                        latex_content += f"Câu {idx}: {ans}\n\n"

        latex_content += "\\end{document}"
        return latex_content



class ExpQuadraticMaxOnIntervalQuestion(BaseOptimizationQuestion):
    """
    Dạng bài: Cực trị hàm mũ-nhị thức trên đoạn, theo mẫu: y = e^{2x}(x^2 - x + m)
    - Ngẫu nhiên hỏi giá trị lớn nhất hoặc nhỏ nhất trên đoạn [L; R]
    - Đặt M = a / e^b với a, b ∈ N rồi yêu cầu tính P = 2a + 3b

    Ghi chú thiết kế:
    - Chọn k = 2 và m ≥ 1 để y' = e^{2x}(2x^2 + (2m - 1)) > 0 ∀x ⇒ hàm tăng trên R
      ⇒ trên đoạn [L; R] (với L, R < 0) ta có: min tại L, max tại R. Cả hai mút đều âm
      nên b = -2x* ∈ N (không âm) và biểu diễn M = a / e^b là hợp lệ.
    """

    SCENARIOS = [
        {
            "context": "quảng cáo truyền hình trong giờ vàng",
            "object": "mức độ quan tâm của khán giả",
        },
        {
            "context": "một tập podcast trên sóng phát thanh",
            "object": "mức độ yêu thích của khán giả",
        },
        {
            "context": "một trailer phim tài liệu trước giờ vàng",
            "object": "mức độ quan tâm của khán giả",
        },
        {
            "context": "một bài đăng trên mạng xã hội",
            "object": "mức độ tương tác",
        },
        {
            "context": "một banner quảng cáo số",
            "object": "chỉ số hiệu quả quảng cáo",
        },
    ]

    def generate_parameters(self) -> Dict[str, Any]:
        # Lấy config nếu có
        cfg: GeneratorConfig = getattr(self, 'config', GeneratorConfig())

        # Chọn k từ cấu hình
        k_choices = tuple(cfg.expq_k_choices) if cfg.expq_k_choices else (1, 2)
        k = random.choice(k_choices)

        # Chọn m từ cấu hình hoặc theo k để đảm bảo đơn điệu tăng
        if cfg.expq_m_choices:
            m = random.choice(tuple(cfg.expq_m_choices))
        else:
            if k == 1:
                # y' = e^{x}(x^2 + x + (m-1)) > 0 nếu \Delta < 0 => m >= 2
                m = random.choice((2, 3, 4, 5, 6))
            else:
                # k = 2 => y' > 0 nếu m >= 1
                m = random.choice((1, 2, 3, 4, 5))

        # Chọn đoạn [L;R] âm từ cấu hình hoặc sinh ngẫu nhiên trong khoảng âm
        if cfg.expq_interval_choices:
            L, R = random.choice(tuple(cfg.expq_interval_choices))
        else:
            lo, hi = cfg.expq_interval_range
            lo = min(lo, -2)
            hi = max(hi, -1)
            while True:
                L = random.randint(lo, -2)
                R = random.randint(L + 1, -1)
                if L < 0 and R < 0 and L < R:
                    break

        # Ép min/max: ưu tiên config, sau đó ENV, cuối cùng random
        extreme_type = None
        if cfg.expq_force_extreme in {"min", "max"}:
            extreme_type = cfg.expq_force_extreme
        else:
            env_extreme = os.environ.get("EXPQ_EXTREME", "").strip().lower()
            if env_extreme in {"min", "max"}:
                extreme_type = env_extreme
        if extreme_type is None:
            extreme_type = random.choice(["max", "min"])  # "max" => tại R; "min" => tại L

        scenario = random.choice(self.SCENARIOS)

        return {
            "k": k,
            "m": m,
            "L": L,
            "R": R,
            "extreme_type": extreme_type,
            "scenario": scenario,
        }

    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        k = params["k"]
        m = params["m"]
        L = params["L"]
        R = params["R"]
        extreme_type = params["extreme_type"]
        scenario = params.get("scenario", {"context": "bối cảnh đã cho", "object": "chỉ số cần phân tích"})

        x_star = R if extreme_type == "max" else L
        # a = x*^2 - x* + m (số nguyên dương)
        a_val = x_star * x_star - x_star + m
        # b = -k x* (vì x* < 0 ⇒ b ∈ N)
        b_val = -k * x_star
        P = 2 * a_val + 3 * b_val
        return f"\\({P}\\)"

    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        k = params["k"]
        m = params["m"]
        L = params["L"]
        R = params["R"]
        extreme_type = params["extreme_type"]

        def compute_P(x_value: int, use_wrong_b: Optional[str] = None, alt_formula: Optional[str] = None) -> int:
            a_local = x_value * x_value - x_value + m
            if use_wrong_b == "sign":
                # Sai: lấy b = k*x (âm)
                b_local = k * x_value
            elif use_wrong_b == "other_endpoint":
                # Sai: b lấy theo đầu mút còn lại
                other_x = L if x_value == R else R
                b_local = -k * other_x
            else:
                b_local = -k * x_value
            if alt_formula == "2a+b":
                return 2 * a_local + b_local
            if alt_formula == "a+3b":
                return a_local + 3 * b_local
            return 2 * a_local + 3 * b_local

        # Đáp án đúng để loại trùng
        x_star = R if extreme_type == "max" else L
        correct_P = compute_P(x_star)

        candidates: List[int] = []
        # 1) Lấy sai đầu mút
        candidates.append(compute_P(L if x_star == R else R))
        # 2) Sai dấu của b
        candidates.append(compute_P(x_star, use_wrong_b="sign"))
        # 3) Sai công thức P
        candidates.append(compute_P(x_star, alt_formula="2a+b"))
        # 4) Thêm một phương án nữa nếu trùng
        candidates.append(compute_P(x_star, alt_formula="a+3b"))

        # Lọc, loại trùng và khác đúng
        uniq: List[int] = []
        seen: set = set([correct_P])
        for v in candidates:
            if v not in seen:
                uniq.append(v)
                seen.add(v)
            if len(uniq) == 3:
                break

        # Bảo đảm có 3 phương án
        j = 1
        while len(uniq) < 3:
            fall = correct_P + (2 * j if j % 2 else -3 * j)
            if fall not in seen:
                uniq.append(fall)
                seen.add(fall)
            j += 1

        return [f"\\({u}\\)" for u in uniq[:3]]

    def generate_question_text(self) -> str:
        params = self.parameters
        k = params["k"]
        m = params["m"]
        L = params["L"]
        R = params["R"]
        extreme_type = params["extreme_type"]
        scenario = params["scenario"]

        phrase = "lớn nhất" if extreme_type == "max" else "nhỏ nhất"
        return (
            f"Một đơn vị đang phân tích {scenario['object']} của {scenario['context']}. "
            f"Chỉ số được mô hình hóa bởi hàm số \\( y = e^{{{k}x}}(x^2 - x + {m}) \\) trên đoạn \\([ {L}; {R}]\\). "
            f"Gọi \\( M = \\dfrac{{a}}{{e^b}} \\) với \\( a,b \\in \\mathbb{{N}} \\) là giá trị {phrase} của hàm số trên đoạn đã cho. "
            f"Khi đó, giá trị của biểu thức \\( P = 2a + 3b \\) bằng bao nhiêu?"
        )

    def generate_solution(self) -> str:
        params = self.parameters
        k = params["k"]
        m = params["m"]
        L = params["L"]
        R = params["R"]
        extreme_type = params["extreme_type"]

        x_star = R if extreme_type == "max" else L
        a_val = x_star * x_star - x_star + m
        b_val = -k * x_star
        P = 2 * a_val + 3 * b_val

        phrase = "lớn nhất" if extreme_type == "max" else "nhỏ nhất"
        at_phrase = f"tại x = {x_star}"

        # Lập đoạn lý luận đơn điệu phụ thuộc k (dùng newline thật, không chèn ký tự \n)
        if k == 2:
            mono_reason = (
                "Với \\(k = 2\\) và \\(m \\ge 1\\), suy ra\n"
                "\\[ y' = e^{2x}\\big(2x^2 + (2m - 1)\\big) > 0,\\; \\forall x. \\]"
                f"\nDo đó, hàm số tăng trên toàn trục số, nên trên đoạn \\([{L}; {R}]\\) giá trị {phrase} đạt được {at_phrase}."
            )
        else:
            mono_reason = (
                "Với \\(k = 1\\) và \\(m \\ge 2\\), ta có \\( y' = e^x(x^2 + x + (m-1)) \\).\n"
                "Tam thức \\(x^2 + x + (m-1)\\) có \\(\\Delta = 1 - 4(m-1) < 0\\) \\(\\Rightarrow\\) luôn dương."
                f"\nSuy ra \\(y' > 0\\) với mọi \\(x\\). Do đó, hàm số tăng trên toàn trục số, nên trên đoạn \\([{L}; {R}]\\) giá trị {phrase} đạt được {at_phrase}."
            )

        # Dòng rút gọn đạo hàm theo k để bám sát văn phong đề mẫu
        if k == 2:
            simp_line = r"Hay \( y' = e^{2x}\big(2x^2 + (2m - 1)\big) \)."
        else:
            simp_line = fr"Hay \( y' = e^x\big(x^2 + x + ({m}-1)\big) \)."

        solution = fr"""
Trong bối cảnh bài toán: một đơn vị đang phân tích {params['scenario']['object']} của {params['scenario']['context']}.

Cho hàm số \( y = e^{{{k}x}}(x^2 - x + {m}) \) trên đoạn \( x \in [{L}; {R}] \), ta cần tìm giá trị {phrase} của hàm số trên đoạn này.

Bước 1. Xét hàm số \( y = e^{{{k}x}}(x^2 - x + {m}) \). Ta đặt:
\( u = e^{{{k}x}},\ \quad v = x^2 - x + {m} \Rightarrow y = u \cdot v \)

Bước 2. Tính đạo hàm:
\( y' = u'v + uv' = {k}e^{{{k}x}}(x^2 - x + {m}) + e^{{{k}x}}(2x - 1) \)

\( \Rightarrow y' = e^{{{k}x}} \left[{k}(x^2 - x + {m}) + (2x - 1)\right] \)

Bước 3. Tính biểu thức trong ngoặc:

\( {k}(x^2 - x + {m}) + (2x - 1) = {k}x^2 - {k}x + {k*m} + 2x - 1 = {k}x^2 + (2 - {k})x + ({k*m} - 1) \)

Do đó:

\( y' = e^{{{k}x}}\big({k}x^2 + (2 - {k})x + ({k*m} - 1)\big) \)

Bước 4. Vì \(e^{{{k}x}} > 0\) với mọi \(x\), ta xét tam thức
\[ q(x) = {k}x^2 + (2 - {k})x + ({k*m} - 1). \]
Ta có \(\Delta_q = (2 - {k})^2 - 4\cdot {k}\cdot ({k*m} - 1) < 0\) và \({k} > 0\) nên \(q(x) > 0\) với mọi \(x\).
Suy ra \(y' > 0\) với mọi \(x\), do đó hàm số tăng trên toàn trục số; trên đoạn \([{L}; {R}]\) giá trị {phrase} đạt tại \(x = {x_star}\).

Bước 5. Tính giá trị tại đầu mút tương ứng:
\[ M = y({x_star}) = e^{{{k}\cdot {x_star}}}\big(({x_star})^2 - ({x_star}) + {m}\big) = e^{{{k}\cdot {x_star}}}\big({a_val}\big) = \frac{{{a_val}}}{{e^{{{-k*x_star}}}}}. \]
Suy ra \( M = \dfrac{{a}}{{e^b}} \) với \( a = {a_val} \), \( b = {-k*x_star} \).

Cuối cùng, \( P = 2a + 3b = 2\cdot {a_val} + 3\cdot {-k*x_star} = {P}. \)
"""
        return solution


class LogisticPeakRateQuestion(BaseOptimizationQuestion):
    """
    Dạng bài: Tốc độ (đạo hàm) của hàm logistic đạt lớn nhất khi nào?
    Mẫu: f(t) = L / (1 + A e^{-k t}), t >= 0. Cực đại của f'(t) tại t* = (ln A)/k.
    """

    SCENARIOS = [
        {"title": "Chiến dịch tiêm chủng", "unit": "tuần", "actor": "một địa phương", "phenomenon": "số người đã tiêm"},
        {"title": "Lan truyền video", "unit": "ngày", "actor": "mạng xã hội", "phenomenon": "số người tiếp cận"},
        {"title": "Tăng trưởng người dùng ứng dụng", "unit": "tuần", "actor": "một ứng dụng", "phenomenon": "số người dùng"},
        {"title": "Mô hình hóa doanh thu", "unit": "tháng", "actor": "một sản phẩm", "phenomenon": "doanh thu tích lũy"},
        {"title": "Phổ biến khóa học trực tuyến", "unit": "ngày", "actor": "một khóa học", "phenomenon": "số người đăng ký"},
    ]

    def generate_parameters(self) -> Dict[str, Any]:
        scenario = random.choice(self.SCENARIOS)
        # Chọn tham số đẹp
        L = random.choice([3000, 5000, 8000])
        A = random.choice([2, 3, 4, 5, 6, 7])
        k = random.choice([1, 2])
        return {
            "L": L,
            "A": A,
            "k": k,
            "scenario": scenario,
        }

    def calculate_answer(self) -> str:
        params = self.parameters or self.generate_parameters()
        A = params["A"]
        k = params["k"]
        t_expr = sp.nsimplify(sp.log(A) / k)
        t_num = float(sp.N(t_expr, 6))
        t_str = f"{t_num:.3f}".replace('.', ',')
        return f"\\({t_str}\\)"

    def generate_wrong_answers(self) -> List[str]:
        params = self.parameters
        L = params["L"]
        A = params["A"]
        k = params["k"]

        correct = self.calculate_answer()
        wrongs = set()

        # Một số phương án sai hợp lý
        cand = [
            (f"\\(\\ln {L}\\)" if k == 1 else f"\\(\\dfrac{{\\ln {L}}}{{{k}}}\\)"),
            ("\\(1\\)" if k == 1 else f"\\(\\dfrac{{1}}{{{k}}}\\)"),
            (f"\\(\\dfrac{{\\ln {A}}}{{{2*k}}}\\)"),
            ("\\(0\\)"),
        ]
        for c in cand:
            if c != correct:
                wrongs.add(c)
            if len(wrongs) == 3:
                break
        # Bổ sung dự phòng
        j = 2
        while len(wrongs) < 3:
            wrongs.add(f"\\(\\dfrac{{\\ln {A}}}{{{k*j}}}\\)")
            j += 1
        return list(wrongs)[:3]

    def generate_question_text(self) -> str:
        p = self.parameters
        L, A, k = p["L"], p["A"], p["k"]
        sc = p["scenario"]
        unit = sc["unit"]
        return (
            f"Giả sử {sc['phenomenon']} của {sc['actor']} tuân theo quy luật logistic "
            f"được mô hình hoá bởi hàm số \\( f(t) = \\dfrac{{{L}}}{{1 + {A}e^{{-{k}t}}}} \\), với \\( t \\ge 0 \\) ({unit}). "
            f"Tốc độ thay đổi là \\( f'(t) \\). Hỏi sau bao lâu thì tốc độ này đạt lớn nhất?"
        )

    def generate_solution(self) -> str:
        p = self.parameters
        L, A, k = p["L"], p["A"], p["k"]
        sc = p["scenario"]
        unit = sc["unit"]

        # Giá trị chính xác và xấp xỉ
        t_expr = sp.nsimplify(sp.log(A) / k)
        # Hiển thị dùng ln thay vì log để nhất quán ký hiệu
        t_ltx = f"\\dfrac{{\\ln {A}}}{{{k}}}"
        t_num = float(sp.N(t_expr, 6))
        t_num_str = f"{t_num:.3f}".replace('.', ',')

        solution = fr"""
Cho hàm số \( f(t) = \dfrac{{{L}}}{{1 + {A}e^{{-{k}t}}}} \), với \( t \ge 0 \).

Ta có: \( f'(t) = \dfrac{{{L}\cdot {A}\cdot {k} e^{{-{k}t}}}}{{(1 + {A}e^{{-{k}t}})^2}} \)


\( \Rightarrow f''(t) = \dfrac{{-{L}\cdot {A}\cdot {k}^2 e^{{-{k}t}}(1 + {A}e^{{-{k}t}})^2 + 2{L}\cdot {A}^2{k}^2 e^{{-2{k}t}}(1 + {A}e^{{-{k}t}})}}{{(1 + {A}e^{{-{k}t}})^4}} \)

\( \Leftrightarrow f''(t) = \dfrac{{{L}\cdot {A}\cdot {k}^2 e^{{-{k}t}}(1 + {A}e^{{-{k}t}})\big({A}e^{{-{k}t}} - 1\big)}}{{(1 + {A}e^{{-{k}t}})^4}} \)

Giải phương trình \( f''(t) = 0 \), ta được:  \\
\( {L}\cdot {A}\cdot {k}^2 e^{{-{k}t}}(1 + {A}e^{{-{k}t}})\big({A}e^{{-{k}t}} - 1\big) = 0 \)

Vì \( e^{{-{k}t}} > 0 \) và \( 1 + {A}e^{{-{k}t}} > 0 \), nên:  \\
\( f''(t) = 0 \Leftrightarrow {A}e^{{-{k}t}} - 1 = 0 \Rightarrow e^{{-{k}t}} = \dfrac{1}{{{A}}} \Rightarrow t = \dfrac{{\ln {A}}}{{{k}}} \)

Kết luận: Tốc độ đạt lớn nhất sau \( {t_ltx} \approx {t_num_str} \) {unit}.
"""
        return solution

# Cập nhật hàm trả về dạng toán để bao gồm lớp mới
def get_available_question_types():  # type: ignore[override]
    return [
        ExpQuadraticMaxOnIntervalQuestion,
        LogisticPeakRateQuestion,
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
        print("❌ Lỗi: Vui lòng nhập số câu hỏi hợp lệ hợp lệ")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
