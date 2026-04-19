"""
Trình sinh đề toán thực tế: Trồng cây trên dải đất hình tròn.
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
RADIUS_CHOICES = list(range(5, 60))  # Bán kính (m)
PRICE_CHOICES = [x * 10000 for x in range(20, 100, 1)] # Đơn giá (đồng/m2)

@dataclass
class GeneratorConfig:
    exact_mode: bool = False # Mặc định là False vì bài này yêu cầu làm tròn

def latex_number(value: NumberLike) -> str:
    """Chuyển giá trị sang LaTeX."""
    try:
        return sp.latex(sp.nsimplify(value))
    except Exception:
        return str(value)

def format_money(value: int) -> str:
    """Định dạng tiền tệ: 1000000 -> 1000000"""
    return str(int(value))

def _generate_garden_parameters() -> Dict[str, Any]:
    """Sinh tham số cho bài toán vườn tròn."""
    radius = random.choice(RADIUS_CHOICES)
    
    # Chọn chiều rộng dải đất sao cho chẵn và nhỏ hơn đường kính
    # w = 2 * x_limit. Để đẹp thì w nên là số nguyên chẵn.
    possible_widths = [w for w in range(4, 2*radius, 2) if w < 2*radius]
    width = random.choice(possible_widths)
    
    price = random.choice(PRICE_CHOICES)
    
    return {
        "radius": radius,
        "width": width,
        "price": price,
        "diameter": 2 * radius
    }

TEMPLATE_QUESTION = Template(
    r"""
Một mảnh vườn hình tròn tâm \(O\) bán kính ${radius} m. Người ta cần trồng cây trên dải đất rộng ${width} m nhận \(O\) làm tâm đối xứng (như hình vẽ). Biết kinh phí trồng cây là ${price_display} đồng/\(\text{m}^2\). Hỏi cần bao nhiêu tiền để trồng cây trên dải đất đó? (làm tròn đến hàng đơn vị).

\begin{center}
${diagram}
\end{center}
"""
)

TEMPLATE_SOLUTION = Template(
    r"""
Chọn hệ trục tọa độ \(Oxy\) sao cho gốc \(O\) trùng với tâm mảnh vườn.
Phương trình đường tròn tâm \(O\) bán kính \(R=${radius}\) là:
\( x^2 + y^2 = ${radius}^2 \Leftrightarrow y = \pm \sqrt{${radius_sq} - x^2} \)
Dải đất cần trồng cây đối xứng qua tâm \(O\) và có chiều rộng ${width} m, nên giới hạn bởi hai đường thẳng \(x = -${half_width}\) và \(x = ${half_width}\).

Diện tích dải đất là:
\( S = \int_{-${half_width}}^{${half_width}} \left( \sqrt{${radius_sq} - x^2} - \left( -\sqrt{${radius_sq} - x^2} \right) \right) \text{d}x = \int_{-${half_width}}^{${half_width}} 2\sqrt{${radius_sq} - x^2} \text{d}x \)
Sử dụng máy tính cầm tay, ta tính được:
\( S \approx ${area_approx} \, (\text{m}^2) \)

Số tiền cần dùng để trồng cây là:
\( T = S \times ${price} \approx ${area_approx} \times ${price} \approx ${total_cost} \, (\text{đồng}) \)

Kết luận: Cần khoảng ${total_cost} đồng.
"""
)

class CircularGardenQuestion:
    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.correct_answer: Optional[str] = None
        self.config = config or GeneratorConfig()

    def generate_parameters(self) -> Dict[str, Any]:
        return _generate_garden_parameters()

    def calculate_answer(self) -> str:
        R = self.parameters["radius"]
        w = self.parameters["width"]
        price = self.parameters["price"]
        
        x = sp.Symbol('x')
        # Diện tích chính xác
        area_expr = sp.Integral(2 * sp.sqrt(R**2 - x**2), (x, -w/2, w/2))
        # Tính giá trị số
        area_val = area_expr.evalf()
        total_cost = area_val * price
        
        # Làm tròn đến hàng đơn vị
        cost_rounded = int(round(total_cost))
        
        self.parameters.update({
            "radius_sq": R**2,
            "half_width": w // 2 if w % 2 == 0 else w/2,
            "price_display": format_money(price),
            "area_approx": f"{area_val:.4f}".replace(".", ","),
            "total_cost": str(cost_rounded),
            "raw_cost": cost_rounded
        })
        
        return f"{cost_rounded}"

    def generate_tikz_diagram(self) -> str:
        R = self.parameters["radius"]
        w = self.parameters["width"]
        
        # Scale down for TikZ
        scale = 2.5 / R 
        tikz_R = R * scale
        tikz_half_w = (w / 2) * scale
        
        tikz = rf"""
\begin{{tikzpicture}}[scale=1, font=\footnotesize]
    \def\R{{{tikz_R:.3f}}}
    \def\hw{{{tikz_half_w:.3f}}}
    
    % Tô màu vùng dải đất
    \begin{{scope}}
        \clip (0,0) circle (\R);
        \fill[pattern=north east lines, pattern color=gray!60] (-\hw, -\R) rectangle (\hw, \R);
    \end{{scope}}

    % Vẽ đường tròn
    \draw[thick] (0,0) circle (\R);
    
    % Vẽ 2 dây cung (giới hạn bởi đường tròn)
    \begin{{scope}}
        \clip (0,0) circle (\R);
        \draw[thick] (-\hw, -2*\R) -- (-\hw, 2*\R);
        \draw[thick] (\hw, -2*\R) -- (\hw, 2*\R);
    \end{{scope}}
    
    % Tâm O
    \fill (0,0) circle (1.5pt) node[below] {{$O$}};
    
    % Kích thước bán kính
    \draw[dashed] (0,0) -- (45:\R) node[midway, above left] {{$R={R}$ m}};
    
    % Kích thước chiều rộng
    \draw[<->] (-\hw, 0.3) -- (\hw, 0.3) node[midway, fill=white, inner sep=1pt] {{$ {w} $ m}};
    
\end{{tikzpicture}}
"""
        return "\n".join(line for line in tikz.splitlines() if line.strip())

    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        logging.info("Đang tạo câu hỏi %s", question_number)
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        
        question_text = TEMPLATE_QUESTION.substitute(
            radius=self.parameters["radius"],
            width=self.parameters["width"],
            price_display=self.parameters["price_display"],
            diagram=self.generate_tikz_diagram()
        ).strip()
        
        solution = TEMPLATE_SOLUTION.substitute(
            radius=self.parameters["radius"],
            radius_sq=self.parameters["radius_sq"],
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
\title{Bài toán Trồng Cây Vườn Tròn}
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
            q = CircularGardenQuestion()
            questions_data.append(q.generate_question_only(i))
            
        latex_content = CircularGardenQuestion.create_latex_document(questions_data)
        
        filename = "circular_garden_questions.tex"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)
            
        print(f"✅ Đã tạo {filename} với {len(questions_data)} câu hỏi")
        print(f"📄 Biên dịch bằng: xelatex {filename}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

