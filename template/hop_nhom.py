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
\begin{tikzpicture}
   \clip(-2.4,-2.5) rectangle (9.5,2.4);
   \fill[fill=black] (-2,2) -- (-2,1) -- (-1,1) -- (-1,2) -- cycle;
   \fill[fill=black] (1,2) -- (1,1) -- (2,1) -- (2.,2.) -- cycle;
   \fill[fill=black] (-2.,-1.) -- (-2.,-2.) -- (-1.,-2.) -- (-1.,-1.) -- cycle;
   \fill[fill=black] (1.,-1.) -- (1.,-2.) -- (2.,-2.) -- (2.,-1.) -- cycle;
   \draw [line width=1.2pt] (3.,-1.)-- (3.,-2.);
   \draw (3.,-2.)-- (7.,-2.)--(7,-1)--(3,-1)--(5,1)--(9,1)--(9,0)--(7,-2);
   \draw (9.,1.)-- (7.,-1.);
   \draw [dashed] (5.,1.)-- (5.,0.);
   \draw [dashed] (5.,0.)-- (3.,-2.);
   \draw [dashed] (5.,0.)-- (9.,0.);
   \draw (-2.,2.)-- (-2.,1.)--(-1,1)--(-1,2);
   \draw (1.,2.)-- (1.,1.)--(2,1)--(2,2)--(1,2);
   \draw (-2.,-1.)-- (-2.,-2.)--(-1,-2)--(-1,-1)--(-2,-1);
   \draw (1.,-1.)-- (1.,-2.)--(2,-2)--(2,-1)--(1,-1);
   \draw (-1.,2.)-- (1.,2.);
   \draw (-1.,1.)-- (1.,1.);
   \draw (-2.,1.)-- (-2.,-1.);
   \draw (-1.,1.)-- (-1.,-1.);
   \draw (1.,1.)-- (1.,-1.);
   \draw (2.,1.)-- (2.,-1.);
   \draw (1.,-2.)-- (-1.,-2.);
   \draw (-1.,-1.)-- (1.,-1.);
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
        pass

    @abstractmethod
    def calculate_answer(self) -> str:
        pass

    @abstractmethod
    def generate_question_text(self) -> str:
        pass

    @abstractmethod
    def generate_solution(self) -> str:
        pass

    def generate_question(self, question_number: int = 1) -> str:
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        q_text = self.generate_question_text()
        solution = self.generate_solution()
        tikz_block = Tikzpicture().tikzpicture()
        return f"Câu {question_number}: {q_text}\n\n{tikz_block}\n\n{solution}\n\nĐáp án: {self.correct_answer}\n\n"


