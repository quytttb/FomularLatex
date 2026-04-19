"""
Hệ thống sinh đề toán về diện tích giấy cắt parabol
Bài toán: Hình chữ nhật ABCD với 2 parabol, tính các diện tích
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


# 20 giá trị cho BC (chiều dài hình chữ nhật)
BC_VALUES: List[Fraction] = [
    Fraction(12), Fraction(124, 10), Fraction(128, 10), Fraction(132, 10), Fraction(136, 10),
    Fraction(14), Fraction(144, 10), Fraction(148, 10), Fraction(152, 10), Fraction(156, 10),
    Fraction(16), Fraction(164, 10), Fraction(168, 10), Fraction(172, 10), Fraction(176, 10),
    Fraction(18), Fraction(184, 10), Fraction(188, 10), Fraction(192, 10), Fraction(20)
]

# 20 giá trị cho AD (chiều rộng hình chữ nhật)
AD_VALUES: List[Fraction] = [
    Fraction(6), Fraction(62, 10), Fraction(64, 10), Fraction(66, 10), Fraction(68, 10),
    Fraction(7), Fraction(72, 10), Fraction(74, 10), Fraction(76, 10), Fraction(78, 10),
    Fraction(8), Fraction(82, 10), Fraction(84, 10), Fraction(86, 10), Fraction(88, 10),
    Fraction(9), Fraction(92, 10), Fraction(94, 10), Fraction(96, 10), Fraction(10)
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


# ==============================================================================
# HÀM TÍNH TOÁN HÌNH HỌC
# ==============================================================================

def parabola_p1(x: sp.Symbol, half_BC: sp.Rational, AD: sp.Rational) -> sp.Expr:
    """
    Parabol P1: đỉnh tại O(0,0), đi qua A(-BC/2, AD) và D(BC/2, AD)
    k = AD / half_BC² => P1 = (AD/half_BC²) * x²
    """
    k = AD / half_BC**2
    return k * x**2


def parabola_p2(x: sp.Symbol, half_BC: sp.Rational, AD: sp.Rational) -> sp.Expr:
    """
    Parabol P2: đỉnh tại (0, AD), đi qua B(-BC/2, 0) và C(BC/2, 0)
    a = -AD / half_BC² => P2 = -(AD/half_BC²) * x² + AD
    """
    k = AD / half_BC**2
    return -k * x**2 + AD


def intersection_x(half_BC: sp.Rational, AD: sp.Rational) -> sp.Expr:
    """
    Tìm hoành độ giao điểm M, N của 2 parabol
    P1 = P2 => (AD/half_BC²)*x² = -(AD/half_BC²)*x² + AD
    => 2*(AD/half_BC²)*x² = AD
    => x² = half_BC² / 2
    => x = ±half_BC / √2 = ±half_BC*√2/2
    """
    return half_BC / sp.sqrt(2)


def intersection_y(half_BC: sp.Rational, AD: sp.Rational) -> sp.Expr:
    """
    Tung độ giao điểm = P1(x_int) = (AD/half_BC²) * (half_BC/√2)² = AD/2
    """
    return AD / 2


def area_triangle_AMN(half_BC: sp.Rational, AD: sp.Rational) -> sp.Expr:
    """
    Diện tích tam giác AMN
    - M(-x_int, AD/2), N(x_int, AD/2), A(-half_BC, AD)
    - x_int = half_BC/√2 => MN = 2*x_int = half_BC*√2
    - Chiều cao từ A đến MN = AD - AD/2 = AD/2
    - S = (1/2) * MN * h = (1/2) * half_BC*√2 * AD/2
    """
    x_int = intersection_x(half_BC, AD)
    MN = 2 * x_int  # = half_BC * sqrt(2)
    h = AD / 2
    return sp.Rational(1, 2) * MN * h


def area_yellow_AMB(half_BC: sp.Rational, AD: sp.Rational) -> sp.Expr:
    """
    Diện tích vùng vàng (giữa AB, P1 và P2 từ x=-half_BC đến x=-x_int):
    S_yellow = ∫_{-half_BC}^{-x_int} (P1(x) - P2(x)) dx
             = ∫_{-half_BC}^{-x_int} (2*(AD/half_BC²)*x² - AD) dx
    """
    x = sp.Symbol('x')
    x_int = intersection_x(half_BC, AD)
    k = AD / half_BC**2
    integrand = 2 * k * x**2 - AD
    return sp.integrate(integrand, (x, -half_BC, -x_int))


def area_red_between_parabolas(half_BC: sp.Rational, AD: sp.Rational) -> sp.Expr:
    """
    Diện tích vùng đỏ (giữa 2 parabol): từ M đến N
    S = ∫_{-x_int}^{x_int} (P2 - P1) dx
      = ∫_{-x_int}^{x_int} (AD - 2*(AD/half_BC²)*x²) dx
    """
    x = sp.Symbol('x')
    x_int = intersection_x(half_BC, AD)
    k = AD / half_BC**2
    integrand = AD - 2 * k * x**2
    return sp.integrate(integrand, (x, -x_int, x_int))


def area_striped_NBC(half_BC: sp.Rational, AD: sp.Rational) -> sp.Expr:
    """
    Diện tích vùng gạch sọc: giới hạn bởi OC, cung ON trên P1, cung NC trên P2
    S = ∫_{0}^{x_int} P1 dx + ∫_{x_int}^{half_BC} P2 dx
    """
    x = sp.Symbol('x')
    x_int = intersection_x(half_BC, AD)
    k = AD / half_BC**2

    P1 = k * x**2
    P2 = -k * x**2 + AD

    area1 = sp.integrate(P1, (x, 0, x_int))
    area2 = sp.integrate(P2, (x, x_int, half_BC))
    return area1 + area2


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

TIKZ_DIAGRAM = r"""
\begin{tikzpicture}[line join=round, line cap=round,>=stealth,thick,scale=0.4]
  % Hệ tọa độ: half_BC = 6, AD = 6
  % P1: y = x²/6 (đi qua A(-6, 6) và D(6, 6))
  % P2: y = 6 - x²/6 (đi qua B(-6, 0) và C(6, 0))
  % Giao điểm M, N: x = ±sqrt(6*6/2) = ±sqrt(18) ≈ ±4.243
  
  % Yellow fill for AMB region (between P2 and line AB from A to M)
  \begin{scope}
    \clip (-6,6) -- (-4.243,3) -- plot[samples=100,domain=-4.243:-6,smooth,variable=\x] (\x, {6 - \x*\x/6}) -- cycle;
    \fill[yellow!40] (-6,6) -- (-4.243,3) -- plot[samples=100,domain=-4.243:-6,smooth,variable=\x] (\x, {6 - \x*\x/6}) -- cycle;
  \end{scope}
  
  % Red fill between parabolas (from M to N)
  \begin{scope}
    \fill[red!30] plot[samples=100,domain=-4.243:4.243,smooth,variable=\x] (\x, {\x*\x/6}) -- plot[samples=100,domain=4.243:-4.243,smooth,variable=\x] (\x, {6 - \x*\x/6}) -- cycle;
  \end{scope}
  
  % Striped pattern: bounded by OC (y=0), arc ON on P1, arc NC on P2
  \begin{scope}
    \fill[gray!25] (0,0) -- (6,0) -- plot[samples=100,domain=6:4.243,smooth,variable=\x] (\x, {6 - \x*\x/6}) -- plot[samples=100,domain=4.243:0,smooth,variable=\x] (\x, {\x*\x/6}) -- cycle;
    \clip (0,0) -- (6,0) -- plot[samples=100,domain=6:4.243,smooth,variable=\x] (\x, {6 - \x*\x/6}) -- plot[samples=100,domain=4.243:0,smooth,variable=\x] (\x, {\x*\x/6}) -- cycle;
    \foreach \i in {-8,-7.5,...,8} {\draw[thin,gray] (\i,0) -- (\i+6,6);}
  \end{scope}
  
  % Rectangle ABCD (w=12, h=6) - parabol áp sát cả 4 góc
  \draw[thick] (-6,0) -- (6,0) -- (6,6) -- (-6,6) -- cycle;
  
  % Parabola P1 (opens upward, vertex at O(0,0), passes through A(-6,6) and D(6,6))
  \draw[samples=100,domain=-6:6,smooth,variable=\x] plot (\x, {\x*\x/6});
  
  % Parabola P2 (opens downward, vertex at (0,6), passes through B(-6,0) and C(6,0))
  \draw[samples=100,domain=-6:6,smooth,variable=\x] plot (\x, {6 - \x*\x/6});
  
  % Labels for vertices
  \path (-6,6) node [above left] {$A$};
  \path (6,6) node [above right] {$D$};
  \path (-6,0) node [below left] {$B$};
  \path (6,0) node [below right] {$C$};
  
  % Intersection points M and N (x = ±sqrt(18) ≈ ±4.243, y = 3)
  \fill (-4.243, 3) circle (3pt);
  \path (-4.243, 3) node [left] {$M$};
  \fill (4.243, 3) circle (3pt);
  \path (4.243, 3) node [right] {$N$};
  
  % Dimensions
  \draw[<->] (-6,-1.5) -- (6,-1.5) node[midway, below] {$BC_VAL$m};
  \draw[<->] (8.5,0) -- (8.5,6) node[midway, right] {$AD_VAL$m};
