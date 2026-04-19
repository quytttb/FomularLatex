"""
Hệ thống sinh đề toán về thể tích chi tiết máy CNC
Bài toán: Khối hộp chữ nhật được mài theo đường cong parabol
Công thức: V = S_thiết_diện × BF, Cost = V × price
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

# 20 giá trị cho AB (chiều dài đáy, cm)
AB_VALUES: List[Fraction] = [
    Fraction(5), Fraction(6), Fraction(7), Fraction(8), Fraction(9),
    Fraction(10), Fraction(11), Fraction(12), Fraction(13), Fraction(14),
    Fraction(15), Fraction(16), Fraction(17), Fraction(18), Fraction(19),
    Fraction(20), Fraction(21), Fraction(22), Fraction(23), Fraction(24)
]

# 20 giá trị cho BC (chiều cao, cm)
BC_VALUES: List[Fraction] = [
    Fraction(4), Fraction(5), Fraction(6), Fraction(7), Fraction(8),
    Fraction(9), Fraction(10), Fraction(11), Fraction(12), Fraction(13),
    Fraction(14), Fraction(15), Fraction(16), Fraction(17), Fraction(18),
    Fraction(19), Fraction(20), Fraction(21), Fraction(22), Fraction(24)
]

# 20 giá trị cho DE (cm)
DE_VALUES: List[Fraction] = [
    Fraction(1), Fraction(2), Fraction(3), Fraction(4), Fraction(5),
    Fraction(6), Fraction(7), Fraction(8), Fraction(9), Fraction(10),
    Fraction(11), Fraction(12), Fraction(13), Fraction(14), Fraction(15),
    Fraction(16), Fraction(17), Fraction(18), Fraction(19), Fraction(20)
]

# 20 giá trị cho AE (cm)
AE_VALUES: List[Fraction] = [
    Fraction(1), Fraction(2), Fraction(3), Fraction(4), Fraction(5),
    Fraction(6), Fraction(7), Fraction(8), Fraction(9), Fraction(10),
    Fraction(11), Fraction(12), Fraction(13), Fraction(14), Fraction(15),
    Fraction(16), Fraction(17), Fraction(18), Fraction(19), Fraction(20)
]

# 20 giá trị cho BF (chiều dài chi tiết, cm)
BF_VALUES: List[Fraction] = [
    Fraction(10), Fraction(11), Fraction(12), Fraction(13), Fraction(14),
    Fraction(15), Fraction(16), Fraction(17), Fraction(18), Fraction(19),
    Fraction(20), Fraction(21), Fraction(22), Fraction(23), Fraction(24),
    Fraction(25), Fraction(26), Fraction(27), Fraction(28), Fraction(30)
]

# 20 giá trị cho khoảng cách từ đỉnh S đến AB (cm)
DIST_S_VALUES: List[Fraction] = [
    Fraction(1), Fraction(2), Fraction(3), Fraction(4), Fraction(5),
    Fraction(6), Fraction(7), Fraction(8), Fraction(9), Fraction(10),
    Fraction(11), Fraction(12), Fraction(13), Fraction(14), Fraction(15),
    Fraction(16), Fraction(17), Fraction(18), Fraction(19), Fraction(20)
]

COST_VALUES: List[int] = [
    8000, 8500, 9000, 9500, 10000, 10500, 11000, 11500, 12000, 12500,
    13000, 13500, 14000, 14500, 15000, 15500, 16000, 16500, 17000, 18000
]


# ==============================================================================
# HÀM TIỆN ÍCH
# ==============================================================================

def format_fraction_vn(frac: Fraction) -> str:
    if frac.denominator == 1:
        return str(frac.numerator)
    decimal_val = float(frac)
    if decimal_val == int(decimal_val):
        return str(int(decimal_val))
    formatted = f"{decimal_val:.2f}".rstrip('0').rstrip('.')
    return formatted.replace(".", ",")


def to_decimal_comma(value: Any) -> str:
    if isinstance(value, Fraction):
        return format_fraction_vn(value)
    return str(value).replace(".", ",")


def format_fraction_latex(frac) -> str:
    if hasattr(frac, 'p') and hasattr(frac, 'q'):
        if frac.q == 1:
            return str(frac.p)
        if frac.p < 0:
            return rf"- \dfrac{{{-frac.p}}}{{{frac.q}}}"
        return rf"\dfrac{{{frac.p}}}{{{frac.q}}}"
    if isinstance(frac, Fraction):
        if frac.denominator == 1:
            return str(frac.numerator)
        if frac.numerator < 0:
            return rf"- \dfrac{{{-frac.numerator}}}{{{frac.denominator}}}"
        return rf"\dfrac{{{frac.numerator}}}{{{frac.denominator}}}"
    return str(frac)


def format_number_thousands(num: int) -> str:
    return f"{num:,}".replace(",", ".")


# ==============================================================================
# HÀM TÍNH TOÁN HÌNH HỌC
# ==============================================================================

def find_parabola_vertex_form(AB: sp.Rational, BC: sp.Rational, AE: sp.Rational,
                               DE: sp.Rational, dist_S: sp.Rational) -> Tuple[sp.Rational, sp.Rational]:
    """
    Tìm hệ số k, m của parabol dạng đỉnh: y = k(x - m)² + dist_S
    
    Hệ toạ độ Oxy: A là gốc, Ox dọc AB, Oy dọc AE.
    Tọa độ: A(0,0), B(AB,0), C(AB,BC), D(DE,AE), E(0,AE), S(m, dist_S)
    
    Parabol có đỉnh S(m, dist_S), đi qua D(DE, AE) và C(AB, BC):
    (1) k(DE - m)² + dist_S = AE
    (2) k(AB - m)² + dist_S = BC
    
    Giải hệ và chọn nghiệm DE < m < AB.
    """
    k_sym, m_sym = sp.symbols('k m')
    
    eq1 = sp.Eq(k_sym * (DE - m_sym)**2 + dist_S, AE)
    eq2 = sp.Eq(k_sym * (AB - m_sym)**2 + dist_S, BC)
    
    solutions = sp.solve([eq1, eq2], [k_sym, m_sym])
    
    # Chọn nghiệm hợp lệ: DE < m < AB
    for sol in solutions:
        k_val, m_val = sol
        if DE < m_val < AB:
            return (k_val, m_val)
    
    # Fallback: trả về nghiệm đầu tiên
    return solutions[0]


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

TIKZ_DIAGRAM_TEMPLATE = r"""
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
   
   \draw [dashed] (0,1) -- (0,0) -- (3.2,-2.75);
   \draw [dashed] (0,0) -- (3.25,0) -- (6.45,-2.75);
   \draw [dashed] (3.25,0) -- (3.25,2.3);
   \draw (0.5,1) -- (0,1) -- (3.2,-1.8) -- (3.7,-1.8) -- (0.5,1) 
   .. controls +(-41.2:0.5) and +(179.4:0.4) .. (1.4, 0.5) 
   .. controls +(-0.6:0.8) and +(-121:0.8) .. (3.2, 2.3) -- (6.45,-0.45) -- (6.45,-2.75) -- (3.2,-2.75) -- (3.2,-1.8);
   \draw (6.45,-0.45) 
   .. controls +(-117.8:0.9) and +(-0.3:0.7) .. (4.6, -2.3) 
   .. controls +(179.7:0.3) and +(-51.5:0.4) .. (3.7, -1.8);
   
   \foreach \x/\y/\pos/\lbl in {
    3.7/-1.8/(270:3mm)/D,
    3.2/-1.8/(200:3mm)/E,
    6.45/-0.45/(45:3mm)/C,
    3.25/0/(135:3mm)/F,
    6.45/-2.75/(330:3mm)/B,
    3.2/-2.75/(240:3mm)/A,
    4.6/-2.3/(270:3mm)/S
   }{
    \fill (\x,\y) circle (1.2pt) node[shift=\pos] {$\lbl$};
   }
   
