# -*- coding: utf-8 -*-
"""
Dạng toán Lực tác dụng lên giá đỡ ba chân trong không gian 3D
Generator cho bài toán cân bằng lực với tam giác đều trên các mặt phẳng tọa độ.
Phiên bản hoàn chỉnh, có thể chạy độc lập từ dòng lệnh.
"""

import random
import math
import argparse
import sys
from typing import Dict, Any, List, Tuple, Type, Union
from abc import ABC, abstractmethod
import re

import sympy as sp


# ========================================================================================
# PHẦN 1: CÁC LỚP VÀ HÀM CƠ SỞ (Tham khảo từ extremum.py)
# ========================================================================================

class BaseOptimizationQuestion(ABC):
    """
    Lớp cơ sở trừu tượng cho tất cả các dạng bài toán.
    Định nghĩa giao diện chung mà mỗi lớp câu hỏi cụ thể phải tuân theo.
    """

    def __init__(self):
        self.parameters = self.generate_parameters()
        self._solution_cache = None

    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên cho bài toán."""
        pass

    @abstractmethod
    def calculate_answer(self) -> str:
        """Tính đáp án đúng dựa trên parameters."""
        pass

    @abstractmethod
    def generate_wrong_answers(self) -> List[str]:
        """Sinh các đáp án sai/nhiễu."""
        pass

    @abstractmethod
    def generate_question_text(self) -> str:
        """Sinh đề bài câu hỏi dạng LaTeX."""
        pass

    @abstractmethod
    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết dạng LaTeX."""
        pass

    def generate_question_package(self, question_number: int = 1, include_multiple_choice: bool = True) -> str:
        question_text = self.generate_question_text()
        solution = self.generate_solution()
        # Chỉ xuất ra phần mệnh đề đúng/sai, không sinh ABCD
        answer_section = self.calculate_answer()
        # Xóa \textbf khỏi phần sinh đề
        full_question = (
            f"Câu {question_number}: {question_text}\n\n"
            f"{answer_section}\n\n"
            f"Lời giải:\n\n{solution}\n\n"
        )
        return full_question


def format_number_clean(num, precision=3):
    """Làm tròn và loại bỏ các số 0 không cần thiết ở cuối."""
    return f'{float(f"{num:.{precision}f}"):g}'


def format_dimension(num, unit):
    """Định dạng số với đơn vị."""
    return f"{format_number_clean(num)} {unit}"


def clean_and_optimize_latex(text):
    """Làm sạch chuỗi LaTeX."""
    return text.strip()


def format_symbolic_latex(expr):
    import sympy as sp
    return sp.latex(sp.nsimplify(expr, rational=True, tolerance=1e-6))


# ========================================================================================
# PHẦN 2: LỚP CÂU HỎI CỤ THỂ (ForceEquilibriumQuestion)
# ========================================================================================

