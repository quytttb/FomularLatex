"""
Dạng bài toán tối ưu hóa với đạo hàm
"""
import math
import random
import logging
from fractions import Fraction
from typing import Union


def format_fraction_latex(num, denom):
    """Format a fraction for LaTeX display theo mẫu asymptote_mc.py"""
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
    """Format coefficient with proper signs and variable."""
    if coeff == 0:
        return ""

    # Handle Fraction coefficients
    if isinstance(coeff, Fraction):
        num, denom = coeff.numerator, coeff.denominator
    else:
        num, denom = int(coeff), 1

    # Format the coefficient part
    if denom == 1:
        coeff_str = str(abs(num)) if abs(num) != 1 or power == 0 else ""
    else:
        coeff_str = f"\\frac{{{abs(num)}}}{{{denom}}}"

    # Handle variable and power
    if power == 0:
        var_str = coeff_str if coeff_str else "1"
    elif power == 1:
        var_str = f"{coeff_str}{var}" if coeff_str else var
    else:
        var_str = f"{coeff_str}{var}^{{{power}}}" if coeff_str else f"{var}^{{{power}}}"

    # Handle signs
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
    """Format polynomial coefficients as LaTeX string."""
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


def escape_latex(text: str) -> str:
    """Escape các ký tự đặc biệt trong LaTeX"""
    replacements = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '^': '\\textasciicircum{}',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '\\': '\\textbackslash{}'
    }

    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    return text


def format_fraction(numerator: int, denominator: int) -> str:
    """Format phân số thành LaTeX - đơn giản hóa"""
    if denominator == 1:
        return f"{numerator}"
    else:
        return f"\\frac{{{numerator}}}{{{denominator}}}"


def format_money(amount: float, currency: str = "đồng") -> str:
    """Format tiền tệ thành chuỗi LaTeX tốt hơn"""
    if amount >= 1000000000:
        if amount % 1000000000 == 0:
            value = f"{int(amount // 1000000000)} tỷ"
        else:
            # Sử dụng format_number_clean để tránh làm tròn sai
            value = f"{format_number_clean(amount / 1000000000)} tỷ"
    elif amount >= 1000000:
        if amount % 1000000 == 0:
            value = f"{int(amount // 1000000)} triệu"
        else:
            # Sử dụng format_number_clean để tránh làm tròn sai
            value = f"{format_number_clean(amount / 1000000)} triệu"
    elif amount >= 1000:
        formatted = f"{int(amount):,}".replace(",", ".")
        value = formatted
    else:
        value = f"{int(amount)}"

    # Only add currency if not empty
    if currency.strip():
        return f"{value} {currency}"
    else:
        return value


def format_scientific(num: float, precision: int = 3) -> str:
    """Format số khoa học thành LaTeX"""
    if abs(num) < 1e-10:
        return "0"

    exponent = int(math.floor(math.log10(abs(num))))
    mantissa = num / (10 ** exponent)

    if exponent == 0:
        return f"{mantissa:.{precision}f}".rstrip('0').rstrip('.')
    else:
        return f"{mantissa:.{precision}f} \\times 10^{{{exponent}}}"


def format_sqrt(number: Union[int, float]) -> str:
    """Format căn bậc hai thành LaTeX"""
    if number == int(number) and int(number) >= 0:
        sqrt_val = math.sqrt(number)
        if sqrt_val == int(sqrt_val):
            return f"{int(sqrt_val)}"
        else:
            return f"\\sqrt{{{int(number)}}}"
    else:
        return f"\\sqrt{{{number}}}"


def format_polynomial_derivative(coefficients: list, variable: str = "x") -> str:
    """Format đạo hàm của đa thức thành LaTeX"""
    if len(coefficients) <= 1:
        return "0"

    derivative_coeffs = []
    for i in range(1, len(coefficients)):
        derivative_coeffs.append(coefficients[i] * i)

    terms = []
    degree = len(derivative_coeffs) - 1

    for i, coeff in enumerate(reversed(derivative_coeffs)):
        power = degree - i

        if coeff == 0:
            continue

        if power == 0:
            terms.append(f"{coeff}")
        elif power == 1:
            if coeff == 1:
                terms.append(f"{variable}")
            elif coeff == -1:
                terms.append(f"-{variable}")
            else:
                terms.append(f"{coeff}{variable}")
        else:
            if coeff == 1:
                terms.append(f"{variable}^{{{power}}}")
            elif coeff == -1:
                terms.append(f"-{variable}^{{{power}}}")
            else:
                terms.append(f"{coeff}{variable}^{{{power}}}")

    if not terms:
        return "0"

    result = terms[0]
    for term in terms[1:]:
        if term.startswith('-'):
            result += term
        else:
            result += f"+{term}"

    return result


def create_table_of_variations(critical_points: list, intervals: list, function_name: str = "f") -> str:
    """Tạo bảng biến thiên bằng TikZ cải thiện"""
    # Tạo header với các điểm tới hạn
    points_str = ",".join([f"{point}" for point in critical_points])

    # Tạo dấu của đạo hàm
    signs = []
    for interval in intervals:
        if interval > 0:
            signs.append("+")
        elif interval < 0:
            signs.append("-")
        else:
            signs.append("0")

    signs_str = ",".join(signs)

    return f"""
\t\\begin{{tikzpicture}}
\t\t\\tkzTabInit[nocadre=false,lgt=1.2,espcl=2.5,deltacl=0.6]
\t\t{{{function_name} /0.6,{function_name}' /0.6,{function_name} /2}}
\t\t{{{points_str}}}
\t\t\\tkzTabLine{{{signs_str}}}
\t\t\\tkzTabVar{{-/$-\\infty$, +/,+/$+\\infty$}}
\t\\end{{tikzpicture}}
"""


def format_dimension(value: float, unit: str = "mét") -> str:
    """Format kích thước với quy tắc bỏ .0"""
    if abs(value - round(value)) < 1e-10:  # Kiểm tra số nguyên
        return f"{int(round(value))} {unit}"
    else:
        formatted = f"{value:.1f}"
        if formatted.endswith('.0'):
            formatted = formatted[:-2]
        return f"{formatted} {unit}"


def format_equation_system(equations: list) -> str:
    """Format hệ phương trình thành LaTeX"""
    if len(equations) == 1:
        return f"\\({equations[0]}\\)"

    equations_str = " \\\\\n\t\t".join(equations)
    return f"""\\(\\begin{{cases}}
\t\t{equations_str}
\t\\end{{cases}}\\)"""


def format_number_clean(value, precision=2):
    """Format số: nếu là số thực và phần thập phân là 0 thì trả về số nguyên, còn lại giữ nguyên."""
    try:
        fval = float(value)
        if abs(fval - round(fval)) < 1e-10:
            return str(int(round(fval)))
        else:
            # Giữ tối đa precision chữ số thập phân, loại bỏ .00 nếu có
            formatted = f"{fval:.{precision}f}"
            while formatted.endswith('0') and '.' in formatted:
                formatted = formatted[:-1]
            if formatted.endswith('.'):
                formatted = formatted[:-1]
            return formatted
    except Exception:
        return str(value)

    # ===== derivative/tikz_figures.py =====
"""
TikZ Figures Module for Derivative Optimization Questions

This module contains TikZ figure templates extracted from sample.tex
to be reused across different optimization problem generators.
"""


def get_fence_e_figure():
    """
    Returns TikZ code for E-shaped fence optimization figure
    Used in fence optimization problems along a river
    """
    return """
\t\\begin{tikzpicture}[scale=0.4,>=stealth, font=\\footnotesize, line join=round, line cap=round]
\t\t\t\\tkzDefPoints{0/0/O,1/4/B,5/4/C,0/1/G}
\t\t\t\\coordinate (D) at ($(O)+(C)-(B)$);
\t\t\t\\coordinate (E) at ($(C)!-1!(B)$);
\t\t\t\\coordinate (F) at ($(O)+(E)-(B)$);
\t\t\t\\coordinate (H) at ($(G)+(B)-(O)$);
\t\t\t\\coordinate (K) at ($(G)+(D)-(O)$);
\t\t\t\\coordinate (L) at ($(H)+(K)-(G)$);
\t\t\t\\coordinate (M) at ($(L)!-1!(H)$);
\t\t\t\\coordinate (N) at ($(G)+(F)-(O)$);
\t\t\t\\coordinate (v) at ($(B)!-0.5!(C)$);
\t\t\t\\coordinate (w) at ($(E)!-0.2!(C)$);
\t\t\t\\tkzInterLL(O,B)(G,K)\\tkzGetPoint{I}
\t\t\t\\tkzInterLL(K,N)(C,D)\\tkzGetPoint{J}
\t\t\t\\tkzInterLL(B,C)(L,K)\\tkzGetPoint{x}
\t\t\t\\tkzInterLL(E,C)(M,N)\\tkzGetPoint{y}
\t\t\t\\tkzInterLL(B,v)(H,G)\\tkzGetPoint{z}
\t\t\t\\coordinate (n) at ($(G)!1.3!(H)$);
\t\t\t\\coordinate (c) at ($(n)+(w)-(v)$);
\t\t\t\\coordinate (h) at ($(v)!0.5!(n)$);
\t\t\t\\coordinate (k) at ($(c)!0.5!(w)$);
\t\t\t\\coordinate (l) at ($(v)!0.6!(n)$);
\t\t\t\\coordinate (m) at ($(w)!0.6!(c)$);
\t\t\t\\coordinate (i) at ($(v)!0.9!(n)$);
\t\t\t\\coordinate (o) at ($(w)!0.9!(c)$);
\t\t\t\\coordinate (q) at ($(v)!0.7!(n)$);
\t\t\t\\coordinate (p) at ($(w)!0.7!(c)$);
\t\t\t\\coordinate (r) at ($(v)!0.8!(n)$);
\t\t\t\\coordinate (t) at ($(w)!0.8!(c)$);
\t\t\t\\tkzDrawSegments[dashed](k,h l,m i,o q,p r,t)
\t\t\t\\tkzDrawSegments(O,F F,E E,M M,N N,F N,G G,O G,H H,B B,I K,L L,C C,J B,x C,y E,w v,z n,c)
\t\\end{tikzpicture}
"""


