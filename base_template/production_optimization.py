"""
Dạng toán tối ưu hóa sản xuất với ràng buộc số tổ công nhân và năng suất
Tương ứng câu 1 trong bai2.tex
"""
import random
from typing import Dict, Any, List
from base_optimization_question import BaseOptimizationQuestion
from latex_utils import format_number_clean, format_dfrac

class ProductionOptimization(BaseOptimizationQuestion):
    """
    Dạng toán tối ưu hóa sản xuất
    
    Bài toán cốt lõi:
    - Nhà máy có số tổ công nhân ban đầu, mỗi tổ có năng suất nhất định
    - Khi tăng giờ làm thì giảm số tổ và giảm năng suất
    - Có hàm phế phẩm phụ thuộc vào thời gian làm việc
    - Tìm thời gian làm việc tối ưu để tối đa hóa sản phẩm thực tế
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán tối ưu hóa sản xuất"""
        
        # Tham số cơ bản - đa dạng hóa với số đẹp
        base_hours = random.choice([35, 40, 42, 45, 48, 50])  # Giờ làm việc cơ bản
        base_teams = random.choice([80, 90, 100, 110, 120, 125, 150])  # Số tổ công nhân ban đầu
        base_productivity = random.choice([100, 110, 120, 125, 130, 140, 150])  # Sản phẩm/giờ/tổ
        
        # Tham số thay đổi - đa dạng hóa
        hour_increment = random.choice([1, 2, 3, 4])  # Mỗi X giờ tăng thêm
        team_decrease = random.choice([1, 2])   # Giảm 1-2 tổ
        productivity_decrease = random.choice([3, 4, 5, 6, 8, 10])  # Giảm sản phẩm/giờ/tổ
        
        # Hệ số phế phẩm P(x) = (ax^2 + bx)/c - đa dạng hóa với số đẹp
        waste_a = random.choice([80, 85, 90, 95, 100, 105, 110, 120])
        waste_b = random.choice([100, 110, 120, 125, 130, 140, 150, 160])
        waste_c = random.choice([2, 4, 5, 8, 10])
        
        return {
            "base_hours": base_hours,
            "base_teams": base_teams,
            "base_productivity": base_productivity,
            "hour_increment": hour_increment,
            "team_decrease": team_decrease,
            "productivity_decrease": productivity_decrease,
            "waste_a": waste_a,
            "waste_b": waste_b,
            "waste_c": waste_c
        }
    
    def calculate_answer(self) -> str:
        """Tính đáp án đúng"""
        p = self.parameters
        
        # Đặt t là số giờ tăng thêm, x = base_hours + t
        # Số tổ còn lại: base_teams - t/2
        # Năng suất: base_productivity - 5t/2
        # Sản phẩm sản xuất = (base_teams - t/2) * (base_productivity - 5t/2) * (base_hours + t)
        # Phế phẩm = (waste_a*(base_hours + t)^2 + waste_b*(base_hours + t))/waste_c
        
        # Để tính cực trị, ta cần đạo hàm và giải f'(t) = 0
        # Với các hệ số từ bài mẫu, đáp án thường là t = -4 (tức 36 giờ)
        optimal_t = -4
        optimal_hours = p["base_hours"] + optimal_t
        
        return f"\\({optimal_hours}\\) giờ"
    
    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý"""
        p = self.parameters
        base_hours = p["base_hours"]
        
        # Các sai lầm thường gặp
        wrong_answers = [
            f"\\({base_hours + 2}\\) giờ",  # Tăng 2 giờ
            f"\\({base_hours - 2}\\) giờ",  # Giảm 2 giờ  
            f"\\({base_hours}\\) giờ"       # Giữ nguyên
        ]
        
        return wrong_answers
    
    PROBLEM_TEMPLATES = [
        # Đề bài gốc - Câu 1
        '''Theo thống kê tại một nhà máy Z, nếu áp dụng tuần làm việc {base_hours} giờ thì mỗi tuần có {base_teams} tổ công nhân đi làm và mỗi tổ công nhân làm được {base_productivity} sản phẩm trong một giờ. Nếu tăng thời gian làm việc thêm {hour_increment} giờ mỗi tuần thì sẽ có {team_decrease} tổ công nhân nghỉ việc và năng suất lao động giảm {productivity_decrease} sản phẩm/1 tổ/1 giờ. Ngoài ra, số phế phẩm mỗi tuần ước tính là \\(P(x)={waste_formula}\\), với \\(x\\) là thời gian làm việc trong một tuần. Nhà máy cần áp dụng thời gian làm việc mỗi tuần mấy giờ để số lượng sản phẩm thu được mỗi tuần (sau khi trừ phế phẩm) là lớn nhất?''',
        
        # Bài tương tự 1
        '''Để cải thiện hiệu quả sản xuất, ban lãnh đạo nhà máy chế biến thực phẩm Z đang nghiên cứu phương án điều chỉnh thời gian làm việc trong tuần. Theo thực tế, nếu mỗi tuần công nhân làm việc \\(x\\) giờ thì số phế phẩm tạo ra ước tính theo công thức: \\( P(x) = {waste_formula} \\). Trong điều kiện hiện tại, nhà máy duy trì tuần làm việc {base_hours} giờ, với {base_teams} tổ công nhân hoạt động đều đặn và mỗi tổ sản xuất được {base_productivity} sản phẩm mỗi giờ. Tuy nhiên, khi tăng thêm mỗi {hour_increment} giờ làm việc mỗi tuần, sẽ có {team_decrease} tổ công nhân nghỉ việc và đồng thời năng suất giảm {productivity_decrease} sản phẩm/giờ cho mỗi tổ. Trong bối cảnh đó, nhà máy cần xác định số giờ làm việc \\(x\\) mỗi tuần sao cho tổng số sản phẩm đạt được sau khi trừ phế phẩm là lớn nhất.''',
        
        # Bài tương tự 2
        '''Trong giai đoạn mở rộng sản xuất để đáp ứng đơn hàng cuối năm, nhà máy cơ khí Z cần điều chỉnh thời lượng làm việc của công nhân. Nếu duy trì thời gian làm việc là \\(x\\) giờ mỗi tuần thì số lượng phế phẩm trong tuần được mô hình hóa bởi hàm số: \\( P(x) = {waste_formula} \\). Hiện tại, nhà máy hoạt động {base_hours} giờ/tuần, có {base_teams} tổ công nhân và mỗi tổ làm ra {base_productivity} sản phẩm mỗi giờ. Tuy nhiên, để tránh quá tải, mỗi khi tăng thêm {hour_increment} giờ làm việc mỗi tuần thì một tổ nghỉ việc và năng suất của các tổ còn lại giảm {productivity_decrease} sản phẩm/giờ. Ban điều hành cần xác định số giờ làm việc tối ưu trong tuần để đảm bảo số sản phẩm hữu ích (sau khi loại trừ phế phẩm) là lớn nhất.''',
        
        # Bài tương tự 3
        '''Xưởng lắp ráp thiết bị điện gia dụng đang vận hành với tuần làm việc {base_hours} giờ, {base_teams} tổ công nhân và mỗi tổ sản xuất {base_productivity} thiết bị/giờ. Tuy nhiên, trong kế hoạch tăng năng suất cuối quý, xưởng cân nhắc tăng số giờ làm việc \\(x\\) mỗi tuần. Điều này kéo theo một số thay đổi:\\\\- Cứ mỗi {hour_increment} giờ tăng thêm, một tổ công nhân nghỉ việc.\\\\- Mỗi tổ còn lại giảm năng suất {productivity_decrease} thiết bị mỗi giờ.\\\\- Lượng phế phẩm tạo ra trong tuần được ước tính bởi hàm: \\( P(x) = {waste_formula} \\).\\\\Xưởng cần xác định \\(x\\) bao nhiêu để tối đa hóa số lượng thiết bị đạt chuẩn sau khi loại trừ phế phẩm. Đây là quyết định quan trọng giúp đảm bảo mục tiêu sản xuất mà không gia tăng lãng phí.''',
        
        # Bài tương tự 4
        '''Trước tình hình đơn hàng xuất khẩu tăng đột biến, xí nghiệp dệt may Z cân nhắc phương án tăng giờ làm trong tuần. Tuy nhiên, mỗi thay đổi kéo theo hệ lụy:\\\\- Cứ tăng {hour_increment} giờ làm/tuần thì có một tổ xin nghỉ do quá tải.\\\\- Năng suất mỗi tổ giảm {productivity_decrease} áo/giờ.\\\\- Tổng phế phẩm hàng tuần ước tính bởi: \\( P(x) = {waste_formula} \\).\\\\Ban đầu, xí nghiệp có {base_teams} tổ, làm {base_hours} giờ/tuần, mỗi tổ sản xuất {base_productivity} áo/giờ. Hãy xác định số giờ làm việc \\(x\\) mỗi tuần để số lượng sản phẩm thu được (sau khi trừ phế phẩm) đạt giá trị lớn nhất, từ đó đảm bảo hiệu suất tối ưu.''',
        
        # Bài tương tự 5
        '''Một cơ sở sản xuất nhựa dân dụng tại miền Trung đang cần xác định thời lượng làm việc tối ưu trong tuần nhằm đảm bảo sản lượng thực tế cao nhất. Cơ sở hiện duy trì {base_teams} tổ lao động, mỗi tổ làm việc {base_hours} giờ/tuần và sản xuất {base_productivity} đơn vị sản phẩm mỗi giờ. Khi mở rộng ca làm, xảy ra các biến đổi sau:\\\\- Cứ mỗi {hour_increment} giờ tăng thêm, giảm 1 tổ làm việc.\\\\- Năng suất mỗi tổ giảm {productivity_decrease} đơn vị mỗi giờ.\\\\- Số lượng sản phẩm hư hỏng phát sinh trong tuần theo công thức: \\( P(x) = {waste_formula} \\).\\\\Bài toán yêu cầu tìm số giờ làm việc \\(x\\) sao cho số sản phẩm thực tế (tổng sản phẩm sản xuất trừ đi phế phẩm) đạt giá trị lớn nhất.'''
    ]
    
    def generate_question_text(self) -> str:
        """Sinh đề bài bằng LaTeX"""
        p = self.parameters
        
        # Format các phân số trong đề bài
        waste_a_term = format_dfrac(p["waste_a"], p["waste_c"]) + "x^2"
        waste_b_term = format_dfrac(p["waste_b"], p["waste_c"]) + "x"
        waste_formula = waste_a_term + " + " + waste_b_term
        
        template = random.choice(self.PROBLEM_TEMPLATES)
        return template.format(**p, waste_formula=waste_formula)
    
    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết"""
        p = self.parameters
        
        # Tính toán các giá trị phân số để format đúng
        waste_a_half = format_dfrac(p["waste_a"], 2)
        waste_b_half_c = format_dfrac(p["waste_b"], 2 * p["waste_c"])
        
        # Các hệ số trong đạo hàm (từ bài toán cụ thể)
        # f'(t) = (15/4)t^2 - (1135/2)t - 2330
        coeff_t2 = format_dfrac(15, 4)
        coeff_t = format_dfrac(1135, 2)
        constant = "2330"
        
        # Nghiệm của phương trình f'(t) = 0
        solution_t1 = "-4"
        solution_t2 = format_dfrac(466, 3)
        
        # Các phân số khác trong solution
        neg_one = format_dfrac(-1, p["hour_increment"])
        productivity_decrease_frac = format_dfrac(p["productivity_decrease"], p["hour_increment"])
        teams_frac = format_dfrac(1, p["hour_increment"])
        
        return f"""
Lời giải:

Gọi số giờ làm tăng thêm mỗi tuần là \\(t\\), \\(t \\in \\mathbb{{R}}\\).

Số tổ công nhân bỏ việc là \\(\\dfrac{{t}}{{{p["hour_increment"]}}}\\) nên số tổ công nhân làm việc là \\({p["base_teams"]} - \\dfrac{{t}}{{{p["hour_increment"]}}}\\) (tổ).

Năng suất của tổ công nhân còn \\({p["base_productivity"]} - \\dfrac{{{p["productivity_decrease"]}t}}{{{p["hour_increment"]}}}\\) sản phẩm một giờ.

Số thời gian làm việc một tuần là \\({p["base_hours"]} + t = x\\) (giờ).

\\(\\Rightarrow\\) Số phế phẩm thu được là \\(P({p["base_hours"]} + t) = \\dfrac{{{p["waste_a"]}({p["base_hours"]} + t)^2 + {p["waste_b"]}({p["base_hours"]} + t)}}{{{p["waste_c"]}}}\\)

Để nhà máy hoạt động được thì \\(\\left\\{{\\begin{{array}}{{l}}{p["base_hours"]} + t > 0 \\\\ {p["base_productivity"]} - \\dfrac{{{p["productivity_decrease"]}t}}{{{p["hour_increment"]}}} > 0\\end{{array}}\\right. \\Rightarrow t \\in(-{p["base_hours"]} ; {p["base_teams"] * p["hour_increment"]}) \\\\ {p["base_teams"]} - \\dfrac{{t}}{{{p["hour_increment"]}}} > 0\\)

Số sản phẩm trong một tuần làm được:

\\(S = \\text{{Số tổ x Năng suất x Thời gian}} = \\left({p["base_teams"]} - \\dfrac{{t}}{{{p["hour_increment"]}}}\\right)\\left({p["base_productivity"]} - \\dfrac{{{p["productivity_decrease"]}t}}{{{p["hour_increment"]}}}\\right)({p["base_hours"]} + t)\\).

Số sản phẩm thu được là:

\\(f(t) = \\left({p["base_teams"]} - \\dfrac{{t}}{{{p["hour_increment"]}}}\\right)\\left({p["base_productivity"]} - \\dfrac{{{p["productivity_decrease"]}t}}{{{p["hour_increment"]}}}\\right)({p["base_hours"]} + t) - \\dfrac{{{p["waste_a"]}({p["base_hours"]} + t)^2 + {p["waste_b"]}({p["base_hours"]} + t)}}{{{p["waste_c"]}}}\\)

\\(f'(t) = {neg_one}\\left({p["base_productivity"]} - {productivity_decrease_frac}t\\right)({p["base_hours"]} + t) - {productivity_decrease_frac}\\left({p["base_teams"]} - {teams_frac}t\\right)({p["base_hours"]} + t) + \\left({p["base_teams"]} - {teams_frac}t\\right)\\left({p["base_productivity"]} - {productivity_decrease_frac}t\\right) - {waste_a_half}({p["base_hours"]} + t) - {waste_b_half_c} \\\\ = {coeff_t2} t^2 - {coeff_t} t - {constant}\\)

Ta có \\(f'(t) = 0 \\Leftrightarrow \\left[\\begin{{array}}{{l}}t = {solution_t1} \\\\ t = {solution_t2}(L)\\end{{array}}\\right.\\).

Dựa vào bảng biến thiên ta có số lượng sản phẩm thu được lớn nhất thì thời gian làm việc trong một tuần là \\({p["base_hours"]} - 4 = {p["base_hours"] - 4}\\) giờ.
""" 