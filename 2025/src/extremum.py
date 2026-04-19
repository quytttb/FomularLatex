"""
File độc lập gộp tất cả dependencies của extremum_from_tikz.py
Dạng toán nhận diện cực trị, giá trị cực trị, điểm cực trị, hoặc tính đơn điệu của hàm số dựa trên bảng biến thiên.
"""
import argparse
import logging
import random
import re
import sys
from abc import ABC, abstractmethod
from typing import Dict
from typing import List, Type, Union, Tuple, Any, Optional


# ========================================================================================
# PHẦN 1: BaseOptimizationQuestion (từ base_optimization_question.py)
# ========================================================================================


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
        """
        Tính đáp án đúng dựa trên parameters
        LƯU Ý: Không được dùng các hàm format hoặc f-string trong hàm này
        vì tính toán phải chuẩn, không làm tròn hoặc định dạng
        """
        pass

    @abstractmethod
    def generate_wrong_answers(self) -> List[str]:
        """
        Sinh 1 đáp án sai cho dạng Đúng/Sai

        Returns:
            List[str]: Danh sách chứa đúng 1 đáp án sai, ngược với đáp án đúng

        Note:
            - Phải đảm bảo trả về đúng 1 đáp án
            - Nếu đáp án đúng là "Đúng" thì trả về ["Sai"]
            - Nếu đáp án đúng là "Sai" thì trả về ["Đúng"]
        """
        pass

    @abstractmethod
    def generate_question_text(self) -> str:
        """
        Sinh đề bài câu hỏi

        Returns:
            str: Nội dung đề bài dạng LaTeX

        Note:
            - Sử dụng định dạng LaTeX cho các công thức toán học
            - Đề bài phải rõ ràng, đầy đủ thông tin
        """
        pass

    @abstractmethod
    def generate_solution(self) -> str:
        """
        Sinh lời giải chi tiết bằng LaTeX

        Returns:
            str: Lời giải chi tiết dạng LaTeX

        Note:
            1. Có thể sử dụng các hàm format hoặc f-string trong hàm này,
               vì phần này chỉ để hiển thị, không ảnh hưởng đến tính toán
            2. Không được tính toán lại đáp án trong hàm này,
               vì đáp án đã được tính toán trong calculate_answer()
            3. Lời giải phải chi tiết, dễ hiểu và có các bước logic
        """
        pass

    def generate_question(self, question_number: int = 1, include_multiple_choice: bool = True):
        """
        Tạo câu hỏi

        Args:
            question_number (int): Số thứ tự câu hỏi (mặc định: 1)
            include_multiple_choice (bool): True để tạo câu hỏi dạng mệnh đề Đúng/Sai,
                                          False để chỉ tạo đề bài và lời giải

        Returns:
            str | tuple:
                - Nếu include_multiple_choice=True: str (câu hỏi hoàn chỉnh với đáp án)
                - Nếu include_multiple_choice=False: tuple (question_content, correct_answer)

        Raises:
            ValueError: Khi include_multiple_choice=True và generate_wrong_answers()
                       không trả về đúng 1 đáp án hoặc có đáp án trùng nhau
        """
        print(f"Đang tạo câu hỏi {question_number}")

        # Sinh tham số và tính toán chung
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()  # Bây giờ là array 4 giá trị
        question_text = self.generate_question_text()  # Đã có dấu * trong từng câu hỏi
        solution = self.generate_solution()

        # Tạo nội dung cơ bản
        question_content = f"Câu {question_number}: {question_text}\n\n"

        if include_multiple_choice:
            # Tạo câu hỏi dạng mệnh đề Đúng/Sai (không hiển thị lựa chọn A/B)
            self.wrong_answers = self.generate_wrong_answers()

            # Kiểm soát số lượng đáp án sai cho dạng Đúng/Sai
            if len(self.wrong_answers) != 1:
                raise ValueError(
                    f"generate_wrong_answers() phải trả về đúng 1 đáp án sai cho dạng Đúng/Sai, nhưng đã trả về {len(self.wrong_answers)} đáp án"
                )

            # Tạo đáp án tổng thể từ array (cho việc kiểm tra)
            correct_answer_summary = "Đúng" if any(answer == "Đúng" for answer in self.correct_answer) else "Sai"
            
            # Kiểm tra đáp án có hợp lệ không
            all_answers = [correct_answer_summary] + self.wrong_answers
            if len(set(all_answers)) != 2:
                duplicates = [ans for ans in all_answers if all_answers.count(ans) > 1]
                raise ValueError(
                    f"Có đáp án trùng nhau: {duplicates}. Đáp án đúng và sai phải khác nhau."
                )

            # Không thêm dấu * ở "Câu..." nữa vì đã có trong từng câu hỏi
            question_content += f"\n\n{solution}\n\n"
            return question_content
        else:
            # Chỉ tạo đề bài và lời giải (không có đáp án trắc nghiệm)
            question_content += f"\n\n{solution}\n\n"
            # Trả về summary answer cho format 2
            correct_answer_summary = "Đúng" if any(answer == "Đúng" for answer in self.correct_answer) else "Sai"
            return question_content, correct_answer_summary


