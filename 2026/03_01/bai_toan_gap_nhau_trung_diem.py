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


# ==================== QUESTION TEMPLATE ====================

TEMPLATE_Q = Template(
    r"""
Câu ${idx}: Chất điểm \(X\) xuất phát từ đầu \(A\) của đoạn thẳng \(AB\) với vận tốc thay đổi theo thời gian \(t\) (giây) theo quy luật \(v(t) = ${alpha_display}t^2 + ${beta_display}t\) (m/s). Sau ${delta_t} giây, chất điểm \(Y\) xuất phát từ đầu \(B\), chuyển động ngược chiều \(X\) với gia tốc không đổi \(a\) (m/s\(^2\)). Hai chất điểm gặp nhau tại trung điểm của \(AB\). Biết \(AB = ${L}\) m. Tính \(a\). (Đáp án làm tròn 2 chữ số sau dấu thập phân)

Lời giải:

${solution}

Đáp án: ${answer_display}
"""
)

# ==================== SOLUTION TEMPLATE (Handwritten style) ====================

TEMPLATE_SOL = Template(
    r"""Gọi \(x\) (giây) là thời gian \(X\) di chuyển đến trung điểm của \(AB\).

\(\Leftrightarrow \displaystyle \Delta S_X \Big|_0^{x} = ${half_L}\).

\(\Leftrightarrow \displaystyle \int_0^{x} \left(${alpha_display}t^2 + ${beta_display}t\right) dt = ${half_L}\).

\(\Leftrightarrow \displaystyle \left. ${alpha_3_display}t^3 + ${beta_2_display}t^2 \right|_0^{x} = ${half_L}\).

\(\Leftrightarrow ${alpha_3_display}x^3 + ${beta_2_display}x^2 - ${half_L} = 0\).

\(\Leftrightarrow x = ${T_X}\).

Quãng đường \(Y\) đi được: \(\displaystyle x_Y(t) = \dfrac{1}{2}a t^2\).

\(\Rightarrow \displaystyle x_Y(${T_Y}) = ${half_L} \Leftrightarrow \dfrac{1}{2} a \cdot ${T_Y}^2 = ${half_L} \Leftrightarrow a = ${a_display}\)."""
)


class MidpointMeetQuestion:
    def __init__(self):
        self.L = 0          # Length of AB
        self.alpha = Fraction(0)   # Coefficient of t^2 in v(t)
        self.beta = Fraction(0)    # Coefficient of t in v(t)
        self.delta_t = 0    # Y starts delta_t seconds after X
        self.T_X = 0        # Time for X to reach midpoint
        self.T_Y = 0        # Time for Y to reach midpoint
        self.a = Fraction(0)       # Acceleration of Y (to find)

    def generate_parameters(self):
        """
        Generate parameters by reverse engineering.
        We choose T_X, delta_t, L, and then construct alpha, beta such that
        integral of v(t) from 0 to T_X equals L/2.
        """
        max_attempts = 1000
        for _ in range(max_attempts):
            # Choose T_X (time for X to reach midpoint) - 20 values
            self.T_X = random.choice([8, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 27, 28, 30, 32, 35, 36, 40])
            
            # Choose delta_t such that T_Y = T_X - delta_t is positive and nice - 20 values
            possible_delta = [d for d in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24, 25] if d < self.T_X and self.T_X - d >= 4]
            if not possible_delta:
                continue
            self.delta_t = random.choice(possible_delta)
            self.T_Y = self.T_X - self.delta_t
            
            # Choose L (even number, L/2 should be nice) - 20 values
            self.L = random.choice([80, 100, 120, 140, 150, 160, 180, 200, 220, 240, 250, 260, 280, 300, 320, 350, 360, 400, 420, 450])
            half_L = Fraction(self.L, 2)
            
            # Calculate a = 2 * (L/2) / T_Y^2 = L / T_Y^2
            a = Fraction(self.L, self.T_Y * self.T_Y)
            
            # Check if a is a nice number
            if a.denominator > 10:
                continue
            
            # Now we need to find alpha, beta such that:
            # integral_0^T_X (alpha*t^2 + beta*t) dt = L/2
            # = (alpha/3)*T_X^3 + (beta/2)*T_X^2 = L/2
            #
            # We can choose alpha and solve for beta, or vice versa.
            # Let's try some simple alpha values and see if beta comes out nice.
            
            T_X_cubed = self.T_X ** 3
            T_X_squared = self.T_X ** 2
            
            # Try different alpha denominators - 20 values
            for alpha_denom in [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 140, 150, 160, 180, 200, 210, 240, 250, 280, 300]:
                alpha = Fraction(1, alpha_denom)
                
                # (alpha/3)*T_X^3 + (beta/2)*T_X^2 = L/2
                # (beta/2)*T_X^2 = L/2 - (alpha/3)*T_X^3
                # beta = (L/2 - (alpha/3)*T_X^3) * 2 / T_X^2
                
                remaining = half_L - (alpha * T_X_cubed / 3)
                if remaining <= 0:
                    continue
                
                beta = remaining * 2 / T_X_squared
                
                # Check if beta is a nice simple fraction
                if beta.denominator <= 10 and beta.numerator > 0:
                    self.alpha = alpha
                    self.beta = beta
                    self.a = a
                    return True
            
        # Fallback to the example from the image
        self.L = 200
        self.alpha = Fraction(1, 80)
        self.beta = Fraction(1, 3)
        self.T_X = 20
        self.delta_t = 10
        self.T_Y = 10
        self.a = Fraction(2)
        return True

    def solve(self):
        """Calculate all solution values"""
        half_L = Fraction(self.L, 2)
        
        # alpha/3 for the primitive
        alpha_3 = self.alpha / 3
        
        # beta/2 for the primitive
        beta_2 = self.beta / 2
        
        return {
            'L': self.L,
            'half_L': int(half_L) if half_L.denominator == 1 else to_latex_num_display(half_L),
            'alpha_display': to_latex_num_display(self.alpha),
            'beta_display': to_latex_num_display(self.beta),
            'alpha_3_display': to_latex_num_display(alpha_3),
            'beta_2_display': to_latex_num_display(beta_2),
            'delta_t': self.delta_t,
            'T_X': self.T_X,
            'T_Y': self.T_Y,
            'a_display': to_latex_num_display(self.a)
        }

    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        sol_data = self.solve()
        
        # Generate solution text
        solution = TEMPLATE_SOL.substitute(sol_data)
        
        # Generate question
        params = {
            'idx': idx,
            'L': self.L,
            'alpha_display': to_latex_num_display(self.alpha),
            'beta_display': to_latex_num_display(self.beta),
            'delta_t': self.delta_t,
            'a_display': to_latex_num_display(self.a),
            'solution': solution,
            'answer_display': format_answer_display(self.a)
        }
        
        return TEMPLATE_Q.substitute(params)


# ==================== MAIN ====================

def main():
    num_questions = 3
    if len(sys.argv) > 1:
        try:
            num_questions = int(sys.argv[1])
        except ValueError:
            pass
    
    questions = []
    for i in range(num_questions):
        q = MidpointMeetQuestion()
        questions.append(q.generate_question(i + 1))
    
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "bai_toan_gap_nhau_trung_diem.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong bai_toan_gap_nhau_trung_diem.tex")


if __name__ == "__main__":
    main()


