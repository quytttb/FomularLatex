"""
Hệ thống sinh đề toán về thể tích tường cong
Bài toán: Tính thể tích khối bê tông tường cong với bề mặt parabol
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


# 20 giá trị cho chiều dài đáy AC (l_base)
L_BASE_VALUES: List[Fraction] = [
    Fraction(30, 10), Fraction(32, 10), Fraction(34, 10), Fraction(36, 10), Fraction(38, 10),
    Fraction(40, 10), Fraction(42, 10), Fraction(44, 10), Fraction(46, 10), Fraction(48, 10),
    Fraction(50, 10), Fraction(52, 10), Fraction(54, 10), Fraction(56, 10), Fraction(58, 10),
    Fraction(60, 10), Fraction(62, 10), Fraction(64, 10), Fraction(66, 10), Fraction(68, 10)
]

# 20 giá trị cho chiều cao tường CE (h_wall)
H_WALL_VALUES: List[Fraction] = [
    Fraction(25, 10), Fraction(27, 10), Fraction(29, 10), Fraction(31, 10), Fraction(33, 10),
    Fraction(35, 10), Fraction(37, 10), Fraction(39, 10), Fraction(41, 10), Fraction(43, 10),
    Fraction(45, 10), Fraction(47, 10), Fraction(49, 10), Fraction(51, 10), Fraction(53, 10),
    Fraction(55, 10), Fraction(57, 10), Fraction(59, 10), Fraction(61, 10), Fraction(63, 10)
]

# 20 giá trị cho chiều rộng đáy AB (w_base)
W_BASE_VALUES: List[Fraction] = [
    Fraction(15, 10), Fraction(16, 10), Fraction(17, 10), Fraction(18, 10), Fraction(19, 10),
    Fraction(20, 10), Fraction(21, 10), Fraction(22, 10), Fraction(23, 10), Fraction(24, 10),
    Fraction(25, 10), Fraction(26, 10), Fraction(27, 10), Fraction(28, 10), Fraction(29, 10),
    Fraction(30, 10), Fraction(31, 10), Fraction(32, 10), Fraction(33, 10), Fraction(34, 10)
]

# 20 giá trị cho tỉ lệ h_mid/h_wall (đảm bảo a > 0)
H_MID_RATIO_VALUES: List[Fraction] = [
    Fraction(20, 100), Fraction(21, 100), Fraction(22, 100), Fraction(23, 100), Fraction(24, 100),
    Fraction(25, 100), Fraction(26, 100), Fraction(27, 100), Fraction(28, 100), Fraction(29, 100),
    Fraction(30, 100), Fraction(31, 100), Fraction(32, 100), Fraction(33, 100), Fraction(34, 100),
    Fraction(35, 100), Fraction(36, 100), Fraction(37, 100), Fraction(38, 100), Fraction(39, 100)
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
    formatted = f"{decimal_val:.6f}".rstrip('0').rstrip('.')
    return formatted.replace(".", ",")


def to_decimal_comma(value: Any) -> str:
    """Chuyển dấu chấm thành dấu phẩy cho số thập phân"""
    if isinstance(value, Fraction):
        return format_fraction_vn(value)
    return str(value).replace(".", ",")


def format_fraction_latex(frac: Fraction) -> str:
    """Format Fraction thành LaTeX dạng phân số"""
    if frac.denominator == 1:
        return str(frac.numerator)
    if frac.numerator < 0:
        return rf"- \dfrac{{{-frac.numerator}}}{{{frac.denominator}}}"
    return rf"\dfrac{{{frac.numerator}}}{{{frac.denominator}}}"


# ==============================================================================
# HÀM TÍNH TOÁN HÌNH HỌC
# ==============================================================================

def find_parabola_coefficients(l_base: Fraction, h_wall: Fraction, h_mid: Fraction) -> Tuple[Fraction, Fraction]:
    """
    Tìm hệ số a, b của parabol y = ax² + bx đi qua:
    - A(0, 0)
    - N(l_base/2, h_mid)
    - E(l_base, h_wall)
    
    Returns: (a, b)
    """
    # From system of equations:
    # c = 0
    # a*(l/2)² + b*(l/2) = h_mid
    # a*l² + b*l = h_wall
    
    # Solution:
    # a = 2*(h_wall - 2*h_mid) / l²
    # b = (4*h_mid - h_wall) / l
    
    l_sq = l_base * l_base
    a = 2 * (h_wall - 2 * h_mid) / l_sq
    b = (4 * h_mid - h_wall) / l_base
    
    return (a, b)


def curved_triangle_area(a: Fraction, b: Fraction, l_base: Fraction) -> Fraction:
    """
    Diện tích tam giác cong ACE:
    S = ∫₀^l (ax² + bx) dx = [ax³/3 + bx²/2]₀^l
    """
    l_cubed = l_base * l_base * l_base
    l_squared = l_base * l_base
    
    area = a * l_cubed / 3 + b * l_squared / 2
    return area


def cross_section_area_formula(a: Fraction, b: Fraction, w_base: Fraction) -> Tuple[Fraction, Fraction]:
    """
    Diện tích thiết diện S(x) = w_base * (ax² + bx) = (w_base*a)x² + (w_base*b)x
    
    Returns: (coefficient of x², coefficient of x)
    """
    return (w_base * a, w_base * b)


def curved_wall_volume(area: Fraction, w_base: Fraction) -> Fraction:
    """
    Thể tích tường cong V = w_base * S_ACE
    """
    return w_base * area


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

TIKZ_DIAGRAM_1 = r"""
\begin{tikzpicture}[line join=round, line cap=round,scale=1,transform shape]
  \path
  (0,0) coordinate (O)
  (-145:2.2) coordinate (A)
  (-3.5,0) coordinate (B)
  ($(A)-(B)$) coordinate (C)
  ($(C)+(0,2.5)$) coordinate (E)
  ($(E)-(C)$) coordinate (F)
  ($(A)!0.5!(C)$) coordinate (M)
  ;
  \draw (B)..controls +(0:1.6) and +(-130:1.2) ..(F)--(E)
  ..controls +(-130:1.2) and +(0:1.6) ..(A)--cycle;
  \path (E)
  ..controls +(-179:1.46) and +(0:2.6) ..(A) coordinate[pos=2/3](B1);
  \path ($(B1)+(2.5,0)$) coordinate (B2);
  \path[name path=m] (B1)--(B2); 
  \path[name path=n] (E)--(C);
  \path[name intersections={of=m and n}] (intersection-1) coordinate (Q);
  \draw (B1)--(M);
  \draw[dashed] (C)--(O)--(B);
  \draw (E)--(C)--(A);
  \foreach \d/\g in {A/-90,C/-90,B/180,E/0,M/-90}{
   \draw[fill=black](\d) +(\g:.35)node{$\d$};}
  \node[right] at ($(E)!.5!(C)$) {$H_WALL$ m};
  \node[below] at ($(A)!.3!(C)$) {$L_BASE$ m};
  \node[below left] at ($(A)!.5!(B)$) {$W_BASE$ m};
  \node[right] at ($(B1)!.5!(M)$) {$H_MID$ m};
