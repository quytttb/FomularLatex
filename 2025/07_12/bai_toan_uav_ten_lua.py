
import math
import random
import sys
import os
from string import Template
from typing import Any, Dict, List
from fractions import Fraction

# ==================== RANDOM TEXT VARIANTS ====================

# Wording variants for the reference plane (mặt phẳng (Oxy)).
GROUND_SURFACES = [
    "mặt đất",
    "mặt sân",
    "mặt sàn",
    "mặt nền",
]

# Origin label variants (avoid clashes with existing point names like A, B, M).
ORIGIN_LABELS = ["O", "N", "P", "Q", "R", "S", "T"]

# ==================== CONFIGURATION & HELPERS ====================

def to_latex_num(value):
    """Format number to LaTeX string, using fractions if appropriate"""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        
        # Check if it's close to an integer
        if abs(value - round(value)) < 1e-9:
            return str(round(value))
            
        # Try fraction
        f = Fraction(value).limit_denominator(100)
        # If the error is small, accept it
        if abs(float(f) - value) < 1e-9:
            if f.denominator == 1:
                return str(f.numerator)
            # Handle negative sign for fraction
            if f.numerator < 0:
                 return f"-\\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"
            return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"
            
    return format_vn_number(value)

def format_vn_number(value, precision=2):
    """Format number for Vietnamese locale (comma as decimal separator)"""
    if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
        return str(int(value))
    s = f"{value:.{precision}f}"
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s.replace('.', ',')

def format_coord(x, y, z):
    """Format coordinate tuple"""
    return f"({to_latex_num(x)}; {to_latex_num(y)}; {to_latex_num(z)})"

def create_latex_document(content):
    return r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage{enumitem}
\begin{document}
""" + content + r"\end{document}"

# ==================== TEMPLATES ====================

TEMPLATE_Q = Template(
    r"""
Câu ${idx}: Trong không gian với hệ trục tọa độ \(${origin_label}xyz\), xét mô hình phòng không như sau: Rađa đặt tại gốc tọa độ \(${origin_label}(0;0;0)\), tên lửa phòng không đặt tại điểm \(A${coord_A}\); mỗi đơn vị tương ứng với ${scale}m; mặt phẳng \((${origin_label}xy)\) trùng với ${ground_name}; giả sử mọi UAV (phương tiện bay không người lái) và tên lửa đều chuyển động thẳng đều. Tại thời điểm \(t=0\), rađa phát hiện ra UAV \(M\) ở tọa độ \(M_0${coord_M0}\); tại thời điểm \(t=${t_observe}\) giây rađa theo dõi thấy UAV \(M\) ở tọa độ \(M_1${coord_M1}\) trên đường thẳng \(d\).

Các mệnh đề sau đúng hay sai?

${label_a} Góc nghiêng của đường thẳng \(d\) và ${ground_name} là \(${angle_val} \, rad\).

${label_b} Khoảng cách giữa UAV \(M\) và gốc \(${origin_label}\) tại thời điểm ${time_b} giây là ${dist_b_val}m.

${label_c} Khoảng cách ngắn nhất từ điểm \(A\) tới đường thẳng \(d\) xấp xỉ ${dist_min_val}m (kết quả làm tròn đến hàng đơn vị của mét).

${label_d} Tại thời điểm \(t=${time_launch}s\), một tên lửa được phóng lên từ \(A\) và chuyển động thẳng đều với vận tốc ${v_missile}m/s, va chạm và phá hủy UAV \(M\) tại điểm \(B\) trên \(d\). Khi đó, sau ${time_impact_val} giây kể từ lúc phóng thì tên lửa va chạm với UAV (kết quả làm tròn đến hàng phần trăm của giây).
"""
)

TEMPLATE_SOL = Template(
    r"""