class ForceEquilibriumQuestion(BaseOptimizationQuestion):
    """
    Lớp tạo câu hỏi về cân bằng lực trên giá đỡ ba chân.
    Sử dụng Sympy để xử lý toán học tượng trưng và sinh lời giải chi tiết.
    """
    CAC_MAT_PHANG = ['Oxy', 'Oyz', 'Oxz']

    def __init__(self):
        super().__init__()

    # --- SINH THAM SỐ GỐC ---
    def generate_parameters(self) -> Dict[str, Any]:
        mat_phang = random.choice(self.CAC_MAT_PHANG)
        diem_d = [random.randint(1, 5) for _ in range(3)]
        do_lon_vector_luc_p = random.randint(2, 6)
        he_so_chuyen_doi = random.randint(30, 60)
        vector_luc_p = [0, 0, -do_lon_vector_luc_p]
        do_lon_luc_p_newton = do_lon_vector_luc_p * he_so_chuyen_doi

        if mat_phang == 'Oxy':
            diem_a, diem_b = self._sinh_toa_do_ab_tren_mat_phang(2, 0)
        elif mat_phang == 'Oyz':
            diem_a, diem_b = self._sinh_toa_do_ab_tren_mat_phang(0, 0)
        else:
            diem_a, diem_b = self._sinh_toa_do_ab_tren_mat_phang(1, 0)

        return {
            "mat_phang": mat_phang, "diem_d": diem_d, "diem_a": diem_a,
            "diem_b": diem_b, "vector_luc_p": vector_luc_p,
            "do_lon_luc_p_newton": do_lon_luc_p_newton,
            "he_so_chuyen_doi": he_so_chuyen_doi
        }

    @staticmethod
    def _sinh_toa_do_ab_tren_mat_phang(chi_so_co_dinh: int, gia_tri_co_dinh: int = 0) -> Tuple[List[int], List[int]]:
        a = [random.randint(-3, 3) for _ in range(3)]
        a[chi_so_co_dinh] = gia_tri_co_dinh
        khoang_cach, goc = random.randint(2, 4), random.uniform(0, 2 * math.pi)
        b = a[:]
        cac_chi_so_con_lai = [i for i in range(3) if i != chi_so_co_dinh]
        b[cac_chi_so_con_lai[0]] += int(khoang_cach * math.cos(goc))
        b[cac_chi_so_con_lai[1]] += int(khoang_cach * math.sin(goc))
        return a, b

    # --- TÍNH TOÁN PHÁI SINH ---
    def _tinh_toan_day_du(self) -> Dict[str, Any]:
        if self._solution_cache:
            return self._solution_cache

        # Chỉ thử một lần với self.parameters, không tự động sinh lại
        tham_so = self.parameters.copy()
        diem_c_tinh_duoc, buoc_giai_c = self._tinh_toa_do_diem_c(tham_so['diem_a'], tham_so['diem_b'], tham_so['mat_phang'])
        # Nếu không giải được ẩn thứ hai thì raise lỗi
        if not (buoc_giai_c.get('nghiem_an2') and len(buoc_giai_c['nghiem_an2']) > 0):
            raise Exception("Không tìm được bộ tham số hợp lệ cho bài toán này. Hãy sinh lại câu hỏi mới.")
        # --- SYMBOLIC: Dùng điểm symbolic cho các phép toán hình học ---
        diem_D_sym = sp.Point3D(*tham_so['diem_d'])
        diem_A_sym = sp.Point3D(*tham_so['diem_a'])
        diem_B_sym = sp.Point3D(*tham_so['diem_b'])
        diem_C_sym = diem_c_tinh_duoc
        # Dùng float cho các phép tính số học vật lý
        def safe_float(x):
            try:
                return float(x)
            except Exception:
                try:
                    return float(x.evalf())
                except Exception:
                    return 0.0
        diem_c_floats = [safe_float(coord) for coord in diem_c_tinh_duoc.args]
        diem_C_sp = sp.Point3D(*diem_c_floats)
        diem_D_sp = sp.Point3D(*[float(x) for x in tham_so['diem_d']])
        diem_A_sp = sp.Point3D(*[float(x) for x in tham_so['diem_a']])
        diem_B_sp = sp.Point3D(*[float(x) for x in tham_so['diem_b']])
        vector_P_sp = sp.Point3D(*tham_so['vector_luc_p'])
        # --- SYMBOLIC: vector hình học ---
        vector_DA_sym = diem_A_sym - diem_D_sym
        vector_DB_sym = diem_B_sym - diem_D_sym
        vector_DC_sym = diem_C_sym - diem_D_sym
        # Đảm bảo hàm ensure_point3d có trước khi sử dụng
        def ensure_point3d(pt):
            if isinstance(pt, sp.Point3D):
                return pt
            elif hasattr(pt, 'x') and hasattr(pt, 'y') and hasattr(pt, 'z'):
                return sp.Point3D(pt.x, pt.y, pt.z)
            elif hasattr(pt, 'args') and len(pt.args) == 3:
                return sp.Point3D(*pt.args)
            else:
                return sp.Point3D(0, 0, 0)
        # --- SỬA: Chỉ truyền Point3D vào _giai_he_luc (float version) ---
        vector_DA_sp = ensure_point3d(diem_A_sp - diem_D_sp)
        vector_DB_sp = ensure_point3d(diem_B_sp - diem_D_sp)
        vector_DC_sp = ensure_point3d(diem_C_sp - diem_D_sp)
        he_so_luc = self._giai_he_luc(vector_DA_sp, vector_DB_sp, vector_DC_sp, vector_P_sp)
        if any(x is None for x in he_so_luc):
            raise Exception("Không tìm được bộ tham số hợp lệ cho bài toán này. Hãy sinh lại câu hỏi mới.")
        tham_so['diem_c'] = diem_c_floats
        # --- Lưu các biến symbolic cho hình học ---
        tham_so['diem_a_sym'] = diem_A_sym
        tham_so['diem_b_sym'] = diem_B_sym
        tham_so['diem_c_sym'] = diem_C_sym
        tham_so['diem_d_sym'] = diem_D_sym
        tham_so['vector_da_sym'] = vector_DA_sym
        tham_so['vector_db_sym'] = vector_DB_sym
        tham_so['vector_dc_sym'] = vector_DC_sym
        self.parameters = tham_so

        tham_so['diem_c'] = [safe_float(coord) for coord in diem_c_tinh_duoc.args]
        tham_so['buoc_giai_c'] = buoc_giai_c

        # --- SYMBOLIC: Tính diện tích và tích có hướng bằng điểm symbolic ---
        dien_tich_data = self._tinh_dien_tich_tam_giac(
            tham_so['diem_a_sym'], tham_so['diem_b_sym'], tham_so['diem_c_sym'], return_detail=True)
        if isinstance(dien_tich_data, dict):
            tham_so.update(dien_tich_data)
        else:
            tham_so['dien_tich'] = dien_tich_data

        # --- FLOAT: Tính các đại lượng vật lý bằng điểm float ---
        diem_D_sp, diem_A_sp, diem_B_sp, diem_C_sp = (
            sp.Point3D(*[float(x) for x in tham_so[k]]) if k != 'diem_c' else sp.Point3D(*[float(x) for x in tham_so[k]])
            for k in ['diem_d', 'diem_a', 'diem_b', 'diem_c']
        )
        vector_P_sp = sp.Point3D(*tham_so['vector_luc_p'])
        vector_DA_sp, vector_DB_sp, vector_DC_sp = diem_A_sp - diem_D_sp, diem_B_sp - diem_D_sp, diem_C_sp - diem_D_sp
        tham_so.update({'vector_da_obj': vector_DA_sp, 'vector_db_obj': vector_DB_sp, 'vector_dc_obj': vector_DC_sp,
                        'vector_p_obj': vector_P_sp})

        def ensure_point3d(pt):
            if isinstance(pt, sp.Point3D):
                return pt
            elif hasattr(pt, 'x') and hasattr(pt, 'y') and hasattr(pt, 'z'):
                return sp.Point3D(pt.x, pt.y, pt.z)
            elif hasattr(pt, 'args') and len(pt.args) == 3:
                return sp.Point3D(*pt.args)
            else:
                return sp.Point3D(0, 0, 0)
        vector_DA_sp = ensure_point3d(vector_DA_sp)
        vector_DB_sp = ensure_point3d(vector_DB_sp)
        vector_DC_sp = ensure_point3d(vector_DC_sp)
        he_so_luc = self._giai_he_luc(vector_DA_sp, vector_DB_sp, vector_DC_sp, vector_P_sp)
        tham_so['he_so_luc'] = he_so_luc

        do_lon_vector_p = vector_P_sp.distance(sp.Point3D(0, 0, 0))
        tham_so['do_lon_vector_p_obj'] = do_lon_vector_p
        tham_so['don_vi_luc'] = float(tham_so['do_lon_luc_p_newton']) / float(do_lon_vector_p) if do_lon_vector_p != 0 else 0.0

        tham_so['tong_binh_phuong_c'] = sum(x ** 2 for x in tham_so['diem_c'])
        dc_magnitude = vector_DC_sp.distance(sp.Point3D(0, 0, 0))
        tham_so['dc_magnitude_obj'] = dc_magnitude
        tham_so['do_lon_f3_don_vi_dai'] = abs(he_so_luc[2]) * float(dc_magnitude)
        tham_so['do_lon_f3_newton'] = float(tham_so['do_lon_f3_don_vi_dai']) * float(tham_so['don_vi_luc'])

        x1, x2, x3 = sp.symbols('x1 x2 x3')
        he_pt_1 = sp.Eq(x1 * vector_DA_sp.x + x2 * vector_DB_sp.x + x3 * vector_DC_sp.x, vector_P_sp.x)
        he_pt_2 = sp.Eq(x1 * vector_DA_sp.y + x2 * vector_DB_sp.y + x3 * vector_DC_sp.y, vector_P_sp.y)
        he_pt_3 = sp.Eq(x1 * vector_DA_sp.z + x2 * vector_DB_sp.z + x3 * vector_DC_sp.z, vector_P_sp.z)
        tham_so['he_pt_luc_obj'] = [he_pt_1, he_pt_2, he_pt_3]

        # --- Lưu nghiệm symbolic cho a^2 + b^2 + c^2 ---
        nghiem_symbolic = None
        if 'ket_qua_he_pt_obj' in buoc_giai_c:
            nghiem = buoc_giai_c['ket_qua_he_pt_obj'][0]
            if tham_so['mat_phang'] == 'Oxy':
                a_expr, b_expr, c_expr = nghiem[0], nghiem[1], 0
            elif tham_so['mat_phang'] == 'Oyz':
                a_expr, b_expr, c_expr = 0, nghiem[0], nghiem[1]
            else:
                a_expr, b_expr, c_expr = nghiem[0], 0, nghiem[1]
            nghiem_symbolic = (a_expr, b_expr, c_expr)
            tham_so['tong_binh_phuong_c_symbolic'] = a_expr**2 + b_expr**2 + c_expr**2
        else:
            tham_so['tong_binh_phuong_c_symbolic'] = None
        # Giá trị số vẫn giữ để tính toán
        tham_so['tong_binh_phuong_c'] = sum(x ** 2 for x in tham_so['diem_c'])

        self._solution_cache = tham_so
        return tham_so

    # --- CÁC HÀM TÍNH TOÁN TĨNH ---
    @staticmethod
    def _tinh_toa_do_diem_c(diem_a: List[float], diem_b: List[float], mat_phang: str) -> Tuple[
        sp.Point3D, Dict[str, Any]]:
        a, b, c = sp.symbols('a b c')
        diem_A_sp, diem_B_sp = sp.Point3D(*diem_a), sp.Point3D(*diem_b)
        buoc_giai = {}
        if mat_phang == 'Oxy':
            diem_C_tuong_trung, an_so_can_tim = sp.Point3D(a, b, 0), (a, b)
        elif mat_phang == 'Oyz':
            diem_C_tuong_trung, an_so_can_tim = sp.Point3D(0, b, c), (b, c)
        else:
            diem_C_tuong_trung, an_so_can_tim = sp.Point3D(a, 0, c), (a, c)
        buoc_giai.update({'an_so_1': str(an_so_can_tim[0]), 'an_so_2': str(an_so_can_tim[1])})
        ab_binh_phuong = diem_A_sp.distance(diem_B_sp) ** 2
        buoc_giai['ab_binh_phuong_obj'] = ab_binh_phuong
        pt1 = sp.Eq(diem_A_sp.distance(diem_C_tuong_trung) ** 2, ab_binh_phuong)
        pt2 = sp.Eq(diem_B_sp.distance(diem_C_tuong_trung) ** 2, ab_binh_phuong)
        buoc_giai.update({'phuong_trinh_1_obj': pt1, 'phuong_trinh_2_obj': pt2})
        # --- BẮT ĐẦU GHI LẠI CÁC BƯỚC GIẢI ĐÚNG THỰC TẾ ---
        # 1. Trừ hai phương trình để loại 1 ẩn
        # Nếu lhs là Point3D, chuyển về tổng bình phương các tọa độ
        def expr_from_lhs(lhs):
            if isinstance(lhs, sp.Point3D):
                coords = list(lhs.args)
                squares = []
                for coord in coords:
                    try:
                        squares.append(sp.sympify(coord)**2)
                    except Exception:
                        squares.append(0)
                return sum(squares)
            return lhs
        lhs1 = sp.sympify(expr_from_lhs(pt1.lhs))
        lhs2 = sp.sympify(expr_from_lhs(pt2.lhs))
        pt_tru = sp.simplify(lhs2 - lhs1)
        pt_tru_eq = sp.Eq(pt_tru, 0)
        buoc_giai['pt_tru_obj'] = pt_tru_eq
        # 2. Giải phương trình bậc nhất này theo một ẩn
        an_1 = an_so_can_tim[0]
        an_2 = an_so_can_tim[1]
        try:
            nghiem_an1 = sp.solve(pt_tru_eq, an_1)
        except Exception:
            nghiem_an1 = []
        buoc_giai['nghiem_an1'] = nghiem_an1
        # 3. Thế nghiệm vào một phương trình gốc để tìm ẩn còn lại
        if nghiem_an1:
            # Chọn nghiệm đầu tiên (có thể chọn thêm logic chọn nghiệm dương)
            an1_val = nghiem_an1[0]
            pt1_sub = pt1.subs(an_1, an1_val)
            try:
                nghiem_an2 = sp.solve(pt1_sub, an_2)
            except Exception:
                nghiem_an2 = []
            buoc_giai['nghiem_an2'] = nghiem_an2
        else:
            an1_val = None
            nghiem_an2 = []
        # 4. Ghi lại các bước giải bằng LaTeX
        # Trình bày hai phương trình gốc
        buoc_giai['trinh_bay_he_phuong_trinh'] = (
            r'\[\begin{cases}' +
            sp.latex(pt1) + r' \\' +
            sp.latex(pt2) + r'\end{cases}\]'
        )
        # Trình bày phép trừ
        def format_sq(var, val):
            sign = '-' if val >= 0 else '+'
            return f"({var} {sign} {abs(val)})^2"
        # Tùy mặt phẳng, xác định biến và giá trị
        if mat_phang == 'Oxy':
            ac_sq = f"{format_sq('a', diem_a[0])} + {format_sq('b', diem_a[1])}"
            bc_sq = f"{format_sq('a', diem_b[0])} + {format_sq('b', diem_b[1])}"
        elif mat_phang == 'Oyz':
            ac_sq = f"{format_sq('b', diem_a[1])} + {format_sq('c', diem_a[2])}"
            bc_sq = f"{format_sq('b', diem_b[1])} + {format_sq('c', diem_b[2])}"
        else: # Oxz
            ac_sq = f"{format_sq('a', diem_a[0])} + {format_sq('c', diem_a[2])}"
            bc_sq = f"{format_sq('a', diem_b[0])} + {format_sq('c', diem_b[2])}"
        buoc_giai['pt_ac'] = f"{ac_sq} = {ab_binh_phuong}"
        buoc_giai['pt_bc'] = f"{bc_sq} = {ab_binh_phuong}"
        # Trình bày phép trừ chuẩn hóa
        buoc_giai['trinh_bay_tru_pt'] = (
            r'\text{Trừ (2) cho (1): }' +
            f"{bc_sq} - {ac_sq} = 0 \\Rightarrow " + sp.latex(pt_tru_eq)
        )
        # Trình bày nghiệm ẩn thứ nhất
        if nghiem_an1:
            buoc_giai['trinh_bay_nghiem_an1'] = (
                r'\text{Giải ra }' + sp.latex(an_1) + '=' + sp.latex(an1_val)
            )
        else:
            buoc_giai['trinh_bay_nghiem_an1'] = r'\text{(Không giải được ẩn thứ nhất)}'
        # Trình bày thế vào giải ẩn còn lại
        if nghiem_an1 and nghiem_an2:
            buoc_giai['trinh_bay_nghiem_an2'] = (
                r'Thế vào phương trình (1): ' + r'\(' + sp.latex(pt1_sub) + r' \Rightarrow ' + sp.latex(an_2) + '=' + sp.latex(nghiem_an2[0]) + r'\)'
            )
        else:
            buoc_giai['trinh_bay_nghiem_an2'] = r'\text{(Không giải được ẩn thứ hai)}'
        # 5. Kết quả hệ nghiệm
        ket_qua_he = sp.solve((pt1, pt2), an_so_can_tim)
        buoc_giai['ket_qua_he_pt_obj'] = ket_qua_he
        # --- SỬA ĐOẠN CHỌN NGHIỆM ĐÚNG ---
        def is_valid_solution(nghiem):
            # Kiểm tra nghiệm thực
            if not all(val.is_real for val in nghiem):
                return False
            # Với mặt phẳng Oyz, b phải âm (vì A, B đều âm)
            if mat_phang == 'Oyz':
                if not (nghiem[0] < 0):
                    return False
            # Với Oxy, c = 0, nghiệm nào cũng được
            # Với Oxz, b = 0, nghiệm nào cũng được
            # Kiểm tra tam giác đều thực sự
            if mat_phang == 'Oxy':
                diem_c_test = sp.Point3D(nghiem[0], nghiem[1], 0)
            elif mat_phang == 'Oyz':
                diem_c_test = sp.Point3D(0, nghiem[0], nghiem[1])
            else:
                diem_c_test = sp.Point3D(nghiem[0], 0, nghiem[1])
            ab = diem_A_sp.distance(diem_B_sp)
            ac = diem_A_sp.distance(diem_c_test)
            bc = diem_B_sp.distance(diem_c_test)
            # So sánh độ dài thực tế
            return abs(float(ac) - float(ab)) < 1e-6 and abs(float(bc) - float(ab)) < 1e-6
        # Ưu tiên nghiệm phù hợp hình học
        nghiem_tot = [nghiem for nghiem in ket_qua_he if is_valid_solution(nghiem)]
        nghiem_final = nghiem_tot[0] if nghiem_tot else ket_qua_he[0]
        diem_c = diem_C_tuong_trung.subs(zip(an_so_can_tim, nghiem_final))
        # Đảm bảo trả về Point3D
        if not isinstance(diem_c, sp.Point3D):
            def safe_float(x):
                try:
                    return float(x)
                except Exception:
                    try:
                        return float(x.evalf())
                    except Exception:
                        return 0.0
            diem_c = sp.Point3D(*[safe_float(coord) for coord in diem_c.args])
        # Trình bày nghiệm cuối cùng
        nghiem_lines = []
        for idx, an in enumerate(an_so_can_tim):
            nghiem_lines.append(rf"{sp.latex(an)} = {format_number_clean(nghiem_final[idx])}")
        # Thêm giá trị cố định (0) cho tọa độ còn lại
        if mat_phang == 'Oxy':
            nghiem_lines.append(r"c = 0")
        elif mat_phang == 'Oyz':
            nghiem_lines.insert(0, r"a = 0")
        else:
            nghiem_lines.insert(1, r"b = 0")
        buoc_giai['giai_he'] = '\\[' + ',\\ '.join(nghiem_lines) + '\\]'
        # Bổ sung sinh hai khóa pt_ac và pt_bc
        an1 = buoc_giai['an_so_1']
        an2 = buoc_giai['an_so_2']
        if mat_phang == 'Oxy':
            buoc_giai['pt_ac'] = f"({an1} - {diem_a[0]})^2 + ({an2} - {diem_a[1]})^2 = {ab_binh_phuong}"
            buoc_giai['pt_bc'] = f"({an1} - {diem_b[0]})^2 + ({an2} - {diem_b[1]})^2 = {ab_binh_phuong}"
        elif mat_phang == 'Oyz':
            buoc_giai['pt_ac'] = f"({an1} - {diem_a[1]})^2 + ({an2} - {diem_a[2]})^2 = {ab_binh_phuong}"
            buoc_giai['pt_bc'] = f"({an1} - {diem_b[1]})^2 + ({an2} - {diem_b[2]})^2 = {ab_binh_phuong}"
        else:
            buoc_giai['pt_ac'] = f"({an1} - {diem_a[0]})^2 + ({an2} - {diem_a[2]})^2 = {ab_binh_phuong}"
            buoc_giai['pt_bc'] = f"({an1} - {diem_b[0]})^2 + ({an2} - {diem_b[2]})^2 = {ab_binh_phuong}"
        return diem_c, buoc_giai

    @staticmethod
    def _giai_he_luc(vector_da: sp.Point3D, vector_db: sp.Point3D, vector_dc: sp.Point3D, vector_p: sp.Point3D) -> List[
        float]:
        x1, x2, x3 = sp.symbols('x1 x2 x3')
        try:
            ket_qua = sp.solve_linear_system(sp.Matrix((
                (vector_da.x, vector_db.x, vector_dc.x, vector_p.x),
                (vector_da.y, vector_db.y, vector_dc.y, vector_p.y),
                (vector_da.z, vector_db.z, vector_dc.z, vector_p.z)
            )), x1, x2, x3)
            if ket_qua is None:
                return [0.0, 0.0, 0.0]
            return [float(ket_qua.get(x, 0)) for x in (x1, x2, x3)]
        except Exception:
            return [0.0, 0.0, 0.0]

    @staticmethod
    def _tinh_dien_tich_tam_giac(diem_a: sp.Point3D, diem_b: sp.Point3D, diem_c: sp.Point3D, return_detail=False):
        # Tính diện tích tam giác 3D bằng công thức nửa tích có hướng (symbolic)
        ab_vec = diem_b - diem_a
        ac_vec = diem_c - diem_a
        ab = sp.Matrix(ab_vec.args)
        ac = sp.Matrix(ac_vec.args)
        cross = ab.cross(ac)
        dien_tich = sp.Rational(1,2) * cross.norm()
        if not return_detail:
            return dien_tich  # Trả về symbolic
        return {'dien_tich': dien_tich, 'vector_ab_obj': ab_vec, 'vector_ac_obj': ac_vec, 'tich_co_huong_obj': cross}

    # --- SINH ĐỀ BÀI, ĐÁP ÁN, LỜI GIẢI ---
    def generate_question_text(self) -> str:
        p = self.parameters
        # Đảm bảo các biểu thức toán học nằm trong môi trường toán
        d_str = f"D({p['diem_d'][0]} ; {p['diem_d'][1]} ; {p['diem_d'][2]})"
        a_str = f"A({p['diem_a'][0]} ; {p['diem_a'][1]} ; {p['diem_a'][2]})"
        b_str = f"B({p['diem_b'][0]} ; {p['diem_b'][1]} ; {p['diem_b'][2]})"
        c_str = f"C(a ; b ; c)"  # Để đúng format mẫu, không điền số cụ thể
        # Đặt toàn bộ biểu thức vector P vào môi trường toán
        p_vec_str = f"\\(\\overrightarrow{{P}}=({p['vector_luc_p'][0]} ; {p['vector_luc_p'][1]} ; {p['vector_luc_p'][2]})\\)"
        mat_phang = p['mat_phang'].replace('O', 'O ').replace('x', 'x ').replace('y', 'y ').replace('z', 'z ')
        question = rf"""
Trong không gian \(Oxyz\), một vật có trọng lượng \({p['do_lon_luc_p_newton']}N\) đặt trên một giá đỡ ba chân với điểm đặt là {d_str}, là ba điểm tiếp xúc với mặt đất {a_str}, {b_str}, {c_str} nằm trên mặt phẳng \(({mat_phang})\). Biết tọa độ các điểm {a_str}, {b_str}, {c_str}, tam giác \(ABC\) đều. Biết rằng trọng lực {p_vec_str} sẽ ép vào ba thanh DA, DB, DC các lực \(\overrightarrow{{F}}_1, \overrightarrow{{F}}_2, \overrightarrow{{F}}_3\) lần lượt hướng dọc theo các vectơ \(\overrightarrow{{DA}}, \overrightarrow{{DB}}, \overrightarrow{{DC}}\). Theo tính chất Vật Lý thì ta có: \(\overrightarrow{{F_1}}+\overrightarrow{{F_2}}+\overrightarrow{{F_3}}=\overrightarrow{{P}}\).

Hỏi trong các mệnh đề dưới đây, mệnh đề nào đúng, mệnh đề nào sai?

\begin{{center}}
    \begin{{tikzpicture}}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.6]
        \draw[fill=cyan] (0,0)--(1,0)--(1.25,0.25)--(1.25,1)--(0.25,1)--(0,0.75)--cycle;
        \draw (1,0)--(1,0.75)--(0,0.75);
        \draw    (1,0.75)--(1.25,1);
        \draw[black,line width=1pt] (0.5,0)coordinate (D)node[above]{{$D$}}--(-1.5,-4)coordinate (A) node[below]{{$A$}};
        \draw[->,blue,line width=1pt] (0.5,0)--(-0.5,-2)node[left]{{$\overrightarrow{{F}}_1$}};
        \draw[red,->,,line width=1pt] (0.5,0)--(0.5,-2.5) node[below]{{$\overrightarrow{{P}}$}};
        \draw[black,line width=1pt] (0.5,0)--(3,-5)coordinate (B)node[right]{{$B$}};
        \draw[blue,->,line width=1pt] (0.5,0)--(1.5,-2) node[right]{{$\overrightarrow{{F}}_2$}};
        \draw[black,line width=1pt] (0.5,0)--(3,-2.5)coordinate (C)node[right]{{$C$}};
        \draw[blue,->,line width=1pt] (0.5,0)--(1.75,-1.25)node[right]{{$\overrightarrow{{F}}_3$}};
        \fill (A) circle(2pt)(B) circle(2pt)(C) circle(2pt)(D) circle(2pt);
        \draw (-5,-6) --(6,-6)(-5,-6) --(-2.5,-2);
        \clip (-2.5,-2)-- (-5,-6)--(6,-6);
        \draw (-5,-6) circle(2cm) node[above,xshift=0.9cm]{{$Oxy$}};
    \end{{tikzpicture}}
\end{{center}}
"""
        return question.strip()

    def calculate_answer(self) -> str:
        import random
        cache = self._tinh_toan_day_du()
        # --- Sử dụng biểu thức symbolic cho mệnh đề a ---
        symbolic_expr = cache.get('tong_binh_phuong_c_symbolic', None)
        if symbolic_expr is not None:
            a_expr_latex = sp.latex(sp.nsimplify(symbolic_expr, rational=True, tolerance=1e-6))
        else:
            a_expr_latex = format_number_clean(cache['tong_binh_phuong_c'])
        # --- Diện tích tam giác dạng symbolic cho mệnh đề c ---
        # Lấy biểu thức symbolic từ tích có hướng (cross product)
        dien_tich_latex = ''
        dien_tich_wrong_latex = ''
        try:
            cross = cache.get('tich_co_huong_obj', None)
            if cross is not None:
                cross_norm = cross.norm().simplify()
                dien_tich_symbolic = (sp.Rational(1,2) * cross_norm).simplify()
                dien_tich_latex = sp.latex(dien_tich_symbolic)
                # Đáp án sai: cộng/trừ một số nguyên nhỏ vào biểu thức symbolic
                noise = random.choice([-1, 1]) * random.randint(1, 3)
                dien_tich_wrong_symbolic = (dien_tich_symbolic + noise).simplify()
                dien_tich_wrong_latex = sp.latex(dien_tich_wrong_symbolic)
            else:
                dien_tich_latex = ''
                dien_tich_wrong_latex = ''
        except Exception:
            dien_tich_latex = ''
            dien_tich_wrong_latex = ''
        # --- Đơn vị lực dạng symbolic cho mệnh đề b ---
        don_vi_luc_symbolic = None
        # Lỗi linter: phép chia Rational / Pow không hợp lệ, phải nhân với nghịch đảo
        try:
            vector_p = cache.get('vector_p_obj', None)
            do_lon_luc_p_newton = cache.get('do_lon_luc_p_newton', None)
            if vector_p is not None and do_lon_luc_p_newton is not None:
                p_norm = sp.sqrt(sum(sp.sympify(x)**2 for x in vector_p.args))
                don_vi_luc_symbolic = sp.Mul(sp.Rational(do_lon_luc_p_newton, 1), sp.Pow(p_norm, -1, evaluate=False))
                don_vi_luc_latex = sp.latex(don_vi_luc_symbolic)
            else:
                don_vi_luc_latex = format_number_clean(cache['don_vi_luc'])
        except Exception:
            don_vi_luc_latex = format_number_clean(cache['don_vi_luc'])
        correct = [
            f"a) \\(a^2+b^2+c^2={a_expr_latex}\\)",
            f"b) Một đơn vị dài trong hệ trục toạ độ Oxyz tương ứng với độ lớn của lực là \\( {don_vi_luc_latex} \\)",
            f"c) Diện tích tam giác ABC bằng \\( {dien_tich_latex} \\)",
            f"d) Độ lớn của lực \\(\overrightarrow{{F}}_3\\) bằng \\( {format_dimension(round(cache['do_lon_f3_newton']), 'N')} \\) (làm tròn kết quả đến hàng đơn vị khi tính theo newton)."
        ]
        # Mệnh đề sai cho đơn vị lực
        don_vi_luc_wrong_latex = don_vi_luc_latex
        if don_vi_luc_symbolic is not None:
            try:
                noise = random.choice([-1, 1]) * random.randint(1, 3)
                don_vi_luc_wrong = sp.Add(don_vi_luc_symbolic, noise, evaluate=False)
                don_vi_luc_wrong_latex = sp.latex(don_vi_luc_wrong)
            except Exception:
                pass
        wrong = []
        # Sinh đáp án sai cho a) ở dạng symbolic nếu có
        if symbolic_expr is not None:
            noise = random.choice([-1, 1]) * random.randint(1, 3)
            wrong_expr = symbolic_expr + noise
            wrong_a_expr_latex = sp.latex(sp.nsimplify(wrong_expr, rational=True, tolerance=1e-6))
        else:
            wrong_a_expr_latex = format_number_clean(cache['tong_binh_phuong_c'] + random.uniform(1, 3))
        wrong.append(f"a) \\(a^2+b^2+c^2={wrong_a_expr_latex}\\)")
        wrong.append(f"b) Một đơn vị dài trong hệ trục toạ độ Oxyz tương ứng với độ lớn của lực là \\( {don_vi_luc_wrong_latex} \\)")
        wrong.append(f"c) Diện tích tam giác ABC bằng \\( {dien_tich_wrong_latex} \\)")
        # Câu d: đáp án nhiễu luôn nhỏ hơn trọng lượng/2
        trong_luong = cache['do_lon_luc_p_newton']
        max_wrong_f3 = max(1, trong_luong / 2 - 1)
        wrong_f3_value = random.uniform(1, max_wrong_f3)
        wrong.append(f"d) Độ lớn của lực \\(\\overrightarrow{{F}}_3\\) bằng \\( {format_dimension(round(wrong_f3_value), 'N')} \\) (làm tròn kết quả đến hàng đơn vị khi tính theo newton).")
        items = []
        for i in range(4):
            is_true = random.choice([True, False])
            correct_clean = re.sub(r'([abcd])\)\.', r'\1)', correct[i])
            wrong_clean = re.sub(r'([abcd])\)\.', r'\1)', wrong[i])
            if is_true:
                items.append(f"* {correct_clean}")
            else:
                items.append(f"{wrong_clean}")
        return "\\\\\n".join(items)

    def generate_wrong_answers(self) -> List[str]:
        cache = self._tinh_toan_day_du()
        wrongs = set()
        import sympy as sp
        symbolic_expr = cache.get('tong_binh_phuong_c_symbolic', None)
        while len(wrongs) < 3:
            # Đáp án sai cho a^2+b^2+c^2 ở dạng căn thức
            if symbolic_expr is not None:
                noise = random.choice([-1, 1]) * random.randint(1, 3)
                wrong_expr = symbolic_expr + noise
                w_coord = sp.latex(sp.nsimplify(wrong_expr, rational=True, tolerance=1e-6))
            else:
                w_coord = format_number_clean(cache['tong_binh_phuong_c'] + random.uniform(-3, 3))
            w_unit = format_dimension(cache['don_vi_luc'] + random.uniform(-30, 30), 'N')
            w_area = format_number_clean(cache['dien_tich'] * random.uniform(0.7, 1.5))
            w_f3 = format_dimension(round(cache['do_lon_f3_newton'] * random.uniform(0.7, 1.5)), 'N')
            wrong_str = f"a^2+b^2+c^2={w_coord}; 1 đơn vị={w_unit}; S={w_area}; \\overrightarrow{{F}}_{{3}}=\\({w_f3}\\)"
            if wrong_str != self.calculate_answer():
                wrongs.add(wrong_str)
        return list(wrongs)

    def generate_solution(self) -> str:
        p = self._tinh_toan_day_du()
        bgc = p['buoc_giai_c']
        loi_giai = []
        # --- Tính dien_tich_latex để dùng cho toàn bộ lời giải ---
        dien_tich = sp.simplify(0.5 * p['tich_co_huong_obj'].norm())
        dien_tich_latex = sp.latex(sp.nsimplify(dien_tich, rational=True, tolerance=1e-6))
        # --- Sử dụng biểu thức symbolic cho đầu lời giải ---
        symbolic_expr = p.get('tong_binh_phuong_c_symbolic', None)
        if symbolic_expr is not None:
            a_expr_latex = sp.latex(sp.nsimplify(symbolic_expr, rational=True, tolerance=1e-6))
        else:
            a_expr_latex = format_number_clean(p['tong_binh_phuong_c'])
        # a) và c) Tìm tọa độ C, tính a^2+b^2+c^2 và diện tích tam giác
        corrects = []
        # a) a^2+b^2+c^2 đúng nếu giá trị đúng
        corrects.append(f"a) \\(a^2+b^2+c^2={a_expr_latex}\\)")
        # c) Diện tích tam giác ABC đúng nếu giá trị đúng
        # Tính dien_tich_latex nếu chưa có
        try:
            dien_tich_latex
        except NameError:
            dien_tich_latex = sp.latex(sp.nsimplify(p['dien_tich'], rational=True, tolerance=1e-6))
        corrects.append(f"c) Diện tích tam giác ABC bằng \\({dien_tich_latex}\\)")
        loi_giai.append(" và ".join(corrects))
        loi_giai.append("")  # Thêm dòng trống để xuống dòng
        # --- TIẾP THEO: CÁC BƯỚC GIẢI TOÁN ---
        an1 = bgc['an_so_1']
        an2 = bgc['an_so_2']
        # Xác định format tọa độ C ban đầu theo mặt phẳng
        if p['mat_phang'] == 'Oxy':
            c_str = f"C({an1}; {an2}; 0)"
        elif p['mat_phang'] == 'Oyz':
            c_str = f"C(0; {an1}; {an2})"
        else:
            c_str = f"C({an1}; 0; {an2})"
        loi_giai.append(r"+ Bước 1: Tìm tọa độ điểm \(C\) để tam giác \(ABC\) đều.")
        loi_giai.append(f"Do C thuộc ({p['mat_phang']}) nên {c_str}.")
        # Thêm đoạn trình bày AB = ... => AB^2 = ...
        ab_binh_phuong = bgc.get('ab_binh_phuong_obj', None)
        if ab_binh_phuong is not None:
            ab_binh_phuong_val = float(ab_binh_phuong)
            ab_val = math.sqrt(ab_binh_phuong_val)
            ab_binh_phuong_latex = sp.latex(sp.nsimplify(ab_binh_phuong, rational=False, tolerance=1e-6))
            ab_latex = sp.latex(sp.nsimplify(ab_val, rational=False, tolerance=1e-6))
            loi_giai.append(rf"\[ AB = {ab_latex} \Rightarrow AB^2 = {ab_binh_phuong_latex} \]")
        loi_giai.append(r"\begin{align}")
        def format_minus_minus(expr_str):
            if expr_str is None:
                return ''
            return expr_str.replace('- -', '+')
        loi_giai.append(rf"AC^2 = {format_minus_minus(bgc.get('pt_ac', '...'))} \tag{{1}} \\")
        loi_giai.append(rf"BC^2 = {format_minus_minus(bgc.get('pt_bc', '...'))} \tag{{2}}")
        loi_giai.append(r"\end{align}")
        # Phép trừ hai phương trình, giải ra ẩn thứ nhất
        default_trinh_bay_tru_pt = r'(\text{Trừ (2) cho (1): ...})'
        loi_giai.append("\\[" + bgc.get('trinh_bay_tru_pt', default_trinh_bay_tru_pt) + "\\]")
        # Thế nghiệm vào phương trình còn lại, giải ra ẩn thứ hai
        default_trinh_bay_nghiem_an2 = r'(\text{Thế nghiệm vào, giải ẩn còn lại ...})'
        loi_giai.append(bgc.get('trinh_bay_nghiem_an2', default_trinh_bay_nghiem_an2))
        # Dòng kết luận (sử dụng biểu thức đẹp)
        # Lấy nghiệm symbolic từ bước giải hệ phương trình
        nghiem_duong = bgc.get('ket_qua_he_pt_obj', [(0,0)])[0]
        if p['mat_phang'] == 'Oxy':
            a_expr, b_expr, c_expr = nghiem_duong[0], nghiem_duong[1], 0
        elif p['mat_phang'] == 'Oyz':
            a_expr, b_expr, c_expr = 0, nghiem_duong[0], nghiem_duong[1]
        else:
            a_expr, b_expr, c_expr = nghiem_duong[0], 0, nghiem_duong[1]
        diem_c_fmt = f"{format_symbolic_latex(a_expr)}; {format_symbolic_latex(b_expr)}; {format_symbolic_latex(c_expr)}"
        loi_giai.append(rf"\[C = ({diem_c_fmt}) \Rightarrow a^2+b^2+c^2={a_expr_latex}\]")
        # Định nghĩa hàm vector_latex trước khi sử dụng (chỉ một lần duy nhất)
        def vector_latex(vec):
            if hasattr(vec, 'tolist'):
                vals = vec.tolist()
                if all(isinstance(v, list) and len(v) == 1 for v in vals):
                    vals = [v[0] for v in vals]
                elif isinstance(vals, list) and len(vals) == 1 and isinstance(vals[0], list):
                    vals = vals[0]
            elif hasattr(vec, 'args'):
                vals = vec.args
            else:
                vals = vec
            def pretty(v):
                try:
                    v = sp.nsimplify(v, rational=False, tolerance=1e-6)
                    v = sp.simplify(v)
                except Exception:
                    pass
                return sp.latex(v)
            return '(' + '; '.join([pretty(v) for v in vals]) + ')'
        # + Bước 2: Tính các vector AB, AC
        loi_giai.append(r"+ Bước 2: Tính các vectơ \(\overrightarrow{AB}\), \(\overrightarrow{AC}\):")
        loi_giai.append(rf"\[ \overrightarrow{{AB}} = \overrightarrow{{B}} - \overrightarrow{{A}} = {vector_latex(p['vector_ab_obj'])} \]")
        loi_giai.append(rf"\[ \overrightarrow{{AC}} = \overrightarrow{{C}} - \overrightarrow{{A}} = {vector_latex(p['vector_ac_obj'])} \]")
        # + Bước 3: Tính tích có hướng
        loi_giai.append(r"+ Bước 3: Tính tích có hướng \(\left[\overrightarrow{AB}, \overrightarrow{AC}\right]\):")
        loi_giai.append(rf"\[ [\overrightarrow{{AB}},  \overrightarrow{{AC}}] = {vector_latex(p['tich_co_huong_obj'])} \]")
        # + Bước 4: Tính diện tích tam giác
        loi_giai.append(r"+ Bước 4: Tính diện tích tam giác:")
        ab = p['vector_ab_obj']
        ac = p['vector_ac_obj']
        cross = p['tich_co_huong_obj']
        cross_norm = cross.norm().simplify()
        cross_norm_sqrt = sp.latex(sp.sqrt(sp.nsimplify(cross_norm**2, rational=True, tolerance=1e-6)))
        cross_norm_latex = sp.latex(sp.nsimplify(cross_norm, rational=False, tolerance=1e-6))
        dien_tich = sp.simplify(0.5 * cross.norm())
        dien_tich_latex = sp.latex(sp.nsimplify(dien_tich, rational=True, tolerance=1e-6))
        dien_tich_float = f"{float(dien_tich):.3f}".rstrip('0').rstrip('.')
        loi_giai.append(r"\[")
        loi_giai.append(r"S = \frac{1}{2} \left\| \overrightarrow{AB} \times \overrightarrow{AC} \right\| = \frac{1}{2} \cdot " + cross_norm_sqrt)
        # loi_giai.append(r"= \frac{1}{2} \cdot (" + cross_norm_latex + ")" )
        loi_giai.append(r"= " + dien_tich_latex)
        loi_giai.append(r"\]")
        loi_giai.append(rf"\[\text{{Diện tích tam giác }} ABC = {dien_tich_latex}\]")
        # b) Đơn vị lực
        # b) Đơn vị lực dạng symbolic
        try:
            vector_p = p.get('vector_p_obj', None)
            do_lon_luc_p_newton = p.get('do_lon_luc_p_newton', None)
            if vector_p is not None and do_lon_luc_p_newton is not None:
                p_norm = sp.sqrt(sum(sp.sympify(x)**2 for x in vector_p.args))
                don_vi_luc_symbolic = sp.Mul(sp.Rational(do_lon_luc_p_newton, 1), sp.Pow(p_norm, -1, evaluate=False))
                don_vi_luc_latex = sp.latex(don_vi_luc_symbolic)
            else:
                don_vi_luc_latex = format_number_clean(p['don_vi_luc'])
        except Exception:
            don_vi_luc_latex = format_number_clean(p['don_vi_luc'])
        loi_giai.append(r"b) Một đơn vị dài trong hệ trục toạ độ Oxyz tương ứng với độ lớn của lực là \({}\).".format(don_vi_luc_latex) + "\n\n")
        loi_giai.append(
            r"Ta có: \(|\overrightarrow{{P}}| = {}\) ứng với \({}\) nên một đơn vị độ dài ứng với \({}\).".format(
                sp.latex(p_norm) if 'p_norm' in locals() else format_number_clean(float(p['do_lon_vector_p_obj'])),
                sp.latex(do_lon_luc_p_newton) if do_lon_luc_p_newton is not None else format_dimension(p['do_lon_luc_p_newton'], 'N'),
                don_vi_luc_latex
            ) + "\n\n"
        )
        # d) Độ lớn của lực F3
        # Định nghĩa lại các hàm và biến cần thiết cho phần lời giải câu d
        def get_coords(vec):
            if hasattr(vec, 'args'):
                return vec.args
            elif hasattr(vec, 'x') and hasattr(vec, 'y') and hasattr(vec, 'z'):
                return [vec.x, vec.y, vec.z]
            else:
                return vec
        da_coords = get_coords(p['vector_da_obj'])
        db_coords = get_coords(p['vector_db_obj'])
        dc_coords = get_coords(p['vector_dc_obj'])
        p_coords = get_coords(p['vector_p_obj'])
        def format_coord_simple(c):
            try:
                c = sp.nsimplify(c, rational=True, tolerance=1e-6)
                if isinstance(c, sp.Integer):
                    return str(c)
                elif isinstance(c, sp.Rational):
                    if abs(c.p) > 1000 or abs(c.q) > 1000:
                        return f"{float(c):.3f}".rstrip('0').rstrip('.')
                    return sp.latex(c)
                elif isinstance(c, sp.Pow) and c.exp == sp.Rational(1, 2):
                    return sp.latex(c)
                else:
                    return f"{float(c):.3f}".rstrip('0').rstrip('.')
            except:
                return f"{float(c):.3f}".rstrip('0').rstrip('.')
        def format_coord_for_eq(c):
            try:
                c = sp.nsimplify(c, rational=True, tolerance=1e-6)
                if isinstance(c, sp.Integer):
                    return str(c)
                elif isinstance(c, sp.Rational):
                    if abs(c.p) > 1000 or abs(c.q) > 1000:
                        return f"{float(c):.3f}".rstrip('0').rstrip('.')
                    return sp.latex(c)
                elif isinstance(c, sp.Pow) and c.exp == sp.Rational(1, 2):
                    return sp.latex(c)
                else:
                    return f"{float(c):.3f}".rstrip('0').rstrip('.')
            except:
                return f"{float(c):.3f}".rstrip('0').rstrip('.')
        # Định nghĩa hàm vector_latex trước khi sử dụng (chỉ một lần duy nhất)
        def vector_latex2(vec):
            if hasattr(vec, 'tolist'):
                vals = vec.tolist()
                if all(isinstance(v, list) and len(v) == 1 for v in vals):
                    vals = [v[0] for v in vals]
                elif isinstance(vals, list) and len(vals) == 1 and isinstance(vals[0], list):
                    vals = vals[0]
            elif hasattr(vec, 'args'):
                vals = vec.args
            else:
                vals = vec
            def pretty(v):
                try:
                    v = sp.nsimplify(v, rational=True, tolerance=1e-6)
                except Exception:
                    pass
                if isinstance(v, sp.Pow) and v.exp == sp.Rational(1, 2):
                    return sp.latex(v)
                if isinstance(v, sp.Integer):
                    return sp.latex(v)
                if isinstance(v, sp.Rational):
                    if abs(v.p) > 1000 or abs(v.q) > 1000:
                        return f"{float(v):.3f}".rstrip('0').rstrip('.')
                    return sp.latex(v)
                if isinstance(v, sp.Float) or isinstance(v, float):
                    if abs(v) < 1e-8:
                        return '0'
                    return f"{float(v):.3f}".rstrip('0').rstrip('.')
                return sp.latex(v)
            return '(' + ', '.join([pretty(v) for v in vals]) + ')'
        # Bổ sung khai triển phép trừ từng thành phần cho DA, DB, DC
        diem_d = p['diem_d']
        diem_a = p['diem_a']
        diem_b = p['diem_b']
        diem_c = p['diem_c']
        loi_giai.append("\n\nd) Độ lớn của \(\overrightarrow{F}_3\) (làm tròn kết quả đến hàng đơn vị khi tính theo newton)." + "\n\n")
        loi_giai.append("+ Tính các vectơ từ D đến A, B, C:" + "\n\n")
        loi_giai.append(rf"\[ \overrightarrow{{DA}} = ({diem_a[0]} - {diem_d[0]}, {diem_a[1]} - {diem_d[1]}, {diem_a[2]} - {diem_d[2]}) = ({format_coord_simple(da_coords[0])}; {format_coord_simple(da_coords[1])}; {format_coord_simple(da_coords[2])}) \]")
        loi_giai.append(rf"\[ \overrightarrow{{DB}} = ({diem_b[0]} - {diem_d[0]}, {diem_b[1]} - {diem_d[1]}, {diem_b[2]} - {diem_d[2]}) = ({format_coord_simple(db_coords[0])}; {format_coord_simple(db_coords[1])}; {format_coord_simple(db_coords[2])}) \]")
        # DC chỉ xuất kết quả cuối cùng dạng căn thức
        nghiem_duong = bgc.get('ket_qua_he_pt_obj', [(0,0)])[0]
        if p['mat_phang'] == 'Oxy':
            c_symbolic = [nghiem_duong[0], nghiem_duong[1], 0]
        elif p['mat_phang'] == 'Oyz':
            c_symbolic = [0, nghiem_duong[0], nghiem_duong[1]]
        else:
            c_symbolic = [nghiem_duong[0], 0, nghiem_duong[1]]
        d_symbolic = p['diem_d']
        dc_symbolic = [sp.simplify(c_symbolic[i] - d_symbolic[i]) for i in range(3)]
        dc_symbolic_latex = "; ".join([sp.latex(sp.nsimplify(x, rational=False, tolerance=1e-6)) for x in dc_symbolic])
        loi_giai.append(rf"\[ \overrightarrow{{DC}} = ({dc_symbolic_latex}) \]")
        loi_giai.append("\n\nDo \(\overrightarrow{F_1},\overrightarrow{F_2}, \overrightarrow{F_3}\) lần lượt cùng phương với \(\overrightarrow{DA}, \overrightarrow{DB}, \overrightarrow{DC}\) nên ta có:" + "\n\n")
        loi_giai.append(r"\[ \overrightarrow{F_1} = x_1 \cdot \overrightarrow{DA},\quad \overrightarrow{F_2} = x_2 \cdot \overrightarrow{DB},\quad \overrightarrow{F_3} = x_3 \cdot \overrightarrow{DC} \]")
        loi_giai.append(r"\[ \Rightarrow x_1 \cdot \overrightarrow{DA} + x_2 \cdot \overrightarrow{DB} + x_3 \cdot \overrightarrow{DC} = \overrightarrow{P} \]")
        loi_giai.append(rf"\[ x_1({format_coord_simple(da_coords[0])}; {format_coord_simple(da_coords[1])}; {format_coord_simple(da_coords[2])}) + x_2({format_coord_simple(db_coords[0])}; {format_coord_simple(db_coords[1])}; {format_coord_simple(db_coords[2])}) + x_3({dc_symbolic_latex}) = ({format_coord_simple(p_coords[0])}; {format_coord_simple(p_coords[1])}; {format_coord_simple(p_coords[2])}) \]")
        loi_giai.append("\n\nKhai triển hệ phương trình:" + "\n\n")
        # Sử dụng sympy.latex với nsimplify để luôn xuất ra căn/phân số
        def format_latex_coef(val):
            import sympy as sp
            try:
                simp = sp.nsimplify(val, rational=False, tolerance=1e-6)
                latex_str = sp.latex(simp)
                # Nếu là số nguyên, số thực ngắn, hoặc phân số mẫu nhỏ thì không cần ngoặc
                if (isinstance(simp, sp.Integer) or
                    (isinstance(simp, sp.Rational) and abs(simp.q) < 1000) or
                    (isinstance(simp, sp.Float) or isinstance(simp, float))):
                    return latex_str
                # Nếu là biểu thức phức tạp, căn, tổng, hiệu, tích... thì thêm ngoặc
                if (isinstance(simp, sp.Add) or isinstance(simp, sp.Mul) or simp.is_Pow):
                    return f"\\left({latex_str}\\right)"
                return latex_str
            except Exception:
                return str(val)

        loi_giai.append(r"\[")
        loi_giai.append(r"\begin{cases}")
        loi_giai.append(rf"{format_latex_coef(da_coords[0])}x_1 + {format_latex_coef(db_coords[0])}x_2 + {format_latex_coef(dc_coords[0])}x_3 = {format_latex_coef(p_coords[0])} \\")
        loi_giai.append(rf"{format_latex_coef(da_coords[1])}x_1 + {format_latex_coef(db_coords[1])}x_2 + {format_latex_coef(dc_coords[1])}x_3 = {format_latex_coef(p_coords[1])} \\")
        loi_giai.append(rf"{format_latex_coef(da_coords[2])}x_1 + {format_latex_coef(db_coords[2])}x_2 + {format_latex_coef(dc_coords[2])}x_3 = {format_latex_coef(p_coords[2])}")
        loi_giai.append(r"\end{cases}")
        loi_giai.append(r"\Leftrightarrow")
        loi_giai.append(r"\begin{cases}")
        loi_giai.append(rf"x_1 \approx {format_number_clean(p['he_so_luc'][0], 6)} \\")
        loi_giai.append(rf"x_1 \approx {format_number_clean(p['he_so_luc'][1], 6)} \\")
        loi_giai.append(rf"x_1 \approx {format_number_clean(p['he_so_luc'][2], 6)} \\")
        loi_giai.append(r"\end{cases}")
        loi_giai.append(r"\]")
        loi_giai.append("+ Tính độ lớn của \(\overrightarrow{DC}\):" + "\n\n")
        loi_giai.append(rf"\[ |\overrightarrow{{DC}}| = \sqrt{{{format_coord_simple(dc_coords[0])}^2 + {format_coord_simple(dc_coords[1])}^2 + {format_coord_simple(dc_coords[2])}^2}} = {format_number_clean(float(p['dc_magnitude_obj']), 3)} \]")
        loi_giai.append("+ Tính độ lớn của \(\overrightarrow{F_3}\) theo đơn vị độ dài:" + "\n\n")
        loi_giai.append(rf"\[ |\overrightarrow{{F_3}}| = x_3 \cdot |\overrightarrow{{DC}}| \approx {format_number_clean(p['he_so_luc'][2], 6)} \cdot {format_number_clean(float(p['dc_magnitude_obj']), 3)} = {format_number_clean(float(p['do_lon_f3_don_vi_dai']), 3)} \]")
        loi_giai.append("+ Đổi sang đơn vị Newton:" + "\n\n")
        loi_giai.append(rf"\[ |\overrightarrow{{F_3}}| \approx {format_number_clean(float(p['do_lon_f3_don_vi_dai']), 3)} \cdot {format_number_clean(p['don_vi_luc'])} = {format_number_clean(round(p['do_lon_f3_newton']))}\,\mathrm{{N}} \]")
        loi_giai.append(rf"\[|\overrightarrow{{F_3}}| = {format_number_clean(round(p['do_lon_f3_newton']))}\,\mathrm{{N}}\]")
        return clean_and_optimize_latex("\n".join(loi_giai))


