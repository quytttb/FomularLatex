import random
import sys
from typing import List, Tuple


# =============================
# CLASS TÍNH TOÁN MẶT CẦU
# =============================
class SphereQuestion:
    def __init__(self):
        self.generate_parameters()

    def generate_question_text(self):
        """Tạo nội dung câu hỏi"""
        # Gọi trực tiếp phương thức tương ứng
        if self.question_type == 13:
            return self.tao_cau_hoi_dang_13_tiep_xuc_truc_hoanh()
        elif self.question_type == 14:
            return self.tao_cau_hoi_dang_14_tiep_xuc_mat_phang_oxy()
        elif self.question_type == 15:
            return self.tao_cau_hoi_dang_15_doi_xung_qua_mat_phang()
        elif self.question_type == 16:
            return self.tao_cau_hoi_dang_16_cat_truc_tam_giac_vuong()
        elif self.question_type == 17:
            return self.tao_cau_hoi_dang_17_cat_mat_phang_duong_tron()
        else:
            raise ValueError(f"Chưa implement câu hỏi dạng {self.question_type}")

    def generate_solution(self):
        """Tạo lời giải"""
        # Gọi trực tiếp phương thức tương ứng
        if self.question_type == 13:
            return self.tao_loi_giai_dang_13_tiep_xuc_truc_hoanh()
        elif self.question_type == 14:
            return self.tao_loi_giai_dang_14_tiep_xuc_mat_phang_oxy()
        elif self.question_type == 15:
            return self.tao_loi_giai_dang_15_doi_xung_qua_mat_phang()
        elif self.question_type == 16:
            return self.tao_loi_giai_dang_16_cat_truc_tam_giac_vuong()
        elif self.question_type == 17:
            return self.tao_loi_giai_dang_17_cat_mat_phang_duong_tron()
        else:
            raise ValueError(f"Chưa implement lời giải dạng {self.question_type}")
    
    # =================================================================
    # HELPER FUNCTIONS - ĐƯỢC THIẾT KẾ ĐỂ TÁI SỬ DỤNG CHO 17 DẠNG BÀI TOÁN
    # =================================================================
    
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
        x_term = self.format_term_for_standard_form(self.a, 'x')
        y_term = self.format_term_for_standard_form(self.b, 'y')
        z_term = self.format_term_for_standard_form(self.c, 'z')
        
        return f"{x_term}^2 + {y_term}^2 + {z_term}^2 = {self.R_squared}"
    
    def simplify_circumference_expression(self, r_squared):
        """
        Rút gọn biểu thức chu vi 2π√(r_squared) về dạng đơn giản nhất
        VD: 2π√27 = 2π·3√3 = 6π√3
        """
        # Tìm thừa số chính phương lớn nhất
        perfect_square_factor = 1
        remaining_factor = r_squared
        
        # Kiểm tra các số chính phương từ 4, 9, 16, 25, ...
        i = 2
        while i * i <= r_squared:
            while remaining_factor % (i * i) == 0:
                perfect_square_factor *= i
                remaining_factor //= (i * i)
            i += 1
        
        # Tính hệ số cuối cùng
        final_coefficient = 2 * perfect_square_factor
        
        if remaining_factor == 1:
            # Trường hợp số chính phương hoàn toàn: 2π√16 = 8π
            return f"{final_coefficient}\\pi"
        else:
            # Trường hợp có căn: 2π√27 = 6π√3
            return f"{final_coefficient}\\pi\\sqrt{{{remaining_factor}}}"
    
    # =================================================================
    # END HELPER FUNCTIONS
    # =================================================================

    def generate_parameters(self):
        """Sinh các tham số ngẫu nhiên cho câu hỏi mặt cầu"""
        # Chỉ random question_type khi chưa được set
        if not hasattr(self, 'question_type'):
            self.question_type = random.choice([13, 14, 15, 16, 17])
        
        # Gọi trực tiếp phương thức tương ứng
        if self.question_type == 13:
            self.sinh_tham_so_dang_13_tiep_xuc_truc_hoanh()
        elif self.question_type == 14:
            self.sinh_tham_so_dang_14_tiep_xuc_mat_phang_oxy()
        elif self.question_type == 15:
            self.sinh_tham_so_dang_15_doi_xung_qua_mat_phang()
        elif self.question_type == 16:
            self.sinh_tham_so_dang_16_cat_truc_tam_giac_vuong()
        elif self.question_type == 17:
            self.sinh_tham_so_dang_17_cat_mat_phang_duong_tron()
        else:
            raise ValueError(f"Chưa implement dạng {self.question_type}")

    def sinh_tham_so_dang_13_tiep_xuc_truc_hoanh(self):
        """Dạng 13: Mặt cầu có tâm cho trước và tiếp xúc với trục hoành"""
        # Sinh tâm mặt cầu
        self.a = random.randint(-3, 3)
        self.b = random.randint(-3, 3)  
        self.c = random.randint(-3, 3)
        
        # Khoảng cách từ tâm đến trục hoành (Ox) = sqrt(b² + c²)
        self.R = (self.b**2 + self.c**2)**0.5
        self.R_squared = self.b**2 + self.c**2
        
        # Tạo phương trình sai để test
        self.wrong_R_squared = self.R_squared + random.choice([-2, -1, 1, 2, 4])

    def sinh_tham_so_dang_14_tiep_xuc_mat_phang_oxy(self):
        """Dạng 14: Mặt cầu có tâm cho trước và tiếp xúc với mặt phẳng Oxy"""
        # Sinh tâm mặt cầu  
        self.a = random.randint(-3, 3)
        self.b = random.randint(-3, 3)
        self.c = random.randint(1, 5)  # c > 0 để có khoảng cách dương
        
        # Khoảng cách từ tâm đến mặt phẳng Oxy = |c|
        self.R = abs(self.c)
        self.R_squared = self.c**2
        
        # Tạo phương trình sai để test
        self.wrong_R_squared = self.R_squared + random.choice([-2, -1, 1, 2])

    def sinh_tham_so_dang_15_doi_xung_qua_mat_phang(self):
        """Dạng 15: Mặt cầu đối xứng qua mặt phẳng Oxy"""
        # Sinh mặt cầu gốc
        self.a = random.randint(-5, 5)
        self.b = random.randint(-3, 3)
        self.c = random.randint(1, 5)  # c > 0 để tâm ở phía dương
        self.R = random.randint(2, 4)
        self.R_squared = self.R**2
        
        # Mặt cầu đối xứng qua Oxy: tâm (a, b, -c), cùng bán kính
        self.a_sym = self.a
        self.b_sym = self.b  
        self.c_sym = -self.c
        
        # Tạo đáp án sai để test
        self.wrong_c_sym = self.c  # Sai khi không đổi dấu

    def sinh_tham_so_dang_16_cat_truc_tam_giac_vuong(self):
        """Dạng 16: Mặt cầu cắt trục Ox tạo tam giác vuông tại tâm"""
        # Sinh tâm mặt cầu
        self.a = random.randint(3, 8)
        self.b = random.randint(4, 8)
        self.c = random.randint(5, 10)
        
        # Để tam giác IAB vuông tại I, cần IA ⊥ IB
        # Với A, B trên Ox: A(a-d, 0, 0), B(a+d, 0, 0)
        # IA = (-d, -b, -c), IB = (d, -b, -c)
        # IA·IB = -d² + b² + c² = 0 => d = sqrt(b² + c²)
        
        self.d = (self.b**2 + self.c**2)**0.5
        self.R = (self.d**2 + self.b**2 + self.c**2)**0.5  # = sqrt(2(b² + c²))
        self.R_squared = 2 * (self.b**2 + self.c**2)
        
        # Tạo đáp án sai
        self.wrong_R_squared = self.b**2 + self.c**2  # Thiếu hệ số 2

    def sinh_tham_so_dang_17_cat_mat_phang_duong_tron(self):
        """Dạng 17: Mặt cầu cắt mặt phẳng Oxy tạo đường tròn có chu vi cho trước"""
        # Sinh tâm mặt cầu
        self.a = random.randint(-2, 3)
        self.b = random.randint(-3, 4)
        self.c = random.randint(1, 3)  # c nhỏ hơn để đảm bảo có giao tuyến
        self.R = random.randint(4, 6)  # R lớn hơn c để có giao tuyến
        
        # Đảm bảo R > |c| để có giao tuyến
        if self.R <= abs(self.c):
            self.R = abs(self.c) + random.randint(1, 3)
        
        # Bán kính đường tròn giao tuyến: r = sqrt(R² - c²)  
        self.r_squared = self.R**2 - self.c**2
        self.r = self.r_squared**0.5
        
        # Tạo chu vi rút gọn
        self.circumference_simplified = self.simplify_circumference_expression(self.r_squared)
        
        # Tạo đáp án sai với công thức sai
        wrong_r_squared = self.R**2 + self.c**2
        self.wrong_circumference_simplified = self.simplify_circumference_expression(wrong_r_squared)

    def tao_cau_hoi_chung(self):
        """Sinh câu hỏi chung cho tất cả các dạng"""
        return "Xét tính đúng sai của các mệnh đề sau về mặt cầu:"

    def tao_cau_hoi_dang_13_tiep_xuc_truc_hoanh(self):
        """Sinh câu hỏi dạng 13: Mặt cầu tiếp xúc với trục hoành"""
        return self.tao_cau_hoi_chung()

    def tao_cau_hoi_dang_14_tiep_xuc_mat_phang_oxy(self):
        """Sinh câu hỏi dạng 14: Mặt cầu tiếp xúc với mặt phẳng Oxy"""
        return self.tao_cau_hoi_chung()

    def tao_cau_hoi_dang_15_doi_xung_qua_mat_phang(self):
        """Sinh câu hỏi dạng 15: Mặt cầu đối xứng qua mặt phẳng"""
        return self.tao_cau_hoi_chung()

    def tao_cau_hoi_dang_16_cat_truc_tam_giac_vuong(self):
        """Sinh câu hỏi dạng 16: Mặt cầu cắt trục tạo tam giác vuông"""
        return self.tao_cau_hoi_chung()

    def tao_cau_hoi_dang_17_cat_mat_phang_duong_tron(self):
        """Sinh câu hỏi dạng 17: Mặt cầu cắt mặt phẳng tạo đường tròn"""
        return self.tao_cau_hoi_chung()

    def tao_menh_de_dang_13_tiep_xuc_truc_hoanh(self):
        """Tạo mệnh đề dạng 13: Mặt cầu tiếp xúc với trục hoành"""
        # Tính R đúng cho điều kiện tiếp xúc với trục hoành
        R_correct_squared = self.b**2 + self.c**2
        
        # Tạo phương trình với R đúng hoặc sai
        x_term = self.format_term_for_standard_form(self.a, 'x')
        y_term = self.format_term_for_standard_form(self.b, 'y')
        z_term = self.format_term_for_standard_form(self.c, 'z')
        
        if random.random() > 0.5:
            # Mệnh đề đúng
            equation = f"{x_term}^2 + {y_term}^2 + {z_term}^2 = {R_correct_squared}"
            stmt = f"Phương trình mặt cầu \\((S)\\) có tâm \\(I({self.a}; {self.b}; {self.c})\\) và tiếp xúc với trục hoành là \\({equation}\\)"
            return stmt, True
        else:
            # Mệnh đề sai
            R_wrong_squared = R_correct_squared + random.choice([-3, -2, -1, 1, 2, 3])
            if R_wrong_squared <= 0:
                R_wrong_squared = R_correct_squared + random.choice([1, 2, 3])
            equation = f"{x_term}^2 + {y_term}^2 + {z_term}^2 = {R_wrong_squared}"
            stmt = f"Phương trình mặt cầu \\((S)\\) có tâm \\(I({self.a}; {self.b}; {self.c})\\) và tiếp xúc với trục hoành là \\({equation}\\)"
            return stmt, False

    def tao_menh_de_dang_14_tiep_xuc_mat_phang_oxy(self):
        """Tạo mệnh đề dạng 14: Mặt cầu tiếp xúc với mặt phẳng Oxy"""
        # Tính R đúng cho điều kiện tiếp xúc với mặt phẳng Oxy
        R_correct_squared = self.c**2
        
        # Tạo phương trình với R đúng hoặc sai
        x_term = self.format_term_for_standard_form(self.a, 'x')
        y_term = self.format_term_for_standard_form(self.b, 'y')
        z_term = self.format_term_for_standard_form(self.c, 'z')
        
        if random.random() > 0.5:
            # Mệnh đề đúng
            equation = f"{x_term}^2 + {y_term}^2 + {z_term}^2 = {R_correct_squared}"
            stmt = f"Phương trình mặt cầu \\((S)\\) có tâm \\(I({self.a}; {self.b}; {self.c})\\) và tiếp xúc với mặt phẳng \\((Oxy)\\) là \\({equation}\\)"
            return stmt, True
        else:
            # Mệnh đề sai
            R_wrong_squared = R_correct_squared + random.choice([-2, -1, 1, 2, 4])
            if R_wrong_squared <= 0:
                R_wrong_squared = R_correct_squared + random.choice([1, 2, 4])
            equation = f"{x_term}^2 + {y_term}^2 + {z_term}^2 = {R_wrong_squared}"
            stmt = f"Phương trình mặt cầu \\((S)\\) có tâm \\(I({self.a}; {self.b}; {self.c})\\) và tiếp xúc với mặt phẳng \\((Oxy)\\) là \\({equation}\\)"
            return stmt, False

    def tao_menh_de_dang_15_doi_xung_qua_mat_phang(self):
        """Tạo mệnh đề dạng 15: Mặt cầu đối xứng qua mặt phẳng Oxy"""
        # Tạo phương trình mặt cầu gốc
        x_term = self.format_term_for_standard_form(self.a, 'x')
        y_term = self.format_term_for_standard_form(self.b, 'y')
        z_term = self.format_term_for_standard_form(self.c, 'z')
        orig_equation = f"{x_term}^2 + {y_term}^2 + {z_term}^2 = {self.R_squared}"
        
        # Tạo phương trình mặt cầu đối xứng
        x_term_sym = self.format_term_for_standard_form(self.a_sym, 'x')
        y_term_sym = self.format_term_for_standard_form(self.b_sym, 'y')
        
        if random.random() > 0.5:
            # Mệnh đề đúng
            z_term_sym = self.format_term_for_standard_form(self.c_sym, 'z')
            sym_equation = f"{x_term_sym}^2 + {y_term_sym}^2 + {z_term_sym}^2 = {self.R_squared}"
            stmt = f"Cho mặt cầu \\((S)\\) có phương trình \\({orig_equation}\\). Phương trình mặt cầu \\((S')\\) đối xứng với mặt cầu \\((S)\\) qua mặt phẳng \\((Oxy)\\) là \\({sym_equation}\\)"
            return stmt, True
        else:
            # Mệnh đề sai - không đổi dấu z
            z_term_wrong = self.format_term_for_standard_form(self.c, 'z')
            wrong_equation = f"{x_term_sym}^2 + {y_term_sym}^2 + {z_term_wrong}^2 = {self.R_squared}"
            stmt = f"Cho mặt cầu \\((S)\\) có phương trình \\({orig_equation}\\). Phương trình mặt cầu \\((S')\\) đối xứng với mặt cầu \\((S)\\) qua mặt phẳng \\((Oxy)\\) là \\({wrong_equation}\\)"
            return stmt, False

    def tao_menh_de_dang_16_cat_truc_tam_giac_vuong(self):
        """Tạo mệnh đề dạng 16: Mặt cầu cắt trục tạo tam giác vuông"""
        # Tính R đúng cho điều kiện tam giác vuông
        R_correct_squared = 2 * (self.b**2 + self.c**2)
        
        # Tạo phương trình
        x_term = self.format_term_for_standard_form(self.a, 'x')
        y_term = self.format_term_for_standard_form(self.b, 'y')
        z_term = self.format_term_for_standard_form(self.c, 'z')
        
        if random.random() > 0.5:
            # Mệnh đề đúng
            equation = f"{x_term}^2 + {y_term}^2 + {z_term}^2 = {R_correct_squared}"
            stmt = f"Phương trình của mặt cầu \\((S)\\) có tâm \\(I({self.a}; {self.b}; {self.c})\\) và cắt trục \\(Ox\\) tại hai điểm \\(A\\), \\(B\\) sao cho tam giác \\(IAB\\) vuông tại \\(I\\) là \\({equation}\\)"
            return stmt, True
        else:
            # Mệnh đề sai - thiếu hệ số 2
            R_wrong_squared = self.b**2 + self.c**2
            equation = f"{x_term}^2 + {y_term}^2 + {z_term}^2 = {R_wrong_squared}"
            stmt = f"Phương trình của mặt cầu \\((S)\\) có tâm \\(I({self.a}; {self.b}; {self.c})\\) và cắt trục \\(Ox\\) tại hai điểm \\(A\\), \\(B\\) sao cho tam giác \\(IAB\\) vuông tại \\(I\\) là \\({equation}\\)"
            return stmt, False

    def tao_menh_de_dang_17_cat_mat_phang_duong_tron(self):
        """Tạo mệnh đề dạng 17: Mặt cầu cắt mặt phẳng tạo đường tròn"""
        # Tạo phương trình mặt cầu
        x_term = self.format_term_for_standard_form(self.a, 'x')
        y_term = self.format_term_for_standard_form(self.b, 'y')
        z_term = self.format_term_for_standard_form(self.c, 'z')
        equation = f"{x_term}^2 + {y_term}^2 + {z_term}^2 = {self.R**2}"
        
        if random.random() > 0.5:
            # Mệnh đề đúng - sử dụng chu vi rút gọn
            stmt = f"Khi mặt cầu \\((S)\\) có phương trình \\({equation}\\) cắt mặt phẳng \\((Oxy)\\), giao tuyến thu được là một đường tròn có chu vi bằng \\({self.circumference_simplified}\\)"
            return stmt, True
        else:
            # Mệnh đề sai - sử dụng công thức sai (R² + c² thay vì R² - c²)
            stmt = f"Khi mặt cầu \\((S)\\) có phương trình \\({equation}\\) cắt mặt phẳng \\((Oxy)\\), giao tuyến thu được là một đường tròn có chu vi bằng \\({self.wrong_circumference_simplified}\\)"
            return stmt, False

    def check_point_on_sphere(self, x, y, z):
        """Kiểm tra điểm có thuộc mặt cầu không"""
        distance_sq = (x - self.a)**2 + (y - self.b)**2 + (z - self.c)**2
        return abs(distance_sq - self.R**2) < 0.001
    
    def make_statement_wrong(self, stmt, index):
        """Biến đổi mệnh đề để thành sai"""
        if "đi qua điểm" in stmt:
            return stmt.replace("A(0; 0; 0)", "A(1; 1; 1)")
        elif "thuộc mặt phẳng" in stmt:
            return stmt.replace("Oxy", "Oxz")
        elif "tiếp xúc" in stmt:
            return stmt.replace("tiếp xúc", "cắt")
        return stmt

    def tao_loi_giai_dang_13_tiep_xuc_truc_hoanh(self):
        """Lời giải dạng 13: Mặt cầu tiếp xúc với trục hoành"""
        solution = f"""
Dữ kiện: Mặt cầu có tâm \\(I({self.a}; {self.b}; {self.c})\\) và tiếp xúc với trục hoành

Bước 1: Xác định điều kiện tiếp xúc

Mặt cầu tiếp xúc với trục hoành \\(Ox\\) khi và chỉ khi khoảng cách từ tâm \\(I\\) đến trục \\(Ox\\) bằng bán kính \\(R\\).

Bước 2: Tính khoảng cách từ tâm đến trục hoành

Khoảng cách từ \\(I({self.a}; {self.b}; {self.c})\\) đến trục \\(Ox\\):
\\[d(I, Ox) = \\sqrt{{y_I^2 + z_I^2}} = \\sqrt{{{self.b}^2 + {self.c}^2}} = \\sqrt{{{self.R_squared}}}\\]

Bước 3: Xác định bán kính và phương trình

Do mặt cầu tiếp xúc với trục hoành: \\(R = d(I, Ox) = \\sqrt{{{self.R_squared}}}\\)

Phương trình mặt cầu: \\({self.build_standard_equation()}\\)

Vậy phương trình mặt cầu là \\({self.build_standard_equation()}\\).
"""
        return solution

    def tao_loi_giai_dang_14_tiep_xuc_mat_phang_oxy(self):
        """Lời giải dạng 14: Mặt cầu tiếp xúc với mặt phẳng Oxy"""
        solution = f"""
Dữ kiện: Mặt cầu có tâm \\(I({self.a}; {self.b}; {self.c})\\) và tiếp xúc với mặt phẳng \\((Oxy)\\)

Bước 1: Xác định điều kiện tiếp xúc

Mặt cầu tiếp xúc với mặt phẳng \\((Oxy)\\) khi và chỉ khi khoảng cách từ tâm \\(I\\) đến mặt phẳng \\((Oxy)\\) bằng bán kính \\(R\\).

Bước 2: Tính khoảng cách từ tâm đến mặt phẳng Oxy

Khoảng cách từ \\(I({self.a}; {self.b}; {self.c})\\) đến mặt phẳng \\((Oxy)\\): \\(z = 0\\)
\\[d(I, (Oxy)) = |z_I| = |{self.c}| = {abs(self.c)}\\]

Bước 3: Xác định bán kính và phương trình

Do mặt cầu tiếp xúc với mặt phẳng \\((Oxy)\\): \\(R = |z_I| = {abs(self.c)}\\)

Phương trình mặt cầu: \\({self.build_standard_equation()}\\)

Vậy phương trình mặt cầu là \\({self.build_standard_equation()}\\).
"""
        return solution

    def tao_loi_giai_dang_15_doi_xung_qua_mat_phang(self):
        """Lời giải dạng 15: Mặt cầu đối xứng qua mặt phẳng"""
        x_term_orig = self.format_term_for_standard_form(self.a, 'x')
        y_term_orig = self.format_term_for_standard_form(self.b, 'y')
        z_term_orig = self.format_term_for_standard_form(self.c, 'z')
        orig_equation = f"{x_term_orig}^2 + {y_term_orig}^2 + {z_term_orig}^2 = {self.R_squared}"
        
        x_term_sym = self.format_term_for_standard_form(self.a_sym, 'x')
        y_term_sym = self.format_term_for_standard_form(self.b_sym, 'y')
        z_term_sym = self.format_term_for_standard_form(self.c_sym, 'z')
        sym_equation = f"{x_term_sym}^2 + {y_term_sym}^2 + {z_term_sym}^2 = {self.R_squared}"
        
        solution = f"""
Dữ kiện: Mặt cầu \\((S): {orig_equation}\\) với tâm \\(I({self.a}; {self.b}; {self.c})\\)

Bước 1: Tìm ảnh của tâm qua mặt phẳng Oxy

Đối xứng qua mặt phẳng \\((Oxy)\\): \\((x, y, z) \\mapsto (x, y, -z)\\)

Tâm \\(I({self.a}; {self.b}; {self.c})\\) có ảnh là \\(I'({self.a_sym}; {self.b_sym}; {self.c_sym})\\)

Bước 2: Xác định bán kính mặt cầu đối xứng

Phép đối xứng qua mặt phẳng bảo toàn khoảng cách, nên bán kính không đổi: \\(R' = R = {self.R}\\)

Bước 3: Viết phương trình mặt cầu đối xứng

Phương trình mặt cầu \\((S')\\): \\({sym_equation}\\)

Vậy phương trình mặt cầu \\((S')\\) đối xứng với \\((S)\\) qua mặt phẳng \\((Oxy)\\) là \\({sym_equation}\\).
"""
        return solution

    def tao_loi_giai_dang_16_cat_truc_tam_giac_vuong(self):
        """Lời giải dạng 16: Mặt cầu cắt trục tạo tam giác vuông"""
        solution = f"""
Dữ kiện: Mặt cầu có tâm \\(I({self.a}; {self.b}; {self.c})\\) cắt trục \\(Ox\\) tại hai điểm \\(A\\), \\(B\\) sao cho tam giác \\(IAB\\) vuông tại \\(I\\)

Bước 1: Xác định toạ độ các điểm giao

Gọi \\(A(x_1; 0; 0)\\), \\(B(x_2; 0; 0)\\) là hai điểm giao của mặt cầu với trục \\(Ox\\).

Do tính đối xứng, ta có thể viết \\(A({self.a} - d; 0; 0)\\), \\(B({self.a} + d; 0; 0)\\) với \\(d > 0\\).

Bước 2: Điều kiện tam giác vuông tại I

Tam giác \\(IAB\\) vuông tại \\(I\\) khi \\(\\overrightarrow{{IA}} \\perp \\overrightarrow{{IB}}\\):

\\[\\overrightarrow{{IA}} = (-d, -{self.b}, -{self.c})\\]
\\[\\overrightarrow{{IB}} = (d, -{self.b}, -{self.c})\\]

\\[\\overrightarrow{{IA}} \\cdot \\overrightarrow{{IB}} = -d^2 + {self.b}^2 + {self.c}^2 = 0\\]

\\[d^2 = {self.b}^2 + {self.c}^2 = {self.b**2 + self.c**2}\\]

\\[d = \\sqrt{{{self.b**2 + self.c**2}}}\\]

Bước 3: Tính bán kính mặt cầu

\\[R = |IA| = \\sqrt{{d^2 + {self.b}^2 + {self.c}^2}} = \\sqrt{{2({self.b}^2 + {self.c}^2)}} = \\sqrt{{{self.R_squared}}}\\]

Phương trình mặt cầu: \\({self.build_standard_equation()}\\)

Vậy phương trình mặt cầu là \\({self.build_standard_equation()}\\).
"""
        return solution

    def tao_loi_giai_dang_17_cat_mat_phang_duong_tron(self):
        """Lời giải dạng 17: Mặt cầu cắt mặt phẳng tạo đường tròn"""
        x_term = self.format_term_for_standard_form(self.a, 'x')
        y_term = self.format_term_for_standard_form(self.b, 'y')
        z_term = self.format_term_for_standard_form(self.c, 'z')
        equation = f"{x_term}^2 + {y_term}^2 + {z_term}^2 = {self.R**2}"
        
        solution = f"""
Dữ kiện: Mặt cầu \\((S): {equation}\\) có tâm \\(I({self.a}; {self.b}; {self.c})\\) và bán kính \\(R = {self.R}\\)

Bước 1: Xác định giao tuyến

Giao tuyến của mặt cầu \\((S)\\) với mặt phẳng \\((Oxy)\\) (phương trình \\(z = 0\\)) là đường tròn.

Bước 2: Tìm tâm đường tròn giao tuyến

Tâm đường tròn giao tuyến là hình chiếu của tâm mặt cầu lên mặt phẳng \\((Oxy)\\):
\\[O'({self.a}; {self.b}; 0)\\]

Bước 3: Tính bán kính đường tròn giao tuyến

Khoảng cách từ tâm \\(I\\) đến mặt phẳng \\((Oxy)\\): \\(h = |z_I| = |{self.c}| = {abs(self.c)}\\)

Bán kính đường tròn giao tuyến:
\\[r = \\sqrt{{R^2 - h^2}} = \\sqrt{{{self.R}^2 - {self.c}^2}} = \\sqrt{{{self.r_squared}}}\\]

Bước 4: Tính chu vi đường tròn

Chu vi đường tròn giao tuyến:
\\[C = 2\\pi r = 2\\pi\\sqrt{{{self.r_squared}}} = {self.circumference_simplified}\\]

Vậy chu vi đường tròn giao tuyến là \\({self.circumference_simplified}\\).
"""
        return solution


