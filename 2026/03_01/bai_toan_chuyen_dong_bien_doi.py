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
        # Standard rounding for display if not exact fraction (though unlikely here)
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
        # Round to 2 decimal places (standard rounding: 3.125 -> 3.13)
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


# ==================== TYPE 1: Finding Initial Velocity ====================
# Given: Stopping time T and distance S, v(t) = v0 + at (decelerating)
# Find: v0

TEMPLATE_Q1 = Template(
    r"""
Câu ${idx}: Một đoàn tàu đang chạy thì hãm phanh. Vận tốc của tàu thay đổi theo thời gian \(t\) (s) theo công thức \(v(t) = v_0 + at\) (m/s), với \(a\) (m/s\(^2\)) là gia tốc. Sau ${T} giây kể từ khi hãm phanh, tàu dừng hẳn và đã đi được quãng đường ${S} m. Tìm vận tốc ban đầu \(v_0\). (Đáp án làm tròn 2 chữ số sau dấu thập phân)

Lời giải:

${solution}

Đáp án: ${answer_display}
"""
)

TEMPLATE_SOL1 = Template(
    r"""Ta có \(v(${T}) = 0 \Leftrightarrow v_0 + ${T}a = 0 \Leftrightarrow a = -\dfrac{v_0}{${T}}\)

\(\Rightarrow v(t) = v_0 - \dfrac{v_0}{${T}}t\)

Quãng đường đi được: \(\displaystyle S = \int_0^{${T}} v(t) \, dt = \int_0^{${T}} \left(v_0 - \dfrac{v_0}{${T}}t\right) dt = \left. v_0 t - \dfrac{v_0}{${T}} \cdot \dfrac{t^2}{2} \right|_0^{${T}} = ${T}v_0 - \dfrac{v_0}{${T_times_2}} \cdot ${T_sq} = \dfrac{${T}v_0}{2}\)

\(\Rightarrow \dfrac{${T}v_0}{2} = ${S} \Leftrightarrow v_0 = ${answer}\) m/s"""
)


# ==================== TYPE 2: Takeoff Distance ====================
# Given: v(t) = t^2 + bt, takeoff velocity v_final
# Find: Runway distance S

TEMPLATE_Q2 = Template(
    r"""
Câu ${idx}: Một máy bay bắt đầu chạy đà trên đường băng với vận tốc thay đổi theo thời gian \(t\) (giây) theo công thức \(v(t) = t^2 + ${b}t\) (m/s). Máy bay cất cánh khi đạt vận tốc ${v_final} m/s. Hỏi máy bay đã chạy được bao nhiêu mét trên đường băng? (Đáp án làm tròn 2 chữ số sau dấu thập phân)

Lời giải:

${solution}

Đáp án: ${answer_display}
"""
)

TEMPLATE_SOL2 = Template(
    r"""Ta có \(v(t) = ${v_final} \Leftrightarrow t^2 + ${b}t = ${v_final} \Leftrightarrow t^2 + ${b}t - ${v_final} = 0 \Leftrightarrow t = ${T}\) (vì \(t > 0\))

Quãng đường máy bay đi được: \(\displaystyle S = \int_0^{${T}} v(t) \, dt = \int_0^{${T}} \left(t^2 + ${b}t\right) dt = \left. \dfrac{t^3}{3} + \dfrac{${b}t^2}{2} \right|_0^{${T}} = \dfrac{${T_cubed}}{3} + \dfrac{${b} \cdot ${T_sq}}{2} = ${answer}\) m"""
)


# ==================== TYPE 3: Stopping Distance ====================
# Given: v(t) = -at + b (decelerating)
# Find: Distance S until stop

TEMPLATE_Q3 = Template(
    r"""
Câu ${idx}: Khi đang chạy với vận tốc ${v0} m/s, người lái ô tô đạp phanh. Vận tốc xe sau đó thay đổi theo thời gian \(t\) (giây) theo quy luật \(v(t) = -${a}t + ${v0}\) (m/s). Tính quãng đường xe đi được cho đến khi dừng hẳn. (Đáp án làm tròn 2 chữ số sau dấu thập phân)

Lời giải:

${solution}

Đáp án: ${answer_display}
"""
)

