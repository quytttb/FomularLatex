#!/usr/bin/env python3
"""
MERGED OPTIMIZATION QUESTIONS GENERATOR
Combined from multiple Python files in base_template
"""

#================================================================================
# LATEX_UTILS.PY
#================================================================================

"""
Các hàm tiện ích LaTeX cho hệ thống sinh câu hỏi toán tối ưu hóa
Tách từ math_template.py - PHẦN 1
"""
import math
from fractions import Fraction
from typing import Union

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


#================================================================================
# TIKZ_FIGURE_LIBRARY.PY
#================================================================================

"""
Thư viện hình vẽ TikZ cho hệ thống sinh câu hỏi toán tối ưu hóa
Tách từ math_template.py - PHẦN 2
"""
    # ===== THÊM TIKZ FIGURES MỚI TẠI ĐÂY =====
    # @staticmethod
    # def get_your_new_figure():
    #     """Mô tả hình vẽ của bạn"""
    #     return """
    #     \\begin{tikzpicture}
    #         % Code TikZ của bạn ở đây
    #     \\end{tikzpicture}
    #     """

def generate_tkztabinit_latex(params):
    """
    Sinh LaTeX cho bảng biến thiên tkzTabInit với các tham số truyền vào.
    params: dict chứa A, B, C, D, E, F (số nguyên) và pattern (dạng bảng biến thiên)
    """
    A, B, C = params["A"], params["B"], params["C"]  # Điểm cực trị
    D, E, F = params["D"], params["E"], params["F"]  # Giá trị cực trị
    pattern = params.get("pattern", "type1")  # Mặc định là dạng 1
    
    # Tạo các nhãn cho trục x (điểm cực trị)
    x_labels = ["\\(-\\infty\\)", f"\\( {A} \\)", f"\\( {B} \\)", f"\\( {C} \\)", "\\(+\\infty\\)"]
    x_labels_str = ",".join(x_labels)
    
    # Chọn dạng bảng biến thiên theo pattern
    if pattern == "type1":
        # Dạng 1: -, 0, +, 0, -, 0, + (Cực đại - Cực tiểu - Cực đại)
        sign_line = ",".join(["-", "0", "+", "0", "-", "0", "+"])
        # D và F là cực đại (vị trí cao), E là cực tiểu (vị trí thấp)
        node_positions = f"""
(N12)node[shift={{(0,-0.2)}}](A){{\\(+\\infty\\)}}
(N23)node[shift={{(0,0.2)}}](B){{\\({D}\\)}}
(N32)node[shift={{(0,-1.5)}}](C){{\\({E}\\)}}
(N43)node[shift={{(0,0.2)}}](D){{\\({F}\\)}}
(N52)node[shift={{(0,-0.2)}}](E){{\\(+\\infty\\)}}"""
    else:  # pattern == "type2"
        # Dạng 2: +, 0, -, 0, +, 0, - (Cực đại - Cực tiểu - Cực đại nhưng xu hướng ngược)
        sign_line = ",".join(["+", "0", "-", "0", "+", "0", "-"])
        # Điều chỉnh vị trí node để phù hợp với dạng 2
        node_positions = f"""
(N13)node[shift={{(0,0.2)}}](A){{\\(+\\infty\\)}}
(N22)node[shift={{(0,-0.2)}}](B){{\\({D}\\)}}
(N32)node[shift={{(0,-1.5)}}](C){{\\({E}\\)}}
(N42)node[shift={{(0,-0.2)}}](D){{\\({F}\\)}}
(N53)node[shift={{(0,0.2)}}](E){{\\(+\\infty\\)}}"""
    
    return f"""
\\begin{{tikzpicture}}[>=stealth, scale=1]
\\tkzTabInit[lgt=2,espcl=2]
{{\\(x\\)/1,\\(f'(x)\\)/0.8,\\(f(x)\\)/3}}
{{{x_labels_str}}}
\\tkzTabLine{{{sign_line}}}
\\path{node_positions};
\\foreach\\X/\\Y in{{A/B,B/C,C/D,D/E}}\\draw[->](\\X)--(\\Y);
\\end{{tikzpicture}}
"""

