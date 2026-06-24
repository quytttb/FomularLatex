import sys

def run():
    with open("tinh_chat_tam_giac_va_goc_oxyz.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Split into parts
    prefix, rest = content.split("def generate_question(config: GeneratorConfig = GeneratorConfig()):")
    
    helpers = """
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
"""

    gen_q, suffix = rest.split("def main():")
    
    # Let's replace the parts in gen_q
    
    # 1. replace the Statement b and d section
    before_stmt, stmts_and_after = gen_q.split("# Statement b")
    stmts, after_stmts = stmts_and_after.split("BA = [xA - xB, yA - yB, zA - zB]")
    
    new_stmts = """
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
        
    """
    
    after_stmts = after_stmts.split("pz1_str = ")[0] # trim up to the statements string part
    
    new_str_logic = """
    pt_str1 = get_point_str(param_name1, mask1, constants1)
    pt_str2 = get_point_str(param_name2, mask2, constants2)
    
    stmt_a_true = f"Số đo của góc $\\widehat{{B}}$ trong tam giác $ABC$ xấp xỉ ${format_number(round(angle_B_deg, 2))}^\\circ$."
    stmt_b_true = f"Cho điểm ${p_name1}{pt_str1}$. Tổng tất cả các giá trị thực của tham số ${param_name1}$ để tam giác $AB{p_name1}$ vuông tại ${p_name1}$ là ${format_number(sum_m1)}$."
    stmt_c_true = f"Tọa độ chân đường phân giác trong kẻ từ đỉnh $A$ của tam giác $ABC$ là điểm $D\\left({format_number(xD)}; {format_number(yD)}; {format_number(zD)}\\right)$."
    stmt_d_true = f"Cho điểm ${p_name2}{pt_str2}$. Tổng tất cả các giá trị thực của tham số ${param_name2}$ để góc $\\widehat{{{tri_name}}}$ bằng $90^\\circ$ là ${format_number(sum_m2)}$."
    
    stmt_a_false = f"Số đo của góc $\\widehat{{B}}$ trong tam giác $ABC$ xấp xỉ ${format_number(round(angle_B_deg + random.uniform(5, 15), 2))}^\\circ$."
    stmt_b_false = f"Cho điểm ${p_name1}{pt_str1}$. Tổng tất cả các giá trị thực của tham số ${param_name1}$ để tam giác $AB{p_name1}$ vuông tại ${p_name1}$ là ${format_number(sum_m1 + random.choice([1, 2, -1, -2]))}$."
    xD_f = xD + random.choice([1, -1])
    stmt_c_false = f"Tọa độ chân đường phân giác trong kẻ từ đỉnh $A$ của tam giác $ABC$ là điểm $D\\left({format_number(xD_f)}; {format_number(yD)}; {format_number(zD)}\\right)$."
    stmt_d_false = f"Cho điểm ${p_name2}{pt_str2}$. Tổng tất cả các giá trị thực của tham số ${param_name2}$ để góc $\\widehat{{{tri_name}}}$ bằng $90^\\circ$ là ${format_number(sum_m2 + random.choice([1, -1, Fraction(1,2)]))}$."
    
    statements = [
"""
    
    # get the bottom part of gen_q
    _, rest2 = gen_q.split("statements = [")
    stmts_def, rest3 = rest2.split("for idx, (s_true, s_false, label) in enumerate(statements):")
    
    sol_logic, return_part = rest3.split("question_str = \"\\n\".join(question_lines)")
    
    new_sol_logic = """for idx, (s_true, s_false, label) in enumerate(statements):
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
            poly_str = format_polynomial(A1, B1, C1, param_name1)
            sol += f"Để tam giác $AB{p_name1}$ vuông tại ${p_name1}$, ta cần $\\vec{{{p_name1}A}} \\cdot \\vec{{{p_name1}B}} = 0$. Phương trình là ${poly_str} = 0$. Vì $\\Delta > 0$, tổng các giá trị của ${param_name1}$ là ${format_number(sum_m1)}$."
            solutions.append(sol)
        elif label == "c":
            sol = f"\\textbf{{{label})}} " + ("Đúng. " if is_true else "Sai. ")
            sol += f"Tính được $AB = {AB}, AC = {AC}$. Do $D$ là chân đường phân giác nên $\\vec{{DB}} = -\\frac{{AB}}{{AC}} \\vec{{DC}}$. Suy ra tọa độ $D\\left({format_number(xD)}; {format_number(yD)}; {format_number(zD)}\\right)$."
            solutions.append(sol)
        elif label == "d":
            sol = f"\\textbf{{{label})}} " + ("Đúng. " if is_true else "Sai. ")
            poly_str2 = format_polynomial(A2, B2, C2, param_name2)
            sol += f"Góc $\\widehat{{{tri_name}}}$ bằng $90^\\circ$ tương đương với tích vô hướng của hai vector bằng $0$. Phương trình là ${poly_str2} = 0$. Tổng các giá trị của ${param_name2}$ là ${format_number(sum_m2)}$."
            solutions.append(sol)
            
    """
    
    final_content = (
        prefix + 
        helpers + 
        before_stmt + 
        "# Statement b\n" + 
        new_stmts + 
        "    BA = [xA - xB, yA - yB, zA - zB]" + 
        after_stmts + 
        new_str_logic + 
        stmts_def + 
        new_sol_logic + 
        "    question_str = \"\\n\".join(question_lines)" + 
        return_part + 
        "def main():" + 
        suffix
    )
    
    with open("tinh_chat_tam_giac_va_goc_oxyz_updated.py", "w", encoding="utf-8") as f:
        f.write(final_content)

run()
