#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ===================== THÔNG TIN BỘ DẠNG (SET 1) =====================
# Dạng 1: Xác định VTPT từ phương trình mặt phẳng — gồm Ví dụ 1, Câu 1
# Dạng 2: Tìm VTPT từ cặp véctơ chỉ phương (tích có hướng) — gồm Ví dụ 2, Câu 2
# Dạng 3: Điểm thuộc mặt phẳng; tham số m để điểm thuộc mặt phẳng — gồm Ví dụ 3, Câu 3, Câu 4
# Dạng 4: Khoảng cách từ điểm đến mặt phẳng — gồm Ví dụ 4, Câu 5
# =====================================================================

import math
import random
from typing import List, Tuple, Dict
from fractions import Fraction
from dataclasses import dataclass


# --------------------- Hằng số cấu hình sinh dữ liệu ---------------------
COORD_RANGE = (-4, 5)
SMALL_COORD_RANGE = (-3, 4)
PLANE_COEFF_RANGE = (-5, 6)
CONST_TERM_RANGE = (-8, 9)
DISTANCE_DELTA_OPTIONS = [1, 2, 3]
FALSE_COORD_DELTA = [-1, 1]
MAX_RETRIES = 100


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


class PointGenerator:
    @staticmethod
    def random_point(coord_range: Tuple[int, int] = SMALL_COORD_RANGE) -> Point3D:
        x = random.randint(*coord_range)
        y = random.randint(*coord_range)
        z = random.randint(*coord_range)
        return Point3D(x, y, z)


# ----------------------------- Tính toán hình học -----------------------------
class DistanceCalculator:
    @staticmethod
    def point_to_plane(plane: PlaneParams, point: Point3D) -> Tuple[int, int]:
        numer = abs(plane.a * point.x + plane.b * point.y + plane.c * point.z + plane.d)
        norm_sq = plane.a * plane.a + plane.b * plane.b + plane.c * plane.c
        return numer, norm_sq


# ----------------------------- Tiện ích/Định dạng -----------------------------
def are_collinear(v: Tuple[int, int, int], w: Tuple[int, int, int]) -> bool:
    x1, y1, z1 = v
    x2, y2, z2 = w
    return (x1 * y2 == y1 * x2) and (x1 * z2 == z1 * x2) and (y1 * z2 == z1 * y2)


def cross(u: Tuple[int, int, int], v: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return (
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    )


def format_point(pt: Tuple[int, int, int]) -> str:
    return f"({pt[0]};{pt[1]};{pt[2]})"


def format_point3d(point: Point3D) -> str:
    return f"({point.x};{point.y};{point.z})"


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


# ----------------------------- Bộ sinh mệnh đề -----------------------------
def prop_normal_vector_from_equation() -> Dict[str, str]:
    low, high = SMALL_COORD_RANGE
    a = random.choice([v for v in range(low, high + 1) if v != 0])
    b = random.randint(*SMALL_COORD_RANGE)
    c = random.choice([v for v in range(low, high + 1) if v != 0])
    d = random.randint(-6, 6)
    true_normal = (a, b, c)
    false_options = [
        (-a, b, c),
        (a, -b, c),
        (a, b, -c),
        (a, b, d),
        (a + 1, b, c),
    ]
    candidates = [w for w in false_options if w != (0, 0, 0) and not are_collinear(true_normal, w)]
    if not candidates:
        for _ in range(MAX_RETRIES):
            w = (random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3))
            if w != (0, 0, 0) and not are_collinear(true_normal, w):
                candidates.append(w)
                break
        if not candidates:
            candidates.append((true_normal[0] + 1, true_normal[1] + 2, true_normal[2] + 3))
    false_normal = random.choice(candidates)
    plane_eq = format_plane_equation(a, b, c, d)
    true_text = f"Véctơ \\(\\vec{{n}} = {format_point(true_normal)}\\) là một véctơ pháp tuyến của mặt phẳng \\((P): {plane_eq}\\)."
    false_text = f"Véctơ \\(\\vec{{n}} = {format_point(false_normal)}\\) là một véctơ pháp tuyến của mặt phẳng \\((P): {plane_eq}\\)."
    return {"true": true_text, "false": false_text}


def prop_normal_vector_from_direction_vectors() -> Dict[str, str]:
    u = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
    v = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
    while are_collinear(u, v) or u == (0, 0, 0) or v == (0, 0, 0):
        u = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
        v = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
    true_normal = cross(u, v)
    candidates = [
        (true_normal[0] + 1, true_normal[1], true_normal[2]),
        (true_normal[0], true_normal[1] + 1, true_normal[2]),
        (true_normal[0], true_normal[1], true_normal[2] + 1),
        (true_normal[0] + 1, true_normal[1] + 1, true_normal[2]),
        (u[0] + v[0], u[1] + v[1], u[2] + v[2]),
    ]
    filtered = [w for w in candidates if w != (0, 0, 0) and not are_collinear(true_normal, w)]
    if not filtered:
        for _ in range(20):
            w = (random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3))
            if w != (0, 0, 0) and not are_collinear(true_normal, w):
                filtered.append(w)
                break
        if not filtered:
            filtered.append((true_normal[0] + 1, true_normal[1] + 2, true_normal[2] + 3))
    false_normal = random.choice(filtered)
    true_text = (
        f"Véctơ \\(\\vec{{n}} = {format_point(true_normal)}\\) là một véctơ pháp tuyến của mặt phẳng "
        f"có cặp véctơ chỉ phương \\(\\vec{{u}} = {format_point(u)}\\), \\(\\vec{{v}} = {format_point(v)}\\)."
    )
    false_text = (
        f"Véctơ \\(\\vec{{n}} = {format_point(false_normal)}\\) là một véctơ pháp tuyến của mặt phẳng "
        f"có cặp véctơ chỉ phương \\(\\vec{{u}} = {format_point(u)}\\), \\(\\vec{{v}} = {format_point(v)}\\)."
    )
    return {"true": true_text, "false": false_text}


