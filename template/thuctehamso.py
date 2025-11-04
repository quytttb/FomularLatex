import sys
import math
import random
from typing import List, Tuple, Dict
import argparse

"""thuctehamso.py

Sinh bộ câu hỏi Đúng/Sai (1 đến 4 mệnh đề đúng ngẫu nhiên – hiện giới hạn lại 1 đến 3 để tránh tất cả đều đúng) dựa trên hàm phân thức một biến thời gian.

TỔNG QUÁT HÓA CÔNG THỨC BAN ĐẦU
--------------------------------
Đề gốc bạn đưa: f(t) = (25 t + 10) / (t + 5).
Ta tổng quát thành: f(t) = (A t + B) / (t + C) với A,B,C > 0.

Lý do tổng quát:
1. Cho phép random để tạo nhiều phiên bản đề khác nhau.
2. Tránh việc thí sinh học thuộc kết quả cụ thể 25,10,5.

ĐẠO HÀM CHUẨN HÓA
------------------
f(t) = (A t + B)/(t + C) = (At + B)(t + C)^{-1}.
f'(t) = [A(t + C) - (At + B)*1] / (t + C)^2 = (AC - B)/(t + C)^2.

Điều kiện f tăng (đơn điệu tăng trên [0, +∞)) ⇔ f'(t) > 0 ⇔ AC - B > 0.
Trong generate_parameters ta cưỡng bức AC - B > 0 bằng cách random B < A*C.

GIỚI HẠN TRÊN
--------------
lim_{t→∞} f(t) = A (vì chia cả tử và mẫu cho t). Đây chính là "ngưỡng" tối đa không vượt quá
trong mệnh đề (câu c). Vì vậy với mỗi A random, ta tự động có giới hạn tương ứng.

GIÁ TRỊ TẠI NĂM CỤ THỂ
-----------------------
Ta quy ước BASE_YEAR = 2000. Khi đề hỏi năm 2000, 2015, 2025 sẽ tương ứng t = 0, 15, 25.
Các giá trị f(0), f(15), f(25) được tính động – không hardcode.

TỐC ĐỘ THAY ĐỔI NĂM 2025
------------------------
Là f'(25) = (AC - B)/(25 + C)^2, sau đó làm tròn ROUND_DIGITS_SPEED (mặc định 3).

CẤU TRÚC MỆNH ĐỀ
----------------
a) Giá trị tại hai năm (Years 2000 & 2015)
b) Công thức đạo hàm tổng quát
c) Tính tăng + chặn trên (không vượt quá A)
d) Tốc độ tại năm 2025

Các mệnh đề đúng chọn ngẫu nhiên (1 đến 3) – các mệnh đề sai được gây nhiễu bằng:
- Sửa giá trị tại năm thứ hai.
- Sửa hệ số tử đạo hàm (AC - B) bằng một perturbation nhỏ.
- Khẳng định vượt qua giới hạn hoặc tăng sai.
- Thay đổi nhẹ giá trị tốc độ đã làm tròn.

GHI DẤU ĐÁP ÁN
--------------
Mỗi mệnh đề đúng được đặt dấu '*' trước chữ cái a,b,c,d theo yêu cầu (có thể có nhiều hơn 1 dấu *).

Muốn cố định lại như đề gốc chỉ cần đặt A=25,B=10,C=5 và bỏ generate_parameters.
"""

# =============================
# BÀI TOÁN HÀM TĂNG DẠNG f(t) = (At + B)/(t + C)
# (1) Đồng bộ docstring: có thể nhiều mệnh đề đúng
# (2) Giới hạn số mệnh đề đúng bằng MIN_CORRECT / MAX_CORRECT
# (4) Chuẩn hóa định dạng số .3f thay vì .3g
# (5) Bảo đảm nhiễu không trùng sau làm tròn
# (6)(7) Lời giải giải thích rõ vì sao đạo hàm >0 & làm sạch dấu toán
# (8)(12) Tách build_solution và tránh tính lặp lại context
# (9) Ràng buộc đạo hàm tối thiểu (A*C - B >= DERIV_MARGIN)
# =============================

BASE_YEAR = 2000
YEAR_1 = 2000   # => t=0
YEAR_2 = 2015   # => t=15
YEAR_3 = 2025   # => t=25

ROUND_DIGITS_SPEED = 3  # làm tròn tốc độ năm YEAR_3

# (2) Giới hạn số mệnh đề đúng
MIN_CORRECT = 1
MAX_CORRECT = 3  # tránh cả 4 đều đúng để tăng độ phân biệt

# (9) Biên tối thiểu cho đạo hàm (AC - B) để tốc độ không quá nhỏ
DERIV_MARGIN = 5

