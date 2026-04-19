import math
import random
import re
import sys
from typing import List, Tuple
import sympy as sp
from sympy import sqrt, Rational, simplify


# =============================
# HÀM HELPER TẠO BIỂU THỨC RANDOM
# =============================
def create_random_sphere_expression(a, b, c, R_squared):
    """
    Tạo biểu thức random cho tâm và bán kính mặt cầu
    
    Args:
        a, b, c: Tọa độ tâm I(a,b,c) - dạng SymPy
        R_squared: Bán kính bình phương R² - dạng SymPy
    
    Returns:
        tuple: (biểu_thức_string, giá_trị_sympy)
    """
    # Random hệ số từ tập [-3, -2, -1, 1, 2, 3]
    coefficients = [-3, -2, -1, 1, 2, 3]
    
    k1 = random.choice(coefficients)  # hệ số của a
    k2 = random.choice(coefficients)  # hệ số của b  
    k3 = random.choice(coefficients)  # hệ số của c
    k4 = random.choice(coefficients)  # hệ số của R²
    
    # Tính giá trị dạng SymPy (giữ nguyên phân số/căn thức)
    value = k1 * a + k2 * b + k3 * c + k4 * R_squared
    
    # Tạo biểu thức string
    def format_term(coeff, var):
        if coeff == 1:
            return var
        elif coeff == -1:
            return f"-{var}"
        else:
            return f"{coeff}{var}"
    
    terms = []
    if k1 != 0:
        terms.append(format_term(k1, "a"))
    if k2 != 0:
        terms.append(format_term(k2, "b"))
    if k3 != 0:
        terms.append(format_term(k3, "c"))
    if k4 != 0:
        terms.append(format_term(k4, "R^2"))
    
    # Nối các terms với dấu +/-
    expression = terms[0] if terms else "0"
    for term in terms[1:]:
        if term.startswith("-"):
            expression += term
        else:
            expression += f"+{term}"
    
    return expression, value