def get_cable_power_plant_figure():
    """
    Returns TikZ code for cable/power line optimization figure
    Shows power plant A, island C, and connection point S on shore
    """
    return """
\t\\begin{tikzpicture}
\t\t\t% Water/wave pattern using efficient loop
\t\t\t\\begin{scope}[scale=0.5]
\t\t\t\t\\foreach \\x in {0,1,...,20} {
\t\t\t\t\t\\foreach \\y in {1,2,...,15} {
\t\t\t\t\t\t\\coordinate (wave) at (\\x,\\y/2);
\t\t\t\t\t\t\\draw ($(wave)-(0.3,0)$) to[out=-60,in=110] ($(wave)+(0.3,0)$);
\t\t\t\t\t}
\t\t\t\t}
\t\t\t\\end{scope}
\t\t\t
\t\t\t% Building structure
\t\t\t\\begin{scope}[xshift=9cm, scale=0.4]
\t\t\t\t% Main building outline
\t\t\t\t\\draw (5,0) rectangle (10.5,3.5);
\t\t\t\t\\draw (7,0) -- (7,3.5);
\t\t\t\t\\draw (5.3,0) -- (5.3,2) -- (6,2.8) -- (6.7,2) -- (6.7,0);
\t\t\t\t
\t\t\t\t% Windows using loop
\t\t\t\t\\foreach \\i in {0,1,2} {
\t\t\t\t\t\\draw (7.5+\\i,2) rectangle (8+\\i,2.5);
\t\t\t\t}
\t\t\t\t
\t\t\t\t% Roof layers using loop
\t\t\t\t\\foreach \\i in {0,2,4,6,8} {
\t\t\t\t\t\\pgfmathsetmacro\\offset{0.05*\\i}
\t\t\t\t\t\\pgfmathsetmacro\\height{0.5*\\i}
\t\t\t\t\t\\draw (5.2+\\offset,3.5+\\height) rectangle (6.8-\\offset,4+\\height);
\t\t\t\t\t\\draw (5.25+\\offset,4+\\height) rectangle (6.7-\\offset,4.5+\\height);
\t\t\t\t}
\t\t\t\t
\t\t\t\t% Ground line and labels
\t\t\t\t\\draw (-25,0) -- (12,0);
\t\t\t\t\\node[below] at (5,0) {$A$};
\t\t\t\t\\node[below] at (-21,0) {$B$};
\t\t\t\t\\node[below left] at (-21,11) {$C$};
\t\t\t\t\\node[below] at (-8,0) {$S$};
\t\t\t\t
\t\t\t\t% Additional elements
\t\t\t\t\\draw (-21,0) -- (-21,11) -- (-8,0);
\t\t\t\t\\draw plot[smooth cycle] coordinates{(-23,11.2)(-21,13)(-19,11.2)};
\t\t\t\\end{scope}
\t\\end{tikzpicture}
"""


def get_travel_rectangle_figure(width=20, length=25, slow_speed=15, fast_speed=30, position=None):
    """
    Returns TikZ code for travel optimization figure
    Shows rectangular land ABCD with barrier MN and path A->X->C

    Args:
        width: Width of the rectangle (BC) in km
        length: Length of the rectangle (AB) in km
        slow_speed: Speed on the first segment (A->X) in km/h
        fast_speed: Speed on the second segment (X->C) in km/h
        position: (float, optional) Position of X on MN (0 = M, 1 = N)
    """
    # Calculate scale factor to maintain proper proportions
    # Use a base unit of 1.5 for scaling
    base_unit = 1.5
    min_size = 2.0
    max_size = 6.0

    # In the TikZ drawing:
    # - length (AB) corresponds to the horizontal dimension (B point)
    # - width (BC) corresponds to the vertical dimension (D point)

    # Calculate the ratio between width and length
    ratio = width / length

    # Scale length and width proportionally
    # For the drawing, we want:
    # - If BC > AB (width > length), then D should be higher than B is to the right
    # - If BC < AB (width < length), then B should be further to the right than D is high
    # - If BC = AB (width = length), then the rectangle should be a square

    # Base scale for the smaller dimension
    base_scale = base_unit * 2.5

    if width > length:
        # Width is larger (BC > AB): rectangle should be taller than wide
        draw_length = base_scale  # Horizontal (B)
        draw_width = base_scale * ratio  # Vertical (D)
    elif width < length:
        # Length is larger (AB > BC): rectangle should be wider than tall
        draw_width = base_scale  # Vertical (D)
        draw_length = base_scale * (length / width)  # Horizontal (B)
    else:
        # Width equals length (square)
        draw_length = base_scale
        draw_width = base_scale

    # X nằm trên MN, xác định theo position (0 < position < 1)
    if position is None:
        # Nếu không truyền position, mặc định lấy theo tỷ lệ vận tốc (cũ)
        position = slow_speed / (slow_speed + fast_speed)
    # Clamp position để tránh trùng M hoặc N
    position = max(0.05, min(0.95, position))

    return f"""
	\\begin{{tikzpicture}}[line join=round, line cap=round]
			\\tikzset{{label style/.style={{font=\\footnotesize}}}}
			% Define parameters
			\\pgfmathsetmacro\\h{{1.5}}
			\\pgfmathsetmacro\\goc{{90}}

			% Define points with proportional dimensions
			\\tkzDefPoint(0,0){{A}}
			\\tkzDefShiftPoint[A](0:{draw_length}){{B}}
			\\tkzDefShiftPoint[A](\\goc:{draw_width}){{D}}
			\\coordinate (C) at ($(B)+(D)-(A)$);
			\\coordinate (M) at ($(A)!0.5!(D)$);
			\\coordinate (N) at ($(B)!0.5!(C)$);
			% X nằm trên MN theo position
			\\coordinate (X) at ($(M)!{position}!(N)$);

			\\pgfresetboundingbox
			\\draw (A) -- (B) -- (C) -- (D) -- cycle 
				  (N) -- (M) 
				  (A) -- (X) -- (C);

			\\tkzDrawPoints[fill=black](A,B,C,D,M,N,X)
			\\tkzLabelPoints[below](A,B)
			\\tkzLabelPoints[above](C,D,X)
			\\tkzLabelPoints[below left](M,N)

			\\draw[decorate, decoration={{brace, amplitude=8pt}}, xshift=0.5cm] 
				  (C) -- (B) node[black, sloped, pos=0.3, right=4pt, yshift=0.5cm] {{{width} km}};
			\\draw[decorate, decoration={{brace, amplitude=8pt}}, yshift=1cm] 
				  (B) -- (A) node[black, midway, below, yshift=-0.2cm] {{{length} km}};

			\\path (C) -- (X) node[black, sloped, pos=0.7, right, yshift=-0.3cm] {{{fast_speed} km/h}};
			\\path (A) -- (X) node[black, sloped, pos=0.3, right, yshift=-0.3cm] {{{slow_speed} km/h}};
			\\path (M) -- (X) node[black, midway, above] {{$x$}};
	\\end{{tikzpicture}}
"""


def get_simple_fence_figure():
    """
    Returns simplified fence figure description for basic fence problems
    when complex TikZ is not needed
    """
    return "[Hình vẽ: Hàng rào hình chữ E dọc sông với khu đất chữ nhật chia làm 2 phần]"


def get_simple_cable_figure():
    """
    Returns simplified cable figure description for basic cable problems
    when complex TikZ is not needed
    """
    return "[Hình vẽ: Nhà máy điện A trên bờ biển, đảo C, điểm S trên bờ. Khoảng cách BC vuông góc với bờ]"


def get_simple_travel_figure():
    """
    Returns simplified travel figure description for basic travel problems
    when complex TikZ is not needed
    """
    return "[Hình vẽ: Khu đất chữ nhật ABCD với rào chắn MN và đường đi A->X->C]"


# Dictionary for easy access to figures
TIKZ_FIGURES = {
    'fence_e': get_fence_e_figure,
    'cable_power': get_cable_power_plant_figure,
    'travel_rectangle': get_travel_rectangle_figure,
    'simple_fence': get_simple_fence_figure,
    'simple_cable': get_simple_cable_figure,
    'simple_travel': get_simple_travel_figure
}


def get_figure(figure_name: str, use_simple: bool = False, **kwargs) -> str:
    """
    Get a TikZ figure by name

    Args:
        figure_name: Name of the figure ('fence', 'cable', 'travel')
        use_simple: If True, returns simple text description instead of TikZ
        **kwargs: Additional parameters to pass to the figure function
                 (e.g., width, length, slow_speed, fast_speed for travel figure)

    Returns:
        String containing TikZ code or simple description
    """
    if use_simple:
        simple_key = f'simple_{figure_name}'
        if simple_key in TIKZ_FIGURES:
            return TIKZ_FIGURES[simple_key]()

    # Map common names to full keys
    name_mapping = {
        'fence': 'fence_e',
        'cable': 'cable_power',
        'travel': 'travel_rectangle'
    }

    key = name_mapping.get(figure_name, figure_name)
    if key in TIKZ_FIGURES:
        # Special handling for travel_rectangle to pass parameters
        if key == 'travel_rectangle':
            return TIKZ_FIGURES[key](**kwargs)
        return TIKZ_FIGURES[key]()

    return f"[Hình vẽ: {figure_name} - Chưa được định nghĩa]"


