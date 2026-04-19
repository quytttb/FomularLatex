"""
Hệ thống sinh đề toán về thể tích tòa nhà
Bài toán: Tòa nhà có thiết diện ngang là hình vuông, mặt cắt đứng chứa đường chéo đáy
bị giới hạn bởi hai parabol đối xứng.
Công thức: f(x) = k(x-m)² + C, S(x) = 2f²(x), V = ∫₀^h 2f²(x)dx
"""

import logging
import math
import os
import random
import sys
from dataclasses import dataclass
from fractions import Fraction
from string import Template
from typing import Any, Dict, List, Optional, Tuple

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

# ==============================================================================
# CẤU HÌNH VÀ HẰNG SỐ
# ==============================================================================

@dataclass
class GeneratorConfig:
    """Cấu hình cho generator"""
    seed: Optional[int] = None

# 20 giá trị cho chiều cao tòa nhà h (m)
H_VALUES: List[int] = list(range(20, 51, 2))  # 20, 22, 24, ..., 50

# 20 giá trị cho cạnh đáy L₀ (m)
L0_VALUES: List[float] = [
    22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
    32, 33, 34, 35, 36, 37, 38, 39, 40
]

# 20 giá trị cho cạnh đỉnh L_h (m)
LH_VALUES: List[float] = [
    16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
    26, 27, 28, 29, 30, 31, 32, 33, 34
]

