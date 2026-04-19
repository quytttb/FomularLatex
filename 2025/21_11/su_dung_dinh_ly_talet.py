import random
import math
import sys
from string import Template
from typing import Any, Dict, Tuple

# ==================== CONFIGURATION & HELPERS ====================

def format_vn_number(value, precision=0):
    """Formats a number to Vietnamese style (comma for decimal)."""
    s = f"{value:.{precision}f}"
    if precision > 0 and '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s.replace('.', ',')

def create_latex_document(content):
    return r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage{tikz}
\usetikzlibrary{patterns, calc, intersections}
\begin{document}
""" + content + r"\end{document}"

# ==================== QUESTION 6: HEXAGON PATH ====================

TEMPLATE_Q6 = Template(
    r"""
Người ta tạo một lối đi xung quanh một sân chơi hình lục giác đều \(ABCDEF\) tâm \(O\) giới hạn bởi các cạnh của lục giác và một đường cong kín \((L)\) (như hình vẽ).
Nếu điểm \(M\) thuộc cạnh của lục giác và tia \(OM\) cắt \((L)\) tại điểm \(N\) thì ta luôn có \(MN = ${d}\) m.
Biết rằng \(OA = ${R}\) m. Diện tích của lối đi đó bằng bao nhiêu mét vuông (làm tròn đến hàng đơn vị).

\begin{center}
${diagram}
\end{center}
"""
)

TEMPLATE_SOL_Q6 = Template(
    r"""
