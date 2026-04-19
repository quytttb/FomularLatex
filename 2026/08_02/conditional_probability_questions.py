"""
Hệ thống sinh đề toán xác suất có điều kiện (Bayes)
Bài toán: Tính tỷ lệ loại A trong số các cặp có kết quả giống nhau
Dạng câu hỏi: Điền số (kết quả làm tròn đến hàng phần trăm)
4 ngữ cảnh: Kiểm định sản xuất, Di truyền thực vật, Truyền tin số hóa, Tâm lý học hành vi
"""

import logging
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


# 20 giá trị cho p_pos (% cặp cùng "positive")
P_POS_VALUES: List[int] = [
    25, 27, 28, 29, 30, 31, 32, 33, 34, 35,
    36, 37, 38, 39, 40, 42, 44, 45, 46, 48,
]

# 20 giá trị cho p_neg (% cặp cùng "negative")
P_NEG_VALUES: List[int] = [
    20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
    30, 31, 32, 33, 34, 35, 36, 37, 38, 40,
]


# ==============================================================================
# 4 NGỮ CẢNH
# ==============================================================================

CONTEXTS: List[Dict[str, str]] = [
    # Context 1: Kiểm định Sản xuất
    {
        "id": "manufacturing",
        "question_template": Template(
            r"""Trong một quy trình kiểm tra bo mạch điện tử, các cặp sản phẩm được đưa qua hệ thống phân loại thuộc hai dòng: dòng Máy A (luôn tạo ra các cặp sản phẩm đồng nhất về chất lượng) và dòng Máy B (có xác suất mỗi sản phẩm đạt hoặc lỗi độc lập là $$0{,}5$$). Thống kê vận hành cho thấy có $$${p_pos}\%$$ cặp sản phẩm đều đạt chuẩn, $$${p_neg}\%$$ cặp sản phẩm đều bị lỗi và $$${p_diff}\%$$ cặp sản phẩm có chất lượng khác nhau (một đạt, một lỗi). Dựa trên số liệu này, hãy tính tỷ lệ các cặp sản phẩm được sản xuất từ dòng Máy A trong tổng số các cặp sản phẩm có chất lượng đồng nhất và làm tròn kết quả đến hàng phần trăm."""
        ),
        "event_A": r"""nhận được cặp sản phẩm từ dòng Máy A""",
        "event_B": r"""nhận được cặp sản phẩm có chất lượng đồng nhất""",
        "A_label": "Máy A",
        "notA_label": "Máy B",
        "reason_BA_1": r"""Do dòng Máy A luôn tạo ra cặp sản phẩm đồng nhất""",
        "reason_BnotA": r"""Và dòng Máy B có xác suất mỗi sản phẩm đạt hoặc lỗi độc lập là $$50\%$$""",
        "pos_label": "đều đạt chuẩn",
        "neg_label": "đều bị lỗi",
    },
    # Context 2: Di truyền thực vật
    {
        "id": "genetics",
        "question_template": Template(
            r"""Một nhà nghiên cứu di truyền học khảo sát các cặp hạt giống trong một loại quả đặc biệt, trong đó các cặp hạt có thể có cùng kiểu gene (luôn cho màu hoa giống nhau) hoặc khác kiểu gene (xác suất mỗi hạt cho hoa màu đỏ hoặc trắng là độc lập và bằng $$0{,}5$$). Kết quả ghi nhận được $$${p_diff}\%$$ số cặp hạt cho ra hai màu hoa khác nhau, $$${p_pos}\%$$ số cặp cùng cho hoa đỏ và $$${p_neg}\%$$ số cặp cùng cho hoa trắng. Từ dữ liệu trên, hãy xác định tỷ lệ cặp hạt có cùng kiểu gene trong số các cặp hạt đã cho ra màu hoa giống nhau (làm tròn kết quả đến hai chữ số thập phân ở đơn vị phần trăm)."""
        ),
        "event_A": r"""nhận được cặp hạt có cùng kiểu gene""",
        "event_B": r"""nhận được cặp hạt cho ra màu hoa giống nhau""",
        "A_label": "cùng kiểu gene",
        "notA_label": "khác kiểu gene",
        "reason_BA_1": r"""Do các cặp hạt cùng kiểu gene luôn cho màu hoa giống nhau""",
        "reason_BnotA": r"""Và các cặp hạt khác kiểu gene có xác suất mỗi hạt cho hoa màu đỏ hoặc trắng độc lập là $$50\%$$""",
        "pos_label": "cùng cho hoa đỏ",
        "neg_label": "cùng cho hoa trắng",
    },
    # Context 3: Truyền tin số hóa
    {
        "id": "digital",
        "question_template": Template(
            r"""Trong hệ thống truyền tín hiệu nhị phân, các cặp bit dữ liệu được gửi đi theo hai phương thức: phương thức Đồng bộ (hai bit luôn luôn giống nhau) và phương thức Ngẫu nhiên (mỗi bit nhận giá trị $$0$$ hoặc $$1$$ với xác suất độc lập $$0{,}5$$). Quan sát thực tế tại trạm thu cho thấy tỷ lệ cặp bit $$(1;1)$$ chiếm $$${p_pos}\%$$, tỷ lệ cặp bit $$(0;0)$$ chiếm $$${p_neg}\%$$ và tỷ lệ các cặp bit khác nhau là $$${p_diff}\%$$. Hãy tính toán tỷ lệ các cặp bit được gửi theo phương thức Đồng bộ trong tổng số các cặp bit có giá trị giống nhau thu được tại trạm và làm tròn kết quả đến hàng phần trăm."""
        ),
        "event_A": r"""nhận được cặp bit gửi theo phương thức Đồng bộ""",
        "event_B": r"""nhận được cặp bit có giá trị giống nhau""",
        "A_label": "Đồng bộ",
        "notA_label": "Ngẫu nhiên",
        "reason_BA_1": r"""Do phương thức Đồng bộ luôn gửi hai bit giống nhau""",
        "reason_BnotA": r"""Và phương thức Ngẫu nhiên có xác suất mỗi bit nhận giá trị $$0$$ hoặc $$1$$ độc lập là $$50\%$$""",
        "pos_label": "cùng là (1;1)",
        "neg_label": "cùng là (0;0)",
    },
    # Context 4: Tâm lý học hành vi
    {
        "id": "psychology",
        "question_template": Template(
            r"""Một thí nghiệm xã hội khảo sát phản ứng của các cặp tình nguyện viên trước một tình huống giả định với hai lựa chọn: "Đồng ý" hoặc "Phản đối". Các cặp này hoặc là nhóm Thống nhất (luôn đưa ra lựa chọn giống hệt nhau) hoặc là nhóm Độc lập (mỗi cá nhân lựa chọn với xác suất $$0{,}5$$ cho mỗi phương án). Thống kê thực nghiệm chỉ ra rằng có $$${p_pos}\%$$ cặp cùng chọn "Đồng ý", $$${p_neg}\%$$ cặp cùng chọn "Phản đối" và $$${p_diff}\%$$ cặp có lựa chọn trái ngược nhau. Hãy tính tỷ lệ nhóm Thống nhất trong tổng các cặp có lựa chọn giống nhau và làm tròn kết quả đến hàng phần trăm."""
        ),
        "event_A": r"""nhận được cặp thuộc nhóm Thống nhất""",
        "event_B": r"""nhận được cặp có lựa chọn giống nhau""",
        "A_label": "Thống nhất",
        "notA_label": "Độc lập",
        "reason_BA_1": r"""Do nhóm Thống nhất luôn đưa ra lựa chọn giống hệt nhau""",
        "reason_BnotA": r"""Và nhóm Độc lập có xác suất mỗi cá nhân lựa chọn độc lập là $$50\%$$""",
        "pos_label": r"""cùng chọn "Đồng ý" """,
        "neg_label": r"""cùng chọn "Phản đối" """,
    },
]


