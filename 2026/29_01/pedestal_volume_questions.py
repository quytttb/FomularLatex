"""
Hệ thống sinh đề toán về thể tích chân đế trang trí
Bài toán: Tính thể tích chân đế = Khối chóp cụt tứ giác đều - Chỏm cầu bị cắt
"""

import logging
import os
import random
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from string import Template
from typing import Any, Dict, List, Optional, Tuple
from fractions import Fraction

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


# 20 giá trị cho cạnh đáy nhỏ a1 (dạng phân số x/10 để tránh float)
# Sử dụng Fraction để giữ chính xác
A1_VALUES: List[Fraction] = [
    Fraction(50, 10), Fraction(53, 10), Fraction(56, 10), Fraction(59, 10), Fraction(62, 10),
    Fraction(65, 10), Fraction(68, 10), Fraction(71, 10), Fraction(74, 10), Fraction(77, 10),
    Fraction(80, 10), Fraction(83, 10), Fraction(86, 10), Fraction(89, 10), Fraction(92, 10),
    Fraction(95, 10), Fraction(98, 10), Fraction(101, 10), Fraction(104, 10), Fraction(107, 10)
]

# 20 giá trị cho cạnh đáy lớn a2
A2_VALUES: List[Fraction] = [
    Fraction(80, 10), Fraction(83, 10), Fraction(86, 10), Fraction(89, 10), Fraction(92, 10),
    Fraction(95, 10), Fraction(98, 10), Fraction(101, 10), Fraction(104, 10), Fraction(107, 10),
    Fraction(110, 10), Fraction(113, 10), Fraction(116, 10), Fraction(119, 10), Fraction(122, 10),
    Fraction(125, 10), Fraction(128, 10), Fraction(131, 10), Fraction(134, 10), Fraction(137, 10)
]

# 20 giá trị cho bề dày khối gỗ h
H_VALUES: List[Fraction] = [
    Fraction(10, 10), Fraction(11, 10), Fraction(12, 10), Fraction(13, 10), Fraction(14, 10),
    Fraction(15, 10), Fraction(16, 10), Fraction(17, 10), Fraction(18, 10), Fraction(19, 10),
    Fraction(20, 10), Fraction(21, 10), Fraction(22, 10), Fraction(23, 10), Fraction(24, 10),
    Fraction(25, 10), Fraction(26, 10), Fraction(27, 10), Fraction(28, 10), Fraction(29, 10)
]

# 20 giá trị cho bán kính hình cầu R
R_SPHERE_VALUES: List[Fraction] = [
    Fraction(40, 10), Fraction(42, 10), Fraction(44, 10), Fraction(46, 10), Fraction(48, 10),
    Fraction(50, 10), Fraction(52, 10), Fraction(54, 10), Fraction(56, 10), Fraction(58, 10),
    Fraction(60, 10), Fraction(62, 10), Fraction(64, 10), Fraction(66, 10), Fraction(68, 10),
    Fraction(70, 10), Fraction(72, 10), Fraction(74, 10), Fraction(76, 10), Fraction(78, 10)
]

# 20 giá trị cho bán kính mặt cắt tròn r_cut
R_CUT_VALUES: List[Fraction] = [
    Fraction(20, 10), Fraction(22, 10), Fraction(24, 10), Fraction(26, 10), Fraction(28, 10),
    Fraction(30, 10), Fraction(32, 10), Fraction(34, 10), Fraction(35, 10), Fraction(36, 10),
    Fraction(38, 10), Fraction(40, 10), Fraction(42, 10), Fraction(44, 10), Fraction(46, 10),
    Fraction(48, 10), Fraction(50, 10), Fraction(52, 10), Fraction(54, 10), Fraction(56, 10)
]


# ==============================================================================
# HÀM TIỆN ÍCH
# ==============================================================================

def format_fraction_vn(frac: Fraction) -> str:
    """Format Fraction thành dạng tiếng Việt (dùng dấu phẩy)"""
    if frac.denominator == 1:
        return str(frac.numerator)
    # Chuyển thành số thập phân và dùng dấu phẩy
    decimal_val = float(frac)
    # Loại bỏ trailing zeros
    if decimal_val == int(decimal_val):
        return str(int(decimal_val))
    formatted = f"{decimal_val:.2f}".rstrip('0').rstrip('.')
    return formatted.replace(".", ",")


def to_decimal_comma(value: Any) -> str:
    """Chuyển dấu chấm thành dấu phẩy cho số thập phân"""
    if isinstance(value, Fraction):
        return format_fraction_vn(value)
    return str(value).replace(".", ",")