# ========================================================================================
# PHẦN 2: TikZ Figure Library (từ tikz_figure_library.py)
# ========================================================================================

def generate_monotonicity_table_type1(params):
    """
    Sinh bảng biến thiên Type 1 - Tìm khoảng nghịch biến
    Dấu: -, 0, +, 0, -, 0, +
    """
    A, B, C = params["A"], params["B"], params["C"]
    D, F, O = params["D"], params["F"], params["O"]

    return f"""\\begin{{tikzpicture}}[>=stealth, scale=1]
\t\\tkzTabInit[lgt=2,espcl=2]
\t{{$x$/1,$f''(x)$/0.8,$f'(x)$/3}}
\t{{$-\\infty$,${A}$,${B}$,${C}$,$+\\infty$}}
\t\\tkzTabLine{{,-,0,+,0,-,0,+,}}
\t\\path
\t(N12)node[shift={{(0,-0.2)}}](A){{$+\\infty$}}
\t(N23)node[shift={{(0,0.2)}}](B){{${D}$}}
\t(N32)node[shift={{(0,-1.5)}}](C){{${O}$}}
\t(N43)node[shift={{(0,0.2)}}](D){{${F}$}}
\t(N52)node[shift={{(0,-0.2)}}](E){{$+\\infty$}};
\t\\foreach \\X/\\Y in {{A/B,B/C,C/D,D/E}} \\draw[->](\\X)--(\\Y);
\\end{{tikzpicture}}"""


def generate_monotonicity_table_type2(params):
    """
    Sinh bảng biến thiên Type 2 - Tìm khoảng đồng biến
    Dấu: +, 0, -, 0, +, 0, -
    """
    A, B, C = params["A"], params["B"], params["C"]
    D, F, O = params["D"], params["F"], params["O"]

    return f"""\\begin{{tikzpicture}}[>=stealth, scale=1]
\t\\tkzTabInit[lgt=2,espcl=2]
\t{{$x$/1,$f''(x)$/0.8,$f'(x)$/3}}
\t{{$-\\infty$,${A}$,${B}$,${C}$,$+\\infty$}}
\t\\tkzTabLine{{,+,0,-,0,+,0,-,}}
\t\\path
\t(N13)node[shift={{(0,0.2)}}](A){{$+\\infty$}}
\t(N22)node[shift={{(0,-0.2)}}](B){{${D}$}}
\t(N32)node[shift={{(0,-1.5)}}](C){{${O}$}}
\t(N42)node[shift={{(0,-0.2)}}](D){{${F}$}}
\t(N53)node[shift={{(0,0.2)}}](E){{$+\\infty$}};
\t\\foreach \\X/\\Y in {{A/B,B/C,C/D,D/E}} \\draw[->](\\X)--(\\Y);
\\end{{tikzpicture}}"""


# ========================================================================================
# PHẦN 3: LaTeX Utils (từ latex_utils.py) - Chỉ lấy các hàm cần thiết
# ========================================================================================

