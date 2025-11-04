import argparse
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import sympy as sp


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
        return f"\\begin{{ex}} {q_text}\n\n{solution}\n\\end{{ex}}\n\n"


# ========================================================================================
# Bài toán hai tam giác đều tạo hình chóp tam giác
# ========================================================================================
class TriangularPyramidOptimization(BaseOptimizationQuestion):
    def __init__(self):
        super().__init__()
        self.correct_x: Optional[float] = None
        self.max_volume: Optional[float] = None
        self.correct_x_latex: Optional[str] = None
        self.max_volume_latex: Optional[str] = None
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()

    def generate_parameters(self):
        # L: cạnh tam giác ABC đều (random từ 3 đến 6, hoặc cố định = 4)
        # Để đa dạng hóa, ta random
        L = random.choice([3, 4, 5, 6])
        
        return {
            "L": L,
        }

    def calculate_answer(self) -> str:
        """
        Tính toán nghiệm tối ưu cho x bằng sympy.
        
        Hình học đúng:
        - Tam giác ABC đều cạnh L, tam giác MNP đều cạnh x
        - MNP có cùng trọng tâm với ABC, xoay 180°
        - Khoảng cách từ trọng tâm G đến đỉnh tam giác đều cạnh a: a/sqrt(3)
        - AG = L/sqrt(3), GM = x/sqrt(3)
        - Vì xoay ngược nhau, A và M nằm hai phía đối nhau của G
        - Do đó: AM = AG + GM = (L + x)/sqrt(3)
        
        Công thức thể tích hình chóp:
        - Cạnh bên SM = AM = (L+x)/sqrt(3)
        - Khoảng cách từ G đến M: GM = x/sqrt(3)
        - Chiều cao: h = sqrt(SM^2 - GM^2) = sqrt((L+x)^2/3 - x^2/3)
        - h = sqrt((L^2 + 2Lx + x^2 - x^2)/3) = sqrt((L^2 + 2Lx)/3)
        - h = sqrt(L(L + 2x)/3) = sqrt(L(L+2x))/sqrt(3)
        - Đơn giản hóa: h^2 = (L^2 + 2Lx)/3 = (36 + 12x)/3 (với L=6)
        - h = sqrt(12 + 4x) = 2*sqrt(3 + x)
        
        - Diện tích đáy: S = x^2*sqrt(3)/4
        - Thể tích: V = (1/3)*S*h = (x^2*sqrt(3)/4) * 2*sqrt(3+x) / 3
        - V = x^2*sqrt(3)*sqrt(3+x) / 6
        
        Đạo hàm V'(x) = sqrt(3)/6 * [2x*sqrt(3+x) + x^2/(2*sqrt(3+x))]
                      = sqrt(3)/6 * [4x(3+x) + x^2] / (2*sqrt(3+x))
                      = sqrt(3)/6 * (5x^2 + 12x) / (2*sqrt(3+x))
                      = sqrt(3)/12 * x(5x + 12) / sqrt(3+x)
        
        V'(x) > 0 với mọi x > 0 (vì 5x+12 > 0)
        => V đồng biến trên (0, L]
        => V max khi x = L
        """
        p = self.parameters
        L = p["L"]
        
        # V(x) đồng biến, max tại x = L
        x_opt = float(L)
        
        # Tính thể tích max: V = x^2*sqrt(3)*sqrt(3+x) / 6
        v_max = (L**2 * sp.sqrt(3) * sp.sqrt(3 + L) / 6)
        v_max = float(v_max.evalf())
        
        # Lưu kết quả
        self.correct_x = x_opt
        self.max_volume = v_max
        self.correct_x_latex = f"{x_opt:.1f}" if x_opt != int(x_opt) else f"{int(x_opt)}"
        self.max_volume_latex = f"{v_max:.2f}"
        
        # Format đáp án: làm tròn đến hàng phần chục (1 chữ số thập phân)
        if x_opt == int(x_opt):
            value = f"{int(x_opt)}"
        else:
            value = f"{x_opt:.1f}"
        value_comma = value.replace(".", ",")
        return f"{value}"

    def generate_question_text(self) -> str:
        p = self.parameters
        L = p["L"]
        return (
            f"Cho một mô hình gồm hai tam giác đều \\(ABC\\) cạnh bằng {L} và \\(MNP\\) cạnh bằng \\(x\\) như hình vẽ. "
            f"Tam giác \\(MNP\\) có cùng trọng tâm với tam giác \\(ABC\\) và được xoay ngược lại như hình vẽ. "
            f"Cắt từ mô hình ra các tam giác \\(AMP\\), \\(MNB\\), \\(NPC\\) rồi gập thành một hình chóp tam giác đều. "
            f"Khi thể tích hình chóp tam giác đều đạt lớn nhất thì giá trị của \\(x\\) bằng bao nhiêu? "
            f"(kết quả làm tròn đến chữ số hàng phần chục)."
        )

    def tikzpicture_flat(self) -> str:
        """Hình vẽ 2 tam giác đều lồng nhau trên mặt phẳng"""
        p = self.parameters
        L = p["L"]
        # Scale cho tam giác nhỏ (tỷ lệ x/L, dùng giá trị trung bình để minh họa)
        x_demo = L / 2  # Để minh họa, dùng x = L/2
        small_radius = 0.5
        large_addition = 3
        
        return r"""  \begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
   \draw  
   (-90:0.5) coordinate (N)
   --(30:0.5)coordinate (P)
   --(150:0.5)coordinate (M)--(N)
   ;
   \draw
   (P)--($(P)!1/2!(M)+(90:3)$)coordinate (A)--(M)
   (M)--($(M)!1/2!(N)+(-150:3)$)coordinate (B)--(N)
   (N)--($(N)!1/2!(P)+(-30:3)$)coordinate (C)--(P)
   ;
   \draw[fill=black!10,opacity=0.7] (A)--(B)--(C)--cycle;
   \foreach \p/\r in {A/90,B/-120,C/-60,M/120,N/-90,P/60
   }
   \fill (\p) circle (1.2pt) node[shift={(\r:3mm)}]{$\p$};
  \end{tikzpicture}"""

    def tikzpicture_pyramid(self) -> str:
        """Hình vẽ hình chóp tam giác đều sau khi gấp"""
        return r"""  \begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
   \def\dai{4}  \def\rong{1} \def\cao{4}
   \path 
   (0,0) coordinate (D)
   (1,\rong) coordinate (A)
   (\dai+1,1) coordinate (B)
   ($(B)+(D)-(A)$) coordinate (C)
   ($($(A)!0.5!(B)$)+(0,\cao)$) coordinate (S)
   ;
   \draw (S)--(A)--(C)--(B)--(S)--(C);
   \draw[dashed] (A)--(B);
   \draw 
   (A) node[left]{$M$}
   (B) node[right]{$P$}
   (C) node[below]{$N$}
   ;
   \draw[fill=black!10,opacity=0.7]
   (S)--(A)--(C)--(B)--cycle;
  \end{tikzpicture}"""

    def generate_solution(self) -> str:
        p = self.parameters
        L = p["L"]
        x_latex = self.correct_x_latex
        
        solution = "\\loigiai{\n\n"
        solution += f"Gọi G là trọng tâm của tam giác \\(ABC\\) và \\(MNP\\).\n\n"
        solution += f"\\(\\Rightarrow \\) \\(AG = \\dfrac{{{L}}}{{\\sqrt{{3}}}}\\), \\(GM = \\dfrac{{x}}{{\\sqrt{{3}}}}\\).\n\n"
        solution += f"Vì hai tam giác cùng trọng tâm nhưng xoay ngược nhau nên \\(A\\) và \\(M\\) nằm hai phía đối nhau của \\(G\\):\n\n"
        solution += f"\\(\\Rightarrow \\) \\(AM = AG + GM = \\dfrac{{{L}}}{{\\sqrt{{3}}}} + \\dfrac{{x}}{{\\sqrt{{3}}}} = \\dfrac{{{L}+x}}{{\\sqrt{{3}}}}\\)\n\n"
        solution += f"Tương tự: \\(BN = CP = \\dfrac{{{L}+x}}{{\\sqrt{{3}}}}\\)\n\n"
        solution += f"Gọi \\(S\\) là đỉnh chóp. Khi gập, \\(SM = AM = \\dfrac{{{L}+x}}{{\\sqrt{{3}}}}\\).\n\n"
        solution += f"Khoảng cách từ \\(G\\) đến \\(M\\): \\(GM = \\dfrac{{x}}{{\\sqrt{{3}}}}\\).\n\n"
        solution += f"Chiều cao chóp:\n\n"
        
        # Dùng sympy để tự động rút gọn biểu thức h
        x_sym = sp.Symbol('x', positive=True)
        h_expr = sp.sqrt(L*(L + 2*x_sym)/3)
        h_simplified = sp.simplify(h_expr)
        h_latex = sp.latex(h_simplified)
        
        solution += f"\\(h = \\sqrt{{SM^2 - GM^2}} = \\sqrt{{\\frac{{({L}+x)^2 - x^2}}{{3}}}} = {h_latex}\\)\n\n"
        solution += "Diện tích đáy: \\(S_{\\triangle MNP} = \\dfrac{x^2\\sqrt{3}}{4}\\)\n\n"
        solution += f"Thể tích:\n\n"
        
        # Tính V(x) và rút gọn triệt để
        V_expr = sp.sqrt(3)/12 * x_sym**2 * h_simplified
        V_simplified = sp.simplify(V_expr)
        V_latex = sp.latex(V_simplified)
        
        solution += f"\\(V(x) = \\dfrac{{1}}{{3}} \\cdot \\dfrac{{x^2\\sqrt{{3}}}}{{4}} \\cdot {h_latex} = {V_latex}\\)\n\n"
        
        # Tính đạo hàm từ V đã rút gọn
        V_derivative = sp.diff(V_simplified, x_sym)
        V_derivative_simplified = sp.simplify(V_derivative)
        V_derivative_latex = sp.latex(V_derivative_simplified)
        
        solution += f"Đạo hàm: \\(V'(x) = {V_derivative_latex}\\)\n\n"
        solution += f"Ta thấy \\(V'(x) > 0\\) với mọi \\(x > 0\\) (vì \\(5x + {2*L} > 0\\))\n\n"
        solution += f"Do đó \\(V(x)\\) đồng biến trên \\((0, {L}]\\).\n\n"
        solution += f"Kết luận: Thể tích đạt giá trị lớn nhất khi \\(x = {x_latex}\\).\n"
        solution += "}"
        
        return solution

    def generate_question(self, question_number: int = 1) -> str:
        q_text = self.generate_question_text()
        solution = self.generate_solution()
        
        # Thêm 2 hình vẽ TikZ
        tikz_flat = self.tikzpicture_flat()
        tikz_pyramid = self.tikzpicture_pyramid()
        
        # Lấy đáp án
        answer = self.correct_answer
        
        return (
            f"\\begin{{ex}} {q_text}\n\n"
            f" \\begin{{center}}\n"
            f"{tikz_flat}\n"
            f"{tikz_pyramid}\n"
            f" \\end{{center}}\n"
            f" \\textbf{{Đáp án: }} {answer}\n\n"
            f" {solution}\n"
            f"\\end{{ex}}\n\n"
        )


