import argparse
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import sympy as sp
import math


# ========================================================================================
# Tikzpicture class
# ========================================================================================
class TikzDiagram:
    def __init__(self, AB: float, AC: float, x_opt: float):
        """
        Vẽ tam giác vuông ABC với hình vuông và hình tròn bên trong
        AB, AC: độ dài 2 cạnh góc vuông
        x_opt: vị trí tối ưu của M trên AB (BM = x_opt)
        """
        self.AB = AB
        self.AC = AC
        self.BC = math.sqrt(AB**2 + AC**2)
        self.x_opt = x_opt
        
    def tikzpicture(self):
        # Scale để hình vẽ đẹp hơn
        scale = 1.5
        AB = self.AB * scale
        AC = self.AC * scale
        BC = self.BC * scale
        
        # Tọa độ các điểm - Tam giác vuông tại A
        # B ở góc trái, A ở góc phải, C ở trên
        B_x, B_y = 0, 0
        A_x, A_y = AB, 0
        C_x, C_y = AB, AC
        
        # M trên AB, với AM = x_opt (phù hợp phần tính toán)
        x_am = self.x_opt * scale
        M_x, M_y = A_x - x_am, 0
        MA = x_am  # Độ dài AM
        
        # N phải nằm trên BC: y = (AC/AB) * x
        slope_BC = (AC / AB) if AB != 0 else 0.0
        rect_side = slope_BC * M_x
        
        # Tọa độ hình chữ nhật: M (đáy), N (trên BC), P trên AC cùng cao với N
        N_x, N_y = M_x, rect_side
        P_x, P_y = A_x, rect_side
        
        # Hình tròn S2 là đường tròn NỘI TIẾP tam giác NPC
        # Tam giác NPC:
        #   N = (M_x, rect_side) - góc trái
        #   P = (A_x, rect_side) - góc vuông (góc dưới phải)
        #   C = (A_x, AC)        - góc trên
        # Đây là tam giác vuông tại P
        
        # Các cạnh của tam giác NPC (vuông tại P)
        PN = P_x - N_x                             # = AM = MA
        PC = AC - rect_side                        # Cạnh dọc
        NC = math.sqrt(PN**2 + PC**2)              # Cạnh huyền
        
        # Bán kính đường tròn nội tiếp tam giác vuông
        # Công thức: r = (a + b - c) / 2
        # với a, b là 2 cạnh góc vuông, c là cạnh huyền
        r = (PN + PC - NC) / 2
        
        # Tâm đường tròn nội tiếp: cách mỗi cạnh góc vuông một khoảng = r
        circle_x = A_x - r      # P_x - r (cách cạnh PC khoảng r, về phía trái)
        circle_y = rect_side + r  # P_y + r (cách cạnh PN khoảng r, lên trên)
        
        tikz = r"""
\begin{tikzpicture}[scale=1.0]
    % Tô màu tam giác ABC (background)
    \fill[gray!10] (""" + f"{B_x},{B_y}" + r""") -- (""" + f"{A_x},{A_y}" + r""") -- (""" + f"{C_x},{C_y}" + r""") -- cycle;
    
    % Tọa độ các điểm
    \coordinate (B) at (""" + f"{B_x},{B_y}" + r""");
    \coordinate (A) at (""" + f"{A_x},{A_y}" + r""");
    \coordinate (C) at (""" + f"{C_x},{C_y}" + r""");
    \coordinate (M) at (""" + f"{M_x},{M_y}" + r""");
    \coordinate (N) at (""" + f"{N_x},{N_y}" + r""");
    \coordinate (P) at (""" + f"{P_x},{P_y}" + r""");
    
    % Vẽ hình chữ nhật S1 (MNPA)
    \fill[gray!40] (M) -- (N) -- (P) -- (A) -- cycle;
    \draw[thick] (M) -- (N) -- (P) -- (A) -- cycle;
    
    % Vẽ hình tròn S2
    \fill[gray!60] (""" + f"{circle_x},{circle_y}" + r""") circle (""" + f"{r}" + r""");
    \draw[thick] (""" + f"{circle_x},{circle_y}" + r""") circle (""" + f"{r}" + r""");
    
    % Vẽ tam giác ABC (viền)
    \draw[very thick] (B) -- (A) -- (C) -- cycle;
    
    % Ghi nhãn các đỉnh
    \node[below left] at (B) {$B$};
    \node[below right] at (A) {$A$};
    \node[above] at (C) {$C$};
    \node[below] at (M) {$M$};
    \node[left] at (N) {$N$};
    \node[right] at (P) {$P$};
    
    % Ghi nhãn diện tích
    \node at (""" + f"{(M_x + A_x)/2},{rect_side/2}" + r""") {$S_1$};
    \node[white] at (""" + f"{circle_x},{circle_y}" + r""") {$S_2$};
    
    % Đánh dấu góc vuông tại A
    \draw[thick] (""" + f"{A_x-0.3},{A_y}" + r""") -- (""" + f"{A_x-0.3},{A_y+0.3}" + r""") -- (""" + f"{A_x},{A_y+0.3}" + r""");
\end{tikzpicture}
"""
        return tikz


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
# Bài toán tối ưu hóa hình học tam giác vuông
# ========================================================================================
class TriangleGeometryOptimization(BaseOptimizationQuestion):
    def __init__(self):
        super().__init__()
        self.x_opt: Optional[float] = None
        self.max_area: Optional[float] = None
        self.x_opt_latex: Optional[str] = None
        self.max_area_latex: Optional[str] = None
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()

    def generate_parameters(self):
        # AB, AC: độ dài 2 cạnh góc vuông, random trong [3, 6]
        AB = random.randint(3, 6)
        # AC khác AB
        ac_choices = [v for v in range(3, 6) if v != AB]
        AC = random.choice(ac_choices)
        
        # BC: cạnh huyền
        BC = math.sqrt(AB**2 + AC**2)
        
        # Câu hỏi: tìm x tối ưu hoặc tìm diện tích lớn nhất
        q_x = "Xác định giá trị x để tổng diện tích \\(S_1 + S_2\\) đạt giá trị lớn nhất."
        q_area = "Tìm giá trị lớn nhất của tổng diện tích \\(S_1 + S_2\\) (làm tròn đến chữ số hàng phần chục)."
        question_type = random.choice(["x", "area"])
        question = q_x if question_type == "x" else q_area
        ask_for_area = (question_type == "area")
        
        return {
            "AB": AB,
            "AC": AC,
            "BC": BC,
            "question": question,
            "ask_for_area": ask_for_area,
        }

    def calculate_answer(self) -> str:
        """
        Tính toán đáp án theo mô hình hình học CHÍNH XÁC:
        
        - Hệ tọa độ: A(0,0), B(AB,0), C(0,AC)
        - M ở vị trí x trên AB (từ A), tức AM = x
        - N phải nằm trên BC để tạo hình chữ nhật AMNP
        - Đường BC: x/AB + y/AC = 1
        - Chiều rộng hình chữ nhật: y = AC(1 - x/AB)
        - S₁ = x·y (diện tích hình chữ nhật)
        - Hình tròn S₂ nội tiếp tam giác NPC (tam giác vuông tại P)
        - r = (PN + PC - NC) / 2 (công thức nội tiếp tam giác vuông)
        - S₂ = πr²
        """
        p = self.parameters
        AB = p["AB"]
        AC = p["AC"]
        BC = p["BC"]
        
        # Biến symbolic
        x = sp.Symbol('x', positive=True, real=True)
        
        # Chiều rộng hình chữ nhật (từ ràng buộc N trên BC)
        y = AC * (1 - x / AB)
        
        # Diện tích hình chữ nhật AMNP
        S1 = x * y
        
        # Tam giác NPC (tam giác vuông tại P):
        # N = (x, y), P = (x, AC), C = (0, AC)
        PN = AB - x         # Cạnh ngang (từ N đến P)
        PC = AC - y         # Cạnh dọc (từ P đến C) = AC - y
        NC = sp.sqrt(PN**2 + PC**2)  # Cạnh huyền
        
        # Bán kính đường tròn nội tiếp tam giác vuông
        r = (PN + PC - NC) / 2
        
        # Diện tích hình tròn
        S2 = sp.pi * r**2
        
        # Tổng diện tích
        S_total = S1 + S2
        
        # Tránh giải biểu thức tượng trưng dễ gây treo; tối ưu hoá số học 1D an toàn
        def S_numeric(xv: float) -> float:
            try:
                if not (0.0 < xv < AB):
                    return float('-inf')
                yv = AC * (1.0 - xv / AB)
                if yv <= 0.0:
                    return float('-inf')
                NPv = AB - xv
                PCv = AC - yv
                NCv = math.sqrt(NPv * NPv + PCv * PCv)
                rv = (NPv + PCv - NCv) / 2.0
                if rv <= 1e-12:
                    return float('-inf')
                S1v = xv * yv
                S2v = math.pi * (rv * rv)
                return S1v + S2v
            except Exception:
                return float('-inf')

        # Coarse scan
        left = 1e-4
        right = max(AB - 1e-4, left + 1e-4)
        best_x = left
        best_S = S_numeric(best_x)
        steps = 400
        for i in range(steps + 1):
            xv = left + (right - left) * i / steps
            Sv = S_numeric(xv)
            if Sv > best_S:
                best_S = Sv
                best_x = xv

        # Local refine with ternary-like search
        for _ in range(3):
            span = max((right - left) / steps, AB * 0.02)
            a = max(left, best_x - span)
            b = min(right, best_x + span)
            for __ in range(60):
                m1 = a + (b - a) / 3.0
                m2 = b - (b - a) / 3.0
                S1v = S_numeric(m1)
                S2v = S_numeric(m2)
                if S1v < S2v:
                    a = m1
                else:
                    b = m2
            best_x = (a + b) / 2.0
            best_S = S_numeric(best_x)
            left, right = a, b

        x_opt = float(best_x)
        max_area = float(best_S)
        
        # Lưu kết quả
        self.x_opt = x_opt
        self.max_area = max_area
        self.x_opt_latex = f"{x_opt:.2f}"
        self.max_area_latex = f"{max_area:.2f}"
        
        # Trả về đáp án theo yêu cầu
        if p.get("ask_for_area"):
            value = f"{max_area:.2f}"
            value_comma = value.replace(".", ",")
            return f"{value}|{value_comma}"
        else:
            value = f"{x_opt:.2f}"
            value_comma = value.replace(".", ",")
            return f"{value}|{value_comma}"

    def generate_question_text(self) -> str:
        p = self.parameters
        return (
            f"Cho tam giác vuông ABC với AB = {p['AB']}, AC = {p['AC']} (góc vuông tại A). "
            f"Hình chữ nhật AMNP có M nằm trên AB, N nằm trên BC, P nằm trên AC như hình vẽ. "
            f"Gọi \\(S_1\\) là diện tích hình chữ nhật AMNP và \\(S_2\\) là diện tích đường tròn "
            f"nội tiếp tam giác NPC. {p['question']}"
        )

    def generate_solution(self) -> str:
        p = self.parameters
        AB = p["AB"]
        AC = p["AC"]
        
        steps = [
            "Lời giải:\n",
            f"Đặt AM = x, AP = y (với 0 < x < {AB}, 0 < y < {AC})\n",
            f"\\(\\Rightarrow\\) AM = PN = x, AP = MN = y\n",
            f"Vì N nằm trên BC nên theo hệ quả của định lý Thales:\n",
            f"\\(\\frac{{PN}}{{AB}} = \\frac{{PC}}{{AC}} \\Leftrightarrow \\frac{{x}}{{{AB}}} + \\frac{{y}}{{{AC}}} = 1 \\Leftrightarrow y = {AC}\\left(1 - \\frac{{x}}{{{AB}}}\\right)\\)\n",
            f"\\(\\Rightarrow S_1 = x \\cdot y = {AC}x - \\frac{{{AC}}}{{{AB}}}x^2\\)\n",
            f"Tam giác PNC (vuông tại P):\n",
            f"\\(PN = x\\), \\(PC = {AC} - y\\), \\(NC = \\sqrt{{PN^2 + PC^2}}\\)\n",
            f"Bán kính nội tiếp: \\(r = \\frac{{PN + PC - NC}}{{2}}\\)\n",
            f"Diện tích hình tròn: \\(S_2 = \\pi r^2\\)\n",
            f"Tổng diện tích: \\(S(x) = S_1 + S_2\\)\n",
            f"Giải \\(S'(x) = 0\\) ta được:\n",
            f"\\(\\Rightarrow x = {self.x_opt_latex}\\)\n",
        ]
        
        if p.get("ask_for_area"):
            steps.append(f"\\(\\Rightarrow S_{{\\max}} = {self.max_area_latex}\\)")
        
        return "\n".join(steps)

    def generate_question(self, question_number: int = 1) -> str:
        q_text = self.generate_question_text()
        solution = self.generate_solution()
        final_answer = self.correct_answer
        
        # Thêm hình vẽ TikZ
        x_val = self.x_opt if self.x_opt is not None else 0.0
        tikz_diagram = TikzDiagram(self.parameters["AB"], self.parameters["AC"], x_val)
        tikz_block = tikz_diagram.tikzpicture()
        
        return f"Câu {question_number}: {q_text}\n\n{tikz_block}\n\n{solution}\n\nĐáp án: {final_answer}\n\n"