# ========================================================================================
# PHẦN 3: KHUNG CHẠY CHƯƠNG TRÌNH (Tham khảo từ extremum.py)
# ========================================================================================

class QuestionManager:
    def __init__(self, question_types: List[Type[BaseOptimizationQuestion]]):
        self.question_types = question_types

    def generate_questions(self, num_questions: int, output_format: int) -> List[Any]:
        questions_data = []
        for i in range(1, num_questions + 1):
            try:
                question_type = random.choice(self.question_types)
                instance = question_type()
                questions_data.append(instance.generate_question_package(i, output_format == 1))
            except Exception as e:
                print(f"Lỗi tạo câu hỏi {i}: {e}", file=sys.stderr)
        return questions_data


class LaTeXDocumentBuilder:
    HEADER = r"""
\documentclass[a4paper,12pt]{{article}}
\usepackage{{amsmath}}
\usepackage{{mathtools}}

\usepackage{{amsfonts}}
\usepackage{{amssymb}}
\usepackage{{geometry}}
\geometry{{a4paper, margin=1in}}
\usepackage{{polyglossia}}
\setmainlanguage{{vietnamese}}
\setmainfont{{Times New Roman}}
\usepackage{{tikz}}
\usepackage{{tkz-tab}}
\usepackage{{tkz-euclide}}
\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}

\begin{{document}}
\title{{{title}}}
\author{{{author}}}
\maketitle
"""
    FOOTER = "\n\\end{document}"
    ANSWER_HEADER = "\n\\section*{Đáp án}\n"

    def build_document(self, questions_data: List[Any], title: str, output_format: int, author: str) -> str:
        content = self.HEADER.format(title=title, author=author)
        if output_format == 1:
            content += "\n\n".join(questions_data)
        else:
            questions = [q[0] for q in questions_data]
            answers = [q[1] for q in questions_data]
            content += "\n\n".join(questions)
            content += self.ANSWER_HEADER
            for idx, answer in enumerate(answers, 1):
                content += f"Câu {idx}: {answer}\n"
        content += self.FOOTER
        return content


