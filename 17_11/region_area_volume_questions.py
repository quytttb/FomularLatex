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


LINE_A_CHOICES = [1, 2, 3]
LINE_B_CHOICES = [2, 3, 4, 5]
PARABOLA_C_CHOICES = [1, 2, 3, 4]
PARABOLA_SIGN_CHOICES = [-1]
TARGET_SQUARES = [1, 4, 9]
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
    return sp.nsimplify(params["line_a"] * X + params["line_b"])


def _parabola_expr(params: Dict[str, Any]) -> sp.Expr:
    return sp.nsimplify(params["par_sign"] * sp.sqrt(X + params["par_c"]))


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


def _ordered_functions(params: Dict[str, Any]) -> Tuple[sp.Expr, sp.Expr]:
    line = _line_expr(params)
    parabola = _parabola_expr(params)
    mid_point = sp.nsimplify((params["x_start"] + params["x_end"]) / 2)
    line_mid = _evaluate(line, mid_point)
    parabola_mid = _evaluate(parabola, mid_point)
    if sp.N(line_mid) >= sp.N(parabola_mid):
        return line, parabola
    return parabola, line


def compute_area_value(params: Dict[str, Any]) -> sp.Expr:
    upper_expr, lower_expr = _ordered_functions(params)
    diff_expr = cast(sp.Expr, upper_expr - lower_expr)  # type: ignore[operator]
    area_expr = sp.integrate(
        sp.simplify(diff_expr),
        (X, params["x_start"], params["x_end"]),
    )
    return sp.nsimplify(area_expr)


def compute_volume_inner(params: Dict[str, Any]) -> sp.Expr:
    line_expr = _line_expr(params)
    parabola_expr = _parabola_expr(params)
    x_start = sp.nsimplify(params["x_start"])
    x_end = sp.nsimplify(params["x_end"])

    line_sq = sp.simplify(line_expr**2)
    parabola_sq = sp.simplify(parabola_expr**2)
    diff_expr = sp.simplify(line_sq - parabola_sq)

    critical_points: List[sp.Expr] = [x_start, x_end]
    try:
        roots = sp.solve(sp.Eq(diff_expr, 0), X)
    except Exception:
        roots = []

    for root in roots:
        if not _is_real_number(root):
            continue
        root_val = sp.nsimplify(root)
        if _to_float(root_val) <= _to_float(x_start) + 1e-9:
            continue
        if _to_float(root_val) >= _to_float(x_end) - 1e-9:
            continue
        critical_points.append(root_val)

    unique_points: List[sp.Expr] = []
    for point in critical_points:
        point = sp.nsimplify(point)
        if any(sp.simplify(point - existing) == 0 for existing in unique_points):
            continue
        unique_points.append(point)

    unique_points.sort(key=_to_float)

    total_expr: sp.Expr = sp.Integer(0)
    for left, right in zip(unique_points, unique_points[1:]):
        segment_width = cast(sp.Expr, right - left)  # type: ignore[operator]
        if _to_float(segment_width) <= 1e-9:
            continue
        mid_point = sp.nsimplify(
            cast(sp.Expr, (left + right) / 2)  # type: ignore[operator]
        )
        line_mid = _evaluate(line_sq, mid_point)
        parabola_mid = _evaluate(parabola_sq, mid_point)
        if sp.N(line_mid) >= sp.N(parabola_mid):
            outer_expr = line_sq
            inner_expr = parabola_sq
        else:
            outer_expr = parabola_sq
            inner_expr = line_sq
        segment_expr = sp.integrate(
            sp.simplify(outer_expr - inner_expr),
            (X, left, right),
        )
        total_expr = sp.nsimplify(
            total_expr + segment_expr  # type: ignore[operator]
        )

    return sp.nsimplify(total_expr)


def compute_volume_value(params: Dict[str, Any]) -> sp.Expr:
    return sp.nsimplify(sp.pi * compute_volume_inner(params))


TEMPLATE_QUESTION_AREA_EXACT = Template(
    r"""
Cho hình phẳng (H) giới hạn bởi hai đường \(y_1 = ${line_func}\) và \(y_2 = ${par_func}\) như hình vẽ.
Biết diện tích (H) có dạng \(\dfrac{a}{b}\) với \(a,b\) nguyên dương tối giản. Tính ${combo_prompt}.

\begin{center}
${diagram}
\end{center}
"""
)


