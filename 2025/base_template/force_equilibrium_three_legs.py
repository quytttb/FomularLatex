"""
Dạng toán Lực tác dụng lên giá đỡ ba chân trong không gian 3D
Generator cho bài toán cân bằng lực với tam giác đều trên các mặt phẳng tọa độ
"""

import random
import math
from typing import Dict, Any, List, Tuple
from base_optimization_question import BaseOptimizationQuestion
import sympy as sp
from sympy import Point3D, symbols, Eq, solve, sqrt, latex
from typing import List, Dict, Any, Tuple
# ==== Import các hàm format từ latex_utils ====
from latex_utils import format_number_clean, format_dimension, clean_and_optimize_latex


class ForceEquilibriumQuestion(BaseOptimizationQuestion):
    def __init__(self):
        super().__init__()
        self._solution_cache = None

    def _compute_core_values(self, parameters=None):
        """Tính toán các giá trị core cho đáp án và sinh phương án sai, bổ sung chi tiết các bước tính toán."""
        p = parameters if parameters is not None else self.parameters
        c = p['diem_c']
        diem_a = p['diem_a']
        diem_b = p['diem_b']
        mat_phang = p['mat_phang']
        if mat_phang == 'Oxy':
            point_c_base_latex = f"C(a; b; 0)"
            point_c_latex = f"C({c[0]:.3f}; {c[1]:.3f}; 0)"
        elif mat_phang == 'Oyz':
            point_c_base_latex = f"C(0; b; c)"
            point_c_latex = f"C(0; {c[1]:.3f}; {c[2]:.3f})"
        else:
            point_c_base_latex = f"C(a; 0; c)"
            point_c_latex = f"C({c[0]:.3f}; 0; {c[2]:.3f})"

        ab_length_squared = sum((diem_b[i] - diem_a[i]) ** 2 for i in range(3))
        ac_length_squared = sum((c[i] - diem_a[i]) ** 2 for i in range(3))
        bc_length_squared = sum((c[i] - diem_b[i]) ** 2 for i in range(3))

        # Biểu thức BC^2 - AC^2 dưới dạng sympy
        a_sym, b_sym, c_sym = sp.symbols('a b c')
        bc2_expr = (a_sym - diem_b[0]) ** 2 + (b_sym - diem_b[1]) ** 2 + (c_sym - diem_b[2]) ** 2
        ac2_expr = (a_sym - diem_a[0]) ** 2 + (b_sym - diem_a[1]) ** 2 + (c_sym - diem_a[2]) ** 2
        bc2_minus_ac2 = sp.simplify(bc2_expr - ac2_expr)

        # Tính các giá trị diện tích tam giác và các vector liên quan, lấy chi tiết
        triangle_data = self._calculate_triangle_area(diem_a, diem_b, c, return_detail=True)
        coord_sum = round(c[0] ** 2 + c[1] ** 2 + c[2] ** 2, 2)
        don_vi_luc = round(p['don_vi_luc'], 2)
        dc_magnitude = sp.sqrt(sum(x ** 2 for x in p['vector_dc']))
        f3_magnitude = round(float(abs(p['he_so_he_phuong_trinh_luc'][2]) * float(dc_magnitude) * p['don_vi_luc']), 0)
        return {
            'sum_of_c_coordinates_squared': coord_sum,
            'unit_force_newton_per_unit': don_vi_luc,
            'triangle_area': round(triangle_data['area'], 3),
            'vector_dc_magnitude': dc_magnitude,
            'force3_magnitude': f3_magnitude,
            'diem_a': diem_a,
            'diem_b': diem_b,
            'diem_c': c,
            'mat_phang': mat_phang,
            'point_c_base_latex': point_c_base_latex,
            'point_c_latex': point_c_latex,
            'ab_length_squared': ab_length_squared,
            'ac_length_squared': ac_length_squared,
            'bc_length_squared': bc_length_squared,
            'bc2_minus_ac2_expr': bc2_minus_ac2,
            'ab_vector': triangle_data['ab_vector'],
            'ac_vector': triangle_data['ac_vector'],
            'ab_ac_cross_str': triangle_data['ab_ac_cross_str'],
            'ab_ac_cross': triangle_data['ab_ac_cross'],
            'ab_cross_ac_detail': triangle_data.get('ab_cross_ac_detail', ''),
            'area_detail': triangle_data.get('area_detail', ''),
            'parameters': p
        }

    """
    Dạng toán cân bằng lực trên giá đỡ ba chân với tam giác đều
    Hỗ trợ 3 mặt phẳng: Oxy (z=0), Oyz (x=0), Oxz (y=0)
    """

    # Các mặt phẳng có thể chọn
    PLANES = ['Oxy', 'Oyz', 'Oxz']

    # Template câu hỏi
    QUESTIONS = [
        "Tính a² + b² + c² với C(a,b,c)",
        "Một đơn vị dài trong hệ trục tọa độ tương ứng với bao nhiêu Newton?",
        "Diện tích tam giác ABC bằng bao nhiêu?",
        "Độ lớn của lực F₃ bằng bao nhiêu Newton? (làm tròn kết quả đến hàng đơn vị)",
    ]

    @staticmethod
    def sinh_toa_do_cua_a_hoac_b_tren_mat_phang(fixed_index: int, fixed_value: int = 0) -> Tuple[List[int], List[int]]:
        """Sinh tọa độ điểm A và B trên mặt phẳng đã chọn"""
        a = [random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)]
        a[fixed_index] = fixed_value
        distance = random.randint(2, 4)
        angle = random.uniform(0, 2 * math.pi)
        b = a.copy()
        b[(fixed_index + 1) % 3] += int(distance * math.cos(angle))
        b[(fixed_index + 2) % 3] += int(distance * math.sin(angle))
        b[fixed_index] = fixed_value
        return a, b

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán lực cân bằng"""

        # 1. Chọn mặt phẳng ngẫu nhiên
        mat_phang = random.choice(self.PLANES)

        # 2. Sinh tọa độ điểm D (điểm đặt lực) - random trong khoảng [1,5]
        diem_d = [random.randint(1, 5) for _ in range(3)]

        # 3. Sinh vector lực P⃗ - luôn có dạng (0,0,-x)
        do_lon_vector_luc_p = random.randint(2, 6)  # Độ lớn vector lực
        vector_luc_p = [0, 0, -do_lon_vector_luc_p]
        do_lon_luc_p = random.randint(120, 300)  # Lực thực tế (Newton)

        # 4. Sinh tọa độ điểm A, B trên mặt phẳng đã chọn
        if mat_phang == 'Oxy':
            # z = 0 cho A, B
            diem_a, diem_b = self.sinh_toa_do_cua_a_hoac_b_tren_mat_phang(2, 0)
        elif mat_phang == 'Oyz':
            # x = 0 cho A, B
            diem_a, diem_b = self.sinh_toa_do_cua_a_hoac_b_tren_mat_phang(0, 0)
        else:  # Oxz
            # y = 0 cho A, B
            diem_a, diem_b = self.sinh_toa_do_cua_a_hoac_b_tren_mat_phang(1, 0)

        # 5. Tính C để tam giác ABC đều
        diem_c = self.tinh_toa_do_diem_c(diem_a, diem_b, mat_phang)

        # 6. Tính các vector DA, DB, DC
        vector_da = [float(diem_a[i] - diem_d[i]) for i in range(3)]
        vector_db = [float(diem_b[i] - diem_d[i]) for i in range(3)]
        vector_dc = [float(diem_c[i] - diem_d[i]) for i in range(3)]

        # 7. Giải hệ phương trình lực: x₁*DA + x₂*DB + x₃*DC = P⃗
        he_so_1, he_so_2, he_so_3 = self.giai_he_luc(vector_da, vector_db, vector_dc,
                                                     [float(x) for x in vector_luc_p])

        return {
            "mat_phang": mat_phang,
            "diem_d": diem_d,
            "diem_a": diem_a,
            "diem_b": diem_b,
            "diem_c": diem_c,
            "vector_luc_p": vector_luc_p,
            "do_lon_vector_luc_p": do_lon_vector_luc_p,
            "do_lon_luc_p": do_lon_luc_p,
            "vector_da": vector_da,
            "vector_db": vector_db,
            "vector_dc": vector_dc,
            "he_so_he_phuong_trinh_luc": [he_so_1, he_so_2, he_so_3],
            "don_vi_luc": do_lon_luc_p / do_lon_vector_luc_p  # Newton per unit
        }

    def tinh_toa_do_diem_c(self, diem_a: List[int], diem_b: List[int], mat_phang: str):
        """Tính tọa độ điểm C để tam giác ABC đều"""
        # Sinh tọa độ C dựa trên mặt phẳng đã chọn
        # Lưu lại các bước tính toán chi tiết để giải thích trong lời giải
        cac_buoc_giai = {'mat_phang': mat_phang}

        # Tính bình phương độ dài cạnh AB. Đây là hằng số cho các cạnh còn lại.
        binh_phuong_a_b = sum((diem_b[i] - diem_a[i]) ** 2 for i in range(3))
        cac_buoc_giai['binh_phuong_a_b'] = str(binh_phuong_a_b)
        cac_buoc_giai['do_dai_a_b'] = round(binh_phuong_a_b ** 0.5, 3)

        # Khởi tạo các biến a, b, c. Chúng sẽ nhận giá trị sau khi tính toán.
        a, b, c = None, None, None
        # Dựa vào mặt phẳng, xác định 1 tọa độ bằng 0 và giải hệ cho 2 tọa độ còn lại.
        if mat_phang == 'Oxy':
            # C có dạng (a, b, 0), với a, b là các giá trị cần tìm
            bien_so_1, bien_so_2, chi_so_1, chi_so_2 = 'a', 'b', 0, 1  # 0 và 1 là chỉ số của chúng trong danh sách
            c = 0
        elif mat_phang == 'Oyz':
            # C có dạng (0, b, c), với b, c là các giá trị cần tìm
            bien_so_1, bien_so_2, chi_so_1, chi_so_2 = 'b', 'c', 1, 2
            a = 0
        else:  # Oxz
            # C có dạng (a, 0, c), với a, c là các giá trị cần tìm
            bien_so_1, bien_so_2, chi_so_1, chi_so_2 = 'a', 'c', 0, 2
            b = 0

        cac_buoc_giai.update({'bien_so_1': bien_so_1, 'bien_so_2': bien_so_2})

        # Giải để tìm biến số 1


    def tinh_dien_tich_tam_giac(A, B, C):
        pass

    def giai_he_luc(self, vector_da, vector_db, vector_dc, param):
        pass


def generate_question_text(self) -> str:
    """Sinh đề bài LaTeX"""
    p = self.parameters

    # Format tọa độ các điểm
    d_str = f"D({p['diem_d'][0]}; {p['diem_d'][1]}; {p['diem_d'][2]})"
    a_str = f"A({p['diem_a'][0]}; {p['diem_a'][1]}; {p['diem_a'][2]})"
    b_str = f"B({p['diem_b'][0]}; {p['diem_b'][1]}; {p['diem_b'][2]})"

    do_lon_luc_p = p['do_lon_luc_p']
    vector_luc_p = p['vector_luc_p']
    force_vector_str = f"\\overrightarrow{{P}}=({vector_luc_p[0]}; {vector_luc_p[1]}; {vector_luc_p[2]})"

    plane_name = p['mat_phang']

    return f"""Trong không gian \\(Oxyz\\), một vật có trọng lượng \\(P={do_lon_luc_p}N\\) đặt trên một giá đỡ ba chân với điểm đặt là \\({d_str}\\). Ba điểm tiếp xúc với mặt đất \\(A, B, C\\) nằm trên mặt phẳng \\(({plane_name})\\). Biết tọa độ các điểm \\({a_str}, {b_str}, C(a; b; c)\\), tam giác \\(ABC\\) đều. \n\nBiết rằng trọng lực \\({force_vector_str}\\) sẽ ép vào ba thanh \\(DA, DB, DC\\) các lực \\(\\overrightarrow{{F}}_1, \\overrightarrow{{F}}_2, \\overrightarrow{{F}}_3\\) lần lượt hướng dọc theo các vectơ \\(\\overrightarrow{{DA}}, \\overrightarrow{{DB}}, \\overrightarrow{{DC}}\\). \n\nTheo tính chất Vật Lý thì ta có: \\(\\overrightarrow{{F_1}}+\\overrightarrow{{F_2}}+\\overrightarrow{{F_3}}=\\overrightarrow{{P}}\\).\n\nHỏi trong các mệnh đề dưới đây, mệnh đề nào đúng, mệnh đề nào sai?"""


def calculate_answer(self) -> str:
    """Tính đáp án đúng dưới dạng string tổng hợp cho trắc nghiệm và lưu các giá trị cần thiết cho solution"""
    cache = self._compute_core_values()
    self._solution_cache = cache
    # Áp dụng format cho từng giá trị
    coord_sum = format_number_clean(cache['sum_of_c_coordinates_squared'])
    don_vi_luc = format_dimension(cache['unit_force_newton_per_unit'], 'N')
    area = format_number_clean(cache['triangle_area'])
    f3 = format_dimension(cache['force3_magnitude'], 'N')
    answer = f"a²+b²+c²={coord_sum}; 1 đơn vị={don_vi_luc}; S={area}; F₃={f3}"
    return clean_and_optimize_latex(answer)


def generate_wrong_answers(self) -> List[str]:
    """Sinh 3 đáp án sai cho các lựa chọn trắc nghiệm (dạng string tổng hợp)"""
    cache = self._compute_core_values()
    coord_sum = cache['sum_of_c_coordinates_squared']
    don_vi_luc = cache['unit_force_newton_per_unit']
    area = cache['triangle_area']
    f3_magnitude = cache['force3_magnitude']

    wrongs = set()
    tries = 0
    while len(wrongs) < 3 and tries < 20:
        tries += 1
        w_coord_sum = format_number_clean(coord_sum + random.choice([-3, -2, -1, 1, 2, 3]))
        w_unit_force = format_dimension(don_vi_luc + random.choice([-30, -20, -10, 10, 20, 30]), 'N')
        w_area = format_number_clean(round(area * random.uniform(0.7, 1.5), 3))
        w_f3 = format_dimension(round(f3_magnitude * random.uniform(0.7, 1.5)), 'N')
        wrong_str = f"a²+b²+c²={w_coord_sum}; 1 đơn vị={w_unit_force}; S={w_area}; F₃={w_f3}"
        wrong_str = clean_and_optimize_latex(wrong_str)
        if wrong_str != self.calculate_answer():
            wrongs.add(wrong_str)
    return list(wrongs)


def generate_solution(self) -> str:
    """Sinh lời giải chi tiết, chỉ hiển thị, không tính toán lại"""
    # Lấy các giá trị đã tính toán từ calculate_answer
    cache = getattr(self, '_solution_cache', None)
    if cache is None:
        # Đảm bảo cache được tạo
        self.calculate_answer()
        cache = self._solution_cache
        if cache is None:
            raise RuntimeError("Solution cache was not set after calculate_answer. Please check implementation.")
    p = cache['parameters']
    diem_a = cache['diem_a']
    diem_b = cache['diem_b']
    diem_c = cache['diem_c']
    mat_phang = cache['mat_phang']
    point_c_base_latex = cache['point_c_base_latex']
    point_c_latex = cache['point_c_latex']
    ab_length_squared = cache['ab_length_squared']
    ac_length_squared = cache['ac_length_squared']
    bc_length_squared = cache['bc_length_squared']
    sum_of_c_coordinates_squared = format_number_clean(cache['sum_of_c_coordinates_squared'])
    unit_force_newton_per_unit = format_dimension(cache['unit_force_newton_per_unit'], 'N')
    triangle_area = format_number_clean(cache['triangle_area'])
    vector_dc_magnitude = format_number_clean(float(cache['vector_dc_magnitude']), precision=3)
    force3_magnitude = format_dimension(cache['force3_magnitude'], 'N')
    ab_vector = cache['ab_vector']
    ac_vector = cache['ac_vector']
    ab_ac_cross_str = cache['ab_ac_cross_str']
    bc2_minus_ac2_expr = cache['bc2_minus_ac2_expr']

    from sympy import latex

    solution = fr"""