TEMPLATE_SOL3 = Template(
    r"""Ta có \(v(t) = 0 \Leftrightarrow -${a}t + ${v0} = 0 \Leftrightarrow t = ${T}\)

Quãng đường ô tô đi được: \(\displaystyle S = \int_0^{${T}} v(t) \, dt = \int_0^{${T}} \left(-${a}t + ${v0}\right) dt = \left. -\dfrac{${a}t^2}{2} + ${v0}t \right|_0^{${T}} = -\dfrac{${a} \cdot ${T_sq}}{2} + ${v0} \cdot ${T} = ${answer}\) m"""
)


# ==================== TYPE 4: Distance in Last k Seconds ====================
# Given: v(t) = -at + b (decelerating), find distance in last k seconds
# Find: Distance S in [T-k, T]

TEMPLATE_Q4 = Template(
    r"""
Câu ${idx}: Ô tô đang chạy với vận tốc ${v0} m/s thì đạp phanh. Vận tốc xe thay đổi theo thời gian \(t\) (giây) theo quy luật \(v(t) = -${a}t + ${v0}\) (m/s) cho đến khi dừng hẳn. Hỏi trong ${k} giây cuối cùng trước khi dừng, xe đã đi được bao nhiêu mét? (Đáp án làm tròn 2 chữ số sau dấu thập phân)

Lời giải:

${solution}

Đáp án: ${answer_display}
"""
)

TEMPLATE_SOL4 = Template(
    r"""Ta có \(v(t) = 0 \Leftrightarrow -${a}t + ${v0} = 0 \Leftrightarrow t = ${T}\)

Quãng đường ô tô đi được trong ${k} giây cuối: \(\displaystyle S = \int_{${T_minus_k}}^{${T}} v(t) \, dt = \int_{${T_minus_k}}^{${T}} \left(-${a}t + ${v0}\right) dt = \left. -\dfrac{${a}t^2}{2} + ${v0}t \right|_{${T_minus_k}}^{${T}}\)

\(\Leftrightarrow S = \left(-\dfrac{${a} \cdot ${T_sq}}{2} + ${v0} \cdot ${T}\right) - \left(-\dfrac{${a} \cdot ${T_minus_k_sq}}{2} + ${v0} \cdot ${T_minus_k}\right) = ${S_at_T} - ${S_at_T_minus_k} = ${answer}\) m"""
)


