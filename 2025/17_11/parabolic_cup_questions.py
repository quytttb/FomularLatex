"""
Trình sinh đề toán thể tích cái ly parabol (2 dạng câu hỏi).
"""

import logging
import os
import random
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from string import Template
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import sympy as sp

NumberLike = Union[int, float, sp.Expr]


HEIGHT_CHOICES = [4, 5, 6, 7, 8, 9, 10]
DIAMETER_CHOICES = [4, 6, 8, 10, 12]
COMBINATION_FORMS: List[Tuple[str, Callable[[int, int], int]]] = [
    ("2a+3b", lambda a, b: 2 * a + 3 * b),
    ("a+3b", lambda a, b: a + 3 * b),
    ("a+b", lambda a, b: a + b),
    ("3a+2b", lambda a, b: 3 * a + 2 * b),
]


@dataclass
class GeneratorConfig:
    exact_mode: bool = True


def latex_number(value: NumberLike) -> str:
    """
    Chuyển một giá trị sang biểu diễn LaTeX (tối giản nếu có thể).
    """
    try:
        return sp.latex(sp.nsimplify(value))
    except Exception:
        return str(value)


def format_decimal(value: float, digits: int = 1) -> str:
    """
    Trả về chuỗi định dạng số thập phân dạng '12.3 | 12,3'.
    """
    dot_format = f"{value:.{digits}f}"
    return f"{dot_format} | {dot_format.replace('.', ',')}"


def compute_volume_fraction(height: int, diameter: int) -> sp.Rational:
    """
    Trả về V/π = h*t^2 / 8 dưới dạng phân số tối giản.
    """
    return sp.nsimplify(sp.Rational(height * diameter * diameter, 8))


def _generate_cup_parameters() -> Dict[str, Any]:
    """
    Sinh ra tập tham số ngẫu nhiên cho chiếc ly.
    """
    height = random.choice(HEIGHT_CHOICES)
    diameter = random.choice(DIAMETER_CHOICES)
    radius = sp.Rational(diameter, 2)
    a_coeff = sp.nsimplify(sp.Rational(height, 1) / (radius**2))
    volume_fraction = compute_volume_fraction(height, diameter)
    volume_exact = sp.nsimplify(sp.pi * volume_fraction)

    return {
        "height": height,
        "diameter": diameter,
        "radius": radius,
        "a_coeff": a_coeff,
        "volume_fraction": volume_fraction,
        "volume_exact": volume_exact,
    }


TEMPLATE_QUESTION_EXACT = Template(
    r"""
Có một vật hình tròn xoay dạng giống cái ly như hình vẽ dưới đây.
Người ta đo được chiều cao là ${height} cm và đường kính miệng ly là ${diameter} cm.
Biết thiết diện của chiếc ly được cắt bởi mặt phẳng đối xứng là một parabol.
Thể tích có dạng \(V = \dfrac{a\pi}{b}\) với \(a,b\) nguyên dương. Tính \(${combo_prompt}\).

\begin{center}
${diagram}
\end{center}
"""
)


TEMPLATE_QUESTION_ROUNDED = Template(
    r"""
Có một vật hình tròn xoay dạng giống cái ly như hình vẽ dưới đây.
Người ta đo được chiều cao là ${height} cm và đường kính miệng ly là ${diameter} cm.
Biết thiết diện của chiếc ly được cắt bởi mặt phẳng đối xứng là một parabol.
Hãy tính thể tích khối tròn xoay đó (làm tròn đến hàng phần mười).

\begin{center}
${diagram}
\end{center}
"""
)


TEMPLATE_SOLUTION_EXACT = Template(
    r"""
Cho hàm số biểu diễn thiết diện: \(y = a x^2\).

Ta có:
\[
a = \frac{${height}}{\left(\dfrac{${diameter}}{2}\right)^2}
\Leftrightarrow a = ${a_coeff}.
\]

Thể tích:
\[
V = \pi\int_0^{${height}} \frac{y}{a}\,dy
\Leftrightarrow
V = \pi \cdot ${volume_fraction}
= \frac{${numerator}\pi}{${denominator}}.
\]

Kết luận:
\[
${combo_expr} = ${combo_value}.
\]
"""
)


