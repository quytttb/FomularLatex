"""
Dạng toán tối ưu hóa chuyển động
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
                    # Luôn in cả 2 định dạng dấu chấm và dấu phẩy, bọc trong inline math
                    ans = answer
                    if ans.startswith("\\(") and ans.endswith("\\)"):
                        ans = ans[2:-2].strip()
                    if ans.startswith("$") and ans.endswith("$"):
                        ans = ans[1:-1].strip()
                    ans_comma = ans.replace('.', ',')
                    latex_content += f"Câu {idx}: \\({ans}\\) | \\({ans_comma}\\)\n\n"

        latex_content += "\\end{document}"
        return latex_content


    """Khoảng cách nhỏ nhất giữa hai khinh khí cầu chuyển động vuông góc trong không gian với độ cao không đổi.
    """

class RectangleInSemicircleMaxAreaQuestion(BaseOptimizationQuestion):
    """
    Diện tích lớn nhất của hình chữ nhật nội tiếp nửa đường tròn bán kính R=4 m,
    cạnh đáy trùng đường kính, hai đỉnh trên chạm vào cung nửa tròn.
    """

    PROBLEM_SCENARIOS = [
        {
            "title": "Cổng vòm",
            "text": r"Một chiếc cổng vòm trong công viên có dạng nửa hình tròn bán kính \(R=4\) mét. Người ta muốn dựng một tấm biển quảng cáo hình chữ nhật sao cho đáy tấm biển nằm trên đường kính và hai góc trên cùng chạm vào vòm nửa hình tròn. Diện tích lớn nhất có thể của tấm biển là bao nhiêu?",
        },
        {
            "title": "Tấm kính cửa sổ",
            "text": r"Một cửa sổ được thiết kế có dạng nửa hình tròn bán kính \(R=4\) mét. Người thợ lắp muốn đặt một tấm kính hình chữ nhật vào trong phần nửa hình tròn đó sao cho cạnh dưới của tấm kính trùng với đường kính và hai đỉnh trên cùng chạm vào cung nửa tròn. Diện tích lớn nhất của tấm kính là bao nhiêu?",
        },
        {
            "title": "Nhà kho",
            "text": r"Một nhà kho có mái vòm hình nửa hình tròn bán kính \(R=4\) mét. Người ta muốn dựng một cửa ra vào hình chữ nhật bên trong nửa hình tròn, có đáy nằm trên mặt đất (trùng với đường kính), hai góc trên cùng chạm vào mái vòm. Tính diện tích lớn nhất của cửa ra vào.",
        },
        {
            "title": "Tấm bảng hiệu",
            "text": r"Một bảng hiệu trang trí được lắp đặt bên trong khung thép có dạng nửa hình tròn bán kính \(R=4\) mét. Bảng hiệu được làm hình chữ nhật sao cho cạnh dưới nằm trên đường kính và hai đỉnh trên cùng chạm vào khung nửa hình tròn. Hỏi diện tích lớn nhất của bảng hiệu?",
        },
        {
            "title": "Mảnh đất ven hồ",
            "text": r"Một mảnh đất ven hồ có biên giới phía trên là một nửa đường tròn bán kính \(R=4\) mét, còn biên giới phía dưới là đường kính. Người ta muốn dựng một chuồng nuôi hình chữ nhật nằm gọn trong mảnh đất đó. Tính diện tích lớn nhất có thể của chuồng nuôi.",
        },
    ]

    def generate_parameters(self) -> Dict[str, Any]:
        scenario = random.choice(self.PROBLEM_SCENARIOS)
        # Random bán kính R trong khoảng 3..8 mét
        R = random.choice([3, 4, 5, 6, 7, 8])
        return {
            "R": R,
            "scenario": scenario,
        }

    def calculate_answer(self) -> str:
        p = self.parameters
        R = sp.Integer(p.get("R", 4))
        # Kết quả chuẩn: S_max = R^2
        s_max = R**2
        self._cache_rect_semicircle = {"R": R, "S_max": s_max}
        return f"\\( {sp.latex(sp.nsimplify(s_max))}\\,\\text{{m}}^2 \\)"

    def generate_wrong_answers(self) -> List[str]:
        if not hasattr(self, '_cache_rect_semicircle'):
            self.calculate_answer()
        R = int(self._cache_rect_semicircle["R"])  # dùng số thực để tránh lỗi kiểu
        Rf = float(R)
        x_vals = [0.5 * Rf, 0.75 * Rf, Rf / math.sqrt(3.0)]
        wrongs: List[str] = []
        for x in x_vals:
            area = 2.0 * x * math.sqrt(max(0.0, Rf*Rf - x*x))
            val = float(area)
            num = round(val + 1e-12, 1)
            if abs(num - float(Rf*Rf)) < 1e-9:
                continue
            wrongs.append(f"\\( {num}\\,\\text{{m}}^2 \\)")
            if len(wrongs) == 3:
                break
        # Fallback nếu trùng
        j = 0.5
        while len(wrongs) < 3 and j < 2.1:
            x = (Rf / math.sqrt(2.0)) + j
            area = 2.0 * x * math.sqrt(max(0.0, Rf*Rf - x*x))
            num = round(float(area) + 1e-12, 1)
            if abs(num - float(Rf*Rf)) > 1e-9 and f"{num}" not in "".join(wrongs):
                wrongs.append(f"\\( {num}\\,\\text{{m}}^2 \\)")
            j += 0.3
        return wrongs[:3]

    def generate_question_text(self) -> str:
        p = self.parameters
        scenario = p.get("scenario", random.choice(self.PROBLEM_SCENARIOS))
        R = p.get("R", 4)
        # Thay R=4 bằng R được random trong mẫu đề
        main_text = scenario["text"].replace("\\(R=4\\)", f"\\(R={R}\\)")

        # Hình vẽ minh họa
        tikz_picture = r"""