class VariableMotionQuestion:
    def __init__(self):
        self.problem_type = 1  # 1, 2, 3, or 4
        # Type 1 params
        self.T1 = 0       # Stopping time
        self.S1 = 0       # Stopping distance
        self.v0_1 = 0     # Initial velocity (answer)
        # Type 2 params
        self.b2 = 0       # Coefficient in v(t) = t^2 + bt
        self.v_final2 = 0 # Takeoff velocity
        self.T2 = 0       # Time to takeoff
        self.S2 = 0       # Runway distance (answer)
        # Type 3 params
        self.a3 = 0       # Deceleration rate
        self.v0_3 = 0     # Initial velocity
        self.T3 = 0       # Stopping time
        self.S3 = 0       # Stopping distance (answer)
        # Type 4 params
        self.a4 = 0       # Deceleration rate
        self.v0_4 = 0     # Initial velocity
        self.T4 = 0       # Stopping time
        self.k4 = 0       # Last k seconds
        self.S4 = 0       # Distance in last k seconds (answer)

    def generate_parameters_type1(self):
        """Type 1: Find v0 given T and S"""
        for _ in range(1000):
            # 20 values each
            self.T1 = random.choice([8, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 26, 28, 30, 32, 35, 36, 40, 42, 45])
            self.v0_1 = random.choice([4, 6, 8, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 26, 28, 30, 32, 35, 36, 40])
            # S = T * v0 / 2
            S = Fraction(self.T1 * self.v0_1, 2)
            if S.denominator == 1 and S.numerator <= 500:
                self.S1 = int(S)
                return True
        # Fallback
        self.T1 = 20
        self.v0_1 = 12
        self.S1 = 120
        return True

    def generate_parameters_type2(self):
        """Type 2: Takeoff distance with v(t) = t^2 + bt"""
        for _ in range(1000):
            # 20 values each
            self.T2 = random.choice([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22])
            self.b2 = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24, 25])
            # v(T) = T^2 + b*T = v_final
            self.v_final2 = self.T2 * self.T2 + self.b2 * self.T2
            if self.v_final2 > 50 and self.v_final2 <= 500:
                # S = T^3/3 + b*T^2/2
                S = Fraction(self.T2 ** 3, 3) + Fraction(self.b2 * self.T2 ** 2, 2)
                if S.denominator == 1 or S.denominator in [2, 3, 6]:
                    self.S2 = S
                    return True
        # Fallback (matching image: T=10, b=10, v_final=200)
        self.T2 = 10
        self.b2 = 10
        self.v_final2 = 200
        self.S2 = Fraction(1000, 3) + Fraction(500, 1)  # 1000/3 + 500 = 2500/3
        return True

    def generate_parameters_type3(self):
        """Type 3: Stopping distance with v(t) = -at + v0"""
        for _ in range(1000):
            # 20 values each
            self.a3 = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24])
            self.v0_3 = random.choice([6, 8, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 27, 28, 30, 32, 35, 36, 40])
            # T = v0 / a
            T = Fraction(self.v0_3, self.a3)
            if T.denominator == 1 and T.numerator <= 20:
                self.T3 = int(T)
                # S = -a*T^2/2 + v0*T = v0*T/2
                S = Fraction(self.v0_3 * self.T3, 2)
                if S.denominator == 1:
                    self.S3 = int(S)
                    return True
        # Fallback (matching image: a=5, v0=10, T=2, S=10)
        self.a3 = 5
        self.v0_3 = 10
        self.T3 = 2
        self.S3 = 10
        return True

    def generate_parameters_type4(self):
        """Type 4: Distance in last k seconds with v(t) = -at + v0"""
        for _ in range(1000):
            # 20 values each
            self.a4 = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24])
            self.v0_4 = random.choice([8, 10, 12, 14, 15, 16, 18, 20, 21, 24, 25, 27, 28, 30, 32, 35, 36, 40, 42, 45])
            # T = v0 / a
            T = Fraction(self.v0_4, self.a4)
            if T.denominator == 1 and T.numerator >= 4 and T.numerator <= 20:
                self.T4 = int(T)
                # k must be less than T, 20 possible values
                possible_k = [k for k in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20] if k < self.T4]
                if not possible_k:
                    continue
                self.k4 = random.choice(possible_k)
                # S = integral from T-k to T of (-at + v0) dt
                # At T: -a*T^2/2 + v0*T
                # At T-k: -a*(T-k)^2/2 + v0*(T-k)
                T_minus_k = self.T4 - self.k4
                S_at_T = Fraction(-self.a4 * self.T4 ** 2, 2) + self.v0_4 * self.T4
                S_at_T_minus_k = Fraction(-self.a4 * T_minus_k ** 2, 2) + self.v0_4 * T_minus_k
                S = S_at_T - S_at_T_minus_k
                if S.denominator == 1 and S.numerator > 0:
                    self.S4 = int(S)
                    return True
        # Fallback
        self.a4 = 2
        self.v0_4 = 10
        self.T4 = 5
        self.k4 = 3
        T_minus_k = self.T4 - self.k4
        S_at_T = Fraction(-self.a4 * self.T4 ** 2, 2) + self.v0_4 * self.T4
        S_at_T_minus_k = Fraction(-self.a4 * T_minus_k ** 2, 2) + self.v0_4 * T_minus_k
        self.S4 = int(S_at_T - S_at_T_minus_k)
        return True

    def generate_parameters(self):
        """Randomly select problem type and generate parameters"""
        self.problem_type = random.choice([1, 2, 3, 4])
        if self.problem_type == 1:
            return self.generate_parameters_type1()
        elif self.problem_type == 2:
            return self.generate_parameters_type2()
        elif self.problem_type == 3:
            return self.generate_parameters_type3()
        else:
            return self.generate_parameters_type4()

    def solve_type1(self):
        """Solution for Type 1"""
        return {
            'T': self.T1,
            'T_sq': self.T1 ** 2,
            'T_times_2': self.T1 * 2,
            'S': self.S1,
            'answer': self.v0_1
        }

    def solve_type2(self):
        """Solution for Type 2"""
        return {
            'b': self.b2,
            'v_final': self.v_final2,
            'T': self.T2,
            'T_sq': self.T2 ** 2,
            'T_cubed': self.T2 ** 3,
            'answer': to_latex_num_display(self.S2)
        }

    def solve_type3(self):
        """Solution for Type 3"""
        return {
            'a': self.a3,
            'v0': self.v0_3,
            'T': self.T3,
            'T_sq': self.T3 ** 2,
            'answer': self.S3
        }

    def solve_type4(self):
        """Solution for Type 4"""
        T_minus_k = self.T4 - self.k4
        S_at_T = Fraction(-self.a4 * self.T4 ** 2, 2) + self.v0_4 * self.T4
        S_at_T_minus_k = Fraction(-self.a4 * T_minus_k ** 2, 2) + self.v0_4 * T_minus_k
        return {
            'a': self.a4,
            'v0': self.v0_4,
            'T': self.T4,
            'T_sq': self.T4 ** 2,
            'k': self.k4,
            'T_minus_k': T_minus_k,
            'T_minus_k_sq': T_minus_k ** 2,
            'S_at_T': to_latex_num_display(S_at_T),
            'S_at_T_minus_k': to_latex_num_display(S_at_T_minus_k),
            'answer': self.S4
        }

    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        
        if self.problem_type == 1:
            sol_data = self.solve_type1()
            solution = TEMPLATE_SOL1.substitute(sol_data)
            params = {
                'idx': idx,
                'T': self.T1,
                'S': self.S1,
                'answer': self.v0_1,
                'answer_display': format_answer_display(self.v0_1),
                'solution': solution
            }
            return TEMPLATE_Q1.substitute(params)
        elif self.problem_type == 2:
            sol_data = self.solve_type2()
            solution = TEMPLATE_SOL2.substitute(sol_data)
            params = {
                'idx': idx,
                'b': self.b2,
                'v_final': self.v_final2,
                'answer': to_latex_num_display(self.S2),
                'answer_display': format_answer_display(self.S2),
                'solution': solution
            }
            return TEMPLATE_Q2.substitute(params)
        elif self.problem_type == 3:
            sol_data = self.solve_type3()
            solution = TEMPLATE_SOL3.substitute(sol_data)
            params = {
                'idx': idx,
                'a': self.a3,
                'v0': self.v0_3,
                'answer': self.S3,
                'answer_display': format_answer_display(self.S3),
                'solution': solution
            }
            return TEMPLATE_Q3.substitute(params)
        else:
            sol_data = self.solve_type4()
            solution = TEMPLATE_SOL4.substitute(sol_data)
            params = {
                'idx': idx,
                'a': self.a4,
                'v0': self.v0_4,
                'k': self.k4,
                'answer': self.S4,
                'answer_display': format_answer_display(self.S4),
                'solution': solution
            }
            return TEMPLATE_Q4.substitute(params)


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
        q = VariableMotionQuestion()
        questions.append(q.generate_question(i + 1))
    
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "bai_toan_chuyen_dong_bien_doi.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong bai_toan_chuyen_dong_bien_doi.tex")


if __name__ == "__main__":
    main()

