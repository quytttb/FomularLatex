"""
Hệ thống sinh đề toán về thể tích tòa nhà (cung tròn)
Bài toán: Tòa nhà có thiết diện ngang là hình vuông, mặt cắt đứng chứa đường chéo đáy
bị giới hạn bởi hai cung tròn đối xứng qua Ox.
Công thức: y = yE - √(R² - (x-xE)²), S(x) = 2y², V = ∫₀^h 2y² dx
"""

import logging
import math
import os
import random
import sys
from dataclasses import dataclass
from string import Template
from typing import Any, Dict, List, Optional, Tuple

from scipy.integrate import quad

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

# ==============================================================================
# CẤU HÌNH VÀ HẰNG SỐ
# ==============================================================================

@dataclass
class GeneratorConfig:
    """Cấu hình cho generator"""
    seed: Optional[int] = None

# Chiều cao tòa nhà h (m)
H_VALUES: List[int] = [24, 26, 28, 30, 32, 34, 36]

# Cạnh đáy L₀ (m)
L0_VALUES: List[float] = [22, 24, 26, 28, 30]

# Cạnh đỉnh L_h (m)
LH_VALUES: List[float] = [16, 18, 20, 22, 24]

# Đường kính cung tròn (dạng a√b)
# Mẫu: 9√34
ARC_DIAMETER_VALUES: List[Tuple[int, int]] = [
    (6, 34), (7, 34), (8, 34), (9, 34), (10, 34),
    (9, 17), (9, 26), (9, 34), (12, 17),
]


# ==============================================================================
# HÀM TIỆN ÍCH
# ==============================================================================

def format_decimal_vn(val: float, decimals: int = 2) -> str:
    """Format số thập phân với dấu phẩy (kiểu VN)"""
    formatted = f"{val:.{decimals}f}".rstrip('0').rstrip('.')
    return formatted.replace(".", ",")


def format_number(val: float, decimals: int = 2) -> str:
    """Format số: nếu là số nguyên thì bỏ phần thập phân"""
    if abs(val - round(val)) < 1e-9:
        return str(int(round(val)))
    return format_decimal_vn(val, decimals)


def format_number_latex(val: float, decimals: int = 2) -> str:
    """Format số cho LaTeX math: dùng dấu chấm (chuẩn math)"""
    if abs(val - round(val)) < 1e-9:
        return str(int(round(val)))
    return f"{val:.{decimals}f}".rstrip('0').rstrip('.')


# ==============================================================================
# HÀM TÍNH TOÁN HÌNH HỌC
# ==============================================================================

def solve_circle_center(
    h: float, yA: float, yD: float, D: float
) -> Tuple[float, float, float]:
    """
    Tìm tâm E(xE, yE) của đường tròn qua A(0,yA) và D(h,yD) với đường kính D.
    R = D/2. Tâm nằm trên trung trực của AD.
    Trả về (xE, yE, R).
    """
    R = D / 2
    R_sq = R * R
    # |AD|²
    AD_sq = h * h + (yD - yA) ** 2
    if AD_sq > D * D + 1e-9:
        raise ValueError("Chord AD dài hơn đường kính D")

    # Tâm trên trung trực: M + u*perp, perp = (yA-yD, h)
    Mx = h / 2
    My = (yA + yD) / 2
    perp_x = yA - yD
    perp_y = h

    # |E-A|² = R² => u² = (R² - |AM|²) / |AD|², với |AM|² = |AD|²/4
    AM_sq = AD_sq / 4
    u_sq = (R_sq - AM_sq) / AD_sq
    if u_sq < -1e-12:
        raise ValueError("Không tồn tại đường tròn")
    u_sq = max(0, u_sq)
    u = math.sqrt(u_sq)

    # Hai tâm: u và -u. Chọn tâm sao cho cung AD là cung lõm (phía dưới đường tròn)
    # Cung AD nối A(0,yA) và D(h,yD), lõm xuống khi yE > (yA+yD)/2
    xE1 = Mx + u * perp_x
    yE1 = My + u * perp_y
    xE2 = Mx - u * perp_x
    yE2 = My - u * perp_y

    # Cung trên: y = yE - √(R²-(x-xE)²) (phần dưới đường tròn)
    # Tại x=0: y = yE - √(R² - xE²). Cần = yA
    # Tại x=h: y = yE - √(R² - (h-xE)²). Cần = yD
    # Chọn tâm mà √(R²-(x-xE)²) cho đúng: y(0)=yA => √(R²-xE²) = yE-yA
    for xE, yE in [(xE1, yE1), (xE2, yE2)]:
        rad_0 = R_sq - xE * xE
        rad_h = R_sq - (h - xE) ** 2
        if rad_0 >= -1e-9 and rad_h >= -1e-9:
            r0 = math.sqrt(max(0, rad_0))
            rh = math.sqrt(max(0, rad_h))
            if abs((yE - r0) - yA) < 0.01 and abs((yE - rh) - yD) < 0.01:
                return (xE, yE, R)
    # Fallback
    return (xE1, yE1, R)


