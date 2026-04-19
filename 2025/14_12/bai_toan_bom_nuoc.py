
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

# ==================== TEMPLATES ====================

TEMPLATE_Q = Template(
    r"""
Câu ${idx}: Thể tích nước của một bể bơi sau $$t$$ phút bơm tính theo công thức $$V(t) = \frac{1}{${K}}\left(${A}t^3 - \frac{t^4}{${B}}\right)$$ (lít) với $$\left(0 \le t \le ${T_max}\right)$$. Tốc độ bơm nước tại thời điểm $$t$$ được tính bởi công thức $$f(t) = V'(t)$$.

Các mệnh đề sau đúng hay sai?
${label_a}) Thể tích nước của bể bơi sau ${t_a} phút bơm là ${prop_a_val} lít.\\
${label_b}) Tốc độ bơm nước tại thời điểm $$t$$ là $$f(t) = ${prop_b_formula}$$.\\
${label_c}) Tốc độ bơm giảm từ phút thứ ${t_c1} đến phút thứ ${t_c2}.\\
${label_d}) ${prop_d_stmt}
"""
)

TEMPLATE_SOL = Template(
    r"""
Lời giải:\\
a) ${res_a_text}: $$V(${t_a}) = \frac{1}{${K}}\left(${A} \cdot ${t_a}^3 - \frac{${t_a}^4}{${B}}\right) = ${V_a_result}$$.\\
b) ${res_b_text}: $$V'(t) = \frac{1}{${K}}\left(${A3}t^2 - \frac{4}{${B}}t^3\right) \Rightarrow f(t) = \frac{1}{${K}}\left(${A3}t^2 - \frac{4}{${B}}t^3\right)$$.\\
c) ${res_c_text}: $$V''(t) = \frac{1}{${K}}\left(${A6}t - \frac{12}{${B}}t^2\right) \Leftrightarrow V''(t) = 0 \Leftrightarrow \left[\begin{array}{l} t = ${t_max_speed} \\ t = 0 \end{array}\right.$$

Bảng biến thiên của hàm số:

\begin{tikzpicture}
\tkzTabInit[lgt=2,espcl=2]{$$t$$ / 0.6, $$V''(t)$$ / 0.6, $$V'(t)$$ / 1.2}{$$0$$, $$${t_max_speed}$$, $$${T_max}$$}
\tkzTabLine{, +, z, -, }
\tkzTabVar{-/ $$0$$, +/ $$${f_max}$$, -/ $$0$$}
\end{tikzpicture}

Suy ra tốc độ bơm giảm từ phút thứ ${t_max_speed} đến phút thứ ${T_max}.\\
d) ${res_d_text}: ${sol_d_stmt}.\\
"""
)

# ==================== MAIN CLASS ====================