\end{tikzpicture}
"""

# TikZ cho lời giải (có hệ trục tọa độ Oxy) - escape $ thành $$ cho Template
TIKZ_SOLUTION = r"""
\begin{tikzpicture}[line join=round, line cap=round,>=stealth,thick,scale=0.4]
  % Hệ tọa độ: half_BC = 6, AD = 6
  
  % Yellow fill for AMB region
  \begin{scope}
    \clip (-6,6) -- (-4.243,3) -- plot[samples=100,domain=-4.243:-6,smooth,variable=\x] (\x, {6 - \x*\x/6}) -- cycle;
    \fill[yellow!40] (-6,6) -- (-4.243,3) -- plot[samples=100,domain=-4.243:-6,smooth,variable=\x] (\x, {6 - \x*\x/6}) -- cycle;
  \end{scope}
  
  % Red fill between parabolas
  \begin{scope}
    \fill[red!30] plot[samples=100,domain=-4.243:4.243,smooth,variable=\x] (\x, {\x*\x/6}) -- plot[samples=100,domain=4.243:-4.243,smooth,variable=\x] (\x, {6 - \x*\x/6}) -- cycle;
  \end{scope}
  
  % Striped pattern
  \begin{scope}
    \fill[gray!25] (0,0) -- (6,0) -- plot[samples=100,domain=6:4.243,smooth,variable=\x] (\x, {6 - \x*\x/6}) -- plot[samples=100,domain=4.243:0,smooth,variable=\x] (\x, {\x*\x/6}) -- cycle;
    \clip (0,0) -- (6,0) -- plot[samples=100,domain=6:4.243,smooth,variable=\x] (\x, {6 - \x*\x/6}) -- plot[samples=100,domain=4.243:0,smooth,variable=\x] (\x, {\x*\x/6}) -- cycle;
    \foreach \i in {-8,-7.5,...,8} {\draw[thin,gray] (\i,0) -- (\i+6,6);}
  \end{scope}
  
  % Rectangle ABCD
  \draw[thick] (-6,0) -- (6,0) -- (6,6) -- (-6,6) -- cycle;
  
  % Parabola P1
  \draw[samples=100,domain=-6:6,smooth,variable=\x] plot (\x, {\x*\x/6});
  
  % Parabola P2
  \draw[samples=100,domain=-6:6,smooth,variable=\x] plot (\x, {6 - \x*\x/6});
  
  % Labels for vertices
  \path (-6,6) node [above left] {$$A$$};
  \path (6,6) node [above right] {$$D$$};
  \path (-6,0) node [below left] {$$B$$};
  \path (6,0) node [below right] {$$C$$};
  
  % Intersection points M and N
  \fill (-4.243, 3) circle (3pt);
  \path (-4.243, 3) node [left] {$$M$$};
  \fill (4.243, 3) circle (3pt);
  \path (4.243, 3) node [right] {$$N$$};
  
  % Trục tọa độ Oxy
  \draw[->] (0,0) -- (7.5,0) node[right] {$$x$$};
  \draw[->] (0,0) -- (0,7.5) node[above] {$$y$$};
  
  % Điểm O (gốc tọa độ)
  \path (0,0) node [below left] {$$O$$};
  
  % Nhãn trên trục Ox (gần C)
  \path (6,0) node [above right] {$$${half_BC}$$};
  
  % Nhãn trên trục Oy
  \path (0,7) node [left] {$$${AD}$$};
