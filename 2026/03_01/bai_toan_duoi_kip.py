import random
import sys
import os
from string import Template
from fractions import Fraction

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


# ==================== TYPE 1: Find v0 (velocity of A after acceleration) ====================

TEMPLATE_Q1 = Template(
    r"""
Câu ${idx}: Tại điểm \(O\), chất điểm \(A\) bắt đầu tăng tốc đều trong ${t1} giây để đạt vận tốc \(v_0\) (m/s), rồi tiếp tục chuyển động thẳng đều. Sau khi \(A\) xuất phát ${delta_t} giây, chất điểm \(B\) cũng xuất phát từ \(O\) với gia tốc không đổi \(a_2 = ${a2}\) (m/s\(^2\)). Biết \(B\) đuổi kịp \(A\) sau ${t2} giây kể từ khi \(B\) khởi hành. Tìm \(v_0\). (Đáp án làm tròn 2 chữ số sau dấu thập phân)

Lời giải:

${solution}

Đáp án: ${answer_display}
"""
)

TEMPLATE_SOL1 = Template(
    r"""Gọi \(a_1\) là gia tốc của \(A\) trong giai đoạn tăng tốc. Ta có \(v_0 = a_1 \cdot ${t1} \Rightarrow a_1 = \dfrac{v_0}{${t1}}\).

Quãng đường \(A\) đi được trong ${t1} giây đầu (tăng tốc): \(\displaystyle x_{A1} = \dfrac{1}{2} a_1 \cdot ${t1}^2 = \dfrac{1}{2} \cdot \dfrac{v_0}{${t1}} \cdot ${t1_sq} = ${x_A1_coef} v_0\).

Thời gian \(A\) chuyển động đều (kể từ lúc \(B\) xuất phát đến lúc gặp nhau): \(t_{\text{đều}} = ${t2} + ${delta_t} - ${t1} = ${t_uniform}\) giây.

Quãng đường \(A\) đi được trong giai đoạn chuyển động đều: \(x_{A2} = v_0 \cdot ${t_uniform} = ${t_uniform} v_0\).

Tổng quãng đường \(A\) đi được (đến lúc gặp \(B\)): \(x_A = x_{A1} + x_{A2} = ${x_A1_coef} v_0 + ${t_uniform} v_0 = ${x_A_total_coef} v_0\).

Quãng đường \(B\) đi được trong ${t2} giây: \(\displaystyle x_B = \dfrac{1}{2} a_2 \cdot ${t2}^2 = \dfrac{1}{2} \cdot ${a2} \cdot ${t2_sq} = ${x_B_val}\).

Khi \(B\) đuổi kịp \(A\): \(x_B = x_A \Leftrightarrow ${x_B_val} = ${x_A_total_coef} v_0 \Leftrightarrow v_0 = ${v0_val}\) m/s."""
)


# ==================== TYPE 2: Find v_B (velocity of B at catch-up) ====================

TEMPLATE_Q2 = Template(
    r"""
Câu ${idx}: Chất điểm \(A\) xuất phát từ \(O\), tăng tốc đều và đạt ${v_A} m/s sau ${t1} giây, sau đó duy trì vận tốc này. Chất điểm \(B\) khởi hành từ \(O\) muộn hơn \(A\) là ${delta_t} giây, chuyển động nhanh dần đều và đuổi kịp \(A\) sau ${t2} giây (tính từ lúc \(B\) xuất phát). Hỏi vận tốc của \(B\) tại thời điểm đuổi kịp \(A\) là bao nhiêu? (Đáp án làm tròn 2 chữ số sau dấu thập phân)

Lời giải:

${solution}

Đáp án: ${answer_display}
"""
)