# 20 giá trị cho cạnh hẹp nhất L_min (m) - phải < L₀ và L_h
L_MIN_VALUES: List[float] = [
    10, 10.5, 11, 11.5, 12, 12.25, 12.5, 12.75, 13, 13.25,
    13.5, 13.75, 14, 14.25, 14.5, 15, 15.5, 16, 16.5, 17
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


def format_fraction(frac) -> str:
    """Chuyển đổi Fraction/sympy Rational thành phân số LaTeX"""
    if hasattr(frac, 'p') and hasattr(frac, 'q'):
        num, den = frac.p, frac.q
    elif hasattr(frac, 'numerator') and hasattr(frac, 'denominator'):
        num, den = frac.numerator, frac.denominator
    else:
        return str(frac)
    if den == 1:
        return str(num)
    if num < 0:
        return rf"-\dfrac{{{abs(num)}}}{{{den}}}"
    return rf"\dfrac{{{num}}}{{{den}}}"


def format_sqrt_coef(coef: float) -> str:
    """Format hệ số nhân √2 cho LaTeX"""
    if abs(coef - round(coef)) < 1e-9:
        c = int(round(coef))
        if c == 1:
            return r"\sqrt{2}"
        if c == -1:
            return r"-\sqrt{2}"
        return f"{c}\\sqrt{{2}}"
    return format_decimal_vn(coef) + r"\sqrt{2}"


# ==============================================================================
# HÀM TÍNH TOÁN HÌNH HỌC
# ==============================================================================

def solve_parabola_params(
    h: float, L0: float, Lh: float, L_min: float
) -> Tuple[float, float]:
    """
    Giải hệ để tìm k và m của parabol f(x) = k(x-m)² + C.
    C = L_min * √2 / 2 (nửa đường chéo tại điểm hẹp nhất)
    f(0) = L₀/√2, f(h) = L_h/√2.

    km² + C = L₀/√2  (1)
    k(h-m)² + C = L_h/√2  (2)

    Trả về (k, m). k có dạng k = a√2, m là số.
    """
    sqrt2 = math.sqrt(2)
    C = L_min * sqrt2 / 2
    y0 = L0 / sqrt2   # half-diagonal at base
    yh = Lh / sqrt2   # half-diagonal at top

    # Subtract: k[m² - (h-m)²] = y0 - yh
    # m² - (h-m)² = 2hm - h²
    diff = y0 - yh
    denom = 2 * h
    # k(2m - h) = diff/h  from... let me recalc
    # m² - (h² - 2hm + m²) = 2hm - h²
    # k(2hm - h²) = y0 - yh
    # So: 2hm - h² ≠ 0 => m ≠ h/2 (for unique solution, we need parabola with min in between)

    # From (1): km² = y0 - C
    # From (2): k(h-m)² = yh - C
    # Ratio: m²/(h-m)² = (y0-C)/(yh-C)
    num1 = y0 - C
    num2 = yh - C
    if abs(num2) < 1e-12:
        raise ValueError("L_h gần bằng L_min, không hợp lệ")
    ratio = num1 / num2
    if ratio <= 0:
        raise ValueError("Tỉ số không dương, kiểm tra L₀ > L_min > L_h hoặc tương tự")

    # m²/(h-m)² = ratio => m/(h-m) = √ratio
    r = math.sqrt(ratio)
    m = h * r / (1 + r)
    k = num1 / (m * m)
    return (k, m)


def integrate_volume(h: float, k: float, m: float, L_min: float) -> float:
    """
    V = ∫₀^h 2·f²(x) dx với f(x) = k(x-m)² + C.
    C = L_min * √2 / 2
    """
    C = L_min * math.sqrt(2) / 2
    # f(x) = k(x-m)² + C
    # f² = k²(x-m)⁴ + 2kC(x-m)² + C²
    # ∫ f² dx: đặt u = x-m, dx = du
    # ∫₀^h f² dx = ∫_{-m}^{h-m} [k²u⁴ + 2kCu² + C²] du
    # = k²·u⁵/5 + 2kC·u³/3 + C²·u |_{-m}^{h-m}
    def F(u):
        return (k**2 * u**5 / 5 + 2*k*C * u**3 / 3 + C**2 * u)
    V_integrand = 2 * (F(h - m) - F(-m))
    return V_integrand


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

TIKZ_BUILDING_3D = r"""
\begin{tikzpicture}[scale=1, >=stealth]
   %%%%%%% viền ngoài
   \draw[fill=cyan!30] (-2,-1.5) -- (1.317,-2.517) -- (3.134,-0.877) 
   .. controls +(130.3:1.9) and +(-117.5:2.2) .. (2.6, 4.6) -- (0,5.133) -- (-1.456,4.218) 
   .. controls +(-60.9:2.3) and +(54:2) .. (-2, -1.5) -- cycle
   ;
   %%%%%%%% đáy trên
   \draw (-1.456,4.218) -- (1.2,3.6) -- (2.628,4.6);
   \draw (1.317,-2.517) 
   .. controls +(99.2:2) and +(-99.5:2.1) .. (1.2, 3.6)
   foreach \i in{1,2,...,10}
   {coordinate[pos=\i/10](A\i)}
   ;
   \draw [dashed] (0,0) -- ++(3.134,-0.877);
   \draw [dashed] (0,0) -- ++(-2,-1.5);
   \clip (-2,-1.5) -- (1.317,-2.517) -- (3.134,-0.877) 
   .. controls +(130.3:1.9) and +(-117.5:2.2) .. (2.6, 4.6) -- (0.074,5.133) -- (-1.456,4.218) 
   .. controls +(-60.9:2.3) and +(54:2) .. (-2, -1.5) -- cycle;
   \draw [dashed] (0,5.133) 
   .. controls +(-81.7:1.8) and +(81:1.7) .. (0, 0) 
   coordinate[pos=0.1](B1)
   coordinate[pos=0.25](B2)
   coordinate[pos=0.39](B3)
   coordinate[pos=0.51](B4)
   coordinate[pos=0.63](B5)
   coordinate[pos=0.72](B6)
   coordinate[pos=0.81](B7)
   coordinate[pos=0.9](B8)
   coordinate[pos=0.95](B9)
   ;
   \draw [dashed] (B1) -- ++(3.134,-0.65);
   \draw [dashed] (B1) -- ++(-2,-1.45);
   \draw [dashed] (B2) -- ++(3.134,-0.8);
   \draw [dashed] (B2) -- ++(-2,-1.45);
   \draw [dashed] (B3) -- ++(3.134,-0.78);
   \draw [dashed] (B3) -- ++(-2,-1.45);
   \draw [dashed] (B4) -- ++(3.134,-0.78);
   \draw [dashed] (B4) -- ++(-2,-1.45);
   \draw [dashed] (B5) -- ++(3.134,-0.73);
   \draw [dashed] (B5) -- ++(-2,-1.45);
   \draw [dashed] (B6) -- ++(3.134,-0.78);
   \draw [dashed] (B6) -- ++(-2,-1.48);
   \draw [dashed] (B7) -- ++(3.134,-0.78);
   \draw [dashed] (B7) -- ++(-2,-1.48);
   \draw [dashed] (B8) -- ++(3.134,-0.7);
   \draw [dashed] (B8) -- ++(-2,-1.4);
   \draw [dashed] (B9) -- ++(3.134,-0.82);
   \draw [dashed] (B9) -- ++(-2,-1.5);
   \foreach \x in {1,2,...,9}
   {\draw[] (A\x)--++(-3.317,1.017);\draw[] (A\x) -- ++(1.817,1.64);}
\end{tikzpicture}
"""


def build_tikz_cross_section(h: float, m: float, k_val: float, C_val: float,
                             yA: float, yD: float) -> str:
    """
    Tạo TikZ mặt cắt đứng ABCD (hình thang cong) với 2 parabol đối xứng qua Ox.
    A(0,yA), B(0,-yA), D(h,yD), C(h,-yD), E(m,C), F(m,-C).
    Thang đo: x_scale, y_scale để vừa khung.
    """
    x_scale = 0.35
    y_scale = 0.22
    # Điểm M, N ở x = h/4
    x_M = h / 4
    y_M = k_val * (x_M - m) ** 2 + C_val
    # Format cho pgf
    def pf(v):
        return f"{v:.6f}".replace(",", ".")

    h_s, m_s = pf(h), pf(m)
    k_s, C_s = pf(k_val), pf(C_val)
    yA_s, yD_s = pf(yA), pf(yD)
    xM_s, yM_s = pf(x_M), pf(y_M)

    return r"""
\begin{tikzpicture}[scale=1, >=stealth, font=\footnotesize, line join=round]
  % Trục tọa độ
  \draw[->] (-0.8, 0) -- (""" + h_s + r"""*0.35 + 1.2, 0) node[below right] {$x$};
  \draw[->] (0, -""" + yA_s + r"""*0.22 - 0.6) -- (0, """ + yA_s + r"""*0.22 + 0.8) node[above left] {$y$};
  \fill (0,0) circle (1.2pt) node[below left] {$O$};
  % Nhãn  h trên trục Ox
  \draw (""" + h_s + r"""*0.35, 0) node[below right] {""" + str(int(h) if h == int(h) else h_s) + r"""};
  % Đoạn thẳng đứng trái AB, phải DC
  \draw[thick] (0, """ + yA_s + r"""*0.22) -- (0, -""" + yA_s + r"""*0.22);
  \draw[thick] (""" + h_s + r"""*0.35, """ + yD_s + r"""*0.22) -- (""" + h_s + r"""*0.35, -""" + yD_s + r"""*0.22);
  % Parabol trên AD
  \draw[thick, brown!70!black] (0, """ + yA_s + r"""*0.22) 
    plot[domain=0:""" + h_s + r""", samples=60] ({\x*0.35}, {(""" + k_s + r"""*(\x-""" + m_s + r""")*(\x-""" + m_s + r""")+""" + C_s + r""")*0.22})
    -- (""" + h_s + r"""*0.35, """ + yD_s + r"""*0.22);
  % Parabol dưới BC
  \draw[thick, brown!70!black] (0, -""" + yA_s + r"""*0.22)
    plot[domain=0:""" + h_s + r""", samples=60] ({\x*0.35}, {(-""" + k_s + r"""*(\x-""" + m_s + r""")*(\x-""" + m_s + r""")-""" + C_s + r""")*0.22})
    -- (""" + h_s + r"""*0.35, -""" + yD_s + r"""*0.22);
  % Đoạn MN (vuông góc Ox tại x = h/4)
  \draw (""" + xM_s + r"""*0.35, """ + yM_s + r"""*0.22) -- (""" + xM_s + r"""*0.35, -""" + yM_s + r"""*0.22);
  % Đoạn EF (vuông góc Ox tại x = m)
  \draw (""" + m_s + r"""*0.35, """ + C_s + r"""*0.22) -- (""" + m_s + r"""*0.35, -""" + C_s + r"""*0.22);
  % Điểm và nhãn
  \fill (0, """ + yA_s + r"""*0.22) circle (1.2pt) node[left] {$A$};
  \fill (0, -""" + yA_s + r"""*0.22) circle (1.2pt) node[left] {$B$};
  \fill (""" + h_s + r"""*0.35, """ + yD_s + r"""*0.22) circle (1.2pt) node[right] {$D$};
  \fill (""" + h_s + r"""*0.35, -""" + yD_s + r"""*0.22) circle (1.2pt) node[right] {$C$};
  \fill (""" + xM_s + r"""*0.35, """ + yM_s + r"""*0.22) circle (1.2pt) node[above right] {$M$};
  \fill (""" + xM_s + r"""*0.35, -""" + yM_s + r"""*0.22) circle (1.2pt) node[below right] {$N$};
  \fill (""" + m_s + r"""*0.35, """ + C_s + r"""*0.22) circle (1.2pt) node[above right] {$E$};
  \fill (""" + m_s + r"""*0.35, -""" + C_s + r"""*0.22) circle (1.2pt) node[below right] {$F$};
\end{tikzpicture}
"""


TEMPLATE_QUESTION = Template(r"""Một kiến trúc sư được giao nhiệm vụ thiết kế một tòa nhà cao ${h} m. Thiết diện nằm ngang tại mọi độ cao, vuông góc với trục thẳng đứng, luôn là một hình vuông (xem hình vẽ).

Đáy của tòa nhà là hình vuông cạnh $$L_0 = ${L0}$$ m, đỉnh là hình vuông cạnh $$L_{${h}} = ${Lh}$$ m. Thiết diện nằm ngang tại chỗ hẹp nhất của tòa nhà là hình vuông cạnh $$L_{\min} = ${Lmin}$$ m. Mặt cắt của tòa nhà theo mặt phẳng đứng chứa đường chéo đáy là một vùng phẳng giới hạn bởi hai parabol đối xứng nhau qua trục thẳng đứng đi qua tâm đáy tòa nhà. Tính thể tích của tòa nhà đó (đơn vị: m$$^3$$).

\begin{center}
${tikz_diagram}
\end{center}
""")


TEMPLATE_SOLUTION = Template(r"""
Mặt cắt của tòa nhà theo mặt phẳng đứng chứa đường chéo đáy là hình thang cong $$ABCD$$ (xem hình vẽ):

\begin{center}
${tikz_cross_section}
\end{center}

Chọn trục $$Ox$$ hướng lên trùng với trục thẳng đứng của tòa nhà, gốc $$O$$ nằm trên mặt đáy, đơn vị trên trục là mét.

Parabol $$(P)$$ có dạng $$y = k(x-m)^2 + C$$ với $$C = \dfrac{L_{\min}\sqrt{2}}{2}$$, đỉnh tại $$E(m; C)$$, $$0 < m < ${h}$$.

$$(P)$$ đi qua $$A(0; \dfrac{L_0}{\sqrt{2}}) \Rightarrow k \cdot m^2 + C = \dfrac{${L0}}{\sqrt{2}}$$ $$(1)$$.

$$(P)$$ đi qua $$B(${h}; \dfrac{L_{${h}}}{\sqrt{2}}) \Rightarrow k \cdot (${h}-m)^2 + C = \dfrac{${Lh}}{\sqrt{2}}$$ $$(2)$$.

Giải $$(1)$$, $$(2)$$ và đối chiếu $$0 < m < ${h}$$ nhận $$m = ${m_val}$$ và $$k = ${k_latex}$$.

Do đó $$f(x) = ${k_latex} \cdot (x - ${m_val})^2 + \dfrac{${Lmin}\sqrt{2}}{2}$$.

Tòa nhà nằm giữa hai mặt phẳng $$x=0$$, $$x=${h}$$. Thiết diện vuông góc trục $$Ox$$ tại $$x$$ $$(0 \le x \le ${h})$$ là hình vuông có độ dài đường chéo $$d = 2f(x)$$ m, diện tích $$S(x) = \left(\dfrac{d}{\sqrt{2}}\right)^2 = 2f^2(x)$$ m$$^2$$.

Thể tích tòa nhà là
\[ V = \int_0^{${h}} S(x)\,dx = \int_0^{${h}} 2f^2(x)\,dx = ${volume_val} \text{ m}^3. \]
""")


# ==============================================================================
# LỚP SINH ĐỀ
# ==============================================================================

class BuildingVolumeQuestion:
    """Bài toán tính thể tích tòa nhà với thiết diện vuông parabol"""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.calculated_values: Dict[str, Any] = {}
        self.config = config or GeneratorConfig()

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên với constraint hợp lệ"""
        max_attempts = 5000
        for _ in range(max_attempts):
            h = random.choice(H_VALUES)
            L0 = random.choice(L0_VALUES)
            Lh = random.choice(LH_VALUES)
            L_min = random.choice(L_MIN_VALUES)

            # L_min < L0, L_min < Lh, và L0 ≠ Lh (parabola có đỉnh bên trong)
            if L_min >= L0 or L_min >= Lh:
                continue
            if abs(L0 - Lh) < 0.5:
                continue
            # Đỉnh parabol trong (0, h) <=> m nằm giữa 0 và h
            # Với parabol có min tại m, cần L0 > L_min và Lh > L_min (đã check)
            # m = h√(L0-L_min) / (√(L0-L_min) + √(Lh-L_min))
            # m > 0 và m < h luôn thỏa khi L0 > L_min, Lh > L_min

            try:
                k, m = solve_parabola_params(h, L0, Lh, L_min)
            except (ValueError, ZeroDivisionError):
                continue

            if not (0.001 < m < h - 0.001):
                continue

            V = integrate_volume(h, k, m, L_min)
            # Ưu tiên kết quả gần số nguyên
            V_int = round(V)
            if abs(V - V_int) < 1e-3:  # sai số < 0.001 m³
                return {
                    "h": h,
                    "L0": L0,
                    "Lh": Lh,
                    "L_min": L_min,
                    "k": k,
                    "m": m,
                    "volume": V_int,
                }
            # Chấp nhận mọi kết quả nếu không tìm được integer
            if _ > max_attempts - 100:
                return {
                    "h": h,
                    "L0": L0,
                    "Lh": Lh,
                    "L_min": L_min,
                    "k": k,
                    "m": m,
                    "volume": round(V),
                }

        # Fallback: dùng bộ mẫu từ đề bài
        h, L0, Lh, L_min = 30, 26, 20, 13.75
        k, m = solve_parabola_params(h, L0, Lh, L_min)
        V = integrate_volume(h, k, m, L_min)
        return {
            "h": h,
            "L0": L0,
            "Lh": Lh,
            "L_min": L_min,
            "k": k,
            "m": m,
            "volume": round(V),
        }

    def calculate_values(self) -> Dict[str, Any]:
        """Tính toán và format các giá trị cho lời giải"""
        p = self.parameters
        h, L0, Lh, L_min = p["h"], p["L0"], p["Lh"], p["L_min"]
        k, m = p["k"], p["m"]
        volume = p["volume"]

        # Format k cho LaTeX (k thường có dạng a√2)
        # k = (L0/√2 - C) / m², C = L_min√2/2
        # Có thể viết k = α√2 với α hữu tỉ
        k_over_sqrt2 = k / math.sqrt(2)
        if abs(k_over_sqrt2 - round(k_over_sqrt2 * 100) / 100) < 1e-6:
            k_latex = format_decimal_vn(round(k_over_sqrt2 * 100) / 100) + r"\sqrt{2}"
        elif abs(k_over_sqrt2 - round(k_over_sqrt2 * 20) / 20) < 1e-6:
            frac = Fraction(round(k_over_sqrt2 * 20), 20)
            if frac.denominator == 1:
                k_latex = str(frac.numerator) + r"\sqrt{2}"
            else:
                k_latex = rf"\dfrac{{{frac.numerator}}}{{{frac.denominator}}}\sqrt{{2}}"
        else:
            k_latex = format_decimal_vn(k / math.sqrt(2), 2) + r"\sqrt{2}"

        m_str = format_number(m) if m == int(m) else format_decimal_vn(m)
        if "." in m_str:
            m_str = m_str.replace(".", ",")

        # Giá trị cho TikZ mặt cắt
        sqrt2 = math.sqrt(2)
        C_val = L_min * sqrt2 / 2
        yA = L0 / sqrt2
        yD = Lh / sqrt2
        tikz_cross_section = build_tikz_cross_section(
            h, m, k, C_val, yA, yD
        )

        return {
            "k_latex": k_latex,
            "m_val": m_str,
            "volume_val": volume,
            "tikz_cross_section": tikz_cross_section,
        }

    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        p = self.parameters
        return TEMPLATE_QUESTION.substitute(
            h=p["h"],
            L0=format_number(p["L0"]),
            Lh=format_number(p["Lh"]),
            Lmin=format_number(p["L_min"]),
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
            Lmin=format_number(p["L_min"]),
            m_val=calc["m_val"],
            k_latex=calc["k_latex"],
            volume_val=calc["volume_val"],
            tikz_cross_section=calc["tikz_cross_section"],
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
        title: str = "Bài tập Thể tích Tòa nhà Parabol",
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
    """
    Hàm main để chạy generator
    Usage: python building_volume_questions.py <num_questions> [seed]
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

        logging.info(f"Đang sinh {num_questions} câu hỏi thể tích tòa nhà...")

        questions_data: List[Tuple[str, str]] = []

        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            question = BuildingVolumeQuestion(config)
            question_content, answer = question.generate_question_only(i + 1)
            questions_data.append((question_content, answer))
            logging.info(f"  Câu {i + 1}: V = {answer} m³")

        latex_content = BuildingVolumeQuestion.create_latex_document(
            questions_data,
            title="Bài tập Thể tích Tòa nhà Parabol"
        )

        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "building_volume_questions.tex")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)

        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")

        print("\n=== ĐÁP ÁN ===")
        for i, (_, answer) in enumerate(questions_data):
            print(f"Câu {i + 1}: V = {answer} m³")

    except ValueError as e:
        print(f"Lỗi: Tham số không hợp lệ - {e}")
        print("Usage: python building_volume_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")
        raise


if __name__ == "__main__":
    main()
