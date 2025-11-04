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
        Tạo câu hỏi

        Args:
            question_number (int): Số thứ tự câu hỏi.
            include_multiple_choice (bool): Giữ để tương thích; hiện luôn dùng True.

        Returns:
            str: Nội dung câu hỏi (đề + lời giải, có thể kèm đáp án tóm tắt nếu cần).

        Raises:
            ValueError: Nếu số lượng đáp án sai sinh ra không đúng yêu cầu hoặc trùng lặp.
        """
        print(f"Đang tạo câu hỏi {question_number}")

        # Sinh tham số và tính toán chung
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        question_text = self.generate_question_text()
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

            question_content += f"\n\n{solution}\n\n"
            return question_content
        else:
            # Nhánh này hiện không còn được sử dụng (format 2 đã loại bỏ) nhưng vẫn trả string để tránh lỗi
            question_content += f"\n\n{solution}\n\n"
            return question_content


# ========================================================================================
# PHẦN 2: TikZ Figure Library
# ========================================================================================


def generate_cubic_graph_tikz(params: Dict[str, Any]) -> str:
    """
    Sinh tikzpicture vẽ đồ thị y = a x^3 + b x^2 + c x + d, kèm đường gợi ý qua
    hai điểm cực trị (t, v) và (u, e).
    """
    a, b, c, d = params["a"], params["b"], params["c"], params["d"]
    t, u = params["t"], params["u"]
    v, e = params["v"], params["e"]
    xt, xp = params["xt"], params["xp"]
    yd, yt = params["yd"], params["yt"]

    # Dùng TỈ LỆ ĐỒNG NHẤT cho cả hai trục để 1 đơn vị trên trục x = 1 đơn vị trên trục y
    # Điều này tránh hiện tượng -1 trên trục x không thẳng hàng với -1 trên trục y.
    x_range = max(1, abs(xp - xt))
    y_range = max(1, abs(yt - yd))
    biggest_span = max(x_range, y_range)
    # Mục tiêu kích thước ~6cm theo chiều lớn hơn; kẹp để không quá to/nhỏ
    uniform_scale = max(0.25, min(0.75, 6.0 / biggest_span))

    # Nhãn: chỉ in một số 0 tại gốc, bỏ nhãn nếu t/u/v/e bằng 0
    label_lines = ["\t\\node at (0,0) [below left]{$0$};"]
    if t != 0:
        label_lines.append(f"\t\\draw ({t},0) node [below]{{$ {t} $}};")
    if u != 0:
        label_lines.append(f"\t\\draw ({u},0) node [below]{{$ {u} $}};")
    if v != 0:
        label_lines.append(f"\t\\draw (0,{v}) node [left]{{$ {v} $}};")
    if e != 0:
        label_lines.append(f"\t\\draw (0,{e}) node [left]{{$ {e} $}};")
    labels_block = "\n".join(label_lines)

    return f"""\\begin{{tikzpicture}}[scale={uniform_scale:.3f}, font=\\footnotesize, line join=round, line cap=round, >=stealth]
