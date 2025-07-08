"""
Dạng toán tối ưu hóa chi phí nhiên liệu tàu
Tương ứng câu 3 trong bai2.tex
"""
import random
import math
from math import gcd
from typing import Dict, Any, List
from base_optimization_question import BaseOptimizationQuestion
from latex_utils import format_number_clean, format_sqrt, format_sqrt_improved, format_dfrac

class FuelCostOptimization(BaseOptimizationQuestion):
    """
    Dạng toán tối ưu hóa chi phí nhiên liệu tàu
    
    Bài toán cốt lõi:
    - Chi phí gồm 2 phần: cố định (a nghìn đồng/giờ) và biến thiên (kv^2 nghìn đồng/giờ)
    - Tìm vận tốc v để chi phí trên 1km là nhỏ nhất
    - f(v) = a/v + kv, tối ưu tại v = sqrt(a/k)
    """
    
    PROBLEM_TEMPLATES = [
        # Đề bài gốc
        '''Trên một khúc sông có dòng nước lặng, một chiếc tàu chạy với tốc độ không đổi, chi phí nhiên liệu được tính bởi hai phần: Phần thứ nhất không phụ thuộc vào tốc độ và mất chi phí {fixed_cost} nghìn đồng/giờ; Phần thứ hai tỉ lệ thuận với bình phương của tốc độ, khi \\(v={ref_speed}(\\mathrm{{~km}} / \\mathrm{{h}})\\) thì chi phí phần thứ hai là {ref_variable_cost} nghìn đồng/giờ. Tìm tốc độ của tàu để tổng chi phí nhiên liệu khi tàu chạy 1 km trên sông là ít nhất (kết quả làm tròn đến hàng phần trăm).''',
        
        # Bài tương tự 1
        '''Một đơn vị vận tải đường thủy đang nghiên cứu phương án giảm thiểu chi phí nhiên liệu trong quá trình vận hành tàu chở hàng trên khúc sông có dòng nước lặng. Việc tối ưu chi phí trở nên quan trọng trong bối cảnh giá nhiên liệu ngày càng tăng và nhu cầu vận chuyển liên tục. Tổng chi phí nhiên liệu cho mỗi giờ hành trình được cấu thành từ hai phần: phần thứ nhất là chi phí cố định, không phụ thuộc vào vận tốc, trị giá {fixed_cost} nghìn đồng/giờ; phần thứ hai là chi phí phụ thuộc vào vận tốc, cụ thể tỉ lệ thuận với bình phương vận tốc của tàu. Tại vận tốc \\(v = {ref_speed}\\) km/h, chi phí phần biến thiên này được xác định là {ref_variable_cost} nghìn đồng/giờ. Bài toán đặt ra là tìm tốc độ \\(v\\) (km/h) để tổng chi phí nhiên liệu cho mỗi km hành trình là ít nhất. Kết quả làm tròn đến hàng phần trăm.''',
        
        # Bài tương tự 2
        '''Một công ty lữ hành đang khai thác tuyến sông nội địa với các tàu du lịch cao cấp phục vụ khách tham quan. Để duy trì lợi nhuận trong mùa thấp điểm, công ty cần tối ưu hóa chi phí nhiên liệu. Qua khảo sát kỹ thuật, người ta xác định rằng chi phí nhiên liệu trong mỗi giờ hành trình bao gồm hai phần: chi phí cố định là {fixed_cost} nghìn đồng, không phụ thuộc vào tốc độ tàu, và chi phí biến thiên phụ thuộc vào bình phương vận tốc. Khi tàu chạy với vận tốc {ref_speed} km/h, chi phí biến thiên đo được là {ref_variable_cost} nghìn đồng mỗi giờ. Hãy xác định vận tốc \\(v\\) (km/h) sao cho chi phí nhiên liệu trên mỗi km hành trình là ít nhất. Làm tròn kết quả đến hàng phần trăm.''',
        
        # Bài tương tự 3
        '''Trên tuyến kênh đào thẳng, không có dòng chảy và thường xuyên được dùng để vận chuyển hàng hóa nặng, một tàu container đang vận hành ổn định. Ban điều hành tuyến vận tải mong muốn tiết kiệm chi phí nhiên liệu nhằm tăng lợi nhuận. Theo phân tích, chi phí nhiên liệu gồm hai phần: phần cố định {fixed_cost} nghìn đồng/giờ, và phần phụ thuộc bình phương vận tốc. Khi tàu chạy với tốc độ {ref_speed} km/h, phần biến thiên này là {ref_variable_cost} nghìn đồng/giờ. Xác định vận tốc \\(v\\) (km/h) sao cho chi phí nhiên liệu để đi hết quãng đường 1 km là ít nhất. Làm tròn đến hàng phần trăm.''',
        
        # Bài tương tự 4
        '''Trên sông lớn với mặt nước êm đềm, một chiếc tàu chở khách được vận hành nhằm phục vụ nhu cầu di chuyển liên tỉnh. Để kiểm soát chi phí vận hành, nhà điều hành tàu cần tính toán vận tốc hợp lý để giảm thiểu lượng nhiên liệu tiêu thụ. Biết rằng chi phí nhiên liệu bao gồm phần không đổi là {fixed_cost} nghìn đồng mỗi giờ và phần biến thiên phụ thuộc bình phương vận tốc. Khi vận tốc tàu là {ref_speed} km/h, phần chi phí biến thiên đo được là {ref_variable_cost} nghìn đồng/giờ. Tìm tốc độ \\(v\\) sao cho chi phí nhiên liệu cho mỗi km hành trình là nhỏ nhất. Làm tròn đến hàng phần trăm.''',
        
        # Bài tương tự 5
        '''Trong công tác cứu hộ trên hồ nước ngọt, thời gian và nhiên liệu đều là những yếu tố cần được tối ưu. Một tàu cứu hộ hiện đang hoạt động thường xuyên và cần xác định tốc độ vận hành hiệu quả nhất. Chi phí nhiên liệu trong mỗi giờ di chuyển bao gồm phần cố định {fixed_cost} nghìn đồng và phần tỉ lệ thuận với bình phương vận tốc. Khi vận tốc là {ref_speed} km/h, phần chi phí biến thiên được đo là {ref_variable_cost} nghìn đồng/giờ. Hãy xác định vận tốc \\(v\\) (km/h) sao cho tổng chi phí nhiên liệu để tàu đi được 1 km là thấp nhất. Làm tròn kết quả đến hàng phần trăm.'''
    ]
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán tối ưu hóa chi phí nhiên liệu"""
        
        # Tham số theo pattern từ bai2.tex
        # Chi phí cố định a (nghìn đồng/giờ)
        fixed_cost = random.choice([630, 600, 650, 580, 670, 610])
        
        # Vận tốc tham chiếu và chi phí biến thiên tương ứng
        ref_speed = 10  # km/h
        ref_variable_cost = random.choice([70, 60, 80, 65, 75])  # nghìn đồng/giờ khi v = 10
        
        # Tính hệ số k: kv^2 = ref_variable_cost khi v = ref_speed
        # k = ref_variable_cost / ref_speed^2
        k = ref_variable_cost / (ref_speed ** 2)
        
        return {
            "fixed_cost": fixed_cost,
            "ref_speed": ref_speed,
            "ref_variable_cost": ref_variable_cost,
            "k": k
        }
    
    def calculate_answer(self) -> str:
        """Tính đáp án đúng"""
        p = self.parameters
        
        # Chi phí tối ưu tại v = sqrt(a/k)
        a = p["fixed_cost"]
        k = p["k"]
        
        optimal_speed = math.sqrt(a / k)
        
        return f"\\({format_number_clean(optimal_speed, precision=2)}\\) km/h"
    
    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý"""
        p = self.parameters
        a = p["fixed_cost"]
        k = p["k"]
        
        optimal_speed = math.sqrt(a / k)
        
        # Các sai lầm thường gặp
        wrong_answers = [
            f"\\({format_number_clean(optimal_speed * 1.1, precision=2)}\\) km/h",  # Cao hơn 10%
            f"\\({format_number_clean(optimal_speed * 0.9, precision=2)}\\) km/h",  # Thấp hơn 10%
            f"\\({p['ref_speed']}\\) km/h"  # Lấy vận tốc tham chiếu
        ]
        
        return wrong_answers
    
    def generate_question_text(self) -> str:
        """Sinh đề bài bằng LaTeX"""
        p = self.parameters
        template = random.choice(self.PROBLEM_TEMPLATES)
        return template.format(**p)
    
    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết"""
        p = self.parameters
        a = p["fixed_cost"]
        ref_speed = p["ref_speed"]
        ref_variable_cost = p["ref_variable_cost"]
        
        # Tính hệ số k đúng như trong bai2.tex: k = ref_variable_cost / ref_speed
        k = ref_variable_cost / ref_speed
        
        # Tính tốc độ tối ưu: x = sqrt(a/k)
        optimal_speed = math.sqrt(a / k)
        
        # Tính chi phí tối thiểu: f(x) = 2*sqrt(a*k)
        min_cost = 2 * math.sqrt(a * k)
        
        # Format các phân số
        one_over_x = format_dfrac(1, 1) + "/x"  # 1/x
        a_over_x = format_dfrac(a, 1) + "/x"    # a/x
        a_over_x_squared = format_dfrac(a, 1) + "/x^2"  # a/x^2
        
        # Xử lý đặc biệt cho căn thức để hiển thị đẹp như trong bai2.tex
        def format_sqrt_special(number):
            """Format căn thức đặc biệt cho bài toán này"""
            sqrt_val = math.sqrt(number)
            
            # Thử tìm dạng a*sqrt(b) với a và b là số nguyên
            for a in range(1, int(sqrt_val) + 1):
                b = number / (a * a)
                if abs(b - round(b)) < 1e-10 and b > 0:
                    b_int = int(round(b))
                    if b_int == 1:
                        return f"{a}"
                    else:
                        if a == 1:
                            return f"\\sqrt{{{b_int}}}"
                        else:
                            return f"{a}\\sqrt{{{b_int}}}"
            
            # Thử tìm dạng a*sqrt(b) với b là phân số đơn giản
            for a in range(1, int(sqrt_val) + 1):
                b = number / (a * a)
                # Kiểm tra xem b có thể viết dưới dạng phân số đơn giản không
                for denom in range(1, 21):  # Thử với mẫu số từ 1 đến 20
                    num = b * denom
                    if abs(num - round(num)) < 1e-10:
                        num_int = int(round(num))
                        if num_int > 0:
                            # Rút gọn phân số
                            gcd_val = gcd(num_int, denom)
                            num_simplified = num_int // gcd_val
                            denom_simplified = denom // gcd_val
                            
                            if denom_simplified == 1:
                                if num_simplified == 1:
                                    return f"{a}"
                                else:
                                    if a == 1:
                                        return f"\\sqrt{{{num_simplified}}}"
                                    else:
                                        return f"{a}\\sqrt{{{num_simplified}}}"
                            else:
                                if a == 1:
                                    return f"\\sqrt{{\\dfrac{{{num_simplified}}}{{{denom_simplified}}}}}"
                                else:
                                    return f"{a}\\sqrt{{\\dfrac{{{num_simplified}}}{{{denom_simplified}}}}}"
            
            # Nếu không thể rút gọn, trả về sqrt(number) với số làm tròn
            return f"\\sqrt{{{format_number_clean(number)}}}"
        
        return f"""