Độ dài lục giác đều là \(a = OA = ${R}\) m nên suy ra \(S_{ABCDEF} = 6 \cdot \frac{a^2\sqrt{3}}{4} = 6 \cdot \frac{${R}^2\sqrt{3}}{4} = ${hex_area} (\text{m}^2)\).\\
Chọn hệ trục tọa độ \(Oxy\) sao cho tọa độ các đỉnh là \(O(0;0), A(${coord_A_x}; ${coord_A_y}), B(${coord_B_x}; ${coord_B_y})\) và đơn vị trên mỗi hệ trục tọa độ là mét.\\
Xét điểm \(M\) thuộc đoạn thẳng \(AB\) (vì tính đối xứng ta sẽ nhân lên sáu lần kết quả này).\\
Ta có: \(M(${coord_A_x}; m) \in [AB], N(x; y)\), trong đó \(${coord_A_y} \le m \le ${coord_B_y}, x > ${coord_A_x}\), suy ra \(ON = \sqrt{x^2+y^2}\).\\
Khi đó: \(OM = ON - MN = \sqrt{x^2+y^2} - ${d}\).\\
Gọi \(H, K\) lần lượt là hình chiếu vuông góc của \(M, N\) lên trục hoành. Theo định lí Thales, ta có:\\
\(\frac{ON}{OM} = \frac{OK}{OH} = \frac{NK}{MH} \Rightarrow \frac{x}{${coord_A_x}} = \frac{\sqrt{x^2+y^2}}{\sqrt{x^2+y^2} - ${d}} = \frac{t}{t-${d}}\), đặt \(t = \sqrt{x^2+y^2}\).\\
Phương trình tương đương: \(${coord_A_x}t = x(t-${d}) \Leftrightarrow t(x-${coord_A_x}) = ${d}x \Leftrightarrow t = \frac{${d}x}{x-${coord_A_x}}\).\\
Mà \(t = \sqrt{x^2+y^2}\) nên suy ra \((L): y = \pm \sqrt{t^2-x^2} = \pm \sqrt{\left(\frac{${d}x}{x-${coord_A_x}}\right)^2 - x^2}\).\\
Khi đó: \(OA: y = -\frac{x}{\sqrt{3}} \cap (L) = P(${coord_P_x}; ${coord_P_y})\) và \(OB: y = \frac{x}{\sqrt{3}} \cap (L) = Q(${coord_Q_x}; ${coord_Q_y})\).\\
Và \((L) \cap Ox \Leftrightarrow \frac{${d}x}{x-${coord_A_x}} = \pm x \Leftrightarrow x = ${d} + ${coord_A_x} \Rightarrow (L) \cap Ox = R(${coord_R_x}; 0)\).\\
Ta có: Diện tích của lối đi là: \(\approx ${result}\) (\(\text{m}^2\)).
"""
)

class Question6:
    def __init__(self):
        self.R = 8
        self.d = 2

    def generate_parameters(self):
        self.R = random.randint(5, 60)
        self.d = random.randint(1, 10)

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        R = self.R
        d = self.d
        
        val_I = 3 * math.sqrt(3) * R * math.log(3)
        area = d * val_I + math.pi * (d**2)

        def fmt_sqrt3(coeff):
            if abs(coeff - round(coeff)) < 1e-9:
                c = int(round(coeff))
                if c == 1: return r"\sqrt{3}"
                if c == -1: return r"-\sqrt{3}"
                return f"{c}" + r"\sqrt{3}"
            else:
                c2 = coeff * 2
                if abs(c2 - round(c2)) < 1e-9:
                    c2 = int(round(c2))
                    return f"\\frac{{{c2}\\sqrt{{3}}}}{{2}}"
                return f"{coeff:.2f}" + r"\sqrt{3}"

        hex_area_coeff = 3 * R * R / 2
        hex_area_str = fmt_sqrt3(hex_area_coeff)

        h_coeff = R / 2
        coord_A_x = fmt_sqrt3(h_coeff)
        coord_A_y = f"-{R//2}" if R % 2 == 0 else f"-{R}/2"
        
        coord_B_x = coord_A_x
        coord_B_y = f"{R//2}" if R % 2 == 0 else f"{R}/2"

        q_coeff = (R + d) / 2
        coord_Q_x = fmt_sqrt3(q_coeff)
        coord_Q_y = f"{(R+d)//2}" if (R+d) % 2 == 0 else f"{(R+d)}/2"
        
        coord_P_x = coord_Q_x
        coord_P_y = f"-{(R+d)//2}" if (R+d) % 2 == 0 else f"-{(R+d)}/2"

        coord_R_x = f"{d} + {coord_A_x}"
        
        return format_vn_number(area, 0), {
            "R": R,
            "d": d,
            "hex_area": hex_area_str,
            "coord_A_x": coord_A_x,
            "coord_A_y": coord_A_y,
            "coord_B_x": coord_B_x,
            "coord_B_y": coord_B_y,
            "coord_P_x": coord_P_x,
            "coord_P_y": coord_P_y,
            "coord_Q_x": coord_Q_x,
            "coord_Q_y": coord_Q_y,
            "coord_R_x": coord_R_x,
            "result": format_vn_number(area, 0)
        }

    def generate_tikz(self) -> str:
        return r"""\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
   \draw[rounded corners=5mm] (-30:2.5)--(30:2.5)--(90:2.5) -- (150:2.5)--(210:2.5)--(-90:2.5)--cycle;
   \draw[fill=violet!30] (-30:2)coordinate (A) --(30:2)coordinate (B)--(90:2)coordinate (C) -- (150:2)coordinate (D)--(210:2)coordinate (E)--(-90:2)coordinate (F)--cycle;
   \draw (0,0)coordinate (O)--(18:1.825)coordinate (M)--(18:2.27)coordinate (N);
   \foreach \p/\r in {A/-40,B/40,C/90,D/140,E/-140,F/-90,M/150,N/0,O/-90}
   \fill (\p) circle (1.2pt) node[shift={(\r:3mm)}]{$\p$};
 \end{tikzpicture}"""

    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        tikz = self.generate_tikz()
        question = TEMPLATE_Q6.substitute(params, diagram=tikz)
        solution = TEMPLATE_SOL_Q6.substitute(params)
        return f"Câu {idx}: {question}\n\nLời giải:\n{solution}\n\nĐáp án: {ans}"

# ==================== QUESTION 9: TRIANGLE PATH ====================

TEMPLATE_Q9 = Template(
    r"""