# =============================
# CLASS TÍNH TOÁN MẶT CẦU
# =============================
class SphereQuestion:
    def __init__(self):
        self.generate_parameters()

    def generate_solution(self):
        """Tạo lời giải"""
        # Gọi trực tiếp phương thức tương ứng
        if self.question_type == 9:
            return self.tao_loi_giai_mat_cau_biet_tam_va_giao_tuyen()
        elif self.question_type == 10:
            return self.tao_loi_giai_mat_cau_ngoai_tiep_tu_dien()
        elif self.question_type == 11:
            return self.tao_loi_giai_mat_cau_di_qua_2_diem_tam_tren_truc()
        elif self.question_type == 12:
            return self.tao_loi_giai_mat_cau_di_qua_3_diem_tam_trong_mp()
        else:
            raise ValueError(f"Chưa implement lời giải dạng {self.question_type}")
    
    # =================================================================
    # HELPER FUNCTIONS - ĐƯỢC THIẾT KẾ ĐỂ TÁI SỬ DỤNG CHO 17 DẠNG BÀI TOÁN
    # =================================================================
    
    def calculate_circumsphere(self):
        """Tính tâm và bán kính mặt cầu ngoại tiếp 4 điểm chính xác"""
        # Sử dụng phương pháp giải hệ phương trình tuyến tính
        # (x-a)² + (y-b)² + (z-c)² = R² cho cả 4 điểm
        x1, y1, z1 = self.A
        x2, y2, z2 = self.B  
        x3, y3, z3 = self.C
        x4, y4, z4 = self.point_D
        
        # Chuyển về hệ phương trình tuyến tính bằng cách trừ phương trình đầu tiên
        # Từ điều kiện IA² = IB²: 
        # (x1-a)² + (y1-b)² + (z1-c)² = (x2-a)² + (y2-b)² + (z2-c)²
        # Rút gọn thành: 2a(x2-x1) + 2b(y2-y1) + 2c(z2-z1) = (x2²+y2²+z2²) - (x1²+y1²+z1²)
        
        # Hệ số ma trận A và vector b cho hệ Ax = b
        # x = [a, b, c]
        A_matrix = []
        b_vector = []
        
        # Phương trình 1: IA² = IB²
        coeff1 = [2*(x2-x1), 2*(y2-y1), 2*(z2-z1)]
        const1 = (x2*x2 + y2*y2 + z2*z2) - (x1*x1 + y1*y1 + z1*z1)
        A_matrix.append(coeff1)
        b_vector.append(const1)
        
        # Phương trình 2: IA² = IC²
        coeff2 = [2*(x3-x1), 2*(y3-y1), 2*(z3-z1)]
        const2 = (x3*x3 + y3*y3 + z3*z3) - (x1*x1 + y1*y1 + z1*z1)
        A_matrix.append(coeff2)
        b_vector.append(const2)
        
        # Phương trình 3: IA² = ID²
        coeff3 = [2*(x4-x1), 2*(y4-y1), 2*(z4-z1)]
        const3 = (x4*x4 + y4*y4 + z4*z4) - (x1*x1 + y1*y1 + z1*z1)
        A_matrix.append(coeff3)
        b_vector.append(const3)
        
        # Giải hệ phương trình 3x3 bằng SymPy
        from sympy import Matrix, Rational
        
        try:
            # Chuyển sang Rational để tính chính xác
            A_rational = Matrix([[Rational(A_matrix[i][j]) for j in range(3)] for i in range(3)])
            b_rational = Matrix([Rational(b_vector[i]) for i in range(3)])
            
            # Giải hệ phương trình
            solution = A_rational.LUsolve(b_rational)
            
            self.center_x = solution[0]
            self.center_y = solution[1]
            self.center_z = solution[2]
            
        except:
            # Fallback về phương pháp đơn giản nếu ma trận không khả nghịch
            self.center_x = Rational(x1 + x2 + x3 + x4, 4)
            self.center_y = Rational(y1 + y2 + y3 + y4, 4)  
            self.center_z = Rational(z1 + z2 + z3 + z4, 4)
        
        # Tính bán kính (khoảng cách từ tâm đến điểm A) bằng SymPy
        dx = x1 - self.center_x
        dy = y1 - self.center_y
        dz = z1 - self.center_z
        self.R_squared = simplify(dx**2 + dy**2 + dz**2)
        self.R = sqrt(self.R_squared)
    
    def calculate_center_on_oz(self):
        """Tính tâm mặt cầu trên trục Oz khi biết 2 điểm"""
        x1, y1, z1 = self.A
        x2, y2, z2 = self.B
        
        # Tâm I(0, 0, c), điều kiện IA = IB
        # IA² = x1² + y1² + (z1-c)²
        # IB² = x2² + y2² + (z2-c)²
        # IA² = IB² => c = (x1² + y1² + z1² - x2² - y2² - z2²) / (2(z1 - z2))
        
        numerator = x1**2 + y1**2 + z1**2 - x2**2 - y2**2 - z2**2
        denominator = 2 * (z1 - z2) if z1 != z2 else 1
        self.center_z = Rational(numerator, denominator) if denominator != 0 else 0
        self.center_x = 0
        self.center_y = 0
        
        # Tính bán kính bằng SymPy
        dx = x1 - self.center_x
        dy = y1 - self.center_y  
        dz = z1 - self.center_z
        self.R_squared = simplify(dx**2 + dy**2 + dz**2)
        self.R = sqrt(self.R_squared)
    
    def calculate_center_in_oxy(self):
        """Tính tâm mặt cầu trong mặt phẳng Oxy khi biết 3 điểm"""
        x1, y1, z1 = self.A
        x2, y2, z2 = self.B
        x3, y3, z3 = self.C
        
        # Tâm I(a, b, 0), điều kiện IA = IB = IC
        # Giải hệ phương trình từ IA² = IB² và IA² = IC²
        
        # Từ IA² = IB²:
        # (a-x1)² + (b-y1)² + z1² = (a-x2)² + (b-y2)² + z2²
        # Rút gọn: 2a(x2-x1) + 2b(y2-y1) = (x2²+y2²+z2²) - (x1²+y1²+z1²)
        
        # Từ IA² = IC²:
        # (a-x1)² + (b-y1)² + z1² = (a-x3)² + (b-y3)² + z3²
        # Rút gọn: 2a(x3-x1) + 2b(y3-y1) = (x3²+y3²+z3²) - (x1²+y1²+z1²)
        
        # Hệ phương trình tuyến tính 2x2:
        # coeff1_a * a + coeff1_b * b = const1
        # coeff2_a * a + coeff2_b * b = const2
        
        coeff1_a = 2 * (x2 - x1)
        coeff1_b = 2 * (y2 - y1)
        const1 = (x2*x2 + y2*y2 + z2*z2) - (x1*x1 + y1*y1 + z1*z1)
        
        coeff2_a = 2 * (x3 - x1)
        coeff2_b = 2 * (y3 - y1)
        const2 = (x3*x3 + y3*y3 + z3*z3) - (x1*x1 + y1*y1 + z1*z1)
        
        # Giải hệ phương trình 2x2 bằng SymPy
        from sympy import Matrix, Rational
        
        try:
            # Chuyển sang Rational để tính chính xác
            A_matrix = Matrix([
                [Rational(coeff1_a), Rational(coeff1_b)],
                [Rational(coeff2_a), Rational(coeff2_b)]
            ])
            b_vector = Matrix([Rational(const1), Rational(const2)])
            
            # Giải hệ phương trình
            solution = A_matrix.LUsolve(b_vector)
            
            self.center_x = solution[0]
            self.center_y = solution[1]
            self.center_z = 0
            
        except:
            # Fallback về phương pháp đơn giản nếu ma trận không khả nghịch
            self.center_x = Rational(x1 + x2 + x3, 3)
            self.center_y = Rational(y1 + y2 + y3, 3)
            self.center_z = 0
        
        # Tính bán kính bằng SymPy
        dx = x1 - self.center_x
        dy = y1 - self.center_y
        dz = z1 - self.center_z  
        self.R_squared = simplify(dx**2 + dy**2 + dz**2)
        self.R = sqrt(self.R_squared)
    
    def format_sympy_to_latex(self, expr):
        """Chuyển biểu thức SymPy thành LaTeX đẹp"""
        if isinstance(expr, (int, float)):
            return str(expr)
        elif hasattr(expr, 'is_integer') and expr.is_integer:
            return str(expr)
        elif hasattr(expr, 'p') and hasattr(expr, 'q'):  # Rational number
            if expr.q == 1:
                return str(expr.p)
            else:
                return f"\\frac{{{expr.p}}}{{{expr.q}}}"
        else:
            # For all other SymPy expressions, use SymPy's latex function
            # This will properly format sqrt, fractions, etc.
            latex_str = sp.latex(expr)
            
            # Fix common formatting issues
            # Convert simple fractions like "5/4" to "\frac{5}{4}"
            # Match patterns like "5/4" but not in \frac{5}{4}
            latex_str = re.sub(r'\b(\d+)/(\d+)\b', r'\\frac{\1}{\2}', latex_str)
            
            return latex_str
    
    def format_linear_equation(self, coeff_a, coeff_b, coeff_c, constant):
        """Định dạng phương trình tuyến tính, bỏ các hạng tử có hệ số 0"""
        terms = []
        
        # Hạng tử a
        if coeff_a != 0:
            if coeff_a == 1:
                terms.append("a")
            elif coeff_a == -1:
                terms.append("-a")
            else:
                terms.append(f"{coeff_a}a")
        
        # Hạng tử b
        if coeff_b != 0:
            if coeff_b == 1:
                if terms:
                    terms.append("+ b")
                else:
                    terms.append("b")
            elif coeff_b == -1:
                terms.append("- b")
            else:
                if coeff_b > 0 and terms:
                    terms.append(f"+ {coeff_b}b")
                else:
                    terms.append(f"{coeff_b}b")
        
        # Hạng tử c
        if coeff_c != 0:
            if coeff_c == 1:
                if terms:
                    terms.append("+ c")
                else:
                    terms.append("c")
            elif coeff_c == -1:
                terms.append("- c")
            else:
                if coeff_c > 0 and terms:
                    terms.append(f"+ {coeff_c}c")
                else:
                    terms.append(f"{coeff_c}c")
        
        # Nếu không có hạng tử nào
        if not terms:
            return f"0 = {constant}"
        
        # Ghép các hạng tử lại
        equation_left = " ".join(terms)
        return f"{equation_left} = {constant}"
    
    def format_term_for_standard_form(self, coefficient, variable):
        """
        Tạo chuỗi cho một hạng tử trong phương trình chuẩn
        VD: format_term_for_standard_form(-2, 'x') → '(x + 2)'
            format_term_for_standard_form(3, 'y') → '(y - 3)'
            format_term_for_standard_form(0, 'z') → 'z'
        """
        # Handle SymPy expressions
        if hasattr(coefficient, 'is_zero') and coefficient.is_zero:
            return variable
        elif hasattr(coefficient, 'is_positive') and coefficient.is_positive:
            coeff_latex = self.format_sympy_to_latex(coefficient)
            return f"({variable} - {coeff_latex})"
        elif hasattr(coefficient, 'is_negative') and coefficient.is_negative:
            coeff_latex = self.format_sympy_to_latex(-coefficient)
            return f"({variable} + {coeff_latex})"
        # Handle regular numbers
        elif coefficient == 0:
            return variable
        elif coefficient > 0:
            return f"({variable} - {coefficient})"
        else:
            return f"({variable} + {-coefficient})"
    
    def build_standard_equation(self):
        """Tạo phương trình chuẩn (x-a)²+(y-b)²+(z-c)²=R²"""
        # Ưu tiên sử dụng center_x, center_y, center_z nếu có, nếu không thì dùng a, b, c
        a = getattr(self, 'center_x', getattr(self, 'a', 0))
        b = getattr(self, 'center_y', getattr(self, 'b', 0))
        c = getattr(self, 'center_z', getattr(self, 'c', 0))
        
        x_term = self.format_term_for_standard_form(a, 'x')
        y_term = self.format_term_for_standard_form(b, 'y')
        z_term = self.format_term_for_standard_form(c, 'z')
        
        # Format R_squared properly
        r_squared_latex = self.format_sympy_to_latex(self.R_squared)
        
        return f"{x_term}^2 + {y_term}^2 + {z_term}^2 = {r_squared_latex}"
    
    # =================================================================
    # END HELPER FUNCTIONS
    # =================================================================

    def generate_parameters(self):
        """Sinh các tham số ngẫu nhiên cho câu hỏi mặt cầu"""
        # Chỉ random question_type khi chưa được set
        if not hasattr(self, 'question_type'):
            self.question_type = random.choice([9, 10, 11, 12])
        
        # Gọi trực tiếp phương thức tương ứng
        if self.question_type == 9:
            self.sinh_tham_so_mat_cau_biet_tam_va_giao_tuyen()
        elif self.question_type == 10:
            self.sinh_tham_so_mat_cau_ngoai_tiep_tu_dien()
        elif self.question_type == 11:
            self.sinh_tham_so_mat_cau_di_qua_2_diem_tam_tren_truc()
        elif self.question_type == 12:
            self.sinh_tham_so_mat_cau_di_qua_3_diem_tam_trong_mp()
        else:
            raise ValueError(f"Chưa implement dạng {self.question_type}")

    def sinh_tham_so_mat_cau_biet_tam_va_giao_tuyen(self):
        """Dạng 1: Mặt cầu biết tâm và điều kiện về giao tuyến với mặt phẳng"""
        # Tâm mặt cầu cho trước
        self.center_x = random.randint(-2, 2)
        self.center_y = random.randint(-2, 2) 
        self.center_z = random.randint(-2, 2)
        
        # Diện tích lớn nhất của giao tuyến chính là diện tích đường tròn lớn
        # Diện tích = π*R² => R² = diện_tích/π
        self.max_area = random.choice([3, 4, 9, 16])  # 3π, 4π, 9π, 16π
        self.R_squared = self.max_area
        self.R = simplify(sqrt(self.R_squared))

    def sinh_tham_so_mat_cau_ngoai_tiep_tu_dien(self):
        """Dạng 2: Mặt cầu ngoại tiếp tứ diện (đi qua 4 điểm)"""
        # Các bộ điểm đẹp được thiết kế để có kết quả tính toán đơn giản
        beautiful_point_sets = [
            [(2,0,0), (0,2,0), (0,0,2), (1,1,1)],
            [(4,0,0), (0,4,0), (0,0,4), (2,2,2)],
            [(3,0,0), (0,3,0), (0,0,3), (1,1,1)],
            [(0,0,0), (2,0,0), (0,2,0), (0,0,2)],
            [(1,1,1), (3,1,1), (1,3,1), (1,1,3)],
            [(2,0,0), (0,2,0), (0,0,4), (1,1,2)],
            [(1,0,0), (0,1,0), (0,0,1), (1,1,1)]
        ]
        
        # Chọn ngẫu nhiên một bộ điểm
        chosen_points = random.choice(beautiful_point_sets)
        self.A, self.B, self.C, self.point_D = chosen_points
        
        # Tính tâm và bán kính bằng phương pháp giải hệ phương trình chính xác
        self.calculate_circumsphere()
        
        # Tạo biểu thức random cho dạng 10 và lưu vào thuộc tính class
        if self.question_type == 10:
            self.random_expression, self.random_expression_value = create_random_sphere_expression(
                self.center_x, self.center_y, self.center_z, self.R_squared
            )

    def sinh_tham_so_mat_cau_di_qua_2_diem_tam_tren_truc(self):
        """Dạng 3: Mặt cầu đi qua 2 điểm và có tâm thuộc trục Oz"""
        # 2 điểm cho trước
        self.A = (random.randint(1, 3), random.randint(-2, 2), random.randint(-2, 2))
        self.B = (random.randint(-2, 2), random.randint(1, 3), random.randint(-3, 3))
        
        # Tâm thuộc trục Oz nên I(0, 0, c)
        # Tính c sao cho IA = IB
        self.calculate_center_on_oz()
        
        # Tạo biểu thức random cho dạng 11
        if self.question_type == 11:
            self.random_expression, self.random_expression_value = create_random_sphere_expression(
                self.center_x, self.center_y, self.center_z, self.R_squared
            )

    def sinh_tham_so_mat_cau_di_qua_3_diem_tam_trong_mp(self):
        """Dạng 4: Mặt cầu đi qua 3 điểm và có tâm thuộc mặt phẳng Oxy"""
        # Sử dụng các bộ điểm được thiết kế sẵn để có kết quả đẹp
        beautiful_point_sets_oxy = [
            [(1, 1, -1), (2, -1, 2), (3, 2, 1)],
            [(2, 0, -2), (0, 2, 1), (-1, -1, 3)],
            [(1, 2, -1), (-1, 1, 2), (2, -2, 1)],
            [(0, 1, -2), (2, 0, 1), (1, -1, 2)],
            [(1, 0, -1), (0, 1, 1), (-1, 0, 2)],
            [(1, 1, 1), (2, 2, -1), (3, 1, 2)],
            [(0, 0, 1), (1, 1, -1), (2, 0, 2)]
        ]
        
        # Chọn ngẫu nhiên một bộ điểm
        chosen_points = random.choice(beautiful_point_sets_oxy)
        self.A, self.B, self.C = chosen_points
        
        # Tâm thuộc mặt phẳng Oxy nên I(a, b, 0)
        # Tính a, b sao cho IA = IB = IC
        self.calculate_center_in_oxy()
        
        # Tạo biểu thức random cho dạng 12
        if self.question_type == 12:
            self.random_expression, self.random_expression_value = create_random_sphere_expression(
                self.center_x, self.center_y, self.center_z, self.R_squared
            )

    def tao_loi_giai_mat_cau_biet_tam_va_giao_tuyen(self):
        """Lời giải ví dụ 9: Mặt cầu biết tâm và điều kiện giao tuyến"""
        center_x_latex = self.format_sympy_to_latex(self.center_x)
        center_y_latex = self.format_sympy_to_latex(self.center_y)
        center_z_latex = self.format_sympy_to_latex(self.center_z)
        r_latex = self.format_sympy_to_latex(self.R)
        max_area_latex = self.format_sympy_to_latex(self.max_area)
        
        solution = f"""
Dữ kiện: Mặt cầu \\((S)\\) có tâm \\(I({center_x_latex}; {center_y_latex}; {center_z_latex})\\) và diện tích lớn nhất của giao tuyến với mặt phẳng là \\({max_area_latex}\\pi\\)

Bước 1: Phân tích điều kiện

Giao tuyến của mặt cầu với mặt phẳng là một đường tròn. Diện tích lớn nhất của giao tuyến đạt được khi mặt phẳng đi qua tâm mặt cầu, lúc này giao tuyến là đường tròn lớn có bán kính bằng bán kính mặt cầu.

Bước 2: Tính bán kính mặt cầu

Diện tích đường tròn lớn: \\(S = \\pi R^2\\)

Từ điều kiện: \\(\\pi R^2 = {max_area_latex}\\pi\\)

\\[\\Rightarrow R^2 = {max_area_latex}\\]

\\[\\Leftrightarrow R = {r_latex}\\]

Bước 3: Viết phương trình mặt cầu

\\[(x - ({center_x_latex}))^2 + (y - ({center_y_latex}))^2 + (z - ({center_z_latex}))^2 = ({r_latex})^2\\]

\\[\\Leftrightarrow {self.build_standard_equation()}\\]

Vậy phương trình mặt cầu \\((S)\\) là: \\({self.build_standard_equation()}\\).
"""
        return solution

    def tao_loi_giai_mat_cau_ngoai_tiep_tu_dien(self):
        """Lời giải ví dụ 10: Mặt cầu ngoại tiếp tứ diện"""
        x1, y1, z1 = self.A
        x2, y2, z2 = self.B
        x3, y3, z3 = self.C
        x4, y4, z4 = self.point_D
        
        center_x_latex = self.format_sympy_to_latex(self.center_x)
        center_y_latex = self.format_sympy_to_latex(self.center_y)
        center_z_latex = self.format_sympy_to_latex(self.center_z)
        r_latex = self.format_sympy_to_latex(self.R)
        
        # Tạo biểu thức random giống như trong câu hỏi
        expression = self.random_expression
        correct_value_latex = self.format_sympy_to_latex(self.random_expression_value)
        
        # Tính các hệ số cho hệ phương trình
        # Phương trình 1: IA² = IB²
        coeff1_a = 2*(x2-x1)
        coeff1_b = 2*(y2-y1) 
        coeff1_c = 2*(z2-z1)
        const1 = (x2*x2 + y2*y2 + z2*z2) - (x1*x1 + y1*y1 + z1*z1)
        
        # Phương trình 2: IA² = IC²
        coeff2_a = 2*(x3-x1)
        coeff2_b = 2*(y3-y1)
        coeff2_c = 2*(z3-z1)
        const2 = (x3*x3 + y3*y3 + z3*z3) - (x1*x1 + y1*y1 + z1*z1)
        
        # Phương trình 3: IA² = ID²
        coeff3_a = 2*(x4-x1)
        coeff3_b = 2*(y4-y1)
        coeff3_c = 2*(z4-z1)
        const3 = (x4*x4 + y4*y4 + z4*z4) - (x1*x1 + y1*y1 + z1*z1)
        
        # Định dạng các phương trình đẹp (bỏ hạng tử có hệ số 0)
        eq1 = self.format_linear_equation(coeff1_a, coeff1_b, coeff1_c, const1)
        eq2 = self.format_linear_equation(coeff2_a, coeff2_b, coeff2_c, const2)
        eq3 = self.format_linear_equation(coeff3_a, coeff3_b, coeff3_c, const3)
        
        solution = f"""
Dữ kiện: Bốn điểm \\(A({x1}; {y1}; {z1})\\), \\(B({x2}; {y2}; {z2})\\), \\(C({x3}; {y3}; {z3})\\), \\(D({x4}; {y4}; {z4})\\)

Bước 1: Thiết lập điều kiện

Mặt cầu ngoại tiếp tứ diện \\(ABCD\\) có phương trình \\((x-a)^2 + (y-b)^2 + (z-c)^2 = R^2\\)

Điều kiện: \\(IA = IB = IC = ID = R\\) với \\(I(a; b; c)\\) là tâm mặt cầu.

Bước 2: Thiết lập hệ phương trình

Từ điều kiện \\(IA^2 = IB^2\\):
\\[({x1}-a)^2 + ({y1}-b)^2 + ({z1}-c)^2 = ({x2}-a)^2 + ({y2}-b)^2 + ({z2}-c)^2\\]
\\[\\Leftrightarrow {eq1}\\]

Từ điều kiện \\(IA^2 = IC^2\\):
\\[({x1}-a)^2 + ({y1}-b)^2 + ({z1}-c)^2 = ({x3}-a)^2 + ({y3}-b)^2 + ({z3}-c)^2\\]
\\[\\Leftrightarrow {eq2}\\]

Từ điều kiện \\(IA^2 = ID^2\\):
\\[({x1}-a)^2 + ({y1}-b)^2 + ({z1}-c)^2 = ({x4}-a)^2 + ({y4}-b)^2 + ({z4}-c)^2\\]
\\[\\Leftrightarrow {eq3}\\]

Bước 3: Hệ phương trình tuyến tính

\\[\\begin{{cases}}
{eq1} \\\\
{eq2} \\\\
{eq3}
\\end{{cases}}\\]

\\[\\Leftrightarrow \\begin{{cases}}
a = {center_x_latex} \\\\
b = {center_y_latex} \\\\
c = {center_z_latex}
\\end{{cases}}\\]

\\[\\Rightarrow \\text{{Tâm }} I({center_x_latex}; {center_y_latex}; {center_z_latex})\\]

Bước 4: Tính bán kính

\\[R^2 = IA^2 = ({x1} - {center_x_latex})^2 + ({y1} - {center_y_latex})^2 + ({z1} - {center_z_latex})^2\\]

\\[R^2 = {self.format_sympy_to_latex(self.R_squared)}\\]

\\[\\Rightarrow R = {r_latex}\\]

Kết luận

Mặt cầu cần tìm có tâm \\(I({center_x_latex}; {center_y_latex}; {center_z_latex})\\) và bán kính \\(R = {r_latex}\\).

Với \\(a = {center_x_latex}, b = {center_y_latex}, c = {center_z_latex}, R^2 = {self.format_sympy_to_latex(self.R_squared)}\\), ta có: \\({expression} = {correct_value_latex}\\)
"""
        return solution

    def tao_loi_giai_mat_cau_di_qua_2_diem_tam_tren_truc(self):
        """Lời giải ví dụ 11: Mặt cầu đi qua 2 điểm và tâm thuộc trục Oz"""
        x1, y1, z1 = self.A
        x2, y2, z2 = self.B
        
        center_x_latex = self.format_sympy_to_latex(self.center_x)
        center_y_latex = self.format_sympy_to_latex(self.center_y)
        center_z_latex = self.format_sympy_to_latex(self.center_z)
        r_squared_latex = self.format_sympy_to_latex(self.R_squared)
        
        # Tạo biểu thức random giống như trong câu hỏi
        expression = self.random_expression
        correct_value_latex = self.format_sympy_to_latex(self.random_expression_value)
        
        solution = f"""
Dữ kiện: \\(A({x1}; {y1}; {z1})\\), \\(B({x2}; {y2}; {z2})\\) và tâm \\(I\\) thuộc trục \\(Oz\\)

Bước 1: Thiết lập tọa độ tâm

Vì tâm \\(I\\) thuộc trục \\(Oz\\) nên \\(I(0; 0; c)\\)

Bước 2: Sử dụng điều kiện \\(IA = IB\\)

\\[IA^2 = {x1}^2 + {y1}^2 + ({z1} - c)^2\\]

\\[IB^2 = {x2}^2 + {y2}^2 + ({z2} - c)^2\\]

Từ \\(IA^2 = IB^2\\):
\\[{x1}^2 + {y1}^2 + ({z1} - c)^2 = {x2}^2 + {y2}^2 + ({z2} - c)^2\\]

Bước 3: Giải phương trình tìm \\(c\\)

\\[{x1**2 + y1**2 + z1**2} - 2 \\cdot {z1} \\cdot c = {x2**2 + y2**2 + z2**2} - 2 \\cdot {z2} \\cdot c\\]

\\[\\Leftrightarrow ({z2} - {z1}) \\cdot 2c = {x2**2 + y2**2 + z2**2} - {x1**2 + y1**2 + z1**2}\\]

\\[\\Leftrightarrow c = {center_z_latex}\\]

Bước 4: Tính bán kính

\\[R^2 = IA^2 = {x1}^2 + {y1}^2 + ({z1} - {center_z_latex})^2 = {r_squared_latex}\\]

\\[\\Rightarrow R = {self.format_sympy_to_latex(self.R)}\\]

Kết luận

Mặt cầu cần tìm có tâm \\(I({center_x_latex}; {center_y_latex}; {center_z_latex})\\) và bán kính \\(R = {self.format_sympy_to_latex(self.R)}\\).

Với \\(a = {center_x_latex}, b = {center_y_latex}, c = {center_z_latex}, R^2 = {r_squared_latex}\\), ta có: \\({expression} = {correct_value_latex}\\)
"""
        return solution

    def tao_loi_giai_mat_cau_di_qua_3_diem_tam_trong_mp(self):
        """Lời giải ví dụ 12: Mặt cầu đi qua 3 điểm và tâm thuộc mặt phẳng Oxy"""
        x1, y1, z1 = self.A
        x2, y2, z2 = self.B
        x3, y3, z3 = self.C
        
        center_x_latex = self.format_sympy_to_latex(self.center_x)
        center_y_latex = self.format_sympy_to_latex(self.center_y)
        center_z_latex = self.format_sympy_to_latex(self.center_z)
        r_squared_latex = self.format_sympy_to_latex(self.R_squared)
        
        # Tạo biểu thức random giống như trong câu hỏi
        expression = self.random_expression
        correct_value_latex = self.format_sympy_to_latex(self.random_expression_value)
        
        # Tính các hệ số cho hệ phương trình
        coeff1_a = 2 * (x2 - x1)
        coeff1_b = 2 * (y2 - y1)
        const1 = (x2*x2 + y2*y2 + z2*z2) - (x1*x1 + y1*y1 + z1*z1)
        
        coeff2_a = 2 * (x3 - x1)
        coeff2_b = 2 * (y3 - y1)
        const2 = (x3*x3 + y3*y3 + z3*z3) - (x1*x1 + y1*y1 + z1*z1)
        
        # Định dạng các phương trình
        eq1 = f"{coeff1_a}a + {coeff1_b}b = {const1}" if coeff1_b >= 0 else f"{coeff1_a}a {coeff1_b}b = {const1}"
        eq2 = f"{coeff2_a}a + {coeff2_b}b = {const2}" if coeff2_b >= 0 else f"{coeff2_a}a {coeff2_b}b = {const2}"
        
        solution = f"""
Dữ kiện: \\(A({x1}; {y1}; {z1})\\), \\(B({x2}; {y2}; {z2})\\), \\(C({x3}; {y3}; {z3})\\) và tâm \\(I \\in (Oxy)\\)

Bước 1: Thiết lập tọa độ tâm

Vì tâm \\(I\\) thuộc mặt phẳng \\(Oxy\\) nên \\(I(a; b; 0)\\)

Bước 2: Thiết lập hệ phương trình từ điều kiện \\(IA = IB = IC\\)

Từ điều kiện \\(IA^2 = IB^2\\):
\\[(a - {x1})^2 + (b - {y1})^2 + {z1}^2 = (a - {x2})^2 + (b - {y2})^2 + {z2}^2\\]

Rút gọn:
\\[{coeff1_a}a + {coeff1_b}b = {const1}\\]

Từ điều kiện \\(IA^2 = IC^2\\):
\\[(a - {x1})^2 + (b - {y1})^2 + {z1}^2 = (a - {x3})^2 + (b - {y3})^2 + {z3}^2\\]

Rút gọn:
\\[{coeff2_a}a + {coeff2_b}b = {const2}\\]

Bước 3: Giải hệ phương trình tuyến tính

\\[\\begin{{cases}}
{eq1} \\\\
{eq2}
\\end{{cases}}\\]

\\[\\Rightarrow \\begin{{cases}}
a = {center_x_latex} \\\\
b = {center_y_latex}
\\end{{cases}}\\]

\\[\\Rightarrow \\text{{Tâm }} I({center_x_latex}; {center_y_latex}; 0)\\]

Bước 4: Tính bán kính

\\[R^2 = IA^2 = ({center_x_latex} - {x1})^2 + ({center_y_latex} - {y1})^2 + {z1}^2 = {r_squared_latex}\\]

\\[\\Rightarrow R = {self.format_sympy_to_latex(self.R)}\\]

Kết luận

Mặt cầu cần tìm có tâm \\(I({center_x_latex}; {center_y_latex}; {center_z_latex})\\) và bán kính \\(R = {self.format_sympy_to_latex(self.R)}\\).

Với \\(a = {center_x_latex}, b = {center_y_latex}, c = {center_z_latex}, R^2 = {r_squared_latex}\\), ta có: \\({expression} = {correct_value_latex}\\)
"""
        return solution


