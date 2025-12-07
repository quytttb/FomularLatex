"""
Dạng toán tối ưu: Tối thiểu T = MA + MO với M thuộc mặt phẳng (P)

Bài toán: Cho mặt phẳng (P): Ax + By + Cz + D = 0, hai điểm A(x_A, y_A, z_A), O(x_O, y_O, z_O).
Tìm điểm M thuộc (P) sao cho T = MA + MO đạt giá trị nhỏ nhất. Sinh tham số ngẫu nhiên.
"""

import logging
import math
import os
import random
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Union
import sympy as sp
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
        # constant term
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


def strip_latex_inline_math(ans: str) -> str:
    if ans.startswith("\\(") and ans.endswith("\\)"):
        return ans[2:-2].strip()
    if ans.startswith("$") and ans.endswith("$"):
        return ans[1:-1].strip()
    return ans


def to_decimal_comma(value: Any) -> str:
    s = str(value)
    return s.replace('.', ',')


def format_decimal_value(expr: Any, decimals: int = 2) -> str:
    numeric = float(sp.N(expr, decimals + 6)) if not isinstance(expr, (int, float)) else float(expr)
    rounded = round(numeric, decimals)
    if math.isclose(rounded, 0.0, abs_tol=10 ** (-(decimals + 2))):
        rounded = 0.0
    return f"{rounded:.{decimals}f}"


@dataclass
class GeneratorConfig:
    seed: Optional[int] = None
    exact_mode: bool = True
    coord_min: int = -2
    coord_max: int = 5
    vector_max_component: int = 3
    time_choices: Tuple[int, ...] = (3, 4, 5, 6, 7, 8)
    # pretty_mode: None | 'normal_line' — chọn O nằm trên pháp tuyến qua A để toạ độ M, O' đẹp
    pretty_mode: Optional[str] = None


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
            # Format 2: câu hỏi + lời giải, đáp án ở cuối mỗi câu
            for question_data in questions_data:
                if isinstance(question_data, tuple):
                    question_content, correct_answer = question_data
                    latex_content += question_content
                    # Thêm đáp án ngay sau mỗi câu hỏi
                    ans = strip_latex_inline_math(correct_answer)
                    ans_comma = to_decimal_comma(ans)
                    latex_content += f"Đáp án: {ans} | {ans_comma}\n\n"
                else:
                    # Fallback cho format cũ
                    latex_content += f"{question_data}\n\n"

        latex_content += "\\end{document}"
        return latex_content


    """Khoảng cách nhỏ nhất giữa hai khinh khí cầu chuyển động vuông góc trong không gian với độ cao không đổi.
    """

# ======================
# Dạng toán MA + MO nhỏ nhất trên (P)
# ======================

