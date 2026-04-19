"""
Hệ thống sinh đề toán về thể tích nước trong cốc hình trụ khi nghiêng
Bài toán: Cốc hình trụ đựng nước, khi nghiêng đến mức nước chạm miệng cốc
và ở đáy mực nước trùng với đường kính đáy. Tính thể tích nước.
Công thức: V = (2/3) * R³ * tan(α) với tan(α) = h/R => V = (2/3) * R² * h
"""

import logging
import os
import random
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from string import Template
from typing import Any, Dict, List, Optional, Tuple

import sympy as sp

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

# ==============================================================================
# CẤU HÌNH VÀ HẰNG SỐ
# ==============================================================================

@dataclass
class GeneratorConfig:
    """Cấu hình cho generator"""
    seed: Optional[int] = None
    exact_mode: bool = True


# 20 giá trị cho đường kính (ưu tiên số chẵn để R nguyên)
# Chọn các giá trị chẵn từ 4 đến 42
DIAMETER_VALUES: List[int] = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22,
                               24, 26, 28, 30, 32, 34, 36, 38, 40, 42]

# 20 giá trị cho chiều cao (từ 6 đến 25)
HEIGHT_VALUES: List[int] = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                            16, 17, 18, 19, 20, 21, 22, 23, 24, 25]


# ==============================================================================
# HÀM TIỆN ÍCH
# ==============================================================================

def latex_number(value: Any) -> str:
    """Chuyển số thành dạng LaTeX"""
    try:
        return sp.latex(sp.nsimplify(value))
    except Exception:
        return str(value)


def to_decimal_comma(value: Any) -> str:
    """Chuyển dấu chấm thành dấu phẩy cho số thập phân"""
    return str(value).replace(".", ",")


# ==============================================================================
# HÀM TÍNH TOÁN HÌNH HỌC
# ==============================================================================

def tilted_water_volume(R: sp.Expr, h: sp.Expr) -> sp.Expr:
    """
    Tính thể tích nước trong cốc hình trụ khi nghiêng.
    
    Khi nghiêng cốc sao cho:
    - Nước chạm miệng cốc (điểm B)
    - Ở đáy, mực nước trùng với đường kính (qua O)
    
    Ta có: tan(∠AOB) = AB/OB = h/R
    
    Công thức thể tích: V = (2/3) * R³ * tan(α)
    Thay tan(α) = h/R: V = (2/3) * R³ * (h/R) = (2/3) * R² * h
    
    Params:
    - R: bán kính đáy cốc
    - h: chiều cao cốc
    
    Returns:
    - Thể tích nước (đơn vị cm³)
    """
    return sp.Rational(2, 3) * R**2 * h


def tilted_water_volume_with_tan(R: sp.Expr, h: sp.Expr) -> Tuple[sp.Expr, sp.Expr]:
    """
    Tính thể tích nước với công thức đầy đủ có tan(α)
    
    Returns:
    - tan_alpha: giá trị tan(α) = h/R
    - volume: thể tích V = (2/3) * R³ * tan(α)
    """
    tan_alpha = h / R
    volume = sp.Rational(2, 3) * R**3 * tan_alpha
    return sp.nsimplify(tan_alpha), sp.nsimplify(volume)


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

TEMPLATE_QUESTION_TILTED = Template(r"""
Bạn A có một cốc thuỷ tinh hình trụ, đường kính trong lòng đáy cốc là ${diameter} cm, 
chiều cao trong lòng cốc là ${height} cm đang đựng một lượng nước. 
Bạn A nghiêng cốc nước, vừa lúc khi nước chạm miệng cốc thì ở đáy mực nước trùng với đường kính đáy. 
Thể tích lượng nước có trong cốc bằng bao nhiêu? (Kết quả làm tròn đến hàng đơn vị, đơn vị cm³)

\begin{center}
${diagram}
\end{center}
""")


TEMPLATE_SOLUTION_TILTED = Template(r"""
Lời giải:

Ta có cốc hình trụ với:
\begin{itemize}
    \item Đường kính đáy: \(d = ${diameter}\) cm \(\Rightarrow\) Bán kính: \(R = ${radius}\) cm
    \item Chiều cao: \(h = ${height}\) cm
\end{itemize}

Khi nghiêng cốc, gọi:
\begin{itemize}
    \item \(O\) là tâm đáy cốc
    \item \(B\) là điểm nước chạm miệng cốc (trên đường sinh)
    \item \(A\) là điểm trên đường kính đáy (mực nước ở đáy)
\end{itemize}

Bước 1: Tính góc nghiêng

Ta có: \(\tan(\widehat{AOB}) = \dfrac{AB}{OB} = \dfrac{h}{R} = \dfrac{${height}}{${radius}} = ${tan_alpha}\)

Bước 2: Áp dụng công thức thể tích

Thể tích nước trong cốc nghiêng (với mực nước qua tâm đáy) được tính bằng công thức:
\[
V = \frac{2}{3} \cdot R^3 \cdot \tan\alpha
\]

Thay số:
\[
V = \frac{2}{3} \cdot ${radius}^3 \cdot ${tan_alpha} = \frac{2}{3} \cdot ${R_cubed} \cdot ${tan_alpha} = ${V_exact} \text{ cm}^3
\]

Bước 3: Làm tròn kết quả
\[
V \approx ${V_numeric} \text{ cm}^3
\]

Đáp án: ${answer}
""")


