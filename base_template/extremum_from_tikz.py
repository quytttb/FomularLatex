"""
Dạng toán nhận diện cực trị, giá trị cực trị, điểm cực trị, hoặc tính đơn điệu của hàm số dựa trên bảng biến thiên.
Tham khảo format từ production_optimization.py
"""
import random
from typing import Dict, Any, List
from base_optimization_question import BaseOptimizationQuestion
from tikz_figure_library import (
    generate_monotonicity_table_type1,
    generate_monotonicity_table_type2
)
from latex_utils import (
    clean_latex_expression,
    format_number_clean,
    strip_latex_inline_math
)

def format_interval_simple(a, b, open_left=True, open_right=True):
    """Hàm đơn giản để format khoảng"""
    left = "(" if open_left else "["
    right = ")" if open_right else "]"
    
    # Xử lý các giá trị đặc biệt
    if str(a) == '-\\infty' or str(a) == '-infty':
        a_str = "-\\infty"
    else:
        a_str = format_number_clean(a) if isinstance(a, (int, float)) else str(a)
    
    if str(b) == '+\\infty' or str(b) == '+infty':
        b_str = "+\\infty"
    else:
        b_str = format_number_clean(b) if isinstance(b, (int, float)) else str(b)
    
    return f"{left}{a_str}; {b_str}{right}"

