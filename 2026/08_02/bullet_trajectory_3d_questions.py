"""
Hệ thống sinh đề toán về đường đạn trong không gian 3D
Bài toán: Tìm khoảng cách CD khi biết điểm va chạm M
Hệ tọa độ Oxyz
Dạng câu hỏi: Điền số (kết quả làm tròn đến hàng phần chục)
"""

import logging
import math
import os
import random
import sys
from dataclasses import dataclass
from string import Template
from typing import Any, Dict, List, Optional, Tuple

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

# ==============================================================================
# CẤU HÌNH VÀ HẰNG SỐ
# ==============================================================================

@dataclass
class GeneratorConfig:
    """Cấu hình cho generator"""
    seed: Optional[int] = None


# 20 giá trị cho mỗi tham số
A_X_VALUES: List[int] = list(range(3, 13))       # 3 đến 12 (10 giá trị)
A_Y_VALUES: List[int] = list(range(5, 15))       # 5 đến 14 (10 giá trị)
A_Z_VALUES: List[int] = list(range(8, 18))       # 8 đến 17 (10 giá trị)

# Vector AB - các thành phần nhỏ để dễ tính
VEC_AB_X_VALUES: List[int] = [1, 2, 3]
VEC_AB_Y_VALUES: List[int] = [1, 2, 3, 4]
VEC_AB_Z_VALUES: List[int] = [1, 2, 3, 4]

C_X_VALUES: List[int] = list(range(12, 22))      # 12 đến 21 (10 giá trị)
C_Y_VALUES: List[int] = list(range(14, 24))      # 14 đến 23 (10 giá trị)
C_Z_VALUES: List[int] = list(range(3, 13))       # 3 đến 12 (10 giá trị)

# Khoảng cách AM (100 đến 200, bước 5)
AM_DIST_VALUES: List[int] = list(range(100, 205, 5))  # 21 giá trị

# Cao độ điểm D (20 đến 40, bước 1)
D_ALTITUDE_VALUES: List[int] = list(range(20, 41))    # 21 giá trị


# ==============================================================================
# HÀM TIỆN ÍCH
# ==============================================================================

def format_decimal_vn(val: float, decimals: int = 1) -> str:
    """Format số thập phân với dấu phẩy"""
    formatted = f"{val:.{decimals}f}".rstrip('0').rstrip('.')
    return formatted.replace(".", ",")


def format_decimal_dot(val: float, decimals: int = 1) -> str:
    """Format số thập phân với dấu chấm"""
    return f"{val:.{decimals}f}".rstrip('0').rstrip('.')


def format_point_3d(name: str, x: int, y: int, z: int) -> str:
    """Format tọa độ điểm 3D theo kiểu Việt Nam"""
    return f"{name}({x};{y};{z})"


# ==============================================================================
# HÀM TÍNH TOÁN HÌNH HỌC 3D
# ==============================================================================