def format_number_clean(value, precision=2):
    """
    Định dạng số với độ chính xác tùy chỉnh, loại bỏ số 0 thừa.
    
    Args:
        value: Giá trị số cần định dạng
        precision: Số chữ số thập phân (mặc định 2)
        
    Returns:
        str: Chuỗi số đã được làm sạch
        
    Examples:
        >>> format_number_clean(4.0)
        '4'
        >>> format_number_clean(3.50)
        '3,5'
    """
    try:
        fval = float(value)
        if abs(fval - round(fval)) < 1e-10:
            return str(int(round(fval)))
        else:
            formatted = f"{fval:.{precision}f}"
            while formatted.endswith('0') and '.' in formatted:
                formatted = formatted[:-1]
            if formatted.endswith('.'):
                formatted = formatted[:-1]
            if '.' in formatted:
                formatted = formatted.replace('.', '{,}')
            return formatted
    except Exception:
        return str(value)


def clean_latex_expression(expression: str) -> str:
    """
    Làm sạch biểu thức LaTeX:
    - Chuyển +- thành -
    - Loại bỏ khoảng trắng thừa
    - Đơn giản hóa các ký hiệu
    - Tối ưu hiển thị
    """
    if not expression:
        return "0"

    # Chuyển +- thành -
    expression = expression.replace("+ -", "- ")
    expression = expression.replace("+-", "-")

    # Loại bỏ khoảng trắng thừa
    expression = re.sub(r'\s+', ' ', expression.strip())

    # Đơn giản hóa các trường hợp đặc biệt
    expression = re.sub(r'\+ 0(?:\s|$)', '', expression)  # Loại bỏ +0
    expression = re.sub(r'- 0(?:\s|$)', '', expression)  # Loại bỏ -0
    expression = re.sub(r'^\+ ', '', expression)  # Loại bỏ dấu + ở đầu
    expression = re.sub(r'\b1\.0+\b', '1', expression)  # 1.000... -> 1
    expression = re.sub(r'\b0\.0+\b', '0', expression)  # 0.000... -> 0

    # Cải thiện hiển thị hệ số 1 và -1
    expression = re.sub(r'\b1x\b', 'x', expression)  # 1x -> x
    expression = re.sub(r'\b1([a-zA-Z])\b', r'\1', expression)  # 1y -> y
    expression = re.sub(r'- 1x\b', '- x', expression)  # -1x -> -x
    expression = re.sub(r'- 1([a-zA-Z])\b', r'- \1', expression)  # -1y -> -y

    # Loại bỏ khoảng trắng thừa sau khi xử lý
    expression = re.sub(r'\s+', ' ', expression.strip())

    # Nếu biểu thức rỗng hoặc chỉ có khoảng trắng, trả về 0
    if not expression or expression.isspace():
        return "0"

    return expression


def strip_latex_inline_math(ans: str) -> str:
    """
    Loại bỏ ký hiệu toán học inline khỏi chuỗi LaTeX.
    
    Args:
        ans: Chuỗi có thể chứa \\(...\\) hoặc $...$
        
    Returns:
        str: Chuỗi đã loại bỏ ký hiệu inline math
        
    Examples:
        >>> strip_latex_inline_math("\\(x^2\\)")
        'x^2'
        >>> strip_latex_inline_math("$y + 1$")
        'y + 1'
    """
    if ans.startswith("\\(") and ans.endswith("\\)"):
        return ans[2:-2].strip()
    if ans.startswith("$") and ans.endswith("$"):
        return ans[1:-1].strip()
    return ans


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


# ========================================================================================
# PHẦN 4: ExtremumFromTikzQuestion - Class chính
# ========================================================================================