# ==============================================================================
# LỚP CƠ SỞ VÀ CÀI ĐẶT
# ==============================================================================

class BaseTiltedCylinderQuestion(ABC):
    """Lớp cơ sở cho các bài toán cốc nghiêng"""
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.correct_answer: Optional[str] = None
        self.config = config or GeneratorConfig()
    
    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh các tham số cho bài toán"""
        pass
    
    @abstractmethod
    def calculate_answer(self) -> str:
        """Tính đáp án"""
        pass
    
    @abstractmethod
    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        pass
    
    @abstractmethod
    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết"""
        pass
    
    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        """Tạo câu hỏi chỉ có đề bài và lời giải"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        question_text = self.generate_question_text().strip()
        solution = self.generate_solution().strip()
        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += solution + "\n"
        return question_content, self.correct_answer
    
    def generate_tikz_diagram(self) -> str:
        """Tạo hình vẽ TikZ cho cốc đứng và cốc nghiêng"""
        params = self.parameters
        if not params:
            return ""
        
        tikz_code = r"""
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
    \def\a{1} % bán trục lớn = bán kính trụ
    \def\b{0.4} % bán trục nhỏ
    \def\h{3} % chiều cao trụ
    \draw (\a,0)--(\a,\h) (-\a,0)--(-\a,\h);
    \path (-\a,0) coordinate (A);
    \path (\a,0) coordinate (H);
    \path (-\a,\h) coordinate (a);
    
    % Tìm trung điểm của A và H, đặt tên là O
    \path (A) -- (H) coordinate[pos=0.5] (O);
    
    \coordinate(M) at ([shift={(O)}]-70:\a cm and \b cm);
    \draw[draw=none] (O) ellipse (\a cm and \b cm);
    \path ($(O)!-1!(M)$) coordinate (N);
    
    \draw[fill=gray!30] (-1,1)arc (-180:-360:\a cm and \b cm) --++(0,-1)
    arc (0:-180:\a cm and \b cm)--cycle
    ;
    \draw[fill=gray!30] (-1,1)arc (180:360:\a cm and \b cm);
    \coordinate(C) at ([shift={(O)}]0:\a cm and \b cm);
    \path ($(C) + (a) - (A)$) coordinate (B);
    \draw[dashed] (\a,0) arc [x radius=\a, y radius=\b, start angle=0, end angle=180];
    \draw (-\a,0) arc [x radius=\a, y radius=\b, start angle=180, end angle=360];
    \draw (0,\h) ellipse (\a cm and \b cm);
    
\end{tikzpicture}
\begin{tikzpicture}[rotate=-70,scale=2]
    \def\a{1} % bán trục lớn = bán kính trụ
    \def\b{0.4} % bán trục nhỏ
    \def\h{3} % chiều cao trụ
    \draw (\a,0)--(\a,\h) (-\a,0)--(-\a,\h);
    \path (-\a,0) coordinate (A);
    \path (\a,0) coordinate (H);
    \path (-\a,\h) coordinate (a);
    
    % Tìm trung điểm của A và H, đặt tên là O
    \path (A) -- (H) coordinate[pos=0.5] (O);
    
    \coordinate(M) at ([shift={(O)}]-70:\a cm and \b cm);
    \draw[draw=none] (O) ellipse (\a cm and \b cm);
    \path ($(O)!-1!(M)$) coordinate (N);
    
    \coordinate(C) at ([shift={(O)}]0:\a cm and \b cm);
    \path ($(C) + (a) - (A)$) coordinate (B);
    \fill[color=gray!30, draw=none]
    (M) .. controls (0.8,1.5) and (1,2.6) .. (B)--(H);
    \fill[color=gray!30, draw=none]
    (M) arc [x radius=\a, y radius=\b, start angle=-70, end angle=110]--(N);
    \fill[color=gray!50, draw=none]
    (O) -- (M) .. controls (0.8,1.6) and (1,2.8) .. (B);
    \fill[color=gray!50, draw=none]
    (O) -- (N) .. controls (0.6,2.6) and (0.8,3.3) .. (B);
    \draw[dashed](M)--(N) (O)--(B) (O)--(H);
    \draw (M) .. controls (0.8,1.6) and (1,2.8) .. (B);
    \draw[dashed] (N) .. controls (0.6,2.6) and (0.8,3.3) .. (B);
    \draw[dashed] (\a,0) arc [x radius=\a, y radius=\b, start angle=0, end angle=180];
    \draw (-\a,0) arc [x radius=\a, y radius=\b, start angle=180, end angle=360];
    \draw (0,\h) ellipse (\a cm and \b cm);
    