\end{tikzpicture}
"""


TEMPLATE_QUESTION = Template(r"""Một mô hình giấy trang trí có dạng hình chữ nhật \(ABCD\) như hình vẽ. Một học sinh muốn cắt tờ giấy theo đường dạng Parabol có đỉnh là trung điểm các cạnh dài của tờ giấy và đi qua hai đỉnh của cạnh đối diện. Gọi \(M, N\) lần lượt là các giao điểm của hai Parabol.

\begin{center}
${tikz_diagram}
\end{center}

${marker_a}a) Diện tích tam giác \(AMN\) có giá trị bằng ${area_amn_statement}.

${marker_b}b) Diện tích phần giấy giới hạn bởi Parabol và đoạn thẳng \(AB\) (phần tô màu vàng) có giá trị ${yellow_statement}.

${marker_c}c) Phần diện tích giới hạn bởi hai đường Parabol (phần tô màu đỏ) có giá trị ${red_statement}.

${marker_d}d) Diện tích phần giấy giới hạn bởi Parabol và đoạn thẳng \(BC\) (phần gạch sọc) có giá trị ${striped_statement}.
""")


TEMPLATE_SOLUTION = Template(r"""
Lời giải:

\begin{center}
""" + TIKZ_SOLUTION + r"""
\end{center}

