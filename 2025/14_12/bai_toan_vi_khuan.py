import random
import sys
import os
import math
from string import Template

# ==================== CONFIGURATION & HELPERS ====================

def to_latex_num(value):
    """Format number to LaTeX string"""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(round(value))
    return str(value)


def format_coeff(value, first=False):
    """Format coefficient for display: hide 1, show -1 as -, etc."""
    if value == 1:
        return "" if first else "+"
    if value == -1:
        return "-"
    if value > 0:
        return f"+{value}" if not first else str(value)
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
\begin{document}
""" + content + r"\end{document}"

# ==================== TEMPLATES ====================

TEMPLATE_Q = Template(
    r"""
Câu ${idx}: Một quần thể vi khuẩn A có số lượng cá thể là $$P(t)$$ sau $$t$$ phút quan sát được phát hiện thay đổi với tốc độ là: $$P'(t) = a \cdot e^{${k1}t} + ${b} \cdot e^{${k2}t}$$ (vi khuẩn/phút) $$(a \in \mathbb{R})$$. Biết rằng lúc bắt đầu quan sát, quần thể có ${P0} vi khuẩn và đạt tốc độ tăng trưởng là ${P0_prime} vi khuẩn/phút.

Các mệnh đề sau đúng hay sai?
${label_a}) Giá trị của $$a = ${prop_a_val}$$.\\
${label_b}) $$P(t) = ${prop_b_formula}$$.\\
${label_c}) Sau ${t1} phút số lượng vi khuẩn trong quần thể là ${prop_c_val} con (làm tròn kết quả đến hàng đơn vị).\\
${label_d}) Sau ${t1} phút, một quần thể vi khuẩn B có tốc độ tăng trưởng là $$G'(t) = ${M} \cdot e^{${k3}t}$$ (vi khuẩn/phút) bắt đầu cạnh tranh nguồn thức ăn trực tiếp với quần thể A. Một cá thể tại quần thể B triệt tiêu một cá thể tại quần thể A. Sau ${t2} phút cạnh tranh quần thể A bị triệt tiêu hoàn toàn. Số lượng vi khuẩn của quần thể B ở thời điểm bắt đầu cạnh tranh là ${prop_d_val} con (làm tròn kết quả đến hàng đơn vị).
"""
)

TEMPLATE_SOL = Template(
    r"""
Lời giải\\
a) ${res_a_text}: $$P'(0) = a + ${b} = ${P0_prime} \Leftrightarrow a = ${a_true}$$.\\
b) ${res_b_text}: $$P(t) = \int P'(t) \, dt = ${a_over_k1} \cdot e^{${k1}t} ${b_over_k2_sign} ${b_over_k2_abs} \cdot e^{${k2}t} + C$$ mà $$P(0) = ${P0}$$ nên $$C = ${C_val}$$.

Vậy hàm số cần tìm là $$P(t) = ${P_formula_true}$$.\\
c) ${res_c_text}: $$P(${t1}) = ${a_over_k1} \cdot e^{${k1} \cdot ${t1}} ${b_over_k2_sign} ${b_over_k2_abs} \cdot e^{${k2} \cdot ${t1}} + ${C_val} \approx ${P_t1_true}$$.\\
d) ${res_d_text}: Sau ${t2} phút cạnh tranh thì quần thể A bị triệt tiêu hoàn toàn mà quần thể A quan sát trước quần thể B ${t1} phút nên số lượng quần thể A ở phút thứ ${t1_plus_t2} bằng số lượng quần thể B ở phút thứ ${t2}, tức là $$P(${t1_plus_t2}) = G(${t2})$$ (*).

Khi đó: $$P(${t1_plus_t2}) = ${a_over_k1} \cdot e^{${k1} \cdot ${t1_plus_t2}} ${b_over_k2_sign} ${b_over_k2_abs} \cdot e^{${k2} \cdot ${t1_plus_t2}} + ${C_val} \approx ${P_t1_t2_true}$$.

Mặt khác: $$G(t) = \int G'(t) \, dt = ${M_over_k3} \cdot e^{${k3}t} + K$$.

$$\Rightarrow G(${t2}) = ${M_over_k3} \cdot e^{${k3} \cdot ${t2}} + K \approx ${G_t2_value} + K$$.

Từ phương trình (*) ta có: $$P(${t1_plus_t2}) = G(${t2}) \Leftrightarrow ${P_t1_t2_true} = ${G_t2_value} + K \Rightarrow K \approx ${K_val}$$.

