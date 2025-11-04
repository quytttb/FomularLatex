import math
import sys
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple

"""tangtruonglogistic.py

Sinh câu hỏi Đúng/Sai (1 đến 4 mệnh đề đúng) dựa trên mô hình tăng trưởng logistic
    L(t) = 600 / (1 + 3 * e^{-0.02 t})
Các mệnh đề xoay quanh: giá trị ban đầu, giá trị tại thời điểm mục tiêu, đạo hàm, tiệm cận, thời gian đạt ngưỡng...

Chuyển đổi từ phiên bản hàm phân thức sang phiên bản logistic với
các tham số cố định và PROBLEM_CONTEXT gồm 10 chủ đề.

Cấu trúc mệnh đề (a)-(d) (nhiều mệnh đề đúng ngẫu nhiên):
    a) Giá trị quần thể tại năm gốc và sau T năm (T = thoi_gian_can_thiet)
    b) Công thức đạo hàm tổng quát
    c) Tiệm cận trên (sức chứa môi trường) và tính đơn điệu tăng
    d) Thời điểm quần thể đạt mốc mục tiêu (so_ca_the_muc_tieu)

Mỗi mệnh đề đúng được đánh dấu * khi in ra.
"""

# ===========================
# Tham số cố định của mô hình logistic
# ===========================
nam_goc = 0  # mốc t=0
so_ca_the_ban_dau = 150  # L(0) kỳ vọng (kiểm tra chênh lệch nhỏ)
so_ca_the_muc_tieu = 300
so_ca_the_toi_da = 600   # sức chứa môi trường K
thoi_gian_can_thiet = 50  # dùng trong mệnh đề a)

# Hàm logistic: L(t) = K / (1 + A e^{-r t}) (các tham số cố định)
K = 600
A = 3
r = 0.02

PROBLEM_CONTEXT: List[Dict] = [
    {"de": 1, "chu_de": "Bảo tồn loài thú quý hiếm", "don_vi": "cá thể"},
    {"de": 2, "chu_de": "Quần thể chim di cư", "don_vi": "cá thể"},
    {"de": 3, "chu_de": "Cá thể rùa biển", "don_vi": "cá thể"},
    {"de": 4, "chu_de": "Đàn voi rừng", "don_vi": "cá thể"},
    {"de": 5, "chu_de": "Đàn cá heo", "don_vi": "cá thể"},
    {"de": 6, "chu_de": "Quần thể gấu trúc", "don_vi": "cá thể"},
    {"de": 7, "chu_de": "Đàn hươu sao", "don_vi": "cá thể"},
    {"de": 8, "chu_de": "Quần thể khỉ", "don_vi": "cá thể"},
    {"de": 9, "chu_de": "Đàn cá sấu", "don_vi": "cá thể"},
    {"de": 10, "chu_de": "Quần thể chim hồng hạc", "don_vi": "cá thể"},
]


def L(t: float) -> float:
    return K / (1 + A * math.exp(-r * t))


def Lprime(t: float) -> float:
    # L'(t) = K * A * r * e^{-r t} / (1 + A e^{-r t})^2
    return (K * A * r * math.exp(-r * t)) / (1 + A * math.exp(-r * t)) ** 2


@dataclass
class LogisticParams:
    K: float = K
    A: float = A
    r: float = r
    nam_goc: int = nam_goc
    so_ca_the_ban_dau: float = so_ca_the_ban_dau
    so_ca_the_muc_tieu: float = so_ca_the_muc_tieu
    so_ca_the_toi_da: float = so_ca_the_toi_da
    thoi_gian_can_thiet: int = thoi_gian_can_thiet


ROUND_DIGITS = 3  # số chữ số thập phân chuẩn cho giá trị L(t)

# Giới hạn số mệnh đề đúng (kiểm soát tối thiểu/tối đa)
MIN_CORRECT = 1
MAX_CORRECT = 3  # không cho tất cả 4 cùng đúng để tăng độ phân biệt

# Hằng số nhân trong đạo hàm để trình bày gọn (K*A*r)
DERIV_COEFF = K * A * r  # = 600*3*0.02 = 36.0


def _ensure_param_consistency(tol: float = 1e-9) -> None:
    """Đảm bảo so_ca_the_ban_dau khớp với L(0); nếu lệch tự động điều chỉnh.

    (Yêu cầu 1) – vì các tham số cố định, việc điều chỉnh chỉ xảy ra nếu người dùng
    sửa một tham số mà quên cập nhật so_ca_the_ban_dau.
    """
    global so_ca_the_ban_dau
    val0 = K / (1 + A)
    while abs(val0 - so_ca_the_ban_dau) > tol:
        # Cập nhật để nhất quán và thông báo.
        original = so_ca_the_ban_dau
        so_ca_the_ban_dau = val0
        print(f"[INFO] Điều chỉnh so_ca_the_ban_dau từ {original} -> {so_ca_the_ban_dau} (tự động nhất quán tham số)")
        # Recompute (trong trường hợp tham số thay đổi vòng sau) – ở đây cố định nên vòng lặp sẽ dừng.
        val0 = K / (1 + A)


