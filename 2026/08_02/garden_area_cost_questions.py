"""
Hệ thống sinh đề toán về khu vườn hình tròn - tính chi phí trồng hoa
Bài toán: Tính diện tích S₁ (parabol + đường tròn), S₂ (hình bán nguyệt) → tổng chi phí
Dạng câu hỏi: Điền số (kết quả làm tròn đến hàng phần mười, đơn vị: triệu đồng)
"""

import logging
import math
import os
import random
import sys
from dataclasses import dataclass
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


# 20 bộ ba Pytago (R, a, h) thỏa R² = a² + h²
# Parabol đi qua O(0,0) và (±a, h), với h = √(R² - a²)
PYTHAGOREAN_SETS: List[Tuple[int, int, int]] = [
    (5, 4, 3),
    (5, 3, 4),
    (10, 8, 6),
    (10, 6, 8),
    (13, 12, 5),
    (13, 5, 12),
    (15, 12, 9),
    (15, 9, 12),
    (17, 15, 8),
    (17, 8, 15),
    (20, 16, 12),
    (20, 12, 16),
    (25, 24, 7),
    (25, 20, 15),
    (25, 7, 24),
    (26, 24, 10),
    (26, 10, 24),
    (29, 20, 21),
    (29, 21, 20),
    (30, 24, 18),
]

# Bán trục nhỏ elip (chiều sâu dưới tâm, sẽ lọc runtime: < R)
B_ELLIPSE_VALUES: List[int] = [3, 4, 5, 6, 7, 8, 9, 10]

# Chi phí trồng hoa (đồng/m²)
COST_ROSE_VALUES: List[int] = [80_000, 90_000, 100_000, 110_000, 120_000]
COST_LILY_VALUES: List[int] = [120_000, 130_000, 140_000, 150_000, 160_000]


# ==============================================================================
# HÀM TIỆN ÍCH
# ==============================================================================

def format_decimal_vn(val: float, decimals: int = 1) -> str:
    """Format số thập phân với dấu phẩy"""
    formatted = f"{val:.{decimals}f}".rstrip('0').rstrip('.')
    return formatted.replace(".", ",")


def format_decimal_dot(val: float, decimals: int = 1) -> str:
    """Format số thập phân với dấu chấm"""
    return f"{val:.{decimals}f}".rstrip('0').rstrip('.')


def format_cost_vn(val: int) -> str:
    """Format chi phí dạng 100.000"""
    return f"{val:,}".replace(",", ".")


# ==============================================================================
# HÀM TÍNH TOÁN
# ==============================================================================

def calculate_S1(R: int, a: int, h: int) -> float:
    """
    Tính S₁: diện tích giới hạn bởi parabol, đường tròn, và x = ±a
    S₁ = ∫₋ₐᵃ |√(R² - x²) - (h/a²)x²| dx
    """
    x = sp.Symbol('x')
    circle_upper = sp.sqrt(R**2 - x**2)
    parabola = sp.Rational(h, a**2) * x**2
    integrand = sp.Abs(circle_upper - parabola)
    result = sp.integrate(integrand, (x, -a, a))
    return float(result.evalf())


def calculate_S2(R: int, b_ellipse: int) -> float:
    """
    Tính S₂: diện tích hình bán nguyệt (nửa dưới hình tròn trừ nửa dưới elip)
    S_circle = πR²
    S_ellipse = πRb (elip có bán trục a_e = R, b_e = b_ellipse)
    S₂ = (S_circle - S_ellipse) / 2
    """
    S_circle = math.pi * R**2
    S_ellipse = math.pi * R * b_ellipse
    return (S_circle - S_ellipse) / 2


def calculate_total_cost(S1: float, S2: float, cost_rose: int, cost_lily: int) -> float:
    """Tính tổng chi phí (triệu đồng)"""
    total = cost_rose * S1 + cost_lily * S2
    return total / 1_000_000


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

# TikZ cố định (chỉ thay labels)
TIKZ_TEMPLATE = Template(r"""
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=0.5]

\definecolor{hongsanho}{RGB}{229,150,150}
\definecolor{botdo}{RGB}{128,0,32}

 \path
 (0,0) coordinate (O)
 ;


 \draw[fill=pink!90,line width=3pt,draw=botdo] (O) circle(10cm);
  \draw[line width=3pt,draw=botdo] plot[domain=-10:10]  (\x,{6/64*(\x)^2}) ;
  \draw[fill=white!70!black,line width=3pt,draw=botdo] plot[domain=-8:8]  (\x,{6/64*(\x)^2}) -- plot[domain=8:10] (\x, {sqrt(100-(\x)^2)})
arc(0:-180:10cm and 5cm)--plot[domain=-10:-8] (\x, {sqrt(100-(\x)^2)})
;
 \draw[fill=hongsanho,line width=3pt,draw=botdo] plot[domain=-8:8]  (\x,{6/64*(\x)^2}) -- plot[domain=8:-8] (\x, {sqrt(100-(\x)^2)});

 \draw[line width=3pt,draw=hongsanho] (180:10) arc(180:360:10cm and 5cm);

 \draw[<->,botdo,line width=1pt] (-8,6)--(8,6)node[above,pos=0.5,scale=2]{$$${two_a}$$ m};
 \draw[<->,black] (0,0)--(0,-5)node[right,pos=0.5,scale=2]{$$${b_ellipse}$$ m};
  \draw[<->,botdo,line width=1pt] (-8,6)--(-8,0)node[right,pos=0.5,scale=1.6]{$$${h}$$ m};
  \draw[red,botdo,line width=1pt] (-10,0)--(10,0);
  \draw (0,3) node[,scale=2]{$$S_1$$};
  \draw (0,-8) node[,scale=2]{$$S_2$$};
   \draw[line width=3pt,draw=botdo] (O) circle(10cm);
\end{tikzpicture}
""")

