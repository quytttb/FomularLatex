"""
Trình sinh đề toán thực tế: Trồng hoa trên dải đất hình Elip.
"""

import logging
import os
import random
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from string import Template
from typing import Any, Dict, List, Optional, Tuple, Union

import sympy as sp

NumberLike = Union[int, float, sp.Expr]

# Cấu hình các lựa chọn tham số
MAJOR_AXIS_CHOICES = [x for x in range(10, 120, 2)]  # Độ dài trục lớn 2a (m)
MINOR_AXIS_CHOICES = [x for x in range(6, 80, 2)]    # Độ dài trục bé 2b (m)
PRICE_CHOICES = [x * 10000 for x in range(5, 60, 1)] # Đơn giá (đồng/m2)

@dataclass
class GeneratorConfig:
    exact_mode: bool = False

def latex_number(value: NumberLike) -> str:
    """Chuyển giá trị sang LaTeX."""
    try:
        return sp.latex(sp.nsimplify(value))
    except Exception:
        return str(value)

def format_money(value: int) -> str:
    """Định dạng tiền tệ: 1000000 -> 1000000 (không dấu chấm theo yêu cầu)"""
    return str(int(value))

def _generate_garden_parameters() -> Dict[str, Any]:
    """Sinh tham số cho bài toán vườn Elip."""
    # Chọn trục lớn và trục bé sao cho trục lớn > trục bé
    while True:
        major_axis = random.choice(MAJOR_AXIS_CHOICES)
        minor_axis = random.choice(MINOR_AXIS_CHOICES)
        if major_axis > minor_axis:
            break
            
    a = major_axis // 2
    b = minor_axis // 2
    
    # Chọn chiều rộng dải đất w < 2a (trục lớn)
    # Dải đất nhận trục bé làm trục đối xứng, tức là cắt trục lớn.
    # Giới hạn x từ -w/2 đến w/2. Điều kiện w/2 < a => w < 2a.
    # Để số đẹp, chọn w chẵn.
    possible_widths = [w for w in range(2, major_axis, 2)]
    width = random.choice(possible_widths)
    
    price = random.choice(PRICE_CHOICES)
    
    return {
        "major_axis": major_axis,
        "minor_axis": minor_axis,
        "a": a,
        "b": b,
        "width": width,
        "price": price
    }

TEMPLATE_QUESTION = Template(
    r"""
Ông An có một mảnh vườn hình Elip có độ dài trục lớn bằng ${major_axis} m và độ dài trục bé bằng ${minor_axis} m. Ông muốn trồng hoa trên một dải đất rộng ${width} m và nhận trục bé của elip làm trục đối xứng (như hình vẽ). Biết kinh phí để trồng hoa là ${price_display} đồng/\(\text{m}^2\). Hỏi ông An cần bao nhiêu tiền để trồng hoa trên dải đất đó? (làm tròn đến hàng đơn vị).

\begin{center}
${diagram}
\end{center}
"""
)

TEMPLATE_SOLUTION = Template(
    r"""
Chọn hệ trục tọa độ \(Oxy\) sao cho gốc \(O\) trùng với tâm đối xứng của mảnh vườn, trục hoành trùng với trục lớn và trục tung trùng với trục bé.
Độ dài trục lớn \(2a = ${major_axis} \Rightarrow a = ${a}\).
Độ dài trục bé \(2b = ${minor_axis} \Rightarrow b = ${b}\).

Phương trình đường Elip là:
\( \frac{x^2}{${a}^2} + \frac{y^2}{${b}^2} = 1 \Leftrightarrow y = \pm \frac{${b}}{${a}} \sqrt{${a_sq} - x^2} \)

Dải đất cần trồng hoa rộng ${width} m và nhận trục bé làm trục đối xứng, nên nó được giới hạn bởi hai đường thẳng \(x = -${half_width}\) và \(x = ${half_width}\).

Diện tích dải đất là:
\( S = \int_{-${half_width}}^{${half_width}} \left( \frac{${b}}{${a}} \sqrt{${a_sq} - x^2} - \left( -\frac{${b}}{${a}} \sqrt{${a_sq} - x^2} \right) \right) \text{d}x = \int_{-${half_width}}^{${half_width}} \frac{${two_b}}{${a}} \sqrt{${a_sq} - x^2} \text{d}x \)

Sử dụng máy tính cầm tay, ta tính được:
\( S \approx ${area_approx} \, (\text{m}^2) \)

Số tiền cần dùng để trồng hoa là:
\( T = S \times ${price} \approx ${area_approx} \times ${price} \approx ${total_cost} \, (\text{đồng}) \)

Kết luận: Cần khoảng ${total_cost} đồng.
"""
)

