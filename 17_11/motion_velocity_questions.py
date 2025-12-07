"""
Hệ thống sinh đề toán về chuyển động thẳng với đồ thị vận tốc
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

T = sp.symbols("t", real=True)
NumberLike = Union[int, float, sp.Expr]


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


def to_decimal_comma(value: Any) -> str:
    return str(value).replace(".", ",")


def format_decimal(value: float, digits: int = 1) -> str:
    dot_format = f"{value:.{digits}f}"
    comma_format = dot_format.replace(".", ",")
    return f"{dot_format} | {comma_format}"


def _velocity_ob_expr(params: Dict[str, Any]) -> sp.Expr:
    tB = sp.Integer(int(params["tB"]))
    vB = sp.Integer(int(params["vB"]))
    return sp.Rational(vB, tB) * T


def _velocity_bcd_expr(params: Dict[str, Any]) -> sp.Expr:
    tC = sp.Integer(int(params["tC"]))
    vC = sp.Integer(int(params["vC"]))
    a_coeff = sp.nsimplify(params["bcd_a_coeff"])
    return sp.nsimplify(a_coeff * (T - tC) ** 2 + vC)


def _velocity_def_expr(params: Dict[str, Any]) -> sp.Expr:
    tE = sp.Integer(int(params["tE"]))
    vE = sp.Integer(int(params["vE"]))
    a_coeff = sp.nsimplify(params["def_a_coeff"])
    return sp.nsimplify(a_coeff * (T - tE) ** 2 + vE)


def _integrate_velocity(
    expr: sp.Expr, start: int, end: int, power: int = 1
) -> sp.Expr:
    start_int = sp.Integer(start)
    end_int = sp.Integer(end)
    integrand = expr if power == 1 else sp.expand(expr**power)
    return sp.nsimplify(sp.integrate(integrand, (T, start_int, end_int)))


def distance_components(params: Dict[str, Any]) -> Tuple[sp.Expr, sp.Expr, sp.Expr]:
    segment_ob = _integrate_velocity(_velocity_ob_expr(params), 0, params["tB"])
    segment_bcd = _integrate_velocity(
        _velocity_bcd_expr(params), params["tB"], params["tD"]
    )
    segment_parabola = _integrate_velocity(
        _velocity_def_expr(params), params["tD"], params["tF"]
    )
    return segment_ob, segment_bcd, segment_parabola


def compute_distance_value(params: Dict[str, Any]) -> sp.Expr:
    ob, bcd, parabola = distance_components(params)
    return sp.nsimplify(sp.Add(ob, bcd, parabola))


def volume_components(params: Dict[str, Any]) -> Tuple[sp.Expr, sp.Expr, sp.Expr]:
    segment_ob = _integrate_velocity(
        _velocity_ob_expr(params), 0, params["tB"], power=2
    )
    segment_bcd = _integrate_velocity(
        _velocity_bcd_expr(params), params["tB"], params["tD"], power=2
    )
    segment_parabola = _integrate_velocity(
        _velocity_def_expr(params), params["tD"], params["tF"], power=2
    )
    return segment_ob, segment_bcd, segment_parabola


def compute_volume_inner(params: Dict[str, Any]) -> sp.Expr:
    ob_sq, bcd_sq, parabola_sq = volume_components(params)
    return sp.nsimplify(sp.Add(ob_sq, bcd_sq, parabola_sq))


TEMPLATE_QUESTION_DISTANCE = Template(r"""
Cho một vật chuyển động thẳng với đồ thị vận tốc theo thời gian trong ${T} giây đầu như hình vẽ. 
Tính quãng đường vật đi được trong ${T} giây đầu tiên (làm tròn đến hàng phần mười).

\begin{center}
${diagram}
\end{center}
""")


TEMPLATE_QUESTION_AREA = Template(r"""
Cho hình phẳng (H) giới hạn bởi đồ thị hàm số \(f(x)\), trục Ox và hai đường thẳng x = 0, x = ${T}. 
Biết đồ thị của \(f(x)\) gồm 3 đoạn OB (tuyến tính), BCD (parabol lồi xuống), DEF (parabol lồi xuống) như hình.

Hãy tính diện tích của (H), làm tròn đến hàng phần mười.

\begin{center}
${diagram}
\end{center}
""")


TEMPLATE_QUESTION_VOLUME = Template(r"""
Cho đường cong (C) biểu diễn hàm số \(f(x)\) trên đoạn [0, ${T}]. 
Khi quay miền giới hạn bởi (C) và trục Ox quanh trục Ox, ta được khối tròn xoay.

