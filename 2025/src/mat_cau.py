import math
import random
import sys
from typing import List, Tuple
import sympy as sp


# =============================
# CLASS TÍNH TOÁN MẶT CẦU
# =============================
class SphereQuestion:
    def __init__(self):
        self.generate_parameters()

    def generate_solution(self):
        """Tạo lời giải"""
        # Gọi trực tiếp phương thức tương ứng
        if self.question_type == 1:
            return self.tao_loi_giai_dang_chuan_tim_tam_ban_kinh()
        elif self.question_type == 2:
            return self.tao_loi_giai_dang_tong_quat_tim_tam_ban_kinh()
        elif self.question_type == 3:
            return self.tao_loi_giai_dieu_kien_tham_so_mat_cau()
        elif self.question_type == 4:
            return self.tao_loi_giai_tim_tham_so_khi_biet_ban_kinh()
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
    
    def build_general_equation_terms(self, include_parameter=False, parameter_name="m"):
        """
        Tạo danh sách các hạng tử cho phương trình tổng quát
        include_parameter: có thêm tham số không
        parameter_name: tên tham số (mặc định là 'm')
        """
        terms = ["x^2", "y^2", "z^2"]
        
        # Thêm các hạng tử bậc 1
        for coeff, var in [(self.D, 'x'), (self.E, 'y'), (self.F, 'z')]:
            if coeff != 0:
                terms.append(f"{coeff}{var}")
        
        # Thêm hằng số G (nếu có)
        if hasattr(self, 'G') and self.G != 0:
            terms.append(str(self.G))
        
        # Thêm tham số nếu cần
        if include_parameter:
            terms.append(parameter_name)
        
        return terms
    
    def build_general_equation(self, include_parameter=False, parameter_name="m"):
        """Tạo phương trình tổng quát x²+y²+z²+Dx+Ey+Fz+G=0"""
        terms = self.build_general_equation_terms(include_parameter, parameter_name)
        return " + ".join(terms).replace("+ -", "- ")
    
    # =================================================================
    # END HELPER FUNCTIONS
    # =================================================================

    def generate_parameters(self):
        """Sinh các tham số ngẫu nhiên cho câu hỏi mặt cầu"""
        # Chỉ random question_type khi chưa được set
        if not hasattr(self, 'question_type'):
            self.question_type = random.choice([1, 2, 3, 4])
        
        # Gọi trực tiếp phương thức tương ứng
        if self.question_type == 1:
            self.sinh_tham_so_dang_chuan_tim_tam_ban_kinh()
        elif self.question_type == 2:
            self.sinh_tham_so_dang_tong_quat_tim_tam_ban_kinh()
        elif self.question_type == 3:
            self.sinh_tham_so_dieu_kien_tham_so_mat_cau()
        elif self.question_type == 4:
            self.sinh_tham_so_tim_tham_so_khi_biet_ban_kinh()
        else:
            raise ValueError(f"Chưa implement dạng {self.question_type}")

    def sinh_tham_so_dang_chuan_tim_tam_ban_kinh(self):
        """Dạng 1: Tìm tâm và bán kính từ phương trình chuẩn"""
        self.a = random.randint(-3, 3)
        self.b = random.randint(-3, 3)
        self.c = random.randint(-3, 3)
        self.R = random.randint(2, 5)
        self.R_squared = self.R ** 2

    def sinh_tham_so_dang_tong_quat_tim_tam_ban_kinh(self):
        """Dạng 2: Tìm tâm và bán kính từ phương trình tổng quát"""
        # Sinh tâm trước
        self.center_x = random.randint(-2, 2)
        self.center_y = random.randint(-2, 2)
        self.center_z = random.randint(-2, 2)
        
        # Tính các hệ số D, E, F
        self.D = -2 * self.center_x
        self.E = -2 * self.center_y
        self.F = -2 * self.center_z
        
        # Chọn bán kính và tính G
        self.R = random.randint(3, 6)
        self.G = self.center_x**2 + self.center_y**2 + self.center_z**2 - self.R**2

    def sinh_tham_so_dieu_kien_tham_so_mat_cau(self):
        """Dạng 3: Điều kiện để phương trình là mặt cầu"""
        self.D = random.choice([-4, -2, 2, 4])
        self.E = random.choice([-4, -2, 2, 4])
        self.F = random.choice([-4, -2, 2, 4])
        # Điều kiện: D² + E² + F² - 4m > 0
        self.threshold = (self.D**2 + self.E**2 + self.F**2) // 4

    def sinh_tham_so_tim_tham_so_khi_biet_ban_kinh(self):
        """Dạng 4: Tìm tham số khi biết bán kính"""
        self.D = random.choice([-4, -2, 2, 4])
        self.E = random.choice([-4, -2, 2, 4])
        self.F = random.choice([-4, -2, 2, 4])
        self.R = random.randint(3, 6)
        # m = (D² + E² + F²)/4 - R²
        self.m_value = (self.D**2 + self.E**2 + self.F**2)//4 - self.R**2

    def check_point_on_sphere(self, x, y, z):
        """Kiểm tra điểm có thuộc mặt cầu không"""
        if self.question_type == 1:
            distance_sq = (x - self.a)**2 + (y - self.b)**2 + (z - self.c)**2
            return abs(distance_sq - self.R**2) < 0.001
        return False
    
    def make_statement_wrong(self, stmt, index):
        """Biến đổi mệnh đề để thành sai"""
        if "đi qua điểm" in stmt:
            return stmt.replace("A(0; 0; 0)", "A(1; 1; 1)")
        elif "thuộc mặt phẳng" in stmt:
            return stmt.replace("Oxy", "Oxz")
        elif "tiếp xúc" in stmt:
            return stmt.replace("tiếp xúc", "cắt")
        return stmt

    def tao_loi_giai_dang_chuan_tim_tam_ban_kinh(self):
        """Lời giải dạng 1: Từ phương trình chuẩn tìm tâm và bán kính"""
        x_term = f"(x - {self.a})" if self.a != 0 else "x"
        y_term = f"(y - {self.b})" if self.b != 0 else "y" 
        z_term = f"(z - {self.c})" if self.c != 0 else "z"
        
        if self.a < 0:
            x_term = f"(x + {-self.a})"
        if self.b < 0:
            y_term = f"(y + {-self.b})"
        if self.c < 0:
            z_term = f"(z + {-self.c})"

        equation = f"{x_term}^2 + {y_term}^2 + {z_term}^2 = {self.R_squared}"
        
        solution = f"""
Dữ kiện: Mặt cầu \\((S): {equation}\\)

Bước 1: Nhận dạng phương trình mặt cầu

Phương trình có dạng \\((x - a)^2 + (y - b)^2 + (z - c)^2 = R^2\\)

Bước 2: Xác định tâm và bán kính

- So sánh với phương trình chuẩn, ta có:

  + Tâm \\(I(a; b; c) = I({self.a}; {self.b}; {self.c})\\)

  + Bán kính \\(R^2 = {self.R_squared} \\Rightarrow R = \\sqrt{{{self.R_squared}}} = {self.R}\\)

Vậy mặt cầu \\((S)\\) có tâm \\(I({self.a}; {self.b}; {self.c})\\) và bán kính \\(R = {self.R}\\).
"""
        return solution

    def tao_loi_giai_dang_tong_quat_tim_tam_ban_kinh(self):
        """Lời giải dạng 2: Từ phương trình tổng quát tìm tâm và bán kính"""
        terms = ["x^2", "y^2", "z^2"]
        
        if self.D > 0:
            terms.append(f"{self.D}x")
        elif self.D < 0:
            terms.append(f"{self.D}x")
            
        if self.E > 0:
            terms.append(f"{self.E}y")
        elif self.E < 0:
            terms.append(f"{self.E}y")
            
        if self.F > 0:
            terms.append(f"{self.F}z")
        elif self.F < 0:
            terms.append(f"{self.F}z")
            
        if self.G > 0:
            terms.append(f"{self.G}")
        elif self.G < 0:
            terms.append(f"{self.G}")
        
        equation = " + ".join(terms).replace("+ -", "- ")
        
        solution = f"""
Dữ kiện: Mặt cầu \\((S): {equation} = 0\\)

Bước 1: Nhận dạng phương trình mặt cầu tổng quát

Phương trình có dạng \\(x^2 + y^2 + z^2 + Dx + Ey + Fz + G = 0\\)

với \\(D = {self.D}\\), \\(E = {self.E}\\), \\(F = {self.F}\\), \\(G = {self.G}\\)

Bước 2: Chuyển về dạng chuẩn

\\[\\left(x + \\frac{{{self.D}}}{{2}}\\right)^2 + \\left(y + \\frac{{{self.E}}}{{2}}\\right)^2 + \\left(z + \\frac{{{self.F}}}{{2}}\\right)^2 = \\frac{{{self.D**2 + self.E**2 + self.F**2}}}{{4}} - ({self.G}) = {self.R**2}\\]

Bước 3: Xác định tâm và bán kính

- Tâm \\(I({self.center_x}; {self.center_y}; {self.center_z})\\)
- Bán kính \\(R = {self.R}\\)

Vậy mặt cầu \\((S)\\) có tâm \\(I({self.center_x}; {self.center_y}; {self.center_z})\\) và bán kính \\(R = {self.R}\\).
"""
        return solution

    def tao_loi_giai_dieu_kien_tham_so_mat_cau(self):
        """Lời giải dạng 3: Điều kiện để phương trình là mặt cầu"""
        terms = ["x^2", "y^2", "z^2"]
        
        if self.D > 0:
            terms.append(f"{self.D}x")
        else:
            terms.append(f"{self.D}x")
            
        if self.E > 0:
            terms.append(f"{self.E}y")
        else:
            terms.append(f"{self.E}y")
            
        if self.F > 0:
            terms.append(f"{self.F}z")
        else:
            terms.append(f"{self.F}z")
        
        terms.append("m")
        equation = " + ".join(terms).replace("+ -", "- ")
        
        solution = f"""
Dữ kiện: Phương trình \\({equation} = 0\\)

Bước 1: Điều kiện để phương trình là mặt cầu

Phương trình tổng quát \\(x^2 + y^2 + z^2 + Dx + Ey + Fz + G = 0\\) là phương trình của một mặt cầu khi và chỉ khi:

\\[D^2 + E^2 + F^2 - 4G > 0\\]

Bước 2: Áp dụng điều kiện

Với \\(D = {self.D}\\), \\(E = {self.E}\\), \\(F = {self.F}\\), \\(G = m\\), ta có:

\\[({self.D})^2 + ({self.E})^2 + ({self.F})^2 - 4m > 0\\]

\\[{self.D**2 + self.E**2 + self.F**2} - 4m > 0\\]

\\[m < {self.threshold}\\]

Vậy phương trình đã cho là phương trình của một mặt cầu khi và chỉ khi \\(m < {self.threshold}\\).
"""
        return solution

    def tao_loi_giai_tim_tham_so_khi_biet_ban_kinh(self):
        """Lời giải dạng 4: Tìm tham số khi biết bán kính"""
        terms = ["x^2", "y^2", "z^2"]
        
        if self.D > 0:
            terms.append(f"{self.D}x")
        else:
            terms.append(f"{self.D}x")
            
        if self.E > 0:
            terms.append(f"{self.E}y")
        else:
            terms.append(f"{self.E}y")
            
        if self.F > 0:
            terms.append(f"{self.F}z")
        else:
            terms.append(f"{self.F}z")
        
        equation = " + ".join(terms).replace("+ -", "- ") + " - m"
        
        solution = f"""
Dữ kiện: Mặt cầu \\((S): {equation} = 0\\) có bán kính \\(R = {self.R}\\)

Bước 1: Chuyển phương trình về dạng chuẩn

Phương trình có dạng \\(x^2 + y^2 + z^2 + Dx + Ey + Fz + G = 0\\)

với \\(D = {self.D}\\), \\(E = {self.E}\\), \\(F = {self.F}\\), \\(G = -m\\)

Bước 2: Sử dụng công thức bán kính

\\[R^2 = \\frac{{D^2 + E^2 + F^2 - 4G}}{{4}}\\]

Bước 3: Thay số và giải phương trình

\\[({self.R})^2 = \\frac{{({self.D})^2 + ({self.E})^2 + ({self.F})^2 + 4m}}{{4}}\\]

\\[{self.R**2 * 4} = {self.D**2 + self.E**2 + self.F**2} + 4m\\]

\\[m = {-self.m_value}\\]

Vậy \\(m = {-self.m_value}\\).
"""
        return solution