Chọn hệ trục tọa độ như hình vẽ với \(O\) là trung điểm \(BC\).

Viết phương trình 2 Parabol:

\(P_1 = kx^2\). Vì \(P_1(${half_BC}) = ${AD}\) nên \(${half_BC_sq} \cdot k = ${AD} \Rightarrow k = ${k_val} \Rightarrow P_1 = ${k_val}x^2\)

\(P_2 = k(x-${half_BC_latex})(x+${half_BC_latex}) + ${AD} = -${k_val}x^2 + ${AD}\)

Xét phương trình tọa độ giao điểm: \(${k_val}x^2 = -${k_val}x^2 + ${AD} \Rightarrow x^2 = \dfrac{${half_BC_sq}}{2} \Rightarrow x = \pm${x_int_latex}\).

a) ${sol_a}

b) ${sol_b}

c) ${sol_c}

d) ${sol_d}
""")


# ==============================================================================
# LỚP CƠ SỞ VÀ CÀI ĐẶT
# ==============================================================================

class BaseParabolaPaperQuestion(ABC):
    """Lớp cơ sở cho các bài toán giấy cắt parabol"""
    
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
        title: str = "Bài tập Diện tích Giấy Cắt Parabol",
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


class ParabolaPaperQuestion(BaseParabolaPaperQuestion):
    """Bài toán tính diện tích giấy cắt parabol"""
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên"""
        BC = random.choice(BC_VALUES)
        AD = random.choice(AD_VALUES)
        
        return {
            "BC": BC,
            "AD": AD,
        }
    
    def calculate_values(self) -> Dict[str, Any]:
        """Tính toán các giá trị"""
        params = self.parameters
        
        BC = sp.Rational(params["BC"].numerator, params["BC"].denominator)
        AD = sp.Rational(params["AD"].numerator, params["AD"].denominator)
        half_BC = BC / 2
        
        # Tính hoành độ giao điểm
        x_int = intersection_x(half_BC, AD)
        y_int = intersection_y(half_BC, AD)
        
        # Tính các diện tích
        S_AMN = area_triangle_AMN(half_BC, AD)
        S_yellow = area_yellow_AMB(half_BC, AD)
        S_red = area_red_between_parabolas(half_BC, AD)
        S_striped = area_striped_NBC(half_BC, AD)
        
        # Giá trị số
        S_AMN_val = float(S_AMN.evalf())
        S_yellow_val = float(S_yellow.evalf())
        S_red_val = float(S_red.evalf())
        S_striped_val = float(S_striped.evalf())
        
        # Random True/False cho mỗi statement
        a_correct = random.choice([True, False])
        b_correct = random.choice([True, False])
        c_correct = random.choice([True, False])
        d_correct = random.choice([True, False])
        
        return {
            "half_BC": half_BC,
            "x_int": x_int,
            "y_int": y_int,
            "S_AMN": S_AMN,
            "S_AMN_val": S_AMN_val,
            "S_yellow": S_yellow,
            "S_yellow_val": S_yellow_val,
            "S_red": S_red,
            "S_red_val": S_red_val,
            "S_striped": S_striped,
            "S_striped_val": S_striped_val,
            "a_correct": a_correct,
            "b_correct": b_correct,
            "c_correct": c_correct,
            "d_correct": d_correct,
        }
    
    def generate_tikz_diagram(self) -> str:
        """Tạo TikZ diagram với giá trị thực
        
        Lưu ý: Template TikZ sử dụng tọa độ cố định (half_BC=6, AD=6) làm hình minh họa.
        Chỉ thay thế các label hiển thị BC_VAL và AD_VAL.
        """
        params = self.parameters
        BC_val = format_fraction_vn(params["BC"])
        AD_val = format_fraction_vn(params["AD"])
        
        # Chỉ thay thế label hiển thị, giữ nguyên tọa độ template
        tikz = TIKZ_DIAGRAM.replace("$BC_VAL$", BC_val)
        tikz = tikz.replace("$AD_VAL$", AD_val)
        
        return tikz
    
    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        params = self.parameters
        calc = self.calculated_values
        
        # Markers
        marker_a = "*" if calc["a_correct"] else ""
        marker_b = "*" if calc["b_correct"] else ""
        marker_c = "*" if calc["c_correct"] else ""
        marker_d = "*" if calc["d_correct"] else ""
        
        # Statements based on correct/wrong
        S_AMN_val = calc["S_AMN_val"]
        S_yellow_val = calc["S_yellow_val"]
        S_red_val = calc["S_red_val"]
        S_striped_val = calc["S_striped_val"]
        
        # a) Diện tích tam giác AMN
        if calc["a_correct"]:
            area_amn_statement = f"\\({format_decimal_vn(S_AMN_val)} \\text{{ m}}^2\\)"
        else:
            wrong_val = S_AMN_val * random.choice([1.2, 1.5, 0.8])
            area_amn_statement = f"\\({format_decimal_vn(wrong_val)} \\text{{ m}}^2\\)"
        
        # b) Diện tích vàng - so sánh
        threshold_yellow = round(S_yellow_val * 0.9, 1)
        if calc["b_correct"]:
            yellow_statement = f"lớn hơn \\({format_decimal_vn(threshold_yellow)} \\text{{ m}}^2\\)"
        else:
            threshold_wrong = round(S_yellow_val * 1.2, 1)
            yellow_statement = f"lớn hơn \\({format_decimal_vn(threshold_wrong)} \\text{{ m}}^2\\)"
        
        # c) Diện tích đỏ - giá trị xấp xỉ
        if calc["c_correct"]:
            red_statement = f"bằng \\({format_decimal_vn(S_red_val, 1)} \\text{{ m}}^2\\)"
        else:
            wrong_val = S_red_val * random.choice([1.3, 0.7])
            red_statement = f"bằng \\({format_decimal_vn(wrong_val, 1)} \\text{{ m}}^2\\)"
        
        # d) Diện tích gạch sọc - so sánh
        threshold_striped = round(S_striped_val * 1.5, 1)
        if calc["d_correct"]:
            striped_statement = f"nhỏ hơn \\({format_decimal_vn(threshold_striped)} \\text{{ m}}^2\\)"
        else:
            threshold_wrong = round(S_striped_val * 0.8, 1)
            striped_statement = f"nhỏ hơn \\({format_decimal_vn(threshold_wrong)} \\text{{ m}}^2\\)"
        
        return TEMPLATE_QUESTION.substitute(
            BC=format_fraction_vn(params["BC"]),
            AD=format_fraction_vn(params["AD"]),
            tikz_diagram=self.generate_tikz_diagram(),
            marker_a=marker_a,
            marker_b=marker_b,
            marker_c=marker_c,
            marker_d=marker_d,
            area_amn_statement=area_amn_statement,
            yellow_statement=yellow_statement,
            red_statement=red_statement,
            striped_statement=striped_statement,
        )
    
    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết"""
        params = self.parameters
        calc = self.calculated_values

        AD = sp.Rational(params["AD"].numerator, params["AD"].denominator)
        half_BC = calc["half_BC"]

        # K tự động rút gọn phân số qua sympy
        k_sym = AD / half_BC**2
        k_val_str = sp.latex(k_sym)  # Format phân số chuẩn

        # Format x_int = half_BC / sqrt(2)
        x_int_latex = sp.latex(calc["x_int"])
        
        # Format half_BC dứoi dạng latex sympy thay vì số thập phân phẩy
        half_BC_latex = sp.latex(half_BC)
        
        # Các biến dùng để render step-by-step math
        term_kx2 = sp.latex(k_sym * sp.Symbol('x')**2)
        AD_str = format_decimal_vn(AD)
        int_P1_minus_P2 = f"{term_kx2} + {term_kx2} - {AD_str}"
        int_P2_minus_P1 = f"-{term_kx2} + {AD_str} - {term_kx2}"
        AH_latex = format_decimal_vn(AD / 2)
        MN_latex = sp.latex(2 * calc["x_int"])

        # Solution for each part with detailed explanation
        sol_a_text = f"\\(N({x_int_latex}; {AH_latex}) \\Rightarrow M(-{x_int_latex}; {AH_latex}) \\Rightarrow MN = {MN_latex}; AH = {AH_latex} \\Rightarrow S_{{AMN}} = \\dfrac{{1}}{{2}} \\cdot {AH_latex} \\cdot {MN_latex} = {format_decimal_vn(calc['S_AMN_val'])} \\, (m^2)\\)"
        sol_a = f"{'Đúng' if calc['a_correct'] else 'Sai'}. {sol_a_text}"
        
        sol_b_text = f"Tính diện tích phần tô màu vàng: \\(\\displaystyle \\int_{{-{half_BC_latex}}}^{{-{x_int_latex}}} \\left( {int_P1_minus_P2} \\right) dx \\approx {format_decimal_vn(calc['S_yellow_val'])} \\, (m^2)\\)"
        sol_b = f"{'Đúng' if calc['b_correct'] else 'Sai'}. {sol_b_text}"
        
        sol_c_text = f"Tính diện tích phần tô màu đỏ: \\(\\displaystyle \\int_{{-{x_int_latex}}}^{{{x_int_latex}}} \\left( {int_P2_minus_P1} \\right) dx \\approx {format_decimal_vn(calc['S_red_val'], 1)} \\, (m^2)\\)"
        sol_c = f"{'Đúng' if calc['c_correct'] else 'Sai'}. {sol_c_text}"
        
        sol_d_text = f"Tính diện tích phần gạch sọc: \\(\\displaystyle \\int_{{0}}^{{{x_int_latex}}} {term_kx2} \\, dx + \\int_{{{x_int_latex}}}^{{{half_BC_latex}}} \\left( -{term_kx2} + {AD_str} \\right) dx \\approx {format_decimal_vn(calc['S_striped_val'])} \\, (m^2)\\)"
        sol_d = f"{'Đúng' if calc['d_correct'] else 'Sai'}. {sol_d_text}"

        return TEMPLATE_SOLUTION.substitute(
            half_BC=format_fraction_vn(half_BC),
            half_BC_latex=half_BC_latex,
            half_BC_sq=format_fraction_vn(half_BC**2),
            AD=format_fraction_vn(params["AD"]),
            k_val=k_val_str,
            x_int_latex=x_int_latex,
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
    Usage: python parabola_paper_questions.py <num_questions> [seed]
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
        
        logging.info(f"Đang sinh {num_questions} câu hỏi giấy cắt parabol...")
        
        questions_data: List[Tuple[str, str]] = []
        
        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            question = ParabolaPaperQuestion(config)
            question_content, correct_markers = question.generate_question_only(i + 1)
            questions_data.append((question_content, correct_markers))
            logging.info(f"  Câu {i + 1}: Đáp án đúng = {correct_markers}")
        
        latex_content = BaseParabolaPaperQuestion.create_latex_document(
            questions_data,
            title="Bài tập Diện tích Giấy Cắt Parabol"
        )
        
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "parabola_paper_questions.tex")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")
        
        print("\n=== ĐÁP ÁN ===")
        for i, (_, markers) in enumerate(questions_data):
            print(f"Câu {i + 1}: {markers if markers else '(không có đáp án đúng)'}")
        
    except ValueError as e:
        print(f"Lỗi: Tham số không hợp lệ - {e}")
        print("Usage: python parabola_paper_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")
        raise


if __name__ == "__main__":
    main()
