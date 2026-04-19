"""
Hệ thống sinh đề toán về thể tích khối tròn xoay
Bài toán: Quay miền H giới hạn bởi đường tròn đường kính AB và cung tròn tâm A quanh trục AB
Công thức: V = π∫[K→B](AB·x - x²)dx - π∫[K→D](AM² - x²)dx
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


# 20 giá trị cho AB (đường kính, cm) - chọn số chẵn để KB = AB - AK đẹp
AB_VALUES: List[Fraction] = [
    Fraction(6), Fraction(8), Fraction(10), Fraction(12), Fraction(14),
    Fraction(16), Fraction(18), Fraction(20), Fraction(22), Fraction(24),
    Fraction(26), Fraction(28), Fraction(30), Fraction(32), Fraction(34),
    Fraction(36), Fraction(38), Fraction(40), Fraction(42), Fraction(44)
]

# 20 giá trị cho AK (khoảng cách từ A đến K, cm)
# Constraint: AK < AB để K nằm giữa A và B
AK_VALUES: List[Fraction] = [
    Fraction(1), Fraction(2), Fraction(3), Fraction(4), Fraction(5),
    Fraction(6), Fraction(7), Fraction(8), Fraction(9), Fraction(10),
    Fraction(11), Fraction(12), Fraction(13), Fraction(14), Fraction(15),
    Fraction(16), Fraction(17), Fraction(18), Fraction(19), Fraction(20)
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


def format_sqrt_latex(val: sp.Expr) -> str:
    """Format biểu thức sqrt thành LaTeX"""
    return sp.latex(val)


# ==============================================================================
# HÀM TÍNH TOÁN HÌNH HỌC
# ==============================================================================

def calculate_MK_squared(AK: sp.Expr, KB: sp.Expr) -> sp.Expr:
    """
    MK² = AK × KB (hệ thức lượng trong tam giác vuông)
    Tam giác AMB vuông tại M, MK là đường cao hạ từ M xuống AB
    """
    return AK * KB


def calculate_AM_squared(AK: sp.Expr, MK_squared: sp.Expr) -> sp.Expr:
    """
    AM² = AK² + MK² (Pythagoras trong tam giác AMK vuông tại K)
    """
    return AK**2 + MK_squared


def calculate_AD(AM_squared: sp.Expr) -> sp.Expr:
    """
    AD = AM (vì D nằm trên đường tròn tâm A bán kính AM)
    AD = √(AM²)
    """
    return sp.sqrt(AM_squared)


def volume_semicircle_part(AB: sp.Expr, K: sp.Expr, B: sp.Expr) -> sp.Expr:
    """
    Thể tích phần từ bán cầu (đường tròn đường kính AB):
    V1 = π ∫[K→B] (AB·x - x²) dx
    
    Đường tròn đường kính AB có tâm (AB/2, 0) và bán kính AB/2:
    (x - AB/2)² + y² = (AB/2)²
    y² = (AB/2)² - (x - AB/2)² = AB·x - x²
    """
    x = sp.Symbol('x')
    integrand = AB * x - x**2
    return sp.pi * sp.integrate(integrand, (x, K, B))


def volume_arc_part(AM_squared: sp.Expr, K: sp.Expr, D: sp.Expr) -> sp.Expr:
    """
    Thể tích phần từ cung tròn tâm A:
    V2 = π ∫[K→D] (AM² - x²) dx
    
    Đường tròn tâm A bán kính AM:
    x² + y² = AM²
    y² = AM² - x²
    """
    x = sp.Symbol('x')
    integrand = AM_squared - x**2
    return sp.pi * sp.integrate(integrand, (x, K, D))


def total_volume(V1: sp.Expr, V2: sp.Expr) -> sp.Expr:
    """
    Thể tích khối tròn xoay = V1 - V2
    (Phần bán cầu lớn trừ phần tử cung tròn nhỏ)
    """
    return V1 - V2


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

# TikZ đề bài (không có hệ tọa độ, giá trị cố định AB=8, AK=3)
TIKZ_QUESTION_TEMPLATE = r"""
\begin{tikzpicture}[scale=0.45, line join=round, line cap=round, >=stealth, thick]
  % Giá trị cố định: AB=8, AK=3, KB=5, MK=sqrt(15), AM=sqrt(24)=2sqrt(6)
  \def\ABval{8}
  \def\AKval{3}
  \def\radius{4}       % AB/2
  \def\MK{3.873}       % sqrt(15)
  \def\AM{4.899}       % sqrt(24)
  
  % Fill miền hình trăng lưỡi liềm (màu xám)
  \begin{scope}
    \clip (\radius, 0) circle (\radius);
    \fill[gray!40] (\radius, 0) circle (\radius);
    \fill[white] (0,0) circle (\AM);
  \end{scope}
  
  % Đường tròn đường kính AB
  \draw[black, thick] (\radius, 0) circle (\radius);
  
  % Cung tròn tâm A bán kính AM
  \draw[black, thick] (0,0) ++({-atan2(\MK, \AKval)}:\AM) arc[start angle={-atan2(\MK, \AKval)}, end angle={atan2(\MK, \AKval)}, radius=\AM];
  
  % Đường kẻ từ A qua K đến B
  \draw[thick] (0,0) -- (\ABval, 0);
  
  % Đường đứt nét từ N qua K đến M
  \draw[dashed, gray!50] (\AKval, -\MK) -- (\AKval, \MK);
  
  % Điểm A, K, B
  \fill (0, 0) circle (2pt) node[left] {$A$};
  \fill (\AKval, 0) circle (2pt) node[below] {$K$};
  \fill (\ABval, 0) circle (2pt) node[right] {$B$};