TOPICS = [
    (1, "Dân số thị trấn", "nghìn người"),
    (2, "Năng suất cây trồng", "tạ/ha"),
    (3, "Sản lượng thủy sản", "nghìn tấn"),
    (4, "Số xe máy lưu hành", "nghìn chiếc"),
    (5, "Doanh thu công ty", "tỷ đồng"),
    (6, "Lượng khách du lịch", "nghìn người"),
    (7, "Sản lượng điện năng", "triệu kWh"),
    (8, "Sản lượng gạo", "nghìn tấn"),
    (9, "Dân số thành phố", "nghìn người"),
    (10, "Lượng hàng hóa vận chuyển", "nghìn tấn"),
    (11, "Lợi nhuận công ty", "tỷ đồng"),
]

# Ký hiệu hàm hiển thị ngẫu nhiên thay vì luôn dùng f
FUNC_SYMBOLS = list("MNPQREKF")  # có thể mở rộng


def f(t: float, A: int, B: int, C: int) -> float:
    return (A * t + B) / (t + C)

def fprime(t: float, A: int, B: int, C: int) -> float:
    return (A * C - B) / (t + C) ** 2

def generate_parameters() -> Dict[str, int]:
    """Random hóa (A,B,C) thỏa AC - B > 0 để f'(t) > 0 mọi t >= 0.

    Chiến lược:
    - Chọn A trong [10,40] để giới hạn không quá nhỏ hoặc quá lớn.
    - Chọn C trong [3,8] để mẫu không quá nhỏ (tránh độ dốc cực lớn) và vẫn đa dạng.
    - Chọn B < A*C nhằm đảm bảo đạo hàm dương.
    - Lặp lại nếu điều kiện phụ (f(0) không quá lớn) bị vi phạm.
    """
    while True:
        A = random.randint(10, 40)
        C = random.randint(3, 8)
        # B <= A*C - DERIV_MARGIN để đảm bảo AC-B >= DERIV_MARGIN
        max_B = A * C - DERIV_MARGIN
        if max_B <= 2:
            continue
        B = random.randint(1, max_B)
        if f(0, A, B, C) < 200:  # điều kiện lỏng (giữ nguyên)
            return {"A": A, "B": B, "C": C}

def compute_context(params: Dict[str,int]):
    # Tính toàn bộ số liệu cho mệnh đề – tránh tính lặp lại.
    A,B,C = params['A'], params['B'], params['C']
    t1 = YEAR_1 - BASE_YEAR
    t2 = YEAR_2 - BASE_YEAR
    t3 = YEAR_3 - BASE_YEAR
    val_t1 = f(t1, A,B,C)
    val_t2 = f(t2, A,B,C)
    speed_t3 = fprime(t3, A,B,C)
    limit_val = A  # giới hạn khi t->∞
    return {
        't1': t1,'t2': t2,'t3': t3,
        'val_t1': val_t1,
        'val_t2': val_t2,
        'speed_t3': speed_t3,
        'limit': limit_val,
        'deriv_num': A*C - B,
    }


