"""
Dạng toán nhận diện cực trị, giá trị cực trị, điểm cực trị, hoặc tính đơn điệu của hàm số dựa trên bảng biến thiên (tkzTabInit) hoặc đồ thị (tikzpicture).
Tham khảo format từ production_optimization.py
"""
import random
from typing import Dict, Any, List
from base_optimization_question import BaseOptimizationQuestion
from tikz_figure_library import (
    generate_tkztabinit_latex, 
    generate_tikzpicture_latex,
    generate_cubic_type1_latex,
    generate_cubic_type2_latex, 
    generate_quartic_latex
)

class ExtremumFromTikzQuestion(BaseOptimizationQuestion):
    """
    Dạng toán nhận diện cực trị, giá trị cực trị, điểm cực trị, hoặc tính đơn điệu
    Dựa trên bảng biến thiên hoặc đồ thị hàm số (tkzTabInit hoặc tikzpicture)
    """
    # Danh sách các câu hỏi dạng cực trị, loại bỏ trùng lặp
    QUESTION_TEMPLATES = [
        "Hàm số đạt cực trị tại điểm nào?",
        "Hàm số đạt cực đại tại điểm nào?",
        "Hàm số đạt cực tiểu tại điểm nào?",
        "Hàm số có cực đại là giá trị nào?",
        "Hàm số có cực tiểu là giá trị nào?",
        "Đồ thị hàm số có điểm cực đại là điểm nào?",
        "Đồ thị hàm số có điểm cực tiểu là điểm nào?",
        "Hàm số đồng biến/nghịch biến trên khoảng nào dưới đây?"
    ]

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán cực trị từ bảng biến thiên hoặc đồ thị"""
        # Sinh giá trị số nguyên cho các điểm cực trị (x-coordinates)
        x_values = random.sample([-3, -2, -1, 1, 2, 3], 3)
        x_values.sort()  # Sắp xếp tăng dần: [x1, x2, x3]
        
        # Sinh giá trị số nguyên cho các giá trị cực trị (y-coordinates)  
        y_values = random.sample([-4, -3, -2, -1, 1, 2, 3, 4], 3)
        
        # Sinh thêm các giá trị ngẫu nhiên khác để làm đáp án nhiễu
        extra_x = random.sample([i for i in range(-5, 6) if i not in x_values and i != 0], 2)
        extra_y = random.sample([i for i in range(-5, 6) if i not in y_values and i != 0], 2)
        
        # Chọn kiểu thể hiện: bảng biến thiên hay đồ thị (có nhiều dạng hơn)
        style = random.choice(['tkztab', 'cubic_type1', 'cubic_type2', 'quartic', 'tikzpicture'])
        
        return {
            # Các điểm cực trị (x-coordinates)
            "A": x_values[0],  # x của điểm cực đại
            "B": x_values[1],  # x của điểm cực tiểu 
            "C": x_values[2],  # x của điểm cực trị thứ 3
            
            # Các giá trị cực trị (y-coordinates)
            "D": y_values[0],  # y của cực đại
            "E": y_values[1],  # y của cực tiểu
            "F": y_values[2],  # y của cực trị thứ 3
            
            # Giá trị phụ để làm đáp án nhiễu
            "extra_x": extra_x,
            "extra_y": extra_y,
            
            # Danh sách đầy đủ để dễ truy cập
            "x_extrema": x_values,  # [A, B, C]
            "y_extrema": y_values,  # [D, E, F]
            
            # Kiểu hình vẽ
            "style": style,
            
            # Offset cho biến thể đồ thị
            "m": random.randint(0, 2)
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
            intro = "Cho đồ thị hàm số \\(y=f(x)\\) như hình vẽ dưới đây:"
        elif p["style"] == "cubic_type2": 
            figure = generate_cubic_type2_latex(p)
            intro = "Cho đồ thị hàm số \\(y=f(x)\\) như hình vẽ dưới đây:"
        elif p["style"] == "quartic":
            figure = generate_quartic_latex(p)
            intro = "Cho đồ thị hàm số \\(y=f(x)\\) như hình vẽ dưới đây:"
        else:  # tikzpicture
            figure = generate_tikzpicture_latex(p)
            intro = "Cho đồ thị hàm số \\(y=f(x)\\) như hình vẽ dưới đây:"
        
        # Sử dụng câu hỏi đã được chọn trong calculate_answer
        if not hasattr(self, '_current_question'):
            self._current_question = random.choice(self.QUESTION_TEMPLATES)
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
            self._current_question = random.choice(self.QUESTION_TEMPLATES)
        q = self._current_question
        
        # Lấy giá trị số nguyên từ parameters
        A, B, C = p["A"], p["B"], p["C"]  # Điểm cực trị
        D, E, F = p["D"], p["E"], p["F"]  # Giá trị cực trị
        
        # Quy tắc lấy đáp án đúng dựa trên file 1200k.tex
        if "cực trị tại điểm" in q:
            return f"\\(x={A}\\) hoặc \\(x={B}\\) hoặc \\(x={C}\\)"
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
        else:
            return f"""
            Quan sát đồ thị hàm số, ta thấy:

- Hàm số có các điểm cực trị tại: \\(x = {A}, x = {B}, x = {C}\\)

- Đỉnh cao nhất (cực đại) tại điểm \\(({A}, {D})\\)

- Đỉnh thấp nhất (cực tiểu) tại điểm \\(({B}, {E})\\)

- Các giá trị số nguyên tương ứng trên đồ thị

Từ đó suy ra đáp án cho câu hỏi đã cho.
""" 

# Alias để tương thích với naming convention
ExtremumFromTikz = ExtremumFromTikzQuestion