def integrate_volume_circular(
    h: float, xE: float, yE: float, R: float
) -> float:
    """
    V = ∫₀^h 2y² dx với y(x) = yE - √(R² - (x-xE)²).
    Chỉ lấy phần x trong [0,h] mà radicand >= 0.
    """
    R_sq = R * R

    def y_func(x):
        rad = R_sq - (x - xE) ** 2
        if rad <= 0:
            return 0.0
        return yE - math.sqrt(rad)

    def integrand(x):
        yv = y_func(x)
        return 2 * yv * yv

    result, _ = quad(integrand, 0, h, limit=200)
    return result


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

TIKZ_BUILDING_3D = r"""
\begin{tikzpicture}[scale=1, >=stealth]
   \draw[fill=cyan!30] (-2,-1.5) -- (1.317,-2.517) -- (3.134,-0.877) 
   .. controls +(130.3:1.9) and +(-117.5:2.2) .. (2.6, 4.6) -- (0,5.133) -- (-1.456,4.218) 
   .. controls +(-60.9:2.3) and +(54:2) .. (-2, -1.5) -- cycle;
   \draw (-1.456,4.218) -- (1.2,3.6) -- (2.628,4.6);
   \draw (1.317,-2.517) .. controls +(99.2:2) and +(-99.5:2.1) .. (1.2, 3.6)
   foreach \i in{1,2,...,10} {coordinate[pos=\i/10](A\i)};
   \draw [dashed] (0,0) -- ++(3.134,-0.877);
   \draw [dashed] (0,0) -- ++(-2,-1.5);
   \clip (-2,-1.5) -- (1.317,-2.517) -- (3.134,-0.877) 
   .. controls +(130.3:1.9) and +(-117.5:2.2) .. (2.6, 4.6) -- (0.074,5.133) -- (-1.456,4.218) 
   .. controls +(-60.9:2.3) and +(54:2) .. (-2, -1.5) -- cycle;
   \draw [dashed] (0,5.133) .. controls +(-81.7:1.8) and +(81:1.7) .. (0, 0)
   coordinate[pos=0.1](B1) coordinate[pos=0.25](B2) coordinate[pos=0.39](B3)
   coordinate[pos=0.51](B4) coordinate[pos=0.63](B5) coordinate[pos=0.72](B6)
   coordinate[pos=0.81](B7) coordinate[pos=0.9](B8) coordinate[pos=0.95](B9);
   \draw [dashed] (B1) -- ++(3.134,-0.65); \draw [dashed] (B1) -- ++(-2,-1.45);
   \draw [dashed] (B2) -- ++(3.134,-0.8); \draw [dashed] (B2) -- ++(-2,-1.45);
   \draw [dashed] (B3) -- ++(3.134,-0.78); \draw [dashed] (B3) -- ++(-2,-1.45);
   \draw [dashed] (B4) -- ++(3.134,-0.78); \draw [dashed] (B4) -- ++(-2,-1.45);
   \draw [dashed] (B5) -- ++(3.134,-0.73); \draw [dashed] (B5) -- ++(-2,-1.45);
   \draw [dashed] (B6) -- ++(3.134,-0.78); \draw [dashed] (B6) -- ++(-2,-1.48);
   \draw [dashed] (B7) -- ++(3.134,-0.78); \draw [dashed] (B7) -- ++(-2,-1.48);
   \draw [dashed] (B8) -- ++(3.134,-0.7); \draw [dashed] (B8) -- ++(-2,-1.4);
   \draw [dashed] (B9) -- ++(3.134,-0.82); \draw [dashed] (B9) -- ++(-2,-1.5);
   \foreach \x in {1,2,...,9}
   {\draw[] (A\x)--++(-3.317,1.017);\draw[] (A\x) -- ++(1.817,1.64);}
\end{tikzpicture}
"""


