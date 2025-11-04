import argparse
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import sympy as sp

# ========================================================================================
# Tikzpicture class
# ========================================================================================
class Tikzpicture:
    def tikzpicture(self):
        return r"""
\begin{center}
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,transform shape,scale=0.4]
   \tikzset{Icon-Tau/.pic={ 
     \def\bk{3}
     \draw
     (0,0)coordinate (O)--(0:\bk)coordinate (A1)-- (60:\bk)coordinate (A2)--cycle
     ($(A1)!0.07*\bk!(A2)$) coordinate (A1') 
     ($(A2)!0.07*\bk!(A1)$) coordinate (A2')
     ($(A2')!1cm!90:(A2)$) coordinate (A2''')
     (intersection of A2'--A2''' and O--A2) coordinate (A2'') 
     ($(A1')!1cm!90:(A1)$) coordinate (A1''')
     (intersection of A1'--A1''' and O--A1) coordinate (A1'') 
     ;
     \draw[fill=black!40] 
     (A2)--(A2')--(A2'')--cycle
     (A1)--(A1')--(A1'')--cycle  
     (A1'')--(A2'')
     ;
     
     
   }}
   \foreach \x in {0,60,...,360}
   \path
   (0,0)pic[rotate=\x]{Icon-Tau}
   ;
   
  \end{tikzpicture}
  \begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
   \path  (0,0)--(1,0); 
   \draw[->,line width=4pt] (0,2)--(1,2); 
  \end{tikzpicture}
  \begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,transform shape,scale=0.7]
   \tikzset{Icon-Tau/.pic={ 
     
     \def\bk{3}
     \path
     (0,0)coordinate (O)--(0:\bk)coordinate (A1)-- (60:\bk)coordinate (A2)--cycle
     ($(A1)!0.07*\bk!(A2)$) coordinate (A1') 
     ($(A2)!0.07*\bk!(A1)$) coordinate (A2')
     ($(A2')!1cm!90:(A2)$) coordinate (A2''')
     (intersection of A2'--A2''' and O--A2) coordinate (A2'') 
     ($(A1')!1cm!90:(A1)$) coordinate (A1''')
     (intersection of A1'--A1''' and O--A1) coordinate (A1'') 
     ;
     \draw 
     (O)--(A1'')--(A1')--(A2')--(A2'')--(O)
     (A1'')--(A2'')
     ;
     
     
   }}
   \foreach \x in {0,60,...,360}
   \path
   (0,0)pic[rotate=\x]{Icon-Tau}
   ;
   
   
   
  \end{tikzpicture}
  \begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
   \path  (0,0)--(1,0); 
   \draw[->,line width=4pt] (0,2)--(1,2); 
  \end{tikzpicture}
  \begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=0.7]
   \path (0,0)coordinate (A1)--++(0.5,-1)coordinate (A2)--++(2,0)coordinate (A3)--++(1.5,1)coordinate (A4)--++(-0.75,1)coordinate (A5)--++(-2,0)coordinate (A6)--cycle
   ;
   \foreach \x in {1,2,...,6}
   {
    \path ($(A\x)+(0,3)$) coordinate (B\x);
   }
   \draw (A1)--(A2)--(A3)--(A4)
   (A1)--(B1) (A2)--(B2)(A3)--(B3)(A4)--(B4)
   (B1)--(B2)--(B3)--(B4)--(B5)--(B6)--cycle
   ;
   \draw[dashed] (A4)--(A5)--(A6)--(A1)
   (A5)--(B5) (A6)--(B6)
   ;
   \end{tikzpicture}
\end{center}
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
    def calculate_answer(self) -> str:
        """Return the final answer string to print under 'Đáp án:'"""
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
        answer = self.calculate_answer()
        q_text = self.generate_question_text()
        solution = self.generate_solution()
        tikz_block = Tikzpicture().tikzpicture()
        return f"Câu {question_number}: {q_text}\n\n{tikz_block}\n\n{solution}\n\nĐáp án: {answer}\n\n"


# ========================================================================================
# Gấp tấm nhôm lục giác thành hình lăng trụ lục giác đều
# ========================================================================================
class HexagonalPrismFromSheetQuestion(BaseOptimizationQuestion):
    """
    Bài toán: Từ tấm nhôm hình lục giác đều cạnh L cm, cắt ở mỗi đỉnh 
    hai tam giác vuông bằng nhau, cạnh góc vuông nhỏ = x cm. Gấp tấm nhôm 
    thành hình lăng trụ lục giác đều không có nắp.

    Phân tích hình học:
    - Tấm nhôm lục giác đều: 6 cạnh = L cm (L được random)
    - Cắt 12 tam giác vuông (mỗi đỉnh 2 tam giác), cạnh góc vuông nhỏ = x
    - Chiều cao lăng trụ = x√3 (do gấp hình học)
    - Đáy lục giác sau khi cắt có cạnh = (L - 2x)

    Công thức toán học:
      - Điều kiện gấp được: 0 < x < L/2
      - Diện tích đáy lục giác: (3√3/2) × (L-2x)²
      - Thể tích lăng trụ: V(x) = (9x(L-2x)²)/2
      - Diện tích phần bị cắt: 12 × (1/2) × x² = 6x²
      - V đạt cực đại khi dV/dx = 0
    """

    def __init__(self):
        super().__init__()
        # Các biến cần cho lời giải rút gọn
        self.V_expr: Optional[str] = None
        self.x_opt: Optional[str] = None
        self.V_max: Optional[str] = None
        # Câu hỏi cuối đề bài
        self.final_question: Optional[str] = None

    def generate_parameters(self) -> Dict[str, Any]:
        # Chọn ngẫu nhiên cạnh lục giác đều từ các giá trị hợp lý
        plate_length = random.choice([80, 90, 100, 110, 120])

        return {
            "plate_length": plate_length,
        }

    def calculate_answer(self) -> str:
        p = self.parameters
        L = p["plate_length"]  # Giữ nguyên là int
        
        # Tạo final_question trước để biết kiểu câu hỏi
        self.final_question = ("Tìm x để thể tích lăng trụ đạt giá trị lớn nhất",
                               "Thể tích lăng trụ đạt giá trị lớn nhất là bao nhiêu")[random.randint(0, 1)]

        # Công thức thể tích lăng trụ lục giác (dùng trong lời giải)
        self.dien_tich_day = f"\\frac{{3\\sqrt{{3}}}}{{2}}({L}-2x)^2"
        self.chieu_cao_lang_tru = f"x\\sqrt{{3}}"
        self.V_expr = f"\\frac{{9x({L}-2x)^2}}{{2}}"

        # Tối ưu thể tích bằng đạo hàm
        x, L_sym = sp.symbols('x L', positive=True)
        V_func = sp.Rational(9, 2) * x * (L_sym - 2 * x) ** 2
        V_prime_simplified_func = sp.simplify(sp.diff(V_func, x))

        # Nghiệm tới hạn và lọc theo 0 < x < L/2
        solutions = sp.solve(V_prime_simplified_func, x)
        valid_solutions = [sol for sol in solutions if sol.is_positive and sol < L_sym / 2]
        x_opt_symbolic = valid_solutions[0].subs(L_sym, L)
        self.x_opt = sp.latex(x_opt_symbolic)

        # Thể tích lớn nhất tương ứng
        V_max_func = V_func.subs([(x, x_opt_symbolic), (L_sym, L)])
        V_max_simplified = sp.simplify(V_max_func)
        self.V_max = sp.latex(V_max_simplified)
        
        # Giá trị số để in gọn
        x_opt_float = float(x_opt_symbolic.evalf())
        V_max_float = float(V_max_simplified.evalf())
        
        # Làm tròn đến hàng đơn vị (theo yêu cầu đề bài)
        x_opt_rounded = round(x_opt_float)
        V_max_rounded = round(V_max_float)
        
        # Kiểm tra xem giá trị có phải là số nguyên chính xác không (sai số < 0.01)
        self.x_opt_is_exact_integer = abs(x_opt_float - x_opt_rounded) < 0.01
        self.V_max_is_exact_integer = abs(V_max_float - V_max_rounded) < 0.01
        
        # Sau khi làm tròn đến hàng đơn vị, kết quả luôn là số nguyên
        self.x_opt_final = int(x_opt_rounded)
        self.V_max_final = int(V_max_rounded)
        
        # Trả về đáp án dạng số nguyên (không có đơn vị và ký hiệu toán học)
        if self.final_question.startswith("Tìm x"):
            return str(self.x_opt_final)
        else:
            return str(self.V_max_final)

    def generate_question_text(self) -> str:
        p = self.parameters
        L = p['plate_length']

        question_text = (
            f"Từ một tấm nhôm hình lục giác đều cạnh bằng {L} cm, người ta cắt ở mỗi đỉnh "
            f"hai tam giác vuông bằng nhau, biết cạnh góc vuông nhỏ bằng x (cm). "
            f"Tiến hành gấp tấm nhôm như hình vẽ để được một hình lăng trụ lục giác đều không có nắp. "
            f"{self.final_question}. (Nếu kết quả là số thập phân, làm tròn đến hàng đơn vị)"
        )

        return question_text + "\n\n"

    def generate_solution(self) -> str:
        # Lời giải rút gọn theo phác thảo hình ảnh: chỉ giữ S_đáy, h, V và kết quả cực đại
        steps: List[str] = [
            "Lời giải:\n",
            # S_đáy
            f"\\(S_{{\\text{{đáy}}}} = {self.dien_tich_day}\\)\n",
            # h = sqrt((2x)^2 - x^2) = x sqrt 3
            f"\\(h = \\sqrt{{(2x)^2 - x^2}} = {self.chieu_cao_lang_tru}\\)\n",
            # V = S_đáy * h => rút gọn
            f"\\(\\Rightarrow V = {self.V_expr}\\)\n",
        ]

        # Cực trị: nếu là số nguyên chính xác thì không cần ≈
        if self.x_opt_is_exact_integer:
            steps.append(f"V đạt GTLN khi \\(x = {self.x_opt_final}\\)\n")
        else:
            steps.append(f"V đạt GTLN khi \\(x = {self.x_opt} \\approx {self.x_opt_final}\\)\n")

        # Nếu câu hỏi hỏi thể tích lớn nhất thì thêm dòng V_max
        if self.final_question and not self.final_question.startswith("Tìm x"):
            if self.V_max_is_exact_integer:
                steps.append(f"\\(\\Rightarrow V_{{\\max}} = {self.V_max_final}\\)")
            else:
                steps.append(f"\\(\\Rightarrow V_{{\\max}} = {self.V_max} \\approx {self.V_max_final}\\)")

        return "\n".join(steps)


# ========================================================================================
# Question Manager
# ========================================================================================
class QuestionManager:
    def __init__(self):
        self.question_types = [HexagonalPrismFromSheetQuestion]

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
    parser = argparse.ArgumentParser(description="Sinh bài tập gấp tấm nhôm thành hình lăng trụ lục giác đều")
    parser.add_argument('num_positional', nargs='?', type=int,
                        help='Số câu hỏi (tùy chọn, nếu cung cấp sẽ ghi đè --num-questions)')
    parser.add_argument('-n', '--num-questions', type=int, default=3,
                        help='Số câu hỏi cần sinh (mặc định: 3)')
    parser.add_argument('-o', '--output', type=str, default="hexagonal_prism_questions.tex",
                        help='Tên file đầu ra .tex')
    parser.add_argument('-t', '--title', type=str, default="Bài tập Lăng trụ lục giác đều",
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