class ExtremumFromTikzQuestion(BaseOptimizationQuestion):
    """
    Dạng toán nhận diện cực trị, giá trị cực trị, điểm cực trị, hoặc tính đơn điệu
    Dựa trên bảng biến thiên
    """
    # Template câu hỏi cho 2 dạng bảng biến thiên (dạng mệnh đề Đúng/Sai)
    QUESTIONS_TYPE1 = [
        "a) Hàm số nghịch biến trên khoảng ({A}; {B_hoac_C})",
        "b) Hàm số có đúng {so_cuc_tri} cực trị",
        "c) Hàm số có đúng {so_cuc_tieu} cực tiểu", 
        "d) Phương trình f'(x) = {a} có đúng {so_nghiem} nghiệm"
    ]

    QUESTIONS_TYPE2 = [
        "a) Hàm số đồng biến trên khoảng ({A}; {B_hoac_C})",
        "b) Hàm số có đúng {so_cuc_tri} cực trị",
        "c) Hàm số có đúng {so_cuc_dai} cực đại",
        "d) Phương trình f'(x) = {a} có đúng {so_nghiem} nghiệm"
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

            # Tham số a cho câu hỏi f'(x) = a
            "a": random.randint(-10, 10),

            # Giá trị phụ để làm đáp án nhiễu
            "extra_x": extra_x,
            "extra_y": extra_y,

            # Danh sách đầy đủ để dễ truy cập
            "x_extrema": [A, B, C],
            "y_extrema": [D, F, O],

            # Kiểu bảng biến thiên
            "monotonicity_type": monotonicity_type,
            
            # Template variables - sẽ được lazy load
            "B_hoac_C": random.choice([B, C]),
            # Các biến này sẽ được tính trong _ensure_template_values()
            "so_cuc_tri": None,
            "so_cuc_tieu": None, 
            "so_cuc_dai": None,
            "so_nghiem": None
        }

    def _ensure_template_values(self):
        """
        Lazy loading cho template variables - chỉ tính khi cần thiết
        Logic: Random chọn giữa đáp án đúng và đáp án sai cho mỗi template variable
        """
        if self.parameters["so_cuc_tri"] is not None:
            return  # Đã được tính rồi
        
        # Tính giá trị thực tế cho từng template variable
        p = self.parameters
        A, B, C = p["A"], p["B"], p["C"]
        D, F, O = p["D"], p["F"], p["O"]
        monotonicity_type = p["monotonicity_type"]
        
        # 1. so_cuc_tri (số cực trị) - luôn là 2 cho cả 2 type
        correct_so_cuc_tri = "4"
        wrong_so_cuc_tri = random.choice(["0", "1", "3", "5"])
        so_cuc_tri = random.choice([correct_so_cuc_tri, wrong_so_cuc_tri])
        
        # 2. so_cuc_tieu (số cực tiểu) - type1 có 2 cực tiểu
        if monotonicity_type == "monotonicity_type1":
            correct_so_cuc_tieu = "2"
            wrong_so_cuc_tieu = random.choice(["0", "1", "3", "4"])
            so_cuc_tieu = random.choice([correct_so_cuc_tieu, wrong_so_cuc_tieu])
        else:
            so_cuc_tieu = "1"  # Default value
            
        # 3. so_cuc_dai (số cực đại) - type2 có 2 cực đại
        if monotonicity_type == "monotonicity_type2":
            correct_so_cuc_dai = "2"
            wrong_so_cuc_dai = random.choice(["0", "1", "3", "4"])
            so_cuc_dai = random.choice([correct_so_cuc_dai, wrong_so_cuc_dai])
        else:
            so_cuc_dai = "1"  # Default value
            
        # 4. so_nghiem (số nghiệm của f'(x) = a) - tính dựa trên giá trị a
        a = p["a"]
        
        # Tính số nghiệm thực tế
        if monotonicity_type == "monotonicity_type1":
            # Logic cho type1
            if D > F:
                if a < F:
                    correct_so_nghiem = "0"
                elif a == F:
                    correct_so_nghiem = "1"
                elif F < a < D:
                    correct_so_nghiem = "2"
                elif a == D or a == O:
                    correct_so_nghiem = "3"
                elif D < a < O:
                    correct_so_nghiem = "4"
                elif a > O:
                    correct_so_nghiem = "2"
                else:
                    correct_so_nghiem = "3"
            else:  # D <= F
                if a < D:
                    correct_so_nghiem = "0"
                elif a == D:
                    correct_so_nghiem = "1"
                elif D < a < F:
                    correct_so_nghiem = "2"
                elif a == F or a == O:
                    correct_so_nghiem = "3"
                elif F < a < O:
                    correct_so_nghiem = "4"
                elif a > O:
                    correct_so_nghiem = "2"
                else:
                    correct_so_nghiem = "3"
        else:  # monotonicity_type2
            # Logic cho type2
            if D > F:
                if a > D:
                    correct_so_nghiem = "0"
                elif a == D:
                    correct_so_nghiem = "1"
                elif a < O or F < a < D:
                    correct_so_nghiem = "2"
                elif a == O or a == F:
                    correct_so_nghiem = "3"
                elif O < a < F:
                    correct_so_nghiem = "4"
                else:
                    correct_so_nghiem = "2"
            else:  # D <= F
                if a > F:
                    correct_so_nghiem = "0"
                elif a == F:
                    correct_so_nghiem = "1"
                elif a < O or D < a < F:
                    correct_so_nghiem = "2"
                elif a == O or a == D:
                    correct_so_nghiem = "3"
                elif O < a < D:
                    correct_so_nghiem = "4"
                else:
                    correct_so_nghiem = "2"
        
        # Chọn random giữa đáp án đúng và sai cho so_nghiem
        wrong_so_nghiem = random.choice(["5", "6", "7", "8", "9"])
        so_nghiem = random.choice([correct_so_nghiem, wrong_so_nghiem])
        
        # Cập nhật parameters
        self.parameters.update({
            "so_cuc_tri": so_cuc_tri,
            "so_cuc_tieu": so_cuc_tieu,
            "so_cuc_dai": so_cuc_dai,
            "so_nghiem": so_nghiem
        })

    def generate_question_text(self) -> str:
        """Sinh đề bài bằng LaTeX với bảng biến thiên monotonicity và tất cả 4 câu hỏi"""
        # Đảm bảo parameters đã được khởi tạo
        if not self.parameters:
            self.parameters = self.generate_parameters()

        # Lazy load template values
        self._ensure_template_values()

        p = self.parameters

        # Chọn hàm sinh bảng biến thiên phù hợp
        if p["monotonicity_type"] == "monotonicity_type1":
            figure = generate_monotonicity_table_type1(p)
            intro = "Cho hàm số \\(y=f(x)\\) có bảng biến thiên \\(f'(x)\\) như dưới đây:"
            questions_template = self.QUESTIONS_TYPE1
        else:  # monotonicity_type2
            figure = generate_monotonicity_table_type2(p)
            intro = "Cho hàm số \\(y=f(x)\\) có bảng biến thiên \\(f'(x)\\) như dưới đây:"
            questions_template = self.QUESTIONS_TYPE2

        # Tạo tất cả 4 câu hỏi với dấu * cho câu đúng
        questions_list = []
        answer_results = self.calculate_answer()  # Sẽ trả về array 4 giá trị đúng/sai
        
        for i, question_template in enumerate(questions_template):
            # Thay thế template variables
            question = question_template.format(**p)
            
            # Thêm dấu * nếu câu hỏi đúng
            if answer_results[i] == "Đúng":
                question = f"*{question}"
            
            questions_list.append(question)

        # Ghép tất cả câu hỏi với xuống dòng
        all_questions = "\n\n".join(questions_list)

        return f"""{intro}

{figure}

Mệnh đề nào sau đây đúng?

{all_questions}"""

    def calculate_answer(self) -> List[str]:
        """
        Tính đáp án đúng cho tất cả 4 câu hỏi - trả về array 4 giá trị Đúng/Sai
        
        Returns:
            List[str]: Array 4 giá trị ["Đúng"/"Sai", "Đúng"/"Sai", "Đúng"/"Sai", "Đúng"/"Sai"]
                      tương ứng với 4 câu hỏi trong QUESTIONS_TYPE
        """
        # Đảm bảo parameters đã được khởi tạo
        if not self.parameters:
            self.parameters = self.generate_parameters()

        # Đảm bảo template values đã được tính
        self._ensure_template_values()

        p = self.parameters
        A, B, C = p["A"], p["B"], p["C"]  # Điểm nghiệm của f'(x) = 0
        D, F, O = p["D"], p["F"], p["O"]  # Giá trị của f(x)
        monotonicity_type = p["monotonicity_type"]
        
        results = []
        
        if monotonicity_type == "monotonicity_type1":
            # TYPE1: 4 câu hỏi theo thứ tự
            # 1. "Hàm số nghịch biến trên khoảng ({A}; {B_hoac_C})"
            B_hoac_C = p["B_hoac_C"]
            if B_hoac_C == B or B_hoac_C == C:
                results.append("Đúng")  # Type1 nghịch biến trên (A,B) và (B,C)
            else:
                results.append("Sai")
            
            # 2. "Hàm số có đúng {so_cuc_tri} cực trị"
            template_value = p["so_cuc_tri"]
            actual_value = "4"  # Type1 có 4 cực trị
            results.append("Đúng" if template_value == actual_value else "Sai")
            
            # 3. "Hàm số có đúng {so_cuc_tieu} cực tiểu"
            template_value = p["so_cuc_tieu"]
            actual_value = "2"  # Type1 có 2 cực tiểu
            results.append("Đúng" if template_value == actual_value else "Sai")
            
            # 4. "Phương trình f'(x) = {a} có đúng {so_nghiem} nghiệm"
            template_value = p["so_nghiem"]
            a = p["a"]
            
            # Tính số nghiệm thực tế cho type1
            if D > F:
                if a < F:
                    actual_value = "0"
                elif a == F:
                    actual_value = "1"
                elif F < a < D:
                    actual_value = "2"
                elif a == D or a == O:
                    actual_value = "3"
                elif D < a < O:
                    actual_value = "4"
                elif a > O:
                    actual_value = "2"
                else:
                    actual_value = "3"
            else:  # D <= F
                if a < D:
                    actual_value = "0"
                elif a == D:
                    actual_value = "1"
                elif D < a < F:
                    actual_value = "2"
                elif a == F or a == O:
                    actual_value = "3"
                elif F < a < O:
                    actual_value = "4"
                elif a > O:
                    actual_value = "2"
                else:
                    actual_value = "3"
            
            results.append("Đúng" if template_value == actual_value else "Sai")
            
        else:  # monotonicity_type2
            # TYPE2: 4 câu hỏi theo thứ tự
            # 1. "Hàm số đồng biến trên khoảng ({A}; {B_hoac_C})"
            B_hoac_C = p["B_hoac_C"]
            if B_hoac_C == B or B_hoac_C == C:
                results.append("Đúng")  # Type2 đồng biến trên (A,B) và (B,C)
            else:
                results.append("Sai")
            
            # 2. "Hàm số có đúng {so_cuc_tri} cực trị"
            template_value = p["so_cuc_tri"]
            actual_value = "4"  # Type2 có 4 cực trị
            results.append("Đúng" if template_value == actual_value else "Sai")
            
            # 3. "Hàm số có đúng {so_cuc_dai} cực đại"
            template_value = p["so_cuc_dai"]
            actual_value = "2"  # Type2 có 2 cực đại
            results.append("Đúng" if template_value == actual_value else "Sai")
            
            # 4. "Phương trình f'(x) = {a} có đúng {so_nghiem} nghiệm"
            template_value = p["so_nghiem"]
            a = p["a"]
            
            # Tính số nghiệm thực tế cho type2
            if D > F:
                if a > D:
                    actual_value = "0"
                elif a == D:
                    actual_value = "1"
                elif a < O or F < a < D:
                    actual_value = "2"
                elif a == O or a == F:
                    actual_value = "3"
                elif O < a < F:
                    actual_value = "4"
                else:
                    actual_value = "2"
            else:  # D <= F
                if a > F:
                    actual_value = "0"
                elif a == F:
                    actual_value = "1"
                elif a < O or D < a < F:
                    actual_value = "2"
                elif a == O or a == D:
                    actual_value = "3"
                elif O < a < D:
                    actual_value = "4"
                else:
                    actual_value = "2"
            
            results.append("Đúng" if template_value == actual_value else "Sai")
        
        return results

    def generate_wrong_answers(self) -> List[str]:
        """
        Sinh đáp án sai (nhiễu) cho dạng True/False
        
        Returns:
            List[str]: Danh sách chứa đúng 1 đáp án sai tổng thể
        """
        # Lấy đáp án đúng (là array 4 giá trị)
        correct_answers = self.calculate_answer()
        
        # Tạo đáp án sai tổng thể (ngược lại với đáp án đúng)
        # Ví dụ: nếu có ít nhất 1 câu đúng -> đáp án tổng thể là "Đúng"
        #        nếu tất cả câu đều sai -> đáp án tổng thể là "Sai"
        has_correct = any(answer == "Đúng" for answer in correct_answers)
        
        if has_correct:
            return ["Sai"]  # Nếu có câu đúng thì đáp án sai tổng thể là "Sai"
        else:
            return ["Đúng"]  # Nếu tất cả đều sai thì đáp án sai tổng thể là "Đúng"

    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết dựa trên bảng biến thiên và template câu hỏi mới"""
        return ""

    # Alias để tương thích với naming convention


ExtremumFromTikz = ExtremumFromTikzQuestion


# ========================================================================================
# PHẦN 5: Hàm main để chạy độc lập
# ========================================================================================

class QuestionManager:
    """Manager đơn giản để sinh câu hỏi"""

    def __init__(self, question_types: Optional[List[Type]] = None):
        self.question_types = question_types or [ExtremumFromTikzQuestion]
        self.failed_count = 0

    def generate_questions(self, num_questions: int, output_format: int, verbose: bool = False) -> List[Union[str, Tuple[str, str]]]:
        """Sinh danh sách câu hỏi"""
        if num_questions <= 0:
            raise ValueError("Số câu hỏi phải lớn hơn 0")
        if output_format not in [1, 2]:
            raise ValueError("Format chỉ có thể là 1 hoặc 2")

        questions_data = []
        if verbose:
            print(f"📋 Bắt đầu sinh {num_questions} câu hỏi")

        for i in range(1, num_questions + 1):
            try:
                question_type = random.choice(self.question_types)
                question_instance = question_type()
                
                if output_format == 1:
                    result = question_instance.generate_question(i, include_multiple_choice=True)
                else:
                    result = question_instance.generate_question(i, include_multiple_choice=False)
                
                questions_data.append(result)
                if verbose:
                    print(f"✅ Đã tạo thành công câu hỏi {i}")
                    
            except Exception as e:
                print(f"❌ Lỗi tạo câu hỏi {i}: {e}")
                self.failed_count += 1

        if self.failed_count > 0:
            print(f"⚠️  Có {self.failed_count} câu hỏi không tạo được")

        if not questions_data:
            raise ValueError("Không thể tạo được câu hỏi nào")

        return questions_data


class LaTeXTemplate:
    """Template LaTeX đơn giản"""
    DOCUMENT_HEADER = r"""\documentclass[a4paper,12pt]{{article}}