# ===== derivative/base_derivative_question.py =====
"""
Base class cho các câu hỏi tối ưu hóa (derivative optimization problems)
"""
import random
import logging
from abc import ABC, abstractmethod
from fractions import Fraction
from typing import List, Tuple, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BaseDerivativeQuestion(ABC):
    """Base class cho tất cả các dạng bài toán tối ưu hóa"""

    def __init__(self):
        self.parameters = {}
        self.correct_answer = None
        self.wrong_answers = []
        self.solution_steps = []

    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        """Generate random parameters cho bài toán"""
        pass

    @abstractmethod
    def calculate_answer(self) -> Any:
        """Tính toán đáp án đúng dựa trên parameters"""
        pass

    @abstractmethod
    def generate_wrong_answers(self) -> List[Any]:
        """Sinh ra 3 đáp án sai gần với đáp án đúng"""
        pass

    @abstractmethod
    def generate_solution(self) -> str:
        """Sinh ra lời giải chi tiết bằng LaTeX"""
        pass

    @abstractmethod
    def generate_question_text(self) -> str:
        """Sinh ra đề bài bằng LaTeX"""
        pass



    def format_number(self, num: float, as_money: bool = False, unit: str = "") -> str:
        """Format số thành chuỗi LaTeX đẹp"""
        if isinstance(num, Fraction):
            if num.denominator == 1:
                result = f"{num.numerator}"
            else:
                result = f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
        elif num == int(num):
            if as_money and num >= 1000000:
                result = f"{int(num // 1000000)} triệu đồng"
            elif as_money and num >= 1000:
                result = f"{int(num // 1000):,}".replace(",", ".") + " đồng"
            else:
                result = f"{int(num)}"
        else:
            result = f"{num:.3f}".rstrip('0').rstrip('.')

        if unit and not as_money:
            result += f" {unit}"

        return result

    def generate_full_question(self, question_number: int = 1) -> str:
        """Tạo câu hỏi hoàn chỉnh"""
        logging.info(f"Generating question {question_number}")

        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        self.wrong_answers = self.generate_wrong_answers()

        question_text = self.generate_question_text()
        solution = self.generate_solution()
        
        # Tạo tất cả đáp án và tìm đáp án đúng
        all_answers = [self.correct_answer] + self.wrong_answers
        random.shuffle(all_answers)
        correct_index = all_answers.index(self.correct_answer)
        
        # Format theo container - text thô + đáp án A/B/C/D
        question_content = f"Câu {question_number}: {question_text}\n\n"
        
        for j, ans in enumerate(all_answers):
            letter = chr(65 + j)  # A, B, C, D
            marker = "*" if j == correct_index else ""
            question_content += f"{marker}{letter}. {ans}\n\n"
        
        question_content += f"Lời giải:\n\n{solution}\n\n"
        
        return question_content

    def generate_question_only(self, question_number: int = 1) -> tuple:
        """Tạo câu hỏi chỉ có đề bài và lời giải, trả về (question_content, correct_answer)"""
        logging.info(f"Generating question only {question_number}")

        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        
        question_text = self.generate_question_text()
        solution = self.generate_solution()
        
        # Format chỉ có đề bài và lời giải
        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += f"Lời giải:\n\n{solution}\n\n"
        
        return question_content, self.correct_answer

    @staticmethod
    def create_latex_document(questions: List[str], title: str = "Câu hỏi Tối ưu hóa với Đạo hàm") -> str:
        """Tạo document LaTeX hoàn chỉnh theo format sample.tex"""

        # Header với packages cần thiết cho TikZ figures
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{polyglossia}}
\\setmainlanguage{{vietnamese}}
\\setmainfont{{DejaVu Serif}}
\\usepackage{{tikz}}
\\usepackage{{tkz-tab}}
\\usepackage{{tkz-euclide}}
\\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\\begin{{document}}
{title}

"""

        latex_content += "\n\n".join(questions)
        latex_content += "\\end{document}"

        return latex_content

    @staticmethod  
    def create_latex_document_with_format(questions_data: List, title: str = "Câu hỏi Tối ưu hóa với Đạo hàm", fmt: int = 1) -> str:
        """Tạo document LaTeX với 2 format khác nhau
        
        Args:
            questions_data: List of tuples (question_content, correct_answer) for fmt=2 
                           or List of strings for fmt=1
            title: Tiêu đề document
            fmt: 1 = đáp án ngay sau câu hỏi, 2 = đáp án tập trung ở cuối
        """
        # Header với packages cần thiết cho TikZ figures
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{polyglossia}}
\\setmainlanguage{{vietnamese}}
\\setmainfont{{DejaVu Serif}}
\\usepackage{{tikz}}
\\usepackage{{tkz-tab}}
\\usepackage{{tkz-euclide}}
\\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\\begin{{document}}
{title}

"""

        if fmt == 1:
            # Format 1: đáp án ngay sau câu hỏi (questions_data là List[str])
            latex_content += "\n\n".join(questions_data)
        else:
            # Format 2: câu hỏi + lời giải, đáp án ở cuối (questions_data là List[tuple])
            correct_answers = []
            for question_content, correct_answer in questions_data:
                latex_content += question_content + "\n\n"
                correct_answers.append(correct_answer)
            
            # Thêm phần đáp án ở cuối
            latex_content += "Đáp án\n\n"
            for idx, answer in enumerate(correct_answers, 1):
                latex_content += f"{idx}. {answer}\n\n"

        latex_content += "\\end{document}"
        return latex_content

    # ===== derivative/pool_optimization.py =====
"""
Bài toán tối ưu hồ chứa nước - khối hộp chữ nhật không nắp
"""
import random
import math
import logging
from fractions import Fraction
from typing import Dict, List, Any