def build_statements(topic: str, unit: str, params: Dict[str,int], func_sym: str, ctx: Dict[str, float]) -> List[Tuple[str, bool]]:
    """Sinh 4 mệnh đề (a→d) giữ nguyên thứ tự.

    ctx được truyền vào (tránh lặp tính) – (12).
    """
    A,B,C = params['A'], params['B'], params['C']

    # a) Giá trị tại YEAR_1, YEAR_2
    val_t1 = ctx['val_t1']
    val_t2 = ctx['val_t2']
    true_a = (
        f"{topic} vào các năm {YEAR_1} và {YEAR_2} lần lượt là "
        f"\\( {val_t1:.3f} \\) {unit} và \\( {val_t2:.3f} \\) {unit}"
    )
    # (5) Tạo nhiễu và bảo đảm khác sau làm tròn
    attempts = 0
    while True:
        attempts += 1
        noise = val_t2 * (1 + random.choice([-0.15,-0.10,0.10,0.15]))
        if round(noise,3) != round(val_t2,3) or attempts > 5:
            break
    wrong_a = (
        f"{topic} vào các năm {YEAR_1} và {YEAR_2} lần lượt là "
        f"\\( {val_t1:.3f} \\) {unit} và \\( {noise:.3f} \\) {unit}"
    )

    # b) Đạo hàm tổng quát
    deriv_expr_true = f"\\dfrac{{{ctx['deriv_num']}}}{{(t+{C})^2}}"
    perturb = ctx['deriv_num'] + random.choice([-10,-5,-4,4,5,10])
    if perturb == ctx['deriv_num']:
        perturb += 3
    deriv_expr_wrong = f"\\dfrac{{{perturb}}}{{(t+{C})^2}}"
    true_b = f"Tốc độ thay đổi {topic.lower()} là \\( {func_sym}'(t) = {deriv_expr_true} \\)"
    wrong_b = f"Tốc độ thay đổi {topic.lower()} là \\( {func_sym}'(t) = {deriv_expr_wrong} \\)"

    # c) Tính tăng & giới hạn
    true_c = f"{topic} luôn tăng nhưng không vượt quá {ctx['limit']:.3f} {unit}"
    wrong_c = f"{topic} luôn tăng và có thể vượt quá {(ctx['limit']+random.choice([1,2,3])):.3f} {unit}"

    # d) Tốc độ tại YEAR_3
    speed_round = round(ctx['speed_t3'], ROUND_DIGITS_SPEED)
    wrong_speed_val = speed_round + random.choice([0.01, -0.01, 0.02, -0.02])
    if round(wrong_speed_val, ROUND_DIGITS_SPEED) == speed_round:
        wrong_speed_val += 0.03
    true_d = (
        f"Vào năm {YEAR_3} tốc độ tăng {topic.lower()}: \\({func_sym}'(25)={speed_round:.3f}\\) {unit}/năm (làm tròn đến hàng phần nghìn)"
    )
    wrong_d = (
        f"Vào năm {YEAR_3} tốc độ tăng {topic.lower()}: \\({func_sym}'(25)={round(wrong_speed_val,ROUND_DIGITS_SPEED):.3f}\\) {unit}/năm (làm tròn đến hàng phần nghìn)"
    )

    # Chọn ngẫu nhiên số mệnh đề đúng k và tập loại đúng
    all_types = ["values","derivative","monotonic","speed"]
    k = random.randint(MIN_CORRECT, MAX_CORRECT)
    correct_types = set(random.sample(all_types, k))

    return [
        (true_a if 'values' in correct_types else wrong_a, 'values' in correct_types),
        (true_b if 'derivative' in correct_types else wrong_b, 'derivative' in correct_types),
        (true_c if 'monotonic' in correct_types else wrong_c, 'monotonic' in correct_types),
        (true_d if 'speed' in correct_types else wrong_d, 'speed' in correct_types),
    ]


def build_solution(func_sym: str, params: Dict[str,int], ctx: Dict[str,float], unit: str, correct_letters: List[str]) -> str:
    """(6)(7)(8) Xây lời giải với giải thích đạo hàm và format sạch."""
    A,B,C = params['A'], params['B'], params['C']
    deriv_num = ctx['deriv_num']
    speed_exact = ctx['speed_t3']
    speed_round = round(speed_exact, ROUND_DIGITS_SPEED)
    letters_join = ", ".join(f"({c})" for c in correct_letters)
    # Viết từng dòng: tách phần giải thích ngôn ngữ khỏi toán để tránh ký tự tiếng Việt trong môi trường toán
    lines = []
    lines.append("Mệnh đề đúng: " + letters_join)
    lines.append(f"Hàm: \\({func_sym}(t)=\\dfrac{{{A}t+{B}}}{{t+{C}}}\\).")
    lines.append(
        f"Đạo hàm: \\({func_sym}'(t)=\\dfrac{{{A}\\cdot {C}-{B}}}{{(t+{C})^2}}\\)."
    )
    lines.append(
        f"Vì \\({A}\\cdot {C}-{B}={deriv_num}>0\\) và \\((t+{C})^2>0\\) nên \\({func_sym}'(t)>0\\) ."
)
    lines.append(
        f"\\(\\Rightarrow {func_sym}(t)\\) tăng trên \\([0,+\\infty)\\)."
    )
    lines.append(f"Giới hạn: \\( \\lim_{{t \\to +\\infty}} {func_sym}(t)={A} \\).")
    lines.append(f"Giá trị: \\({func_sym}(0)={ctx['val_t1']:.3f}\\) {unit}, \\({func_sym}(15)={ctx['val_t2']:.3f}\\) {unit}.")
    lines.append(
        f"Tốc độ tại năm {YEAR_3}: \\({func_sym}'(25)=\\dfrac{{{deriv_num}}}{{(25+{C})^2}}={speed_exact:.6f} \\approx {speed_round:.3f}\\) {unit}/năm."
    )
    # Thêm \\ để LaTeX xuống dòng, cuối cùng thêm khoảng cách nhỏ.
    # Xuống dòng rõ ràng mỗi câu: thêm \\ cuối dòng, không dùng \par trộn lẫn.
    # Không thêm ký tự backslash literal vào nội dung file: dùng \\ chỉ một lần.
    # Mỗi dòng kết thúc bằng \\% để tránh khoảng trắng không mong muốn trước newline.
    formatted = "\n".join(f"{l}\\\\%" for l in lines)
    return formatted + "\n\\medskip\n"