\end{tikzpicture}
"""
        return tikz_code
    
    @staticmethod
    def create_latex_document_with_format(
        questions_data: List[Tuple[str, str]],
        title: str = "Bài tập Thể tích nước trong cốc nghiêng",
    ) -> str:
        """Tạo tài liệu LaTeX hoàn chỉnh"""
        
        questions_content = "\n\n".join(
            [q_content for q_content, _ in questions_data]
        )
        
        latex_document = rf"""\documentclass[a4paper,12pt]{{article}}
\usepackage{{amsmath, amsfonts, amssymb}}
\usepackage{{geometry}}
\geometry{{a4paper, margin=1in}}
\usepackage{{fontspec}}
\usepackage{{polyglossia}}
\setmainlanguage{{vietnamese}}
\setmainfont{{Times New Roman}}
\usepackage{{tikz}}
\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing,intersections}}
\usepackage{{enumitem}}

\title{{{title}}}
\author{{Generator}}
\date{{\today}}

\begin{{document}}
\maketitle

{questions_content}

\end{{document}}
"""
        return latex_document


class TiltedCylinderVolumeQuestion(BaseTiltedCylinderQuestion):
    """Bài toán tính thể tích nước trong cốc nghiêng"""
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên"""
        diameter = random.choice(DIAMETER_VALUES)
        height = random.choice(HEIGHT_VALUES)
        radius = diameter // 2  # Đường kính chẵn nên R nguyên
        
        return {
            "diameter": diameter,
            "height": height,
            "radius": radius,
        }
    
    def calculate_answer(self) -> str:
        """Tính thể tích nước và làm tròn đến hàng đơn vị"""
        params = self.parameters
        R = sp.Integer(params["radius"])
        h = sp.Integer(params["height"])
        
        # Tính thể tích bằng SymPy
        V_exact = tilted_water_volume(R, h)
        
        # Chuyển sang số và làm tròn
        V_numeric = float(V_exact.evalf())
        V_rounded = round(V_numeric)
        
        return str(V_rounded)
    
    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        params = self.parameters
        diameter = params["diameter"]
        height = params["height"]
        
        diagram = self.generate_tikz_diagram()
        
        return TEMPLATE_QUESTION_TILTED.substitute(
            diameter=diameter,
            height=height,
            diagram=diagram,
        )
    
    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết"""
        params = self.parameters
        diameter = params["diameter"]
        height = params["height"]
        radius = params["radius"]
        
        R = sp.Integer(radius)
        h = sp.Integer(height)
        
        # Tính các giá trị
        tan_alpha, V_exact = tilted_water_volume_with_tan(R, h)
        R_cubed = R**3
        
        V_numeric = float(V_exact.evalf())
        V_rounded = round(V_numeric)
        
        return TEMPLATE_SOLUTION_TILTED.substitute(
            diameter=diameter,
            height=height,
            radius=radius,
            tan_alpha=sp.latex(tan_alpha),
            R_cubed=R_cubed,
            V_exact=sp.latex(V_exact),
            V_numeric=f"{V_numeric:.2f}",
            answer=V_rounded,
        )


# ==============================================================================
# HÀM MAIN
# ==============================================================================

def get_available_question_types():
    """Trả về danh sách các loại câu hỏi có sẵn"""
    return [
        TiltedCylinderVolumeQuestion,
    ]


def main():
    """
    Hàm main để chạy generator
    Usage: python tilted_cylinder_water_questions.py <num_questions> [seed]
    """
    try:
        # Parse arguments
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else None
        
        # Lấy seed từ environment variable nếu có
        if seed is None:
            seed = os.environ.get("OPT_SEED")
            if seed:
                seed = int(seed)
        
        if seed is not None:
            random.seed(seed)
            logging.info(f"Sử dụng seed: {seed}")
        
        logging.info(f"Đang sinh {num_questions} câu hỏi thể tích nước trong cốc nghiêng...")
        
        questions_data: List[Tuple[str, str]] = []
        
        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            question = TiltedCylinderVolumeQuestion(config)
            question_content, correct_answer = question.generate_question_only(i + 1)
            questions_data.append((question_content, correct_answer))
            logging.info(f"  Câu {i + 1}: Đáp án = {correct_answer} cm³")
        
        # Tạo tài liệu LaTeX
        latex_content = BaseTiltedCylinderQuestion.create_latex_document_with_format(
            questions_data,
            title="Bài tập Thể tích nước trong cốc nghiêng"
        )
        
        # Ghi file
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "tilted_cylinder_water_questions.tex")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")
        
        # In đáp án
        print("\n=== ĐÁP ÁN ===")
        for i, (_, answer) in enumerate(questions_data):
            print(f"Câu {i + 1}: {answer} cm³")
        
    except ValueError as e:
        print(f"Lỗi: Tham số không hợp lệ - {e}")
        print("Usage: python tilted_cylinder_water_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")
        raise


if __name__ == "__main__":
    main()