\end{tikzpicture}
"""


QUESTION_TPL = Template(r"""Một chi tiết máy được thiết kế bởi khối hộp chữ nhật được mài nhẵn đều bởi máy kỹ thuật số CNC theo đường cong là một parabol \((P)\) với đỉnh \(S\) cách \(AB\) một đoạn bằng \(${dist_S} \text{ cm}\) (được mô hình hóa bởi hình vẽ dưới đây). Biết rằng \(AB = ${AB} \text{ cm}, BC = ${BC} \text{ cm}, DE = ${DE} \text{ cm}, AE = ${AE} \text{ cm}\) và \(BF = ${BF} \text{ cm}\). Giả sử chi phí để gia công chi tiết máy đó được tính theo \(1 \text{ cm}^3\) là ${cost_per_cm3} đồng. Hãy tính số tiền cần để gia công chi phí máy đó (đơn vị: nghìn đồng).

\begin{center}
${tikz_diagram}
\end{center}
""")


SOLUTION_TPL = Template(r"""Lời giải:

Khi cắt chi tiết máy bởi mặt phẳng vuông góc với \(BF\) thu được thiết diện diện tích không đổi là diện tích ngũ giác cong \(ABCDE\).

Do đó thể tích của chi tiết máy là \(V = S_{\text{ngũ giác cong } ABCDE} \cdot BF\).