def time_to_reach(value: float) -> float:
    """Tính thời điểm t sao cho L(t) = value (0 < value < K).
    value = K / (1 + A e^{-r t}) => 1 + A e^{-r t} = K/value
    A e^{-r t} = K/value - 1 => e^{-r t} = (K/value - 1)/A
    t = -(1/r) ln((K/value - 1)/A)
    """
    if not (0 < value < K):
        raise ValueError("value phải giữa 0 và K")
    ratio = (K / value) - 1
    inner = ratio / A
    return - (1 / r) * math.log(inner)


def build_statements_logistic(ctx: Dict) -> List[Tuple[str, bool]]:
    """Sinh 4 mệnh đề (a-d) theo văn phong chuẩn hóa cung cấp.

    Các nhóm mệnh đề:
      a) Giá trị ban đầu (initial)
      b) Xu thế tăng & ổn định (monotonic)
      c) Thời gian để vượt ngưỡng mục tiêu 300 (time_threshold)
      d) Giới hạn trên 600 (upper_bound)

    Ta vẫn cho phép ngẫu nhiên 1..3 mệnh đề đúng để giữ tính trắc nghiệm.
    """
    unit = ctx['don_vi']
    params = LogisticParams()

    # a) Giá trị ban đầu 150
    true_a = f"Ban đầu có {params.so_ca_the_ban_dau:.0f} {unit}."
    # Sai: nhiễu ± (10,20,30)
    wrong_init = params.so_ca_the_ban_dau + random.choice([-30,-20,-10,10,20,30])
    while wrong_init == params.so_ca_the_ban_dau or wrong_init <= 0:
        wrong_init += random.choice([5,-5,15])
    wrong_a = f"Ban đầu có {wrong_init:.0f} {unit}."

    # b) Tính tăng dần & ổn định (đúng) / sai: giảm dần hoặc tăng rồi giảm
    true_b = "Quần thể tăng đều và tiến tới ổn định."
    wrong_b = "Quần thể ban đầu tăng rồi giảm về 0."

    # c) Thời gian vượt 300 (đúng: cần ~ t >= time_to_reach(300))
    t_reach = time_to_reach(params.so_ca_the_muc_tieu)
    t_reach_round = round(t_reach)
    true_c = f"Cần ít nhất {t_reach_round} năm để vượt {params.so_ca_the_muc_tieu} {unit}."
    # Sai: nói vượt trước đáng kể (trừ 10 hoặc 15 năm nhưng không âm)
    wrong_c_year = max(1, t_reach_round - random.choice([10,15]))
    wrong_c = f"Chỉ cần khoảng {wrong_c_year} năm là vượt mức {params.so_ca_the_muc_tieu} {unit}."

    # d) Giới hạn trên 600 (đúng) / sai: nói có thể vượt quá hoặc đạt tối đa nhỏ hơn
    true_d = f"Quần thể không vượt quá {params.so_ca_the_toi_da} {unit}."
    wrong_d = f"Quần thể có thể vượt quá {params.so_ca_the_toi_da} {unit}."

    types = ["initial","monotonic","time_threshold","upper"]
    k = random.randint(MIN_CORRECT, MAX_CORRECT)
    correct = set(random.sample(types, k))

    return [
        (true_a if 'initial' in correct else wrong_a, 'initial' in correct),
        (true_b if 'monotonic' in correct else wrong_b, 'monotonic' in correct),
        (true_c if 'time_threshold' in correct else wrong_c, 'time_threshold' in correct),
        (true_d if 'upper' in correct else wrong_d, 'upper' in correct),
    ]


