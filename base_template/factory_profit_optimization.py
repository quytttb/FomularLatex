"""
Dạng toán tối ưu hóa lợi nhuận nhà máy với thuế GTGT
Tương ứng câu 4 trong bai2.tex
"""
import random
from typing import Dict, Any, List
from base_optimization_question import BaseOptimizationQuestion
from latex_utils import format_number_clean, format_dfrac

class FactoryProfitOptimization(BaseOptimizationQuestion):
    """
    Dạng toán tối ưu hóa lợi nhuận nhà máy
    
    Bài toán cốt lõi:
    - Giá bán: p(x) = a - bx^2
    - Chi phí: C(x) = (c + dx)/2
    - Thuế GTGT 10% trên doanh thu
    - Tối ưu hóa lợi nhuận = Doanh thu - Chi phí - Thuế
    """
    
    PROBLEM_TEMPLATES = [
        # Đề bài gốc - Câu 4
        '''Nhà máy A chuyên sản suất một loại sản phẩm cho nhà máy B. Hai nhà máy thỏa thuận rằng, hàng tháng nhà máy A cung cấp cho nhà máy B số lượng sản phẩm theo đơn đặt hàng của nhà máy B (tối đa {max_production} tấn sản phẩm). Nếu số lượng đặt hàng là \(x\) tấn sản phẩm. Thì giá bán cho mỗi tấn sản phẩm là \(p(x)={price_a}-{price_b} x^2\) (đơn vị triệu đồng). Chi phí để nhà máy A sản suất \(x\) tấn sản phẩm trong một tháng là \(C(x)=\dfrac{{1}}{{2}}({cost_c}+{cost_d} x)\) (đơn vị: triệu đồng), thuế giá trị gia tăng mà nhà máy A phải đóng cho nhà nước là {vat_rate_percent}\% tổng doanh thu mỗi tháng. Hỏi nhà máy A bán cho nhà máy B bao nhiêu tấn sản phẩm mỗi tháng để thu được lợi nhuận (sau khi đã trừ thuế giá trị gia tăng) cao nhất?''',
        
        # Bài tương tự 1
        '''Trong bối cảnh thị trường xây dựng đang có xu hướng phục hồi sau khủng hoảng, nhiều doanh nghiệp sản xuất vật liệu xây dựng chuyên cung cấp gạch ốp lát cho các công trình dân dụng và đối tác lớn. Tuy nhiên, để đảm bảo chất lượng và tiến độ, công ty giới hạn lượng hàng cung cấp mỗi tháng không vượt quá {max_production} tấn. Doanh thu bán hàng chịu thuế GTGT {vat_rate_percent}\%. Chi phí sản xuất \(x\) tấn mỗi tháng là \(C(x) = \dfrac{{1}}{{2}}({cost_c} + {cost_d}x)\) (triệu đồng). Giá bán mỗi tấn sản phẩm được tính theo công thức \(p(x) = {price_a} - {price_b}x^2\) (triệu đồng). Hỏi doanh nghiệp nên bán bao nhiêu tấn mỗi tháng để thu được lợi nhuận sau thuế lớn nhất?''',
        
        # Bài tương tự 2
        '''Đáp ứng nhu cầu sử dụng thực phẩm sạch ngày càng cao tại các thành phố lớn, một nông trại rau hữu cơ tại vùng ven đô mở rộng sản lượng để cung cấp cho chuỗi siêu thị nội địa. Tuy nhiên, do giới hạn vận chuyển và bảo quản, nông trại chỉ có thể cung cấp tối đa {max_production} tấn rau mỗi tháng. Doanh thu từ việc bán rau bị đánh thuế GTGT {vat_rate_percent}\%. Chi phí sản xuất khi cung ứng \(x\) tấn là \(C(x) = \dfrac{{1}}{{2}}({cost_c} + {cost_d}x)\) (triệu đồng). Giá bán mỗi tấn rau được mô hình hóa theo hàm \(p(x) = {price_a} - {price_b}x^2\) (triệu đồng). Nên bán bao nhiêu tấn rau để tối ưu lợi nhuận sau thuế?''',
        
        # Bài tương tự 3
        '''Một công ty sản xuất nước giải khát tại miền Trung vừa ra mắt dòng sản phẩm nước hoa quả lên men không đường nhằm phục vụ nhóm khách hàng quan tâm đến sức khỏe. Sản phẩm được phân phối đến chuỗi siêu thị lớn tại các thành phố lớn như Hà Nội và Đà Nẵng. Do hạn chế về hệ thống kho lạnh và phương tiện vận chuyển chuyên dụng, mỗi tháng công ty chỉ có thể xuất không quá {max_production} tấn sản phẩm ra thị trường. Toàn bộ doanh thu từ việc phân phối sản phẩm sẽ chịu thuế GTGT {vat_rate_percent}\%. Chi phí sản xuất lượng hàng \(x\) tấn là \(C(x) = \dfrac{{1}}{{2}}({cost_c} + {cost_d}x)\) (triệu đồng), và giá bán mỗi tấn phụ thuộc vào sản lượng tiêu thụ: \(p(x) = {price_a} - {price_b}x^2\) (triệu đồng). Hỏi công ty nên bán bao nhiêu tấn mỗi tháng để lợi nhuận sau thuế đạt tối đa?''',
        
        # Bài tương tự 4
        '''Một cơ sở chế biến thủy sản tại Khánh Hòa chuyên sản xuất cá phi lê đông lạnh theo tiêu chuẩn HACCP để cung ứng cho chuỗi nhà hàng hải sản và khách sạn 4–5 sao tại TP. Hồ Chí Minh và Nha Trang. Do hệ thống kho đông và phương tiện bảo quản còn giới hạn, mỗi tháng cơ sở chỉ có thể vận chuyển tối đa {max_production} tấn cá thành phẩm ra thị trường. Doanh thu từ hoạt động kinh doanh phải chịu thuế GTGT {vat_rate_percent}\% theo quy định hiện hành. Chi phí chế biến cá \(x\) tấn được mô hình hóa theo hàm \(C(x) = \dfrac{{1}}{{2}}({cost_c} + {cost_d}x)\) (triệu đồng). Giá bán mỗi tấn sản phẩm phụ thuộc vào khối lượng tiêu thụ, được tính theo công thức: \(p(x) = {price_a} - {price_b}x^2\) (triệu đồng). Hỏi cơ sở nên bán bao nhiêu tấn cá mỗi tháng để lợi nhuận sau thuế là lớn nhất?''',
        
        # Bài tương tự 5
        '''Một xưởng gỗ tại Tây Nguyên hợp tác với một chuỗi công ty nội thất chuyên sản xuất bàn, tủ và giường cho thị trường nội địa và xuất khẩu. Trong bối cảnh giá nguyên vật liệu tăng và yêu cầu về chứng nhận nguồn gỗ hợp pháp ngày càng chặt chẽ, xưởng phải giới hạn sản lượng tối đa ở mức {max_production} tấn gỗ mỗi tháng để đảm bảo chất lượng và đáp ứng tiêu chuẩn bền vững. Mọi doanh thu từ việc bán gỗ đều phải nộp thuế GTGT {vat_rate_percent}\%. Chi phí sản xuất gỗ theo sản lượng \(x\) tấn là \(C(x) = \dfrac{{1}}{{2}}({cost_c} + {cost_d}x)\) (triệu đồng), trong khi giá bán mỗi tấn được điều chỉnh theo lượng cung ứng và được cho bởi \(p(x) = {price_a} - {price_b}x^2\) (triệu đồng). Công ty nên đặt hàng bao nhiêu tấn mỗi tháng để xưởng thu được lợi nhuận cao nhất sau thuế?''',
        
        # Bài tương tự 6
        '''Một trang trại bò sữa tại Đà Lạt có hệ thống chăn nuôi khép kín với sản lượng cung ứng ổn định quanh năm. Trang trại ký hợp đồng với một công ty chế biến sữa hộp để cung cấp sữa tươi nguyên liệu. Tuy nhiên, do giới hạn công suất xe lạnh và hệ thống bảo quản tại điểm tiếp nhận, lượng sữa được phép giao tối đa mỗi tháng là {max_production} tấn. Doanh thu từ việc bán sữa phải chịu thuế GTGT {vat_rate_percent}\%. Chi phí để sản xuất ra \(x\) tấn sữa là \(C(x) = \dfrac{{1}}{{2}}({cost_c} + {cost_d}x)\) (triệu đồng). Giá bán mỗi tấn sữa tươi phụ thuộc vào lượng cung cấp, được cho bởi \(p(x) = {price_a} - {price_b}x^2\) (triệu đồng). Trang trại nên cung cấp bao nhiêu tấn mỗi tháng để đạt được lợi nhuận sau thuế lớn nhất?''',
        
        # Bài tương tự 7
        '''Một công ty hóa chất công nghiệp có trụ sở tại khu công nghiệp Biên Hòa chuyên sản xuất chất phụ gia cho ngành dệt nhuộm và xử lý nước. Trước những quy định khắt khe về môi trường, công ty buộc phải giới hạn lượng nguyên liệu hóa chất bán ra ở mức không quá {max_production} tấn mỗi tháng để đảm bảo an toàn vận hành và quy trình xử lý chất thải. Doanh thu bán hàng mỗi tháng chịu thuế GTGT {vat_rate_percent}\%. Chi phí để sản xuất ra \(x\) tấn sản phẩm là \(C(x) = \dfrac{{1}}{{2}}({cost_c} + {cost_d}x)\) (triệu đồng). Giá bán mỗi tấn sản phẩm tùy theo quy mô đơn hàng và được xác định bởi hàm \(p(x) = {price_a} - {price_b}x^2\) (triệu đồng). Công ty nên cung cấp bao nhiêu tấn mỗi tháng để đạt lợi nhuận sau thuế cao nhất?''',
        
        # Bài tương tự 8
        '''Một hợp tác xã nông nghiệp tại Đồng bằng sông Cửu Long đầu tư dây chuyền sản xuất phân bón hữu cơ phục vụ các tỉnh lân cận và xuất khẩu tiểu ngạch sang Campuchia. Do đặc thù vận chuyển bằng ghe tàu, kho chứa hạn chế và điều kiện bảo quản phân hữu cơ, hợp tác xã chỉ có thể cung ứng tối đa {max_production} tấn phân bón mỗi tháng. Mọi doanh thu thu được đều phải chịu thuế giá trị gia tăng {vat_rate_percent}\%. Chi phí sản xuất \(x\) tấn phân là \(C(x) = \dfrac{{1}}{{2}}({cost_c} + {cost_d}x)\) (triệu đồng). Giá bán mỗi tấn phân bón được xác định theo công thức \(p(x) = {price_a} - {price_b}x^2\) (triệu đồng). Hợp tác xã nên cung cấp bao nhiêu tấn mỗi tháng để tối đa hóa lợi nhuận sau thuế?''',
    ]

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán tối ưu hóa lợi nhuận nhà máy"""
        
        # Tham số theo pattern từ bai2.tex
        # p(x) = a - b*x^2, thường a = 90, b = 0.01
        price_a = random.choice([90, 85, 95, 88, 92])
        price_b = random.choice([0.01, 0.008, 0.012, 0.009, 0.011])
        
        # C(x) = (c + d*x)/2, thường c = 200, d = 27
        cost_c = random.choice([200, 180, 220, 190, 210])
        cost_d = random.choice([27, 25, 30, 26, 28])
        
        # Giới hạn sản lượng
        max_production = 100  # tấn
        
        # Thuế GTGT
        vat_rate = 0.1  # 10%
        
        return {
            "price_a": price_a,
            "price_b": price_b,
            "cost_c": cost_c,
            "cost_d": cost_d,
            "max_production": max_production,
            "vat_rate": vat_rate,
            "vat_rate_percent": int(vat_rate * 100)
        }
    
    def calculate_answer(self) -> str:
        """Tính đáp án đúng"""
        p = self.parameters
        
        # Tính toán chính xác theo công thức
        coef_x = p["price_a"] * (1 - p["vat_rate"]) - p["cost_d"] / 2
        coef_x3 = -p["price_b"] * (1 - p["vat_rate"])
        
        # Giải phương trình L'(x) = 0: 3*coef_x3*x² + coef_x = 0
        # x² = -coef_x / (3*coef_x3)
        optimal_production = int((coef_x / (3 * abs(coef_x3)))**0.5)
        
        return f"${optimal_production}$ tấn"
    
    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý"""
        p = self.parameters
        
        # Tính đáp án đúng để tạo đáp án sai
        coef_x = p["price_a"] * (1 - p["vat_rate"]) - p["cost_d"] / 2
        coef_x3 = -p["price_b"] * (1 - p["vat_rate"])
        correct_answer = int((coef_x / (3 * abs(coef_x3)))**0.5)
        
        # Các sai lầm thường gặp
        wrong_answers = [
            f"${correct_answer + 10}$ tấn",   # Cao hơn
            f"${max(0, correct_answer - 10)}$ tấn",   # Thấp hơn
            f"${p['max_production']}$ tấn"   # Tối đa
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
        
        # Tính toán các hệ số theo pattern chuẩn
        # L(x) = B(x) - C(x) - T(x)
        # = x(p_a - p_b*x²) - 1/2(c + d*x) - 0.1*x(p_a - p_b*x²)
        # = x*p_a - p_b*x³ - c/2 - d*x/2 - 0.1*p_a*x + 0.1*p_b*x³
        # = (p_a - 0.1*p_a - d/2)*x + (-p_b + 0.1*p_b)*x³ - c/2
        # = (0.9*p_a - d/2)*x + (-0.9*p_b)*x³ - c/2
        
        coef_x = p["price_a"] * (1 - p["vat_rate"]) - p["cost_d"] / 2
        coef_x3 = -p["price_b"] * (1 - p["vat_rate"])
        const_term = -p["cost_c"] / 2
        
        # Đạo hàm: L'(x) = coef_x - 3*coef_x3*x²
        # Giải L'(x) = 0: coef_x - 3*coef_x3*x² = 0
        # x² = coef_x / (3*coef_x3)
        # x = sqrt(coef_x / (3*coef_x3))
        
        optimal_x = int((coef_x / (3 * abs(coef_x3)))**0.5)
        
        # Format các phân số
        one_half = format_dfrac(1, 2)
        one_tenth = format_dfrac(1, 10)
        vat_rate_frac = format_dfrac(int(p["vat_rate"] * 100), 100)
        
        return f"""
Lời giải:

Giả sử số lượng sản phẩm bán ra là \\(x\\) tấn, \\(0 \\leq x \\leq {p["max_production"]}\\).

Doanh thu \\(B(x) = x \\cdot p(x) = x({p["price_a"]} - {p["price_b"]}x^2)\\).

Thuế giá trị gia tăng \\(T(x) = {format_number_clean(p["vat_rate"] * 100)}\\% B(x) = {one_tenth} x({p["price_a"]} - {p["price_b"]}x^2)\\).

Lợi nhuận = Doanh thu - Chi phí - Thuế:

\\(L(x) = B(x) - C(x) - T(x) = x({p["price_a"]} - {p["price_b"]}x^2) - {one_half}({p["cost_c"]} + {p["cost_d"]}x) - {one_tenth} x({p["price_a"]} - {p["price_b"]}x^2) = {format_number_clean(coef_x3)}x^3 + {format_number_clean(coef_x)}x {format_number_clean(const_term)}\\).

\\(L'(x) = {format_number_clean(3 * coef_x3)}x^2 + {format_number_clean(coef_x)} = 0 \\Leftrightarrow x = {optimal_x}\\).

Lập bảng biến thiên ta được lợi nhuận cao nhất khi \\(x = {optimal_x}\\).
"""