\end{tikzpicture}
"""

TIKZ_DIAGRAM_2 = r"""
\begin{tikzpicture}[scale=1, line join=round, line cap=round, >=stealth,transform shape]
  \path
  (0,0) coordinate (O)
  (-145:2.2) coordinate (A)
  (-3.5,0) coordinate (B)
  ($(A)-(B)$) coordinate (C)
  ($(C)+(0,2.5)$) coordinate (E)
  ($(E)-(C)$) coordinate (F)
  ($(A)!0.5!(C)$) coordinate (M)
  ;
  \draw[->] (A) -- ($(A)!1.5!(C)$) node[right] {$x$}; 
  \draw[->] (A) -- ($ (A) +1.6*($(E)-(C)$) $) node[above left] {$y$};
  \draw (B)..controls +(0:1.6) and +(-130:1.2) ..(F)--(E)
  ..controls +(-130:1.2) and +(0:1.6) ..(A)--cycle;
  \path (E)
  ..controls +(-179:1.46) and +(0:2.6) ..(A) coordinate[pos=2/3](B1);
  \path ($(B1)+(2.5,0)$) coordinate (B2);
  \path[name path=m] (B1)--(B2); 
  \path[name path=n] (E)--(C);
  \path[name intersections={of=m and n}] (intersection-1) coordinate (Q);
  \draw (B1)--(M);
  \path ($(A)!0.5!(C)$) coordinate (X2);
  \path ($(A)!1!(C)$) coordinate (X4);
  \node[below] at (X2) {$L_HALF$};
  \node[below] at (X4) {$L_BASE$};
  \filldraw[black] (X2) circle (1pt);
  \filldraw[black] (X4) circle (1pt);
  \path ($(X2) + 0.25*($(E)-(C)$) $) coordinate (P21);
  \path ($(A) + 0.25*($(E)-(C)$) $) coordinate (P01);
  \filldraw[black] (P01) circle (1pt) node[left] {$H_MID$};
  \draw[dashed] (X2) -- (P21) -- (P01);
  \path ($(A) + 1*($(E)-(C)$)$) coordinate (P03);
  \filldraw[black] (P03) circle (1pt) node[left] {$H_WALL$};
  \draw[dashed] (C)--(O)--(B) (E) -- (P03) (O)--(F);
  \draw (E)--(C)--(A);
  \foreach \d/\g in {A/-90,B/180,E/0}{
   \draw[fill=black](\d) +(\g:.35)node{$\d$};}
  \node[right] at ($(E)!.5!(C)$) {$H_WALL$ m};
  \node[below] at ($(A)!.3!(C)$) {$L_BASE$ m};
  \node[below left] at ($(A)!.5!(B)$) {$W_BASE$ m};
  \node[right] at ($(B1)!.5!(M)$) {$H_MID$ m};