def generate_cubic_type1_latex(params):
    """
    Sinh LaTeX cho đồ thị hàm bậc 3 loại 1 (như Câu 3 trong 1200k.tex)
    Cực đại trước, cực tiểu sau: x^3 - 3x - 1
    params: dict chứa A, B (điểm cực trị), D, E (giá trị cực trị), m (offset)
    Vị trí trên hình vẽ: A âm (cực đại), B+m dương (cực tiểu), D dương (y cực đại), E âm (y cực tiểu)
    """
    A = params["A"]  # x của cực đại (âm)
    B = params["B"]  # x của cực tiểu (dương) 
    D = params["D"]  # y của cực đại (dương)
    E = params["E"]  # y của cực tiểu (âm)
    m = params.get("m", 0)  # offset cho điểm B
    B_offset = B + m  # tính giá trị cụ thể
    
    return f"""
\\begin{{tikzpicture}}[line join=round, line cap=round,>=stealth,scale=1]
\\tikzset{{label style/.style={{font=\\footnotesize}}}}
\\draw[->] (-2.1,0)--(2.5,0) node[below right] {{\\(x\\)}};
\\draw[->] (0,-3.1)--(0,2.1) node[below left] {{\\(y\\)}};
\\draw (0,0) node [below right] {{\\(O\\)}}circle(1.5pt);

% Đánh dấu các điểm cực trị - VỊ TRÍ TRÊN HÌNH VẼ CỐ ĐỊNH
\\draw[dashed,thin](-1,0)--(-1,1)--(0,1);
\\draw[dashed,thin](1,0)--(1,-3)--(0,-3);
\\draw (1,0) node[above]{{\\( {B_offset} \\)}}; 
\\draw (-1,0) node[below]{{\\( {A} \\)}};
\\draw (0,-3) node[left]{{\\( {E} \\)}};
\\draw (0,1) node[right]{{\\( {D} \\)}};

% Vẽ đường cong hàm số bậc 3 loại 1
\\begin{{scope}}
\\clip (-2,-3) rectangle (2,2);
\\draw[samples=200,domain=-2:2,smooth,variable=\\x] plot (\\x,{{(\\x)^3-3*(\\x)-1}});
\\end{{scope}}
\\end{{tikzpicture}}
"""

def generate_cubic_type2_latex(params):
    """
    Sinh LaTeX cho đồ thị hàm bậc 3 loại 2 (như Câu 4 trong 1200k.tex)
    Cực tiểu trước, cực đại sau: -x^3 + 3x - 1
    params: dict chứa A, B (điểm cực trị), D, E (giá trị cực trị), m (offset)
    Vị trí trên hình vẽ: A âm (cực tiểu), B+m dương (cực đại), D âm (y cực tiểu), E dương (y cực đại)
    """
    A = params["A"]  # x của cực tiểu (âm)
    B = params["B"]  # x của cực đại (dương)
    D = params["D"]  # y của cực tiểu (âm)  
    E = params["E"]  # y của cực đại (dương)
    m = params.get("m", 0)  # offset cho điểm B
    B_offset = B + m  # tính giá trị cụ thể
    
    return f"""
\\begin{{tikzpicture}}[scale=1, font=\\footnotesize, line join=round, line cap=round, >=stealth]
\\draw[->] (-2.5,0)--(3.5,0) node[below] {{\\(x\\)}};
\\draw[->] (0,-3.5)--(0,2.5) node[left] {{\\(y\\)}};
\\draw[fill=black] (0,0) circle (1pt) node[below left=-2pt] {{\\(O\\)}};

% Đánh dấu các điểm cực trị - VỊ TRÍ TRÊN HÌNH VẼ CỐ ĐỊNH
\\draw[fill=black] (-1,0) circle (1pt) node[below] {{\\({A}\\)}};
\\draw[fill=black] (1,0) circle (1pt) node[below] {{\\({B_offset}\\)}};
\\draw[fill=black] (0,1) circle (1pt) node[above left] {{\\({E}\\)}};
\\draw[fill=black] (0,-3) circle (1pt) node[below left] {{\\({D}\\)}};

% Đường kẻ phụ - VỊ TRÍ TRÊN HÌNH VẼ CỐ ĐỊNH
\\draw[dashed] (-1,0)--(-1,-3)--(2,-3)--(2,0);
\\draw[dashed] (-2,0)--(-2,1)--(1,1)--(1,0);

% Vẽ đường cong hàm số bậc 3 loại 2 (ngược)
\\begin{{scope}}
\\clip (-2.5,-3.5) rectangle (3.5,2.5);
\\draw[smooth,samples=100,domain=-2.5:3.5] plot(\\x,{{-1*(\\x)^3+3*(\\x)-1}});
\\end{{scope}}
\\end{{tikzpicture}}
"""

