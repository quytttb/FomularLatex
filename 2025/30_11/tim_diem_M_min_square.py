import random
import math
import sys
from string import Template
from typing import Any, Dict, Tuple
import os
from fractions import Fraction

# ==================== CONFIGURATION & HELPERS ====================

def format_vn_number(value, precision=2):
    if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
        return str(int(value))
    s = f"{value:.{precision}f}"
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s

def format_answer(value, precision=2):
    """Format answer with both dot and comma versions if decimal"""
    if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
        return str(int(value))
    s = f"{value:.{precision}f}"
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    s_comma = s.replace('.', ',')
    return f"{s} | {s_comma}"

def format_coord(x, y, z):
    """Format tọa độ điểm"""
    return f"({x}; {y}; {z})"

def format_fraction(num, den):
    """Format phân số đẹp"""
    if den == 0:
        return "0"
    from math import gcd
    g = gcd(abs(int(num)), abs(int(den)))
    n, d = int(num) // g, int(den) // g
    if d < 0:
        n, d = -n, -d
    if d == 1:
        return str(n)
    return f"\\dfrac{{{n}}}{{{d}}}"

def format_sqrt(value):
    """Format căn bậc hai đẹp"""
    sqrt_val = math.sqrt(value)
    if sqrt_val == int(sqrt_val):
        return str(int(sqrt_val))
    
    factor_out = 1
    remaining = value
    for i in range(2, int(math.sqrt(value)) + 1):
        while remaining % (i * i) == 0:
            factor_out *= i
            remaining //= (i * i)
    
    if remaining == 1:
        return str(factor_out)
    elif factor_out == 1:
        return f"\\sqrt{{{value}}}"
    else:
        return f"{factor_out}\\sqrt{{{remaining}}}"

def gcd_list(lst):
    from math import gcd
    result = lst[0]
    for x in lst[1:]:
        result = gcd(result, x)
    return result

def create_latex_document(content):
    return r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage{tikz}
\usetikzlibrary{patterns, calc}
\begin{document}
""" + content + r"\end{document}"

# ==================== QUESTION TEMPLATES ====================

# Dạng bình phương: P = a*MA^2 + b*MB^2 + c*MC^2
TEMPLATE_Q = Template(
    r"""
Câu ${idx}. Cho biểu thức \(P = ${coef_a}MA^2${sign_b}${coef_b}MB^2${sign_c}${coef_c}MC^2\) với \(A${coord_A}\), \(B${coord_B}\), \(C${coord_C}\).

Gọi \(M(A; B; C)\) là điểm thuộc ${plane_text} sao cho \(P\) đạt giá trị nhỏ nhất. Gọi \(T\) là giá trị nhỏ nhất đó. Tính \(${expr_formula}\).

(Kết quả làm tròn đến 2 chữ số thập phân)
"""
)

# ==================== SOLUTION TEMPLATES ====================

TEMPLATE_SOL = Template(
    r"""
Lời giải:

Gọi \(G\) là điểm có tọa độ: \(G = \dfrac{${coef_a_full} \cdot A${sign_b}${coef_b_full} \cdot B${sign_c}${coef_c_full} \cdot C}{${sum_coef}} = ${coord_G}\)

Ta có: \(${coef_a}MA^2${sign_b}${coef_b}MB^2${sign_c}${coef_c}MC^2 = ${sum_coef} \cdot MG^2 + k\)

với \(k = ${coef_a_full} \cdot GA^2${sign_b}${coef_b_full} \cdot GB^2${sign_c}${coef_c_full} \cdot GC^2 = ${const_k}\)

Suy ra: \(P = ${sum_coef} \cdot MG^2 + ${const_k}\). P nhỏ nhất khi \(MG\) nhỏ nhất.

${sub_solution}

Đáp án: ${answer}
"""
)

TEMPLATE_SUB_SOL_COORD_PLANE = Template(
    r"""
