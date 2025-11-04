import argparse
import logging
import random
import re
import sys
from abc import ABC, abstractmethod
from typing import Dict
from typing import List, Type, Any, Optional


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
        Tạo câu hỏi (phiên bản chỉ còn 1 format: đáp án xuất hiện ngay sau lời giải).

        Args:
            question_number (int): Số thứ tự câu hỏi.
            include_multiple_choice (bool): Tham số giữ tương thích, hiện luôn True trong luồng sử dụng.

        Returns:
            str: Nội dung câu hỏi đầy đủ (đề + lời giải).

        Raises:
            ValueError: Nếu số đáp án sai sinh ra không đúng hoặc trùng lặp.
        """
        print(f"Đang tạo câu hỏi {question_number}")

        # Sinh tham số và tính toán chung
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        question_text = self.generate_question_text()
        solution = self.generate_solution()

        # Tạo nội dung cơ bản
        question_content = f"Câu {question_number}: {question_text}\n\n"

        # Chỉ áp dụng luồng Đúng/Sai nếu đáp án thực sự là "Đúng" hoặc "Sai"
        is_true_false = isinstance(self.correct_answer, str) and self.correct_answer.strip() in {"Đúng", "Sai"}

        if include_multiple_choice and is_true_false:
            # Tạo câu hỏi dạng mệnh đề Đúng/Sai (không hiển thị lựa chọn A/B)
            self.wrong_answers = self.generate_wrong_answers()

            # Kiểm soát số lượng đáp án sai cho dạng Đúng/Sai
            if len(self.wrong_answers) != 1:
                raise ValueError(
                    f"generate_wrong_answers() phải trả về đúng 1 đáp án sai cho dạng Đúng/Sai, nhưng đã trả về {len(self.wrong_answers)} đáp án"
                )

            correct_answer_summary = self.correct_answer.strip()
            all_answers = [correct_answer_summary] + self.wrong_answers
            if len(set(all_answers)) != 2:
                duplicates = [ans for ans in all_answers if all_answers.count(ans) > 1]
                raise ValueError(
                    f"Có đáp án trùng nhau: {duplicates}. Đáp án đúng và sai phải khác nhau."
                )

            question_content += f"\n\n{solution}\n\n"
            return question_content

        # Mặc định: không phải dạng Đúng/Sai → chỉ in đề và lời giải
        question_content += f"\n\n{solution}\n\n"
        return question_content


# ========================================================================================
# PHẦN 2: TikZ Figure Library
# ========================================================================================


def generate_rational11_increasing_tikz(params: Dict[str, Any]) -> str:
    """Bảng biến thiên dạng tăng (hai nhánh cùng tăng)."""
    D, E = params["D"], params["E"]
    line = "+,d,+"
    inf_left = "+\\infty"
    inf_right = "-\\infty"
    A_coord = "N13"
    D_coord = "N32"
    arrow_pairs = "A/B,C/D"
    return f"""\\begin{{tikzpicture}}[>=stealth, scale=1]