# =============================
# GENERATOR CHÍNH
# =============================
class SphereGenerator:
    @classmethod
    def generate_single_mixed_question(cls, question_number: int = 1) -> Tuple[str, List[bool]]:
        """Tạo một câu hỏi ĐÚNG/SAI với 4 mệnh đề từ 4 dạng khác nhau"""
        # Tạo 4 bài toán khác nhau
        statements_all = []
        solutions_all = []
        
        for qtype in [1, 2, 3, 4]:
            q = SphereQuestion()
            q.question_type = qtype
            if qtype == 1:
                q.sinh_tham_so_dang_chuan_tim_tam_ban_kinh()
            elif qtype == 2:
                q.sinh_tham_so_dang_tong_quat_tim_tam_ban_kinh()
            elif qtype == 3:
                q.sinh_tham_so_dieu_kien_tham_so_mat_cau()
            elif qtype == 4:
                q.sinh_tham_so_tim_tham_so_khi_biet_ban_kinh()
            
            # Tạo mệnh đề cho từng dạng
            if qtype == 1:
                # Dạng 1: phương trình chuẩn - kiểm tra tâm và bán kính
                x_term = f"(x - {q.a})" if q.a != 0 else "x"
                y_term = f"(y - {q.b})" if q.b != 0 else "y" 
                z_term = f"(z - {q.c})" if q.c != 0 else "z"
                
                if q.a < 0:
                    x_term = f"(x + {-q.a})"
                if q.b < 0:
                    y_term = f"(y + {-q.b})"
                if q.c < 0:
                    z_term = f"(z + {-q.c})"
                
                equation = f"{x_term}^2 + {y_term}^2 + {z_term}^2 = {q.R_squared}"
                
                # Random đúng/sai
                if random.random() > 0.5:
                    full_stmt = f"Mặt cầu \\((S): {equation}\\) có tâm \\(I({q.a}; {q.b}; {q.c})\\) và \\(R = {q.R}\\)"
                    is_correct = True
                else:
                    wrong_R = q.R + random.choice([-1, 1, 2, -2])
                    full_stmt = f"Mặt cầu \\((S): {equation}\\) có tâm \\(I({q.a}; {q.b}; {q.c})\\) và \\(R = {wrong_R}\\)"
                    is_correct = False
                
            elif qtype == 2:
                # Dạng 2: phương trình tổng quát
                terms = ["x^2", "y^2", "z^2"]
                
                if q.D > 0:
                    terms.append(f"{q.D}x")
                elif q.D < 0:
                    terms.append(f"{q.D}x")
                    
                if q.E > 0:
                    terms.append(f"{q.E}y")
                elif q.E < 0:
                    terms.append(f"{q.E}y")
                    
                if q.F > 0:
                    terms.append(f"{q.F}z")
                elif q.F < 0:
                    terms.append(f"{q.F}z")
                    
                if q.G > 0:
                    terms.append(f"{q.G}")
                elif q.G < 0:
                    terms.append(f"{q.G}")
                
                equation = " + ".join(terms).replace("+ -", "- ")
                
                # Random đúng/sai
                if random.random() > 0.5:
                    full_stmt = f"Mặt cầu \\((S): {equation} = 0\\) có tâm \\(I({q.center_x}; {q.center_y}; {q.center_z})\\) và \\(R = {q.R}\\)"
                    is_correct = True
                else:
                    wrong_center_x = q.center_x + random.choice([-1, 1])
                    full_stmt = f"Mặt cầu \\((S): {equation} = 0\\) có tâm \\(I({wrong_center_x}; {q.center_y}; {q.center_z})\\) và \\(R = {q.R}\\)"
                    is_correct = False
                
            elif qtype == 3:
                # Dạng 3: điều kiện tham số
                terms = ["x^2", "y^2", "z^2"]
                
                if q.D > 0:
                    terms.append(f"{q.D}x")
                else:
                    terms.append(f"{q.D}x")
                    
                if q.E > 0:
                    terms.append(f"{q.E}y")
                else:
                    terms.append(f"{q.E}y")
                    
                if q.F > 0:
                    terms.append(f"{q.F}z")
                else:
                    terms.append(f"{q.F}z")
                
                terms.append("m")
                equation = " + ".join(terms).replace("+ -", "- ")
                
                # Tạo mệnh đề về số lượng giá trị nguyên trong khoảng
                # Điều kiện: m < threshold, nên tạo khoảng quanh threshold
                start = q.threshold - 3
                end = q.threshold + 2
                # Đếm số giá trị nguyên m sao cho m < threshold trong khoảng mở (start, end)
                count_correct = len([m for m in range(start + 1, end) if m < q.threshold])
                
                # Random tạo câu đúng hoặc sai
                if random.random() > 0.5:
                    # Câu đúng
                    full_stmt = f"Trong khoảng \\(({start}; {end})\\), có {count_correct} giá trị nguyên của \\(m\\) để phương trình \\({equation} = 0\\) là phương trình của một mặt cầu"
                    is_correct = True
                else:
                    # Câu sai - thay đổi số lượng
                    wrong_count = count_correct + random.choice([-1, 1, 2, -2])
                    if wrong_count < 0:
                        wrong_count = count_correct + 1
                    full_stmt = f"Trong khoảng \\(({start}; {end})\\), có {wrong_count} giá trị nguyên của \\(m\\) để phương trình \\({equation} = 0\\) là phương trình của một mặt cầu"
                    is_correct = False
                
            elif qtype == 4:
                # Dạng 4: tìm tham số theo bán kính
                terms = ["x^2", "y^2", "z^2"]
                
                if q.D > 0:
                    terms.append(f"{q.D}x")
                else:
                    terms.append(f"{q.D}x")
                    
                if q.E > 0:
                    terms.append(f"{q.E}y")
                else:
                    terms.append(f"{q.E}y")
                    
                if q.F > 0:
                    terms.append(f"{q.F}z")
                else:
                    terms.append(f"{q.F}z")
                
                equation = " + ".join(terms).replace("+ -", "- ") + " - m"
                
                # Chọn ngẫu nhiên giá trị m để kiểm tra
                if random.random() > 0.5:
                    test_m = -q.m_value
                    is_correct = True
                else:
                    test_m = -q.m_value + random.choice([-1, 1, 2, -2])
                    is_correct = False
                    
                full_stmt = f"Mặt cầu \\((S): {equation} = 0\\) có bán kính \\(R = {q.R}\\) khi \\(m = {test_m}\\)"
            
            statements_all.append((full_stmt, is_correct))
            solutions_all.append(q.generate_solution())
        
        # Trộn thứ tự các mệnh đề và lời giải cùng nhau
        combined = list(zip(statements_all, solutions_all))
        random.shuffle(combined)
        statements_all, solutions_all = zip(*combined)
        
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