a) \(a^2+b^2+c^2={sum_of_c_coordinates_squared}\) \\
c) Diện tích tam giác ABC bằng \({triangle_area}\)\\

+ Bước 1: Tìm tọa độ điểm \(C\) để tam giác \(ABC\) đều. \\

Do \(C\) thuộc \({mat_phang}\) nên \({point_c_base_latex}\)

Biết:
\[
AB = {format_number_clean(float(ab_length_squared) ** 0.5, precision=3)} \Rightarrow AB^2 = {format_number_clean(ab_length_squared, precision=3)}
\]
\[
AC^2 = (a - {diem_a[0]})^2 + (b - {diem_a[1]})^2 + (c - {diem_a[2]})^2 = {format_number_clean(ac_length_squared, precision=3)} \tag{{1}}
\]
\[
BC^2 = (a - {diem_b[0]})^2 + (b - {diem_b[1]})^2 + (c - {diem_b[2]})^2 = {format_number_clean(bc_length_squared, precision=3)} \tag{{2}}
\]

Trừ \((2)\) cho \((1)\):
\[
\left[(a - {diem_b[0]})^2 + (b - {diem_b[1]})^2 + (c - {diem_b[2]})^2\right] - \left[(a - {diem_a[0]})^2 + (b - {diem_a[1]})^2 + (c - {diem_a[2]})^2\right] = 0
\]
\[
\Leftrightarrow {latex(bc2_minus_ac2_expr)} = 0
\]
Thế vào để tìm các giá trị còn lại, ta được:
\[
C = {point_c_latex}
\]
\[
a^2 + b^2 + c^2 = {sum_of_c_coordinates_squared}
\]

