import math
import os
import sys
import random
from fractions import Fraction
from typing import Tuple

CONTEXTS = [
    {
        "space": "không gian studio 3D $Oxyz$",
        "A_desc": "vị trí camera",
        "S_desc": "quả cầu LED",
        "I_desc": "tâm điều khiển",
        "plane_desc": "vách kính màn hình",
        "a_stmt": "Vị trí đặt camera $A$ nằm an toàn ngoài quả cầu LED $(S)$.",
        "b_stmt": "Trục chiếu sáng $IA$ tạo với vách kính $(\\alpha)$ một góc",
        "c_stmt": "Vùng khói hiệu ứng hình nón đỉnh $I$ có đáy là giao của vách kính $(\\alpha)$ và quả cầu $(S)$ có thể tích cần bơm là",
        "d_stmt": "Vách kính $(\\alpha)$ cắt quả cầu $(S)$ theo một quỹ đạo tròn $(C)$. Cảm biến lấy nét đặt tại điểm $M_1(x_1; y_1; z_1)$ thuộc quỹ đạo $(C)$ sao cho khoảng cách từ $M_1$ đến camera $A$ nhỏ nhất là $m$ và cảm biến đo chiều sâu đặt tại điểm $M_2(x_2; y_2; z_2)$ thuộc quỹ đạo $(C)$ sao cho khoảng cách từ $M_2$ đến $A$ lớn nhất là $M$. Khi đó mã hiệu chuẩn tiêu cự phần mềm là $x_1 - 2x_2 + y_1 - 3y_2 + m + M = $"
    },
    {
        "space": "không gian giả lập 3D $Oxyz$ của hệ thống robot phẫu thuật",
        "A_desc": "vị trí đầu phát tia laser",
        "S_desc": "khối u có màng bọc dạng mặt cầu",
        "I_desc": "tâm",
        "plane_desc": "mặt phẳng mô phân cách",
        "a_stmt": "Vị trí đầu phát tia laser $A$ nằm ở khoảng cách an toàn, hoàn toàn bên ngoài khối u $(S)$ (để tránh va chạm vật lý trước khi kích hoạt).",
        "b_stmt": "Trục chiếu tia laser $IA$ tạo với mặt phẳng mô phân cách $(\\alpha)$ một góc",
        "c_stmt": "Vùng mô cần xử lý nhiệt có dạng khối nón với đỉnh là tâm $I$ và đáy là phần vết cắt giao tuyến của mặt phẳng $(\\alpha)$ và khối u $(S)$ có thể tích không gian bằng",
        "d_stmt": "Mặt phẳng phân cách $(\\alpha)$ cắt khối u $(S)$ tạo thành một đường rạch vòng tròn $(C)$. Mũi dao robot được lập trình di chuyển đến điểm $M_1(x_1; y_1; z_1)$ thuộc đường rạch $(C)$ sao cho khoảng cách truyền tia laser từ $A$ là ngắn nhất (cường độ mạnh nhất, khoảng cách đạt giá trị $m$). Sau đó, mũi dao chuyển đến điểm $M_2(x_2; y_2; z_2)$ thuộc $(C)$ sao cho khoảng cách từ $A$ là lớn nhất (cường độ yếu nhất, khoảng cách đạt giá trị $M$). Khi đó, mã sinh trắc học để hệ thống duyệt lệnh cắt là: $x_1 - 2x_2 + y_1 - 3y_2 + m + M = $"
    },
    {
        "space": "không gian định vị thủy âm $Oxyz$ dưới đáy đại dương", 
        "A_desc": "vị trí của trạm phát sóng Sonar trên Tàu ngầm mẹ",
        "S_desc": "màng chắn năng lượng dạng khối cầu",
        "I_desc": "tâm",
        "plane_desc": "mặt phẳng rạn san hô dốc",
        "a_stmt": "Vị trí Tàu ngầm mẹ $A$ đang neo đậu an toàn, nằm hoàn toàn bên ngoài màng chắn năng lượng $(S)$.",
        "b_stmt": "Trục truyền tín hiệu sóng âm $IA$ tạo với mặt phẳng rạn san hô $(\\alpha)$ một góc",
        "c_stmt": "Vùng sinh thái lấy mẫu có dạng hình nón với đỉnh là tâm trạm $I$ và đáy là phần miệng hang (giao tuyến của rạn san hô $(\\alpha)$ và màng chắn $(S)$) có thể tích không gian chứa nước bằng",
        "d_stmt": "Rạn san hô $(\\alpha)$ cắt màng chắn $(S)$ tạo thành một đường hầm sinh thái hình vòng tròn $(C)$. Một robot lặn (ROV) di chuyển dọc theo vòng tròn $(C)$ này để ghi hình. Tại điểm $M_1(x_1; y_1; z_1)$ thuộc $(C)$, tín hiệu từ ROV truyền về Tàu mẹ $A$ là mạnh nhất (khoảng cách đạt giá trị nhỏ nhất là $m$). Tại điểm $M_2(x_2; y_2; z_2)$ thuộc $(C)$, tín hiệu truyền về Tàu mẹ $A$ là yếu nhất (khoảng cách đạt giá trị lớn nhất là $M$). Khi đó, mã khóa bảo mật để đồng bộ dữ liệu hình ảnh về tàu mẹ là: $x_1 - 2x_2 + y_1 - 3y_2 + m + M = $"
    },
    {
        "space": "không gian thiết lập gian hàng trải nghiệm 3D $Oxyz$",
        "A_desc": "vị trí máy chiếu holographic",
        "S_desc": "vùng không gian tạo hiệu ứng khói sương",
        "I_desc": "tâm phát",
        "plane_desc": "vách ngăn acrylic trong suốt",
        "a_stmt": "Vị trí đặt máy chiếu $A$ nằm an toàn bên ngoài vùng hiệu ứng khói sương $(S)$.",
        "b_stmt": "Trục định hướng ánh sáng $IA$ tạo với vách ngăn acrylic $(\\alpha)$ một góc",
        "c_stmt": "Vùng chiếu sáng điểm nhấn là một hình nón có đỉnh $I$ và đáy là giao tuyến của vách ngăn acrylic $(\\alpha)$ cắt vùng khói sương $(S)$. Thể tích vùng chiếu sáng này được thiết lập bằng",
        "d_stmt": "Vách ngăn $(\\alpha)$ giao cắt với vùng hiệu ứng $(S)$ tạo thành một đường ray LED tròn $(C)$. Kỹ thuật viên lắp đặt hệ thống tracking trên đường ray này: một module cảm biến chuyển động được cố định tại điểm $M_1(x_1; y_1; z_1)$ thuộc $(C)$ sao cho khoảng cách từ module này đến máy chiếu $A$ là ngắn nhất (đạt giá trị $m$), và một module camera góc rộng được lắp tại điểm $M_2(x_2; y_2; z_2)$ thuộc $(C)$ sao cho khoảng cách đến máy chiếu $A$ là xa nhất (đạt giá trị $M$). Khi đó, tham số cấu hình đồng bộ không gian trên phần mềm quản lý là: $x_1 - 2x_2 + y_1 - 3y_2 + m + M = $"
    },
    {
        "space": "phần mềm thiết kế 3D với hệ trục tọa độ $Oxyz$",
        "A_desc": "vị trí nguồn sáng chính (Directional Light)",
        "S_desc": "khối cầu trang trí dạng bong bóng",
        "I_desc": "tâm",
        "plane_desc": "mặt phẳng phông nền pastel",
        "a_stmt": "Vị trí nguồn sáng $A$ nằm an toàn bên ngoài khối cầu bong bóng $(S)$ (tránh lỗi xuyên sáng khi render).",
        "b_stmt": "Trục tia sáng $IA$ tạo với phông nền $(\\alpha)$ một góc",
        "c_stmt": "Vùng hiệu ứng ánh sáng (Volumetric light) hình nón có đỉnh là tâm $I$ và đáy là đường tròn giao tuyến của phông nền $(\\alpha)$ với khối cầu bong bóng $(S)$ có thể tích không gian bằng",
        "d_stmt": "Phông nền $(\\alpha)$ cắt khối cầu bong bóng $(S)$ tạo thành một vệt sáng hình tròn $(C)$. Phần mềm tự động đặt một keyframe animation tại điểm $M_1(x_1; y_1; z_1)$ di chuyển trên vệt sáng $(C)$ sao cho khoảng cách đến nguồn sáng $A$ là ngắn nhất (đạt giá trị $m$). Một keyframe khác được đặt tại $M_2(x_2; y_2; z_2)$ thuộc $(C)$ sao cho khoảng cách đến $A$ là xa nhất (đạt giá trị $M$). Khi đó, mã kiểm tra tối ưu hóa khung hình có giá trị: $x_1 - 2x_2 + y_1 - 3y_2 + m + M = $"
    },
    {
        "space": "hệ thống định vị không gian $Oxyz$ của một khu vực khảo sát",
        "A_desc": "vị trí trạm điều khiển trung tâm",
        "S_desc": "khinh khí cầu quan trắc thời tiết có vùng từ trường bảo vệ dạng khối cầu",
        "I_desc": "tâm",
        "plane_desc": "mặt phẳng ranh giới quét radar",
        "a_stmt": "Vị trí trạm điều khiển $A$ nằm ở khoảng cách an toàn, hoàn toàn bên ngoài vùng từ trường $(S)$ của khinh khí cầu.",
        "b_stmt": "Hướng truyền tín hiệu thẳng $IA$ tạo với mặt phẳng ranh giới radar $(\\alpha)$ một góc",
        "c_stmt": "Vùng quét dữ liệu đa chiều hình nón có đỉnh là tâm $I$ và đáy là phần giao tuyến của mặt phẳng radar $(\\alpha)$ với vùng từ trường $(S)$ có thể tích không gian bằng",
        "d_stmt": "Mặt phẳng radar $(\\alpha)$ cắt vùng từ trường $(S)$ tạo thành một quỹ đạo bay hình tròn $(C)$ an toàn. Một drone số 1 được lập trình bay đến điểm $M_1(x_1; y_1; z_1)$ thuộc quỹ đạo $(C)$ sao cho khoảng cách truyền tín hiệu về trạm $A$ là ngắn nhất (đạt giá trị $m$). Một drone số 2 bay đến điểm $M_2(x_2; y_2; z_2)$ thuộc quỹ đạo $(C)$ sao cho khoảng cách về $A$ là lớn nhất (đạt giá trị $M$). Khi đó, mã đồng bộ hệ thống bay được phần mềm xác nhận là: $x_1 - 2x_2 + y_1 - 3y_2 + m + M = $"
    }
]

