import argparse
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import math
import sympy as sp


# ========================================================================================
# Tikzpicture class
# ========================================================================================
class Tikzpicture:
    def tikzpicture(self):
        return r"""
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
  
  \path 
  (0,0) coordinate (A)
  (4,0) coordinate (B)
  (4,4) coordinate (C)
  (0,4) coordinate (D)
  ($(A)!1/2!(B)$) coordinate (M)
  ($(B)!1/2!(C)$) coordinate (N)
  ($(C)!1/2!(D)$) coordinate (P)
  ($(D)!1/2!(A)$) coordinate (Q)
  ($(A)+(1.2,1.2)$) coordinate (A1)
  ($(B)+(-1.2,1.2)$) coordinate (B1)
  ($(C)+(-1.2,-1.2)$) coordinate (C1)
  ($(D)+(1.2,-1.2)$) coordinate (D1)
  ;
  \draw (A)--(B)--(C)--(D)--cycle;  
  \draw[fill=cyan,opacity=0.6] (M)--(B1)--(N)--(C1)--(P)--(D1)--(Q)--(A1)--cycle;  
  \draw[fill=orange,opacity=0.8] (A1)--(B1)--(C1)--(D1)--cycle;  
  \draw 
  (A1) node[below left]{Bỏ}
  (B1) node[below right]{Bỏ}
  (C1) node[above right]{Bỏ}
  (D1) node[above left]{Bỏ}
  ;
  
  
 \end{tikzpicture}
 \begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
  \path (0,-2)--(2,-2);
  \draw[->,scale=1,line width=4pt,red] (0.5,0)--(2.5,0)node[pos=0.5,above]{Gấp thành};
 \end{tikzpicture}
 \begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
  \def\dai{4}  \def\rong{1} \def\cao{3.5}
  \path 
  (0,0) coordinate (B)
  (1,\rong) coordinate (A)
  (\dai,1) coordinate (D)
  ($(B)+(D)-(A)$) coordinate (C)
  ($(B)!1/2!(D)$) coordinate (O)
  ($(O)+(0,\cao)$) coordinate (S)
  ;
  \fill[cyan,opacity=0.6] (A)--(B)--(C)--(D)--cycle;
  \fill[orange,opacity=0.8] (A)--(B)--(C)--(D)--cycle;
  \draw[line width=0.8pt] (B)--(C)--(D) (S)--(B) (S)--(C) (S)--(D);
  \draw[dashed,line width=0.8pt] (B)--(A)--(D) (A)--(S);

 \end{tikzpicture}
"""

