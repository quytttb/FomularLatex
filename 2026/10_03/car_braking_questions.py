import os
import random
import logging
from fractions import Fraction
from typing import Dict, Any, List, Tuple

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


def fmt_dec(f: Fraction, places: int = 2) -> str:
    val = float(f)
    s = f"{val:.{places}f}".rstrip('0').rstrip('.')
    if s in ("", "-0"):
        s = "0"
    return s.replace(".", ",")


def safe_int(f: Fraction) -> int:
    assert f.denominator == 1, f"Expected integer, got {f}"
    return int(f)


# ==============================================================================
# 10 CONTEXTS
# ==============================================================================

CONTEXTS = [
    {
        "intro": (
            "Trong một cuộc thử nghiệm tại trung tâm nghiên cứu giao thông, một con tàu điện "
            "đang vận hành ở tốc độ {v0_kmh} km/h tại điểm mốc A. Hệ thống Autopilot được "
            "lập trình để dừng tàu tại ga B cách A một khoảng cách {AB} m. Giai đoạn đầu, "
            "máy tính điều khiển lực hãm để vận tốc giảm theo mô hình tuyến tính "
            "$v(t) = at + b$ $(m/s)$, với $t$ tính theo giây và bắt đầu tính từ lúc đạp phanh. "
            "Đúng {t1} giây sau khi kích hoạt lệnh dừng, bộ cảm biến LiDAR phát hiện một "
            "chướng ngại vật tĩnh trên đường ray cách tàu {gap} m. Để tránh va chạm, "
            "hệ thống chuyển sang chế độ Safe-Mode, duy trì vận tốc hằng số {vC} m/s. "
            "Chế độ này được giữ trong {t2} giây cho đến khi tàu đi qua hoàn toàn khu vực cảnh "
            "báo. Sau khi nhận tín hiệu an toàn, hệ thống thực hiện lệnh phanh cuối theo hàm "
            "số $v(t) = ct^2 + d$ $(m/s)$ để đảm bảo tàu dừng chính xác tại điểm B ($v_B = 0$)."
        ),
        "obstacle_name": "khu vực có chướng ngại vật (vùng cảnh báo)",
        "vehicle": "tàu",
        "start": "điểm mốc A",
        "end": "ga B",
    },
    {
        "intro": (
            "Một đoàn tàu điện ngầm đang lướt đi với vận tốc {v0_kmh} km/h qua trạm điều "
            "phối A. Hệ thống trung tâm lập kế hoạch cho tàu dừng tại ga B cách đó {AB} m "
            "bằng cách giảm tốc độ theo hàm $v(t) = at + b$ $(m/s)$, với $t$ tính theo giây "
            "và bắt đầu tính từ lúc đạp phanh. Sau {t1} giây giảm tốc, hệ thống nhận được "
            "cảnh báo có nhân viên đang bảo trì đường ray tại vị trí cách tàu {gap} m. "
            "Để đảm bảo an toàn, tàu được lệnh giữ nguyên vận tốc {vC} m/s trong suốt "
            "{t2} giây để đi qua khu vực bảo trì. Vừa thoát khỏi khu vực này, tàu lập tức "
            "hãm phanh theo quy luật hàm bậc hai $v(t) = ct^2 + d$ $(m/s)$ để dừng đúng vị "
            "trí đón khách tại ga B ($v_B = 0$)."
        ),
        "obstacle_name": "khu vực có nhân viên đang bảo trì đường ray",
        "vehicle": "tàu",
        "start": "trạm điều phối A",
        "end": "ga B",
    },
    {
        "intro": (
            "Một thiết bị bay không người lái (Drone) đang bay thẳng ở độ cao thấp với "
            "vận tốc {v0_kmh} km/h. Cách điểm đáp B là {AB} m, Drone bắt đầu giảm tốc "
            "theo lộ trình $v(t) = at + b$ $(m/s)$, với $t$ tính theo giây. Sau {t1} giây, "
            "cảm biến siêu âm phát hiện một vùng nhiễu động không khí mạnh cách đó {gap} m. "
            "Để đảm bảo hàng hóa bên trong không bị rung lắc, Drone duy trì vận tốc ổn định "
            "{vC} m/s trong {t2} giây để bay qua vùng này. Sau khi thoát vùng nhiễu động, "
            "Drone tiếp tục giảm tốc theo hàm bậc hai $v(t) = ct^2 + d$ $(m/s)$ và hạ cánh "
            "dừng hẳn tại B ($v_B = 0$)."
        ),
        "obstacle_name": "vùng nhiễu động không khí mạnh",
        "vehicle": "Drone",
        "start": "vị trí bắt đầu giảm tốc",
        "end": "điểm đáp B",
    },
    {
        "intro": (
            "Bác tài Tâm lái xe chở kính cường lực đi qua vị trí A với vận tốc "
            "{v0_kmh} km/h. Để dừng lại tại kho hàng B cách đó {AB} m, bác Tâm rà phanh "
            "theo biểu thức $v(t) = at + b$ $(m/s)$, với $t$ tính theo giây. Sau {t1} giây, "
            "bác phát hiện một đoạn đường gồ ghề đầy ổ gà cách xe {gap} m. Để kính không "
            "bị rung vỡ, bác giữ tốc độ ổn định {vC} m/s trong {t2} giây để đi qua. "
            "Khi vượt qua đoạn đường xóc, bác lại giảm tốc độ theo quy luật hàm bậc hai "
            "$v(t) = ct^2 + d$ $(m/s)$ và dừng hẳn tại cửa kho B ($v_B = 0$)."
        ),
        "obstacle_name": "đoạn đường gồ ghề đầy ổ gà",
        "vehicle": "xe",
        "start": "vị trí A",
        "end": "cửa kho B",
    },
    {
        "intro": (
            "Một chiếc xe bọc thép đang di chuyển với tốc độ {v0_kmh} km/h hướng về cổng "
            "kho bạc B cách vị trí A là {AB} m. Tại A, xe bắt đầu giảm tốc theo hàm số "
            "$v(t) = at + b$ $(m/s)$, với $t$ tính theo giây. Sau {t1} giây, xe tới gần khu "
            "vực kiểm soát an ninh cách đó {gap} m. Để nhân viên an ninh thực hiện quét mã "
            "nhận diện từ xa, xe phải giữ tốc độ không đổi {vC} m/s trong {t2} giây. Vừa "
            "qua khỏi trạm kiểm soát, xe thực hiện lệnh dừng theo hàm số bậc hai "
            "$v(t) = ct^2 + d$ $(m/s)$ để đỗ đúng vị trí bốc dỡ an toàn tại B ($v_B = 0$)."
        ),
        "obstacle_name": "khu vực kiểm soát an ninh",
        "vehicle": "xe",
        "start": "vị trí A",
        "end": "điểm bốc dỡ B",
    },
    {
        "intro": (
            "Một xe nâng tự động đang di chuyển trên đường ray với vận tốc {v0_kmh} km/h. "
            "Hệ thống lập trình cho xe dừng tại vị trí xếp hàng B cách vị trí A là {AB} m "
            "theo hàm $v(t) = at + b$ $(m/s)$, với $t$ tính theo giây. Được {t1} giây, "
            "cảm biến phát hiện có Robot khác đang chuẩn bị băng ngang đường cách đó {gap} m. "
            "Xe giữ vận tốc ổn định {vC} m/s trong {t2} giây để chờ đường thông thoáng. "
            "Sau đó, xe tiếp tục giảm tốc theo hàm bậc hai $v(t) = ct^2 + d$ $(m/s)$ "
            "và dừng hẳn tại B ($v_B = 0$)."
        ),
        "obstacle_name": "khu vực giao nhau (nơi Robot khác băng ngang)",
        "vehicle": "xe nâng",
        "start": "vị trí A",
        "end": "điểm B",
    },
    {
        "intro": (
            "Xe buýt nhanh BRT đang chạy với vận tốc {v0_kmh} km/h tại vị trí A. Tài xế "
            "bắt đầu giảm tốc để dừng tại bến B cách đó {AB} m theo biểu thức "
            "$v(t) = at + b$ $(m/s)$, với $t$ tính theo giây. Sau khi thực hiện giảm tốc "
            "được {t1} giây, tài xế thấy phía trước cách xe {gap} m có một vũng nước sâu. "
            "Tài xế điều chỉnh để giữ vận tốc ổn định {vC} m/s trong {t2} giây để xe lướt "
            "qua vũng nước mà không làm chết máy. Sau đó, tài xế thực hiện phanh dừng theo "
            "quy luật $v(t) = ct^2 + d$ $(m/s)$ để dừng hẳn tại bến B ($v_B = 0$)."
        ),
        "obstacle_name": "vũng nước sâu",
        "vehicle": "xe buýt",
        "start": "vị trí A",
        "end": "bến B",
    },
    {
        "intro": (
            "Cua-rơ đang lao về đích với vận tốc {v0_kmh} km/h tại vị trí mốc A cách "
            "đích B là {AB} m. Vận động viên bắt đầu giảm tốc độ theo hàm số "
            "$v(t) = at + b$ $(m/s)$, với $t$ tính theo giây. Sau {t1} giây, phía trước "
            "cách {gap} m là khu vực đông cổ động viên tràn xuống đường cổ vũ. Vận động viên "
            "phải giữ đều tay lái ở vận tốc {vC} m/s trong {t2} giây để đảm bảo an toàn. "
            "Sau khi qua đám đông, vận động viên bóp phanh theo quy luật hàm bậc hai "
            "$v(t) = ct^2 + d$ $(m/s)$ để dừng đúng vạch dừng quy định ($v_B = 0$)."
        ),
        "obstacle_name": "khu vực có đông cổ động viên tràn xuống đường",
        "vehicle": "vận động viên",
        "start": "vị trí mốc A",
        "end": "đích B",
    },
    {
        "intro": (
            "Một đoàn tàu điện du lịch đang chạy tốc độ {v0_kmh} km/h qua khu vực A. "
            "Để dừng tại điểm trả khách B cách đó {AB} m, tàu giảm tốc theo hàm "
            "$v(t) = at + b$ $(m/s)$, với $t$ tính theo giây. Được {t1} giây, tàu tiến vào "
            "khu vực quan sát thú quý hiếm cách đó {gap} m. Tàu giữ vận tốc chậm {vC} m/s "
            "trong {t2} giây để du khách kịp chụp ảnh mà không làm thú hoảng sợ. Ra khỏi "
            "khu vực này, tàu tiếp tục giảm tốc theo hàm bậc hai $v(t) = ct^2 + d$ $(m/s)$ "
            "và dừng hẳn tại B ($v_B = 0$)."
        ),
        "obstacle_name": "khu vực quan sát thú quý hiếm",
        "vehicle": "tàu",
        "start": "vị trí A",
        "end": "điểm trả khách B",
    },
    {
        "intro": (
            "Một chiếc xe chữa cháy đang chạy tốc độ {v0_kmh} km/h tại vị trí A trong "
            "buổi diễn tập. Mục tiêu là dừng tại vị trí B cách đó {AB} m để triển khai "
            "vòi rồng. Xe giảm tốc theo hàm $v(t) = at + b$ $(m/s)$, với $t$ tính theo "
            "giây. Được {t1} giây thì gặp đoạn đường có khói mù bao phủ cách đó {gap} m. "
            "Tài xế giữ vận tốc {vC} m/s trong {t2} giây để đảm bảo tầm nhìn. Sau khi "
            "thoát khỏi khói, xe phanh mạnh theo hàm bậc hai $v(t) = ct^2 + d$ $(m/s)$ "
            "để dừng chính xác tại điểm B ($v_B = 0$)."
        ),
        "obstacle_name": "đoạn đường có khói mù bao phủ",
        "vehicle": "xe chữa cháy",
        "start": "vị trí A",
        "end": "điểm B",
    },
]