# ========================================================================================
# Bài toán tấm nhôm cắt góc tạo hộp không nắp (thay thế cho problem cắt dây)
# ========================================================================================
class AluminumBoxOptimizationQuestion(BaseOptimizationQuestion):
    def __init__(self):
        super().__init__()
        # Lưu thêm hai trường để dùng trong lời giải
        self.correct_x: Optional[str] = None
        self.max_volume: Optional[str] = None
        self.correct_x_latex: Optional[str] = None
        self.max_volume_latex: Optional[str] = None
        self.parameters = self.generate_parameters()
        # correct_answer là chuỗi cuối cùng tương ứng với yêu cầu đề bài
        self.correct_answer = self.calculate_answer()

    def generate_parameters(self):
        # plate_length: chiều dài cạnh tấm nhôm (cm), random trong [12;20]
        plate_length = random.randint(12, 20)

        # unit: đơn vị đo, chọn ngẫu nhiên dm hoặc cm
        unit = random.choice(["dm", "cm"])

        # question: Câu hỏi cuối đề bài
        q_x = "Tìm x để hộp nhận được có thể tích lớn nhất."
        q_v = "Thể tích lớn nhất là bao nhiêu?"
        question = random.choice([q_x, q_v])
        ask_for_volume = (question == q_v)

        return {
            "plate_length": plate_length,
            "unit": unit,
            "question": question,
            "ask_for_volume": ask_for_volume,
        }

    def calculate_answer(self) -> str:
        p = self.parameters
        L = p["plate_length"]
        unit = p["unit"]

        # Điểm tới hạn nội suy: x_opt = L/6 và biên x=0, x=L/2 (V=0). Max tại x=L/6.
        x_opt = L / 6
        vmax = (2 / 27) * (L ** 3)

        # Lưu hai giá trị (định dạng) để dùng trong phần giải thích
        self.correct_x = f"{x_opt:.2f} {unit}"
        self.max_volume = f"{vmax:.2f} {unit}^3"
        # Bản LaTeX an toàn để chèn trong môi trường toán
        self.correct_x_latex = f"{x_opt:.2f}\\,\\mathrm{{{unit}}}"
        self.max_volume_latex = f"{vmax:.2f}\\,\\mathrm{{{unit}}}^3"

        # Trả về đáp án cuối cùng theo yêu cầu đề bài (không có đơn vị, format: 2.17|2,17)
        if p.get("ask_for_volume"):
            value = f"{vmax:.2f}"
            value_comma = value.replace(".", ",")
            return f"{value}|{value_comma}"
        else:
            value = f"{x_opt:.2f}"
            value_comma = value.replace(".", ",")
            return f"{value}|{value_comma}"

    def generate_question_text(self) -> str:
        p = self.parameters
        return (
            f"Cho một tấm nhôm hình vuông cạnh {p['plate_length']} {p['unit']}. "
            f"Người ta cắt ở bốn góc của tấm nhôm đó bốn hình vuông bằng nhau, "
            f"mỗi hình vuông có cạnh bằng x {p['unit']}, rồi gấp tấm nhôm lại như hình vẽ dưới đây "
            f"để được một cái hộp không nắp. {p['question']}"
        )

    def generate_solution(self) -> str:
        p = self.parameters
        L = p["plate_length"]
        unit = p["unit"]
        steps = [
            "Lời giải:\n",
            f"Chiều cao hộp = x, cạnh đáy = {L} - 2x ({unit})\n",
            f"Thể tích: \\(V(x) = x({L} - 2x)^2\\) (\\(\\mathrm{{{unit}}}^3\\))\n",
            f"Đạo hàm: \\(V'(x) = ({L} - 2x)({L} - 6x) = 0\\)\n",
            f"\\(\\Rightarrow x = \\frac{{{L}}}{{6}}\\) (loại \\(x = \\frac{{{L}}}{{2}}\\) là đầu mút)\n"
            f"\\(\\Rightarrow\\) x tối ưu: \\(x = {self.correct_x_latex}\\).\n",
        ]

        # Nếu câu hỏi yêu cầu thể tích lớn nhất
        if p.get("ask_for_volume"):
            steps.append(f"\\(\\Rightarrow\\) \\(V_{{\\max}} = \\frac{{2}}{{27}}\\cdot {L}^3 = {self.max_volume_latex}\\).")

        return "\n".join(steps)

    def generate_question(self, question_number: int = 1) -> str:
        q_text = self.generate_question_text()
        solution = self.generate_solution()
        # Đáp án cuối cùng đã được chuẩn hoá trong calculate_answer()
        final_answer = self.correct_answer
        # Thêm hình vẽ TikZ ngay sau đề bài và trước lời giải
        tikz_block = Tikzpicture().tikzpicture()
        return f"Câu {question_number}: {q_text}\n\n{tikz_block}\n\n{solution}\n\nĐáp án: {final_answer}\n\n"


# ========================================================================================
# Question Manager
# ========================================================================================
class QuestionManager:
    def __init__(self):
        self.question_types = [AluminumBoxOptimizationQuestion]

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
    parser = argparse.ArgumentParser(description="Sinh câu hỏi tối ưu hóa tấm nhôm tạo hộp")
    parser.add_argument('num_positional', nargs='?', type=int,
                        help='Số câu hỏi (tùy chọn, nếu cung cấp sẽ ghi đè --num-questions)')
    parser.add_argument('-n', '--num-questions', type=int, default=3,
                        help='Số câu hỏi cần sinh (mặc định: 3)')
    parser.add_argument('-o', '--output', type=str, default="aluminum_box_questions.tex",
                        help='Tên file đầu ra .tex')
    parser.add_argument('-t', '--title', type=str, default="Câu hỏi Tối ưu hóa Tấm nhôm",
                        help='Tiêu đề tài liệu')
    args = parser.parse_args()

    if args.num_positional is not None:
        args.num_questions = args.num_positional

    qm = QuestionManager()
    questions = qm.generate_questions(args.num_questions)

    content = f"\\documentclass[a4paper,12pt]{{article}}\n"
    content += "\\usepackage{amsmath}\n\\usepackage{tikz}\n\\begin{document}\n"
    content += f"\\title{{{args.title}}}\n\\author{{dev}}\n\\maketitle\n\n"
    content += "\n".join(questions)
    content += "\\end{document}"

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Đã tạo file {args.output} với {len(questions)} câu hỏi")


if __name__ == "__main__":
    main()