def generate_quartic_latex(params):
    """
    Sinh LaTeX cho đồ thị hàm bậc 4 (như Câu 5 trong 1200k.tex)
    Cực đại giữa, 2 cực tiểu hai bên: x^4 - 2x^2 - 2
    params: dict chứa A, C (điểm cực tiểu), D, E (giá trị cực trị)
    Vị trí trên hình vẽ: A âm (cực tiểu trái), C dương (cực tiểu phải), D âm (y cực tiểu), E âm (y cực đại)
    """
    A = params["A"]  # x của cực tiểu trái (âm)
    C = params["C"]  # x của cực tiểu phải (dương) 
    D = params["D"]  # y của cực tiểu (âm)
    E = params["E"]  # y của cực đại (âm nhưng cao hơn D)
    
    return f"""
\\begin{{tikzpicture}}[scale=1, font=\\footnotesize, line join=round, line cap=round, >=stealth]
\\draw[->] (-3,0)--(3,0) node[below] {{\\(x\\)}};
\\draw[->] (0,-3.5)--(0,2.5) node[left] {{\\(y\\)}};
\\draw[fill=black] (0,0) circle (1pt) node[above left=-2pt] {{\\(O\\)}};

% Đánh dấu các điểm cực trị - VỊ TRÍ TRÊN HÌNH VẼ CỐ ĐỊNH
\\draw[fill=black] (-1,0) circle (1pt) node[below] {{\\({A}\\)}};
\\draw[fill=black] (1,0) circle (1pt) node[below] {{\\({C}\\)}};
\\draw[fill=black] (0,-2) circle (1pt) node[above left] {{\\({E}\\)}};
\\draw[fill=black] (0,-3) circle (1pt);
\\draw[fill=black] (0,-3.12) node[above left] {{\\({D}\\)}};

% Đường kẻ phụ - VỊ TRÍ TRÊN HÌNH VẼ CỐ ĐỊNH
\\draw[dashed] (-1,0)--(-1,-3)--(1,-3)--(1,0);

% Vẽ đường cong hàm số bậc 4
\\begin{{scope}}
\\clip (-2,-3.5) rectangle (2,3.25);
\\draw[smooth,samples=100,domain=-1.8:1.8] plot(\\x,{{(\\x)^4-2*(\\x)^2-2}});
\\end{{scope}}
\\end{{tikzpicture}}
"""


#================================================================================
# BASE_OPTIMIZATION_QUESTION.PY
#================================================================================

"""
Lớp cơ sở cho các dạng bài toán tối ưu hóa
Tách từ math_template.py - PHẦN 3
"""
import random
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any


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



    def generate_full_question(self, question_number: int = 1) -> str:
        """Tạo câu hỏi hoàn chỉnh với 4 đáp án A/B/C/D"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        self.wrong_answers = self.generate_wrong_answers()
        question_text = self.generate_question_text()
        all_answers = [self.correct_answer] + self.wrong_answers
        random.shuffle(all_answers)
        correct_index = all_answers.index(self.correct_answer)
        question_content = f"Câu {question_number}: {question_text}\n\n"
        for j, ans in enumerate(all_answers):
            letter = chr(65 + j)
            marker = "*" if j == correct_index else ""
            question_content += f"{marker}{letter}. {ans}\n\n"
        return question_content

    def generate_question_only(self, question_number: int = 1) -> tuple:
        """Tạo câu hỏi chỉ có đề bài"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        question_text = self.generate_question_text()
        question_content = f"Câu {question_number}: {question_text}\n\n"
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
        """Tạo document LaTeX với format cụ thể"""
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{fontspec}}
\\usepackage{{tikz}}
\\usepackage{{tkz-tab}}
\\usepackage{{tkz-euclide}}
\\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\\begin{{document}}
\\title{{{title}}}
\\maketitle

"""
        for question_data in questions_data:
            latex_content += f"{question_data}\n\n"
        latex_content += "\n\\end{document}"
        return latex_content


# Danh sách các dạng toán có sẵn
def get_available_question_types():
    """Trả về danh sách các dạng toán có sẵn"""
    return [
        ExtremumFromTikzQuestion,
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


#================================================================================
# EXTREMUM_FROM_TIKZ.PY
#================================================================================

"""
Dạng toán nhận diện cực trị, giá trị cực trị, điểm cực trị, hoặc tính đơn điệu của hàm số dựa trên bảng biến thiên (tkzTabInit) hoặc đồ thị (tikzpicture).
Tham khảo format từ production_optimization.py
"""


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

 

# Alias để tương thích với naming convention
ExtremumFromTikz = ExtremumFromTikzQuestion

#================================================================================
# MAIN_RUNNER.PY
#================================================================================

#!/usr/bin/env python3
"""
MAIN FUNCTION để chạy hệ thống tối ưu hóa
"""

import random
import sys
import logging


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
            latex_content = BaseOptimizationQuestion.create_latex_document_with_format(questions_data, "Câu hỏi Tối ưu hóa", fmt)

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

