"""
Hệ thống sinh đề toán diện tích / thể tích hình phẳng giới hạn bởi đường thẳng
và đường cong dạng căn bậc hai.
"""

import logging
import os
import random
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from string import Template
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

import sympy as sp

X = sp.symbols("x", real=True)
NumberLike = Union[int, float, sp.Expr]


# Hệ số góc đường thẳng f(x) = ax + b (a nhỏ để đồ thị thoải)
LINE_A_CHOICES = [1, 2, 3]  # Hệ số góc nhỏ để đường thẳng không quá dốc
# Hằng số c trong căn thức g(x) = -√(x + c)
PARABOLA_C_CHOICES = list(range(1, 11))  # 1 đến 10
# Khoảng cách từ x_start đến x_end (đảm bảo vùng gạch chéo đủ lớn)
X_END_OFFSET_CHOICES = list(range(2, 8))  # 2 đến 7 (giảm để đồ thị gọn hơn)
COMBINATION_FORMS: List[Tuple[str, Callable[[int, int], int]]] = [
    ("2a+3b", lambda a, b: 2 * a + 3 * b),
    ("a+3b", lambda a, b: a + 3 * b),
    ("a+b", lambda a, b: a + b),
    ("3a+2b", lambda a, b: 3 * a + 2 * b),
]


@dataclass
class GeneratorConfig:
    seed: Optional[int] = None
    exact_mode: bool = True


def latex_number(value: NumberLike) -> str:
    try:
        return sp.latex(sp.nsimplify(value))
    except Exception:
        return str(value)


def format_decimal(value: float, digits: int = 1) -> str:
    dot_format = f"{value:.{digits}f}"
    comma_format = dot_format.replace(".", ",")
    return f"{dot_format} | {comma_format}"


def _line_expr(params: Dict[str, Any]) -> sp.Expr:
    """f(x) = ax + b - đường thẳng"""
    return sp.nsimplify(params["line_a"] * X + params["line_b"])


def _parabola_expr(params: Dict[str, Any]) -> sp.Expr:
    """g(x) = -√(x + c) - căn thức âm (phần dưới trục Ox của parabol nằm ngang)"""
    return sp.nsimplify(-sp.sqrt(X + params["par_c"]))


def _evaluate(expr: sp.Expr, value: NumberLike) -> sp.Expr:
    return sp.nsimplify(expr.subs(X, value))


def _is_real_number(value: sp.Expr) -> bool:
    try:
        val = complex(sp.N(value))
    except Exception:
        return False
    return abs(val.imag) < 1e-9


def _to_float(value: NumberLike) -> float:
    return float(sp.N(value))


def compute_area_value(params: Dict[str, Any]) -> sp.Expr:
    """
    Tính diện tích hình phẳng giới hạn bởi f(x) và g(x).
    S = ∫_{x_start}^{x_end} [f(x) - g(x)] dx
    (f(x) > g(x) trong khoảng này)
    """
    line_expr = _line_expr(params)
    parabola_expr = _parabola_expr(params)
    diff_expr = cast(sp.Expr, line_expr - parabola_expr)  # type: ignore[operator]
    area_expr = sp.integrate(
        sp.simplify(diff_expr),
        (X, params["x_start"], params["x_end"]),
    )
    return sp.nsimplify(area_expr)


def compute_volume_inner(params: Dict[str, Any]) -> sp.Expr:
    """
    Tính phần trong của thể tích (không có π).
    
    Theo công thức từ hình:
    V = π∫[g²(x) - f²(x)]dx + π∫f²(x)dx = π∫g²(x)dx
    
    Với g(x) = √(x + c), ta có g²(x) = x + c
    Vậy V_inner = ∫_{x_start}^{x_end} (x + c) dx
    """
    par_c = params["par_c"]
    x_start = sp.nsimplify(params["x_start"])
    x_end = sp.nsimplify(params["x_end"])
    
    # g²(x) = x + c
    g_squared = X + par_c
    
    volume_inner = sp.integrate(g_squared, (X, x_start, x_end))
    return sp.nsimplify(volume_inner)


def compute_volume_value(params: Dict[str, Any]) -> sp.Expr:
    return sp.nsimplify(sp.pi * compute_volume_inner(params))