\t\\def\\a{{{a}}} \\def\\b{{{b}}} \\def\\c{{{c}}} \\def\\d{{{d}}}
\t\\def\\xt{{{xt}}} \\def\\xp{{{xp}}} \\def\\yt{{{yt}}} \\def\\yd{{{yd}}}
\t\\draw[->] (\\xt,0)--(\\xp,0) node [below]{{$x$}};
\t\\draw[->] (0,\\yd)--(0,\\yt) node [left]{{$y$}};
\t\\clip (\\xt-0.1,\\yd+0.1) rectangle (\\xp-0.1,\\yt-0.1);
\t\\draw[smooth,samples=180,domain=\\xt:\\xp] plot(\\x,{{\\a*(\\x)^3+\\b*(\\x)^2+\\c*(\\x)+\\d}});
\t\\draw[dashed,thin]({t},0)--({t},{v})--(0,{v});
\t\\draw[dashed,thin]({u},0)--({u},{e})--(0,{e});
{labels_block}
\\end{{tikzpicture}}"""


def generate_monotonicity_table_tikz(params: Dict[str, Any]) -> str:
    """
    Sinh bảng biến thiên (tkz-tab) cho hàm bậc ba dựa trên hai điểm cực trị (t, v), (u, e).
    - Gọi x1 = min(t,u), x2 = max(t,u). Với a>0: f' dấu +,0,-,0,+ và f(x) tăng-giảm-tăng
      với các mức cực đại/cực tiểu tương ứng; với a<0 thì ngược lại.
    """
    a = params["a"]
    t, u = params["t"], params["u"]
    v, e = params["v"], params["e"]

    # Sắp xếp theo trục x
    x1, x2 = (t, u) if t < u else (u, t)
    y1 = v if x1 == t else e
    y2 = e if x2 == u else v

    # Dòng dấu của f'(x)
    if a > 0:
        sign_line = ",+,0,-,0,+,"
        # x1 là cực đại, x2 là cực tiểu
        big_val = y1
        small_val = y2
        var_line = f"-/$-\\infty$,+/${{ {big_val} }}$,-/${{ {small_val} }}$,+/$+\\infty$"
    else:
        sign_line = ",-,0,+,0,-,"
        # x1 là cực tiểu, x2 là cực đại
        small_val = y1
        big_val = y2
        var_line = f"+/$+\\infty$,-/${{ {small_val} }}$,+/${{ {big_val} }}$,-/$-\\infty$"

    x1_tex = format_number_clean(x1)
    x2_tex = format_number_clean(x2)

    return (
        "\\begin{tikzpicture}[>=stealth, scale=1]\n"
        "\t\\tkzTabInit[lgt=2,espcl=2.7]\n"
        "\t{$x$/0.8,$f'(x)$/0.8,$f(x)$/3}\n"
        f"\t{{$-\\infty$,$ {x1_tex} $,$ {x2_tex} $,$+\\infty$}}\n"
        f"\t\\tkzTabLine{{{sign_line}}}\n"
        f"\t\\tkzTabVar{{{var_line}}}\n"
        "\\end{tikzpicture}"
    )


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
    if str(a) == '-\\infty' or str(a) == '-infinity':
        a_str = "-\\infty"
    else:
        a_str = format_number_clean(a) if isinstance(a, (int, float)) else str(a)

    if str(b) == '+\\infty' or str(b) == '+infinity':
        b_str = "+\\infty"
    else:
        b_str = format_number_clean(b) if isinstance(b, (int, float)) else str(b)

    return f"{left}{a_str}; {b_str}{right}"


# ========================================================================================
# PHẦN 4: CubicFunctionGraphQuestion: Hàm bậc 3
# ========================================================================================

class CubicFunctionGraphQuestion(BaseOptimizationQuestion):
    """
    Dạng mới: Cho đồ thị hàm bậc ba y = f(x), biết hai điểm cực trị (t, v), (u, e)
    suy ra hệ số nguyên a, b, c, d, rồi hỏi 1 câu: tổ hợp hệ số hoặc giá trị f(x0).
    """

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh (t,u,v,e) rồi giải hệ để thu a,b,c,d nguyên (|coef|≤10)."""
        from fractions import Fraction

        attempts = 0
        while attempts < 200:
            attempts += 1
            t = random.randint(-3, 3)
            u = random.randint(-3, 3)
            if t == u:
                continue
            v = random.randint(-5, 5)
            e = random.randint(-5, 5)
            if v == e:
                continue

            denom = (u - t) ** 3
            if denom == 0:
                continue

            a_frac = Fraction(2 * (v - e), denom)
            if a_frac.denominator != 1:
                continue
            a = a_frac.numerator

            b_frac = Fraction(-3 * a * (t + u), 2)
            if b_frac.denominator != 1:
                continue
            b = b_frac.numerator

            c = 3 * a * t * u

            d_frac = Fraction(v) - Fraction(a * t * t * (-t + 3 * u), 2)
            if d_frac.denominator != 1:
                continue
            d = d_frac.numerator

            if all(abs(coef) <= 10 for coef in (a, b, c, d)):
                xt = min(-3, t, u) - 1
                xp = max(3, t, u) + 1
                # Biên y dựa trên các mức quan sát được từ đề (tránh giá trị quá lớn làm méo tỷ lệ)
                y_min = min(v, e, 0)
                y_max = max(v, e, 0)
                base_range = max(2, y_max - y_min)
                # Đặt khoảng tối thiểu 6 và tối đa 20 để cân bằng với trục x
                target_range = min(20, max(6, base_range + 4))
                y_mid = (y_min + y_max) / 2
                yd = int(round(y_mid - target_range / 2))
                yt = int(round(y_mid + target_range / 2))

                if random.random() < 0.5:
                    question_type = "linear_comb"
                    while True:
                        p = random.randint(-3, 3)
                        q = random.randint(-3, 3)
                        r = random.randint(-3, 3)
                        s = random.randint(-3, 3)
                        if not (p == 0 and q == 0 and r == 0 and s == 0):
                            break
                    params = {
                        "t": t, "u": u, "v": v, "e": e,
                        "a": a, "b": b, "c": c, "d": d,
                        "xt": xt, "xp": xp, "yd": yd, "yt": yt,
                        "question_type": question_type,
                        "p": p, "q": q, "r": r, "s": s,
                        "representation": getattr(self, "representation", 1)
                    }
                else:
                    question_type = "value_at_point"
                    candidates = [x for x in range(-3, 4) if x not in (t, u)]
                    x0 = random.choice(candidates)
                    params = {
                        "t": t, "u": u, "v": v, "e": e,
                        "a": a, "b": b, "c": c, "d": d,
                        "xt": xt, "xp": xp, "yd": yd, "yt": yt,
                        "question_type": question_type,
                        "x0": x0,
                        "representation": getattr(self, "representation", 1)
                    }

                return params

        raise ValueError("Không tìm được bộ (t,u,v,e) cho hệ số nguyên trong 200 lần thử")

    def calculate_answer(self) -> str:
        """Trả về đáp án số (dạng chuỗi)."""
        if not self.parameters:
            self.parameters = self.generate_parameters()

        p = self.parameters
        a, b, c, d = p["a"], p["b"], p["c"], p["d"]

        if p["question_type"] == "linear_comb":
            value = p["p"] * a + p["q"] * b + p["r"] * c + p["s"] * d
            return str(value)
        else:
            x0 = p["x0"]
            value = a * x0 ** 3 + b * x0 ** 2 + c * x0 + d
            return str(value)

    def generate_question_text(self) -> str:
        """Sinh đề bài kèm đồ thị tikz và câu hỏi 1 dòng."""
        if not self.parameters:
            self.parameters = self.generate_parameters()

        p = self.parameters
        representation = p.get("representation", getattr(self, "representation", 1))
        if representation == 2:
            figure = generate_monotonicity_table_tikz(p)
            intro = "Cho bảng biến thiên của hàm số \\(y = a x^3 + b x^2 + c x + d\\) như sau."
        else:
            figure = generate_cubic_graph_tikz(p)
            intro = "Cho đồ thị của hàm số \\(y = a x^3 + b x^2 + c x + d\\) như hình vẽ dưới đây."

        if p["question_type"] == "linear_comb":
            # Format biểu thức với dấu chính xác
            pp, qq, rr, ss = p['p'], p['q'], p['r'], p['s']
            expr_parts = []
            
            # Phần pa
            if pp == 1:
                expr_parts.append("a")
            elif pp == -1:
                expr_parts.append("-a")
            else:
                expr_parts.append(f"{format_number_clean(pp)}a")
            
            # Phần qb
            if qq > 0:
                if qq == 1:
                    expr_parts.append("+ b")
                else:
                    expr_parts.append(f"+ {format_number_clean(qq)}b")
            elif qq < 0:
                if qq == -1:
                    expr_parts.append("- b")
                else:
                    expr_parts.append(f"- {format_number_clean(abs(qq))}b")
            
            # Phần rc  
            if rr > 0:
                if rr == 1:
                    expr_parts.append("+ c")
                else:
                    expr_parts.append(f"+ {format_number_clean(rr)}c")
            elif rr < 0:
                if rr == -1:
                    expr_parts.append("- c")
                else:
                    expr_parts.append(f"- {format_number_clean(abs(rr))}c")
            
            # Phần sd
            if ss > 0:
                if ss == 1:
                    expr_parts.append("+ d")
                else:
                    expr_parts.append(f"+ {format_number_clean(ss)}d")
            elif ss < 0:
                if ss == -1:
                    expr_parts.append("- d")
                else:
                    expr_parts.append(f"- {format_number_clean(abs(ss))}d")
            
            linear_expr = " ".join(expr_parts)
            question = f"Tính giá trị của \\({linear_expr}\\)."
        else:
            question = f"Tính \\(f({p['x0']})\\)."

        return f"""{intro}

{figure}

{question}"""

    def generate_solution(self) -> str:
        """Lời giải tóm tắt các bước suy ra a,b,c,d và kết quả cần tính."""
        p = self.parameters
        t, u, v, e = p["t"], p["u"], p["v"], p["e"]
        a, b, c, d = p["a"], p["b"], p["c"], p["d"]

        # Định dạng các số và biểu thức LaTeX
        tf, uf, vf, ef = (
            format_number_clean(t),
            format_number_clean(u),
            format_number_clean(v),
            format_number_clean(e),
        )
        af, bf, cf, df = (
            format_number_clean(a),
            format_number_clean(b),
            format_number_clean(c),
            format_number_clean(d),
        )

        lines = []
        lines.append("Lời giải.")
        if p.get("representation", getattr(self, "representation", 1)) == 2:
            lines.append(f"Từ bảng biến thiên, hai điểm cực trị là ({tf}, {vf}) và ({uf}, {ef}).")
        else:
            lines.append(f"Từ đồ thị, hai điểm cực trị là ({tf}, {vf}) và ({uf}, {ef}).")
        lines.append(r"Theo đề, hàm số có dạng \(f(x)=ax^3+bx^2+cx+d\), khi đó \(f'(x)=3ax^2+2bx+c\).")
        lines.append(fr"Vì \(({tf}, {vf})\) là cực trị nên ta có hệ:")
        # Format with \cdot and proper parentheses handling
        tf_formatted = tf if t >= 0 else f"({tf})"
        lines.append(fr"\(\begin{{cases}}3a \cdot {tf_formatted}^2+2b \cdot {tf_formatted}+c=0\\ a \cdot {tf_formatted}^3+b \cdot {tf_formatted}^2+c \cdot {tf_formatted}+d={vf}\end{{cases}}\)")
        
        # Hệ chuẩn hóa cho điểm (t,v)
        def format_equation_term(coeff, var):
            if coeff == 0:
                return ""
            elif coeff == 1:
                return f"+ {var}" if var else "+ 1"
            elif coeff == -1:
                return f"- {var}" if var else "- 1"
            elif coeff > 0:
                return f"+ {format_number_clean(coeff)}{var}"
            else:
                return f"- {format_number_clean(abs(coeff))}{var}"
        
        def build_equation_left_side(terms):
            """Build left side of equation from list of (coeff, var) tuples"""
            result_parts = []
            for i, (coeff, var) in enumerate(terms):
                if coeff == 0:
                    continue
                
                # Check if this is effectively the first term to display
                is_first_display = len(result_parts) == 0
                
                if is_first_display:  # First term to display
                    if coeff == 1:
                        result_parts.append(var if var else "1")
                    elif coeff == -1:
                        result_parts.append(f"-{var}" if var else "-1")
                    else:
                        result_parts.append(f"{format_number_clean(coeff)}{var}")
                else:  # Subsequent terms
                    term_str = format_equation_term(coeff, var)
                    if term_str:
                        result_parts.append(term_str)
            
            if not result_parts:
                return "0"
            return " ".join(result_parts)
        
        # Phương trình 1: 3a*t^2 + 2b*t + c = 0
        t2 = t * t
        t3 = t * t * t
        eq1_terms = [(3 * t2, "a"), (2 * t, "b"), (1, "c")]
        eq1 = f"{build_equation_left_side(eq1_terms)} = 0"
        
        # Phương trình 2: a*t^3 + b*t^2 + c*t + d = v
        eq2_terms = [(t3, "a"), (t2, "b"), (t, "c"), (1, "d")]
        eq2 = f"{build_equation_left_side(eq2_terms)} = {vf}"
        
        lines.append(fr"\(\Leftrightarrow \begin{{cases}}{eq1}\\ {eq2}\end{{cases}}\)")
        
        lines.append(fr"Vì \(({uf}, {ef})\) là cực trị nên ta có hệ:")
        # Format with \cdot and proper parentheses handling
        uf_formatted = uf if u >= 0 else f"({uf})"
        lines.append(fr"\(\begin{{cases}}3a \cdot {uf_formatted}^2+2b \cdot {uf_formatted}+c=0\\ a \cdot {uf_formatted}^3+b \cdot {uf_formatted}^2+c \cdot {uf_formatted}+d={ef}\end{{cases}}\)")
        
        # Hệ chuẩn hóa cho điểm (u,e)
        u2 = u * u
        u3 = u * u * u
        eq3_terms = [(3 * u2, "a"), (2 * u, "b"), (1, "c")]
        eq3 = f"{build_equation_left_side(eq3_terms)} = 0"
        
        eq4_terms = [(u3, "a"), (u2, "b"), (u, "c"), (1, "d")]
        eq4 = f"{build_equation_left_side(eq4_terms)} = {ef}"
        
        lines.append(fr"\(\Leftrightarrow \begin{{cases}}{eq3}\\ {eq4}\end{{cases}}\)")
        
        lines.append(fr"Suy ra \(a={af},\ b={bf},\ c={cf},\ d={df}\).")

        # Format hàm số f(x) với dấu chính xác
        fx_parts = []
        
        # Phần ax^3
        if a == 1:
            fx_parts.append("x^3")
        elif a == -1:
            fx_parts.append("-x^3")
        else:
            fx_parts.append(f"{af}x^3")
        
        # Phần bx^2
        if b > 0:
            if b == 1:
                fx_parts.append("+ x^2")
            else:
                fx_parts.append(f"+ {bf}x^2")
        elif b < 0:
            if b == -1:
                fx_parts.append("- x^2")
            else:
                fx_parts.append(f"- {format_number_clean(abs(b))}x^2")
        
        # Phần cx
        if c > 0:
            if c == 1:
                fx_parts.append("+ x")
            else:
                fx_parts.append(f"+ {cf}x")
        elif c < 0:
            if c == -1:
                fx_parts.append("- x")
            else:
                fx_parts.append(f"- {format_number_clean(abs(c))}x")
        
        # Phần d
        if d > 0:
            fx_parts.append(f"+ {df}")
        elif d < 0:
            fx_parts.append(f"- {format_number_clean(abs(d))}")
        
        fx_expr = " ".join(fx_parts)
        lines.append(f"\\(f(x)={fx_expr}\\). ")

        if p["question_type"] == "linear_comb":
            value = int(self.calculate_answer())
            pp, qq, rr, ss = p["p"], p["q"], p["r"], p["s"]
            
            # Format biểu thức tính toán với dấu chính xác
            calc_parts = []
            
            # Phần pa
            if pp == 1:
                calc_parts.append(f"{af}")
            elif pp == -1:
                calc_parts.append(f"-{af}")
            else:
                calc_parts.append(f"{format_number_clean(pp)} \\cdot {af}")
            
            # Phần qb
            if qq > 0:
                if qq == 1:
                    calc_parts.append(f"+ {bf}")
                else:
                    calc_parts.append(f"+ {format_number_clean(qq)} \\cdot {bf}")
            elif qq < 0:
                if qq == -1:
                    calc_parts.append(f"- {bf}")
                else:
                    calc_parts.append(f"- {format_number_clean(abs(qq))} \\cdot {bf}")
            
            # Phần rc
            if rr > 0:
                if rr == 1:
                    calc_parts.append(f"+ {cf}")
                else:
                    calc_parts.append(f"+ {format_number_clean(rr)} \\cdot {cf}")
            elif rr < 0:
                if rr == -1:
                    calc_parts.append(f"- {cf}")
                else:
                    calc_parts.append(f"- {format_number_clean(abs(rr))} \\cdot {cf}")
            
            # Phần sd
            if ss > 0:
                if ss == 1:
                    calc_parts.append(f"+ {df}")
                else:
                    calc_parts.append(f"+ {format_number_clean(ss)} \\cdot {df}")
            elif ss < 0:
                if ss == -1:
                    calc_parts.append(f"- {df}")
                else:
                    calc_parts.append(f"- {format_number_clean(abs(ss))} \\cdot {df}")
            
            calc_expr = " ".join(calc_parts)
            lines.append(f"Tính toán: \\({calc_expr} = {format_number_clean(value)}\\). ")
        else:
            x0 = p["x0"]
            value = int(self.calculate_answer())
            x0f = format_number_clean(x0)
            
            # Format biểu thức f(x0) với dấu chính xác
            calc_parts = []
            
            # Phần ax0^3
            term1 = f"{af} \\cdot ({x0f})^3" if x0 >= 0 else f"{af} \\cdot ({x0f})^3"
            calc_parts.append(term1)
            
            # Phần bx0^2
            term2 = f"{bf} \\cdot ({x0f})^2" if x0 >= 0 else f"{bf} \\cdot ({x0f})^2"
            if b >= 0:
                calc_parts.append(f"+ {term2}")
            else:
                calc_parts.append(f"- {format_number_clean(abs(b))} \\cdot ({x0f})^2")
            
            # Phần cx0
            term3 = f"{cf} \\cdot ({x0f})" if x0 >= 0 else f"{cf} \\cdot ({x0f})"
            if c >= 0:
                calc_parts.append(f"+ {term3}")
            else:
                calc_parts.append(f"- {format_number_clean(abs(c))} \\cdot ({x0f})")
            
            # Phần d
            if d >= 0:
                calc_parts.append(f"+ {df}")
            else:
                calc_parts.append(f"- {format_number_clean(abs(d))}")
            
            calc_expr = " ".join(calc_parts)
            lines.append(f"Tính \\(f({x0f}) = {calc_expr} = {format_number_clean(value)}\\). ")

        lines_with_breaks = []
        for ln in lines:
            stripped = ln.strip()
            if stripped.endswith("\\]"):
                # Dòng là display math, không thêm \\
                lines_with_breaks.append(ln)
            else:
                lines_with_breaks.append(ln + r" \\")
        return "\n" + "\n".join(lines_with_breaks) + "\n"

    def generate_question(self, question_number: int = 1, include_multiple_choice: bool = True):
        """Sinh câu hỏi dạng string duy nhất (format 1)."""
        print(f"Đang tạo câu hỏi {question_number}")

        self.parameters = self.generate_parameters()
        answer = self.calculate_answer()
        question_text = self.generate_question_text()
        solution = self.generate_solution()

        content = f"Câu {question_number}: {question_text}\n\n{solution}\n\n"

        if include_multiple_choice:
            # Trả về nội dung kèm đáp án ngay sau mỗi câu
            content += f"Đáp án: {answer}\n\n"
            return content
        else:
            return content

    def generate_wrong_answers(self) -> List[str]:
        """
        Sinh đáp án sai (nhiễu) cho dạng True/False

        Returns:
            List[str]: Danh sách chứa đúng 1 đáp án sai tổng thể
        """
        # Lấy đáp án đúng (là array 4 giá trị)
        correct_answers = self.calculate_answer()

        # Tạo đáp án sai tổng thể (ngược lại với đáp án đúng)
        # Ví dụ: nếu có ít nhất 1 câu đúng -> đáp án sai tổng thể là "Sai"
        #        nếu tất cả câu đều sai -> đáp án sai tổng thể là "Đúng"
        has_correct = any(answer == "Đúng" for answer in correct_answers)

        if has_correct:
            return ["Sai"]  # Nếu có câu đúng thì đáp án sai tổng thể là "Sai"
        else:
            return ["Đúng"]  # Nếu tất cả đều sai thì đáp án sai tổng thể là "Đúng"