# ========================================================================================
# Base class
# ========================================================================================
class BaseOptimizationQuestion(ABC):
    def __init__(self):
        self.parameters: Dict[str, Any] = {}
        self.correct_answer: Optional[str] = None
        self.solution_steps: List[str] = []

    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        """Return a dict of randomized parameters for the question."""
        raise NotImplementedError

    @abstractmethod
    def calculate_answer(self) -> None:
        """Return the final answer string to print under 'Đáp án:'"""
        raise NotImplementedError

    @abstractmethod
    def generate_wrong_answers(self) -> None:
        """Generate wrong answer options and store in instance attributes."""
        raise NotImplementedError

    @abstractmethod
    def generate_question_text(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_solution(self) -> str:
        raise NotImplementedError

    def generate_question(self, question_number: int = 1) -> str:
        # (Re)generate parameters for each question
        self.parameters = self.generate_parameters()
        self.calculate_answer()
        self.generate_wrong_answers()
        q_text = self.generate_question_text()
        solution = self.generate_solution()
        return f"Câu {question_number}: {q_text}\n\n{solution}\n\n"


# ========================================================================================
# Gấp miếng bìa thành hình chóp tứ giác đều (dạng Đúng/Sai)
# ========================================================================================
class SquarePyramidFromSheetQuestion(BaseOptimizationQuestion):
    """
    Bài toán: Từ miếng bìa vuông cạnh L (đơn vị: cm), cắt bỏ bốn góc để giữ lại
    1 hình vuông cạnh x và bốn tam giác cân có chung cạnh đáy là x. Gấp lại tạo
    thành hình chóp tứ giác đều (T) có đáy là hình vuông cạnh x.

    Phân tích hình học:
    - Miếng bìa vuông L×L
    - Cắt bỏ 4 góc, giữ lại: hình vuông trung tâm x×x + 4 tam giác cân
    - Mỗi tam giác cân có: đáy = x, chiều cao = (L-x)/2
    - Khi gấp thành chóp: cạnh bên chóp = chiều cao tam giác = (L-x)/2

    Công thức toán học:
      - Điều kiện gấp được: 0 < x < L
      - Cạnh bên chóp: s = (L-x)/2
      - Chiều cao chóp: h = √[s² - (x√2/2)²] = √[(L-x)²/4 - x²/8] = (1/2)√[(L-x)² - x²/2]
      - Thể tích: V(x) = (1/3) × x² × h
      - Diện tích phần bị cắt: S_cắt = L² - [x² + 4×(1/2)×x×(L-x)/2] = L² - x² - x(L-x) = L² - Lx
      - V đạt cực đại khi dV/dx = 0
    """

    def __init__(self):
        super().__init__()
        # Các biến lưu trữ công thức LaTeX để in trong lời giải

        # Miền xác định
        self.domain: Optional[str] = None
        self.wrong_domain: Optional[str] = None

        # Diện tích bị cắt
        self.Scut_expr: Optional[str] = None
        self.wrong_scut: Optional[str] = None

        # Thể tích khối chóp
        self.V_expr: Optional[str] = None
        self.wrong_V_expr: Optional[str] = None

        # x tối ưu cho thể tích tối đa
        self.x_opt: Optional[str] = None
        self.wrong_x_opt: Optional[str] = None

        # Thể tích tối đa
        self.V_max: Optional[str] = None
        self.wrong_V_max: Optional[str] = None

        # Loại câu hỏi cho mệnh đề d
        self.question_type_d: Optional[str] = None

    def generate_parameters(self) -> Dict[str, Any]:
        # Chọn ngẫu nhiên độ dài cạnh miếng bìa từ tập hợp các giá trị hợp lý
        plate_length = random.choice([20, 22, 24, 25, 26, 28, 30, 32, 34, 35, 36, 38, 40, 45, 50])

        return {
            "plate_length": plate_length,
        }

    def calculate_answer(self) -> None:
        p = self.parameters
        L = p["plate_length"]  # Giữ nguyên là int

        # Phần a: Miền xác định đúng
        self.domain = f"0 < x < {L}"

        # Phần b: Diện tích bị cắt
        self.S_vuong = f"x^2"
        self.chieu_cao_tam_giac = f"\\dfrac{{{L} - x}}{{2}}"
        self.S_1_tam_giac = f"\\frac{{1}}{{2}}x \\cdot \\dfrac{{{L} - x}}{{2}}"
        self.S_4_tam_giac = f"{L}x - x^2"
        self.S_lay = f"{L}x"

        # Kết quả
        self.Scut_expr = f"{L}^2 - {L}x"

        # Phần c: Thể tích khối chóp
        self.chieu_cao_chop = f"\\sqrt{{\\left(\\frac{{{L}-x}}{{2}}\\right)^2 - \\left(\\frac{{x}}{{2}}\\right)^2}}"
        self.V_chua_rut_gon = f"\\frac{{1}}{{3}} \\cdot x^2 \\cdot {self.chieu_cao_chop}"

        # Kết quả
        self.V_expr = f"\\frac{{1}}{{6}} x^2 \\sqrt{{{L}({L}-2x)}}"

        # Phần d: Tìm x tối ưu cho thể tích tối đa hoặc tính thể tích tối đa
        # Định nghĩa hàm symbolic
        x, L_sym = sp.symbols('x L', positive=True)
        # Định nghĩa hàm V từ V_expr: V = (1/6) * x^2 * sqrt(L*(L-2*x))
        V_func = sp.Rational(1, 6) * x ** 2 * sp.sqrt(L_sym * (L_sym - 2 * x))

        # Tính đạo hàm
        V_prime_func = sp.diff(V_func, x)
        V_prime_simplified_func = sp.simplify(V_prime_func)

        # Chuyển về LaTeX với giá trị L cụ thể
        V_prime_latex = sp.latex(V_prime_simplified_func.subs(L_sym, L))
        self.V_prime_simplified = f"V'(x) = {V_prime_latex}"

        # Giải phương trình V'(x) = 0
        solutions = sp.solve(V_prime_simplified_func, x)
        # Lọc nghiệm dương và nhỏ hơn L/2
        valid_solutions = [sol for sol in solutions if sol.is_positive and sol < L_sym / 2]

        x_opt_symbolic = valid_solutions[0].subs(L_sym, L)

        # Kết quả
        self.x_opt = sp.latex(x_opt_symbolic)

        # Tính V_max
        V_max_func = V_func.subs([(x, x_opt_symbolic), (L_sym, L)])
        V_max_simplified = sp.simplify(V_max_func)

        # Kết quả
        self.V_max = f"V_{{\\max}} = {sp.latex(V_max_simplified)}"

    def generate_wrong_answers(self) -> None:
        p = self.parameters
        L = p["plate_length"]

        # 1. Miền xác định sai
        wrong_domains_options = [
            f"0 < x < \\frac{{{L}}}{{2}}",
            f"0 < x < \\frac{{{L}}}{{3}}",
            f"0 < x < \\frac{{2{L}}}{{3}}",
            f"0 < x < {L - 2}",
            f"0 < x < {L + 2}",
            f"0 \\leq x \\leq {L}"
        ]
        self.wrong_domain = random.choice(wrong_domains_options)

        # 2. Diện tích bị cắt sai
        wrong_scut_options = [
            f"{L}^2 - {L}x + x^2",
            f"{L}^2 - 2{L}x",
            f"{L}^2 - x^2",
            f"{L}^2",
            f"{L}^2 - \\frac{{{L}x}}{{2}}",
            f"2{L}^2 - {L}x"
        ]
        self.wrong_scut = random.choice(wrong_scut_options)

        # 3. Thể tích sai
        wrong_V_expr_options = [
            f"\\frac{{1}}{{3}} x^2 \\sqrt{{{L}({L}-2x)}}",
            f"\\frac{{1}}{{6}} x^2 \\sqrt{{{L}({L}-x)}}",
            f"\\frac{{1}}{{6}} x \\sqrt{{{L}({L}-2x)}}",
            f"\\frac{{1}}{{12}} x^2 \\sqrt{{{L}({L}-2x)}}"
        ]
        self.wrong_V_expr = random.choice(wrong_V_expr_options)

        # 4. x tối ưu sai
        x, L_sym = sp.symbols('x L', positive=True)
        wrong_x_opts_options = [
            sp.latex(L_sym / 3),
            sp.latex(L_sym / 4),
            sp.latex(3 * L_sym / 5),
            sp.latex(L_sym / 2)
        ]
        chosen_x_opt = random.choice(wrong_x_opts_options).replace('L', str(L))
        self.wrong_x_opt = chosen_x_opt

        # 5. V_max sai - tạo các giá trị đơn giản để tránh số phức
        wrong_V_maxs_options = [
            f"V_{{\\max}} = \\frac{{{L}^3}}{{27}}",
            f"V_{{\\max}} = \\frac{{{L}^3}}{{36}}",
            f"V_{{\\max}} = \\frac{{{L}^3}}{{50}}",
            f"V_{{\\max}} = \\frac{{{L}^3}}{{75}}",
            f"V_{{\\max}} = \\frac{{{L}^3 \\sqrt{{5}}}}{{125}}",
            f"V_{{\\max}} = \\frac{{{L}^3}}{{60}}"
        ]

        # Loại bỏ các giá trị trùng với V_max đúng
        available_options = [option for option in wrong_V_maxs_options if option != self.V_max]

        # Nếu tất cả đều trùng (trường hợp hiếm), tạo một giá trị mới
        if not available_options:
            available_options = [f"V_{{\\max}} = \\frac{{{L}^3}}{{100}}"]

        self.wrong_V_max = random.choice(available_options)

    def generate_question_text(self) -> str:
        p = self.parameters
        L = p['plate_length']

        intro = (
            f"Từ một miếng bìa vuông cạnh bằng {L} cm, người ta cắt bỏ 4 phần ở 4 góc như hình vẽ và giữ lại "
            f"mảnh được tô hai màu (gồm 1 hình vuông cạnh bằng x và 4 tam giác cân). "
            f"Tiến hành gấp mảnh còn lại thành một hình chóp tứ giác đều (T). "
            f"Hỏi trong các mệnh đề dưới đây, mệnh đề nào đúng, mệnh đề nào sai?"
        )

        # Thêm hình tikz vào đây
        tikz_block = Tikzpicture().tikzpicture()

        # Random chọn giá trị đúng hoặc sai cho từng mệnh đề và đánh dấu *
        domain_is_correct = random.choice([True, False])
        domain_display = self.domain if domain_is_correct else self.wrong_domain
        domain_mark = "*" if domain_is_correct else ""

        scut_is_correct = random.choice([True, False])
        scut_display = self.Scut_expr if scut_is_correct else self.wrong_scut
        scut_mark = "*" if scut_is_correct else ""

        v_expr_is_correct = random.choice([True, False])
        v_expr_display = self.V_expr if v_expr_is_correct else self.wrong_V_expr
        v_expr_mark = "*" if v_expr_is_correct else ""

        # Random chọn dạng câu hỏi cho mệnh đề d và lưu vào instance variable
        self.question_type_d = random.choice(['x_opt', 'V_max'])
        d_is_correct = random.choice([True, False])
        d_mark = "*" if d_is_correct else ""

        if self.question_type_d == 'x_opt':
            x_opt_display = self.x_opt if d_is_correct else self.wrong_x_opt
            statement_d = f"{d_mark}d) Thể tích khối chóp (T) lớn nhất khi \\(x = {x_opt_display}\\) (cm).\n"
        else:  # V_max
            v_max_display = self.V_max if d_is_correct else self.wrong_V_max
            statement_d = f"{d_mark}d) Thể tích khối chóp lớn nhất \\({v_max_display}\\) (cm\\(^3\\)).\n"

        items = [
            f"{domain_mark}a) Điều kiện để gấp được hình chóp là \\({domain_display}\\).\n",
            f"{scut_mark}b) Diện tích phần bị cắt bỏ là \\({scut_display}\\) (cm\\(^2\\)).\n",
            f"{v_expr_mark}c) Thể tích khối chóp là \\(V(x) = {v_expr_display}\\) (cm\\(^3\\)).\n",
            statement_d
        ]

        return intro + "\n\n" + tikz_block + "\n\n" + "\n".join(items)

    def generate_solution(self) -> str:
        p = self.parameters
        L = p['plate_length']

        steps: List[str] = [f"Lời giải:\n",
                            f"a) Đáp án đúng là: \\({self.domain}\\)\n",
                            f"b) \\(S_{{\\text{{vuông}}}} = {self.S_vuong}\\)\n",
                            f"Chiều cao \\(\\triangle\\) cân \\(= {self.chieu_cao_tam_giac}\\)\n",
                            f"\\(\\Rightarrow S_{{1\\triangle\\,\\text{{cân}}}} = {self.S_1_tam_giac}\\)\n",
                            f"\\(\\Rightarrow S_{{4\\triangle}} = {self.S_4_tam_giac}\\)\n",
                            f"\\(\\Rightarrow S_{{\\text{{lấy}}}} = {self.S_lay}\\)\n",
                            f"\\(\\Rightarrow S_{{\\text{{bỏ}}}} = {self.Scut_expr}\\)\n",
                            f"c) Chiều cao của chóp \\(= {self.chieu_cao_chop}\\)\n",
                            f"\\(\\Rightarrow V = {self.V_chua_rut_gon}\\)\n",
                            f"\\(\\Leftrightarrow V = {self.V_expr}\\)\n",
                            f"d) \\({self.V_prime_simplified}\\)\n",
                            f"\\(V'(x) = 0 \\Leftrightarrow x = 0\\) hoặc \\(x = {self.x_opt}\\)\n",
                            f"Vì \\(x > 0\\) nên \\(x = {self.x_opt}\\)\n"]

        # Chỉ thêm dòng V_max nếu câu hỏi là về V_max
        if self.question_type_d == 'V_max':
            steps.append(f"\\({self.V_max}\\)\n")

        return "\n".join(steps)


# ========================================================================================
# Question Manager
# ========================================================================================
class QuestionManager:
    def __init__(self):
        self.question_types = [SquarePyramidFromSheetQuestion]

    def generate_questions(self, num_questions: int):
        questions = []
        for i in range(1, num_questions + 1):
            q = self.question_types[0]()
            questions.append(q.generate_question(i))
        return questions


# ========================================================================================
# Main
# ========================================================================================
def main():
    parser = argparse.ArgumentParser(description="Sinh bài tập gấp miếng bìa thành hình chóp tứ giác đều (Đúng/Sai)")
    parser.add_argument('num_positional', nargs='?', type=int,
                        help='Số câu hỏi (tùy chọn, nếu cung cấp sẽ ghi đè --num-questions)')
    parser.add_argument('-n', '--num-questions', type=int, default=3,
                        help='Số câu hỏi cần sinh (mặc định: 3)')
    parser.add_argument('-o', '--output', type=str, default="pyramid_tf_questions.tex",
                        help='Tên file đầu ra .tex')
    parser.add_argument('-t', '--title', type=str, default="Bài tập Hình chóp tứ giác đều (Đúng/Sai)",
                        help='Tiêu đề tài liệu')
    args = parser.parse_args()

    if args.num_positional is not None:
        args.num_questions = args.num_positional

    qm = QuestionManager()
    questions = qm.generate_questions(args.num_questions)

    content = f"\\documentclass[a4paper,12pt]{{article}}\n"
    content += "\\usepackage{polyglossia}\n"
    content += "\\setmainlanguage{vietnamese}\n"
    content += "\\usepackage{amsmath,amssymb}\n\\usepackage{tikz}\n\\usetikzlibrary{calc}\n\\begin{document}\n"
    content += f"\\title{{{args.title}}}\n\\author{{dev}}\n\\maketitle\n\n"
    content += "\n\n".join(questions)
    content += "\\end{document}"

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Đã tạo file {args.output} với {len(questions)} câu hỏi")


if __name__ == "__main__":
    main()
