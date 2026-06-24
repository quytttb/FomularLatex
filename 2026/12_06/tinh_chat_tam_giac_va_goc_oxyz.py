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
        py1, pz1 = random.randint(-8, 8), random.randint(-8, 8)
        B1 = -(xA + xB + zA + zB - 2*pz1)
        C1 = xA*xB + (yA - py1)*(yB - py1) + (zA - pz1)*(zB - pz1)
        delta1 = B1**2 - 4 * 2 * C1
        if delta1 <= 0:
            continue
        sum_m1 = Fraction(-B1, 2)
        
        # Statement d
        u1, v_y1, w1 = v1
        if u1 == 0 or w1 == 0:
            continue
            
        target_angle = random.choice([30, 45, 60, 120, 135, 150])
        if target_angle in [60, 120]:
            cos_sq_d = Fraction(1, 4)
        elif target_angle in [45, 135]:
            cos_sq_d = Fraction(1, 2)
        else:
            cos_sq_d = Fraction(3, 4)
            
        py2, pz2 = random.randint(-8, 8), random.randint(-8, 8)
        dot_d = -u1*xA + v_y1*(py2 - yA) + w1*(pz2 - zA)
        
        if target_angle < 90 and dot_d <= 0:
            continue
        if target_angle > 90 and dot_d >= 0:
            continue
            
        len_AB_sq = u1**2 + v_y1**2 + w1**2
        a_d = w1**2 + u1**2
        b_half_d = -(w1*xA + u1*(pz2 - zA))
        c_d = xA**2 + (py2 - yA)**2 + (pz2 - zA)**2
        
        K_d = Fraction(dot_d**2, cos_sq_d * len_AB_sq)
        delta_prime_d = b_half_d**2 - a_d*(c_d - K_d)
        
        if delta_prime_d <= 0:
            continue
            
        sum_m2 = Fraction(-2*b_half_d, a_d)
        
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
    
    pz1_str = f"+{pz1}" if pz1 > 0 else (f"{pz1}" if pz1 < 0 else "")
    
    w1_str = f"{w1}" if w1 != 1 and w1 != -1 else ("-" if w1 == -1 else "")
    u1_str = f"{-u1}" if -u1 != 1 and -u1 != -1 else ("-" if -u1 == -1 else "")
    pz2_str = f"+{pz2}" if pz2 > 0 else (f"{pz2}" if pz2 < 0 else "")
    P_d_str = f"P({w1_str}m; {py2}; {u1_str}m{pz2_str})"

    stmt_a_true = f"Số đo của góc $\\widehat{{B}}$ trong tam giác $ABC$ xấp xỉ ${format_number(round(angle_B_deg, 2))}^\\circ$."
    stmt_b_true = f"Cho điểm $P(m; {py1}; m{pz1_str})$. Tổng tất cả các giá trị thực của tham số $m$ để tam giác $ABP$ vuông tại $P$ là ${format_number(sum_m1)}$."
    stmt_c_true = f"Tọa độ chân đường phân giác trong kẻ từ đỉnh $A$ của tam giác $ABC$ là điểm $D\\left({format_number(xD)}; {format_number(yD)}; {format_number(zD)}\\right)$."
    
    stmt_d_true = f"Cho điểm ${P_d_str}$. Tổng tất cả các giá trị thực của tham số $m$ để góc $\\widehat{{PAB}}$ bằng ${target_angle}^\\circ$ là ${format_number(sum_m2)}$."
    
    stmt_a_false = f"Số đo của góc $\\widehat{{B}}$ trong tam giác $ABC$ xấp xỉ ${format_number(round(angle_B_deg + random.uniform(5, 15), 2))}^\\circ$."
    stmt_b_false = f"Cho điểm $P(m; {py1}; m{pz1_str})$. Tổng tất cả các giá trị thực của tham số $m$ để tam giác $ABP$ vuông tại $P$ là ${format_number(sum_m1 + random.choice([1, 2, -1, -2]))}$."
    xD_f = xD + random.choice([1, -1])
    stmt_c_false = f"Tọa độ chân đường phân giác trong kẻ từ đỉnh $A$ của tam giác $ABC$ là điểm $D\\left({format_number(xD_f)}; {format_number(yD)}; {format_number(zD)}\\right)$."
    stmt_d_false = f"Cho điểm ${P_d_str}$. Tổng tất cả các giá trị thực của tham số $m$ để góc $\\widehat{{PAB}}$ bằng ${target_angle}^\\circ$ là ${format_number(sum_m2 + random.choice([1, -1, Fraction(1,2)]))}$."
    
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
            question_lines.append(f"{{\\True {s_true}}}")
        else:
            question_lines.append(f"{{{s_false}}}")
        
        if label == "a":
            sol = f"\\textbf{{{label})}} " + ("Đúng. " if is_true else "Sai. ")
            sol += f"Ta có $\\vec{{BA}} = ({BA[0]}; {BA[1]}; {BA[2]})$, $\\vec{{BC}} = ({BC[0]}; {BC[1]}; {BC[2]})$. $\\cos B = \\frac{{\\vec{{BA}} \\cdot \\vec{{BC}}}}{{AB \\cdot BC}} \\approx {format_number(round(cos_B, 4))} \\implies \\widehat{{B}} \\approx {format_number(round(angle_B_deg, 2))}^\\circ$."
            solutions.append(sol)
        elif label == "b":
            sol = f"\\textbf{{{label})}} " + ("Đúng. " if is_true else "Sai. ")
            sol += f"Để tam giác $ABP$ vuông tại $P$, ta cần $\\vec{{PA}} \\cdot \\vec{{PB}} = 0$. Phương trình là $2m^2 + {B1}m + {C1} = 0$. Vì $\\Delta > 0$, tổng các giá trị của $m$ là ${format_number(sum_m1)}$."
            solutions.append(sol)
        elif label == "c":
            sol = f"\\textbf{{{label})}} " + ("Đúng. " if is_true else "Sai. ")
            sol += f"Tính được $AB = {AB}, AC = {AC}$. Do $D$ là chân đường phân giác nên $\\vec{{DB}} = -\\frac{{AB}}{{AC}} \\vec{{DC}}$. Suy ra tọa độ $D\\left({format_number(xD)}; {format_number(yD)}; {format_number(zD)}\\right)$."
            solutions.append(sol)
        elif label == "d":
            cos_str_map = {30: "\\frac{\\sqrt{3}}{2}", 45: "\\frac{\\sqrt{2}}{2}", 60: "\\frac{1}{2}", 120: "-\\frac{1}{2}", 135: "-\\frac{\\sqrt{2}}{2}", 150: "-\\frac{\\sqrt{3}}{2}"}
            cos_str = cos_str_map[target_angle]
            sol = f"\\textbf{{{label})}} " + ("Đúng. " if is_true else "Sai. ")
            sol += f"Góc $\\widehat{{PAB}}$ bằng ${target_angle}^\\circ$ tương đương với $\\cos \\widehat{{PAB}} = {cos_str}$. Bằng cách tính tích vô hướng $\\vec{{AP}} \\cdot \\vec{{AB}}$ và độ dài hai vector, ta thu được phương trình bậc 2 theo $m$: ${a_d}m^2 + {2*b_half_d}m + {format_number(c_d - K_d)} = 0$. Áp dụng định lý Vi-ét, tổng các giá trị của $m$ là ${format_number(sum_m2)}$."
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