TEMPLATE_SOLUTION_ROUNDED = Template(
    r"""
Cho hàm số biểu diễn thiết diện: \(y = a x^2\).

Ta có:
\[
a = \frac{${height}}{\left(\dfrac{${diameter}}{2}\right)^2}
\Leftrightarrow a = ${a_coeff}.
\]

Thể tích:
\[
V = \pi\int_0^{${height}} \frac{y}{a}\,dy
\Leftrightarrow
V = \pi \cdot ${volume_fraction}
= ${volume_exact}.
\]

Kết luận: \(V \approx ${volume_round}\,\text{cm}^3\).
"""
)


class BaseParabolicCupQuestion(ABC):
    """
    Lớp cơ sở cho hai dạng câu hỏi về ly parabol.
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
        self.correct_answer = self.calculate_answer()
        question_text = self.generate_question_text().strip()
        solution = self.generate_solution().strip()
        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += "Lời giải:\n\n" + solution + "\n"
        return question_content, self.correct_answer or ""

    @staticmethod
    def create_latex_document_with_format(
        questions_data: List[Tuple[str, str]],
        title: str = "Câu hỏi Ly Parabol",
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

    def generate_tikz_diagram(self) -> str:
        if not self.parameters:
            return ""

        diameter = float(self.parameters["diameter"])
        radius = diameter / 2.0
        minor_radius = max(radius * 0.25, 0.35)
        height = float(self.parameters["height"])
        a_coeff = float(self.parameters["a_coeff"])
        dimension_level = 0.8
        vertical_label_x = radius + 0.3

        tikz = rf"""
\begin{{tikzpicture}}[
    scale=.8,
    font=\sffamily,
    dotstyle/.style={{circle, draw, fill=white, inner sep=1.5pt, thick}}
]
\fill[pattern=north west lines, pattern color=black!70]
    (0,0) ellipse ({radius:.3f}cm and {minor_radius:.3f}cm);
\draw[very thick, domain={-radius:.3f}:{radius:.3f}, samples=120]
    plot (\x, {{ {a_coeff:.4f}*\x*\x - {height:.4f} }});
\draw[dashed] (-{radius:.3f},0) -- (-{radius:.3f},-{height:.3f});
\draw[dashed] ({radius:.3f},0) -- ({radius:.3f},-{height:.3f});
\draw[dashed] (0,0) -- (0,-{height:.3f});
\draw[dashed] (-{radius:.3f},-{height:.3f}) -- ({radius:.3f},-{height:.3f});
\draw[<->] (-{radius:.3f},{dimension_level}) -- ({radius:.3f},{dimension_level})
    node[midway, above] {{$ {self.parameters['diameter']}\,\text{{cm}} $}};
\draw[<->] ({vertical_label_x:.3f},0) -- ({vertical_label_x:.3f},-{height:.3f})
    node[midway, right] {{$ {self.parameters['height']}\,\text{{cm}} $}};
