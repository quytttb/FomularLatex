"""
Trình sinh đề toán thực tế: Tính chi phí làm cổng vòm (Parabol + Bán nguyệt).
"""

import logging
import os
import random
import sys
from dataclasses import dataclass
from string import Template
from typing import Any, Dict, List, Optional, Tuple, Union

import sympy as sp

# Cấu hình
RADIUS_CHOICES = list(range(2, 60)) # Bán kính (m)
PRICE_HIGH_CHOICES = [x * 10000 for x in range(100, 300, 2)] # Giá phần hoa văn (1tr - 3tr)
PRICE_LOW_CHOICES = [x * 10000 for x in range(20, 100, 1)] # Giá phần còn lại (200k - 1tr)

@dataclass
class GeneratorConfig:
    pass

def format_money(value: int) -> str:
    return str(int(value))

def _generate_arch_parameters() -> Dict[str, Any]:
    R = random.choice(RADIUS_CHOICES)
    
    # Chọn trường hợp giao điểm đẹp: x0 = R/2
    # Khi đó y0 = R * sqrt(3) / 2
    # Parabola y = a*x^2 đi qua (R/2, R*sqrt(3)/2)
    # => R*sqrt(3)/2 = a * (R^2 / 4) => a = (2*sqrt(3))/R
    
    x0 = R / 2
    a_val = (2 * sp.sqrt(3)) / R
    
    # Giá tiền
    p1 = random.choice(PRICE_HIGH_CHOICES)
    p2 = random.choice([p for p in PRICE_LOW_CHOICES if p < p1])
    
    return {
        "radius": R,
        "diameter": 2 * R,
        "x_intersection": x0,
        "a_coeff": a_val,
        "price_pattern": p1,
        "price_plain": p2
    }

TEMPLATE_QUESTION = Template(
    r"""
Vòm trên một cái cổng có dạng như hình vẽ. Phần gạch chéo là hình phẳng giới hạn bởi parabol \(y = ${parabola_eq}\) và nửa đường tròn có đường kính bằng ${diameter} m (phần tô đậm trong hình vẽ).
Người ta làm một họa tiết để đặt vừa khít vào phần gạch chéo với giá ${price1_display} đồng/\(\text{m}^2\). Phần còn lại có giá ${price2_display} đồng/\(\text{m}^2\).
Số tiền cần chi trả để làm vòm cổng gần với số nào nhất sau đây?

\begin{center}
${diagram}
\end{center}
"""
)

TEMPLATE_SOLUTION = Template(
    r"""
Chọn hệ trục tọa độ \(Oxy\) như hình vẽ, gốc \(O\) là trung điểm của đường kính.
Phương trình đường tròn tâm \(O\) bán kính \(R=${radius}\) (nửa trên) là:
\( y = \sqrt{${radius}^2 - x^2} \)
Phương trình parabol là \(y = ${parabola_eq}\).

Hoành độ giao điểm của parabol và nửa đường tròn là nghiệm của phương trình:
\( ${parabola_eq} = \sqrt{${radius}^2 - x^2} \)
Giải phương trình này (hoặc dựa vào hình vẽ/tính chất), ta tìm được các hoành độ giao điểm là \(x = \pm ${x_inter}\).

Diện tích phần gạch chéo (hoa văn) là:
\( S_1 = \int_{-${x_inter}}^{${x_inter}} \left( \sqrt{${radius}^2 - x^2} - ${parabola_eq} \right) \text{d}x \)
Sử dụng máy tính cầm tay, ta tính được:
\( S_1 \approx ${s1_approx} \, (\text{m}^2) \)

Diện tích của cả vòm cổng (nửa hình tròn) là:
\( S_{\text{total}} = \frac{1}{2} \pi R^2 = \frac{1}{2} \pi \cdot ${radius}^2 \approx ${s_total_approx} \, (\text{m}^2) \)

Diện tích phần còn lại là:
\( S_2 = S_{\text{total}} - S_1 \approx ${s2_approx} \, (\text{m}^2) \)

Tổng chi phí là:
\( T = S_1 \times ${price1} + S_2 \times ${price2} \)
\( T \approx ${s1_approx} \times ${price1} + ${s2_approx} \times ${price2} \approx ${total_cost} \, (\text{đồng}) \)

Kết luận: Cần khoảng ${total_cost} đồng.
"""
)

