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
def format_linear_latex(a: int, b: int) -> str:
    """Chuẩn hóa ax + b theo yêu cầu:
    - Chỉ đảo vị trí nếu a < 0 và b > 0: viết "b - |a|x" (vd: -2x + 2 → 2 - 2x)
    - Các trường hợp khác giữ thứ tự "ax ± |b|" như thông thường
    - |a| = 1 hiển thị "x" thay vì "1x"; xử lý a = 0, b = 0
    """
    # a = 0
    if a == 0:
        return str(b)
    # b = 0
    if b == 0:
        if a == 1:
            return "x"
        if a == -1:
            return "-x"
        return f"{a}x"

    # a < 0 và b > 0: đảo vị trí theo yêu cầu
    if a < 0 and b > 0:
        x_abs_part = "x" if abs(a) == 1 else f"{abs(a)}x"
        return f"{b} - {x_abs_part}"

    # Mặc định: giữ "ax ± |b|"
    if a == 1:
        a_part = "x"
    elif a == -1:
        a_part = "-x"
    else:
        a_part = f"{a}x"
    op = "+" if b > 0 else "-"
    return f"{a_part} {op} {abs(b)}"



def format_function_notation(func_name, var, expression):
    """Format function notation like f(x) = expression"""
    return f"{func_name}({var}) = {expression}"


def simplify_for_latex(expr: sp.Expr) -> sp.Expr:
    """Simplify but keep sums as sums to avoid huge single-fraction outputs."""
    try:
        if isinstance(expr, sp.Add):
            simplified_terms = [sp.simplify(sp.radsimp(arg)) for arg in expr.args]
            # keep as unevaluated sum
            return sp.Add(*simplified_terms, evaluate=False)
        return sp.simplify(sp.radsimp(expr))
    except Exception:
        return sp.simplify(expr)