# ========================================================================================
# PHẦN 6: Hàm main để chạy độc lập
# ========================================================================================

class QuestionManager:
    """Manager đơn giản để sinh câu hỏi"""

    def __init__(self, question_types: Optional[List[Type]] = None):
        # Nếu không truyền danh sách dạng câu hỏi, dùng mặc định
        # Tránh lỗi random.choice(None) gây "object of type 'NoneType' has no len()"
        if question_types is None:
            self.question_types = [CubicFunctionGraphQuestion]
        else:
            self.question_types = question_types
        self.failed_count = 0

    def generate_questions(self, num_questions: int, verbose: bool = False, representation: int = 1) -> List[str]:
        """Sinh danh sách câu hỏi (chỉ còn format 1)"""
        if num_questions <= 0:
            raise ValueError("Số câu hỏi phải lớn hơn 0")
        questions_data: List[str] = []
        if verbose:
            print(f"📋 Bắt đầu sinh {num_questions} câu hỏi (format 1)")
        for i in range(1, num_questions + 1):
            try:
                question_type = random.choice(self.question_types)
                question_instance = question_type()
                # Gắn kiểu biểu diễn: 1=đồ thị, 2=bảng biến thiên
                setattr(question_instance, "representation", 1 if representation != 2 else 2)
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
        """Tạo document LaTeX hoàn chỉnh (chỉ format 1)."""
        if not questions_data:
            raise ValueError("Danh sách câu hỏi không được rỗng")
        if not title.strip():
            raise ValueError("Tiêu đề không được rỗng")

        # Tạo header
        latex_content = self.template.DOCUMENT_HEADER.format(title=title, author=author)

        if not all(isinstance(q, str) for q in questions_data):
            raise ValueError("Tất cả items phải là string trong format 1")
        latex_content += "\n\n".join(questions_data)

        # Thêm footer
        latex_content += self.template.DOCUMENT_FOOTER
        return latex_content


