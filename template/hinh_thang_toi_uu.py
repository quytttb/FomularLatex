import argparse
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import sympy as sp


# ========================================================================================
# Helper functions
# ========================================================================================
def format_number(value: float) -> str:
    """Format number, removing unnecessary .0 or .00"""
    if value == int(value):
        return str(int(value))
    else:
        # Format with 2 decimal places and strip trailing zeros
        formatted = f"{value:.2f}".rstrip('0').rstrip('.')
        return formatted


# ========================================================================================
# Tikzpicture class - Dynamic generation
# ========================================================================================
class Tikzpicture:
    def __init__(self, L: float, AE: float, BF: float, x: float, y: float):
        self.L = L
        self.AE = AE
        self.BF = BF
        self.x = x
        self.y = y
    
    def tikzpicture(self):
        """Generate TikZ code for the square with trapezoid EFGH"""
        L = self.L
        AE = self.AE
        BF = self.BF
        x = self.x
        y = self.y
        
        # Scale for drawing (assuming L in range 20-40, scale to fit ~6cm drawing)
        scale = 6.0 / L
        
        return f"""
\\begin{{tikzpicture}}[scale={scale:.2f}]
  % Define coordinates
  % A at origin, B at (L,0), C at (L,L), D at (0,L)
  \\coordinate (A) at (0,0);
  \\coordinate (B) at ({L},0);
  \\coordinate (C) at ({L},{L});
  \\coordinate (D) at (0,{L});
  
  % Points on edges
  \\coordinate (E) at ({AE},0);     % E on AB, distance AE from A
  \\coordinate (F) at ({L},{BF});   % F on BC, distance BF from B
  \\coordinate (G) at ({L-y},{L});  % G on DC, CG = y (distance y from C)
  \\coordinate (H) at (0,{x});      % H on AD, AH = x (distance x from A)
  
  % Draw square ABCD
  \\draw[line width=1pt] (A) -- (B) -- (C) -- (D) -- cycle;
  
  % Draw and fill trapezoid EFGH
  \\fill[cyan, opacity=0.5] (E) -- (F) -- (G) -- (H) -- cycle;
  \\draw[line width=1.2pt, blue] (E) -- (F) -- (G) -- (H) -- cycle;
  
  % Label vertices
  \\node[below left] at (A) {{$A$}};
  \\node[below right] at (B) {{$B$}};
  \\node[above right] at (C) {{$C$}};
  \\node[above left] at (D) {{$D$}};
  
  \\node[below] at (E) {{$E$}};
  \\node[right] at (F) {{$F$}};
  \\node[above] at (G) {{$G$}};
  \\node[left] at (H) {{$H$}};
  
  % Mark distances
  \\draw[|<->|, >=latex] ($(A)+(0,-0.5)$) -- ($(E)+(0,-0.5)$) node[midway, below] {{{AE:.0f} cm}};
  \\draw[|<->|, >=latex] ($(B)+(0.5,0)$) -- ($(F)+(0.5,0)$) node[midway, right] {{{BF:.0f} cm}};
  \\draw[|<->|, >=latex] ($(D)+(-0.5,0)$) -- ($(H)+(-0.5,0)$) node[midway, left] {{$x$ cm}};
  \\draw[|<->|, >=latex] ($(G)+(0,0.5)$) -- ($(C)+(0,0.5)$) node[midway, above] {{$y$ cm}};
\\end{{tikzpicture}}
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
        return f"Câu {question_number}: {q_text}\n\n{solution}\n\nĐáp án: {self.correct_answer}\n\n"


# ========================================================================================
# Bài toán hình thang EFGH tối ưu trong hình vuông
# ========================================================================================
class TrapezoidOptimizationQuestion(BaseOptimizationQuestion):
    def __init__(self):
        super().__init__()
        # Store optimization results
        self.x_opt: float = 0.0
        self.y_opt: float = 0.0
        self.s_min: float = 0.0
        self.s_total_max: float = 0.0
        self.x_opt_latex: str = ""
        self.y_opt_latex: str = ""
        self.s_min_latex: str = ""
        self.s_total_max_latex: str = ""
        self.S_AEH_latex: str = ""
        self.S_BEF_latex: str = ""
        self.S_BEF_value: float = 0.0
        self.S_CFG_latex: str = ""
        self.S_DGH_latex: str = ""
        self.S_DGH_expanded: str = ""
        self.S_total_formula: str = ""
        self.dS_dx: str = ""
        self.dS_dy: str = ""

    def generate_parameters(self):
        # Random square side length
        L = random.choice([20, 24, 25, 28, 30, 32, 36, 40])
        
        # Random positions for E and F
        # AE should be reasonable: between 2 and L/4
        AE = random.randint(2, max(3, L // 4))
        
        # BF should be reasonable: between 2 and L/4
        BF = random.randint(2, max(3, L // 4))
        
        # Question type: ask for sum x+y or minimum area
        question_type = random.choice(["sum_xy", "s_min"])
        
        return {
            "L": L,
            "AE": AE,
            "BF": BF,
            "question_type": question_type,
        }

    def calculate_answer(self) -> str:
        p = self.parameters
        L = p["L"]
        AE = p["AE"]
        BF = p["BF"]
        
        # Define symbolic variables
        x, y = sp.symbols('x y', real=True, positive=True)
        
        # NEW LOGIC: Calculate area of 4 triangles being cut
        # Triangle AEH: base AE, height x (H on AD at distance x from A)
        S_AEH = sp.Rational(1, 2) * AE * x
        
        # Triangle BEF: base BE = L - AE, height BF (constant)
        S_BEF = sp.Rational(1, 2) * (L - AE) * BF
        
        # Triangle CFG: base CF = L - BF, height y (G on DC at distance y from D, so CG = y)
        S_CFG = sp.Rational(1, 2) * (L - BF) * y
        
        # Triangle DGH: base DG = L - y, height DH = L - x
        S_DGH = sp.Rational(1, 2) * (L - y) * (L - x)
        
        # Total area of triangles
        S_total = S_AEH + S_BEF + S_CFG + S_DGH
        S_total_expanded = sp.expand(S_total)
        
        # Store formulas for solution display
        self.S_AEH_latex = sp.latex(S_AEH)
        self.S_BEF_latex = sp.latex(S_BEF)
        self.S_BEF_value = float(S_BEF)
        self.S_CFG_latex = sp.latex(S_CFG)
        self.S_DGH_latex = sp.latex(S_DGH)
        self.S_DGH_expanded = sp.latex(sp.expand(S_DGH))
        self.S_total_formula = sp.latex(S_total_expanded)
        
        # Area of trapezoid EFGH
        # S_EFGH = L² - S_total
        # To minimize S_EFGH, we need to maximize S_total
        
        # Take partial derivatives of S_total
        dS_dx = sp.diff(S_total_expanded, x)
        dS_dy = sp.diff(S_total_expanded, y)
        
        self.dS_dx = sp.latex(dS_dx)
        self.dS_dy = sp.latex(dS_dy)
        
        # Solve system of equations: dS_total/dx = 0, dS_total/dy = 0
        solutions = sp.solve([dS_dx, dS_dy], [x, y])
        
        # Filter valid solutions (0 < x < L, 0 < y < L)
        valid_solutions = []
        if isinstance(solutions, dict):
            x_val = solutions.get(x)
            y_val = solutions.get(y)
            if x_val and y_val:
                solutions = [(x_val, y_val)]
        
        for sol in solutions:
            if isinstance(sol, tuple):
                x_val, y_val = sol
            else:
                continue
            
            # Check if solution is valid
            try:
                x_numeric = float(x_val.evalf())
                y_numeric = float(y_val.evalf())
                if 0 < x_numeric < L and 0 < y_numeric < L:
                    valid_solutions.append((x_val, y_val))
            except Exception:
                pass
        
        if valid_solutions:
            x_opt_sym, y_opt_sym = valid_solutions[0]
        else:
            # Fallback to numerical solution if symbolic fails
            x_opt_sym = L / 2
            y_opt_sym = L / 2
        
        # Store results
        self.x_opt = float(x_opt_sym.evalf())
        self.y_opt = float(y_opt_sym.evalf())
        self.x_opt_latex = sp.latex(x_opt_sym)
        self.y_opt_latex = sp.latex(y_opt_sym)
        
        # Calculate S_total_max and S_EFGH_min
        s_total_max_sym = S_total_expanded.subs([(x, x_opt_sym), (y, y_opt_sym)])
        self.s_total_max = float(s_total_max_sym.evalf())
        self.s_total_max_latex = sp.latex(sp.simplify(s_total_max_sym))
        
        # S_EFGH_min = L² - S_total_max
        self.s_min = L**2 - self.s_total_max
        self.s_min_latex = f"{L}^2 - {self.s_total_max_latex}"
        
        # Return answer based on question type
        if p["question_type"] == "sum_xy":
            sum_val = self.x_opt + self.y_opt
            value = format_number(sum_val)
            # If integer, return single value; otherwise return both formats
            if "." in value:
                value_comma = value.replace(".", ",")
                return f"{value}|{value_comma}"
            else:
                return value
        else:  # s_min
            value = format_number(self.s_min)
            # If integer, return single value; otherwise return both formats
            if "." in value:
                value_comma = value.replace(".", ",")
                return f"{value}|{value_comma}"
            else:
                return value

    def generate_question_text(self) -> str:
        p = self.parameters
        L = p["L"]
        AE = p["AE"]
        BF = p["BF"]
        
        # Generate TikZ figure
        tikz = Tikzpicture(L, AE, BF, self.x_opt, self.y_opt)
        tikz_block = tikz.tikzpicture()
        
        question_text = (
            f"Cho một tấm nhôm hình vuông cạnh {L} cm. "
            f"Người ta muốn cắt một hình thang như hình vẽ. Tìm tổng $x + y$ để diện tích "
            f"hình thang $EFGH$ đạt giá trị nhỏ nhất (làm tròn kết quả đến hàng phần trăm)."
        )
        
        if p["question_type"] == "s_min":
            question_text = (
                f"Cho một tấm nhôm hình vuông cạnh {L} cm. "
                f"Người ta muốn cắt một hình thang như hình vẽ. Tìm diện tích nhỏ nhất "
                f"của hình thang $EFGH$ (làm tròn kết quả đến hàng phần trăm, đơn vị: cm$^2$)."
            )
        
        return question_text + "\n\n" + tikz_block

    def generate_solution(self) -> str:
        p = self.parameters
        L = p["L"]
        AE = p["AE"]
        BF = p["BF"]
        
        steps = [
            "Lời giải:\n\n",
            f"\\(S_{{\\Delta AEH}} = \\dfrac{{1}}{{2}} \\cdot AE \\cdot AH = {self.S_AEH_latex}\\)\n\n",
            f"\\(S_{{\\Delta BEF}} = \\dfrac{{1}}{{2}} \\cdot BE \\cdot BF = \\dfrac{{1}}{{2}} \\cdot {L - AE} \\cdot {BF} = {self.S_BEF_value:g}\\) (cm\\(^2\\))\n\n",
            f"\\(S_{{\\Delta CFG}} = \\dfrac{{1}}{{2}} \\cdot CF \\cdot CG = {self.S_CFG_latex}\\)\n\n",
            f"\\(S_{{\\Delta DGH}} = \\dfrac{{1}}{{2}} \\cdot DG \\cdot DH = {self.S_DGH_latex} = {self.S_DGH_expanded}\\)\n\n",
            f"\\(\\sum S_{{\\Delta}} = S_{{\\Delta AEH}} + S_{{\\Delta BEF}} + S_{{\\Delta CFG}} + S_{{\\Delta DGH}}\\)\n\n",
            f"\\(\\sum S_{{\\Delta}} = {self.S_total_formula}\\)\n\n",
            f"\\(S_{{EFGH}} = S_{{ABCD}} - \\sum S_{{\\Delta}}\\)\n\n",
            f"Để \\(S_{{EFGH}}\\) nhỏ nhất \\(\\Leftrightarrow\\) \\(\\sum S_{{\\Delta}}\\) lớn nhất.\n\n",
            f"Tính đạo hàm riêng:\n\n",
            f"\\(\\dfrac{{d \\sum S_{{\\Delta}}}}{{d x}} = {self.dS_dx}\\)\n\n",
            f"\\(\\dfrac{{d \\sum S_{{\\Delta}}}}{{d y}} = {self.dS_dy}\\)\n\n",
            f"Giải hệ phương trình:\n\n",
            f"\\(\\begin{{cases}} \\dfrac{{d \\sum S_{{\\Delta}}}}{{d x}} = 0 \\\\ \\dfrac{{d \\sum S_{{\\Delta}}}}{{d y}} = 0 \\end{{cases}}\\)\n\n",
            f"\\(\\Rightarrow \\begin{{cases}} x = {self.x_opt_latex} \\\\ y = {self.y_opt_latex} \\end{{cases}}\\)\n\n",
        ]
        
        if p["question_type"] == "sum_xy":
            sum_val = self.x_opt + self.y_opt
            x_str = format_number(self.x_opt)
            y_str = format_number(self.y_opt)
            sum_str = format_number(sum_val)
            steps.append(f"\\(\\Rightarrow x + y = {x_str} + {y_str} = {sum_str}\\) (cm)\n")
        else:
            s_total_str = format_number(self.s_total_max)
            s_min_str = format_number(self.s_min)
            steps.append(f"\\(\\sum S_{{\\Delta \\max}} = {self.s_total_max_latex} = {s_total_str}\\) (cm\\(^2\\))\n\n")
            steps.append(f"\\(S_{{EFGH \\, \\min}} = {L}^2 - {s_total_str} = {s_min_str}\\) (cm\\(^2\\))\n")
        
        return "".join(steps)


# ========================================================================================
# Question Manager
# ========================================================================================
class QuestionManager:
    def __init__(self):
        self.question_types = [TrapezoidOptimizationQuestion]

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
    parser = argparse.ArgumentParser(description="Sinh câu hỏi tối ưu hóa hình thang trong hình vuông")
    parser.add_argument('num_positional', nargs='?', type=int,
                        help='Số câu hỏi (tùy chọn, nếu cung cấp sẽ ghi đè --num-questions)')
    parser.add_argument('-n', '--num-questions', type=int, default=3,
                        help='Số câu hỏi cần sinh (mặc định: 3)')
    parser.add_argument('-o', '--output', type=str, default="trapezoid_optimization.tex",
                        help='Tên file đầu ra .tex')
    parser.add_argument('-t', '--title', type=str, default="Câu hỏi Tối ưu hóa Hình thang",
                        help='Tiêu đề tài liệu')
    args = parser.parse_args()

    if args.num_positional is not None:
        args.num_questions = args.num_positional

    qm = QuestionManager()
    questions = qm.generate_questions(args.num_questions)

    content = f"\\documentclass[a4paper,12pt]{{article}}\n"
    content += "\\usepackage{amsmath}\n\\usepackage{tikz}\n\\usetikzlibrary{calc}\n\\begin{document}\n"
    content += f"\\title{{{args.title}}}\n\\author{{dev}}\n\\maketitle\n\n"
    content += "\n".join(questions)
    content += "\\end{document}"

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Đã tạo file {args.output} với {len(questions)} câu hỏi")


if __name__ == "__main__":
    main()

