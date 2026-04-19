import math
import random
import sys
from typing import List, Tuple
import sympy as sp
from scipy.optimize import minimize_scalar


# =============================
# CLASS TÍNH TOÁN
# =============================
class BoxDistanceQuestion:
    def __init__(self):
        self.generate_parameters()

    def generate_parameters(self):
        self.AB = random.randint(10, 25)
        self.AD = random.randint(15, 30)
        self.AA_prime = random.randint(8, 20)
        self.v_M = round(random.uniform(1.0, 3.0), 1)
        self.v_N = round(random.uniform(1.5, 3.5), 1)
        self.calculate_process_variables()

    def calculate_process_variables(self):
        self.A = (0, 0, 0)
        self.B = (self.AB, 0, 0)
        self.C = (self.AB, self.AD, 0)
        self.D = (0, self.AD, 0)
        self.B_prime = (self.AB, 0, self.AA_prime)
        self.D_prime = (0, self.AD, self.AA_prime)

        # Vector và độ dài cho kiến M (B' -> A)
        self.vec_B_prime_A = (-self.AB, 0, -self.AA_prime)
        self.distance_B_prime_A = math.sqrt(self.AB ** 2 + self.AA_prime ** 2)

        # Vector và độ dài cho kiến N (C -> D')
        self.vec_C_D_prime = (-self.AB, 0, self.AA_prime)  # D' - C = (0,AD,AA') - (AB,AD,0)
        self.distance_C_D_prime = math.sqrt(self.AB ** 2 + self.AA_prime ** 2)

        # Hệ số vận tốc cho kiến M
        self.coefficient_Mx = self.v_M * self.AB / self.distance_B_prime_A
        self.coefficient_Mz = self.v_M * self.AA_prime / self.distance_B_prime_A

        # FIXED: Hệ số vận tốc cho kiến N
        self.coefficient_Nx = self.v_N * self.AB / self.distance_C_D_prime
        self.coefficient_Nz = self.v_N * self.AA_prime / self.distance_C_D_prime

        self.calculate_minimum_distance()

    def position_M(self, t):
        """Vị trí con kiến M tại thời điểm t"""
        x = self.AB - self.coefficient_Mx * t
        y = 0
        z = self.AA_prime - self.coefficient_Mz * t
        return (x, y, z)

    def position_N(self, t):
        """Vị trí con kiến N tại thời điểm t"""
        x = self.AB - self.coefficient_Nx * t  # Di chuyển từ AB về 0
        y = self.AD  # Không đổi
        z = self.coefficient_Nz * t  # Di chuyển từ 0 lên AA_prime
        return (x, y, z)

    def distance_function(self, t):
        """Hàm khoảng cách giữa hai con kiến tại thời điểm t"""
        pos_M = self.position_M(t)
        pos_N = self.position_N(t)
        dx = pos_M[0] - pos_N[0]
        dy = pos_M[1] - pos_N[1]
        dz = pos_M[2] - pos_N[2]
        return math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

    def calculate_minimum_distance(self):
        """Tính khoảng cách nhỏ nhất và thời điểm tương ứng"""
        t_max_M = self.distance_B_prime_A / self.v_M
        t_max_N = self.distance_C_D_prime / self.v_N
        t_max = min(t_max_M, t_max_N)

        # Tìm minimum trong khoảng [0, t_max]
        result = minimize_scalar(self.distance_function, bounds=(0, t_max), method='bounded')
        self.t_optimal = result.x
        self.d_min = result.fun

    def generate_wrong_answers(self):
        correct = round(self.d_min, 1)
        wrong_answers = set()
        while len(wrong_answers) < 3:
            delta = random.uniform(0.5, 3.0) * random.choice([-1, 1])
            wrong = round(correct + delta, 1)
            if wrong != correct and wrong > 0:
                wrong_answers.add(wrong)
        return list(wrong_answers)

    def generate_question_text(self):
        question = r'''
Với một hình hộp chữ nhật \(ABCD.A'B'C'D'\) có \(AB=%d\), \(AD=%d\), \(AA'=%d\) như hình vẽ. Ở cùng một thời điểm hai con kiến coi như bò chuyển động thẳng đều, con kiến \(M\) bò từ \(B'\) đến điểm \(A\) với tốc độ \(%s\,\mathrm{cm/s}\) và con kiến \(N\) bò từ \(C\) đến \(D'\) với tốc độ bằng \(%s\,\mathrm{cm/s}\). Hãy tính khoảng cách nhỏ nhất giữa hai con kiến theo đơn vị centimet (làm tròn kết quả đến hàng phần mười)?

\begin{tikzpicture}[scale=1.0]
%% Định nghĩa các đỉnh của hình hộp với phép chiếu đúng
\coordinate (B) at (0,0);
\coordinate (C) at (4,0);
\coordinate (A) at (1.5,1.5);
\coordinate (D) at (5.5,1.5);
\coordinate (B') at (0,3);
\coordinate (C') at (4,3);
\coordinate (A') at (1.5,4.5);
\coordinate (D') at (5.5,4.5);
%% Vẽ các cạnh nhìn thấy của hình hộp
\draw (B) -- (C);
\draw (B') -- (C') -- (D') -- (A') -- cycle;
\draw (B) -- (B');
\draw (C) -- (C');
\draw (C) -- (D);
\draw (D) -- (D');
%% Vẽ các cạnh ẩn bằng đường đứt nét
\draw[dashed] (B) -- (A);
\draw[dashed] (A) -- (D);
\draw[dashed] (A') -- (A);
%% Định nghĩa điểm M trên đường chéo AB'
\coordinate (M) at (0.75,2.25);
%% Định nghĩa điểm N trên cạnh CD'
\coordinate (N) at (4.75,2.25);
%% Vẽ đường chéo AB' bằng đường đứt nét đỏ (nhưng dùng màu đen theo yêu cầu)
\draw[dashed, thick] (A) -- (B');
%% Vẽ đường từ C đến N đến D' (đường xanh trong gốc, nhưng dùng màu đen)
\draw[thick] (C) -- (N) -- (D');
%% Vẽ các mũi tên
\draw[->, thick] (0.1,2.7) -- (0.5,2.3);  %% Mũi tên từ B' về phía M
\draw[->, thick] (4.17,0.3) -- (4.57,1.4);
%% Đánh dấu các điểm
\fill (A) circle (1.2pt);
\fill (B) circle (1.2pt);
\fill (C) circle (1.2pt);
\fill (D) circle (1.2pt);
\fill (A') circle (1.2pt);
\fill (B') circle (1.2pt);
\fill (C') circle (1.2pt);
\fill (D') circle (1.2pt);
\fill (M) circle (1.2pt);
\fill (N) circle (1.2pt);
%% Gắn nhãn cho các điểm
\node[below right] at (A) {\(A\)};
\node[below left] at (B) {\(B\)};
\node[below right] at (C) {\(C\)};
\node[below right] at (D) {\(D\)};
\node[above right] at (A') {\(A'\)};
\node[above left] at (B') {\(B'\)};
\node[above left] at (C') {\(C'\)};
\node[above right] at (D') {\(D'\)};
\node[right] at (M) {\(M\)};
\node[right] at (N) {\(N\)};
\end{tikzpicture}
''' % (self.AB, self.AD, self.AA_prime, self.v_M, self.v_N)
        return question

        # latex_BC = sp.latex(self.BC)
        # latex_BD = sp.latex(self.BD)

    def generate_solution(self):
        # AD là cạnh vuông góc với AB, thay cho AC và BC
        latex_AD = sp.latex(self.AD)
        solution = rf"""
Dữ kiện:\\
+ Hình hộp chữ nhật \(ABCD.A'B'C'D'\) có:\\
\[
AB = {self.AB},\quad AD = {self.AD},\quad AA' = {self.AA_prime}
\]
+ Gán tọa độ:
\[
A = (0, 0, 0),\quad B = ({self.AB}, 0, 0),\quad D = (0, {self.AD}, 0),\quad B' = ({self.AB}, 0, {self.AA_prime}),\quad D' = (0, {self.AD}, {self.AA_prime})
\]
+ Con kiến \(M\) bò từ \(B'\) đến \(A\) với tốc độ \({self.v_M}\, \text{{cm/s}}\)\\
+ Con kiến \(N\) bò từ \(C\) đến \(D'\) với tốc độ \({self.v_N}\, \text{{cm/s}}\)\\
Bước 1: Phương trình chuyển động\\
Con kiến \(M\):\\
Vector chỉ phương đường đi:
\[
\overrightarrow{{B'A}} = (0, 0, 0) - ({self.AB}, 0, {self.AA_prime}) = ( {-self.AB}, 0, {-self.AA_prime} )
\]
Chiều dài đoạn \(B'A\):
\[
|\overrightarrow{{B'A}}| = \sqrt{{{self.AB}^2 + {self.AA_prime}^2}} = \sqrt{{{self.AB ** 2} + {self.AA_prime ** 2}}} = \sqrt{{{self.AB ** 2 + self.AA_prime ** 2}}}
\]
Trong một giây con kiến tại \(M\) đi được \(\frac{{{self.v_M}}}{{\sqrt{{{self.AB ** 2 + self.AA_prime ** 2}}}}}\) lần \(\overrightarrow{{B'A}}\)\\
Véctơ vận tốc của con kiến tại \(M\) là:
\[
\overrightarrow{{v}}_M = \frac{{{self.v_M}}}{{\sqrt{{{self.AB ** 2 + self.AA_prime ** 2}}}}} \cdot ( {-self.AB}, 0, {-self.AA_prime} )
\]
Vị trí tại thời điểm \(t\):
\[
M(t) = ({self.AB}, 0, {self.AA_prime}) + t \cdot \frac{{{self.v_M}}}{{\sqrt{{{self.AB ** 2 + self.AA_prime ** 2}}}}} \cdot ( {-self.AB}, 0, {-self.AA_prime} )
= \left( {self.AB} - \frac{{{self.coefficient_Mx:.1f}t}}{{\sqrt{{{self.AB ** 2 + self.AA_prime ** 2}}}}},\; 0,\; {self.AA_prime} - \frac{{{self.coefficient_Mz:.1f}t}}{{\sqrt{{{self.AB ** 2 + self.AA_prime ** 2}}}}} \right)
\]
Con kiến \(N\): Làm tương tự ta có:\\
Vị trí tại thời điểm \(t\):
\[
N(t) = ({self.AB}, {self.AD}, 0) + t \cdot \frac{{{self.v_N}}}{{\sqrt{{{self.AB ** 2 + self.AA_prime ** 2}}}}} \cdot ({-self.AB}, 0, {self.AA_prime})
= \left( {self.AB} - \frac{{{self.coefficient_Nx:.1f}t}}{{\sqrt{{{self.AB ** 2 + self.AA_prime ** 2}}}}},\; {self.AD},\; \frac{{{self.coefficient_Nz:.1f}t}}{{\sqrt{{{self.AB ** 2 + self.AA_prime ** 2}}}}} \right)
\]
Bước 2: Tính khoảng cách giữa hai con kiến tại thời điểm \(t\)
\[
d(t) = \sqrt{{\left({self.AB} - \frac{{{self.coefficient_Mx:.1f}t}}{{\sqrt{{{self.AB ** 2 + self.AA_prime ** 2}}}}}\right)^2 + {self.AD}^2 + \left({self.AA_prime} - \frac{{{self.coefficient_Mz:.1f}t}}{{\sqrt{{{self.AB ** 2 + self.AA_prime ** 2}}}}} - {self.v_N}t\right)^2}}
\]
Bước 3: Tìm khoảng cách nhỏ nhất
\[
d'(t)=0\Leftrightarrow t \approx {self.t_optimal:.2f} \Rightarrow d_{{min}}={self.d_min:.1f}cm\
\]
"""
        return solution

    def calculate_answer(self):
        return f"{round(self.d_min, 1)}"

    def generate_full_question(self, question_number: int) -> str:
        correct = self.calculate_answer()
        wrongs = self.generate_wrong_answers()
        all_answers = [correct] + wrongs
        random.shuffle(all_answers)
        correct_index = all_answers.index(correct)
        question = self.generate_question_text()
        content = f"Câu {question_number}: {question}\n\n"
        for j, ans in enumerate(all_answers):
            letter = chr(65 + j)
            marker = "*" if j == correct_index else ""
            content += f"{marker}{letter}. {ans} cm\n\n"
        content += f"Lời giải:\n\n{self.generate_solution()}\n\n"
        return content

    def generate_question_only(self, question_number: int) -> Tuple[str, str]:
        question = self.generate_question_text()
        solution = self.generate_solution()
        correct = self.calculate_answer()
        content = f"Câu {question_number}: {question}\n\n"
        content += f"Lời giải:\n\n{solution}\n\n"
        return content, correct