# ==============================================================================
# HÀM TÍNH TOÁN HÌNH HỌC
# ==============================================================================

def frustum_volume(a1: sp.Expr, a2: sp.Expr, h: sp.Expr) -> sp.Expr:
    """
    Thể tích khối chóp cụt tứ giác đều:
    V = (1/3) * h * (S1 + S2 + sqrt(S1 * S2))
    Trong đó: S1 = a1², S2 = a2²
    """
    S1 = a1 ** 2
    S2 = a2 ** 2
    return sp.Rational(1, 3) * h * (S1 + S2 + sp.sqrt(S1 * S2))


def spherical_cap_volume_by_height(R: sp.Expr, h_cap: sp.Expr) -> sp.Expr:
    """
    Thể tích chỏm cầu theo chiều cao:
    V = π * h² * (R - h/3)
    """
    return sp.pi * h_cap**2 * (R - h_cap / 3)


def pedestal_volume(a1: sp.Expr, a2: sp.Expr, h: sp.Expr, 
                    R: sp.Expr, r_cut: sp.Expr) -> sp.Expr:
    """
    Thể tích chân đế = Thể tích khối chóp cụt - Thể tích chỏm cầu
    """
    V_frustum = frustum_volume(a1, a2, h)
    OH = sp.sqrt(R**2 - r_cut**2)
    h_cap = R - OH
    V_cap = spherical_cap_volume_by_height(R, h_cap)
    return V_frustum - V_cap


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

TIKZ_DIAGRAM_TEMPLATE = r"""
\begin{tikzpicture}[line join=round, line cap=round,>=stealth,thick]
  % Hình trái - Khối chóp cụt
  \coordinate (A) at (0,0);
  \coordinate (B) at (-1.5,-1);
  \coordinate (D) at (4,0);
  \coordinate (C) at ($(B)+(D)-(A)$);
  \coordinate (O) at ($(A)!0.5!(C)$);
  \coordinate (I) at ($(O)+(0,3.5)$);
  \coordinate (A') at ([scale around={0.71:(I)}] A);
  \coordinate (B') at ([scale around={0.71:(I)}] B);
  \coordinate (C') at ([scale around={0.71:(I)}] C);
  \coordinate (D') at ([scale around={0.71:(I)}] D);
  \coordinate (O') at ($(A')!0.5!(C')$);
  \draw(B)--(C)--(D)--(D')--(C')--(B')--(A')--(D') (C)--(C') (B)--(B');
  \draw[dashed,thin](A')--(A)--(B) (A)--(D);
  \draw[dashed,<->](O)--(O')node[right,pos=0.3]{\tiny $HVAL$ cm};
  \coordinate (vt) at (0,0.2);
  \coordinate (A1) at ($(A')+(vt)$);
  \coordinate (D1) at ($(D')+(vt)$);
  \draw[|<->|](A1)--(D1)node[above,sloped,pos=0.5]{\tiny $A1VAL$ cm};
  \coordinate (vt1) at (0,0.1);
  \coordinate (B1) at ($(B)-(vt)$);
  \coordinate (C1) at ($(C)-(vt)$);
  \draw[|<->|](B1)--(C1)node[below,sloped,pos=0.5]{\tiny $A2VAL$ cm};
\end{tikzpicture}\hfill
\begin{tikzpicture}[line join=round, line cap=round,>=stealth,thick,scale=0.8]
  % Hình giữa - Chỏm cầu H
  \def\bk{3}
  \def\bkba{0.15}
  \def\bkbb{0.8}
  \def\ga{-50}
  \def\gb{180-\ga}
  \def\gc{0-\gb}
  \coordinate (O) at (0,0);
  \coordinate (M) at ($(O) + (\ga:\bk)$);
  \coordinate (N) at ($(O) + (\gb:\bk)$);
  \coordinate (I) at ($(M)!0.5!(N)$);
  \draw[name path=c1,dashed] (M) arc (\ga:\gb:\bk);
  \path let \p1=(I),\p2=(M),\n1={scalar(veclen(\x2-\x1,\y2-\y1)/1cm)} in \pgfextra{\xdef\bke{\n1}};
  \fill[gray](M) arc (\ga:\gc:\bk)--(N) arc (180:0:\bke cm and \bkba cm)--cycle;
  \draw[name path=c1] (M) arc (\ga:\gc:\bk);
  \draw[name path=ne1,dashed] (M) arc (0:180:\bke cm and \bkba cm) (M)--(N);
  \draw[name path=ne1] (M) arc (0:-180:\bke cm and \bkba cm);
  \draw[name path=ela,dashed] (O) ellipse (\bk cm and \bkbb cm) ($(O)-(\bk,0)$)--($(O)+(\bk,0)$);
  \coordinate (P) at ($(O) + (250:0.9*\bk)$);
  \coordinate (Q) at ($(O) + (235:1.1*\bk)$);
  \path(Q) node [left] {\Large\bf $H$};
  \draw[->](Q)--(P);
\end{tikzpicture}\hfill
\begin{tikzpicture}[line join=round, line cap=round,>=stealth,thick,rotate=90,scale=0.8]
  % Hình phải - Mặt cắt
  \def\bk{3}
  \def\bkba{0.15}
  \def\bkbb{0.8}
  \def\ga{-50}
  \def\gb{180-\ga}
  \def\gc{0-\gb}
  \coordinate (O) at (0,0);
  \coordinate (M) at ($(O) + (\ga:\bk)$);
  \coordinate (N) at ($(O) + (\gb:\bk)$);
  \coordinate (I) at ($(M)!0.5!(N)$);
  \coordinate (J) at ($(O)+(M)-(I)$);
  \draw(M) arc (\ga:\gb:\bk);
  \path let \p1=(I),\p2=(M),\n1={scalar(veclen(\x2-\x1,\y2-\y1)/1cm)} in \pgfextra{\xdef\bke{\n1}};
  \fill[gray](M) arc (\ga:-90:\bk)--(I)--cycle;
  \draw(M) arc (\ga:\gc:\bk);
  \draw(M) arc (0:180:\bke cm and \bkba cm);
  \draw[dashed](M) arc (0:-180:\bke cm and \bkba cm);
  \coordinate (P) at ($(O) + (250:0.9*\bk)$);
  \coordinate (Q) at ($(O) + (235:1.1*\bk)$);
  \path(Q) node [below] {\Large\bf $H$};
  \coordinate (A) at ($(O) + (180:\bk)$);
  \coordinate (B) at ($(O) + (0:\bk)$);
  \coordinate (C) at ($(O) + (-90:\bk)$);
  \coordinate (D) at ($(O) + (90:\bk)$);
  \draw(B) arc (0:180:\bk cm and \bkbb cm);
  \draw[dashed](B) arc (0:-180:\bk cm and \bkbb cm);
  \draw[dashed](J)--(M)--(N) (C)--(D) (A)--(B);
  \draw[->](Q)--(P);
  \draw[->](C)--($(C)-(0,0.5)$)node[below]{$x$};
  \draw[->](B)--($(B)+(0.5,0)$)node[right]{$y$};
  \draw(A)--($(A)-(0.5,0)$) (D)--($(D)+(0,0.5)$); 
  \path(O) node[below left]{$O$};
  \path(J) node[left=-0.05]{\tiny $RCUTVAL$};
  \path($(B)+(0.15,0)$)node[left]{\tiny $RVAL$};
\end{tikzpicture}
"""


