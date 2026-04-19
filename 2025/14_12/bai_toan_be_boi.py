
import math
import random
import sys
import os
from string import Template
from fractions import Fraction

# ==================== CONFIGURATION & HELPERS ====================

def to_latex_num(value):
    """Format number to LaTeX string, using fractions if appropriate"""
    # Handle Fraction type directly
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
        
        # Check if it's close to an integer
        if abs(value - round(value)) < 1e-9:
            return str(round(value))
            
        # Try fraction
        f = Fraction(value).limit_denominator(100)
        # If the error is small, accept it
        if abs(float(f) - value) < 1e-9:
            if f.denominator == 1:
                return str(f.numerator)
            # Handle negative sign for fraction
            if f.numerator < 0:
                 return f"-\\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"
            return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"
            
    return format_vn_number(value)

def format_vn_number(value, precision=2):
    """Format number for Vietnamese locale (comma as decimal separator)"""


def coeff_latex(value, var):
    """Format coefficient before variable: 1x -> x, -1x -> -x, 2x -> 2x"""
    if isinstance(value, Fraction):
        if value == 1:
            return var
        if value == -1:
            return f"-{var}"
        return f"{to_latex_num(value)}{var}"
    if value == 1:
        return var
    if value == -1:
        return f"-{var}"
    return f"{to_latex_num(value)}{var}"
    if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
        return str(int(value))
    s = f"{value:.{precision}f}"
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s.replace('.', ',')

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
\begin{document}
""" + content + r"\end{document}"

# ==================== TEMPLATES ====================

TEMPLATE_Q = Template(
    r"""
Câu ${idx}: Một bể bơi hình trụ có đường kính $$${d_val}$$ m và chiều cao $$${h_val}$$ m; bể được bơm nước vào với tốc độ không đổi. Sau khi nước được bơm đầy, bể bơi bị thủng một lỗ ở đáy và nước chảy ra ngoài; bể bơi chảy hết nước trong ${T_val} giờ. Biết tốc độ giảm chiều cao của bể bơi khi nước chảy ra ngoài vào thời điểm $$t$$ giờ (tính từ lúc nước đầy bể và ngừng bơm) được cho bởi hàm số $$h'(t) = at + b$$, với $$a, b \in \mathbb{R}$$. Lúc nước chảy hết ra ngoài thì tốc độ giảm chiều cao bằng 0.
\begin{center}
\begin{tikzpicture}[scale=0.8]
    % Tank body - dark gray
    \fill[gray!60] (-2.5,0) -- (-2.5,2.5) arc (180:360:2.5 and 0.5) -- (2.5,0) arc (0:-180:2.5 and 0.5);
    \fill[gray!50] (0,2.5) ellipse (2.5 and 0.5);
    
    % Water inside - cyan
    \fill[cyan!50, opacity=0.7] (-2.5,0) -- (-2.5,1.8) arc (180:360:2.5 and 0.5) -- (2.5,0) arc (0:-180:2.5 and 0.5);
    \fill[cyan!40, opacity=0.8] (0,1.8) ellipse (2.5 and 0.5);
    
    % Tank outline
    \draw[thick, gray!80] (0,0) ellipse (2.5 and 0.5);
    \draw[thick, gray!80] (0,2.5) ellipse (2.5 and 0.5);
    \draw[thick, gray!80] (-2.5,0) -- (-2.5,2.5);
    \draw[thick, gray!80] (2.5,0) -- (2.5,2.5);
    
    % Leak hole at bottom side
    \fill[black] (2.3, 0.15) circle (0.08);
    
    % Water leaking out - curved stream
    \draw[cyan!70, thick, line width=1.5pt] (2.38, 0.15) .. controls (2.8, 0.1) and (3.0, -0.2) .. (3.2, -0.5);
    \draw[cyan!70, thick, line width=1.2pt] (2.38, 0.12) .. controls (2.7, 0.0) and (2.9, -0.3) .. (3.1, -0.6);
    \fill[cyan!50, opacity=0.6] (3.0, -0.6) ellipse (0.3 and 0.1);
    
    % Water drops
    \fill[cyan!60] (2.9, -0.3) circle (0.04);
    \fill[cyan!60] (3.05, -0.45) circle (0.03);
    \fill[cyan!60] (2.95, -0.5) circle (0.035);
    
    % Dimension arrows
    \draw[<->, thick] (3.5, 0) -- (3.5, 2.5) node[midway, right] {$$${h_val}$$m};
    \draw[<->, thick] (-2.5, -1.2) -- (2.5, -1.2) node[midway, below] {$$${d_val}$$m};
    
    % Water level label
    \node at (0, 0.9) {$$h(t)$$};
    \draw[<->, thick] (2.7, 0) -- (2.7, 1.8);