TEMPLATE_QUESTION = Template(r"""Khu vườn nhà ông Ba có dạng hình tròn, bán kính ${R} m. Ông Ba dự định trồng hoa Hồng ở khu vực $$S_1$$ và hoa Ly ở khu vực hình bán nguyệt $$S_2$$. Với $$S_1$$ là phần diện tích giới hạn bởi đường parabol đi qua tâm hình tròn và $$S_2$$ là phần diện tích giới hạn bởi nửa đường elip không chứa tâm hình tròn (kích thước như hình vẽ). Biết rằng kinh phí trồng hoa Hồng là ${cost_rose} đồng/$$m^2$$, kinh phí trồng hoa Ly là ${cost_lily} đồng/$$m^2$$. Hỏi ông Ba phải mất bao nhiêu triệu đồng để trồng hoa lên hai dải đất đó \textit{(làm tròn kết quả đến hàng phần mười)}

\begin{center}
${tikz_diagram}
\end{center}
""")


TEMPLATE_SOLUTION = Template(r"""
Lời giải:

Phương trình parabol đi qua tâm hình tròn là $$y = \dfrac{${h}}{${a_sq}}x^2 = \dfrac{${h_over_a_sq_num}}{${h_over_a_sq_den}}x^2$$ và phương trình đường tròn là $$x^2 + y^2 = ${R_sq}$$.

Diện tích dải đất trồng hoa Hồng là diện tích hình phẳng được giới hạn bởi parabol $$(P)$$, hình tròn $$(C)$$ và hai đường thẳng $$x = -${a}$$, $$x = ${a}$$. Khi đó $$S_1 = \displaystyle\int_{-${a}}^{${a}}\left|\sqrt{${R_sq} - x^2} - \dfrac{${h_over_a_sq_num}}{${h_over_a_sq_den}}x^2\right|dx \xrightarrow{\text{casio}} S_1 = ${S1_result}\text{ m}^2$$.

Xét nửa hình tròn chứa hình bán nguyệt, ta thấy nửa hình tròn tạo bởi hình bán nguyệt và nửa hình elip với hình elip có độ dài hai bán trục $$a = ${b_ellipse}$$, $$b = ${R} \Rightarrow S_{(E)} = \pi ab = ${S_ellipse_exact}\pi\text{ m}^2$$.

Vậy diện tích hình bán nguyệt là $$S_2 = \dfrac{S_{(C)} - S_{(E)}}{2} = \dfrac{${R}^2\pi - ${S_ellipse_exact}\pi}{2} = ${S2_exact}\pi\text{ m}^2$$.

Tổng số tiền ông Ba cần phải chi để trồng hoa là $$T = ${cost_rose_raw} \cdot S_1 + ${cost_lily_raw} \cdot S_2 \approx ${total_cost}$$ triệu đồng.

Đáp án: ${total_cost} | ${total_cost_dot}
""")


# ==============================================================================
# LỚP SINH ĐỀ
# ==============================================================================