TEMPLATE_QUESTION_AREA_EXACT = Template(
    r"""
Cho hình phẳng (H) giới hạn bởi hai đường \(f(x) = ${line_func}\) và \(g(x) = ${par_func}\) như hình vẽ.
Biết diện tích (H) có dạng \(\dfrac{a}{b}\) với \(a,b\) nguyên dương tối giản. Tính ${combo_prompt}.

\begin{center}
${diagram}
\end{center}
"""
)


TEMPLATE_QUESTION_AREA_ROUNDED = Template(
    r"""
Cho hình phẳng (H) giới hạn bởi hai đường \(f(x) = ${line_func}\) và \(g(x) = ${par_func}\) như hình vẽ.
Hãy tính diện tích (H) (làm tròn đến hàng phần mười).

\begin{center}
${diagram}
\end{center}
"""
)


TEMPLATE_QUESTION_VOLUME_EXACT = Template(
    r"""
Cho hình phẳng (H) được tạo bởi hai đường \(f(x) = ${line_func}\) và \(g(x) = ${par_func}\) như hình.
Khi quay (H) xung quanh trục Ox, ta được khối tròn xoay có thể tích dạng \(\dfrac{a\pi}{b}\) với \(a,b\) nguyên dương.
Tính ${combo_prompt}.

\begin{center}
${diagram}
\end{center}
"""
)


TEMPLATE_QUESTION_VOLUME_ROUNDED = Template(
    r"""
Cho hình phẳng (H) được tạo bởi hai đường \(f(x) = ${line_func}\) và \(g(x) = ${par_func}\) như hình.
Khi quay (H) xung quanh trục Ox, hãy tính thể tích khối tròn xoay thu được (làm tròn đến hàng phần mười).

\begin{center}
${diagram}
\end{center}
"""
)


TEMPLATE_SOLUTION_AREA_EXACT = Template(
    r"""
Cho hàm số \(f(x) = ${line_func}\) và \(g(x) = ${par_func}\).

Tìm giao điểm của \(f(x)\) và \(g(x)\):
\[
\begin{aligned}
f(x) = g(x) &\Leftrightarrow ${line_func} = ${par_func}\\
            &\Leftrightarrow x = ${x_start}.
\end{aligned}
\]

Diện tích hình phẳng:
\[
\begin{aligned}
S &= \int_{${x_start}}^{${x_end}} \big(f(x) - g(x)\big)\,dx\\
  &= \int_{${x_start}}^{${x_end}} \left(${area_integrand}\right)\,dx\\
  &= ${area_expr}.
\end{aligned}
\]

Kết luận:
\[
${combo_expr} = ${combo_value}.
\]
"""
)


TEMPLATE_SOLUTION_AREA_ROUNDED = Template(
    r"""
Cho hàm số \(f(x) = ${line_func}\) và \(g(x) = ${par_func}\).

Tìm giao điểm của \(f(x)\) và \(g(x)\):
\[
\begin{aligned}
f(x) = g(x) &\Leftrightarrow ${line_func} = ${par_func}\\
            &\Leftrightarrow x = ${x_start}.
\end{aligned}
\]

Diện tích hình phẳng:
\[
\begin{aligned}
S &= \int_{${x_start}}^{${x_end}} \big(f(x) - g(x)\big)\,dx\\
  &= \int_{${x_start}}^{${x_end}} \left(${area_integrand}\right)\,dx\\
  &= ${area_expr}.
\end{aligned}
\]

Kết luận: \(S \approx ${area_round}\).
"""
)


TEMPLATE_SOLUTION_VOLUME_EXACT = Template(
    r"""
Cho hàm số \(f(x) = ${line_func}\) và \(g(x) = ${par_func}\).

Tìm giao điểm của \(f(x)\) và \(g(x)\):
\[
\begin{aligned}
f(x) = g(x) &\Leftrightarrow ${line_func} = ${par_func}\\
            &\Leftrightarrow x = ${x_start}.
\end{aligned}
\]

Thể tích khối tròn xoay:
\[
\begin{aligned}
V &= \pi\int_{${x_start}}^{${x_end}} \Big[g^2(x) - f^2(x)\Big]\,dx + \pi\int_{${x_start}}^{${x_end}} f^2(x)\,dx\\
  &= \pi\int_{${x_start}}^{${x_end}} g^2(x)\,dx\\
  &= \pi\int_{${x_start}}^{${x_end}} \left(${par_sq}\right)\,dx\\
  &= \pi\cdot ${volume_inner}.
\end{aligned}
\]

Kết luận:
\[
${combo_expr} = ${combo_value}.
\]
"""
)


