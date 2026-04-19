"""
Hệ thống sinh đề toán về thể tích máng Parabol thu nhiệt
Bài toán: Tính thể tích khối silic của các máng parabol
Công thức: S_parabol = (2/3) × base × height
"""

import logging
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


# 20 giá trị cho chiều rộng máng (m)
WIDTH_VALUES: List[Fraction] = [
    Fraction(15, 10), Fraction(16, 10), Fraction(17, 10), Fraction(18, 10), Fraction(19, 10),
    Fraction(20, 10), Fraction(21, 10), Fraction(22, 10), Fraction(23, 10), Fraction(24, 10),
    Fraction(25, 10), Fraction(26, 10), Fraction(27, 10), Fraction(28, 10), Fraction(29, 10),
    Fraction(30, 10), Fraction(31, 10), Fraction(32, 10), Fraction(33, 10), Fraction(34, 10)
]

# 20 giá trị cho độ cao đỉnh (m) - đơn vị dm trong đề, convert sang m
HEIGHT_VALUES: List[Fraction] = [
    Fraction(4, 10), Fraction(42, 100), Fraction(44, 100), Fraction(46, 100), Fraction(48, 100),
    Fraction(5, 10), Fraction(52, 100), Fraction(54, 100), Fraction(56, 100), Fraction(58, 100),
    Fraction(6, 10), Fraction(62, 100), Fraction(64, 100), Fraction(66, 100), Fraction(68, 100),
    Fraction(7, 10), Fraction(72, 100), Fraction(74, 100), Fraction(76, 100), Fraction(78, 100)
]

# 20 giá trị cho bề dày silic (m) - đơn vị dm trong đề, convert sang m
THICKNESS_VALUES: List[Fraction] = [
    Fraction(10, 100), Fraction(11, 100), Fraction(12, 100), Fraction(13, 100), Fraction(14, 100),
    Fraction(15, 100), Fraction(16, 100), Fraction(17, 100), Fraction(18, 100), Fraction(19, 100),
    Fraction(20, 100), Fraction(21, 100), Fraction(22, 100), Fraction(23, 100), Fraction(24, 100),
    Fraction(25, 100), Fraction(26, 100), Fraction(27, 100), Fraction(28, 100), Fraction(29, 100)
]

# 20 giá trị cho chiều dài máng (m)
LENGTH_VALUES: List[Fraction] = [
    Fraction(25, 10), Fraction(26, 10), Fraction(27, 10), Fraction(28, 10), Fraction(29, 10),
    Fraction(30, 10), Fraction(31, 10), Fraction(32, 10), Fraction(33, 10), Fraction(34, 10),
    Fraction(35, 10), Fraction(36, 10), Fraction(37, 10), Fraction(38, 10), Fraction(39, 10),
    Fraction(40, 10), Fraction(41, 10), Fraction(42, 10), Fraction(43, 10), Fraction(44, 10)
]