PRESETS = [
    ((-2, 6, 3), (0, 2, -3), 24, (1, 1, 0, 4)),
    ((8, 4, -5), (2, -2, 1), 24, (1, 1, 0, -4)),
    ((6, -10, 3), (0, 2, -3), 24, (1, 1, 0, 0)),
    ((-2, 6, 3), (0, 2, -3), 24, (1, 1, 0, -2)),
    ((2, -5, 7), (0, 1, 1), 25, (1, 1, 0, 3)),
    ((10, -6, 1), (2, 0, 1), 25, (2, 1, 0, 1)),
    ((8, 4, -5), (2, -2, 1), 25, (1, 1, 0, 0)),
    ((4, -6, 2), (1, 3, -2), 30, (1, 1, 0, 0)),
    ((3, -8, 1), (0, 3, 1), 36, (1, 1, 0, 3)),
    ((-10, -10, -3), (-1, 2, 0), 6, (2, 1, 0, 0)),
    ((-9, -2, -7), (1, 3, -1), 6, (2, 1, 0, 0)),
    ((-10, -3, -6), (-1, 2, -2), 8, (1, 1, 0, 1)),
    ((-10, -3, 1), (-1, 0, 1), 8, (1, 1, 0, 1)),
    ((-10, -9, -1), (-1, 2, -1), 10, (1, -1, 0, -1)),
    ((-10, -9, 1), (0, 3, 1), 10, (1, -1, 0, -1)),
    ((-10, -10, -3), (-1, 3, -3), 10, (1, 1, 0, 2)),
    ((-10, -4, -2), (0, 0, -2), 10, (1, 1, 0, 2)),
    ((-10, -7, 0), (0, 3, 0), 10, (1, 2, 0, -1)),
    ((-10, -7, -1), (0, 3, -1), 10, (1, 2, 0, -1)),
    ((-10, -10, -1), (1, 3, -1), 10, (2, 1, 0, 0)),
    ((-10, -10, 1), (1, 3, 1), 10, (2, 1, 0, 0)),
    ((-10, -10, -1), (-1, 1, -1), 16, (1, -1, 0, -2)),
    ((-10, -10, -3), (-1, 1, -3), 16, (1, -1, 0, -2)),
    ((-10, 9, 2), (-1, 0, -3), 16, (1, -1, 0, 1)),
    ((-7, 10, -7), (1, 2, -1), 16, (1, -1, 0, 1)),
    ((-5, -9, -7), (0, 1, -1), 16, (1, 2, 0, -2)),
    ((-5, -9, -7), (0, 1, -2), 16, (1, 2, 0, -2)),
    ((-10, -5, -7), (0, 0, 1), 16, (2, 1, 0, 0)),
    ((-9, -2, -7), (-1, 2, -1), 16, (2, 1, 0, 0)),
    ((-9, 10, -7), (1, 0, 0), 18, (1, -1, 0, -3)),
    ((-9, 10, -7), (1, 0, -2), 18, (1, -1, 0, -3)),
    ((-10, -7, 0), (1, 2, 0), 18, (1, -1, 0, 1)),
    ((-7, 10, -7), (0, 3, 1), 18, (1, -1, 0, 1)),
    ((-9, -10, -7), (1, 0, 1), 18, (1, 1, 0, -3)),
    ((-10, -7, -7), (-1, 2, 0), 18, (1, 1, 0, -3)),
    ((-10, -5, -7), (0, 1, 1), 18, (1, 1, 0, -1)),
    ((-10, -7, -7), (0, 3, -2), 18, (1, 1, 0, -1)),
    ((-10, -3, -7), (0, 3, 1), 20, (1, -1, 0, -1)),
    ((-10, -7, 0), (-1, 0, 0), 20, (1, -1, 0, -1)),
    ((-10, -9, 0), (0, 3, 0), 20, (1, -1, 0, 1)),
    ((-10, -9, -3), (0, 3, -3), 20, (1, -1, 0, 1)),
    ((-10, 3, -5), (0, 1, -1), 24, (1, 1, 0, -3)),
    ((-10, -1, -7), (0, 3, -1), 24, (1, 1, 0, -3)),
    ((-10, 0, 7), (1, 1, -2), 25, (1, -1, 0, 4)),
    ((-8, 10, -7), (-1, 3, -1), 25, (1, -1, 0, 4)),
    ((-9, -10, 3), (1, 0, -3), 25, (1, 1, 0, -1)),
    ((-10, -7, 3), (-1, 2, -3), 25, (1, 1, 0, -1)),
    ((-10, -9, -7), (-1, 0, -1), 25, (1, 1, 0, 1)),
    ((-10, -1, -5), (1, 2, 1), 25, (1, 1, 0, 1)),
    ((-10, -9, 7), (0, 1, -3), 30, (2, 1, 0, -1)),
    ((-9, -6, 7), (-1, 3, -3), 30, (2, 1, 0, -1)),
    ((-10, -9, -1), (0, 3, -1), 40, (1, -1, 0, -1)),
    ((-10, -9, -1), (-1, 2, -1), 40, (1, -1, 0, -1)),
    ((-10, -5, 7), (1, 0, -1), 48, (1, -1, 0, -1)),
    ((-10, -7, 7), (1, 0, -2), 48, (1, -1, 0, -1)),
    ((-10, 6, -6), (0, 0, 0), 49, (1, 1, 0, -4)),
    ((-10, 6, -5), (0, 0, 1), 49, (1, 1, 0, -4)),
    ((-10, -4, -7), (0, 0, 0), 50, (1, -1, 0, -2)),
    ((-10, -4, -7), (1, 1, 1), 50, (1, -1, 0, -2)),
]

