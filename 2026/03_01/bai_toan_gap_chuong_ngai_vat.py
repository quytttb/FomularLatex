import random
import sys
import os
from string import Template
from fractions import Fraction
import math

# ==================== CONFIGURATION & HELPERS ====================

def to_latex_num(value):
    """Format number to LaTeX string, using fractions if appropriate"""
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        if value.numerator < 0:
            return f"-\\frac{{{abs(value.numerator)}}}{{{value.denominator}}}"
        return f"\\frac{{{value.numerator}}}{{{value.denominator}}}"
    
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        if abs(value - round(value)) < 1e-9:
            return str(round(value))
        f = Fraction(value).limit_denominator(100)
        if abs(float(f) - value) < 1e-9:
            if f.denominator == 1:
                return str(f.numerator)
            if f.numerator < 0:
                return f"-\\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"
            return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"
        # Standard rounding
        rounded = int(value * 100 + 0.5) / 100.0
        return str(rounded)
    return str(value)


def to_latex_num_display(value):
    """Format number to LaTeX string for display math, using dfrac"""
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        if value.numerator < 0:
            return f"-\\dfrac{{{abs(value.numerator)}}}{{{value.denominator}}}"
        return f"\\dfrac{{{value.numerator}}}{{{value.denominator}}}"
    
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        if abs(value - round(value)) < 1e-9:
            return str(round(value))
        f = Fraction(value).limit_denominator(100)
        if abs(float(f) - value) < 1e-9:
            if f.denominator == 1:
                return str(f.numerator)
            if f.numerator < 0:
                return f"-\\dfrac{{{abs(f.numerator)}}}{{{f.denominator}}}"
            return f"\\dfrac{{{f.numerator}}}{{{f.denominator}}}"
        # Standard rounding
        rounded = int(value * 100 + 0.5) / 100.0
        return str(rounded)
    return str(value)


def format_answer_display(value):
    """Format answer for display: number only, no unit. If decimal, show both 4.5 | 4,5"""
    if isinstance(value, Fraction):
        value = float(value)
    
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        # Round to 2 decimal places (standard rounding)
        rounded = int(value * 100 + 0.5) / 100.0
        if rounded == int(rounded):
            return str(int(rounded))
        # Format with both . and , separators
        str_dot = f"{rounded:.2f}".rstrip('0').rstrip('.')
        str_comma = str_dot.replace('.', ',')
        if '.' in str_dot:
            return f"{str_dot} | {str_comma}"
        return str_dot
    
    if isinstance(value, int):
        return str(value)
    
    return str(value)


def create_latex_document(content):
    return r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage{enumitem}
\usepackage{tikz}
\usepackage{tkz-tab}
\begin{document}
""" + content + r"\end{document}"


# ==================== SCENARIOS ====================

SCENARIOS = [
    {"subject": "chất điểm", "obstacle": "chướng ngại vật"},
    {"subject": "ô tô", "obstacle": "đèn đỏ"},
    {"subject": "xe máy", "obstacle": "vật cản trên đường"},
    {"subject": "xe đạp", "obstacle": "ổ gà trên đường"},
    {"subject": "tàu hỏa", "obstacle": "trạm dừng"},
    {"subject": "xe buýt", "obstacle": "trạm xe buýt"},
    {"subject": "xe tải", "obstacle": "trạm thu phí"},
    {"subject": "robot", "obstacle": "vật cản phía trước"},
    {"subject": "drone", "obstacle": "vùng cấm bay"},
    {"subject": "tàu điện", "obstacle": "ga tàu điện"},
]

# ==================== QUESTION TEMPLATE ====================

TEMPLATE_Q = Template(
    r"""
Câu ${idx}: Ban đầu, một ${subject} khởi hành và chuyển động thẳng đều với vận tốc \(v_0\) (m/s). Sau ${t1} giây, khi phát hiện ${obstacle} phía trước, ${subject} bắt đầu giảm tốc theo quy luật \(v(t) = -${k_display}t + a\) (m/s) cho đến khi dừng hẳn. Biết tổng quãng đường ${subject} đã đi từ lúc khởi hành đến khi dừng là ${S_total} m. Hãy tính \(v_0\). (Đáp án làm tròn 2 chữ số sau dấu thập phân)

Lời giải:

${solution}

Đáp án: ${answer_display}
"""
)

# ==================== SOLUTION TEMPLATE (Handwritten style) ====================

TEMPLATE_SOL = Template(
    r"""Giai đoạn 1: \(0 \to ${t1}\) (s): \(v_1 = v_0\)