def build_solution(correct_letters: List[str], func_symbol: str) -> str:
    """(6) Xây dựng lời giải chi tiết; cho phép đa dạng hóa ký hiệu hàm logistic.

    func_symbol: một ký tự trong tập {H,G,K,L,M,N,F} được chọn ngẫu nhiên cho mỗi câu.
    """
    params = LogisticParams()
    t_reach_exact = time_to_reach(params.so_ca_the_muc_tieu)
    t_reach_round = round(t_reach_exact, 3)
    fs = func_symbol  # alias ngắn
    lines: List[str] = []
    lines.append("Mệnh đề đúng: " + ", ".join(f"({c})" for c in correct_letters))
    # (5) Giải thích chi tiết đạo hàm & (10) công thức t mục tiêu
    lines.append(
        f"Đạo hàm: \\( {fs}'(t)=\\dfrac{{{DERIV_COEFF:.0f} e^{{-{r}t}}}}{{(1+{A} e^{{-{r}t}})^2}} \\)."
    )
    lines.append(f"Vì \\( e^{{-{r}t}} > 0 \\) và mẫu bình phương dương nên \\( {fs}'(t) > 0 \\Rightarrow {fs}(t) \\) tăng.")
    lines.append(f"Tiệm cận: \\( \\lim_{{t \\to +\\infty}} {fs}(t) = {K} \\).")
    lines.append(f"Giá trị: {fs}(0)={L(0):.0f}, {fs}({params.thoi_gian_can_thiet})={L(params.thoi_gian_can_thiet):.0f} (xấp xỉ).")
    lines.append(f"Mốc {params.so_ca_the_muc_tieu}: \\( t = \\tfrac{{1}}{{{r}}} \\ln 3 \\approx {t_reach_round:.1f} \\) năm.")
    lines.append(f"Suy luận: \\( \\tfrac{{K}}{{{params.so_ca_the_muc_tieu}}} = 2 \\Rightarrow 1 + A e^{{-{r}t}} = 2 \\Rightarrow A e^{{-{r}t}} = 1 \\Rightarrow e^{{-{r}t}} = \\tfrac{{1}}{{3}} \\).")
    return "\n".join((l + (" \\\\[2pt]" if i < len(lines)-1 else "")) for i,l in enumerate(lines))


def build_question(idx: int, ctx: Dict) -> Tuple[str,str]:
    func_symbol = 'N'  # Chuẩn hóa ký hiệu theo ví dụ
    subject = ctx['chu_de'].lower()
    # Loại bỏ chuỗi dẫn trùng 'số lượng cá thể của cá thể' nếu vô tình xuất hiện
    subject = subject.replace('cá thể ', '') if subject.startswith('cá thể cá') else subject
    intro = (f"Câu {idx}: Người ta ước tính rằng số lượng cá thể của {subject} sau t năm kể từ khi chính sách bảo vệ được thiết lập có thể "
             f"được mô hình hóa bởi: \\({func_symbol}(t)=\\dfrac{{{K}}}{{1+{A} e^{{-{r}t}}}}\\), \\( t \\ge 0 \\).\n\n ")
    statements = build_statements_logistic(ctx)
    content = intro
    correct_letters: List[str] = []
    for i,(text,is_correct) in enumerate(statements):
        letter = chr(ord('a')+i)
        mark = '*' if is_correct else ''
        if is_correct:
            correct_letters.append(letter)
        content += f"{mark}{letter}) {text}\n\n"
    solution = build_solution(correct_letters, func_symbol)
    return content, solution


def generate_multiple(n: int = 5, shuffle: bool = True) -> Tuple[List[str], List[str]]:
    subset = PROBLEM_CONTEXT[:]
    if shuffle:
        random.shuffle(subset)
    subset = subset[:min(n, len(subset))]
    questions = []
    solutions = []
    for i,ctx in enumerate(subset, start=1):
        q, s = build_question(i, ctx)
        questions.append(q)
        solutions.append(s)
    return questions, solutions


def create_latex_document(questions: List[str], solutions: List[str], title: str = "Bài tập Tăng trưởng Logistic") -> str:
    header = ("\\documentclass[a4paper,12pt]{article}\n"
              "\\usepackage{fontspec,polyglossia,amsmath,amssymb,geometry,enumitem}\n"
              "\\setdefaultlanguage{vietnamese}\n"
              "\\setmainfont{Times New Roman}\n"
              "\\geometry{margin=1in}\n"
              f"\\begin{{document}}\\title{{{title}}}\\maketitle\n")
    blocks = []
    for q,s in zip(questions, solutions):
        blocks.append(q + "Lời giải:\n" + s + "\n")
    return header + "\n".join(blocks) + "\\end{document}\n"


def create_latex_file(questions: List[str], solutions: List[str], filename: str = "logistic_questions.tex") -> str:
    doc = create_latex_document(questions, solutions)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(doc)
    print(f"Đã tạo file: {filename}")
    return filename


def main():
    """(9) Hàm CLI chuẩn hóa + gọi kiểm tra tham số.

    Dùng: python tangtruonglogistic.py [n] [--no-shuffle]
    """
    _ensure_param_consistency()
    n = 5
    shuffle = True
    args = sys.argv[1:]
    for a in args:
        if a == '--no-shuffle':
            shuffle = False
        else:
            try:
                n = int(a)
            except ValueError:
                pass
    questions, solutions = generate_multiple(n, shuffle=shuffle)
    create_latex_file(questions, solutions)


if __name__ == "__main__":
    main()