# ==============================================================================
# MATH ENGINE
# ==============================================================================

class CarBrakingQuestion:

    def generate_parameters(self) -> Dict[str, Any]:
        """Random bộ số đảm bảo kết quả nguyên. Dùng int thuần túy cho tốc độ."""
        # Pre-filter valid (v0, vC, t1) combos where AC is integer
        # AC = (vC - v0) * t1 / 2 + v0 * t1 = t1 * (vC + v0) / 2
        # AC integer <=> t1 * (vC + v0) % 2 == 0
        V0_POOL = [10, 15, 20, 25]
        VC_POOL = [5, 8, 10, 12, 15]
        T1_POOL = [10, 15, 20, 25, 30]
        T2_POOL = [10, 15, 18, 20, 22, 24, 25, 30]

        for _ in range(500):
            v0 = random.choice(V0_POOL)
            vC = random.choice(VC_POOL)
            if vC >= v0:
                continue

            # AC = t1 * (v0 + vC) / 2, need AC integer
            valid_t1 = [t for t in T1_POOL if (t * (v0 + vC)) % 2 == 0]
            if not valid_t1:
                continue
            t1 = random.choice(valid_t1)
            AC = t1 * (v0 + vC) // 2  # always integer by filter

            # Phase 2
            t2 = random.choice(T2_POOL)
            CE = vC * t2  # always integer (both int)

            if CE <= 30:
                continue
            gap = random.randint(30, min(CE - 10, 100))
            DE = CE - gap

            # Phase 3: EB must make tB = 3*EB/(2*vC) integer
            # => EB must be divisible by 2*vC/3
            # => 3*EB must be divisible by 2*vC
            # => EB = 2*vC*k/3 for integer k, and EB integer => vC*k divisible by 3... too complex
            # Simpler: tB integer => EB = 2*vC*tB/3, so need 2*vC*tB % 3 == 0
            # Pick tB directly, filter for EB integer
            tB_pool = list(range(10, 120))
            random.shuffle(tB_pool)
            found = False
            for tB in tB_pool:
                if (2 * vC * tB) % 3 != 0:
                    continue
                EB = 2 * vC * tB // 3
                if EB < 50:
                    continue
                found = True
                break
            if not found:
                continue

            AB = AC + CE + EB
            AD = AC + gap
            v0_kmh = v0 * 18 // 5
            total_time = t1 + t2 + tB

            # a = (vC - v0) / t1 as Fraction
            a = Fraction(vC - v0, t1)
            c_coeff = Fraction(-vC, tB**2)

            return {
                "v0": Fraction(v0), "v0_kmh": v0_kmh, "vC": Fraction(vC),
                "t1": Fraction(t1), "t2": Fraction(t2), "gap": Fraction(gap),
                "a": a, "b": Fraction(v0),
                "AC": Fraction(AC), "CE": Fraction(CE), "DE": Fraction(DE), "AD": Fraction(AD),
                "EB": Fraction(EB), "tB": Fraction(tB), "AB": Fraction(AB),
                "c_coeff": c_coeff, "d_coeff": Fraction(vC),
                "total_time": Fraction(total_time),
            }
        raise ValueError("Could not find valid parameters after 500 attempts")

    def generate(self, q_num: int) -> Tuple[str, str]:
        ctx = random.choice(CONTEXTS)
        p = self.generate_parameters()

        v0 = p["v0"]; v0_kmh = p["v0_kmh"]; vC = p["vC"]
        t1 = p["t1"]; t2 = p["t2"]; gap = p["gap"]
        a = p["a"]; b = p["b"]
        AC = p["AC"]; CE = p["CE"]; DE = p["DE"]; AD = p["AD"]
        EB = p["EB"]; tB = p["tB"]; AB = p["AB"]
        c_coeff = p["c_coeff"]; d_coeff = p["d_coeff"]
        total_time = p["total_time"]

        # --- Decide True/False ---
        TF = [random.choice([True, False]) for _ in range(4)]

        # a) b = v0
        correct_b = safe_int(b)
        if TF[0]:
            shown_b = correct_b
        else:
            shown_b = correct_b + random.choice([5, -5, 10])
        stmt_a_text = f"a) Giá trị của tham số $b$ trong biểu thức vận tốc giai đoạn đầu là ${shown_b}$."
        stmt_a = ("*" if TF[0] else "") + stmt_a_text

        # b) Quãng đường thực tế obstacle = DE
        correct_DE = safe_int(DE)
        if TF[1]:
            shown_b_val = correct_DE
        else:
            wrong_pool = [safe_int(CE), correct_DE + 20, correct_DE - 20, correct_DE + 30]
            wrong_pool = [w for w in wrong_pool if w != correct_DE and w > 0]
            shown_b_val = random.choice(wrong_pool)
        stmt_b_text = (
            f"b) Quãng đường thực tế của {ctx['obstacle_name']} "
            f"dài ${shown_b_val}$ m."
        )
        stmt_b = ("*" if TF[1] else "") + stmt_b_text

        # c) Quãng đường từ A đến vùng obstacle = AD
        correct_AD = safe_int(AD)
        if TF[2]:
            shown_c_val = correct_AD
        else:
            wrong_pool = [correct_AD + 10, correct_AD - 10, correct_AD + 20, correct_AD - 15]
            wrong_pool = [w for w in wrong_pool if w != correct_AD and w > 0]
            shown_c_val = random.choice(wrong_pool)
        stmt_c_text = (
            f"c) Quãng đường tính từ {ctx['start']} đến khi {ctx['vehicle']} "
            f"bắt đầu tiếp xúc với {ctx['obstacle_name']} là ${shown_c_val}$ m."
        )
        stmt_c = ("*" if TF[2] else "") + stmt_c_text

        # d) Tổng thời gian = total_time
        correct_T = safe_int(total_time)
        if TF[3]:
            shown_d_val = correct_T
        else:
            shown_d_val = correct_T + random.choice([6, -6, 8, -14])
        stmt_d_text = (
            f"d) Tổng thời gian kể từ lúc {ctx['vehicle']} bắt đầu giảm tốc "
            f"tại A cho đến khi dừng hẳn tại {ctx['end']} là ${shown_d_val}$ giây."
        )
        stmt_d = ("*" if TF[3] else "") + stmt_d_text

        # --- Build question ---
        intro_filled = ctx["intro"].format(
            v0_kmh=v0_kmh, AB=safe_int(AB), t1=safe_int(t1), gap=safe_int(gap),
            vC=safe_int(vC), t2=safe_int(t2),
        )

        question_text = (
            f"{intro_filled}\n\n"
            f"{stmt_a}\n\n"
            f"{stmt_b}\n\n"
            f"{stmt_c}\n\n"
            f"{stmt_d}"
        )

        # --- Build solution ---
        ans = ["Đúng" if t else "Sai" for t in TF]

        solution_text = (
            f"Lời giải\n\n"
            f"Đổi: ${v0_kmh}$ km/h $= {safe_int(v0)}$ m/s.\n\n"
            # Phase 1
            f"a) {ans[0]}. Tại $t = 0$: $v(0) = a \\cdot 0 + b = b$. "
            f"Mà $v(0) = {safe_int(v0)}$ m/s nên $b = {safe_int(b)}$.\n\n"
            f"Vận tốc sau ${safe_int(t1)}$ giây: $v({safe_int(t1)}) = {safe_int(vC)}$ m/s "
            f"$\\Rightarrow a \\cdot {safe_int(t1)} + {safe_int(b)} = {safe_int(vC)}$ "
            f"$\\Rightarrow a = {frac_str(a)}$.\n\n"
            f"Quãng đường giai đoạn 1 (A$\\to$C): "
            f"$AC = \\displaystyle\\int_0^{{{safe_int(t1)}}} v(t) \\, dt = \\int_0^{{{safe_int(t1)}}} "
            f"\\left({frac_str(a)}t + {safe_int(b)}\\right) dt = {safe_int(AC)}$ (m).\n\n"
            # Phase 2
            f"b) {ans[1]}. Giai đoạn 2: vận tốc hằng ${safe_int(vC)}$ m/s trong ${safe_int(t2)}$ giây.\n\n"
            f"$CE = {safe_int(vC)} \\cdot {safe_int(t2)} = {safe_int(CE)}$ (m).\n\n"
            #f"Tuy nhiên, khoảng cách từ vị trí kết thúc giai đoạn 1 (C) đến đầu {ctx['obstacle_name']} (D) "
            #f"là ${safe_int(gap)}$ m.\n\n"
            #f"Vậy quãng đường thực tế của {ctx['obstacle_name']}: "
            f"$DE = CE - {safe_int(gap)} = {safe_int(CE)} - {safe_int(gap)} = {safe_int(DE)}$ (m).\n\n"
            #f"$DE = CE - {safe_int(gap)} = {safe_int(CE)} - {safe_int(gap)} = {safe_int(DE)}$ (m).\n\n"
            # Phase 2 - distance A to D
            f"c) {ans[2]}. $v_C = {safe_int(vC)}\\,(\\text{{m/s}})=v({safe_int(t1)})=a\\cdot {safe_int(t1)}+b,\\ b={safe_int(b)} "
            f"\\Rightarrow a={frac_str(a)}$.\n\n"
            f"$\\Rightarrow v(t)={frac_str(a)}t+{safe_int(b)}\\,(\\text{{m/s}}),\\ A\\to C "
            f"\\Rightarrow AC=\\displaystyle\\int_0^{{{safe_int(t1)}}}v(t)\\,dt="
            f"\\displaystyle\\int_0^{{{safe_int(t1)}}}\\left({frac_str(a)}t+{safe_int(b)}\\right)dt={safe_int(AC)}\\,(\\text{{m}})$.\n\n"
            f"$\\Rightarrow AD=AC+CD={safe_int(AC)}+{safe_int(gap)}={safe_int(AD)}\\,(\\text{{m}})$.\n\n"
            # Phase 3
            f"d) {ans[3]}. Gọi khoảng thời gian đi từ E $\\to$ B là $t_B$, khi đó "
            f"$EB={safe_int(AB)}-{safe_int(AC)}-{safe_int(CE)}={safe_int(EB)}\\,(\\text{{m}})$.\n\n"
            f"$t=0\\Rightarrow c\\cdot 0^2+d={safe_int(vC)}\\Rightarrow d={safe_int(vC)}$.\n\n"
            f"$t=t_B\\Rightarrow c\\cdot t_B^2+d=0\\Rightarrow c=-\\dfrac{{d}}{{t_B^2}}=-\\dfrac{{{safe_int(vC)}}}{{t_B^2}}$.\n\n"
            f"$EB=\\displaystyle\\int_0^{{t_B}}(ct^2+d)\\,dt\\quad (ct^2+d\\ge 0)$.\n\n"
            f"$\\Rightarrow {safe_int(EB)}=\\displaystyle\\int_0^{{t_B}}\\left(-\\dfrac{{{safe_int(vC)}}}{{t_B^2}}t^2+{safe_int(vC)}\\right)dt$.\n\n"
            f"$\\Leftrightarrow {safe_int(EB)}=\\left.\\left(-\\dfrac{{{safe_int(vC)}}}{{t_B^2}}\\cdot\\dfrac{{t^3}}{{3}}+{safe_int(vC)}t\\right)\\right|_0^{{t_B}}="
            f"-\\dfrac{{{safe_int(vC)}t_B}}{{3}}+{safe_int(vC)}t_B=\\dfrac{{2\\cdot {safe_int(vC)}\\cdot t_B}}{{3}}$.\n\n"
            f"$\\Rightarrow t_B=\\dfrac{{3\\cdot {safe_int(EB)}}}{{2\\cdot {safe_int(vC)}}}={safe_int(tB)}\\,(\\text{{s}})$.\n\n"
            f"Khoảng thời gian A $\\to$ B là: ${safe_int(t1)}+{safe_int(t2)}+{safe_int(tB)}={safe_int(total_time)}$ (s)."
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

    gen = CarBrakingQuestion()
    qs = []
    for i in range(num_q):
        qs.append(gen.generate(i + 1))

    latex_content = create_document(qs)
    out_file = os.path.join(os.path.dirname(__file__), "car_braking_questions.tex")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(latex_content)
    logging.info(f"Saved to {out_file}")