Vậy hàm $$G(t) = ${M_over_k3} \cdot e^{${k3}t} + ${K_val} \Rightarrow G(0) = ${M_over_k3} + ${K_val} = ${G0_true}$$.
"""
)

# ==================== MAIN CLASS ====================

class BacteriaQuestion:
    def __init__(self):
        # Parameters for P'(t) = a*e^(k1*t) + b*e^(k2*t)
        self.a = 0  # unknown to find
        self.b = 0  # given constant
        self.k1 = 0  # exponent coefficient 1
        self.k2 = 0  # exponent coefficient 2 (negative)
        self.P0 = 0  # P(0) initial population
        self.P0_prime = 0  # P'(0) initial growth rate
        
        # For population B
        self.M = 0  # coefficient in G'(t)
        self.k3 = 0  # exponent coefficient for G
        self.t1 = 0  # time for question c
        self.t2 = 0  # competition time
        
        # Props
        self.res_a = True
        self.res_b = True
        self.res_c = True
        self.res_d = True
        
        self.prop_a_val = ""
        self.prop_b_formula = ""
        self.prop_c_val = ""
        self.prop_d_val = ""

    def generate_parameters(self):
        """
        Generate parameters for bacteria growth problem.
        P'(t) = a*e^(k1*t) + b*e^(k2*t)
        P(t) = (a/k1)*e^(k1*t) + (b/k2)*e^(k2*t) + C
        
        Constraints:
        - P'(0) = a + b = given rate
        - P(0) = (a/k1) + (b/k2) + C = given population
        
        For nice results:
        - k1, k2 should divide a, b nicely
        
        ~30 values for each parameter type
        """
        # k1: positive exponent coefficients (~6 values)
        k1_choices = [0.05, 0.08, 0.1, 0.12, 0.15, 0.2]
        self.k1 = random.choice(k1_choices)
        
        # k2: negative exponent coefficients (~5 values)
        k2_choices = [-0.02, -0.03, -0.04, -0.05, -0.06]
        self.k2 = random.choice(k2_choices)
        
        # a/k1: coefficient after integration (~15 values)
        a_over_k1_choices = list(range(1000, 4000, 200))  # 1000, 1200, ..., 3800 (15 values)
        self.a_over_k1 = random.choice(a_over_k1_choices)
        self.a = round(self.a_over_k1 * self.k1)  # a = (a/k1) * k1
        
        # b/k2: coefficient after integration (~15 values, negative)
        b_over_k2_choices = list(range(-8000, -2000, 400))  # -8000, -7600, ..., -2400 (15 values)
        self.b_over_k2 = random.choice(b_over_k2_choices)
        self.b = round(self.b_over_k2 * self.k2)  # b = (b/k2) * k2, this makes b positive!
        
        # P'(0) = a + b
        self.P0_prime = self.a + self.b
        
        # P(0): initial population (~15 values)
        self.P0 = random.choice(list(range(150000, 300000, 10000)))  # 150000, 160000, ..., 290000
        
        # C = P(0) - (a/k1) - (b/k2)
        self.C = self.P0 - self.a_over_k1 - self.b_over_k2
        
        # t1: time for question c (~15 values)
        self.t1 = random.choice(list(range(8, 20)))  # 8, 9, ..., 19 (12 values)
        
        # t2: competition time (~8 values)
        self.t2 = random.choice(list(range(3, 10)))  # 3, 4, ..., 9 (7 values)
        
        # Population B parameters
        # G'(t) = M*e^(k3*t)
        # k3: (~6 values)
        k3_choices = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35]
        self.k3 = random.choice(k3_choices)
        
        # M/k3: coefficient after integration (~10 values)
        M_over_k3_choices = list(range(1500, 4000, 250))  # 1500, 1750, ..., 3750 (10 values)
        self.M_over_k3 = random.choice(M_over_k3_choices)
        self.M = round(self.M_over_k3 * self.k3)

    def solve(self):
        # a) Find a: P'(0) = a + b => a = P'(0) - b
        a_true = self.a
        
        # b) P(t) = (a/k1)*e^(k1*t) + (b/k2)*e^(k2*t) + C
        P_formula_true = f"{self.a_over_k1} \\cdot e^{{{self.k1}t}} {'+' if self.b_over_k2 > 0 else '-'} {abs(self.b_over_k2)} \\cdot e^{{{self.k2}t}} + {self.C}"
        
        # c) P(t1)
        P_t1_true = self.a_over_k1 * math.exp(self.k1 * self.t1) + self.b_over_k2 * math.exp(self.k2 * self.t1) + self.C
        P_t1_true = round(P_t1_true)
        
        # d) G(0) at start of competition
        # P(t1 + t2) = G(t2)
        t1_plus_t2 = self.t1 + self.t2
        P_t1_t2_true = self.a_over_k1 * math.exp(self.k1 * t1_plus_t2) + self.b_over_k2 * math.exp(self.k2 * t1_plus_t2) + self.C
        P_t1_t2_true = round(P_t1_t2_true)
        
        # G(t) = (M/k3)*e^(k3*t) + K
        # G(t2) = (M/k3)*e^(k3*t2) + K
        G_t2_value = round(self.M_over_k3 * math.exp(self.k3 * self.t2))
        
        # P(t1+t2) = G(t2)
        # P_t1_t2_true = G_t2_value + K
        K_val = P_t1_t2_true - G_t2_value
        
        # G(0) = (M/k3)*e^0 + K = M/k3 + K
        G0_true = self.M_over_k3 + K_val
        
        return {
            'a_true': a_true,
            'P_formula_true': P_formula_true,
            'P_t1_true': P_t1_true,
            'P_t1_t2_true': P_t1_t2_true,
            'G_t2_value': G_t2_value,
            'K_val': K_val,
            'G0_true': G0_true,
            't1_plus_t2': t1_plus_t2,
        }

    def distort_and_set_props(self, sol_data):
        # A: Value of a
        if random.random() < 0.5:
            self.res_a = True
            self.prop_a_val = str(sol_data['a_true'])
        else:
            self.res_a = False
            fake = sol_data['a_true'] + random.choice([10, -10, 50, -50])
            self.prop_a_val = str(fake)
        
        # B: Formula for P(t)
        if random.random() < 0.5:
            self.res_b = True
            self.prop_b_formula = sol_data['P_formula_true']
        else:
            self.res_b = False
            # Wrong formula - wrong coefficient or wrong C
            fake_C = self.C + random.choice([1000, -1000, 3000])
            self.prop_b_formula = f"{self.a_over_k1} \\cdot e^{{{self.k1}t}} {'+' if self.b_over_k2 > 0 else '-'} {abs(self.b_over_k2)} \\cdot e^{{{self.k2}t}} + {fake_C}"
        
        # C: P(t1)
        if random.random() < 0.5:
            self.res_c = True
            self.prop_c_val = str(sol_data['P_t1_true'])
        else:
            self.res_c = False
            fake = sol_data['P_t1_true'] + random.choice([100, -100, 500, -500])
            self.prop_c_val = str(fake)
        
        # D: G(0)
        if random.random() < 0.5:
            self.res_d = True
            self.prop_d_val = str(sol_data['G0_true'])
        else:
            self.res_d = False
            fake = sol_data['G0_true'] + random.choice([100, -100, 500, -500])
            self.prop_d_val = str(fake)

    @staticmethod
    def label_with_star(letter: str, is_true: bool) -> str:
        return f"*{letter}" if is_true else f"{letter}"

    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        sol_data = self.solve()
        self.distort_and_set_props(sol_data)
        
        b_over_k2_sign = "+" if self.b_over_k2 > 0 else "-"
        
        params = {
            'idx': idx,
            'k1': self.k1,
            'k2': self.k2,
            'b': self.b,
            'P0': self.P0,
            'P0_prime': self.P0_prime,
            't1': self.t1,
            't2': self.t2,
            'M': self.M,
            'k3': self.k3,
            
            'label_a': self.label_with_star('a', self.res_a),
            'label_b': self.label_with_star('b', self.res_b),
            'label_c': self.label_with_star('c', self.res_c),
            'label_d': self.label_with_star('d', self.res_d),
            
            'res_a_text': "Đúng" if self.res_a else "Sai",
            'res_b_text': "Đúng" if self.res_b else "Sai",
            'res_c_text': "Đúng" if self.res_c else "Sai",
            'res_d_text': "Đúng" if self.res_d else "Sai",
            
            'prop_a_val': self.prop_a_val,
            'prop_b_formula': self.prop_b_formula,
            'prop_c_val': self.prop_c_val,
            'prop_d_val': self.prop_d_val,
            
            'a_true': sol_data['a_true'],
            'a_over_k1': self.a_over_k1,
            'b_over_k2_sign': b_over_k2_sign,
            'b_over_k2_abs': abs(self.b_over_k2),
            'C_val': self.C,
            'P_formula_true': sol_data['P_formula_true'],
            'P_t1_true': sol_data['P_t1_true'],
            't1_plus_t2': sol_data['t1_plus_t2'],
            'P_t1_t2_true': sol_data['P_t1_t2_true'],
            'M_over_k3': self.M_over_k3,
            'G_t2_value': sol_data['G_t2_value'],
            'K_val': sol_data['K_val'],
            'G0_true': sol_data['G0_true'],
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
        q = BacteriaQuestion()
        questions.append(q.generate_question(i + 1))
        
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "bai_toan_vi_khuan.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong bai_toan_vi_khuan.tex")

if __name__ == "__main__":
    main()