\(M\) thuộc ${plane_text} nên \(${plane_eq}\).

Khoảng cách từ \(G${coord_G}\) đến ${plane_text}: \(d(G, ${plane_symbol}) = ${distance_formula} = ${distance_val}\)

Hình chiếu của \(G\) lên ${plane_text} là \(M${coord_M}\).

\(T = P_{min} = ${sum_coef} \cdot d(G, ${plane_symbol})^2 + ${const_k} = ${sum_coef} \cdot ${dist_squared} + ${const_k} = ${pmin_val}\)

Vậy: \(A = ${M_A}\), \(B = ${M_B}\), \(C = ${M_C}\), \(T = ${pmin_val}\).
"""
)

TEMPLATE_SUB_SOL_GENERAL_PLANE = Template(
    r"""
Mặt phẳng \((\alpha)\) có vector pháp tuyến \(\overrightarrow{n} = ${normal_vector}\).

Khoảng cách từ \(G${coord_G}\) đến \((\alpha)\): \(d(G, (\alpha)) = \dfrac{${distance_num}}{${distance_den}} = ${distance_val}\)

Hình chiếu của \(G\) lên \((\alpha)\) là \(M${coord_M}\).

\(T = P_{min} = ${sum_coef} \cdot d(G, (\alpha))^2 + ${const_k} = ${sum_coef} \cdot ${dist_squared} + ${const_k} = ${pmin_val}\)