Lời giải:\\
Vectơ chỉ phương của \(d\): \(\vec{u} = \frac{1}{${t_observe}}\overrightarrow{M_0M_1} = ${vec_u}\).\\
Vectơ pháp tuyến của mặt phẳng \((${origin_label}xy)\) là \(\vec{k} = (0;0;1)\).\\
a) \(\sin(d, (${origin_label}xy)) = \frac{|\vec{u} \cdot \vec{k}|}{|\vec{u}| \cdot |\vec{k}|} = \frac{|${uz}|}{\sqrt{${ux}^2 + ${uy}^2 + ${uz}^2}} \approx ${sin_val}\).\\
Suy ra góc nghiêng \(\approx ${angle_rad} \, rad\).\\
b) Phương trình tham số của \(d\): \(\begin{cases} x = ${x0} + (${ux})t \\ y = ${y0} + (${uy})t \\ z = ${z0} + (${uz})t \end{cases}\)\\
(Do UAV chuyển động thẳng đều nên ta có thể đồng nhất \(t\) với số giây bay được của UAV, tính từ lúc nó bị rađa phát hiện).\\
Tại \(t=${time_b}\), tọa độ UAV là \(M_{${time_b}} ${coord_Mb}\).\\
\(${origin_label}M_{${time_b}} = \sqrt{${xb}^2 + ${yb}^2 + ${zb}^2} \approx ${dist_OM_unit}\).\\
Khoảng cách thực tế: \(${dist_OM_unit} \times ${scale} = ${dist_OM_real}m\).\\
c) Ta có: \(MA^2 = (${x0} + ${ux}t - ${ax})^2 + (${y0} + ${uy}t - ${ay})^2 + (${z0} + ${uz}t - ${az})^2\)\\
\(\phantom{MA^2} = ${quad_a}t^2 + (${quad_b})t + ${quad_c}\).\\
Suy ra \(MA \ge ${dist_A_d_unit}\). Vậy khoảng cách ngắn nhất từ \(A\) tới \(d\) là \(${dist_A_d_unit} \times ${scale} \approx ${dist_A_d_real}m\).\\
d) Vận tốc của UAV là \(v_1 = |\vec{u}| \times ${scale} = \sqrt{${u_sq}} \times ${scale} \approx ${v_uav} m/s\).\\
Vận tốc tên lửa \(v_2 = ${v_missile} m/s\).\\
Giả sử tên lửa gặp UAV tại thời điểm \(t\) (tính từ \(t=0\)). Thời gian bay của tên lửa là \(t - ${time_launch}\).\\
Quãng đường tên lửa bay: \(S_2 = v_2 \times (t - ${time_launch})\).\\
Quãng đường này chính là \(AB\) với \(B \in d\) ứng với tham số \(t\).\\
\(B(${x0} + ${ux}t; ${y0} + ${uy}t; ${z0} + ${uz}t)\).\\
Giải phương trình: \(AB = \frac{v_2}{${scale}} (t - ${time_launch})\) (quy về đơn vị tọa độ).\\
Giải phương trình tìm được \(t \approx ${t_intercept}\).\\
Thời gian bay của tên lửa: \(\Delta t = t - ${time_launch} \approx ${time_flight}\) giây.\\
"""
)

# ==================== MAIN CLASS ====================

class UAVMissileQuestion:
    def __init__(self):
        self.scale = 10  # 1 unit = 10m
        self.O = (0, 0, 0)
        self.A = (0, 0, 0)
        self.M0 = (0, 0, 0)
        self.M1 = (0, 0, 0)
        self.t_observe = 1  # Random observation time
        self.velocity = (0, 0, 0)  # Velocity per second
        self.time_b = 0
        self.time_launch = 0
        self.v_missile = 0
        
        # Correct values
        self.angle_rad = 0
        self.dist_b_real = 0
        self.dist_min_real = 0
        self.time_flight = 0
        
        # Display values (can be distorted)
        self.prop_a_val = 0
        self.prop_b_val = 0
        self.prop_c_val = 0
        self.prop_d_val = 0
        
        self.res_a = True
        self.res_b = True
        self.res_c = True
        self.res_d = True

    def get_nice_velocity_vector(self):
        """Find a velocity vector with integer magnitude and components"""
        # We want vx in [-50, -20], vy in [1, 30], vz in [-5, 5]
        # such that sqrt(vx^2 + vy^2 + vz^2) is integer
        candidates = []
        for vx in range(-50, -20):
            for vy in range(1, 31):
                for vz in range(-5, 6):
                    mag = math.sqrt(vx**2 + vy**2 + vz**2)
                    if mag.is_integer():
                        candidates.append((vx, vy, vz))
        
        if candidates:
            return random.choice(candidates)
        return (-30, 20, 0) # Fallback

    def generate_parameters(self):
        # Scale: 1 unit = 10m
        self.scale = 10

        # Randomize narrative labels (used in proposition a/b and context)
        self.ground_name = random.choice(GROUND_SURFACES)
        self.origin_label = random.choice(ORIGIN_LABELS)
        
        # A: Missile launcher (ground or low altitude)
        self.A = (random.randint(-20, 20), random.randint(60, 99), 0)
        
        # M0: UAV start position (high altitude, far away)
        # x large, y small, z moderate
        possible_m0_x = [15000 + 250 * i for i in range(40)]
        self.M0 = (random.choice(possible_m0_x), 0, random.randint(15, 44))
        
        # Random observation time (t_observe) - nice integer values
        self.t_observe = random.choice([2, 3, 4, 5])
        
        # Velocity vector of UAV (u) per second
        # Use integer magnitude vector for nicer numbers
        vx, vy, vz = self.get_nice_velocity_vector()
        
        # M1 is position at t = t_observe (multiply velocity by t_observe for integer coords)
        self.M1 = (self.M0[0] + vx * self.t_observe, self.M0[1] + vy * self.t_observe, self.M0[2] + vz * self.t_observe)
        
        # Store velocity per second for calculations
        self.velocity = (vx, vy, vz)
        
        # Time for question b
        self.time_b = random.randint(5, 34)
        
        # Time launch for question d
        self.time_launch = self.time_b  # Often same as time_b or close
        
        # Missile speed (m/s)
        missile_options = [300 + 10 * i for i in range(35)]
        self.v_missile = random.choice(missile_options)

    def solve(self):
        # Vector u = velocity per second (direction vector of d)
        ux, uy, uz = self.velocity
        u_sq = ux**2 + uy**2 + uz**2
        u_len = math.sqrt(u_sq)
        
        # a) Angle with ground (Oxy)
        # sin(alpha) = |uz| / u_len
        sin_alpha = abs(uz) / u_len
        self.angle_rad = math.asin(sin_alpha)
        
        # b) Distance at time_b
        # M(t) = M0 + t*u
        Mb_x = self.M0[0] + ux * self.time_b
        Mb_y = self.M0[1] + uy * self.time_b
        Mb_z = self.M0[2] + uz * self.time_b
        dist_OM_unit = math.sqrt(Mb_x**2 + Mb_y**2 + Mb_z**2)
        self.dist_b_real = dist_OM_unit * self.scale
        
        # c) Shortest distance from A to line d
        # Vector AM0
        am0_x = self.M0[0] - self.A[0]
        am0_y = self.M0[1] - self.A[1]
        am0_z = self.M0[2] - self.A[2]
        
        # Cross product [AM0, u]
        c_x = am0_y * uz - am0_z * uy
        c_y = am0_z * ux - am0_x * uz
        c_z = am0_x * uy - am0_y * ux
        cross_sq = c_x**2 + c_y**2 + c_z**2
        
        dist_A_d_unit = math.sqrt(cross_sq) / u_len
        self.dist_min_real = dist_A_d_unit * self.scale
        
        # Quadratic coefficients for MA^2 = at^2 + bt + c
        # MA^2 = |M0 + ut - A|^2 = |(M0-A) + ut|^2 = |D0 + ut|^2
        # = |D0|^2 + 2(D0.u)t + |u|^2 t^2
        d0x = am0_x
        d0y = am0_y
        d0z = am0_z
        
        dot_D0_u = d0x*ux + d0y*uy + d0z*uz
        len_D0_sq = d0x**2 + d0y**2 + d0z**2
        
        quad_a = u_sq
        quad_b = 2 * dot_D0_u
        quad_c = len_D0_sq
        
        # d) Intercept time
        # Solve for t > time_launch:
        # dist(A, M(t)) = (v_missile / scale) * (t - time_launch)
        # Let V_m_unit = v_missile / scale
        # |M(t) - A|^2 = V_m_unit^2 * (t - t_L)^2
        # M(t) - A = (M0x - Ax + ux*t, ...)
        # Let D0 = M0 - A
        # d0x = self.M0[0] - self.A[0] # Already calculated above
        # d0y = self.M0[1] - self.A[1]
        # d0z = self.M0[2] - self.A[2]
        
        # LHS = (d0x + ux*t)^2 + ... = (ux^2+...)*t^2 + 2*(d0x*ux+...)*t + (d0x^2+...)
        # LHS = u_sq * t^2 + 2*(D0.u) * t + |D0|^2
        
        # dot_D0_u = d0x*ux + d0y*uy + d0z*uz # Already calculated
        # len_D0_sq = d0x**2 + d0y**2 + d0z**2 # Already calculated
        
        V_m_unit = self.v_missile / self.scale
        
        # RHS = V^2 * (t - t_L)^2 = V^2 * (t^2 - 2*t_L*t + t_L^2)
        
        # Equation: A*t^2 + B*t + C = 0
        # LHS = u_sq * t^2 + 2*dot * t + len_sq
        # RHS = V^2 * t^2 - 2*V^2*t_L * t + V^2*t_L^2
        
        # (u_sq - V^2) * t^2 + (2*dot + 2*V^2*t_L) * t + (len_sq - V^2*t_L^2) = 0
        
        qa = u_sq - V_m_unit**2
        qb = 2 * dot_D0_u + 2 * V_m_unit**2 * self.time_launch
        qc = len_D0_sq - V_m_unit**2 * self.time_launch**2
        
        t_intercept = -1
        
        if abs(qa) < 1e-9:
            # Linear case: qb*t + qc = 0
            if abs(qb) > 1e-9:
                t_sol = -qc / qb
                if t_sol > self.time_launch:
                    t_intercept = t_sol
        else:
            # Quadratic case
            delta = qb**2 - 4*qa*qc
            
            if delta >= 0:
                t1 = (-qb - math.sqrt(delta)) / (2*qa)
                t2 = (-qb + math.sqrt(delta)) / (2*qa)
                # We need t > time_launch
                candidates = []
                if t1 > self.time_launch: candidates.append(t1)
                if t2 > self.time_launch: candidates.append(t2)
                
                if candidates:
                    t_intercept = min(candidates)
        
        intercept_point = None
        if t_intercept > 0:
            self.time_flight = t_intercept - self.time_launch
            intercept_point = (
                self.M0[0] + ux * t_intercept,
                self.M0[1] + uy * t_intercept,
                self.M0[2] + uz * t_intercept
            )
        else:
            self.time_flight = 0 # Should not happen with good params

        return {
            'ux': ux, 'uy': uy, 'uz': uz,
            'u_sq': u_sq, 'u_len': u_len,
            'sin_alpha': sin_alpha,
            'Mb_x': Mb_x, 'Mb_y': Mb_y, 'Mb_z': Mb_z,
            'dist_OM_unit': dist_OM_unit,
            'vec_AM0': f"({d0x}; {d0y}; {d0z})",
            'vec_cross': f"({c_x}; {c_y}; {c_z})",
            'cross_sq': cross_sq,
            'dist_A_d_unit': dist_A_d_unit,
            'v_uav': u_len * self.scale,
            't_intercept': t_intercept,
            'intercept_point': intercept_point,
            'am0_x': am0_x, 'am0_y': am0_y, 'am0_z': am0_z,
            'c_x': c_x, 'c_y': c_y, 'c_z': c_z,
            'quad_a': quad_a, 'quad_b': quad_b, 'quad_c': quad_c
        }

    def distort_and_set_props(self):
        # Randomly decide which propositions are True/False
        # We want a mix.
        
        # Prop A: Angle
        if random.random() < 0.5:
            self.prop_a_val = self.angle_rad
            self.res_a = True
        else:
            self.prop_a_val = self.angle_rad * random.uniform(0.8, 1.2)
            if abs(self.prop_a_val - self.angle_rad) < 0.001:
                self.prop_a_val += 0.01
            self.res_a = False
            
        # Prop B: Distance OM
        if random.random() < 0.5:
            self.prop_b_val = round(self.dist_b_real)
            self.res_b = True
        else:
            self.prop_b_val = round(self.dist_b_real * random.uniform(0.9, 1.1))
            if self.prop_b_val == round(self.dist_b_real):
                self.prop_b_val += 100
            self.res_b = False
            
        # Prop C: Min Distance A to d
        if random.random() < 0.5:
            self.prop_c_val = round(self.dist_min_real)
            self.res_c = True
        else:
            self.prop_c_val = round(self.dist_min_real * random.uniform(0.9, 1.1))
            if self.prop_c_val == round(self.dist_min_real):
                self.prop_c_val += 50
            self.res_c = False
            
        # Prop D: Flight time
        if random.random() < 0.5:
            self.prop_d_val = self.time_flight
            self.res_d = True
        else:
            self.prop_d_val = self.time_flight * random.uniform(0.8, 1.2)
            if abs(self.prop_d_val - self.time_flight) < 0.1:
                self.prop_d_val += 1.0
            self.res_d = False

    @staticmethod
    def label_with_star(letter: str, is_true: bool) -> str:
        return f"*{letter})" if is_true else f"{letter})"

    def generate_question(self, idx: int) -> str:
        # Loop to ensure valid interception
        while True:
            self.generate_parameters()
            sol_data = self.solve()
            if sol_data['t_intercept'] > 0:
                break

        self.distort_and_set_props()
        
        params = {
            'idx': idx,
            'ground_name': self.ground_name,
            'origin_label': self.origin_label,
            'coord_A': format_coord(*self.A),
            'scale': self.scale,
            'coord_M0': format_coord(*self.M0),
            'coord_M1': format_coord(*self.M1),
            't_observe': self.t_observe,
            'label_a': self.label_with_star('a', self.res_a),
            'label_b': self.label_with_star('b', self.res_b),
            'label_c': self.label_with_star('c', self.res_c),
            'label_d': self.label_with_star('d', self.res_d),
            'angle_val': format_vn_number(self.prop_a_val, 3),
            'time_b': self.time_b,
            'dist_b_val': format_vn_number(self.prop_b_val, 0),
            'dist_min_val': format_vn_number(self.prop_c_val, 0),
            'time_launch': self.time_launch,
            'v_missile': self.v_missile,
            'time_impact_val': format_vn_number(self.prop_d_val, 2),
            
            # Solution params
            'vec_u': format_coord(sol_data['ux'], sol_data['uy'], sol_data['uz']),
            'ux': to_latex_num(sol_data['ux']), 
            'uy': to_latex_num(sol_data['uy']), 
            'uz': to_latex_num(sol_data['uz']),
            'sin_val': format_vn_number(sol_data['sin_alpha'], 4),
            'angle_rad': format_vn_number(self.angle_rad, 3),
            
            'x0': to_latex_num(self.M0[0]), 
            'y0': to_latex_num(self.M0[1]), 
            'z0': to_latex_num(self.M0[2]),
            'coord_Mb': format_coord(sol_data['Mb_x'], sol_data['Mb_y'], sol_data['Mb_z']),
            'xb': to_latex_num(sol_data['Mb_x']), 
            'yb': to_latex_num(sol_data['Mb_y']), 
            'zb': to_latex_num(sol_data['Mb_z']),
            'dist_OM_unit': format_vn_number(sol_data['dist_OM_unit'], 2),
            'dist_OM_real': format_vn_number(self.dist_b_real, 0),
            
            'vec_AM0': format_coord(sol_data['am0_x'], sol_data['am0_y'], sol_data['am0_z']),
            'vec_cross': format_coord(sol_data['c_x'], sol_data['c_y'], sol_data['c_z']),
            'cross_sq': to_latex_num(sol_data['cross_sq']),
            'u_sq': to_latex_num(sol_data['u_sq']),
            'dist_A_d_unit': format_vn_number(sol_data['dist_A_d_unit'], 2),
            'dist_A_d_real': format_vn_number(self.dist_min_real, 0),
            
            'quad_a': to_latex_num(sol_data['quad_a']),
            'quad_b': to_latex_num(sol_data['quad_b']),
            'quad_c': to_latex_num(sol_data['quad_c']),
            
            'v_uav': format_vn_number(sol_data['v_uav'], 2),
            'ax': to_latex_num(self.A[0]), 
            'ay': to_latex_num(self.A[1]), 
            'az': to_latex_num(self.A[2]),
            't_intercept': format_vn_number(sol_data['t_intercept'], 2),
            'time_flight': format_vn_number(self.time_flight, 2)
        }
        
        question = TEMPLATE_Q.substitute(params)
        solution = TEMPLATE_SOL.substitute(params)
        
        return f"{question}\n{solution}"

# ==================== MAIN ====================

def main():
    num_questions = 5
    if len(sys.argv) > 1:
        try:
            num_questions = max(1, int(sys.argv[1]))
        except ValueError:
            print("Tham số không hợp lệ, sử dụng mặc định 5 câu hỏi.")
    
    questions = []
    for i in range(num_questions):
        q = UAVMissileQuestion()
        questions.append(q.generate_question(i + 1))
        
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "bai_toan_uav_ten_lua.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong bai_toan_uav_ten_lua.tex")

if __name__ == "__main__":
    main()