Người ta tạo một lối đi xung quanh một sân chơi hình tam giác đều \(ABC\) tâm \(O\) giới hạn bởi các cạnh của tam giác và một đường cong kín \((L)\) (như hình vẽ).
Nếu điểm \(M\) thuộc cạnh của tam giác và tia \(OM\) cắt \((L)\) tại điểm \(N\) thì ta luôn có \(MN = ${d}\) m.
Biết rằng \(OA = ${R}\) m thì diện tích của lối đi đó bằng bao nhiêu mét vuông (Kết quả làm tròn đến hàng đơn vị).

\begin{center}
${diagram}
\end{center}
"""
)

TEMPLATE_SOL_Q9 = Template(
    r"""
Độ dài cạnh tam giác đều là \(a = R\sqrt{3} = ${R}\sqrt{3}\) m nên suy ra \(S_{ABC} = \frac{a^2\sqrt{3}}{4} = \frac{(${R}\sqrt{3})^2\sqrt{3}}{4} = ${tri_area} (\text{m}^2)\).\\
Chọn hệ trục tọa độ \(Oxy\) sao cho tọa độ các đỉnh là \(O(0;0), A(${coord_A_x}; ${coord_A_y}), B(${coord_B_x}; ${coord_B_y})\) và đơn vị trên mỗi hệ trục tọa độ là mét.\\
Xét điểm \(M\) thuộc đoạn thẳng \(AB\) (vì tính đối xứng ta sẽ nhân lên ba lần kết quả này).\\
Ta có: \(M(${coord_A_x}; m) \in [AB], N(x; y)\), trong đó \(${coord_A_y} \le m \le ${coord_B_y}, x > ${coord_A_x}\), suy ra \(ON = \sqrt{x^2+y^2}\).\\
Khi đó: \(OM = ON - MN = \sqrt{x^2+y^2} - ${d}\).\\
Gọi \(H, K\) lần lượt là hình chiếu vuông góc của \(M, N\) lên trục hoành. Theo định lí Thales, ta có:\\
\(\frac{ON}{OM} = \frac{OK}{OH} = \frac{NK}{MH} \Rightarrow \frac{x}{${coord_A_x}} = \frac{\sqrt{x^2+y^2}}{\sqrt{x^2+y^2} - ${d}} = \frac{t}{t-${d}}\), đặt \(t = \sqrt{x^2+y^2}\).\\
Phương trình tương đương: \(${coord_A_x}t = x(t-${d}) \Leftrightarrow t(x-${coord_A_x}) = ${d}x \Leftrightarrow t = \frac{${d}x}{x-${coord_A_x}}\).\\
Mà \(t = \sqrt{x^2+y^2}\) nên suy ra \((L): y = \pm \sqrt{t^2-x^2} = \pm \sqrt{\left(\frac{${d}x}{x-${coord_A_x}}\right)^2 - x^2}\).\\
Khi đó: \(OA: y = -\sqrt{3}x \cap (L) = P(${coord_P_x}; ${coord_P_y})\) và \(OB: y = \sqrt{3}x \cap (L) = Q(${coord_Q_x}; ${coord_Q_y})\).\\
Và \((L) \cap Ox \Leftrightarrow \frac{${d}x}{x-${coord_A_x}} = \pm x \Leftrightarrow x = ${d} + ${coord_A_x} \Rightarrow (L) \cap Ox = R(${coord_R_x}; 0)\).\\
Ta có: Diện tích của lối đi là: \(\approx ${result}\) (\(\text{m}^2\)).
"""
)

class Question9:
    def __init__(self):
        self.R = 6
        self.d = 2

    def generate_parameters(self):
        self.R = random.randint(4, 60)
        self.d = random.randint(1, 8)

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        R = self.R
        d = self.d
        
        val_I = 3 * R * math.log(2 + math.sqrt(3))
        area = d * val_I + math.pi * (d**2)

        def fmt_sqrt3(coeff):
            if abs(coeff - round(coeff)) < 1e-9:
                c = int(round(coeff))
                if c == 1: return r"\sqrt{3}"
                if c == -1: return r"-\sqrt{3}"
                return f"{c}" + r"\sqrt{3}"
            else:
                c2 = coeff * 2
                if abs(c2 - round(c2)) < 1e-9:
                    c2 = int(round(c2))
                    return f"\\frac{{{c2}\\sqrt{{3}}}}{{2}}"
                return f"{coeff:.2f}" + r"\sqrt{3}"

        tri_area_coeff = 3 * R * R / 4
        tri_area_str = fmt_sqrt3(tri_area_coeff)

        h_coeff = R / 2
        coord_A_x = f"{R//2}" if R % 2 == 0 else f"{R}/2"
        
        y_coeff = -R / 2
        coord_A_y = fmt_sqrt3(y_coeff)
        
        coord_B_x = coord_A_x
        coord_B_y = fmt_sqrt3(-y_coeff)

        coord_Q_x = f"{d}"
        coord_Q_y = fmt_sqrt3(d)
        
        coord_P_x = f"{d}"
        coord_P_y = fmt_sqrt3(-d)

        if R % 2 == 0:
            coord_R_x = f"{R//2 + d}"
        else:
            coord_R_x = f"\\frac{{{R + 2*d}}}{{2}}"
        
        return format_vn_number(area, 0), {
            "R": R,
            "d": d,
            "tri_area": tri_area_str,
            "coord_A_x": coord_A_x,
            "coord_A_y": coord_A_y,
            "coord_B_x": coord_B_x,
            "coord_B_y": coord_B_y,
            "coord_P_x": coord_P_x,
            "coord_P_y": coord_P_y,
            "coord_Q_x": coord_Q_x,
            "coord_Q_y": coord_Q_y,
            "coord_R_x": coord_R_x,
            "result": format_vn_number(area, 0)
        }

    def generate_tikz(self) -> str:
        return r"""\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.7]
   \path 
   (70:3) coordinate (C)
   (70+120:3) coordinate (A)
   (70+240:3) coordinate (B)
   (70:4.5) coordinate (C')
   (70+120:4.5) coordinate (A')
   (70+240:4.5) coordinate (B')
   ;
   \draw[fill=violet!30] (A)--(C)--(B)--cycle;
   \draw (A')..controls +(190-140:5) and +(70+140:5) ..
   (C')..controls +(70-140:5) and +(310+140:5) ..
   (B')..controls +(310-140:5) and +(190+140:5) .. cycle;
   \draw (0,0) coordinate (O) -- (51:1.98)coordinate (M)--(51:3.4) coordinate (N);
   \foreach \p/\r in {A/190,B/310,C/70,O/190,M/-20,N/40}
   \fill (\p) circle (1.2pt) node[shift={(\r:3mm)}]{$\p$};
 \end{tikzpicture}"""

    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        tikz = self.generate_tikz()
        question = TEMPLATE_Q9.substitute(params, diagram=tikz)
        solution = TEMPLATE_SOL_Q9.substitute(params)
        return f"Câu {idx}: {question}\n\nLời giải:\n{solution}\n\nĐáp án: {ans}"

# ==================== QUESTION 13: SQUARE FLOWER ====================

TEMPLATE_Q13 = Template(
    r"""
Người nghệ sĩ vẽ một bông hoa trên một miếng bìa hình vuông \(ABCD\) tâm \(O\) bằng một đường cong kín \((L)\) rồi tô màu cho bông hoa ở giữa.
Phần bên ngoài đường cong này của hình vuông thì không tô màu (minh họa như hình vẽ).
Nếu điểm \(M\) thuộc cạnh của hình vuông \(ABCD\) và tia \(OM\) cắt \((L)\) tại điểm \(N\) thì \(MN = ${d}\) dm.
Biết rằng \(AB = ${side}\) dm thì phần được nghệ sĩ để trắng có diện tích bằng bao nhiêu \(\text{dm}^2\)? (Kết quả làm tròn đến hàng đơn vị).

\begin{center}
${diagram}
\end{center}
"""
)

TEMPLATE_SOL_Q13 = Template(
    r"""
Diện tích hình vuông là \(S_{ABCD} = a^2 = ${side}^2 = ${sq_area} (\text{dm}^2)\).\\
Chọn hệ trục tọa độ \(Oxy\) sao cho tọa độ các đỉnh là \(O(0;0), A(${coord_A_x}; ${coord_A_y}), B(${coord_B_x}; ${coord_B_y})\) và đơn vị trên mỗi hệ trục tọa độ là dm.\\
Xét điểm \(M\) thuộc đoạn thẳng \(AB\) (vì tính đối xứng ta sẽ nhân lên bốn lần kết quả này).\\
Ta có: \(M(${coord_A_x}; m) \in [AB], N(x; y)\), trong đó \(${coord_A_y} \le m \le ${coord_B_y}, x < ${coord_A_x}\), suy ra \(ON = \sqrt{x^2+y^2}\).\\
Khi đó: \(OM = ON + MN = \sqrt{x^2+y^2} + ${d}\).\\
Gọi \(H, K\) lần lượt là hình chiếu vuông góc của \(M, N\) lên trục hoành. Theo định lí Thales, ta có:\\
\(\frac{ON}{OM} = \frac{OK}{OH} = \frac{NK}{MH} \Rightarrow \frac{x}{${coord_A_x}} = \frac{\sqrt{x^2+y^2}}{\sqrt{x^2+y^2} + ${d}} = \frac{t}{t+${d}}\), đặt \(t = \sqrt{x^2+y^2}\).\\
Phương trình tương đương: \(${coord_A_x}t = x(t+${d}) \Leftrightarrow t(${coord_A_x}-x) = ${d}x \Leftrightarrow t = \frac{${d}x}{${coord_A_x}-x}\).\\
Mà \(t = \sqrt{x^2+y^2}\) nên suy ra \((L): y = \pm \sqrt{t^2-x^2} = \pm \sqrt{\left(\frac{${d}x}{${coord_A_x}-x}\right)^2 - x^2}\).\\
Khi đó: \(OA: y = -x \cap (L) = P(${coord_P_x}; ${coord_P_y})\) và \(OB: y = x \cap (L) = Q(${coord_Q_x}; ${coord_Q_y})\).\\
Và \((L) \cap Ox \Leftrightarrow \frac{${d}x}{${coord_A_x}-x} = \pm x \Leftrightarrow x = ${coord_A_x} - ${d} \Rightarrow (L) \cap Ox = R(${coord_R_x}; 0)\).\\
Ta có: Diện tích phần để trắng là: \(\approx ${result}\) (\(\text{dm}^2\)).
"""
)

class Question13:
    def __init__(self):
        self.side = 8
        self.d = 2

    def generate_parameters(self):
        self.side = random.randint(10, 70)
        max_d = int(self.side / 2) - 1
        if max_d < 1: max_d = 1
        self.d = random.randint(1, max_d)

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        a = self.side
        d = self.d
        
        val_I = 4 * a * math.log(math.sqrt(2) + 1)
        area = d * val_I - math.pi * (d**2)

        def fmt_num(val):
            if val == int(val): return str(int(val))
            return f"{val:.1f}".replace('.', ',')

        sq_area = a * a

        h = a / 2
        coord_A_x = fmt_num(h)
        coord_A_y = fmt_num(-h)
        
        coord_B_x = fmt_num(h)
        coord_B_y = fmt_num(h)

        val_x_Q = h - d / math.sqrt(2)
        coord_Q_x = fmt_num(val_x_Q)
        coord_Q_y = fmt_num(val_x_Q)
        
        coord_P_x = fmt_num(val_x_Q)
        coord_P_y = fmt_num(-val_x_Q)

        coord_R_x = fmt_num(h - d)
        
        return format_vn_number(area, 0), {
            "side": a,
            "d": d,
            "sq_area": sq_area,
            "coord_A_x": coord_A_x,
            "coord_A_y": coord_A_y,
            "coord_B_x": coord_B_x,
            "coord_B_y": coord_B_y,
            "coord_P_x": coord_P_x,
            "coord_P_y": coord_P_y,
            "coord_Q_x": coord_Q_x,
            "coord_Q_y": coord_Q_y,
            "coord_R_x": coord_R_x,
            "result": format_vn_number(area, 0)
        }

    def generate_tikz(self) -> str:
        return r"""\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.8]
   \draw[line width=1pt,name path=vuonglon] (-3,-3)coordinate (B) -- (3,-3)coordinate (D)--(3,3)coordinate (C)--(-3,3)coordinate (A)--cycle ;
   \draw[fill=orange!20,draw=red,line width=1pt,name path=vuong] (45:2) ..controls +(-140:0.5) and +(-40:0.5) ..  (135:2) ..controls +(-40:0.5) and +(40:0.5) ..  (-135:2) ..controls +(40:0.5) and +(140:0.5) ..(-45:2) ..controls +(140:0.5) and +(-140:0.5) ..
   cycle;
   \draw[name path=duong] (0,0)--++(150:5);
   \path [name intersections={of=duong and vuong, by=N}];
   \path [name intersections={of=duong and vuonglon, by=M}];
   \fill 
   (0,0) circle(2pt) node[right]{$O$}
   (N) circle(2pt) node[below left]{$N$}
   (M) circle(2pt) node[below left]{$M$}
   (45:2)circle(2pt)
   (135:2)circle(2pt)
   (-135:2)circle(2pt)
   (-45:2)circle(2pt)
   (-70:2) node[]{$(L)$}
   ;
   \foreach \p/\r in {A/140,B/-140,C/40,D/-40}
   \fill (\p) circle (1.2pt) node[shift={(\r:3mm)}]{$\p$};
 \end{tikzpicture}"""

    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        tikz = self.generate_tikz()
        question = TEMPLATE_Q13.substitute(params, diagram=tikz)
        solution = TEMPLATE_SOL_Q13.substitute(params)
        return f"Câu {idx}: {question}\n\nLời giải:\n{solution}\n\nĐáp án: {ans}"

# ==================== MAIN ====================

def main():
    question_types = [Question6, Question9, Question13]
    
    num_questions = 3
    question_type_idx = None
    
    if len(sys.argv) > 1:
        try:
            num_questions = int(sys.argv[1])
        except ValueError:
            print("Tham số đầu tiên (số câu hỏi) phải là số nguyên.")
            return
    
    if len(sys.argv) > 2:
        try:
            question_type_idx = int(sys.argv[2])
            if question_type_idx < 0 or question_type_idx >= len(question_types):
                print(f"Tham số thứ hai (loại câu hỏi) phải từ 0 đến {len(question_types)-1}.")
                return
        except ValueError:
            print("Tham số thứ hai (loại câu hỏi) phải là số nguyên.")
            return
        
    questions = []
    for i in range(num_questions):
        if question_type_idx is not None:
            q_class = question_types[question_type_idx]
        else:
            q_class = question_types[i % len(question_types)]
        
        q_instance = q_class()
        questions.append(q_instance.generate_question(i + 1))
        
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    import os
    output_path = os.path.join(os.path.dirname(__file__), "su_dung_dinh_ly_talet.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong su_dung_dinh_ly_talet.tex")

if __name__ == "__main__":
    main()
