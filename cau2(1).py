"""
Dạng toán tối ưu hóa sản xuất và xuất khẩu
"""

import logging
import random
import sys
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import math
from fractions import Fraction
from typing import Union
from math import gcd


"""
Các hàm tiện ích LaTeX cho hệ thống sinh câu hỏi toán tối ưu hóa
"""


def format_fraction_latex(num, denom):
    if denom == 0:
        return "undefined"
    frac = Fraction(num, denom)
    if frac.denominator == 1:
        return str(frac.numerator)
    elif frac.numerator == 0:
        return "0"
    else:
        return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"


def format_coefficient(coeff, is_first=False, var='x', power=1):
    if coeff == 0:
        return ""
    if isinstance(coeff, Fraction):
        num, denom = coeff.numerator, coeff.denominator
    else:
        num, denom = int(coeff), 1
    if denom == 1:
        coeff_str = str(abs(num)) if abs(num) != 1 or power == 0 else ""
    else:
        coeff_str = f"\\frac{{{abs(num)}}}{{{denom}}}"
    if power == 0:
        var_str = coeff_str if coeff_str else "1"
    elif power == 1:
        var_str = f"{coeff_str}{var}" if coeff_str else var
    else:
        var_str = f"{coeff_str}{var}^{{{power}}}" if coeff_str else f"{var}^{{{power}}}"
    if is_first:
        if num < 0:
            return f"-{var_str}"
        else:
            return var_str
    else:
        if num < 0:
            return f" - {var_str}"
        else:
            return f" + {var_str}"


def format_polynomial(coeffs, var='x'):
    if not coeffs or all(c == 0 for c in coeffs):
        return "0"
    terms = []
    degree = len(coeffs) - 1
    for i, coeff in enumerate(coeffs):
        if coeff == 0:
            continue
        power = degree - i
        term = format_coefficient(coeff, len(terms) == 0, var, power)
        if term:
            terms.append(term)
    if not terms:
        return "0"
    return "".join(terms)


def format_number_clean(value, precision=2):
    """Định dạng số theo chuẩn LaTeX, loại bỏ số thập phân nếu là số nguyên"""
    try:
        fval = float(value)
        if abs(fval - round(fval)) < 1e-10:
            return str(int(round(fval)))
        else:
            formatted = f"{fval:.{precision}f}"
            # Bỏ số 0 thừa ở cuối
            while formatted.endswith('0') and '.' in formatted:
                formatted = formatted[:-1]
            if formatted.endswith('.'):
                formatted = formatted[:-1]
            if '.' in formatted:
                formatted = formatted.replace('.', ',')
            return formatted
    except (ValueError, TypeError):
        return str(value)


def format_coord_solution(coord):
    if isinstance(coord, Fraction):
        if coord.denominator == 1:
            return str(coord.numerator)
        else:
            return f"\\dfrac{{{coord.numerator}}}{{{coord.denominator}}}"
    return format_number_clean(coord, precision=10).replace('\\frac', '\\dfrac')


def format_scientific(num: float, precision: int = 3) -> str:
    if abs(num) < 1e-10:
        return "0"
    exponent = int(math.floor(math.log10(abs(num))))
    mantissa = num / (10 ** exponent)
    if exponent == 0:
        return f"{mantissa:.{precision}f}".rstrip('0').rstrip('.')
    else:
        return f"{mantissa:.{precision}f} \\times 10^{{{exponent}}}"


def format_sqrt(number: Union[int, float]) -> str:
    """Format căn bậc hai thành LaTeX - cải thiện để hiển thị đẹp hơn"""
    if number == int(number) and int(number) >= 0:
        sqrt_val = math.sqrt(number)
        if sqrt_val == int(sqrt_val):
            return f"{int(sqrt_val)}"
        else:
            # Kiểm tra xem có thể viết dưới dạng a*sqrt(b) không
            for a in range(1, int(sqrt_val) + 1):
                b = number / (a * a)
                if abs(b - round(b)) < 1e-10 and b > 0:
                    b_int = int(round(b))
                    if b_int == 1:
                        return f"{a}"
                    else:
                        return f"{a}\\sqrt{{{b_int}}}"
            # Nếu không thể viết dưới dạng a*sqrt(b), trả về sqrt(number)
            return f"\\sqrt{{{int(number)}}}"
    else:
        # Với số thực, thử tìm dạng a*sqrt(b)
        sqrt_val = math.sqrt(number)
        for a in range(1, int(sqrt_val) + 1):
            b = number / (a * a)
            if abs(b - round(b)) < 1e-10 and b > 0:
                b_int = int(round(b))
                if b_int == 1:
                    return f"{a}"
                else:
                    return f"{a}\\sqrt{{{b_int}}}"
        # Nếu không thể, trả về sqrt(number) với số làm tròn
        return f"\\sqrt{{{format_number_clean(number)}}}"


def format_sqrt_improved(number: Union[int, float]) -> str:
    """Format căn bậc hai thành LaTeX - phiên bản cải tiến cho các trường hợp đặc biệt"""
    if number == int(number) and int(number) >= 0:
        sqrt_val = math.sqrt(number)
        if sqrt_val == int(sqrt_val):
            return f"{int(sqrt_val)}"
        else:
            # Kiểm tra xem có thể viết dưới dạng a*sqrt(b) không
            for a in range(1, int(sqrt_val) + 1):
                b = number / (a * a)
                if abs(b - round(b)) < 1e-10 and b > 0:
                    b_int = int(round(b))
                    if b_int == 1:
                        return f"{a}"
                    else:
                        return f"{a}\\sqrt{{{b_int}}}"
            # Nếu không thể viết dưới dạng a*sqrt(b), trả về sqrt(number)
            return f"\\sqrt{{{int(number)}}}"
    else:
        # Với số thực, thử tìm dạng a*sqrt(b)
        sqrt_val = math.sqrt(number)
        for a in range(1, int(sqrt_val) + 1):
            b = number / (a * a)
            if abs(b - round(b)) < 1e-10 and b > 0:
                b_int = int(round(b))
                if b_int == 1:
                    return f"{a}"
                else:
                    return f"{a}\\sqrt{{{b_int}}}"
        # Nếu không thể, trả về sqrt(number) với số làm tròn
        return f"\\sqrt{{{format_number_clean(number)}}}"


def format_dimension(value: float, unit: str = "mét") -> str:
    if abs(value - round(value)) < 1e-10:
        return f"{int(round(value))} {unit}"
    else:
        formatted = f"{value:.1f}"
        if formatted.endswith('.0'):
            formatted = formatted[:-2]
        return f"{formatted} {unit}"


def strip_latex_inline_math(ans: str) -> str:
    if ans.startswith("\\(") and ans.endswith("\\)"):
        return ans[2:-2].strip()
    if ans.startswith("$") and ans.endswith("$"):
        return ans[1:-1].strip()
    return ans


def format_dfrac(num, denom):
    """Format fraction using dfrac for better display"""
    if denom == 0:
        return "undefined"
    frac = Fraction(num, denom)
    if frac.denominator == 1:
        return str(frac.numerator)
    elif frac.numerator == 0:
        return "0"
    else:
        return f"\\dfrac{{{frac.numerator}}}{{{frac.denominator}}}"


def format_money(value, unit="triệu đồng"):
    """Format money values cleanly"""
    return f"{format_number_clean(value)} {unit}"


def format_percentage(value):
    """Format percentage values"""
    return f"{format_number_clean(value * 100)}\\%"


def format_function_notation(func_name, var, expression):
    """Format function notation like f(x) = expression"""
    return f"{func_name}({var}) = {expression}"


"""
Lớp cơ sở cho các dạng bài toán tối ưu hóa
"""


class BaseOptimizationQuestion(ABC):
    """
    Lớp cơ sở cho tất cả các dạng bài toán tối ưu hóa
    """

    def __init__(self):
        self.parameters = {}
        self.correct_answer = None
        self.wrong_answers = []
        self.solution_steps = []

    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên cho bài toán"""
        pass

    @abstractmethod
    def calculate_answer(self) -> str:
        """Tính đáp án đúng dựa trên parameters"""
        pass

    @abstractmethod
    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý"""
        pass

    @abstractmethod
    def generate_question_text(self) -> str:
        """Sinh đề bài bằng LaTeX"""
        pass

    @abstractmethod
    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết bằng LaTeX"""
        pass

    def generate_full_question(self, question_number: int = 1) -> str:
        """Tạo câu hỏi hoàn chỉnh với 4 đáp án A/B/C/D"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        self.wrong_answers = self.generate_wrong_answers()
        question_text = self.generate_question_text()
        solution = self.generate_solution()
        all_answers = [self.correct_answer] + self.wrong_answers
        random.shuffle(all_answers)
        correct_index = all_answers.index(self.correct_answer)
        question_content = f"Câu {question_number}: {question_text}\n\n"
        for j, ans in enumerate(all_answers):
            letter = chr(65 + j)
            marker = "*" if j == correct_index else ""
            question_content += f"{marker}{letter}. {ans}\n\n"
        question_content += f"Lời giải:\n\n{solution}\n\n"
        return question_content

    def generate_question_only(self, question_number: int = 1) -> tuple:
        """Tạo câu hỏi chỉ có đề bài và lời giải"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        question_text = self.generate_question_text()
        solution = self.generate_solution()
        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += f"Lời giải:\n\n{solution}\n\n"
        return question_content, self.correct_answer

    @staticmethod
    def create_latex_document(questions: List[str], title: str = "Câu hỏi Tối ưu hóa") -> str:
        """Tạo document LaTeX hoàn chỉnh"""
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{polyglossia}}
\\setmainlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage{{tikz}}
\\usepackage{{tkz-tab}}
\\usepackage{{tkz-euclide}}
\\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\\begin{{document}}
\\title{{{title}}}
\\maketitle

"""
        latex_content += "\n\n".join(questions)
        latex_content += "\n\\end{document}"
        return latex_content

    @staticmethod
    def create_latex_document_with_format(questions_data: List, title: str = "Câu hỏi Tối ưu hóa", fmt: int = 1) -> str:
        """Tạo document LaTeX với 2 format khác nhau"""
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{polyglossia}}
\\setmainlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage{{tikz}}
\\usepackage{{tkz-tab}}
\\usepackage{{tkz-euclide}}
\\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\\begin{{document}}
\\title{{{title}}}
\\maketitle