# Hằng số cấu hình mặc định (đã bỏ DEFAULT_FORMAT)
DEFAULT_NUM_QUESTIONS = 3
DEFAULT_FILENAME = "optimization_questions.tex"
DEFAULT_TITLE = "Câu hỏi Tối ưu hóa"


def parse_arguments() -> argparse.Namespace:
    """Xử lý tham số dòng lệnh (đã bỏ lựa chọn format)."""
    parser = argparse.ArgumentParser(
        description="Generator câu hỏi tối ưu hóa (chỉ còn format 1 - đáp án ngay sau câu hỏi)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
    python3 ham_so_bac_3.py              # Tạo 3 câu hỏi (đồ thị)
    python3 ham_so_bac_3.py 5            # Tạo 5 câu hỏi (đồ thị)
    python3 ham_so_bac_3.py 9 2          # Tạo 9 câu hỏi (bảng biến thiên)
  python3 ham_so_bac_3.py -n 10 -o test.tex  # Tùy chỉnh số câu và tên file
        """
    )
    parser.add_argument('num_questions', nargs='?', type=int, default=DEFAULT_NUM_QUESTIONS,
                        help=f'Số câu hỏi cần tạo (mặc định: {DEFAULT_NUM_QUESTIONS})')
    parser.add_argument('representation', nargs='?', type=int, default=1,
                        help='Kiểu biểu diễn: 1=đồ thị, 2=bảng biến thiên (mặc định: 1)')
    parser.add_argument('-n', '--num-questions', type=int, dest='num_questions_override',
                        help='Số câu hỏi cần tạo (ghi đè positional argument)')
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
    if args.representation not in (1, 2):
        parser.error("representation phải là 1 (đồ thị) hoặc 2 (bảng biến thiên)")
    return args


def generate_questions(num_questions: int, verbose: bool = False, representation: int = 1) -> List[Any]:
    """Sinh danh sách câu hỏi tối ưu hóa (format 1)."""
    manager = QuestionManager()
    return manager.generate_questions(num_questions, verbose, representation)


def create_latex_file(questions_data: List, filename: str, title: str) -> None:
    """Tạo file LaTeX chứa danh sách câu hỏi (format 1)."""
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
        questions_data = generate_questions(args.num_questions, args.verbose, args.representation)

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