class EllipticalGardenQuestion:
    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.correct_answer: Optional[str] = None
        self.config = config or GeneratorConfig()

    def generate_parameters(self) -> Dict[str, Any]:
        return _generate_garden_parameters()

    def calculate_answer(self) -> str:
        a = self.parameters["a"]
        b = self.parameters["b"]
        w = self.parameters["width"]
        price = self.parameters["price"]
        
        x = sp.Symbol('x')
        # Diện tích: tích phân từ -w/2 đến w/2 của (2*b/a * sqrt(a^2 - x^2))
        # y_upper = (b/a) * sqrt(a^2 - x^2)
        # height = 2 * y_upper
        integrand = (2 * b / a) * sp.sqrt(a**2 - x**2)
        area_expr = sp.Integral(integrand, (x, -w/2, w/2))
        
        # Tính giá trị số
        area_val = area_expr.evalf()
        total_cost = area_val * price
        
        # Làm tròn đến hàng đơn vị
        cost_rounded = int(round(total_cost))
        
        self.parameters.update({
            "a_sq": a**2,
            "b_sq": b**2,
            "two_b": 2*b,
            "half_width": w // 2 if w % 2 == 0 else w/2,
            "price_display": format_money(price),
            "area_approx": f"{area_val:.4f}".replace(".", ","),
            "total_cost": str(cost_rounded), # Không format dấu chấm
            "raw_cost": cost_rounded
        })
        
        return f"{cost_rounded}"

    def generate_tikz_diagram(self) -> str:
        a = self.parameters["a"]
        b = self.parameters["b"]
        w = self.parameters["width"]
        
        # Scale down for TikZ to fit nicely
        # Base scale on major axis 'a'
        scale = 3.0 / a 
        tikz_a = a * scale
        tikz_b = b * scale
        tikz_half_w = (w / 2) * scale
        
        tikz = rf"""
\begin{{tikzpicture}}[scale=1, font=\footnotesize]
    \def\hw{{{tikz_half_w:.3f}}}
    
    % Tô màu vùng dải đất (cắt bởi elip)
    \begin{{scope}}
        \clip (0,0) ellipse ({tikz_a:.3f} and {tikz_b:.3f});
        \fill[pattern=north east lines, pattern color=gray!60] (-\hw, -{tikz_b:.3f}) rectangle (\hw, {tikz_b:.3f});
    \end{{scope}}

    % Vẽ Elip
    \draw[thick] (0,0) ellipse ({tikz_a:.3f} and {tikz_b:.3f});
    
    % Vẽ 2 đường giới hạn dải đất
    \begin{{scope}}
        \clip (0,0) ellipse ({tikz_a:.3f} and {tikz_b:.3f});
        \draw[thick] (-\hw, -2*{tikz_b:.3f}) -- (-\hw, 2*{tikz_b:.3f});
        \draw[thick] (\hw, -2*{tikz_b:.3f}) -- (\hw, 2*{tikz_b:.3f});
    \end{{scope}}
    
    % Kích thước chiều rộng
    \draw[<->] (-\hw, 0) -- (\hw, 0) node[midway, above, fill=white, inner sep=1pt] {{$ {w} $ m}};
    
\end{{tikzpicture}}
"""
        return "\n".join(line for line in tikz.splitlines() if line.strip())

    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        logging.info("Đang tạo câu hỏi %s", question_number)
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        
        question_text = TEMPLATE_QUESTION.substitute(
            major_axis=self.parameters["major_axis"],
            minor_axis=self.parameters["minor_axis"],
            width=self.parameters["width"],
            price_display=self.parameters["price_display"],
            diagram=self.generate_tikz_diagram()
        ).strip()
        
        solution = TEMPLATE_SOLUTION.substitute(
            major_axis=self.parameters["major_axis"],
            minor_axis=self.parameters["minor_axis"],
            a=self.parameters["a"],
            b=self.parameters["b"],
            a_sq=self.parameters["a_sq"],
            two_b=self.parameters["two_b"],
            width=self.parameters["width"],
            half_width=self.parameters["half_width"],
            area_approx=self.parameters["area_approx"],
            price=self.parameters["price"],
            total_cost=self.parameters["total_cost"]
        ).strip()
        
        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += "Lời giải:\n\n" + solution + "\n"
        return question_content, self.correct_answer or ""

    @staticmethod
    def create_latex_document(questions_data: List[Tuple[str, str]]) -> str:
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
\title{Bài toán Trồng Hoa Vườn Elip}
\maketitle
"""
        for question_content, correct_answer in questions_data:
            latex_content += question_content + "\n\n"
            latex_content += f"Đáp án: {correct_answer}\n\n"
        latex_content += "\\end{document}"
        return latex_content

def main():
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else None
        
        if seed is not None:
            random.seed(seed)
            
        questions_data = []
        for i in range(1, num_questions + 1):
            q = EllipticalGardenQuestion()
            questions_data.append(q.generate_question_only(i))
            
        latex_content = EllipticalGardenQuestion.create_latex_document(questions_data)
        
        filename = "elliptical_garden_questions.tex"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)
            
        print(f"✅ Đã tạo {filename} với {len(questions_data)} câu hỏi")
        print(f"📄 Biên dịch bằng: xelatex {filename}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