TEMPLATE_SOL2 = Template(
    r"""Gọi \(a_1\) là gia tốc của \(A\) trong giai đoạn tăng tốc. Ta có \(${v_A} = a_1 \cdot ${t1} \Rightarrow a_1 = \dfrac{${v_A}}{${t1}}\).

Quãng đường \(A\) đi được trong ${t1} giây đầu (tăng tốc): \(\displaystyle x_{A1} = \dfrac{1}{2} a_1 \cdot ${t1}^2 = \dfrac{1}{2} \cdot \dfrac{${v_A}}{${t1}} \cdot ${t1_sq} = ${x_A1_val}\).

Thời gian \(A\) chuyển động đều (kể từ lúc \(B\) xuất phát đến lúc gặp nhau): \(t_{\text{đều}} = ${t2} + ${delta_t} - ${t1} = ${t_uniform}\) giây.

Quãng đường \(A\) đi được trong giai đoạn chuyển động đều: \(x_{A2} = ${v_A} \cdot ${t_uniform} = ${x_A2_val}\).

Tổng quãng đường \(A\) đi được (đến lúc gặp \(B\)): \(x_A = x_{A1} + x_{A2} = ${x_A1_val} + ${x_A2_val} = ${x_A_total}\).

Gọi \(a_2\) là gia tốc của \(B\), \(v_B\) là vận tốc của \(B\) khi đuổi kịp \(A\). Ta có \(v_B = a_2 \cdot ${t2} \Rightarrow a_2 = \dfrac{v_B}{${t2}}\).

Quãng đường \(B\) đi được trong ${t2} giây: \(\displaystyle x_B = \dfrac{1}{2} a_2 \cdot ${t2}^2 = \dfrac{1}{2} \cdot \dfrac{v_B}{${t2}} \cdot ${t2_sq} = ${x_B_coef} v_B\).

Khi \(B\) đuổi kịp \(A\): \(x_B = x_A \Leftrightarrow ${x_B_coef} v_B = ${x_A_total} \Leftrightarrow v_B = ${v_B_val}\) m/s."""
)


