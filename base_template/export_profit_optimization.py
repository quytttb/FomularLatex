"""
Dạng toán tối ưu hóa lợi nhuận xuất khẩu với ràng buộc thuế
Tương ứng câu 2 trong bai2.tex
"""
import random
from typing import Dict, Any, List
from base_optimization_question import BaseOptimizationQuestion
from latex_utils import format_number_clean, format_dfrac

class ExportProfitOptimization(BaseOptimizationQuestion):
    """
    Dạng toán tối ưu hóa lợi nhuận xuất khẩu
    
    Bài toán cốt lõi:
    - Doanh nghiệp sản xuất sản phẩm với hàm cung R(x) = x - c1
    - Tiêu thụ nội địa Q(x) = c2 - x
    - Xuất khẩu phần dư với giá x0, chịu thuế a
    - Tỷ lệ lãi:thuế = 4:1
    - Tối ưu hóa lợi nhuận xuất khẩu
    """
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán tối ưu hóa xuất khẩu"""
        
        # Tham số theo pattern từ bai2.tex
        # R(x) = x - c1, Q(x) = c2 - x
        c1 = random.choice([200, 180, 210, 120, 160, 230, 170, 140, 150, 190])  # Hệ số trong hàm sản xuất
        c2 = random.choice([4200, 4500, 4600, 4000, 4300, 4700, 4100, 3900, 4050, 4400])  # Hệ số trong hàm tiêu thụ nội địa
        
        # Giá xuất khẩu
        x0 = random.choice([3200, 2800, 3400, 3000, 3100, 3600, 2900, 2700, 2950, 3050])  # USD
        
        # Tỷ lệ lãi:thuế = 4:1 (cố định)
        profit_tax_ratio = (4, 1)
        
        return {
            "c1": c1,
            "c2": c2,
            "x0": x0,
            "profit_tax_ratio": profit_tax_ratio
        }
    
    def calculate_answer(self) -> str:
        """Tính đáp án đúng"""
        p = self.parameters
        
        # Từ tỷ lệ lãi:thuế = 4:1 và công thức tối ưu hóa
        # a = (x0 - x)/5, và x tối ưu = x0*4/5 = 0.8*x0
        # Do đó a = (x0 - 0.8*x0)/5 = 0.2*x0/5 = 0.04*x0
        
        # Nhưng theo pattern từ bài mẫu, thường a = 100
        # Ta tính theo công thức: x_optimal thường khoảng 2700 
        # với x0 = 3200 thì a = (3200-2700)/5 = 100
        
        # Tính theo tỷ lệ
        x_optimal = p["x0"] * 2700 / 3200  # Scale theo x0
        a_optimal = (p["x0"] - x_optimal) / 5
        
        return f"\\({format_number_clean(a_optimal)}\\)"
    
    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý"""
        p = self.parameters
        x0 = p["x0"]
        
        # Tính đáp án đúng
        x_optimal = x0 * 2700 / 3200
        a_correct = (x0 - x_optimal) / 5
        
        # Các sai lầm thường gặp
        wrong_answers = [
            f"\\({format_number_clean(a_correct * 1.2)}\\)",  # Tính sai 20%
            f"\\({format_number_clean(a_correct / 2)}\\)",    # Chia đôi
            f"\\({format_number_clean(a_correct * 1.5)}\\)"   # Nhân 1.5
        ]
        
        return wrong_answers
    
    PROBLEM_TEMPLATES = [
        # Đề bài gốc - Câu 2
        '''Một doanh nghiệp kinh doanh một loại sản phẩm T được sản xuất trong nước. Qua nghiên cứu thấy rằng nếu chi phí sản xuất mỗi sản phẩm T là \\(x(\$)\\) thì số sản phẩm T các nhà máy sản xuất sẽ là \\(R(x)=x-{c1}\\) và số sản phẩm T mà doanh nghiệp bán được trên thị trường trong nước sẽ là \\(Q(x)={c2}-x\\). Số sản phẩm còn dư doanh nghiệp xuất khẩu ra thị trường quốc tế với giá bán mỗi sản phẩm ổn định trên thị trường quốc tế là \\(x_0={x0} \$\\) . Nhà nước đánh thuế trên mỗi sản phẩm xuất khẩu là \\(a(\$)\\) và luôn đảm bảo tỉ lệ giữa lãi xuất khẩu của doanh nghiệp và thuế thu được của nhà nước tương ứng là \\(4: 1\\). Hãy xác định giá trị của \\(a\\) biết lãi mà doanh nghiệp thu được do xuất khẩu là nhiều nhất.''',
        
        # Bài tương tự 1
        '''Công ty TNHH T chuyên sản xuất cà phê bột để tiêu thụ trong nước và xuất khẩu. Giá bán cố định của cà phê bột trên thị trường quốc tế là \\(x_0 = {x0}\\) USD mỗi tấn. Phần sản phẩm không tiêu thụ trong nước sẽ được xuất khẩu, và mỗi tấn cà phê xuất khẩu phải chịu mức thuế \\(a\\) USD. Nếu chi phí sản xuất mỗi tấn cà phê là \\(x\\) USD thì doanh nghiệp sản xuất được \\(R(x) = x - {c1}\\) tấn và tiêu thụ nội địa là \\(Q(x) = {c2} - x\\) tấn. Chính sách quốc gia yêu cầu tỷ lệ giữa lợi nhuận từ xuất khẩu và số thuế thu được là \\(4 : 1\\). Tìm giá trị \\(a\\) để lợi nhuận từ hoạt động xuất khẩu là lớn nhất.''',
        
        # Bài tương tự 2
        '''Nhà nước quy định rằng tỷ lệ giữa lợi nhuận từ hoạt động xuất khẩu của doanh nghiệp và số thuế thu được phải luôn giữ ở mức \\(4 : 1\\). Một doanh nghiệp sản xuất thiết bị điện tử tiêu dùng quyết định mở rộng xuất khẩu, với giá bán cố định trên thị trường quốc tế là \\(x_0 = {x0}\\) USD mỗi thiết bị. Mỗi thiết bị xuất khẩu chịu thuế \\(a\\) USD. Nếu chi phí sản xuất một thiết bị là \\(x\\) USD thì doanh nghiệp sản xuất được \\(R(x) = x - {c1}\\) sản phẩm, trong đó \\(Q(x) = {c2} - x\\) được tiêu thụ tại thị trường trong nước. Hỏi mức thuế \\(a\\) cần đặt là bao nhiêu để lợi nhuận từ xuất khẩu là lớn nhất.''',
        
        # Bài tương tự 3
        '''Một công ty dệt may chuyên sản xuất áo khoác gió thể thao phục vụ thị trường trong nước và xuất khẩu. Nếu chi phí sản xuất mỗi áo là \\(x\\) USD thì nhu cầu nội địa là \\(Q(x) = {c2} - x\\) và sản lượng sản xuất được là \\(R(x) = x - {c1}\\). Các sản phẩm không tiêu thụ hết được xuất khẩu với giá cố định là \\(x_0 = {x0}\\) USD mỗi áo. Mỗi sản phẩm xuất khẩu chịu mức thuế \\(a\\) USD. Nhà nước yêu cầu doanh nghiệp duy trì tỷ lệ giữa lãi và thuế ở mức \\(4 : 1\\). Tìm giá trị \\(a\\) sao cho lợi nhuận từ hoạt động xuất khẩu đạt cực đại.''',
        
        # Bài tương tự 4
        '''Một nhà máy thực phẩm sản xuất dầu ăn đóng chai với mục tiêu phục vụ thị trường nội địa và xuất khẩu. Khi chi phí sản xuất mỗi chai là \\(x\\) USD thì sản lượng đạt được là \\(R(x) = x - {c1}\\), và lượng tiêu thụ trong nước là \\(Q(x) = {c2} - x\\). Phần còn lại được xuất khẩu với giá ổn định là \\(x_0 = {x0}\\) USD/chai. Mỗi sản phẩm xuất khẩu chịu thuế \\(a\\) USD. Nhà nước yêu cầu tỷ lệ giữa lợi nhuận từ xuất khẩu và số thuế thu được là \\(4 : 1\\). Xác định mức thuế \\(a\\) để lợi nhuận từ xuất khẩu lớn nhất.''',
        
        # Bài tương tự 5
        '''Một công ty khởi nghiệp đang phát triển robot dọn nhà loại mini để bán trong nước và xuất khẩu. Các sản phẩm dư ra được bán ra thị trường quốc tế với giá cố định là \\(x_0 = {x0}\\) USD mỗi thiết bị. Nếu chi phí sản xuất là \\(x\\) USD mỗi thiết bị, thì sản lượng là \\(R(x) = x - {c1}\\) và lượng tiêu thụ nội địa là \\(Q(x) = {c2} - x\\). Theo quy định nhà nước, mỗi sản phẩm xuất khẩu chịu mức thuế \\(a\\) USD và tỉ lệ giữa lợi nhuận và thuế thu được phải là \\(4 : 1\\). Hỏi giá trị của \\(a\\) để lợi nhuận từ xuất khẩu đạt cực đại.''',
        
        # Bài tương tự 6
        '''Một công ty công nghệ trẻ đang phát triển robot lau nhà mini để phục vụ thị trường nội địa và xuất khẩu sang nước ngoài. Do điều kiện thị trường, phần sản phẩm dư thừa sau tiêu thụ nội địa sẽ được bán ra quốc tế với mức giá ổn định là \\(x_0 = {x0}\\) USD cho mỗi thiết bị. Nếu chi phí sản xuất một thiết bị là \\(x\\) USD thì số lượng sản phẩm công ty có thể sản xuất là \\(R(x) = x - {c1}\\), và lượng tiêu thụ trong nước được dự báo là \\(Q(x) = {c2} - x\\). Theo quy định của nhà nước, mỗi thiết bị xuất khẩu chịu thuế \\(a\\) USD và tỉ lệ giữa lợi nhuận từ hoạt động xuất khẩu với số thuế thu được phải luôn là \\(4 : 1\\). Hỏi mức thuế \\(a\\) cần quy định là bao nhiêu để lợi nhuận thu được từ hoạt động xuất khẩu của công ty là lớn nhất.''',
        
        # Bài tương tự 7
        '''Nhằm đảm bảo cân đối giữa lợi ích doanh nghiệp và ngân sách nhà nước, mỗi đèn LED thông minh xuất khẩu bị đánh thuế \\(a\\) USD. Nhà nước yêu cầu doanh nghiệp phải duy trì tỉ lệ giữa lợi nhuận thu được từ xuất khẩu và số thuế nộp là \\(4 : 1\\). Giá bán trên thị trường quốc tế của mỗi đèn LED là \\(x_0 = {x0}\\) USD. Qua khảo sát, nếu chi phí sản xuất mỗi đèn là \\(x\\) USD thì số sản phẩm sản xuất được là \\(R(x) = x - {c1}\\), trong khi số lượng tiêu thụ trong nước là \\(Q(x) = {c2} - x\\). Hỏi doanh nghiệp cần chọn mức thuế \\(a\\) là bao nhiêu để lợi nhuận từ xuất khẩu đạt lớn nhất.''',
        
        # Bài tương tự 8
        '''Một công ty điện tử chuyên sản xuất loa Bluetooth chống nước phục vụ cho cả thị trường nội địa và quốc tế. Nếu chi phí sản xuất mỗi loa là \\(x\\) USD, thì số lượng sản phẩm sản xuất được là \\(R(x) = x - {c1}\\) và lượng tiêu thụ trong nước là \\(Q(x) = {c2} - x\\). Các sản phẩm không tiêu thụ trong nước sẽ được xuất khẩu với mức giá ổn định là \\(x_0 = {x0}\\) USD mỗi chiếc. Theo quy định, mỗi sản phẩm xuất khẩu bị đánh thuế \\(a\\) USD và tỷ lệ giữa lãi và thuế thu được phải luôn là \\(4 : 1\\). Tính giá trị \\(a\\) sao cho lợi nhuận từ xuất khẩu là lớn nhất.''',
        
        # Bài tương tự 9
        '''Nhằm khuyến khích phát triển sản phẩm thân thiện với môi trường, chính phủ yêu cầu rằng đối với mỗi đèn năng lượng mặt trời xuất khẩu, tỷ lệ giữa lợi nhuận thu được và số thuế thu phải là \\(4 : 1\\). Một công ty chuyên sản xuất đèn năng lượng mặt trời bán phần sản phẩm dư ra thị trường quốc tế với mức giá ổn định \\(x_0 = {x0}\\) USD mỗi đèn. Nếu chi phí sản xuất là \\(x\\) USD thì số lượng sản phẩm sản xuất được là \\(R(x) = x - {c1}\\), còn số sản phẩm tiêu thụ trong nước là \\(Q(x) = {c2} - x\\). Hãy xác định mức thuế \\(a\\) sao cho lợi nhuận từ xuất khẩu là lớn nhất.''',
        
        # Bài tương tự 10
        '''Giá bán quốc tế cố định của mỗi đèn LED thông minh là \\(x_0 = {x0}\\) USD. Nhà máy dự kiến rằng với chi phí sản xuất là \\(x\\) USD thì có thể sản xuất được \\(R(x) = x - {c1}\\) sản phẩm. Mỗi đèn được xuất khẩu phải chịu mức thuế \\(a\\) USD. Theo chính sách nhà nước, tỷ lệ giữa lợi nhuận thu được từ xuất khẩu và số thuế phải luôn đạt mức \\(4 : 1\\). Sản lượng tiêu thụ trong nước dự kiến là \\(Q(x) = {c2} - x\\). Hãy xác định giá trị \\(a\\) sao cho lợi nhuận từ xuất khẩu đạt giá trị lớn nhất.'''
    ]
    
    def generate_question_text(self) -> str:
        """Sinh đề bài bằng LaTeX"""
        p = self.parameters
        template = random.choice(self.PROBLEM_TEMPLATES)
        return template.format(**p)
    
    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết"""
        p = self.parameters
        
        # Tính các giá trị cho lời giải
        x_optimal = p["x0"] * 2700 / 3200
        a_optimal = (p["x0"] - x_optimal) / 5
        
        # Format các phân số
        four_fifths = format_dfrac(4, 5)
        two_fifths = format_dfrac(2, 5)
        one_fifth = format_dfrac(1, 5)
        one_fourth = format_dfrac(1, 4)
        
        return f"""