def build_tikz_cross_section_circular(
    h: float, yA: float, yD: float, xE: float, yE: float, R: float
) -> str:
    """Tạo TikZ mặt cắt đứng ABCD với 2 cung tròn đối xứng qua Ox."""
    def pf(v):
        return f"{v:.6f}".replace(",", ".")

    h_s = pf(h)
    yA_s, yD_s = pf(yA), pf(yD)
    xE_s, yE_s = pf(xE), pf(yE)
    R_sq = R * R

    # Điểm M, N ở x = h/2
    x_M = h / 2
    rad_m = R_sq - (x_M - xE) ** 2
    y_M = yE - math.sqrt(rad_m) if rad_m > 0 else (yA + yD) / 2
    xM_s, yM_s = pf(x_M), pf(y_M)
    R_s = pf(R)
    y_max = pf(max(yA, yE) + 0.5)

    return r"""
\begin{tikzpicture}[scale=1, >=stealth, font=\footnotesize, line join=round]
  \draw[->] (-0.8, 0) -- (""" + h_s + r"""*0.35 + 1.2, 0) node[below right] {$x$};
  \draw[->] (0, -""" + yA_s + r"""*0.22 - 0.6) -- (0, """ + y_max + r"""*0.22) node[above left] {$y$};
  \fill (0,0) circle (1.2pt) node[below left] {$O$};
  \draw (""" + h_s + r"""*0.35, 0) node[below] {""" + str(int(h) if h == int(h) else h_s) + r"""};
  \draw[thick] (0, """ + yA_s + r"""*0.22) -- (0, -""" + yA_s + r"""*0.22);
  \draw[thick] (""" + h_s + r"""*0.35, """ + yD_s + r"""*0.22) -- (""" + h_s + r"""*0.35, -""" + yD_s + r"""*0.22);
  % Cung tròn trên AD
  \draw[thick, brown!70!black] (0, """ + yA_s + r"""*0.22) 
    plot[domain=0:""" + h_s + r""", samples=80] ({\x*0.35}, {(""" + yE_s + r""" - sqrt(""" + R_s + r"""*""" + R_s + r""" - (\x-""" + xE_s + r""")*(\x-""" + xE_s + r"""))) * 0.22})
    -- (""" + h_s + r"""*0.35, """ + yD_s + r"""*0.22);
  % Cung tròn dưới BC
  \draw[thick, brown!70!black] (0, -""" + yA_s + r"""*0.22)
    plot[domain=0:""" + h_s + r""", samples=80] ({\x*0.35}, {(-(""" + yE_s + r""" - sqrt(""" + R_s + r"""*""" + R_s + r""" - (\x-""" + xE_s + r""")*(\x-""" + xE_s + r"""))) * 0.22})
    -- (""" + h_s + r"""*0.35, -""" + yD_s + r"""*0.22);
  \draw[dashed] (""" + xM_s + r"""*0.35, """ + yM_s + r"""*0.22) -- (""" + xM_s + r"""*0.35, -""" + yM_s + r"""*0.22);
  % Tam giác AED (tâm E)
  \draw[dashed] (0, """ + yA_s + r"""*0.22) -- (""" + xE_s + r"""*0.35, """ + yE_s + r"""*0.22) -- (""" + h_s + r"""*0.35, """ + yD_s + r"""*0.22);
  % Đoạn thẳng đứng qua xE (hẹp nhất)
  \draw[dashed] (""" + xE_s + r"""*0.35, """ + pf(yE - R) + r"""*0.22) -- (""" + xE_s + r"""*0.35, """ + pf(R - yE) + r"""*0.22);
  \fill (0, """ + yA_s + r"""*0.22) circle (1.2pt) node[left] {$A$};
  \fill (0, -""" + yA_s + r"""*0.22) circle (1.2pt) node[left] {$B$};
  \fill (""" + h_s + r"""*0.35, """ + yD_s + r"""*0.22) circle (1.2pt) node[right] {$D$};
  \fill (""" + h_s + r"""*0.35, -""" + yD_s + r"""*0.22) circle (1.2pt) node[right] {$C$};
  \fill (""" + xM_s + r"""*0.35, """ + yM_s + r"""*0.22) circle (1.2pt) node[above right] {$M$};
  \fill (""" + xM_s + r"""*0.35, -""" + yM_s + r"""*0.22) circle (1.2pt) node[below right] {$N$};
  \fill (""" + xE_s + r"""*0.35, """ + yE_s + r"""*0.22) circle (1.2pt) node[above right] {$E$};
  \fill (""" + xE_s + r"""*0.35, """ + pf(R - yE) + r"""*0.22) circle (1.2pt) node[below right] {$F$};
\end{tikzpicture}
"""