class PoolOptimization(BaseDerivativeQuestion):
    """Bài toán tối ưu chi phí xây hồ chứa nước"""

    def generate_parameters(self) -> Dict[str, Any]:
        """Generate parameters cho bài toán hồ nước với nghiệm đẹp"""
        logging.info("Generating pool optimization parameters")

        # Tỷ lệ dài/rộng
        length_width_ratio = random.choice([2, 3, 4])

        # Chọn x đẹp (nghiệm của phương trình x³ = (1+ratio)V/ratio)
        nice_x_values = [2, 3, 4, 5]
        x_optimal = random.choice(nice_x_values)

        # Tính V để có nghiệm đẹp: x³ = (1+ratio)V/ratio
        # => V = ratio * x³ / (1+ratio)
        x_cubed = x_optimal ** 3
        volume_float = length_width_ratio * x_cubed / (1 + length_width_ratio)

        # Chuyển về phân số đẹp
        if volume_float == int(volume_float):
            volume = Fraction(int(volume_float), 1)
        else:
            # Thử một số mẫu số phổ biến
            for denominator in [2, 3, 4, 5, 6, 8, 9, 12]:
                if abs(volume_float * denominator - round(volume_float * denominator)) < 0.001:
                    numerator = round(volume_float * denominator)
                    volume = Fraction(numerator, denominator)
                    break
            else:
                # Fallback: làm tròn đến 1 chữ số thập phân và chuyển thành phân số
                volume_rounded = round(volume_float * 10) / 10
                volume = Fraction(volume_rounded).limit_denominator(100)

        # Giá nhân công (đồng/m²)
        labor_costs = [300000, 400000, 500000, 600000, 800000]
        labor_cost = random.choice(labor_costs)

        return {
            'volume': volume,
            'length_width_ratio': length_width_ratio,  # dài = ratio * rộng
            'labor_cost': labor_cost,
            'x_optimal': x_optimal,  # Lưu lại để dùng trong solution
            'question_type': random.choice([1, 2, 3])  # 1: chi phí, 2: chiều dài, 3: chiều rộng
        }

    def calculate_exact_pool_solution(self) -> str:
        """Tính nghiệm chính xác của bài toán hồ nước dưới dạng căn thức"""
        V = self.parameters['volume']
        ratio = self.parameters['length_width_ratio']
        
        # Công thức: x³ = (2 + 2*ratio)*V / (2*ratio²)
        # Simplify: x³ = (1 + ratio)*V / ratio²
        
        numerator = (1 + ratio) * V.numerator
        denominator = ratio * ratio * V.denominator
        
        # Rút gọn phân số trong căn thức
        from math import gcd
        common_divisor = gcd(int(numerator), denominator)
        numerator //= common_divisor
        denominator //= common_divisor
        
        # Trả về dạng căn bậc 3
        if denominator == 1:
            return f"\\sqrt[3]{{{numerator}}}"
        else:
            return f"\\sqrt[3]{{\\frac{{{numerator}}}{{{denominator}}}}}"

    def calculate_answer(self) -> str:
        """Tính đáp án theo loại câu hỏi với kết quả chính xác"""
        V = float(self.parameters['volume'])
        ratio = self.parameters['length_width_ratio']
        cost_per_m2 = self.parameters['labor_cost']
        question_type = self.parameters['question_type']

        # Tính x_optimal chính xác từ công thức
        x_optimal_calculated = ((2 + 2 * ratio) * V / (2 * ratio ** 2)) ** (1 / 3)

        if question_type == 1:  # Chi phí
            # Diện tích tối thiểu với x_optimal_calculated
            min_area = ratio * x_optimal_calculated ** 2 + (2 + 2 * ratio) * V / (ratio * x_optimal_calculated)
            # Chi phí tối thiểu
            min_cost = min_area * cost_per_m2
            return format_money(min_cost)
        elif question_type == 2:  # Chiều dài
            # Tính chính xác: length = ratio * x_optimal
            length_value = ratio * x_optimal_calculated
            if abs(length_value - round(length_value)) < 0.01:
                return f"\\({int(round(length_value))}\\) mét"
            else:
                return f"\\({length_value:.2f}\\) mét"
        else:  # question_type == 3, Chiều rộng
            # Trả về kết quả chính xác dưới dạng thập phân
            if abs(x_optimal_calculated - round(x_optimal_calculated)) < 0.01:
                return f"\\({int(round(x_optimal_calculated))}\\) mét"
            else:
                return f"\\({x_optimal_calculated:.2f}\\) mét"

    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý, đúng dạng toán học"""
        from fractions import Fraction
        V = self.parameters['volume']
        ratio = self.parameters['length_width_ratio']
        question_type = self.parameters['question_type']

        # Đáp án đúng: x = \sqrt[3]{\frac{(1+ratio)V}{ratio^2}}
        numerator = (1 + ratio) * V.numerator
        denominator = ratio * ratio * V.denominator
        from math import gcd, sqrt
        common_divisor = gcd(int(numerator), denominator)
        numerator //= common_divisor
        denominator //= common_divisor

        wrong_answers = []
        if question_type == 2 or question_type == 3:
            # Tính giá trị thập phân của x_optimal
            V_float = float(V)
            x_optimal_decimal = ((2 + 2 * ratio) * V_float / (2 * ratio ** 2)) ** (1 / 3)
            
            # Tạo các đáp án sai bằng cách thay đổi giá trị
            wrong_x_values = [x_optimal_decimal * 0.85, x_optimal_decimal * 1.15, x_optimal_decimal * 0.75]
            
            if question_type == 2:  # Chiều dài
                wrong_lengths = [ratio * x for x in wrong_x_values]
                wrong_answers = []
                for length in wrong_lengths:
                    if abs(length - round(length)) < 0.01:
                        wrong_answers.append(f"\\({int(round(length))}\\) mét")
                    else:
                        wrong_answers.append(f"\\({length:.2f}\\) mét")
            else:  # Chiều rộng
                wrong_answers = []
                for x in wrong_x_values:
                    if abs(x - round(x)) < 0.01:
                        wrong_answers.append(f"\\({int(round(x))}\\) mét")
                    else:
                        wrong_answers.append(f"\\({x:.2f}\\) mét")
        else:
            V = float(self.parameters['volume'])
            cost_per_m2 = self.parameters['labor_cost']
            x_optimal_calculated = ((2 + 2 * ratio) * V / (2 * ratio ** 2)) ** (1 / 3)
            min_area = ratio * x_optimal_calculated ** 2 + (2 + 2 * ratio) * V / (ratio * x_optimal_calculated)
            min_cost = min_area * cost_per_m2
            error_ratios = [1.13, 1.07, 1.20]
            wrong_costs = [min_cost * ratio for ratio in error_ratios]
            wrong_answers = [format_money(cost) for cost in wrong_costs]
        return wrong_answers

    def generate_question_text(self) -> str:
        """Sinh đề bài theo loại câu hỏi"""
        volume = self.parameters['volume']
        ratio = self.parameters['length_width_ratio']
        cost = self.parameters['labor_cost']
        question_type = self.parameters['question_type']

        volume_str = format_fraction_latex(volume.numerator, volume.denominator)
        cost_str = format_money(cost, "")

        if ratio == 2:
            ratio_text = "gấp đôi"
        elif ratio == 3:
            ratio_text = "gấp ba lần"
        else:
            ratio_text = f"gấp {ratio} lần"

        # Phần đầu câu hỏi giống nhau
        base_text = f"""Người ta cần xây một hồ chứa nước với dạng khối hộp chữ nhật không nắp có thể tích bằng \\({volume_str}\\) m\\(^3\\). Đáy hồ là hình chữ nhật có chiều dài {ratio_text} chiều rộng. Giá thuê nhân công xây hồ là \\({cost_str}\\) đồng/m\\(^2\\). Người ta xác định kích thước của hồ nước sao cho chi phí thuê nhân công là thấp nhất."""

        # Câu hỏi kết thúc theo loại
        question_endings = {
            1: "Tính chi phí thấp nhất đó.",
            2: "Để chi phí thuê nhân công là thấp nhất thì chiều dài là bao nhiêu?",
            3: "Để chi phí thuê nhân công là thấp nhất thì chiều rộng là bao nhiêu?"
        }

        return f"{base_text} {question_endings[question_type]}"

    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết theo loại câu hỏi"""
        V = self.parameters['volume']
        ratio = self.parameters['length_width_ratio']
        cost = self.parameters['labor_cost']
        x_optimal = self.parameters['x_optimal']  # Nghiệm đẹp
        question_type = self.parameters['question_type']

        V_float = float(V)
        x_cubed_calculated = (2 + 2 * ratio) * V_float / (2 * ratio ** 2)
        min_area = self._calculate_min_area()
        min_cost = min_area * cost

        volume_str = format_fraction_latex(V.numerator, V.denominator)

        # Tính giá trị thập phân cho kết quả cuối
        x_optimal_decimal = ((2 + 2 * ratio) * V_float / (2 * ratio ** 2)) ** (1 / 3)
        min_area_decimal = ratio * x_optimal_decimal ** 2 + (2 + 2 * ratio) * V_float / (ratio * x_optimal_decimal)
        
        # Tính x_cubed để hiện thị trong lời giải
        x_cubed_decimal = (2 + 2 * ratio) * V_float / (2 * ratio ** 2)
        if abs(x_cubed_decimal - round(x_cubed_decimal)) < 0.01:
            x_cubed_str = str(int(round(x_cubed_decimal)))
        else:
            x_cubed_str = f"{x_cubed_decimal:.2f}"
        
        # Format kết quả cuối thành thập phân
        if abs(x_optimal_decimal - round(x_optimal_decimal)) < 0.01:
            x_optimal_result = str(int(round(x_optimal_decimal)))
        else:
            x_optimal_result = f"{x_optimal_decimal:.2f}"
            
        if abs(min_area_decimal - round(min_area_decimal)) < 0.01:
            min_area_result = str(int(round(min_area_decimal)))
        else:
            min_area_result = f"{min_area_decimal:.2f}"

        common_solution = f"""Gọi \\(x\\) là chiều rộng hồ nước, suy ra chiều dài hồ nước là \\({ratio}x\\). Ta có \\(V=x\cdot {ratio}x\cdot h\Leftrightarrow h=\dfrac{{V}}{{{ratio}x^2}}.\\)
		Diện tích cần xây dựng cho hồ nước là 
		\\(S={ratio}x^2+2(xh+{ratio}xh)={ratio}x^2+{2 + 2 * ratio}xh={ratio}x^2+\dfrac{{{2 + 2 * ratio}V}}{{{ratio}x}}=f(x).\\)
		Có \\(f'(x)={2 * ratio}x-\dfrac{{{2 + 2 * ratio}V}}{{{ratio}x^2}}\\), \\(f'(x)=0\\Leftrightarrow x^3=\dfrac{{{2 + 2 * ratio}V}}{{{2 * ratio ** 2}}}={x_cubed_str}\\Leftrightarrow x={x_optimal_result}\\).\n\n
		Lập bảng biến thiên, ta suy ra diện tích nhỏ nhất cần cho hồ nước là \\(S_{{\\text{{min}}}}=f({x_optimal_result})={min_area_result}\\) m\\(^2\\).\n\n"""

        if question_type == 1:  # Chi phí
            min_cost_million = min_cost / 1_000_000
            min_cost_million_str = format_number_clean(min_cost_million, precision=1)
            conclusion = f"""Tổng chi phí thấp nhất cần trả là \\(P={min_area_result}\\times{cost // 1000}={min_cost_million_str}\\) triệu đồng."""
        elif question_type == 2:  # Chiều dài
            length_decimal = ratio * x_optimal_decimal
            if abs(length_decimal - round(length_decimal)) < 0.01:
                length_result = str(int(round(length_decimal)))
            else:
                length_result = f"{length_decimal:.2f}"
            conclusion = f"""Vậy chiều dài tối ưu của hồ nước là \\({ratio} \\times {x_optimal_result} = {length_result}\\) mét."""
        else:  # question_type == 3, Chiều rộng
            conclusion = f"""Vậy chiều rộng tối ưu của hồ nước là \\({x_optimal_result}\\) mét."""

        return common_solution + conclusion

    def _calculate_min_area(self) -> float:
        """Tính diện tích tối thiểu (helper method)"""
        V = float(self.parameters['volume'])
        ratio = self.parameters['length_width_ratio']
        x_optimal_calculated = ((2 + 2 * ratio) * V / (2 * ratio ** 2)) ** (1 / 3)
        return ratio * x_optimal_calculated ** 2 + (2 + 2 * ratio) * V / (ratio * x_optimal_calculated)

    # ===== derivative/fence_optimization.py =====
"""
Bài toán tối ưu hàng rào hình chữ E dọc bờ sông
"""
import random
import math
from typing import Dict, List, Any


class FenceOptimization(BaseDerivativeQuestion):
    """Bài toán tối ưu diện tích hàng rào hình chữ E"""

    def generate_parameters(self) -> Dict[str, Any]:
        """Generate parameters cho bài toán hàng rào"""
        # Tổng ngân sách (triệu đồng)
        budgets = [12, 15, 18, 20, 24, 30]
        budget = random.choice(budgets) * 1000000

        # Chi phí hàng rào song song với sông (đồng/mét)
        parallel_costs = [50000, 60000, 80000, 100000]
        parallel_cost = random.choice(parallel_costs)

        # Chi phí hàng rào vuông góc với sông (đồng/mét) - thường rẻ hơn
        perpendicular_costs = [30000, 40000, 50000]
        perpendicular_cost = random.choice(perpendicular_costs)

        return {
            'budget': budget,
            'parallel_cost': parallel_cost,  # chi phí hàng rào song song với sông
            'perpendicular_cost': perpendicular_cost  # chi phí 3 hàng rào vuông góc
        }

    def calculate_exact_fence_area(self) -> str:
        """Tính diện tích chính xác dưới dạng phân số"""
        budget = self.parameters['budget']
        parallel_cost = self.parameters['parallel_cost']
        perp_cost = self.parameters['perpendicular_cost']
        
        # Công thức đúng cho hàng rào hình E với 1 mặt song song:
        # Ràng buộc: 3*perp_cost*x + parallel_cost*y = budget
        # => y = (budget - 3*perp_cost*x) / parallel_cost
        # S = x*y = x*(budget - 3*perp_cost*x) / parallel_cost
        # S' = (budget - 6*perp_cost*x) / parallel_cost = 0
        # => x_optimal = budget / (6*perp_cost)
        # => y_optimal = (budget - budget/2) / parallel_cost = budget / (2*parallel_cost)
        # => max_area = x_optimal * y_optimal = budget² / (12*perp_cost*parallel_cost)
        
        numerator = budget * budget
        denominator = 12 * perp_cost * parallel_cost
        
        # Rút gọn phân số
        from math import gcd
        common_divisor = gcd(numerator, denominator)
        numerator //= common_divisor
        denominator //= common_divisor
        
        # Trả về dạng phân số nếu cần
        if denominator == 1:
            return str(numerator)
        else:
            return f"\\frac{{{numerator}}}{{{denominator}}}"

    def calculate_answer(self) -> str:
        """Tính diện tích tối đa với kết quả chính xác"""
        budget = self.parameters['budget']
        parallel_cost = self.parameters['parallel_cost']
        perp_cost = self.parameters['perpendicular_cost']
        
        # Tính diện tích tối đa dưới dạng thập phân
        x_optimal = budget / (6 * perp_cost)
        y_optimal = (budget - 3 * x_optimal * perp_cost) / parallel_cost
        max_area = x_optimal * y_optimal
        
        if abs(max_area - round(max_area)) < 0.01:
            return f"\\({int(round(max_area))}\\) m\\(^2\\)"
        else:
            return f"\\({max_area:.2f}\\) m\\(^2\\)"

    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai"""
        budget = self.parameters['budget']
        parallel_cost = self.parameters['parallel_cost']
        perp_cost = self.parameters['perpendicular_cost']

        x_optimal = budget / (6 * perp_cost)
        y_optimal = (budget - 3 * x_optimal * perp_cost) / parallel_cost
        correct_area = x_optimal * y_optimal

        # Các sai số thường gặp
        wrong_areas = [
            correct_area / 2,  # Quên nhân 2 trong công thức diện tích
            correct_area * 0.8,  # Sai tính đạo hàm
            correct_area * 1.25  # Nhầm hệ số trong ràng buộc
        ]

        return [f"\\({area:.2f}\\) m\\(^2\\)" if abs(area - round(area)) >= 0.01 else f"\\({int(round(area))}\\) m\\(^2\\)" for area in wrong_areas]

    def generate_question_text(self) -> str:
        """Sinh đề bài với hình vẽ TikZ"""
        budget = self.parameters['budget']
        parallel_cost = self.parameters['parallel_cost']
        perp_cost = self.parameters['perpendicular_cost']

        budget_str = format_money(budget, "")
        parallel_str = format_money(parallel_cost, "")
        perp_str = format_money(perp_cost, "")

        # Sử dụng hình vẽ từ tikz_figures module
        tikz_figure = get_figure('fence', use_simple=False)

        return f"""Một người nông dân có {budget_str} đồng muốn làm một cái hàng rào hình chữ \\(E\\) dọc theo một con sông (như hình vẽ) để làm một khu đất có hai phần chữ nhật để trồng rau. Đối với mặt hàng rào song song với bờ sông thì chi phí nguyên vật liệu là {parallel_str} đồng một mét, còn đối với ba mặt hàng rào vuông góc với bờ sông thì chi phí nguyên vật liệu là {perp_str} đồng một mét. Tìm diện tích lớn nhất của đất rào thu được.