\end{tikzpicture}
"""


TEMPLATE_QUESTION = Template(r"""Chướng ngại vật "tường cong" trong một sân thi đấu thể thao là một khối bê tông có chiều cao từ mặt đất lên là \(${h_wall} \text{ m}\). Bề mặt tiếp xúc với mặt đất là một hình chữ nhật, giao của mặt tường cong và mặt đất là đoạn thẳng \(AB = ${w_base} \text{ m}\). Thiết diện của tường cong khi cắt bởi mặt phẳng vuông góc với \(AB\) tại \(A\) là một tam giác cong \(ACE\) vuông tại \(C\) với \(AC = ${l_base} \text{ m}, CE = ${h_wall} \text{ m}\), cạnh cong \(AE\) nằm trên một đường parabol có trục đối xứng vuông góc với mặt đất. Tại vị trí \(M\) là trung điểm \(AC\) thì đường cong có độ cao \(${h_mid} \text{ m}\) (xem hình vẽ sau).

\begin{center}
${tikz_diagrams}
\end{center}

${marker_a}a) Chọn hệ trục tọa độ \(Oxy\) sao cho \(O\) trùng \(A\), điểm \(C\) thuộc tia \(Ox\) và \(Oy\) vuông góc với mặt đất. Khi đó cạnh cong \(AE\) nằm trên parabol \((P)\) đi qua các điểm ${points_statement}.

${marker_b}b) Diện tích tam giác cong \(ACE\) là \(S = ${area_statement} \text{ m}^2\).

${marker_c}c) Cắt vật thể bởi mặt phẳng vuông góc với \(Ox\) tại điểm có hoành độ \(x \; (0 < x \leq ${l_base})\) ta được thiết diện là hình chữ nhật với diện tích \(S(x) = ${sx_statement}\).