TEMPLATE_QUESTION_PEDESTAL = Template(r"""Để đặt được một vật trang trí trên mặt bàn, người ta thiết kế một chân đế như sau. Lấy một khối gỗ có dạng khối chóp cụt tứ giác đều với độ dài hai cạnh đáy lần lượt bằng \(${a1} \mathrm{~cm}\) và \(${a2} \mathrm{~cm}\), bề dày của khối gỗ bằng \(${h_frustum} \mathrm{~cm}\). Sau đó khoét bỏ đi một phần của khối gỗ sao cho phần đó có dạng vật thể \(H\), ở đó \(H\) nhận được bằng cách cắt khối cầu bán kính \(${R_sphere} \mathrm{~cm}\) bởi một mặt phẳng cắt mà mặt cắt là hình tròn bán kính \(${r_cut} \mathrm{~cm}\) (xem hình dưới).

\begin{center}
${tikz_diagram}
\end{center}

 Thể tích của khối chân đế bằng bao nhiêu centimét khối (không làm tròn kết quả các phép tính trung gian, chỉ làm tròn kết quả cuối cùng đến hàng phần mười)?
""")


TEMPLATE_SOLUTION_PEDESTAL = Template(r"""
Lời giải:

Thể tích khối gỗ là \(V_1 = \dfrac{1}{3}.${h_frustum}.\left(${a2}^2 + \sqrt{${a2}^2.${a1}^2} + ${a1}^2\right)\).

Phương trình đường tròn tâm \(O\) bán kính \(R = ${R_sphere}\) là:

\(x^2 + y^2 = ${R_sphere}^2 \Rightarrow y^2 = ${R_sphere}^2 - x^2\).

Ta có: \(OH = \sqrt{${R_sphere}^2 - ${r_cut}^2} = \sqrt{${R_sq_minus_r_sq}}\)

Thể tích chỏm cầu là \(V_H = \pi.\displaystyle\int\limits_{\sqrt{${R_sq_minus_r_sq}}}^{${R_sphere}} \left(${R_sphere}^2 - x^2\right) \mathrm{d}x\).

Vậy thể tích của chân đế là

\[V = V_1 - V_H = \dfrac{1}{3}.${h_frustum}.\left(${a2}^2 + \sqrt{${a2}^2.${a1}^2} + ${a1}^2\right) - \pi.\displaystyle\int\limits_{\sqrt{${R_sq_minus_r_sq}}}^{${R_sphere}} \left(${R_sphere}^2 - x^2\right) \mathrm{d}x \approx ${answer_vn}\]

Đáp án: ${answer_vn} | ${answer}
""")