# ========================================================================================
# Question Manager
# ========================================================================================
class QuestionManager:
    def __init__(self):
        self.question_types = [TriangularPyramidOptimization]

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
    parser = argparse.ArgumentParser(description="Sinh câu hỏi tối ưu hóa hình chóp tam giác đều")
    parser.add_argument('num_positional', nargs='?', type=int,
                        help='Số câu hỏi (tùy chọn, nếu cung cấp sẽ ghi đè --num-questions)')
    parser.add_argument('-n', '--num-questions', type=int, default=3,
                        help='Số câu hỏi cần sinh (mặc định: 3)')
    parser.add_argument('-o', '--output', type=str, default="triangular_pyramid_questions.tex",
                        help='Tên file đầu ra .tex')
    parser.add_argument('-t', '--title', type=str, default="Câu hỏi Tối ưu hóa Hình chóp Tam giác",
                        help='Tiêu đề tài liệu')
    args = parser.parse_args()

    if args.num_positional is not None:
        args.num_questions = args.num_positional

    qm = QuestionManager()
    questions = qm.generate_questions(args.num_questions)

    content = f"\\documentclass[a4paper,12pt]{{article}}\n"
    content += "\\usepackage{amsmath}\n"
    content += "\\usepackage{tikz}\n"
    content += "\\usetikzlibrary{calc}\n"
    content += "\\newcounter{ex}\n"
    content += "\\newenvironment{ex}{\\refstepcounter{ex}\\par\\medskip\\noindent Bài~\\theex. \\rmfamily}{\\medskip}\n"
    content += "\\newcommand{\\loigiai}[1]{\\par\\noindent Lời giải: #1}\n"
    content += "\\begin{document}\n"
    content += f"\\title{{{args.title}}}\n\\author{{dev}}\n\\maketitle\n\n"
    content += "\n".join(questions)
    content += "\\end{document}"

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Đã tạo file {args.output} với {len(questions)} câu hỏi")


if __name__ == "__main__":
    main()