TEMPLATE_SOLUTION_VOLUME_ROUNDED = Template(
    r"""
Cho hàm số \(f(x) = ${line_func}\) và \(g(x) = ${par_func}\).

Tìm giao điểm của \(f(x)\) và \(g(x)\):
\[
\begin{aligned}
f(x) = g(x) &\Leftrightarrow ${line_func} = ${par_func}\\
            &\Leftrightarrow x = ${x_start}.
\end{aligned}
\]

Thể tích khối tròn xoay:
\[
\begin{aligned}
V &= \pi\int_{${x_start}}^{${x_end}} \Big[g^2(x) - f^2(x)\Big]\,dx + \pi\int_{${x_start}}^{${x_end}} f^2(x)\,dx\\
  &= \pi\int_{${x_start}}^{${x_end}} g^2(x)\,dx\\
  &= \pi\int_{${x_start}}^{${x_end}} \left(${par_sq}\right)\,dx\\
  &= \pi\cdot ${volume_inner}.
\end{aligned}
\]

Kết luận: \(V \approx ${volume_round}\).
"""
)


MAX_ATTEMPTS = 128


class BaseRegionQuestion(ABC):
    """
    Lớp cơ sở cho bài toán hình phẳng giữa đường thẳng và đường căn.
    """

    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.correct_answer: Optional[str] = None
        self.config = config or GeneratorConfig()

    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def calculate_answer(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_question_text(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_solution(self) -> str:
        raise NotImplementedError

    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        logging.info("Đang tạo câu hỏi %s", question_number)
        self.parameters = self.generate_parameters()
        self._prepare_common_parameters()
        self.correct_answer = self.calculate_answer()
        question_text = self.generate_question_text().strip()
        solution_text = self.generate_solution().strip()
        content = f"Câu {question_number}: {question_text}\n\n"
        content += "Lời giải:\n\n" + solution_text + "\n"
        return content, self.correct_answer or ""

    @staticmethod
    def create_latex_document_with_format(
        questions_data: List[Tuple[str, str]],
        title: str = "Câu hỏi Hình phẳng",
    ) -> str:
        latex_content = r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage{tikz}
\usetikzlibrary{patterns}
\begin{document}
"""
        latex_content += f"\\title{{{title}}}\n\\maketitle\n\n"
        for question_content, correct_answer in questions_data:
            latex_content += question_content + "\n\n"
            latex_content += f"Đáp án: {correct_answer}\n\n"
        latex_content += "\\end{document}"
        return latex_content

    def _prepare_common_parameters(self) -> None:
        if not self.parameters:
            return
        params = self.parameters
        params["x_start_latex"] = latex_number(params["x_start"])
        params["x_end_latex"] = latex_number(params["x_end"])
        # Tính integrand cho diện tích: f(x) - g(x)
        area_integrand = sp.simplify(params["line_expr"] - params["par_expr"])
        params["area_integrand_latex"] = sp.latex(area_integrand)
        # Tính bình phương cho thể tích: g²(x) = x + c
        par_sq = sp.simplify(params["par_expr"] ** 2)
        params["par_sq_latex"] = sp.latex(par_sq)

    def _build_region_profile(self) -> Dict[str, Any]:
        """
        Sinh tham số cho hình phẳng giới hạn bởi f(x) = ax + b và g(x) = -√(x + c).
        
        Logic:
        - g(x) = -√(x + c) là phần dưới trục Ox của parabol nằm ngang
        - Giao điểm f(x) ∩ g(x) tại y = 0: x_start = -c (gốc căn thức)
        - f(x) đi qua (-c, 0): b = a*c => f(x) = a(x + c)
        - x_end = x_start + offset (random)
        - Vùng gạch chéo nằm dưới trục Ox
        """
        for _ in range(MAX_ATTEMPTS):
            line_a = random.choice(LINE_A_CHOICES)
            par_c = random.choice(PARABOLA_C_CHOICES)
            x_end_offset = random.choice(X_END_OFFSET_CHOICES)
            
            # Giao điểm tại y = 0: x_start = -par_c
            x_start = sp.Integer(-par_c)
            x_end = sp.Integer(-par_c + x_end_offset)
            
            # f(x) đi qua điểm (-par_c, 0): a*(-par_c) + b = 0 => b = a*par_c
            line_b = line_a * par_c
            
            params: Dict[str, Any] = {
                "line_a": line_a,
                "line_b": line_b,
                "par_c": par_c,
            }
            
            line_expr = _line_expr(params)
            parabola_expr = _parabola_expr(params)
            
            # Kiểm tra f(x) > g(x) trong (x_start, x_end]
            # Vì g(x) < 0 và f(x) có thể > 0 hoặc < 0, cần f(x) > g(x)
            interval = x_end - x_start
            quarter = sp.nsimplify(interval / 4)
            sample_points = [
                x_start + quarter,
                x_start + 2 * quarter,
                x_start + 3 * quarter,
            ]
            
            ok_segment = True
            for point in sample_points:
                line_val = _evaluate(line_expr, point)
                parabola_val = _evaluate(parabola_expr, point)
                # f(x) phải lớn hơn g(x) (g(x) âm, f(x) dương)
                if sp.N(line_val) <= sp.N(parabola_val):
                    ok_segment = False
                    break
            
            if not ok_segment:
                continue
            
            params["x_start"] = x_start
            params["x_end"] = x_end
            params["line_expr"] = line_expr
            params["par_expr"] = parabola_expr
            
            # Validation: kiểm tra kết quả tích phân là số đẹp
            try:
                area_val = compute_area_value(params)
                area_num, area_den = sp.fraction(sp.nsimplify(area_val))
                if abs(int(area_num)) >= 100 or abs(int(area_den)) >= 100:
                    continue
                
                vol_inner = compute_volume_inner(params)
                vol_num, vol_den = sp.fraction(sp.nsimplify(vol_inner))
                if abs(int(vol_num)) >= 100 or abs(int(vol_den)) >= 100:
                    continue
            except Exception:
                continue
            
            params["line_latex"] = sp.latex(line_expr)
            params["par_latex"] = sp.latex(parabola_expr)
            return params
        
        raise RuntimeError("Không sinh được cấu hình hợp lệ cho hình phẳng")

    def generate_tikz_diagram(self) -> str:
        """
        Sinh mã TikZ cho hình vẽ minh họa.
        
        - Vùng gạch chéo: giữa f(x) và g(x) từ x_start đến x_end
        - g(x) = -√(x+c) là căn âm (nằm dưới trục Ox)
        - Giao điểm tại y = 0 (trên trục Ox)
        - Ẩn tọa độ giao điểm
        - Thêm đường thẳng đứng tại x = x_end
        """
        if not self.parameters:
            return ""
        params = self.parameters
        line_a = params["line_a"]
        line_b = params["line_b"]
        par_c = params["par_c"]
        line_expr = params["line_expr"]
        par_expr = params["par_expr"]
        x_start = _to_float(params["x_start"])
        x_end = _to_float(params["x_end"])
        line_label = params["line_latex"]
        par_label = params["par_latex"]

        def fmt(value: NumberLike) -> str:
            return f"{_to_float(value):.4f}"

        interval = max(x_end - x_start, 1.0)
        x_extend_right = max(1.5, 0.5 * interval)
        x_extend_left = max(1.0, 0.5 * interval)
        
        # Miền xác định của căn thức: x >= -par_c
        sqrt_domain_start = -par_c
        sqrt_domain_end = x_end + x_extend_right
        
        line_domain_start = min(x_start - x_extend_left, sqrt_domain_start)
        line_domain_end = x_end + x_extend_right

        x_axis_min = min(line_domain_start - 0.5, sqrt_domain_start - 0.5, -1.5)
        x_axis_max = max(line_domain_end + 0.5, 2.5)

        # Tính y của đường thẳng tại các điểm biên
        y_line_start = line_a * line_domain_start + line_b
        y_line_end = line_a * line_domain_end + line_b
        
        # y của căn tại x_end (âm vì g(x) = -√(x+c))
        par_at_end = _to_float(_evaluate(par_expr, params["x_end"]))
        
        # Trục y cần bao gồm cả phần âm (g(x) < 0)
        y_axis_min = min(par_at_end - 0.5, -2.5)
        y_axis_max = max(y_line_start, y_line_end, 2.5) + 0.5

        # Vị trí đặt nhãn đường cong
        mid_line_x = x_start + 0.5 * interval
        mid_line_y = _to_float(_evaluate(line_expr, mid_line_x))
        # Vị trí nhãn g(x): đặt ở bên phải, xa vùng gạch chéo
        mid_par_x = x_end + 0.3 * interval
        mid_par_y = _to_float(_evaluate(par_expr, mid_par_x))

        # Giá trị y tại x_end
        line_end_val = _to_float(_evaluate(line_expr, params["x_end"]))
        par_end_val = _to_float(_evaluate(par_expr, params["x_end"]))
        
        # Giá trị y tại x_start (giao điểm tại y = 0)
        line_start_val = _to_float(_evaluate(line_expr, params["x_start"]))
        
        # Label cho x_end
        x_end_latex = latex_number(params["x_end"])

        tikz = rf"""
\begin{{tikzpicture}}[scale=.85,samples=200]
\draw[->, thick] ({fmt(x_axis_min)},0) -- ({fmt(x_axis_max)},0) node[below] {{$x$}};
\draw[->, thick] (0,{fmt(y_axis_min)}) -- (0,{fmt(y_axis_max)}) node[left] {{$y$}};
\node[below right] at (0,0) {{$O$}};
% Vùng gạch chéo giữa f(x) và g(x) từ x_start đến x_end
\fill[pattern=north west lines, pattern color=gray!70]
  plot[domain={fmt(x_start)}:{fmt(x_end)}] (\x, {{ {line_a}*\x + {line_b} }})
  -- plot[domain={fmt(x_end)}:{fmt(x_start)}] (\x, {{ -sqrt(\x + {par_c}) }});
% Đường thẳng f(x) = ax + b
\draw[very thick, domain={fmt(line_domain_start)}:{fmt(line_domain_end)}] plot (\x, {{ {line_a}*\x + {line_b} }});
\node[above left,rotate=45,scale=0.75,yshift=4pt] at ({fmt(mid_line_x)}, {fmt(mid_line_y)}) {{$f(x)={line_label}$}};
% Căn thức g(x) = -sqrt(x + c) (phần dưới trục Ox)
\draw[very thick, domain={fmt(sqrt_domain_start)}:{fmt(sqrt_domain_end)}] plot (\x, {{ -sqrt(\x + {par_c}) }});
\node[below,scale=0.75] at ({fmt(mid_par_x)}, {fmt(mid_par_y)}) {{$g(x)={par_label}$}};
% Đường thẳng đứng tại x = x_end (giới hạn phải của vùng gạch chéo)
\draw[dashed] ({fmt(x_end)}, {fmt(line_end_val)}) -- ({fmt(x_end)}, {fmt(par_end_val)});
% Nhãn x_end tại trục Ox
\node[above] at ({fmt(x_end)}, 0) {{${x_end_latex}$}};
% Đánh dấu giao điểm f(x) và g(x) tại y = 0
\fill ({fmt(x_start)}, 0) circle (2pt);
\end{{tikzpicture}}
"""
        return "\n".join(line for line in tikz.splitlines() if line.strip())


class RegionAreaExactQuestion(BaseRegionQuestion):
    def generate_parameters(self) -> Dict[str, Any]:
        return self._build_region_profile()

    def calculate_answer(self) -> str:
        area_exact = compute_area_value(self.parameters)
        area_exact = sp.nsimplify(area_exact)
        num, den = sp.fraction(area_exact)
        num_int = int(sp.Integer(sp.nsimplify(num)))
        den_int = int(sp.Integer(sp.nsimplify(den)))
        if den_int < 0:
            num_int *= -1
            den_int *= -1
        combo_expr, combo_fn = random.choice(COMBINATION_FORMS)
        combo_value = combo_fn(num_int, den_int)
        self.parameters.update(
            {
                "area_exact": area_exact,
                "area_fraction_num": num_int,
                "area_fraction_den": den_int,
                "combo_expr": combo_expr,
                "combo_value": latex_number(combo_value),
                "area_expr_latex": latex_number(area_exact),
            }
        )
        return latex_number(combo_value)

    def generate_question_text(self) -> str:
        params = self.parameters
        return TEMPLATE_QUESTION_AREA_EXACT.substitute(
            line_func=params["line_latex"],
            par_func=params["par_latex"],
            combo_prompt=params["combo_expr"],
            diagram=self.generate_tikz_diagram(),
        ).strip()

    def generate_solution(self) -> str:
        params = self.parameters
        return TEMPLATE_SOLUTION_AREA_EXACT.substitute(
            line_func=params["line_latex"],
            par_func=params["par_latex"],
            x_start=params["x_start_latex"],
            x_end=params["x_end_latex"],
            area_integrand=params["area_integrand_latex"],
            area_expr=params["area_expr_latex"],
            combo_expr=params["combo_expr"],
            combo_value=params["combo_value"],
        ).strip()


class RegionAreaRoundedQuestion(BaseRegionQuestion):
    def generate_parameters(self) -> Dict[str, Any]:
        return self._build_region_profile()

    def calculate_answer(self) -> str:
        area_exact = sp.nsimplify(compute_area_value(self.parameters))
        numeric_area = float(area_exact.evalf())
        rounded = round(numeric_area, 1)
        rounded_display = format_decimal(rounded)
        self.parameters.update(
            {
                "area_exact": area_exact,
                "area_expr_latex": latex_number(area_exact),
                "area_round": rounded_display,
            }
        )
        return rounded_display

    def generate_question_text(self) -> str:
        params = self.parameters
        return TEMPLATE_QUESTION_AREA_ROUNDED.substitute(
            line_func=params["line_latex"],
            par_func=params["par_latex"],
            diagram=self.generate_tikz_diagram(),
        ).strip()

    def generate_solution(self) -> str:
        params = self.parameters
        return TEMPLATE_SOLUTION_AREA_ROUNDED.substitute(
            line_func=params["line_latex"],
            par_func=params["par_latex"],
            x_start=params["x_start_latex"],
            x_end=params["x_end_latex"],
            area_integrand=params["area_integrand_latex"],
            area_expr=params["area_expr_latex"],
            area_round=params["area_round"],
        ).strip()


class RegionVolumeExactQuestion(BaseRegionQuestion):
    def generate_parameters(self) -> Dict[str, Any]:
        return self._build_region_profile()

    def calculate_answer(self) -> str:
        volume_inner = sp.nsimplify(compute_volume_inner(self.parameters))
        volume_exact = sp.nsimplify(sp.pi * volume_inner)
        num, den = sp.fraction(volume_inner)
        num_int = int(sp.Integer(sp.nsimplify(num)))
        den_int = int(sp.Integer(sp.nsimplify(den)))
        if den_int < 0:
            num_int *= -1
            den_int *= -1
        combo_expr, combo_fn = random.choice(COMBINATION_FORMS)
        combo_value = combo_fn(num_int, den_int)
        self.parameters.update(
            {
                "volume_inner": volume_inner,
                "volume_exact": volume_exact,
                "volume_inner_latex": latex_number(volume_inner),
                "combo_expr": combo_expr,
                "combo_value": latex_number(combo_value),
            }
        )
        return latex_number(combo_value)

    def generate_question_text(self) -> str:
        params = self.parameters
        return TEMPLATE_QUESTION_VOLUME_EXACT.substitute(
            line_func=params["line_latex"],
            par_func=params["par_latex"],
            combo_prompt=params["combo_expr"],
            diagram=self.generate_tikz_diagram(),
        ).strip()

    def generate_solution(self) -> str:
        params = self.parameters
        return TEMPLATE_SOLUTION_VOLUME_EXACT.substitute(
            line_func=params["line_latex"],
            par_func=params["par_latex"],
            x_start=params["x_start_latex"],
            x_end=params["x_end_latex"],
            par_sq=params["par_sq_latex"],
            volume_inner=params["volume_inner_latex"],
            combo_expr=params["combo_expr"],
            combo_value=params["combo_value"],
        ).strip()


class RegionVolumeRoundedQuestion(BaseRegionQuestion):
    def generate_parameters(self) -> Dict[str, Any]:
        return self._build_region_profile()

    def calculate_answer(self) -> str:
        volume_inner = sp.nsimplify(compute_volume_inner(self.parameters))
        volume_exact = sp.nsimplify(sp.pi * volume_inner)
        numeric_volume = float(volume_exact.evalf())
        rounded = round(numeric_volume, 1)
        rounded_display = format_decimal(rounded)
        self.parameters.update(
            {
                "volume_inner": volume_inner,
                "volume_exact": volume_exact,
                "volume_inner_latex": latex_number(volume_inner),
                "volume_round": rounded_display,
            }
        )
        return rounded_display

    def generate_question_text(self) -> str:
        params = self.parameters
        return TEMPLATE_QUESTION_VOLUME_ROUNDED.substitute(
            line_func=params["line_latex"],
            par_func=params["par_latex"],
            diagram=self.generate_tikz_diagram(),
        ).strip()

    def generate_solution(self) -> str:
        params = self.parameters
        return TEMPLATE_SOLUTION_VOLUME_ROUNDED.substitute(
            line_func=params["line_latex"],
            par_func=params["par_latex"],
            x_start=params["x_start_latex"],
            x_end=params["x_end_latex"],
            par_sq=params["par_sq_latex"],
            volume_inner=params["volume_inner_latex"],
            volume_round=params["volume_round"],
        ).strip()


def get_available_question_types() -> List[type]:
    return [
        RegionAreaExactQuestion,
        RegionAreaRoundedQuestion,
        RegionVolumeExactQuestion,
        RegionVolumeRoundedQuestion,
    ]


def main():
    """
    Sinh file LaTeX chứa các câu hỏi diện tích/thể tích hình phẳng.
    Usage: python region_area_volume_questions.py <num_questions> [question_type] [seed]
           question_type: 1=Diện tích (exact), 2=Diện tích (làm tròn),
                          3=Thể tích (exact), 4=Thể tích (làm tròn)
    """

    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 4

        question_type_param: Optional[int] = None
        if len(sys.argv) > 2:
            try:
                question_type_param = int(sys.argv[2])
                if question_type_param not in (1, 2, 3, 4):
                    print("⚠️  question_type phải trong [1, 2, 3, 4]")
                    question_type_param = None
            except ValueError:
                question_type_param = None

        seed: Optional[int] = None
        if len(sys.argv) > 3:
            try:
                seed = int(sys.argv[3])
            except ValueError:
                seed = None
        if seed is None:
            env_seed = os.environ.get("OPT_SEED")
            if env_seed is not None:
                try:
                    seed = int(env_seed)
                except ValueError:
                    seed = None
        if seed is not None:
            random.seed(seed)

        question_types = get_available_question_types()
        type_map = {
            1: RegionAreaExactQuestion,
            2: RegionAreaRoundedQuestion,
            3: RegionVolumeExactQuestion,
            4: RegionVolumeRoundedQuestion,
        }
        type_names = {
            1: "Diện tích (exact)",
            2: "Diện tích (làm tròn)",
            3: "Thể tích (exact)",
            4: "Thể tích (làm tròn)",
        }

        selected_type = type_map.get(question_type_param) if question_type_param else None
        questions_data: List[Tuple[str, str]] = []

        for i in range(1, num_questions + 1):
            try:
                question_class = selected_type or random.choice(question_types)
                instance = question_class(GeneratorConfig())
                question_content, answer = instance.generate_question_only(i)
                questions_data.append((question_content, answer))
                logging.info("Đã tạo câu hỏi %s thành công", i)
            except Exception as exc:
                logging.error("Lỗi tạo câu hỏi %s: %s", i, exc, exc_info=True)
                continue

        if not questions_data:
            print("❌ Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)

        if question_type_param and question_type_param in type_names:
            title = f"Câu hỏi {type_names[question_type_param]}"
        else:
            title = "Câu hỏi Hình phẳng"

        latex_content = BaseRegionQuestion.create_latex_document_with_format(
            questions_data, title
        )

        filename = "region_questions.tex"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)

        print(f"✅ Đã tạo {filename} với {len(questions_data)} câu hỏi")
        if question_type_param:
            print(f"📝 Dạng: {type_names.get(question_type_param, 'Ngẫu nhiên')}")
        else:
            print("📝 Dạng: Ngẫu nhiên")
        print(f"📄 Biên dịch bằng: xelatex {filename}")
        print("📋 Format: lời giải tự luận")

    except ValueError:
        print("❌ Lỗi: Vui lòng nhập số câu hỏi hợp lệ")
        sys.exit(1)
    except Exception as exc:
        print(f"❌ Lỗi: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

