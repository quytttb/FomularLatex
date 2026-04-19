"""
Hệ thống sinh đề toán về ô tô nhập làn cao tốc
Bài toán: Ô tô tăng tốc nhập làn, tính vận tốc, quãng đường, phanh
Dạng câu hỏi: True/False (4 statements)
"""

import logging
import math
import os
import random
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from fractions import Fraction
from string import Template
from typing import Any, Dict, List, Optional, Tuple

import sympy as sp

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

# ==============================================================================
# CẤU HÌNH VÀ HẰNG SỐ
# ==============================================================================

@dataclass
class GeneratorConfig:
    """Cấu hình cho generator"""
    seed: Optional[int] = None
    exact_mode: bool = True


# 20 giá trị cho d0 (khoảng cách đến điểm nhập làn, m)
D0_VALUES: List[Fraction] = [
    Fraction(180), Fraction(184), Fraction(188), Fraction(192), Fraction(196),
    Fraction(200), Fraction(204), Fraction(208), Fraction(212), Fraction(216),
    Fraction(220), Fraction(224), Fraction(228), Fraction(232), Fraction(236),
    Fraction(240), Fraction(244), Fraction(248), Fraction(252), Fraction(260)
]

# 20 giá trị cho v0 (tốc độ ban đầu, km/h) - chọn bội số của 3.6 để b đẹp
V0_VALUES: List[Fraction] = [
    Fraction(30), Fraction(32), Fraction(33), Fraction(34), Fraction(36),
    Fraction(37), Fraction(38), Fraction(39), Fraction(40), Fraction(41),
    Fraction(42), Fraction(43), Fraction(44), Fraction(45), Fraction(46),
    Fraction(47), Fraction(48), Fraction(50), Fraction(52), Fraction(54)
]

# 20 giá trị cho T1 (thời gian tăng tốc đến nhập làn, s)
T1_VALUES: List[Fraction] = [
    Fraction(10), Fraction(105, 10), Fraction(11), Fraction(115, 10), Fraction(12),
    Fraction(125, 10), Fraction(13), Fraction(135, 10), Fraction(14), Fraction(145, 10),
    Fraction(15), Fraction(155, 10), Fraction(16), Fraction(165, 10), Fraction(17),
    Fraction(175, 10), Fraction(18), Fraction(185, 10), Fraction(19), Fraction(20)
]

# 20 giá trị cho T2 (tổng thời gian tăng tốc, s) - phải > T1
T2_VALUES: List[Fraction] = [
    Fraction(20), Fraction(21), Fraction(22), Fraction(23), Fraction(24),
    Fraction(25), Fraction(26), Fraction(27), Fraction(28), Fraction(29),
    Fraction(30), Fraction(31), Fraction(32), Fraction(33), Fraction(34),
    Fraction(35), Fraction(36), Fraction(37), Fraction(38), Fraction(40)
]

# 20 giá trị cho gia tốc phanh (m/s²) - giá trị âm
A_BRAKE_VALUES: List[Fraction] = [
    Fraction(-2), Fraction(-21, 10), Fraction(-22, 10), Fraction(-23, 10), Fraction(-24, 10),
    Fraction(-25, 10), Fraction(-26, 10), Fraction(-27, 10), Fraction(-28, 10), Fraction(-29, 10),
    Fraction(-3), Fraction(-31, 10), Fraction(-32, 10), Fraction(-33, 10), Fraction(-34, 10),
    Fraction(-35, 10), Fraction(-36, 10), Fraction(-37, 10), Fraction(-38, 10), Fraction(-4)
]

# 20 giá trị cho khoảng cách chướng ngại vật (m)
D_OBSTACLE_VALUES: List[Fraction] = [
    Fraction(280), Fraction(290), Fraction(300), Fraction(310), Fraction(320),
    Fraction(330), Fraction(340), Fraction(350), Fraction(360), Fraction(370),
    Fraction(380), Fraction(390), Fraction(400), Fraction(410), Fraction(420),
    Fraction(430), Fraction(440), Fraction(450), Fraction(460), Fraction(500)
]


