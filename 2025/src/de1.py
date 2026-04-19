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



"""Dạng bài: Chuyển động thẳng đều trong không gian và tính khoảng cách sau t giây.

Mô tả tổng quát:
- Vật bắt đầu tại điểm A(xA, yA, zA)
- Chuyển động thẳng đều theo vectơ chỉ phương u(a,b,c) với vận tốc v (m/s)
- Người quan sát đứng tại điểm B(xB, yB, zB)
- Hỏi sau T giây, khoảng cách giữa vật và người quan sát là bao nhiêu (làm tròn đến 0.1 m)
"""
class MotionDistance3DQuestion(BaseOptimizationQuestion):

    PROBLEM_SCENARIOS = [
        {"location": "núi Bà Đen", "observer_role": "một người", "object_name": "cabin cáp treo", "observer_label": "B", "start_label": "A"},
        {"location": "đỉnh núi Hàm Rồng", "observer_role": "một nhân viên kiểm soát", "object_name": "flycam", "observer_label": "M", "start_label": "N"},
        {"location": "cảng hàng không quốc tế Long Thành", "observer_role": "một kỹ sư điều hành", "object_name": "máy bay không người lái", "observer_label": "G", "start_label": "H"},
        {"location": "công viên khoa học Quy Nhơn", "observer_role": "một học sinh", "object_name": "robot thí nghiệm", "observer_label": "P", "start_label": "Q"},
        {"location": "cảng Hải Phòng", "observer_role": "một thủy thủ", "object_name": "tàu ngầm mini", "observer_label": "T", "start_label": "U"},
        {"location": "khu bảo tồn thiên nhiên Cát Tiên", "observer_role": "một nhà sinh học", "object_name": "thiết bị ghi hình bay", "observer_label": "E", "start_label": "F"},
    ]

    def __init__(self, config: Optional["GeneratorConfig"] = None):
        super().__init__(config)
        # exact mode can be toggled via env var OPT_EXACT
        env_exact = os.environ.get("OPT_EXACT")
        if env_exact is not None:
            self.config.exact_mode = env_exact.strip() in {"1", "true", "True"}

    def generate_parameters(self) -> Dict[str, Any]:
        """
        Sinh tham số ngẫu nhiên cho bài toán chuyển động 3D
        
        Biến sử dụng:
        - kich_ban: kịch bản câu chuyện (địa điểm, đối tượng quan sát, tên điểm)
        - diem_xuat_phat_*: tọa độ điểm xuất phát A (x, y, z)
        - diem_quan_sat_*: tọa độ điểm người quan sát B (x, y, z) 
        - vector_chi_phuong_*: thành phần vector chỉ phương chuyển động (x, y, z)
        - van_toc_chuyen_dong: vận tốc chuyển động (m/s)
        - thoi_gian_chuyen_dong: thời gian chuyển động (giây)
        """
        
        # Chọn kịch bản câu chuyện ngẫu nhiên (đều nhau, không ưu tiên)
        kich_ban = random.choice(self.PROBLEM_SCENARIOS)

        # Độ dài mỗi đơn vị trên trục toạ độ (m/đv) – không cố định 1, chọn ngẫu nhiên
        do_dai_don_vi_met = random.choice([1, 2, 3, 4])

        # Sinh vectơ chỉ phương nguyên nhỏ (không chuẩn hóa bằng chia nguyên)
        def random_direction_vector(max_component: int) -> Tuple[int, int, int]:
            while True:
                ax = random.randint(-max_component, max_component)
                ay = random.randint(-max_component, max_component)
                az = random.randint(-max_component, max_component)
                if (ax, ay, az) == (0, 0, 0):
                    continue
                return ax, ay, az

        vector_chi_phuong_x, vector_chi_phuong_y, vector_chi_phuong_z = random_direction_vector(self.config.vector_max_component)
        norm_sq = vector_chi_phuong_x ** 2 + vector_chi_phuong_y ** 2 + vector_chi_phuong_z ** 2

        # Chọn vận tốc giúp k đẹp: thêm các ứng viên là bội của norm_sq để có k = sqrt(norm_sq) khi v = norm_sq
        default_candidates = [3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 18, 20, 21, 24]
        derived = [m * norm_sq for m in range(1, 7)]
        cac_van_toc_ung_vien = sorted(set(default_candidates + derived))
        van_toc_chuyen_dong = random.choice(cac_van_toc_ung_vien)
        thoi_gian_chuyen_dong = random.choice(self.config.time_choices)

        # Sinh điểm A, B trong miền cấu hình và khác nhau
        def sinh_toa_do_ngau_nhien():
            return random.randint(self.config.coord_min, self.config.coord_max)
        diem_xuat_phat_x, diem_xuat_phat_y, diem_xuat_phat_z = sinh_toa_do_ngau_nhien(), sinh_toa_do_ngau_nhien(), sinh_toa_do_ngau_nhien()
        diem_quan_sat_x, diem_quan_sat_y, diem_quan_sat_z = sinh_toa_do_ngau_nhien(), sinh_toa_do_ngau_nhien(), sinh_toa_do_ngau_nhien()
        while (diem_xuat_phat_x, diem_xuat_phat_y, diem_xuat_phat_z) == (diem_quan_sat_x, diem_quan_sat_y, diem_quan_sat_z):
            diem_quan_sat_x, diem_quan_sat_y, diem_quan_sat_z = sinh_toa_do_ngau_nhien(), sinh_toa_do_ngau_nhien(), sinh_toa_do_ngau_nhien()

        return {
            "kich_ban": kich_ban,
            "do_dai_don_vi_met": do_dai_don_vi_met,
            "diem_xuat_phat_x": diem_xuat_phat_x, "diem_xuat_phat_y": diem_xuat_phat_y, "diem_xuat_phat_z": diem_xuat_phat_z,
            "diem_quan_sat_x": diem_quan_sat_x, "diem_quan_sat_y": diem_quan_sat_y, "diem_quan_sat_z": diem_quan_sat_z,
            "vector_chi_phuong_x": vector_chi_phuong_x, "vector_chi_phuong_y": vector_chi_phuong_y, "vector_chi_phuong_z": vector_chi_phuong_z,
            "van_toc_chuyen_dong": van_toc_chuyen_dong,
            "thoi_gian_chuyen_dong": thoi_gian_chuyen_dong,
        }

    def calculate_answer(self) -> str:
        """
        Tính đáp án cho bài toán chuyển động 3D
        
        Biến sử dụng:
        - cac_tham_so: dictionary chứa tất cả tham số đầu vào
        - diem_xuat_phat_*: tọa độ điểm xuất phát A (x, y, z)
        - diem_quan_sat_*: tọa độ điểm quan sát B (x, y, z)
        - thanh_phan_vector_*: thành phần vector chỉ phương (x, y, z)
        - van_toc: vận tốc chuyển động (m/s)
        - thoi_gian: thời gian chuyển động (giây)
        - do_dai_vector: độ dài vector chỉ phương |u|
        - he_so_don_vi: hệ số k = v/|u| (tỉ lệ chuyển động mỗi giây)
        - vi_tri_sau_*: tọa độ vật sau thời gian t (x, y, z)
        - khoang_cach_tinh_toan: khoảng cách thực tế giữa vật và người quan sát
        - khoang_cach_lam_tron: khoảng cách làm tròn đến 0.1m
        """
        
        # Đảm bảo parameters đã được sinh ra
        if not hasattr(self, 'parameters') or not self.parameters:
            self.parameters = self.generate_parameters()
            
        cac_tham_so = self.parameters
        diem_xuat_phat_x, diem_xuat_phat_y, diem_xuat_phat_z = cac_tham_so["diem_xuat_phat_x"], cac_tham_so["diem_xuat_phat_y"], cac_tham_so["diem_xuat_phat_z"]
        diem_quan_sat_x, diem_quan_sat_y, diem_quan_sat_z = cac_tham_so["diem_quan_sat_x"], cac_tham_so["diem_quan_sat_y"], cac_tham_so["diem_quan_sat_z"]
        thanh_phan_vector_x, thanh_phan_vector_y, thanh_phan_vector_z = cac_tham_so["vector_chi_phuong_x"], cac_tham_so["vector_chi_phuong_y"], cac_tham_so["vector_chi_phuong_z"]
        van_toc = cac_tham_so["van_toc_chuyen_dong"]
        thoi_gian = cac_tham_so["thoi_gian_chuyen_dong"]

        # Tính độ dài vector chỉ phương và kiểm tra vector hợp lệ
        norm_squared = sp.nsimplify(thanh_phan_vector_x ** 2 + thanh_phan_vector_y ** 2 + thanh_phan_vector_z ** 2)
        do_dai_vector_sym = sp.sqrt(norm_squared)  # độ dài của u theo đơn vị toạ độ
        L_m_per_unit = sp.Integer(self.parameters.get("do_dai_don_vi_met", 1))
        
        if norm_squared == 0:
            raise ValueError("Vector chỉ phương không thể bằng vector không")
        
        # Tính hệ số đơn vị: k = v / (|u| * L) (đơn vị theo toạ độ mỗi giây)
        self._norm_units_exact = do_dai_vector_sym
        self._unit_length_m = L_m_per_unit
        den1 = cast(Any, do_dai_vector_sym * L_m_per_unit)
        self._he_so_exact = sp.nsimplify(sp.Rational(van_toc) / den1)

        # Tính tọa độ vật sau thời gian t: A + k*t*u (symbolic)
        k_sym = self._he_so_exact
        t_sym = sp.Integer(thoi_gian)
        vi_tri_sau_x = sp.nsimplify(sp.Integer(diem_xuat_phat_x) + k_sym * t_sym * sp.Integer(thanh_phan_vector_x))
        vi_tri_sau_y = sp.nsimplify(sp.Integer(diem_xuat_phat_y) + k_sym * t_sym * sp.Integer(thanh_phan_vector_y))
        vi_tri_sau_z = sp.nsimplify(sp.Integer(diem_xuat_phat_z) + k_sym * t_sym * sp.Integer(thanh_phan_vector_z))

        # Tính khoảng cách (symbolic)
        dx = sp.nsimplify(vi_tri_sau_x - sp.Integer(diem_quan_sat_x))
        dy = sp.nsimplify(vi_tri_sau_y - sp.Integer(diem_quan_sat_y))
        dz = sp.nsimplify(vi_tri_sau_z - sp.Integer(diem_quan_sat_z))
        d2_units = sp.nsimplify(dx**2 + dy**2 + dz**2)
        d2_units = sp.simplify(sp.expand(d2_units))
        d_exact = sp.sqrt(d2_units) * L_m_per_unit  # đổi sang mét

        # Lưu kết quả để sử dụng trong generate_solution(), dạng chính xác
        self._ket_qua_tinh_toan = {
            "norm_squared": norm_squared,
            "norm_units_exact": self._norm_units_exact,
            "unit_length_m": self._unit_length_m,
            "he_so_exact": self._he_so_exact,
            "vi_tri_sau_x": vi_tri_sau_x, "vi_tri_sau_y": vi_tri_sau_y, "vi_tri_sau_z": vi_tri_sau_z,
            "dx": dx, "dy": dy, "dz": dz,
            "d2_units_exact": d2_units,
            "d_exact": d_exact,
        }

        # Trả về đáp án dạng số (làm tròn 0.1 m)
        d_numeric = float(sp.N(d_exact, 12))
        d_round = round(d_numeric + 1e-12, 1)
        # Lưu phục vụ lời giải nếu cần
        self._ket_qua_tinh_toan["d_numeric"] = d_numeric
        self._ket_qua_tinh_toan["d_round"] = d_round
        return f"\\({to_decimal_comma(d_round)}\\)"

    def generate_wrong_answers(self) -> List[str]:
        """
        Sinh các đáp án sai dựa trên các lỗi thường gặp
        
        Biến sử dụng:
        - cac_tham_so: dictionary chứa tất cả tham số đầu vào
        - cac_loi_thuong_gap: danh sách các khoảng cách tính sai
        - cac_dap_an_sai_da_format: danh sách đáp án sai đã định dạng LaTeX
        - cac_dap_an_duy_nhat: danh sách đáp án sau khi loại trùng
        
        Các lỗi mô phỏng:
        1. Dùng trực tiếp vận tốc làm hệ số (bỏ qua chuẩn hóa vector)
        2. Quên nhân với thời gian (chỉ di chuyển 1 đơn vị thời gian)
        3. Làm tròn sai (làm tròn thành số nguyên thay vì 0.1)
        """
        
        # Đảm bảo parameters đã được sinh ra
        if not hasattr(self, 'parameters') or not self.parameters:
            self.parameters = self.generate_parameters()
            
        cac_tham_so = self.parameters
        
        # Lấy các tham số và dựng biểu thức symbolic cần thiết
        A = sp.Matrix([
            sp.Integer(cac_tham_so["diem_xuat_phat_x"]),
            sp.Integer(cac_tham_so["diem_xuat_phat_y"]),
            sp.Integer(cac_tham_so["diem_xuat_phat_z"]),
        ])
        B = sp.Matrix([
            sp.Integer(cac_tham_so["diem_quan_sat_x"]),
            sp.Integer(cac_tham_so["diem_quan_sat_y"]),
            sp.Integer(cac_tham_so["diem_quan_sat_z"]),
        ])
        u = sp.Matrix([
            sp.Integer(cac_tham_so["vector_chi_phuong_x"]),
            sp.Integer(cac_tham_so["vector_chi_phuong_y"]),
            sp.Integer(cac_tham_so["vector_chi_phuong_z"]),
        ])
        v = sp.Integer(cac_tham_so["van_toc_chuyen_dong"])
        t = sp.Integer(cac_tham_so["thoi_gian_chuyen_dong"])
        norm_u = sp.sqrt(u.dot(u))
        norm_den = cast(Any, norm_u)
        k = sp.nsimplify(sp.Rational(v) / norm_den)
        A_t = sp.nsimplify(A + k * t * u)
        delta = sp.nsimplify(A_t - B)
        D_correct = sp.sqrt(sp.nsimplify(delta.dot(delta)))

        # Các phương án sai có chủ đích và không quá cực đoan
        wrong_exprs = []

        # Sai 1: Dùng "chuẩn hóa" theo L1-norm thay vì L2
        vx = cac_tham_so["vector_chi_phuong_x"]
        vy = cac_tham_so["vector_chi_phuong_y"]
        vz = cac_tham_so["vector_chi_phuong_z"]
        l1 = sp.Integer(abs(vx) + abs(vy) + abs(vz))
        denom_l1 = (l1 if l1 != 0 else sp.Integer(1))
        denom_l1_any = cast(Any, denom_l1)
        k_l1 = sp.nsimplify(sp.Rational(v) / denom_l1_any)
        A1 = sp.nsimplify(A + k_l1 * t * u)
        delta1 = sp.nsimplify(A1 - B)
        D1 = sp.sqrt(sp.nsimplify(delta1.dot(delta1)))
        wrong_exprs.append(D1)

        # Sai 2: Quên bình phương một thành phần trong khoảng cách (bỏ z^2)
        D2_sq = sp.nsimplify((A_t[0]-B[0])**2 + (A_t[1]-B[1])**2 + sp.Abs(A_t[2]-B[2]))
        D2 = sp.sqrt(D2_sq)
        wrong_exprs.append(D2)

        # Sai 3: Khoảng cách Manhattan
        t1 = cast(Any, sp.Abs(A_t[0]-B[0]))
        t2 = cast(Any, sp.Abs(A_t[1]-B[1]))
        t3 = cast(Any, sp.Abs(A_t[2]-B[2]))
        D3 = sp.nsimplify(t1 + t2 + t3)
        wrong_exprs.append(D3)

        # Sai 4: Quên nhân với thời gian
        A4 = sp.nsimplify(A + k * u)
        delta4 = sp.nsimplify(A4 - B)
        D4 = sp.sqrt(sp.nsimplify(delta4.dot(delta4)))
        wrong_exprs.append(D4)

        # Trả về đáp án số (làm tròn 0.1 m)
        correct_val = float(sp.N(D_correct * sp.Integer(self.parameters.get("do_dai_don_vi_met", 1)), 12))
        correct_round = round(correct_val + 1e-12, 1)
        seen_vals: set = {correct_round}
        out_vals: List[float] = []
        for expr in wrong_exprs:
            val = float(sp.N(expr * sp.Integer(self.parameters.get("do_dai_don_vi_met", 1)), 12))
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
        return [f"\\({to_decimal_comma(v)}\\)" for v in out_vals[:3]]

    def generate_question_text(self) -> str:
        """
        Tạo văn bản câu hỏi dạng LaTeX
        
        Biến sử dụng:
        - cac_tham_so: dictionary chứa tất cả tham số đầu vào
        - kich_ban: thông tin kịch bản (địa điểm, đối tượng, vai trò người quan sát)
        
        Return: Chuỗi văn bản câu hỏi hoàn chỉnh với định dạng LaTeX
        """
        
        cac_tham_so = self.parameters
        kich_ban = cac_tham_so["kich_ban"]
        
        return (
            f"Tại một vị trí cụ thể ở {kich_ban['location']} người ta đặt cố định một hệ trục tọa độ \\( Oxyz \\), mỗi đơn vị trên mỗi trục có độ dài bằng {cac_tham_so['do_dai_don_vi_met']} mét. "
            f"{kich_ban['observer_role'].capitalize()} đứng cố định tại vị trí \\({kich_ban['observer_label']}({cac_tham_so['diem_quan_sat_x']}; {cac_tham_so['diem_quan_sat_y']}; {cac_tham_so['diem_quan_sat_z']})\\), quan sát một {kich_ban['object_name']} xuất phát từ điểm "
            f"\\({kich_ban['start_label']}({cac_tham_so['diem_xuat_phat_x']}; {cac_tham_so['diem_xuat_phat_y']}; {cac_tham_so['diem_xuat_phat_z']})\\), chuyển động thẳng đều theo hướng của vectơ \\( \\vec{{u}}({cac_tham_so['vector_chi_phuong_x']}; {cac_tham_so['vector_chi_phuong_y']}; {cac_tham_so['vector_chi_phuong_z']}) \\) với vận tốc {cac_tham_so['van_toc_chuyen_dong']} mét/giây. "
            f"Hỏi sau {cac_tham_so['thoi_gian_chuyen_dong']} giây kể từ lúc xuất phát, khoảng cách giữa {kich_ban['object_name']} và người quan sát bằng bao nhiêu mét? (Làm tròn kết quả đến hàng phần mười, tức 0,1 m)."
        )

    def generate_solution(self) -> str:
        """
        Tạo lời giải chi tiết cho bài toán chuyển động 3D
        
        Biến sử dụng:
        - cac_tham_so: dictionary chứa tất cả tham số đầu vào
        - ket_qua_tinh_toan: dictionary chứa kết quả tính toán từ calculate_answer()
        - kich_ban: thông tin kịch bản câu chuyện
        - cac_bien_tam_thoi: các biến tạm để lưu trữ tham số và kết quả
        - dinh_dang_so: hàm local để định dạng số đẹp
        - loi_giai_hoan_chinh: chuỗi LaTeX chứa lời giải từng bước
        
        Return: Chuỗi lời giải hoàn chỉnh với định dạng LaTeX
        """
        
        cac_tham_so = self.parameters
        if not hasattr(self, '_ket_qua_tinh_toan'):
            self.calculate_answer()  # Tính toán nếu chưa có kết quả
            
        ket_qua_tinh_toan = self._ket_qua_tinh_toan
        kich_ban = cac_tham_so['kich_ban']
        
        # Lấy các tham số đầu vào
        diem_xuat_phat_x, diem_xuat_phat_y, diem_xuat_phat_z = cac_tham_so['diem_xuat_phat_x'], cac_tham_so['diem_xuat_phat_y'], cac_tham_so['diem_xuat_phat_z']
        diem_quan_sat_x, diem_quan_sat_y, diem_quan_sat_z = cac_tham_so['diem_quan_sat_x'], cac_tham_so['diem_quan_sat_y'], cac_tham_so['diem_quan_sat_z']
        thanh_phan_vector_x, thanh_phan_vector_y, thanh_phan_vector_z = cac_tham_so['vector_chi_phuong_x'], cac_tham_so['vector_chi_phuong_y'], cac_tham_so['vector_chi_phuong_z']
        van_toc = cac_tham_so['van_toc_chuyen_dong']
        thoi_gian = cac_tham_so['thoi_gian_chuyen_dong']
        
        # Lấy các kết quả tính toán (symbolic và số)
        vi_tri_sau_x, vi_tri_sau_y, vi_tri_sau_z = ket_qua_tinh_toan['vi_tri_sau_x'], ket_qua_tinh_toan['vi_tri_sau_y'], ket_qua_tinh_toan['vi_tri_sau_z']
        norm_squared = ket_qua_tinh_toan['norm_squared']
        norm_units_exact = ket_qua_tinh_toan['norm_units_exact']
        unit_length_m = ket_qua_tinh_toan['unit_length_m']
        he_so_exact = ket_qua_tinh_toan['he_so_exact']
        dx, dy, dz = ket_qua_tinh_toan['dx'], ket_qua_tinh_toan['dy'], ket_qua_tinh_toan['dz']
        d2_units_exact = ket_qua_tinh_toan['d2_units_exact']
        sqrt_units_display = latex_sqrt_sum_of_squares(dx, dy, dz)

        # Chuyển các biểu thức sang LaTeX để tránh xuất hiện "/" và "sqrt(...)"
        norm_units_ltx = sp.latex(norm_units_exact)
        unit_length_ltx = sp.latex(unit_length_m)
        norm_meters_ltx = sp.latex(sp.nsimplify(norm_units_exact * unit_length_m))
        he_so_exact_ltx = sp.latex(he_so_exact)
        vi_tri_sau_x_ltx = sp.latex(vi_tri_sau_x)
        vi_tri_sau_y_ltx = sp.latex(vi_tri_sau_y)
        vi_tri_sau_z_ltx = sp.latex(vi_tri_sau_z)
        d_round = ket_qua_tinh_toan.get('d_round')
        if d_round is None:
            d_round = round(float(sp.N(sp.sqrt(d2_units_exact) * unit_length_m, 12)) + 1e-12, 1)

        loi_giai_hoan_chinh = fr"""
Bước 1: Trong 1 giây {kich_ban['object_name']} đi được bao nhiêu đơn vị của véc tơ \(\vec u\)?
Ở hệ trục này, mỗi 1 đơn vị ứng với {unit_length_ltx} m. Do đó
\( \|\vec u\|_{{đv}} = \sqrt{{{thanh_phan_vector_x}^2 + {thanh_phan_vector_y}^2 + {thanh_phan_vector_z}^2}} = \sqrt{{{norm_squared}}} = {norm_units_ltx} \),
và \( \|\vec u\|_{{m}} = {unit_length_ltx}\,\cdot\,{norm_units_ltx} = {norm_meters_ltx} \).
Vì tốc độ là {cac_tham_so['van_toc_chuyen_dong']} m/s nên trong 1 giây đi được \( k = \dfrac{{v}}{{\|\vec u\|_{{m}}}} = \dfrac{{{cac_tham_so['van_toc_chuyen_dong']}}}{{{norm_meters_ltx}}} = {he_so_exact_ltx} \) lần \(\vec u\).

Bước 2: Lập biểu thức tọa độ của {kich_ban['object_name']} sau \(t\) giây.
\( A(t) = A + t \cdot k \cdot \vec u \).

Bước 3: Thay \( t = {thoi_gian} \) vào công thức trên:
\( A_{{{thoi_gian}}} = ({diem_xuat_phat_x}; {diem_xuat_phat_y}; {diem_xuat_phat_z}) + {thoi_gian} \cdot {he_so_exact_ltx} \cdot ({thanh_phan_vector_x}; {thanh_phan_vector_y}; {thanh_phan_vector_z}) = ({vi_tri_sau_x_ltx}; {vi_tri_sau_y_ltx}; {vi_tri_sau_z_ltx}) \).

Bước 4: Tính độ dài khoảng cách giữa người quan sát và {kich_ban['object_name']}.
Tọa độ người quan sát là \( {kich_ban['observer_label']}({diem_quan_sat_x}; {diem_quan_sat_y}; {diem_quan_sat_z}) \). Khoảng cách (đơn vị mét) tại thời điểm đó:
\( d = {unit_length_ltx}\,\cdot\,{sqrt_units_display} \approx {to_decimal_comma(d_round)}\,\text{{m}} \).

Kết luận: Sau {thoi_gian} giây, khoảng cách giữa {kich_ban['object_name']} và người quan sát là khoảng \( {to_decimal_comma(d_round)} \) mét.
"""
        return loi_giai_hoan_chinh



# Cập nhật hàm trả về dạng toán để bao gồm lớp mới
def get_available_question_types():  # type: ignore[override]
    return [
        MotionDistance3DQuestion,
        #MotionFromTwoPointsQuestion,
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