Vậy: \(A = ${M_A}\), \(B = ${M_B}\), \(C = ${M_C}\), \(T = ${pmin_val}\).
"""
)

# ==================== MAIN CLASS ====================

class TimDiemMMinSquareQuestion:
    def __init__(self):
        self.A = [0, 0, 0]
        self.B = [0, 0, 0]
        self.C = [0, 0, 0]
        self.coef_a = 1
        self.coef_b = 1
        self.coef_c = 1
        self.plane = None
        # Hệ số cho biểu thức cuối: kA*A + kB*B + kC*C + kT*T
        self.kA = 1
        self.kB = 1
        self.kC = 1
        self.kT = 1

    def generate_parameters(self, plane_option=None):
        """Random các tham số bài toán"""
        
        # Random tọa độ A, B, C (số nguyên từ -15 đến 15)
        self.A = [random.randint(-15, 15) for _ in range(3)]
        self.B = [random.randint(-15, 15) for _ in range(3)]
        self.C = [random.randint(-15, 15) for _ in range(3)]
        
        # Đảm bảo 3 điểm không trùng nhau
        while self.A == self.B or self.B == self.C or self.A == self.C:
            self.B = [random.randint(-15, 15) for _ in range(3)]
            self.C = [random.randint(-15, 15) for _ in range(3)]
        
        # Random hệ số a, b, c sao cho a + b + c ≠ 0
        while True:
            self.coef_a = random.randint(1, 10)
            self.coef_b = random.choice([i for i in range(-10, 11) if i != 0])
            self.coef_c = random.choice([i for i in range(-10, 11) if i != 0])
            
            if self.coef_a + self.coef_b + self.coef_c != 0:
                break
        
        # Random mặt phẳng
        if plane_option == 1:
            plane_type = 'coord'
        elif plane_option == 2:
            plane_type = 'general'
        else:
            plane_type = random.choice(['coord', 'general'])
        
        if plane_type == 'coord':
            self.plane = random.choice(['Oxy', 'Oyz', 'Ozx'])
        else:
            # Mặt phẳng bất kỳ ax + by + cz + d = 0
            while True:
                pa = random.randint(-10, 10)
                pb = random.randint(-10, 10)
                pc = random.randint(-10, 10)
                pd = random.randint(-15, 15)
                
                if pa != 0 or pb != 0 or pc != 0:
                    non_zero = [abs(x) for x in [pa, pb, pc, pd] if x != 0]
                    if non_zero:
                        g = gcd_list(non_zero)
                        if g > 1:
                            pa, pb, pc, pd = pa // g, pb // g, pc // g, pd // g
                    break
            
            self.plane = {'a': pa, 'b': pb, 'c': pc, 'd': pd}
        
        # Random hệ số cho biểu thức cuối: kA*A + kB*B + kC*C + kT*T
        self.kA = random.choice([1, 2, 3])
        self.kB = random.choice([1, 2, 3])
        self.kC = random.choice([1, 2, 3])
        self.kT = random.choice([1, 2, 3, 4, 5, 6])

    def get_G_coord(self):
        """Tính tọa độ điểm G"""
        s = self.coef_a + self.coef_b + self.coef_c
        Gx = (self.coef_a * self.A[0] + self.coef_b * self.B[0] + self.coef_c * self.C[0]) / s
        Gy = (self.coef_a * self.A[1] + self.coef_b * self.B[1] + self.coef_c * self.C[1]) / s
        Gz = (self.coef_a * self.A[2] + self.coef_b * self.B[2] + self.coef_c * self.C[2]) / s
        return [Gx, Gy, Gz]

    def get_const_k(self, G):
        """Tính hằng số k cho dạng bình phương"""
        GA2 = (self.A[0] - G[0])**2 + (self.A[1] - G[1])**2 + (self.A[2] - G[2])**2
        GB2 = (self.B[0] - G[0])**2 + (self.B[1] - G[1])**2 + (self.B[2] - G[2])**2
        GC2 = (self.C[0] - G[0])**2 + (self.C[1] - G[1])**2 + (self.C[2] - G[2])**2
        return self.coef_a * GA2 + self.coef_b * GB2 + self.coef_c * GC2

    def get_plane_info(self, plane):
        """Lấy thông tin mặt phẳng"""
        if isinstance(plane, str):
            if plane == 'Oxy':
                return {'name': '(Oxy)', 'text': 'mặt phẳng \\((Oxy)\\)', 'symbol': '(Oxy)', 'a': 0, 'b': 0, 'c': 1, 'd': 0, 'eq': 'z = 0'}
            elif plane == 'Oyz':
                return {'name': '(Oyz)', 'text': 'mặt phẳng \\((Oyz)\\)', 'symbol': '(Oyz)', 'a': 1, 'b': 0, 'c': 0, 'd': 0, 'eq': 'x = 0'}
            elif plane == 'Ozx':
                return {'name': '(Ozx)', 'text': 'mặt phẳng \\((Ozx)\\)', 'symbol': '(Ozx)', 'a': 0, 'b': 1, 'c': 0, 'd': 0, 'eq': 'y = 0'}
        else:
            a, b, c, d = plane['a'], plane['b'], plane['c'], plane['d']
            eq_parts = []
            if a != 0:
                eq_parts.append(f"{a}x" if a not in [1, -1] else ("x" if a == 1 else "-x"))
            if b != 0:
                sign = "+" if b > 0 and eq_parts else ""
                eq_parts.append(f"{sign}{b}y" if b not in [1, -1] else (f"{sign}y" if b == 1 else "-y"))
            if c != 0:
                sign = "+" if c > 0 and eq_parts else ""
                eq_parts.append(f"{sign}{c}z" if c not in [1, -1] else (f"{sign}z" if c == 1 else "-z"))
            if d != 0:
                eq_parts.append(f"+{d}" if d > 0 else f"{d}")
            eq_parts.append("=0")
            eq = "".join(eq_parts)
            
            return {'name': '(\\alpha)', 'text': f'mặt phẳng \\((\\alpha): {eq}\\)', 'symbol': '(\\alpha)', 'a': a, 'b': b, 'c': c, 'd': d, 'eq': eq}

    def get_projection(self, G, plane_info):
        """Tính hình chiếu của G lên mặt phẳng"""
        a, b, c, d = plane_info['a'], plane_info['b'], plane_info['c'], plane_info['d']
        numerator = a * G[0] + b * G[1] + c * G[2] + d
        denominator = a**2 + b**2 + c**2
        t = -numerator / denominator
        
        Mx = G[0] + a * t
        My = G[1] + b * t
        Mz = G[2] + c * t
        return [Mx, My, Mz]

    def get_distance(self, G, plane_info):
        """Tính khoảng cách từ G đến mặt phẳng"""
        a, b, c, d = plane_info['a'], plane_info['b'], plane_info['c'], plane_info['d']
        numerator = abs(a * G[0] + b * G[1] + c * G[2] + d)
        denominator = math.sqrt(a**2 + b**2 + c**2)
        return numerator / denominator

    def format_coord_nice(self, coord):
        """Format tọa độ điểm dạng phân số nếu cần"""
        parts = []
        for val in coord:
            if val == int(val):
                parts.append(str(int(val)))
            else:
                frac = Fraction(val).limit_denominator(100)
                if frac.denominator == 1:
                    parts.append(str(frac.numerator))
                else:
                    parts.append(f"\\dfrac{{{frac.numerator}}}{{{frac.denominator}}}")
        return f"\\left({parts[0]}; {parts[1]}; {parts[2]}\\right)"

    def format_value_nice(self, val):
        """Format giá trị dạng phân số hoặc số thập phân đẹp"""
        if val == int(val):
            return str(int(val))
        frac = Fraction(val).limit_denominator(100)
        if frac.denominator == 1:
            return str(frac.numerator)
        else:
            return f"\\dfrac{{{frac.numerator}}}{{{frac.denominator}}}"

    def calculate_answer(self) -> Dict[str, Any]:
        G = self.get_G_coord()
        sum_coef = self.coef_a + self.coef_b + self.coef_c
        const_k = self.get_const_k(G)
        
        # Format hệ số
        sign_b = " + " if self.coef_b > 0 else " - "
        sign_c = " + " if self.coef_c > 0 else " - "
        abs_coef_b = abs(self.coef_b) if abs(self.coef_b) != 1 else ""
        abs_coef_c = abs(self.coef_c) if abs(self.coef_c) != 1 else ""
        
        plane_info = self.get_plane_info(self.plane)
        M = self.get_projection(G, plane_info)
        dist = self.get_distance(G, plane_info)
        dist_squared = dist ** 2
        pmin = sum_coef * dist_squared + const_k
        
        # Tính kA*A + kB*B + kC*C + kT*T
        M_A, M_B, M_C = M[0], M[1], M[2]
        result = self.kA * M_A + self.kB * M_B + self.kC * M_C + self.kT * pmin
        
        # Tạo biểu thức cuối
        expr_parts = []
        if self.kA == 1:
            expr_parts.append("A")
        else:
            expr_parts.append(f"{self.kA}A")
        if self.kB == 1:
            expr_parts.append(" + B")
        else:
            expr_parts.append(f" + {self.kB}B")
        if self.kC == 1:
            expr_parts.append(" + C")
        else:
            expr_parts.append(f" + {self.kC}C")
        if self.kT == 1:
            expr_parts.append(" + T")
        else:
            expr_parts.append(f" + {self.kT}T")
        expr_formula = "".join(expr_parts)
        
        # Format lời giải con
        if isinstance(self.plane, str):
            plane_eq = plane_info['eq']
            
            if self.plane == 'Oxy':
                distance_formula = f"|{format_vn_number(G[2])}|"
            elif self.plane == 'Oyz':
                distance_formula = f"|{format_vn_number(G[0])}|"
            else:
                distance_formula = f"|{format_vn_number(G[1])}|"
            
            sub_solution = TEMPLATE_SUB_SOL_COORD_PLANE.substitute(
                plane_text=plane_info['text'],
                plane_symbol=plane_info['symbol'],
                plane_eq=plane_eq,
                coord_G=self.format_coord_nice(G),
                distance_formula=distance_formula,
                distance_val=format_vn_number(dist, 3),
                coord_M=self.format_coord_nice(M),
                sum_coef=sum_coef,
                dist_squared=format_vn_number(dist_squared, 3),
                const_k=format_vn_number(const_k, 2),
                pmin_val=format_vn_number(pmin, 3),
                M_A=self.format_value_nice(M_A),
                M_B=self.format_value_nice(M_B),
                M_C=self.format_value_nice(M_C)
            )
        else:
            a, b, c, d = plane_info['a'], plane_info['b'], plane_info['c'], plane_info['d']
            dist_den_sq = a**2 + b**2 + c**2
            
            sub_solution = TEMPLATE_SUB_SOL_GENERAL_PLANE.substitute(
                plane_text=plane_info['text'],
                normal_vector=f"({a}; {b}; {c})",
                coord_G=self.format_coord_nice(G),
                distance_num=f"|{format_vn_number(a * G[0] + b * G[1] + c * G[2] + d)}|",
                distance_den=format_sqrt(dist_den_sq),
                distance_val=format_vn_number(dist, 3),
                coord_M=self.format_coord_nice(M),
                sum_coef=sum_coef,
                dist_squared=format_vn_number(dist_squared, 3),
                const_k=format_vn_number(const_k, 2),
                pmin_val=format_vn_number(pmin, 3),
                M_A=self.format_value_nice(M_A),
                M_B=self.format_value_nice(M_B),
                M_C=self.format_value_nice(M_C)
            )
        
        return {
            "coef_a": self.coef_a if self.coef_a != 1 else "",
            "coef_b": abs(self.coef_b) if abs(self.coef_b) != 1 else "",
            "coef_c": abs(self.coef_c) if abs(self.coef_c) != 1 else "",
            "coef_a_full": self.coef_a,
            "coef_b_full": abs(self.coef_b),
            "coef_c_full": abs(self.coef_c),
            "sign_b": sign_b,
            "sign_c": sign_c,
            "coord_A": format_coord(self.A[0], self.A[1], self.A[2]),
            "coord_B": format_coord(self.B[0], self.B[1], self.B[2]),
            "coord_C": format_coord(self.C[0], self.C[1], self.C[2]),
            "coord_G": self.format_coord_nice(G),
            "sum_coef": sum_coef,
            "const_k": format_vn_number(const_k, 2),
            "plane_text": plane_info['text'],
            "sub_solution": sub_solution,
            "expr_formula": expr_formula,
            "answer": format_answer(result, 2)
        }

    def generate_question(self, idx: int, plane_option=None) -> str:
        self.generate_parameters(plane_option)
        params = self.calculate_answer()
        params['idx'] = idx
        
        question = TEMPLATE_Q.substitute(params)
        solution = TEMPLATE_SOL.substitute(params)
        
        return f"{question}\n{solution}"

# ==================== MAIN ====================

def main():
    num_questions = 1
    plane_option = None
    
    if len(sys.argv) > 1:
        try:
            num_questions = int(sys.argv[1])
        except ValueError:
            print("Tham số 1 phải là số nguyên (số lượng câu hỏi)")
            return

    if len(sys.argv) > 2:
        try:
            plane_option = int(sys.argv[2])
            if plane_option not in [1, 2]:
                print("Tham số 2 phải là 1 (Oxy, Oyz, Ozx) hoặc 2 (mặt phẳng bất kỳ)")
                return
        except ValueError:
            print("Tham số 2 phải là số nguyên (1 hoặc 2)")
            return
    
    questions = []
    for i in range(num_questions):
        q = TimDiemMMinSquareQuestion()
        questions.append(q.generate_question(i+1, plane_option))
        
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "tim_diem_M_min_square.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong tim_diem_M_min_square.tex")

if __name__ == "__main__":
    main()