\t\\tkzTabInit[lgt=2,espcl=4]
\t{{$x$/0.8,$f'(x)$/0.8,$f(x)$/3}}
\t{{$-\\infty$,$ {D} $,$+\\infty$}}
\t\\tkzTabLine{{,{line},}}
\t\\path
\t({A_coord})node[shift={{(0,0.2)}}](A){{$ {E} $}}
\t(N22)node[shift={{(-0.5,-0.2)}}](B){{$ {inf_left} $}}
\t(N23)node[shift={{(0.5,0.2)}}](C){{$ {inf_right} $}}
\t({D_coord})node[shift={{(0,-0.2)}}](D){{$ {E} $}};
\t\\foreach\\X/\\Y in{{{arrow_pairs}}}\\draw[->](\\X)--(\\Y);
\t\\draw[double,double distance=2pt](N22)--(N23);
\\end{{tikzpicture}}"""


def generate_rational11_decreasing_tikz(params: Dict[str, Any]) -> str:
    """Bảng biến thiên dạng giảm (hai nhánh cùng giảm)."""
    D, E = params["D"], params["E"]
    Df = format_number_clean(D)
    Ef = format_number_clean(E)
    return f"""\\begin{{tikzpicture}}
\t\\tkzTabInit[nocadre=false,lgt=0.8,espcl=3]
\t{{$x$ /0.6,$y'$ /0.6,$y$ /2}}
\t{{$-\\infty$,$ {Df} $,$+\\infty$}}
\t\\tkzTabLine{{,-,d,-,}}
\t\\tkzTabVar{{+/${Ef}$,-D+/$-\\infty$/$+\\infty$,-/${Ef}$}}
\\end{{tikzpicture}}"""


def generate_rational11_tikz(params: Dict[str, Any]) -> str:
    """
    Wrapper tương thích: gọi bảng tăng/giảm theo tham số `is_increasing`.
    """
    is_increasing = params.get("is_increasing", False)
    if is_increasing:
        return generate_rational11_increasing_tikz(params)
    return generate_rational11_decreasing_tikz(params)


# ========================================================================================
# PHẦN 3: LaTeX Utils
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
# PHẦN 4: RationalLinearOverLinearQuestion: Hàm bậc 1/1
# ========================================================================================

class RationalLinearOverLinearQuestion(BaseOptimizationQuestion):
    """
    Dạng: Hàm phân thức bậc 1/1: y = (a x + b1) / (u x + b2).
    Dựa vào đồ thị kiểu Bậc 1-1: tiệm cận đứng x = D, tiệm cận ngang y = E.
    Câu hỏi: (1) tổ hợp hệ số p a + q b1 + r u + s b2, hoặc (2) tính f(x0).
    """

    def generate_parameters(self) -> Dict[str, Any]:
        attempts = 0
        while attempts < 200:
            attempts += 1
            # Chọn tham số đẹp trong [-5..5]
            D = random.choice([i for i in range(-3, 4) if i != 0])
            E = random.randint(-3, 3)
            u = random.choice([-3, -2, 2, 3])  # tránh u quá nhỏ 1 để b2 gọn hơn

            b2 = -u * D
            a = u * E

            # Chọn tính đơn điệu ngẫu nhiên
            is_increasing = random.choice([True, False])

            # Chọn s theo dấu mong muốn của y' (sgn(u*s))
            s_sign = 1 if is_increasing else -1
            s_val = s_sign if u > 0 else -s_sign
            # b1 = E*b2 - s, khi đó a*b2 - u*b1 = u*s  => dấu theo u*s
            b1 = E * b2 - s_val

            # Hạn chế trị tuyệt đối các hệ số
            if all(abs(v) <= 20 for v in [a, b1, u, b2]):
                # Chọn biến thể câu hỏi
                if random.random() < 0.5:
                    question_type = "linear_comb"
                    nz = [-3, -2, -1, 1, 2, 3]
                    p = random.choice(nz)
                    s = random.choice(nz)
                    params = {
                        "D": D, "E": E, "a": a, "b1": b1, "u": u, "b2": b2,
                        "question_type": question_type,
                        "p": p, "q": 0, "s": s,
                        "is_increasing": is_increasing
                    }
                else:
                    question_type = "value_at_point"
                    x_candidates = [x for x in range(-3, 4) if x != D]
                    x0 = random.choice(x_candidates)
                    params = {
                        "D": D, "E": E, "a": a, "b1": b1, "u": u, "b2": b2,
                        "question_type": question_type,
                        "x0": x0,
                        "is_increasing": is_increasing
                    }
                return params

        raise ValueError("Không tìm được bộ tham số phù hợp cho hàm bậc 1/1")

    def calculate_answer(self) -> str:
        if not self.parameters:
            self.parameters = self.generate_parameters()
        p = self.parameters
        a, b1, u, b2 = p["a"], p["b1"], p["u"], p["b2"]

        if p["question_type"] == "linear_comb":
            value = p["p"] * a + p["s"] * b2
            return str(value)
        else:
            x0 = p["x0"]
            value = (a * x0 + b1) / (u * x0 + b2)
            # Trả về số nguyên nếu gần nguyên, ngược lại làm tròn 2 chữ số thập phân (văn bản thuần)
            if abs(value - int(round(value))) < 1e-9:
                return str(int(round(value)))
            return f"{value:.2f}"

    def generate_question_text(self) -> str:
        if not self.parameters:
            self.parameters = self.generate_parameters()
        p = self.parameters
        figure = generate_rational11_tikz(p)
        
        # Format toàn bộ hàm số để xử lý dấu chính xác
        b1f = format_number_clean(p["b1"])
        uf = format_number_clean(p["u"])
        
        # Tạo tử số với dấu chính xác
        if p["b1"] >= 0:
            numerator = f"a x + {b1f}"
        else:
            numerator = f"a x - {abs(p['b1'])}"
        
        # Tạo mẫu số
        denominator = f"{uf} x + b"
        
        function_expr = f"\\dfrac{{{numerator}}}{{{denominator}}}"
        
        if p["question_type"] == "linear_comb":
            question_parts = []
            pp = p["p"]
            ss = p["s"]
            
            # Phần pa (giống logic trong lời giải)
            if pp == 1:
                question_parts.append("a")
            elif pp == -1:
                question_parts.append("-a")
            else:
                question_parts.append(f"{format_number_clean(pp)}a")
            
            # Phần sb (giống logic trong lời giải)
            if ss > 0:
                if ss == 1:
                    question_parts.append("+ b")
                else:
                    question_parts.append(f"+ {format_number_clean(ss)}b")
            else:
                if ss == -1:
                    question_parts.append("- b")
                else:
                    question_parts.append(f"- {format_number_clean(abs(ss))}b")
            
            question_expr = " ".join(question_parts)
            question = f"Tính giá trị của \\({question_expr}\\)."
        else:
            question = f"Tính \\(f({p['x0']})\\)."
        return f"""Cho bảng biến thiên của hàm số \\(y={function_expr}\\) dưới đây:
 
 {figure}
 
 {question}"""

    def generate_solution(self) -> str:
        p = self.parameters
        D, E, a, b1, u, b2 = p["D"], p["E"], p["a"], p["b1"], p["u"], p["b2"]

        # Định dạng số
        Df = format_number_clean(D)
        Ef = format_number_clean(E)
        af = format_number_clean(a)
        b1f = format_number_clean(b1)
        uf = format_number_clean(u)
        b2f = format_number_clean(b2)

        lines = []
        lines.append("Lời giải.")
        lines.append(f"Tiệm cận đứng: \\(x={Df} \\Leftrightarrow -\\dfrac{{b}}{{{uf}}}={Df} \\Rightarrow b={b2f}\\)")
        lines.append(f"Tiệm cận ngang: \\(y={Ef} \\Leftrightarrow \\dfrac{{a}}{{{uf}}}={Ef} \\Rightarrow a={af}\\)")

        # Format hàm số hoàn chỉnh với dấu chính xác
        # Tử số
        if b1 >= 0:
            fx_numerator = f"{af}x + {b1f}"
        else:
            fx_numerator = f"{af}x - {format_number_clean(abs(b1))}"
        
        # Mẫu số  
        if b2 >= 0:
            fx_denominator = f"{uf}x + {b2f}"
        else:
            fx_denominator = f"{uf}x - {format_number_clean(abs(b2))}"
            
        fx_expr = f"\\dfrac{{{fx_numerator}}}{{{fx_denominator}}}"
        lines.append(f"Suy ra \\(f(x)={fx_expr}\\). ")

        if p["question_type"] == "linear_comb":
            value_str = self.calculate_answer()
            try:
                value_fmt = format_number_clean(float(value_str))
            except Exception:
                value_fmt = format_number_clean(value_str)

            pp = p["p"]
            ss = p["s"]
            
            # Format biểu thức tính toán với dấu chính xác
            calc_parts = []
            
            # Phần pa
            if pp == 1:
                calc_parts.append("a")
            elif pp == -1:
                calc_parts.append("-a")
            else:
                calc_parts.append(f"{format_number_clean(pp)}a")
            
            # Phần sb
            if ss > 0:
                if ss == 1:
                    calc_parts.append("+ b")
                else:
                    calc_parts.append(f"+ {format_number_clean(ss)}b")
            else:
                if ss == -1:
                    calc_parts.append("- b")
                else:
                    calc_parts.append(f"- {format_number_clean(abs(ss))}b")
            
            calc_expr = " ".join(calc_parts)
            lines.append(f"Tính được \\({calc_expr} = {value_fmt}\\). ")
        else:
            x0 = p["x0"]
            x0f = format_number_clean(x0)
            value_str = self.calculate_answer()
            try:
                value_fmt = format_number_clean(float(value_str))
            except Exception:
                value_fmt = format_number_clean(value_str)

            # Format tử số và mẫu số với dấu chính xác
            # Tử số: af*x0 + b1f
            term1 = f"{af} \\cdot {x0f}" if x0 >= 0 else f"{af} \\cdot ({x0f})"
            if b1 >= 0:
                numer = f"{term1} + {b1f}"
            else:
                numer = f"{term1} - {format_number_clean(abs(b1))}"
            
            # Mẫu số: uf*x0 + b2f  
            term2 = f"{uf} \\cdot {x0f}" if x0 >= 0 else f"{uf} \\cdot ({x0f})"
            if b2 >= 0:
                denom = f"{term2} + {b2f}"
            else:
                denom = f"{term2} - {format_number_clean(abs(b2))}"
                
            lines.append(f"Tính \\(f({x0f}) = \\dfrac{{{numer}}}{{{denom}}} = {value_fmt}\\). ")

        lines_with_breaks = [f"{ln} \\\\" for ln in lines]
        return "\n" + "\n".join(lines_with_breaks) + "\n"

    def generate_question(self, question_number: int = 1, include_multiple_choice: bool = True):
        print(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        answer = self.calculate_answer()
        question_text = self.generate_question_text()
        solution = self.generate_solution()
        content = f"Câu {question_number}: {question_text}\n\n{solution}\n\nĐáp án: {answer}\n\n"
        return content

    def generate_wrong_answers(self) -> List[str]:
        # Không dùng trong format hiện tại; trả về placeholder để thỏa abstract
        return ["Sai"]


# ========================================================================================
# PHẦN 5: Hàm main để chạy độc lập
# ========================================================================================

class QuestionManager:
    """Manager đơn giản để sinh câu hỏi"""

    def __init__(self, question_types: Optional[List[Type]] = None):
        # Nếu không truyền danh sách dạng câu hỏi, dùng mặc định
        # Tránh lỗi random.choice(None) gây "object of type 'NoneType' has no len()"
        if question_types is None:
            self.question_types = [RationalLinearOverLinearQuestion]
        else:
            self.question_types = question_types
        self.failed_count = 0

    def generate_questions(self, num_questions: int, verbose: bool = False) -> List[str]:
        if num_questions <= 0:
            raise ValueError("Số câu hỏi phải lớn hơn 0")
        questions_data: List[str] = []
        if verbose:
            print(f"📋 Bắt đầu sinh {num_questions} câu hỏi (format 1)")
        for i in range(1, num_questions + 1):
            try:
                question_type = random.choice(self.question_types)
                question_instance = question_type()
                result = question_instance.generate_question(i, include_multiple_choice=True)
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

    def build_document(self, questions_data: List[Any], title: str, author: str = "dev") -> str:
        if not questions_data:
            raise ValueError("Danh sách câu hỏi không được rỗng")
        if not title.strip():
            raise ValueError("Tiêu đề không được rỗng")

        # Tạo header
        latex_content = self.template.DOCUMENT_HEADER.format(title=title, author=author)

        # Xử lý content theo format
        if not all(isinstance(q, str) for q in questions_data):
            raise ValueError("Tất cả items phải là string trong format 1")
        latex_content += "\n\n".join(questions_data)

        # Thêm footer
        latex_content += self.template.DOCUMENT_FOOTER
        return latex_content


# Hằng số cấu hình mặc định (bỏ DEFAULT_FORMAT)
DEFAULT_NUM_QUESTIONS = 3
DEFAULT_FILENAME = "optimization_questions.tex"
DEFAULT_TITLE = "Câu hỏi Tối ưu hóa"


def parse_arguments() -> argparse.Namespace:
    """Xử lý tham số dòng lệnh"""
    parser = argparse.ArgumentParser(
        description="Generator câu hỏi tối ưu hóa (chỉ format 1 - đáp án ngay sau câu hỏi)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python3 ham_so_bac_1_1.py            # Tạo 3 câu hỏi
  python3 ham_so_bac_1_1.py 5          # Tạo 5 câu hỏi
  python3 ham_so_bac_1_1.py -n 10 -o test.tex  # Tùy chỉnh số câu & tên file
        """
    )
    parser.add_argument('num_questions', nargs='?', type=int, default=DEFAULT_NUM_QUESTIONS,
                        help=f'Số câu hỏi cần tạo (mặc định: {DEFAULT_NUM_QUESTIONS})')
    parser.add_argument('-n', '--num-questions', type=int, dest='num_questions_override',
                        help='Số câu hỏi cần tạo (ghi đè positional)')
    parser.add_argument('-o', '--output', type=str, default=DEFAULT_FILENAME,
                        help=f'Tên file output (mặc định: {DEFAULT_FILENAME})')
    parser.add_argument('-t', '--title', type=str, default=DEFAULT_TITLE,
                        help=f'Tiêu đề document (mặc định: "{DEFAULT_TITLE}")')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Hiển thị thông tin chi tiết')
    args = parser.parse_args()
    if args.num_questions_override is not None:
        args.num_questions = args.num_questions_override
    if args.num_questions <= 0:
        parser.error("Số câu hỏi phải lớn hơn 0")
    return args


def generate_questions(num_questions: int, verbose: bool = False) -> List[Any]:
    """Sinh danh sách câu hỏi tối ưu hóa"""
    manager = QuestionManager()
    return manager.generate_questions(num_questions, verbose)


def create_latex_file(questions_data: List, filename: str, title: str) -> None:
    """Tạo file LaTeX chứa danh sách câu hỏi"""
    try:
        latex_builder = LaTeXDocumentBuilder()
        latex_content = latex_builder.build_document(questions_data, title)

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
        questions_data = generate_questions(args.num_questions, args.verbose)

        if not questions_data:
            print("❌ Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)

        # Create LaTeX file
        create_latex_file(questions_data, args.output, args.title)

        # Success messages
        print(f"✅ Đã tạo thành công {args.output} với {len(questions_data)} câu hỏi (format 1)")
        print(f"📄 Biên dịch bằng: xelatex {args.output}")

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