def fmt_coord(v):
    """Format a number: convert float to int if it's a whole number."""
    if isinstance(v, float) and v == int(v):
        return int(v)
    return v

def fmt_point(p):
    return f"({fmt_coord(p[0])}; {fmt_coord(p[1])}; {fmt_coord(p[2])})"

def sqrt_tex(n):
    if n == 0: return "0"
    root = int(math.sqrt(n))
    if root * root == n:
        return str(root)
    a, b = 1, n
    for p in [2, 3, 5, 7, 11, 13]:
        while b % (p*p) == 0:
            a *= p
            b //= (p*p)
    if b == 1: return str(a)
    if a == 1: return rf"\sqrt{{{b}}}"
    return rf"{a}\sqrt{{{b}}}"

def format_plane(a, b, c, d):
    terms = []
    if a == 1: terms.append("x")
    elif a == -1: terms.append("-x")
    elif a != 0: terms.append(f"{a}x")
    if b == 1: terms.append("+y" if terms else "y")
    elif b == -1: terms.append("-y")
    elif b != 0: terms.append(f"{'+' if b>0 and terms else ''}{b}y")
    if c == 1: terms.append("+z" if terms else "z")
    elif c == -1: terms.append("-z")
    elif c != 0: terms.append(f"{'+' if c>0 and terms else ''}{c}z")
    
    d_str = ""
    if d > 0: d_str = f"+{d}"
    elif d < 0: d_str = f"{d}"
    
    return "".join(terms) + d_str + " = 0"