def _latex_post(s: str) -> str:
    # Replace log with ln for readability
    return s.replace('\\log', '\\ln')


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
        question_content += f"{solution}\n\n"
        return question_content

    def generate_question_only(self, question_number: int = 1) -> tuple:
        """Tạo câu hỏi chỉ có đề bài và lời giải"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        question_text = self.generate_question_text()
        solution = self.generate_solution()
        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += f"{solution}\n\n"
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
                    # Chuẩn hóa: bỏ wrapper để xử lý và thêm lại inline math
                    ans = answer
                    if ans.startswith("\\(") and ans.endswith("\\)"):
                        ans = ans[2:-2].strip()
                    if ans.startswith("$") and ans.endswith("$"):
                        ans = ans[1:-1].strip()

                    # Nếu là số thập phân (có dấu phẩy), in thêm dạng dấu chấm, cả hai gói trong math
                    if ',' in ans:
                        ans_dot = ans.replace(',', '.')
                        latex_content += f"Câu {idx}: \\({ans}\\)|\\({ans_dot}\\)\n\n"
                    else:
                        latex_content += f"Câu {idx}: \\({ans}\\)\n\n"

        latex_content += "\\end{document}"
        return latex_content


class IndefiniteIntegralQuestion:
    """
    Sinh câu hỏi trắc nghiệm tính nguyên hàm nhiều hạng tử cơ bản.

    - Tạo biểu thức tích phân là tổng 2–4 hạng tử từ các công thức cơ bản:
      k.x^n, k/x, k.(Ax+B)^n, k/(Ax+B), 1/(Ax+B)^n,
      sin/cos/tan/cot(Ax+B), 1/cos^2 x, 1/sin^2 x,
      e^x, a^x, 1/e^{Ax+B}, 1/a^{Ax+B}, a^{Ax+B} b^{Cx+D} / c^{Ex+F}.
    - Tính nguyên hàm đúng bằng SymPy và sinh 3 đáp án sai phổ biến bằng cách
      bỏ hệ số 1/A, sai dấu, quên chia ln(a)/ln(k), v.v.

    Hàm generate_question() trả về dict:
    {
        "question": "Chuỗi biểu thức tích phân",
        "options": ["A", "B", "C", "D"],
        "answer": "B",
        "solution": "Giải thích ngắn gọn công thức áp dụng"
    }
    """

    def __init__(self, config: Optional["GeneratorConfig"] = None, seed: Optional[int] = None,
                 forced_terms: Optional[List[Dict[str, Any]]] = None):
        """Initializer.
        Improvements applied:
        - Optional reproducible randomness via seed (Issue #1)
        - Store config (future usage) and forced_terms with validation (Issue #1 & #4)
        - Validation prevents illegal cases (n = -1 in power forms, A = 0 in linear forms)
        """
        self.config = config or GeneratorConfig()
        if seed is not None:
            # Re-seed global RNG (simplest integration without refactor of all random calls)
            random.seed(seed)
        self.forced_terms = forced_terms
        if self.forced_terms:
            self._validate_forced_terms(self.forced_terms)

    LETTERS = ['A', 'B', 'C', 'D']
    SAMPLE_POINTS = (-2, -1, 0, 1, 2, 3)

    def _rand_int(self, lo: int, hi: int, exclude: Optional[set] = None) -> int:
        """Random int in [lo, hi] excluding values; raises clear error if impossible (Issue #2)."""
        exclude = exclude or set()
        candidates = [v for v in range(lo, hi + 1) if v not in exclude]
        if not candidates:
            raise ValueError(f"No integers available in range [{lo},{hi}] after excluding {exclude}")
        return random.choice(candidates)

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    def _validate_forced_terms(self, terms: List[Dict[str, Any]]):
        """Validate externally supplied terms to avoid runtime math errors.
        Checks:
        - kx_pow_n: n != -1
        - k_lin_pow_n: n != -1 and A != 0
        - k_over_lin / one_over_lin_pow_n: A != 0
        - trig *_lin & inv_*_lin: A != 0
        - mixed_exp_ratio: resulting base k != 1 (fix or raise)
        """
        x = sp.Symbol('x', real=True)
        adjusted = []
        for t in terms:
            ttype = t.get("type")
            if ttype == "kx_pow_n" and t.get("n") == -1:
                raise ValueError("forced_terms: n = -1 invalid for kx_pow_n (would produce ln)")
            if ttype == "k_lin_pow_n" and t.get("n") == -1:
                raise ValueError("forced_terms: n = -1 invalid for k_lin_pow_n")
            if ttype in {"k_lin_pow_n", "k_over_lin", "one_over_lin_pow_n", "sin_lin", "cos_lin", "tan_lin", "cot_lin", "inv_e_lin", "inv_a_lin"}:
                if t.get("A") == 0:
                    raise ValueError(f"forced_terms: A=0 invalid for {ttype}")
            if ttype == "mixed_exp_ratio":
                a, b, c = t["a"], t["b"], t["c"]
                A, B, C, D, E, F_ = t["A"], t["B"], t["C"], t["D"], t["E"], t["F"]
                k = (a ** A) * (b ** C) * (c ** (-E))
                if k == 1:
                    # Try to mutate E slightly to avoid ln(1) (Issue #3/#4)
                    if E < 5:
                        t["E"] = E + 1
                    else:
                        raise ValueError("forced_terms: mixed_exp_ratio produced k=1; adjust parameters")
            adjusted.append(t)
        # replace (mutation in-place, but keep pattern)
        self.forced_terms = adjusted

    def _choose_base_gt1(self) -> int:
        return random.choice([2, 3, 4, 5])

    def _rand_linear_params(self) -> Tuple[sp.Expr, sp.Expr]:
        # Cho phép hệ số A hữu tỉ và pha B có thể là bội của pi
        A_candidates = [
            -3, -2, -1, 1, 2, 3,
            sp.Rational(1, 2), sp.Rational(-1, 2),
            sp.Rational(1, 3), sp.Rational(-1, 3),
        ]
        A = random.choice(A_candidates)

        # B có thể là số nguyên nhỏ hoặc pha pi đặc biệt (±pi/6, ±pi/4, ±pi/3, ±pi/2)
        if random.random() < 0.5:
            B = self._rand_int(-5, 5)
        else:
            q_choices = [2, 3, 4, 6]
            q = random.choice(q_choices)
            p = random.choice([-1, 1])
            B = sp.Rational(p, q) * sp.pi
        # Bảo đảm trả về SymPy Expr cho cả A và B
        return sp.sympify(A), sp.sympify(B)

    def _are_expressions_equal(self, expr1: sp.Expr, expr2: sp.Expr, x: sp.Symbol) -> bool:
        """Kiểm tra 2 biểu thức có bằng nhau (hoặc chỉ khác hằng số C).
        
        Returns True nếu expr1 ≡ expr2 hoặc expr1 = expr2 + const.
        Tối ưu hóa tối đa - chỉ dùng numeric evaluation (không simplify).
        """
        try:
            expr1_s = sp.sympify(expr1)
            expr2_s = sp.sympify(expr2)
            
            # Kiểm tra numeric nhanh: đạo hàm tại 3 điểm
            # Nếu đạo hàm bằng nhau tại 3 điểm -> coi như trùng (đủ tin cậy)
            sample_points = [1, 2, 3]
            deriv_matches = 0
            
            for v in sample_points:
                try:
                    dv1 = complex(sp.diff(expr1_s, x).subs(x, v).evalf())  # type: ignore
                    dv2 = complex(sp.diff(expr2_s, x).subs(x, v).evalf())  # type: ignore
                    if abs(dv1 - dv2) < 1e-8:
                        deriv_matches += 1
                except Exception:
                    # Nếu không tính được, bỏ qua điểm này
                    pass
            
            # Nếu đạo hàm khớp ở cả 3 điểm -> chỉ khác hằng số -> trùng
            return deriv_matches == 3
            
        except Exception:
            # Nếu không so sánh được, coi như không trùng (safe fallback)
            return False

    def _build_term(self) -> Dict[str, Any]:
        """Sinh 1 hạng tử theo danh mục công thức cho trước."""
        term_types = [
            "kx_pow_n",
            "k_over_x",
            "k_lin_pow_n",
            "k_over_lin",
            "one_over_lin_pow_n",
            "sin_lin",
            "cos_lin",
            "tan_lin",
            "cot_lin",
            "sec2",
            "csc2",
            "e_pow_x",
            "a_pow_x",
            "inv_e_lin",
            "inv_a_lin",
            "mixed_exp_ratio",
            "poly_over_x",
        ]
        t = random.choice(term_types)
        if t == "kx_pow_n":
            if random.random() < 0.5:
                k = self._rand_int(-5, 5, {0})
            else:
                num = self._rand_int(-5, 5, {0})
                den = self._rand_int(2, 5)
                k = sp.Rational(num, den)
            n_choices = [-3, -2, 0, 1, 2, 3, 4]
            n = random.choice(n_choices)
            return {"type": t, "k": k, "n": n}
        if t == "k_over_x":
            k = self._rand_int(-5, 5, {0})
            return {"type": t, "k": k}
        if t == "k_lin_pow_n":
            k = self._rand_int(-4, 4, {0})
            A = random.choice([-3, -2, -1, 1, 2, 3])
            B = self._rand_int(-5, 5)
            n = random.choice([-3, -2, 0, 2, 3, 4])
            return {"type": t, "k": k, "A": A, "B": B, "n": n}
        if t == "k_over_lin":
            k = self._rand_int(-4, 4, {0})
            A = random.choice([-3, -2, -1, 1, 2, 3])
            B = self._rand_int(-5, 5)
            return {"type": t, "k": k, "A": A, "B": B}
        if t == "one_over_lin_pow_n":
            k = self._rand_int(-5, 5, {0})
            A, B = self._rand_linear_params()
            n = random.choice([2, 3, 4])
            return {"type": t, "k": k, "A": A, "B": B, "n": n}
        if t in {"sin_lin", "cos_lin", "tan_lin", "cot_lin"}:
            k = self._rand_int(-5, 5, {0})
            A, B = self._rand_linear_params()
            return {"type": t, "k": k, "A": A, "B": B}
        if t in {"sec2", "csc2"}:
            k = self._rand_int(-5, 5, {0})
            return {"type": t, "k": k}
        if t == "e_pow_x":
            return {"type": t}
        if t == "a_pow_x":
            a = self._choose_base_gt1()
            return {"type": t, "a": a}
        if t == "inv_e_lin":
            A, B = self._rand_linear_params()
            return {"type": t, "A": A, "B": B}
        if t == "inv_a_lin":
            a = self._choose_base_gt1()
            A, B = self._rand_linear_params()
            return {"type": t, "a": a, "A": A, "B": B}
        if t == "poly_over_x":
            a = self._rand_int(-4, 4, {0})
            b = self._rand_int(-6, 6)
            c = self._rand_int(-6, 6, {0})
            return {"type": t, "a": a, "b": b, "c": c}
        # mixed_exp_ratio
        a = self._choose_base_gt1()
        b = self._choose_base_gt1()
        c = self._choose_base_gt1()
        A = random.choice([1, 2, 3])
        C = random.choice([1, 2, 3])
        E = random.choice([1, 2, 3])
        B = self._rand_int(-3, 3)
        D = self._rand_int(-3, 3)
        F = self._rand_int(-3, 3)
        attempts_guard = 0
        while (a ** A) * (b ** C) == (c ** E) and attempts_guard < 6:
            attempts_guard += 1
            E = E + 1
            if E > 5:
                prev_c = c
                c_choices = [2, 3, 4, 5]
                c_choices.remove(prev_c)
                c = random.choice(c_choices)
                E = random.choice([1, 2, 3])
        if (a ** A) * (b ** C) == (c ** E):
            A = A + 1 if A < 4 else A + 2
        return {"type": "mixed_exp_ratio", "a": a, "b": b, "c": c, "A": A, "B": B, "C": C, "D": D, "E": E, "F": F}

    def _term_expr_and_antiderivatives(self, term: Dict[str, Any]) -> Tuple[sp.Expr, sp.Expr, List[sp.Expr]]:
        x = sp.Symbol('x', real=True)
        t = term["type"]
        wrongs: List[sp.Expr] = []
        if t == "kx_pow_n":
            k, n = term["k"], term["n"]
            expr = k * x ** n
            F = k * x ** (n + 1) / (n + 1)
            wrongs = [k * x ** (n + 1), x ** (n + 1) / (n + 1)]
            return expr, sp.simplify(F), wrongs
        if t == "k_over_x":
            k = term["k"]
            expr = k / x
            F = k * sp.log(sp.Abs(x))
            wrongs = [sp.log(sp.Abs(x))]  # type: ignore
            return sp.sympify(expr), sp.simplify(F), wrongs
        if t == "k_lin_pow_n":
            k, A, B, n = term["k"], term["A"], term["B"], term["n"]
            lin = A * x + B
            expr = k * lin ** n
            if n == 1:
                F = k * (A * x**2 / 2 + B * x)
                wrongs = [
                    k * (A * x**2 + B * x),
                    k * lin ** 2 / (2 * A),
                ]
                return expr, sp.simplify(F), wrongs
            F = k * lin ** (n + 1) / (A * (n + 1))
            wrongs = [
                k * lin ** (n + 1) / (n + 1),
                k * lin ** (n + 1),
            ]
            return expr, sp.simplify(F), wrongs
        if t == "k_over_lin":
            k, A, B = term["k"], term["A"], term["B"]
            lin = A * x + B
            expr = k / lin
            F = k * sp.log(sp.Abs(lin)) / A
            wrongs = [k * sp.log(sp.Abs(lin))]
            return expr, sp.simplify(F), wrongs
        if t == "one_over_lin_pow_n":
            k, A, B, n = term.get("k", 1), term["A"], term["B"], term["n"]
            lin = A * x + B
            expr = k * (lin ** (-n))
            F = k * (lin ** (1 - n)) / ((1 - n) * A)
            wrongs = [
                k * (lin ** (1 - n)) / (1 - n),
                k * (lin ** (1 - n)) / ((n - 1) * A),
            ]
            return expr, sp.simplify(F), wrongs
        if t in {"sin_lin", "cos_lin", "tan_lin", "cot_lin"}:
            k, A, B = term.get("k", 1), term["A"], term["B"]
            lin = A * x + B
            trig_map = {
                "sin_lin": (k * sp.sin(lin), -k * sp.cos(lin) / A, [k * sp.cos(lin) / A, -k * sp.cos(lin)]),
                "cos_lin": (k * sp.cos(lin), k * sp.sin(lin) / A, [-k * sp.sin(lin) / A, k * sp.sin(lin)]),
                "tan_lin": (k * sp.tan(lin), -k * sp.log(sp.Abs(sp.cos(lin))) / A, [k * sp.log(sp.Abs(sp.cos(lin))) / A, -k * sp.log(sp.Abs(sp.cos(lin)))],),
                "cot_lin": (k * sp.cot(lin), k * sp.log(sp.Abs(sp.sin(lin))) / A, [-k * sp.log(sp.Abs(sp.sin(lin))) / A, k * sp.log(sp.Abs(sp.sin(lin)))],),
            }
            expr, F, wrongs = trig_map[t]
            return expr, sp.simplify(F), list(wrongs)
        if t == "sec2":
            k = term.get("k", 1)
            expr = k * sp.Pow(sp.cos(x), -2)
            F = k * sp.tan(x)
            wrongs = [-k * sp.tan(x)]
            return expr, sp.simplify(F), wrongs
        if t == "csc2":
            k = term.get("k", 1)
            expr = k * sp.Pow(sp.sin(x), -2)
            F = -k * sp.cot(x)
            wrongs = [k * sp.cot(x)]
            return expr, sp.simplify(F), wrongs
        if t == "e_pow_x":
            expr = sp.exp(x)
            F = sp.exp(x)
            wrongs = [sp.exp(x + sp.Integer(1)), sp.Integer(2) * sp.exp(x)]
            return sp.sympify(expr), sp.simplify(F), wrongs
        if t == "a_pow_x":
            a = term["a"]
            expr = a ** x
            F = (a ** x) / sp.log(a)
            wrongs = [a ** x]
            return expr, sp.simplify(F), wrongs
        if t == "inv_e_lin":
            A, B = term["A"], term["B"]
            lin = A * x + B
            expr = sp.exp(-lin)
            F = -sp.exp(-lin) / A  # type: ignore[operator]
            wrongs = [sp.exp(-lin) / A, -sp.exp(-lin)]  # type: ignore[list-item]
            return sp.sympify(expr), sp.simplify(F), wrongs
        if t == "inv_a_lin":
            a, A, B = term["a"], term["A"], term["B"]
            lin = A * x + B
            expr = a ** (-lin)
            F = -(a ** (-lin)) / (A * sp.log(a))
            wrongs = [-(a ** (-lin)) / A, -(a ** (-lin)) / sp.log(a)]
            return expr, sp.simplify(F), wrongs
        if t == "poly_over_x":
            a, b, c = term["a"], term["b"], term["c"]
            expr = (a * x**2 + b * x + c) / x
            F = a * x**2 / 2 + b * x + c * sp.log(sp.Abs(x))
            wrongs = [
                a * x**2 + b * x + c * sp.log(sp.Abs(x)),
                a * x**2 / 2 + b * x + sp.log(sp.Abs(x)),
                a * x**2 / 2 + b * x + c * x,
            ]
            return expr, sp.simplify(F), wrongs
        # mixed_exp_ratio
        a, b, c = term["a"], term["b"], term["c"]
        A, B, C, D, E, F_ = term["A"], term["B"], term["C"], term["D"], term["E"], term["F"]
        aS, bS, cS = sp.Integer(a), sp.Integer(b), sp.Integer(c)
        k0 = (aS ** B) * (bS ** D) * (cS ** (-F_))
        k = (aS ** A) * (bS ** C) * (cS ** (-E))
        expr = k0 * (k ** x)
        Fexpr = k0 * (k ** x) / sp.log(k)
        wrongs = [k0 * (k ** x)]
        return expr, sp.simplify(Fexpr), wrongs

    def _expr_to_latex(self, expr: sp.Expr) -> str:
        return _latex_post(sp.latex(simplify_for_latex(expr)))

    def generate_question(self) -> Dict[str, Any]:
        """Tạo 1 câu hỏi nguyên hàm gồm 4 lựa chọn, có đáp án đúng và lời giải ngắn."""
        x = sp.Symbol('x', real=True)
        # Sinh 1–4 hạng tử (hoặc dùng forced_terms nếu được truyền vào)
        if self.forced_terms is not None and len(self.forced_terms) > 0:
            terms = self.forced_terms
        else:
            num_terms = random.choice([1, 2, 3, 4])
            terms = [self._build_term() for _ in range(num_terms)]

        # Lắp biểu thức và nguyên hàm đúng theo từng hạng tử
        expr_parts: List[sp.Expr] = []
        correct_parts: List[sp.Expr] = []
        wrong_parts_list: List[List[sp.Expr]] = []

        for t in terms:
            e, F, wrongs = self._term_expr_and_antiderivatives(t)
            expr_parts.append(e)
            correct_parts.append(F)
            wrong_parts_list.append(wrongs)

        integrand = sp.Add(*expr_parts) if expr_parts else sp.Integer(0)
        correct_F = sp.Add(*correct_parts) if correct_parts else sp.Integer(0)
        integrand = sp.sympify(integrand)
        correct_F = sp.sympify(correct_F)

        # Xây 3 đáp án sai bằng cách áp dụng sai cho 1–2 hạng tử
        def is_correct_candidate(Fcand: sp.Expr) -> bool:
            """Robust correctness test (Issues #5 & #6):
            - Symbolically simplify derivative difference.
            - If simplify(diff)==0 -> correct.
            - Else evaluate on multiple sample points.
            - Reject if derivative OK but function differs from correct by constant? (still valid integral) -> treat as correct so not used as wrong.
            """
            try:
                Fcand_s = sp.sympify(Fcand)
                d_diff = sp.simplify(sp.diff(Fcand_s, x) - integrand)
                if d_diff == 0:
                    return True
                # numeric fallback on wider set
                sample_points = [-3, -2, -1, 0, 1, 2, 3, 4]
                for v in sample_points:
                    try:
                        val = sp.simplify(d_diff.subs(x, v))
                        if val != 0:
                            return False
                    except Exception:
                        return False
                return True
            except Exception:
                return False

        wrong_candidates: List[sp.Expr] = []

        # Candidate 1: sai ở 1 hạng tử
        idxs_with_wrongs = [i for i, ws in enumerate(wrong_parts_list) if ws]
        attempts = 0
        while len(wrong_candidates) < 3 and attempts < 12:
            attempts += 1
            if idxs_with_wrongs:
                pick_count = 1 if len(wrong_candidates) == 0 else min(2, len(idxs_with_wrongs))
                pick = random.sample(idxs_with_wrongs, pick_count)
            else:
                pick = []
            parts = []
            for i, (Ftrue, wrongs) in enumerate(zip(correct_parts, wrong_parts_list)):
                if i in pick and wrongs:
                    parts.append(random.choice(wrongs))
                else:
                    parts.append(Ftrue)
            Fcand = sp.Add(*parts) if parts else sp.Integer(0)
            if not is_correct_candidate(Fcand) and not self._are_expressions_equal(Fcand, correct_F, x):
                # de-duplicate: kiểm tra không trùng với các đáp án sai khác
                if all(not self._are_expressions_equal(Fcand, w, x) for w in wrong_candidates):
                    wrong_candidates.append(Fcand)

        # Fallback nếu thiếu, thêm biến đổi đơn giản nhưng sai
        # Fallback strategy (Issues #6 & #7): generate structured wrong answers
        # 1. Add + x (shifts derivative by 1)
        # 2. Scale one random term's antiderivative incorrectly (remove a denominator factor)
        # 3. Multiply entire correct by 2 then subtract a linear term so derivative not simple 2*integrand
        attempts_extra = 0
        while len(wrong_candidates) < 3 and attempts_extra < 5:
            attempts_extra += 1
            if len(wrong_candidates) == 0:
                cand = correct_F + x
            elif len(wrong_candidates) == 1:
                # remove a factor from one power/linear term if possible
                # simple heuristic: divide by 2 (unless already rational causing same derivative)
                cand = correct_F * sp.Rational(1, 2) + x  # derivative = 0.5 integrand + 1
            else:
                cand = 2 * correct_F - x  # derivative = 2 integrand - 1
            if not is_correct_candidate(cand) and not self._are_expressions_equal(cand, correct_F, x):
                if all(not self._are_expressions_equal(cand, w, x) for w in wrong_candidates):
                    wrong_candidates.append(sp.sympify(cand))
        # Final safety: if still shortage, append artificial polynomial shift
        while len(wrong_candidates) < 3:
            idx_factor = sp.Integer(len(wrong_candidates) + 1)
            cand = correct_F + x**2 + idx_factor * x
            if not is_correct_candidate(cand) and not self._are_expressions_equal(cand, correct_F, x):
                if all(not self._are_expressions_equal(cand, w, x) for w in wrong_candidates):
                    wrong_candidates.append(sp.sympify(cand))

        # Validation cuối: Kiểm tra nhanh tất cả đáp án không trùng lặp
        # Đơn giản hóa để tránh treo - chỉ log warning thay vì raise error
        all_options = [correct_F] + wrong_candidates[:3]
        for i in range(len(all_options)):
            for j in range(i + 1, len(all_options)):
                if self._are_expressions_equal(all_options[i], all_options[j], x):
                    # Phát hiện trùng lặp - log chi tiết
                    logging.warning(
                        f"Phát hiện đáp án trùng lặp: "
                        f"Option {i} và Option {j} giống nhau. "
                        f"Expr1={sp.latex(all_options[i])}, Expr2={sp.latex(all_options[j])}"
                    )
                    # Tạo đáp án thay thế đơn giản (không lặp quá nhiều lần)
                    for k in range(3):
                        noise_factor = sp.Integer(j * 3 + k + 1)
                        new_cand = correct_F + noise_factor * x**2 - noise_factor * x
                        if not is_correct_candidate(new_cand):
                            # Thay thế đáp án trùng
                            if j > 0:
                                wrong_candidates[j - 1] = sp.sympify(new_cand)
                            break
                    # Cập nhật all_options
                    all_options = [correct_F] + wrong_candidates[:3]

        # Biểu diễn LaTeX
        integrand_latex = self._expr_to_latex(integrand)
        correct_latex = self._expr_to_latex(correct_F)
        wrongs_latex = [self._expr_to_latex(w) for w in wrong_candidates[:3]]

        # Trộn đáp án
        options_expr = [correct_latex] + wrongs_latex
        random.shuffle(options_expr)
        options = [f"\\( {opt} + C \\)" for opt in options_expr]
        correct_index = options_expr.index(correct_latex)
        answer_letter = self.LETTERS[correct_index]

        # Lời giải ngắn gọn: liệt kê công thức sử dụng (LaTeX inline math)
        note_map = {
            "kx_pow_n": "\\( \\int kx^n \\, dx = \\dfrac{k x^{n+1}}{n+1}, \\ n \\ne -1 \\)",
            "k_over_x": "\\( \\int \\dfrac{k}{x} \\, dx = k \\ln|x| \\)",
            "k_lin_pow_n": "\\( \\int k(Ax+B)^n \\, dx = \\dfrac{k(Ax+B)^{n+1}}{A(n+1)} \\)",
            "k_over_lin": "\\( \\int \\dfrac{k}{Ax+B} \\, dx = \\dfrac{k}{A} \\ln|Ax+B| \\)",
            "one_over_lin_pow_n": "\\( \\int \\dfrac{1}{(Ax+B)^n} \\, dx = \\dfrac{(Ax+B)^{1-n}}{(1-n)A} \\)",
            "sin_lin": "\\( \\int \\sin(Ax+B) \\, dx = -\\dfrac{\\cos(Ax+B)}{A} \\)",
            "cos_lin": "\\( \\int \\cos(Ax+B) \\, dx = \\dfrac{\\sin(Ax+B)}{A} \\)",
            "tan_lin": "\\( \\int \\tan(Ax+B) \\, dx = -\\dfrac{\\ln|\\cos(Ax+B)|}{A} \\)",
            "cot_lin": "\\( \\int \\cot(Ax+B) \\, dx = \\dfrac{\\ln|\\sin(Ax+B)|}{A} \\)",
            "sec2": "\\( \\int \\dfrac{1}{\\cos^2 x} \\, dx = \\tan x \\)",
            "csc2": "\\( \\int \\dfrac{1}{\\sin^2 x} \\, dx = -\\cot x \\)",
            "e_pow_x": "\\( \\int e^x \\, dx = e^x \\)",
            "a_pow_x": "\\( \\int a^x \\, dx = \\dfrac{a^x}{\\ln a}, \\ a>0, a\\ne1 \\)",
            "inv_e_lin": "\\( \\int e^{-(Ax+B)} \\, dx = -\\dfrac{e^{-(Ax+B)}}{A} \\)",
            "inv_a_lin": "\\( \\int a^{-(Ax+B)} \\, dx = -\\dfrac{a^{-(Ax+B)}}{A \\ln a} \\)",
            "mixed_exp_ratio": "\\( \\int K \\cdot k^x \\, dx = \\dfrac{K \\cdot k^x}{\\ln k}, \\ k>0, k\\ne1 \\)",
        }
        # Ghi chú công thức: xử lý đặc biệt cho k_lin_pow_n với n = 1
        formula_notes: List[str] = []
        for t in terms:
            ttype = t.get("type")
            if ttype == "k_lin_pow_n" and t.get("n") == 1:
                formula_notes.append(r"\( \int k(Ax+B) \, dx = kA \dfrac{x^{2}}{2} + kB x \)")
            elif isinstance(ttype, str) and ttype in note_map:
                # For n=0 case, note_map entry already valid.
                formula_notes.append(note_map[ttype])

        solution_text = (
            "Áp dụng tuyến tính của tích phân và các công thức cơ bản: "
            + "; ".join(formula_notes)
        )

        question_text = (
            f"Tính nguyên hàm: \\( \\displaystyle \\int ( {integrand_latex} ) \\, dx \\)"
        )

        return {
            "question": question_text,
            "options": options,
            "answer": answer_letter,
            "solution": solution_text,
        }

    # Các API tương thích với BaseOptimizationQuestion để có thể dùng chung main()
    def generate_full_question(self, question_number: int = 1) -> str:
        q = self.generate_question()
        content = f"Câu {question_number}: {q['question']}\n\n"
        letters = ['A', 'B', 'C', 'D']
        correct_letter = q['answer']
        for idx, opt in enumerate(q['options']):
            letter = letters[idx]
            marker = "*" if letter == correct_letter else ""
            content += f"{marker}{letter}. {opt}\n\n"
        # Ẩn lời giải: không thêm q['solution'] vào output
        return content

    def generate_question_only(self, question_number: int = 1) -> tuple:
        q = self.generate_question()
        # Ẩn lời giải: chỉ trả về đề bài
        content = f"Câu {question_number}: {q['question']}\n\n"
        # Trả về chữ cái đáp án đúng để phần Đáp án hiển thị \(B\)
        return content, q['answer']

#Thêm các dạng toán khác ở đây

# Cập nhật hàm trả về dạng toán để bao gồm lớp mới
def get_available_question_types():  # type: ignore[override]
    return [
        IndefiniteIntegralQuestion,
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
        # Luôn random: không thiết lập seed từ tham số hay ENV

        # Tạo câu hỏi
        question_types = get_available_question_types()
        questions_data = []

        for i in range(1, num_questions + 1):
            try:
                question_type = random.choice(question_types)
                # Không truyền seed; giữ hành vi ngẫu nhiên mặc định
                question_instance = question_type()
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