Hãy tính thể tích khối tròn xoay đó (làm tròn đến hàng phần mười).

\begin{center}
${diagram}
\end{center}
""")


TEMPLATE_QUESTION_DISTANCE_EXACT = Template(r"""
Cho một vật chuyển động thẳng với đồ thị vận tốc theo thời gian trong ${T} giây đầu như hình vẽ. 
Biết quãng đường vật đi được trong ${T} giây đầu có dạng \(\dfrac{a}{b}\) với \(a,b\) nguyên dương tối giản. Tính ${combo_prompt}.

\begin{center}
${diagram}
\end{center}
""")


TEMPLATE_QUESTION_AREA_EXACT = Template(r"""
Cho hình phẳng (H) giới hạn bởi đồ thị hàm số \(f(x)\), trục Ox và hai đường thẳng x = 0, x = ${T}. 
Biết diện tích (H) có dạng \(\dfrac{a}{b}\) với \(a,b\) nguyên dương tối giản. Tính ${combo_prompt}.

\begin{center}
${diagram}
\end{center}
""")


TEMPLATE_QUESTION_VOLUME_EXACT = Template(r"""
Cho đường cong (C) biểu diễn hàm số \(f(x)\) trên đoạn [0, ${T}]. 
Khi quay miền giới hạn bởi (C) và trục Ox quanh trục Ox, ta được khối tròn xoay có thể tích \(\dfrac{a\pi}{b}\) với \(a,b\) nguyên dương. Tính ${combo_prompt}.

\begin{center}
${diagram}
\end{center}
""")


TEMPLATE_SOLUTION_DISTANCE = Template(r"""
Cho một vật chuyển động thẳng với đồ thị vận tốc theo thời gian.

Lập phương trình cho từng đoạn:

Đoạn OB: đi qua O(0,0) và B(${tB},${vB}), do đó:
\[
v_{OB}(t) = \frac{${vB}}{${tB}}\,t.
\]

Đoạn BCD là parabol đối xứng, đỉnh tại C(${tC},${vC}):
\[
v_{BCD}(t) = ${bcd_a_value}(t - ${tC})^2 + ${vC}.
\]

Đoạn DEF là parabol đối xứng, với đỉnh tại E(${tE},${vE}):
\[
v_{DEF}(t) = ${def_a_value}(t - ${tE})^2 + ${vE}.
\]

Ta có: Quãng đường vật đi được:

\[
S = \int_0^{${tB}} v_{OB}(t)\,dt \;+\; 
\int_{${tB}}^{${tD}} v_{BCD}(t)\,dt \;+\; 
\int_{${tD}}^{${tF}} v_{DEF}(t)\,dt.
\]

Tính nguyên hàm:

Đoạn OB:
\[
\int_0^{${tB}} \frac{${vB}}{${tB}} t \, dt = ${segment_ob_integral}.
\]

Đoạn BCD (parabol):
\[
\int_{${tB}}^{${tD}} \left[${bcd_a_value}(t - ${tC})^2 + ${vC}\right] dt 
= ${segment_bcd_integral}.
\]

Đoạn DEF (parabol):
\[
\int_{${tD}}^{${tF}} \left[${def_a_value}(t - ${tE})^2 + ${vE}\right] dt 
= ${segment_parabola_integral}.
\]

Kết luận:

\[
S = ${S_value}.
\]

(làm tròn: \(\approx ${S_round}\)).
""")


TEMPLATE_SOLUTION_AREA = Template(r"""
Cho hình phẳng (H) giới hạn bởi đồ thị hàm số \(f(x)\), trục Ox và hai đường thẳng x = 0, x = ${T}.

Hàm số \(f(x)\) gồm 3 đoạn:

OB: \(f_{OB}(x)=\frac{${vB}}{${tB}} x\).

BCD: \(f_{BCD}(x)=${bcd_a_value}(x-${tC})^2+${vC}\).

DEF: \(f_{DEF}(x)=${def_a_value}(x-${tE})^2+${vE}\).

Ta có: Diện tích hình phẳng (H):

\[
S = \int_0^{${T}} f(x)\,dx.
\]

Vì \(f(x) \ge 0\) trên toàn miền nên không cần trị tuyệt đối.

Tính tích phân từng đoạn:

\[
S = ${segment_ob_integral} + ${segment_bcd_integral} + ${segment_parabola_integral}.
\]

Kết luận:

\[
S = ${S_value} \quad (\text{làm tròn}: ${S_round}).
\]
""")


TEMPLATE_SOLUTION_VOLUME = Template(r"""
Cho đường cong (C) biểu diễn hàm số \(f(x)\) trên đoạn [0, ${T}].