def format_diameter_latex(a: int, b: int) -> str:
    """Format đường kính a√b cho LaTeX"""
    if b == 1:
        return str(a)
    return f"{a}\\sqrt{{{b}}}"


TEMPLATE_QUESTION = Template(r"""Một kiến trúc sư chịu trách nhiệm thiết kế một tòa nhà cao ${h} m. Thiết diện ngang tại mọi độ cao, vuông góc với trục thẳng đứng, luôn là một hình vuông (xem hình vẽ).

Mặt đáy tòa nhà là hình vuông có cạnh $$L_0 = ${L0}$$ m, mặt đỉnh là hình vuông có cạnh $$L_{${h}} = ${Lh}$$ m. Mặt cắt của tòa nhà theo mặt phẳng đứng chứa đường chéo đáy có dạng là hình phẳng giới hạn bởi hai cung tròn có cùng đường kính ${diam_latex} m đối xứng nhau qua trục thẳng đứng đi qua tâm đáy của tòa nhà. Tính thể tích của tòa nhà đó (làm tròn kết quả đến hàng đơn vị, đơn vị tính: mét khối).

\begin{center}
${tikz_diagram}
\end{center}
""")


TEMPLATE_SOLUTION = Template(r"""
Mặt cắt của tòa nhà theo mặt phẳng đứng chứa đường chéo đáy là hình thang cong $$ABCD$$ với cung tròn AD, BC đối xứng nhau qua Ox (xem hình vẽ):

\begin{center}
${tikz_cross_section}
\end{center}

Chọn trục $$Ox$$ hướng lên trùng với trục thẳng đứng của tòa nhà, gốc $$O$$ nằm trên mặt đáy, đơn vị trên trục là mét.

Tọa độ các điểm: $$A(0; \dfrac{${L0}}{\sqrt{2}})$$, $$B(0; -\dfrac{${L0}}{\sqrt{2}})$$, $$D(${h}; \dfrac{${Lh}}{\sqrt{2}})$$, $$C(${h}; -\dfrac{${Lh}}{\sqrt{2}})$$.

Tâm $$E$$ của cung tròn $$AD$$ thỏa mãn $$|EA|^2 = |ED|^2 = R^2 = \left(\dfrac{${diam_latex}}{2}\right)^2$$. Giải ra được $$E\left(${xE_val}; \dfrac{${yE_num}}{\sqrt{2}}\right)$$.

Phương trình cung tròn $$AD$$: $$(x - ${xE_val})^2 + \left(y - \dfrac{${yE_num}}{\sqrt{2}}\right)^2 = ${R_sq_latex}$$.

Do đó $$y = \dfrac{${yE_num}}{\sqrt{2}} - \sqrt{${R_sq_latex} - (x - ${xE_val})^2}$$.

Tòa nhà nằm giữa hai mặt phẳng $$x=0$$, $$x=${h}$$. Thiết diện vuông góc trục $$Ox$$ tại $$x$$ $$(0 \le x \le ${h})$$ là hình vuông có độ dài đường chéo $$d = MN = 2y$$ m, diện tích $$S(x) = \left(\dfrac{d}{\sqrt{2}}\right)^2 = 2y^2$$ m$$^2$$.

Thể tích tòa nhà là
\[ V = \int_0^{${h}} S(x)\,dx = \int_0^{${h}} 2y^2\,dx \approx ${volume_val} \text{ m}^3. \]
""")