def format_volume(r_sq, h_num, h_den_sq):
    num = r_sq * h_num
    den = 3 * h_den_sq
    f = Fraction(num, den)
    a, b = 1, h_den_sq
    for p in [2, 3, 5, 7, 11, 13]:
        while b % (p*p) == 0:
            a *= p
            b //= (p*p)
    num2 = f.numerator * a
    den2 = f.denominator
    f2 = Fraction(num2, den2)
    res_num = f2.numerator
    res_den = f2.denominator
    
    top = r"\pi" if res_num == 1 else f"{res_num}\\pi"
    if b > 1: top += rf"\sqrt{{{b}}}"
    if res_den == 1: return top
    return rf"\frac{{{top}}}{{{res_den}}}"

def format_sin(num, den_sq):
    if num == 0:
        return "0"
    f = Fraction(num**2, den_sq)
    N = f.numerator
    D = f.denominator
    
    A, u = 1, N
    for p in [2, 3, 5, 7, 11, 13]:
        while u % (p*p) == 0:
            A *= p
            u //= (p*p)
            
    B, v = 1, D
    for p in [2, 3, 5, 7, 11, 13]:
        while v % (p*p) == 0:
            B *= p
            v //= (p*p)
            
    if u == 1: top = str(A)
    elif A == 1: top = rf"\sqrt{{{u}}}"
    else: top = rf"{A}\sqrt{{{u}}}"
    
    if v == 1: bot = str(B)
    elif B == 1: bot = rf"\sqrt{{{v}}}"
    else: bot = rf"{B}\sqrt{{{v}}}"
    
    if bot == "1": return top
    return rf"\frac{{{top}}}{{{bot}}}"