\end{tikzpicture}
"""
# TikZ lời giải (có hệ tọa độ, giá trị cố định)
TIKZ_SOLUTION_TEMPLATE = r"""
\begin{tikzpicture}[scale=0.45, line join=round, line cap=round, >=stealth, thick]
  % Giá trị cố định: AB=8, AK=3
  \def\ABval{8}
  \def\AKval{3}
  \def\radius{4}       % AB/2
  \def\MK{3.873}       % sqrt(15)
  \def\AM{4.899}       % sqrt(24)
  
  % Vẽ trục tọa độ Oxy với gốc tại A
  \draw[->] (-6, 0) -- (\ABval + 1, 0) node[right] {$x$};
  \draw[->] (0, -\AM - 0.5) -- (0, \AM + 0.5) node[above] {$y$};
  
  % Fill miền hình trăng lưỡi liềm (màu xám)
  \begin{scope}
    \clip (\radius, 0) circle (\radius);
    \fill[gray!40] (\radius, 0) circle (\radius);
    \fill[white] (0,0) circle (\AM);
  \end{scope}
  
  % Đường tròn đường kính AB
  \draw[black, thick] (\radius, 0) circle (\radius);
  
  % Đường tròn tâm A bán kính AM (vẽ hết)
  \draw[black, thick] (0,0) circle (\AM);
  
  % Đường kẻ từ A đến B
  \draw[thick] (0,0) -- (\ABval, 0);
  
  % Đoạn thẳng AM
  \draw[thick] (0, 0) -- (\AKval, \MK);
  
  % Đoạn thẳng BM
  \draw[thick] (\ABval, 0) -- (\AKval, \MK);
  
  % Đường đứt nét từ K lên M
  \draw[dashed, gray!50] (\AKval, 0) -- (\AKval, \MK);
  
  % Điểm A, K, D, B, M
  \fill (0, 0) circle (2pt) node[below left] {$A$};
  \fill (\AKval, 0) circle (2pt) node[below] {$K$};
  \fill (\radius, 0) circle (2pt) node[below] {$D$};
  \fill (\ABval, 0) circle (2pt) node[below right] {$B$};
  \fill (\AKval, \MK) circle (2pt) node[above right] {$M$};