class ArchGateQuestion:
    def __init__(self):
        self.parameters = {}
        self.correct_answer = ""

    def generate_parameters(self):
        return _generate_arch_parameters()

    def calculate_answer(self):
        R = self.parameters["radius"]
        a = self.parameters["a_coeff"]
        # x0 = self.parameters["x_intersection"] # Dùng giá trị chính xác thay vì float
        p1 = self.parameters["price_pattern"]
        p2 = self.parameters["price_plain"]
        
        x = sp.Symbol('x')
        
        # Sử dụng tính toán hình thức (symbolic) để đảm bảo chính xác
        R_sym = sp.Integer(R)
        x0_sym = sp.Rational(R, 2)
        
        # Diện tích S1 (hoa văn)
        # S1 = Integral(sqrt(R^2 - x^2) - a*x^2) from -x0 to x0
        # Do tính đối xứng: 2 * Integral(sqrt(R^2 - x^2) - a*x^2) from 0 to x0
        
        # Tính chính xác bằng sympy
        integrand = sp.sqrt(R_sym**2 - x**2) - a * x**2
        # Dùng doit() để tính tích phân dạng hình thức trước khi xấp xỉ số
        s1_expr = 2 * sp.Integral(integrand, (x, 0, x0_sym)).doit()
        s1_val = s1_expr.evalf()
        
        # Diện tích tổng (nửa tròn)
        s_total_expr = sp.Rational(1, 2) * sp.pi * R_sym**2
        s_total_val = s_total_expr.evalf()
        
        # Diện tích S2
        s2_expr = s_total_expr - s1_expr
        s2_val = s2_expr.evalf()
        
        # Tính chi phí dựa trên biểu thức chính xác
        total_cost_expr = s1_expr * p1 + s2_expr * p2
        total_cost = total_cost_expr.evalf()
        
        # Làm tròn số học (0.5 làm tròn lên) để khớp với đáp án thông thường
        cost_rounded = int(total_cost + 0.5)
        
        # Format phương trình parabol cho đẹp
        # a có thể chứa sqrt(3).
        # Nếu R=2, a=sqrt(3). y = sqrt(3)x^2.
        # Nếu R=4, a=sqrt(3)/2. y = \frac{\sqrt{3}}{2}x^2.
        a_latex = sp.latex(a)
        if "sqrt" in str(a): # Simple check, sympy latex usually handles it well
             # Custom fix for cleaner latex if needed, but sp.latex is usually good
             pass
             
        # Force specific formatting if it's exactly sqrt(3) or similar
        if a == sp.sqrt(3):
            parabola_eq = r"\sqrt{3}x^2"
        else:
            parabola_eq = f"{a_latex}x^2"

        self.parameters.update({
            "parabola_eq": parabola_eq,
            "x_inter": sp.latex(sp.nsimplify(x0_sym)),
            "price1_display": format_money(p1),
            "price2_display": format_money(p2),
            "price1": p1,
            "price2": p2,
            "s1_approx": f"{s1_val:.4f}".replace(".", ","),
            "s_total_approx": f"{s_total_val:.4f}".replace(".", ","),
            "s2_approx": f"{s2_val:.4f}".replace(".", ","),
            "total_cost": format_money(cost_rounded)
        })
        
        return f"{format_money(cost_rounded)}"

    def generate_tikz_diagram(self) -> str:
        R = self.parameters["radius"]
        x0 = float(self.parameters["x_intersection"])
        a_val = float(self.parameters["a_coeff"].evalf())
        
        # Scale để hình vẽ không quá to hoặc nhỏ trong LaTeX
        scale = 2.5 / R
        tikz_R = R * scale
        tikz_x0 = x0 * scale
        
        # Parabola trong tikz: y = a_tikz * x^2
        # y_real = a_real * x_real^2
        # y_tikz / scale = a_real * (x_tikz / scale)^2
        # y_tikz = a_real * x_tikz^2 / scale
        # => a_tikz = a_real / scale
        tikz_a = a_val / scale

        tikz = rf"""
\begin{{tikzpicture}}[scale=1, font=\footnotesize]
    \def\R{{{tikz_R:.3f}}}
    \def\xzero{{{tikz_x0:.3f}}}
    \def\a{{{tikz_a:.3f}}}
    
    % Trục tọa độ
    \draw[->] (-\R-0.5, 0) -- (\R+0.5, 0) node[right] {{$x$}};
    \draw[->] (0, 0) -- (0, \R+0.5) node[above] {{$y$}};
    \fill (0,0) circle (1pt) node[below right] {{$O$}};
    
    % Nửa đường tròn
    \draw[thick, name path=circle] (\R, 0) arc (0:180:\R);
    
    % Parabol
    \draw[thick, domain=-\xzero-0.5:\xzero+0.5, samples=100, name path=parabola] plot (\x, {{\a * \x * \x}});
    
    % Tô màu vùng giao (S1)
    % Vùng giới hạn bởi parabol (dưới) và đường tròn (trên)
    \begin{{scope}}
        % Clip hình tròn
        \clip (0,0) circle (\R);
        % Clip phía trên parabol: Tạo path bao quanh vùng phía trên parabol
        % Đi từ -R đến R theo parabol, rồi lên R+1, sang trái -R, rồi về
        \clip plot[domain=-\R:\R, samples=100] (\x, {{\a * \x * \x}}) -- (\R, \R+1) -- (-\R, \R+1) -- cycle;
        \fill[pattern=north east lines, pattern color=gray!60] (-\R, -\R) rectangle (\R, \R);
    \end{{scope}}
    
    % Vẽ lại đường viền cho rõ (optional)
    \draw[thick] (\R, 0) arc (0:180:\R);
    
    % Các mốc tọa độ
    \draw (\xzero, 0.1) -- (\xzero, -0.1) node[below] {{${self.parameters['x_inter']}$}};
    \draw (-\xzero, 0.1) -- (-\xzero, -0.1) node[below] {{$-{self.parameters['x_inter']}$}};
    \draw (\R, 0.1) -- (\R, -0.1) node[below] {{${self.parameters['radius']}$}};
    \draw (-\R, 0.1) -- (-\R, -0.1) node[below] {{$-{self.parameters['radius']}$}};
    
\end{{tikzpicture}}
"""
        return "\n".join(line for line in tikz.splitlines() if line.strip())

    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        
        question_text = TEMPLATE_QUESTION.substitute(
            parabola_eq=self.parameters["parabola_eq"],
            diameter=self.parameters["diameter"],
            price1_display=self.parameters["price1_display"],
            price2_display=self.parameters["price2_display"],
            diagram=self.generate_tikz_diagram()
        ).strip()
        
        solution = TEMPLATE_SOLUTION.substitute(
            radius=self.parameters["radius"],
            parabola_eq=self.parameters["parabola_eq"],
            x_inter=self.parameters["x_inter"],
            s1_approx=self.parameters["s1_approx"],
            s_total_approx=self.parameters["s_total_approx"],
            s2_approx=self.parameters["s2_approx"],
            price1=self.parameters["price1"],
            price2=self.parameters["price2"],
            total_cost=self.parameters["total_cost"]
        ).strip()
        
        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += "Lời giải:\n\n" + solution + "\n"
        return question_content, self.correct_answer

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
\usetikzlibrary{patterns, intersections}
\begin{document}
\title{Bài toán Cổng Vòm (Parabol + Đường Tròn)}
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
            q = ArchGateQuestion()
            questions_data.append(q.generate_question_only(i))
            
        latex_content = ArchGateQuestion.create_latex_document(questions_data)
        
        filename = "arch_gate_questions.tex"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)
            
        print(f"✅ Đã tạo {filename} với {len(questions_data)} câu hỏi")
        print(f"📄 Biên dịch bằng: xelatex {filename}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
