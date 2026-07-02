import math
import random
import sys
from typing import List, Tuple
from scipy.optimize import minimize_scalar


# Tất cả đường chéo của hình hộp ABCD.A'B'C'D' (mỗi đường chéo một hướng)
ALL_DIAGONALS = [
    # Mặt ABB'A' (y=0)
    ("B'", "A"), ("B", "A'"),
    # Mặt DCC'D' (y=AD)
    ("C", "D'"), ("D", "C'"),
    # Mặt ADD'A' (x=0)
    ("A", "D'"), ("D", "A'"),
    # Mặt BCC'B' (x=AB)
    ("B", "C'"), ("C", "B'"),
    # Mặt đáy ABCD (z=0)
    ("A", "C"), ("B", "D"),
    # Mặt trên A'B'C'D' (z=AA')
    ("A'", "C'"), ("B'", "D'"),
    # Đường chéo không gian
    ("A", "C'"), ("B", "D'"), ("C", "A'"), ("D", "B'"),
]

# Tọa độ 2D chiếu của các đỉnh trong hình TikZ
TIKZ_2D_COORDS = {
    "A": (1.5, 1.5), "B": (0.0, 0.0), "C": (4.0, 0.0), "D": (5.5, 1.5),
    "A'": (1.5, 4.5), "B'": (0.0, 3.0), "C'": (4.0, 3.0), "D'": (5.5, 4.5),
}


def latex_vertex(label: str) -> str:
    """Chuyển nhãn đỉnh A' thành LaTeX an toàn (tránh lỗi parser Azota)."""
    if label.endswith("'"):
        return label[:-1] + r"^{\prime}"
    return label