class GrowthQuestionGenerator:
    @classmethod
    def generate_single(cls, topic_id: int, index: int) -> Tuple[str, str]:
        """Sinh 1 câu hỏi và lời giải (có thể nhiều mệnh đề đúng)."""
        topic_meta = {t[0]: t for t in TOPICS}[topic_id]
        _, topic, unit = topic_meta
        params = generate_parameters()
        func_sym = random.choice(FUNC_SYMBOLS)
        ctx = compute_context(params)
        statements = build_statements(topic, unit, params, func_sym, ctx)
        A, B, C = params['A'], params['B'], params['C']
        func_str = f"{func_sym}(t)=\\dfrac{{{A}t+{B}}}{{t+{C}}}"
        # Bổ sung đơn vị trong ngoặc ngay sau cụm "sau t năm" theo yêu cầu: (đơn vị <unit>)
        content = (
            f"Câu {index}: Giả sử {topic.lower()} sau t năm (đơn vị {unit}) kể từ năm {BASE_YEAR} được mô tả bởi hàm số \\( {func_str} \\), \\( t \\ge 0 \\). "
            f"Trong các mệnh đề sau, mệnh đề nào đúng?\n\n"
        )
        correct_letters: List[str] = []
        for i, (text, is_correct) in enumerate(statements):
            letter = chr(ord('a') + i)
            marker = '*' if is_correct else ''
            if is_correct:
                correct_letters.append(letter)
            content += f"{marker}{letter}) {text}.\n\n"
        solution_text = build_solution(func_sym, params, ctx, unit, correct_letters)
        return content, solution_text


def main():
    parser = argparse.ArgumentParser()
    # Cho phép cả cú pháp: thuctehamso.py 20  hoặc  thuctehamso.py -n 20
    parser.add_argument('N', nargs='?', type=int, help='Số câu hỏi (positional, tùy chọn)')
    parser.add_argument('-n', type=int, help='Số câu hỏi tạo ra (tùy chọn, ưu tiên nếu có)')
    parser.add_argument('-o','--output', default='growth_questions.tex', help='Tên file .tex xuất ra (mặc định: growth_questions.tex)')
    parser.add_argument('--title', default='Bộ câu hỏi hàm phân thức', help='Tiêu đề LaTeX')
    parser.add_argument('--plain', action='store_true', help='In văn bản thô thay vì ghi file LaTeX')
    args = parser.parse_args()
    # Ưu tiên -n, sau đó đến positional, cuối cùng mặc định 5
    n = args.n if args.n is not None else (args.N if args.N is not None else 5)
    if not (1 <= n <= 1000):
        print('Tham số n không hợp lệ')
        sys.exit(1)
    blocks = []  # lưu từng block Q + solution
    for i in range(1, n+1):
        topic_id = random.randint(1, len(TOPICS))
        q, sol = GrowthQuestionGenerator.generate_single(topic_id, i)
        block = q + 'Lời giải:\n' + sol
        blocks.append(block)

    if args.plain:
        joined = ('\n' + '-'*40 + '\n').join(blocks)
        print(joined)
    else:
        tex = build_full_latex(blocks, args.title)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(tex)
        print(f"Đã tạo file LaTeX: {args.output}\nGợi ý biên dịch: xelatex {args.output}")


def build_full_latex(blocks: List[str], title: str) -> str:
    """Tạo tài liệu LaTeX đầy đủ từ các block câu hỏi."""
    header = ("\\documentclass[a4paper,12pt]{article}\n"
              "\\usepackage{fontspec}\n"
              "\\usepackage{polyglossia}\n"
              "\\setdefaultlanguage{vietnamese}\n"
              "\\defaultfontfeatures{Ligatures=TeX}\n"
              "\\setmainfont{Times New Roman}\n"
              "\\usepackage{amsmath,amssymb,geometry,enumitem}\n"
              "\\geometry{margin=1in}\n"
              f"\\title{{{title}}}\n\\begin{{document}}\\maketitle\n")
    body_parts = []
    for blk in blocks:
        # Thay \n bằng \par cho LaTeX rồi thêm khoảng cách nhỏ
        body_parts.append(blk.replace('\\n', '\n\\par '))
        body_parts.append('\\bigskip')
    body = '\n'.join(body_parts)
    return header + body + "\n\\end{document}\n"


if __name__ == '__main__':
    main()