class GardenAreaCostQuestion:
    """Bài toán khu vườn hình tròn - chi phí trồng hoa"""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.calculated_values: Dict[str, Any] = {}
        self.config = config or GeneratorConfig()

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên"""
        R, a, h = random.choice(PYTHAGOREAN_SETS)

        # Lọc b_ellipse < R
        valid_b = [b for b in B_ELLIPSE_VALUES if b < R]
        b_ellipse = random.choice(valid_b)

        cost_rose = random.choice(COST_ROSE_VALUES)
        cost_lily = random.choice(COST_LILY_VALUES)

        return {
            "R": R,
            "a": a,
            "h": h,
            "b_ellipse": b_ellipse,
            "cost_rose": cost_rose,
            "cost_lily": cost_lily,
        }

    def calculate_values(self) -> Dict[str, Any]:
        """Tính toán các giá trị"""
        params = self.parameters

        R = params["R"]
        a = params["a"]
        h = params["h"]
        b_ellipse = params["b_ellipse"]
        cost_rose = params["cost_rose"]
        cost_lily = params["cost_lily"]

        # Tính S₁ bằng sympy
        S1 = calculate_S1(R, a, h)
        S1_rounded = round(S1, 2)

        # Tính S₂
        S2 = calculate_S2(R, b_ellipse)

        # Tổng chi phí (triệu đồng)
        total_cost = calculate_total_cost(S1, S2, cost_rose, cost_lily)
        total_cost_rounded = round(total_cost, 1)

        # Hệ số parabol rút gọn: h/a²
        from math import gcd
        g = gcd(h, a**2)
        h_over_a_sq_num = h // g
        h_over_a_sq_den = (a**2) // g

        # S_ellipse exact coefficient (trước π)
        S_ellipse_exact = R * b_ellipse

        # S₂ exact coefficient (trước π)
        S2_exact_num = R**2 - R * b_ellipse
        # S2 = S2_exact_num * π / 2
        # Rút gọn
        g2 = gcd(S2_exact_num, 2)
        S2_display_num = S2_exact_num // g2
        S2_display_den = 2 // g2

        if S2_display_den == 1:
            S2_exact_str = str(S2_display_num)
        else:
            S2_exact_str = f"\\dfrac{{{S2_display_num}}}{{{S2_display_den}}}"

        return {
            "S1": S1,
            "S1_rounded": S1_rounded,
            "S2": S2,
            "total_cost": total_cost,
            "total_cost_rounded": total_cost_rounded,
            "h_over_a_sq_num": h_over_a_sq_num,
            "h_over_a_sq_den": h_over_a_sq_den,
            "S_ellipse_exact": S_ellipse_exact,
            "S2_exact_str": S2_exact_str,
        }

    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        params = self.parameters
        calc = self.calculated_values

        tikz = TIKZ_TEMPLATE.substitute(
            two_a=2 * params["a"],
            h=params["h"],
            b_ellipse=params["b_ellipse"],
        )

        return TEMPLATE_QUESTION.substitute(
            R=params["R"],
            cost_rose=format_cost_vn(params["cost_rose"]),
            cost_lily=format_cost_vn(params["cost_lily"]),
            tikz_diagram=tikz,
        )

    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết"""
        params = self.parameters
        calc = self.calculated_values

        return TEMPLATE_SOLUTION.substitute(
            R=params["R"],
            R_sq=params["R"]**2,
            a=params["a"],
            a_sq=params["a"]**2,
            h=params["h"],
            h_over_a_sq_num=calc["h_over_a_sq_num"],
            h_over_a_sq_den=calc["h_over_a_sq_den"],
            b_ellipse=params["b_ellipse"],
            S1_result=format_decimal_vn(calc["S1_rounded"], 2),
            S_ellipse_exact=calc["S_ellipse_exact"],
            S2_exact=calc["S2_exact_str"],
            cost_rose_raw=format_cost_vn(params["cost_rose"]),
            cost_lily_raw=format_cost_vn(params["cost_lily"]),
            total_cost=format_decimal_vn(calc["total_cost_rounded"]),
            total_cost_dot=format_decimal_dot(calc["total_cost_rounded"]),
        )

    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        """Sinh một câu hỏi hoàn chỉnh"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.calculated_values = self.calculate_values()

        question_text = self.generate_question_text().strip()
        solution = self.generate_solution().strip()

        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += solution + "\n"

        answer_vn = format_decimal_vn(self.calculated_values["total_cost_rounded"])
        answer_dot = format_decimal_dot(self.calculated_values["total_cost_rounded"])
        answer = f"{answer_vn} | {answer_dot}"

        return question_content, answer

    @staticmethod
    def create_latex_document(
        questions_data: List[Tuple[str, str]],
        title: str = "Bài tập Khu Vườn Hình Tròn - Chi Phí Trồng Hoa",
    ) -> str:
        """Tạo document LaTeX hoàn chỉnh"""
        questions_content = "\n\n\\newpage\n\n".join(
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


# ==============================================================================
# HÀM MAIN
# ==============================================================================

def main():
    """
    Hàm main để chạy generator
    Usage: python garden_area_cost_questions.py <num_questions> [seed]
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

        logging.info(f"Đang sinh {num_questions} câu hỏi khu vườn hình tròn...")

        questions_data: List[Tuple[str, str]] = []

        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            question = GardenAreaCostQuestion(config)
            question_content, answer = question.generate_question_only(i + 1)
            questions_data.append((question_content, answer))
            logging.info(f"  Câu {i + 1}: Chi phí = {answer} triệu đồng")

        latex_content = GardenAreaCostQuestion.create_latex_document(
            questions_data,
            title="Bài tập Khu Vườn Hình Tròn - Chi Phí Trồng Hoa"
        )

        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "garden_area_cost_questions.tex")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)

        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")

        print("\n=== ĐÁP ÁN ===")
        for i, (_, answer) in enumerate(questions_data):
            print(f"Câu {i + 1}: Chi phí = {answer} triệu đồng")

    except ValueError as e:
        print(f"Lỗi: Tham số không hợp lệ - {e}")
        print("Usage: python garden_area_cost_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")
        raise


if __name__ == "__main__":
    main()