class MinSumDistancesOnPlaneQuestion(BaseOptimizationQuestion):
    """
    Tối thiểu hóa T = MA + MO với M thuộc mặt phẳng (P): Ax + By + Cz + D = 0.
    Hai điểm A(x_A, y_A, z_A) và O(x_O, y_O, z_O) cho trước (ngẫu nhiên).

    Lời giải tổng quát (tóm tắt):
    - Nếu f(A)·f(O) < 0 (khác phía hoặc một điểm thuộc (P)) ⇒ T_min = AO, M = AO ∩ (P).
    - Nếu f(A)·f(O) > 0 (cùng phía) ⇒ phản chiếu O qua (P) thành O', T_min = AO', M = AO' ∩ (P).
    """

    DECIMAL_PLACES = 2

    # Danh sách tên điểm có thể random (loại trừ M vì đã dùng cho điểm cần tìm)
    POINT_NAMES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

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
        # Sinh (A,B,C) là pháp tuyến, D và hai điểm A, O trong khoảng nguyên
        cfg = self.config
        low, high = cfg.coord_min, cfg.coord_max
        # Chế độ pretty: đặt O trên pháp tuyến qua A để M = A và O' đối xứng nguyên đẹp
        if getattr(cfg, 'pretty_mode', None) == 'normal_line':
            # Chọn pháp tuyến với chuẩn là số nguyên (3D triple), và A,B,C,D đều ≠ 0
            nice_normals: Tuple[Tuple[int, int, int], ...] = (
                (1, 2, 2),
                (2, 1, 2),
                (2, 2, 1),
            )
            Aco, Bco, Cco = random.choice(nice_normals)
            # Chọn A nguyên nhỏ sao cho D = -<n,A> ≠ 0
            attempts = 0
            while True:
                xA, yA, zA = (
                    random.randint(max(-2, low), min(2, high)),
                    random.randint(max(-2, low), min(2, high)),
                    random.randint(max(-2, low), min(2, high)),
                )
                dot_val = Aco*xA + Bco*yA + Cco*zA
                if dot_val != 0:
                    break
                attempts += 1
                if attempts > 50:
                    # fallback đổi normal để thoát
                    Aco, Bco, Cco = random.choice(nice_normals)
            Dco = -dot_val
            # Chọn O = A + k n với k nhỏ để O nguyên, k ≠ 0
            k = random.choice([1, 2])
            xO, yO, zO = (xA + k*Aco, yA + k*Bco, zA + k*Cco)
            return {
                "A": Aco, "B": Bco, "C": Cco, "D": Dco,
                "xA": xA, "yA": yA, "zA": zA,
                "xO": xO, "yO": yO, "zO": zO,
                "point1_name": random.choice(self.POINT_NAMES),
                "point2_name": random.choice([p for p in self.POINT_NAMES if p != 'A'])
            }

        # Mặc định: ngẫu nhiên, đảm bảo từng hệ số A, B, C, D đều khác 0
        def _rand_nonzero(lo: int, hi: int) -> int:
            while True:
                v = random.randint(lo, hi)
                if v != 0:
                    return v
        A = _rand_nonzero(low, high)
        B = _rand_nonzero(low, high)
        C = _rand_nonzero(low, high)
        D = _rand_nonzero(low - 2, high + 2)
        xA, yA, zA = self._random_point(low, high)
        xO, yO, zO = self._random_point(low, high)

        # Tránh trường hợp A và O trùng nhau
        if (xA, yA, zA) == (xO, yO, zO):
            xO, yO, zO = self._random_point(low, high)

        # Random tên điểm (chọn 2 tên khác nhau)
        point_names = random.sample(self.POINT_NAMES, 2)
        point1_name, point2_name = point_names[0], point_names[1]

        return {
            "A": A, "B": B, "C": C, "D": D,
            "xA": xA, "yA": yA, "zA": zA,
            "xO": xO, "yO": yO, "zO": zO,
            "point1_name": point1_name,
            "point2_name": point2_name,
        }

    @staticmethod
    def _dot_plane(a: int, b: int, c: int, d: int, x: int, y: int, z: int) -> sp.Expr:
        return sp.Integer(a)*x + sp.Integer(b)*y + sp.Integer(c)*z + sp.Integer(d)  # type: ignore

    @staticmethod
    def _norm(vec: Tuple[sp.Expr, sp.Expr, sp.Expr]) -> sp.Expr:
        vx, vy, vz = vec
        return sp.sqrt(sp.simplify(vx**2 + vy**2 + vz**2))  # type: ignore

    def _compute_core(self) -> Dict[str, Any]:
        """Tính toán toàn bộ đại lượng cần thiết cho đáp án và lời giải."""
        p = self.parameters
        A, B, C, D = p["A"], p["B"], p["C"], p["D"]
        xA, yA, zA = p["xA"], p["yA"], p["zA"]
        xO, yO, zO = p["xO"], p["yO"], p["zO"]

        # Các biểu thức Sympy để tính chính xác
        fA = self._dot_plane(A, B, C, D, xA, yA, zA)
        fO = self._dot_plane(A, B, C, D, xO, yO, zO)
        n2 = sp.Integer(A)**2 + sp.Integer(B)**2 + sp.Integer(C)**2  # type: ignore
        n_norm = sp.sqrt(sp.simplify(n2))

        AO_vec = (sp.Integer(xO - xA), sp.Integer(yO - yA), sp.Integer(zO - zA))
        AO_len = self._norm(AO_vec)

        # Phân loại phía (kể cả trường hợp tích bằng 0 ⇒ có giao trên (P))
        product_value = int(fA) * int(fO)
        different_or_touch = product_value <= 0

        # Giao điểm AO với (P)
        denom_t = sp.Integer(A)*(xO - xA) + sp.Integer(B)*(yO - yA) + sp.Integer(C)*(zO - zA)
        t_on_AO = None
        M_on_AO = None
        if denom_t != 0:
            t_on_AO = sp.nsimplify(-fA / denom_t)
            M_on_AO = (
                sp.nsimplify(xA + t_on_AO*(xO - xA)),
                sp.nsimplify(yA + t_on_AO*(yO - yA)),
                sp.nsimplify(zA + t_on_AO*(zO - zA)),
            )

        # Phản chiếu O qua (P): O' = O - 2 f(O)/||n||^2 * n
        O_ref = (
            sp.nsimplify(xO - 2*fO*A/n2),  # type: ignore
            sp.nsimplify(yO - 2*fO*B/n2),  # type: ignore
            sp.nsimplify(zO - 2*fO*C/n2),  # type: ignore
        )
        AO_ref_vec = (
            sp.nsimplify(O_ref[0] - xA),
            sp.nsimplify(O_ref[1] - yA),
            sp.nsimplify(O_ref[2] - zA),
        )
        AO_ref_len = self._norm(AO_ref_vec)

        # Giao điểm AO' với (P)
        denom_t2 = sp.Integer(A)*(O_ref[0] - xA) + sp.Integer(B)*(O_ref[1] - yA) + sp.Integer(C)*(O_ref[2] - zA)
        t_on_AO_ref = None
        M_on_AO_ref = None
        if denom_t2 != 0:
            t_on_AO_ref = sp.nsimplify(-fA / denom_t2)
            M_on_AO_ref = (
                sp.nsimplify(xA + t_on_AO_ref*(O_ref[0] - xA)),
                sp.nsimplify(yA + t_on_AO_ref*(O_ref[1] - yA)),
                sp.nsimplify(zA + t_on_AO_ref*(O_ref[2] - zA)),
            )

        # Khoảng cách tới (P) (phục vụ phương án nhiễu)
        dist_A_to_P = sp.nsimplify(sp.Abs(fA) / n_norm)  # type: ignore
        dist_O_to_P = sp.nsimplify(sp.Abs(fO) / n_norm)  # type: ignore

        return {
            "fA": fA, "fO": fO, "n2": n2, "n_norm": n_norm,
            "AO_len": AO_len,
            "different_or_touch": different_or_touch,
            "t_on_AO": t_on_AO, "M_on_AO": M_on_AO,
            "O_ref": O_ref, "AO_ref_len": AO_ref_len,
            "t_on_AO_ref": t_on_AO_ref, "M_on_AO_ref": M_on_AO_ref,
            "dist_A_to_P": dist_A_to_P, "dist_O_to_P": dist_O_to_P,
        }

    def calculate_answer(self) -> str:
        core = self._compute_core()
        # Xác định T_min và điểm M đạt cực trị
        if core["different_or_touch"]:
            T_min = core["AO_len"]
            M = core.get("M_on_AO")
            if M is None:
                # Thử dựng lại M = A + t(AO), t = -f(A)/<n,AO>
                p = self.parameters
                Aco, Bco, Cco, Dco = p["A"], p["B"], p["C"], p["D"]
                xA, yA, zA = p["xA"], p["yA"], p["zA"]
                xO, yO, zO = p["xO"], p["yO"], p["zO"]
                denom = sp.Integer(Aco)*(xO - xA) + sp.Integer(Bco)*(yO - yA) + sp.Integer(Cco)*(zO - zA)
                if denom != 0:
                    t = sp.nsimplify(-core["fA"] / denom)
                    M = (
                        sp.nsimplify(xA + t*(xO - xA)),
                        sp.nsimplify(yA + t*(yO - yA)),
                        sp.nsimplify(zA + t*(zO - zA)),
                    )
                else:
                    # Degenerate: chọn M = A (A ∈ (P))
                    M = (sp.Integer(xA), sp.Integer(yA), sp.Integer(zA))
        else:
            T_min = core["AO_ref_len"]
            M = core.get("M_on_AO_ref")
            if M is None:
                # Dựng lại bằng A + t(AO'), O' trong core
                p = self.parameters
                Aco, Bco, Cco = p["A"], p["B"], p["C"]
                xA, yA, zA = p["xA"], p["yA"], p["zA"]
                Oxp, Oyp, Ozp = core["O_ref"]
                denom = sp.Integer(Aco)*(Oxp - xA) + sp.Integer(Bco)*(Oyp - yA) + sp.Integer(Cco)*(Ozp - zA)
                if denom != 0:
                    t = sp.nsimplify(-core["fA"] / denom)
                    M = (
                        sp.nsimplify(xA + t*(Oxp - xA)),
                        sp.nsimplify(yA + t*(Oyp - yA)),
                        sp.nsimplify(zA + t*(Ozp - zA)),
                    )
                else:
                    M = (sp.Integer(xA), sp.Integer(yA), sp.Integer(zA))
        Mx, My, Mz = M
        expr = sp.simplify(Mx + My + Mz + sp.simplify(T_min))
        decimal_value = format_decimal_value(expr, self.DECIMAL_PLACES)
        return f"\\( {decimal_value} \\)"

    def generate_wrong_answers(self) -> List[str]:
        core = self._compute_core()
        wrongs: List[str] = []

        # Xác định T_min đúng, T_alt sai và M đúng/sai để dựng biểu thức a+b+c+T
        p = self.parameters
        xA, yA, zA = p["xA"], p["yA"], p["zA"]
        xO, yO, zO = p["xO"], p["yO"], p["zO"]

        if core["different_or_touch"]:
            T_min = sp.simplify(core["AO_len"])
            T_alt = sp.simplify(core["AO_ref_len"])
            M_true = core.get("M_on_AO")
            if M_true is None:
                Aco, Bco, Cco = p["A"], p["B"], p["C"]
                denom = sp.Integer(Aco)*(xO - xA) + sp.Integer(Bco)*(yO - yA) + sp.Integer(Cco)*(zO - zA)
                if denom != 0:
                    t = sp.nsimplify(-core["fA"] / denom)
                    M_true = (
                        sp.nsimplify(xA + t*(xO - xA)),
                        sp.nsimplify(yA + t*(yO - yA)),
                        sp.nsimplify(zA + t*(zO - zA)),
                    )
                else:
                    M_true = (sp.Integer(xA), sp.Integer(yA), sp.Integer(zA))
            # Sai: dùng T_alt với toạ độ đúng
            sum_M_true = sp.simplify(M_true[0] + M_true[1] + M_true[2])
            wrongs.append(
                f"\\( {format_decimal_value(sp.simplify(sum_M_true + T_alt), self.DECIMAL_PLACES)} \\)"
            )
            # Sai: dùng toạ độ A thay cho M
            sum_A = sp.Integer(xA) + sp.Integer(yA) + sp.Integer(zA)
            wrongs.append(
                f"\\( {format_decimal_value(sp.simplify(sum_A + T_min), self.DECIMAL_PLACES)} \\)"
            )
            # Sai: dùng toạ độ O thay cho M
            sum_O = sp.Integer(xO) + sp.Integer(yO) + sp.Integer(zO)
            wrongs.append(
                f"\\( {format_decimal_value(sp.simplify(sum_O + T_min), self.DECIMAL_PLACES)} \\)"
            )
        else:
            T_min = sp.simplify(core["AO_ref_len"])
            T_alt = sp.simplify(core["AO_len"])
            M_true = core.get("M_on_AO_ref")
            if M_true is None:
                Aco, Bco, Cco = p["A"], p["B"], p["C"]
                Oxp, Oyp, Ozp = core["O_ref"]
                denom = sp.Integer(Aco)*(Oxp - xA) + sp.Integer(Bco)*(Oyp - yA) + sp.Integer(Cco)*(Ozp - zA)
                if denom != 0:
                    t = sp.nsimplify(-core["fA"] / denom)
                    M_true = (
                        sp.nsimplify(xA + t*(Oxp - xA)),
                        sp.nsimplify(yA + t*(Oyp - yA)),
                        sp.nsimplify(zA + t*(Ozp - zA)),
                    )
                else:
                    M_true = (sp.Integer(xA), sp.Integer(yA), sp.Integer(zA))
            sum_M_true = sp.simplify(M_true[0] + M_true[1] + M_true[2])
            # Sai: đúng M nhưng chọn T_alt
            wrongs.append(
                f"\\( {format_decimal_value(sp.simplify(sum_M_true + T_alt), self.DECIMAL_PLACES)} \\)"
            )
            # Sai: toạ độ A
            sum_A = sp.Integer(xA) + sp.Integer(yA) + sp.Integer(zA)
            wrongs.append(
                f"\\( {format_decimal_value(sp.simplify(sum_A + T_min), self.DECIMAL_PLACES)} \\)"
            )
            # Sai: toạ độ O
            sum_O = sp.Integer(xO) + sp.Integer(yO) + sp.Integer(zO)
            wrongs.append(
                f"\\( {format_decimal_value(sp.simplify(sum_O + T_min), self.DECIMAL_PLACES)} \\)"
            )

        # Khử trùng và cắt còn 3 phương án
        unique_wrongs: List[str] = []
        ans = self.calculate_answer()
        for w in wrongs:
            if w != ans and w not in unique_wrongs:
                unique_wrongs.append(w)

        # Dự phòng nếu thiếu
        if len(unique_wrongs) < 3:
            # Pha thêm phương án dựa trên khoảng cách tới (P)
            sum_A = sp.Integer(xA) + sp.Integer(yA) + sp.Integer(zA)
            sum_O = sp.Integer(xO) + sp.Integer(yO) + sp.Integer(zO)
            cand_exprs = [
                sp.simplify(sum_A + core["dist_A_to_P"] + core["dist_O_to_P"]),
                sp.simplify(sum_O + core["dist_A_to_P"] + core["dist_O_to_P"]),
            ]
            for expr in cand_exprs:
                w = f"\\( {format_decimal_value(expr, self.DECIMAL_PLACES)} \\)"
                if w != ans and w not in unique_wrongs:
                    unique_wrongs.append(w)
                if len(unique_wrongs) >= 3:
                    break

        return unique_wrongs[:3]

    def generate_question_text(self) -> str:
        p = self.parameters
        A, B, C, D = p["A"], p["B"], p["C"], p["D"]
        xA, yA, zA = p["xA"], p["yA"], p["zA"]
        xO, yO, zO = p["xO"], p["yO"], p["zO"]
        point1_name = p["point1_name"]
        point2_name = p["point2_name"]

        plane_expr = format_plane_equation_latex(A, B, C, D)
        plane_tex = f"(P): {plane_expr} = 0"
        A_tex = f"{point1_name}({xA};{yA};{zA})"
        O_tex = f"{point2_name}({xO};{yO};{zO})"

        text = (
            f"Cho mặt phẳng \\({plane_tex}\\), hai điểm \\({A_tex}\\), \\({O_tex}\\). Cho \\(M(a;b;c)\\) nằm bất kỳ thuộc mặt phẳng \\((P)\\) . "
            f"\\(T\\) là giá trị nhỏ nhất của biểu thức \\({{M{point1_name} + M{point2_name}}}\\). "
            f"Khi đó biểu thức \\({{a + b + c + T}}\\) bằng?"
        )
        return text

    def generate_solution(self) -> str:
        core = self._compute_core()

        # Lấy giá trị số cụ thể từ đề bài
        p = self.parameters
        A, B, C, D = p["A"], p["B"], p["C"], p["D"]
        xA, yA, zA = p["xA"], p["yA"], p["zA"]
        xO, yO, zO = p["xO"], p["yO"], p["zO"]
        point1_name = p["point1_name"]
        point2_name = p["point2_name"]

        plane_tex = format_plane_equation_latex(A, B, C, D)

        parts: List[str] = []
        parts.append(f"Xét \\(f(x,y,z) = {plane_tex}\\).")
        parts.append(f"\\(f({point1_name}) = {sp.latex(core['fA'])}\\), \\(f({point2_name}) = {sp.latex(core['fO'])}\\).")

        if core["different_or_touch"]:
            parts.append(f"Vì \\(f({point1_name}) \\cdot f({point2_name}) < 0\\) nên {point1_name}, {point2_name} khác phía đối với \\((P)\\).")
            parts.append(f"Đoạn \\({point1_name}{point2_name}\\) cắt \\((P)\\) tại \\(M'\\). Theo bất đẳng thức tam giác: \\(T = M{point1_name} + M{point2_name} \\ge {point1_name}{point2_name}\\).")
            parts.append(f"Dấu = xảy ra khi \\({point1_name}{point2_name} \\cap (P) = M\\).\n")
            parts.append(f"\\(\\Rightarrow T_{{\\min}} = {point1_name}{point2_name} = {sp.latex(sp.simplify(core['AO_len']))}\\).\n")
            parts.append(f"\\(\\Rightarrow {point1_name}; M'; {point2_name}\\) thẳng hàng.")
            if core["M_on_AO"] is not None:
                # M' = A + t * AO, viết toạ độ tuyến tính theo t
                denom_t = sp.Integer(A)*(xO - xA) + sp.Integer(B)*(yO - yA) + sp.Integer(C)*(zO - zA)
                t_val = core["t_on_AO"]  # tham số t trong trình bày dưới
                Mx, My, Mz = core["M_on_AO"]

                dx, dy, dz = (xO - xA), (yO - yA), (zO - zA)
                def lin_coord(c0: int, d: int) -> str:
                    if d == 0:
                        return f"{c0}"
                    sign = "+" if d > 0 else "-"
                    coef = abs(d)
                    if c0 == 0:
                        return f"{coef if coef != 1 else ''}t" if sign == "+" else f"-{coef if coef != 1 else ''}t"
                    return f"{c0} {sign} {'' if coef == 1 else coef}t"

                Mlin_x = lin_coord(xA, dx)
                Mlin_y = lin_coord(yA, dy)
                Mlin_z = lin_coord(zA, dz)

                parts.append(f" \\(\\Leftrightarrow \\overrightarrow{{{point1_name}M'}} = t\\,\\overrightarrow{{{point1_name}{point2_name}}}\\) với \\(t \\in \\mathbb{{R}}\\).")
                parts.append(f"\\(\\Leftrightarrow M' = {point1_name} + t\\,\\overrightarrow{{{point1_name}{point2_name}}}\\)")
                parts.append(f"\\(\\Leftrightarrow M' = ( {Mlin_x}; {Mlin_y}; {Mlin_z} )\\).")
                # Dùng format_plane_equation_latex để trình bày vế trái gọn đẹp rồi thế x,y,z bằng toạ độ M'
                plane_expr_tmpl = format_plane_equation_latex(A, B, C, D)  # ví dụ: '2x - 3y + z + 4'
                expr_at_Mh = (
                    plane_expr_tmpl
                    .replace("x", f"({Mlin_x})")
                    .replace("y", f"({Mlin_y})")
                    .replace("z", f"({Mlin_z})")
                )
                parts.append(f"Vì \\(M' \\in (P)\\) \\(\\Rightarrow {expr_at_Mh} = 0\\)")
                parts.append(f"\\(\\Leftrightarrow t = -\\dfrac{{{sp.latex(core['fA'])}}}{{{sp.latex(denom_t)}}} = {sp.latex(t_val)}\\).")
                parts.append(f"Vậy \\(M' = ({sp.latex(Mx)}; {sp.latex(My)}; {sp.latex(Mz)})\\).")
        else:
            parts.append(f"Vì \\(f({point1_name}) \\cdot f({point2_name}) > 0\\) nên {point1_name}, {point2_name} cùng phía đối với \\((P)\\).")
            Oxp, Oyp, Ozp = core["O_ref"]
            parts.append(
                f"Phản chiếu \\({point2_name}({xO};{yO};{zO})\\) qua \\((P)\\): \\({point2_name}' = ({sp.latex(Oxp)}; {sp.latex(Oyp)}; {sp.latex(Ozp)})\\)."
            )
            parts.append(f"Từ đó \\(T_{{\\min}} = |{point1_name}{point2_name}'| = {sp.latex(sp.simplify(core['AO_ref_len']))}\\).")
            if core["M_on_AO_ref"] is not None:
                denom_t2 = sp.Integer(A)*(Oxp - xA) + sp.Integer(B)*(Oyp - yA) + sp.Integer(C)*(Ozp - zA)
                t2_val = core["t_on_AO_ref"]
                Mx, My, Mz = core["M_on_AO_ref"]

                # Đồng bộ cách trình bày: tham số hoá với t, viết toạ độ tuyến tính theo t
                parts.append(f"\\(\\Rightarrow {point1_name}; M; {point2_name}'\\) thẳng hàng.")
                parts.append(f" \\((\\Leftrightarrow \\overrightarrow{{{point1_name}M}} = t\\,\\overrightarrow{{{point1_name}{point2_name}'}}\\) với \\(t \\in \\mathbb{{R}}\\).")
                parts.append(f"\\(\\Leftrightarrow M = {point1_name} + t\\,\\overrightarrow{{{point1_name}{point2_name}'}}\\)")

                dx2 = sp.nsimplify(Oxp - xA)
                dy2 = sp.nsimplify(Oyp - yA)
                dz2 = sp.nsimplify(Ozp - zA)
                M2_x = f"{xA}" if dx2 == 0 else f"{xA} + ({sp.latex(dx2)})t"
                M2_y = f"{yA}" if dy2 == 0 else f"{yA} + ({sp.latex(dy2)})t"
                M2_z = f"{zA}" if dz2 == 0 else f"{zA} + ({sp.latex(dz2)})t"
                parts.append(f"\\(\\Leftrightarrow M = ( {M2_x}; {M2_y}; {M2_z} )\\).")

                # Thế vào phương trình (P) bằng biểu thức gọn từ format_plane_equation_latex
                plane_expr_tmpl2 = format_plane_equation_latex(A, B, C, D)
                expr_at_Mh2 = (
                    plane_expr_tmpl2
                    .replace("x", f"({M2_x})")
                    .replace("y", f"({M2_y})")
                    .replace("z", f"({M2_z})")
                )
                parts.append(f"Vì \\(M \\in (P)\\) \\(\\Rightarrow {expr_at_Mh2} = 0\\)")
                parts.append(f"\\(\\Leftrightarrow t = -\\dfrac{{{sp.latex(core['fA'])}}}{{{sp.latex(denom_t2)}}} = {sp.latex(t2_val)}\\).")
                parts.append(f"Vậy \\(M = ({sp.latex(Mx)}; {sp.latex(My)}; {sp.latex(Mz)})\\).")
        
        # Kết luận thống nhất
        parts.append("Kết luận:")
        if core["different_or_touch"]:
            parts.append(f"Vì \\(f({point1_name}) \\cdot f({point2_name}) < 0\\), ta có \\(T_{{\\min}} = |{point1_name}{point2_name}|\\) với \\(M = {point1_name}{point2_name} \\cap (P)\\).")
        else:
            parts.append(f"Vì \\(f({point1_name}) \\cdot f({point2_name}) > 0\\), ta có \\(T_{{\\min}} = |{point1_name}{point2_name}'|\\) với \\(M = {point1_name}{point2_name}' \\cap (P)\\).")

        # Thêm kết luận về a+b+c+T theo cách hỏi mới
        if core["different_or_touch"]:
            T_min_expr = sp.simplify(core["AO_len"])
            M = core.get("M_on_AO")
            if M is None:
                p2 = self.parameters
                Aco, Bco, Cco = p2["A"], p2["B"], p2["C"]
                xA2, yA2, zA2 = p2["xA"], p2["yA"], p2["zA"]
                xO2, yO2, zO2 = p2["xO"], p2["yO"], p2["zO"]
                denom = sp.Integer(Aco)*(xO2 - xA2) + sp.Integer(Bco)*(yO2 - yA2) + sp.Integer(Cco)*(zO2 - zA2)
                if denom != 0:
                    t = sp.nsimplify(-core["fA"] / denom)
                    M = (
                        sp.nsimplify(xA2 + t*(xO2 - xA2)),
                        sp.nsimplify(yA2 + t*(yO2 - yA2)),
                        sp.nsimplify(zA2 + t*(zO2 - zA2)),
                    )
                else:
                    M = (sp.Integer(xA2), sp.Integer(yA2), sp.Integer(zA2))
        else:
            T_min_expr = sp.simplify(core["AO_ref_len"])
            M = core.get("M_on_AO_ref")
            if M is None:
                p2 = self.parameters
                Aco, Bco, Cco = p2["A"], p2["B"], p2["C"]
                xA2, yA2, zA2 = p2["xA"], p2["yA"], p2["zA"]
                Oxp, Oyp, Ozp = core["O_ref"]
                denom = sp.Integer(Aco)*(Oxp - xA2) + sp.Integer(Bco)*(Oyp - yA2) + sp.Integer(Cco)*(Ozp - zA2)
                if denom != 0:
                    t = sp.nsimplify(-core["fA"] / denom)
                    M = (
                        sp.nsimplify(xA2 + t*(Oxp - xA2)),
                        sp.nsimplify(yA2 + t*(Oyp - yA2)),
                        sp.nsimplify(zA2 + t*(Ozp - zA2)),
                    )
                else:
                    M = (sp.Integer(xA2), sp.Integer(yA2), sp.Integer(zA2))
        sum_M = sp.simplify(M[0] + M[1] + M[2])
        total_expr = sp.simplify(sum_M + T_min_expr)
        decimal_total = format_decimal_value(total_expr, self.DECIMAL_PLACES)
        decimal_total_comma = to_decimal_comma(decimal_total)
        parts.append(
            f"Do đó với \\(M(a;b;c)\\) đạt cực trị, \\(a+b+c+T = {decimal_total}\\)"
            f" (hay \\({decimal_total_comma}\\))."
        )
        
        return "\n\n".join(parts)

# Cập nhật hàm trả về dạng toán để bao gồm lớp mới
def get_available_question_types():  # type: ignore[override]
    return [
        MinSumDistancesOnPlaneQuestion,
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