# =============================
# GENERATOR CHÍNH
# =============================
class BoxDistanceGenerator:
    @classmethod
    def generate_multiple_questions(cls, num_questions: int = 5) -> List[str]:
        questions = []
        for i in range(1, num_questions + 1):
            q = BoxDistanceQuestion()
            questions.append(q.generate_full_question(i))
        return questions

    @classmethod
    def generate_multiple_questions_with_format(cls, num_questions: int = 5, fmt: int = 1):
        if fmt == 1:
            return cls.generate_multiple_questions(num_questions)
        else:
            questions_data = []
            for i in range(1, num_questions + 1):
                q = BoxDistanceQuestion()
                content, correct = q.generate_question_only(i)
                questions_data.append((content, correct))
            return questions_data

    @staticmethod
    def create_latex_document_with_format(questions_data, title: str = "Bài toán",
                                          fmt: int = 1) -> str:
        header = r"""
\documentclass[a4paper,12pt]{article}
\usepackage{amsmath}
\usepackage{mathtools}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage{tikz}
\usepackage{tkz-tab}
\usepackage{tkz-euclide}
\usetikzlibrary{calc,decorations.pathmorphing,decorations.pathreplacing}
\begin{document}
\title{%s}
\maketitle
""" % title
        footer = r"\end{document}"
        if fmt == 1:
            body = "\n\n".join(questions_data)
        else:
            body = ""
            correct_answers = []
            for content, correct in questions_data:
                body += content + "\n\n"
                correct_answers.append(correct)
            body += "Đáp án\n\n"
            for idx, ans in enumerate(correct_answers, 1):
                body += f"{idx}. {ans} cm\n\n"
        return header + body + footer

    @classmethod
    def create_latex_file_with_format(cls, questions_data, filename: str = "khoang_cach_hai_vat_chuyen_dong.tex",
                                      title: str = "Bài toán", fmt: int = 1) -> str:
        latex_content = cls.create_latex_document_with_format(questions_data, title, fmt)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        print(f"Đã tạo file: {filename}")
        return filename


# =============================
# MAIN
# =============================
def main():
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        fmt = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] in ['1', '2'] else 1
        generator = BoxDistanceGenerator()
        questions_data = generator.generate_multiple_questions_with_format(num_questions, fmt)
        if not questions_data:
            print("Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)
        filename = generator.create_latex_file_with_format(questions_data,
                                                           filename="khoang_cach_hai_vat_chuyen_dong.tex", fmt=fmt)
        print(f"📄 Biên dịch bằng: xelatex {filename}")
        print(f"📋 Format: {fmt} ({'đáp án ngay sau câu hỏi' if fmt == 1 else 'đáp án ở cuối'})")
    except ValueError:
        print("❌ Lỗi: Vui lòng nhập số câu hỏi hợp lệ")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
