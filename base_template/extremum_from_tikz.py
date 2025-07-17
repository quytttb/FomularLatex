"""
Dạng toán nhận diện cực trị, giá trị cực trị, điểm cực trị, hoặc tính đơn điệu của hàm số dựa trên bảng biến thiên.
Tham khảo format từ production_optimization.py
"""
import random
from typing import Dict, Any, List
from base_optimization_question import BaseOptimizationQuestion
from tikz_figure_library import (
    # generate_tkztabinit_latex, 
    # generate_cubic_type1_latex,
    # generate_cubic_type2_latex, 
    # generate_quartic_latex
)

class ExtremumFromTikzQuestion(BaseOptimizationQuestion):
    """
    Dạng toán nhận diện cực trị, giá trị cực trị, điểm cực trị, hoặc tính đơn điệu
    Dựa trên bảng biến thiên hoặc đồ thị hàm số (tkzTabInit hoặc tikzpicture)
    """
    # Danh sách các câu hỏi dạng cực trị, loại bỏ trùng lặp
    QUESTIONS = [
        "Hàm số đồng biến/nghịch biến trên khoảng nào dưới đây?",
        "Hàm số đạt cực trị tại điểm nào?",
        "Hàm số đạt cực đại tại điểm nào?",
        "Hàm số đạt cực tiểu tại điểm nào?",
        "Hàm số có cực đại là giá trị nào?",
        "Hàm số có cực tiểu là giá trị nào?",
        "Đồ thị hàm số có điểm cực đại là điểm nào?",
        "Đồ thị hàm số có điểm cực tiểu là điểm nào?",

    ]

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán cực trị từ bảng biến thiên hoặc đồ thị"""
        # Chọn kiểu thể hiện trước để sinh tham số phù hợp
        style = random.choice(['tkztab', 'cubic_type1', 'cubic_type2', 'quartic', 'tikzpicture'])
        
        if style == 'tkztab':
            # Bảng biến thiên - sinh như cũ
            x_values = random.sample([-3, -2, -1, 1, 2, 3], 3)
            x_values.sort()  # Sắp xếp tăng dần: [x1, x2, x3]
            y_values = random.sample([-4, -3, -2, -1, 1, 2, 3, 4], 3)
            A, B, C = x_values
            D, E, F = y_values
            m = random.randint(0, 2)
            
        elif style in ['cubic_type1', 'tikzpicture']:
            # Cubic type 1: A âm (cực đại), B dương (cực tiểu)
            A = random.choice([-3, -2, -1])  # x cực đại (âm)
            B = random.choice([1, 2])        # x cực tiểu (dương) - giảm để có chỗ cho offset
            D = random.choice([1, 2, 3, 4])  # y cực đại (dương)
            E = random.choice([-4, -3, -2, -1])  # y cực tiểu (âm)
            
            # Tham số m: đảm bảo B+m > 0 và B+m > |A|
            min_m_positive = -B + 1  # Đảm bảo B+m > 0
            min_m_greater = abs(A) - B + 1  # Đảm bảo B+m > |A|
            min_m = max(min_m_positive, min_m_greater)
            max_m = 5  # Giới hạn để không quá lớn
            m = random.randint(min_m, max_m) if min_m <= max_m else abs(A) - B + 1
            
            C = random.choice([1, 2, 3])  # Không sử dụng nhưng cần có
            F = random.choice([-4, -3, -2, -1])  # Không sử dụng nhưng cần có
            
        elif style == 'cubic_type2':
            # Cubic type 2: A âm (cực tiểu), B dương (cực đại)
            A = random.choice([-3, -2, -1])  # x cực tiểu (âm)
            B = random.choice([1, 2])        # x cực đại (dương) - giảm để có chỗ cho offset
            D = random.choice([-4, -3, -2, -1])  # y cực tiểu (âm)
            E = random.choice([1, 2, 3, 4])  # y cực đại (dương)
            
            # Tham số m: đảm bảo B+m > 0 và B+m > |A|
            min_m_positive = -B + 1  # Đảm bảo B+m > 0
            min_m_greater = abs(A) - B + 1  # Đảm bảo B+m > |A|
            min_m = max(min_m_positive, min_m_greater)
            max_m = 5  # Giới hạn để không quá lớn
            m = random.randint(min_m, max_m) if min_m <= max_m else abs(A) - B + 1
            
            C = random.choice([1, 2, 3])  # Không sử dụng nhưng cần có
            F = random.choice([-4, -3, -2, -1])  # Không sử dụng nhưng cần có
            
        else:  # quartic
            # Quartic: A âm (cực tiểu trái), C dương (cực tiểu phải)
            A = random.choice([-3, -2, -1])  # x cực tiểu trái (âm)
            C = random.choice([1, 2, 3])     # x cực tiểu phải (dương)
            D = random.choice([-4, -3, -2, -1])  # y cực tiểu (âm)
            E = random.choice([-3, -2, -1])  # y cực đại (âm nhưng cao hơn D)
            
            # Đảm bảo E > D (cực đại cao hơn cực tiểu)
            while E <= D:
                E = random.choice([-3, -2, -1])
            
            B = random.choice([1, 2, 3])  # Không sử dụng nhưng cần có
            F = random.choice([-4, -3, -2, -1])  # Không sử dụng nhưng cần có
            m = 0  # Quartic không dùng m
        
        # Sinh thêm các giá trị ngẫu nhiên khác để làm đáp án nhiễu
        all_x = [A, B, C]
        all_y = [D, E, F]
        extra_x = random.sample([i for i in range(-5, 6) if i not in all_x and i != 0], 2)
        extra_y = random.sample([i for i in range(-5, 6) if i not in all_y and i != 0], 2)
        
        return {
            # Các điểm cực trị (x-coordinates)
            "A": A,
            "B": B,
            "C": C,
            
            # Các giá trị cực trị (y-coordinates)
            "D": D,
            "E": E,
            "F": F,
            
            # Giá trị phụ để làm đáp án nhiễu
            "extra_x": extra_x,
            "extra_y": extra_y,
            
            # Danh sách đầy đủ để dễ truy cập
            "x_extrema": [A, B, C],
            "y_extrema": [D, E, F],
            
            # Kiểu hình vẽ
            "style": style,
            
            # Offset cho biến thể đồ thị
            "m": m
        }

    def generate_question_text(self) -> str:
        """Sinh đề bài bằng LaTeX, random chọn bảng biến thiên hoặc đồ thị"""
        # Đảm bảo parameters đã được khởi tạo
        if not self.parameters:
            self.parameters = self.generate_parameters()
            
        p = self.parameters
        
        # Chọn hàm sinh hình vẽ phù hợp
        if p["style"] == "tkztab":
            figure = generate_tkztabinit_latex(p)
            intro = "Cho hàm số \\(y=f(x)\\) có bảng biến thiên như dưới đây:"
        elif p["style"] == "cubic_type1":
            figure = generate_cubic_type1_latex(p)
            intro = "Cho đồ thị hàm số \\(y=f(x)\\) có đồ thị như hình vẽ dưới đây:"
        elif p["style"] == "cubic_type2": 
            figure = generate_cubic_type2_latex(p)
            intro = "Cho đồ thị hàm số \\(y=f(x)\\) có đồ thị như hình vẽ dưới đây:"
        elif p["style"] == "quartic":
            figure = generate_quartic_latex(p)
            intro = "Cho đồ thị hàm số \\(y=f(x)\\) có đồ thị như hình vẽ dưới đây:"
        else:  # tikzpicture - sử dụng cubic_type1 thay thế
            figure = generate_cubic_type1_latex(p)
            intro = "Cho đồ thị hàm số \\(y=f(x)\\) có đồ thị như hình vẽ dưới đây:"
        
        # Sử dụng câu hỏi đã được chọn trong calculate_answer
        if not hasattr(self, '_current_question'):
            self._current_question = random.choice(self.QUESTIONS)
        question = self._current_question
        
        return f"""{intro}

