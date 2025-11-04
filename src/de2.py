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

"""
Bài toán: Xác định vận tốc từ hai vị trí A -> C trong thời gian t1, suy ra vị trí sau T và khoảng cách tới B.

"""

class MotionFromTwoPointsQuestion(BaseOptimizationQuestion):


    PROBLEM_SCENARIOS = [
        {"title": "Núi Bà Đen", "context": "Tại một vị trí cụ thể ở núi Bà Đen", "actor": "Một người", "object": "cabin cáp treo"},
        {"title": "Tháp truyền hình Hà Nội", "context": "Tại một vị trí quan sát gần tháp truyền hình Hà Nội", "actor": "Một kỹ thuật viên", "object": "thiết bị bay không người lái"},
        {"title": "Khu công nghệ cao TP.HCM", "context": "Tại một khu vực kiểm soát trong Khu công nghệ cao TP.HCM", "actor": "Một nhân viên điều khiển", "object": "robot vận chuyển"},
        {"title": "Trạm radar Trường Sa", "context": "Tại một trạm radar thuộc quần đảo Trường Sa", "actor": "Một chiến sĩ", "object": "mục tiêu bay"},
        {"title": "Trung tâm nghiên cứu không gian Việt Nam", "context": "Tại một điểm trong khu vực điều khiển của Trung tâm nghiên cứu không gian Việt Nam", "actor": "Một chuyên gia", "object": "mô hình tàu vũ trụ mini"},
        {"title": "Phòng thí nghiệm mô phỏng – ĐH Bách khoa Hà Nội", "context": "Trong một phòng thí nghiệm mô phỏng tại Trường Đại học Bách khoa Hà Nội", "actor": "Một sinh viên", "object": "thiết bị mô phỏng"},
    ]

    def generate_parameters(self) -> Dict[str, Any]:
        # Sinh ngẫu nhiên tham số thay vì hardcode
        cfg = self.config

        def rand_coord() -> int:
            return random.randint(cfg.coord_min, cfg.coord_max)

        # Điểm A ngẫu nhiên
        Ax, Ay, Az = rand_coord(), rand_coord(), rand_coord()

        # Điểm B ngẫu nhiên khác A
        while True:
            Bx, By, Bz = rand_coord(), rand_coord(), rand_coord()
            if (Bx, By, Bz) != (Ax, Ay, Az):
                break

        # Vận tốc ngẫu nhiên (khác (0,0,0))
        def rand_vel_comp() -> int:
            return random.randint(-cfg.vector_max_component, cfg.vector_max_component)

        while True:
            vx, vy, vz = rand_vel_comp(), rand_vel_comp(), rand_vel_comp()
            if (vx, vy, vz) != (0, 0, 0):
                break

        # t quan sát dạng hữu tỉ đẹp
        t_candidates: Tuple[sp.Rational, ...] = (
            sp.Rational(3, 2),
            sp.Rational(2, 1),
            sp.Rational(5, 2),
            sp.Rational(3, 1),
        )
        t_observe = random.choice(t_candidates)

        # C = A + v * t_observe
        Cx = sp.nsimplify(sp.Integer(Ax) + sp.Integer(vx) * t_observe)
        Cy = sp.nsimplify(sp.Integer(Ay) + sp.Integer(vy) * t_observe)
        Cz = sp.nsimplify(sp.Integer(Az) + sp.Integer(vz) * t_observe)

        # T nguyên > t_observe nếu có trong cấu hình, nếu không lấy ceil + 1
        time_pool = [t for t in cfg.time_choices if sp.Integer(t) > t_observe]
        if time_pool:
            T = random.choice(time_pool)
        else:
            T = int(sp.ceiling(t_observe + sp.Integer(1)))

        # Chọn kịch bản để nhất quán giữa đề và lời giải
        scenario = random.choice(self.PROBLEM_SCENARIOS)

        return {
            "A": (Ax, Ay, Az),
            "B": (Bx, By, Bz),
            "C": (Cx, Cy, Cz),
            "t_observe": t_observe,
            "T": T,
            "scenario": scenario,
        }

    def calculate_answer(self) -> str:
        p = self.parameters
        Ax, Ay, Az = p["A"]
        Cx, Cy, Cz = p["C"]
        Bx, By, Bz = p["B"]
        t1 = p["t_observe"]
        T = p["T"]
        Cx_s = sp.nsimplify(Cx); Cy_s = sp.nsimplify(Cy); Cz_s = sp.nsimplify(Cz)
        AC = (sp.nsimplify(Cx_s - sp.Integer(Ax)),
              sp.nsimplify(Cy_s - sp.Integer(Ay)),
              sp.nsimplify(Cz_s - sp.Integer(Az)))
        v = tuple(sp.nsimplify(comp / t1) for comp in AC)
        M = (Ax + T * v[0], Ay + T * v[1], Az + T * v[2])
        dx = sp.nsimplify(M[0] - Bx)
        dy = sp.nsimplify(M[1] - By)
        dz = sp.nsimplify(M[2] - Bz)
        d2 = sp.simplify(dx**2 + dy**2 + dz**2)
        d = sp.sqrt(d2)
        d_numeric = float(sp.N(d, 12))
        d_round = round(d_numeric + 1e-12, 1)
        self._cached = {"AC": AC, "v": v, "M": M, "dx": dx, "dy": dy, "dz": dz, "d": d, "d2": d2, "d_round": d_round}
        return f"\\( {to_decimal_comma(d_round)} \\)"

    def generate_wrong_answers(self) -> List[str]:
        if not hasattr(self, '_cached'):
            self.calculate_answer()
        p = self.parameters
        Ax, Ay, Az = p["A"]
        Bx, By, Bz = p["B"]
        Cx, Cy, Cz = p["C"]
        t1 = p["t_observe"]
        T = p["T"]
        cache = self._cached
        AC = cache["AC"]
        # Sai 1: lấy AC làm vận tốc (quên chia t1)
        M1 = (Ax + T * AC[0], Ay + T * AC[1], Az + T * AC[2])
        d1 = sp.sqrt(sp.simplify((M1[0]-Bx)**2 + (M1[1]-By)**2 + (M1[2]-Bz)**2))
        # Sai 2: khoảng cách tại thời điểm t1 (dùng C,B)
        Cx_s = sp.nsimplify(Cx); Cy_s = sp.nsimplify(Cy); Cz_s = sp.nsimplify(Cz)
        d2 = sp.sqrt(sp.simplify((Cx_s-Bx)**2 + (Cy_s-By)**2 + (Cz_s-Bz)**2))
        # Sai 3: sai dấu z trong M
        v = cache["v"]
        M3 = (Ax + T * v[0], Ay + T * v[1], Az - T * v[2])
        d3 = sp.sqrt(sp.simplify((M3[0]-Bx)**2 + (M3[1]-By)**2 + (M3[2]-Bz)**2))
        wrong_exprs = [d1, d2, d3]

        # Trả về số làm tròn 0.1 m, không trùng đáp án đúng
        correct_round = cache.get("d_round")
        if correct_round is None:
            correct_round = round(float(sp.N(cache["d"], 12)) + 1e-12, 1)
        seen_vals: set = {correct_round}
        out_vals: List[float] = []
        for expr in wrong_exprs:
            val = float(sp.N(expr, 12))
            val_r = round(max(0.0, val) + 1e-12, 1)
            if val_r in seen_vals:
                continue
            seen_vals.add(val_r)
            out_vals.append(val_r)
            if len(out_vals) == 3:
                break
        # Nếu thiếu, thêm jitter quanh đáp án đúng
        if len(out_vals) < 3:
            for j in [0.2, -0.3, 0.4, -0.5, 0.6, -0.7]:
                cand = round(max(0.0, correct_round + j), 1)
                if cand not in seen_vals:
                    seen_vals.add(cand)
                    out_vals.append(cand)
                    if len(out_vals) == 3:
                        break
        return [f"\\( {to_decimal_comma(v)} \\)" for v in out_vals[:3]]

    def generate_question_text(self) -> str:
        p = self.parameters
        Ax, Ay, Az = p["A"]
        Bx, By, Bz = p["B"]
        Cx, Cy, Cz = p["C"]
        t1 = p["t_observe"]
        T = p["T"]
        base = p.get("scenario", random.choice(self.PROBLEM_SCENARIOS))
        main_text = (
            f"{base['context']} người ta đặt cố định một hệ trục tọa độ \\( Oxyz \\), mỗi đơn vị trên mỗi trục có độ dài bằng 1 mét. "
            f"{base['actor']} đứng cố định tại vị trí \\( B({Bx}; {By}; {Bz}) \\), quan sát một {base['object']} và thấy rằng {base['object']} này xuất phát từ điểm "
            f"\\( A({Ax}; {Ay}; {Az}) \\), biết rằng sau \\({sp.latex(t1)}\\) giây {base['object']} đến điểm \\( C({sp.latex(sp.nsimplify(Cx))}; {sp.latex(sp.nsimplify(Cy))}; {sp.latex(sp.nsimplify(Cz))}) \\). "
            f"Hỏi sau {T} giây kể từ lúc xuất phát, khoảng cách giữa {base['object']} và người quan sát bằng bao nhiêu mét? (Làm tròn kết quả đến hàng phần mười)."
        )
        return main_text

    def generate_solution(self) -> str:
        if not hasattr(self, '_cached'):
            self.calculate_answer()
        p = self.parameters
        cache = self._cached
        Ax, Ay, Az = p["A"]
        Bx, By, Bz = p["B"]
        Cx, Cy, Cz = p["C"]
        t1 = p["t_observe"]
        T = p["T"]
        AC = cache["AC"]; v = cache["v"]; M = cache["M"]; d = cache["d"]
        scenario = p.get("scenario", {})
        actor = scenario.get("actor", "người quan sát")
        object_name = scenario.get("object", "vật")
        ac_x = sp.latex(sp.nsimplify(Cx) - sp.Integer(Ax))
        ac_y = sp.latex(sp.nsimplify(Cy) - sp.Integer(Ay))
        ac_z = sp.latex(sp.nsimplify(Cz) - sp.Integer(Az))
        ac0 = sp.latex(AC[0]); ac1 = sp.latex(AC[1]); ac2 = sp.latex(AC[2])
        v0 = sp.latex(v[0]); v1 = sp.latex(v[1]); v2 = sp.latex(v[2])
        m0 = sp.latex(M[0]); m1 = sp.latex(M[1]); m2 = sp.latex(M[2])
        d0 = sp.latex(M[0]-Bx); d1 = sp.latex(M[1]-By); d2o = sp.latex(M[2]-Bz)
        t1_ltx = sp.latex(t1); d_ltx = sp.latex(d)
        d_round = cache.get("d_round")
        if d_round is None:
            d_round = round(float(sp.N(d, 12)) + 1e-12, 1)

        # Xây dựng lời giải theo văn phong mẫu và ngữ cảnh kịch bản
        part1 = (
            "Ta có: \\(" 
            + f" \\vec{{AC}} = C - A = ({ac_x}; {ac_y}; {ac_z}) = ({ac0}; {ac1}; {ac2}) "
            + "\\)"
        )

        part2 = (
            f"Do {object_name} di chuyển từ A đến C trong \\({t1_ltx}\\) giây, nên véc tơ vận tốc mỗi giây là:\n\n"
            "\\( \\vec v = \\frac{\\text{Quãng đường}}{\\text{Thời gian}} = \\frac{\\vec{AC}}{" + t1_ltx + "} = ("
            + v0 + "; " + v1 + "; " + v2 + ") \\)"
        )

        part3 = (
            f"Sau {T} giây, vị trí của {object_name} là: \n\\( M = A + {T}\\vec v = (" + m0 + "; " + m1 + "; " + m2 + ") \\)"
        )

        sqrt_inner = "(" + d0 + ")^2 + (" + d1 + ")^2 + (" + d2o + ")^2"
        part4 = (
            f"Tọa độ người quan sát ({actor.lower()}) là \\( B({Bx}; {By}; {Bz}) \\), khoảng cách tại thời điểm đó là:\n\n"
            "\\( BM = \\sqrt{" + sqrt_inner + "} = " + d_ltx + f" \\approx {to_decimal_comma(d_round)} \\text{{ (mét)}} \\)"
        )

        part5 = f"Đáp án: Sau {T} giây, khoảng cách giữa {object_name} và {actor.lower()} là khoảng \\( {to_decimal_comma(d_round)} \\) mét."

        return "\n\n".join([part1, part2, part3, part4, part5])



# Cập nhật hàm trả về dạng toán để bao gồm lớp mới
def get_available_question_types():  # type: ignore[override]
    return [
        #MotionDistance3DQuestion,
        MotionFromTwoPointsQuestion,
        #TwoBalloonMinDistanceQuestion,
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