+ Bước 2: Tính tích có hướng \([\overrightarrow{{AB}} , \overrightarrow{{AC}}]\):

\[
\overrightarrow{{AB}} = ({ab_vector[0]}, {ab_vector[1]}, {ab_vector[2]})
\]
\[
\overrightarrow{{AC}} = ({format_number_clean(ac_vector[0], precision=3)}, {format_number_clean(ac_vector[1], precision=3)}, {format_number_clean(ac_vector[2], precision=3)})
\]
\[
[\overrightarrow{{AB}},  \overrightarrow{{AC}}] = {ab_ac_cross_str}
\]

+ Bước 3: Tính diện tích tam giác:
\[
S = \frac{{1}}{{2}} \left\| \overrightarrow{{AB}} \times \overrightarrow{{AC}} \right\| = {triangle_area}
\]

Kết luận:
\[
\boxed{{\text{{Diện tích tam giác }} ABC = {triangle_area}}}
\]

b) Một đơn vị dài trong hệ trục toạ độ Oxyz tương ứng với độ lớn của lực là \({unit_force_newton_per_unit}\).

Ta có: \(|\overrightarrow{{P}}|={format_number_clean(p['do_lon_vector_luc_p'])}\) ứng với \({format_dimension(p['do_lon_luc_p'], 'N')}\) nên một đơn vị độ dài ứng với \({unit_force_newton_per_unit}\)