{tikz_figure}"""

    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết theo sample.tex"""
        budget = self.parameters['budget']
        parallel_cost = self.parameters['parallel_cost']
        perp_cost = self.parameters['perpendicular_cost']

        x_optimal = budget / (6 * perp_cost)
        y_optimal = (budget - 3 * x_optimal * perp_cost) / parallel_cost
        max_area = x_optimal * y_optimal
        
        # Sử dụng kết quả thập phân cho kết quả cuối
        x_optimal_str = format_number_clean(x_optimal)
        if abs(max_area - round(max_area)) < 0.01:
            max_area_str = str(int(round(max_area)))
        else:
            max_area_str = f"{max_area:.2f}"

        # Tính các hệ số cho công thức
        total_perp_cost = 3 * perp_cost  # Tổng chi phí 3 mặt hàng rào vuông góc
        budget_millions = budget // 1000000
        total_perp_cost_thousands = total_perp_cost // 1000
        parallel_cost_thousands = parallel_cost // 1000
        
        # Rút gọn phân số total_perp_cost_thousands / parallel_cost_thousands
        from math import gcd
        coeff_numerator = total_perp_cost_thousands
        coeff_denominator = parallel_cost_thousands
        coeff_gcd = gcd(coeff_numerator, coeff_denominator)
        coeff_simplified_num = coeff_numerator // coeff_gcd
        coeff_simplified_den = coeff_denominator // coeff_gcd
        
        # Tạo chuỗi phân số rút gọn
        if coeff_simplified_den == 1:
            coeff_str = str(coeff_simplified_num)
        else:
            coeff_str = f"\\dfrac{{{coeff_simplified_num}}}{{{coeff_simplified_den}}}"

        # Tạo bảng biến thiên
        table = f"""
\t\t\t\\begin{{tikzpicture}}
\t\t\t\t\\tkzTabInit[nocadre=false,lgt=1.2,espcl=2.5,deltacl=0.6]
\t\t\t\t{{$x$ /0.6,$S'$ /0.6,$S$ /2}}
\t\t\t\t{{$0$,${x_optimal_str}$,$+\\infty$}}
\t\t\t\t\\tkzTabLine{{,+,$0$,-,}}
\t\t\t\t\\tkzTabVar{{-/$0$, +/${max_area_str}$,-/$-\\infty$}}
\t\t\t\\end{{tikzpicture}}
"""

        return f"""Gọi \\(x\\) là chiều dài 1 mặt hàng rào vuông góc với bờ sông (trong ba mặt vuông góc, \\(x>0\\)).\n\n
\t\tGọi \\(y\\) là chiều dài mặt hàng rào song song với bờ sông \\(y>0\\)).\n\n
\t\tSố tiền phải làm là \\(3x\\times {perp_cost // 1000}000+y\\times {parallel_cost_thousands}000={budget_millions}000000\\Leftrightarrow y=\\dfrac{{{budget_millions}000-{total_perp_cost_thousands}x}}{{{parallel_cost_thousands}}}\\).\n\n
\t\tDiện tích đất \\(S=xy=x\\cdot \\dfrac{{{budget_millions}000-{total_perp_cost_thousands}x}}{{{parallel_cost_thousands}}}={budget // parallel_cost}x-{coeff_str}x^2\\).\n\n
\t\tTa có \\(S'={budget // parallel_cost}-{coeff_str}\\cdot 2x\\), \\(S'=0\\Leftrightarrow x={x_optimal_str}\\).\n\n
\t\tBảng biến thiên
{table}
\t\tVậy \\(\\max\\limits_{{(0;+\\infty)}} S={max_area_str}\\) \\(m^2\\) khi \\(x={x_optimal_str}\\).\n\n"""

    # ===== derivative/cable_optimization.py =====
"""
Bài toán tối ưu chi phí dây điện từ bờ biển ra đảo
"""
import random
import math
from fractions import Fraction
from typing import Dict, List, Any