TEMPLATE_QUESTION_AREA_ROUNDED = Template(
    r"""
Cho hình phẳng (H) giới hạn bởi hai đường \(y_1 = ${line_func}\) và \(y_2 = ${par_func}\) như hình vẽ.
Hãy tính diện tích (H) (làm tròn đến hàng phần mười).

\begin{center}
${diagram}
\end{center}
"""
)


TEMPLATE_QUESTION_VOLUME_EXACT = Template(
    r"""
Cho hình phẳng (H) được tạo bởi hai đường \(y_1 = ${line_func}\) và \(y_2 = ${par_func}\) như hình.
Khi quay (H) xung quanh trục Ox, ta được khối tròn xoay có thể tích dạng \(\dfrac{a\pi}{b}\) với \(a,b\) nguyên dương.
Tính ${combo_prompt}.

\begin{center}
${diagram}
\end{center}
"""
)


TEMPLATE_QUESTION_VOLUME_ROUNDED = Template(
    r"""
Cho hình phẳng (H) được tạo bởi hai đường \(y_1 = ${line_func}\) và \(y_2 = ${par_func}\) như hình.
Khi quay (H) xung quanh trục Ox, hãy tính thể tích khối tròn xoay thu được (làm tròn đến hàng phần mười).

\begin{center}
${diagram}
\end{center}
"""
)


TEMPLATE_SOLUTION_AREA_EXACT = Template(
    r"""
Cho hàm số \(f(x) = ${line_func}\) và \(y_2 = ${par_func}\).

Ta có:
\[
\begin{aligned}
f(x)\cap Ox &\Leftrightarrow f(x) = 0\\
            &\Leftrightarrow ${line_func} = 0\\
            &\Leftrightarrow x = ${x_start}.
\end{aligned}
\]

Lấy đối xứng \(y_2\) qua \(Ox\) được \(g(x) = ${par_ref_func}\).

\[
\begin{aligned}
f(x)\cap g(x) &\Leftrightarrow f(x) = g(x)\\
              &\Leftrightarrow ${line_func} = ${par_ref_func}\\
              &\Leftrightarrow x = ${x_end}.
\end{aligned}
\]

Diện tích hình phẳng:
\[
\begin{aligned}
S &= \int_{${x_start}}^{${x_end}} \big(f(x) - y_2\big)\,dx\\
  &\Leftrightarrow S = \int_{${x_start}}^{${x_end}} \left(${area_integrand}\right)\,dx\\
  &\Leftrightarrow S = ${area_expr}.
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
Cho hàm số \(f(x) = ${line_func}\) và \(y_2 = ${par_func}\).

Ta có:
\[
\begin{aligned}
f(x)\cap Ox &\Leftrightarrow f(x) = 0\\
            &\Leftrightarrow ${line_func} = 0\\
            &\Leftrightarrow x = ${x_start}.
\end{aligned}
\]

Lấy đối xứng \(y_2\) qua \(Ox\) được \(g(x) = ${par_ref_func}\).

\[
\begin{aligned}
f(x)\cap g(x) &\Leftrightarrow f(x) = g(x)\\
              &\Leftrightarrow ${line_func} = ${par_ref_func}\\
              &\Leftrightarrow x = ${x_end}.
\end{aligned}
\]

Diện tích hình phẳng:
\[
\begin{aligned}
S &= \int_{${x_start}}^{${x_end}} \big(f(x) - y_2\big)\,dx\\
  &\Leftrightarrow S = \int_{${x_start}}^{${x_end}} \left(${area_integrand}\right)\,dx\\
  &\Leftrightarrow S = ${area_expr}.
\end{aligned}
\]

Kết luận: \(S \approx ${area_round}\).
"""
)


