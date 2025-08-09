import random
import sys
from typing import List, Tuple
from sympy import Rational, sqrt, simplify


# =============================
# CLASS TÍNH TOÁN MẶT CẦU
# =============================
class SphereQuestion:
    def __init__(self):
        self.generate_parameters()

    def generate_question_text(self):
        """Tạo nội dung câu hỏi"""
        # Gọi trực tiếp phương thức tương ứng
        if self.question_type == 5:
            return self.tao_cau_hoi_tim_phuong_trinh_khi_biet_tam_ban_kinh()
        elif self.question_type == 6:
            return self.tao_cau_hoi_tim_phuong_trinh_khi_biet_tam_diem()
        elif self.question_type == 7:
            return self.tao_cau_hoi_tim_phuong_trinh_tam_trong_tam()
        elif self.question_type == 8:
            return self.tao_cau_hoi_tim_phuong_trinh_khi_biet_tam_the_tich()
        else:
            raise ValueError(f"Chưa implement câu hỏi dạng {self.question_type}")

    def generate_solution(self):
        """Tạo lời giải"""
        # Gọi trực tiếp phương thức tương ứng
        if self.question_type == 5:
            return self.tao_loi_giai_tim_phuong_trinh_khi_biet_tam_ban_kinh()
        elif self.question_type == 6:
            return self.tao_loi_giai_tim_phuong_trinh_khi_biet_tam_diem()
        elif self.question_type == 7:
            return self.tao_loi_giai_tim_phuong_trinh_tam_trong_tam()
        elif self.question_type == 8:
            return self.tao_loi_giai_tim_phuong_trinh_khi_biet_tam_the_tich()
        else:
            raise ValueError(f"Chưa implement lời giải dạng {self.question_type}")
    
    # =================================================================
    # HELPER FUNCTIONS - ĐƯỢC THIẾT KẾ ĐỂ TÁI SỬ DỤNG CHỌ 17 DẠNG BÀI TOÁN
    # =================================================================
    
    def format_sympy_to_latex(self, expr):
        """Chuyển biểu thức SymPy thành LaTeX đẹp"""
        if isinstance(expr, (int, float)):
            return str(expr)
        elif hasattr(expr, 'p') and hasattr(expr, 'q'):  # Rational number
            if expr.q == 1:
                return str(expr.p)
            else:
                return f"\\frac{{{expr.p}}}{{{expr.q}}}"
        else:
            return str(expr)
    
    def format_term_for_standard_form(self, coefficient, variable):
        """
        Tạo chuỗi cho một hạng tử trong phương trình chuẩn
        VD: format_term_for_standard_form(-2, 'x') → '(x + 2)'
            format_term_for_standard_form(3, 'y') → '(y - 3)'
            format_term_for_standard_form(0, 'z') → 'z'
        """
        if coefficient == 0:
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
            self.question_type = random.choice([5, 6, 7, 8])
        
        # Gọi trực tiếp phương thức tương ứng
        if self.question_type == 5:
            self.sinh_tham_so_tim_phuong_trinh_khi_biet_tam_ban_kinh()
        elif self.question_type == 6:
            self.sinh_tham_so_tim_phuong_trinh_khi_biet_tam_diem()
        elif self.question_type == 7:
            self.sinh_tham_so_tim_phuong_trinh_tam_trong_tam()
        elif self.question_type == 8:
            self.sinh_tham_so_tim_phuong_trinh_khi_biet_tam_the_tich()
        else:
            raise ValueError(f"Chưa implement dạng {self.question_type}")

    def sinh_tham_so_tim_phuong_trinh_khi_biet_tam_ban_kinh(self):
        """Dạng 5: Tìm phương trình khi biết tâm và bán kính"""
        self.center_x = random.randint(-3, 3)
        self.center_y = random.randint(-3, 3)
        self.center_z = random.randint(-3, 3)
        self.R = random.randint(2, 5)
        self.R_squared = self.R ** 2

    def sinh_tham_so_tim_phuong_trinh_khi_biet_tam_diem(self):
        """Dạng 6: Tìm phương trình khi biết tâm và điểm đi qua"""
        self.center_x = random.randint(-2, 2)
        self.center_y = random.randint(-2, 2)
        self.center_z = random.randint(-2, 2)
        
        # Chọn bán kính đẹp trước
        self.R = random.randint(1, 4)
        self.R_squared = self.R**2
        
        # Tạo điểm đi qua với khoảng cách đúng bằng R
        # Cách đơn giản: thay đổi 1 tọa độ để có khoảng cách đẹp
        direction = random.choice(['x', 'y', 'z'])
        if direction == 'x':
            self.point_x = self.center_x + self.R
            self.point_y = self.center_y 
            self.point_z = self.center_z
        elif direction == 'y':
            self.point_x = self.center_x
            self.point_y = self.center_y + self.R
            self.point_z = self.center_z
        else:  # direction == 'z'
            self.point_x = self.center_x
            self.point_y = self.center_y
            self.point_z = self.center_z + self.R

    def sinh_tham_so_tim_phuong_trinh_tam_trong_tam(self):
        """Dạng 7: Tìm phương trình mặt cầu tâm A đi qua trọng tâm tam giác"""
        # Tọa độ 3 đỉnh tam giác
        self.A_x = random.randint(1, 3)
        self.A_y = random.randint(1, 3)
        self.A_z = random.randint(0, 2)
        
        self.B_x = random.randint(-1, 2)
        self.B_y = random.randint(-1, 2)
        self.B_z = random.randint(1, 3)
        
        self.C_x = random.randint(-1, 2)
        self.C_y = random.randint(2, 4)
        self.C_z = random.randint(2, 4)
        
        # Tâm mặt cầu là A
        self.center_x = self.A_x
        self.center_y = self.A_y
        self.center_z = self.A_z
        
        # Trọng tâm tam giác - sử dụng SymPy Rational
        self.G_x = Rational(self.A_x + self.B_x + self.C_x, 3)
        self.G_y = Rational(self.A_y + self.B_y + self.C_y, 3)
        self.G_z = Rational(self.A_z + self.B_z + self.C_z, 3)
        
        # Bán kính = khoảng cách từ A đến G - sử dụng SymPy
        distance_squared = (self.G_x - self.A_x)**2 + (self.G_y - self.A_y)**2 + (self.G_z - self.A_z)**2
        self.R_squared = simplify(distance_squared)
        self.R = sqrt(self.R_squared)

    def sinh_tham_so_tim_phuong_trinh_khi_biet_tam_the_tich(self):
        """Dạng 8: Tìm phương trình khi biết tâm và thể tích"""
        self.center_x = random.randint(-2, 2)
        self.center_y = random.randint(-2, 2)
        self.center_z = random.randint(-2, 2)
        
        # Chọn bán kính đẹp trước, sau đó tính thể tích
        self.R = random.choice([3, 4, 5])
        self.R_squared = self.R**2
        
        # Tính thể tích: V = (4/3)πR³
        # Để có dạng V = (k*π)/3, ta có: (4/3)πR³ = (k*π)/3
        # => k = 4R³
        self.volume = 4 * (self.R**3)

    def tao_cau_hoi_tim_phuong_trinh_khi_biet_tam_ban_kinh(self):
        """Sinh câu hỏi dạng 5: Tìm phương trình khi biết tâm và bán kính"""
        question = f"Phương trình mặt cầu \\((S)\\) có tâm \\(I({self.center_x}; {self.center_y}; {self.center_z})\\), bán kính \\(R = {self.R}\\) là:"
        return question

    def tao_cau_hoi_tim_phuong_trinh_khi_biet_tam_diem(self):
        """Sinh câu hỏi dạng 6: Tìm phương trình khi biết tâm và điểm đi qua"""
        question = f"Phương trình mặt cầu \\((S)\\) có tâm \\(I({self.center_x}; {self.center_y}; {self.center_z})\\) và đi qua điểm \\(A({self.point_x}; {self.point_y}; {self.point_z})\\) là:"
        return question

    def tao_cau_hoi_tim_phuong_trinh_tam_trong_tam(self):
        """Sinh câu hỏi dạng 7: Tìm phương trình mặt cầu tâm A đi qua trọng tâm tam giác"""
        question = f"Cho tam giác \\(ABC\\) có \\(A({self.A_x}; {self.A_y}; {self.A_z})\\), \\(B({self.B_x}; {self.B_y}; {self.B_z})\\), \\(C({self.C_x}; {self.C_y}; {self.C_z})\\). Mặt cầu \\((S)\\) có tâm \\(A\\) và đi qua trọng tâm \\(G\\) của tam giác \\(ABC\\) có phương trình là:"
        return question

    def tao_cau_hoi_tim_phuong_trinh_khi_biet_tam_the_tich(self):
        """Sinh câu hỏi dạng 8: Tìm phương trình khi biết tâm và thể tích"""
        question = f"Cho mặt cầu \\((S)\\) có tâm \\(I({self.center_x}; {self.center_y}; {self.center_z})\\) và thể tích bằng \\(\\frac{{{self.volume}\\pi}}{{3}}\\). Phương trình của \\((S)\\) là:"
        return question

    def generate_statements(self):
        """Tạo 4 mệnh đề độc lập về mặt cầu, mỗi mệnh đề có thể đúng hoặc sai"""
        statements = []
        
        # Chỉ hỗ trợ dạng 5-8
        if self.question_type == 5:
            # Dạng 5: Tìm phương trình khi biết tâm và bán kính
            correct_eq = self.build_standard_equation()
            wrong_eqs = [
                self.build_standard_equation().replace(f"= {self.R_squared}", f"= {self.R}"),  # Nhầm R thành R²
                self.build_standard_equation().replace(f"({self.format_term_for_standard_form(self.center_x, 'x')})", f"({self.format_term_for_standard_form(-self.center_x, 'x')})"),  # Đổi dấu tâm
                self.build_standard_equation().replace(f"= {self.R_squared}", f"= \\sqrt{{{self.R}}}"),  # Nhầm căn
            ]
            statements = [
                (f"\\({correct_eq}\\)", True),
                (f"\\({wrong_eqs[0]}\\)", False),
                (f"\\({wrong_eqs[1]}\\)", False),
                (f"\\({wrong_eqs[2]}\\)", False)
            ]
        elif self.question_type == 6:
            # Dạng 6: Tìm phương trình khi biết tâm và điểm đi qua
            correct_eq = self.build_standard_equation()
            wrong_R_squared = self.R_squared + random.choice([-1, 1, 3, -3])
            wrong_center_x = self.center_x + random.choice([-1, 1])
            
            statements = [
                (f"\\({correct_eq}\\)", True),
                (f"\\({correct_eq.replace(str(self.R_squared), str(wrong_R_squared))}\\)", False),
                (f"\\({correct_eq.replace(str(self.center_x), str(wrong_center_x))}\\)", False),
                (f"\\({correct_eq.replace(str(self.R_squared), str(self.R))}\\)", False)
            ]
        elif self.question_type == 7:
            # Dạng 7: Tìm phương trình mặt cầu tâm A đi qua trọng tâm tam giác
            r_squared_latex = self.format_sympy_to_latex(self.R_squared)
            correct_eq = f"(x - {self.center_x})^2 + (y - {self.center_y})^2 + (z - {self.center_z})^2 = {r_squared_latex}"
            wrong_center_eq = f"(x + {self.center_x})^2 + (y + {self.center_y})^2 + (z - {self.center_z})^2 = {random.randint(4, 9)}"
            wrong_R_eq = f"(x - {self.center_x})^2 + (y - {self.center_y})^2 + (z - {self.center_z})^2 = \\sqrt{{{r_squared_latex}}}"
            
            # Generate a different wrong value for R_squared
            if isinstance(self.R_squared, (int, float)):
                wrong_r2_value = int(self.R_squared) + 1
            else:
                wrong_r2_value = 2  # fallback value
            wrong_R2_eq = f"(x - {self.center_x})^2 + (y - {self.center_y})^2 + (z - {self.center_z})^2 = {wrong_r2_value}"
            
            statements = [
                (f"\\({correct_eq}\\)", True),
                (f"\\({wrong_center_eq}\\)", False),
                (f"\\({wrong_R_eq}\\)", False),
                (f"\\({wrong_R2_eq}\\)", False)
            ]
        elif self.question_type == 8:
            # Dạng 8: Tìm phương trình khi biết tâm và thể tích
            correct_eq = self.build_standard_equation()
            wrong_R_eq = correct_eq.replace(str(self.R_squared), str(self.R))
            wrong_center_eq = correct_eq.replace(f"- {self.center_x}", f"+ {self.center_x}")
            wrong_both_eq = correct_eq.replace(str(self.R_squared), str(self.R**3))
            
            statements = [
                (f"\\({correct_eq}\\)", True),
                (f"\\({wrong_R_eq}\\)", False),
                (f"\\({wrong_center_eq}\\)", False), 
                (f"\\({wrong_both_eq}\\)", False)
            ]
        
        # Random đúng/sai cho một số mệnh đề để tạo độ khó
        randomized_statements = []
        for i, (stmt, is_correct) in enumerate(statements):
            # Một số mệnh đề có thể random đúng/sai
            if i == 2:  # Mệnh đề thứ 3 có thể random
                final_correct = is_correct if random.random() > 0.3 else not is_correct
                if not final_correct and is_correct:
                    stmt = self.make_statement_wrong(stmt, i)
            else:
                final_correct = is_correct
                
            randomized_statements.append((stmt, final_correct))
        
        return randomized_statements

    def make_statement_wrong(self, stmt, index):
        """Biến đổi mệnh đề để thành sai"""
        if "đi qua điểm" in stmt:
            return stmt.replace("A(0; 0; 0)", "A(1; 1; 1)")
        elif "thuộc mặt phẳng" in stmt:
            return stmt.replace("Oxy", "Oxz")
        elif "tiếp xúc" in stmt:
            return stmt.replace("tiếp xúc", "cắt")
        return stmt

    def tao_loi_giai_tim_phuong_trinh_khi_biet_tam_ban_kinh(self):
        """Lời giải dạng 5: Tìm phương trình khi biết tâm và bán kính"""
        solution = f"""
Dữ kiện: Mặt cầu \\((S)\\) có tâm \\(I({self.center_x}; {self.center_y}; {self.center_z})\\), bán kính \\(R = {self.R}\\)

Bước 1: Sử dụng công thức phương trình mặt cầu

Phương trình mặt cầu có tâm \\(I(a; b; c)\\) và bán kính \\(R\\) là:
\\[(x - a)^2 + (y - b)^2 + (z - c)^2 = R^2\\]

Bước 2: Thay số vào công thức

\\[(x - ({self.center_x}))^2 + (y - ({self.center_y}))^2 + (z - ({self.center_z}))^2 = ({self.R})^2\\]

\\[{self.build_standard_equation()}\\]

Vậy phương trình mặt cầu \\((S)\\) là: \\({self.build_standard_equation()}\\).
"""
        return solution

    def tao_loi_giai_tim_phuong_trinh_khi_biet_tam_diem(self):
        """Lời giải dạng 6: Tìm phương trình khi biết tâm và điểm đi qua"""
        solution = f"""
Dữ kiện: Mặt cầu \\((S)\\) có tâm \\(I({self.center_x}; {self.center_y}; {self.center_z})\\) và đi qua điểm \\(A({self.point_x}; {self.point_y}; {self.point_z})\\)

Bước 1: Tính bán kính

Bán kính \\(R = IA = \\sqrt{{(x_A - x_I)^2 + (y_A - y_I)^2 + (z_A - z_I)^2}}\\)

\\[R = \\sqrt{{({self.point_x} - ({self.center_x}))^2 + ({self.point_y} - ({self.center_y}))^2 + ({self.point_z} - ({self.center_z}))^2}}\\]

\\[R = \\sqrt{{{self.R_squared}}} = {self.R}\\]

Bước 2: Viết phương trình mặt cầu

\\[(x - ({self.center_x}))^2 + (y - ({self.center_y}))^2 + (z - ({self.center_z}))^2 = {self.R_squared}\\]

\\[{self.build_standard_equation()}\\]

Vậy phương trình mặt cầu \\((S)\\) là: \\({self.build_standard_equation()}\\).
"""
        return solution

    def tao_loi_giai_tim_phuong_trinh_tam_trong_tam(self):
        """Lời giải dạng 7: Tìm phương trình mặt cầu tâm A đi qua trọng tâm tam giác"""
        # Format coordinates as fractions
        g_x_latex = self.format_sympy_to_latex(self.G_x)
        g_y_latex = self.format_sympy_to_latex(self.G_y)
        g_z_latex = self.format_sympy_to_latex(self.G_z)
        r_squared_latex = self.format_sympy_to_latex(self.R_squared)
        
        solution = f"""
Dữ kiện: Tam giác \\(ABC\\) có \\(A({self.A_x}; {self.A_y}; {self.A_z})\\), \\(B({self.B_x}; {self.B_y}; {self.B_z})\\), \\(C({self.C_x}; {self.C_y}; {self.C_z})\\)
Mặt cầu \\((S)\\) có tâm \\(A\\) và đi qua trọng tâm \\(G\\) của tam giác \\(ABC\\)

Bước 1: Tìm tọa độ trọng tâm \\(G\\)

\\[G\\left(\\frac{{x_A + x_B + x_C}}{{3}}; \\frac{{y_A + y_B + y_C}}{{3}}; \\frac{{z_A + z_B + z_C}}{{3}}\\right)\\]

\\[G\\left(\\frac{{{self.A_x} + {self.B_x} + {self.C_x}}}{{3}}; \\frac{{{self.A_y} + {self.B_y} + {self.C_y}}}{{3}}; \\frac{{{self.A_z} + {self.B_z} + {self.C_z}}}{{3}}\\right)\\]

\\[G({g_x_latex}; {g_y_latex}; {g_z_latex})\\]

Bước 2: Tính bán kính \\(R = AG\\)

\\[R = \\sqrt{{({g_x_latex} - {self.A_x})^2 + ({g_y_latex} - {self.A_y})^2 + ({g_z_latex} - {self.A_z})^2}}\\]

\\[R = \\sqrt{{{r_squared_latex}}}\\]

Bước 3: Viết phương trình mặt cầu

\\[(x - {self.center_x})^2 + (y - {self.center_y})^2 + (z - {self.center_z})^2 = {r_squared_latex}\\]

Vậy phương trình mặt cầu \\((S)\\) là: \\((x - {self.center_x})^2 + (y - {self.center_y})^2 + (z - {self.center_z})^2 = {r_squared_latex}\\).
"""
        return solution

    def tao_loi_giai_tim_phuong_trinh_khi_biet_tam_the_tich(self):
        """Lời giải dạng 8: Tìm phương trình khi biết tâm và thể tích"""
        solution = f"""
Dữ kiện: Mặt cầu \\((S)\\) có tâm \\(I({self.center_x}; {self.center_y}; {self.center_z})\\) và thể tích \\(V = \\frac{{{self.volume}\\pi}}{{3}}\\)

Bước 1: Tính bán kính từ thể tích

Công thức thể tích mặt cầu: \\(V = \\frac{{4}}{{3}}\\pi R^3\\)

\\[\\frac{{{self.volume}\\pi}}{{3}} = \\frac{{4}}{{3}}\\pi R^3\\]

\\[{self.volume} = 4R^3\\]

\\[R^3 = \\frac{{{self.volume}}}{{4}} = {self.volume // 4}\\]

\\[R = {self.R}\\]

Bước 2: Viết phương trình mặt cầu

\\[(x - ({self.center_x}))^2 + (y - ({self.center_y}))^2 + (z - ({self.center_z}))^2 = {self.R_squared}\\]

\\[{self.build_standard_equation()}\\]

Vậy phương trình mặt cầu \\((S)\\) là: \\({self.build_standard_equation()}\\).
"""
        return solution