# ==============================================================================
# HÀM TIỆN ÍCH
# ==============================================================================

def format_fraction_vn(frac: Fraction) -> str:
    """Format Fraction thành dạng tiếng Việt (dùng dấu phẩy)"""
    if frac.denominator == 1:
        return str(frac.numerator)
    decimal_val = float(frac)
    if decimal_val == int(decimal_val):
        return str(int(decimal_val))
    formatted = f"{decimal_val:.2f}".rstrip('0').rstrip('.')
    return formatted.replace(".", ",")


def to_decimal_comma(value: Any) -> str:
    """Chuyển dấu chấm thành dấu phẩy cho số thập phân"""
    if isinstance(value, Fraction):
        return format_fraction_vn(value)
    s = str(value)
    return s.replace(".", ",")


def format_decimal_vn(val: float, decimals: int = 2) -> str:
    """Format số thập phân với dấu phẩy"""
    formatted = f"{val:.{decimals}f}".rstrip('0').rstrip('.')
    return formatted.replace(".", ",")


def format_fraction_latex(frac: Fraction) -> str:
    """Format Fraction thành LaTeX"""
    if frac.denominator == 1:
        return str(frac.numerator)
    if frac.numerator < 0:
        return rf"-\dfrac{{{-frac.numerator}}}{{{frac.denominator}}}"
    return rf"\dfrac{{{frac.numerator}}}{{{frac.denominator}}}"


# ==============================================================================
# HÀM TÍNH TOÁN VẬT LÝ
# ==============================================================================

def calculate_acceleration_params(d0: float, v0_kmh: float, T1: float) -> Tuple[float, float, float, float]:
    """
    Tính a và b từ điều kiện:
    - v(0) = b = v0 (m/s) = v0_kmh / 3.6
    - Xe chạy đều 2 giây đầu: s_initial = b * 2
    - Quãng đường tăng tốc: d_accel = d0 - s_initial
    - s = ∫₀^T1 (at + b) dt = aT1²/2 + bT1 = d_accel
    => a = 2(d_accel - bT1) / T1²
    """
    b = v0_kmh / 3.6  # Chuyển km/h → m/s
    s_initial = b * 2  # Quãng đường 2 giây đầu chạy đều
    d_accel = d0 - s_initial  # Quãng đường còn lại để tăng tốc
    a = 2 * (d_accel - b * T1) / (T1 ** 2)
    return a, b, s_initial, d_accel


def velocity_at_time(a: float, b: float, t: float) -> float:
    """v(t) = at + b"""
    return a * t + b


def distance_traveled(a: float, b: float, T: float) -> float:
    """s = ∫₀^T (at + b) dt = aT²/2 + bT"""
    return a * T**2 / 2 + b * T


def braking_distance(v_initial: float, a_brake: float) -> float:
    """
    Quãng đường phanh: v² = v₀² + 2as
    Khi v = 0: s = -v₀²/(2a) (a < 0)
    """
    return -v_initial**2 / (2 * a_brake)


def time_to_stop(v_initial: float, a_brake: float) -> float:
    """
    Thời gian phanh: v = v₀ + at
    Khi v = 0: t = -v₀/a
    """
    return -v_initial / a_brake


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

# TikZ để trống theo yêu cầu
TIKZ_DIAGRAM = ""
TIKZ_SOLUTION = ""


TEMPLATE_QUESTION = Template(r"""Một người điều khiển ô tô đang ở đường dẫn muốn nhập làn vào đường cao tốc. Khi ô tô cách điểm nhập làn \(${d0}\) m, tốc độ của ô tô là \(${v0}\) km/h. Hai giây sau đó, ô tô bắt đầu tăng tốc với tốc độ \(v(t) = at + b\) (m/s), trong đó \(a > 0\) và \(t\) là thời gian tính bằng giây kể từ khi bắt đầu tăng tốc. Biết rằng ô tô nhập làn cao tốc sau \(${T1}\) giây tăng tốc và duy trì sự tăng tốc trong \(${T2}\) giây kể từ khi bắt đầu tăng tốc.

${marker_a}a) ${statement_a}

${marker_b}b) ${statement_b}

${marker_c}c) ${statement_c}

${marker_d}d) ${statement_d}
""")