d) Độ lớn của lực \(\overrightarrow{{F}}_3\) bằng \({force3_magnitude}\) (làm tròn kết quả đến hàng đơn vị khi tính theo newton).

\[
\overrightarrow{{DA}} = ({diem_a[0]}-{p['diem_d'][0]}, {diem_a[1]}-{p['diem_d'][1]}, {diem_a[2]}-{p['diem_d'][2]}) = ({format_number_clean(p['vector_da'][0], precision=3)}; {format_number_clean(p['vector_da'][1], precision=3)}; {format_number_clean(p['vector_da'][2], precision=3)})
\]
\[
\overrightarrow{{DB}} = ({diem_b[0]}-{p['diem_d'][0]}, {diem_b[1]}-{p['diem_d'][1]}, {diem_b[2]}-{p['diem_d'][2]}) = ({format_number_clean(p['vector_db'][0], precision=3)}; {format_number_clean(p['vector_db'][1], precision=3)}; {format_number_clean(p['vector_db'][2], precision=3)})
\]
\[
\overrightarrow{{DC}} = ({format_number_clean(diem_c[0], precision=3)}-{p['diem_d'][0]}, {format_number_clean(diem_c[1], precision=3)}-{p['diem_d'][1]}, {format_number_clean(diem_c[2], precision=3)}-{p['diem_d'][2]}) = ({format_number_clean(p['vector_dc'][0], precision=3)}; {format_number_clean(p['vector_dc'][1], precision=3)}; {format_number_clean(p['vector_dc'][2], precision=3)})
\]