# ==============================================================================
# LỚP SINH ĐỀ
# ==============================================================================

class BuildingVolumeCircularQuestion:
    """Bài toán tính thể tích tòa nhà với thiết diện vuông, cung tròn"""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.calculated_values: Dict[str, Any] = {}
        self.config = config or GeneratorConfig()

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số - ưu tiên bộ mẫu từ đề bài"""
        # Thử ngẫu nhiên
        max_attempts = 3000
        for _ in range(max_attempts):
            h = random.choice(H_VALUES)
            L0 = random.choice(L0_VALUES)
            Lh = random.choice(LH_VALUES)
            a, b = random.choice(ARC_DIAMETER_VALUES)
            D = a * math.sqrt(b)

            sqrt2 = math.sqrt(2)
            yA = L0 / sqrt2
            yD = Lh / sqrt2

            if abs(yA - yD) < 0.1:
                continue

            try:
                xE, yE, R = solve_circle_center(h, yA, yD, D)
            except ValueError:
                continue

            if not (0.001 < xE < h - 0.001):
                continue

            V = integrate_volume_circular(h, xE, yE, R)
            if V > 0 and V < 50000:
                return {
                    "h": h, "L0": L0, "Lh": Lh,
                    "diam_a": a, "diam_b": b, "D": D,
                    "xE": xE, "yE": yE, "R": R,
                    "volume": math.floor(V + 0.5),
                }

        # Fallback: bộ mẫu từ đề
        h, L0, Lh = 30, 26, 20
        a, b = 9, 34
        D = 9 * math.sqrt(34)
        sqrt2 = math.sqrt(2)
        yA, yD = L0 / sqrt2, Lh / sqrt2
        xE, yE, R = solve_circle_center(h, yA, yD, D)
        V = integrate_volume_circular(h, xE, yE, R)
        return {
            "h": h, "L0": L0, "Lh": Lh,
            "diam_a": a, "diam_b": b, "D": D,
            "xE": xE, "yE": yE, "R": R,
            "volume": math.floor(V + 0.5),
        }

    def calculate_values(self) -> Dict[str, Any]:
        """Tính toán và format cho lời giải"""
        p = self.parameters
        h, L0, Lh = p["h"], p["L0"], p["Lh"]
        xE, yE, R = p["xE"], p["yE"], p["R"]
        a, b = p["diam_a"], p["diam_b"]
        volume = p["volume"]

        sqrt2 = math.sqrt(2)
        yA = L0 / sqrt2
        yD = Lh / sqrt2

        # yE = yE_num / √2
        yE_num = round(yE * sqrt2)
        if abs(yE * sqrt2 - yE_num) < 0.01:
            yE_num_val = yE_num
        else:
            yE_num_val = round(yE * sqrt2 * 10) / 10

        R_sq = R * R
        # R² = 1377/2 cho 9√34
        if abs(R_sq - 1377/2) < 0.1:
            R_sq_latex = r"\dfrac{1377}{2}"
        elif abs(R_sq - round(R_sq)) < 0.1:
            R_sq_latex = str(int(round(R_sq)))
        else:
            R_sq_latex = format_number_latex(R_sq, 1)

        xE_str = format_number_latex(xE)
        yE_num_str = str(int(yE_num_val)) if yE_num_val == int(yE_num_val) else format_number_latex(yE_num_val, 1)

        tikz_cross_section = build_tikz_cross_section_circular(
            h, yA, yD, xE, yE, R
        )

        return {
            "xE_val": xE_str,
            "yE_num": yE_num_str,
            "R_sq_latex": R_sq_latex,
            "volume_val": volume,
            "tikz_cross_section": tikz_cross_section,
            "diam_latex": format_diameter_latex(a, b),
        }

    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        p = self.parameters
        diam_latex = format_diameter_latex(p["diam_a"], p["diam_b"])
        return TEMPLATE_QUESTION.substitute(
            h=p["h"],
            L0=format_number(p["L0"]),
            Lh=format_number(p["Lh"]),
            diam_latex=diam_latex,
            tikz_diagram=TIKZ_BUILDING_3D,
        )

    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết"""
        p = self.parameters
        calc = self.calculated_values
        h = p["h"]
        return TEMPLATE_SOLUTION.substitute(
            h=h,
            L0=format_number(p["L0"]),
            Lh=format_number(p["Lh"]),
            xE_val=calc["xE_val"],
            yE_num=calc["yE_num"],
            R_sq_latex=calc["R_sq_latex"],
            volume_val=calc["volume_val"],
            tikz_cross_section=calc["tikz_cross_section"],
            diam_latex=calc["diam_latex"],
        )

    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        """Sinh một câu hỏi hoàn chỉnh dạng Azota"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.calculated_values = self.calculate_values()

        question_text = self.generate_question_text().strip()
        solution = self.generate_solution().strip()
        answer = str(self.calculated_values["volume_val"])

        question_content = (
            f"\\begin{{ex}}%Câu {question_number}\n"
            f"{question_text}\n\n"
            f"\\shortans{{{answer}}}\n"
            f"\\loigiai{{\n{solution}\n}}\n"
            f"\\end{{ex}}\n"
        )

        return question_content, answer

    @staticmethod
    def create_latex_document(
        questions_data: List[Tuple[str, str]],
        title: str = "Bài tập Thể tích Tòa nhà (Cung tròn)",
    ) -> str:
        """Tạo document LaTeX hoàn chỉnh"""
        questions_content = "\n\n".join(
            [q_content for q_content, _ in questions_data]
        )

        latex_document = r"""\documentclass[12pt,a4paper]{article}
