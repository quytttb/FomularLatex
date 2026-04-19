#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ===================== THÔNG TIN BỘ DẠNG (SET 2) =====================
# Dạng 5: Hình chiếu điểm lên mặt phẳng, độ dài AH — gồm Ví dụ 5, Câu 6
# Dạng 6: Đối xứng qua mặt phẳng, tính độ dài AB — gồm Câu 7, Câu 8
# Dạng 7: Khoảng cách giữa hai mặt phẳng song song — gồm Ví dụ 6, Câu 9, Câu 10
# Dạng 8: Điều kiện khoảng cách có tham số (m1, m2), tính m1 m2 |m1 + m2| — gồm Ví dụ 7
# =====================================================================

import math
import random
from typing import List, Tuple, Dict, Optional
from fractions import Fraction
from dataclasses import dataclass


# --------------------- Hằng số cấu hình sinh dữ liệu ---------------------
COORD_RANGE = (-4, 5)
SMALL_COORD_RANGE = (-3, 4)
PLANE_COEFF_RANGE = (-5, 6)
CONST_TERM_RANGE = (-8, 9)
DISTANCE_DELTA_OPTIONS = [1, 2, 3]


# ----------------------------- Kiểu dữ liệu ------------------------------
@dataclass
class PlaneParams:
    a: int
    b: int
    c: int
    d: int


@dataclass
class Point3D:
    x: int
    y: int
    z: int

    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.x, self.y, self.z)


# ----------------------------- Tiện ích hình học -----------------------------
def are_collinear(v: Tuple[int, int, int], w: Tuple[int, int, int]) -> bool:
    x1, y1, z1 = v
    x2, y2, z2 = w
    return (x1 * y2 == y1 * x2) and (x1 * z2 == z1 * x2) and (y1 * z2 == z1 * y2)


def format_point3d(point: Point3D) -> str:
    return f"({point.x};{point.y};{point.z})"


def format_point(pt: Tuple[int, int, int]) -> str:
    return f"({pt[0]};{pt[1]};{pt[2]})"


def format_plane_equation(a: int, b: int, c: int, d: int) -> str:
    parts: List[str] = []
    if a == 1:
        parts.append("x")
    elif a == -1:
        parts.append("-x")
    elif a != 0:
        parts.append(f"{a}x")
    if b != 0:
        if parts:
            if b == 1:
                parts.append("+ y")
            elif b == -1:
                parts.append("- y")
            elif b > 0:
                parts.append(f"+ {b}y")
            else:
                parts.append(f"- {abs(b)}y")
        else:
            if b == 1:
                parts.append("y")
            elif b == -1:
                parts.append("-y")
            else:
                parts.append(f"{b}y")
    if c != 0:
        if parts:
            if c == 1:
                parts.append("+ z")
            elif c == -1:
                parts.append("- z")
            elif c > 0:
                parts.append(f"+ {c}z")
            else:
                parts.append(f"- {abs(c)}z")
        else:
            if c == 1:
                parts.append("z")
            elif c == -1:
                parts.append("-z")
            else:
                parts.append(f"{c}z")
    if d != 0:
        if d > 0 and parts:
            parts.append(f"+ {d}")
        else:
            parts.append(str(d))
    if not parts:
        parts.append("0")
    return " ".join(parts) + " = 0"


def format_plane_params(plane: PlaneParams) -> str:
    return format_plane_equation(plane.a, plane.b, plane.c, plane.d)


def format_distance(numer: int, norm_sq: int) -> str:
    if norm_sq == 0:
        return "0"
    return f"\\dfrac{{{numer}}}{{\\sqrt{{{norm_sq}}}}}"


# ----------------------------- Bộ sinh ngẫu nhiên -----------------------------
class PlaneGenerator:
    @staticmethod
    def random_coefficients(
        coeff_range: Tuple[int, int] = COORD_RANGE,
        ensure_non_zero: bool = True,
    ) -> Tuple[int, int, int]:
        low, high = coeff_range
        domain = list(range(low, high + 1))
        a = b = c = 0
        if ensure_non_zero:
            for _ in range(10):
                a = random.choice(domain)
                b = random.choice(domain)
                c = random.choice(domain)
                if not (a == 0 and b == 0 and c == 0):
                    break
            if a == 0 and b == 0 and c == 0:
                a = 1
        else:
            a = random.choice(domain)
            b = random.choice(domain)
            c = random.choice(domain)
        return a, b, c

    @staticmethod
    def random_plane(
        coeff_range: Tuple[int, int] = PLANE_COEFF_RANGE,
        const_range: Tuple[int, int] = CONST_TERM_RANGE,
        ensure_non_zero: bool = True,
    ) -> PlaneParams:
        a, b, c = PlaneGenerator.random_coefficients(coeff_range, ensure_non_zero)
        d = random.randint(*const_range)
        return PlaneParams(a, b, c, d)

    @staticmethod
    def parallel_plane(base_plane: PlaneParams, scale_factor: Optional[int] = None) -> PlaneParams:
        if scale_factor is None:
            scale_factor = random.choice([2, 3, -2, -3, 1])
        a2 = scale_factor * base_plane.a
        b2 = scale_factor * base_plane.b
        c2 = scale_factor * base_plane.c
        d2 = random.randint(*CONST_TERM_RANGE)
        while d2 == scale_factor * base_plane.d:
            d2 = random.randint(*CONST_TERM_RANGE)
        return PlaneParams(a2, b2, c2, d2)