# ==============================================================================
# HÀM TIỆN ÍCH
# ==============================================================================

def format_decimal_vn(val: float, decimals: int = 2) -> str:
    """Format số thập phân với dấu phẩy"""
    formatted = f"{val:.{decimals}f}".rstrip('0').rstrip('.')
    return formatted.replace(".", ",")


def format_decimal_dot(val: float, decimals: int = 2) -> str:
    """Format số thập phân với dấu chấm"""
    return f"{val:.{decimals}f}".rstrip('0').rstrip('.')


# ==============================================================================
# HÀM TÍNH TOÁN XÁC SUẤT
# ==============================================================================

def calculate_P_B(p_pos: int, p_neg: int) -> float:
    """P(B) = (p_pos + p_neg) / 100"""
    return (p_pos + p_neg) / 100


def calculate_P_A(p_pos: int, p_neg: int) -> float:
    """
    P(A) = (P(B) - P(B|notA)) / (P(B|A) - P(B|notA))
         = (P(B) - 0.5) / (1 - 0.5)
         = 2·P(B) - 1
    """
    P_B = calculate_P_B(p_pos, p_neg)
    return 2 * P_B - 1


def calculate_P_A_given_B(P_A: float, P_B: float) -> float:
    """P(A|B) = P(B|A)·P(A) / P(B) = P(A) / P(B)"""
    return P_A / P_B


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