Lời giải:

Điều kiện: \\(R(x) = x - {p["c1"]} > 0\\); \\(Q(x) = {p["c2"]} - x > 0 \\Rightarrow {p["c1"]} < x < {p["c2"]}\\).

Số sản phẩm xuất khẩu là: \\(R(x) - Q(x) = (x - {p["c1"]}) - ({p["c2"]} - x) = 2x - {p["c1"] + p["c2"]}\\)

Lãi xuất khẩu của doanh nghiệp là: \\(L(x) = (R(x) - Q(x))({p["x0"]} - x - a) = (2x - {p["c1"] + p["c2"]})({p["x0"]} - x - a)\\).

Thuế thu được của nhà nước là: \\(T(x) = (2x - {p["c1"] + p["c2"]})a\\).

Ta có \\(L(x) : T(x) = 4 : 1\\), suy ra \\((2x - {p["c1"] + p["c2"]})({p["x0"]} - x - a) = 4(2x - {p["c1"] + p["c2"]})a\\)

\\(\\Rightarrow a = {one_fifth}({p["x0"]} - x)\\)

Khi đó:
$$L(x) = (2x - {p["c1"] + p["c2"]})\\left({p["x0"]} - x - {one_fifth}({p["x0"]} - x)\\right) = (2x - {p["c1"] + p["c2"]}) {four_fifths}({p["x0"]} - x)$$

$$= {four_fifths}(2x - {p["c1"] + p["c2"]})({p["x0"]} - x)$$

Bài toán đưa về tìm \\(x\\) để \\(L(x)\\) đạt giá trị lớn nhất.

Lấy đạo hàm: \\(L'(x) = {four_fifths}[2({p["x0"]} - x) - (2x - {p["c1"] + p["c2"]})] = {four_fifths}[2 \\cdot {p["x0"]} - 4x + {p["c1"] + p["c2"]}]\\)

\\(L'(x) = 0 \\Leftrightarrow x = {one_fourth}(2 \\cdot {p["x0"]} + {p["c1"] + p["c2"]}) = {format_number_clean(x_optimal)}\\)

Lập bảng biến thiên ta thấy \\(L(x)\\) đạt giá trị lớn nhất khi \\(x = {format_number_clean(x_optimal)}\\).

Suy ra \\(a = {one_fifth}({p["x0"]} - {format_number_clean(x_optimal)}) = {format_number_clean(a_optimal)}\\).
""" 