Hàm số \(f(x)\) gồm 3 đoạn:

\[
f(x)=
\begin{cases}
\dfrac{${vB}}{${tB}} x & 0\le x\le ${tB},\\[4pt]
${bcd_a_value}(x - ${tC})^2 + ${vC} & ${tB}\le x\le ${tD},\\[4pt]
${def_a_value}(x - ${tE})^2 + ${vE} & ${tD}\le x\le ${tF}.
\end{cases}
\]

Ta có: Thể tích khối tròn xoay khi quay quanh trục Ox:

\[
V = \pi \int_0^{${T}} (f(x))^2\,dx.
\]

Tính nguyên hàm từng đoạn:

Đoạn OB:
\[
\int_0^{${tB}} \left(\frac{${vB}}{${tB}}x\right)^2 dx = ${segment_ob_sq}.
\]

Đoạn BCD (parabol):
\[
\int_{${tB}}^{${tD}} (f_{BCD}(x))^2 dx = ${segment_bcd_sq}.
\]

Đoạn DEF (parabol):
\[
\int_{${tD}}^{${tF}} \left[${def_a_value}(x-${tE})^2 + ${vE}\right]^2 dx = ${segment_parabola_sq}.
\]

Kết luận:

\[
V = \pi\big(${V_value}\big) \approx ${V_round}.
\]
""")


TEMPLATE_SOLUTION_DISTANCE_EXACT = Template(r"""
Cho một vật chuyển động thẳng với đồ thị vận tốc theo thời gian.

Lập phương trình cho từng đoạn:

Đoạn OB: đi qua O(0,0) và B(${tB},${vB}), do đó:
\[
v_{OB}(t) = \frac{${vB}}{${tB}}\,t.
\]

Đoạn BCD là parabol đối xứng, đỉnh tại C(${tC},${vC}):
\[
v_{BCD}(t) = ${bcd_a_value}(t - ${tC})^2 + ${vC}.
\]

Đoạn DEF là parabol đối xứng, với đỉnh tại E(${tE},${vE}):
\[
v_{DEF}(t) = ${def_a_value}(t - ${tE})^2 + ${vE}.
\]

Quãng đường:
\[
S = \int_0^{${tB}} v_{OB}(t)\,dt + 
\int_{${tB}}^{${tD}} v_{BCD}(t)\,dt + 
\int_{${tD}}^{${tF}} v_{DEF}(t)\,dt
\Leftrightarrow
S = ${S_value}.
\]

Kết luận:
\[
${combo_expr} = ${combo_value}.
\]
""")


TEMPLATE_SOLUTION_AREA_EXACT = Template(r"""
Cho hình phẳng (H) giới hạn bởi đồ thị hàm số \(f(x)\), trục Ox và hai đường thẳng x = 0, x = ${T}.

Hàm số \(f(x)\) gồm 3 đoạn:

OB: \(f_{OB}(x)=\frac{${vB}}{${tB}} x\).

BCD: \(f_{BCD}(x)=${bcd_a_value}(x-${tC})^2+${vC}\).

DEF: \(f_{DEF}(x)=${def_a_value}(x-${tE})^2+${vE}\).

Ta có:
\[
S = \int_0^{${T}} f(x)\,dx
= ${S_value}.
\]

Kết luận:
\[
${combo_expr} = ${combo_value}.
\]
""")


TEMPLATE_SOLUTION_VOLUME_EXACT = Template(r"""
Cho đường cong (C) biểu diễn hàm số \(f(x)\) trên đoạn [0, ${T}].

Hàm số \(f(x)\) gồm 3 đoạn:
\[
f(x)=
\begin{cases}
\dfrac{${vB}}{${tB}} x & 0\le x\le ${tB},\\[4pt]
${bcd_a_value}(x - ${tC})^2 + ${vC} & ${tB}\le x\le ${tD},\\[4pt]
${def_a_value}(x - ${tE})^2 + ${vE} & ${tD}\le x\le ${tF}.
\end{cases}
\]

Thể tích khối tròn xoay:
\[
V = \pi \int_0^{${T}} (f(x))^2\,dx
\Leftrightarrow
V = \pi\cdot ${V_inner} = ${V_exact}.
\]