TEMPLATE_SOLUTION = Template(r"""
Lời giải:

Xét các biến cố $$A$$ "${event_A}" và $$B$$ "${event_B}"

Do ${reason_BA_1} nên $$P(B \mid A) = 1$$

${reason_BnotA} nên lần lượt có được:

$$P\left(B \mid \overline{A}\right) = P\left(\overline{B} \mid A\right) = 1$$

Từ các thống kê trên ta suy ra biến cố $$B$$ là hợp giữa xác suất ${pos_label} và ${neg_label} nên ta có: $$P(B) = ${p_pos_decimal} + ${p_neg_decimal} = ${P_B}$$ và $$P\left(\overline{B}\right) = ${p_diff_decimal}$$.

Áp dụng công thức xác suất toàn phần, ta có:

$$P(B) = P(B \mid A).P(A) + P\left(B \mid \overline{A}\right).P\left(\overline{A}\right) = P(B \mid A).P(A) + P\left(B \mid \overline{A}\right).\left[1 - P(A)\right] = ${P_B}$$

Suy ra: $$P(A) = \dfrac{P(B) - P\left(B \mid \overline{A}\right)}{P(B \mid A) - P\left(B \mid \overline{A}\right)} = \dfrac{${P_B} - 0{,}5}{1 - 0{,}5} = ${P_A}$$.

Xác suất cần tìm là: $$P(A \mid B) = \dfrac{P(B \mid A).P(A)}{P(B)} = \dfrac{${P_A} \cdot 1}{${P_B}} = ${P_A_given_B_exact}$$.

Đáp án: ${answer} | ${answer_dot}
""")


# ==============================================================================
# LỚP SINH ĐỀ
# ==============================================================================