\usepackage{{amsmath}}
\usepackage{{amsfonts}}
\usepackage{{amssymb}}
\usepackage{{geometry}}
\geometry{{a4paper, margin=1in}}
\usepackage{{polyglossia}}
\setmainlanguage{{vietnamese}}
\setmainfont{{Times New Roman}}
\usepackage{{tikz}}
\usepackage{{tkz-tab}}
\usepackage{{tkz-euclide}}
\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\begin{{document}}
\title{{{title}}}
\author{{{author}}}
\maketitle

"""

    DOCUMENT_FOOTER = r"""
\end{document}"""

    ANSWER_SECTION_HEADER = r"""
\section*{Đáp án}"""


class LaTeXDocumentBuilder:
    """Builder tạo document LaTeX"""

    def __init__(self):
        self.template = LaTeXTemplate()

    def build_document(self, questions_data: List[Any], title: str, output_format: int, author: str = "dev") -> str:
        """Tạo document LaTeX hoàn chỉnh"""
        if not questions_data:
            raise ValueError("Danh sách câu hỏi không được rỗng")
        if not title.strip():
            raise ValueError("Tiêu đề không được rỗng")

        # Tạo header
        latex_content = self.template.DOCUMENT_HEADER.format(title=title, author=author)

        # Xử lý content theo format
        if output_format == 1:
            # Format 1: đáp án ngay sau câu hỏi
            if not all(isinstance(q, str) for q in questions_data):
                raise ValueError("Với format 1, tất cả items phải là string")
            latex_content += "\n\n".join(questions_data)
        else:
            # Format 2: đáp án ở cuối
            if not all(isinstance(q, tuple) and len(q) == 2 for q in questions_data):
                raise ValueError("Với format 2, tất cả items phải là tuple (content, answer)")
            
            questions = [q[0] for q in questions_data]
            answers = [q[1] for q in questions_data]
            
            latex_content += "\n\n".join(questions)
            latex_content += self.template.ANSWER_SECTION_HEADER
            
            for idx, answer in enumerate(answers, 1):
                latex_content += f"\n\\textbf{{Câu {idx}}}: {answer}"

        # Thêm footer
        latex_content += self.template.DOCUMENT_FOOTER
        return latex_content


# Hằng số cấu hình mặc định
DEFAULT_NUM_QUESTIONS = 3
DEFAULT_FORMAT = 1
DEFAULT_FILENAME = "optimization_questions.tex"
DEFAULT_TITLE = "Câu hỏi Tối ưu hóa"


def parse_arguments() -> argparse.Namespace:
    """Xử lý tham số dòng lệnh"""
    parser = argparse.ArgumentParser(
        description="Generator câu hỏi tối ưu hóa với hỗ trợ 2 format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python3 main_runner.py                    # Tạo 3 câu hỏi, format 1
  python3 main_runner.py 5                  # Tạo 5 câu hỏi, format 1
  python3 main_runner.py 5 2                # Tạo 5 câu hỏi, format 2
  python3 main_runner.py -n 10 -f 2 -o test.tex  # Tùy chỉnh đầy đủ
        """
    )

    parser.add_argument('num_questions', nargs='?', type=int, default=DEFAULT_NUM_QUESTIONS,
                        help=f'Số câu hỏi cần tạo (mặc định: {DEFAULT_NUM_QUESTIONS})')
    parser.add_argument('format', nargs='?', type=int, choices=[1, 2], default=DEFAULT_FORMAT,
                        help=f'Format: 1=đáp án ngay sau câu hỏi, 2=đáp án ở cuối (mặc định: {DEFAULT_FORMAT})')
    parser.add_argument('-n', '--num-questions', type=int, dest='num_questions_override',
                        help='Số câu hỏi cần tạo (ghi đè positional argument)')
    parser.add_argument('-f', '--format', type=int, choices=[1, 2], dest='format_override',
                        help='Format output (ghi đè positional argument)')
    parser.add_argument('-o', '--output', type=str, default=DEFAULT_FILENAME,
                        help=f'Tên file output (mặc định: {DEFAULT_FILENAME})')
    parser.add_argument('-t', '--title', type=str, default=DEFAULT_TITLE,
                        help=f'Tiêu đề document (mặc định: "{DEFAULT_TITLE}")')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Hiển thị thông tin chi tiết')

    args = parser.parse_args()

    # Override positional args with named args if provided
    if args.num_questions_override is not None:
        args.num_questions = args.num_questions_override
    if args.format_override is not None:
        args.format = args.format_override

    # Validate
    if args.num_questions <= 0:
        parser.error("Số câu hỏi phải lớn hơn 0")

    return args


