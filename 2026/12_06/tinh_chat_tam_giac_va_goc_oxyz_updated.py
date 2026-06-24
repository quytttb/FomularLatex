import math
import random
import sys
from fractions import Fraction
import sympy as sp
from dataclasses import dataclass

@dataclass
class GeneratorConfig:
    seed: int = None

def format_number(num):
    if isinstance(num, (int, sp.Integer)):
        return str(num)
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    if isinstance(num, sp.Rational):
        if num.q == 1:
            return str(num.p)
        return f"\\frac{{{num.p}}}{{{num.q}}}"
    if isinstance(num, float):
        return f"{num:.2f}".replace('.', ',')
    return str(num).replace('.', ',')


def compute_equation(pt1, pt2, param_mask, constants):
    A, B, C = 0, 0, 0
    for i in range(3):
        if param_mask[i]:
            A += 1
            B += -(pt1[i] + pt2[i] - 2*constants[i])
            C += (pt1[i] - constants[i])*(pt2[i] - constants[i])
        else:
            C += (pt1[i] - constants[i])*(pt2[i] - constants[i])
    return A, B, C

def get_point_str(param_name, param_mask, constants):
    coords = []
    for i in range(3):
        if param_mask[i]:
            if constants[i] > 0:
                coords.append(f"{param_name}+{constants[i]}")
            elif constants[i] < 0:
                coords.append(f"{param_name}{constants[i]}")
            else:
                coords.append(f"{param_name}")
        else:
            coords.append(f"{constants[i]}")
    return "(" + "; ".join(coords) + ")"

def format_polynomial(A, B, C, var):
    terms = []
    if A != 0:
        if A == 1:
            terms.append(f"{var}^2")
        elif A == -1:
            terms.append(f"-{var}^2")
        else:
            terms.append(f"{A}{var}^2")
    if B != 0:
        if B == 1:
            terms.append(f"{var}")
        elif B == -1:
            terms.append(f"-{var}")
        else:
            terms.append(f"{B}{var}")
    if C != 0:
        terms.append(f"{C}")
        
    if not terms:
        return "0"
        
    s = terms[0]
    for term in terms[1:]:
        if term.startswith("-"):
            s += f" - {term[1:]}"
        else:
            s += f" + {term}"
    return s