${marker_d}d) Thể tích của khối bê tông này lớn hơn \(${threshold_statement} \text{ m}^3\).""")


# Solution template không dùng Template vì cần logic điều kiện phức tạp
# => Xây dựng trực tiếp trong generate_solution()


# ==============================================================================
# LỚP CƠ SỞ VÀ CÀI ĐẶT
# ==============================================================================

class BaseCurvedWallQuestion(ABC):
    """Lớp cơ sở cho các bài toán tường cong"""
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.correct_answer: Optional[str] = None
        self.config = config or GeneratorConfig()
    
    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def calculate_answer(self) -> str:
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
        self.correct_answer = self.calculate_answer()
        question_text = self.generate_question_text().strip()
        solution = self.generate_solution().strip()
        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += f"Lời giải:\n{solution}\n"
        return question_content, self.correct_answer
    
    @staticmethod
    def create_latex_document(
        questions_data: List[Tuple[str, str]],
        title: str = "Bài tập Tường Cong",
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
\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing,intersections,patterns}}
\usepackage{{enumitem}}

\title{{{title}}}
\author{{Generator}}
\date{{\today}}

\begin{{document}}
\maketitle

{questions_content}

\end{{document}}
"""
        return latex_document


class CurvedWallVolumeQuestion(BaseCurvedWallQuestion):
    """Bài toán tính thể tích tường cong với 4 câu True/False"""
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên"""
        max_attempts = 500
        for _ in range(max_attempts):
            l_base = random.choice(L_BASE_VALUES)
            h_wall = random.choice(H_WALL_VALUES)
            w_base = random.choice(W_BASE_VALUES)
            h_mid_ratio = random.choice(H_MID_RATIO_VALUES)
            
            h_mid = h_wall * h_mid_ratio
            
            # Tính hệ số parabol
            a, b = find_parabola_coefficients(l_base, h_wall, h_mid)
            
            # Constraint: a > 0 và b > 0 (parabol mở lên, S(x) > 0 trên (0, l_base))
            if a <= 0 or b <= 0:
                continue
            
            # Tính diện tích và thể tích
            area = curved_triangle_area(a, b, l_base)
            volume = curved_wall_volume(area, w_base)
            
            # Tính công thức S(x)
            sx_a, sx_b = cross_section_area_formula(a, b, w_base)
            
            # Random True/False cho 4 câu
            tf_choices = [random.choice([True, False]) for _ in range(4)]
            
            return {
                "l_base": l_base,
                "h_wall": h_wall,
                "w_base": w_base,
                "h_mid": h_mid,
                "a": a,
                "b": b,
                "area": area,
                "volume": volume,
                "sx_a": sx_a,
                "sx_b": sx_b,
                "tf_a": tf_choices[0],
                "tf_b": tf_choices[1],
                "tf_c": tf_choices[2],
                "tf_d": tf_choices[3],
            }
        
        raise ValueError("Không tìm được bộ tham số hợp lệ (a > 0, b > 0) sau nhiều lần thử")
    
    def calculate_answer(self) -> str:
        """Tạo chuỗi đáp án ĐĐSS"""
        params = self.parameters
        answer = ""
        answer += "Đ" if params["tf_a"] else "S"
        answer += "Đ" if params["tf_b"] else "S"
        answer += "Đ" if params["tf_c"] else "S"
        answer += "Đ" if params["tf_d"] else "S"
        return answer
    
    def generate_tikz_diagrams(self) -> str:
        """Tạo TikZ diagrams với các giá trị cụ thể"""
        params = self.parameters
        
        l_half = params["l_base"] / 2
        
        tikz1 = TIKZ_DIAGRAM_1
        tikz1 = tikz1.replace("$H_WALL$", format_fraction_vn(params["h_wall"]))
        tikz1 = tikz1.replace("$L_BASE$", format_fraction_vn(params["l_base"]))
        tikz1 = tikz1.replace("$W_BASE$", format_fraction_vn(params["w_base"]))
        tikz1 = tikz1.replace("$H_MID$", format_fraction_vn(params["h_mid"]))
        
        tikz2 = TIKZ_DIAGRAM_2
        tikz2 = tikz2.replace("$H_WALL$", format_fraction_vn(params["h_wall"]))
        tikz2 = tikz2.replace("$L_BASE$", format_fraction_vn(params["l_base"]))
        tikz2 = tikz2.replace("$W_BASE$", format_fraction_vn(params["w_base"]))
        tikz2 = tikz2.replace("$H_MID$", format_fraction_vn(params["h_mid"]))
        tikz2 = tikz2.replace("$L_HALF$", format_fraction_vn(l_half))
        
        return tikz1 + r"\hfill" + "\n" + tikz2
    
    def _format_points(self, h_mid_val: Fraction) -> str:
        """Format 3 điểm trên parabol cho LaTeX"""
        params = self.parameters
        l_half = params["l_base"] / 2
        return f"\\((0; 0), ({format_fraction_vn(l_half)}; {format_fraction_vn(h_mid_val)}), ({format_fraction_vn(params['l_base'])}; {format_fraction_vn(params['h_wall'])})\\)"

    def generate_statement_a(self) -> str:
        """Generate statement a) - points on parabola"""
        params = self.parameters
        
        if params["tf_a"]:
            return self._format_points(params['h_mid'])
        else:
            # Wrong middle point - thêm hoặc bớt để tạo giá trị sai
            wrong_h_mid = params["h_mid"] + Fraction(1, 2)
            params["wrong_h_mid"] = wrong_h_mid  # Lưu lại để dùng trong lời giải
            return self._format_points(wrong_h_mid)
    
    def generate_statement_b(self) -> str:
        """Generate statement b) - area"""
        params = self.parameters
        
        if params["tf_b"]:
            return format_fraction_latex(params["area"])
        else:
            # Wrong area - thay đổi tử số 1 đơn vị
            wrong_area = params["area"] + Fraction(2, 3)
            params["wrong_area"] = wrong_area  # Lưu lại để dùng trong lời giải
            return format_fraction_latex(wrong_area)
    
    def generate_statement_c(self) -> str:
        """Generate statement c) - S(x) formula"""
        params = self.parameters
        
        if params["tf_c"]:
            return f"{format_fraction_latex(params['sx_a'])}x^2 + {format_fraction_latex(params['sx_b'])}x"
        else:
            # Swap coefficients (đảm bảo sx_a != sx_b)
            if params['sx_a'] == params['sx_b']:
                # Nếu trùng nhau, dùng cách khác: nhân hệ số x² với 2
                wrong_sx_a = params['sx_a'] * 2
                wrong_sx_b = params['sx_b']
            else:
                wrong_sx_a = params['sx_b']
                wrong_sx_b = params['sx_a']
            params["wrong_sx_a"] = wrong_sx_a
            params["wrong_sx_b"] = wrong_sx_b
            return f"{format_fraction_latex(wrong_sx_a)}x^2 + {format_fraction_latex(wrong_sx_b)}x"
    
    def generate_statement_d(self) -> str:
        """Generate statement d) - volume threshold"""
        params = self.parameters
        volume_float = float(params["volume"])
        
        if params["tf_d"]:
            # Threshold < actual (TRUE: V > threshold)
            threshold = math.floor(volume_float) - 1
        else:
            # Threshold > actual (FALSE: V > threshold)
            threshold = math.ceil(volume_float) + 1
        
        params["threshold"] = max(1, threshold)
        return str(max(1, threshold))
    
    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        params = self.parameters
        tikz = self.generate_tikz_diagrams()
        
        # Markers: * for true statements, empty for false
        marker_a = "*" if params["tf_a"] else ""
        marker_b = "*" if params["tf_b"] else ""
        marker_c = "*" if params["tf_c"] else ""
        marker_d = "*" if params["tf_d"] else ""
        
        return TEMPLATE_QUESTION.substitute(
            h_wall=format_fraction_vn(params["h_wall"]),
            w_base=format_fraction_vn(params["w_base"]),
            l_base=format_fraction_vn(params["l_base"]),
            h_mid=format_fraction_vn(params["h_mid"]),
            tikz_diagrams=tikz,
            marker_a=marker_a,
            marker_b=marker_b,
            marker_c=marker_c,
            marker_d=marker_d,
            points_statement=self.generate_statement_a(),
            area_statement=self.generate_statement_b(),
            sx_statement=self.generate_statement_c(),
            threshold_statement=self.generate_statement_d(),
        )
    
    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết"""
        params = self.parameters
        l_half = params["l_base"] / 2
        
        # Format các giá trị cần dùng
        h_wall_s = format_fraction_vn(params["h_wall"])
        w_base_s = format_fraction_vn(params["w_base"])
        l_base_s = format_fraction_vn(params["l_base"])
        h_mid_s = format_fraction_vn(params["h_mid"])
        l_half_s = format_fraction_vn(l_half)
        a_coef_s = format_fraction_latex(params["a"])
        b_coef_s = format_fraction_latex(params["b"])
        
        correct_points = self._format_points(params['h_mid'])
        correct_area_s = format_fraction_latex(params["area"])
        correct_sx = f"{format_fraction_latex(params['sx_a'])}x^2 + {format_fraction_latex(params['sx_b'])}x"
        volume_frac_s = format_fraction_latex(params["volume"])
        volume_float = float(params["volume"])
        volume_decimal_s = f"{volume_float:.4f}".rstrip('0').rstrip('.').replace(".", ",")
        
        # Phần chung - dẫn nhập
        sol = rf"""Chọn hệ tọa độ \(Oxy\) sao cho: Gốc tọa độ \(O\) trùng với điểm \(A\), tia \(Ox\) trùng với tia \(AC\), tia \(Oy\) cùng hướng với vectơ \(\overrightarrow{{CE}}\).

Gọi \(N\) là điểm trên cạnh cong \(AE\) và cách mặt đất \({h_mid_s}\) m.

Xét mặt phẳng \(Oxy\): Với cách chọn hệ tọa độ như trên, ta có \(A(0;0)\), \(N({l_half_s};{h_mid_s})\) và \(E({l_base_s};{h_wall_s})\).

Gọi phương trình của cạnh cong \(AE\) (là parabol) có dạng \(y = ax^2 + bx + c\).

Vì parabol đi qua ba điểm \(A\), \(N\) và \(E\) nên ta có hệ phương trình:
\[
\begin{{cases}} c = 0 \\ {l_half_s}^2 a + {l_half_s} b + c = {h_mid_s} \\ {l_base_s}^2 a + {l_base_s} b + c = {h_wall_s} \end{{cases}} \Leftrightarrow \begin{{cases}} a = {a_coef_s} \\ b = {b_coef_s} \\ c = 0 \end{{cases}}
\]

Suy ra phương trình của parabol là \(y = {a_coef_s} x^2 + {b_coef_s} x\).
"""
        
        # ---- Mệnh đề a) - điểm trên parabol ----
        if params["tf_a"]:
            sol += f"\na) Xét mệnh đề về đường parabol: Parabol đi qua {correct_points}, đúng với đề bài \\(\\Rightarrow\\) Mệnh đề này Đúng.\n"
        else:
            wrong_points = self._format_points(params["wrong_h_mid"])
            sol += f"\na) Xét mệnh đề về đường parabol: Đề bài cho parabol đi qua {wrong_points}. Nhưng parabol thực tế đi qua {correct_points} \\(\\Rightarrow\\) Mệnh đề này Sai.\n"
        
        # ---- Mệnh đề b) - diện tích ----
        sol += f"\nb) Xét mệnh đề về diện tích tam giác cong \\(ACE\\): \\(S_{{ACE}} = \\displaystyle\\int_0^{{{l_base_s}}} \\left({a_coef_s} x^2 + {b_coef_s} x\\right) dx = {correct_area_s}\\) m\\(^2\\)."
        if params["tf_b"]:
            sol += " Đúng với đề bài \\(\\Rightarrow\\) Mệnh đề này Đúng.\n"
        else:
            wrong_area_s = format_fraction_latex(params["wrong_area"])
            sol += f" Đề bài cho \\(S = {wrong_area_s}\\) m\\(^2\\) \\(\\neq {correct_area_s}\\) \\(\\Rightarrow\\) Mệnh đề này Sai.\n"
        
        # ---- Mệnh đề c) - S(x) ----
        sol += f"\nc) Xét mệnh đề về công thức diện tích thiết diện: \\(S(x) = {w_base_s} \\cdot \\left({a_coef_s} x^2 + {b_coef_s} x\\right) = {correct_sx}\\)."
        if params["tf_c"]:
            sol += " Đúng với đề bài \\(\\Rightarrow\\) Mệnh đề này Đúng.\n"
        else:
            wrong_sx = f"{format_fraction_latex(params['wrong_sx_a'])}x^2 + {format_fraction_latex(params['wrong_sx_b'])}x"
            sol += f" Đề bài cho \\(S(x) = {wrong_sx}\\) \\(\\neq {correct_sx}\\) \\(\\Rightarrow\\) Mệnh đề này Sai.\n"
        
        # ---- Mệnh đề d) - thể tích ----
        threshold = params["threshold"]
        if params["volume"].denominator == 1:
            vol_display = f"{params['volume'].numerator}"
            vol_compare = f"= {vol_display}"
        else:
            vol_display = f"{volume_frac_s} \\approx {volume_decimal_s}"
            vol_compare = f"\\approx {volume_decimal_s}"
        
        sol += f"\nd) Xét mệnh đề về thể tích khối bê tông: \\(V = {w_base_s} \\cdot {correct_area_s} = {vol_display}\\) m\\(^3\\)."
        if params["tf_d"]:
            sol += f" Ta có \\(V {vol_compare} > {threshold}\\), đúng với đề bài \\(\\Rightarrow\\) Mệnh đề này Đúng.\n"
        else:
            sol += f" Ta có \\(V {vol_compare} < {threshold}\\), trái với đề bài \\(\\Rightarrow\\) Mệnh đề này Sai.\n"
        
        return sol


# ==============================================================================
# HÀM MAIN
# ==============================================================================

def main():
    """
    Hàm main để chạy generator
    Usage: python curved_wall_questions.py <num_questions> [seed]
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
        
        logging.info(f"Đang sinh {num_questions} câu hỏi tường cong...")
        
        questions_data: List[Tuple[str, str]] = []
        
        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            question = CurvedWallVolumeQuestion(config)
            question_content, correct_answer = question.generate_question_only(i + 1)
            questions_data.append((question_content, correct_answer))
            logging.info(f"  Câu {i + 1}: Đáp án = {correct_answer}")
        
        latex_content = BaseCurvedWallQuestion.create_latex_document(
            questions_data,
            title="Bài tập Thể tích Tường Cong"
        )
        
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "curved_wall_questions.tex")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")
        
        print("\n=== ĐÁP ÁN ===")
        for i, (_, answer) in enumerate(questions_data):
            print(f"Câu {i + 1}: {answer}")
        
    except ValueError as e:
        print(f"Lỗi: Tham số không hợp lệ - {e}")
        print("Usage: python curved_wall_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")
        raise


if __name__ == "__main__":
    main()
