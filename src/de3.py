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

    @staticmethodtikz
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
                    # Luôn in cả 2 định dạng dấu chấm và dấu phẩy
                    ans = answer
                    if ans.startswith("\\(") and ans.endswith("\\)"):
                        ans = ans[2:-2].strip()
                    if ans.startswith("$") and ans.endswith("$"):
                        ans = ans[1:-1].strip()
                    ans_comma = ans.replace('.', ',')
                    latex_content += f"Câu {idx}: {ans} | {ans_comma}\n\n"

        latex_content += "\\end{document}"
        return latex_content


    """Khoảng cách nhỏ nhất giữa hai khinh khí cầu chuyển động vuông góc trong không gian với độ cao không đổi.
    """
class TwoBalloonMinDistanceQuestion(BaseOptimizationQuestion):


    PROBLEM_SCENARIOS = [
        {"title": "Khung cảnh mặc định", "context": "Gắn hệ trục tọa độ \\((Oxyz)\\) với mặt đất là mặt phẳng toạ độ \\((Oxy)\\)", "place_extra": ""},
        {"title": "Khu du lịch Sa Pa", "context": "Trong hệ trục toạ độ \\((Oxyz)\\) gắn với mặt đất", "place_extra": "tại khu du lịch Sa Pa"},
        {"title": "Bãi biển Nha Trang", "context": "Trên một hệ toạ độ \\((Oxyz)\\)", "place_extra": "gần bãi biển Nha Trang"},
        {"title": "Lễ hội khinh khí cầu Huế", "context": "Hệ trục \\((Oxyz)\\) được chọn", "place_extra": "tại lễ hội khinh khí cầu Huế"},
        {"title": "Cánh đồng Mộc Châu", "context": "Trong hệ toạ độ \\((Oxyz)\\)", "place_extra": "trên cánh đồng Mộc Châu"},
        {"title": "Đồng bằng sông Cửu Long", "context": "Một hệ toạ độ \\((Oxyz)\\) được chọn", "place_extra": "ở đồng bằng sông Cửu Long"},
    ]

    def generate_parameters(self) -> Dict[str, Any]:
        # Chọn kịch bản để nhất quán giữa đề và lời giải
        scenario = random.choice(self.PROBLEM_SCENARIOS)

        # Hồ sơ toạ độ để đa dạng hoá khoảng cách ban đầu → thời gian tối ưu phong phú
        profile = random.choices(["near", "mid", "far"], weights=[3, 2, 1], k=1)[0]
        if profile == "near":
            low_c, high_c = self.config.coord_min, self.config.coord_max
        elif profile == "mid":
            low_c, high_c = -10, 10
        else:
            low_c, high_c = -20, 25

        def rand_coord() -> int:
            return random.randint(low_c, high_c)

        # Tìm bộ tham số sao cho t_min rơi vào dải mong muốn (giảm trường hợp t*=0)
        target_min_h = 1.0 / 60.0   # 1 phút
        target_max_h = 0.6          # 36 phút
        best_tuple: Optional[Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int], float]] = None
        for _ in range(30):
            X0 = (rand_coord(), rand_coord(), rand_coord())
            while True:
                Y0 = (rand_coord(), rand_coord(), rand_coord())
                if Y0 != X0:
                    break

            # Hồ sơ tốc độ nhanh/chậm để ảnh hưởng đến thời gian đạt cực tiểu
            speed_profile = random.choices(["slow", "medium", "fast"], weights=[2, 3, 2], k=1)[0]
            if speed_profile == "slow":
                vx_mag_choices = [6, 8, 10, 12]
                vy_mag_choices = [4, 6, 8, 10]
            elif speed_profile == "medium":
                vx_mag_choices = [15, 18, 20, 25]
                vy_mag_choices = [10, 12, 15, 18]
            else:
                vx_mag_choices = [25, 30, 35, 40]
                vy_mag_choices = [18, 20, 25]
            vX = (-random.choice(vx_mag_choices), 0, 0)
            vY = (0, random.choice(vy_mag_choices), 0)

            # Ước tính nhanh t_min = -b/(2a) cho d^2(t)
            dx0 = Y0[0] - X0[0]
            dy0 = Y0[1] - X0[1]
            dvx = vY[0] - vX[0]  # = |vX_x|
            dvy = vY[1] - vX[1]  # = |vY_y|
            a_coef = dvx * dvx + dvy * dvy
            b_coef = 2.0 * (dx0 * dvx + dy0 * dvy)
            if a_coef == 0:
                t_min_est = 0.0
            else:
                t_min_est = -b_coef / (2.0 * a_coef)

            # Lưu lại cấu hình hợp lệ đầu tiên trong dải mục tiêu
            if target_min_h <= t_min_est <= target_max_h:
                best_tuple = (X0, Y0, vX, vY, t_min_est)
                break
            # Nếu chưa rơi vào dải thì giữ lại cấu hình có t_min_est dương nhỏ nhất để fallback
            if t_min_est > 0:
                if best_tuple is None or t_min_est < best_tuple[4]:
                    best_tuple = (X0, Y0, vX, vY, t_min_est)

        # Chốt cấu hình
        if best_tuple is not None:
            X0, Y0, vX, vY, _ = best_tuple
        else:
            # Fallback cuối cùng nếu tất cả đều không đạt
            X0 = (rand_coord(), rand_coord(), rand_coord())
            Y0 = (rand_coord(), rand_coord(), rand_coord())
            speed_profile = random.choice(["slow", "medium", "fast"])  # không dùng nữa, chỉ để ghi nhớ
            vx_mag_choices = [15, 18, 20, 25]
            vy_mag_choices = [10, 12, 15, 18]
            vX = (-random.choice(vx_mag_choices), 0, 0)
            vY = (0, random.choice(vy_mag_choices), 0)

        return {
            "X0": X0,
            "Y0": Y0,
            "vX": vX,  # km/h
            "vY": vY,
            "scenario": scenario,
        }

    def calculate_answer(self) -> str:
        p = self.parameters
        # Symbolic time t
        t = sp.symbols('t', real=True)
        X0 = p["X0"]; Y0 = p["Y0"]; vX = p["vX"]; vY = p["vY"]
        X_t = [X0[i] + vX[i]*t for i in range(3)]
        Y_t = [Y0[i] + vY[i]*t for i in range(3)]
        diff = [sp.simplify(Y_t[i]-X_t[i]) for i in range(3)]
        d2 = sp.simplify(sum(sp.expand(comp**2) for comp in diff))
        # t_min = -b/(2a) cho d2(t) = a t^2 + b t + c
        poly = sp.Poly(sp.expand(d2), t)
        coeffs = poly.all_coeffs()
        a = sp.nsimplify(coeffs[0]); b = sp.nsimplify(coeffs[1])
        t_min = sp.nsimplify(-b / (2 * a))
        # Clamp t to [0, +inf)
        t_star = sp.Max(0, t_min)
        d2_star = sp.simplify(d2.subs(t, t_star))
        d_star = sp.sqrt(d2_star)
        d_star_numeric = float(sp.N(d_star, 12))
        d_star_round = round(d_star_numeric + 1e-12, 1)
        t_star_numeric = float(sp.N(t_star, 12))
        t_star_round = round(t_star_numeric + 1e-12, 1)
        self._cache_balloon = {
            "t": t, "X_t": X_t, "Y_t": Y_t, "diff": diff, "d2": d2,
            "t_min": t_min, "t_star": t_star, "d2_star": d2_star, "d_star": d_star,
            "d_min_round": d_star_round, "t_min_round": t_star_round
        }
        t_display = format_time_hours_or_minutes(t_star_numeric, 1)
        return f"\\( d_\\text{{min}} = {d_star_round}\\,\\text{{km}},\\ t = {t_display} \\)"

    def generate_wrong_answers(self) -> List[str]:
        if not hasattr(self, '_cache_balloon'):
            self.calculate_answer()
        c = self._cache_balloon
        t_sym = c["t"]; d2 = c["d2"]
        t_min = c["t_min"]; t_star = c["t_star"]
        # Sai 1: Dùng khoảng cách tại t=0
        t_wrong_1 = 0
        d_wrong_1 = sp.simplify(d2.subs(t_sym, t_wrong_1))
        # Sai 2: Khoảng cách tại t = t_star/2
        t_wrong_2 = sp.nsimplify(t_star/2)
        d_wrong_2 = sp.simplify(d2.subs(t_sym, t_wrong_2))
        # Sai 3: Chọn thời điểm lệch và/hoặc quên lấy căn (d^2)
        t_wrong_3 = sp.nsimplify(t_star + sp.Rational(3, 10))
        d_wrong_3 = sp.simplify(d2.subs(t_sym, t_wrong_3))

        wrong_pairs = [
            (t_wrong_1, d_wrong_1, True),
            (t_wrong_2, d_wrong_2, True),
            (t_wrong_3, d_wrong_3, False),
        ]

        answers: List[str] = []
        seen: set = set([(c.get("d_min_round"), c.get("t_min_round"))])
        for tw, dw, take_sqrt in wrong_pairs:
            t_num = float(sp.N(tw, 12))
            t_r = round(max(0.0, t_num) + 1e-12, 1)
            d_num = float(sp.N(sp.sqrt(dw) if take_sqrt else dw, 12))
            d_r = round(max(0.0, d_num) + 1e-12, 1)
            key = (d_r, t_r)
            if key in seen:
                continue
            seen.add(key)
            t_display = format_time_hours_or_minutes(t_r, 1)
            answers.append(f"\\( d_\\text{{min}} = {d_r}\\,\\text{{km}},\\ t = {t_display} \\)")
            if len(answers) == 3:
                break

        # Nếu thiếu thì jitter thêm
        j = 0.2
        while len(answers) < 3 and j < 1.1:
            t_r = round(float(sp.N(t_star, 12)) + j, 1)
            d_num = float(sp.N(sp.sqrt(d2.subs(t_sym, t_r)), 12))
            d_r = round(d_num + 1e-12, 1)
            key = (d_r, t_r)
            if key not in seen:
                seen.add(key)
                t_display = format_time_hours_or_minutes(t_r, 1)
                answers.append(f"\\( d_\\text{{min}} = {d_r}\\,\\text{{km}},\\ t = {t_display} \\)")
            j += 0.2

        return answers[:3]

    def generate_question_text(self) -> str:
        p = self.parameters
        base = p.get("scenario", random.choice(self.PROBLEM_SCENARIOS))
        X0 = p["X0"]; Y0 = p["Y0"]; vX = p["vX"]; vY = p["vY"]
        # Main statement
        location_prefix = base['context']
        extra = (" " + base['place_extra']) if base.get('place_extra') else ""
        main_text = (
            f"{location_prefix}{extra}, gắn hệ trục tọa độ \\(Oxyz\\) với mặt đất là mặt phẳng tọa độ \\((Oxy)\\), đơn vị 1 km, trục \\(Ox\\) hướng Nam, \\(Oy\\) hướng Đông. "
            f"Tại thời điểm ban đầu có hai khinh khí cầu X, Y với tọa độ \\(X({X0[0]}; {X0[1]}; {X0[2]})\\), \\(Y({Y0[0]}; {Y0[1]}; {Y0[2]})\\). "
            f"Khinh khí cầu X bay về phía Bắc với tốc độ {abs(vX[0])} km/h, khinh khí cầu Y bay về phía Đông với tốc độ {vY[1]} km/h, độ cao không đổi. "
            "Hỏi khoảng cách nhỏ nhất giữa hai khinh khí cầu và thời điểm đạt được khoảng cách đó (tính bằng giờ)."
        )
        
        # Thêm hình vẽ tikzpicture
        tikz_picture = f"""
\\begin{{tikzpicture}}[
	scale=2,
	axis/.style={{->, >=stealth, thick}},
	dashed_line/.style={{dashed, thin}}
	]
	% Vẽ các trục tọa độ
	\\draw[axis] (-2,0,0) -- (2.2,0,0) node[below left] {{$y$}};
	\\draw[axis] (0,-1.5,0) -- (0,1.5,0) node[below right] {{$z$}};
	\\draw[axis] (0,0,-3) -- (0,0,3) node[above] {{$x$}};
	
	% Gốc tọa độ
	\\node[below left] at (0,0,0) {{$O$}};
	
	% Các nhãn phương hướng
	\\node[below] at (0,0,3.2) {{Nam}};
	\\node[right] at (2.3,0,0) {{Đông}};
	
	% Điểm X và các đường gióng
	\\coordinate (X) at (1.2,0.5,0);
	\\coordinate (X_proj) at (1.2,-0.5,0);
	\\draw[dashed_line] (X) -- (X_proj);
	\\fill (X) circle (1pt);
	\\fill (X_proj) circle (1pt);
	\\node[above] at (X) {{$X$}};
	
	% Vector X1
	\\draw[axis, thick] (X) -- (1.2,0.5,-1) node[above right] {{$X_1$}};
	
	% Điểm Y và các đường gióng
	\\coordinate (Y) at (-1,0.5,1);
	\\coordinate (Y_proj) at (-1,-0.25,1);
	\\draw[dashed_line] (Y) -- (Y_proj);
	\\fill (Y) circle (1pt);
	\\fill (Y_proj) circle (1pt);
	\\node[above] at (Y) {{$Y$}};
	
	% Vector Y1
	\\coordinate (Y1_start) at (-1,0.5,1);
	\\coordinate (Y1_end) at (-0.2,0.5,1);
	\\draw[axis, thick] (Y1_start) -- (Y1_end) node[midway, above] {{$Y_1$}};
	
\\end{{tikzpicture}}
"""
        
        return main_text + "\n\n" + tikz_picture

    def generate_solution(self) -> str:
        if not hasattr(self, '_cache_balloon'):
            self.calculate_answer()
        p = self.parameters
        c = self._cache_balloon
        t = c["t"]; diff = c["diff"]; d2 = c["d2"]; tmin = c["t_min"]; tstar = c["t_star"]; d_star = c["d_star"]
        X0 = p["X0"]; Y0 = p["Y0"]; vX = p["vX"]; vY = p["vY"]
        base = p.get("scenario", {})
        location_prefix = base.get('context', 'Gắn hệ trục tọa độ \\(Oxyz\\) với mặt đất là mặt phẳng toạ độ \\((Oxy)\\)')
        place_extra = base.get('place_extra', '')
        place_text = (" " + place_extra) if place_extra else ""

        # Biểu thức LaTeX gọn gàng
        X_t0 = [sp.latex(sp.simplify(expr)) for expr in c["X_t"]]
        Y_t0 = [sp.latex(sp.simplify(expr)) for expr in c["Y_t"]]
        diff_ltx = [sp.latex(sp.simplify(expr)) for expr in diff]
        d2_ltx = sp.latex(sp.simplify(d2))
        tmin_ltx = sp.latex(sp.nsimplify(tmin))
        tstar_ltx = sp.latex(sp.nsimplify(tstar))
        dmin_ltx = sp.latex(sp.nsimplify(d_star))

        # Xấp xỉ
        tmin_hours = float(sp.N(tmin, 12))
        tstar_hours = float(sp.N(tstar, 12))
        tstar_minutes = tstar_hours * 60.0
        tstar_minutes_approx = to_decimal_comma(f"{tstar_minutes:.1f}")
        dmin_approx = to_decimal_comma(f"{float(sp.N(d_star, 12)):.3f}")

        parts: List[str] = []

        # Ngữ cảnh
        parts.append(
            f"{location_prefix}{place_text}."
        )

        # Vị trí ban đầu
        parts.append(
            "+ Vị trí ban đầu:\n\n"
            f"Tại thời điểm ban đầu (\\(t=0\\)): Khinh khí cầu X có tọa độ \\(X({X0[0]}; {X0[1]}; {X0[2]})\\), khinh khí cầu Y có tọa độ \\(Y({Y0[0]}; {Y0[1]}; {Y0[2]})\\)."
        )

        # Vector vận tốc
        parts.append(
            "+ Vector vận tốc:\n\n"
            f"Khinh khí cầu X bay về phía Bắc với tốc độ \\({abs(vX[0])}\\,\\mathrm{{km/h}}\\). Hướng Bắc ngược chiều với trục \\(Ox\\), do đó \\(\\vec v_X = ({vX[0]}, {vX[1]}, {vX[2]})\\). "
            f"Khinh khí cầu Y bay về phía Đông với tốc độ \\({vY[1]}\\,\\mathrm{{km/h}}\\). Hướng Đông cùng chiều với trục \\(Oy\\), do đó \\(\\vec v_Y = ({vY[0]}, {vY[1]}, {vY[2]})\\)."
        )

        # Phương trình tọa độ theo thời gian
        parts.append(
            "+ Phương trình tọa độ theo thời gian \\(t\\):\n\n"
            f"Tọa độ của X và Y tại thời điểm \\(t\\) (tính bằng giờ) là: "
            + "\n\\(X(t) = (" + X_t0[0] + ", " + X_t0[1] + ", " + X_t0[2] + ")\\), \\(Y(t) = (" + Y_t0[0] + ", " + Y_t0[1] + ", " + Y_t0[2] + ")\\)."
        )

        # Khoảng cách
        parts.append(
            "+ Khoảng cách giữa hai khinh khí cầu:\n\n"
            + "Vector chênh lệch: \\( \\vec{XY}(t) = Y(t) - X(t) = (" + diff_ltx[0] + ", " + diff_ltx[1] + ", " + diff_ltx[2] + ") \\).\n\n"
            + "Bình phương khoảng cách: \\( d^2(t) = " + d2_ltx + " \\)."
        )

        # Tối ưu
        if tmin_hours < 0:
            parts.append(
                "+ Tìm khoảng cách ngắn nhất:\n\n"
                + "Do \\(d(t)\\) đạt cực tiểu khi \\(d^2(t)\\) đạt cực tiểu, nghiệm tới hạn \\( t_0 = -\\dfrac{b}{2a} = " + tmin_ltx + "\\) là âm (trong quá khứ)."
                + "\nVì bài toán xét từ \\(t=0\\), cực tiểu trên \\( [0, +\\infty) \\) đạt tại \\( t^* = 0 \\)."
            )
        else:
            parts.append(
                "+ Tìm khoảng cách ngắn nhất:\n\n"
                + "Do \\(d(t)\\) đạt cực tiểu khi \\(d^2(t)\\) đạt cực tiểu, xét hàm bậc hai \\(f(t)=d^2(t)\\). Khi đó \\(f'(t)=0\\) cho "
                + "\\( t_0 = -\\dfrac{b}{2a} = " + tmin_ltx + f" \\approx {tmin_hours:.3f}\\,\\text{{giờ}}\\)."
                + "\nVì \\(t_0 \\ge 0\\), ta có \\( t^* = t_0 = " + tstar_ltx + "\\)."
            )

        # Khoảng cách nhỏ nhất
        parts.append(
            "+ Khoảng cách nhỏ nhất:\n\n"
            + "Tại \\( t^* = " + tstar_ltx + f" \\approx {tstar_hours:.3f}\\,\\text{{giờ}} = {tstar_minutes_approx}\\,\\text{{phút}}\\), ta được \\( d_\\text{{min}} = " + dmin_ltx + f" \\approx {dmin_approx}\\,\\text{{km}} \\)."
        )

        # Kết luận
        parts.append(
            f"Kết luận: Hai khinh khí cầu gần nhau nhất sau khoảng \\({tstar_minutes_approx}\\) phút với khoảng cách xấp xỉ \\({dmin_approx}\\,\\text{{km}}\\)."
        )

        return "\n\n".join(parts)

#Thêm dạng toán khác ở đây

# Cập nhật hàm trả về dạng toán để bao gồm lớp mới
def get_available_question_types():  # type: ignore[override]
    return [
        TwoBalloonMinDistanceQuestion,
        #Thêm dạng toán khác ở đây
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