def generate_question(context_idx=None) -> Tuple[str, str, str]:
    if context_idx is None:
        context = random.choice(CONTEXTS)
    else:
        context = CONTEXTS[context_idx % len(CONTEXTS)]
        
    A, I, R_sq, plane = random.choice(PRESETS)
    pa, pb, pc, pd = plane
    R_tex = sqrt_tex(R_sq)
    plane_str = format_plane(pa, pb, pc, pd)
    
    den_sq = pa**2 + pb**2 + pc**2
    IA_vec = (A[0]-I[0], A[1]-I[1], A[2]-I[2])
    IA_sq = sum(x**2 for x in IA_vec)
    
    h_num = abs(pa*I[0] + pb*I[1] + pc*I[2] + pd)
    h_sq = h_num**2 / den_sq
    r_sq = round(R_sq - h_sq)
    
    V_tex = format_volume(r_sq, h_num, den_sq)
    
    t_K = -(pa*I[0] + pb*I[1] + pc*I[2] + pd) / den_sq
    K = (I[0] + pa*t_K, I[1] + pb*t_K, I[2] + pc*t_K)
    
    t_H = -(pa*A[0] + pb*A[1] + pc*A[2] + pd) / den_sq
    H = (A[0] + pa*t_H, A[1] + pb*t_H, A[2] + pc*t_H)
    
    HK_vec = (K[0]-H[0], K[1]-H[1], K[2]-H[2])
    HK_sq = sum(x**2 for x in HK_vec)
    HK = math.sqrt(HK_sq)
    r = math.sqrt(r_sq)
    scale = r / HK
    
    M1 = (round(K[0] + scale*(H[0]-K[0])), round(K[1] + scale*(H[1]-K[1])), round(K[2] + scale*(H[2]-K[2])))
    M2 = (round(K[0] - scale*(H[0]-K[0])), round(K[1] - scale*(H[1]-K[1])), round(K[2] - scale*(H[2]-K[2])))
    
    AH_sq = round(sum((A[i]-H[i])**2 for i in range(3)))
    HX_min = abs(HK - r)
    HX_max = HK + r
    m_sq = round(AH_sq + HX_min**2)
    M_sq = round(AH_sq + HX_max**2)
    
    m_tex = sqrt_tex(m_sq)
    M_tex = sqrt_tex(M_sq)
    m_val = math.sqrt(m_sq)
    M_val = math.sqrt(M_sq)
    
    part1 = M1[0] - 2*M2[0] + M1[1] - 3*M2[1]
    ans_d_exact = part1 + m_val + M_val
    ans_d_rounded = round(ans_d_exact, 1)
    
    # Statement A
    a_correct = random.choice([True, False])
    stmt_a_text = context['a_stmt']
    if not a_correct:
        stmt_a_text = stmt_a_text.replace("ngoài", "trong").replace("bên ngoài", "bên trong")
    stmt_a = rf"{'*' if a_correct else ''}a) {stmt_a_text}"
        
    def fmt_sq(v):
        if v < 0:
            return f"({v})^2"
        return f"{v}^2"
    
    sol_a = rf"""a) {'Đúng' if a_correct else 'Sai'}.
Ta tính khoảng cách $IA$:
$\overrightarrow{{IA}} = {fmt_point(IA_vec)} \Rightarrow IA = \sqrt{{{fmt_sq(IA_vec[0])} + {fmt_sq(IA_vec[1])} + {fmt_sq(IA_vec[2])}}} = \sqrt{{{IA_sq}}} = {sqrt_tex(IA_sq)}$.
Bán kính mặt cầu là $R = {R_tex} = \sqrt{{{R_sq}}}$.
Vì $IA > R$ (do $\sqrt{{{IA_sq}}} > \sqrt{{{R_sq}}}$) nên điểm $A$ nằm hoàn toàn bên ngoài mặt cầu $(S)$."""
    
    # Statement B
    b_correct = random.choice([True, False])
    dot_IA_n = pa*IA_vec[0] + pb*IA_vec[1] + pc*IA_vec[2]
    num_sin = abs(dot_IA_n)
    den_sin_sq = IA_sq * den_sq
    sin_val = num_sin / math.sqrt(den_sin_sq)
    angle_deg = math.degrees(math.asin(sin_val))
    angle_deg_r2 = round(angle_deg, 2)
    
    sin_tex = format_sin(num_sin, den_sin_sq)
    b_is_true = False
    if b_correct:
        stmt_b_text = rf"{context['b_stmt']} ${angle_deg_r2}^\circ$ (làm tròn đến $2$ chữ số thập phân)."
        b_is_true = True
    else:
        wrong_angle = round(angle_deg + random.choice([-15, -10, -5, 5, 10, 15, 20, 25, 30, 45 - angle_deg]), 2)
        if wrong_angle <= 0: wrong_angle = round(angle_deg + 15, 2)
        stmt_b_text = rf"{context['b_stmt']} ${wrong_angle}^\circ$ (làm tròn đến $2$ chữ số thập phân)."
    stmt_b = rf"{'*' if b_is_true else ''}b) {stmt_b_text}"

    sol_b = rf"""b) {'Đúng' if b_is_true else 'Sai'}.
Đường thẳng $IA$ có vectơ chỉ phương $\overrightarrow{{IA}} = {fmt_point(IA_vec)}$, ta chọn $\vec{{u}} = {fmt_point(IA_vec)}$.
Mặt phẳng $(\alpha): {plane_str}$ có vectơ pháp tuyến $\vec{{n}} = {fmt_point((pa, pb, pc))}$.
Gọi $\phi$ là góc giữa trục $IA$ và mặt phẳng $(\alpha)$, ta có:
$\sin \phi = \frac{{|\vec{{u}} \cdot \vec{{n}}|}}{{|\vec{{u}}| \cdot |\vec{{n}}|}} = \frac{{|{pa} \cdot ({IA_vec[0]}) + {pb} \cdot ({IA_vec[1]}) + {pc} \cdot ({IA_vec[2]})|}}{{\sqrt{{{IA_sq}}} \cdot \sqrt{{{den_sq}}}}} = {sin_tex}$.
Vậy $\phi = \arcsin\left({sin_tex}\right) \approx {angle_deg_r2}^\circ$."""
    
    # Statement C
    c_correct = random.choice([True, False])
    stmt_c_text = rf"{context['c_stmt']} $5$."
    c_is_true = False 
    if c_correct:
        stmt_c_text = rf"{context['c_stmt']} ${V_tex}$."
        c_is_true = True
    stmt_c = rf"{'*' if c_is_true else ''}c) {stmt_c_text}"

    sol_c = rf"""c) {'Đúng' if c_is_true else 'Sai'}.
Chiều cao khối nón là khoảng cách từ tâm $I$ đến mặt phẳng đáy $(\alpha)$:
$h = d(I, \alpha) = \frac{{|{pa}({I[0]}) + {pb}({I[1]}) + {pc}({I[2]}) {f'+{pd}' if pd>0 else (f'{pd}' if pd<0 else '')}|}}{{\sqrt{{{den_sq}}}}} = \frac{{{h_num}}}{{\sqrt{{{den_sq}}}}}$.
Bán kính đường tròn đáy nón $r$ được tính theo định lý Pytago:
$r = \sqrt{{R^2 - h^2}} = \sqrt{{{R_sq} - {h_sq:g}}} = \sqrt{{{r_sq}}}$.
Thể tích khối nón là: $V = \frac{{1}}{{3}}\pi r^2 h = \frac{{1}}{{3}}\pi ({r_sq}) \left(\frac{{{h_num}}}{{\sqrt{{{den_sq}}}}}\right) = {V_tex}$."""
    
    # Statement D
    d_correct = random.choice([True, False])
    d_is_true = False
    if d_correct:
        stmt_d_text = rf"{context['d_stmt']} ${ans_d_rounded}$ (làm tròn đến $1$ chữ số thập phân)."
        d_is_true = True
    else:
        noise = random.choice([-3.2, -2.5, -1.8, -1.1, -0.7, 0.7, 1.1, 1.8, 2.5, 3.2])
        wrong_val = round(ans_d_rounded + noise, 1)
        stmt_d_text = rf"{context['d_stmt']} ${wrong_val}$ (làm tròn đến $1$ chữ số thập phân)."
    stmt_d = rf"{'*' if d_is_true else ''}d) {stmt_d_text}"

    sol_d = rf"""d) {'Đúng' if d_is_true else 'Sai'}.
Gọi $K$ là hình chiếu vuông góc của $I{fmt_point(I)}$ lên $(\alpha)$.
Đường thẳng qua $I$ vuông góc $(\alpha)$ có dạng $\heva{{x &= {I[0]} {'+' if pa>0 else ''}{pa}t \\ y &= {I[1]} {'+' if pb>0 else ''}{pb}t {rf'\\  z &= {I[2]} {chr(43) if pc>0 else ""}{pc}t' if pc != 0 else rf'\\  z &= {I[2]}'}}}$.
Thay vào $(\alpha) \Rightarrow t = {fmt_coord(t_K)}$. Do đó $K{fmt_point(K)}$.
Khoảng cách $K$ là tâm của đường tròn $(C)$, bán kính $(C)$ là $r = \sqrt{{{r_sq}}}$.
Tương tự, gọi $H$ là hình chiếu của $A{fmt_point(A)}$ lên $(\alpha)$.
Thay vào $(\alpha) \Rightarrow t = {fmt_coord(t_H)}$. Do đó $H{fmt_point(H)}$.
Khoảng cách $AH = \sqrt{{{AH_sq}}} = {sqrt_tex(AH_sq)}$.
Lấy điểm tuỳ ý $X \in (C)$, do $AH \perp (\alpha)$ nên tam giác $AHX$ vuông tại $H \Rightarrow AX^2 = AH^2 + HX^2$.
Do $AH$ không đổi, $AX$ đạt GTLN/GTNN khi $X$ là giao điểm của đường thẳng $HK$ với đường tròn $(C)$.
Ta có $\overrightarrow{{HK}} = {fmt_point(HK_vec)} \Rightarrow HK = {sqrt_tex(round(HK_sq))}$.
$\Rightarrow HX_{{min}} = |HK - r| = {sqrt_tex(round(HX_min**2))}$.
$\Rightarrow HX_{{max}} = HK + r = {sqrt_tex(round(HX_max**2))}$.
$\Rightarrow m = \sqrt{{AH^2 + HX_{{min}}^2}} = \sqrt{{{AH_sq} + {round(HX_min**2)}}} = {m_tex}$ (đạt tại điểm $M_1$).
$\Rightarrow M = \sqrt{{AH^2 + HX_{{max}}^2}} = \sqrt{{{AH_sq} + {round(HX_max**2)}}} = {M_tex}$ (đạt tại điểm $M_2$).
Hai điểm $M_1$ và $M_2$ nằm trên đường thẳng $HK$.
$\overrightarrow{{KM_1}} = \frac{{r}}{{HK}}\overrightarrow{{KH}} \Rightarrow M_1{fmt_point(M1)}$.
$\overrightarrow{{KM_2}} = -\frac{{r}}{{HK}}\overrightarrow{{KH}} \Rightarrow M_2{fmt_point(M2)}$.
Với $M_1{fmt_point(M1)}$ và $M_2{fmt_point(M2)}$, ta có: 
$x_1 - 2x_2 + y_1 - 3y_2 = {M1[0]} - 2({M2[0]}) + ({M1[1]}) - 3({M2[1]}) = {part1}$.
Vậy mã kiểm tra thu được là ${part1} + m + M = {part1} + {m_tex} + {M_tex} \approx {part1} + {round(m_val, 4)} + {round(M_val, 4)} \approx {ans_d_rounded}$."""
    
    stem = rf"Trong {context['space']}, cho {context['A_desc']} $A{fmt_point(A)}$, {context['S_desc']} $(S)$ có {context['I_desc']} $I{fmt_point(I)}$, bán kính bằng ${R_tex}$ và {context['plane_desc']} $(\alpha)$ có phương trình ${plane_str}$. Xét tính đúng/sai của các mệnh đề sau:"
    
    question = f"""{stem}

{stmt_a}

{stmt_b}

{stmt_c}

{stmt_d}"""

    solution = "\n\n".join([sol_a, sol_b, sol_c, sol_d])
    key = ", ".join(["Đ" if x else "S" for x in [a_correct, b_is_true, c_is_true, d_is_true]])
    
    return question, solution, key

def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    out_dir = os.path.dirname(os.path.abspath(__file__))
    
    content = ""
    keys = []
    
    for i in range(num_questions):
        q, s, k = generate_question(i % len(CONTEXTS))
        keys.append(k)
        content += rf"""Câu {i+1}: {q}

Lời giải:

{s}

"""

    template = r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath, amsfonts, amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\usepackage{tikz}
\usetikzlibrary{calc,angles,quotes}

\newcommand{\heva}[1]{\left\{\begin{aligned}#1\end{aligned}\right.}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)

    out_path = os.path.join(out_dir, "cau_2_questions.tex")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {out_path}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")

if __name__ == "__main__":
    main()