\end{tikzpicture}
"""


TEMPLATE_QUESTION = Template(r"""Một khối tròn xoay được tạo thành khi quay hình phẳng \((H)\) (phần màu xám trong hình vẽ) quanh trục \(AB\).

\begin{center}
${tikz_diagram}
\end{center}

Miền \((H)\) được giới hạn bởi đường tròn đường kính \(AB\) và cung tròn tâm \(A\). Biết \(AB = ${AB} \text{ cm}\) và điểm \(K\) trong hình vẽ thỏa mãn \(AK = ${AK} \text{ cm}\). Thể tích của khối tròn xoay đó bằng bao nhiêu \(\text{cm}^3\)? \textit{(làm tròn kết quả đến hàng đơn vị)}
""")


TEMPLATE_SOLUTION = Template(r"""
Lời giải:

\begin{center}
${tikz_solution}
\end{center}

Chọn hệ trục tọa độ như hình vẽ. Ta có \(A(0; 0)\), \(B(${AB}; 0)\), \(K(${AK}; 0)\).

Tam giác \(AMB\) vuông tại \(M\), \(MK\) là đường cao nên:
\(MK^2 = AK \cdot KB = ${AK} \cdot ${KB} = ${MK_squared}\)

Tam giác \(AMK\) vuông tại \(K\) nên:
\(AM = \sqrt{MK^2 + AK^2} = \sqrt{${MK_squared} + ${AK_squared}} = ${AM_latex}\)

Suy ra \(AD = ${AM_latex} \Rightarrow D(${AD_latex}; 0)\)

Đường tròn đường kính \(AB\) có phương trình \((x - ${half_AB})^2 + y^2 = ${half_AB_sq}\) \(\Rightarrow y = \sqrt{${AB}x - x^2}\).

Đường tròn tâm \(A\) bán kính \(AM\) có phương trình \(x^2 + y^2 = ${AM_squared}\) \(\Rightarrow y^2 = ${AM_squared} - x^2\)

Thể tích cần tìm là:
\[V = \pi \int_{${AK}}^{${AB}} \left(${AB}x - x^2\right) dx - \pi \int_{${AK}}^{${AD_latex}} \left(${AM_squared} - x^2\right) dx \approx ${answer} \text{ cm}^3\]