class PointGenerator:
    @staticmethod
    def random_point(coord_range: Tuple[int, int] = SMALL_COORD_RANGE) -> Point3D:
        x = random.randint(*coord_range)
        y = random.randint(*coord_range)
        z = random.randint(*coord_range)
        return Point3D(x, y, z)


class DistanceCalculator:
    @staticmethod
    def point_to_plane(plane: PlaneParams, point: Point3D) -> Tuple[int, int]:
        numer = abs(plane.a * point.x + plane.b * point.y + plane.c * point.z + plane.d)
        norm_sq = plane.a * plane.a + plane.b * plane.b + plane.c * plane.c
        return numer, norm_sq

    @staticmethod
    def between_parallel_planes(plane1: PlaneParams, plane2: PlaneParams) -> Tuple[int, int]:
        a1, b1, c1, d1 = plane1.a, plane1.b, plane1.c, plane1.d
        a2, b2, c2, d2 = plane2.a, plane2.b, plane2.c, plane2.d
        n1_sq = a1 * a1 + b1 * b1 + c1 * c1
        if n1_sq == 0:
            return 0, 1
        if not are_collinear((a1, b1, c1), (a2, b2, c2)):
            return 0, 1
        if a1 == a2 and b1 == b2 and c1 == c2:
            return abs(d1 - d2), n1_sq
        k: Optional[Fraction] = None
        for u1, u2 in ((a1, a2), (b1, b2), (c1, c2)):
            if u1 != 0:
                k = Fraction(u2, u1)
                break
        if k is None:
            return 0, 1
        d2_prime = Fraction(d2, 1) / k
        diff = Fraction(d1, 1) - d2_prime
        numer = abs(diff.numerator)
        denom = diff.denominator
        norm_sq = n1_sq * (denom * denom)
        return numer, norm_sq


# ----------------------------- Các mệnh đề (dạng) -----------------------------
def prop_point_projection_distance() -> Dict[str, str]:
    plane = PlaneGenerator.random_plane(COORD_RANGE, CONST_TERM_RANGE)
    point = PointGenerator.random_point(SMALL_COORD_RANGE)
    numer, norm_sq = DistanceCalculator.point_to_plane(plane, point)
    true_text = (
        f"Gọi H là hình chiếu của điểm A{format_point3d(point)} lên mặt phẳng \\((P): {format_plane_params(plane)}\\). "
        f"Độ dài đoạn \\(AH\\) bằng \\({format_distance(numer, norm_sq)}\\)."
    )
    delta = random.choice(DISTANCE_DELTA_OPTIONS)
    false_numer = numer + delta if numer > 0 else numer + 2
    false_text = (
        f"Gọi H là hình chiếu của điểm A{format_point3d(point)} lên mặt phẳng \\((P): {format_plane_params(plane)}\\). "
        f"Độ dài đoạn \\(AH\\) bằng \\({format_distance(false_numer, norm_sq)}\\)."
    )
    return {"true": true_text, "false": false_text}


def prop_reflection_segment_length() -> Dict[str, str]:
    low, high = COORD_RANGE
    a = random.choice([v for v in range(low, high + 1) if v != 0])
    b = random.randint(*COORD_RANGE)
    c = random.randint(*COORD_RANGE)
    d = random.randint(-6, 6)
    A = (random.randint(*SMALL_COORD_RANGE), random.randint(*SMALL_COORD_RANGE), random.randint(*SMALL_COORD_RANGE))
    numer = abs(a * A[0] + b * A[1] + c * A[2] + d)
    norm_sq = a * a + b * b + c * c
    true_text = (
        f"Gọi B là điểm đối xứng của A{format_point(A)} qua mặt phẳng (P): {format_plane_equation(a,b,c,d)}. "
        f"Khi đó độ dài \\(AB\\) bằng \\({format_distance(2 * numer, norm_sq)}\\)."
    )
    delta = random.choice([1, 2])
    false_text = (
        f"Gọi B là điểm đối xứng của A{format_point(A)} qua mặt phẳng (P): {format_plane_equation(a,b,c,d)}. "
        f"Khi đó độ dài \\(AB\\) bằng \\({format_distance(2 * numer + delta, norm_sq)}\\)."
    )
    return {"true": true_text, "false": false_text}