# =============================
# GENERATOR CHÍNH
# =============================
class SphereGenerator:
    @classmethod
    def generate_single_mixed_question(cls, question_number: int = 1) -> Tuple[str, List[bool]]:
        """Tạo một câu hỏi ĐÚNG/SAI với 5 mệnh đề từ 5 dạng khác nhau (13-17)"""
        # Tạo 5 bài toán khác nhau cho 5 dạng
        statements_all = []
        questions_for_solution = []  # Lưu các đối tượng câu hỏi để tạo lời giải
        
        for qtype in [13, 14, 15, 16, 17]:
            q = SphereQuestion()
            q.question_type = qtype
            
            # Sinh tham số cho từng dạng
            if qtype == 13:
                q.sinh_tham_so_dang_13_tiep_xuc_truc_hoanh()
                stmt, is_correct = q.tao_menh_de_dang_13_tiep_xuc_truc_hoanh()
            elif qtype == 14:
                q.sinh_tham_so_dang_14_tiep_xuc_mat_phang_oxy()
                stmt, is_correct = q.tao_menh_de_dang_14_tiep_xuc_mat_phang_oxy()
            elif qtype == 15:
                q.sinh_tham_so_dang_15_doi_xung_qua_mat_phang()
                stmt, is_correct = q.tao_menh_de_dang_15_doi_xung_qua_mat_phang()
            elif qtype == 16:
                q.sinh_tham_so_dang_16_cat_truc_tam_giac_vuong()
                stmt, is_correct = q.tao_menh_de_dang_16_cat_truc_tam_giac_vuong()
            elif qtype == 17:
                q.sinh_tham_so_dang_17_cat_mat_phang_duong_tron()
                stmt, is_correct = q.tao_menh_de_dang_17_cat_mat_phang_duong_tron()
            
            statements_all.append((stmt, is_correct, qtype))
            questions_for_solution.append(q)
        
        # Trộn thứ tự các mệnh đề - giữ track index để match với lời giải
        indexed_statements = list(enumerate(statements_all))
        random.shuffle(indexed_statements)
        
        # Tạo nội dung câu hỏi
        content = f"Câu {question_number}: Xét tính đúng sai của các mệnh đề sau:\n\n"
        
        correct_answers = []
        solution_content = "Lời giải:\n\n"
        
        for i, (orig_index, (stmt, is_correct, qtype)) in enumerate(indexed_statements):
            marker = "*" if is_correct else ""
            letter = chr(ord('a') + i)  # a, b, c, d, e
            
            content += f"{marker}{letter}) {stmt}.\n\n"
            correct_answers.append(is_correct)
            
            # Thêm lời giải cho mệnh đề này
            solution_content += f"{letter}) "
            q_for_solution = questions_for_solution[orig_index]
            solution_content += q_for_solution.generate_solution() + "\n\n"
        
        # Ghép câu hỏi và lời giải
        full_content = content + solution_content
        
        return full_content, correct_answers

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