class ExtremumFromTikzQuestion(BaseOptimizationQuestion):
    """
    Dạng toán nhận diện cực trị, giá trị cực trị, điểm cực trị, hoặc tính đơn điệu
    Dựa trên bảng biến thiên
    """
    # Template câu hỏi cho 2 dạng bảng biến thiên
    QUESTIONS_TYPE1 = [
        "Hàm số nghịch biến trên khoảng nào?",
        "Hàm số có bao nhiêu cực trị?", 
        "Hàm số có bao nhiêu cực tiểu?",
        "Phương trình f'(x) = a có bao nhiêu nghiệm?"
    ]
    
    QUESTIONS_TYPE2 = [
        "Hàm số đồng biến trên khoảng nào?",
        "Hàm số có bao nhiêu cực trị?",
        "Hàm số có bao nhiêu cực đại?", 
        "Phương trình f'(x) = a có bao nhiêu nghiệm?"
    ]

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán cực trị từ bảng biến thiên monotonicity"""
        # Chọn kiểu bảng biến thiên: type1 (dạng W) hoặc type2 (dạng M)
        monotonicity_type = random.choice(['monotonicity_type1', 'monotonicity_type2'])
        
        # Sinh 3 điểm nghiệm của f"(x) = 0, đảm bảo A < B < C (tham khảo dothihamso3.py)
        A = random.randint(-5, -1)
        B = random.randint(0, 3) 
        C = random.randint(4, 7)
        while B <= A or C <= B:
            A = random.randint(-5, -1)
            B = random.randint(0, 3)
            C = random.randint(4, 7)
        
        # Sinh các giá trị của f'(x) tại các điểm đặc biệt (tham khảo dothihamso3.py)
        if monotonicity_type == 'monotonicity_type1':
            # Type 1 (W): giống generate_question_type_1
            D = random.randint(-10, -6)
            F = random.randint(-4, -1)
            while D == F or D in [A, B, C] or F in [A, B, C]:
                D = random.randint(-10, -6)
                F = random.randint(-4, -1)
            O = random.randint(8, 10)
        else:
            # Type 2 (M): giống generate_question_type_2  
            D = random.randint(1, 3)
            F = random.randint(8, 10)
            while D == F or D in [A, B, C] or F in [A, B, C]:
                D = random.randint(1, 3)
                F = random.randint(8, 10)
            O = random.randint(-5, -1)
        
        # Sinh thêm các giá trị ngẫu nhiên khác để làm đáp án nhiễu
        all_x = [A, B, C]
        all_y = [D, F, O]
        extra_x = random.sample([i for i in range(-5, 6) if i not in all_x and i != 0], 2)
        extra_y = random.sample([i for i in range(-5, 6) if i not in all_y and i != 0], 2)
        
        return {
            # Các điểm nghiệm của f"(x) = 0 (x-coordinates)
            "A": A,
            "B": B, 
            "C": C,
            
            # Các giá trị của f'(x) tại các điểm đặc biệt (y-coordinates)
            "D": D,
            "F": F,
            "O": O,
            
            # Giá trị phụ để làm đáp án nhiễu
            "extra_x": extra_x,
            "extra_y": extra_y,
            
            # Danh sách đầy đủ để dễ truy cập
            "x_extrema": [A, B, C],
            "y_extrema": [D, F, O],
            
            # Kiểu bảng biến thiên
            "monotonicity_type": monotonicity_type
        }

    def generate_question_text(self) -> str:
        """Sinh đề bài bằng LaTeX với bảng biến thiên monotonicity"""
        # Đảm bảo parameters đã được khởi tạo
        if not self.parameters:
            self.parameters = self.generate_parameters()
            
        p = self.parameters
        
        # Chọn hàm sinh bảng biến thiên phù hợp
        if p["monotonicity_type"] == "monotonicity_type1":
            figure = generate_monotonicity_table_type1(p)
            intro = "Cho hàm số \\(y=f(x)\\) có bảng biến thiên \\(f'(x)\\) như dưới đây:"
        else:  # monotonicity_type2
            figure = generate_monotonicity_table_type2(p)
            intro = "Cho hàm số \\(y=f(x)\\) có bảng biến thiên \\(f'(x)\\) như dưới đây:"
        
        # Sử dụng câu hỏi đã được chọn trong calculate_answer
        if not hasattr(self, '_current_question'):
            # Chọn câu hỏi theo monotonicity_type
            if p["monotonicity_type"] == "monotonicity_type1":
                self._current_question = random.choice(self.QUESTIONS_TYPE1)
            else:
                self._current_question = random.choice(self.QUESTIONS_TYPE2)
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
            # Chọn câu hỏi theo monotonicity_type
            if p["monotonicity_type"] == "monotonicity_type1":
                self._current_question = random.choice(self.QUESTIONS_TYPE1)
            else:
                self._current_question = random.choice(self.QUESTIONS_TYPE2)
        q = self._current_question
        
        # Lấy giá trị từ parameters
        A, B, C = p["A"], p["B"], p["C"]  # Điểm nghiệm của f'(x) = 0
        D, F, O = p["D"], p["F"], p["O"]  # Giá trị của f(x)
        monotonicity_type = p["monotonicity_type"]
        
        # Quy tắc lấy đáp án đúng dựa trên loại bảng biến thiên và câu hỏi
        if monotonicity_type == "monotonicity_type1":
            # Type 1 (dạng W): dấu -, 0, +, 0, -, 0, +
            # Cực trị: A (cực tiểu), B (cực đại), C (cực tiểu)
            # Nghịch biến trên: (-∞,A) ∪ (B,C), đồng biến trên: (A,B) ∪ (C,+∞)
            
            if "nghịch biến" in q:
                # a) Hàm số nghịch biến trên khoảng nào?
                intervals = [
                    f"\\({format_interval_simple('-\\infty', A, True, True)}\\)",
                    f"\\({format_interval_simple(B, C, True, True)}\\)"
                ]
                return random.choice(intervals)
                
            elif "có bao nhiêu cực trị" in q:
                # b) Hàm số có bao nhiêu cực trị?
                return "3"
                
            elif "có bao nhiêu cực tiểu" in q:
                # c) Hàm số có bao nhiêu cực tiểu?
                return "2"
                
            elif "f'(x) = a có bao nhiêu nghiệm" in q:
                # d) Phương trình f'(x) = a có bao nhiêu nghiệm?
                # Phụ thuộc vào giá trị a, thường cho a = 0 hoặc a trong khoảng đặc biệt
                # Cho a = 0: có 3 nghiệm (tại A, B, C)
                return "3"  # Mặc định cho a = 0
                
        else:  # monotonicity_type2
            # Type 2 (dạng M): dấu +, 0, -, 0, +, 0, -
            # Cực trị: A (cực đại), B (cực tiểu), C (cực đại)  
            # Đồng biến trên: (-∞,A) ∪ (B,C), nghịch biến trên: (A,B) ∪ (C,+∞)
            
            if "đồng biến" in q:
                # a) Hàm số đồng biến trên khoảng nào?
                intervals = [
                    f"\\({format_interval_simple('-\\infty', A, True, True)}\\)",
                    f"\\({format_interval_simple(B, C, True, True)}\\)"
                ]
                return random.choice(intervals)
                
            elif "có bao nhiêu cực trị" in q:
                # b) Hàm số có bao nhiêu cực trị?
                return "3"
                
            elif "có bao nhiêu cực đại" in q:
                # c) Hàm số có bao nhiêu cực đại?
                return "2"
                
            elif "f'(x) = a có bao nhiêu nghiệm" in q:
                # d) Phương trình f'(x) = a có bao nhiêu nghiệm?
                # Phụ thuộc vào giá trị a, thường cho a = 0 hoặc a trong khoảng đặc biệt
                # Cho a = 0: có 3 nghiệm (tại A, B, C)
                return "3"  # Mặc định cho a = 0
                
        return ""

    def generate_wrong_answers(self) -> List[str]:
        """Sinh đáp án sai (nhiễu) theo template câu hỏi mới"""
        # Đảm bảo parameters đã được khởi tạo
        if not self.parameters:
            self.parameters = self.generate_parameters()
            
        p = self.parameters
        A, B, C = p["A"], p["B"], p["C"]  # Điểm nghiệm của f'(x) = 0
        monotonicity_type = p["monotonicity_type"]
        
        # Lấy câu hỏi hiện tại
        if not hasattr(self, '_current_question'):
            if monotonicity_type == "monotonicity_type1":
                self._current_question = random.choice(self.QUESTIONS_TYPE1)
            else:
                self._current_question = random.choice(self.QUESTIONS_TYPE2)
        q = self._current_question
        
        # Sinh đáp án sai dựa trên loại câu hỏi
        if "nghịch biến" in q or "đồng biến" in q:
            # Câu a) - Đáp án sai là các khoảng ngược lại hoặc sai
            if monotonicity_type == "monotonicity_type1":
                # Đúng: nghịch biến trên (-∞,A) ∪ (B,C)
                # Sai: đưa khoảng đồng biến hoặc khoảng sai
                wrongs = [
                    f"\\({format_interval_simple(A, B, True, True)}\\)",  # Khoảng đồng biến thay vì nghịch biến
                    f"\\({format_interval_simple(C, '+\\infty', True, True)}\\)",  # Khoảng đồng biến khác
                    f"\\({format_interval_simple('-\\infty', '+\\infty', True, True)}\\)",  # Toàn bộ tập xác định
                    f"\\({format_interval_simple(A, C, True, True)}\\)"  # Khoảng sai
                ]
            else:  # type2
                # Đúng: đồng biến trên (-∞,A) ∪ (B,C)
                # Sai: đưa khoảng nghịch biến hoặc khoảng sai
                wrongs = [
                    f"\\({format_interval_simple(A, B, True, True)}\\)",  # Khoảng nghịch biến thay vì đồng biến
                    f"\\({format_interval_simple(C, '+\\infty', True, True)}\\)",  # Khoảng nghịch biến khác
                    f"\\({format_interval_simple('-\\infty', '+\\infty', True, True)}\\)",  # Toàn bộ tập xác định
                    f"\\({format_interval_simple(A, C, True, True)}\\)"  # Khoảng sai
                ]
        
        elif "có bao nhiêu cực trị" in q:
            # Câu b) - Đúng: 3, Sai: 1, 2, 4, 5
            wrongs = ["1", "2", "4", "5", "0"]
            
        elif "có bao nhiêu cực tiểu" in q or "có bao nhiêu cực đại" in q:
            # Câu c) - Đúng: 2, Sai: 0, 1, 3, 4
            wrongs = ["0", "1", "3", "4", "5"]
            
        elif "f'(x) = a có bao nhiêu nghiệm" in q:
            # Câu d) - Đúng: 3 (cho a=0), Sai: 0, 1, 2, 4, 5, 6
            wrongs = ["0", "1", "2", "4", "5", "6"]
            
        else:
            # Fallback - đáp án mặc định
            wrongs = ["1", "2", "4", "5"]
        
        return random.sample(wrongs, min(3, len(wrongs)))

    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết dựa trên bảng biến thiên và template câu hỏi mới"""
        # Đảm bảo parameters đã được khởi tạo
        if not self.parameters:
            self.parameters = self.generate_parameters()
            
        p = self.parameters
        A, B, C = p["A"], p["B"], p["C"]  # Điểm nghiệm của f'(x) = 0
        monotonicity_type = p["monotonicity_type"]
        
        # Lấy câu hỏi hiện tại
        if not hasattr(self, '_current_question'):
            if monotonicity_type == "monotonicity_type1":
                self._current_question = random.choice(self.QUESTIONS_TYPE1)
            else:
                self._current_question = random.choice(self.QUESTIONS_TYPE2)
        q = self._current_question
        
        if monotonicity_type == "monotonicity_type1":
            # Dạng W: dấu -, 0, +, 0, -, 0, +
            base_analysis = f"""Dựa vào bảng biến thiên \\(f'(x)\\), ta xác định được:

- Dấu của \\(f'(x)\\): âm trên \\({format_interval_simple('-\\infty', A, True, True)}\\), dương trên \\({format_interval_simple(A, B, True, True)}\\), âm trên \\({format_interval_simple(B, C, True, True)}\\), dương trên \\({format_interval_simple(C, '+\\infty', True, True)}\\)

- Hàm số có các điểm cực trị tại: \\(x = {format_number_clean(A)}, x = {format_number_clean(B)}, x = {format_number_clean(C)}\\)

- Điểm cực tiểu: \\(x = {format_number_clean(A)}\\) và \\(x = {format_number_clean(C)}\\) (chuyển từ giảm sang tăng)

- Điểm cực đại: \\(x = {format_number_clean(B)}\\) (chuyển từ tăng sang giảm)

- Hàm số nghịch biến trên \\({format_interval_simple('-\\infty', A, True, True)} \\cup {format_interval_simple(B, C, True, True)}\\)

- Hàm số đồng biến trên \\({format_interval_simple(A, B, True, True)} \\cup {format_interval_simple(C, '+\\infty', True, True)}\\)"""

            if "nghịch biến" in q:
                return clean_latex_expression(base_analysis + f"""

**Kết luận:** Hàm số nghịch biến trên các khoảng \\({format_interval_simple('-\\infty', A, True, True)}\\) và \\({format_interval_simple(B, C, True, True)}\\).""")
            elif "có bao nhiêu cực trị" in q:
                return clean_latex_expression(base_analysis + f"""

**Kết luận:** Hàm số có 3 cực trị (tại x = {format_number_clean(A)}, x = {format_number_clean(B)}, x = {format_number_clean(C)}).""")
            elif "có bao nhiêu cực tiểu" in q:
                return clean_latex_expression(base_analysis + f"""

**Kết luận:** Hàm số có 2 cực tiểu (tại x = {format_number_clean(A)} và x = {format_number_clean(C)}).""")
            elif "f'(x) = a có bao nhiêu nghiệm" in q:
                return clean_latex_expression(base_analysis + f"""

**Kết luận:** Với a = 0, phương trình f'(x) = 0 có 3 nghiệm (tại x = {format_number_clean(A)}, x = {format_number_clean(B)}, x = {format_number_clean(C)}).""")
            
        else:  # monotonicity_type2
            # Dạng M: dấu +, 0, -, 0, +, 0, -
            base_analysis = f"""Dựa vào bảng biến thiên \\(f'(x)\\), ta xác định được:

- Dấu của \\(f'(x)\\): dương trên \\({format_interval_simple('-\\infty', A, True, True)}\\), âm trên \\({format_interval_simple(A, B, True, True)}\\), dương trên \\({format_interval_simple(B, C, True, True)}\\), âm trên \\({format_interval_simple(C, '+\\infty', True, True)}\\)

- Hàm số có các điểm cực trị tại: \\(x = {format_number_clean(A)}, x = {format_number_clean(B)}, x = {format_number_clean(C)}\\)

- Điểm cực đại: \\(x = {format_number_clean(A)}\\) và \\(x = {format_number_clean(C)}\\) (chuyển từ tăng sang giảm)

- Điểm cực tiểu: \\(x = {format_number_clean(B)}\\) (chuyển từ giảm sang tăng)

- Hàm số đồng biến trên \\({format_interval_simple('-\\infty', A, True, True)} \\cup {format_interval_simple(B, C, True, True)}\\)

- Hàm số nghịch biến trên \\({format_interval_simple(A, B, True, True)} \\cup {format_interval_simple(C, '+\\infty', True, True)}\\)"""

            if "đồng biến" in q:
                return clean_latex_expression(base_analysis + f"""

**Kết luận:** Hàm số đồng biến trên các khoảng \\({format_interval_simple('-\\infty', A, True, True)}\\) và \\({format_interval_simple(B, C, True, True)}\\).""")
            elif "có bao nhiêu cực trị" in q:
                return clean_latex_expression(base_analysis + f"""

**Kết luận:** Hàm số có 3 cực trị (tại x = {format_number_clean(A)}, x = {format_number_clean(B)}, x = {format_number_clean(C)}).""")
            elif "có bao nhiêu cực đại" in q:
                return clean_latex_expression(base_analysis + f"""

**Kết luận:** Hàm số có 2 cực đại (tại x = {format_number_clean(A)} và x = {format_number_clean(C)}).""")
            elif "f'(x) = a có bao nhiêu nghiệm" in q:
                return clean_latex_expression(base_analysis + f"""

**Kết luận:** Với a = 0, phương trình f'(x) = 0 có 3 nghiệm (tại x = {format_number_clean(A)}, x = {format_number_clean(B)}, x = {format_number_clean(C)}).""")
        
        return clean_latex_expression(base_analysis) 

# Alias để tương thích với naming convention
ExtremumFromTikz = ExtremumFromTikzQuestion