Giai đoạn 2: \(0 \to t\) (s): \(v_2 = -${k_display}t + a = -${k_display}t + v_0\)

\(v_2(0) = v_1(${t1}) \Rightarrow a = v_0\)

Lập hệ: \[\begin{cases} S_1 = ${t1} \cdot v_0 \\ \displaystyle S_2 = \dfrac{0^2 - v_0^2}{2 \cdot \left(-${k_display}\right)} = ${S2_formula} \end{cases}\]

\(\Rightarrow S_1 + S_2 = ${S_total} \Leftrightarrow ${t1} v_0 + ${S2_formula} = ${S_total}\)

\(\Leftrightarrow v_0 = ${v0}\) m/s"""
)


class ObstacleStopQuestion:
    def __init__(self):
        self.t1 = 0         # Duration of uniform motion (phase 1)
        self.k = Fraction(0)  # Deceleration coefficient (k/2 is the slope)
        self.v0 = 0         # Initial velocity (answer)
        self.S_total = 0    # Total distance
        self.scenario = SCENARIOS[0]  # Current scenario

    def generate_parameters(self):
        """
        Generate parameters by reverse engineering.
        We choose v0, t1, k such that S_total is a nice integer.
        
        Logic:
        - S1 = t1 * v0
        - S2 = v0^2 / k (derived from v^2 - v0^2 = 2*a*s where a = -k/2)
        - S_total = S1 + S2 = t1 * v0 + v0^2 / k
        """
        # Random scenario from 10 options
        self.scenario = random.choice(SCENARIOS)
        
        max_attempts = 1000
        for _ in range(max_attempts):
            # 20 values each
            self.v0 = random.choice([4, 5, 6, 8, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 27, 28, 30, 32, 35])
            self.t1 = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
            # k_num from 20 values, deceleration is -k_num/2
            k_num = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
            self.k = Fraction(k_num, 2)
            
            # S1 = t1 * v0
            S1 = self.t1 * self.v0
            
            # S2 = v0^2 / (2k)
            # v^2 - v0^2 = 2aS => 0 - v0^2 = 2(-k)S2 => S2 = v0^2 / (2k)
            S2 = Fraction(self.v0 * self.v0, 1) / (2 * self.k)
            
            # S_total = S1 + S2
            S_total = S1 + S2
            
            # Check if S_total is a nice integer
            if S_total.denominator == 1 and 50 <= S_total.numerator <= 500:
                self.S_total = int(S_total)
                return True
        
        # Fallback to the example from the image
        self.v0 = 10
        self.t1 = 6
        self.k = Fraction(5, 2)
        self.S_total = 80
        return True

    def solve(self):
        """Calculate all solution values"""
        # S2 = v0^2 / 2k
        S2 = Fraction(self.v0 * self.v0, 1) / (2 * self.k)
        
        # Format k for display (e.g., 5/2)
        k_display = to_latex_num_display(self.k)
        
        # S2 formula: v0^2 / 2k
        two_k = 2 * self.k
        if two_k.denominator == 1:
            S2_formula = f"\\dfrac{{v_0^2}}{{{two_k.numerator}}}"
        else:
            # two_k = num/den
            if two_k.numerator == 1:
                S2_formula = f"{two_k.denominator} v_0^2"
            else:
                S2_formula = f"\\dfrac{{{two_k.denominator} v_0^2}}{{{two_k.numerator}}}"
        
        return {
            't1': self.t1,
            'k_display': k_display,
            'v0': self.v0,
            'S_total': self.S_total,
            'S2_formula': S2_formula
        }

    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        sol_data = self.solve()
        
        # Generate solution text
        solution = TEMPLATE_SOL.substitute(sol_data)
        
        # Generate question
        params = {
            'idx': idx,
            'subject': self.scenario['subject'],
            'obstacle': self.scenario['obstacle'],
            't1': self.t1,
            'k_display': to_latex_num_display(self.k),
            'v0': self.v0,
            'S_total': self.S_total,
            'solution': solution,
            'answer_display': format_answer_display(self.v0)
        }
        
        return TEMPLATE_Q.substitute(params)


# ==================== MAIN ====================

def main():
    num_questions = 4
    if len(sys.argv) > 1:
        try:
            num_questions = int(sys.argv[1])
        except ValueError:
            pass
    
    questions = []
    for i in range(num_questions):
        q = ObstacleStopQuestion()
        questions.append(q.generate_question(i + 1))
    
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "bai_toan_gap_chuong_ngai_vat.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong bai_toan_gap_chuong_ngai_vat.tex")


if __name__ == "__main__":
    main()