# 20 giá trị cho số máng
NUM_TROUGHS_VALUES: List[int] = [
    60, 65, 70, 75, 80, 85, 90, 95, 100, 105,
    110, 115, 120, 125, 130, 135, 140, 145, 150, 155
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
    return str(value).replace(".", ",")


def format_fraction_latex(frac: Fraction) -> str:
    """Format Fraction thành LaTeX dạng phân số"""
    if frac.denominator == 1:
        return str(frac.numerator)
    return rf"\dfrac{{{frac.numerator}}}{{{frac.denominator}}}"


def dm_to_m_str(dm_value: Fraction) -> str:
    """Convert dm value to m and format as Vietnamese string"""
    m_value = dm_value  # Already in m
    return format_fraction_vn(m_value)


# ==============================================================================
# HÀM TÍNH TOÁN HÌNH HỌC
# ==============================================================================

def parabola_segment_area(base: sp.Expr, height: sp.Expr) -> sp.Expr:
    """
    Diện tích mặt cắt parabol:
    S = (2/3) × base × height
    """
    return sp.Rational(2, 3) * base * height


def cross_section_area(width: sp.Expr, height: sp.Expr, thickness: sp.Expr) -> sp.Expr:
    """
    Diện tích thiết diện = S_large - S_small
    S_large = (2/3) * (width + 2*thickness) * height
    S_small = (2/3) * width * (height - thickness)
    """
    s_large = parabola_segment_area(width + 2 * thickness, height)
    s_small = parabola_segment_area(width, height - thickness)
    return s_large - s_small


def trough_volume(cross_section: sp.Expr, length: sp.Expr) -> sp.Expr:
    """
    Thể tích một máng = thiết diện × chiều dài
    V = ∫₀^length S_td dx = S_td × length
    """
    return cross_section * length


def total_volume(volume_one: sp.Expr, num_troughs: int) -> sp.Expr:
    """
    Tổng thể tích = thể tích một máng × số máng
    """
    return volume_one * num_troughs


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

TIKZ_DIAGRAM_TEMPLATE = r"""
\begin{tikzpicture}[scale=1, >=stealth]
   \coordinate (P4) at (0,0);
   \coordinate (P5) at (0.6,0);
   \coordinate (P6) at (4.9,0);
   \coordinate (P7) at (5.5,0);
   \coordinate (P8) at (2.75,0.85);
   \coordinate (P9) at (2.75,1.4);
   \coordinate (P10) at (8.7,1.4);
   \coordinate (PD11) at (9.3,1.4);
   \coordinate (P12) at (14.2,1.4);
   \coordinate (PD13) at (13.6,1.4);
   \coordinate (P14) at (11.45,2.8);
   \coordinate (PD15) at (11.45,2.25);
   
   \draw (P4) .. controls +(45:0.919) and +(180:1) .. (P9) .. controls (3.7,1.4) and (4.9,0.7) .. (P7) -- (P6) .. controls +(138.37:0.602) and +(0:0.9) .. (P8) .. controls (1.95,0.85) and (1.05,0.4) .. (P5) -- (P4) -- cycle;
   \draw (P10) .. controls +(47.29:0.885) and +(180:1.05) .. (P14) .. controls (12.55,2.8) and (13.45,2.05) .. (P12) -- (PD13) .. controls +(143.13:0.75) and +(0:0.8) .. (PD15) .. controls (10.7,2.25) and (9.9,1.85) .. (PD11) -- (P10) -- cycle;
   \draw (P9) -- (P14);
   \draw (P7) -- (P12);
   \draw [dashed] (PD13) -- (P6);
   \draw [dashed] (P5) -- (PD11);
   \draw [dashed] (P10) -- (P4);
\end{tikzpicture}
"""


TEMPLATE_QUESTION = Template(r"""Một nhà máy nhiệt điện sử dụng ${num_troughs} máng Parabol thu nhiệt năng lượng mặt trời có cùng kích thước, bề mặt cong đều nhau (tham khảo hình vẽ). Mỗi máng có chiều rộng \(${width} \text{ m}\), bề dày của khối silic làm mặt máng là \(${thickness_dm} \text{ dm}\), chiều dài \(${length} \text{ m}\). Đặt máng tiếp giáp mặt đất có điểm cao nhất của khối silic làm mặt máng so với mặt đất là \(${height_dm} \text{ dm}\). Khi đó thể tích của khối silic làm ${num_troughs} mặt máng bằng bao nhiêu mét khối (làm tròn đến hàng phần mười)?

\begin{center}
${tikz_diagram}
\end{center}
""")


TEMPLATE_SOLUTION = Template(r"""
Lời giải:

Đổi đơn vị: bề dày \(${thickness_dm} \text{ dm} = ${thickness_m} \text{ m}\), độ cao \(${height_dm} \text{ dm} = ${height_m} \text{ m}\).

Diện tích mặt cắt parabol lớn (mặt ngoài):

\[S_1 = \dfrac{2}{3} \cdot (${width} + 2 \cdot ${thickness_m}) \cdot ${height_m} = ${s_large}\]

Diện tích mặt cắt parabol nhỏ (mặt trong, sau khi trừ bề dày):

\[S_2 = \dfrac{2}{3} \cdot ${width} \cdot (${height_m} - ${thickness_m}) = \dfrac{2}{3} \cdot ${width} \cdot ${height_inner} = ${s_small}\]

Diện tích thiết diện (phần silic):

\[S_{td} = S_1 - S_2 = ${s_large} - ${s_small} = ${s_td}\]

Thể tích của một máng là:

\[V_1 = \displaystyle\int\limits_0^{${length}} ${s_td} \, dx = ${s_td} \cdot ${length} = ${volume_one}\]

Vậy thể tích của ${num_troughs} máng là:

\[V = ${num_troughs} \cdot ${volume_one} = ${answer_vn} \text{ m}^3\]

Đáp án: ${answer_vn} | ${answer}
""")


# ==============================================================================
# LỚP CƠ SỞ VÀ CÀI ĐẶT
# ==============================================================================

class BaseParabolicTroughQuestion(ABC):
    """Lớp cơ sở cho các bài toán máng parabol"""
    
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
        question_content += solution + "\n"
        return question_content, self.correct_answer
    
    @staticmethod
    def create_latex_document(
        questions_data: List[Tuple[str, str]],
        title: str = "Bài tập Thể tích Máng Parabol",
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
\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing,intersections}}

\title{{{title}}}
\author{{Generator}}
\date{{\today}}

\begin{{document}}
\maketitle

{questions_content}

