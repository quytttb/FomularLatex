import math
import random
import sys
from typing import List, Tuple, Optional
import sympy as sp
import subprocess
import os

# =============================
# CONFIGURATION CLASS
# =============================
class Config:
    """Configuration settings for the plane equation generator"""
    
    # File settings
    OUTPUT_FILENAME = "solution"
    OUTPUT_DIR = None  # None means current directory
    
    # LaTeX compilation settings
    LATEX_ENGINE = "xelatex"
    COMPILE_TIMEOUT = 60
    BATCH_MODE = True
    
    # Math range settings
    POINT_RANGE_MIN = -5
    POINT_RANGE_MAX = 5
    VECTOR_RANGE_MIN = -3
    VECTOR_RANGE_MAX = 3
    GIVEN_PLANE_D_RANGE_MIN = -5
    GIVEN_PLANE_D_RANGE_MAX = 5
    
    # Generation settings
    MAX_TRIANGLE_ATTEMPTS = 10
    MAX_ERROR_DISPLAY = 5
    LOG_LINES_TO_CHECK = 20
    
    # Progress settings
    SHOW_PROGRESS = True
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """Load configuration from file (future enhancement)"""
        # TODO: Implement config file loading
        return cls()
    
    @classmethod
    def get_output_path(cls) -> str:
        """Get full output path for files"""
        if cls.OUTPUT_DIR:
            return os.path.join(cls.OUTPUT_DIR, cls.OUTPUT_FILENAME)
        return cls.OUTPUT_FILENAME

# =============================
# LEGACY CONSTANTS (for backwards compatibility)
# =============================
POINT_RANGE_MIN = Config.POINT_RANGE_MIN
POINT_RANGE_MAX = Config.POINT_RANGE_MAX
VECTOR_RANGE_MIN = Config.VECTOR_RANGE_MIN
VECTOR_RANGE_MAX = Config.VECTOR_RANGE_MAX
GIVEN_PLANE_D_RANGE_MIN = Config.GIVEN_PLANE_D_RANGE_MIN
GIVEN_PLANE_D_RANGE_MAX = Config.GIVEN_PLANE_D_RANGE_MAX
MAX_TRIANGLE_ATTEMPTS = Config.MAX_TRIANGLE_ATTEMPTS
COMPILE_TIMEOUT = Config.COMPILE_TIMEOUT
MAX_ERROR_DISPLAY = Config.MAX_ERROR_DISPLAY
LOG_LINES_TO_CHECK = Config.LOG_LINES_TO_CHECK