TEMPLATE_SOLUTION_VOLUME_EXACT = Template(
    r"""
Cho hàm số \(f(x) = ${line_func}\) và \(y_2 = ${par_func}\).

Ta có:
\[
\begin{aligned}
f(x)\cap Ox &\Leftrightarrow f(x) = 0\\
            &\Leftrightarrow ${line_func} = 0\\
            &\Leftrightarrow x = ${x_start}.
\end{aligned}
\]

Lấy đối xứng \(y_2\) qua \(Ox\) được \(g(x) = ${par_ref_func}\).

\[
\begin{aligned}
f(x)\cap g(x) &\Leftrightarrow f(x) = g(x)\\
              &\Leftrightarrow ${line_func} = ${par_ref_func}\\
              &\Leftrightarrow x = ${x_end}.
\end{aligned}
\]

Thể tích khối tròn xoay:
\[
\begin{aligned}
V &= \pi\int_{${x_start}}^{${x_end}} \Big[(f(x))^2 - (g(x))^2\Big]\,dx\\
  &\Leftrightarrow V = \pi\int_{${x_start}}^{${x_end}} \left(${line_sq} - ${par_ref_sq}\right)\,dx\\
  &\Leftrightarrow V = \pi\int_{${x_start}}^{${x_end}} \left(${volume_integrand}\right)\,dx\\
  &\Leftrightarrow V = \pi\cdot ${volume_inner}.
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
Cho hàm số \(f(x) = ${line_func}\) và \(y_2 = ${par_func}\).

Ta có:
\[
\begin{aligned}
f(x)\cap Ox &\Leftrightarrow f(x) = 0\\
            &\Leftrightarrow ${line_func} = 0\\
            &\Leftrightarrow x = ${x_start}.
\end{aligned}
\]

Lấy đối xứng \(y_2\) qua \(Ox\) được \(g(x) = ${par_ref_func}\).

\[
\begin{aligned}
f(x)\cap g(x) &\Leftrightarrow f(x) = g(x)\\
              &\Leftrightarrow ${line_func} = ${par_ref_func}\\
              &\Leftrightarrow x = ${x_end}.
\end{aligned}
\]

Thể tích khối tròn xoay:
\[
\begin{aligned}
V &= \pi\int_{${x_start}}^{${x_end}} \Big[(f(x))^2 - (g(x))^2\Big]\,dx\\
  &\Leftrightarrow V = \pi\int_{${x_start}}^{${x_end}} \left(${line_sq} - ${par_ref_sq}\right)\,dx\\
  &\Leftrightarrow V = \pi\int_{${x_start}}^{${x_end}} \left(${volume_integrand}\right)\,dx\\
  &\Leftrightarrow V = \pi\cdot ${volume_inner}.
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
        par_ref_expr = sp.sqrt(X + params["par_c"])
        params["par_ref_expr"] = par_ref_expr
        params["par_ref_latex"] = sp.latex(par_ref_expr)
        params["x_start_latex"] = latex_number(params["x_start"])
        params["x_end_latex"] = latex_number(params["x_end"])
        area_integrand = sp.simplify(params["line_expr"] - params["par_expr"])
        params["area_integrand_latex"] = sp.latex(area_integrand)
        line_sq = sp.simplify(params["line_expr"] ** 2)
        par_ref_sq = sp.simplify(par_ref_expr ** 2)
        params["line_sq_latex"] = sp.latex(line_sq)
        params["par_ref_sq_latex"] = sp.latex(par_ref_sq)
        params["volume_integrand_latex"] = sp.latex(sp.simplify(line_sq - par_ref_sq))

    def _build_region_profile(self) -> Dict[str, Any]:
        for _ in range(MAX_ATTEMPTS):
            line_a = random.choice(LINE_A_CHOICES)
            par_c = random.choice(PARABOLA_C_CHOICES)
            params: Dict[str, Any] = {
                "line_a": line_a,
                "line_b": line_a * par_c,
                "par_c": par_c,
                "par_sign": -1,
            }
            x_start = sp.Integer(-par_c)
            line_expr = _line_expr(params)
            parabola_expr = _parabola_expr(params)
            x_end = sp.nsimplify(sp.Rational(1, line_a**2) - par_c)
            interval = x_end - x_start
            if _to_float(interval) < 1 - 1e-9:
                continue
            quarter = sp.nsimplify(interval / 4)
            if _to_float(quarter) <= 1e-9:
                continue
            sample_points = [
                x_start + quarter,
                x_start + 2 * quarter,
                x_start + 3 * quarter,
            ]
            ok_segment = True
            for point in sample_points:
                line_val = _evaluate(line_expr, point)
                parabola_val = _evaluate(parabola_expr, point)
                if sp.N(line_val) <= sp.N(parabola_val):
                    ok_segment = False
                    break
                if sp.N(line_val) <= 0:
                    ok_segment = False
                    break
            if not ok_segment:
                continue

            params["x_start"] = x_start
            params["x_end"] = sp.nsimplify(x_end)
            params["line_expr"] = line_expr
            params["par_expr"] = parabola_expr
            params["line_latex"] = sp.latex(line_expr)
            params["par_latex"] = sp.latex(parabola_expr)
            return params
        raise RuntimeError("Không sinh được cấu hình hợp lệ cho hình phẳng")

    def generate_tikz_diagram(self) -> str:
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
        x_extend_right = max(1.5, 0.8 * interval)
        x_extend_left = max(1.0, 0.4 * interval)
        line_domain_start = x_start - x_extend_left
        line_domain_end = x_end + x_extend_right
        sqrt_domain_end = x_end + x_extend_right

        x_axis_min = min(line_domain_start - 0.5, -1.5)
        x_axis_max = max(line_domain_end + 0.5, 2.5)

        y_line_start = line_a * line_domain_start + line_b
        y_line_end = line_a * line_domain_end + line_b
        par_min = _to_float(_evaluate(par_expr, params["x_start"]))
        y_axis_min = min(par_min - 1.0, -2.5)
        y_axis_max = max(y_line_start, y_line_end, 2.5) + 0.5

        mid_line_x = x_start + 0.3 * interval
        mid_line_y = _to_float(_evaluate(line_expr, mid_line_x))
        mid_par_x = x_start + 0.7 * interval
        mid_par_y = _to_float(_evaluate(par_expr, mid_par_x))

        line_end_val = _to_float(_evaluate(line_expr, params["x_end"]))
        par_end_val = _to_float(_evaluate(par_expr, params["x_end"]))

        # Build coordinate labels: skip x_end if it equals 0 (coincides with O)
        x_start_label_node = rf"\node[below] at ({fmt(x_start)},0) {{$ {latex_number(params['x_start'])} $}};"
        x_end_label_node = ""
        if abs(x_end) > 1e-6:
            x_end_label_node = rf"\node[below] at ({fmt(x_end)},0) {{$ {latex_number(params['x_end'])} $}};"

        tikz = rf"""
\begin{{tikzpicture}}[scale=.85,samples=200]
\draw[->, thick] ({fmt(x_axis_min)},0) -- ({fmt(x_axis_max)},0) node[below] {{$x$}};
\draw[->, thick] (0,{fmt(y_axis_min)}) -- (0,{fmt(y_axis_max)}) node[left] {{$y$}};
\node[below right] at (0,0) {{$O$}};
\fill[pattern=north west lines, pattern color=gray!70]
  plot[domain={fmt(x_start)}:{fmt(x_end)}] (\x, {{ {line_a}*\x + {line_b} }})
  -- plot[domain={fmt(x_end)}:{fmt(x_start)}] (\x, {{ -sqrt(\x + {par_c}) }});
\draw[very thick, domain={fmt(line_domain_start)}:{fmt(line_domain_end)}] plot (\x, {{ {line_a}*\x + {line_b} }});
\node[above right,rotate=45,scale=0.75,yshift=8pt,xshift=4pt] at ({fmt(mid_line_x)}, {fmt(mid_line_y)}) {{$y={line_label}$}};
\draw[very thick, domain={fmt(x_start)}:{fmt(sqrt_domain_end)}] plot (\x, {{ -sqrt(\x + {par_c}) }});
\node[below right,rotate=-30,scale=0.75,yshift=-4pt] at ({fmt(mid_par_x)}, {fmt(mid_par_y)}) {{$y={par_label}$}};
\draw[dashed] ({fmt(x_end)}, {fmt(line_end_val)}) -- ({fmt(x_end)}, {fmt(par_end_val)});
{x_start_label_node}
{x_end_label_node}
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
            par_ref_func=params["par_ref_latex"],
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
            par_ref_func=params["par_ref_latex"],
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
            par_ref_func=params["par_ref_latex"],
            x_start=params["x_start_latex"],
            x_end=params["x_end_latex"],
            line_sq=params["line_sq_latex"],
            par_ref_sq=params["par_ref_sq_latex"],
            volume_integrand=params["volume_integrand_latex"],
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
            par_ref_func=params["par_ref_latex"],
            x_start=params["x_start_latex"],
            x_end=params["x_end_latex"],
            line_sq=params["line_sq_latex"],
            par_ref_sq=params["par_ref_sq_latex"],
            volume_integrand=params["volume_integrand_latex"],
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