# ==============================================================================
# LỚP CƠ SỞ VÀ CÀI ĐẶT
# ==============================================================================

class BasePedestalQuestion(ABC):
    """Lớp cơ sở cho các bài toán chân đế"""
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.correct_answer: Optional[str] = None
        self.config = config or GeneratorConfig()
    
    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh các tham số cho bài toán"""
        pass
    
    @abstractmethod
    def calculate_answer(self) -> str:
        """Tính đáp án"""
        pass
    
    @abstractmethod
    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        pass
    
    @abstractmethod
    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết"""
        pass
    
    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        """Tạo câu hỏi chỉ có đề bài và lời giải"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        question_text = self.generate_question_text().strip()
        solution = self.generate_solution().strip()
        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += solution + "\n"
        return question_content, self.correct_answer
    
    @staticmethod
    def create_latex_document_with_format(
        questions_data: List[Tuple[str, str]],
        title: str = "Bài tập Thể tích Chân đế",
    ) -> str:
        """Tạo tài liệu LaTeX hoàn chỉnh"""
        
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


class PedestalVolumeQuestion(BasePedestalQuestion):
    """Bài toán tính thể tích chân đế"""
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên với constraint hợp lệ"""
        max_attempts = 100
        
        for _ in range(max_attempts):
            a1 = random.choice(A1_VALUES)
            a2 = random.choice(A2_VALUES)
            h = random.choice(H_VALUES)
            R = random.choice(R_SPHERE_VALUES)
            r_cut = random.choice(R_CUT_VALUES)
            
            # Constraints: a2 > a1 và r_cut < R
            if a2 > a1 and r_cut < R:
                return {
                    "a1": a1,
                    "a2": a2,
                    "h_frustum": h,
                    "R_sphere": R,
                    "r_cut": r_cut,
                }
        
        # Fallback với giá trị mặc định từ đề mẫu
        return {
            "a1": Fraction(74, 10),
            "a2": Fraction(104, 10),
            "h_frustum": Fraction(15, 10),
            "R_sphere": Fraction(58, 10),
            "r_cut": Fraction(35, 10),
        }
    
    def calculate_answer(self) -> str:
        """Tính thể tích chân đế và làm tròn đến hàng phần mười"""
        params = self.parameters
        
        # Chuyển Fraction sang SymPy Rational để tính toán chính xác
        a1 = sp.Rational(params["a1"].numerator, params["a1"].denominator)
        a2 = sp.Rational(params["a2"].numerator, params["a2"].denominator)
        h = sp.Rational(params["h_frustum"].numerator, params["h_frustum"].denominator)
        R = sp.Rational(params["R_sphere"].numerator, params["R_sphere"].denominator)
        r = sp.Rational(params["r_cut"].numerator, params["r_cut"].denominator)
        
        # Tính thể tích
        V_exact = pedestal_volume(a1, a2, h, R, r)
        
        # Chuyển sang số và làm tròn
        V_numeric = float(V_exact.evalf())
        V_rounded = round(V_numeric, 1)
        
        return to_decimal_comma(V_rounded)
    
    def generate_tikz_diagram(self) -> str:
        """Tạo TikZ diagram với các giá trị cụ thể"""
        params = self.parameters
        
        tikz = TIKZ_DIAGRAM_TEMPLATE
        tikz = tikz.replace("$A1VAL$", format_fraction_vn(params["a1"]))
        tikz = tikz.replace("$A2VAL$", format_fraction_vn(params["a2"]))
        tikz = tikz.replace("$HVAL$", format_fraction_vn(params["h_frustum"]))
        tikz = tikz.replace("$RVAL$", format_fraction_vn(params["R_sphere"]))
        tikz = tikz.replace("$RCUTVAL$", format_fraction_vn(params["r_cut"]))
        
        return tikz
    
    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        params = self.parameters
        tikz = self.generate_tikz_diagram()
        
        return TEMPLATE_QUESTION_PEDESTAL.substitute(
            a1=format_fraction_vn(params["a1"]),
            a2=format_fraction_vn(params["a2"]),
            h_frustum=format_fraction_vn(params["h_frustum"]),
            R_sphere=format_fraction_vn(params["R_sphere"]),
            r_cut=format_fraction_vn(params["r_cut"]),
            tikz_diagram=tikz,
        )
    
    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết - format theo chuẩn AZOTA"""
        params = self.parameters
        
        # Chuyển sang SymPy Rational để tính toán symbolic chính xác
        a1 = sp.Rational(params["a1"].numerator, params["a1"].denominator)
        a2 = sp.Rational(params["a2"].numerator, params["a2"].denominator)
        h = sp.Rational(params["h_frustum"].numerator, params["h_frustum"].denominator)
        R = sp.Rational(params["R_sphere"].numerator, params["R_sphere"].denominator)
        r = sp.Rational(params["r_cut"].numerator, params["r_cut"].denominator)
        
        # Helper function để format số thành dạng thập phân đẹp (dùng dấu phẩy)
        def fmt(val, decimals=2):
            """Format giá trị thành chuỗi thập phân với dấu phẩy"""
            num = float(val.evalf()) if hasattr(val, 'evalf') else float(val)
            # Làm tròn và loại bỏ trailing zeros
            formatted = f"{round(num, decimals):.{decimals}f}".rstrip('0').rstrip('.')
            return formatted.replace(".", ",")
        
        # Tính các giá trị trung gian
        R_sq_minus_r_sq = R**2 - r**2
        
        V_frustum = frustum_volume(a1, a2, h)
        V_frustum_numeric = float(V_frustum.evalf())
        
        OH = sp.sqrt(R_sq_minus_r_sq)
        h_cap = R - OH
        
        V_cap = spherical_cap_volume_by_height(R, h_cap)
        V_cap_numeric = float(V_cap.evalf())
        
        V_final = V_frustum_numeric - V_cap_numeric
        V_rounded = round(V_final, 1)
        
        return TEMPLATE_SOLUTION_PEDESTAL.substitute(
            a1=format_fraction_vn(params["a1"]),
            a2=format_fraction_vn(params["a2"]),
            h_frustum=format_fraction_vn(params["h_frustum"]),
            R_sphere=format_fraction_vn(params["R_sphere"]),
            r_cut=format_fraction_vn(params["r_cut"]),
            R_sq_minus_r_sq=fmt(R_sq_minus_r_sq),
            answer=str(V_rounded),
            answer_vn=str(V_rounded).replace(".", ","),
        )


# ==============================================================================
# HÀM MAIN
# ==============================================================================

def get_available_question_types():
    """Trả về danh sách các loại câu hỏi có sẵn"""
    return [
        PedestalVolumeQuestion,
    ]


def main():
    """
    Hàm main để chạy generator
    Usage: python pedestal_volume_questions.py <num_questions> [seed]
    """
    try:
        # Parse arguments
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else None
        
        # Lấy seed từ environment variable nếu có
        if seed is None:
            seed = os.environ.get("OPT_SEED")
            if seed:
                seed = int(seed)
        
        if seed is not None:
            random.seed(seed)
            logging.info(f"Sử dụng seed: {seed}")
        
        logging.info(f"Đang sinh {num_questions} câu hỏi thể tích chân đế...")
        
        questions_data: List[Tuple[str, str]] = []
        
        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            question = PedestalVolumeQuestion(config)
            question_content, correct_answer = question.generate_question_only(i + 1)
            questions_data.append((question_content, correct_answer))
            logging.info(f"  Câu {i + 1}: Đáp án = {correct_answer} cm³")
        
        # Tạo tài liệu LaTeX
        latex_content = BasePedestalQuestion.create_latex_document_with_format(
            questions_data,
            title="Bài tập Thể tích Chân đế"
        )
        
        # Ghi file
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "pedestal_volume_questions.tex")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")
        
        # In đáp án
        print("\n=== ĐÁP ÁN ===")
        for i, (_, answer) in enumerate(questions_data):
            print(f"Câu {i + 1}: {answer} cm³")
        
    except ValueError as e:
        print(f"Lỗi: Tham số không hợp lệ - {e}")
        print("Usage: python pedestal_volume_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")
        raise


if __name__ == "__main__":
    main()