\end{tikzpicture}
\end{center}
Các mệnh đề sau đúng hay sai?
${label_a}) Thể tích của bể bơi sau khi nước được làm đầy là $$${prop_a_val}$$ $$m^3$$.\\
${label_b}) $$${prop_b_eq1}$$ và $$${prop_b_eq2}$$.\\
${label_c}) Sau ${t_c} giờ kể từ lúc bể bị rò, lượng nước bị mất đi bằng $$${prop_c_val}$$ $$m^3$$.\\
${label_d}) Lượng nước bị rò rỉ ra ngoài một nửa sau $$${prop_d_val}$$ giờ.
"""
)

TEMPLATE_SOL = Template(
    r"""
Lời giải:\\
a) Mệnh đề ${res_a_text}.\\
Bể nước hình trụ có bán kính đáy $$r = ${r_val}$$ m, chiều cao $$h = ${h_val}$$ m.\\
Thể tích khi đầy $$V = \pi r^2 h = \pi \cdot ${r_val}^2 \cdot ${h_val} = ${vol_full}$$ $$m^3$$.\\
b) Mệnh đề ${res_b_text}.\\
Ta có $$h'(${T_val}) = 0 \Rightarrow ${T_val}a + b = 0$$ (1).\\
Vì $$\begin{cases} h(0) = ${h_val} \\ h(${T_val}) = 0 \end{cases} \Rightarrow \begin{cases} c = ${h_val} \\ ${half_T_sq}a + ${T_val}b + ${h_val} = 0 \end{cases}$$ (2).\\
Từ (1) và (2) suy ra $$a = ${a_val}, b = ${b_val}$$. Khi đó $$${prop_b_eq1_true}$$ và $$${prop_b_eq2_true}$$.\\
c) Mệnh đề ${res_c_text}.\\
Chiều cao mực nước trong bể sau ${t_c} giờ là: $$h(${t_c}) = ${h_tc}$$ m.\\
Lượng nước còn lại trong bể sau ${t_c} giờ là $$\pi \cdot ${r_val}^2 \cdot ${h_tc} = ${vol_rem_c}$$ $$m^3$$.\\
Lượng nước đã thoát ra sau ${t_c} giờ là $$${vol_full} - ${vol_rem_c} = ${vol_lost_c}$$ $$m^3$$.\\
d) Mệnh đề ${res_d_text}.\\
Lượng nước còn lại khi đã mất một nửa là $$\frac{${vol_full}}{2} = ${vol_half}$$ $$m^3$$.\\
Chiều cao tương ứng $$h(t_1) = ${h_half}$$ m.\\
Giải phương trình $$h(t_1) = ${h_half}$$ ta được $$t_1 = ${time_half}$$ (giờ) thỏa mãn $$0 < t_1 < ${T_val}$$.
"""
)

# ==================== MAIN CLASS ====================

class SwimmingPoolQuestion:
    def __init__(self):
        self.r = 0
        self.h_max = 0
        self.T = 0
        self.a = 0
        self.b = 0
        
        # Props
        self.res_a = True
        self.res_b = True
        self.res_c = True
        self.res_d = True
        
        self.prop_a_val = ""
        self.prop_b_eq1 = ""
        self.prop_b_eq2 = ""
        self.prop_b_eq1_true = ""
        self.prop_b_eq2_true = ""
        self.prop_c_val = ""
        self.prop_d_val = ""
        self.prop_b_check = ""

    def generate_parameters(self):
        """
        Generate parameters ensuring nice results:
        - d (diameter), h (height), T (time) are natural numbers
        - a = 2h/T^2 and b = -2h/T should be nice fractions
        
        Strategy: Use pre-computed nice (h, T) combinations
                  Pick r (radius) as integer from 1-5
        """
        # Pre-computed nice combinations where coeff_a = T^2/(2h) is reasonable
        # Format: (h, T) where a = 2h/T^2, b = -2h/T
        nice_combinations = [
            # T=4: T^2=16, 2h/T^2 = h/8, coeff_a = 8/h
            (1, 4),   # a=1/8, b=-1/2, coeff_a=8, coeff_b=2
            (2, 4),   # a=1/4, b=-1, coeff_a=4, coeff_b=1
            (4, 4),   # a=1/2, b=-2, coeff_a=2, coeff_b=1/2
            
            # T=6: T^2=36, coeff_a = 18/h
            (2, 6),   # a=1/9, b=-2/3, coeff_a=9, coeff_b=3/2
            (3, 6),   # a=1/6, b=-1, coeff_a=6, coeff_b=1
            
            # T=8: T^2=64, coeff_a = 32/h
            (2, 8),   # a=1/16, b=-1/2, coeff_a=16, coeff_b=2
            (4, 8),   # a=1/8, b=-1, coeff_a=8, coeff_b=1
            
            # T=10: T^2=100, coeff_a = 50/h
            (2, 10),  # a=1/25, b=-2/5, coeff_a=25, coeff_b=5/2
            (5, 10),  # a=1/10, b=-1, coeff_a=10, coeff_b=1
            
            # T=12: T^2=144, coeff_a = 72/h
            (3, 12),  # a=1/24, b=-1/2, coeff_a=24, coeff_b=2
            (4, 12),  # a=1/18, b=-2/3, coeff_a=18, coeff_b=3/2
        ]
        
        h, T = random.choice(nice_combinations)
        self.h_max = h
        self.T = T
        
        # r (radius): integer from 1 to 5
        self.r = random.randint(1, 5)
        
        # Calculate a, b using Fraction for exact arithmetic
        # a = 2h/T^2, b = -2h/T
        self.a = Fraction(2 * self.h_max, self.T**2)
        self.b = Fraction(-2 * self.h_max, self.T)

    def solve(self):
        # a) Volume full: V = pi * r^2 * h
        vol_full_coeff = Fraction(self.r**2 * self.h_max)
        
        # c) Volume lost after t_c
        # h(t) = h * (1 - t/T)^2 = h * ((T-t)/T)^2
        # For nice result, we want (T-t_c)/T to be a simple fraction
        # This means t_c = T * (1 - k/n) where k/n is simple like 1/2, 1/3, 2/3, 3/4
        # Or equivalently: t_c = T * m/n where m/n is simple
        
        # Nice ratios: t_c/T in {1/2, 1/3, 1/4, 2/3, 3/4}
        # => (T-t_c)/T in {1/2, 2/3, 3/4, 1/3, 1/4}
        # For t_c to be integer: T must be divisible by denominator
        nice_ratios = [(1, 2), (1, 3), (1, 4), (2, 3), (3, 4)]
        possible_tc = []
        for num, den in nice_ratios:
            if self.T % den == 0:
                t_c_val = self.T * num // den
                if 1 <= t_c_val < self.T:
                    possible_tc.append(t_c_val)
        
        if not possible_tc:
            possible_tc = [self.T // 2] if self.T % 2 == 0 else [1]
        
        t_c = random.choice(possible_tc)
        
        # h(t) = h * (1 - t/T)^2 = h * ((T-t)/T)^2
        ratio = Fraction(self.T - t_c, self.T)
        h_tc_frac = Fraction(self.h_max) * ratio * ratio
        
        vol_rem_coeff = h_tc_frac * Fraction(self.r**2)
        vol_lost_coeff = vol_full_coeff - vol_rem_coeff
        
        # d) Time half
        # h(t_half) = h/2 => (1 - t/T)^2 = 1/2 => t = T(1 - 1/sqrt(2)) = T - T/sqrt(2)
        # Rationalize: t = T - (T*sqrt(2))/2
        # The image format: 8 - 4\sqrt{2}.
        # General: T - (T/2)\sqrt{2}.
        t_half_coeff = self.T // 2  # This is T/2
        if self.T % 2 == 0:
            t_half_str = f"{self.T} - {t_half_coeff}\\sqrt{{2}}"
        else:
            t_half_str = f"{self.T} - \\frac{{{self.T}}}{{2}}\\sqrt{{2}}"
             
        return {
            'vol_full_coeff': vol_full_coeff,
            't_c': t_c,
            'h_tc_frac': h_tc_frac,
            'vol_lost_coeff': vol_lost_coeff,
            'vol_rem_coeff': vol_rem_coeff,
            't_half_str': t_half_str
        }

    def distort_and_set_props(self, sol_data):
        # A: Volume
        if random.random() < 0.5:
            self.res_a = True
            self.prop_a_val = f"{to_latex_num(sol_data['vol_full_coeff'])}\\pi"
        else:
            self.res_a = False
            fake = sol_data['vol_full_coeff'] * Fraction(random.choice([2, 3, Fraction(1,2)])).limit_denominator()
            self.prop_a_val = f"{to_latex_num(fake)}\\pi"
            
        # B: Relation - Format like image: "32a + 1 = 0" and "4b - 1 = 0"
        # True: a = 2h/T^2 => (T^2/(2h)) * a = 1 => coeff_a * a - 1 = 0
        # But image uses format: coeff*a + sign = 0
        # a = 2h/T^2, so 1/a = T^2/(2h). We want X*a + Y = 0 => X = -Y/a = -Y*T^2/(2h)
        # If Y = 1: X = -T^2/(2h). So: (-T^2/(2h))a + 1 = 0 => T^2/(2h) * a - 1 = 0
        # Image format: 32a + 1 = 0 means a = -1/32. But our a > 0.
        # Let's use: (T^2/2h)a - 1 = 0 format
        coeff_a = Fraction(self.T**2) / Fraction(2 * self.h_max).limit_denominator()
        coeff_b = Fraction(self.T) / Fraction(2 * self.h_max).limit_denominator()
        
        # True equations - use coeff_latex to handle coefficient 1 correctly
        self.prop_b_eq1_true = f"{coeff_latex(coeff_a, 'a')} - 1 = 0"
        self.prop_b_eq2_true = f"{coeff_latex(coeff_b, 'b')} + 1 = 0"
        
        if random.random() < 0.5:
            self.res_b = True
            self.prop_b_eq1 = self.prop_b_eq1_true
            self.prop_b_eq2 = self.prop_b_eq2_true
            self.prop_b_check = "Mệnh đề đúng"
        else:
            self.res_b = False
            # Distort one of the equations - only change coefficient, keep signs
            if random.random() < 0.5:
                fake_coeff = coeff_a + random.choice([1, -1, 2])
                self.prop_b_eq1 = f"{coeff_latex(fake_coeff, 'a')} - 1 = 0"
                self.prop_b_eq2 = self.prop_b_eq2_true
            else:
                self.prop_b_eq1 = self.prop_b_eq1_true
                fake_coeff = coeff_b + random.choice([1, -1, 2])
                self.prop_b_eq2 = f"{coeff_latex(fake_coeff, 'b')} + 1 = 0"
            self.prop_b_check = "Mệnh đề sai"
            
        # C: Volume lost
        if random.random() < 0.5:
            self.res_c = True
            self.prop_c_val = f"{to_latex_num(sol_data['vol_lost_coeff'])}\\pi"
        else:
            self.res_c = False
            fake = sol_data['vol_lost_coeff'] + random.choice([1, 2, Fraction(1,2)])
            self.prop_c_val = f"{to_latex_num(fake)}\\pi"
            
        # D: Time half
        if random.random() < 0.5:
            self.res_d = True
            self.prop_d_val = sol_data['t_half_str']
        else:
            self.res_d = False
            # Distort: different coefficient or different sqrt
            if random.random() < 0.5:
                # Wrong sqrt
                if self.T % 2 == 0:
                    self.prop_d_val = f"{self.T} - {to_latex_num(self.T/2)}\\sqrt{{3}}"
                else:
                    self.prop_d_val = f"{self.T} - \\frac{{{self.T}}}{{2}}\\sqrt{{3}}"
            else:
                # Wrong coefficient (use T+2 or T-2 instead)
                fake_T = self.T + random.choice([2, -2, 4])
                if fake_T % 2 == 0:
                    self.prop_d_val = f"{fake_T} - {to_latex_num(fake_T/2)}\\sqrt{{2}}"
                else:
                    self.prop_d_val = f"{fake_T} - \\frac{{{fake_T}}}{{2}}\\sqrt{{2}}"

    @staticmethod
    def label_with_star(letter: str, is_true: bool) -> str:
        return f"*{letter}" if is_true else f"{letter}"

    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        sol_data = self.solve()
        self.distort_and_set_props(sol_data)
        
        params = {
            'idx': idx,
            'd_val': to_latex_num(self.r * 2),
            'r_val': to_latex_num(self.r),
            'h_val': to_latex_num(self.h_max),
            'T_val': self.T,
            'half_T_sq': to_latex_num(Fraction(self.T**2, 2)),
            
            'label_a': self.label_with_star('a', self.res_a),
            'label_b': self.label_with_star('b', self.res_b),
            'label_c': self.label_with_star('c', self.res_c),
            'label_d': self.label_with_star('d', self.res_d),
            
            'res_a_text': "đúng" if self.res_a else "sai",
            'res_b_text': "đúng" if self.res_b else "sai",
            'res_c_text': "đúng" if self.res_c else "sai",
            'res_d_text': "đúng" if self.res_d else "sai",
            
            'prop_a_val': self.prop_a_val,
            'prop_b_eq1': self.prop_b_eq1,
            'prop_b_eq2': self.prop_b_eq2,
            'prop_b_eq1_true': self.prop_b_eq1_true,
            'prop_b_eq2_true': self.prop_b_eq2_true,
            'prop_c_val': self.prop_c_val,
            'prop_d_val': self.prop_d_val,
            
            't_c': sol_data['t_c'],
            
            # Solution
            'vol_full': f"{to_latex_num(sol_data['vol_full_coeff'])}\\pi",
            'a_val': to_latex_num(self.a),
            'b_val': to_latex_num(self.b),
            'prop_b_check': self.prop_b_check,
            'h_tc': to_latex_num(sol_data['h_tc_frac']),
            'vol_rem_c': f"{to_latex_num(sol_data['vol_rem_coeff'])}\\pi",
            'vol_lost_c': f"{to_latex_num(sol_data['vol_lost_coeff'])}\\pi",
            'vol_half': f"{to_latex_num(sol_data['vol_full_coeff']/2)}\\pi",
            'h_half': to_latex_num(self.h_max/2),
            'time_half': sol_data['t_half_str']
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
        q = SwimmingPoolQuestion()
        questions.append(q.generate_question(i + 1))
        
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "bai_toan_be_boi.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong bai_toan_be_boi.tex")

if __name__ == "__main__":
    main()

