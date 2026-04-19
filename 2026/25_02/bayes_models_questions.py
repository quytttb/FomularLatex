import os
import random
import logging
from fractions import Fraction
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


# ==============================================================================
# UTILS
# ==============================================================================

def frac_str(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    if f.numerator < 0:
        return rf"-\dfrac{{{abs(f.numerator)}}}{{{f.denominator}}}"
    return rf"\dfrac{{{f.numerator}}}{{{f.denominator}}}"


def fmt_dec(f: Fraction, places: int = 4) -> str:
    """Format Fraction as Vietnamese decimal string (comma separator)."""
    val = float(f)
    s = f"{val:.{places}f}".rstrip('0').rstrip('.')
    if s in ("", "-0"):
        s = "0"
    return s.replace(".", ",")


def fmt_pct(f: Fraction) -> str:
    """Format Fraction as percentage with Vietnamese comma."""
    val = float(f) * 100
    if abs(val - round(val)) < 1e-9:
        return f"{int(round(val))}\\%"
    s = f"{val:.2f}".rstrip('0').rstrip('.')
    return s.replace(".", ",") + "\\%"


def format_prob(f: Fraction) -> str:
    """Format probability as exact decimal if possible, else as fraction."""
    if f.denominator == 1:
        return str(f.numerator)
    d = f.denominator
    while d % 2 == 0: d //= 2
    while d % 5 == 0: d //= 5
    if d == 1:
        val = float(f)
        s = f"{val:.6f}".rstrip('0').rstrip('.')
        if s in ("", "-0"):
            s = "0"
        return s.replace(".", ",")
    else:
        return frac_str(f)


# ==============================================================================
# 10 CONTEXTS
# ==============================================================================

CONTEXTS = [
    {
        "intro": (
            "Một công ty khí tượng sử dụng hai mô hình dự báo thời tiết hoạt động "
            "độc lập với nhau là Mô hình 1 và Mô hình 2."
        ),
        "event_name": "Trời có mưa",
        "event_bar_name": "Trời không mưa",
        "model1_name": "Mô hình 1",
        "model2_name": "Mô hình 2",
        "predict_pos": "dự báo có mưa",
        "predict_neg": "dự báo không mưa",
        "base_desc": "tỷ lệ ngày có mưa trong năm ở khu vực này",
        "sol_event": "A",
        "sol_event_desc": "Trời có mưa",
    },
    {
        "intro": (
            "Tại một xưởng chế tác đồng hồ thủ công tại Thụy Sĩ, trung bình có một tỷ lệ "
            "linh kiện máy gặp lỗi vi mô mà mắt thường không thấy được. Xưởng sử dụng hai "
            "lớp kiểm định độc lập: Hệ thống cảm biến laser (Mô hình 1) và Kính hiển vi "
            "điện tử (Mô hình 2)."
        ),
        "event_name": "Linh kiện bị lỗi",
        "event_bar_name": "Linh kiện đạt chuẩn",
        "model1_name": "Cảm biến laser",
        "model2_name": "Kính hiển vi",
        "predict_pos": "báo lỗi",
        "predict_neg": "báo chuẩn",
        "base_desc": "tỷ lệ linh kiện bị lỗi",
        "sol_event": "A",
        "sol_event_desc": "Linh kiện bị lỗi",
    },
    {
        "intro": (
            "Trong hệ thống quản trị dữ liệu của một tập đoàn, có một tỷ lệ nhất định các "
            "gói tin gửi đến là mã độc. Tập đoàn sử dụng Tường lửa Alpha (Mô hình 1) và "
            "AI Scanner (Mô hình 2) để quét virus độc lập."
        ),
        "event_name": "Gói tin là mã độc",
        "event_bar_name": "Gói tin an toàn",
        "model1_name": "Tường lửa Alpha",
        "model2_name": "AI Scanner",
        "predict_pos": "báo mã độc",
        "predict_neg": "báo an toàn",
        "base_desc": "tỷ lệ gói tin là mã độc",
        "sol_event": "A",
        "sol_event_desc": "Gói tin là mã độc",
    },
    {
        "intro": (
            "Một bệnh viện sử dụng hai phương pháp xét nghiệm độc lập để chẩn đoán bệnh X "
            "cho bệnh nhân: Xét nghiệm máu (Mô hình 1) và Chụp CT (Mô hình 2)."
        ),
        "event_name": "Bệnh nhân mắc bệnh X",
        "event_bar_name": "Bệnh nhân không mắc bệnh X",
        "model1_name": "Xét nghiệm máu",
        "model2_name": "Chụp CT",
        "predict_pos": "chẩn đoán dương tính",
        "predict_neg": "chẩn đoán âm tính",
        "base_desc": "tỷ lệ mắc bệnh X trong cộng đồng",
        "sol_event": "A",
        "sol_event_desc": "Bệnh nhân mắc bệnh X",
    },
    {
        "intro": (
            "Một nhà máy sản xuất vi mạch bán dẫn sử dụng hai hệ thống kiểm tra chất lượng "
            "độc lập: Máy quét quang học (Mô hình 1) và Máy đo điện trở (Mô hình 2)."
        ),
        "event_name": "Vi mạch bị lỗi",
        "event_bar_name": "Vi mạch đạt chuẩn",
        "model1_name": "Máy quét quang học",
        "model2_name": "Máy đo điện trở",
        "predict_pos": "phát hiện lỗi",
        "predict_neg": "báo đạt chuẩn",
        "base_desc": "tỷ lệ vi mạch bị lỗi",
        "sol_event": "A",
        "sol_event_desc": "Vi mạch bị lỗi",
    },
    {
        "intro": (
            "Một sân bay quốc tế sử dụng hai hệ thống an ninh độc lập để phát hiện hành lý "
            "chứa hàng cấm: Máy X-quang (Mô hình 1) và Chó nghiệp vụ (Mô hình 2)."
        ),
        "event_name": "Hành lý chứa hàng cấm",
        "event_bar_name": "Hành lý an toàn",
        "model1_name": "Máy X-quang",
        "model2_name": "Chó nghiệp vụ",
        "predict_pos": "phát hiện hàng cấm",
        "predict_neg": "báo an toàn",
        "base_desc": "tỷ lệ hành lý chứa hàng cấm",
        "sol_event": "A",
        "sol_event_desc": "Hành lý chứa hàng cấm",
    },
    {
        "intro": (
            "Một công ty bất động sản sử dụng hai mô hình dự đoán độc lập để đánh giá rủi ro "
            "tín dụng của khách hàng vay mua nhà: Mô hình chấm điểm tín dụng (Mô hình 1) "
            "và Mô hình phân tích thu nhập (Mô hình 2)."
        ),
        "event_name": "Khách hàng vỡ nợ",
        "event_bar_name": "Khách hàng trả nợ đầy đủ",
        "model1_name": "Mô hình chấm điểm",
        "model2_name": "Mô hình phân tích",
        "predict_pos": "cảnh báo rủi ro",
        "predict_neg": "đánh giá an toàn",
        "base_desc": "tỷ lệ khách hàng vỡ nợ",
        "sol_event": "A",
        "sol_event_desc": "Khách hàng vỡ nợ",
    },
    {
        "intro": (
            "Một trang trại chăn nuôi quy mô lớn sử dụng hai hệ thống giám sát độc lập để "
            "phát hiện dịch bệnh ở đàn gia súc: Cảm biến thân nhiệt (Mô hình 1) và Xét "
            "nghiệm nhanh (Mô hình 2)."
        ),
        "event_name": "Gia súc bị nhiễm bệnh",
        "event_bar_name": "Gia súc khỏe mạnh",
        "model1_name": "Cảm biến thân nhiệt",
        "model2_name": "Xét nghiệm nhanh",
        "predict_pos": "phát hiện bệnh",
        "predict_neg": "báo khỏe mạnh",
        "base_desc": "tỷ lệ gia súc bị nhiễm bệnh",
        "sol_event": "A",
        "sol_event_desc": "Gia súc bị nhiễm bệnh",
    },
    {
        "intro": (
            "Một tòa nhà cao tầng lắp đặt hai hệ thống cảnh báo cháy độc lập: Đầu dò khói "
            "(Mô hình 1) và Cảm biến nhiệt hồng ngoại (Mô hình 2)."
        ),
        "event_name": "Có cháy xảy ra",
        "event_bar_name": "Không có cháy",
        "model1_name": "Đầu dò khói",
        "model2_name": "Cảm biến nhiệt",
        "predict_pos": "báo cháy",
        "predict_neg": "báo an toàn",
        "base_desc": "tỷ lệ các tình huống thực sự có cháy",
        "sol_event": "A",
        "sol_event_desc": "Có cháy xảy ra",
    },
    {
        "intro": (
            "Một công ty viễn thông sử dụng hai hệ thống giám sát mạng độc lập để phát hiện "
            "sự cố đường truyền: Hệ thống SNMP (Mô hình 1) và Hệ thống giám sát lưu lượng "
            "(Mô hình 2)."
        ),
        "event_name": "Đường truyền bị sự cố",
        "event_bar_name": "Đường truyền hoạt động bình thường",
        "model1_name": "Hệ thống SNMP",
        "model2_name": "Giám sát lưu lượng",
        "predict_pos": "phát hiện sự cố",
        "predict_neg": "báo bình thường",
        "base_desc": "tỷ lệ đường truyền gặp sự cố",
        "sol_event": "A",
        "sol_event_desc": "Đường truyền bị sự cố",
    },
]


# ==============================================================================
# PARAMETER VALUE POOLS (for randomization)
# ==============================================================================

P_A_VALUES: List[Fraction] = [
    Fraction(1, 20),   # 5%
    Fraction(2, 25),   # 8%
    Fraction(1, 10),   # 10%
    Fraction(3, 25),   # 12%
    Fraction(1, 8),    # 12,5%
    Fraction(3, 20),   # 15%
    Fraction(4, 25),   # 16%
    Fraction(1, 5),    # 20%
    Fraction(1, 4),    # 25%
    Fraction(6, 25),   # 24%
    Fraction(7, 25),   # 28%
    Fraction(3, 10),   # 30%
    Fraction(8, 25),   # 32%
    Fraction(7, 20),   # 35%
    Fraction(9, 25),   # 36%
    Fraction(3, 8),    # 37,5%
    Fraction(2, 5),    # 40%
    Fraction(11, 25),  # 44%
    Fraction(9, 20),   # 45%
    Fraction(1, 2),    # 50%
]

ACC_VALUES: List[Fraction] = [
    Fraction(3, 5),    # 60%
    Fraction(5, 8),    # 62,5%
    Fraction(13, 20),  # 65%
    Fraction(17, 25),  # 68%
    Fraction(7, 10),   # 70%
    Fraction(18, 25),  # 72%
    Fraction(3, 4),    # 75%
    Fraction(19, 25),  # 76%
    Fraction(4, 5),    # 80%
    Fraction(21, 25),  # 84%
    Fraction(17, 20),  # 85%
    Fraction(7, 8),    # 87,5%
    Fraction(22, 25),  # 88%
    Fraction(9, 10),   # 90%
    Fraction(23, 25),  # 92%
    Fraction(47, 50),  # 94%
    Fraction(19, 20),  # 95%
    Fraction(24, 25),  # 96%
    Fraction(97, 100), # 97%
    Fraction(49, 50),  # 98%
]


def _make_wrong_value(correct: Fraction, offsets: List[Fraction]) -> Fraction:
    """Generate a plausible wrong value in [0, 1]."""
    shuffled = list(offsets)
    random.shuffle(shuffled)
    for delta in shuffled:
        candidate = correct + delta
        if Fraction(0) < candidate < Fraction(1):
            return candidate
    return correct + Fraction(1, 50) if correct < Fraction(1, 2) else correct - Fraction(1, 50)


# ==============================================================================
# MATH ENGINE (all Fraction-based)
# ==============================================================================

class BayesModelsQuestion:

    def __init__(self):
        self.P_A = Fraction(1, 5)
        self.P_Abar = Fraction(4, 5)
        self.acc1 = Fraction(4, 5)
        self.acc2 = Fraction(9, 10)

    def generate_parameters(self) -> None:
        """Randomize P_A, acc1, acc2 for each question."""
        while True:
            self.P_A = random.choice(P_A_VALUES)
            self.P_Abar = 1 - self.P_A
            acc_pool = list(ACC_VALUES)
            random.shuffle(acc_pool)
            self.acc1, self.acc2 = acc_pool[0], acc_pool[1]
            
            # Ensure P_M1_right != P_M2_right for statement b
            m1_right_numer = self.P_Abar * self.acc1 * (1 - self.acc2)
            m2_right_numer = self.P_A * (1 - self.acc1) * self.acc2
            if m1_right_numer != m2_right_numer:
                break

    def compute_all(self):
        P_A = self.P_A
        P_Abar = self.P_Abar
        acc1 = self.acc1
        acc2 = self.acc2

        # Model 1: P(H1|A) = acc1, P(Hbar1|Abar) = acc1
        P_H1_A = acc1
        P_Hbar1_Abar = acc1
        P_Hbar1_A = 1 - acc1
        P_H1_Abar = 1 - acc1

        # Model 2: P(H2|A) = acc2, P(Hbar2|Abar) = acc2
        P_H2_A = acc2
        P_Hbar2_Abar = acc2
        P_Hbar2_A = 1 - acc2
        P_H2_Abar = 1 - acc2

        # --- a1: P(cả 2 sai) ---
        # "cả 2 đều nhận diện SAI" = both M1 wrong AND M2 wrong (independent)
        # P(M1 wrong) = P(Hbar1|A) (if A) or P(H1|Abar) (if Abar)
        # Since independent per sample:
        # P(both wrong) = P(A)*P(Hbar1|A)*P(Hbar2|A) + P(Abar)*P(H1|Abar)*P(H2|Abar)
        P_both_wrong = P_A * P_Hbar1_A * P_Hbar2_A + P_Abar * P_H1_Abar * P_H2_Abar

        # --- a2: P(cả 2 đúng) ---
        P_both_right = P_A * P_H1_A * P_H2_A + P_Abar * P_Hbar1_Abar * P_Hbar2_Abar

        # --- b: M1 báo Abar, M2 báo A ---
        # P(Hbar1 ∩ H2) = P(A)*P(Hbar1|A)*P(H2|A) + P(Abar)*P(Hbar1|Abar)*P(H2|Abar)
        P_Hbar1_H2 = P_A * P_Hbar1_A * P_H2_A + P_Abar * P_Hbar1_Abar * P_H2_Abar

        # P(Abar | Hbar1 ∩ H2) = M1 đúng = P(Abar)*P(Hbar1|Abar)*P(H2|Abar) / P(Hbar1∩H2)
        P_M1_right_given_conflict = P_Abar * P_Hbar1_Abar * P_H2_Abar / P_Hbar1_H2

        # P(A | Hbar1 ∩ H2) = M2 đúng
        P_M2_right_given_conflict = P_A * P_Hbar1_A * P_H2_A / P_Hbar1_H2

        # (So sánh M1 vs M2 được quyết định ở generate(), không ghi số cố định ở đây.)

        # --- c1: P(cả 2 cùng báo A) = P(H1 ∩ H2) ---
        P_H1_H2 = P_A * P_H1_A * P_H2_A + P_Abar * P_H1_Abar * P_H2_Abar

        # --- d1: P(A | H1 ∩ H2) ---
        P_A_given_H1H2 = P_A * P_H1_A * P_H2_A / P_H1_H2

        # --- c2: P(cả 2 cùng báo Abar) = P(Hbar1 ∩ Hbar2) ---
        P_Hbar1_Hbar2 = P_A * P_Hbar1_A * P_Hbar2_A + P_Abar * P_Hbar1_Abar * P_Hbar2_Abar

        # --- d2: P(Abar | Hbar1 ∩ Hbar2) ---
        P_Abar_given_Hbar1Hbar2 = P_Abar * P_Hbar1_Abar * P_Hbar2_Abar / P_Hbar1_Hbar2

        return {
            "P_A": P_A, "P_Abar": P_Abar,
            "acc1": acc1, "acc2": acc2,
            "P_H1_A": P_H1_A, "P_Hbar1_A": P_Hbar1_A,
            "P_H1_Abar": P_H1_Abar, "P_Hbar1_Abar": P_Hbar1_Abar,
            "P_H2_A": P_H2_A, "P_Hbar2_A": P_Hbar2_A,
            "P_H2_Abar": P_H2_Abar, "P_Hbar2_Abar": P_Hbar2_Abar,
            "P_both_wrong": P_both_wrong,
            "P_both_right": P_both_right,
            "P_Hbar1_H2": P_Hbar1_H2,
            "P_M1_right": P_M1_right_given_conflict,
            "P_M2_right": P_M2_right_given_conflict,
            "P_H1_H2": P_H1_H2,
            "P_A_given_H1H2": P_A_given_H1H2,
            "P_Hbar1_Hbar2": P_Hbar1_Hbar2,
            "P_Abar_given_Hbar1Hbar2": P_Abar_given_Hbar1Hbar2,
        }

    def generate(self, q_num: int) -> Tuple[str, str]:
        self.generate_parameters()
        ctx = random.choice(CONTEXTS)
        v = self.compute_all()

        # Decide True/False for each statement
        TF = [random.choice([True, False]) for _ in range(4)]

        # --- Choose a1 or a2 ---
        use_a1 = random.choice([True, False])

        if use_a1:
            correct_a_val = v["P_both_wrong"]
            if TF[0]:
                shown_a_val = correct_a_val
            else:
                shown_a_val = _make_wrong_value(
                    correct_a_val,
                    [Fraction(1, 50), Fraction(-1, 100), Fraction(1, 25), Fraction(-1, 50)],
                )
            stmt_a_text = (
                f"a) Xác suất để cả hai hệ thống đều nhận diện sai trạng thái là "
                f"${format_prob(shown_a_val)}$."
            )
            sol_a_detail = (
                f"$P(\\text{{cả 2 sai}}) = P(A) \\cdot P(\\overline{{H_1}}|A) \\cdot P(\\overline{{H_2}}|A) "
                f"+ P(\\overline{{A}}) \\cdot P(H_1|\\overline{{A}}) \\cdot P(H_2|\\overline{{A}})$\n\n"
                f"$= {fmt_dec(v['P_A'])} \\cdot {fmt_dec(v['P_Hbar1_A'])} \\cdot {fmt_dec(v['P_Hbar2_A'])} "
                f"+ {fmt_dec(v['P_Abar'])} \\cdot {fmt_dec(v['P_H1_Abar'])} \\cdot {fmt_dec(v['P_H2_Abar'])} "
                f"= {format_prob(correct_a_val)}$"
            )
        else:
            correct_a_val = v["P_both_right"]
            if TF[0]:
                shown_a_val = correct_a_val
            else:
                shown_a_val = _make_wrong_value(
                    correct_a_val,
                    [Fraction(1, 50), Fraction(-1, 50), Fraction(-1, 25), Fraction(1, 20)],
                )
            stmt_a_text = (
                f"a) Xác suất để cả hai hệ thống đều nhận diện đúng trạng thái là "
                f"${format_prob(shown_a_val)}$."
            )
            sol_a_detail = (
                f"$P(\\text{{cả 2 đúng}}) = P(A) \\cdot P(H_1|A) \\cdot P(H_2|A) "
                f"+ P(\\overline{{A}}) \\cdot P(\\overline{{H_1}}|\\overline{{A}}) \\cdot P(\\overline{{H_2}}|\\overline{{A}})$\n\n"
                f"$= {fmt_dec(v['P_A'])} \\cdot {fmt_dec(v['P_H1_A'])} \\cdot {fmt_dec(v['P_H2_A'])} "
                f"+ {fmt_dec(v['P_Abar'])} \\cdot {fmt_dec(v['P_Hbar1_Abar'])} \\cdot {fmt_dec(v['P_Hbar2_Abar'])} "
                f"= {format_prob(correct_a_val)}$"
            )

        stmt_a = ("*" if TF[0] else "") + stmt_a_text

        # --- b: M1 báo Abar, M2 báo A, compare ---
        # M1_higher = True khi P(M1 đúng | conflict) > P(M2 đúng | conflict)
        M1_higher = v["P_M1_right"] > v["P_M2_right"]
        if TF[1]:
            stmt_b_text = (
                f"b) Trong trường hợp {ctx['model1_name']} {ctx['predict_neg']} và "
                f"{ctx['model2_name']} {ctx['predict_pos']}, xác suất {ctx['model1_name']} "
                f"dự báo đúng {'cao hơn' if M1_higher else 'thấp hơn'} xác suất {ctx['model2_name']} dự báo đúng."
            )
        else:
            stmt_b_text = (
                f"b) Trong trường hợp {ctx['model1_name']} {ctx['predict_neg']} và "
                f"{ctx['model2_name']} {ctx['predict_pos']}, xác suất {ctx['model1_name']} "
                f"dự báo đúng {'thấp hơn' if M1_higher else 'cao hơn'} xác suất {ctx['model2_name']} dự báo đúng."
            )
        stmt_b = ("*" if TF[1] else "") + stmt_b_text

        P_Abar_Hbar1_H2_numer = v["P_Abar"] * v["P_Hbar1_Abar"] * v["P_H2_Abar"]
        P_A_Hbar1_H2_numer = v["P_A"] * v["P_Hbar1_A"] * v["P_H2_A"]
        cmp_op = ">" if M1_higher else "<"
        higher_name = ctx["model1_name"] if M1_higher else ctx["model2_name"]
        lower_name = ctx["model2_name"] if M1_higher else ctx["model1_name"]
        
        m1_right_str = format_prob(v['P_M1_right'])
        if m1_right_str.startswith(r"\dfrac"):
            m1_right_str += f" \\approx {fmt_dec(v['P_M1_right'], 4)}"
            
        m2_right_str = format_prob(v['P_M2_right'])
        if m2_right_str.startswith(r"\dfrac"):
            m2_right_str += f" \\approx {fmt_dec(v['P_M2_right'], 4)}"
            
        sol_b_detail = (
            f"Xét điều kiện ($\\overline{{H_1}} \\cap H_2$) ({ctx['model1_name']} {ctx['predict_neg']}, "
            f"{ctx['model2_name']} {ctx['predict_pos']}):\n\n"
            f"$P(\\overline{{H_1}} \\cap H_2) = P(A)P(\\overline{{H_1}}|A)P(H_2|A) "
            f"+ P(\\overline{{A}})P(\\overline{{H_1}}|\\overline{{A}})P(H_2|\\overline{{A}})$\n\n"
            f"$= {fmt_dec(v['P_A'])} \\cdot {fmt_dec(v['P_Hbar1_A'])} \\cdot {fmt_dec(v['P_H2_A'])} "
            f"+ {fmt_dec(v['P_Abar'])} \\cdot {fmt_dec(v['P_Hbar1_Abar'])} \\cdot {fmt_dec(v['P_H2_Abar'])} "
            f"= {fmt_dec(v['P_Hbar1_H2'])}$\n\n"
            f"Xác suất {ctx['model1_name']} đúng: $P(\\overline{{A}}|\\overline{{H_1}} \\cap H_2) "
            f"= \\dfrac{{{fmt_dec(P_Abar_Hbar1_H2_numer)}}}{{{fmt_dec(v['P_Hbar1_H2'])}}} "
            f"= {m1_right_str}$\n\n"
            f"Xác suất {ctx['model2_name']} đúng: $P(A|\\overline{{H_1}} \\cap H_2) "
            f"= \\dfrac{{{fmt_dec(P_A_Hbar1_H2_numer)}}}{{{fmt_dec(v['P_Hbar1_H2'])}}} "
            f"= {m2_right_str}$\n\n"
            f"Vì ${format_prob(v['P_M1_right'])} {cmp_op} {format_prob(v['P_M2_right'])}$ nên {higher_name} dự báo đúng "
            f"có xác suất cao hơn {lower_name}."
        )

        # --- c, d: choose pair (c1, d2) or (c2, d1) ---
        use_c1_d2 = random.choice([True, False])

        if use_c1_d2:
            # c = c1: P(H1 ∩ H2)
            correct_c_val = v["P_H1_H2"]
            if TF[2]:
                shown_c_val = correct_c_val
            else:
                shown_c_val = _make_wrong_value(
                    correct_c_val,
                    [Fraction(1, 25), Fraction(-1, 25), Fraction(1, 20), Fraction(-1, 20)],
                )
            stmt_c_text = (
                f"c) Xác suất để cả hai hệ thống cùng {ctx['predict_pos']} là "
                f"${format_prob(shown_c_val)}$."
            )
            sol_c_detail = (
                f"$P(H_1 \\cap H_2) = P(A)P(H_1|A)P(H_2|A) + P(\\overline{{A}})P(H_1|\\overline{{A}})P(H_2|\\overline{{A}})$\n\n"
                f"$= {fmt_dec(v['P_A'])} \\cdot {fmt_dec(v['P_H1_A'])} \\cdot {fmt_dec(v['P_H2_A'])} "
                f"+ {fmt_dec(v['P_Abar'])} \\cdot {fmt_dec(v['P_H1_Abar'])} \\cdot {fmt_dec(v['P_H2_Abar'])} "
                f"= {format_prob(correct_c_val)}$"
            )

            # d = d2: P(Abar | Hbar1 ∩ Hbar2)
            correct_d_val = v["P_Abar_given_Hbar1Hbar2"]
            if TF[3]:
                shown_d_val = correct_d_val
            else:
                shown_d_val = _make_wrong_value(
                    correct_d_val,
                    [Fraction(-1, 20), Fraction(1, 20), Fraction(-1, 10), Fraction(1, 25)],
                )
            stmt_d_text = (
                f"d) Nếu cả hai hệ thống cùng {ctx['predict_neg']} thì xác suất thực tế "
                f"``{ctx['event_bar_name']}'' là ${format_prob(shown_d_val)}$."
            )
            
            m1_d2_str = format_prob(correct_d_val)
            if m1_d2_str.startswith(r"\dfrac"):
                m1_d2_str += f" \\approx {fmt_dec(correct_d_val, 4)}"
                
            sol_d_detail = (
                f"$P(\\overline{{H_1}} \\cap \\overline{{H_2}}) = P(A)P(\\overline{{H_1}}|A)P(\\overline{{H_2}}|A) "
                f"+ P(\\overline{{A}})P(\\overline{{H_1}}|\\overline{{A}})P(\\overline{{H_2}}|\\overline{{A}})$\n\n"
                f"$= {fmt_dec(v['P_A'])} \\cdot {fmt_dec(v['P_Hbar1_A'])} \\cdot {fmt_dec(v['P_Hbar2_A'])} "
                f"+ {fmt_dec(v['P_Abar'])} \\cdot {fmt_dec(v['P_Hbar1_Abar'])} \\cdot {fmt_dec(v['P_Hbar2_Abar'])} "
                f"= {fmt_dec(v['P_Hbar1_Hbar2'])}$\n\n"
                f"$P(\\overline{{A}} | \\overline{{H_1}} \\cap \\overline{{H_2}}) "
                f"= \\dfrac{{{fmt_dec(v['P_Abar'] * v['P_Hbar1_Abar'] * v['P_Hbar2_Abar'])}}}"
                f"{{{fmt_dec(v['P_Hbar1_Hbar2'])}}} = {m1_d2_str}$"
            )
        else:
            # c = c2: P(Hbar1 ∩ Hbar2)
            correct_c_val = v["P_Hbar1_Hbar2"]
            if TF[2]:
                shown_c_val = correct_c_val
            else:
                shown_c_val = _make_wrong_value(
                    correct_c_val,
                    [Fraction(1, 25), Fraction(-1, 25), Fraction(8, 100), Fraction(-1, 20)],
                )
            stmt_c_text = (
                f"c) Xác suất để cả hai hệ thống cùng {ctx['predict_neg']} là "
                f"${format_prob(shown_c_val)}$."
            )
            sol_c_detail = (
                f"$P(\\overline{{H_1}} \\cap \\overline{{H_2}}) = P(A)P(\\overline{{H_1}}|A)P(\\overline{{H_2}}|A) "
                f"+ P(\\overline{{A}})P(\\overline{{H_1}}|\\overline{{A}})P(\\overline{{H_2}}|\\overline{{A}})$\n\n"
                f"$= {fmt_dec(v['P_A'])} \\cdot {fmt_dec(v['P_Hbar1_A'])} \\cdot {fmt_dec(v['P_Hbar2_A'])} "
                f"+ {fmt_dec(v['P_Abar'])} \\cdot {fmt_dec(v['P_Hbar1_Abar'])} \\cdot {fmt_dec(v['P_Hbar2_Abar'])} "
                f"= {format_prob(correct_c_val)}$"
            )

            # d = d1: P(A | H1 ∩ H2)
            correct_d_val = v["P_A_given_H1H2"]
            if TF[3]:
                shown_d_val = correct_d_val
            else:
                shown_d_val = _make_wrong_value(
                    correct_d_val,
                    [Fraction(-1, 10), Fraction(1, 20), Fraction(-1, 20), Fraction(1, 25)],
                )
            stmt_d_text = (
                f"d) Nếu cả hai hệ thống cùng {ctx['predict_pos']} thì xác suất thực tế "
                f"``{ctx['event_name']}'' là ${format_prob(shown_d_val)}$."
            )
            
            m1_d1_str = format_prob(correct_d_val)
            if m1_d1_str.startswith(r"\dfrac"):
                m1_d1_str += f" \\approx {fmt_dec(correct_d_val, 4)}"
                
            sol_d_detail = (
                f"$P(H_1 \\cap H_2) = P(A)P(H_1|A)P(H_2|A) + P(\\overline{{A}})P(H_1|\\overline{{A}})P(H_2|\\overline{{A}})$\n\n"
                f"$= {fmt_dec(v['P_A'])} \\cdot {fmt_dec(v['P_H1_A'])} \\cdot {fmt_dec(v['P_H2_A'])} "
                f"+ {fmt_dec(v['P_Abar'])} \\cdot {fmt_dec(v['P_H1_Abar'])} \\cdot {fmt_dec(v['P_H2_Abar'])} "
                f"= {fmt_dec(v['P_H1_H2'])}$\n\n"
                f"$P(A | H_1 \\cap H_2) "
                f"= \\dfrac{{{fmt_dec(v['P_A'] * v['P_H1_A'] * v['P_H2_A'])}}}"
                f"{{{fmt_dec(v['P_H1_H2'])}}} = {m1_d1_str}$"
            )

        stmt_c = ("*" if TF[2] else "") + stmt_c_text
        stmt_d = ("*" if TF[3] else "") + stmt_d_text

        ans = ["Đúng" if t else "Sai" for t in TF]

        # --- Build question text ---
        acc1_pct = fmt_pct(self.acc1)
        acc2_pct = fmt_pct(self.acc2)
        base_pct = fmt_pct(self.P_A)

        question_text = (
            f"{ctx['intro']}\n\n"
            f"1) {ctx['model1_name']}: Có xác suất dự báo đúng là ${acc1_pct}$. "
            f"Nghĩa là, nếu thực tế ``{ctx['event_name']}'', xác suất {ctx['model1_name']} "
            f"{ctx['predict_pos']} là ${acc1_pct}$; nếu thực tế ``{ctx['event_bar_name']}'', "
            f"xác suất {ctx['model1_name']} {ctx['predict_neg']} là ${acc1_pct}$.\n\n"
            f"2) {ctx['model2_name']}: Có xác suất dự báo đúng là ${acc2_pct}$. "
            f"Nghĩa là, nếu thực tế ``{ctx['event_name']}'', xác suất {ctx['model2_name']} "
            f"{ctx['predict_pos']} là ${acc2_pct}$; nếu thực tế ``{ctx['event_bar_name']}'', "
            f"xác suất {ctx['model2_name']} {ctx['predict_neg']} là ${acc2_pct}$.\n\n"
            f"Biết rằng {ctx['base_desc']} là ${base_pct}$.\n\n"
            f"{stmt_a}\n\n"
            f"{stmt_b}\n\n"
            f"{stmt_c}\n\n"
            f"{stmt_d}"
        )

        # --- Build solution text ---
        solution_text = (
            f"Lời giải\n\n"
            f"Gọi $A$ là biến cố ``{ctx['event_name']}''. Theo giả thiết:\n\n"
            f"$P(A) = {fmt_dec(self.P_A)}$, $P(\\overline{{A}}) = {fmt_dec(self.P_Abar)}$.\n\n"
            f"Gọi $H_1$ là biến cố ``{ctx['model1_name']} {ctx['predict_pos']}''.\n\n"
            f"Gọi $H_2$ là biến cố ``{ctx['model2_name']} {ctx['predict_pos']}''.\n\n"
            f"Dựa trên độ chính xác của các mô hình:\n\n"
            f"{str(ctx['model1_name']).capitalize()}: "
            f"$P(H_1|A) = {fmt_dec(self.acc1)}$; $P(\\overline{{H_1}}|\\overline{{A}}) = {fmt_dec(self.acc1)}$ (đúng)\n\n"
            f"$P(\\overline{{H_1}}|A) = {fmt_dec(1 - self.acc1)}$; $P(H_1|\\overline{{A}}) = {fmt_dec(1 - self.acc1)}$ (sai)\n\n"
            f"{str(ctx['model2_name']).capitalize()}: "
            f"$P(H_2|A) = {fmt_dec(self.acc2)}$; $P(\\overline{{H_2}}|\\overline{{A}}) = {fmt_dec(self.acc2)}$ (đúng)\n\n"
            f"$P(\\overline{{H_2}}|A) = {fmt_dec(1 - self.acc2)}$; $P(H_2|\\overline{{A}}) = {fmt_dec(1 - self.acc2)}$ (sai)\n\n"
            f"Mệnh đề a: {ans[0]}. Vì hai mô hình độc lập:\n\n"
            f"{sol_a_detail}\n\n"
            f"Mệnh đề b: {ans[1]}.\n\n"
            f"{sol_b_detail}\n\n"
            f"Mệnh đề c: {ans[2]}.\n\n"
            f"{sol_c_detail}\n\n"
            f"Mệnh đề d: {ans[3]}.\n\n"
            f"{sol_d_detail}"
        )

        final = (
            f"\\begin{{ex}}%Câu {q_num}\n"
            + question_text.strip()
            + "\n\n\\loigiai{\n"
            + solution_text.strip()
            + "\n}\n\\end{ex}"
        )
        return final, ""


# ==============================================================================
# DOCUMENT
# ==============================================================================

def create_document(questions: List[Tuple[str, str]]) -> str:
    content = "\n\n".join(q for q, _ in questions)
    return (
        r"\documentclass[12pt,a4paper]{article}" "\n"
        r"\usepackage{amsmath,amssymb}" "\n"
        r"\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}" "\n"
        r"\usepackage[solcolor]{ex_test}" "\n\n"
        r"\begin{document}" "\n\n"
        + content + "\n\n"
        r"\end{document}" "\n"
    )


if __name__ == "__main__":
    import sys
    num_q = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else random.randint(1, 10000)
    random.seed(seed)
    logging.info(f"Generating {num_q} questions with seed {seed}")

    gen = BayesModelsQuestion()
    qs = []
    for i in range(num_q):
        qs.append(gen.generate(i + 1))

    latex_content = create_document(qs)
    out_file = os.path.join(os.path.dirname(__file__), "bayes_models_questions.tex")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(latex_content)
    logging.info(f"Saved to {out_file}")