Chọn hệ trục toạ độ \(Oxy\) sao cho các tia \(Ox\), \(Oy\) lần lượt trùng với các tia \(AB\), \(AE\) và đơn vị trên mỗi trục toạ độ là centimét.

Toạ độ các điểm là \(A(0;\,0)\), \(B(${AB};\,0)\), \(C(${AB};\,${BC})\), \(D(${DE};\,${AE})\), \(E(0;\,${AE})\), \(S(m;\,${dist_S})\) \((${DE} < m < ${AB})\).

Parabol có đỉnh \(S(m;\,${dist_S}) \Rightarrow y = k(x - m)^2 + ${dist_S}\)

Đi qua điểm \(D(${DE};\,${AE}) \Leftrightarrow k \cdot (${DE} - m)^2 + ${dist_S} = ${AE}\) \((1)\).

Đi qua điểm \(C(${AB};\,${BC}) \Leftrightarrow k \cdot (${AB} - m)^2 + ${dist_S} = ${BC}\) \((2)\).

Giải \((1)\), \((2)\) và đối chiếu \(${DE} < m < ${AB} \Rightarrow k = ${k_val};\, m = ${m_val} \Rightarrow y = ${parabola_expr}\).

Số tiền gia công chi tiết máy là \(F = ${cost_raw}V = ${cost_raw} \cdot \left[\displaystyle\int\limits_{0}^{${DE}} ${AE}\, dx + \int\limits_{${DE}}^{${AB}} \left(${parabola_expr_inner}\right) dx\right] \cdot ${BF} = ${cost_thousand}\) nghìn đồng.
""")


# ==============================================================================
# LỚP CƠ SỞ VÀ CÀI ĐẶT
# ==============================================================================

class BaseMachinedPartQuestion(ABC):
    """Lớp cơ sở cho các bài toán chi tiết máy"""

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
        question_content += solution + "\n\n"
        question_content += f"Đáp án: {self.correct_answer}\n"
        return question_content, self.correct_answer

    @staticmethod
    def create_latex_document(
        questions_data: List[Tuple[str, str]],
        title: str = "Bài tập Thể tích Chi tiết Máy CNC",
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


class MachinedPartVolumeQuestion(BaseMachinedPartQuestion):
    """Bài toán tính thể tích và giá gia công chi tiết máy CNC"""

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên với constraint hợp lệ"""
        max_attempts = 1000
        for _ in range(max_attempts):
            AB = random.choice(AB_VALUES)
            BC = random.choice(BC_VALUES)
            DE = random.choice(DE_VALUES)
            AE = random.choice(AE_VALUES)
            BF = random.choice(BF_VALUES)
            dist_S = random.choice(DIST_S_VALUES)
            cost_per_cm3 = random.choice(COST_VALUES)

            # Constraints:
            # DE < AB, AE < BC, dist_S < AE
            if DE >= AB or AE >= BC or dist_S >= AE:
                continue

            # (BC - dist_S) / (AE - dist_S) phải là bình phương số hữu tỉ
            # để k, m là số hữu tỉ (không có căn)
            num = BC - dist_S
            den = AE - dist_S
            ratio = Fraction(num) / Fraction(den)
            # Kiểm tra ratio = p²/q²
            from math import isqrt
            n = ratio.numerator
            d = ratio.denominator
            sn = isqrt(n)
            sd = isqrt(d)
            if sn * sn == n and sd * sd == d:
                return {
                    "AB": AB, "BC": BC, "DE": DE, "AE": AE,
                    "BF": BF, "dist_S": dist_S, "cost_per_cm3": cost_per_cm3,
                }

        raise ValueError("Không tìm được bộ tham số hợp lệ sau nhiều lần thử")

    def _to_sympy(self) -> Dict[str, Any]:
        params = self.parameters
        return {k: sp.Rational(v.numerator, v.denominator) if isinstance(v, Fraction) else v
                for k, v in params.items()}

    def calculate_answer(self) -> str:
        s = self._to_sympy()
        AB, BC, DE, AE, BF = s["AB"], s["BC"], s["DE"], s["AE"], s["BF"]
        dist_S, cost_per_cm3 = s["dist_S"], s["cost_per_cm3"]

        k, m = find_parabola_vertex_form(AB, BC, AE, DE, dist_S)

        x = sp.Symbol('x')
        parabola = k * (x - m)**2 + dist_S

        # Diện tích thiết diện: S = AE·DE + ∫_DE^AB parabola dx
        S_rect = AE * DE
        S_parabola = sp.integrate(parabola, (x, DE, AB))
        S_total = S_rect + S_parabola

        V_final = S_total * BF
        total_cost = float(V_final.evalf()) * cost_per_cm3
        return str(round(total_cost / 1000))

    def generate_tikz_diagram(self) -> str:
        return TIKZ_DIAGRAM_TEMPLATE

    def generate_question_text(self) -> str:
        p = self.parameters
        return QUESTION_TPL.substitute(
            AB=format_fraction_vn(p["AB"]), BC=format_fraction_vn(p["BC"]),
            DE=format_fraction_vn(p["DE"]), AE=format_fraction_vn(p["AE"]),
            BF=format_fraction_vn(p["BF"]), dist_S=format_fraction_vn(p["dist_S"]),
            cost_per_cm3=format_number_thousands(p["cost_per_cm3"]),
            tikz_diagram=self.generate_tikz_diagram(),
        )

    def generate_solution(self) -> str:
        s = self._to_sympy()
        AB, BC, DE, AE, BF = s["AB"], s["BC"], s["DE"], s["AE"], s["BF"]
        dist_S, cost_per_cm3 = s["dist_S"], s["cost_per_cm3"]

        k, m = find_parabola_vertex_form(AB, BC, AE, DE, dist_S)

        x = sp.Symbol('x')
        parabola = k * (x - m)**2 + dist_S
        parabola_expanded = sp.expand(parabola)

        # Diện tích
        S_rect = AE * DE
        S_parabola = sp.integrate(parabola, (x, DE, AB))
        S_total = S_rect + S_parabola

        V_final = S_total * BF
        total_cost_float = float(V_final.evalf()) * cost_per_cm3
        cost_thousand = round(total_cost_float / 1000)

        # Biểu thức parabol cho LaTeX
        parabola_expr = sp.latex(parabola_expanded)
        parabola_expr_inner = sp.latex(parabola_expanded)

        # cost_raw: đơn giá tính theo nghìn đồng (vd: 11000 -> 11, 9500 -> 9{,}5)
        cost_raw_frac = Fraction(int(cost_per_cm3), 1000)
        if cost_raw_frac.denominator == 1:
            cost_raw_val = str(cost_raw_frac.numerator)
        else:
            cost_raw_val = str(float(cost_raw_frac)).rstrip('0').rstrip('.').replace('.', '{,}')

        return SOLUTION_TPL.substitute(
            AB=format_fraction_latex(AB),
            BC=format_fraction_latex(BC),
            DE=format_fraction_latex(DE),
            AE=format_fraction_latex(AE),
            BF=format_fraction_latex(BF),
            dist_S=format_fraction_latex(dist_S),
            k_val=format_fraction_latex(k),
            m_val=format_fraction_latex(m),
            parabola_expr=parabola_expr,
            parabola_expr_inner=parabola_expr_inner,
            cost_raw=cost_raw_val,
            cost_thousand=cost_thousand,
        )


# ==============================================================================
# HÀM MAIN
# ==============================================================================

def main():
    """
    Hàm main để chạy generator
    Usage: python machined_part_questions.py <num_questions> [seed]
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

        logging.info(f"Đang sinh {num_questions} câu hỏi chi tiết máy CNC...")

        questions_data: List[Tuple[str, str]] = []

        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            question = MachinedPartVolumeQuestion(config)
            question_content, correct_answer = question.generate_question_only(i + 1)
            questions_data.append((question_content, correct_answer))
            logging.info(f"  Câu {i + 1}: Đáp án = {correct_answer} nghìn đồng")

        latex_content = BaseMachinedPartQuestion.create_latex_document(
            questions_data,
            title="Bài tập Thể tích Chi tiết Máy CNC"
        )

        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "machined_part_questions.tex")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)

        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")

        print("\n=== ĐÁP ÁN ===")
        for i, (_, answer) in enumerate(questions_data):
            print(f"Câu {i + 1}: {answer} nghìn đồng")

    except ValueError as e:
        print(f"Lỗi: Tham số không hợp lệ - {e}")
        print("Usage: python machined_part_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")
        raise


if __name__ == "__main__":
    main()
