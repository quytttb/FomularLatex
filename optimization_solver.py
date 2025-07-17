from fractions import Fraction

import sympy as sp


def calculate_answer(base_hours, base_teams, base_productivity,
                     hour_increment, team_decrease, productivity_decrease,
                     waste_a, waste_b, waste_c, verbose=True, return_latex=False):
    """
    Tính toán số giờ làm việc tối ưu để tối đa hóa sản phẩm thu được (sau khi trừ phế phẩm)
    
    Parameters:
    - base_hours: Giờ làm việc ban đầu
    - base_teams: Số tổ ban đầu  
    - base_productivity: Năng suất ban đầu (sản phẩm/giờ/tổ)
    - hour_increment: Cứ tăng hour_increment giờ
    - team_decrease: thì giảm team_decrease tổ
    - productivity_decrease: và giảm productivity_decrease sản phẩm/giờ/tổ
    - waste_a, waste_b, waste_c: Hệ số trong công thức phế phẩm P(x) = (waste_a*x² + waste_b*x)/waste_c
    - verbose: Hiển thị chi tiết tính toán
    - return_latex: Nếu True, return LaTeX solution thay vì số
    
    Returns:
    - optimal_hours: Số giờ làm việc tối ưu
    - max_products: Số sản phẩm thu được lớn nhất
    - details: Chi tiết tính toán HOẶC LaTeX solution nếu return_latex=True
    """

    # Định nghĩa biến symbolic
    t = sp.Symbol('t', real=True)

    # Tính các thông số theo t
    teams_working = base_teams - (t / hour_increment) * team_decrease
    productivity_per_team = base_productivity - (t / hour_increment) * productivity_decrease
    working_hours = base_hours + t

    # Số sản phẩm làm được
    products_made = teams_working * productivity_per_team * working_hours

    # Số phế phẩm
    waste_products = (waste_a * working_hours ** 2 + waste_b * working_hours) / waste_c

    # Hàm mục tiêu: f(t) = sản phẩm làm được - phế phẩm
    f = products_made - waste_products

    # Tính đạo hàm bậc 1 và bậc 2
    f_prime = sp.diff(f, t)
    f_double_prime = sp.diff(f_prime, t)


    # Giải phương trình f'(t) = 0
    critical_points = sp.solve(f_prime, t)


    # Tìm miền xác định hợp lệ
    # Từ teams_working > 0: t > -base_teams * hour_increment / team_decrease
    t_min = -base_teams * hour_increment / team_decrease
    # Từ productivity_per_team > 0: t < base_productivity * hour_increment / productivity_decrease
    t_max = base_productivity * hour_increment / productivity_decrease
    # Từ working_hours > 0: t > -base_hours
    t_min = max(t_min, -base_hours)


    # Lọc các điểm tới hạn trong miền xác định
    valid_points = []
    for point in critical_points:
        if point.is_real:
            point_val = float(point.evalf())
            if t_min < point_val < t_max:
                # Kiểm tra đạo hàm bậc 2 để xác định cực đại/cực tiểu
                second_derivative_val = float(f_double_prime.subs(t, point_val).evalf())
                point_type = "cực đại" if second_derivative_val < 0 else "cực tiểu" if second_derivative_val > 0 else "uốn"
                valid_points.append((point_val, point_type))


    # Tính giá trị hàm tại các điểm quan trọng
    test_points = [p[0] for p in valid_points] + [t_min + 0.001, t_max - 0.001]  # Thêm điểm biên

    best_t = None
    max_value = float('-inf')

    for t_val in test_points:
        f_val = float(f.subs(t, t_val).evalf())
        hours_val = base_hours + t_val

        if f_val > max_value:
            max_value = f_val
            best_t = t_val

    # Kết quả tối ưu
    optimal_hours = base_hours + best_t

    # Chi tiết tại điểm tối ưu
    optimal_teams = float(teams_working.subs(t, best_t).evalf())
    optimal_productivity = float(productivity_per_team.subs(t, best_t).evalf())
    optimal_products_made = float(products_made.subs(t, best_t).evalf())
    optimal_waste = float(waste_products.subs(t, best_t).evalf())

    details = {
        't_optimal': best_t,
        'teams_working': optimal_teams,
        'productivity_per_team': optimal_productivity,
        'products_made': optimal_products_made,
        'waste_products': optimal_waste,
        'net_products': max_value,
        'function': str(sp.expand(f)),
        'derivative': str(sp.expand(f_prime)),
        'second_derivative': str(sp.expand(f_double_prime)),
        'critical_points': [float(cp.evalf()) for cp in critical_points if cp.is_real],
        'valid_critical_points': valid_points,
        'domain': (t_min, t_max)
    }

    # Nếu cần return LaTeX, tạo LaTeX solution
    if return_latex:
        # Expand và simplify đạo hàm để có dạng đơn giản
        f_prime_expanded = sp.expand(f_prime)
        f_prime_simplified = sp.simplify(f_prime_expanded)

        # Tìm critical point thứ hai (bị loại)
        other_critical_point = None
        for cp in details['critical_points']:
            if abs(cp - best_t) > 0.1:  # Not the same as optimal
                other_critical_point = cp
                break

        # Convert đạo hàm thành dạng fraction để hiển thị đẹp
        def format_derivative_latex(expr):
            """Format derivative in standard form like ax^2 + bx + c"""
            coeffs = sp.Poly(expr, t).all_coeffs()
            if len(coeffs) == 3:  # Quadratic: at^2 + bt + c
                a, b, c = coeffs
                # Convert to fractions
                a_frac = Fraction(float(a)).limit_denominator()
                b_frac = Fraction(float(b)).limit_denominator()
                c_frac = Fraction(float(c)).limit_denominator()

                terms = []

                # Term a*t^2
                if a_frac != 0:
                    if a_frac.denominator == 1:
                        if a_frac == 1:
                            terms.append("t^2")
                        elif a_frac == -1:
                            terms.append("-t^2")
                        else:
                            terms.append(f"{a_frac} t^2")
                    else:
                        if a_frac > 0:
                            terms.append(f"\\dfrac{{{a_frac.numerator}}}{{{a_frac.denominator}}} t^2")
                        else:
                            terms.append(f"-\\dfrac{{{abs(a_frac.numerator)}}}{{{a_frac.denominator}}} t^2")

                # Term b*t  
                if b_frac != 0:
                    if b_frac.denominator == 1:
                        if b_frac == 1:
                            terms.append("t" if not terms else "+t")
                        elif b_frac == -1:
                            terms.append("-t")
                        else:
                            if terms and b_frac > 0:
                                terms.append(f"+{b_frac} t")
                            else:
                                terms.append(f"{b_frac} t")
                    else:
                        if b_frac > 0:
                            prefix = "+" if terms else ""
                            terms.append(f"{prefix}\\dfrac{{{b_frac.numerator}}}{{{b_frac.denominator}}} t")
                        else:
                            terms.append(f"-\\dfrac{{{abs(b_frac.numerator)}}}{{{b_frac.denominator}}} t")

                # Constant term c
                if c_frac != 0:
                    if c_frac.denominator == 1:
                        if terms and c_frac > 0:
                            terms.append(f"+{c_frac.numerator}")
                        else:
                            terms.append(str(c_frac.numerator))
                    else:
                        if c_frac > 0:
                            prefix = "+" if terms else ""
                            terms.append(f"{prefix}\\dfrac{{{c_frac.numerator}}}{{{c_frac.denominator}}}")
                        else:
                            terms.append(f"-\\dfrac{{{abs(c_frac.numerator)}}}{{{c_frac.denominator}}}")

                return "".join(terms)
            else:
                return sp.latex(expr)

        # Format second critical point
        if other_critical_point is not None:
            if abs(other_critical_point - round(other_critical_point)) < 0.01:
                second_cp_latex = f"{int(round(other_critical_point))}"
            else:
                # Try to express as fraction
                frac = Fraction(float(other_critical_point)).limit_denominator(10)
                if frac.denominator == 1:
                    second_cp_latex = str(frac.numerator)
                else:
                    second_cp_latex = f"\\dfrac{{{frac.numerator}}}{{{frac.denominator}}}"
        else:
            second_cp_latex = "\\text{(khác)}"

        # Generate LaTeX solution
        latex_solution = f"""\\loigiai{{
\tGọi số giờ làm tăng thêm mỗi tuần là \\(t, t \\in \\mathbb{{R}}\\). 
\t
\tSố tổ công nhân bỏ việc là \\(\\dfrac{{t}}{{{hour_increment}}}\\) nên số tổ công nhân làm việc là \\({base_teams}-\\dfrac{{t}}{{{hour_increment}}}\\) (tổ). 
\t
\tNăng suất của tổ công nhân còn \\({base_productivity}-\\dfrac{{{productivity_decrease} t}}{{{hour_increment}}}\\) sản phẩm một giờ. 
\t
\tSố thời gian làm việc một tuần là \\({base_hours}+t=x\\) (giờ).
\t
\t\\(\\Rightarrow\\) Số phế phẩm thu được là \\(P({base_hours}+t)=\\dfrac{{{waste_a}({base_hours}+t)^2+{waste_b}({base_hours}+t)}}{{{waste_c}}}\\)
\t
\tĐể nhà máy hoạt động được thì \\(\\left\\{{\\begin{{array}}{{l}}{base_hours}+t>0 \\\\ {base_productivity}-\\dfrac{{{productivity_decrease} t}}{{{hour_increment}}}>0\\end{{array}}\\right. \\Rightarrow t \\in({t_min} ; {t_max}) \\\\
\t{base_teams}-\\dfrac{{t}}{{{hour_increment}}}>0\\)
\t
\tSố sản phẩm trong một tuần làm được: 
\t
\t\\(S=\\text{{Số tổ x Năng suất x Thời gian}}= \\left({base_teams}-\\dfrac{{t}}{{{hour_increment}}}\\right)\\left({base_productivity}-\\dfrac{{{productivity_decrease} t}}{{{hour_increment}}}\\right)({base_hours}+t)\\). 
\t
\tSố sản phẩm thu được là:
\t
\t\\(
\tf(t)  =\\left({base_teams}-\\dfrac{{t}}{{{hour_increment}}}\\right)\\left({base_productivity}-\\dfrac{{{productivity_decrease} t}}{{{hour_increment}}}\\right)({base_hours}+t)-\\dfrac{{{waste_a}({base_hours}+t)^2+{waste_b}({base_hours}+t)}}{{{waste_c}}} \\)
\t
\t\\(f^{{\\prime}}(t) = {format_derivative_latex(f_prime_simplified)}\\)
\t
\tTa có \\(f^{{\\prime}}(t)=0 \\Leftrightarrow\\left[\\begin{{array}}{{l}}t={best_t:.0f} \\\\ t={second_cp_latex}(L)\\end{{array}}\\right.\\). 
\t
\tDựa vào bảng biến thiên ta có số lượng sản phẩm thu được lớn nhất thì thời gian làm việc trong một tuần là \\({base_hours}{best_t:+.0f}={optimal_hours:.0f}\\).
\t
}}"""

        return None, None, latex_solution

    return optimal_hours, max_value, details


# Hướng dẫn sử dụng
if __name__ == "__main__":
    print("=== HƯỚNG DẪN SỬ DỤNG ===")
    print("1. Để tính toán kết quả số:")
    print("   optimal_hours, max_products, details = calculate_answer(40, 100, 120, 2, 1, 5, 95, 120, 4)")
    print("\n2. Để tạo LaTeX solution:")
    print("   _, _, latex_solution = calculate_answer(40, 100, 120, 2, 1, 5, 95, 120, 4, return_latex=True)")
    print("\n3. Để có chi tiết tính toán:")
    print("   optimal_hours, max_products, details = calculate_answer(40, 100, 120, 2, 1, 5, 95, 120, 4, verbose=True)")