class WaterPumpQuestion:
    def __init__(self):
        # Parameters for V(t) = (1/K) * (A*t^3 - t^4/B)
        self.A = 0
        self.K = 0
        self.B = 0
        self.T_max = 0  # T_max = 3A (when V'(t) = 0 again)
        self.t_max_speed = 0  # When V''(t) = 0, t = 2A
        self.f_max = 0
        
        # Props
        self.res_a = True
        self.res_b = True
        self.res_c = True
        self.res_d = True
        
        self.prop_a_val = ""
        self.prop_b_formula = ""
        self.prop_d_val = ""  # used when d-variant asks for time
        self.t_c1 = 0
        self.t_c2 = 0
        # Variant for proposition d: 'time' or 'value'
        self.d_variant = 'time'

    def generate_parameters(self):
        """
        Generate parameters for V(t) = (1/K)(A*t^3 - t^4/B)
        V'(t) = (1/K)\big(3A*t^2 - (4/B)*t^3\big) = (t^2/K)\big(3A - (4/B)t\big)
        V'(t) = 0 when t = 0 or t = 3AB/4
        V''(t) = (1/K)\big(6A*t - (12/B)*t^2\big) = (6t/K)\big(A - (2/B)t\big)
        V''(t) = 0 when t = 0 or t = AB/2
        Max speed at t = AB/2
        
        For nice results:
        - A should be chosen such that V(t_a), V'(t), etc. are nice integers
        - K divides nicely into calculations
        - t_a should be a multiple of B (for t^4/B term)
        
        ~30 values for each parameter:
        - A: multiples of 10 from 10 to 100 (10 values)
        - B: {2, 4, 8} (3 values)
        - K: {50, 100, 200} (3 values)
        - Combined: ~90 nice combinations
        """
        # A: multiples of 10 from 10 to 100 (~10 values)
        # This gives T_max = 3A from 30 to 300
        # t_max_speed = 2A from 20 to 200
        self.A = random.choice(list(range(10, 110, 10)))  # 10, 20, 30, ..., 100
        
        # B: choose from small even numbers for clean fractions
        self.B = random.choice([2, 4, 8])

        # K: choose from values that divide nicely
        # With general B, f_max = A^3 B^2/(4K); choose K from a small nice set
        self.K = random.choice([50, 100, 200])
        
        # Domain [0, 3AB/4]
        self.T_max = (3 * self.A * self.B) // 4
        self.t_max_speed = (self.A * self.B) // 2  # Max of V'(t)
        
        # f(t_max) = V'(AB/2) = (1/K)*(A^3 B^2 / 4)
        self.f_max = (self.A**3 * self.B**2) // (4 * self.K)

    def solve(self):
        # a) Volume at specific time t_a
        # V(t) = (1/K)(A*t^3 - t^4/B)
        # For t^4/B to be integer, t should be multiple of B
        # For nice results, t_a should be multiple of lcm(10, B) and <= T_max
        
        # lcm helper
        def _gcd(x, y):
            while y:
                x, y = y, x % y
            return x
        def _lcm(x, y):
            return x // _gcd(x, y) * y

        step = _lcm(10, self.B)

        # Generate ~10-15 possible t_a values based on A and B
        possible_ta = [t for t in range(step, self.T_max, step) if t <= self.T_max - step]
        if not possible_ta:
            possible_ta = [step]
        
        t_a = random.choice(possible_ta[:15])  # Limit to first 15 choices
        
        # V(t_a) = (1/K)(A*t_a^3 - t_a^4/B)
        # Ensure integer result
        numerator = self.A * t_a**3 - t_a**4 // self.B
        V_a = numerator // self.K
        
        return {
            't_a': t_a,
            'V_a': V_a,
            'A3': 3 * self.A,  # 3A coefficient
            'A6': 6 * self.A,  # 6A coefficient
        }

    def distort_and_set_props(self, sol_data):
        t_a = sol_data['t_a']
        V_a = sol_data['V_a']
        
        # A: Volume at t_a
        if random.random() < 0.5:
            self.res_a = True
            self.prop_a_val = str(V_a)
        else:
            self.res_a = False
            fake = V_a + random.choice([100, -100, 500, -500])
            self.prop_a_val = str(fake)
        
        # B: Formula for f(t)
        # True: f(t) = (1/K)(3A*t^2 - (4/B)*t^3)
        A3 = sol_data['A3']
        if random.random() < 0.5:
            self.res_b = True
            self.prop_b_formula = f"\\frac{{1}}{{{self.K}}}\\left({A3}t^2 - \\frac{{4}}{{{self.B}}}t^3\\right)"
        else:
            self.res_b = False
            # Wrong formula - tweak coefficient or omit factor B
            fake_coeff = A3 + random.choice([10, -10, 30])
            # two types of wrong: missing 1/K or wrong 4/B factor
            if random.random() < 0.5:
                self.prop_b_formula = f"{fake_coeff}t^2 - t^3"
            else:
                self.prop_b_formula = f"\\frac{{1}}{{{self.K}}}\\left({fake_coeff}t^2 - 4t^3\\right)"
        
        # C: Speed decreases from t_c1 to t_c2
        # True: decreases from t_max_speed (2A) to T_max (3A)
        if random.random() < 0.5:
            self.res_c = True
            self.t_c1 = self.t_max_speed
            self.t_c2 = self.T_max
        else:
            self.res_c = False
            # Wrong interval - say it decreases before the maximum
            self.t_c1 = self.t_max_speed - 20
            self.t_c2 = self.T_max
        
        # D: Randomize between asking for time of max speed or the max speed value
        self.d_variant = random.choice(['time', 'value'])
        if self.d_variant == 'time':
            # Statement about time of maximum speed
            if random.random() < 0.5:
                self.res_d = True
                self.prop_d_val = str(self.t_max_speed)
            else:
                self.res_d = False
                fake_t = self.t_max_speed + random.choice([10, -10, 20])
                self.prop_d_val = str(fake_t)
        else:
            # Statement about the maximum speed value (liters per minute)
            if random.random() < 0.5:
                self.res_d = True
                # use true f_max
                self.prop_d_val = str(self.f_max)
            else:
                self.res_d = False
                fake_f = self.f_max + random.choice([50, -50, 100, -100])
                self.prop_d_val = str(fake_f)

    @staticmethod
    def label_with_star(letter: str, is_true: bool) -> str:
        return f"*{letter}" if is_true else f"{letter}"

    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        sol_data = self.solve()
        self.distort_and_set_props(sol_data)
        
        # Prepare proposition d text depending on variant (use inline math to avoid unwanted line breaks)
        if self.d_variant == 'time':
            prop_d_stmt = f"Tốc độ bơm lớn nhất tại thời điểm $t = {self.prop_d_val}$ phút."
            sol_d_stmt = f"Từ bảng biến thiên ta có tốc độ lớn nhất khi $t = {self.t_max_speed}$ phút"
        else:
            prop_d_stmt = f"Tốc độ bơm lớn nhất bằng ${self.prop_d_val}$ lít/phút."
            sol_d_stmt = f"Từ bảng biến thiên ta có tốc độ lớn nhất bằng ${self.f_max}$ lít/phút"

        params = {
            'idx': idx,
            'K': self.K,
            'A': self.A,
            'B': self.B,
            'T_max': self.T_max,
            
            'label_a': self.label_with_star('a', self.res_a),
            'label_b': self.label_with_star('b', self.res_b),
            'label_c': self.label_with_star('c', self.res_c),
            'label_d': self.label_with_star('d', self.res_d),
            
            'res_a_text': "Đúng" if self.res_a else "Sai",
            'res_b_text': "Đúng" if self.res_b else "Sai",
            'res_c_text': "Đúng" if self.res_c else "Sai",
            'res_d_text': "Đúng" if self.res_d else "Sai",
            
            't_a': sol_data['t_a'],
            'prop_a_val': self.prop_a_val,
            'V_a_result': sol_data['V_a'],
            
            'prop_b_formula': self.prop_b_formula,
            'A3': sol_data['A3'],
            'A6': sol_data['A6'],
            
            't_c1': self.t_c1,
            't_c2': self.t_c2,
            't_max_speed': self.t_max_speed,
            
            'prop_d_val': self.prop_d_val,
            'prop_d_stmt': prop_d_stmt,
            'sol_d_stmt': sol_d_stmt,
            'f_max': self.f_max,
        }
        
        question = TEMPLATE_Q.substitute(params)
        solution = TEMPLATE_SOL.substitute(params)
        
        return f"{question}\n{solution}"

# ==================== MAIN ====================

def main():
    num_questions = 5
    if len(sys.argv) > 1:
        try:
            num_questions = max(1, int(sys.argv[1]))
        except ValueError:
            print("Tham số không hợp lệ, sử dụng mặc định 5 câu hỏi.")
    
    questions = []
    for i in range(num_questions):
        q = WaterPumpQuestion()
        questions.append(q.generate_question(i + 1))
        
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "bai_toan_bom_nuoc.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong bai_toan_bom_nuoc.tex")

if __name__ == "__main__":
    main()