def prop_point_on_plane_membership() -> Dict[str, str]:
    low, high = COORD_RANGE
    a = random.choice([v for v in range(low, high + 1) if v != 0])
    b = random.randint(*COORD_RANGE)
    c = random.randint(*COORD_RANGE)
    d = random.randint(-6, 6)
    x = random.randint(*SMALL_COORD_RANGE)
    y = random.randint(*SMALL_COORD_RANGE)
    if c == 0:
        z = random.randint(*SMALL_COORD_RANGE)
        d = -(a * x + b * y)
    else:
        numerator = -(a * x + b * y + d)
        if numerator % c == 0:
            z = numerator // c
        else:
            z = random.randint(*SMALL_COORD_RANGE)
            d = -(a * x + b * y + c * z)
    P = (x, y, z)
    true_text = f"Điểm M{format_point(P)} thuộc mặt phẳng \\((P): {format_plane_equation(a, b, c, d)}\\)."
    Pf = (P[0] + random.choice(FALSE_COORD_DELTA), P[1], P[2])
    false_text = f"Điểm M{format_point(Pf)} thuộc mặt phẳng \\((P): {format_plane_equation(a, b, c, d)}\\)."
    return {"true": true_text, "false": false_text}


def prop_point_with_m_on_plane() -> Dict[str, str]:
    low, high = SMALL_COORD_RANGE
    for _ in range(MAX_RETRIES):
        a = random.choice([v for v in range(low, high + 1) if v != 0])
        b = random.randint(*SMALL_COORD_RANGE)
        c = random.randint(*SMALL_COORD_RANGE)
        d = random.randint(-6, 6)
        coeff_m = a + b + 2 * c
        if coeff_m != 0:
            break
    else:
        a, b, c, d = 1, 0, 0, 0
        coeff_m = 1
    const_term = -b + c + d
    frac = Fraction(-const_term, coeff_m)
    if frac.denominator == 1:
        m_display = str(frac.numerator)
    else:
        m_display = f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
    true_text = (
        f"Với \\(m = {m_display}\\), điểm \\(A(m;\\, m-1;\\, 1+2m)\\) thuộc mặt phẳng "
        f"\\((P): {format_plane_equation(a, b, c, d)}\\)."
    )
    if frac.denominator == 1:
        m_false_val = frac.numerator + random.choice([1, -1, 2, -2])
        m_false_display = str(m_false_val)
    else:
        candidates = [0, 1, -1, 2, -2]
        candidates = [v for v in candidates if Fraction(v, 1) != frac]
        m_false_display = str(random.choice(candidates))
    false_text = (
        f"Với \\(m = {m_false_display}\\), điểm \\(A(m;\\, m-1;\\, 1+2m)\\) thuộc mặt phẳng "
        f"\\((P): {format_plane_equation(a, b, c, d)}\\)."
    )
    return {"true": true_text, "false": false_text}


def prop_point_plane_distance() -> Dict[str, str]:
    plane = PlaneGenerator.random_plane(PLANE_COEFF_RANGE, CONST_TERM_RANGE)
    point = PointGenerator.random_point(COORD_RANGE)
    numer, norm_sq = DistanceCalculator.point_to_plane(plane, point)
    true_text = (
        f"Khoảng cách từ điểm A{format_point3d(point)} đến mặt phẳng (P): {format_plane_params(plane)} "
        f"bằng \\( {format_distance(numer, norm_sq)} \\)."
    )
    delta = random.choice(DISTANCE_DELTA_OPTIONS)
    false_numer = numer + delta if numer != 0 else numer + 2
    false_text = (
        f"Khoảng cách từ điểm A{format_point3d(point)} đến mặt phẳng (P): {format_plane_params(plane)} "
        f"bằng \\( {format_distance(false_numer, norm_sq)} \\)."
    )
    return {"true": true_text, "false": false_text}


# ----------------------------- Gom nhóm DẠNG -----------------------------
# Mỗi phần tử là 1 DẠNG; một dạng có thể chứa 1 hoặc nhiều generator cùng chủ đề
PART_GROUPS: List[List] = [
    [prop_normal_vector_from_equation],
    [prop_normal_vector_from_direction_vectors],
    [prop_point_on_plane_membership, prop_point_with_m_on_plane],
    [prop_point_plane_distance],
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


def create_latex_document(questions: List[str], title: str = "Part A - Set 1 (Dạng 1-4)") -> str:
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
    out = "plane_true_false_part_A_set1.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(questions)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()