def main():
    """Hàm main: điều phối toàn bộ quá trình sinh câu hỏi và xuất ra file LaTeX."""
    parser = argparse.ArgumentParser(description="Generator câu hỏi cân bằng lực.")
    parser.add_argument('num_questions', nargs='?', type=int, default=3, help='Số câu hỏi cần tạo.')
    parser.add_argument('format', nargs='?', type=int, choices=[1, 2], default=1,
                        help='Format output: 1=đáp án ngay sau, 2=đáp án ở cuối.')
    parser.add_argument('-o', '--output', type=str, default="cau_hoi_can_bang_luc.tex", help='Tên file output.')
    parser.add_argument('-t', '--title', type=str, default="Bài tập Cân bằng lực", help='Tiêu đề document.')
    args = parser.parse_args()

    try:
        manager = QuestionManager(question_types=[ForceEquilibriumQuestion])
        questions_data = manager.generate_questions(args.num_questions, args.format)

        builder = LaTeXDocumentBuilder()
        latex_content = builder.build_document(questions_data, args.title, args.format, "Dev")

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(latex_content)

        print(f"✅ Đã tạo thành công file '{args.output}' với {len(questions_data)} câu hỏi.")
        print(f"   Biên dịch bằng: xelatex {args.output}")

    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import sys
    # Nếu chạy trong Jupyter/Colab, sys.argv sẽ có tham số kernel json, cần loại bỏ
    if 'ipykernel' in sys.modules:
        sys.argv = [sys.argv[0]]
    main()