def generate_questions(num_questions: int, output_format: int, verbose: bool = False) -> List[Any]:
    """Sinh danh sách câu hỏi tối ưu hóa"""
    manager = QuestionManager()
    return manager.generate_questions(num_questions, output_format, verbose)


def create_latex_file(questions_data: List, filename: str, title: str, output_format: int) -> None:
    """Tạo file LaTeX chứa danh sách câu hỏi"""
    try:
        latex_builder = LaTeXDocumentBuilder()
        latex_content = latex_builder.build_document(questions_data, title, output_format)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)
    except IOError as e:
        raise IOError(f"Không thể ghi file {filename}: {e}")


def main() -> None:
    """Hàm main: điều phối toàn bộ quá trình sinh câu hỏi tối ưu hóa và xuất ra file LaTeX"""
    try:
        # Parse arguments
        args = parse_arguments()

        # Setup logging
        if args.verbose:
            logging.basicConfig(level=logging.INFO)

        # Generate questions
        questions_data = generate_questions(args.num_questions, args.format, args.verbose)

        if not questions_data:
            print("❌ Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)

        # Create LaTeX file
        create_latex_file(questions_data, args.output, args.title, args.format)

        # Success messages
        print(f"✅ Đã tạo thành công {args.output} với {len(questions_data)} câu hỏi")
        print(f"📄 Biên dịch bằng: xelatex {args.output}")
        print(f"📋 Format: {args.format} ({'đáp án ngay sau câu hỏi' if args.format == 1 else 'đáp án ở cuối'})")

    except KeyboardInterrupt:
        print("\n❌ Đã hủy bởi người dùng")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Lỗi tham số: {e}")
        sys.exit(1)
    except IOError as e:
        print(f"❌ Lỗi file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