{figure}

{question}"""

    def calculate_answer(self) -> str:
        """Tính đáp án đúng dựa trên tham số và câu hỏi"""
        # Đảm bảo parameters đã được khởi tạo
        if not self.parameters:
            self.parameters = self.generate_parameters()
            
        p = self.parameters
        # Lưu trữ câu hỏi hiện tại để có thể phân tích
        if not hasattr(self, '_current_question'):
            self._current_question = random.choice(self.QUESTIONS)
        q = self._current_question
        
        # Lấy giá trị số nguyên từ parameters
        A, B, C = p["A"], p["B"], p["C"]  # Điểm cực trị
        D, E, F = p["D"], p["E"], p["F"]  # Giá trị cực trị
        style = p["style"]
        m = p.get("m", 0)
        B_actual = B + m  # Điểm thực tế sau offset
        
        # Quy tắc lấy đáp án đúng dựa trên loại đồ thị và câu hỏi
        if style == "tkztab":
            # Bảng biến thiên có đầy đủ 3 điểm cực trị
            if "cực trị tại điểm" in q:
                # Chọn random 1 trong 3 điểm cực trị
                return f"\\(x={random.choice([A, B, C])}\\)"
            if "cực đại tại điểm" in q:
                return f"\\(x={A}\\)"  # A là điểm cực đại
            if "cực tiểu tại điểm" in q:
                return f"\\(x={B}\\)"  # B là điểm cực tiểu
            if "cực đại là giá trị" in q:
                return f"\\(y={D}\\)"  # D là giá trị cực đại
            if "cực tiểu là giá trị" in q:
                return f"\\(y={E}\\)"  # E là giá trị cực tiểu
            if "điểm cực đại" in q:
                return f"\\(({A},{D})\\)"  # (x_cực_đại, y_cực_đại)
            if "điểm cực tiểu" in q:
                return f"\\(({B},{E})\\)"  # (x_cực_tiểu, y_cực_tiểu)
            if "đồng biến" in q or "nghịch biến" in q:
                return f"\\(({A};{B})\\)"  # Khoảng giữa 2 điểm
        elif style in ["cubic_type1", "cubic_type2", "tikzpicture"]:
            # Hàm bậc 3 chỉ có 2 điểm cực trị (bao gồm cả tikzpicture cũ)
            if "cực trị tại điểm" in q:
                # Chọn random 1 trong 2 điểm cực trị
                return f"\\(x={random.choice([A, B_actual])}\\)"
            if style in ["cubic_type1", "tikzpicture"]:
                # A là cực đại, B_actual là cực tiểu
                if "cực đại tại điểm" in q:
                    return f"\\(x={A}\\)"
                if "cực tiểu tại điểm" in q:
                    return f"\\(x={B_actual}\\)"
                if "cực đại là giá trị" in q:
                    return f"\\(y={D}\\)"
                if "cực tiểu là giá trị" in q:
                    return f"\\(y={E}\\)"
                if "điểm cực đại" in q:
                    return f"\\(({A},{D})\\)"
                if "điểm cực tiểu" in q:
                    return f"\\(({B_actual},{E})\\)"
            else:  # cubic_type2
                # A là cực tiểu, B_actual là cực đại
                if "cực đại tại điểm" in q:
                    return f"\\(x={B_actual}\\)"
                if "cực tiểu tại điểm" in q:
                    return f"\\(x={A}\\)"
                if "cực đại là giá trị" in q:
                    return f"\\(y={E}\\)"
                if "cực tiểu là giá trị" in q:
                    return f"\\(y={D}\\)"
                if "điểm cực đại" in q:
                    return f"\\(({B_actual},{E})\\)"
                if "điểm cực tiểu" in q:
                    return f"\\(({A},{D})\\)"
            if "đồng biến" in q or "nghịch biến" in q:
                return f"\\(({A};{B_actual})\\)"
        elif style == "quartic":
            # Hàm bậc 4 có 3 điểm: A (cực tiểu), 0 (cực đại), C (cực tiểu)
            if "cực trị tại điểm" in q:
                # Chọn random 1 trong 3 điểm cực trị
                return f"\\(x={random.choice([A, 0, C])}\\)"
            if "cực đại tại điểm" in q:
                return f"\\(x=0\\)"
            if "cực tiểu tại điểm" in q:
                return f"\\(x={A}\\)"  # hoặc C, chọn A làm đại diện
            if "cực đại là giá trị" in q:
                return f"\\(y={E}\\)"
            if "cực tiểu là giá trị" in q:
                return f"\\(y={D}\\)"
            if "điểm cực đại" in q:
                return f"\\((0,{E})\\)"
            if "điểm cực tiểu" in q:
                return f"\\(({A},{D})\\)"
            if "đồng biến" in q or "nghịch biến" in q:
                return f"\\(({A};0)\\)"
        else:  # tikzpicture - generic case với 2 điểm
            if "cực trị tại điểm" in q:
                # Chọn random 1 trong 2 điểm cực trị
                return f"\\(x={random.choice([A, B])}\\)"
            if "cực đại tại điểm" in q:
                return f"\\(x={A}\\)"
            if "cực tiểu tại điểm" in q:
                return f"\\(x={B}\\)"
            if "cực đại là giá trị" in q:
                return f"\\(y={D}\\)"
            if "cực tiểu là giá trị" in q:
                return f"\\(y={E}\\)"
            if "điểm cực đại" in q:
                return f"\\(({A},{D})\\)"
            if "điểm cực tiểu" in q:
                return f"\\(({B},{E})\\)"
            if "đồng biến" in q or "nghịch biến" in q:
                return f"\\(({A};{B})\\)"
        return ""

    def generate_wrong_answers(self) -> List[str]:
        """Sinh đáp án sai (nhiễu) theo quy tắc trong file 1200k.tex"""
        # Đảm bảo parameters đã được khởi tạo
        if not self.parameters:
            self.parameters = self.generate_parameters()
            
        p = self.parameters
        A, B, C = p["A"], p["B"], p["C"]  # Điểm cực trị
        D, E, F = p["D"], p["E"], p["F"]  # Giá trị cực trị
        extra_x = p["extra_x"]
        extra_y = p["extra_y"]
        m = p.get("m", 0)
        B_actual = B + m  # Điểm thực tế sau offset
        
        # Đáp án nhiễu: đánh tráo x/y, ghép cặp sai, lấy giá trị không liên quan
        wrongs = [
            f"\\(x={D}\\)",  # Đánh tráo x/y (dùng giá trị y thay x)
            f"\\(y={A}\\)",  # Đánh tráo x/y (dùng giá trị x thay y)
            f"\\(({C},{B})\\)",  # Ghép cặp sai
            f"\\(({D},{E})\\)",  # Ghép 2 giá trị y làm điểm
            f"\\(x={extra_x[0]}\\)",  # Dùng giá trị không liên quan
            f"\\(y={extra_y[0]}\\)",  # Dùng giá trị không liên quan
            f"\\(({A},{F})\\)",  # Cặp điểm sai
            f"\\(({extra_x[1]},{extra_y[1]})\\)",  # Điểm hoàn toàn sai
            f"\\(x={B}\\)",  # Dùng B thay vì B_actual
            f"\\(({B},{E})\\)",  # Dùng B thay vì B_actual trong cặp
        ]
        return random.sample(wrongs, 3)

    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết dựa trên bảng biến thiên hoặc đồ thị"""
        # Đảm bảo parameters đã được khởi tạo
        if not self.parameters:
            self.parameters = self.generate_parameters()
            
        p = self.parameters
        A, B, C = p["A"], p["B"], p["C"]  # Điểm cực trị
        D, E, F = p["D"], p["E"], p["F"]  # Giá trị cực trị
        style = p["style"]
        m = p.get("m", 0)
        B_actual = B + m  # Điểm thực tế sau offset
        
        if style == "tkztab":
            return f"""
Dựa vào bảng biến thiên, ta xác định được:

- Hàm số có các điểm cực trị tại: \\(x = {A}, x = {B}, x = {C}\\)

- Giá trị cực đại: \\(y = {D}\\) tại \\(x = {A}\\)

- Giá trị cực tiểu: \\(y = {E}\\) tại \\(x = {B}\\)

- Điểm cực đại: \\(({A}, {D})\\)

- Điểm cực tiểu: \\(({B}, {E})\\)

Từ đó suy ra đáp án cho câu hỏi đã cho.
"""
        elif style in ["cubic_type1", "cubic_type2"]:
            # Hàm bậc 3 chỉ có 2 điểm cực trị
            if style == "cubic_type1":
                # A là cực đại, B là cực tiểu
                return f"""
            Quan sát đồ thị hàm số, ta thấy:

- Hàm số có các điểm cực trị tại: \\(x = {A}, x = {B_actual}\\)

- Đỉnh cao nhất (cực đại) tại điểm \\(({A}, {D})\\)

- Đỉnh thấp nhất (cực tiểu) tại điểm \\(({B_actual}, {E})\\)

- Các giá trị số nguyên tương ứng trên đồ thị

Từ đó suy ra đáp án cho câu hỏi đã cho.
"""
            else:  # cubic_type2
                # A là cực tiểu, B là cực đại (ngược lại)
                return f"""
            Quan sát đồ thị hàm số, ta thấy:

- Hàm số có các điểm cực trị tại: \\(x = {A}, x = {B_actual}\\)

- Đỉnh cao nhất (cực đại) tại điểm \\(({B_actual}, {E})\\)

- Đỉnh thấp nhất (cực tiểu) tại điểm \\(({A}, {D})\\)

- Các giá trị số nguyên tương ứng trên đồ thị

Từ đó suy ra đáp án cho câu hỏi đã cho.
"""
        elif style == "quartic":
            # Hàm bậc 4 có 3 điểm cực trị: A (cực tiểu), 0 (cực đại), C (cực tiểu)
            return f"""
            Quan sát đồ thị hàm số, ta thấy:

- Hàm số có các điểm cực trị tại: \\(x = {A}, x = 0, x = {C}\\)

- Đỉnh cao nhất (cực đại) tại điểm \\((0, {E})\\)

- Đỉnh thấp nhất (cực tiểu) tại điểm \\(({A}, {D})\\) và \\(({C}, {D})\\)

- Các giá trị số nguyên tương ứng trên đồ thị

Từ đó suy ra đáp án cho câu hỏi đã cho.
"""
        else:  # tikzpicture - default generic case
            return f"""
            Quan sát đồ thị hàm số, ta thấy:

- Hàm số có các điểm cực trị tại: \\(x = {A}, x = {B_actual}\\)

- Đỉnh cao nhất (cực đại) tại điểm \\(({A}, {D})\\)

- Đỉnh thấp nhất (cực tiểu) tại điểm \\(({B_actual}, {E})\\)

- Các giá trị số nguyên tương ứng trên đồ thị

Từ đó suy ra đáp án cho câu hỏi đã cho.
""" 

# Alias để tương thích với naming convention
ExtremumFromTikz = ExtremumFromTikzQuestion