class ConditionalProbabilityQuestion:
    """Bài toán xác suất có điều kiện (Bayes)"""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.calculated_values: Dict[str, Any] = {}
        self.config = config or GeneratorConfig()

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên"""
        # Random context
        context = random.choice(CONTEXTS)

        # Random p_pos và p_neg, đảm bảo p_same > 50
        while True:
            p_pos = random.choice(P_POS_VALUES)
            p_neg = random.choice(P_NEG_VALUES)
            p_same = p_pos + p_neg
            p_diff = 100 - p_same
            if p_same > 50 and p_diff > 0:
                break

        return {
            "context": context,
            "p_pos": p_pos,
            "p_neg": p_neg,
            "p_diff": p_diff,
            "p_same": p_same,
        }

    def calculate_values(self) -> Dict[str, Any]:
        """Tính toán các giá trị"""
        params = self.parameters
        p_pos = params["p_pos"]
        p_neg = params["p_neg"]

        P_B = calculate_P_B(p_pos, p_neg)
        P_A = calculate_P_A(p_pos, p_neg)
        P_A_given_B = calculate_P_A_given_B(P_A, P_B)
        P_A_given_B_rounded = round(P_A_given_B, 2)

        return {
            "P_B": P_B,
            "P_A": P_A,
            "P_A_given_B": P_A_given_B,
            "P_A_given_B_rounded": P_A_given_B_rounded,
        }

    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        params = self.parameters
        context = params["context"]

        return context["question_template"].substitute(
            p_pos=params["p_pos"],
            p_neg=params["p_neg"],
            p_diff=params["p_diff"],
        )

    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết"""
        params = self.parameters
        calc = self.calculated_values
        context = params["context"]

        # Tính P(A|B) dạng phân số chính xác nếu có thể
        P_A_given_B_exact = format_decimal_vn(calc["P_A_given_B"], 4)

        return TEMPLATE_SOLUTION.substitute(
            event_A=context["event_A"],
            event_B=context["event_B"],
            reason_BA_1=context["reason_BA_1"],
            reason_BnotA=context["reason_BnotA"],
            pos_label=context["pos_label"],
            neg_label=context["neg_label"],
            p_pos_decimal=format_decimal_vn(params["p_pos"] / 100, 2),
            p_neg_decimal=format_decimal_vn(params["p_neg"] / 100, 2),
            p_diff_decimal=format_decimal_vn(params["p_diff"] / 100, 2),
            P_B=format_decimal_vn(calc["P_B"], 2),
            P_A=format_decimal_vn(calc["P_A"], 2),
            P_A_given_B_exact=P_A_given_B_exact,
            answer=format_decimal_vn(calc["P_A_given_B_rounded"], 2),
            answer_dot=format_decimal_dot(calc["P_A_given_B_rounded"], 2),
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

        answer_vn = format_decimal_vn(self.calculated_values["P_A_given_B_rounded"], 2)
        answer_dot = format_decimal_dot(self.calculated_values["P_A_given_B_rounded"], 2)
        answer = f"{answer_vn} | {answer_dot}"
        context_id = self.parameters["context"]["id"]

        logging.info(f"  Context: {context_id}")

        return question_content, answer

    @staticmethod
    def create_latex_document(
        questions_data: List[Tuple[str, str]],
        title: str = "Bài tập Xác Suất Có Điều Kiện (Bayes)",
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
    Usage: python conditional_probability_questions.py <num_questions> [seed]
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

        logging.info(f"Đang sinh {num_questions} câu hỏi xác suất Bayes...")

        questions_data: List[Tuple[str, str]] = []

        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            question = ConditionalProbabilityQuestion(config)
            question_content, answer = question.generate_question_only(i + 1)
            questions_data.append((question_content, answer))
            logging.info(f"  Câu {i + 1}: P(A|B) = {answer}")

        latex_content = ConditionalProbabilityQuestion.create_latex_document(
            questions_data,
            title="Bài tập Xác Suất Có Điều Kiện (Bayes)"
        )

        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "conditional_probability_questions.tex")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)

        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")

        print("\n=== ĐÁP ÁN ===")
        for i, (_, answer) in enumerate(questions_data):
            print(f"Câu {i + 1}: P(A|B) = {answer}")

    except ValueError as e:
        print(f"Lỗi: Tham số không hợp lệ - {e}")
        print("Usage: python conditional_probability_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")
        raise


if __name__ == "__main__":
    main()