def prop_distance_between_parallel_planes() -> Dict[str, str]:
    plane1 = PlaneGenerator.random_plane(SMALL_COORD_RANGE, (-8, 9))
    plane2 = PlaneGenerator.parallel_plane(plane1, scale_factor=1)
    numer, norm_sq = DistanceCalculator.between_parallel_planes(plane1, plane2)
    true_text = (
        f"Khoảng cách giữa hai mặt phẳng \\((P): {format_plane_params(plane1)}\\) và \\((Q): {format_plane_params(plane2)}\\) "
        f"bằng \\({format_distance(numer, norm_sq)}\\)."
    )
    delta = random.choice([1, 2])
    false_numer = numer + delta
    false_text = (
        f"Khoảng cách giữa hai mặt phẳng \\((P): {format_plane_params(plane1)}\\) và \\((Q): {format_plane_params(plane2)}\\) "
        f"bằng \\({format_distance(false_numer, norm_sq)}\\)."
    )
    return {"true": true_text, "false": false_text}


def prop_complex_distance_condition() -> Dict[str, str]:
    a = random.choice([1, 2])
    b = random.choice([1, 2])
    c = random.choice([1, 2])
    A = (1, 1, 1)
    target_distance = random.choice([1, 2])
    S = a + b + c
    N2 = a * a + b * b + c * c
    product = S * S - (target_distance * target_distance) * N2
    sum_m_abs = 2 * abs(S)
    result = abs(product) * sum_m_abs
    true_text = (
        f"Cho mặt phẳng \\((P): {a}x + {b}y + {c}z + m = 0\\) và điểm A{format_point(A)}. "
        f"Có hai giá trị \\(m_1, m_2\\) thỏa mãn \\(d(A,(P)) = {target_distance}\\). "
        f"Giá trị \\(m_1 m_2 |m_1 + m_2|\\) bằng \\({result}\\)."
    )
    false_result = result + random.choice([N2, -N2, 2 * N2, -2 * N2])
    false_text = (
        f"Cho mặt phẳng \\((P): {a}x + {b}y + {c}z + m = 0\\) và điểm A{format_point(A)}. "
        f"Có hai giá trị \\(m_1, m_2\\) thỏa mãn \\(d(A,(P)) = {target_distance}\\). "
        f"Giá trị \\(m_1 m_2 |m_1 + m_2|\\) bằng \\({false_result}\\)."
    )
    return {"true": true_text, "false": false_text}


# ----------------------------- Gom nhóm DẠNG -----------------------------
PART_GROUPS: List[List] = [
    [prop_point_projection_distance],
    [prop_reflection_segment_length],
    [prop_distance_between_parallel_planes],
    [prop_complex_distance_condition],
]


# ----------------------------- Sinh câu hỏi + LaTeX -----------------------------
def generate_question(question_number: int) -> str:
    selected_group = random.choice(PART_GROUPS)
    primary_gen = random.choice(selected_group)
    all_gens = [g for grp in PART_GROUPS for g in grp]
    remaining_pool = [g for g in all_gens if g not in selected_group]
    if len(remaining_pool) >= 3:
        other_gens = random.sample(remaining_pool, 3)
    else:
        other_gens = [random.choice(remaining_pool) for _ in range(3)] if remaining_pool else [primary_gen] * 3
    selected_gens = [primary_gen] + other_gens
    propositions: List[Dict[str, str]] = [gen() for gen in selected_gens]
    num_true = random.randint(1, 4)
    true_indices = set(random.sample(range(4), num_true))
    option_labels = ['a', 'b', 'c', 'd']
    content = f"Câu {question_number}: Chọn các mệnh đề đúng.\n\n"
    for i in range(4):
        if i in true_indices:
            text = propositions[i]['true']
            marker = '*'
        else:
            text = propositions[i]['false']
            marker = ''
        content += f"{marker}{option_labels[i]}) {text}\n\n"
    return content


def create_latex_document(questions: List[str], title: str = "Part A - Set 2 (Dạng 5-8)") -> str:
    latex = (
        "\\documentclass[a4paper,12pt]{article}\n"
        "\\usepackage{amsmath,amssymb}\n"
        "\\usepackage{geometry}\n"
        "\\geometry{a4paper, margin=1in}\n"
        "\\usepackage{polyglossia}\n"
        "\\setmainlanguage{vietnamese}\n"
        "\\setmainfont{Times New Roman}\n"
        "\\begin{document}\n\n"
        f"\\section*{{{title}}}\n\n"
    )
    latex += "\n\n".join(questions)
    latex += "\n\n\\end{document}"
    return latex


def main():
    import sys
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    except Exception:
        num_questions = 5
    random.seed()
    questions = [generate_question(i + 1) for i in range(num_questions)]
    tex = create_latex_document(questions)
    out = "plane_true_false_part_A_set2.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(questions)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()