class CableOptimization(BaseDerivativeQuestion):
    """Bài toán tối ưu chi phí dây điện từ nhà máy qua bờ biển ra đảo"""

    def generate_parameters(self) -> Dict[str, Any]:
        """Generate parameters cho bài toán dây điện với nghiệm đẹp"""
        # Chỉ sinh các bộ tham số sao cho nghiệm x_optimal là số nguyên nhỏ, đẹp
        # x = ab - land_cost * bc / sqrt(underwater_cost^2 - land_cost^2)
        candidates = []
        island_distances = [1, 1.5, 2, 2.5, 3]  # BC (km)
        shore_distances = [4, 5, 6, 8]  # AB (km)
        underwater_costs = [4000, 5000, 6000]  # USD/km
        land_costs = [2000, 2500, 3000]  # USD/km
        for bc in island_distances:
            for ab in shore_distances:
                for underwater_cost in underwater_costs:
                    for land_cost in land_costs:
                        if underwater_cost <= land_cost:
                            continue
                        for x_optimal in range(1, int(ab)):
                            # x = ab - land_cost * bc / sqrt(underwater_cost^2 - land_cost^2)
                            denominator = math.sqrt(underwater_cost ** 2 - land_cost ** 2)
                            if denominator == 0:
                                continue
                            calc_x = ab - (land_cost * bc) / denominator
                            # Chỉ nhận nghiệm gần x_optimal nguyên
                            if abs(calc_x - x_optimal) < 1e-2:
                                # Đảm bảo nghiệm đẹp, đáp án đẹp
                                if abs(Fraction(calc_x).limit_denominator(20).denominator) <= 20:
                                    candidates.append({
                                        'island_distance': bc,
                                        'shore_distance': ab,
                                        'underwater_cost': underwater_cost,
                                        'land_cost': land_cost,
                                        'x_optimal': x_optimal
                                    })
        params = random.choice(candidates)
        # Xóa x_optimal khỏi dict trả về để không lộ đáp án
        params.pop('x_optimal')
        return params

    def calculate_answer(self) -> str:
        """Tính vị trí tối ưu điểm S"""
        bc = self.parameters['island_distance']
        ab = self.parameters['shore_distance']
        underwater_cost = self.parameters['underwater_cost']
        land_cost = self.parameters['land_cost']

        # Tính x_optimal dưới dạng thập phân
        denominator = math.sqrt(underwater_cost ** 2 - land_cost ** 2)
        x_optimal = ab - (land_cost * bc) / denominator
        
        if abs(x_optimal - round(x_optimal)) < 0.01:
            return f"\\({int(round(x_optimal))}\\) km"
        else:
            return f"\\({x_optimal:.2f}\\) km"

    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý, đúng dạng toán học"""
        from fractions import Fraction
        import math
        bc = self.parameters['island_distance']
        ab = self.parameters['shore_distance']
        underwater_cost = self.parameters['underwater_cost']
        land_cost = self.parameters['land_cost']

        denominator = math.sqrt(underwater_cost ** 2 - land_cost ** 2)
        x_correct = ab - (land_cost * bc) / denominator

        wrong_answers = []
        # Sai 1: Đổi dấu trừ thành cộng
        x1 = ab + (land_cost * bc) / denominator
        # Sai 2: Đổi vị trí land_cost và underwater_cost trong công thức
        if underwater_cost > land_cost:
            denom2 = math.sqrt(land_cost ** 2 - underwater_cost ** 2) if land_cost ** 2 - underwater_cost ** 2 > 0 else denominator
        else:
            denom2 = denominator
        x2 = ab - (underwater_cost * bc) / abs(denom2)
        # Sai 3: Quên căn bậc hai (lấy mẫu số là hiệu, không căn)
        denom3 = underwater_cost ** 2 - land_cost ** 2
        if denom3 != 0:
            x3 = ab - (land_cost * bc) / denom3
        else:
            x3 = ab

        # Định dạng đáp án sai theo dạng thập phân
        def format_wrong(x):
            if abs(x - round(x)) < 0.01:
                return f"\\({int(round(x))}\\) km"
            else:
                return f"\\({x:.2f}\\) km"

        wrong_answers = [format_wrong(x1), format_wrong(x2), format_wrong(x3)]
        return wrong_answers

    def generate_question_text(self) -> str:
        """Sinh đề bài với hình vẽ TikZ"""
        bc = self.parameters['island_distance']
        ab = self.parameters['shore_distance']
        underwater_cost = self.parameters['underwater_cost']
        land_cost = self.parameters['land_cost']

        # Sử dụng hình vẽ từ tikz_figures module
        tikz_figure = get_figure('cable', use_simple=False)

        return f"""Một đường dây điện được nối từ một nhà máy điện ở \\(A\\) (nằm tại bờ biển là đường thẳng \\(AB\\)) đến một hòn đảo \\(C\\), khoảng cách ngắn nhất từ đảo về bờ biển là đoạn \\(BC\\) dài \\({bc}\\) km, khoảng cách từ \\(B\\) đến \\(A\\) là \\({ab}\\) km được minh họa bằng hình vẽ dưới đây.
{tikz_figure}
\tBiết rằng mỗi km dây điện đặt dưới nước chi phí mất \\({underwater_cost}\\) USD, còn đặt dưới đất chi phí mất \\({land_cost}\\) USD. Hỏi điểm \\(S\\) trên bờ cách \\(A\\) bao nhiêu để khi mắc dây điện từ \\(A\\) qua \\(S\\) rồi đến \\(C\\) có chi phí là ít nhất?"""

    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết"""
        bc = self.parameters['island_distance']
        ab = self.parameters['shore_distance']
        underwater_cost = self.parameters['underwater_cost']
        land_cost = self.parameters['land_cost']

        denominator = math.sqrt(underwater_cost ** 2 - land_cost ** 2)
        x_optimal = ab - (land_cost * bc) / denominator

        # Tính một số giá trị trung gian cho lời giải
        bs_optimal = ab - x_optimal
        cs_optimal = math.sqrt(bc ** 2 + bs_optimal ** 2)
        total_cost = land_cost * x_optimal + underwater_cost * cs_optimal

        # Format các số thành thập phân
        if abs(x_optimal - round(x_optimal)) < 0.01:
            x_optimal_str = str(int(round(x_optimal)))
        else:
            x_optimal_str = f"{x_optimal:.2f}"
        total_cost_str = format_number_clean(total_cost)

        # Tạo bảng biến thiên
        table = f"""
\t\t\t\\begin{{tikzpicture}}
\t\t\t\t\\tkzTab
\t\t\t\t[nocadre=false,lgt=1.2,espcl=2.5,deltacl=0.6]
\t\t\t\t{{$x$/1.2, $f'(x)$/0.6, $f(x)$/2}}
\t\t\t\t{{$0$, ${x_optimal_str}$, ${ab}$}}
\t\t\t\t{{,-,$0$,+,}}
\t\t\t\t{{+/, -/${total_cost_str}$/, +/}}
\t\t\t\\end{{tikzpicture}}
"""

        return f"""Đặt \\(AS=x\\) với \\(0<x<{ab}\\), khi đó \\(BS={ab}-x\\) và \\(CS=\\sqrt{{BC^2+BS^2}}=\\sqrt{{{bc}^2+({ab}-x)^2}}\\).\n\n
\t\tChi phí lắp đặt dây điện từ \\(A\\) đến \\(S\\) là \\(P_1={land_cost}x\\).\n\n
\t\tChi phí lắp đặt dây điện từ \\(C\\) đến \\(S\\) là \\(P_2={underwater_cost}\\sqrt{{{bc}^2+({ab}-x)^2}}\\).\n\n
\t\tTổng chi phí lắp đặt dây điện là \\(P=P_1+P_2={land_cost}x+{underwater_cost}\\sqrt{{{bc}^2+({ab}-x)^2}}\\).\n\n
\t\tXét hàm \\(f(x)={land_cost}x+{underwater_cost}\\sqrt{{{bc}^2+({ab}-x)^2}}\\) trên khoảng \\((0,{ab})\\).\n\n
\t\tTa có \\(f'(x)={land_cost}-\\dfrac{{{underwater_cost}({ab}-x)}}{{\\sqrt{{x^2-{2 * ab}x+{ab ** 2 + bc ** 2}}}}}\\), khi đó \\(f'(x)=0\\Leftrightarrow {underwater_cost // 1000}({ab}-x)={land_cost // 1000}\\sqrt{{x^2-{2 * ab}x+{ab ** 2 + bc ** 2}}}\\Leftrightarrow x={x_optimal_str}\\).\n\n
\t\tBảng biến thiên của hàm số \\(f(x)\\) như sau\n\n
{table}
\t\t\n\nVậy để chi phí mắc dây điện là ít nhất thì điểm \\(S\\) cách \\(A\\) một khoảng là \\({x_optimal_str}\\) km."""

    def calculate_exact_cable_solution(self, bc, ab, land_cost, underwater_cost):
        """
        Tính toán chính xác nghiệm bài toán dây điện dưới dạng phân số/căn thức
        Công thức: x = ab - (land_cost * bc) / sqrt(underwater_cost^2 - land_cost^2)
        """
        import math
        from fractions import Fraction
        from math import gcd
        
        # Tính các giá trị trung gian
        underwater_squared = underwater_cost ** 2
        land_squared = land_cost ** 2
        denominator_squared = underwater_squared - land_squared
        
        # Kiểm tra xem denominator_squared có phải số chính phương không
        sqrt_denom = math.sqrt(denominator_squared)
        
        # Nếu denominator_squared là số chính phương
        if abs(sqrt_denom - round(sqrt_denom)) < 1e-10:
            # Trường hợp đơn giản: denominator là số nguyên
            denom_int = int(round(sqrt_denom))
            
            # x = ab - (land_cost * bc) / denom_int
            # Chuyển về dạng phân số
            numerator = ab * denom_int - land_cost * bc
            denominator = denom_int
            
            # Rút gọn phân số
            common_divisor = gcd(int(abs(numerator)), denominator)
            numerator //= common_divisor
            denominator //= common_divisor
            
            if denominator == 1:
                return f"{numerator}"
            else:
                return f"\\frac{{{numerator}}}{{{denominator}}}"
        
        else:
            # Trường hợp phức tạp: cần dùng căn thức
            # Thử phân tích denominator_squared = k^2 * n với n không có thừa số chính phương
            n = int(denominator_squared)
            k = 1
            temp_n = n
            
            # Tách các thừa số chính phương
            for i in range(2, int(math.sqrt(temp_n)) + 1):
                while temp_n % (i * i) == 0:
                    temp_n //= (i * i)
                    k *= i
            
            # Bây giờ denominator_squared = k^2 * temp_n
            # sqrt(denominator_squared) = k * sqrt(temp_n)
            
            if k > 1:
                # x = ab - (land_cost * bc) / (k * sqrt(temp_n))
                # Hữu tỷ hóa: = ab - (land_cost * bc * sqrt(temp_n)) / (k * temp_n)
                
                # Phần nguyên: ab
                # Phần trừ: (land_cost * bc * sqrt(temp_n)) / (k * temp_n)
                
                coeff_numerator = int(land_cost * bc)
                coeff_denominator = k * temp_n
                
                # Rút gọn phân số
                common_divisor = gcd(coeff_numerator, coeff_denominator)
                coeff_numerator //= common_divisor
                coeff_denominator //= common_divisor
                
                if coeff_denominator == 1:
                    if coeff_numerator == 1:
                        return f"{ab} - \\sqrt{{{temp_n}}}"
                    else:
                        return f"{ab} - {coeff_numerator}\\sqrt{{{temp_n}}}"
                else:
                    if coeff_numerator == 1:
                        return f"{ab} - \\frac{{\\sqrt{{{temp_n}}}}}{{{coeff_denominator}}}"
                    else:
                        return f"{ab} - \\frac{{{coeff_numerator}\\sqrt{{{temp_n}}}}}{{{coeff_denominator}}}"
            else:
                # k = 1, nghĩa là sqrt(denominator_squared) = sqrt(temp_n)
                coeff_numerator = int(land_cost * bc)
                
                if coeff_numerator == 1:
                    return f"{ab} - \\frac{{\\sqrt{{{temp_n}}}}}{{{temp_n}}}"
                else:
                    return f"{ab} - \\frac{{{coeff_numerator}\\sqrt{{{temp_n}}}}}{{{temp_n}}}"


# ===== derivative/travel_optimization.py =====
"""
Bài toán tối ưu thời gian di chuyển với hai vận tốc khác nhau
"""
import random
import math
from fractions import Fraction
from typing import Dict, List, Any