class CatchUpQuestion:
    def __init__(self):
        self.problem_type = 1  # 1 or 2
        self.t1 = 0       # Thời gian A tăng tốc
        self.delta_t = 0  # B xuất phát sau A bao lâu
        self.t2 = 0       # Thời gian B chạy đến khi đuổi kịp A
        
        # Type 1 specific
        self.a2 = 0       # Gia tốc của B (given)
        self.v0 = 0       # Vận tốc của A sau khi tăng tốc (to find)
        
        # Type 2 specific
        self.v_A = 0      # Vận tốc của A sau khi tăng tốc (given)
        self.v_B = 0      # Vận tốc của B khi đuổi kịp A (to find)

    def generate_parameters_type1(self):
        """Generate random parameters for Type 1: Find v0"""
        max_attempts = 1000
        for _ in range(max_attempts):
            # 20 values each
            self.t1 = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
            self.delta_t = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
            self.t2 = random.choice([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24])
            self.a2 = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
            
            if self.t2 + self.delta_t <= self.t1:
                continue
            
            x_B = Fraction(1, 2) * self.a2 * self.t2 * self.t2
            x_A_coef = Fraction(self.t2 + self.delta_t) - Fraction(self.t1, 2)
            
            if x_A_coef <= 0:
                continue
            
            v0 = x_B / x_A_coef
            
            if v0.denominator == 1 and 1 <= v0.numerator <= 50:
                self.v0 = v0
                return True
            elif v0.denominator <= 5 and v0.numerator <= 100:
                self.v0 = v0
                return True
        
        # Fallback
        self.t1 = 4
        self.delta_t = 2
        self.t2 = 6
        self.a2 = 3
        x_B = Fraction(1, 2) * self.a2 * self.t2 * self.t2
        x_A_coef = Fraction(self.t2 + self.delta_t) - Fraction(self.t1, 2)
        self.v0 = x_B / x_A_coef
        return True

    def generate_parameters_type2(self):
        """Generate random parameters for Type 2: Find v_B"""
        max_attempts = 1000
        for _ in range(max_attempts):
            # 20 values each
            self.t1 = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
            self.delta_t = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
            self.t2 = random.choice([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24])
            self.v_A = random.choice([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24, 25, 27, 30])
            
            if self.t2 + self.delta_t <= self.t1:
                continue
            
            # x_A = (t1/2) * v_A + (t2 + delta_t - t1) * v_A
            #     = (t1/2 + t2 + delta_t - t1) * v_A
            #     = (t2 + delta_t - t1/2) * v_A
            x_A_coef = Fraction(self.t2 + self.delta_t) - Fraction(self.t1, 2)
            
            if x_A_coef <= 0:
                continue
            
            x_A = x_A_coef * self.v_A
            
            # x_B = (t2/2) * v_B => v_B = 2 * x_A / t2
            v_B = Fraction(2) * x_A / Fraction(self.t2)
            
            if v_B.denominator == 1 and 1 <= v_B.numerator <= 50:
                self.v_B = v_B
                return True
            elif v_B.denominator <= 5 and v_B.numerator <= 100:
                self.v_B = v_B
                return True
        
        # Fallback (matching the image example: t1=8, v_A=6, delta_t=12, t2=8)
        self.t1 = 8
        self.delta_t = 12
        self.t2 = 8
        self.v_A = 6
        x_A_coef = Fraction(self.t2 + self.delta_t) - Fraction(self.t1, 2)
        x_A = x_A_coef * self.v_A
        self.v_B = Fraction(2) * x_A / Fraction(self.t2)
        return True

    def generate_parameters(self):
        """Randomly select problem type and generate parameters"""
        self.problem_type = random.choice([1, 2])
        if self.problem_type == 1:
            return self.generate_parameters_type1()
        else:
            return self.generate_parameters_type2()

    def solve_type1(self):
        """Calculate solution values for Type 1"""
        t1 = self.t1
        delta_t = self.delta_t
        t2 = self.t2
        a2 = self.a2
        
        x_A1_coef = Fraction(t1, 2)
        t_uniform = t2 + delta_t - t1
        x_A_total_coef = x_A1_coef + t_uniform
        x_B = Fraction(1, 2) * a2 * t2 * t2
        
        return {
            't1': t1,
            't1_sq': t1 * t1,
            'delta_t': delta_t,
            't2': t2,
            't2_sq': t2 * t2,
            'a2': a2,
            'x_A1_coef': to_latex_num_display(x_A1_coef),
            't_uniform': t_uniform,
            'x_A_total_coef': to_latex_num_display(x_A_total_coef),
            'x_B_val': to_latex_num_display(x_B),
            'v0_val': to_latex_num_display(self.v0)
        }

    def solve_type2(self):
        """Calculate solution values for Type 2"""
        t1 = self.t1
        delta_t = self.delta_t
        t2 = self.t2
        v_A = self.v_A
        
        # x_A1 = (t1/2) * v_A
        x_A1 = Fraction(t1, 2) * v_A
        
        t_uniform = t2 + delta_t - t1
        
        # x_A2 = t_uniform * v_A
        x_A2 = t_uniform * v_A
        
        # x_A = x_A1 + x_A2
        x_A_total = x_A1 + x_A2
        
        # x_B = (t2/2) * v_B
        x_B_coef = Fraction(t2, 2)
        
        return {
            't1': t1,
            't1_sq': t1 * t1,
            'delta_t': delta_t,
            't2': t2,
            't2_sq': t2 * t2,
            'v_A': v_A,
            'x_A1_val': to_latex_num_display(x_A1),
            't_uniform': t_uniform,
            'x_A2_val': to_latex_num_display(x_A2),
            'x_A_total': to_latex_num_display(x_A_total),
            'x_B_coef': to_latex_num_display(x_B_coef),
            'v_B_val': to_latex_num_display(self.v_B)
        }

    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        
        if self.problem_type == 1:
            sol_data = self.solve_type1()
            solution = TEMPLATE_SOL1.substitute(sol_data)
            params = {
                'idx': idx,
                't1': self.t1,
                'delta_t': self.delta_t,
                't2': self.t2,
                'a2': self.a2,
                'answer_display': format_answer_display(self.v0),
                'solution': solution
            }
            return TEMPLATE_Q1.substitute(params)
        else:
            sol_data = self.solve_type2()
            solution = TEMPLATE_SOL2.substitute(sol_data)
            params = {
                'idx': idx,
                't1': self.t1,
                'delta_t': self.delta_t,
                't2': self.t2,
                'v_A': self.v_A,
                'answer_display': format_answer_display(self.v_B),
                'solution': solution
            }
            return TEMPLATE_Q2.substitute(params)


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
        q = CatchUpQuestion()
        questions.append(q.generate_question(i + 1))
    
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "bai_toan_duoi_kip.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong bai_toan_duoi_kip.tex")


if __name__ == "__main__":
    main()