\begin{tikzpicture}[line cap=round, line join=round]
  \coordinate (A) at (-4,0); \coordinate (B) at (4,0); \coordinate (O) at (0,0);
  \coordinate (Q) at (-3,0); \coordinate (P) at (3,0);
  \coordinate (M) at (-3,2.64575131); \coordinate (N) at (3,2.64575131);

  \draw (A) -- (B);
  \draw (-4,0) arc (180:0:4);

  \fill[gray!15] (Q) -- (P) -- (N) -- (M) -- cycle;
  \draw (Q) -- (P) -- (N) -- (M) -- cycle;
  \draw (Q) -- (M) (P) -- (N);

  \fill (Q) circle (1pt) (P) circle (1pt) (O) circle (1pt);
  \node[below left=2pt]  at (Q) {\(Q\)};
  \node[below right=2pt] at (P) {\(P\)};
  \node[below=2pt]       at (O) {\(O\)};
  \node[above left=2pt]  at (M) {\(M\)};
  \node[above right=2pt] at (N) {\(N\)};
\end{tikzpicture}
"""
        return main_text + "\n\n" + tikz_picture

    def generate_solution(self) -> str:
        if not hasattr(self, '_cache_rect_semicircle'):
            self.calculate_answer()
        p = self.parameters
        R = int(self._cache_rect_semicircle["R"]) if hasattr(self, '_cache_rect_semicircle') else int(p.get("R", 4))
        # Thiết lập biểu thức để trình bày (không cần tính biểu thức Pow * Rational để tránh cảnh báo typing)
        x = sp.symbols('x', real=True, nonnegative=True)
        A = 2*x*sp.sqrt(R**2 - x**2)
        dA = sp.diff(A, x)
        # Dạng nghiệm tối ưu
        x_star_ltx = "\\dfrac{R}{\\sqrt{2}}"
        h_star_ltx = "\\dfrac{R}{\\sqrt{2}}"
        width_ltx = r"\sqrt{2}\,R"
        parts: List[str] = []
        parts.append(f"Xét nửa đường tròn bán kính \\(R={R}\\) (đơn vị: mét). Gọi \\(x\\) là nửa chiều dài hình chữ nhật, \\(h\\) là chiều rộng.")
        # Cách 1 (đạo hàm) — tạm thời ẩn đi theo yêu cầu
        # parts.append("Miền xác định: \\(x\\in[0," + str(R) + "]\\). Tại biên \\(x=0\\) hoặc \\(x=" + str(R) + "\\) thì \\(S=0\\).")
        # parts.append("Tính đạo hàm và giải \\(S'(x)=0\\) được \\(R^2-2x^2=0 \\Rightarrow x_{\\max} = \\dfrac{R}{\\sqrt{2}}\\), khi đó \\(h_{\\max} = \\dfrac{R}{\\sqrt{2}}\\).")
        smax_num_ltx = sp.latex(sp.nsimplify(R*R))
        # Trình bày lượng giác theo từng bước, dùng \alpha thay cho \theta và thêm bước S = 2xh
        parts.append("Gọi \\(\\alpha\\) là góc giữa bán kính \\(ON\\) và trục \\(Oy\\) (\\(0 \\le \\alpha \\le \\tfrac{\\pi}{2}\\)).")
        parts.append("\\(\\Rightarrow x = R\\sin\\alpha\\) và \\(h = R\\cos\\alpha\\).")
        parts.append("Khi đó \\(S = 2R^2\\sin\\alpha\\cos\\alpha = R^2\\sin 2\\alpha\\).")
        parts.append("Hàm \\(\\sin 2\\alpha\\) đạt giá trị lớn nhất bằng 1 tại \\(\\alpha = \\tfrac{\\pi}{4}\\).")
        parts.append("\\(\\Rightarrow x_{\\max} = \\dfrac{R}{\\sqrt{2}},\\ h_{\\max} = \\dfrac{R}{\\sqrt{2}}\\)")
        parts.append("\\(\\Rightarrow S_{\\max} = R^2 = " + smax_num_ltx + "\\,\\text{m}^2\\)")
        return "\n\n".join(parts)

# Cập nhật hàm trả về dạng toán để bao gồm lớp mới
def get_available_question_types():  # type: ignore[override]
    return [
        RectangleInSemicircleMaxAreaQuestion,
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