class TravelOptimization(BaseDerivativeQuestion):
    """
    Generator cho bài tối ưu hóa thời gian di chuyển
    Dựa trên bài toán đi xe đạp từ A đến C qua rào chắn MN
    """

    def generate_parameters(self) -> Dict[str, Any]:
        """Generate parameters cho bài toán di chuyển với nghiệm đẹp"""
        # Chỉ sinh các bộ tham số sao cho nghiệm x_optimal là số nguyên nhỏ, đẹp
        # f'(x) = x/(v1*sqrt(x^2 + (w/2)^2)) + (x-L)/(v2*sqrt((x-L)^2 + (w/2)^2)) = 0
        # Để nghiệm đẹp, chọn width, length, slow_speed, fast_speed, x_optimal nguyên nhỏ
        candidates = []
        widths = [20, 24, 30, 16, 18]  # BC (km)
        lengths = [20, 25, 30, 35]  # AB (km)
        slow_speeds = [10, 12, 15, 18]  # km/h
        fast_speeds = [24, 30, 36]  # km/h
        for width in widths:
            for length in lengths:
                for slow_speed in slow_speeds:
                    for fast_speed in fast_speeds:
                        if fast_speed <= slow_speed:
                            continue
                        half_width = width / 2
                        for x_optimal in range(2, length - 1):
                            # Tính đạo hàm tại x_optimal, kiểm tra nghiệm đúng
                            # f'(x) = x/(v1*sqrt(x^2 + (w/2)^2)) + (x-L)/(v2*sqrt((x-L)^2 + (w/2)^2))
                            denom1 = slow_speed * math.sqrt(x_optimal ** 2 + half_width ** 2)
                            denom2 = fast_speed * math.sqrt((x_optimal - length) ** 2 + half_width ** 2)
                            fprime = x_optimal / denom1 + (x_optimal - length) / denom2
                            # Chỉ nhận nghiệm gần 0 (sai số nhỏ)
                            if abs(fprime) < 1e-3:
                                # Tính thời gian tối thiểu
                                ax_distance = math.sqrt(x_optimal ** 2 + half_width ** 2)
                                cx_distance = math.sqrt((x_optimal - length) ** 2 + half_width ** 2)
                                min_time = ax_distance / slow_speed + cx_distance / fast_speed
                                # Đảm bảo thời gian là số đẹp (gần phân số đơn giản)
                                if abs(Fraction(min_time).limit_denominator(20).denominator) <= 20:
                                    candidates.append({
                                        'width': width,
                                        'length': length,
                                        'slow_speed': slow_speed,
                                        'fast_speed': fast_speed,
                                        'x_optimal': x_optimal,
                                        'min_time': min_time,
                                        'half_width': half_width
                                    })
        params = random.choice(candidates)
        return params

    def get_correct_answer(self) -> str:
        """Trả về đáp án đúng"""
        min_time = self.parameters['min_time']
        time_frac = Fraction(min_time).limit_denominator(20)
        frac_str = format_fraction(time_frac.numerator, time_frac.denominator)
        # Add escape characters for sqrt like in sample.tex
        if "sqrt" in frac_str:
            frac_str = frac_str.replace("sqrt", "\\\\sqrt")
        return f"\\({frac_str}\\) giờ"

    def calculate_answer(self) -> str:
        """Calculate đáp án đúng (method required by base class)"""
        min_time = self.parameters['min_time']
        if abs(min_time - round(min_time)) < 0.01:
            return f"\\({int(round(min_time))}\\) giờ"
        else:
            return f"\\({min_time:.2f}\\) giờ"

    def generate_wrong_answers(self) -> List[str]:
        """Generate các đáp án sai"""
        min_time = self.parameters['min_time']
        results = []

        # Tạo thời gian sai bằng cách thay đổi vận tốc hoặc đường đi
        wrong_times = [
            min_time * 0.8,  # Quá optimistic
            min_time * 1.2,  # Hơi lâu
            min_time * 1.5,  # Quá lâu
            min_time / 1.3  # Gần đúng nhưng sai
        ]

        for time_val in wrong_times:
            if abs(time_val - round(time_val)) < 0.01:
                results.append(f"\\({int(round(time_val))}\\) giờ")
            else:
                results.append(f"\\({time_val:.2f}\\) giờ")

        return results[:3]  # Chỉ lấy 3 đáp án sai

    def generate_question_text(self) -> str:
        """Generate đề bài"""
        width = self.parameters['width']
        length = self.parameters['length']
        slow_speed = self.parameters['slow_speed']
        fast_speed = self.parameters['fast_speed']

        # Sử dụng hình vẽ từ tikz_figures module với các tham số thực tế
        tikz_figure = get_figure('travel', use_simple=False,
                                 width=width, length=length,
                                 slow_speed=slow_speed, fast_speed=fast_speed)

        return f"""Một khu đất phẳng hình chữ nhật \\(ABCD\\) có \\(AB={length}\\) km, \\(BC={width}\\) km và rào chắn \\(MN\\) (với \\(M\\), \\(N\\) lần lượt là trung điểm của \\(AD\\), \\(BC\\)). Một người đi xe đạp xuất phát từ \\(A\\) đi đến \\(C\\) bằng cách đi thẳng từ \\(A\\) đến cửa \\(X\\) thuộc đoạn \\(MN\\) với vận tốc \\({slow_speed}\\) km/giờ rồi đi thẳng từ \\(X\\) đến \\(C\\) với vận tốc \\({fast_speed}\\) km/giờ (hình vẽ). Thời gian ít nhất để người ấy đi từ \\(A\\) đến \\(C\\) là mấy giờ?

{tikz_figure}"""

    def generate_solution(self) -> str:
        """Generate lời giải"""
        width = self.parameters['width']
        length = self.parameters['length']
        slow_speed = self.parameters['slow_speed']
        fast_speed = self.parameters['fast_speed']
        x_optimal = self.parameters['x_optimal']
        min_time = self.parameters['min_time']
        half_width = self.parameters['half_width']

        x_frac = Fraction(x_optimal).limit_denominator(20)
        time_frac = Fraction(min_time).limit_denominator(20)

        # Format các số với format_number_clean và phân số chính xác
        half_width_squared = format_number_clean(half_width ** 2)
        x_optimal_str = format_number_clean(x_optimal)
        
        # Tính giá trị thập phân cho kết quả cuối
        time_float = time_frac.numerator / time_frac.denominator
        if abs(time_float - round(time_float)) < 0.01:
            time_frac_str = str(int(round(time_float)))
        else:
            time_frac_str = f"{time_float:.2f}"

        return f"""Gọi \\(MX=x\\) (km) với \\(0\\leq x\\leq {length}\\).\n\n
\t\tKhi đó, quãng đường \\(AX=\\sqrt{{x^2+{half_width_squared}}}\\) nên thời gian tương ứng là \\(\\dfrac{{\\sqrt{{x^2+{half_width_squared}}}}}{{{slow_speed}}}\\) (h).\n\n
\t\tQuãng đường \\(CX=\\sqrt{{({length}-x)^2+{half_width_squared}}}\\) nên thời gian tương ứng là \\(\\dfrac{{\\sqrt{{({length}-x)^2+{half_width_squared}}}}}{{{fast_speed}}}\\) (h).\n\n
\t\tDo đó tổng thời gian tương ứng là \\(f(x)=\\dfrac{{\\sqrt{{x^2+{half_width_squared}}}}}{{{slow_speed}}}+\\dfrac{{\\sqrt{{({length}-x)^2+{half_width_squared}}}}}{{{fast_speed}}}\\) với \\(x\\in[0;{length}]\\). Ta tìm giá trị nhỏ nhất của \\(f(x)\\) trên \\([0;{length}]\\).\n\n
        \t\tTa có \\(f'(x)=\\dfrac{{x}}{{{slow_speed}\\sqrt{{x^2+{half_width_squared}}}}}+\\dfrac{{x-{length}}}{{{fast_speed}\\sqrt{{({length}-x)^2+{half_width_squared}}}}}=0\\Leftrightarrow x={x_optimal_str}.\\)
\t\tTính các giá trị tại biên và điểm tới hạn, ta có \\(f({x_optimal_str})={time_frac_str}\\).\n\n
\t\tVậy hàm số đạt GTNN bằng \\({time_frac_str}\\) tại \\(x={x_optimal_str}\\)."""


# ===== derivative/rental_optimization.py =====
"""
Bài toán tối ưu doanh thu cho thuê căn hộ
"""
import random
import math
from typing import Dict, List, Any


class RentalOptimization(BaseDerivativeQuestion):
    """Bài toán tối ưu doanh thu cho thuê căn hộ"""

    def generate_parameters(self) -> Dict[str, Any]:
        """Generate parameters cho bài toán cho thuê với nghiệm đẹp"""
        # Chỉ sinh các bộ tham số sao cho nghiệm x_optimal là số nguyên nhỏ, hợp lý
        # x_optimal = (price_increase * apartments - base_price * vacancy_rate) / (2 * price_increase * vacancy_rate)
        # Ta chọn x_optimal nguyên, nhỏ (1-8)
        candidates = []
        total_apartments_list = [40, 45, 50, 60, 80]
        base_prices = [1.5, 2.0, 2.5, 3.0]  # triệu đồng
        price_increases = [100000, 150000, 200000, 250000]
        vacancy_rates = [1, 2, 3]
        for apartments in total_apartments_list:
            for base_price in base_prices:
                for price_increase in price_increases:
                    for vacancy_rate in vacancy_rates:
                        for x_optimal in range(1, 9):
                            # base_price, price_increase đều tính theo đồng
                            base_price_vnd = int(base_price * 1_000_000)
                            numerator = 2 * price_increase * vacancy_rate * x_optimal + base_price_vnd * vacancy_rate
                            denom = price_increase
                            apartments_calc = numerator // denom
                            # Kiểm tra số căn hộ hợp lý
                            if apartments_calc in total_apartments_list and apartments_calc > x_optimal * vacancy_rate:
                                # Giá thuê tối ưu
                                optimal_price = base_price_vnd + x_optimal * price_increase
                                # Đảm bảo giá thuê tối ưu là số đẹp (tròn 100k hoặc 1 triệu)
                                if optimal_price % 100_000 == 0:
                                    candidates.append({
                                        'total_apartments': apartments_calc,
                                        'base_price': base_price_vnd,
                                        'price_increase': price_increase,
                                        'vacancy_rate': vacancy_rate,
                                        'x_optimal': x_optimal,
                                        'optimal_price': optimal_price
                                    })
        # Chọn ngẫu nhiên một bộ hợp lệ
        params = random.choice(candidates)
        # Xóa x_optimal, optimal_price khỏi dict trả về để không lộ đáp án
        params.pop('x_optimal')
        params.pop('optimal_price')
        return params

    def calculate_answer(self) -> str:
        """Tính giá thuê tối ưu"""
        apartments = self.parameters['total_apartments']
        base_price = self.parameters['base_price']
        price_increase = self.parameters['price_increase']
        vacancy_rate = self.parameters['vacancy_rate']

        # Gọi x là số đơn vị tăng giá (x * price_increase)
        # Giá thuê = base_price + x * price_increase
        # Số căn thuê được = apartments - x * vacancy_rate
        # Doanh thu = (base_price + x * price_increase) * (apartments - x * vacancy_rate)

        # R(x) = (base_price + x * price_increase) * (apartments - x * vacancy_rate)
        # R'(x) = price_increase * (apartments - x * vacancy_rate) - (base_price + x * price_increase) * vacancy_rate
        # R'(x) = 0 => price_increase * apartments - x * price_increase * vacancy_rate - base_price * vacancy_rate - x * price_increase * vacancy_rate = 0
        # => x * 2 * price_increase * vacancy_rate = price_increase * apartments - base_price * vacancy_rate
        # => x = (price_increase * apartments - base_price * vacancy_rate) / (2 * price_increase * vacancy_rate)

        x_optimal = (price_increase * apartments - base_price * vacancy_rate) / (2 * price_increase * vacancy_rate)
        optimal_price = base_price + x_optimal * price_increase

        return format_money(optimal_price, "")

    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai"""
        apartments = self.parameters['total_apartments']
        base_price = self.parameters['base_price']
        price_increase = self.parameters['price_increase']
        vacancy_rate = self.parameters['vacancy_rate']

        x_optimal = (price_increase * apartments - base_price * vacancy_rate) / (2 * price_increase * vacancy_rate)
        correct_price = base_price + x_optimal * price_increase

        # Tạo các đáp án sai khác biệt rõ ràng
        multipliers = [0.85, 1.15, 0.7]  # Tỷ lệ để tạo sai số

        wrong_prices = []
        for mult in multipliers:
            wrong_price = correct_price * mult
            # Làm tròn đến hàng trăm nghìn để tạo số đẹp
            wrong_price = round(wrong_price / 100000) * 100000
            wrong_prices.append(wrong_price)

        return [format_money(price, "") for price in wrong_prices]

    def generate_question_text(self) -> str:
        """Sinh đề bài"""
        apartments = self.parameters['total_apartments']
        base_price = self.parameters['base_price']
        price_increase = self.parameters['price_increase']
        vacancy_rate = self.parameters['vacancy_rate']

        base_price_str = format_money(base_price, "")
        increase_str = format_money(price_increase, "")

        return f"""Một công ty bất động sản có \\({apartments}\\) căn hộ cho thuê. Biết rằng nếu cho thuê mỗi căn hộ với giá {base_price_str} đồng thì mỗi tháng mọi căn hộ đều có người thuê và cứ tăng thêm giá cho thuê mỗi căn hộ {increase_str} đồng một tháng thì sẽ có \\({vacancy_rate}\\) căn hộ bị bỏ trống. Hỏi muốn thu nhập cao nhất thì công ty đó cho thuê mỗi căn hộ với giá bao nhiêu một tháng?"""

    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết đúng mẫu trình bày như hình, không dấu phẩy, công thức S không xuống dòng, bỏ .0 nếu là số nguyên."""
        apartments = self.parameters['total_apartments']
        base_price = self.parameters['base_price']
        price_increase = self.parameters['price_increase']
        vacancy_rate = self.parameters['vacancy_rate']

        # Đổi về nghìn đồng
        base_price_k = base_price // 1000
        price_increase_k = price_increase // 1000

        # Số lần tăng tối ưu
        x_optimal = (price_increase * apartments - base_price * vacancy_rate) / (2 * price_increase * vacancy_rate)
        optimal_price = base_price + x_optimal * price_increase
        optimal_price_m = optimal_price / 1_000_000

        # Format các số với format_number_clean
        x_optimal_str = format_number_clean(x_optimal)
        optimal_price_m_str = format_number_clean(optimal_price_m)

        # Hệ số triển khai S(x)
        a = -vacancy_rate * price_increase_k
        b = apartments * price_increase_k - vacancy_rate * base_price_k
        c = apartments * base_price_k

        # Số căn hộ bị bỏ trống
        if vacancy_rate == 1:
            empty_str = 'x'
        else:
            empty_str = f'{vacancy_rate}x'

        return f"""Gọi \\(x\\) là số lần tăng {price_increase_k} nghìn đồng tiền phòng. Giá thuê mỗi căn hộ là \\( {base_price_k} + {price_increase_k}x\\) (nghìn đồng). Khi đó, số căn hộ bị bỏ trống là {empty_str}. Tổng số tiền thu được là:

\\(S = ({apartments} - {empty_str})({base_price_k} + {price_increase_k}x) = {a}x^2 + ({b})x + {c}\\)

Suy ra \\(S\\) đạt giá trị lớn nhất khi \\(x = {x_optimal_str}\\). Vậy để thu nhập cao nhất thì giá thuê mỗi căn hộ là {optimal_price_m_str} triệu đồng."""