# =============================
# GENERATOR CHÍNH
# =============================
class SphereGenerator:
    @classmethod
    def generate_single_mixed_question(cls, question_number: int = 1) -> Tuple[str, List[bool]]:
        """Tạo một câu hỏi ĐÚNG/SAI với 4 mệnh đề từ 4 dạng khác nhau"""
        # Tạo 4 bài toán khác nhau theo 4 dạng mới
        statements_all = []
        solutions_all = []
        
        for qtype in [9, 10, 11, 12]:
            q = SphereQuestion()
            q.question_type = qtype
            # Gọi generate_parameters để sinh tham số theo từng dạng mới
            q.generate_parameters()
            
            # Tạo mệnh đề cho từng dạng mới
            if qtype == 9:
                # Dạng 9: Mặt cầu biết tâm và giao tuyến
                center_x_latex = q.format_sympy_to_latex(q.center_x)
                center_y_latex = q.format_sympy_to_latex(q.center_y)
                center_z_latex = q.format_sympy_to_latex(q.center_z)
                r_squared_latex = q.format_sympy_to_latex(q.R_squared)
                equation = q.build_standard_equation()
                full_stmt = f"Mặt cầu có tâm \\(I({center_x_latex}; {center_y_latex}; {center_z_latex})\\) và diện tích giao tuyến lớn nhất \\({q.max_area}\\pi\\) có phương trình \\({equation}\\)"
                is_correct = True
                
            elif qtype == 10:
                # Dạng 10: Mặt cầu ngoại tiếp tứ diện
                x1, y1, z1 = q.A
                x2, y2, z2 = q.B
                x3, y3, z3 = q.C  
                x4, y4, z4 = q.point_D
                # Sử dụng biểu thức random - luôn tạo mệnh đề đúng trước
                expression = q.random_expression
                correct_value_latex = q.format_sympy_to_latex(q.random_expression_value)
                full_stmt = f"Mặt cầu ngoại tiếp tứ diện với các đỉnh \\(A({x1}; {y1}; {z1})\\), \\(B({x2}; {y2}; {z2})\\), \\(C({x3}; {y3}; {z3})\\), \\(D({x4}; {y4}; {z4})\\). Mặt cầu có tâm \\(I(a,b,c)\\) và bán kính \\(R\\), khi đó \\({expression} = {correct_value_latex}\\)"
                is_correct = True
                
            elif qtype == 11:
                # Dạng 11: Mặt cầu đi qua 2 điểm, tâm trên trục Oz
                x1, y1, z1 = q.A
                x2, y2, z2 = q.B
                # Sử dụng biểu thức random thay vì phương trình
                expression = q.random_expression
                correct_value_latex = q.format_sympy_to_latex(q.random_expression_value)
                full_stmt = f"Mặt cầu đi qua \\(A({x1}; {y1}; {z1})\\), \\(B({x2}; {y2}; {z2})\\) và có tâm I thuộc trục \\(Oz\\). Mặt cầu có tâm \\(I(a,b,c)\\) và bán kính \\(R\\), khi đó \\({expression} = {correct_value_latex}\\)"
                is_correct = True
                
            elif qtype == 12:
                # Dạng 12: Mặt cầu đi qua 3 điểm, tâm trong Oxy
                x1, y1, z1 = q.A
                x2, y2, z2 = q.B
                x3, y3, z3 = q.C
                # Sử dụng biểu thức random thay vì phương trình
                expression = q.random_expression
                correct_value_latex = q.format_sympy_to_latex(q.random_expression_value)
                full_stmt = f"Mặt cầu đi qua \\(A({x1}; {y1}; {z1})\\), \\(B({x2}; {y2}; {z2})\\), \\(C({x3}; {y3}; {z3})\\) và tâm \\(I \\in (Oxy)\\). Mặt cầu có tâm \\(I(a,b,c)\\) và bán kính \\(R\\), khi đó \\({expression} = {correct_value_latex}\\)"
                is_correct = True
            
            statements_all.append((full_stmt, is_correct))
            solutions_all.append(q.generate_solution())
        
        # Chọn ngẫu nhiên 1-2 mệnh đề để làm sai, còn lại để đúng
        num_correct = random.choice([1, 2])  # 1 hoặc 2 mệnh đề đúng
        correct_indices = random.sample(range(4), num_correct)
        
        # Cập nhật trạng thái đúng/sai cho các mệnh đề
        for i in range(4):
            stmt, _ = statements_all[i]
            if i in correct_indices:
                statements_all[i] = (stmt, True)  # Mệnh đề đúng - sẽ có dấu *
            else:
                # Làm sai mệnh đề này
                wrong_stmt = cls.make_statement_wrong(stmt, i)
                statements_all[i] = (wrong_stmt, False)  # Mệnh đề sai - không có dấu *
        
        # Tạo nội dung câu hỏi
        content = f"Câu {question_number}: Trong các mệnh đề dưới đây, mệnh đề nào đúng?\n\n"
        
        correct_answers = []
        for i, (stmt, is_correct) in enumerate(statements_all):
            marker = "*" if is_correct else ""  # Chỉ mệnh đề đúng có dấu *
            letter = chr(ord('a') + i)  # a, b, c, d
            
            content += f"{marker}{letter}) {stmt}.\n\n"
            correct_answers.append(is_correct)
        
        # Thêm phần lời giải
        content += "Lời giải:\n\n"
        for i, solution in enumerate(solutions_all):
            letter = chr(ord('a') + i)
            content += f"{letter}) {solution}\n\n"
        
        return content, correct_answers

    @staticmethod
    def make_statement_wrong(stmt: str, index: int) -> str:
        """Biến đổi mệnh đề đúng thành mệnh đề sai"""
        # Xử lý biểu thức random từ create_random_sphere_expression
        if "khi đó" in stmt and "=" in stmt:
            import re
            # Tìm phần "= giá_trị" ở cuối mệnh đề
            # Có thể là số nguyên, phân số, hoặc căn thức
            pattern_equals = r'= ([^.]+)(?=\\.)'  # Tìm từ = đến trước dấu .
            match = re.search(pattern_equals, stmt)
            if match:
                original_value = match.group(1).strip()
                # Tạo giá trị sai đơn giản
                if original_value.lstrip('-').isdigit():
                    # Số nguyên (có thể âm)
                    original_num = int(original_value)
                    wrong_value = original_num + random.choice([-2, -1, 1, 2])
                    return stmt.replace(f"= {original_value}", f"= {wrong_value}")
                elif "\\frac" in original_value:
                    # Phân số - thay đổi tử số
                    frac_pattern = r'\\frac\{(-?\d+)\}\{(\d+)\}'
                    frac_match = re.search(frac_pattern, original_value)
                    if frac_match:
                        num, den = frac_match.groups()
                        new_num = int(num) + random.choice([-1, 1])
                        wrong_value = original_value.replace(f"\\frac{{{num}}}{{{den}}}", f"\\frac{{{new_num}}}{{{den}}}")
                        return stmt.replace(f"= {original_value}", f"= {wrong_value}")
                else:
                    # Trường hợp khác - thử tìm số trong biểu thức và thay đổi
                    number_pattern = r'(-?\d+)'
                    numbers = re.findall(number_pattern, original_value)
                    if numbers:
                        # Thay đổi số đầu tiên tìm được
                        old_num = numbers[0]
                        new_num = int(old_num) + random.choice([-1, 1])
                        wrong_value = original_value.replace(old_num, str(new_num), 1)
                        return stmt.replace(f"= {original_value}", f"= {wrong_value}")
                    else:
                        # Fallback: thêm +1
                        wrong_value = original_value + " + 1"
                        return stmt.replace(f"= {original_value}", f"= {wrong_value}")
        
        if "tâm I(" in stmt and "có phương trình" not in stmt:
            # Trường hợp chỉ nói về tâm (không còn sử dụng)
            import re
            pattern = r'I\(([^;]+); ([^;]+); ([^)]+)\)'
            match = re.search(pattern, stmt)
            if match:
                x, y, z = match.groups()
                try:
                    new_x = int(x) + random.choice([-1, 1])
                    new_y = int(y) + random.choice([-1, 1]) 
                    new_z = int(z) + random.choice([-1, 1])
                    return stmt.replace(f"I({x}; {y}; {z})", f"I({new_x}; {new_y}; {new_z})")
                except:
                    return stmt.replace("tâm I", "tâm J")
        elif "bán kính R = " in stmt:
            # Thay đổi bán kính
            import re
            pattern = r'R = (\d+)'
            match = re.search(pattern, stmt)
            if match:
                r_value = int(match.group(1))
                new_r = r_value + random.choice([-1, 1, 2, -2])
                if new_r <= 0:
                    new_r = 1
                return stmt.replace(f"R = {r_value}", f"R = {new_r}")
        elif "diện tích" in stmt and "π" in stmt:
            # Thay đổi diện tích
            import re
            pattern = r'(\d+)π'
            match = re.search(pattern, stmt)
            if match:
                area_value = int(match.group(1))
                new_area = area_value + random.choice([-1, 1, 2, -2])
                if new_area <= 0:
                    new_area = 1
                return stmt.replace(f"{area_value}π", f"{new_area}π")
        elif "có phương trình" in stmt:
            # Xử lý tất cả các trường hợp có phương trình
            import re
            
            # Xử lý trường hợp phương trình có phân số như \frac{43}{8}
            pattern_frac = r'= \\frac\{(\d+)\}\{(\d+)\}'
            match_frac = re.search(pattern_frac, stmt)
            if match_frac:
                numerator = int(match_frac.group(1))
                denominator = int(match_frac.group(2))
                # Thay đổi tử số
                new_numerator = numerator + random.choice([-1, 1, 2, -2])
                if new_numerator <= 0:
                    new_numerator = 1
                return stmt.replace(f"\\frac{{{numerator}}}{{{denominator}}}", f"\\frac{{{new_numerator}}}{{{denominator}}}")
            
            # Xử lý trường hợp phương trình có số nguyên ở cuối
            pattern_int = r'= (\d+)'
            match_int = re.search(pattern_int, stmt)
            if match_int:
                right_value = int(match_int.group(1))
                new_value = right_value + random.choice([-1, 1, 2, -2])
                if new_value <= 0:
                    new_value = 1
                return stmt.replace(f"= {right_value}", f"= {new_value}")
            
            # Xử lý trường hợp có tâm trong phương trình - thay đổi tọa độ tâm
            if "thuộc trục Oz" in stmt:
                # Dạng 11: thay đổi tọa độ z của tâm hoặc thay "trục Oz" thành "trục Ox"
                if random.choice([True, False]):
                    return stmt.replace("thuộc trục Oz", "thuộc trục Ox")
                else:
                    # Thay đổi một tọa độ trong phương trình (x-0)² -> (x-1)²
                    if "x^2" in stmt:
                        return stmt.replace("x^2", "(x - 1)^2")
                    elif "y^2" in stmt:
                        return stmt.replace("y^2", "(y - 1)^2")
            
            elif "thuộc mặt phẳng Oxy" in stmt:
                # Dạng 12: thay đổi mặt phẳng hoặc tọa độ tâm
                if random.choice([True, False]):
                    return stmt.replace("thuộc mặt phẳng Oxy", "thuộc mặt phẳng Oxz")
                else:
                    # Thay đổi một tọa độ trong phương trình
                    if "(z - 0)" in stmt or "z^2" in stmt:
                        return stmt.replace("z^2", "(z - 1)^2")
            
            # Trường hợp chung: thay đổi một điểm trong mệnh đề
            patterns = [r'A\(([^;]+); ([^;]+); ([^)]+)\)', r'B\(([^;]+); ([^;]+); ([^)]+)\)', r'C\(([^;]+); ([^;]+); ([^)]+)\)']
            for pattern in patterns:
                match = re.search(pattern, stmt)
                if match:
                    point_letter = pattern[0]  # A, B, hoặc C
                    x, y, z = match.groups()
                    try:
                        new_x = int(x) + random.choice([-1, 1])
                        new_y = int(y) + random.choice([-1, 1])
                        new_z = int(z) + random.choice([-1, 1])
                        return stmt.replace(f"{point_letter}({x}; {y}; {z})", f"{point_letter}({new_x}; {new_y}; {new_z})")
                    except:
                        continue
                
        elif "ngoại tiếp tứ diện" in stmt and "có phương trình" in stmt:
            # Trường hợp đặc biệt cho mặt cầu ngoại tiếp tứ diện - thay đổi một điểm đỉnh
            import re
            # Thay đổi tọa độ của điểm đầu tiên A
            pattern = r'A\((\d+); (\d+); (\d+)\)'
            match = re.search(pattern, stmt)
            if match:
                x, y, z = match.groups()
                new_x = int(x) + random.choice([-1, 1])
                new_y = int(y) + random.choice([-1, 1])
                new_z = int(z) + random.choice([-1, 1])
                return stmt.replace(f"A({x}; {y}; {z})", f"A({new_x}; {new_y}; {new_z})")
                
        elif "thuộc trục Oz" in stmt:
            return stmt.replace("thuộc trục Oz", "thuộc trục Ox")
        elif "thuộc mặt phẳng Oxy" in stmt:
            return stmt.replace("thuộc mặt phẳng Oxy", "thuộc mặt phẳng Oxz")
        
        return stmt

    @classmethod
    def generate_multiple_questions(cls, num_questions: int = 5) -> List[str]:
        questions = []
        for i in range(1, num_questions + 1):
            content, _ = cls.generate_single_mixed_question(i)
            questions.append(content)
        return questions

    @staticmethod
    def create_latex_document(questions_data, title: str = "Bài tập về Mặt cầu") -> str:
        header = r"""
\documentclass[a4paper,12pt]{article}
\usepackage{amsmath}
\usepackage{mathtools}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage{tikz}
\usepackage{tkz-tab}
\usepackage{tkz-euclide}
\usetikzlibrary{calc,decorations.pathmorphing,decorations.pathreplacing}
\begin{document}
\title{%s}
\maketitle
""" % title
        footer = r"\end{document}"
        
        body = "\n\n".join(questions_data)
        
        return header + body + footer

    @classmethod
    def create_latex_file(cls, questions_data, filename: str = "mat_cau_questions.tex",
                         title: str = "Bài tập về Mặt cầu") -> str:
        latex_content = cls.create_latex_document(questions_data, title)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        print(f"Đã tạo file: {filename}")
        return filename


# =============================
# MAIN
# =============================
def main():
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 5
        
        generator = SphereGenerator()
        questions_data = generator.generate_multiple_questions(num_questions)
        
        if not questions_data:
            print("Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)
        
        filename = generator.create_latex_file(questions_data, filename="mat_cau_questions.tex")
        print(f"📄 Biên dịch bằng: xelatex {filename}")
        
    except ValueError:
        print("❌ Lỗi: Vui lòng nhập số câu hỏi hợp lệ")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()