\usepackage{amsmath,amssymb}
\usepackage{tikz}
\usetikzlibrary{calc}
\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}
\usepackage[solcolor]{ex_test}

\begin{document}

""" + questions_content + r"""

\end{document}
"""
        return latex_document


# ==============================================================================
# HÀM MAIN
# ==============================================================================

def main():
    """Usage: python building_volume_circular_questions.py <num_questions> [seed]"""
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else None

        if seed is None:
            s = os.environ.get("OPT_SEED")
            seed = int(s) if s else None

        if seed is not None:
            random.seed(seed)
            logging.info(f"Sử dụng seed: {seed}")

        logging.info(f"Đang sinh {num_questions} câu hỏi thể tích tòa nhà (cung tròn)...")

        questions_data: List[Tuple[str, str]] = []
        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            q = BuildingVolumeCircularQuestion(config)
            content, answer = q.generate_question_only(i + 1)
            questions_data.append((content, answer))
            logging.info(f"  Câu {i + 1}: V = {answer} m³")

        latex_content = BuildingVolumeCircularQuestion.create_latex_document(
            questions_data, title="Bài tập Thể tích Tòa nhà (Cung tròn)"
        )

        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "building_volume_circular_questions.tex")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)

        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")

        print("\n=== ĐÁP ÁN ===")
        for i, (_, ans) in enumerate(questions_data):
            print(f"Câu {i + 1}: V = {ans} m³")

    except ValueError as e:
        print(f"Lỗi: {e}")
        print("Usage: python building_volume_circular_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi: {e}")
        raise


if __name__ == "__main__":
    main()