# ========================================================================================
# Question Manager
# ========================================================================================
class QuestionManager:
    def __init__(self):
        self.question_types = [TriangleGeometryOptimization]

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
    parser = argparse.ArgumentParser(description="Sinh câu hỏi tối ưu hóa hình học tam giác vuông")
    parser.add_argument('num_positional', nargs='?', type=int,
                        help='Số câu hỏi (tùy chọn, nếu cung cấp sẽ ghi đè --num-questions)')
    parser.add_argument('-n', '--num-questions', type=int, default=3,
                        help='Số câu hỏi cần sinh (mặc định: 3)')
    parser.add_argument('-o', '--output', type=str, default="triangle_geometry_questions.tex",
                        help='Tên file đầu ra .tex')
    parser.add_argument('-t', '--title', type=str, default="Câu hỏi Tối ưu hóa Hình học Tam giác",
                        help='Tiêu đề tài liệu')
    args = parser.parse_args()

    if args.num_positional is not None:
        args.num_questions = args.num_positional

    qm = QuestionManager()
    questions = qm.generate_questions(args.num_questions)

    content = f"\\documentclass[a4paper,12pt]{{article}}\n"
    content += "\\usepackage{fontspec}\n"
    content += "\\usepackage{polyglossia}\n"
    content += "\\setdefaultlanguage{vietnamese}\n"
    content += "\\usepackage{amsmath}\n"
    content += "\\usepackage{amssymb}\n"
    content += "\\usepackage{tikz}\n"
    content += "\\usepackage{geometry}\n"
    content += "\\geometry{margin=2cm}\n"
    content += "\\begin{document}\n"
    content += f"\\title{{{args.title}}}\n\\author{{dev}}\n\\maketitle\n\n"
    content += "\n".join(questions)
    content += "\\end{document}"

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Đã tạo file {args.output} với {len(questions)} câu hỏi")


if __name__ == "__main__":
    main()