Do \(\overrightarrow{{F_1}},\overrightarrow{{F_2}}, \overrightarrow{{F_3}}\) lần lượt cùng phương với \(\overrightarrow{{DA}}, \overrightarrow{{DB}}, \overrightarrow{{DC}}\) nên ta có:
\[
\overrightarrow{{F_1}} = x_1 \cdot \overrightarrow{{DA}},\quad \overrightarrow{{F_2}} = x_2 \cdot \overrightarrow{{DB}},\quad \overrightarrow{{F_3}} = x_3 \cdot \overrightarrow{{DC}}
\]
\[
\Rightarrow x_1 \cdot \overrightarrow{{DA}} + x_2 \cdot \overrightarrow{{DB}} + x_3 \cdot \overrightarrow{{DC}} = {tuple(p['vector_luc_p'])}
\]

Từ đây ta có hệ phương trình và nghiệm:
\[
x_1 = {format_number_clean(p['he_so_he_phuong_trinh_luc'][0], precision=6)},\quad x_2 = {format_number_clean(p['he_so_he_phuong_trinh_luc'][1], precision=6)},\quad x_3 = {format_number_clean(p['he_so_he_phuong_trinh_luc'][2], precision=6)}
\]

+ Tính độ lớn của \(\overrightarrow{{F_3}}\)
\[
|\overrightarrow{{DC}}| = \sqrt{{{format_number_clean(p['vector_dc'][0], precision=3)}^2 + {format_number_clean(p['vector_dc'][1], precision=3)}^2 + {format_number_clean(p['vector_dc'][2], precision=3)}^2}} = {vector_dc_magnitude}
\Rightarrow |\overrightarrow{{F_3}}| = |x_3| \cdot |\overrightarrow{{DC}}| = {format_number_clean(abs(p['he_so_he_phuong_trinh_luc'][2]), precision=3)} \cdot {vector_dc_magnitude} = {format_number_clean(abs(p['he_so_he_phuong_trinh_luc'][2]) * float(cache['vector_dc_magnitude']), precision=3)}
\]

Nhân với \({unit_force_newton_per_unit}\):
\[
|\overrightarrow{{F_3}}| = {format_number_clean(abs(p['he_so_he_phuong_trinh_luc'][2]) * float(cache['vector_dc_magnitude']), precision=3)} \cdot {unit_force_newton_per_unit} = {force3_magnitude}
\]
"""
    return clean_and_optimize_latex(solution)


# Alias để tương thích
ForceEquilibrium = ForceEquilibriumQuestion
