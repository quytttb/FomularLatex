"""
Dạng toán tối ưu hóa chi phí trung bình cho chụp đèn hình chóp cụt
Tương ứng câu 5 trong bai2.tex
"""
import random
import math
from typing import Dict, Any, List
from base_optimization_question import BaseOptimizationQuestion
from latex_utils import format_number_clean, format_dfrac

class LampCostOptimization(BaseOptimizationQuestion):
    """
    Dạng toán tối ưu hóa chi phí trung bình cho chụp đèn
    
    Bài toán cốt lõi:
    - Chi phí vật liệu: C(x) = x^2 + a
    - Thời gian sản xuất: T(x) = x + b
    - Tối ưu hóa chi phí trung bình: f(x) = C(x)/T(x)
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán tối ưu hóa chi phí chụp đèn"""
        
        # Tham số theo pattern từ bai2.tex
        # C(x) = x^2 + a, thường a = 108
        cost_a = random.choice([108, 100, 112, 96, 120])
        
        # T(x) = x + b, thường b = 6
        time_b = random.choice([6, 5, 7, 4, 8])
        
        return {
            "cost_a": cost_a,
            "time_b": time_b
        }
    
    def calculate_answer(self) -> str:
        """Tính đáp án đúng"""
        p = self.parameters
        
        # f(x) = (x^2 + a)/(x + b)
        # f'(x) = (2x(x + b) - (x^2 + a))/(x + b)^2 = (x^2 + 2bx - a)/(x + b)^2
        # f'(x) = 0 khi x^2 + 2bx - a = 0
        # x = (-2b + sqrt(4b^2 + 4a))/2 = -b + sqrt(b^2 + a)
        
        a = p["cost_a"]
        b = p["time_b"]
        
        optimal_x = -b + math.sqrt(b*b + a)
        
        return f"\\(x = {format_number_clean(optimal_x)}\\) dm"
    
    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý"""
        p = self.parameters
        a = p["cost_a"]
        b = p["time_b"]
        
        optimal_x = -b + math.sqrt(b*b + a)
        
        # Các sai lầm thường gặp
        wrong_answers = [
            f"\\(x = {format_number_clean(optimal_x * 1.1)}\\) dm",  # Cao hơn 10%
            f"\\(x = {format_number_clean(optimal_x * 0.9)}\\) dm",  # Thấp hơn 10%
            f"\\(x = {format_number_clean(math.sqrt(a))}\\) dm"      # Lấy sqrt(a)
        ]
        
        return wrong_answers
    
    PROBLEM_TEMPLATES = [
        # Đề bài gốc - Câu 5
        '''Một xưởng thủ công mỹ nghệ sản xuất loại chụp đèn trang trí dạng hình chóp cụt tứ giác đều. Gọi \\(x\\) là độ dài cạnh đáy lớn (đơn vị:dm). Tính toán cho thấy tổng chi phí vật liệu (tính bằng nghìn đồng) cho một chụp đèn là \\(C(x)=x^2+{cost_a}\\) (nghìn đồng). Thời gian sản xuất cho một chụp đèn được xác định là \\(T(x)=x+{time_b}\\) (giờ). Xưởng muốn xác định kích thước \\(x\\) để chi phí vật liệu trung bình trên một giờ sản xuất là thấp nhất, nhằm tối ưu hóa hiệu quả sử dụng thời gian và vật liệu.''',
        
        # Bài tương tự 1
        '''Một xưởng chế tác thủ công tại Hội An chuyên sản xuất chao đèn trang trí bằng tre cho các khu nghỉ dưỡng cao cấp. Một loại chao đèn đặc biệt có dạng hình chóp cụt tứ giác đều, được thiết kế tinh xảo để tạo hiệu ứng ánh sáng mềm mại. Để cân đối giữa chi phí vật liệu và thời gian sản xuất cho mỗi sản phẩm, chủ xưởng cần xác định kích thước đáy lớn phù hợp. Gọi \\(x\\) (đơn vị: dm) là độ dài cạnh đáy lớn. Chi phí vật liệu để sản xuất một chao đèn được tính theo công thức \\(C(x) = x^2 + {cost_a}\\) (nghìn đồng), còn thời gian để hoàn thiện một sản phẩm là \\(T(x) = x + {time_b}\\) (giờ). Để sử dụng hiệu quả nguyên vật liệu và công sức lao động, xưởng mong muốn tìm giá trị của \\(x\\) sao cho chi phí vật liệu trung bình trên mỗi giờ sản xuất là nhỏ nhất.''',
        
        # Bài tương tự 2
        '''Một xưởng gốm ở Bát Tràng sản xuất các loại chân đèn gốm theo đơn đặt hàng từ các cửa hàng nội thất. Một mẫu đèn có phần chụp được thiết kế theo dạng hình chóp cụt tứ giác đều với cạnh đáy lớn là \\(x\\) (dm). Chủ xưởng mong muốn tính toán để tiết kiệm nguyên liệu đất sét và công sức lao động. Chi phí vật liệu (nghìn đồng) là \\(C(x) = x^2 + {cost_a}\\), còn thời gian sản xuất mỗi sản phẩm là \\(T(x) = x + {time_b}\\) (giờ). Họ cần xác định kích thước \\(x\\) sao cho chi phí vật liệu trung bình trên mỗi giờ làm việc là thấp nhất.''',
        
        # Bài tương tự 3
        '''Một công ty thiết kế đèn trang trí nhận hợp đồng sản xuất loạt đèn bàn theo mẫu hình chóp cụt tứ giác đều. Để tiết kiệm chi phí và đẩy nhanh tiến độ sản xuất, bộ phận kỹ thuật cần tính toán kích thước đáy lớn tối ưu. Gọi \\(x\\) (dm) là độ dài cạnh đáy lớn, khi đó chi phí vật liệu để làm một chiếc đèn là \\(C(x) = x^2 + {cost_a}\\) (nghìn đồng) và thời gian cần thiết để hoàn thành một sản phẩm là \\(T(x) = x + {time_b}\\) (giờ). Công ty mong muốn biết với kích thước \\(x\\) nào thì chi phí vật liệu trung bình trên mỗi giờ sản xuất sẽ đạt giá trị thấp nhất.''',
        
        # Bài tương tự 4
        '''Một nhóm sinh viên khởi nghiệp sản xuất đèn handmade từ giấy kraft tái chế để phục vụ phân khúc quà tặng sáng tạo. Mẫu đèn chóp cụt tứ giác đều của nhóm rất được ưa chuộng nhờ kiểu dáng độc đáo và tinh tế. Trong quá trình thiết kế và sản xuất, nhóm cần xác định kích thước cạnh đáy lớn \\(x\\) (dm) sao cho hiệu quả sử dụng giấy và thời gian hoàn thiện sản phẩm được tối ưu. Chi phí giấy là \\(C(x) = x^2 + {cost_a}\\) (nghìn đồng) và thời gian sản xuất mỗi đèn là \\(T(x) = x + {time_b}\\) (giờ). Họ cần tìm giá trị của \\(x\\) sao cho chi phí vật liệu trung bình trên một giờ làm việc là nhỏ nhất.''',
        
        # Bài tương tự 5
        '''Một cơ sở sản xuất đồ thủ công mỹ nghệ đang thực hiện đơn hàng xuất khẩu lô đèn trang trí kiểu cổ điển sang thị trường châu Âu. Mỗi chiếc đèn có phần chụp được thiết kế theo dạng hình chóp cụt tứ giác đều, đòi hỏi sự tỉ mỉ trong từng công đoạn gia công. Để đạt hiệu quả cao trong sản xuất hàng loạt, kỹ sư thiết kế của cơ sở cần xác định độ dài cạnh đáy lớn \\(x\\) (dm) sao cho chi phí vật liệu trung bình trên mỗi giờ sản xuất là thấp nhất. Biết rằng chi phí vật liệu là \\(C(x) = x^2 + {cost_a}\\) (nghìn đồng) và thời gian hoàn thành một chiếc đèn là \\(T(x) = x + {time_b}\\) (giờ).'''
    ]
    
    def generate_question_text(self) -> str:
        """Sinh đề bài bằng LaTeX"""
        p = self.parameters
        template = random.choice(self.PROBLEM_TEMPLATES)
        return template.format(**p)
    
    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết"""
        p = self.parameters
        a = p["cost_a"]
        b = p["time_b"]
        optimal_x = -b + math.sqrt(b*b + a)
        min_cost = (optimal_x*optimal_x + a)/(optimal_x + b)
        
        # Format các phân số
        cost_over_time = format_dfrac(1, 1) + "C(x)/T(x)"  # C(x)/T(x)
        x_squared_plus_a = format_dfrac(1, 1) + "(x^2 + " + str(a) + ")"  # (x^2 + a)
        x_plus_b = format_dfrac(1, 1) + "(x + " + str(b) + ")"  # (x + b)
        
        return f"""
Lời giải:

Gọi hàm chi phí vật liệu trung bình trên một giờ sản xuất là \\(f(x)={cost_over_time}=\\dfrac{{x^2+{a}}}{{x+{b}}}, x>0\\).

Ta có \\(f'(x)=\\dfrac{{x^2+{2*b}x-{a}}}{{(x+{b})^2}}=0 \\Leftrightarrow \\left[\\begin{{array}}{{l}}x=-{b}-\\sqrt{{{b*b+a}}}(L) \\\\ x=-{b}+\\sqrt{{{b*b+a}}}\\end{{array}}\\right.\\)

Từ bảng biến thiên ta thấy \\(f(x)\\) đạt GTNN bằng \\({format_number_clean(min_cost)}\\) khi \\(x={format_number_clean(optimal_x)}\\).

Vậy để chi phí vật liệu trung bình trên một giờ sản xuất là thấp nhất thì \\(x={format_number_clean(optimal_x)}\\).
""" 