\node[dotstyle, label=above left:$A$] at (-{radius:.3f},0) {{}};
\node[dotstyle, label=above right:$B$] at ({radius:.3f},0) {{}};
\node[dotstyle, label=above:$O$] at (0,0) {{}};
\node[dotstyle, label=below:$I$] at (0,-{height:.3f}) {{}};
\draw[thick] (0,0) ellipse ({radius:.3f}cm and {minor_radius:.3f}cm);
\end{{tikzpicture}}
"""
        return "\n".join(line for line in tikz.splitlines() if line.strip())


class ParabolicCupExactQuestion(BaseParabolicCupQuestion):
    def generate_parameters(self) -> Dict[str, Any]:
        return _generate_cup_parameters()

    def calculate_answer(self) -> str:
        volume_fraction = sp.nsimplify(self.parameters["volume_fraction"])
        numerator, denominator = map(int, sp.fraction(volume_fraction))
        combo_expr, combo_fn = random.choice(COMBINATION_FORMS)
        combo_value = combo_fn(numerator, denominator)

        self.parameters.update(
            {
                "numerator": numerator,
                "denominator": denominator,
                "combo_expr": combo_expr,
                "combo_value": latex_number(combo_value),
                "combo_prompt": combo_expr,
            }
        )
        return latex_number(combo_value)

    def generate_question_text(self) -> str:
        params = self.parameters
        return TEMPLATE_QUESTION_EXACT.substitute(
            height=params["height"],
            diameter=params["diameter"],
            combo_prompt=params["combo_prompt"],
            diagram=self.generate_tikz_diagram(),
        ).strip()

    def generate_solution(self) -> str:
        params = self.parameters
        return TEMPLATE_SOLUTION_EXACT.substitute(
            height=params["height"],
            diameter=params["diameter"],
            a_coeff=latex_number(params["a_coeff"]),
            volume_fraction=latex_number(params["volume_fraction"]),
            numerator=params["numerator"],
            denominator=params["denominator"],
            combo_expr=params["combo_expr"],
            combo_value=params["combo_value"],
        ).strip()


class ParabolicCupRoundedQuestion(BaseParabolicCupQuestion):
    def generate_parameters(self) -> Dict[str, Any]:
        return _generate_cup_parameters()

    def calculate_answer(self) -> str:
        volume_exact = sp.nsimplify(self.parameters["volume_exact"])
        numeric_volume = float(volume_exact.evalf())
        rounded_value = round(numeric_volume, 1)
        round_display = format_decimal(rounded_value)
        self.parameters.update(
            {
                "volume_round": round_display,
            }
        )
        return round_display

    def generate_question_text(self) -> str:
        params = self.parameters
        return TEMPLATE_QUESTION_ROUNDED.substitute(
            height=params["height"],
            diameter=params["diameter"],
            diagram=self.generate_tikz_diagram(),
        ).strip()

    def generate_solution(self) -> str:
        params = self.parameters
        return TEMPLATE_SOLUTION_ROUNDED.substitute(
            height=params["height"],
            diameter=params["diameter"],
            a_coeff=latex_number(params["a_coeff"]),
            volume_fraction=latex_number(params["volume_fraction"]),
            volume_exact=latex_number(params["volume_exact"]),
            volume_round=params["volume_round"],
        ).strip()


def get_available_question_types() -> List[type]:
    return [ParabolicCupExactQuestion, ParabolicCupRoundedQuestion]


def main():
    """
    Tạo file LaTeX chứa các câu hỏi ly parabol.
    Usage: python parabolic_cup_questions.py <num_questions> [question_type] [seed]
           question_type: 1 = dạng biểu thức, 2 = dạng làm tròn
    """

    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3

        question_type_param: Optional[int] = None
        if len(sys.argv) > 2:
            try:
                question_type_param = int(sys.argv[2])
                if question_type_param not in (1, 2):
                    print("⚠️  question_type phải là 1 (biểu thức) hoặc 2 (làm tròn)")
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
            1: ParabolicCupExactQuestion,
            2: ParabolicCupRoundedQuestion,
        }
        type_names = {
            1: "Dạng biểu thức",
            2: "Dạng làm tròn",
        }

        selected_type = type_map.get(question_type_param) if question_type_param else None
        questions_data: List[Tuple[str, str]] = []

        for i in range(1, num_questions + 1):
            try:
                question_class = selected_type or random.choice(question_types)
                question_instance = question_class(GeneratorConfig())
                question_content, correct_answer = question_instance.generate_question_only(i)
                questions_data.append((question_content, correct_answer))
                logging.info("Đã tạo câu hỏi %s", i)
            except Exception as exc:
                logging.error("Lỗi tạo câu hỏi %s: %s", i, exc, exc_info=True)
                continue

        if not questions_data:
            print("❌ Lỗi: không tạo được câu hỏi nào")
            sys.exit(1)

        if question_type_param and question_type_param in type_names:
            title = f"Câu hỏi {type_names[question_type_param]}"
        else:
            title = "Câu hỏi Ly Parabol"

        latex_content = BaseParabolicCupQuestion.create_latex_document_with_format(
            questions_data, title
        )

        filename = "parabolic_cup_questions.tex"
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

