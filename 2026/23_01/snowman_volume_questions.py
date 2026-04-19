"""
Hệ thống sinh đề toán về thể tích người tuyết (tổ hợp 2 khối cầu bị cắt chỏm)
Bài toán: Tính thể tích người tuyết được ghép từ 2 hình cầu, mỗi cầu bị cắt một chỏm
và ghép lại theo đường tròn có bán kính r'.
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


# 20 giá trị cho bán kính thân (R) - số nguyên từ 22 đến 60
R_BODY_VALUES: List[int] = [22, 24, 26, 28, 30, 32, 34, 36, 38, 40,
                            42, 44, 46, 48, 50, 52, 54, 56, 58, 60]

# 20 giá trị cho r² (bán kính đầu r = √n) - chọn n sao cho tính toán hợp lý
R_HEAD_SQUARED_VALUES: List[int] = [100, 121, 125, 136, 144, 149, 169, 196,
                                     200, 225, 256, 289, 324, 361, 400, 441,
                                     484, 529, 576, 625]

# 20 giá trị cho bán kính đường tròn ghép (r') - số nguyên từ 6 đến 25
R_PRIME_VALUES: List[int] = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
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


def format_sqrt_latex(n: int) -> str:
    """Format √n thành LaTeX, đơn giản hóa nếu có thể"""
    simplified = sp.sqrt(n)
    return sp.latex(simplified)


# ==============================================================================
# HÀM TÍNH TOÁN HÌNH HỌC
# ==============================================================================

def sphere_volume(R: sp.Expr) -> sp.Expr:
    """
    Thể tích hình cầu: V = (4/3)πR³
    """
    return sp.Rational(4, 3) * sp.pi * R**3


def cap_height(R: sp.Expr, r_prime: sp.Expr) -> sp.Expr:
    """
    Tính chiều cao chỏm cầu bị cắt.
    Với hình cầu bán kính R, cắt theo đường tròn bán kính r':
    - Khoảng cách từ tâm đến mặt cắt: d = √(R² - r'²)
    - Chiều cao chỏm cầu: h = R - d = R - √(R² - r'²)
    """
    return R - sp.sqrt(R**2 - r_prime**2)


def spherical_cap_volume(R: sp.Expr, h: sp.Expr) -> sp.Expr:
    """
    Thể tích chỏm cầu: V = π * h² * (R - h/3)
    Trong đó:
    - R: bán kính hình cầu
    - h: chiều cao chỏm cầu
    """
    return sp.pi * h**2 * (R - h / 3)


def snowman_volume(R_body: sp.Expr, r_head_sq: sp.Expr, r_prime: sp.Expr) -> sp.Expr:
    """
    Tính thể tích người tuyết = V_thân + V_đầu - V_chỏm_thân - V_chỏm_đầu
    
    Params:
    - R_body: bán kính thân (số nguyên)
    - r_head_sq: r² của đầu (r_head = √r_head_sq)
    - r_prime: bán kính đường tròn ghép
    """
    r_head = sp.sqrt(r_head_sq)
    
    # Thể tích 2 hình cầu nguyên
    V_body = sphere_volume(R_body)
    V_head = sphere_volume(r_head)
    
    # Chiều cao các chỏm cầu bị cắt
    # Với thân: OH = √(R² - r'²), h_thân = R - OH
    h_body = cap_height(R_body, r_prime)
    
    # Với đầu: O'H' = √(r² - r'²), h_đầu = r - O'H'  
    h_head = cap_height(r_head, r_prime)
    
    # Thể tích các chỏm cầu
    V_cap_body = spherical_cap_volume(R_body, h_body)
    V_cap_head = spherical_cap_volume(r_head, h_head)
    
    # Thể tích người tuyết = V_thân - chỏm_thân + V_đầu - chỏm_đầu
    V_total = V_body - V_cap_body + V_head - V_cap_head
    
    return sp.nsimplify(sp.simplify(V_total))


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

TEMPLATE_QUESTION_SNOWMAN = Template(r"""
Bạn An muốn đúc một mô hình người tuyết. Để tạo hình đầu và thân của người tuyết, 
khuôn đúc được ghép lại từ hai hình cầu có bán kính lần lượt là \(R = ${R_body} \mathrm{~cm}\) 
và \(r = ${r_head_latex} \mathrm{~cm}\). Hai hình cầu này được cắt bỏ một phần chỏm cầu 
và được ghép lại với nhau theo một đường tròn có bán kính \(r' = ${r_prime} \mathrm{~cm}\). 
Thể tích người tuyết sau khi đúc (kết quả làm tròn đến hàng đơn vị và tính theo đơn vị là \(\mathrm{dm}^3\)) 
bằng bao nhiêu?
""")


TEMPLATE_SOLUTION_SNOWMAN = Template(r"""
Lời giải:

\begin{center}
${diagram}
\end{center}

Ta có hai hình cầu:
\begin{itemize}
    \item Hình cầu thân có bán kính \(R = ${R_body}\) cm
    \item Hình cầu đầu có bán kính \(r = ${r_head_latex}\) cm
    \item Bán kính đường tròn ghép \(r' = ${r_prime}\) cm
\end{itemize}

Bước 1: Tính các khoảng cách từ tâm đến mặt cắt

Với hình cầu thân (tâm O, bán kính R):
\[
OH = \sqrt{R^2 - r'^2} = \sqrt{${R_body}^2 - ${r_prime}^2} = \sqrt{${R_sq_minus_rprime_sq}} = ${OH_value}
\]

Với hình cầu đầu (tâm O', bán kính r):
\[
O'H' = \sqrt{r^2 - r'^2} = \sqrt{${r_head_sq} - ${r_prime}^2} = \sqrt{${r_sq_minus_rprime_sq}} = ${OpHp_value}
\]

Bước 2: Tính chiều cao các chỏm cầu bị cắt

Chiều cao chỏm cầu thân (MN):
\[
MN = R - OH = ${R_body} - ${OH_value} = ${h_body}
\]

Chiều cao chỏm cầu đầu (M'N'):
\[
M'N' = r - O'H' = ${r_head_latex} - ${OpHp_value} = ${h_head}
\]

Bước 3: Tính thể tích hình cầu đầu
\[
V_{\text{đầu}} = \frac{4}{3}\pi r^3 = \frac{4}{3}\pi \left(${r_head_latex}\right)^3 = ${V_head_expr}
\]

Bước 4: Tính thể tích chỏm cầu đầu bị cắt

Công thức chỏm cầu: \(V_{\text{chỏm}} = \pi h^2 \left(R - \dfrac{h}{3}\right)\)
\[
V_{\text{chỏm đầu}} = \pi \cdot \left(${h_head}\right)^2 \cdot \left(${r_head_latex} - \frac{${h_head}}{3}\right) = ${V_cap_head_expr}
\]

Bước 5: Tính thể tích hình cầu thân
\[
V_{\text{thân}} = \frac{4}{3}\pi R^3 = \frac{4}{3}\pi \cdot ${R_body}^3 = ${V_body_expr}
\]

Bước 6: Tính thể tích chỏm cầu thân bị cắt
\[
V_{\text{chỏm thân}} = \pi \cdot \left(${h_body}\right)^2 \cdot \left(${R_body} - \frac{${h_body}}{3}\right) = ${V_cap_body_expr}
\]

Bước 7: Tính thể tích người tuyết
\[
V_{\text{người tuyết}} = V_{\text{đầu}} - V_{\text{chỏm đầu}} + V_{\text{thân}} - V_{\text{chỏm thân}}
\]
\[
V_{\text{người tuyết}} = ${V_total_expr} \approx ${V_numeric} \text{ cm}^3
\]

Đổi sang \(\mathrm{dm}^3\): 
\[
V = \frac{${V_numeric}}{1000} \approx ${V_dm3} \text{ dm}^3
\]

Đáp án: ${answer}
""")


# ==============================================================================
# LỚP CƠ SỞ VÀ CÀI ĐẶT
# ==============================================================================

class BaseSnowmanQuestion(ABC):
    """Lớp cơ sở cho các bài toán người tuyết"""
    
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
        """Tạo hình vẽ TikZ cho người tuyết"""
        params = self.parameters
        if not params:
            return ""
        
        R = params["R_body"]
        r_head_sq = params["r_head_sq"]
        r_prime = params["r_prime"]
        
        # Tính các giá trị hình học
        r_head = float(sp.sqrt(r_head_sq).evalf())
        OH = float(sp.sqrt(R**2 - r_prime**2).evalf())
        OpHp = float(sp.sqrt(r_head_sq - r_prime**2).evalf())
        
        # Format r_head cho hiển thị trong TikZ
        r_head_sympy = sp.sqrt(r_head_sq)
        if r_head_sympy.is_Integer:
            r_head_display = str(r_head_sympy)
        else:
            r_head_display = rf"\sqrt{{{r_head_sq}}}"
        
        # Scale để vẽ đẹp (normalize về khoảng hợp lý)
        scale = 3.0 / R  # Scale sao cho R ~ 3cm trên hình
        
        R_scaled = R * scale
        r_scaled = r_head * scale
        r_prime_scaled = r_prime * scale
        OH_scaled = OH * scale
        OpHp_scaled = OpHp * scale
        
        # Vị trí tâm O (thân - ở dưới) và O' (đầu - ở trên)
        # O ở gốc, H là điểm giao trên trục y
        O_y = 0
        H_y = OH_scaled  # Điểm giao nằm trên trục y cách O một đoạn OH
        Op_y = H_y + OpHp_scaled  # Tâm đầu ở phía trên H một đoạn O'H'
        
        tikz_code = rf"""
\begin{{tikzpicture}}[scale=1, >=stealth]
    % Hình cầu thân (dưới) - tâm O
    \draw[blue, thick] (0, {O_y}) circle ({R_scaled});
    \fill[blue] (0, {O_y}) circle (1.5pt) node[below] {{$O$}};
    
    % Hình cầu đầu (trên) - tâm O'
    \draw[blue, thick] (0, {Op_y}) circle ({r_scaled});
    \fill[blue] (0, {Op_y}) circle (1.5pt) node[left] {{$O'$}};
    
    % Điểm H (giao điểm trên trục nối tâm)
    \fill[red] (0, {H_y}) circle (1.5pt) node[right] {{$H$}};
    
    % Điểm A và B trên đường tròn ghép (bán kính r')
    \fill[red] (-{r_prime_scaled}, {H_y}) circle (1.5pt) node[left] {{$A$}};
    \fill[red] ({r_prime_scaled}, {H_y}) circle (1.5pt) node[right] {{$B$}};
    
    % Đường nối các điểm quan trọng
    \draw[red, dashed] (0, {O_y}) -- (0, {H_y});  % OH (trục)
    \draw[red, dashed] (0, {H_y}) -- (0, {Op_y}); % HO' (trục)
    \draw[red, dashed] (-{r_prime_scaled}, {H_y}) -- ({r_prime_scaled}, {H_y}); % AB (đường kính ghép)
    \draw[red, dashed] (0, {O_y}) -- ({r_prime_scaled}, {H_y});  % OB
    \draw[red, dashed] (0, {Op_y}) -- ({r_prime_scaled}, {H_y}); % O'B
    
    % Điểm M' (đỉnh đầu)
    \fill[blue] (0, {Op_y + r_scaled}) circle (1.5pt) node[above] {{$M'$}};
    
    % Mũi tên chú thích OH
    \draw[<->, thick] ({R_scaled + 0.5}, {O_y}) -- ({R_scaled + 0.5}, {H_y}) 
        node[midway, right] {{$OH$}};
    
    % Mũi tên chú thích O'H'
    \draw[<->, thick] ({r_prime_scaled + 0.8}, {H_y}) -- ({r_prime_scaled + 0.8}, {Op_y}) 
        node[midway, right] {{$O'H'$}};
    
    % Chú thích bán kính đầu (trên đỉnh)
    \node[above left] at (0, {Op_y + r_scaled}) {{$r = {r_head_display}$ cm}};
    
    % Chú thích r' = ... cm (bên phải điểm B)
    \node[right] at ({r_prime_scaled + 0.3}, {H_y - 0.3}) {{$r' = {r_prime}$ cm}};
    
\end{{tikzpicture}}
"""
        return tikz_code
    
    @staticmethod
    def create_latex_document_with_format(
        questions_data: List[Tuple[str, str]],
        title: str = "Bài tập Thể tích Người tuyết",
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
\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
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


class SnowmanVolumeQuestion(BaseSnowmanQuestion):
    """Bài toán tính thể tích người tuyết"""
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên với constraint hợp lệ"""
        max_attempts = 100
        
        for _ in range(max_attempts):
            R_body = random.choice(R_BODY_VALUES)
            r_head_sq = random.choice(R_HEAD_SQUARED_VALUES)
            r_prime = random.choice(R_PRIME_VALUES)
            
            r_head = sp.sqrt(r_head_sq)
            r_head_float = float(r_head.evalf())
            
            # Constraint: r' < r và r' < R và r'² < r² và r'² < R²
            if r_prime < r_head_float and r_prime < R_body:
                if r_prime**2 < r_head_sq and r_prime**2 < R_body**2:
                    return {
                        "R_body": R_body,
                        "r_head_sq": r_head_sq,
                        "r_prime": r_prime,
                    }
        
        # Fallback với giá trị mặc định từ đề mẫu
        return {
            "R_body": 26,
            "r_head_sq": 149,
            "r_prime": 10,
        }
    
    def calculate_answer(self) -> str:
        """Tính thể tích người tuyết và làm tròn sang dm³"""
        params = self.parameters
        R = sp.Integer(params["R_body"])
        r_sq = sp.Integer(params["r_head_sq"])
        r_prime = sp.Integer(params["r_prime"])
        
        # Tính thể tích bằng SymPy
        V_exact = snowman_volume(R, r_sq, r_prime)
        
        # Chuyển sang số và đổi cm³ → dm³ (chia 1000)
        V_numeric = float(V_exact.evalf())
        V_dm3 = V_numeric / 1000
        
        # Làm tròn đến hàng đơn vị
        V_rounded = round(V_dm3)
        
        return str(V_rounded)
    
    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        params = self.parameters
        R_body = params["R_body"]
        r_head_sq = params["r_head_sq"]
        r_prime = params["r_prime"]
        
        # Format r_head
        r_head_simplified = sp.sqrt(r_head_sq)
        if r_head_simplified.is_Integer:
            r_head_latex = str(r_head_simplified)
        else:
            r_head_latex = rf"\sqrt{{{r_head_sq}}}"
        
        return TEMPLATE_QUESTION_SNOWMAN.substitute(
            R_body=R_body,
            r_head_latex=r_head_latex,
            r_prime=r_prime,
        )
    
    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết"""
        params = self.parameters
        R_body = params["R_body"]
        r_head_sq = params["r_head_sq"]
        r_prime = params["r_prime"]
        
        diagram = self.generate_tikz_diagram()
        
        R = sp.Integer(R_body)
        r_sq = sp.Integer(r_head_sq)
        r_p = sp.Integer(r_prime)
        r_head = sp.sqrt(r_sq)
        
        # Format r_head cho LaTeX
        if r_head.is_Integer:
            r_head_latex = str(r_head)
        else:
            r_head_latex = rf"\sqrt{{{r_head_sq}}}"
        
        # Tính các giá trị trung gian
        R_sq_minus_rprime_sq = R**2 - r_p**2
        r_sq_minus_rprime_sq = r_sq - r_p**2
        
        OH = sp.sqrt(R_sq_minus_rprime_sq)
        OpHp = sp.sqrt(r_sq_minus_rprime_sq)
        
        # Format OH và O'H'
        OH_simplified = sp.simplify(OH)
        OpHp_simplified = sp.simplify(OpHp)
        
        if OH_simplified.is_Integer:
            OH_value = str(OH_simplified)
        else:
            OH_value = sp.latex(OH_simplified)
        
        if OpHp_simplified.is_Integer:
            OpHp_value = str(OpHp_simplified)
        else:
            OpHp_value = sp.latex(OpHp_simplified)
        
        # Chiều cao chỏm cầu
        h_body = R - OH
        h_head = r_head - OpHp
        
        h_body_simplified = sp.simplify(h_body)
        h_head_simplified = sp.simplify(h_head)
        
        # Thể tích các phần
        V_body = sphere_volume(R)
        V_head = sphere_volume(r_head)
        V_cap_body = spherical_cap_volume(R, h_body)
        V_cap_head = spherical_cap_volume(r_head, h_head)
        
        V_body_simplified = sp.nsimplify(V_body)
        V_head_simplified = sp.nsimplify(V_head)
        V_cap_body_simplified = sp.nsimplify(sp.simplify(V_cap_body))
        V_cap_head_simplified = sp.nsimplify(sp.simplify(V_cap_head))
        
        V_total = V_body - V_cap_body + V_head - V_cap_head
        V_total_simplified = sp.nsimplify(sp.simplify(V_total))
        
        V_numeric = float(V_total_simplified.evalf())
        V_dm3 = V_numeric / 1000
        V_rounded = round(V_dm3)
        
        return TEMPLATE_SOLUTION_SNOWMAN.substitute(
            diagram=diagram,
            R_body=R_body,
            r_head_latex=r_head_latex,
            r_head_sq=r_head_sq,
            r_prime=r_prime,
            R_sq_minus_rprime_sq=R_sq_minus_rprime_sq,
            r_sq_minus_rprime_sq=r_sq_minus_rprime_sq,
            OH_value=OH_value,
            OpHp_value=OpHp_value,
            h_body=sp.latex(h_body_simplified),
            h_head=sp.latex(h_head_simplified),
            V_body_expr=sp.latex(V_body_simplified),
            V_head_expr=sp.latex(V_head_simplified),
            V_cap_body_expr=sp.latex(V_cap_body_simplified),
            V_cap_head_expr=sp.latex(V_cap_head_simplified),
            V_total_expr=sp.latex(V_total_simplified),
            V_numeric=f"{V_numeric:.2f}",
            V_dm3=f"{V_dm3:.2f}",
            answer=V_rounded,
        )


# ==============================================================================
# HÀM MAIN
# ==============================================================================

def get_available_question_types():
    """Trả về danh sách các loại câu hỏi có sẵn"""
    return [
        SnowmanVolumeQuestion,
    ]


def main():
    """
    Hàm main để chạy generator
    Usage: python snowman_volume_questions.py <num_questions> [seed]
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
        
        logging.info(f"Đang sinh {num_questions} câu hỏi thể tích người tuyết...")
        
        questions_data: List[Tuple[str, str]] = []
        
        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            question = SnowmanVolumeQuestion(config)
            question_content, correct_answer = question.generate_question_only(i + 1)
            questions_data.append((question_content, correct_answer))
            logging.info(f"  Câu {i + 1}: Đáp án = {correct_answer} dm³")
        
        # Tạo tài liệu LaTeX
        latex_content = BaseSnowmanQuestion.create_latex_document_with_format(
            questions_data,
            title="Bài tập Thể tích Người tuyết"
        )
        
        # Ghi file
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "snowman_volume_questions.tex")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")
        
        # In đáp án
        print("\n=== ĐÁP ÁN ===")
        for i, (_, answer) in enumerate(questions_data):
            print(f"Câu {i + 1}: {answer} dm³")
        
    except ValueError as e:
        print(f"Lỗi: Tham số không hợp lệ - {e}")
        print("Usage: python snowman_volume_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")
        raise


if __name__ == "__main__":
    main()