# =============================
# GENERATOR CHÍNH
# =============================
class SphereGenerator:
    @classmethod
    def create_question(cls, question_type: int) -> 'SphereQuestion':
        """Tạo một câu hỏi dựa trên loại câu hỏi"""
        q = SphereQuestion()
        q.question_type = question_type
        
        if question_type == 5:
            q.sinh_tham_so_tim_phuong_trinh_khi_biet_tam_ban_kinh()
        elif question_type == 6:
            q.sinh_tham_so_tim_phuong_trinh_khi_biet_tam_diem()
        elif question_type == 7:
            q.sinh_tham_so_tim_phuong_trinh_tam_trong_tam()
        elif question_type == 8:
            q.sinh_tham_so_tim_phuong_trinh_khi_biet_tam_the_tich()
        
        return q
    
    @classmethod
    def generate_single_mixed_question(cls, question_number: int = 1) -> Tuple[str, List[bool]]:
        """Tạo một câu hỏi ĐÚNG/SAI với 4 mệnh đề từ 4 dạng 5-8"""
        # Tạo 4 bài toán khác nhau từ 4 dạng 5-8
        statements_all = []
        solutions_all = []
        
        # Sử dụng tất cả 4 dạng 5-8
        selected_types = [5, 6, 7, 8]
        
        for qtype in selected_types:
            q = cls.create_question(question_type=qtype)
            
            # Tạo mệnh đề ĐÚNG và SAI cho từng dạng
            if qtype == 5:
                # Dạng 5: tìm phương trình khi biết tâm và bán kính
                correct_eq = q.build_standard_equation()
                correct_stmt = f"Phương trình mặt cầu có tâm \\(I({q.center_x}; {q.center_y}; {q.center_z})\\), bán kính \\(R = {q.R}\\) là \\({correct_eq}\\)"
                
                # Tạo mệnh đề sai: thay R² bằng R
                wrong_eq = correct_eq.replace(str(q.R_squared), str(q.R))
                wrong_stmt = f"Phương trình mặt cầu có tâm \\(I({q.center_x}; {q.center_y}; {q.center_z})\\), bán kính \\(R = {q.R}\\) là \\({wrong_eq}\\)"
                    
            elif qtype == 6:
                # Dạng 6: tìm phương trình khi biết tâm và điểm đi qua
                correct_eq = q.build_standard_equation()
                correct_stmt = f"Phương trình mặt cầu có tâm \\(I({q.center_x}; {q.center_y}; {q.center_z})\\) đi qua điểm \\(A({q.point_x}; {q.point_y}; {q.point_z})\\) là \\({correct_eq}\\)"
                
                # Tạo mệnh đề sai: thay R² bằng R²+2
                wrong_R_squared = q.R_squared + 2
                wrong_eq = correct_eq.replace(str(q.R_squared), str(wrong_R_squared))
                wrong_stmt = f"Phương trình mặt cầu có tâm \\(I({q.center_x}; {q.center_y}; {q.center_z})\\) đi qua điểm \\(A({q.point_x}; {q.point_y}; {q.point_z})\\) là \\({wrong_eq}\\)"
                    
            elif qtype == 7:
                # Dạng 7: tìm phương trình mặt cầu tâm A đi qua trọng tâm tam giác
                r_squared_latex = q.format_sympy_to_latex(q.R_squared)
                correct_eq = f"(x - {q.center_x})^2 + (y - {q.center_y})^2 + (z - {q.center_z})^2 = {r_squared_latex}"
                correct_stmt = f"Mặt cầu tâm \\(A({q.A_x}; {q.A_y}; {q.A_z})\\) đi qua trọng tâm tam giác \\(ABC\\) có phương trình \\({correct_eq}\\)"
                
                # Tạo mệnh đề sai: thay R² bằng 2 (giá trị cố định khác)
                wrong_eq = f"(x - {q.center_x})^2 + (y - {q.center_y})^2 + (z - {q.center_z})^2 = 2"
                wrong_stmt = f"Mặt cầu tâm \\(A({q.A_x}; {q.A_y}; {q.A_z})\\) đi qua trọng tâm tam giác \\(ABC\\) có phương trình \\({wrong_eq}\\)"
                    
            elif qtype == 8:
                # Dạng 8: tìm phương trình khi biết tâm và thể tích
                correct_eq = q.build_standard_equation()
                correct_stmt = f"Mặt cầu có tâm \\(I({q.center_x}; {q.center_y}; {q.center_z})\\) và thể tích \\(V = \\frac{{{q.volume}\\pi}}{{3}}\\) có phương trình \\({correct_eq}\\)"
                
                # Tạo mệnh đề sai: thay R² bằng R
                wrong_eq = correct_eq.replace(str(q.R_squared), str(q.R))
                wrong_stmt = f"Mặt cầu có tâm \\(I({q.center_x}; {q.center_y}; {q.center_z})\\) và thể tích \\(V = \\frac{{{q.volume}\\pi}}{{3}}\\) có phương trình \\({wrong_eq}\\)"
            
            # Luôn luôn tạo cả câu đúng và sai, rồi sẽ chọn random
            statements_all.append((correct_stmt, True, wrong_stmt, False))
            solutions_all.append(q.generate_solution())
        
        # Chọn đúng 1 vị trí để làm đúng, các vị trí khác làm sai
        correct_index = random.randint(0, 3)
        final_statements = []
        
        for i in range(4):
            correct_stmt, _, wrong_stmt, _ = statements_all[i]
            if i == correct_index:
                final_statements.append((correct_stmt, True))
            else:
                final_statements.append((wrong_stmt, False))
        
        statements_all = final_statements
        
        # Tạo nội dung câu hỏi
        content = f"Câu {question_number}: Trong các mệnh đề dưới đây, mệnh đề nào đúng?\n\n"
        
        correct_answers = []
        for i, (stmt, is_correct) in enumerate(statements_all):
            marker = "*" if is_correct else ""
            letter = chr(ord('a') + i)  # a, b, c, d
            
            content += f"{marker}{letter}) {stmt}.\n\n"
            correct_answers.append(is_correct)
        
        # Thêm phần lời giải
        content += "Lời giải:\n\n"
        for i, solution in enumerate(solutions_all):
            letter = chr(ord('a') + i)
            content += f"{letter}) {solution}\n\n"
        
        return content, correct_answers

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