# ===== derivative/derivative_generator.py =====
"""
Generator chính cho các câu hỏi tối ưu hóa đạo hàm
Dựa trên mẫu asymptote_mc.py
"""
import random
import sys
import logging
from typing import List, Type

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DerivativeGenerator:
    """Generator chính cho các câu hỏi tối ưu hóa đạo hàm"""

    # Danh sách các class câu hỏi có sẵn
    QUESTION_TYPES = [
        PoolOptimization,
        FenceOptimization,
        CableOptimization,
        TravelOptimization,
        RentalOptimization
    ]

    @classmethod
    def generate_question(cls, question_number: int, question_type: Type[BaseDerivativeQuestion] = None) -> str:
        """Generate một câu hỏi cụ thể"""
        logging.info(f"Generating question {question_number}")

        if question_type is None:
            question_type = random.choice(cls.QUESTION_TYPES)

        try:
            question_instance = question_type()
            return question_instance.generate_full_question(question_number)
        except Exception as e:
            logging.error(f"Error generating question {question_number}: {e}")
            raise

    @classmethod
    def generate_multiple_questions(cls, num_questions: int = 5, typed: int = None) -> List[str]:
        """Generate nhiều câu hỏi"""
        logging.info(f"Generating {num_questions} questions")

        questions = []
        for i in range(1, num_questions + 1):
            if typed == None:
                question_type = random.choice(cls.QUESTION_TYPES)
            else:
                question_type = cls.QUESTION_TYPES[typed-1]

            try:
                question = cls.generate_question(i, question_type)
                questions.append(question)
                logging.info(f"Successfully generated question {i}")
            except Exception as e:
                logging.error(f"Failed to generate question {i}: {e}")
                # Thử lại với loại câu hỏi khác
                try:
                    question_type = random.choice(cls.QUESTION_TYPES)
                    question = cls.generate_question(i, question_type)
                    questions.append(question)
                    logging.info(f"Successfully generated question {i} on retry")
                except Exception as e2:
                    logging.error(f"Failed to generate question {i} on retry: {e2}")
                    continue

        return questions

    @classmethod
    def generate_multiple_questions_with_format(cls, num_questions: int = 5, typed: int = None, fmt: int = 1):
        """Generate nhiều câu hỏi với format cụ thể"""
        logging.info(f"Generating {num_questions} questions with format {fmt}")

        if fmt == 1:
            # Format 1: sử dụng generate_full_question
            return cls.generate_multiple_questions(num_questions, typed)
        else:
            # Format 2: sử dụng generate_question_only
            questions_data = []
            for i in range(1, num_questions + 1):
                if typed == None:
                    question_type = random.choice(cls.QUESTION_TYPES)
                else:
                    question_type = cls.QUESTION_TYPES[typed-1]

                try:
                    question_instance = question_type() if question_type else random.choice(cls.QUESTION_TYPES)()
                    question_content, correct_answer = question_instance.generate_question_only(i)
                    questions_data.append((question_content, correct_answer))
                    logging.info(f"Successfully generated question {i} {question_type}")
                except Exception as e:
                    logging.error(f"Failed to generate question {i}: {e}")
                    # Thử lại với loại câu hỏi khác
                    try:
                        question_type = random.choice(cls.QUESTION_TYPES)
                        question_instance = question_type()
                        question_content, correct_answer = question_instance.generate_question_only(i)
                        questions_data.append((question_content, correct_answer))
                        logging.info(f"Successfully generated question {i} on retry")
                    except Exception as e2:
                        logging.error(f"Failed to generate question {i} on retry: {e2}")
                        continue

            return questions_data

    @classmethod
    def create_latex_file(cls, questions: List[str], filename: str = "derivative_optimization_questions.tex",
                          title: str = "Câu hỏi Trắc nghiệm về Tối ưu hóa Đạo hàm") -> str:
        """Tạo file LaTeX hoàn chỉnh"""
        logging.info(f"Creating LaTeX file: {filename}")

        latex_content = BaseDerivativeQuestion.create_latex_document(questions, title)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(latex_content)

            logging.info(f"Successfully wrote LaTeX content to {filename}")
            return filename
        except Exception as e:
            logging.error(f"Error writing to file {filename}: {e}")
            raise

    @classmethod
    def create_latex_file_with_format(cls, questions_data, filename: str = "derivative_optimization_questions.tex",
                                    title: str = "Câu hỏi Trắc nghiệm về Tối ưu hóa Đạo hàm", fmt: int = 1) -> str:
        """Tạo file LaTeX hoàn chỉnh với format cụ thể"""
        logging.info(f"Creating LaTeX file: {filename} with format {fmt}")

        latex_content = BaseDerivativeQuestion.create_latex_document_with_format(questions_data, title, fmt)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(latex_content)

            logging.info(f"Successfully wrote LaTeX content to {filename}")
            return filename
        except Exception as e:
            logging.error(f"Error writing to file {filename}: {e}")
            raise


def main():
    """Hàm main với hỗ trợ 2 format như force_resultant_question.py"""
    try:
        # Số câu hỏi và định dạng từ command line
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        fmt = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] in ['1','2'] else 1
        question_type = int(sys.argv[3]) if(len(sys.argv)) > 3 else None
        
        # Tạo nội dung LaTeX với định dạng
        generator = DerivativeGenerator()
        if len(sys.argv) > 1:
            # Generate all questions với format (có thể trùng dạng)
            questions_data = generator.generate_multiple_questions_with_format(num_questions, question_type, fmt=fmt)
        else:
            # Mặc định: sinh đúng 5 câu hỏi, mỗi câu 1 dạng
            if fmt == 1:
                questions_data = []
                for i, qtype in enumerate(DerivativeGenerator.QUESTION_TYPES, 1):
                    try:
                        question = DerivativeGenerator.generate_question(i, qtype)
                        questions_data.append(question)
                    except Exception as e:
                        print(f"Failed to generate question {i}: {e}")
                        continue
            else:
                questions_data = []
                for i, qtype in enumerate(DerivativeGenerator.QUESTION_TYPES, 1):
                    try:
                        question_instance = qtype()
                        question_content, correct_answer = question_instance.generate_question_only(i)
                        questions_data.append((question_content, correct_answer))
                    except Exception as e:
                        print(f"Failed to generate question {i}: {e}")
                        continue
        
        if not questions_data:
            print("Error: No questions were generated successfully")
            sys.exit(1)
        
        # Tạo LaTeX content với format
        latex_content = BaseDerivativeQuestion.create_latex_document_with_format(questions_data, fmt=fmt)
        
        # Ghi file
        filename = "derivative_optimization_questions.tex"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        print(f"Generated {filename} with {len(questions_data)} question(s). Compile with XeLaTeX.")
        
        # In thông tin về câu hỏi được tạo
        print(f"\nChi tiết:")
        print(f"- Số câu hỏi: {num_questions}")
        print(f"- Format: {fmt} ({'đáp án ngay sau câu hỏi' if fmt == 1 else 'đáp án ở cuối'})")
        print(f"- File LaTeX output: {filename}")
        print(f"- Để biên dịch: xelatex {filename}")
        
    except ValueError as e:
        print("Error: Please provide a valid number for questions")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()