Lời giải:

Gọi \\(x\\) (km/h) là tốc độ của tàu \\((x > 0)\\).

Thời gian để tàu chạy 1 km trên sông là \\({one_over_x}\\) (giờ).

Chi phí cho phần thứ nhất để tàu chạy 1 km là: \\(p_1={a} \\cdot {one_over_x}={a_over_x}\\) (nghìn đồng/giờ).

Chi phí cho phần thứ hai để tàu chạy 1 km có dạng: \\(p_2=k x^2 \\cdot {one_over_x}=k x\\) (nghìn đồng/giờ).

Khi \\(x={ref_speed}\\) thì \\(p_2={ref_variable_cost}\\) nên \\(k={k}\\). Do đó \\(p_2={k} x\\) (nghìn đồng/giờ).

Vậy tổng chi phí để tàu chạy 1 km trên khúc sông đó là: \\(f(x)={a_over_x}+{k} x\\) (nghìn đồng/giờ).

Ta có: \\(f^{{\\prime}}(x)=-{a_over_x_squared}+{k}\\).

        Giải phương trình: \\(f^{{\\prime}}(x)=0 \\Leftrightarrow x={format_sqrt_special(a/k)}\\) (thoả mãn) hoặc \\(x=-{format_sqrt_special(a/k)}\\) (loại vì \\(x>0\\)).

        Lập bảng biến thiên của hàm số \\(f(x)\\) với \\(x>0\\), ta tìm được \\(\\min_{{x \\in(0 ;+\\infty)}} f(x)=f({format_sqrt_special(a/k)})={format_sqrt_special(a*k)}\\).

        Vậy tốc độ của tàu để tổng chi phí nhiên liệu khi tàu chạy 1 km trên sông ít nhất là \\({format_sqrt_special(a/k)} \\approx {format_number_clean(optimal_speed, precision=2)}\\) (km/h).
""" 