Kết luận:
\[
${combo_expr} = ${combo_value}.
\]
""")


class BaseMotionQuestion(ABC):
    """
    Lớp cơ sở cho các bài toán chuyển động với đồ thị vận tốc
    """

    def __init__(self, config: Optional["GeneratorConfig"] = None):
        self.parameters: Dict[str, Any] = {}
        self.correct_answer: Optional[str] = None
        self.config = config or GeneratorConfig()

    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên cho bài toán"""
        raise NotImplementedError

    @abstractmethod
    def calculate_answer(self) -> str:
        """Tính đáp án đúng dựa trên parameters"""
        raise NotImplementedError

    @abstractmethod
    def generate_question_text(self) -> str:
        """Sinh đề bài bằng LaTeX"""
        raise NotImplementedError

    @abstractmethod
    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết bằng LaTeX"""
        raise NotImplementedError

    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        """Tạo câu hỏi chỉ có đề bài và lời giải"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        question_text = self.generate_question_text().strip()
        solution = self.generate_solution().strip()
        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += "Lời giải:\n\n" + solution + "\n"
        return question_content, self.correct_answer or ""

    @staticmethod
    def create_latex_document_with_format(
        questions_data: List[Tuple[str, str]],
        title: str = "Câu hỏi Đồ thị Vận tốc",
    ) -> str:
        """Tạo document LaTeX với format tự luận (câu hỏi + lời giải + đáp án)"""
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{polyglossia}}
\\setmainlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage{{tikz}}
\\usepackage{{tkz-tab}}
\\usepackage{{tkz-euclide}}
\\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\\begin{{document}}
\\title{{{title}}}
\\maketitle

"""

        for question_content, correct_answer in questions_data:
            latex_content += question_content + "\n\n"
            latex_content += f"Đáp án: {correct_answer}\n\n"

        latex_content += "\\end{document}"
        return latex_content

    def generate_tikz_diagram(self) -> str:
        params = self.parameters
        if not params:
            return ""

        time_keys = ["tB", "tC", "tD", "tE", "tF"]
        velocity_keys = ["vB", "vC", "vD", "vE", "vF"]

        time_points = [0] + [int(params[key]) for key in time_keys]
        velocity_points = [0] + [int(params[key]) for key in velocity_keys]
        x_axis_limit = time_points[-1] + int(params["tB"])
        y_axis_limit = max(velocity_points) + 2

        target_x = 16.0
        target_y = 10.0
        shrink_factor = 2.0 / 3.0
        base_x_scale = target_x / x_axis_limit if x_axis_limit else 1.0
        base_y_scale = target_y / y_axis_limit if y_axis_limit else 1.0
        x_scale = shrink_factor * base_x_scale
        y_scale = shrink_factor * base_y_scale

        def unique_ordered(values: List[int]) -> List[int]:
            seen: List[int] = []
            for value in values:
                if value not in seen:
                    seen.append(value)
            return seen

        x_ticks_values = unique_ordered(time_points[1:])
        y_ticks_values = unique_ordered([v for v in velocity_points[1:] if v > 0])

        x_ticks_list = ",".join(str(x) for x in x_ticks_values)
        y_ticks_list = ",".join(str(y) for y in y_ticks_values)

        x_ticks_block = (
            rf"""
\foreach \x in {{{x_ticks_list}}}
  \node[below] at (\x,0) {{\x}};
"""
            if x_ticks_list
            else ""
        )
        y_ticks_block = (
            rf"""
\foreach \y in {{{y_ticks_list}}}
  \node[left] at (0,\y) {{\y}};
"""
            if y_ticks_list
            else ""
        )

        vertical_dashed = (
            rf"""
\foreach \x in {{{x_ticks_list}}}
  \draw[dashed] (\x,0) -- (\x,{y_axis_limit});
"""
            if x_ticks_list
            else ""
        )
        horizontal_dashed = (
            rf"""
\foreach \y in {{{y_ticks_list}}}
  \draw[dashed] (0,\y) -- ({x_axis_limit},\y);
"""
            if y_ticks_list
            else ""
        )

        point_specs = [
            ("O", 0, 0, "below right"),
            ("B", time_points[1], velocity_points[1], "above right"),
            ("C", time_points[2], velocity_points[2], "above left"),
            ("D", time_points[3], velocity_points[3], "below right"),
            ("E", time_points[4], velocity_points[4], "above left"),
            ("F", time_points[5], velocity_points[5], "below left"),
        ]

        label_lines = "\n".join(
            rf"\node[{anchor}] at ({x},{y}) {{{label}}};"
            for label, x, y, anchor in point_specs
        )
        point_entries = ",".join(f"{x}/{y}" for _, x, y, _ in point_specs)
        fill_block = rf"""
\foreach \x/\y in {{{point_entries}}}
  \fill (\x,\y) circle (2pt);