def generate_question(config: GeneratorConfig = GeneratorConfig()):

    if config.seed is not None:
        random.seed(config.seed)
        
    nice_vectors = [
        # magnitude 3
        (1, 2, 2), (2, 1, 2), (2, 2, 1),
        # magnitude 5
        (3, 4, 0), (4, 3, 0), (0, 3, 4), (0, 4, 3), (3, 0, 4), (4, 0, 3),
        # magnitude 6
        (4, 4, 2), (4, 2, 4), (2, 4, 4),
        # magnitude 7
        (2, 3, 6), (3, 2, 6), (6, 2, 3), (6, 3, 2), (3, 6, 2), (2, 6, 3),
        # magnitude 9
        (1, 4, 8), (4, 1, 8), (8, 4, 1), (8, 1, 4), (4, 8, 1), (1, 8, 4),
        (4, 7, 4), (7, 4, 4), (4, 4, 7),
        # magnitude 10
        (6, 0, 8), (0, 6, 8), (8, 6, 0), (6, 8, 0),
        # magnitude 11
        (2, 6, 9), (6, 2, 9), (9, 6, 2), (9, 2, 6), (6, 9, 2), (2, 9, 6),
        # magnitude 13
        (3, 4, 12), (4, 3, 12), (12, 3, 4), (12, 4, 3), (4, 12, 3), (3, 12, 4),
        # magnitude 15
        (5, 10, 10), (10, 5, 10), (10, 10, 5),
        (9, 0, 12), (0, 9, 12), (12, 9, 0),
    ]
    
    while True:
        xA, yA, zA = random.randint(-8, 8), random.randint(-8, 8), random.randint(-8, 8)
        
        v1 = random.choice(nice_vectors)
        v2 = random.choice(nice_vectors)
        
        v1 = [v * random.choice([1, -1]) for v in v1]
        v2 = [v * random.choice([1, -1]) for v in v2]
        
        if v1 == v2 or v1 == [-v for v in v2]:
            continue
            
        xB, yB, zB = xA + v1[0], yA + v1[1], zA + v1[2]
        xC, yC, zC = xA + v2[0], yA + v2[1], zA + v2[2]
        
        # Check non-collinear
        cross_x = v1[1]*v2[2] - v1[2]*v2[1]
        cross_y = v1[2]*v2[0] - v1[0]*v2[2]
        cross_z = v1[0]*v2[1] - v1[1]*v2[0]
        if cross_x == 0 and cross_y == 0 and cross_z == 0:
            continue
            
        AB = int(math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2))
        AC = int(math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2))
        
        # Statement b

        p_name1 = random.choice(["M", "N", "P", "Q", "E", "F", "K"])
        param_name1 = random.choice(["m", "t", "a", "k"])
        mask1 = random.choice([[True, True, False], [True, False, True], [False, True, True], [True, True, True]])
        constants1 = [random.randint(-8, 8) for _ in range(3)]
        
        A1, B1, C1 = compute_equation((xA, yA, zA), (xB, yB, zB), mask1, constants1)
        delta1 = B1**2 - 4 * A1 * C1
        if delta1 <= 0:
            continue
        sum_m1 = Fraction(-B1, A1)
        
        # Statement d
        p_name2 = random.choice(["M", "N", "P", "Q", "E", "F", "K"])
        while p_name2 == p_name1:
            p_name2 = random.choice(["M", "N", "P", "Q", "E", "F", "K"])
        param_name2 = random.choice(["m", "t", "a", "k"])
        mask2 = random.choice([[True, True, False], [True, False, True], [False, True, True], [True, True, True]])
        constants2 = [random.randint(-8, 8) for _ in range(3)]
        
        triangle_choice = random.choice(['1', '2'])
        if triangle_choice == '1':
            tri_name = f'B{p_name2}C'
            pt1, pt2 = (xB, yB, zB), (xC, yC, zC)
        else:
            tri_name = f'C{p_name2}A'
            pt1, pt2 = (xC, yC, zC), (xA, yA, zA)
            
        A2, B2, C2 = compute_equation(pt1, pt2, mask2, constants2)
        delta2 = B2**2 - 4 * A2 * C2
        if delta2 <= 0:
            continue
        sum_m2 = Fraction(-B2, A2)
        
        break
        
        BA = [xA - xB, yA - yB, zA - zB]
    BC = [xC - xB, yC - yB, zC - zB]
    dot_B = sum(BA[i]*BC[i] for i in range(3))
    len_BA = math.sqrt(sum(x**2 for x in BA))
    len_BC = math.sqrt(sum(x**2 for x in BC))
    cos_B = dot_B / (len_BA * len_BC)
    angle_B_rad = math.acos(cos_B)
    angle_B_deg = math.degrees(angle_B_rad)
    
    xD = Fraction(AC * xB + AB * xC, AB + AC)
    yD = Fraction(AC * yB + AB * yC, AB + AC)
    zD = Fraction(AC * zB + AB * zC, AB + AC)
    
    
    pt_str1 = get_point_str(param_name1, mask1, constants1)
    pt_str2 = get_point_str(param_name2, mask2, constants2)
    
    stmt_a_true = f"Số đo của góc $\widehat{{B}}$ trong tam giác $ABC$ xấp xỉ ${format_number(round(angle_B_deg, 2))}^\circ$."
    stmt_b_true = f"Cho điểm ${p_name1}{pt_str1}$. Tổng tất cả các giá trị thực của tham số ${param_name1}$ để tam giác $AB{p_name1}$ vuông tại ${p_name1}$ là ${format_number(sum_m1)}$."
    stmt_c_true = f"Tọa độ chân đường phân giác trong kẻ từ đỉnh $A$ của tam giác $ABC$ là điểm $D\left({format_number(xD)}; {format_number(yD)}; {format_number(zD)}\right)$."
    stmt_d_true = f"Cho điểm ${p_name2}{pt_str2}$. Tổng tất cả các giá trị thực của tham số ${param_name2}$ để góc $\widehat{{{tri_name}}}$ bằng $90^\circ$ là ${format_number(sum_m2)}$."
    
    stmt_a_false = f"Số đo của góc $\widehat{{B}}$ trong tam giác $ABC$ xấp xỉ ${format_number(round(angle_B_deg + random.uniform(5, 15), 2))}^\circ$."
    stmt_b_false = f"Cho điểm ${p_name1}{pt_str1}$. Tổng tất cả các giá trị thực của tham số ${param_name1}$ để tam giác $AB{p_name1}$ vuông tại ${p_name1}$ là ${format_number(sum_m1 + random.choice([1, 2, -1, -2]))}$."
    xD_f = xD + random.choice([1, -1])
    stmt_c_false = f"Tọa độ chân đường phân giác trong kẻ từ đỉnh $A$ của tam giác $ABC$ là điểm $D\left({format_number(xD_f)}; {format_number(yD)}; {format_number(zD)}\right)$."
    stmt_d_false = f"Cho điểm ${p_name2}{pt_str2}$. Tổng tất cả các giá trị thực của tham số ${param_name2}$ để góc $\widehat{{{tri_name}}}$ bằng $90^\circ$ là ${format_number(sum_m2 + random.choice([1, -1, Fraction(1,2)]))}$."
    
    statements = [

        (stmt_a_true, stmt_a_false, "a"),
        (stmt_b_true, stmt_b_false, "b"),
        (stmt_c_true, stmt_c_false, "c"),
        (stmt_d_true, stmt_d_false, "d")
    ]
    
    question_lines = [f"Trong không gian với hệ tọa độ $Oxyz$, cho ba điểm $A({xA}; {yA}; {zA})$, $B({xB}; {yB}; {zB})$ và $C({xC}; {yC}; {zC})$.\\choiceTFt"]
    markers = []
    solutions = []
    
    for idx, (s_true, s_false, label) in enumerate(statements):
        is_true = random.choice([True, False])
        markers.append("Đ" if is_true else "S")
        if is_true:
            question_lines.append(f"{{\True {s_true}}}")
        else:
            question_lines.append(f"{{{s_false}}}")
        
        if label == "a":
            sol = f"\textbf{{{label})}} " + ("Đúng. " if is_true else "Sai. ")
            sol += f"Ta có $\vec{{BA}} = ({BA[0]}; {BA[1]}; {BA[2]})$, $\vec{{BC}} = ({BC[0]}; {BC[1]}; {BC[2]})$. $\cos B = \frac{{\vec{{BA}} \cdot \vec{{BC}}}}{{AB \cdot BC}} \approx {format_number(round(cos_B, 4))} \implies \widehat{{B}} \approx {format_number(round(angle_B_deg, 2))}^\circ$."
            solutions.append(sol)
        elif label == "b":
            sol = f"\textbf{{{label})}} " + ("Đúng. " if is_true else "Sai. ")
            poly_str = format_polynomial(A1, B1, C1, param_name1)
            sol += f"Để tam giác $AB{p_name1}$ vuông tại ${p_name1}$, ta cần $\vec{{{p_name1}A}} \cdot \vec{{{p_name1}B}} = 0$. Phương trình là ${poly_str} = 0$. Vì $\Delta > 0$, tổng các giá trị của ${param_name1}$ là ${format_number(sum_m1)}$."
            solutions.append(sol)
        elif label == "c":
            sol = f"\textbf{{{label})}} " + ("Đúng. " if is_true else "Sai. ")
            sol += f"Tính được $AB = {AB}, AC = {AC}$. Do $D$ là chân đường phân giác nên $\vec{{DB}} = -\frac{{AB}}{{AC}} \vec{{DC}}$. Suy ra tọa độ $D\left({format_number(xD)}; {format_number(yD)}; {format_number(zD)}\right)$."
            solutions.append(sol)
        elif label == "d":
            sol = f"\textbf{{{label})}} " + ("Đúng. " if is_true else "Sai. ")
            poly_str2 = format_polynomial(A2, B2, C2, param_name2)
            sol += f"Góc $\widehat{{{tri_name}}}$ bằng $90^\circ$ tương đương với tích vô hướng của hai vector bằng $0$. Phương trình là ${poly_str2} = 0$. Tổng các giá trị của ${param_name2}$ là ${format_number(sum_m2)}$."
            solutions.append(sol)
            
        question_str = "\n".join(question_lines)
    solution_str = "\n".join(solutions)
    return question_str, solution_str, markers

def main():
    num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    with open("tinh_chat_tam_giac_va_goc_oxyz_output.tex", "w", encoding="utf-8") as f:
        f.write("\\documentclass[12pt,a4paper]{article}\n\\usepackage{amsmath,amssymb}\n\\usepackage{polyglossia}\n\\setdefaultlanguage{vietnamese}\n\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}\n\\usepackage[solcolor]{ex_test}\n\\begin{document}\n")
        for i in range(num_questions):
            q, s, m = generate_question(GeneratorConfig())
            f.write(f"\\begin{{ex}}\n{q}\n\\end{{ex}}\n\n")
        f.write("\\end{document}\n")

if __name__ == "__main__":
    main()