def latex_segment(start: str, end: str) -> str:
    return latex_vertex(start) + latex_vertex(end)


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

        # Chọn ngẫu nhiên 2 đường chéo khác nhau cho M và N
        chosen = random.sample(ALL_DIAGONALS, 2)
        # Ngẫu nhiên đổi chiều mỗi đường chéo
        self.diag_M = chosen[0] if random.random() < 0.5 else (chosen[0][1], chosen[0][0])
        self.diag_N = chosen[1] if random.random() < 0.5 else (chosen[1][1], chosen[1][0])

        self.calculate_process_variables()

    def get_3d_coord(self, label):
        coords = {
            "A":  (0,        0,        0),
            "B":  (self.AB,  0,        0),
            "C":  (self.AB,  self.AD,  0),
            "D":  (0,        self.AD,  0),
            "A'": (0,        0,        self.AA_prime),
            "B'": (self.AB,  0,        self.AA_prime),
            "C'": (self.AB,  self.AD,  self.AA_prime),
            "D'": (0,        self.AD,  self.AA_prime),
        }
        return coords[label]

    def calculate_process_variables(self):
        s_M, e_M = self.diag_M
        s_N, e_N = self.diag_N

        self.start_M = self.get_3d_coord(s_M)
        self.end_M   = self.get_3d_coord(e_M)
        self.start_N = self.get_3d_coord(s_N)
        self.end_N   = self.get_3d_coord(e_N)

        self.vec_M = tuple(e - s for s, e in zip(self.start_M, self.end_M))
        self.vec_N = tuple(e - s for s, e in zip(self.start_N, self.end_N))

        self.dist_M = math.sqrt(sum(x ** 2 for x in self.vec_M))
        self.dist_N = math.sqrt(sum(x ** 2 for x in self.vec_N))

        self.vel_M = tuple(self.v_M * x / self.dist_M for x in self.vec_M)
        self.vel_N = tuple(self.v_N * x / self.dist_N for x in self.vec_N)

        self.calculate_minimum_distance()

    def position_M(self, t):
        return tuple(s + v * t for s, v in zip(self.start_M, self.vel_M))

    def position_N(self, t):
        return tuple(s + v * t for s, v in zip(self.start_N, self.vel_N))

    def distance_function(self, t):
        pos_M = self.position_M(t)
        pos_N = self.position_N(t)
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(pos_M, pos_N)))

    def calculate_minimum_distance(self):
        t_max_M = self.dist_M / self.v_M
        t_max_N = self.dist_N / self.v_N
        t_max = min(t_max_M, t_max_N)
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

    def _fmt_signed(self, base, coeff):
        """Trả về chuỗi 'base + coeff*t' hoặc 'base - |coeff|*t' cho đẹp."""
        if coeff >= 0:
            return rf"{base} + {coeff:.4f}t"
        else:
            return rf"{base} - {abs(coeff):.4f}t"

    def generate_tikz_picture(self):
        s_M, e_M = self.diag_M
        s_N, e_N = self.diag_N

        sx_M, sy_M = TIKZ_2D_COORDS[s_M]
        ex_M, ey_M = TIKZ_2D_COORDS[e_M]
        sx_N, sy_N = TIKZ_2D_COORDS[s_N]
        ex_N, ey_N = TIKZ_2D_COORDS[e_N]

        mx_M, my_M = (sx_M + ex_M) / 2, (sy_M + ey_M) / 2
        mx_N, my_N = (sx_N + ex_N) / 2, (sy_N + ey_N) / 2

        ax_M = sx_M + (ex_M - sx_M) * 0.10
        ay_M = sy_M + (ey_M - sy_M) * 0.10
        bx_M = sx_M + (ex_M - sx_M) * 0.30
        by_M = sy_M + (ey_M - sy_M) * 0.30

        ax_N = sx_N + (ex_N - sx_N) * 0.10
        ay_N = sy_N + (ey_N - sy_N) * 0.10
        bx_N = sx_N + (ex_N - sx_N) * 0.30
        by_N = sy_N + (ey_N - sy_N) * 0.30

        return rf"""
\begin{{tikzpicture}}[scale=1.0]
%% Các đỉnh hình hộp
\coordinate (B) at (0,0);
\coordinate (C) at (4,0);
\coordinate (A) at (1.5,1.5);
\coordinate (D) at (5.5,1.5);
\coordinate (B') at (0,3);
\coordinate (C') at (4,3);
\coordinate (A') at (1.5,4.5);
\coordinate (D') at (5.5,4.5);
%% Cạnh nhìn thấy
\draw (B) -- (C);
\draw (B') -- (C') -- (D') -- (A') -- cycle;
\draw (B) -- (B');
\draw (C) -- (C');
\draw (C) -- (D);
\draw (D) -- (D');
%% Cạnh ẩn
\draw[dashed] (B) -- (A);
\draw[dashed] (A) -- (D);
\draw[dashed] (A') -- (A);
%% Điểm M và N (giữa đường chéo tương ứng)
\coordinate (M) at ({mx_M:.2f},{my_M:.2f});
\coordinate (N) at ({mx_N:.2f},{my_N:.2f});
%% Đường đi của M (đứt nét)
\draw[dashed, thick] ({s_M}) -- ({e_M});
%% Đường đi của N
\draw[thick] ({s_N}) -- ({e_N});
%% Mũi tên chỉ hướng di chuyển
\draw[->, thick] ({ax_M:.2f},{ay_M:.2f}) -- ({bx_M:.2f},{by_M:.2f});
\draw[->, thick] ({ax_N:.2f},{ay_N:.2f}) -- ({bx_N:.2f},{by_N:.2f});
%% Đánh dấu các đỉnh
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
%% Nhãn
\node[below right] at (A) {{\(A\)}};
\node[below left] at (B) {{\(B\)}};
\node[below right] at (C) {{\(C\)}};
\node[below right] at (D) {{\(D\)}};
\node[above right] at (A') {{\(A'\)}};
\node[above left] at (B') {{\(B'\)}};
\node[above left] at (C') {{\(C'\)}};
\node[above right] at (D') {{\(D'\)}};
\node[right] at (M) {{\(M\)}};
\node[right] at (N) {{\(N\)}};
\end{{tikzpicture}}"""

    def generate_question_text(self):
        s_M, e_M = self.diag_M
        s_N, e_N = self.diag_N
        tikz = self.generate_tikz_picture()
        ls_M, le_M = latex_vertex(s_M), latex_vertex(e_M)
        ls_N, le_N = latex_vertex(s_N), latex_vertex(e_N)

        question = rf"""
Với một hình hộp chữ nhật $ABCD.A^{{\prime}}B^{{\prime}}C^{{\prime}}D^{{\prime}}$ có $AB={self.AB}$, $AD={self.AD}$, $AA^{{\prime}}={self.AA_prime}$ như hình vẽ. Ở cùng một thời điểm hai con kiến coi như bò chuyển động thẳng đều, con kiến $M$ bò từ ${ls_M}$ đến ${le_M}$ với tốc độ ${self.v_M}\,\mathrm{{cm/s}}$ và con kiến $N$ bò từ ${ls_N}$ đến ${le_N}$ với tốc độ ${self.v_N}\,\mathrm{{cm/s}}$. Hãy tính khoảng cách nhỏ nhất giữa hai con kiến theo đơn vị centimet (làm tròn kết quả đến hàng phần mười)?

{tikz}
"""
        return question

    def generate_solution(self):
        s_M, e_M = self.diag_M
        s_N, e_N = self.diag_N
        ls_M, le_M = latex_vertex(s_M), latex_vertex(e_M)
        ls_N, le_N = latex_vertex(s_N), latex_vertex(e_N)
        seg_M = latex_segment(s_M, e_M)
        seg_N = latex_segment(s_N, e_N)

        sx_M, sy_M, sz_M = self.start_M
        ex_M, ey_M, ez_M = self.end_M
        sx_N, sy_N, sz_N = self.start_N
        ex_N, ey_N, ez_N = self.end_N

        vx_M, vy_M, vz_M = self.vel_M
        vx_N, vy_N, vz_N = self.vel_N

        dist_M_sq = int(round(sum(x ** 2 for x in self.vec_M)))
        dist_N_sq = int(round(sum(x ** 2 for x in self.vec_N)))

        vec_M_str = f"({self.vec_M[0]},\\ {self.vec_M[1]},\\ {self.vec_M[2]})"
        vec_N_str = f"({self.vec_N[0]},\\ {self.vec_N[1]},\\ {self.vec_N[2]})"

        pos_M_str = (
            f"\\left({self._fmt_signed(sx_M, vx_M)},\\;"
            f" {self._fmt_signed(sy_M, vy_M)},\\;"
            f" {self._fmt_signed(sz_M, vz_M)}\\right)"
        )
        pos_N_str = (
            f"\\left({self._fmt_signed(sx_N, vx_N)},\\;"
            f" {self._fmt_signed(sy_N, vy_N)},\\;"
            f" {self._fmt_signed(sz_N, vz_N)}\\right)"
        )

        solution = rf"""
Dữ kiện:
+ Hình hộp chữ nhật $ABCD.A^{{\prime}}B^{{\prime}}C^{{\prime}}D^{{\prime}}$ có:
\[
AB = {self.AB},\quad AD = {self.AD},\quad AA^{{\prime}} = {self.AA_prime}
\]
+ Gán tọa độ:
\[
A=(0,0,0),\quad B=({self.AB},0,0),\quad C=({self.AB},{self.AD},0),\quad D=(0,{self.AD},0)
\]
\[
A^{{\prime}}=(0,0,{self.AA_prime}),\quad B^{{\prime}}=({self.AB},0,{self.AA_prime}),\quad C^{{\prime}}=({self.AB},{self.AD},{self.AA_prime}),\quad D^{{\prime}}=(0,{self.AD},{self.AA_prime})
\]
+ Con kiến $M$ bò từ ${ls_M}=({sx_M},{sy_M},{sz_M})$ đến ${le_M}=({ex_M},{ey_M},{ez_M})$ với tốc độ ${self.v_M}\,\text{{cm/s}}$
+ Con kiến $N$ bò từ ${ls_N}=({sx_N},{sy_N},{sz_N})$ đến ${le_N}=({ex_N},{ey_N},{ez_N})$ với tốc độ ${self.v_N}\,\text{{cm/s}}$

Bước 1: Phương trình chuyển động
Con kiến $M$: Vector chỉ phương:
\[
\overrightarrow{{{seg_M}}} = ({ex_M}-{sx_M},\; {ey_M}-{sy_M},\; {ez_M}-{sz_M}) = {vec_M_str}
\]
Chiều dài ${seg_M}$:
\[
|{seg_M}| = \sqrt{{{dist_M_sq}}} \approx {self.dist_M:.4f}
\]
Vị trí tại thời điểm $t$:
\[
M(t) = ({sx_M},{sy_M},{sz_M}) + \frac{{{self.v_M}}}{{\sqrt{{{dist_M_sq}}}}} \cdot t \cdot {vec_M_str} = {pos_M_str}
\]
Con kiến $N$: Vector chỉ phương:
\[
\overrightarrow{{{seg_N}}} = ({ex_N}-{sx_N},\; {ey_N}-{sy_N},\; {ez_N}-{sz_N}) = {vec_N_str}
\]
Chiều dài ${seg_N}$:
\[
|{seg_N}| = \sqrt{{{dist_N_sq}}} \approx {self.dist_N:.4f}
\]
Vị trí tại thời điểm $t$:
\[
N(t) = ({sx_N},{sy_N},{sz_N}) + \frac{{{self.v_N}}}{{\sqrt{{{dist_N_sq}}}}} \cdot t \cdot {vec_N_str} = {pos_N_str}
\]
Bước 2: Khoảng cách giữa hai con kiến
\[
d(t) = \sqrt{{(x_M-x_N)^2 + (y_M-y_N)^2 + (z_M-z_N)^2}}
\]
Bước 3: Tìm khoảng cách nhỏ nhất
\[
d'(t)=0 \Leftrightarrow t \approx {self.t_optimal:.2f}\,\text{{s}} \Rightarrow d_{{\min}} \approx {self.d_min:.1f}\,\text{{cm}}
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