# =============================
# CLASS TÍNH TOÁN PHƯƠNG TRÌNH MẶT PHẲNG
# =============================
class PlaneQuestion:
    def __init__(self):
        self.x, self.y, self.z = sp.symbols('x y z')
        self.generate_parameters()

    def random_point(self, min_val=POINT_RANGE_MIN, max_val=POINT_RANGE_MAX) -> Tuple[int, int, int]:
        """Tạo điểm ngẫu nhiên, tránh gốc tọa độ để tránh edge cases"""
        while True:
            point = (random.randint(min_val, max_val), 
                    random.randint(min_val, max_val), 
                    random.randint(min_val, max_val))
            # Tránh điểm gốc tọa độ
            if point != (0, 0, 0):
                return point
    
    def random_vector(self, min_val=VECTOR_RANGE_MIN, max_val=VECTOR_RANGE_MAX) -> Tuple[int, int, int]:
        """Tạo vector ngẫu nhiên (không bằng 0)"""
        while True:
            vec = (random.randint(min_val, max_val), 
                   random.randint(min_val, max_val), 
                   random.randint(min_val, max_val))
            if vec != (0, 0, 0):
                return vec
    
    def validate_triangle(self, A: Tuple[int, int, int], B: Tuple[int, int, int], C: Tuple[int, int, int]) -> bool:
        """
        Kiểm tra tam giác không suy biến
        
        Args:
            A, B, C: Ba đỉnh của tam giác
            
        Returns:
            True nếu tam giác không suy biến (ba điểm không thẳng hàng)
        """
        # Vector AB và AC
        AB = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
        AC = (C[0] - A[0], C[1] - A[1], C[2] - A[2])
        
        # Tích có hướng AB x AC
        cross_product = (
            AB[1] * AC[2] - AB[2] * AC[1],
            AB[2] * AC[0] - AB[0] * AC[2],
            AB[0] * AC[1] - AB[1] * AC[0]
        )
        
        # Tam giác không suy biến nếu tích có hướng khác vector 0
        return cross_product != (0, 0, 0)
    
    def validate_equation(self, coeffs: Tuple[int, int, int, int]) -> bool:
        """
        Kiểm tra phương trình mặt phẳng hợp lệ
        
        Args:
            coeffs: Tuple hệ số (a, b, c, d)
            
        Returns:
            True nếu phương trình hợp lệ (a, b, c không đồng thời bằng 0)
        """
        a, b, c, d = coeffs
        return not (a == 0 and b == 0 and c == 0)
    
    def format_point(self, point: Tuple[int, int, int]) -> str:
        """
        Format điểm thành chuỗi LaTeX
        
        Args:
            point: Tuple chứa tọa độ (x, y, z)
            
        Returns:
            String định dạng "(x;y;z)"
        """
        return f"({point[0]};{point[1]};{point[2]})"
    
    def format_vector(self, vec: Tuple[int, int, int]) -> str:
        """
        Format vector thành chuỗi LaTeX
        
        Args:
            vec: Tuple chứa thành phần vector (x, y, z)
            
        Returns:
            String định dạng "(x;y;z)"
        """
        return f"({vec[0]};{vec[1]};{vec[2]})"
    
    def format_equation(self, coeffs: Tuple[int, int, int, int]) -> str:
        """
        Format phương trình mặt phẳng ax + by + cz + d = 0
        
        Args:
            coeffs: Tuple chứa các hệ số (a, b, c, d)
            
        Returns:
            String phương trình được format đẹp
        """
        a, b, c, d = coeffs
        terms = []
        
        # Xử lý hệ số x
        if a == 1:
            terms.append("x")
        elif a == -1:
            terms.append("-x")
        elif a != 0:
            terms.append(f"{a}x")
        
        # Xử lý hệ số y
        if b == 1:
            terms.append("+ y" if terms else "y")
        elif b == -1:
            terms.append("- y")
        elif b > 0 and terms:
            terms.append(f"+ {b}y")
        elif b < 0:
            terms.append(f"- {abs(b)}y" if terms else f"{b}y")
        elif b != 0:
            terms.append(f"{b}y")
        
        # Xử lý hệ số z
        if c == 1:
            terms.append("+ z" if terms else "z")
        elif c == -1:
            terms.append("- z")
        elif c > 0 and terms:
            terms.append(f"+ {c}z")
        elif c < 0:
            terms.append(f"- {abs(c)}z" if terms else f"{c}z")
        elif c != 0:
            terms.append(f"{c}z")
        
        # Xử lý hằng số
        if d > 0 and terms:
            terms.append(f"+ {d}")
        elif d < 0:
            terms.append(f"- {abs(d)}" if terms else str(d))
        elif d != 0:
            terms.append(str(d))
        
        equation = " ".join(terms) if terms else "0"
        return f"{equation} = 0"

    def generate_parameters(self):
        """Sinh các tham số ngẫu nhiên cho câu hỏi mặt phẳng"""
        # Chỉ random question_type khi chưa được set
        if not hasattr(self, 'question_type'):
            self.question_type = random.choice([1, 2, 3, 4])
        
        # Gọi trực tiếp phương thức tương ứng (chỉ một lần)
        if self.question_type == 1:
            self.type1_point_normal()
        elif self.question_type == 2:
            self.type2_centroid_perpendicular()
        elif self.question_type == 3:
            self.type3_parallel_plane()
        elif self.question_type == 4:
            self.type4_perpendicular_bisector()
        else:
            raise ValueError(f"Chưa implement dạng {self.question_type}")

    def type1_point_normal(self) -> dict:
        """Dạng 1: Mặt phẳng qua điểm với vector pháp tuyến"""
        point = self.random_point()
        normal = self.random_vector()
        
        # Tính phương trình: a(x-x0) + b(y-y0) + c(z-z0) = 0
        a, b, c = normal
        x0, y0, z0 = point
        
        # Khai triển: ax - ax0 + by - by0 + cz - cz0 = 0
        # ax + by + cz + (-ax0 - by0 - cz0) = 0
        d = -a*x0 - b*y0 - c*z0
        
        self.point = point
        self.normal = normal
        self.correct = (a, b, c, d)
        
        # Validate equation
        if not self.validate_equation(self.correct):
            # Fallback: tạo phương trình đơn giản
            self.correct = (1, 0, 0, -point[0])
            
        self.question_text = f"Phương trình mặt phẳng (P) qua điểm A{self.format_point(point)} và có VTPT \\(\\vec{{n}}={self.format_vector(normal)}\\) là"
        
        return {
            'question': self.question_text,
            'correct': self.correct,
            'type': 'type1'
        }
    
    def type2_centroid_perpendicular(self) -> dict:
        """Dạng 2: Mặt phẳng qua trọng tâm tam giác và vuông góc với cạnh"""
        # Tạo tam giác không suy biến
        max_attempts = MAX_TRIANGLE_ATTEMPTS
        for _ in range(max_attempts):
            A = self.random_point()
            B = self.random_point()
            C = self.random_point()
            
            if self.validate_triangle(A, B, C):
                break
        else:
            # Fallback: tạo tam giác đơn giản không suy biến
            A = (0, 0, 0)
            B = (1, 0, 0)
            C = (0, 1, 0)
        
        # Tính trọng tâm G (sử dụng phép chia thông thường)
        G = ((A[0] + B[0] + C[0]) / 3, 
             (A[1] + B[1] + C[1]) / 3, 
             (A[2] + B[2] + C[2]) / 3)
        
        # Vector BC làm VTPT
        BC = (C[0] - B[0], C[1] - B[1], C[2] - B[2])
        
        # Tính phương trình
        a, b, c = BC
        x0, y0, z0 = G
        d = -a*x0 - b*y0 - c*z0
        
        # Đảm bảo d là integer (làm tròn nếu cần)
        if isinstance(d, float):
            d = int(round(d))
        
        self.A = A
        self.B = B
        self.C = C
        self.G = G
        self.BC = BC
        self.correct = (a, b, c, d)
        
        # Validate equation
        if not self.validate_equation(self.correct):
            # Fallback: tạo phương trình đơn giản từ centroid
            fallback_d = -int(G[0]) if isinstance(G[0], float) else -G[0]
            self.correct = (1, 0, 0, fallback_d)
            
        self.question_text = f"Cho A{self.format_point(A)}, B{self.format_point(B)}, C{self.format_point(C)}. Phương trình mặt phẳng (P) qua trọng tâm G của \\(\\triangle ABC\\) và vuông góc với BC là"
        
        return {
            'question': self.question_text,
            'correct': self.correct,
            'type': 'type2'
        }
    
    def type3_parallel_plane(self) -> dict:
        """Dạng 3: Mặt phẳng qua điểm và song song với mặt phẳng cho trước"""
        point = self.random_point()
        
        # Tạo mặt phẳng cho trước
        given_normal = self.random_vector()
        given_d = random.randint(GIVEN_PLANE_D_RANGE_MIN, GIVEN_PLANE_D_RANGE_MAX)
        
        # Mặt phẳng song song có cùng VTPT
        a, b, c = given_normal
        x0, y0, z0 = point
        d = -a*x0 - b*y0 - c*z0
        
        self.point = point
        self.given_normal = given_normal
        self.given_d = given_d
        self.correct = (a, b, c, d)
        
        # Validate equation
        if not self.validate_equation(self.correct):
            # Fallback: tạo phương trình đơn giản
            self.correct = (1, 0, 0, -point[0])
            
        given_eq = self.format_equation((*given_normal, given_d))
        self.question_text = f"Phương trình mặt phẳng (P) qua A{self.format_point(point)} và (P) // (Q): {given_eq} là"
        
        return {
            'question': self.question_text,
            'correct': self.correct,
            'type': 'type3'
        }
    
    def type4_perpendicular_bisector(self) -> dict:
        """Dạng 4: Mặt phẳng trung trực của đoạn thẳng"""
        A = self.random_point()
        B = self.random_point()
        
        # Trung điểm I (sử dụng phép chia thông thường để tránh làm tròn)
        I = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2, (A[2] + B[2]) / 2)
        
        # Vector AB làm VTPT
        AB = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
        
        # Tính phương trình
        a, b, c = AB
        x0, y0, z0 = I
        d = -a*x0 - b*y0 - c*z0
        
        # Đảm bảo d là integer (có thể làm tròn nếu cần)
        if isinstance(d, float):
            d = int(round(d))
        
        self.A = A
        self.B = B
        self.I = I
        self.AB = AB
        self.correct = (a, b, c, d)
        
        # Validate equation
        if not self.validate_equation(self.correct):
            # Fallback: tạo phương trình đơn giản
            fallback_d = -int(I[0]) if isinstance(I[0], float) else -I[0]
            self.correct = (1, 0, 0, fallback_d)
            
        self.question_text = f"Phương trình mặt phẳng trung trực (P) của đoạn AB với A{self.format_point(A)}, B{self.format_point(B)} là"
        
        return {
            'question': self.question_text,
            'correct': self.correct,
            'type': 'type4'
        }
    
    def generate_wrong_answers(self, correct: Tuple[int, int, int, int], num_wrong=3) -> List[Tuple[int, int, int, int]]:
        """
        Tạo các đáp án sai
        
        Args:
            correct: Tuple hệ số đúng (a, b, c, d)
            num_wrong: Số đáp án sai cần tạo
            
        Returns:
            List các tuple hệ số sai
        """
        wrong_answers = []
        a, b, c, d = correct
        
        methods = [
            # Đổi dấu một hệ số
            lambda: (-a, b, c, d),
            lambda: (a, -b, c, d),
            lambda: (a, b, -c, d),
            lambda: (a, b, c, -d),
            # Cộng/trừ 1-3 vào hệ số
            lambda: (a + random.randint(1, 3), b, c, d),
            lambda: (a - random.randint(1, 3), b, c, d),
            lambda: (a, b + random.randint(1, 3), c, d),
            lambda: (a, b - random.randint(1, 3), c, d),
            lambda: (a, b, c + random.randint(1, 3), d),
            lambda: (a, b, c - random.randint(1, 3), d),
            lambda: (a, b, c, d + random.randint(1, 3)),
            lambda: (a, b, c, d - random.randint(1, 3)),
            # Hoán đổi hệ số
            lambda: (b, a, c, d),
            lambda: (a, c, b, d),
            # Nhân một hệ số với 2
            lambda: (2*a, b, c, d),
            lambda: (a, 2*b, c, d),
        ]
        
        # Tránh infinite loop bằng cách giới hạn số lần thử
        max_attempts = len(methods) * 3
        attempts = 0
        
        while len(wrong_answers) < num_wrong and attempts < max_attempts:
            method = random.choice(methods)
            wrong = method()
            if wrong != correct and wrong not in wrong_answers:
                wrong_answers.append(wrong)
            attempts += 1
        
        # Nếu không đủ wrong answers, tạo thêm bằng cách đơn giản
        while len(wrong_answers) < num_wrong:
            offset = random.randint(1, 5) * random.choice([-1, 1])
            wrong = (a + offset, b, c, d)
            if wrong != correct and wrong not in wrong_answers:
                wrong_answers.append(wrong)
        
        return wrong_answers[:num_wrong]