def calculate_point_B(A: Tuple[int, int, int], vec_AB: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Tính tọa độ điểm B từ A và vector AB"""
    return (A[0] + vec_AB[0], A[1] + vec_AB[1], A[2] + vec_AB[2])


def calculate_vector_length(vec: Tuple[int, int, int]) -> float:
    """Tính độ dài vector"""
    return math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)


def calculate_point_M(A: Tuple[int, int, int], vec_AB: Tuple[int, int, int], AM_dist: int) -> Tuple[float, float, float]:
    """
    Tính tọa độ điểm M trên đường thẳng AB với AM = AM_dist
    M = A + t * vec_AB, với t = AM_dist / |vec_AB|
    """
    AB_length = calculate_vector_length(vec_AB)
    t = AM_dist / AB_length
    return (
        A[0] + t * vec_AB[0],
        A[1] + t * vec_AB[1],
        A[2] + t * vec_AB[2]
    )


def calculate_vector_CM(C: Tuple[int, int, int], M: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Tính vector CM"""
    return (M[0] - C[0], M[1] - C[1], M[2] - C[2])


def calculate_point_D(C: Tuple[int, int, int], vec_CM: Tuple[float, float, float], D_altitude: int) -> Tuple[float, float, float]:
    """
    Tính tọa độ điểm D trên đường thẳng CM với z_D = D_altitude
    D = C + t' * vec_CM, với t' = (D_altitude - C_z) / vec_CM_z
    """
    if vec_CM[2] == 0:
        raise ValueError("Vector CM có thành phần z = 0, không thể tìm D")
    
    t_prime = (D_altitude - C[2]) / vec_CM[2]
    return (
        C[0] + t_prime * vec_CM[0],
        C[1] + t_prime * vec_CM[1],
        D_altitude
    )


def calculate_distance_CD(C: Tuple[int, int, int], D: Tuple[float, float, float]) -> float:
    """Tính khoảng cách CD"""
    return math.sqrt(
        (D[0] - C[0])**2 +
        (D[1] - C[1])**2 +
        (D[2] - C[2])**2
    )


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

TIKZ_DIAGRAM = r"""
\begin{tikzpicture}[scale=0.54, line join=round, line cap=round]
  % Cây bên trái (A) - từ mặt đất lên
  \draw[thick, brown] (-4.2,0) -- (-4.2,1.9);

  % Cây giữa trái (B) - cao 2.4, kết thúc ở tâm B
  \draw[thick, brown] (-1.8,1.7) -- (-1.8,4.1);
  
  % Cây giữa phải (D) - cao 2.4, kết thúc ở tâm D
  \draw[thick, brown] (1.8,1.7) -- (1.8,4.1);
  
  % Cây bên phải (C) - từ mặt đất lên
  \draw[thick, brown] (4.2,0) -- (4.2,1.9);
  
  % Vòng tròn A
  \draw[very thick, red!70!purple] (-4.2,1.9) circle (1.2);
  \fill[red!20, opacity=0.5] (-4.2,1.9) circle (1.2);
  \fill[black] (-4.2,1.9) circle (0.08);
  \node[above left=0.05cm] at (-4.2,1.9) {$A$};
  
  % Vòng tròn B
  \draw[very thick, red!70!purple] (-1.8,4.1) circle (1.2);
  \fill[red!20, opacity=0.5] (-1.8,4.1) circle (1.2);
  \fill[black] (-1.8,4.1) circle (0.08);
  \node[above left=0.05cm] at (-1.8,4.1) {$B$};
  
  % Vòng tròn D
  \draw[very thick, red!70!purple] (1.8,4.1) circle (1.2);
  \fill[red!20, opacity=0.5] (1.8,4.1) circle (1.2);
  \fill[black] (1.8,4.1) circle (0.08);
  \node[above right=0.05cm] at (1.8,4.1) {$D$};

  % Vòng tròn C
  \draw[very thick, red!70!purple] (4.2,1.9) circle (1.2);
  \fill[red!20, opacity=0.5] (4.2,1.9) circle (1.2);
  \fill[black] (4.2,1.9) circle (0.08);
  \node[above right=0.05cm] at (4.2,1.9) {$C$};
  
  % Đường thẳng đi qua A và B (kéo dài)
  \draw[very thick, red!70!purple] (-5.5, 0.76) -- (-4.2, 1.9) -- (-1.8, 4.1) -- (0, 5.92);
  
  % Đường thẳng đi qua C và D (kéo dài)
   \draw[very thick, red!70!purple] (5.5, 0.76) -- (4.2, 1.9) -- (1.8, 4.1) -- (0, 5.92);
   
\end{tikzpicture}
"""

TEMPLATE_QUESTION = Template(r"""Trong một đợt diễn tập quốc phòng, hai người ở hai vị trí khác nhau cùng ngắm bắn một mục tiêu cố định trên không. Người ta gắn một hệ trục tọa độ \(Oxyz\) (đơn vị trên mỗi trục tính theo mét), mặt phẳng \((Oxy)\) trùng mặt đất. Người thứ nhất bắn một viên đạn đi qua hai điểm \(${point_A}\) và \(${point_B}\). Người thứ hai bắn một viên đạn đi qua hai điểm \(${point_C}\) và \(D\) (điểm \(D\) ở độ cao \(${D_altitude}\text{m}\) so với mặt đất). Biết rằng sau một thời gian rời khỏi nòng súng, hai viên đạn va chạm nhau tại một vị trí cách \(A\) một khoảng bằng \(${AM_dist}\text{m}\) (tham khảo hình vẽ). Hỏi \(D\) cách \(C\) một khoảng bao nhiêu mét? \textit{(Kết quả làm tròn đến hàng phần chục)}

\begin{center}
${tikz_diagram}
\end{center}
""")


TEMPLATE_SOLUTION = Template(r"""
Lời giải:

Gọi \(M = AB \cap CD\) (là điểm hai viên đạn va chạm nhau) khi đó \(AM = ${AM_dist}\text{m}\) (1)

Ta có \(\overrightarrow{AB}(${vec_AB_x};${vec_AB_y};${vec_AB_z})\) là vectơ chỉ phương của đường thẳng \(AB\)

\(\Rightarrow\) Phương trình tham số đường thẳng \(AB\) là \[\begin{cases} x = ${A_x} + ${vec_AB_x}t \\\\ y = ${A_y} + ${vec_AB_y}t \\\\ z = ${A_z} + ${vec_AB_z}t \end{cases}\] \((t \in \mathbb{R})\).

Do \(M \in AB \Rightarrow M(${A_x} + ${vec_AB_x}t; ${A_y} + ${vec_AB_y}t; ${A_z} + ${vec_AB_z}t)\). Từ (1) ta có \(\sqrt{${t_equation}} = ${AM_dist} \Leftrightarrow |t| = ${t_abs}\).

Với \(t = ${t_abs} \Rightarrow M(${M_x};${M_y};${M_z})\)

Với \(t = -${t_abs} \Rightarrow M(${M_neg_x};${M_neg_y};${M_neg_z})\)

Vì cao độ điểm \(D\) dương nên cao độ của điểm \(M\) dương \(\Rightarrow M(${M_x};${M_y};${M_z})\)

Vậy vectơ chỉ phương của đường thẳng \(CD\) là \(\overrightarrow{CM} = (${vec_CM_x};${vec_CM_y};${vec_CM_z})\)

\(\Rightarrow\) Phương trình tham số đường thẳng \(CD\) là \[\begin{cases} x = ${C_x} + ${vec_CM_x}t' \\\\ y = ${C_y} + ${vec_CM_y}t' \\\\ z = ${C_z} + ${vec_CM_z}t' \end{cases}\] \((t' \in \mathbb{R})\).

Mà điểm \(D\) cách mặt đất \(${D_altitude}\text{m}\) nên điểm \(D\) có cao độ bằng \(${D_altitude} \Rightarrow ${C_z} + ${vec_CM_z}t' = ${D_altitude} \Leftrightarrow t' = ${t_prime} \Rightarrow D(${D_x};${D_y};${D_altitude})\)

Khi đó độ dài \(CD = \sqrt{(${C_x} - ${D_x})^2 + (${C_y} - ${D_y})^2 + (${C_z} - ${D_altitude})^2} \approx ${CD_result}\text{m}\).

Đáp án: ${CD_result} | ${CD_result_dot}
""")


# ==============================================================================
# LỚP SINH ĐỀ
# ==============================================================================

class BulletTrajectory3DQuestion:
    """Bài toán đường đạn trong không gian 3D"""
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.calculated_values: Dict[str, Any] = {}
        self.config = config or GeneratorConfig()
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên"""
        # Điểm A
        A_x = random.choice(A_X_VALUES)
        A_y = random.choice(A_Y_VALUES)
        A_z = random.choice(A_Z_VALUES)
        
        # Vector AB
        vec_AB_x = random.choice(VEC_AB_X_VALUES)
        vec_AB_y = random.choice(VEC_AB_Y_VALUES)
        vec_AB_z = random.choice(VEC_AB_Z_VALUES)
        
        # Điểm C
        C_x = random.choice(C_X_VALUES)
        C_y = random.choice(C_Y_VALUES)
        C_z = random.choice(C_Z_VALUES)
        
        # Khoảng cách AM và cao độ D
        AM_dist = random.choice(AM_DIST_VALUES)
        D_altitude = random.choice(D_ALTITUDE_VALUES)
        
        return {
            "A": (A_x, A_y, A_z),
            "vec_AB": (vec_AB_x, vec_AB_y, vec_AB_z),
            "C": (C_x, C_y, C_z),
            "AM_dist": AM_dist,
            "D_altitude": D_altitude,
        }
    
    def calculate_values(self) -> Dict[str, Any]:
        """Tính toán các giá trị"""
        params = self.parameters
        
        A = params["A"]
        vec_AB = params["vec_AB"]
        C = params["C"]
        AM_dist = params["AM_dist"]
        D_altitude = params["D_altitude"]
        
        # Tính B
        B = calculate_point_B(A, vec_AB)
        
        # Tính |AB|
        AB_length = calculate_vector_length(vec_AB)
        
        # Tính t = AM_dist / |AB|
        t_abs = AM_dist / AB_length
        
        # Tính M (với t dương)
        M = calculate_point_M(A, vec_AB, AM_dist)
        
        # Tính M với t âm (để so sánh)
        M_neg = (
            A[0] - t_abs * vec_AB[0],
            A[1] - t_abs * vec_AB[1],
            A[2] - t_abs * vec_AB[2]
        )
        
        # Tính vector CM
        vec_CM = calculate_vector_CM(C, M)
        
        # Tính D
        D = calculate_point_D(C, vec_CM, D_altitude)
        
        # Tính CD
        CD = calculate_distance_CD(C, D)
        CD_rounded = round(CD, 1)
        
        # t' = (D_altitude - C_z) / vec_CM_z
        t_prime = (D_altitude - C[2]) / vec_CM[2]
        
        return {
            "B": B,
            "AB_length": AB_length,
            "t_abs": t_abs,
            "M": M,
            "M_neg": M_neg,
            "vec_CM": vec_CM,
            "D": D,
            "CD": CD,
            "CD_rounded": CD_rounded,
            "t_prime": t_prime,
        }
    
    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        params = self.parameters
        A = params["A"]
        C = params["C"]
        calc = self.calculated_values
        B = calc["B"]
        
        return TEMPLATE_QUESTION.substitute(
            point_A=format_point_3d("A", A[0], A[1], A[2]),
            point_B=format_point_3d("B", B[0], B[1], B[2]),
            point_C=format_point_3d("C", C[0], C[1], C[2]),
            D_altitude=params["D_altitude"],
            AM_dist=params["AM_dist"],
            tikz_diagram=TIKZ_DIAGRAM,
        )
    
    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết"""
        params = self.parameters
        calc = self.calculated_values
        
        A = params["A"]
        C = params["C"]
        vec_AB = params["vec_AB"]
        M = calc["M"]
        M_neg = calc["M_neg"]
        vec_CM = calc["vec_CM"]
        D = calc["D"]
        
        # Tính phương trình t cho AM
        # AM² = (vec_AB_x * t)² + (vec_AB_y * t)² + (vec_AB_z * t)²
        # = t² * (vec_AB_x² + vec_AB_y² + vec_AB_z²)
        coef_sum = vec_AB[0]**2 + vec_AB[1]**2 + vec_AB[2]**2
        t_equation = f"{coef_sum}t^2"
        
        return TEMPLATE_SOLUTION.substitute(
            AM_dist=params["AM_dist"],
            vec_AB_x=vec_AB[0],
            vec_AB_y=vec_AB[1],
            vec_AB_z=vec_AB[2],
            A_x=A[0],
            A_y=A[1],
            A_z=A[2],
            t_equation=t_equation,
            t_abs=int(calc["t_abs"]) if calc["t_abs"] == int(calc["t_abs"]) else format_decimal_vn(calc["t_abs"]),
            M_x=int(M[0]) if M[0] == int(M[0]) else format_decimal_vn(M[0]),
            M_y=int(M[1]) if M[1] == int(M[1]) else format_decimal_vn(M[1]),
            M_z=int(M[2]) if M[2] == int(M[2]) else format_decimal_vn(M[2]),
            M_neg_x=int(M_neg[0]) if M_neg[0] == int(M_neg[0]) else format_decimal_vn(M_neg[0]),
            M_neg_y=int(M_neg[1]) if M_neg[1] == int(M_neg[1]) else format_decimal_vn(M_neg[1]),
            M_neg_z=int(M_neg[2]) if M_neg[2] == int(M_neg[2]) else format_decimal_vn(M_neg[2]),
            C_x=C[0],
            C_y=C[1],
            C_z=C[2],
            vec_CM_x=int(vec_CM[0]) if vec_CM[0] == int(vec_CM[0]) else format_decimal_vn(vec_CM[0]),
            vec_CM_y=int(vec_CM[1]) if vec_CM[1] == int(vec_CM[1]) else format_decimal_vn(vec_CM[1]),
            vec_CM_z=int(vec_CM[2]) if vec_CM[2] == int(vec_CM[2]) else format_decimal_vn(vec_CM[2]),
            D_altitude=params["D_altitude"],
            t_prime=format_decimal_vn(calc["t_prime"], 2) if calc["t_prime"] != int(calc["t_prime"]) else int(calc["t_prime"]),
            D_x=int(D[0]) if D[0] == int(D[0]) else format_decimal_vn(D[0]),
            D_y=int(D[1]) if D[1] == int(D[1]) else format_decimal_vn(D[1]),
            CD_result=format_decimal_vn(calc["CD_rounded"]),
            CD_result_dot=format_decimal_dot(calc["CD_rounded"]),
        )
    
    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        """Sinh một câu hỏi hoàn chỉnh"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.calculated_values = self.calculate_values()
        
        question_text = self.generate_question_text().strip()
        solution = self.generate_solution().strip()
        
        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += solution + "\n"
        
        # Đáp án
        answer_vn = format_decimal_vn(self.calculated_values["CD_rounded"])
        answer_dot = format_decimal_dot(self.calculated_values["CD_rounded"])
        answer = f"{answer_vn} | {answer_dot}"
        
        return question_content, answer
    
    @staticmethod
    def create_latex_document(
        questions_data: List[Tuple[str, str]],
        title: str = "Bài tập Đường Đạn Trong Không Gian 3D",
    ) -> str:
        """Tạo document LaTeX hoàn chỉnh"""
        questions_content = "\n\n\\newpage\n\n".join(
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
\usetikzlibrary{{calc}}

\title{{{title}}}
\author{{Generator}}
\date{{\today}}

\begin{{document}}
\maketitle

{questions_content}

\end{{document}}
"""
        return latex_document


# ==============================================================================
# HÀM MAIN
# ==============================================================================

def main():
    """
    Hàm main để chạy generator
    Usage: python bullet_trajectory_3d_questions.py <num_questions> [seed]
    """
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else None
        
        if seed is None:
            seed = os.environ.get("OPT_SEED")
            if seed:
                seed = int(seed)
        
        if seed is not None:
            random.seed(seed)
            logging.info(f"Sử dụng seed: {seed}")
        
        logging.info(f"Đang sinh {num_questions} câu hỏi đường đạn 3D...")
        
        questions_data: List[Tuple[str, str]] = []
        
        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            question = BulletTrajectory3DQuestion(config)
            question_content, answer = question.generate_question_only(i + 1)
            questions_data.append((question_content, answer))
            logging.info(f"  Câu {i + 1}: CD = {answer}m")
        
        latex_content = BulletTrajectory3DQuestion.create_latex_document(
            questions_data,
            title="Bài tập Đường Đạn Trong Không Gian 3D"
        )
        
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "bullet_trajectory_3d_questions.tex")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")
        
        print("\n=== ĐÁP ÁN ===")
        for i, (_, answer) in enumerate(questions_data):
            print(f"Câu {i + 1}: CD = {answer}m")
        
    except ValueError as e:
        print(f"Lỗi: Tham số không hợp lệ - {e}")
        print("Usage: python bullet_trajectory_3d_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")
        raise


if __name__ == "__main__":
    main()