\end{{document}}
"""
        return latex_document


class ParabolicTroughVolumeQuestion(BaseParabolicTroughQuestion):
    """Bài toán tính thể tích máng parabol"""
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên với constraint hợp lệ"""
        # Chọn ngẫu nhiên các tham số
        width = random.choice(WIDTH_VALUES)
        height = random.choice(HEIGHT_VALUES)
        length = random.choice(LENGTH_VALUES)
        num_troughs = random.choice(NUM_TROUGHS_VALUES)
        
        # Chọn thickness sao cho thickness < height
        valid_thickness = [t for t in THICKNESS_VALUES if t < height]
        if not valid_thickness:
            # Fallback nếu không có thickness hợp lệ
            thickness = Fraction(1, 10)
        else:
            thickness = random.choice(valid_thickness)
        
        return {
            "width": width,
            "height": height,  # in m
            "thickness": thickness,  # in m
            "length": length,
            "num_troughs": num_troughs,
        }
    
    def calculate_answer(self) -> str:
        """Tính thể tích tổng và làm tròn đến hàng phần mười"""
        params = self.parameters
        
        # Convert to SymPy for exact calculation
        width = sp.Rational(params["width"].numerator, params["width"].denominator)
        height = sp.Rational(params["height"].numerator, params["height"].denominator)
        thickness = sp.Rational(params["thickness"].numerator, params["thickness"].denominator)
        length = sp.Rational(params["length"].numerator, params["length"].denominator)
        num_troughs = params["num_troughs"]
        
        # Calculate
        s_td = cross_section_area(width, height, thickness)
        v_one = trough_volume(s_td, length)
        v_total = total_volume(v_one, num_troughs)
        
        # Round to 1 decimal
        v_total_float = float(v_total.evalf())
        v_rounded = round(v_total_float, 1)
        
        return to_decimal_comma(v_rounded)
    
    def generate_tikz_diagram(self) -> str:
        """Tạo TikZ diagram"""
        return TIKZ_DIAGRAM_TEMPLATE
    
    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        params = self.parameters
        
        # Convert m to dm for display (height and thickness)
        height_dm = params["height"] * 10  # m to dm
        thickness_dm = params["thickness"] * 10  # m to dm
        
        return TEMPLATE_QUESTION.substitute(
            num_troughs=params["num_troughs"],
            width=format_fraction_vn(params["width"]),
            thickness_dm=format_fraction_vn(thickness_dm),
            length=format_fraction_vn(params["length"]),
            height_dm=format_fraction_vn(height_dm),
            tikz_diagram=self.generate_tikz_diagram(),
        )
    
    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết"""
        params = self.parameters
        
        # Convert to SymPy
        width = sp.Rational(params["width"].numerator, params["width"].denominator)
        height = sp.Rational(params["height"].numerator, params["height"].denominator)
        thickness = sp.Rational(params["thickness"].numerator, params["thickness"].denominator)
        length = sp.Rational(params["length"].numerator, params["length"].denominator)
        num_troughs = params["num_troughs"]
        
        # Calculate intermediate values
        s_large = parabola_segment_area(width + 2 * thickness, height)
        height_inner = height - thickness
        s_small = parabola_segment_area(width, height_inner)
        s_td = s_large - s_small
        v_one = trough_volume(s_td, length)
        v_total = total_volume(v_one, num_troughs)
        
        # Round final answer
        v_total_float = float(v_total.evalf())
        v_rounded = round(v_total_float, 1)
        
        # Convert m to dm for display
        height_dm = params["height"] * 10
        thickness_dm = params["thickness"] * 10
        
        # Format as fractions
        def fmt_frac(val):
            if hasattr(val, 'p') and hasattr(val, 'q'):
                if val.q == 1:
                    return str(val.p)
                return rf"\dfrac{{{val.p}}}{{{val.q}}}"
            return str(val)
        
        return TEMPLATE_SOLUTION.substitute(
            width=format_fraction_vn(params["width"]),
            height_m=format_fraction_vn(params["height"]),
            thickness_m=format_fraction_vn(params["thickness"]),
            height_dm=format_fraction_vn(height_dm),
            thickness_dm=format_fraction_vn(thickness_dm),
            length=format_fraction_vn(params["length"]),
            num_troughs=num_troughs,
            height_inner=format_fraction_vn(Fraction(height_inner.p, height_inner.q)),
            s_large=fmt_frac(s_large),
            s_small=fmt_frac(s_small),
            s_td=fmt_frac(s_td),
            volume_one=fmt_frac(v_one),
            answer=str(v_rounded),
            answer_vn=str(v_rounded).replace(".", ","),
        )


# ==============================================================================
# HÀM MAIN
# ==============================================================================

def main():
    """
    Hàm main để chạy generator
    Usage: python parabolic_trough_questions.py <num_questions> [seed]
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
        
        logging.info(f"Đang sinh {num_questions} câu hỏi máng parabol...")
        
        questions_data: List[Tuple[str, str]] = []
        
        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            question = ParabolicTroughVolumeQuestion(config)
            question_content, correct_answer = question.generate_question_only(i + 1)
            questions_data.append((question_content, correct_answer))
            logging.info(f"  Câu {i + 1}: Đáp án = {correct_answer} m³")
        
        latex_content = BaseParabolicTroughQuestion.create_latex_document(
            questions_data,
            title="Bài tập Thể tích Máng Parabol"
        )
        
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "parabolic_trough_questions.tex")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")
        
        print("\n=== ĐÁP ÁN ===")
        for i, (_, answer) in enumerate(questions_data):
            print(f"Câu {i + 1}: {answer} m³")
        
    except ValueError as e:
        print(f"Lỗi: Tham số không hợp lệ - {e}")
        print("Usage: python parabolic_trough_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")
        raise


if __name__ == "__main__":
    main()