Đáp án: ${answer}
""")


# ==============================================================================
# LỚP CƠ SỞ VÀ CÀI ĐẶT
# ==============================================================================

class BaseSphereRotationQuestion(ABC):
    """Lớp cơ sở cho các bài toán khối tròn xoay"""
    
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
        title: str = "Bài tập Thể tích Khối Tròn Xoay",
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
% \setmainfont{{Times New Roman}}
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


class SphereRotationVolumeQuestion(BaseSphereRotationQuestion):
    """Bài toán tính thể tích khối tròn xoay"""
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên với constraint hợp lệ"""
        # Chọn AB trước
        AB = random.choice(AB_VALUES)
        
        # Chọn AK sao cho AK < AB (K nằm giữa A và B)
        valid_AK = [ak for ak in AK_VALUES if ak < AB]
        if not valid_AK:
            AK = Fraction(1)
        else:
            AK = random.choice(valid_AK)
        
        return {
            "AB": AB,
            "AK": AK,
        }
    
    def calculate_answer(self) -> str:
        """Tính thể tích và làm tròn đến hàng đơn vị"""
        params = self.parameters
        
        # Convert to SymPy
        AB = sp.Rational(params["AB"].numerator, params["AB"].denominator)
        AK = sp.Rational(params["AK"].numerator, params["AK"].denominator)
        KB = AB - AK
        
        # Tính các giá trị trung gian
        MK_squared = calculate_MK_squared(AK, KB)
        AM_squared = calculate_AM_squared(AK, MK_squared)
        AD = calculate_AD(AM_squared)
        
        # Tính thể tích
        V1 = volume_semicircle_part(AB, AK, AB)
        V2 = volume_arc_part(AM_squared, AK, AD)
        V_total = total_volume(V1, V2)
        
        # Làm tròn đến hàng đơn vị
        V_float = float(V_total.evalf())
        V_rounded = round(V_float)
        
        return str(V_rounded)
    
    def generate_tikz_question(self) -> str:
        """Tạo TikZ cho đề bài - sử dụng template cố định"""
        return TIKZ_QUESTION_TEMPLATE
    
    def generate_tikz_solution(self) -> str:
        """Tạo TikZ cho lời giải - sử dụng template cố định"""
        return TIKZ_SOLUTION_TEMPLATE
    
    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        params = self.parameters
        
        return TEMPLATE_QUESTION.substitute(
            AB=format_fraction_vn(params["AB"]),
            AK=format_fraction_vn(params["AK"]),
            tikz_diagram=self.generate_tikz_question(),
        )
    
    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết"""
        params = self.parameters
        
        # Convert to SymPy
        AB = sp.Rational(params["AB"].numerator, params["AB"].denominator)
        AK = sp.Rational(params["AK"].numerator, params["AK"].denominator)
        KB = AB - AK
        
        # Tính các giá trị
        MK_squared = calculate_MK_squared(AK, KB)
        AK_squared = AK**2
        AM_squared = calculate_AM_squared(AK, MK_squared)
        AD = calculate_AD(AM_squared)
        
        half_AB = AB / 2
        half_AB_sq = half_AB**2
        
        # Format AM và AD
        AM_simplified = sp.sqrt(AM_squared)
        AM_latex = sp.latex(AM_simplified)
        AD_latex = sp.latex(AD)
        
        return TEMPLATE_SOLUTION.substitute(
            tikz_solution=self.generate_tikz_solution(),
            AB=format_fraction_vn(params["AB"]),
            AK=format_fraction_vn(params["AK"]),
            KB=format_fraction_vn(Fraction(int(KB), 1) if KB.is_integer else params["AB"] - params["AK"]),
            MK_squared=str(int(MK_squared)) if MK_squared.is_integer else sp.latex(MK_squared),
            AK_squared=str(int(AK_squared)) if AK_squared.is_integer else sp.latex(AK_squared),
            AM_squared=str(int(AM_squared)) if AM_squared.is_integer else sp.latex(AM_squared),
            AM_latex=AM_latex,
            AD_latex=AD_latex,
            half_AB=format_fraction_vn(Fraction(int(half_AB), 1) if half_AB.is_integer else Fraction(params["AB"].numerator, params["AB"].denominator * 2)),
            half_AB_sq=str(int(half_AB_sq)) if half_AB_sq.is_integer else sp.latex(half_AB_sq),
            answer=self.correct_answer,
        )


# ==============================================================================
# HÀM MAIN
# ==============================================================================

def main():
    """
    Hàm main để chạy generator
    Usage: python sphere_rotation_volume_questions.py <num_questions> [seed]
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
        
        logging.info(f"Đang sinh {num_questions} câu hỏi khối tròn xoay...")
        
        questions_data: List[Tuple[str, str]] = []
        
        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            question = SphereRotationVolumeQuestion(config)
            question_content, correct_answer = question.generate_question_only(i + 1)
            questions_data.append((question_content, correct_answer))
            logging.info(f"  Câu {i + 1}: Đáp án = {correct_answer} cm³")
        
        latex_content = BaseSphereRotationQuestion.create_latex_document(
            questions_data,
            title="Bài tập Thể tích Khối Tròn Xoay"
        )
        
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "sphere_rotation_volume_questions.tex")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")
        
        print("\n=== ĐÁP ÁN ===")
        for i, (_, answer) in enumerate(questions_data):
            print(f"Câu {i + 1}: {answer} cm³")
        
    except ValueError as e:
        print(f"Lỗi: Tham số không hợp lệ - {e}")
        print("Usage: python sphere_rotation_volume_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")
        raise


if __name__ == "__main__":
    main()