"""

        if fmt == 1:
            # Format 1: đáp án ngay sau câu hỏi
            for question_data in questions_data:
                if isinstance(question_data, tuple):
                    latex_content += f"{question_data[0]}\n\n"
                else:
                    latex_content += f"{question_data}\n\n"
        else:
            # Format 2: câu hỏi + lời giải, đáp án ở cuối
            correct_answers = []
            for question_data in questions_data:
                if isinstance(question_data, tuple):
                    question_content, correct_answer = question_data
                    latex_content += question_content + "\n\n"
                    correct_answers.append(correct_answer)
                else:
                    # Fallback cho format cũ
                    latex_content += f"{question_data}\n\n"

            # Thêm phần đáp án ở cuối
            if correct_answers:
                latex_content += "Đáp án\n\n"
                for idx, answer in enumerate(correct_answers, 1):
                    # Loại bỏ ký hiệu LaTeX để hiển thị đáp án sạch
                    ans = answer
                    if ans.startswith("\\(") and ans.endswith("\\)"):
                        ans = ans[2:-2].strip()
                    if ans.startswith("$") and ans.endswith("$"):
                        ans = ans[1:-1].strip()

                    # Nếu là số thập phân (có dấu phẩy), in thêm dạng dấu chấm
                    if ',' in ans:
                        ans_dot = ans.replace(',', '.')
                        latex_content += f"Câu {idx}: {ans}|{ans_dot}\n\n"
                    else:
                        latex_content += f"Câu {idx}: {ans}\n\n"

        latex_content += "\\end{document}"
        return latex_content


"""
Dạng toán tối ưu hóa sản xuất với ràng buộc số tổ công nhân và năng suất
Tương ứng câu 1 trong bai2.tex
"""


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
        team_decrease = random.choice([1, 2])  # Giảm 1-2 tổ
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
        params = self.parameters

        # ==============================================================================
        # BƯỚC 1: Thiết lập biến và tham số
        # ==============================================================================
        # Đặt t = số giờ tăng thêm so với base_hours
        # Tổng thời gian làm việc: x = base_hours + t

        h0 = params["base_hours"]           # Giờ làm việc ban đầu
        n0 = params["base_teams"]           # Số tổ ban đầu
        p0 = params["base_productivity"]    # Năng suất ban đầu (sản phẩm/giờ/tổ)
        h_inc = params["hour_increment"]    # Cứ tăng h_inc giờ
        n_dec = params["team_decrease"]     # thì giảm n_dec tổ
        p_dec = params["productivity_decrease"]  # và giảm p_dec sản phẩm/giờ/tổ
        a = params["waste_a"]               # Hệ số trong công thức phế phẩm
        b = params["waste_b"]
        c = params["waste_c"]

        # ==============================================================================
        # BƯỚC 2: Thiết lập hàm mục tiêu f(t) = S(t) - P(t)
        # ==============================================================================
        # S(t): Tổng sản phẩm sản xuất được
        # P(t): Tổng phế phẩm tạo ra

        # Số tổ còn làm việc: n0 - (t/h_inc) * n_dec
        # Năng suất còn lại: p0 - (t/h_inc) * p_dec
        # Thời gian làm việc: h0 + t
        # => S(t) = [n0 - n_dec*t/h_inc] * [p0 - p_dec*t/h_inc] * [h0 + t]

        # Phế phẩm: P(t) = [a*(h0+t)² + b*(h0+t)] / c

        # ==============================================================================
        # BƯỚC 3: Khai triển S(t) thành đa thức bậc 3
        # ==============================================================================
        # S(t) = (n0 - n_dec*t/h_inc)(p0 - p_dec*t/h_inc)(h0 + t)

        # Bước 3a: Khai triển tích 2 nhân tử đầu
        # (n0 - n_dec*t/h_inc)(p0 - p_dec*t/h_inc) =
        # = n0*p0 - (n0*p_dec + n_dec*p0)*t/h_inc + n_dec*p_dec*t²/(h_inc²)

        # Bước 3b: Nhân với nhân tử thứ 3 (h0 + t)
        # S(t) = [n0*p0 - (n0*p_dec + n_dec*p0)*t/h_inc + n_dec*p_dec*t²/(h_inc²)] * (h0 + t)
        # Khai triển ra ta được S(t) có dạng: at³ + bt² + ct + d

        # ==============================================================================
        # BƯỚC 4: Khai triển P(t) thành đa thức bậc 2
        # ==============================================================================
        # P(t) = [a*(h0+t)² + b*(h0+t)] / c
        # = [a*(h0² + 2*h0*t + t²) + b*h0 + b*t] / c
        # = (a*h0² + b*h0)/c + (2*a*h0 + b)*t/c + a*t²/c

        # ==============================================================================
        # BƯỚC 5: Tính f'(t) = S'(t) - P'(t) = At² + Bt + C
        # ==============================================================================
        # Từ khai triển trên, f'(t) là đa thức bậc 2 với các hệ số:

        A = 3 * n_dec * p_dec / (h_inc * h_inc)  # Hệ số t²

        B = 2 * (-(n0 * p_dec + n_dec * p0) / h_inc + n_dec * p_dec * h0 / (h_inc * h_inc)) - 2 * a / c  # Hệ số t

        C = n0 * p0 - (n0 * p_dec + n_dec * p0) * h0 / h_inc - (2 * a * h0 + b) / c  # Hằng số

        # ==============================================================================
        # BƯỚC 6: Giải phương trình f'(t) = 0 để tìm cực trị
        # ==============================================================================
        import math

        if abs(A) < 1e-10:
            # Trường hợp đặc biệt: A ≈ 0, phương trình bậc 1: Bt + C = 0
            if abs(B) > 1e-10:
                optimal_t = -C / B
            else:
                optimal_t = 0  # Fallback khi cả A và B đều ≈ 0
        else:
            # Trường hợp thông thường: phương trình bậc 2: At² + Bt + C = 0
            delta = B * B - 4 * A * C

            if delta >= 0:
                t1 = (-B + math.sqrt(delta)) / (2 * A)
                t2 = (-B - math.sqrt(delta)) / (2 * A)

                # Logic chọn nghiệm: ưu tiên nghiệm âm (giảm giờ làm)
                # vì thường bài toán có nghiệm tối ưu là giảm thời gian
                if t1 <= 0 and t2 <= 0:
                    optimal_t = max(t1, t2)  # Chọn nghiệm âm gần 0 nhất
                elif t1 <= 0:
                    optimal_t = t1
                elif t2 <= 0:
                    optimal_t = t2
                else:
                    optimal_t = min(t1, t2)  # Nếu cả 2 nghiệm đều dương, chọn nhỏ hơn
            else:
                optimal_t = -4  # Fallback khi delta < 0 (không có nghiệm thực)

        # ==============================================================================
        # BƯỚC 7: Kiểm tra và điều chỉnh theo các ràng buộc thực tế
        # ==============================================================================
        optimal_t = max(optimal_t, -h0)  # Đảm bảo tổng thời gian > 0: h0 + t > 0
        optimal_t = min(optimal_t, n0 * h_inc / n_dec)  # Đảm bảo số tổ > 0
        optimal_t = min(optimal_t, p0 * h_inc / p_dec)  # Đảm bảo năng suất > 0

        # ==============================================================================
        # BƯỚC 8: Tính kết quả cuối cùng
        # ==============================================================================
        optimal_hours = int(round(params["base_hours"] + optimal_t))

        return f"\\({optimal_hours}\\)"

    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý"""
        p = self.parameters
        base_hours = p["base_hours"]

        # Các sai lầm thường gặp
        wrong_answers = [
            f"\\({base_hours + 2}\\)",  # Tăng 2 giờ
            f"\\({base_hours - 2}\\)",  # Giảm 2 giờ
            f"\\({base_hours}\\)"  # Giữ nguyên
        ]

        return wrong_answers

    PROBLEM_TEMPLATES = [
        # Đề bài gốc - Câu 1
        '''Theo thống kê tại một nhà máy Z, nếu áp dụng tuần làm việc {base_hours} giờ thì mỗi tuần có {base_teams} tổ công nhân đi làm và mỗi tổ công nhân làm được {base_productivity} sản phẩm trong một giờ. Nếu tăng thời gian làm việc thêm {hour_increment} giờ mỗi tuần thì sẽ có {team_decrease} tổ công nhân nghỉ việc và năng suất lao động giảm {productivity_decrease} sản phẩm/1 tổ/1 giờ. Ngoài ra, số phế phẩm mỗi tuần ước tính là \\(P(x)={waste_formula}\\), với \\(x\\) là thời gian làm việc trong một tuần. Nhà máy cần áp dụng thời gian làm việc mỗi tuần mấy giờ để số lượng sản phẩm thu được mỗi tuần (sau khi trừ phế phẩm) là lớn nhất? (Đơn vị: giờ)''',

        # Bài tương tự 1
        '''Để cải thiện hiệu quả sản xuất, ban lãnh đạo nhà máy chế biến thực phẩm Z đang nghiên cứu phương án điều chỉnh thời gian làm việc trong tuần. Theo thực tế, nếu mỗi tuần công nhân làm việc \\(x\\) giờ thì số phế phẩm tạo ra ước tính theo công thức: \\( P(x) = {waste_formula} \\). Trong điều kiện hiện tại, nhà máy duy trì tuần làm việc {base_hours} giờ, với {base_teams} tổ công nhân hoạt động đều đặn và mỗi tổ sản xuất được {base_productivity} sản phẩm mỗi giờ. Tuy nhiên, khi tăng thêm mỗi {hour_increment} giờ làm việc mỗi tuần, sẽ có {team_decrease} tổ công nhân nghỉ việc và đồng thời năng suất giảm {productivity_decrease} sản phẩm/giờ cho mỗi tổ. Trong bối cảnh đó, nhà máy cần xác định số giờ làm việc \\(x\\) mỗi tuần sao cho tổng số sản phẩm đạt được sau khi trừ phế phẩm là lớn nhất. (Đơn vị: giờ)''',

        # Bài tương tự 2
        '''Trong giai đoạn mở rộng sản xuất để đáp ứng đơn hàng cuối năm, nhà máy cơ khí Z cần điều chỉnh thời lượng làm việc của công nhân. Nếu duy trì thời gian làm việc là \\(x\\) giờ mỗi tuần thì số lượng phế phẩm trong tuần được mô hình hóa bởi hàm số: \\( P(x) = {waste_formula} \\). Hiện tại, nhà máy hoạt động {base_hours} giờ/tuần, có {base_teams} tổ công nhân và mỗi tổ làm ra {base_productivity} sản phẩm mỗi giờ. Tuy nhiên, để tránh quá tải, mỗi khi tăng thêm {hour_increment} giờ làm việc mỗi tuần thì một tổ nghỉ việc và năng suất của các tổ còn lại giảm {productivity_decrease} sản phẩm/giờ. Ban điều hành cần xác định số giờ làm việc tối ưu trong tuần để đảm bảo số sản phẩm hữu ích (sau khi loại trừ phế phẩm) là lớn nhất. (Đơn vị: giờ)''',

        # Bài tương tự 3
        '''Xưởng lắp ráp thiết bị điện gia dụng đang vận hành với tuần làm việc {base_hours} giờ, {base_teams} tổ công nhân và mỗi tổ sản xuất {base_productivity} thiết bị/giờ. Tuy nhiên, trong kế hoạch tăng năng suất cuối quý, xưởng cân nhắc tăng số giờ làm việc \\(x\\) mỗi tuần. Điều này kéo theo một số thay đổi:\n\n- Cứ mỗi {hour_increment} giờ tăng thêm, một tổ công nhân nghỉ việc.\n\n- Mỗi tổ còn lại giảm năng suất {productivity_decrease} thiết bị mỗi giờ.\n\n- Lượng phế phẩm tạo ra trong tuần được ước tính bởi hàm: \\( P(x) = {waste_formula} \\).\\\\Xưởng cần xác định \\(x\\) bao nhiêu để tối đa hóa số lượng thiết bị đạt chuẩn sau khi loại trừ phế phẩm. Đây là quyết định quan trọng giúp đảm bảo mục tiêu sản xuất mà không gia tăng lãng phí. (Đơn vị: giờ)''',

        # Bài tương tự 4
        '''Trước tình hình đơn hàng xuất khẩu tăng đột biến, xí nghiệp dệt may Z cân nhắc phương án tăng giờ làm trong tuần. Tuy nhiên, mỗi thay đổi kéo theo hệ lụy:\n\n- Cứ tăng {hour_increment} giờ làm/tuần thì có một tổ xin nghỉ do quá tải.\n\n- Năng suất mỗi tổ giảm {productivity_decrease} áo/giờ.\n\n- Tổng phế phẩm hàng tuần ước tính bởi: \\( P(x) = {waste_formula} \\).\\\\Ban đầu, xí nghiệp có {base_teams} tổ, làm {base_hours} giờ/tuần, mỗi tổ sản xuất {base_productivity} áo/giờ. Hãy xác định số giờ làm việc \\(x\\) mỗi tuần để số lượng sản phẩm thu được (sau khi trừ phế phẩm) đạt giá trị lớn nhất, từ đó đảm bảo hiệu suất tối ưu. (Đơn vị: giờ)''',

        # Bài tương tự 5
        '''Một cơ sở sản xuất nhựa dân dụng tại miền Trung đang cần xác định thời lượng làm việc tối ưu trong tuần nhằm đảm bảo sản lượng thực tế cao nhất. Cơ sở hiện duy trì {base_teams} tổ lao động, mỗi tổ làm việc {base_hours} giờ/tuần và sản xuất {base_productivity} đơn vị sản phẩm mỗi giờ. Khi mở rộng ca làm, xảy ra các biến đổi sau:\n\n- Cứ mỗi {hour_increment} giờ tăng thêm, giảm 1 tổ làm việc.\n\n- Năng suất mỗi tổ giảm {productivity_decrease} đơn vị mỗi giờ.\n\n- Số lượng sản phẩm hư hỏng phát sinh trong tuần theo công thức: \\( P(x) = {waste_formula} \\).\\\\Bài toán yêu cầu tìm số giờ làm việc \\(x\\) sao cho số sản phẩm thực tế (tổng sản phẩm sản xuất trừ đi phế phẩm) đạt giá trị lớn nhất. (Đơn vị: giờ)'''
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
        params = self.parameters

        # Sử dụng kết quả từ calculate_answer() thay vì tính toán lại
        answer_latex = self.calculate_answer()
        # Extract số từ LaTeX format \\(số\\) và xử lý dấu phẩy thập phân
        optimal_hours = int(float(answer_latex.replace("\\(", "").replace("\\)", "").replace(",", ".")))

        # Tính nghiệm thực sự của phương trình đạo hàm cho hiển thị trong lời giải
        h0 = params["base_hours"]
        n0 = params["base_teams"]
        p0 = params["base_productivity"]
        h_inc = params["hour_increment"]
        n_dec = params["team_decrease"]
        p_dec = params["productivity_decrease"]
        a = params["waste_a"]
        b = params["waste_b"]
        c = params["waste_c"]

        # Tính hệ số của đạo hàm f'(t) = At^2 + Bt + C như trong calculate_answer
        A = 3 * n_dec * p_dec / (h_inc * h_inc)
        B = 2 * (-(n0 * p_dec + n_dec * p0) / h_inc + n_dec * p_dec * h0 / (h_inc * h_inc)) - 2 * a / c
        C = n0 * p0 - (n0 * p_dec + n_dec * p0) * h0 / h_inc - (2 * a * h0 + b) / c

        # Tính nghiệm cho hiển thị trong lời giải
        import math
        if abs(A) < 1e-10:  # Phương trình bậc 1
            if abs(B) > 1e-10:
                optimal_t = -C / B
            else:
                optimal_t = 0
        else:  # Phương trình bậc 2
            delta = B * B - 4 * A * C
            if delta >= 0:
                t1 = (-B + math.sqrt(delta)) / (2 * A)
                t2 = (-B - math.sqrt(delta)) / (2 * A)
                if t1 <= 0 and t2 <= 0:
                    optimal_t = max(t1, t2)
                elif t1 <= 0:
                    optimal_t = t1
                elif t2 <= 0:
                    optimal_t = t2
                else:
                    optimal_t = min(t1, t2)
            else:
                optimal_t = -4  # Fallback

        optimal_t = max(optimal_t, -h0)
        optimal_t = min(optimal_t, n0 * h_inc / n_dec)
        optimal_t = min(optimal_t, p0 * h_inc / p_dec)

        # Các phân số cho hiển thị
        neg_one = format_dfrac(-n_dec, h_inc)
        productivity_decrease_frac = format_dfrac(p_dec, h_inc)
        teams_frac = format_dfrac(n_dec, h_inc)
        waste_derivative_coeff = format_dfrac(2 * a, c)
        waste_derivative_const = format_dfrac(b, c)

        # Format hệ số đạo hàm thực tế
        coeff_t2 = format_number_clean(A, precision=4)
        coeff_t = format_number_clean(-B, precision=2)  # Đổi dấu để hiển thị dạng - coeff_t*t
        constant = format_number_clean(-C, precision=2)  # Đổi dấu để hiển thị dạng - constant

        # Tính và format nghiệm
        solution_t1 = format_number_clean(optimal_t, precision=2)

        # Tính nghiệm còn lại (không sử dụng)
        if abs(A) > 1e-10:
            delta = B * B - 4 * A * C
            if delta >= 0:
                t1 = (-B + math.sqrt(delta)) / (2 * A)
                t2 = (-B - math.sqrt(delta)) / (2 * A)
                # Chọn nghiệm không được sử dụng làm nghiệm loại
                if abs(t1 - optimal_t) < 1e-6:
                    solution_t2 = format_number_clean(t2, precision=2)
                else:
                    solution_t2 = format_number_clean(t1, precision=2)
            else:
                solution_t2 = "\\text{không có nghiệm thực}"
        else:
            solution_t2 = "\\text{phương trình bậc 1}"

        # Sử dụng params thay vì các biến riêng lẻ
        p = params

        return f"""
Gọi số giờ làm tăng thêm mỗi tuần là \\(t\\), \\(t \\in \\mathbb{{R}}\\).

Số tổ công nhân bỏ việc là \\(\\dfrac{{{p["team_decrease"]}t}}{{{p["hour_increment"]}}}\\) nên số tổ công nhân làm việc là \\({p["base_teams"]} - \\dfrac{{{p["team_decrease"]}t}}{{{p["hour_increment"]}}}\\) (tổ).

Năng suất của tổ công nhân còn \\({p["base_productivity"]} - \\dfrac{{{p["productivity_decrease"]}t}}{{{p["hour_increment"]}}}\\) sản phẩm một giờ.

Số thời gian làm việc một tuần là \\({p["base_hours"]} + t = x\\) (giờ).

\\(\\Rightarrow\\) Số phế phẩm thu được là \\(P({p["base_hours"]} + t) = \\dfrac{{{p["waste_a"]}({p["base_hours"]} + t)^2 + {p["waste_b"]}({p["base_hours"]} + t)}}{{{p["waste_c"]}}}\\)

Để nhà máy hoạt động được thì \\(\\left\\{{\\begin{{array}}{{l}}{p["base_hours"]} + t > 0 \\\\ {p["base_productivity"]} - \\dfrac{{{p["productivity_decrease"]}t}}{{{p["hour_increment"]}}} > 0\\end{{array}}\\right. \\Rightarrow t \\in(-{p["base_hours"]} ; {p["base_teams"] * p["hour_increment"]}) \\\\ {p["base_teams"]} - \\dfrac{{{p["team_decrease"]}t}}{{{p["hour_increment"]}}} > 0\\)

Số sản phẩm trong một tuần làm được:

\\(S = \\text{{Số tổ x Năng suất x Thời gian}} = \\left({p["base_teams"]} - \\dfrac{{{p["team_decrease"]}t}}{{{p["hour_increment"]}}}\\right)\\left({p["base_productivity"]} - \\dfrac{{{p["productivity_decrease"]}t}}{{{p["hour_increment"]}}}\\right)({p["base_hours"]} + t)\\).

Số sản phẩm thu được là:

\\(f(t) = \\left({p["base_teams"]} - \\dfrac{{{p["team_decrease"]}t}}{{{p["hour_increment"]}}}\\right)\\left({p["base_productivity"]} - \\dfrac{{{p["productivity_decrease"]}t}}{{{p["hour_increment"]}}}\\right)({p["base_hours"]} + t) - \\dfrac{{{p["waste_a"]}({p["base_hours"]} + t)^2 + {p["waste_b"]}({p["base_hours"]} + t)}}{{{p["waste_c"]}}}\\)

\\(f'(t) = {neg_one}\\left({p["base_productivity"]} - {productivity_decrease_frac}t\\right)({p["base_hours"]} + t) - {productivity_decrease_frac}\\left({p["base_teams"]} - {teams_frac}t\\right)({p["base_hours"]} + t) + \\left({p["base_teams"]} - {teams_frac}t\\right)\\left({p["base_productivity"]} - {productivity_decrease_frac}t\\right) - {waste_derivative_coeff}({p["base_hours"]} + t) - {waste_derivative_const} \\\\ = {coeff_t2} t^2 - {coeff_t} t - {constant}\\)

Ta có \\(f'(t) = 0 \\Leftrightarrow \\left[\\begin{{array}}{{l}}t \\approx {solution_t1} \\\\ t = {solution_t2}(L)\\end{{array}}\\right.\\).

Dựa vào bảng biến thiên ta có số lượng sản phẩm thu được lớn nhất thì thời gian làm việc trong một tuần là \\({p["base_hours"]} + ({solution_t1}) \\approx {optimal_hours}\\) giờ.
"""


"""
Dạng toán tối ưu hóa lợi nhuận xuất khẩu với ràng buộc thuế
Tương ứng câu 2 trong bai2.tex
"""


class ExportProfitOptimization(BaseOptimizationQuestion):
    """
    Dạng toán tối ưu hóa lợi nhuận xuất khẩu

    Bài toán cốt lõi:
    - Doanh nghiệp sản xuất sản phẩm với hàm cung R(x) = x - c1
    - Tiêu thụ nội địa Q(x) = c2 - x
    - Xuất khẩu phần dư với giá x0, chịu thuế a
    - Tỷ lệ lãi:thuế = profit_ratio:tax_ratio
    - Tối ưu hóa lợi nhuận xuất khẩu
    """

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán tối ưu hóa xuất khẩu"""

        # Tham số theo pattern từ bai2.tex
        # R(x) = x - c1, Q(x) = c2 - x
        c1 = random.choice([200, 180, 210, 120, 160, 230, 170, 140, 150, 190])  # Hệ số trong hàm sản xuất
        c2 = random.choice(
            [4200, 4500, 4600, 4000, 4300, 4700, 4100, 3900, 4050, 4400])  # Hệ số trong hàm tiêu thụ nội địa

        # Giá xuất khẩu
        x0 = random.choice([3200, 2800, 3400, 3000, 3100, 3600, 2900, 2700, 2950, 3050])  # USD

        # Tỷ lệ lãi:thuế ngẫu nhiên (số nguyên:số nguyên, từ 1 đến 10)
        profit_ratio = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])  # Lãi
        tax_ratio = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])     # Thuế
        profit_tax_ratio = (profit_ratio, tax_ratio)

        return {
            "c1": c1,
            "c2": c2,
            "x0": x0,
            "profit_tax_ratio": profit_tax_ratio
        }

    def calculate_answer(self) -> str:
        """Tính đáp án đúng theo phương pháp toán học chính xác"""
        p = self.parameters

        # Lấy tỷ lệ lãi:thuế
        profit_ratio, tax_ratio = p["profit_tax_ratio"]

        c1 = p["c1"]
        c2 = p["c2"]
        x0 = p["x0"]
        ratio_sum = profit_ratio + tax_ratio

        # Phương pháp toán học đúng:
        # Từ ràng buộc L:T = profit_ratio:tax_ratio
        # Ta có: L = (profit_ratio/tax_ratio) * T
        # Mà L + T = (2x - c1 - c2) * (x0 - x) (tổng lợi nhuận)
        # Nên: T = (tax_ratio/(profit_ratio + tax_ratio)) * (2x - c1 - c2) * (x0 - x)
        # Do đó: a = T / (2x - c1 - c2) = (tax_ratio/ratio_sum) * (x0 - x)

        # Và L = (profit_ratio/ratio_sum) * (2x - c1 - c2) * (x0 - x)
        # Để tối đa hóa L(x), lấy đạo hàm L'(x) = 0
        # L'(x) = (profit_ratio/ratio_sum) * [2(x0 - x) - (2x - c1 - c2)]
        #       = (profit_ratio/ratio_sum) * [2*x0 - 4x + c1 + c2]
        # L'(x) = 0 khi x = (2*x0 + c1 + c2) / 4

        x_optimal = (2 * x0 + c1 + c2) / 4

        # Kiểm tra điều kiện xuất khẩu dương: 2x - c1 - c2 > 0
        export_quantity = 2 * x_optimal - (c1 + c2)
        if export_quantity <= 0:
            # Nếu số lượng xuất khẩu âm hoặc bằng 0, tìm nghiệm biên
            x_min_export = (c1 + c2) / 2  # x tối thiểu để xuất khẩu dương
            x_optimal = x_min_export + 1  # Đảm bảo xuất khẩu dương

        # Tính a theo công thức đúng: a = (tax_ratio/ratio_sum) * (x0 - x)
        a_optimal = (tax_ratio / ratio_sum) * (x0 - x_optimal)

        return f"\\({format_number_clean(a_optimal)}\\)"

    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý"""
        p = self.parameters
        x0 = p["x0"]
        profit_ratio, tax_ratio = p["profit_tax_ratio"]

        # Tính đáp án đúng
        ratio_sum = profit_ratio + tax_ratio
        x_optimal = x0 * profit_ratio / ratio_sum
        a_correct = (x0 - x_optimal) / ratio_sum

        # Các sai lầm thường gặp
        wrong_answers = [
            f"\\({format_number_clean(a_correct * 1.2)}\\)",  # Tính sai 20%
            f"\\({format_number_clean(a_correct / 2)}\\)",  # Chia đôi
            f"\\({format_number_clean(a_correct * 1.5)}\\)"  # Nhân 1.5
        ]

        return wrong_answers

    PROBLEM_TEMPLATES = [
        # Đề bài gốc - Câu 2
        '''Một doanh nghiệp kinh doanh một loại sản phẩm T được sản xuất trong nước. Qua nghiên cứu thấy rằng nếu chi phí sản xuất mỗi sản phẩm T là \\(x\\) USD thì số sản phẩm T các nhà máy sản xuất sẽ là \\(R(x)=x-{c1}\\) và số sản phẩm T mà doanh nghiệp bán được trên thị trường trong nước sẽ là \\(Q(x)={c2}-x\\). Số sản phẩm còn dư doanh nghiệp xuất khẩu ra thị trường quốc tế với giá bán mỗi sản phẩm ổn định trên thị trường quốc tế là \\(x_0={x0} \$\\) . Nhà nước đánh thuế trên mỗi sản phẩm xuất khẩu là \\(a\\) USD và luôn đảm bảo tỉ lệ giữa lãi xuất khẩu của doanh nghiệp và thuế thu được của nhà nước tương ứng là \\({profit_ratio}: {tax_ratio}\\). Hãy xác định giá trị của \\(a\\) biết lãi mà doanh nghiệp thu được do xuất khẩu là nhiều nhất? (Đơn vị: USD)''',

        # Bài tương tự 1
        '''Công ty TNHH T chuyên sản xuất cà phê bột để tiêu thụ trong nước và xuất khẩu. Giá bán cố định của cà phê bột trên thị trường quốc tế là \\(x_0 = {x0}\\) USD mỗi tấn. Phần sản phẩm không tiêu thụ trong nước sẽ được xuất khẩu, và mỗi tấn cà phê xuất khẩu phải chịu mức thuế \\(a\\) USD. Nếu chi phí sản xuất mỗi tấn cà phê là \\(x\\) USD thì doanh nghiệp sản xuất được \\(R(x) = x - {c1}\\) tấn và tiêu thụ nội địa là \\(Q(x) = {c2} - x\\) tấn. Chính sách quốc gia yêu cầu tỷ lệ giữa lợi nhuận từ xuất khẩu và số thuế thu được là \\({profit_ratio} : {tax_ratio}\\). Tìm giá trị \\(a\\) để lợi nhuận từ hoạt động xuất khẩu là lớn nhất. (Đơn vị: USD)''',

        # Bài tương tự 2
        '''Nhà nước quy định rằng tỷ lệ giữa lợi nhuận từ hoạt động xuất khẩu của doanh nghiệp và số thuế thu được phải luôn giữ ở mức \\({profit_ratio} : {tax_ratio}\\). Một doanh nghiệp sản xuất thiết bị điện tử tiêu dùng quyết định mở rộng xuất khẩu, với giá bán cố định trên thị trường quốc tế là \\(x_0 = {x0}\\) USD mỗi thiết bị. Mỗi thiết bị xuất khẩu chịu thuế \\(a\\) USD. Nếu chi phí sản xuất một thiết bị là \\(x\\) USD thì doanh nghiệp sản xuất được \\(R(x) = x - {c1}\\) sản phẩm, trong đó \\(Q(x) = {c2} - x\\) được tiêu thụ tại thị trường trong nước. Hỏi mức thuế \\(a\\) cần đặt là bao nhiêu để lợi nhuận từ xuất khẩu là lớn nhất. (Đơn vị: USD)''',

        # Bài tương tự 3
        '''Một công ty dệt may chuyên sản xuất áo khoác gió thể thao phục vụ thị trường trong nước và xuất khẩu. Nếu chi phí sản xuất mỗi áo là \\(x\\) USD thì nhu cầu nội địa là \\(Q(x) = {c2} - x\\) và sản lượng sản xuất được là \\(R(x) = x - {c1}\\). Các sản phẩm không tiêu thụ hết được xuất khẩu với giá cố định là \\(x_0 = {x0}\\) USD mỗi áo. Mỗi sản phẩm xuất khẩu chịu mức thuế \\(a\\) USD. Nhà nước yêu cầu doanh nghiệp duy trì tỷ lệ giữa lãi và thuế ở mức \\({profit_ratio} : {tax_ratio}\\). Tìm giá trị \\(a\\) sao cho lợi nhuận từ hoạt động xuất khẩu đạt cực đại. (Đơn vị: USD)''',

        # Bài tương tự 4
        '''Một nhà máy thực phẩm sản xuất dầu ăn đóng chai với mục tiêu phục vụ thị trường nội địa và xuất khẩu. Khi chi phí sản xuất mỗi chai là \\(x\\) USD thì sản lượng đạt được là \\(R(x) = x - {c1}\\), và lượng tiêu thụ trong nước là \\(Q(x) = {c2} - x\\). Phần còn lại được xuất khẩu với giá ổn định là \\(x_0 = {x0}\\) USD/chai. Mỗi sản phẩm xuất khẩu chịu thuế \\(a\\) USD. Nhà nước yêu cầu tỷ lệ giữa lợi nhuận từ xuất khẩu và số thuế thu được là \\({profit_ratio} : {tax_ratio}\\). Xác định mức thuế \\(a\\) để lợi nhuận từ xuất khẩu lớn nhất. (Đơn vị: USD)''',

        # Bài tương tự 5
        '''Một công ty khởi nghiệp đang phát triển robot dọn nhà loại mini để bán trong nước và xuất khẩu. Các sản phẩm dư ra được bán ra thị trường quốc tế với giá cố định là \\(x_0 = {x0}\\) USD mỗi thiết bị. Nếu chi phí sản xuất là \\(x\\) USD mỗi thiết bị, thì sản lượng là \\(R(x) = x - {c1}\\) và lượng tiêu thụ nội địa là \\(Q(x) = {c2} - x\\). Theo quy định nhà nước, mỗi sản phẩm xuất khẩu chịu mức thuế \\(a\\) USD và tỉ lệ giữa lợi nhuận và thuế thu được phải là \\({profit_ratio} : {tax_ratio}\\). Hỏi giá trị của \\(a\\) để lợi nhuận từ xuất khẩu đạt cực đại. (Đơn vị: USD)''',

        # Bài tương tự 6
        '''Một công ty công nghệ trẻ đang phát triển robot lau nhà mini để phục vụ thị trường nội địa và xuất khẩu sang nước ngoài. Do điều kiện thị trường, phần sản phẩm dư thừa sau tiêu thụ nội địa sẽ được bán ra quốc tế với mức giá ổn định là \\(x_0 = {x0}\\) USD cho mỗi thiết bị. Nếu chi phí sản xuất một thiết bị là \\(x\\) USD thì số lượng sản phẩm công ty có thể sản xuất là \\(R(x) = x - {c1}\\), và lượng tiêu thụ trong nước được dự báo là \\(Q(x) = {c2} - x\\). Theo quy định của nhà nước, mỗi thiết bị xuất khẩu chịu thuế \\(a\\) USD và tỉ lệ giữa lợi nhuận từ hoạt động xuất khẩu với số thuế thu được phải luôn là \\({profit_ratio} : {tax_ratio}\\). Hỏi mức thuế \\(a\\) cần quy định là bao nhiêu để lợi nhuận thu được từ hoạt động xuất khẩu của công ty là lớn nhất. (Đơn vị: USD)''',

        # Bài tương tự 7
        '''Nhằm đảm bảo cân đối giữa lợi ích doanh nghiệp và ngân sách nhà nước, mỗi đèn LED thông minh xuất khẩu bị đánh thuế \\(a\\) USD. Nhà nước yêu cầu doanh nghiệp phải duy trì tỉ lệ giữa lợi nhuận thu được từ xuất khẩu và số thuế nộp là \\({profit_ratio} : {tax_ratio}\\). Giá bán trên thị trường quốc tế của mỗi đèn LED là \\(x_0 = {x0}\\) USD. Qua khảo sát, nếu chi phí sản xuất mỗi đèn là \\(x\\) USD thì số sản phẩm sản xuất được là \\(R(x) = x - {c1}\\), trong khi số lượng tiêu thụ trong nước là \\(Q(x) = {c2} - x\\). Hỏi doanh nghiệp cần chọn mức thuế \\(a\\) là bao nhiêu để lợi nhuận từ xuất khẩu đạt lớn nhất. (Đơn vị: USD)''',

        # Bài tương tự 8
        '''Một công ty điện tử chuyên sản xuất loa Bluetooth chống nước phục vụ cho cả thị trường nội địa và quốc tế. Nếu chi phí sản xuất mỗi loa là \\(x\\) USD, thì số lượng sản phẩm sản xuất được là \\(R(x) = x - {c1}\\) và lượng tiêu thụ trong nước là \\(Q(x) = {c2} - x\\). Các sản phẩm không tiêu thụ trong nước sẽ được xuất khẩu với mức giá ổn định là \\(x_0 = {x0}\\) USD mỗi chiếc. Theo quy định, mỗi sản phẩm xuất khẩu bị đánh thuế \\(a\\) USD và tỷ lệ giữa lãi và thuế thu được phải luôn là \\({profit_ratio} : {tax_ratio}\\). Tính giá trị \\(a\\) sao cho lợi nhuận từ xuất khẩu là lớn nhất. (Đơn vị: USD)''',

        # Bài tương tự 9
        '''Nhằm khuyến khích phát triển sản phẩm thân thiện với môi trường, chính phủ yêu cầu rằng đối với mỗi đèn năng lượng mặt trời xuất khẩu, tỷ lệ giữa lợi nhuận thu được và số thuế thu phải là \\({profit_ratio} : {tax_ratio}\\). Một công ty chuyên sản xuất đèn năng lượng mặt trời bán phần sản phẩm dư ra thị trường quốc tế với mức giá ổn định \\(x_0 = {x0}\\) USD mỗi đèn. Nếu chi phí sản xuất là \\(x\\) USD thì số lượng sản phẩm sản xuất được là \\(R(x) = x - {c1}\\), còn số sản phẩm tiêu thụ trong nước là \\(Q(x) = {c2} - x\\). Hãy xác định mức thuế \\(a\\) sao cho lợi nhuận từ xuất khẩu là lớn nhất. (Đơn vị: USD)''',

        # Bài tương tự 10
        '''Giá bán quốc tế cố định của mỗi đèn LED thông minh là \\(x_0 = {x0}\\) USD. Nhà máy dự kiến rằng với chi phí sản xuất là \\(x\\) USD thì có thể sản xuất được \\(R(x) = x - {c1}\\) sản phẩm. Mỗi đèn được xuất khẩu phải chịu mức thuế \\(a\\) USD. Theo chính sách nhà nước, tỷ lệ giữa lợi nhuận thu được từ xuất khẩu và số thuế phải luôn đạt mức \\({profit_ratio} : {tax_ratio}\\). Sản lượng tiêu thụ trong nước dự kiến là \\(Q(x) = {c2} - x\\). Hãy xác định giá trị \\(a\\) sao cho lợi nhuận từ xuất khẩu đạt giá trị lớn nhất. (Đơn vị: USD)'''
    ]

    def generate_question_text(self) -> str:
        """Sinh đề bài bằng LaTeX"""
        p = self.parameters
        profit_ratio, tax_ratio = p["profit_tax_ratio"]

        # Thêm profit_ratio và tax_ratio vào parameters để format template
        format_params = p.copy()
        format_params["profit_ratio"] = profit_ratio
        format_params["tax_ratio"] = tax_ratio

        template = random.choice(self.PROBLEM_TEMPLATES)
        return template.format(**format_params)

    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết"""
        p = self.parameters
        profit_ratio, tax_ratio = p["profit_tax_ratio"]

        # Sử dụng kết quả từ calculate_answer() thay vì tính toán lại
        answer_latex = self.calculate_answer()
        # Extract số từ LaTeX format \\(số\\) và xử lý dấu phẩy thập phân
        a_optimal = float(answer_latex.replace("\\(", "").replace("\\)", "").replace(",", "."))

        # Tính các giá trị cho lời giải theo công thức đúng
        ratio_sum = profit_ratio + tax_ratio
        x_optimal = (2 * p["x0"] + p["c1"] + p["c2"]) / 4

        # Format các phân số
        profit_fraction = format_dfrac(profit_ratio, ratio_sum)
        tax_fraction = format_dfrac(tax_ratio, ratio_sum)
        one_over_ratio_sum = format_dfrac(1, ratio_sum)
        one_over_profit_plus_tax = format_dfrac(1, profit_ratio + tax_ratio)

        return f"""
Điều kiện: \\(R(x) = x - {p["c1"]} > 0\\); \\(Q(x) = {p["c2"]} - x > 0 \\Rightarrow {p["c1"]} < x < {p["c2"]}\\).

Số sản phẩm xuất khẩu là: \\(R(x) - Q(x) = (x - {p["c1"]}) - ({p["c2"]} - x) = 2x - {p["c1"] + p["c2"]}\\)

Lãi xuất khẩu của doanh nghiệp là: \\(L(x) = (R(x) - Q(x))({p["x0"]} - x - a) = (2x - {p["c1"] + p["c2"]})({p["x0"]} - x - a)\\).

Thuế thu được của nhà nước là: \\(T(x) = (2x - {p["c1"] + p["c2"]})a\\).

Ta có \\(L(x) : T(x) = {profit_ratio} : {tax_ratio}\\), suy ra \\(L(x) = \\dfrac{{{profit_ratio}}}{{{tax_ratio}}} \\times T(x)\\)

\\(\\Rightarrow (2x - {p["c1"] + p["c2"]})({p["x0"]} - x - a) = \\dfrac{{{profit_ratio}}}{{{tax_ratio}}} \\times (2x - {p["c1"] + p["c2"]})a\\)

\\(\\Rightarrow {p["x0"]} - x - a = \\dfrac{{{profit_ratio}}}{{{tax_ratio}}} \\times a\\)

\\(\\Rightarrow {p["x0"]} - x = a + \\dfrac{{{profit_ratio}}}{{{tax_ratio}}} \\times a = a\\left(1 + \\dfrac{{{profit_ratio}}}{{{tax_ratio}}}\\right) = a \\times \\dfrac{{{tax_ratio} + {profit_ratio}}}{{{tax_ratio}}}\\)

\\(\\Rightarrow a = \\dfrac{{{tax_ratio}}}{{{ratio_sum}}}({p["x0"]} - x)\\)

Khi đó:
$$L(x) = (2x - {p["c1"] + p["c2"]})\\left({p["x0"]} - x - \\dfrac{{{tax_ratio}}}{{{ratio_sum}}}({p["x0"]} - x)\\right) = (2x - {p["c1"] + p["c2"]}) \\dfrac{{{profit_ratio}}}{{{ratio_sum}}}({p["x0"]} - x)$$

$$= {profit_fraction}(2x - {p["c1"] + p["c2"]})({p["x0"]} - x)$$

Bài toán đưa về tìm \\(x\\) để \\(L(x)\\) đạt giá trị lớn nhất.

Lấy đạo hàm: \\(L'(x) = {profit_fraction}[2({p["x0"]} - x) - (2x - {p["c1"] + p["c2"]})] = {profit_fraction}[2 \\cdot {p["x0"]} - 4x + {p["c1"] + p["c2"]}]\\)

\\(L'(x) = 0 \\Leftrightarrow x = \\dfrac{{1}}{{4}}(2 \\cdot {p["x0"]} + {p["c1"] + p["c2"]}) \\approx {format_number_clean(x_optimal)}\\)

Lập bảng biến thiên ta thấy \\(L(x)\\) đạt giá trị lớn nhất khi \\(x \\approx {format_number_clean(x_optimal)}\\).

Suy ra \\(a = \\dfrac{{{tax_ratio}}}{{{ratio_sum}}}({p["x0"]} - {format_number_clean(x_optimal)}) \\approx {format_number_clean(a_optimal)}\\).
"""


"""
Dạng toán tối ưu hóa chi phí nhiên liệu tàu
Tương ứng câu 3 trong bai2.tex
"""


class FuelCostOptimization(BaseOptimizationQuestion):
    """
    Dạng toán tối ưu hóa chi phí nhiên liệu tàu

    Bài toán cốt lõi:
    - Chi phí gồm 2 phần: cố định (a nghìn đồng/giờ) và biến thiên (kv^2 nghìn đồng/giờ)
    - Tìm vận tốc v để chi phí trên 1km là nhỏ nhất(Đơn vị: km/h)
    - f(v) = a/v + kv, tối ưu tại v = sqrt(a/k)
    """

    PROBLEM_TEMPLATES = [
        # Đề bài gốc
        '''Trên một khúc sông có dòng nước lặng, một chiếc tàu chạy với tốc độ không đổi, chi phí nhiên liệu được tính bởi hai phần: Phần thứ nhất không phụ thuộc vào tốc độ và mất chi phí {fixed_cost} nghìn đồng/giờ; Phần thứ hai tỉ lệ thuận với bình phương của tốc độ, khi \\(v={ref_speed}(\\mathrm{{~km}} / \\mathrm{{h}})\\) thì chi phí phần thứ hai là {ref_variable_cost} nghìn đồng/giờ. Tìm tốc độ của tàu để tổng chi phí nhiên liệu khi tàu chạy 1 km trên sông là ít nhất (kết quả làm tròn đến hàng phần trăm). (Đơn vị: km/h)''',

        # Bài tương tự 1
        '''Một đơn vị vận tải đường thủy đang nghiên cứu phương án giảm thiểu chi phí nhiên liệu trong quá trình vận hành tàu chở hàng trên khúc sông có dòng nước lặng. Việc tối ưu chi phí trở nên quan trọng trong bối cảnh giá nhiên liệu ngày càng tăng và nhu cầu vận chuyển liên tục. Tổng chi phí nhiên liệu cho mỗi giờ hành trình được cấu thành từ hai phần: phần thứ nhất là chi phí cố định, không phụ thuộc vào vận tốc, trị giá {fixed_cost} nghìn đồng/giờ; phần thứ hai là chi phí phụ thuộc vào vận tốc, cụ thể tỉ lệ thuận với bình phương vận tốc của tàu. Tại vận tốc \\(v = {ref_speed}\\) km/h, chi phí phần biến thiên này được xác định là {ref_variable_cost} nghìn đồng/giờ. Bài toán đặt ra là tìm tốc độ \\(v\\) (km/h) để tổng chi phí nhiên liệu cho mỗi km hành trình là ít nhất. Kết quả làm tròn đến hàng phần trăm. (Đơn vị: km/h)''',

        # Bài tương tự 2
        '''Một công ty lữ hành đang khai thác tuyến sông nội địa với các tàu du lịch cao cấp phục vụ khách tham quan. Để duy trì lợi nhuận trong mùa thấp điểm, công ty cần tối ưu hóa chi phí nhiên liệu. Qua khảo sát kỹ thuật, người ta xác định rằng chi phí nhiên liệu trong mỗi giờ hành trình bao gồm hai phần: chi phí cố định là {fixed_cost} nghìn đồng, không phụ thuộc vào tốc độ tàu, và chi phí biến thiên phụ thuộc vào bình phương vận tốc. Khi tàu chạy với vận tốc {ref_speed} km/h, chi phí biến thiên đo được là {ref_variable_cost} nghìn đồng mỗi giờ. Hãy xác định vận tốc \\(v\\) (km/h) sao cho chi phí nhiên liệu trên mỗi km hành trình là ít nhất. Làm tròn kết quả đến hàng phần trăm. (Đơn vị: km/h)''',

        # Bài tương tự 3
        '''Trên tuyến kênh đào thẳng, không có dòng chảy và thường xuyên được dùng để vận chuyển hàng hóa nặng, một tàu container đang vận hành ổn định. Ban điều hành tuyến vận tải mong muốn tiết kiệm chi phí nhiên liệu nhằm tăng lợi nhuận. Theo phân tích, chi phí nhiên liệu gồm hai phần: phần cố định {fixed_cost} nghìn đồng/giờ, và phần phụ thuộc bình phương vận tốc. Khi tàu chạy với tốc độ {ref_speed} km/h, phần biến thiên này là {ref_variable_cost} nghìn đồng/giờ. Xác định vận tốc \\(v\\) (km/h) sao cho chi phí nhiên liệu để đi hết quãng đường 1 km là ít nhất. Làm tròn đến hàng phần trăm. (Đơn vị: km/h)''',

        # Bài tương tự 4
        '''Trên sông lớn với mặt nước êm đềm, một chiếc tàu chở khách được vận hành nhằm phục vụ nhu cầu di chuyển liên tỉnh. Để kiểm soát chi phí vận hành, nhà điều hành tàu cần tính toán vận tốc hợp lý để giảm thiểu lượng nhiên liệu tiêu thụ. Biết rằng chi phí nhiên liệu bao gồm phần không đổi là {fixed_cost} nghìn đồng mỗi giờ và phần biến thiên phụ thuộc bình phương vận tốc. Khi vận tốc tàu là {ref_speed} km/h, phần chi phí biến thiên đo được là {ref_variable_cost} nghìn đồng/giờ. Tìm tốc độ \\(v\\) sao cho chi phí nhiên liệu cho mỗi km hành trình là nhỏ nhất. Làm tròn đến hàng phần trăm. (Đơn vị: km/h)''',

        # Bài tương tự 5
        '''Trong công tác cứu hộ trên hồ nước ngọt, thời gian và nhiên liệu đều là những yếu tố cần được tối ưu. Một tàu cứu hộ hiện đang hoạt động thường xuyên và cần xác định tốc độ vận hành hiệu quả nhất. Chi phí nhiên liệu trong mỗi giờ di chuyển bao gồm phần cố định {fixed_cost} nghìn đồng và phần tỉ lệ thuận với bình phương vận tốc. Khi vận tốc là {ref_speed} km/h, phần chi phí biến thiên được đo là {ref_variable_cost} nghìn đồng/giờ. Hãy xác định vận tốc \\(v\\) (km/h) sao cho tổng chi phí nhiên liệu để tàu đi được 1 km là thấp nhất. Làm tròn kết quả đến hàng phần trăm. (Đơn vị: km/h)'''
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

        return f"\\({format_number_clean(optimal_speed, precision=2)}\\)"

    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý"""
        p = self.parameters
        a = p["fixed_cost"]
        k = p["k"]

        optimal_speed = math.sqrt(a / k)

        # Các sai lầm thường gặp
        wrong_answers = [
            f"\\({format_number_clean(optimal_speed * 1.1, precision=2)}\\)",  # Cao hơn 10%
            f"\\({format_number_clean(optimal_speed * 0.9, precision=2)}\\)",  # Thấp hơn 10%
            f"\\({p['ref_speed']}\\)"  # Lấy vận tốc tham chiếu
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

        # Sử dụng kết quả từ calculate_answer() thay vì tính toán lại
        answer_latex = self.calculate_answer()
        # Extract số từ LaTeX format \\(số\\) và xử lý dấu phẩy thập phân
        optimal_speed = float(answer_latex.replace("\\(", "").replace("\\)", "").replace(",", "."))

        # Tính hệ số k đúng như trong generate_parameters: k = ref_variable_cost / ref_speed^2
        k = ref_variable_cost / (ref_speed ** 2)

        # Tính chi phí tối thiểu: f(x) = 2*sqrt(a*k)
        min_cost = 2 * math.sqrt(a * k)

        # Format các phân số
        one_over_x = format_dfrac(1, 1) + "/x"  # 1/x
        a_over_x = format_dfrac(a, 1) + "/x"  # a/x
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
Gọi \\(x\\) (km/h) là tốc độ của tàu \\((x > 0)\\).

Thời gian để tàu chạy 1 km trên sông là \\({one_over_x}\\) (giờ).

Chi phí cho phần thứ nhất để tàu chạy 1 km là: \\(p_1={a} \\cdot {one_over_x}={a_over_x}\\) (nghìn đồng/giờ).

Chi phí cho phần thứ hai để tàu chạy 1 km có dạng: \\(p_2=k x^2 \\cdot {one_over_x}=k x\\) (nghìn đồng/giờ).

Khi \\(x={ref_speed}\\) thì \\(p_2={ref_variable_cost}\\) nên \\(k={k}\\). Do đó \\(p_2={k} x\\) (nghìn đồng/giờ).

Vậy tổng chi phí để tàu chạy 1 km trên khúc sông đó là: \\(f(x)={a_over_x}+{k} x\\) (nghìn đồng/giờ).

Ta có: \\(f^{{\\prime}}(x)=-{a_over_x_squared}+{k}\\).

        Giải phương trình: \\(f^{{\\prime}}(x)=0 \\Leftrightarrow x={format_sqrt_special(a / k)}\\) (thoả mãn) hoặc \\(x=-{format_sqrt_special(a / k)}\\) (loại vì \\(x>0\\)).

        Lập bảng biến thiên của hàm số \\(f(x)\\) với \\(x>0\\), ta tìm được \\(\\min_{{x \\in(0 ;+\\infty)}} f(x)=f({format_sqrt_special(a / k)})={format_sqrt_special(a * k)}\\).

        Vậy tốc độ của tàu để tổng chi phí nhiên liệu khi tàu chạy 1 km trên sông ít nhất là \\({format_sqrt_special(a / k)} \\approx {format_number_clean(optimal_speed, precision=2)}\\) (km/h).
"""


"""
Dạng toán tối ưu hóa lợi nhuận nhà máy với thuế GTGT
Tương ứng câu 4 trong bai2.tex
"""


class FactoryProfitOptimization(BaseOptimizationQuestion):
    """
    Dạng toán tối ưu hóa lợi nhuận nhà máy

    Bài toán cốt lõi:
    - Giá bán: p(x) = a - bx^2
    - Chi phí: C(x) = phân_số × (c + dx) (với phân số ngẫu nhiên)
    - Thuế GTGT : vat_rate_percent%
    - Tối ưu hóa lợi nhuận = Doanh thu - Chi phí - Thuế
    """

    PROBLEM_TEMPLATES = [
        # Đề bài gốc - Câu 4
        '''Nhà máy A chuyên sản suất một loại sản phẩm cho nhà máy B. Hai nhà máy thỏa thuận rằng, hàng tháng nhà máy A cung cấp cho nhà máy B số lượng sản phẩm theo đơn đặt hàng của nhà máy B (tối đa {max_production} tấn sản phẩm). Nếu số lượng đặt hàng là \\(x\\)  tấn sản phẩm. Thì giá bán cho mỗi tấn sản phẩm là \(p(x)={price_a}-{price_b} x^2\) (đơn vị triệu đồng). Chi phí để nhà máy A sản suất \\(x\\)  tấn sản phẩm trong một tháng là \(C(x)=\dfrac{{{cost_numerator}}}{{{cost_denominator}}}({cost_c}+{cost_d} x)\) (đơn vị: triệu đồng), thuế giá trị gia tăng mà nhà máy A phải đóng cho nhà nước là {vat_rate_percent}\\% tổng doanh thu mỗi tháng. Hỏi nhà máy A bán cho nhà máy B bao nhiêu tấn sản phẩm mỗi tháng để thu được lợi nhuận (sau khi đã trừ thuế giá trị gia tăng) cao nhất? (Đơn vị: tấn)''',

        # Bài tương tự 1
        '''Trong bối cảnh thị trường xây dựng đang có xu hướng phục hồi sau khủng hoảng, nhiều doanh nghiệp sản xuất vật liệu xây dựng chuyên cung cấp gạch ốp lát cho các công trình dân dụng và đối tác lớn. Tuy nhiên, để đảm bảo chất lượng và tiến độ, công ty giới hạn lượng hàng cung cấp mỗi tháng không vượt quá {max_production} tấn. Doanh thu bán hàng chịu thuế GTGT {vat_rate_percent}\\%. Chi phí sản xuất \\(x\\) tấn mỗi tháng là \\(C(x) = \\dfrac{{{cost_numerator}}}{{{cost_denominator}}}({cost_c} + {cost_d}x)\\) (triệu đồng). Giá bán mỗi tấn sản phẩm được tính theo công thức \\(p(x) = {price_a} - {price_b}x^2\\) (triệu đồng). Hỏi doanh nghiệp nên bán bao nhiêu tấn mỗi tháng để thu được lợi nhuận sau thuế lớn nhất? (Đơn vị: tấn)''',

        # Bài tương tự 2
        '''Đáp ứng nhu cầu sử dụng thực phẩm sạch ngày càng cao tại các thành phố lớn, một nông trại rau hữu cơ tại vùng ven đô mở rộng sản lượng để cung cấp cho chuỗi siêu thị nội địa. Tuy nhiên, do giới hạn vận chuyển và bảo quản, nông trại chỉ có thể cung cấp tối đa {max_production} tấn rau mỗi tháng. Doanh thu từ việc bán rau bị đánh thuế GTGT {vat_rate_percent}\\%. Chi phí sản xuất khi cung ứng \\(x\\) tấn là \\(C(x) = \\dfrac{{{cost_numerator}}}{{{cost_denominator}}}({cost_c} + {cost_d}x)\\) (triệu đồng). Giá bán mỗi tấn rau được mô hình hóa theo hàm \\(p(x) = {price_a} - {price_b}x^2\\) (triệu đồng). Nên bán bao nhiêu tấn rau để tối ưu lợi nhuận sau thuế? (Đơn vị: tấn)''',

        # Bài tương tự 3
        '''Một công ty sản xuất nước giải khát tại miền Trung vừa ra mắt dòng sản phẩm nước hoa quả lên men không đường nhằm phục vụ nhóm khách hàng quan tâm đến sức khỏe. Sản phẩm được phân phối đến chuỗi siêu thị lớn tại các thành phố lớn như Hà Nội và Đà Nẵng. Do hạn chế về hệ thống kho lạnh và phương tiện vận chuyển chuyên dụng, mỗi tháng công ty chỉ có thể xuất không quá {max_production} tấn sản phẩm ra thị trường. Toàn bộ doanh thu từ việc phân phối sản phẩm sẽ chịu thuế GTGT {vat_rate_percent}\\%. Chi phí sản xuất lượng hàng \\(x\\) tấn là \\(C(x) = \\dfrac{{{cost_numerator}}}{{{cost_denominator}}}({cost_c} + {cost_d}x)\\) (triệu đồng), và giá bán mỗi tấn phụ thuộc vào sản lượng tiêu thụ: \\(p(x) = {price_a} - {price_b}x^2\\) (triệu đồng). Hỏi công ty nên bán bao nhiêu tấn mỗi tháng để lợi nhuận sau thuế đạt tối đa? (Đơn vị: tấn)''',

        # Bài tương tự 4
        '''Một cơ sở chế biến thủy sản tại Khánh Hòa chuyên sản xuất cá phi lê đông lạnh theo tiêu chuẩn HACCP để cung ứng cho chuỗi nhà hàng hải sản và khách sạn 4–5 sao tại TP. Hồ Chí Minh và Nha Trang. Do hệ thống kho đông và phương tiện bảo quản còn giới hạn, mỗi tháng cơ sở chỉ có thể vận chuyển tối đa {max_production} tấn cá thành phẩm ra thị trường. Doanh thu từ hoạt động kinh doanh phải chịu thuế GTGT {vat_rate_percent}\\% theo quy định hiện hành. Chi phí chế biến cá \\(x\\)  tấn được mô hình hóa theo hàm \(C(x) = \dfrac{{{cost_numerator}}}{{{cost_denominator}}}({cost_c} + {cost_d}x)\) (triệu đồng). Giá bán mỗi tấn sản phẩm phụ thuộc vào khối lượng tiêu thụ, được tính theo công thức: \(p(x) = {price_a} - {price_b}x^2\) (triệu đồng). Hỏi cơ sở nên bán bao nhiêu tấn cá mỗi tháng để lợi nhuận sau thuế là lớn nhất? (Đơn vị: tấn)''',

        # Bài tương tự 5
        '''Một xưởng gỗ tại Tây Nguyên hợp tác với một chuỗi công ty nội thất chuyên sản xuất bàn, tủ và giường cho thị trường nội địa và xuất khẩu. Trong bối cảnh giá nguyên vật liệu tăng và yêu cầu về chứng nhận nguồn gỗ hợp pháp ngày càng chặt chẽ, xưởng phải giới hạn sản lượng tối đa ở mức {max_production} tấn gỗ mỗi tháng để đảm bảo chất lượng và đáp ứng tiêu chuẩn bền vững. Mọi doanh thu từ việc bán gỗ đều phải nộp thuế GTGT {vat_rate_percent}\\%. Chi phí sản xuất gỗ theo sản lượng \\(x\\)  tấn là \(C(x) = \dfrac{{{cost_numerator}}}{{{cost_denominator}}}({cost_c} + {cost_d}x)\) (triệu đồng), trong khi giá bán mỗi tấn được điều chỉnh theo lượng cung ứng và được cho bởi \(p(x) = {price_a} - {price_b}x^2\) (triệu đồng). Công ty nên đặt hàng bao nhiêu tấn mỗi tháng để xưởng thu được lợi nhuận cao nhất sau thuế? (Đơn vị: tấn)''',

        # Bài tương tự 6
        '''Một trang trại bò sữa tại Đà Lạt có hệ thống chăn nuôi khép kín với sản lượng cung ứng ổn định quanh năm. Trang trại ký hợp đồng với một công ty chế biến sữa hộp để cung cấp sữa tươi nguyên liệu. Tuy nhiên, do giới hạn công suất xe lạnh và hệ thống bảo quản tại điểm tiếp nhận, lượng sữa được phép giao tối đa mỗi tháng là {max_production} tấn. Doanh thu từ việc bán sữa phải chịu thuế GTGT {vat_rate_percent}\\% theo quy định hiện hành. Chi phí để sản xuất ra \\(x\\)  tấn sữa là \(C(x) = \dfrac{{{cost_numerator}}}{{{cost_denominator}}}({cost_c} + {cost_d}x)\) (triệu đồng). Giá bán mỗi tấn sữa tươi phụ thuộc vào lượng cung cấp, được cho bởi \(p(x) = {price_a} - {price_b}x^2\) (triệu đồng). Trang trại nên cung cấp bao nhiêu tấn mỗi tháng để đạt được lợi nhuận sau thuế lớn nhất? (Đơn vị: tấn)''',

        # Bài tương tự 7
        '''Một công ty hóa chất công nghiệp có trụ sở tại khu công nghiệp Biên Hòa chuyên sản xuất chất phụ gia cho ngành dệt nhuộm và xử lý nước. Trước những quy định khắt khe về môi trường, công ty buộc phải giới hạn lượng nguyên liệu hóa chất bán ra ở mức không quá {max_production} tấn mỗi tháng để đảm bảo an toàn vận hành và quy trình xử lý chất thải. Doanh thu bán hàng mỗi tháng chịu thuế GTGT {vat_rate_percent}\\%. Chi phí để sản xuất ra \\(x\\)  tấn sản phẩm là \(C(x) = \dfrac{{{cost_numerator}}}{{{cost_denominator}}}({cost_c} + {cost_d}x)\) (triệu đồng). Giá bán mỗi tấn sản phẩm tùy theo quy mô đơn hàng và được xác định bởi hàm \(p(x) = {price_a} - {price_b}x^2\) (triệu đồng). Công ty nên cung cấp bao nhiêu tấn mỗi tháng để đạt lợi nhuận sau thuế cao nhất? (Đơn vị: tấn)''',

        # Bài tương tự 8
        '''Một hợp tác xã nông nghiệp tại Đồng bằng sông Cửu Long đầu tư dây chuyền sản xuất phân bón hữu cơ phục vụ các tỉnh lân cận và xuất khẩu tiểu ngạch sang Campuchia. Do đặc thù vận chuyển bằng ghe tàu, kho chứa hạn chế và điều kiện bảo quản phân hữu cơ, hợp tác xã chỉ có thể cung ứng tối đa {max_production} tấn phân bón mỗi tháng. Mọi doanh thu thu được đều phải chịu thuế giá trị gia tăng {vat_rate_percent}\\%. Chi phí sản xuất \\(x\\)  tấn phân là \(C(x) = \dfrac{{{cost_numerator}}}{{{cost_denominator}}}({cost_c} + {cost_d}x)\) (triệu đồng). Giá bán mỗi tấn phân bón được xác định theo công thức \(p(x) = {price_a} - {price_b}x^2\) (triệu đồng). Hợp tác xã nên cung cấp bao nhiêu tấn mỗi tháng để tối đa hóa lợi nhuận sau thuế? (Đơn vị: tấn)''',
    ]

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán tối ưu hóa lợi nhuận nhà máy"""

        # Tham số theo pattern từ bai2.tex
        # p(x) = a - b*x^2, thường a = 90, b = 0.01
        price_a = random.choice([90, 85, 95, 88, 92])
        price_b = random.choice([0.01, 0.008, 0.012, 0.009, 0.011])

        # C(x) = phân_số * (c + d*x), với phân số ngẫu nhiên  
        cost_c = random.choice([200, 180, 220, 190, 210])
        cost_d = random.choice([27, 25, 30, 26, 28])

        # Sinh phân số ngẫu nhiên cho chi phí (tử số / mẫu số)
        cost_numerator = random.choice([1, 2, 3, 4, 5])
        cost_denominator = random.choice([2, 3, 4, 5, 6, 7, 8])
        # Đảm bảo phân số khác 1 để có tính thú vị
        while cost_numerator == cost_denominator:
            cost_denominator = random.choice([2, 3, 4, 5, 6, 7, 8])

        # Giới hạn sản lượng
        max_production = 100  # tấn

        # Thuế GTGT (random từ 8% đến 20%)
        vat_rate = random.choice([0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20])

        return {
            "price_a": price_a,
            "price_b": price_b,
            "cost_c": cost_c,
            "cost_d": cost_d,
            "cost_numerator": cost_numerator,
            "cost_denominator": cost_denominator,
            "max_production": max_production,
            "vat_rate": vat_rate,
            "vat_rate_percent": int(vat_rate * 100)
        }

    def calculate_answer(self) -> str:
        """Tính đáp án đúng"""
        p = self.parameters

        # Tính toán chính xác theo công thức
        # C(x) = (cost_numerator/cost_denominator) * (cost_c + cost_d*x)
        cost_fraction = p["cost_numerator"] / p["cost_denominator"]
        coef_x = p["price_a"] * (1 - p["vat_rate"]) - p["cost_d"] * cost_fraction
        coef_x3 = -p["price_b"] * (1 - p["vat_rate"])

        # Giải phương trình L'(x) = 0: 3*coef_x3*x² + coef_x = 0
        # x² = -coef_x / (3*coef_x3)
        optimal_production = int((coef_x / (3 * abs(coef_x3))) ** 0.5)

        return f"\\({optimal_production}\\)"

    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý"""
        p = self.parameters

        # Tính đáp án đúng để tạo đáp án sai
        coef_x = p["price_a"] * (1 - p["vat_rate"]) - p["cost_d"] / 2
        coef_x3 = -p["price_b"] * (1 - p["vat_rate"])
        correct_answer = int((coef_x / (3 * abs(coef_x3))) ** 0.5)

        # Các sai lầm thường gặp
        wrong_answers = [
            f"\\({correct_answer + 10}\\)",  # Cao hơn 10 tấn
            f"\\({max(0, correct_answer - 10)}\\)",  # Thấp hơn 10 tấn
            f"\\({p['max_production']}\\)",  # Lấy sản lượng tối đa
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

        # Sử dụng kết quả từ calculate_answer() thay vì tính toán lại
        answer_latex = self.calculate_answer()
        # Extract số từ LaTeX format \\(số\\) và xử lý dấu phẩy thập phân
        optimal_x = int(float(answer_latex.replace("\\(", "").replace("\\)", "").replace(",", ".")))

        # Tính toán các hệ số theo pattern chuẩn cho hiển thị trong lời giải
        # L(x) = B(x) - C(x) - T(x)
        # = x(p_a - p_b*x²) - (numerator/denominator)*(c + d*x) - vat_rate*x(p_a - p_b*x²)
        # = x*p_a - p_b*x³ - (numerator/denominator)*c - (numerator/denominator)*d*x - vat_rate*p_a*x + vat_rate*p_b*x³
        # = (p_a - vat_rate*p_a - (numerator/denominator)*d)*x + (-p_b + vat_rate*p_b)*x³ - (numerator/denominator)*c
        # = (p_a*(1-vat_rate) - (numerator/denominator)*d)*x + (-p_b*(1-vat_rate))*x³ - (numerator/denominator)*c

        cost_fraction = p["cost_numerator"] / p["cost_denominator"]
        coef_x = p["price_a"] * (1 - p["vat_rate"]) - p["cost_d"] * cost_fraction
        coef_x3 = -p["price_b"] * (1 - p["vat_rate"])
        const_term = -p["cost_c"] * cost_fraction

        # Format các phân số
        cost_fraction_frac = format_dfrac(p["cost_numerator"], p["cost_denominator"])
        vat_rate_frac = format_dfrac(int(p["vat_rate"] * 100), 100)

        return f"""
Giả sử số lượng sản phẩm bán ra là \\(x\\) tấn, \\(0 \\leq x \\leq {p["max_production"]}\\).

Doanh thu \\(B(x) = x \\cdot p(x) = x({p["price_a"]} - {p["price_b"]}x^2)\\).

Thuế giá trị gia tăng \\(T(x) = {format_number_clean(p["vat_rate"] * 100)}\\% B(x) = {vat_rate_frac} x({p["price_a"]} - {p["price_b"]}x^2)\\).

Lợi nhuận = Doanh thu - Chi phí - Thuế:

\\(L(x) = B(x) - C(x) - T(x) = x({p["price_a"]} - {p["price_b"]}x^2) - {cost_fraction_frac}({p["cost_c"]} + {p["cost_d"]}x) - {format_number_clean(p["vat_rate"] * 100)}\\% x({p["price_a"]} - {p["price_b"]}x^2) = {format_number_clean(coef_x3, 4)}x^3 + {format_number_clean(coef_x)}x + {format_number_clean(const_term)}\\).

\\(L'(x) = {format_number_clean(3 * coef_x3, 4)}x^2 + {format_number_clean(coef_x)} = 0 \\Leftrightarrow x \\approx {optimal_x}\\).

Lập bảng biến thiên ta được lợi nhuận cao nhất khi \\(x \\approx {optimal_x}\\).
"""


"""
Dạng toán tối ưu hóa chi phí trung bình cho chụp đèn hình chóp cụt
Tương ứng câu 5 trong bai2.tex
"""


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

        optimal_x = -b + math.sqrt(b * b + a)

        return f"\\({format_number_clean(optimal_x)}\\)"

    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý"""
        p = self.parameters
        a = p["cost_a"]
        b = p["time_b"]

        optimal_x = -b + math.sqrt(b * b + a)

        # Các sai lầm thường gặp
        wrong_answers = [
            f"\\({format_number_clean(optimal_x * 1.1)}\\)",  # Cao hơn 10%
            f"\\({format_number_clean(optimal_x * 0.9)}\\)",  # Thấp hơn 10%
            f"\\({format_number_clean(math.sqrt(a))}\\)"  # Lấy sqrt(a)
        ]

        return wrong_answers

    PROBLEM_TEMPLATES = [
        # Đề bài gốc - Câu 5
        '''Một xưởng thủ công mỹ nghệ sản xuất loại chụp đèn trang trí dạng hình chóp cụt tứ giác đều. Gọi \\(x\\) là độ dài cạnh đáy lớn (đơn vị:dm). Tính toán cho thấy tổng chi phí vật liệu (tính bằng nghìn đồng) cho một chụp đèn là \\(C(x)=x^2+{cost_a}\\) (nghìn đồng). Thời gian sản xuất cho một chụp đèn được xác định là \\(T(x)=x+{time_b}\\) (giờ). Xưởng muốn xác định kích thước \\(x\\) để chi phí vật liệu trung bình trên một giờ sản xuất là thấp nhất, nhằm tối ưu hóa hiệu quả sử dụng thời gian và vật liệu. (Đơn vị: dm)''',

        # Bài tương tự 1
        '''Một xưởng chế tác thủ công tại Hội An chuyên sản xuất chao đèn trang trí bằng tre cho các khu nghỉ dưỡng cao cấp. Một loại chao đèn đặc biệt có dạng hình chóp cụt tứ giác đều, được thiết kế tinh xảo để tạo hiệu ứng ánh sáng mềm mại. Để cân đối giữa chi phí vật liệu và thời gian sản xuất cho mỗi sản phẩm, chủ xưởng cần xác định kích thước đáy lớn phù hợp. Gọi \\(x\\) (đơn vị: dm) là độ dài cạnh đáy lớn. Chi phí vật liệu để sản xuất một chao đèn được tính theo công thức \\(C(x) = x^2 + {cost_a}\\) (nghìn đồng), còn thời gian để hoàn thiện một sản phẩm là \\(T(x) = x + {time_b}\\) (giờ). Để sử dụng hiệu quả nguyên vật liệu và công sức lao động, xưởng mong muốn tìm giá trị của \\(x\\) sao cho chi phí vật liệu trung bình trên mỗi giờ sản xuất là nhỏ nhất. (Đơn vị: dm)''',

        # Bài tương tự 2
        '''Một xưởng gốm ở Bát Tràng sản xuất các loại chân đèn gốm theo đơn đặt hàng từ các cửa hàng nội thất. Một mẫu đèn có phần chụp được thiết kế theo dạng hình chóp cụt tứ giác đều với cạnh đáy lớn là \\(x\\) (dm). Chủ xưởng mong muốn tính toán để tiết kiệm nguyên liệu đất sét và công sức lao động. Chi phí vật liệu (nghìn đồng) là \\(C(x) = x^2 + {cost_a}\\), còn thời gian sản xuất mỗi sản phẩm là \\(T(x) = x + {time_b}\\) (giờ). Họ cần xác định kích thước \\(x\\) sao cho chi phí vật liệu trung bình trên mỗi giờ làm việc là thấp nhất. (Đơn vị: dm)''',

        # Bài tương tự 3
        '''Một công ty thiết kế đèn trang trí nhận hợp đồng sản xuất loạt đèn bàn theo mẫu hình chóp cụt tứ giác đều. Để tiết kiệm chi phí và đẩy nhanh tiến độ sản xuất, bộ phận kỹ thuật cần tính toán kích thước đáy lớn tối ưu. Gọi \\(x\\) (dm) là độ dài cạnh đáy lớn, khi đó chi phí vật liệu để làm một chiếc đèn là \\(C(x) = x^2 + {cost_a}\\) (nghìn đồng) và thời gian cần thiết để hoàn thành một sản phẩm là \\(T(x) = x + {time_b}\\) (giờ). Công ty mong muốn biết với kích thước \\(x\\) nào thì chi phí vật liệu trung bình trên mỗi giờ sản xuất sẽ đạt giá trị thấp nhất. (Đơn vị: dm)''',

        # Bài tương tự 4
        '''Một nhóm sinh viên khởi nghiệp sản xuất đèn handmade từ giấy kraft tái chế để phục vụ phân khúc quà tặng sáng tạo. Mẫu đèn chóp cụt tứ giác đều của nhóm rất được ưa chuộng nhờ kiểu dáng độc đáo và tinh tế. Trong quá trình thiết kế và sản xuất, nhóm cần xác định kích thước cạnh đáy lớn \\(x\\) (dm) sao cho hiệu quả sử dụng giấy và thời gian hoàn thiện sản phẩm được tối ưu. Chi phí giấy là \\(C(x) = x^2 + {cost_a}\\) (nghìn đồng) và thời gian sản xuất mỗi đèn là \\(T(x) = x + {time_b}\\) (giờ). Họ cần tìm giá trị của \\(x\\) sao cho chi phí vật liệu trung bình trên một giờ làm việc là nhỏ nhất. (Đơn vị: dm)''',

        # Bài tương tự 5
        '''Một cơ sở sản xuất đồ thủ công mỹ nghệ đang thực hiện đơn hàng xuất khẩu lô đèn trang trí kiểu cổ điển sang thị trường châu Âu. Mỗi chiếc đèn có phần chụp được thiết kế theo dạng hình chóp cụt tứ giác đều, đòi hỏi sự tỉ mỉ trong từng công đoạn gia công. Để đạt hiệu quả cao trong sản xuất hàng loạt, kỹ sư thiết kế của cơ sở cần xác định độ dài cạnh đáy lớn \\(x\\) (dm) sao cho chi phí vật liệu trung bình trên mỗi giờ sản xuất là thấp nhất. Biết rằng chi phí vật liệu là \\(C(x) = x^2 + {cost_a}\\) (nghìn đồng) và thời gian hoàn thành một chiếc đèn là \\(T(x) = x + {time_b}\\) (giờ). (Đơn vị: dm)'''
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

        # Sử dụng kết quả từ calculate_answer() thay vì tính toán lại
        answer_latex = self.calculate_answer()
        # Extract số từ LaTeX format \\(số\\) và xử lý dấu phẩy thập phân
        optimal_x = float(answer_latex.replace("\\(", "").replace("\\)", "").replace(",", "."))

        min_cost = (optimal_x * optimal_x + a) / (optimal_x + b)

        # Tính giá trị thập phân cho hai nghiệm
        x1_value = -b - math.sqrt(b * b + a)  # Nghiệm loại
        x2_value = -b + math.sqrt(b * b + a)  # Nghiệm nhận

        return f"""
Gọi hàm chi phí vật liệu trung bình trên một giờ sản xuất là \\(f(x)=\\dfrac{{C(x)}}{{T(x)}}=\\dfrac{{x^2+{a}}}{{x+{b}}}, x>0\\).

Ta có \\(f'(x)=\\dfrac{{x^2+{2 * b}x-{a}}}{{(x+{b})^2}}=0 \\Leftrightarrow \\left[\\begin{{array}}{{l}}x \\approx {format_number_clean(x1_value, 2)}(L) \\\\ x \\approx {format_number_clean(x2_value, 2)}\\end{{array}}\\right.\\)

Từ bảng biến thiên ta thấy \\(f(x)\\) đạt GTNN bằng \\({format_number_clean(min_cost)}\\) khi \\(x \\approx {format_number_clean(optimal_x)}\\).

Vậy để chi phí vật liệu trung bình trên một giờ sản xuất là thấp nhất thì \\(x \\approx {format_number_clean(optimal_x)}\\).
"""



# Danh sách các dạng toán có sẵn
def get_available_question_types():
    """Trả về danh sách các dạng toán có sẵn"""

    return [
        ProductionOptimization,
        ExportProfitOptimization,
        FuelCostOptimization,
        FactoryProfitOptimization,
        LampCostOptimization
    ]


def generate_mixed_questions(num_questions: int = 9) -> str:
    """Sinh nhiều câu hỏi từ các dạng toán khác nhau"""
    question_types = get_available_question_types()
    questions = []

    for i in range(num_questions):
        question_type = random.choice(question_types)
        question_generator = question_type()
        question_content, _ = question_generator.generate_question_only(i + 1)
        questions.append(question_content)

    return BaseOptimizationQuestion.create_latex_document(questions, "Tổng hợp Câu hỏi Tối ưu hóa từ bai2.tex")


def main():
    """
    Hàm main để chạy generator với hỗ trợ 2 format
    Cách sử dụng:
    python main_runner.py [số_câu] [format]
    """
    try:
        # Lấy tham số từ command line
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        fmt = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] in ['1', '2'] else 1

        # Tạo câu hỏi
        question_types = get_available_question_types()
        questions_data = []

        for i in range(1, num_questions + 1):
            try:
                question_type = random.choice(question_types)
                question_instance = question_type()
                if fmt == 1:
                    question = question_instance.generate_full_question(i)
                    questions_data.append(question)
                else:
                    question_content, correct_answer = question_instance.generate_question_only(i)
                    questions_data.append((question_content, correct_answer))
                logging.info(f"Đã tạo thành công câu hỏi {i}")
            except Exception as e:
                logging.error(f"Lỗi tạo câu hỏi {i}: {e}")
                continue

        if not questions_data:
            print("Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)

        # Tạo file LaTeX
        if fmt == 1:
            latex_content = BaseOptimizationQuestion.create_latex_document(questions_data, "Câu hỏi Tối ưu hóa")
        else:
            latex_content = BaseOptimizationQuestion.create_latex_document_with_format(questions_data,
                                                                                       "Câu hỏi Tối ưu hóa", fmt)

        filename = "optimization_questions.tex"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)

        print(f"✅ Đã tạo thành công {filename} với {len(questions_data)} câu hỏi")
        print(f"📄 Biên dịch bằng: xelatex {filename}")
        print(f"📋 Format: {fmt} ({'đáp án ngay sau câu hỏi' if fmt == 1 else 'đáp án ở cuối'})")

    except ValueError:
        print("❌ Lỗi: Vui lòng nhập số câu hỏi hợp lệ hợp lệ")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