# =============================
# GENERATOR CHÍNH
# =============================
class PlaneGenerator:
    def __init__(self):
        """Khởi tạo generator với object reusable"""
        self._question_obj = PlaneQuestion()
    
    @classmethod
    def generate_single_mixed_question(cls, question_number: int = 1) -> Tuple[str, List[bool]]:
        """Tạo một câu hỏi với 4 mệnh đề từ 4 dạng khác nhau, mỗi mệnh đề random đúng/sai"""
        # Tạo 4 bài toán khác nhau
        statements_all = []
        
        # Tái sử dụng một object duy nhất
        q = PlaneQuestion()
        
        for qtype in [1, 2, 3, 4]:
            q.question_type = qtype
            
            # Regenerate cho type mới
            q.generate_parameters()
            
            # Tạo mệnh đề cho từng dạng
            correct = q.correct
            
            # Random chọn tạo mệnh đề đúng hay sai (độc lập cho mỗi mệnh đề)
            is_correct = random.choice([True, False])
            
            if is_correct:
                # Sử dụng đáp án đúng
                equation = correct
            else:
                # Tạo đáp án sai
                wrong_answers = q.generate_wrong_answers(correct, 1)
                equation = wrong_answers[0]
            
            # Tạo mệnh đề hoàn chỉnh
            equation_text = f"(P): {q.format_equation(equation)}"
            full_stmt = f"{q.question_text} {equation_text}"
            
            statements_all.append((full_stmt, is_correct))
        
        # Trộn thứ tự các mệnh đề 
        random.shuffle(statements_all)
        
        # Tạo nội dung câu hỏi
        content = f"Câu {question_number}: Trong các mệnh đề dưới đây, mệnh đề nào đúng?\n\n"
        
        correct_answers = []
        for i, (stmt, is_correct) in enumerate(statements_all):
            marker = "*" if is_correct else ""
            letter = chr(ord('a') + i)  # a, b, c, d
            
            content += f"{marker}{letter}) {stmt}.\n\n"
            correct_answers.append(is_correct)
        
        return content, correct_answers

    @classmethod
    def generate_multiple_questions(cls, num_questions: int = 5) -> List[str]:
        """
        Tạo nhiều câu hỏi với progress indicator
        
        Args:
            num_questions: Số câu hỏi cần tạo
            
        Returns:
            List các câu hỏi đã format
        """
        questions = []
        print(f"🔄 Đang tạo {num_questions} câu hỏi...")
        
        for i in range(1, num_questions + 1):
            if num_questions > 3:  # Chỉ hiển thị progress khi có nhiều câu hỏi
                print(f"  📝 Câu hỏi {i}/{num_questions}...", end='\r')
            
            content, _ = cls.generate_single_mixed_question(i)
            questions.append(content)
        
        if num_questions > 3:
            print(f"  ✅ Hoàn thành {num_questions} câu hỏi!     ")
        
        return questions

    @staticmethod
    def create_latex_document(questions_data, title: str = "Bài tập về Phương trình mặt phẳng") -> str:
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
    def create_latex_file(cls, questions_data, filename: str = "phuong_trinh_mat_phang.tex",
                         title: str = "Bài tập về Phương trình mặt phẳng") -> str:
        latex_content = cls.create_latex_document(questions_data, title)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        print(f"Đã tạo file: {filename}")
        return filename
    
    @staticmethod
    def compile_latex_quietly(filename: str, config: Optional[Config] = None) -> bool:
        """Biên dịch LaTeX với log thu gọn"""
        import subprocess
        import os
        
        if config is None:
            config = Config()
        
        # Validation
        if not filename or not isinstance(filename, str):
            print("❌ Tên file không hợp lệ")
            return False
            
        if not filename.endswith('.tex'):
            print("❌ File phải có đuôi .tex")
            return False
            
        if not os.path.exists(filename):
            print(f"❌ File {filename} không tồn tại")
            return False
        
        try:
            if config.SHOW_PROGRESS:
                print(f"🔄 Đang biên dịch {filename}...")
            
            # Chạy LaTeX engine với batch mode
            cmd = [config.LATEX_ENGINE]
            if config.BATCH_MODE:
                cmd.append('-interaction=batchmode')
            cmd.append(filename)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                timeout=config.COMPILE_TIMEOUT
            )
            
            pdf_filename = filename.replace('.tex', '.pdf')
            
            if result.returncode == 0 and os.path.exists(pdf_filename):
                print(f"✅ Biên dịch thành công: {pdf_filename}")
                return True
            else:
                print(f"❌ Lỗi khi biên dịch (exit code: {result.returncode})")
                # Hiển thị vài dòng cuối của log nếu có lỗi
                log_file = filename.replace('.tex', '.log')
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            print("Một số lỗi từ log:")
                            error_count = 0
                            for line in lines[-LOG_LINES_TO_CHECK:]:  # Kiểm tra 20 dòng cuối
                                if any(keyword in line.lower() for keyword in ['error', '!', 'undefined']):
                                    print(f"  {line.strip()}")
                                    error_count += 1
                                    if error_count >= MAX_ERROR_DISPLAY:  # Chỉ hiển thị 5 lỗi đầu tiên
                                        break
                    except Exception as log_error:
                        print(f"  Không thể đọc log file: {log_error}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Timeout: Biên dịch quá lâu (>{COMPILE_TIMEOUT}s)")
            return False
        except FileNotFoundError:
            print("❌ Không tìm thấy xelatex. Hãy cài đặt TeX Live")
            return False
        except Exception as e:
            print(f"❌ Lỗi không mong đợi khi chạy xelatex: {e}")
            return False


# =============================
# MAIN
# =============================
def main():
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 5
        
        # Load configuration (for future enhancement)
        config = Config()
        
        generator = PlaneGenerator()
        questions_data = generator.generate_multiple_questions(num_questions)
        
        if not questions_data:
            print("Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)
        
        # Use config for output filename
        output_filename = f"{config.get_output_path()}.tex"
        filename = generator.create_latex_file(questions_data, filename=output_filename)
        
        # Tự động biên dịch với config settings
        if config.SHOW_PROGRESS:
            print("🔄 Đang biên dịch LaTeX...")
        success = generator.compile_latex_quietly(filename, config)
        
        if not success:
            print(f"Thử biên dịch thủ công: {config.LATEX_ENGINE} {filename}")
        
    except ValueError:
        print("❌ Lỗi: Vui lòng nhập số câu hỏi hợp lệ")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()