"""

        bcd_coeff = sp.sstr(sp.nsimplify(params["bcd_a_coeff"]))
        def_coeff = sp.sstr(sp.nsimplify(params["def_a_coeff"]))
        tB = int(params["tB"])
        tC = int(params["tC"])
        tD = int(params["tD"])
        tE = int(params["tE"])
        tF = int(params["tF"])
        vB = int(params["vB"])
        vC = int(params["vC"])
        vE = int(params["vE"])

        bcd_expr = f"({bcd_coeff})*(\\t-{tC})^2 + {vC}"
        def_expr = f"({def_coeff})*(\\t-{tE})^2 + {vE}"

        ob_segment = rf"\draw[line width=0.9pt] (0,0) -- ({tB},{vB});"
        bcd_segment = rf"""
\draw[line width=0.9pt,domain={tB}:{tD},smooth,variable=\t]
  plot ({{\t}},{{{bcd_expr}}});
"""
        def_segment = rf"""
\draw[line width=0.9pt,domain={tD}:{tF},smooth,variable=\t]
  plot ({{\t}},{{{def_expr}}});
"""

        tikz = f"""
\\begin{{tikzpicture}}[xscale={x_scale:.4f},yscale={y_scale:.4f},>=stealth]
\\draw[->] (0,0) -- (0,{y_axis_limit}) node[left]{{\\(v\\,(m/s)\\)}};
\\draw[->] (0,0) -- ({x_axis_limit},0) node[below]{{\\(t\\,(s)\\)}};
{y_ticks_block}
{x_ticks_block}
{horizontal_dashed}
{vertical_dashed}
{label_lines}
{fill_block}
{ob_segment}
{bcd_segment}
{def_segment}
\\end{{tikzpicture}}
"""
        return "\n".join(line for line in tikz.splitlines() if line.strip())

    def _build_motion_profile(self) -> Dict[str, Any]:
        span = random.choice([2, 3, 4])
        tB = span
        tC = 2 * span
        tD = 3 * span
        tE = 4 * span
        tF = 5 * span

        vB = random.choice([4, 5, 6, 7])
        vC = vB + span
        vD = vB
        vF = vB
        vE = vC + random.choice([1, 2, 3])

        bcd_a_coeff = sp.Rational(vB - vC, (tB - tC) ** 2)
        def_a_coeff = sp.Rational(vD - vE, (tD - tE) ** 2)

        return {
            "tB": tB,
            "tC": tC,
            "tD": tD,
            "tE": tE,
            "tF": tF,
            "T": tF,
            "vB": vB,
            "vC": vC,
            "vD": vD,
            "vE": vE,
            "vF": vF,
            "bcd_a_coeff": bcd_a_coeff,
            "def_a_coeff": def_a_coeff,
        }


class MotionDistanceQuestion(BaseMotionQuestion):
    def generate_parameters(self) -> Dict[str, Any]:
        return self._build_motion_profile()

    def calculate_answer(self) -> str:
        total_distance = compute_distance_value(self.parameters)
        ob_part, bcd_part, parabola_part = distance_components(self.parameters)
        numeric_distance = cast(float, total_distance.evalf())
        rounded_value = round(float(numeric_distance), 1)
        self.parameters["distance_exact"] = total_distance
        self.parameters["distance_round"] = rounded_value
        distance_parts: Dict[str, sp.Expr] = {
            "ob": ob_part,
            "bcd": bcd_part,
            "parabola": parabola_part,
        }
        self.parameters["distance_parts"] = distance_parts
        approx_str = format_decimal(rounded_value)
        return approx_str

    def generate_question_text(self) -> str:
        params = self.parameters
        return TEMPLATE_QUESTION_DISTANCE.substitute(
            T=params["T"],
            tB=params["tB"],
            vB=params["vB"],
            tC=params["tC"],
            vC=params["vC"],
            tD=params["tD"],
            vD=params["vD"],
            tE=params["tE"],
            vE=params["vE"],
            tF=params["tF"],
            vF=params["vF"],
            diagram=self.generate_tikz_diagram(),
        ).strip()

    def generate_solution(self) -> str:
        params = self.parameters
        parts = cast(Dict[str, sp.Expr], params["distance_parts"])
        return TEMPLATE_SOLUTION_DISTANCE.substitute(
            tB=params["tB"],
            vB=params["vB"],
            tC=params["tC"],
            vC=params["vC"],
            tD=params["tD"],
            vD=params["vD"],
            tE=params["tE"],
            vE=params["vE"],
            tF=params["tF"],
            bcd_a_value=latex_number(params["bcd_a_coeff"]),
            def_a_value=latex_number(params["def_a_coeff"]),
            segment_ob_integral=latex_number(parts["ob"]),
            segment_bcd_integral=latex_number(parts["bcd"]),
            segment_parabola_integral=latex_number(parts["parabola"]),
            S_value=latex_number(params["distance_exact"]),
            S_round=format_decimal(params["distance_round"]),
        ).strip()


class MotionDistanceExactQuestion(BaseMotionQuestion):
    def generate_parameters(self) -> Dict[str, Any]:
        return self._build_motion_profile()

    def calculate_answer(self) -> str:
        total_distance = sp.nsimplify(compute_distance_value(self.parameters))
        ob_part, bcd_part, parabola_part = distance_components(self.parameters)
        num, den = sp.fraction(total_distance)
        num_int = int(sp.Integer(sp.nsimplify(num)))
        den_int = int(sp.Integer(sp.nsimplify(den)))
        if den_int < 0:
            num_int *= -1
            den_int *= -1
        combo_expr, combo_fn = random.choice(COMBINATION_FORMS)
        combo_value = combo_fn(num_int, den_int)
        self.parameters.update(
            {
                "distance_exact": total_distance,
                "distance_parts": {
                    "ob": ob_part,
                    "bcd": bcd_part,
                    "parabola": parabola_part,
                },
                "distance_fraction": (num_int, den_int),
                "combo_expr": combo_expr,
                "combo_value": latex_number(combo_value),
                "combo_prompt": combo_expr,
                "distance_exact_latex": latex_number(total_distance),
            }
        )
        return latex_number(combo_value)

    def generate_question_text(self) -> str:
        params = self.parameters
        return TEMPLATE_QUESTION_DISTANCE_EXACT.substitute(
            T=params["T"],
            combo_prompt=params["combo_prompt"],
            diagram=self.generate_tikz_diagram(),
        ).strip()

    def generate_solution(self) -> str:
        params = self.parameters
        parts = cast(Dict[str, sp.Expr], params["distance_parts"])
        return TEMPLATE_SOLUTION_DISTANCE_EXACT.substitute(
            tB=params["tB"],
            vB=params["vB"],
            tC=params["tC"],
            vC=params["vC"],
            tD=params["tD"],
            tE=params["tE"],
            tF=params["tF"],
            vE=params["vE"],
            bcd_a_value=latex_number(params["bcd_a_coeff"]),
            def_a_value=latex_number(params["def_a_coeff"]),
            S_value=params["distance_exact_latex"],
            combo_expr=params["combo_expr"],
            combo_value=params["combo_value"],
        ).strip()


class MotionAreaQuestion(BaseMotionQuestion):
    def generate_parameters(self) -> Dict[str, Any]:
        return self._build_motion_profile()

    def calculate_answer(self) -> str:
        total_area = compute_distance_value(self.parameters)
        ob_part, bcd_part, parabola_part = distance_components(self.parameters)
        numeric_area = cast(float, total_area.evalf())
        rounded_value = round(float(numeric_area), 1)
        self.parameters["area_exact"] = total_area
        self.parameters["area_round"] = rounded_value
        area_parts: Dict[str, sp.Expr] = {
            "ob": ob_part,
            "bcd": bcd_part,
            "parabola": parabola_part,
        }
        self.parameters["area_parts"] = area_parts
        approx_str = format_decimal(rounded_value)
        return approx_str

    def generate_question_text(self) -> str:
        params = self.parameters
        return TEMPLATE_QUESTION_AREA.substitute(
            T=params["T"],
            diagram=self.generate_tikz_diagram(),
        ).strip()

    def generate_solution(self) -> str:
        params = self.parameters
        parts = cast(Dict[str, sp.Expr], params["area_parts"])
        return TEMPLATE_SOLUTION_AREA.substitute(
            vB=params["vB"],
            tB=params["tB"],
            tC=params["tC"],
            vC=params["vC"],
            tE=params["tE"],
            tF=params["tF"],
            tD=params["tD"],
            vE=params["vE"],
            T=params["T"],
            bcd_a_value=latex_number(params["bcd_a_coeff"]),
            def_a_value=latex_number(params["def_a_coeff"]),
            segment_ob_integral=latex_number(parts["ob"]),
            segment_bcd_integral=latex_number(parts["bcd"]),
            segment_parabola_integral=latex_number(parts["parabola"]),
            S_value=latex_number(params["area_exact"]),
            S_round=format_decimal(params["area_round"]),
        ).strip()


class MotionAreaExactQuestion(BaseMotionQuestion):
    def generate_parameters(self) -> Dict[str, Any]:
        return self._build_motion_profile()

    def calculate_answer(self) -> str:
        total_area = sp.nsimplify(compute_distance_value(self.parameters))
        ob_part, bcd_part, parabola_part = distance_components(self.parameters)
        num, den = sp.fraction(total_area)
        num_int = int(sp.Integer(sp.nsimplify(num)))
        den_int = int(sp.Integer(sp.nsimplify(den)))
        if den_int < 0:
            num_int *= -1
            den_int *= -1
        combo_expr, combo_fn = random.choice(COMBINATION_FORMS)
        combo_value = combo_fn(num_int, den_int)
        self.parameters.update(
            {
                "area_exact": total_area,
                "area_parts": {
                    "ob": ob_part,
                    "bcd": bcd_part,
                    "parabola": parabola_part,
                },
                "area_fraction": (num_int, den_int),
                "combo_expr": combo_expr,
                "combo_value": latex_number(combo_value),
                "combo_prompt": combo_expr,
                "area_exact_latex": latex_number(total_area),
            }
        )
        return latex_number(combo_value)

    def generate_question_text(self) -> str:
        params = self.parameters
        return TEMPLATE_QUESTION_AREA_EXACT.substitute(
            T=params["T"],
            combo_prompt=params["combo_prompt"],
            diagram=self.generate_tikz_diagram(),
        ).strip()

    def generate_solution(self) -> str:
        params = self.parameters
        return TEMPLATE_SOLUTION_AREA_EXACT.substitute(
            vB=params["vB"],
            tB=params["tB"],
            tC=params["tC"],
            vC=params["vC"],
            tE=params["tE"],
            tF=params["tF"],
            tD=params["tD"],
            vE=params["vE"],
            T=params["T"],
            bcd_a_value=latex_number(params["bcd_a_coeff"]),
            def_a_value=latex_number(params["def_a_coeff"]),
            S_value=params["area_exact_latex"],
            combo_expr=params["combo_expr"],
            combo_value=params["combo_value"],
        ).strip()


class MotionVolumeQuestion(BaseMotionQuestion):
    def generate_parameters(self) -> Dict[str, Any]:
        return self._build_motion_profile()

    def calculate_answer(self) -> str:
        volume_inner = compute_volume_inner(self.parameters)
        volume_exact = sp.nsimplify(sp.pi * volume_inner)
        ob_sq, bcd_sq, parabola_sq = volume_components(self.parameters)
        numeric_volume = cast(float, volume_exact.evalf())
        rounded_value = round(float(numeric_volume), 1)
        self.parameters["volume_inner"] = volume_inner
        self.parameters["volume_exact"] = volume_exact
        self.parameters["volume_round"] = rounded_value
        volume_parts: Dict[str, sp.Expr] = {
            "ob": ob_sq,
            "bcd": bcd_sq,
            "parabola": parabola_sq,
        }
        self.parameters["volume_parts"] = volume_parts
        approx_str = format_decimal(rounded_value)
        return approx_str

    def generate_question_text(self) -> str:
        params = self.parameters
        return TEMPLATE_QUESTION_VOLUME.substitute(
            T=params["T"],
            diagram=self.generate_tikz_diagram(),
        ).strip()

    def generate_solution(self) -> str:
        params = self.parameters
        parts = cast(Dict[str, sp.Expr], params["volume_parts"])
        return TEMPLATE_SOLUTION_VOLUME.substitute(
            T=params["T"],
            vB=params["vB"],
            tB=params["tB"],
            tC=params["tC"],
            tD=params["tD"],
            tE=params["tE"],
            tF=params["tF"],
            vC=params["vC"],
            vE=params["vE"],
            bcd_a_value=latex_number(params["bcd_a_coeff"]),
            def_a_value=latex_number(params["def_a_coeff"]),
            segment_ob_sq=latex_number(parts["ob"]),
            segment_bcd_sq=latex_number(parts["bcd"]),
            segment_parabola_sq=latex_number(parts["parabola"]),
            V_value=latex_number(params["volume_inner"]),
            V_round=format_decimal(params["volume_round"]),
        ).strip()


class MotionVolumeExactQuestion(BaseMotionQuestion):
    def generate_parameters(self) -> Dict[str, Any]:
        return self._build_motion_profile()

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
                "volume_exact_latex": latex_number(volume_exact),
                "combo_expr": combo_expr,
                "combo_value": latex_number(combo_value),
                "combo_prompt": combo_expr,
            }
        )
        return latex_number(combo_value)

    def generate_question_text(self) -> str:
        params = self.parameters
        return TEMPLATE_QUESTION_VOLUME_EXACT.substitute(
            T=params["T"],
            combo_prompt=params["combo_prompt"],
            diagram=self.generate_tikz_diagram(),
        ).strip()

    def generate_solution(self) -> str:
        params = self.parameters
        return TEMPLATE_SOLUTION_VOLUME_EXACT.substitute(
            T=params["T"],
            vB=params["vB"],
            tB=params["tB"],
            tC=params["tC"],
            tD=params["tD"],
            tE=params["tE"],
            tF=params["tF"],
            vC=params["vC"],
            vE=params["vE"],
            bcd_a_value=latex_number(params["bcd_a_coeff"]),
            def_a_value=latex_number(params["def_a_coeff"]),
            V_inner=params["volume_inner_latex"],
            V_exact=params["volume_exact_latex"],
            combo_expr=params["combo_expr"],
            combo_value=params["combo_value"],
        ).strip()


def get_available_question_types():
    return [
        MotionDistanceQuestion,
        MotionDistanceExactQuestion,
        MotionAreaQuestion,
        MotionAreaExactQuestion,
        MotionVolumeQuestion,
        MotionVolumeExactQuestion,
    ]


def main():
    """
    Hàm main để chạy generator (format tự luận)
    Usage: python motion_velocity_questions.py <num_questions> [question_type]
           question_type:
             1 = Quãng đường (làm tròn)
             2 = Quãng đường (exact)
             3 = Diện tích (làm tròn)
             4 = Diện tích (exact)
             5 = Thể tích (làm tròn)
             6 = Thể tích (exact)
           (mặc định: random)
    """
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        
        # Đọc question_type từ tham số thứ 2
        question_type_param: Optional[int] = None
        if len(sys.argv) > 2:
            try:
                question_type_param = int(sys.argv[2])
                if question_type_param not in [1, 2, 3, 4, 5, 6]:
                    print(
                        "⚠️  question_type phải thuộc [1, 2, 3, 4, 5, 6] "
                        "(xem hướng dẫn trong docstring)"
                    )
                    question_type_param = None
            except ValueError:
                pass
        
        # Đọc seed từ tham số thứ 3 hoặc env
        seed: Optional[int] = None
        if len(sys.argv) > 3:
            try:
                seed = int(sys.argv[3])
            except Exception:
                seed = None
        if seed is None:
            env_seed = os.environ.get("OPT_SEED")
            if env_seed is not None:
                try:
                    seed = int(env_seed)
                except Exception:
                    seed = None
        if seed is not None:
            random.seed(seed)

        question_types = get_available_question_types()
        
        # Map question_type_param sang class tương ứng
        type_map = {
            1: MotionDistanceQuestion,
            2: MotionDistanceExactQuestion,
            3: MotionAreaQuestion,
            4: MotionAreaExactQuestion,
            5: MotionVolumeQuestion,
            6: MotionVolumeExactQuestion,
        }
        type_names = {
            1: "Quãng đường (làm tròn)",
            2: "Quãng đường (exact)",
            3: "Diện tích (làm tròn)",
            4: "Diện tích (exact)",
            5: "Thể tích (làm tròn)",
            6: "Thể tích (exact)",
        }
        
        selected_type = type_map.get(question_type_param) if question_type_param else None
        questions_data: List[Tuple[str, str]] = []

        for i in range(1, num_questions + 1):
            try:
                if selected_type:
                    question_type = selected_type
                else:
                    question_type = random.choice(question_types)
                question_instance = question_type(GeneratorConfig(seed=None))
                question_content, correct_answer = question_instance.generate_question_only(i)
                questions_data.append((question_content, correct_answer))
                logging.info(f"Đã tạo thành công câu hỏi {i}")
            except Exception as exc:
                logging.error(f"Lỗi tạo câu hỏi {i}: {exc}", exc_info=True)
                continue

        if not questions_data:
            print("Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)

        # Chọn title phù hợp
        if question_type_param and question_type_param in type_names:
            title = f"Câu hỏi {type_names[question_type_param]}"
        else:
            title = "Câu hỏi Đồ thị Vận tốc"
        
        latex_content = BaseMotionQuestion.create_latex_document_with_format(
            questions_data, title
        )

        filename = "motion_questions.tex"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)

        print(f"✅ Đã tạo thành công {filename} với {len(questions_data)} câu hỏi")
        if question_type_param:
            print(f"📝 Dạng: {type_names[question_type_param]}")
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