TEMPLATE_SOLUTION = Template(r"""
Lời giải:

Vận tốc ban đầu: \(v_0 = ${v0}\) km/h \(= \dfrac{${v0}}{3,6} = ${b}\) m/s. Vậy \(b = ${b}\) m/s.

Quãng đường 2 giây đầu chạy đều: \(s_0 = ${b} \cdot 2 = ${s_initial}\) m.

Quãng đường còn lại để tăng tốc: \(${d0} - ${s_initial} = ${d_accel}\) m.

Từ \(\displaystyle\int_0^{${T1}} (at + ${b})\, dt = ${d_accel}\):

\[\dfrac{a \cdot ${T1}^2}{2} + ${b} \cdot ${T1} = ${d_accel}\]

\[\Rightarrow a = \dfrac{2 \cdot (${d_accel} - ${bT1})}{${T1_sq}} = ${a}\text{ m/s}^2\]

${sol_a}

${sol_b}

${sol_c}

${sol_d}
""")


# ==============================================================================
# LỚP CƠ SỞ VÀ CÀI ĐẶT
# ==============================================================================

class BaseHighwayMergeQuestion(ABC):
    """Lớp cơ sở cho các bài toán nhập làn cao tốc"""
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.calculated_values: Dict[str, Any] = {}
        self.config = config or GeneratorConfig()
    
    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def calculate_values(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def generate_question_text(self) -> str:
        pass
    
    @abstractmethod
    def generate_solution(self) -> str:
        pass
    
    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.calculated_values = self.calculate_values()
        question_text = self.generate_question_text().strip()
        solution = self.generate_solution().strip()
        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += solution + "\n"
        
        # Return markers for correct answers
        markers = ""
        if self.calculated_values.get("a_correct", False):
            markers += "a"
        if self.calculated_values.get("b_correct", False):
            markers += "b"
        if self.calculated_values.get("c_correct", False):
            markers += "c"
        if self.calculated_values.get("d_correct", False):
            markers += "d"
        
        return question_content, markers
    
    @staticmethod
    def create_latex_document(
        questions_data: List[Tuple[str, str]],
        title: str = "Bài tập Ô tô Nhập làn Cao tốc",
    ) -> str:
        questions_content = "\n\n".join(
            [q_content for q_content, _ in questions_data]
        )
        
        latex_document = rf"""\documentclass[a4paper,12pt]{{article}}
\usepackage{{amsmath, amsfonts, amssymb}}
\usepackage{{geometry}}
\geometry{{a4paper, margin=1in}}
\usepackage{{fontspec}}
\usepackage{{polyglossia}}
\setmainlanguage{{vietnamese}}
\setmainfont{{Times New Roman}}
\usepackage{{tikz}}
\usetikzlibrary{{calc}}

\title{{{title}}}
\author{{Generator}}
\date{{\today}}

\begin{{document}}
\maketitle

{questions_content}

\end{{document}}
"""
        return latex_document


class HighwayMergeQuestion(BaseHighwayMergeQuestion):
    """Bài toán ô tô nhập làn cao tốc"""
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên với ràng buộc a > 0 và d_stop > 0"""
        max_attempts = 1000
        for _ in range(max_attempts):
            d0 = random.choice(D0_VALUES)
            v0 = random.choice(V0_VALUES)
            T1 = random.choice(T1_VALUES)

            valid_T2 = [t for t in T2_VALUES if t > T1]
            if not valid_T2:
                continue
            T2 = random.choice(valid_T2)

            b_frac = v0 * Fraction(5, 18)
            s_initial_frac = b_frac * 2
            d_accel_frac = d0 - s_initial_frac
            a_frac = 2 * (d_accel_frac - b_frac * T1) / (T1 ** 2)

            if a_frac <= 0:
                continue

            a_brake = random.choice(A_BRAKE_VALUES)
            d_obstacle = random.choice(D_OBSTACLE_VALUES)

            v_T2_frac = a_frac * T2 + b_frac
            s_brake_frac = v_T2_frac ** 2 / (2 * abs(a_brake))
            d_stop_frac = d_obstacle - s_brake_frac

            if d_stop_frac <= 0:
                continue

            return {
                "d0": d0, "v0": v0, "T1": T1, "T2": T2,
                "a_brake": a_brake, "d_obstacle": d_obstacle,
            }

        raise ValueError("Không tìm được bộ tham số hợp lệ (a > 0, d_stop > 0) sau nhiều lần thử")
    
    def calculate_values(self) -> Dict[str, Any]:
        """Tính toán các giá trị (dùng Fraction cho giá trị chính xác)"""
        params = self.parameters

        d0 = params["d0"]
        v0 = params["v0"]
        T1 = params["T1"]
        T2 = params["T2"]
        a_brake = params["a_brake"]
        d_obstacle = params["d_obstacle"]

        b_frac = v0 * Fraction(5, 18)
        s_initial_frac = b_frac * 2
        d_accel_frac = d0 - s_initial_frac
        a_frac = 2 * (d_accel_frac - b_frac * T1) / (T1 ** 2)

        v_at_T1_frac = a_frac * T1 + b_frac
        v_at_T2_frac = a_frac * T2 + b_frac

        s_T1_frac = a_frac * T1 ** 2 / 2 + b_frac * T1
        s_T2_frac = a_frac * T2 ** 2 / 2 + b_frac * T2

        s_brake_frac = v_at_T2_frac ** 2 / (2 * abs(a_brake))
        d_stop_frac = d_obstacle - s_brake_frac

        a_correct = random.choice([True, False])
        b_correct = random.choice([True, False])
        c_correct = random.choice([True, False])
        d_correct = random.choice([True, False])

        return {
            "a_frac": a_frac, "b_frac": b_frac,
            "a": float(a_frac), "b": float(b_frac),
            "s_initial_frac": s_initial_frac,
            "d_accel_frac": d_accel_frac,
            "s_initial": float(s_initial_frac),
            "d_accel": float(d_accel_frac),
            "v_at_T1": float(v_at_T1_frac),
            "v_at_T2": float(v_at_T2_frac),
            "v_at_T2_frac": v_at_T2_frac,
            "s_T1": float(s_T1_frac),
            "s_T2": float(s_T2_frac),
            "s_T2_frac": s_T2_frac,
            "s_brake": float(s_brake_frac),
            "s_brake_frac": s_brake_frac,
            "d_stop": float(d_stop_frac),
            "d_stop_frac": d_stop_frac,
            "a_correct": a_correct,
            "b_correct": b_correct,
            "c_correct": c_correct,
            "d_correct": d_correct,
        }
    
    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        params = self.parameters
        calc = self.calculated_values

        marker_a = "*" if calc["a_correct"] else ""
        marker_b = "*" if calc["b_correct"] else ""
        marker_c = "*" if calc["c_correct"] else ""
        marker_d = "*" if calc["d_correct"] else ""

        # Statement a: Phanh và dừng cách chướng ngại vật X m
        d_stop_correct = calc["d_stop"]
        if calc["a_correct"]:
            d_stop_shown = round(d_stop_correct, 2)
        else:
            d_stop_shown = round(d_stop_correct * random.choice([0.7, 1.3, 1.5]), 2)

        T2_display = format_fraction_vn(params["T2"])
        time_maintain = 5
        statement_a = (
            f"Sau {T2_display} giây kể từ khi tăng tốc, "
            f"ô tô duy trì tốc độ cao nhất trong vòng {time_maintain} giây thì phát hiện chướng ngại vật "
            f"cách đó {format_fraction_vn(params['d_obstacle'])} m, người điều khiển lập tức đạp phanh "
            f"và ô tô chuyển động chậm dần đều với \\(a(t) = {format_decimal_vn(float(params['a_brake']))}\\) m/s². "
            f"Khi đó ô tô dừng lại cách chướng ngại vật {format_decimal_vn(d_stop_shown)} m."
        )

        # Statement b: Công thức tích phân (dùng phân số chính xác khi đúng)
        T1_display = format_fraction_vn(params["T1"])
        if calc["b_correct"]:
            coef_shown = format_fraction_latex(calc["a_frac"])
            b_shown_in_formula = format_fraction_latex(calc["b_frac"])
        else:
            wrong_a_val = round(calc["a"] * random.choice([0.8, 1.2]), 2)
            coef_shown = format_decimal_vn(wrong_a_val)
            b_shown_in_formula = str(round(calc["b"]))

        statement_b = (
            f"Quãng đường (đơn vị: mét) ô tô đi được từ khi tăng tốc đến khi nhập làn được tính theo công thức "
            f"\\(s = \\displaystyle\\int_0^{{{T1_display}}} ({coef_shown}t + {b_shown_in_formula})\\, dt\\)."
        )

        # Statement c: Quãng đường T2 giây kể từ khi bắt đầu tăng tốc (CHỈ tính s_T2)
        s_T2_correct = calc["s_T2"]
        s_T2_frac = calc["s_T2_frac"]
        if calc["c_correct"]:
            if s_T2_frac.denominator == 1:
                s_shown = str(s_T2_frac.numerator)
            else:
                s_shown = format_decimal_vn(s_T2_correct, 2)
        else:
            s_shown = str(round(s_T2_correct * random.choice([0.85, 1.15])))

        statement_c = (
            f"Quãng đường mà ô tô đi được trong thời gian {format_fraction_vn(params['T2'])} giây "
            f"kể từ khi bắt đầu tăng tốc là {s_shown} m."
        )

        # Statement d: Giá trị của b (dùng phân số chính xác khi đúng)
        if calc["d_correct"]:
            b_shown_latex = format_fraction_latex(calc["b_frac"])
        else:
            wrong_b = round(calc["b"] * random.choice([0.8, 1.2]))
            b_shown_latex = str(wrong_b)

        statement_d = f"Giá trị của \\(b\\) là \\({b_shown_latex}\\)."

        return TEMPLATE_QUESTION.substitute(
            d0=format_fraction_vn(params["d0"]),
            v0=format_fraction_vn(params["v0"]),
            T1=format_fraction_vn(params["T1"]),
            T2=format_fraction_vn(params["T2"]),
            marker_a=marker_a,
            marker_b=marker_b,
            marker_c=marker_c,
            marker_d=marker_d,
            statement_a=statement_a,
            statement_b=statement_b,
            statement_c=statement_c,
            statement_d=statement_d,
        )
    
    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết"""
        params = self.parameters
        calc = self.calculated_values

        a_frac = calc["a_frac"]
        b_frac = calc["b_frac"]
        s_initial_frac = calc["s_initial_frac"]
        d_accel_frac = calc["d_accel_frac"]
        v_T2_frac = calc["v_at_T2_frac"]
        s_T2_frac = calc["s_T2_frac"]

        T1 = params["T1"]
        T2 = params["T2"]
        T1_str = format_fraction_vn(T1)
        T2_str = format_fraction_vn(T2)

        bT1_frac = b_frac * T1
        T1_sq_frac = T1 ** 2

        # sol_a: Vận tốc MAX và phanh
        sol_a = f"a) {'Đúng' if calc['a_correct'] else 'Sai'}.\n\n"
        sol_a += (
            f"Vận tốc MAX (tại t = {T2_str}s): "
            f"\\(v({T2_str}) = {format_fraction_latex(a_frac)} \\cdot {T2_str} + {format_fraction_latex(b_frac)} "
            f"= {format_fraction_latex(v_T2_frac)} \\approx {format_decimal_vn(calc['v_at_T2'])}\\) m/s.\n\n"
        )
        sol_a += (
            f"Quãng đường phanh: \\(s = \\dfrac{{v^2}}{{2|a|}} = "
            f"\\dfrac{{{format_decimal_vn(calc['v_at_T2'])}^2}}{{2 \\cdot {format_fraction_vn(abs(params['a_brake']))}}} "
            f"\\approx {format_decimal_vn(calc['s_brake'])}\\) m.\n\n"
        )
        sol_a += (
            f"Khoảng cách dừng: \\({format_fraction_vn(params['d_obstacle'])} - {format_decimal_vn(calc['s_brake'])} "
            f"\\approx {format_decimal_vn(calc['d_stop'])}\\) m."
        )

        # sol_b: Tích phân cho d_accel
        sol_b = f"b) {'Đúng' if calc['b_correct'] else 'Sai'}.\n\n"
        sol_b += (
            f"Công thức đúng: \\(s = \\displaystyle\\int_0^{{{T1_str}}} "
            f"({format_fraction_latex(a_frac)}t + {format_fraction_latex(b_frac)})\\, dt "
            f"= {format_fraction_latex(d_accel_frac)}\\) m."
        )

        # sol_c: Quãng đường T2 giây kể từ khi bắt đầu tăng tốc (CHỈ s_T2)
        sol_c = f"c) {'Đúng' if calc['c_correct'] else 'Sai'}.\n\n"
        sol_c += (
            f"Quãng đường tăng tốc {T2_str}s: "
            f"\\(\\displaystyle\\int_0^{{{T2_str}}} "
            f"({format_fraction_latex(a_frac)}t + {format_fraction_latex(b_frac)})\\, dt "
            f"= {format_fraction_latex(s_T2_frac)}\\) m."
        )

        # sol_d: Giá trị b (phân số chính xác)
        sol_d = f"d) {'Đúng' if calc['d_correct'] else 'Sai'}.\n\n"
        sol_d += (
            f"\\(b = \\dfrac{{{format_fraction_vn(params['v0'])}}}{{3,6}} "
            f"= {format_fraction_latex(b_frac)}\\) m/s."
        )

        return TEMPLATE_SOLUTION.substitute(
            d0=format_fraction_latex(params["d0"]),
            v0=format_fraction_vn(params["v0"]),
            T1=T1_str,
            T2=T2_str,
            T1_sq=format_fraction_latex(T1_sq_frac),
            a=format_fraction_latex(a_frac),
            b=format_fraction_latex(b_frac),
            bT1=format_fraction_latex(bT1_frac),
            s_initial=format_fraction_latex(s_initial_frac),
            d_accel=format_fraction_latex(d_accel_frac),
            sol_a=sol_a,
            sol_b=sol_b,
            sol_c=sol_c,
            sol_d=sol_d,
        )


# ==============================================================================
# HÀM MAIN
# ==============================================================================

def main():
    """
    Hàm main để chạy generator
    Usage: python highway_merge_questions.py <num_questions> [seed]
    """
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else None
        
        if seed is None:
            seed = os.environ.get("OPT_SEED")
            if seed:
                seed = int(seed)
        
        if seed is not None:
            random.seed(seed)
            logging.info(f"Sử dụng seed: {seed}")
        
        logging.info(f"Đang sinh {num_questions} câu hỏi nhập làn cao tốc...")
        
        questions_data: List[Tuple[str, str]] = []
        
        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            question = HighwayMergeQuestion(config)
            question_content, correct_markers = question.generate_question_only(i + 1)
            questions_data.append((question_content, correct_markers))
            logging.info(f"  Câu {i + 1}: Đáp án đúng = {correct_markers}")
        
        latex_content = BaseHighwayMergeQuestion.create_latex_document(
            questions_data,
            title="Bài tập Ô tô Nhập làn Cao tốc"
        )
        
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "highway_merge_questions.tex")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")
        
        print("\n=== ĐÁP ÁN ===")
        for i, (_, markers) in enumerate(questions_data):
            print(f"Câu {i + 1}: {markers if markers else '(không có đáp án đúng)'}")
        
    except ValueError as e:
        print(f"Lỗi: Tham số không hợp lệ - {e}")
        print("Usage: python highway_merge_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")
        raise


if __name__ == "__main__":
    main()
