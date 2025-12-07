import argparse
import logging
import math
import random
import sys
from math import gcd
from typing import Any, Dict, List, Tuple


Point = Tuple[int, int, int]
Vector = Tuple[int, int, int]


def dot(u: Vector, v: Vector) -> int:
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


def cross(u: Vector, v: Vector) -> Vector:
    return (
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    )


def add(u: Point, v: Vector) -> Point:
    return u[0] + v[0], u[1] + v[1], u[2] + v[2]


def sub(u: Point, v: Point) -> Vector:
    return u[0] - v[0], u[1] - v[1], u[2] - v[2]


def scale(v: Vector, k: int) -> Vector:
    return v[0] * k, v[1] * k, v[2] * k


def norm_sq(v: Vector) -> int:
    return dot(v, v)


def gcd_multiple(values: Tuple[int, ...]) -> int:
    g = 0
    for value in values:
        if value != 0:
            g = gcd(g, abs(value)) if g else abs(value)
    return g or 1


def simplify_vector(v: Vector) -> Vector:
    g = gcd_multiple(v)
    return v[0] // g, v[1] // g, v[2] // g


def format_point(p: Point) -> str:
    return f"({p[0]};{p[1]};{p[2]})"


def append_linear_term(parts: List[str], coeff: int, text: str) -> None:
    if coeff == 0:
        return
    if not parts:
        if coeff == 1:
            parts.append(text)
        elif coeff == -1:
            parts.append(f"-{text}")
        else:
            parts.append(f"{coeff}{text}")
    else:
        if coeff == 1:
            parts.append(f"+ {text}")
        elif coeff == -1:
            parts.append(f"- {text}")
        elif coeff > 0:
            parts.append(f"+ {coeff}{text}")
        else:
            parts.append(f"- {abs(coeff)}{text}")


def append_constant(parts: List[str], value: int) -> None:
    if value == 0:
        return
    if not parts:
        parts.append(str(value))
    elif value > 0:
        parts.append(f"+ {value}")
    else:
        parts.append(f"- {abs(value)}")


def format_plane_equation(a: int, b: int, c: int, d: int) -> str:
    parts: List[str] = []
    append_linear_term(parts, a, "x")
    append_linear_term(parts, b, "y")
    append_linear_term(parts, c, "z")
    append_constant(parts, d)
    if not parts:
        parts.append("0")
    return " ".join(parts) + " = 0"


def format_square_term(var: str, shift: int) -> str:
    if shift == 0:
        return f"{var}^2"
    if shift > 0:
        return f"({var} - {shift})^2"
    return f"({var} + {abs(shift)})^2"


def format_sphere_center_form(center: Point, radius_sq: int) -> str:
    term_x = format_square_term("x", center[0])
    term_y = format_square_term("y", center[1])
    term_z = format_square_term("z", center[2])
    return f"{term_x} + {term_y} + {term_z} = {radius_sq}"


def format_sphere_expanded(center: Point, radius_sq: int) -> str:
    a, b, c = center
    A = -2 * a
    B = -2 * b
    C = -2 * c
    D = a * a + b * b + c * c - radius_sq
    parts: List[str] = ["x^2 + y^2 + z^2"]
    append_linear_term(parts, A, "x")
    append_linear_term(parts, B, "y")
    append_linear_term(parts, C, "z")
    append_constant(parts, D)
    return " ".join(parts) + " = 0"


def format_param_line(base: Point, direction: Vector) -> str:
    rows: List[str] = []
    for name, b, d in zip(("x", "y", "z"), base, direction):
        if d == 0:
            rows.append(f"{name} = {b}")
        else:
            sign = "+" if d > 0 else "-"
            coeff = abs(d)
            if coeff == 1:
                term = "t"
            else:
                term = f"{coeff}t"
            rows.append(f"{name} = {b} {sign} {term}")
    joined = " \\\\\n".join(rows)
    return "\\begin{cases}\n" + joined + "\n\\end{cases}"


def format_canonical_line(base: Point, direction: Vector) -> str:
    parts: List[str] = []
    for name, b, d in zip(("x", "y", "z"), base, direction):
        if d == 0:
            continue
        if b == 0:
            numerator = name
        elif b > 0:
            numerator = f"{name} - {b}"
        else:
            numerator = f"{name} + {abs(b)}"
        if d == 1:
            parts.append(numerator)
        elif d == -1:
            parts.append(f"-({numerator})")
        else:
            parts.append(f"\\dfrac{{{numerator}}}{{{d}}}")
    return " = ".join(parts)


def format_linear_combination(coeffs: Tuple[int, int, int], symbols: Tuple[str, str, str]) -> str:
    parts: List[str] = []
    for coeff, symbol in zip(coeffs, symbols):
        append_linear_term(parts, coeff, symbol)
    return " ".join(parts) if parts else "0"


def format_affine_term(base: int, coefficient: int) -> str:
    if coefficient == 0:
        return str(base)
    if coefficient > 0:
        if coefficient == 1:
            return f"{base} + t"
        return f"{base} + {coefficient}t"
    if coefficient == -1:
        return f"{base} - t"
    return f"{base} - {abs(coefficient)}t"


def format_signed_product(coeff: int, expr: str, first: bool = False) -> str:
    if coeff == 0:
        return ""
    if first:
        if coeff == 1:
            return expr
        if coeff == -1:
            return f"-{expr}"
        return f"{coeff}{expr}"
    if coeff == 1:
        return f"+ {expr}"
    if coeff == -1:
        return f"- {expr}"
    if coeff > 0:
        return f"+ {coeff}{expr}"
    return f"- {abs(coeff)}{expr}"


def random_point(min_val: int = -4, max_val: int = 4) -> Point:
    return (
        random.randint(min_val, max_val),
        random.randint(min_val, max_val),
        random.randint(min_val, max_val),
    )


def random_nonzero_vector(min_val: int = -4, max_val: int = 4) -> Vector:
    for _ in range(200):
        v = random_point(min_val, max_val)
        if v != (0, 0, 0):
            return v
    return (1, 0, 0)


def perpendicular_vector(direction: Vector) -> Vector:
    candidates = [
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
        (1, 1, 0),
        (1, 0, 1),
        (0, 1, 1),
    ]
    for cand in candidates:
        v = cross(direction, cand)
        if v != (0, 0, 0):
            return simplify_vector(v)
    fallback = (direction[1], -direction[0], direction[2] if direction[2] != 0 else 1)
    return simplify_vector(fallback)


def format_line_expression(line_data: Dict[str, Any]) -> str:
    direction = line_data["direction"]
    # Chỉ dùng dạng chính tắc nếu cả 3 thành phần đều khác 0
    if line_data.get("style") == "canonical" and all(d != 0 for d in direction):
        expr = format_canonical_line(line_data["point"], direction)
        if expr:
            return expr
    return format_param_line(line_data["point"], direction)


def format_sphere_expression(sphere_data: Dict[str, Any]) -> str:
    if sphere_data["type"] == "center":
        return format_sphere_center_form(sphere_data["center"], sphere_data["radius_sq"])
    return format_sphere_expanded(sphere_data["center"], sphere_data["radius_sq"])


def pick_wrong_integer(true_value: int) -> int:
    deltas = [i for i in range(-7, 8) if i != 0]
    random.shuffle(deltas)
    for delta in deltas:
        candidate = true_value + delta
        if candidate != true_value:
            return candidate
    return true_value + 5


def sqrt_term(value: int) -> str:
    if value == 1:
        return "1"
    return f"\\sqrt{{{value}}}"


def angle_denominator(norm_u: int, norm_v: int) -> str:
    term_u = sqrt_term(norm_u)
    term_v = sqrt_term(norm_v)
    if term_u == "1" and term_v == "1":
        return "1"
    if term_u == "1":
        return term_v
    if term_v == "1":
        return term_u
    return f"{term_u} \\cdot {term_v}"


def format_angle_expression(kind: str, numerator: int, norm_u: int, norm_v: int) -> str:
    denominator = angle_denominator(norm_u, norm_v)
    if denominator == "1":
        fraction = str(numerator)
    else:
        fraction = f"\\dfrac{{{numerator}}}{{{denominator}}}"
    if kind == "cos":
        return f"\\arccos\\left({fraction}\\right)"
    return f"\\arcsin\\left({fraction}\\right)"


def compute_angle_degree(kind: str, numerator: int, norm_a: int, norm_b: int) -> int:
    # kind: 'cos' or 'sin'; norms are squared lengths
    den = math.sqrt(max(0.0, float(norm_a))) * math.sqrt(max(0.0, float(norm_b)))
    if den == 0:
        return 0
    ratio = max(0.0, min(1.0, float(numerator) / den))
    rad = math.acos(ratio) if kind == "cos" else math.asin(ratio)
    return int(round(math.degrees(rad)))


def adjust_numerator(numerator: int, den_sq: int) -> int:
    limit = max(1, int(math.isqrt(den_sq)))
    candidates = [numerator + d for d in (-2, -1, 1, 2) if 0 <= numerator + d <= limit]
    for cand in candidates:
        if cand != numerator:
            return cand
    if numerator < limit:
        return numerator + 1
    return max(0, numerator - 1)


class SpatialGeometryQuestion:
    def __init__(self) -> None:
        self.parameters: Dict[str, Any] = {}

    def _make_line(self, label: str) -> Dict[str, Any]:
        point = random_point(-4, 4)
        direction = random_nonzero_vector(-3, 3)
        style = "canonical" if random.random() < 0.5 else "param"
        return {"label": label, "point": point, "direction": direction, "style": style}

    def _normalize_plane(self, normal: Vector, d: int) -> Tuple[Vector, int]:
        g = gcd_multiple((normal[0], normal[1], normal[2], d))
        if g != 0:
            normal = (normal[0] // g, normal[1] // g, normal[2] // g)
            d //= g
        if normal[0] < 0 or (normal[0] == 0 and normal[1] < 0) or (normal[0] == 0 and normal[1] == 0 and normal[2] < 0):
            normal = (-normal[0], -normal[1], -normal[2])
            d = -d
        return normal, d

    def _build_statement_a(self) -> Dict[str, Any]:
        line = self._make_line("d_1")
        normal = random_nonzero_vector(-3, 3)
        while dot(normal, line["direction"]) == 0:
            normal = random_nonzero_vector(-3, 3)
        intersection = line["point"]
        plane_d = -dot(normal, intersection)
        normal, plane_d = self._normalize_plane(simplify_vector(normal), plane_d)
        plane = {"label": "P_1", "normal": normal, "d": plane_d}
        expr_coeffs = (
            random.choice([-2, -1, 1, 2, 3]),
            random.choice([-2, -1, 1, 2, 3]),
            random.choice([-2, -1, 1, 2, 3]),
        )
        while expr_coeffs == (0, 0, 0):
            expr_coeffs = (
                random.choice([-2, -1, 1, 2, 3]),
                random.choice([-2, -1, 1, 2, 3]),
                random.choice([-2, -1, 1, 2, 3]),
            )
        value = (
            expr_coeffs[0] * intersection[0]
            + expr_coeffs[1] * intersection[1]
            + expr_coeffs[2] * intersection[2]
        )
        wrong = pick_wrong_integer(value)
        coeff_line = dot(normal, line["direction"])
        return {
            "line": line,
            "plane": plane,
            "intersection": intersection,
            "expr_coeffs": expr_coeffs,
            "value": value,
            "wrong": wrong,
            "coeff_line": coeff_line,
        }

    def _build_statement_b(self) -> Dict[str, Any]:
        line = self._make_line("d_2")
        dir_norm = norm_sq(line["direction"])
        step = random.randint(2, 4)
        radius_sq = dir_norm * step * step
        sphere_type = random.choice(["center", "expanded"])
        sphere = {
            "label": "S_2",
            "center": line["point"],
            "radius_sq": radius_sq,
            "type": sphere_type,
        }
        point_a = add(line["point"], scale(line["direction"], step))
        point_b = add(line["point"], scale(line["direction"], -step))
        coeffs = (
            random.choice([-3, -2, -1, 1, 2, 3]),
            random.choice([-3, -2, -1, 1, 2, 3]),
            random.choice([-3, -2, -1, 1, 2, 3]),
        )
        while coeffs == (0, 0, 0):
            coeffs = (
                random.choice([-3, -2, -1, 1, 2, 3]),
                random.choice([-3, -2, -1, 1, 2, 3]),
                random.choice([-3, -2, -1, 1, 2, 3]),
            )
        value = (
            coeffs[0] * (point_a[0] + point_b[0])
            + coeffs[1] * (point_a[1] + point_b[1])
            + coeffs[2] * (point_a[2] + point_b[2])
        )
        wrong = pick_wrong_integer(value)
        return {
            "line": line,
            "sphere": sphere,
            "points": (point_a, point_b),
            "coeffs": coeffs,
            "value": value,
            "wrong": wrong,
            "step": step,
            "dir_norm": dir_norm,
        }

    def _build_statement_c(self) -> Dict[str, Any]:
        if random.random() < 0.5:
            normal = random_nonzero_vector(-3, 3)
            normal = simplify_vector(normal)
            H = random_point(-3, 3)
            plane_d = -dot(normal, H)
            normal, plane_d = self._normalize_plane(normal, plane_d)
            shift = random.choice([1, 2, 3])
            sign = random.choice([-1, 1])
            M = add(H, scale(normal, sign * shift))
            normal_norm = norm_sq(normal)
            plane_numerator = dot(normal, M) + plane_d
            value = sum(H)
            wrong = pick_wrong_integer(value)
            return {
                "target_type": "plane",
                "plane": {"label": "P_2", "normal": normal, "d": plane_d},
                "H": H,
                "M": M,
                "value": value,
                "wrong": wrong,
                "normal_norm": normal_norm,
                "plane_numerator": plane_numerator,
            }
        line = self._make_line("d_3")
        s = random.randint(-2, 2)
        H = add(line["point"], scale(line["direction"], s))
        offset = perpendicular_vector(line["direction"])
        M = add(H, offset)
        vector_PM = sub(M, line["point"])
        dir_norm = norm_sq(line["direction"])
        proj_numerator = dot(vector_PM, line["direction"])
        value = sum(H)
        wrong = pick_wrong_integer(value)
        return {
            "target_type": "line",
            "line": line,
            "H": H,
            "M": M,
            "value": value,
            "wrong": wrong,
            "vector_PM": vector_PM,
            "dir_norm": dir_norm,
            "proj_numerator": proj_numerator,
        }

    def _build_statement_d(self) -> Dict[str, Any]:
        if random.random() < 0.5:
            line1 = self._make_line("d_4")
            line2 = self._make_line("d_5")
            while cross(line1["direction"], line2["direction"]) == (0, 0, 0):
                line2 = self._make_line("d_5")
            dot_val = dot(line1["direction"], line2["direction"])
            numerator = abs(dot_val)
            norm_u = norm_sq(line1["direction"])
            norm_v = norm_sq(line2["direction"])
            angle_true = format_angle_expression("cos", numerator, norm_u, norm_v)
            wrong_num = adjust_numerator(numerator, norm_u * norm_v)
            if wrong_num == numerator:
                wrong_num = max(0, numerator - 1)
            angle_false = format_angle_expression("cos", wrong_num, norm_u, norm_v)
            deg_true = compute_angle_degree("cos", numerator, norm_u, norm_v)
            deg_false = compute_angle_degree("cos", wrong_num, norm_u, norm_v)
            return {
                "type": "line_line",
                "line1": line1,
                "line2": line2,
                "dot_product": dot_val,
                "numerator": numerator,
                "norm_u": norm_u,
                "norm_v": norm_v,
                "angle_true": angle_true,
                "angle_false": angle_false,
                "deg_true": deg_true,
                "deg_false": deg_false,
                "wrong_numerator": wrong_num,
            }
        line = self._make_line("d_4")
        normal = random_nonzero_vector(-3, 3)
        while dot(normal, line["direction"]) == 0:
            normal = random_nonzero_vector(-3, 3)
        point_plane = random_point(-3, 3)
        plane_d = -dot(normal, point_plane)
        normal, plane_d = self._normalize_plane(simplify_vector(normal), plane_d)
        numerator = abs(dot(normal, line["direction"]))
        norm_u = norm_sq(line["direction"])
        norm_n = norm_sq(normal)
        angle_true = format_angle_expression("sin", numerator, norm_n, norm_u)
        wrong_num = adjust_numerator(numerator, norm_n * norm_u)
        if wrong_num == numerator:
            wrong_num = max(0, numerator - 1)
        angle_false = format_angle_expression("sin", wrong_num, norm_n, norm_u)
        deg_true = compute_angle_degree("sin", numerator, norm_n, norm_u)
        deg_false = compute_angle_degree("sin", wrong_num, norm_n, norm_u)
        return {
            "type": "line_plane",
            "line": line,
            "plane": {"label": "P_3", "normal": normal, "d": plane_d},
            "numerator": numerator,
            "norm_u": norm_u,
            "norm_n": norm_n,
            "angle_true": angle_true,
            "angle_false": angle_false,
            "deg_true": deg_true,
            "deg_false": deg_false,
            "wrong_numerator": wrong_num,
        }

    def generate_parameters(self) -> Dict[str, Any]:
        params = {
            "a": self._build_statement_a(),
            "b": self._build_statement_b(),
            "c": self._build_statement_c(),
            "d": self._build_statement_d(),
        }
        self.parameters = params
        return params

    def generate_question(self, question_number: int) -> str:
        params = self.generate_parameters()

        statements_info: List[Dict[str, object]] = []

        # Statement a
        data_a = params["a"]
        expr_a = format_linear_combination(data_a["expr_coeffs"], ("a", "b", "c"))
        line_a_expr = format_line_expression(data_a["line"])
        plane_a_eq = format_plane_equation(
            data_a["plane"]["normal"][0],
            data_a["plane"]["normal"][1],
            data_a["plane"]["normal"][2],
            data_a["plane"]["d"],
        )
        line_label_a_math = f"\\({data_a['line']['label']}\\)"
        plane_label_a_math = f"\\({data_a['plane']['label']}\\)"
        plane_label_a_phrase = f"({plane_label_a_math})"
        true_text_a = (
            f"Cho đường thẳng {line_label_a_math}: \\({line_a_expr}\\) "
            f"và mặt phẳng {plane_label_a_phrase}: \\({plane_a_eq}\\). "
            f"Giao điểm của {line_label_a_math} và {plane_label_a_phrase} là A(a,b,c). Khi đó \\({expr_a} = {data_a['value']}\\)."
        )
        false_text_a = true_text_a.replace(f"= {data_a['value']}\\)", f"= {data_a['wrong']}\\)")
        statements_info.append(
            {
                "label": "a",
                "true_text": true_text_a,
                "false_text": false_text_a,
                "display_true": data_a["value"],
                "display_false": data_a["wrong"],
            }
        )

        # Statement b
        data_b = params["b"]
        line_b_expr = format_line_expression(data_b["line"])
        sphere_eq = format_sphere_expression(data_b["sphere"])
        line_label_b_math = f"\\({data_b['line']['label']}\\)"
        sphere_label_b_math = f"\\({data_b['sphere']['label']}\\)"
        sphere_label_b_phrase = f"({sphere_label_b_math})"
        comb_parts: List[str] = []
        append_linear_term(comb_parts, data_b["coeffs"][0], "(a + x)")
        append_linear_term(comb_parts, data_b["coeffs"][1], "(b + y)")
        append_linear_term(comb_parts, data_b["coeffs"][2], "(c + z)")
        comb_expr = " ".join(comb_parts) if comb_parts else "0"
        true_text_b = (
            f"Cho đường thẳng {line_label_b_math}: \\({line_b_expr}\\) "
            f"và mặt cầu {sphere_label_b_phrase}: \\({sphere_eq}\\). "
            f"Giao điểm của {line_label_b_math} và {sphere_label_b_phrase} là A(a,b,c), B(x,y,z). Khi đó \\({comb_expr} = {data_b['value']}\\)."
        )
        false_text_b = true_text_b.replace(f"= {data_b['value']}\\)", f"= {data_b['wrong']}\\)")
        statements_info.append(
            {
                "label": "b",
                "true_text": true_text_b,
                "false_text": false_text_b,
                "display_true": data_b["value"],
                "display_false": data_b["wrong"],
            }
        )

        # Statement c
        data_c = params["c"]
        if data_c["target_type"] == "plane":
            plane_c_eq = format_plane_equation(
                data_c["plane"]["normal"][0],
                data_c["plane"]["normal"][1],
                data_c["plane"]["normal"][2],
                data_c["plane"]["d"],
            )
            plane_label_c_math = f"\\({data_c['plane']['label']}\\)"
            plane_label_c_phrase = f"({plane_label_c_math})"
            true_text_c = (
                f"Cho điểm M{format_point(data_c['M'])}. Hình chiếu vuông góc của M lên mặt phẳng {plane_label_c_phrase}: \\({plane_c_eq}\\)"
                f" là H(x,y,z). Khi đó \\(x + y + z = {data_c['value']}\\)."
            )
            false_text_c = true_text_c.replace(f"= {data_c['value']}\\)", f"= {data_c['wrong']}\\)")
        else:
            line_c_expr = format_line_expression(data_c["line"])
            line_label_c_math = f"\\({data_c['line']['label']}\\)"
            true_text_c = (
                f"Cho điểm M{format_point(data_c['M'])}. Hình chiếu vuông góc của M lên đường thẳng {line_label_c_math}: \\({line_c_expr}\\) "
                f"là H(x,y,z). Khi đó \\(x + y + z = {data_c['value']}\\)."
            )
            false_text_c = true_text_c.replace(f"= {data_c['value']}\\)", f"= {data_c['wrong']}\\)")
        statements_info.append(
            {
                "label": "c",
                "true_text": true_text_c,
                "false_text": false_text_c,
                "display_true": data_c["value"],
                "display_false": data_c["wrong"],
            }
        )

        # Statement d
        data_d = params["d"]
        if data_d["type"] == "line_line":
            line1_expr = format_line_expression(data_d["line1"])
            line2_expr = format_line_expression(data_d["line2"])
            line1_label_math = f"\\({data_d['line1']['label']}\\)"
            line2_label_math = f"\\({data_d['line2']['label']}\\)"
            true_text_d = (
                f"Cho {line1_label_math}: \\({line1_expr}\\) "
                f"và {line2_label_math}: \\({line2_expr}\\). "
                f"Góc giữa {line1_label_math} và {line2_label_math} bằng \\({data_d['deg_true']}^{{\\circ}}\\)."
            )
            false_text_d = true_text_d.replace(
                f"\\({data_d['deg_true']}^{{\\circ}}\\)", f"\\({data_d['deg_false']}^{{\\circ}}\\)"
            )
            display_true_d = f"{data_d['deg_true']}^{{\\circ}}"
            display_false_d = f"{data_d['deg_false']}^{{\\circ}}"
        else:
            line_d_expr = format_line_expression(data_d["line"])
            plane_d_eq = format_plane_equation(
                data_d["plane"]["normal"][0],
                data_d["plane"]["normal"][1],
                data_d["plane"]["normal"][2],
                data_d["plane"]["d"],
            )
            line_label_d_math = f"\\({data_d['line']['label']}\\)"
            plane_label_d_math = f"\\({data_d['plane']['label']}\\)"
            plane_label_d_phrase = f"({plane_label_d_math})"
            true_text_d = (
                f"Cho {line_label_d_math}: \\({line_d_expr}\\) "
                f"và mặt phẳng {plane_label_d_phrase}: \\({plane_d_eq}\\). "
                f"Góc giữa {line_label_d_math} và {plane_label_d_phrase} bằng \\({data_d['deg_true']}^{{\\circ}}\\)."
            )
            false_text_d = true_text_d.replace(
                f"\\({data_d['deg_true']}^{{\\circ}}\\)", f"\\({data_d['deg_false']}^{{\\circ}}\\)"
            )
            display_true_d = f"{data_d['deg_true']}^{{\\circ}}"
            display_false_d = f"{data_d['deg_false']}^{{\\circ}}"
        statements_info.append(
            {
                "label": "d",
                "true_text": true_text_d,
                "false_text": false_text_d,
                "display_true": display_true_d,
                "display_false": display_false_d,
            }
        )

        num_true = random.randint(1, 4)
        true_indices = set(random.sample(range(4), num_true))

        option_labels = ["a", "b", "c", "d"]
        question_lines: List[str] = []
        solutions: List[str] = ["Lời giải."]
        correct_labels: List[str] = []

        for idx, statement in enumerate(statements_info):
            is_true = idx in true_indices
            text = statement["true_text"] if is_true else statement["false_text"]
            displayed_value = statement["display_true"] if is_true else statement["display_false"]
            prefix = "*" if is_true else ""
            question_lines.append(f"{prefix}{option_labels[idx]}) {text}")
            if is_true:
                correct_labels.append(option_labels[idx])

            label = statement["label"]
            if label == "a":
                data = params["a"]
                line = data["line"]
                plane = data["plane"]
                expr = format_linear_combination(data["expr_coeffs"], ("a", "b", "c"))
                
                # Format phương trình đường thẳng
                line_expr = format_line_expression(line)
                
                # Format phương trình mặt phẳng
                plane_eq = format_plane_equation(
                    plane["normal"][0], plane["normal"][1], plane["normal"][2], plane["d"]
                )
                
                # Thay tọa độ điểm trên đường thẳng vào phương trình mặt phẳng
                parts: List[str] = []
                for coeff, base_val, dir_val in zip(
                    plane["normal"], line["point"], line["direction"]
                ):
                    parts.append(
                        format_signed_product(
                            coeff,
                            f"({format_affine_term(base_val, dir_val)})",
                            first=not parts,
                        )
                    )
                lhs = " ".join(part for part in parts if part)
                plane_d = plane["d"]
                if plane_d != 0:
                    sign = "+" if plane_d > 0 else "-"
                    term = f"{abs(plane_d)}"
                    lhs = f"{lhs} {sign} {term}" if lhs else (term if plane_d > 0 else f"-{term}")
                lhs = lhs.strip() + " = 0"
                
                # Tính vế phải đúng: -(n·P0 + d) (bằng 0 vì P0 ở trên đường thẳng qua giao điểm)
                rhs = -(dot(plane["normal"], line["point"]) + plane["d"])
                
                status = " \\quad(\\text{đúng})" if is_true else f" \\neq {displayed_value} \\Rightarrow \\text{{sai}}"
                
                solution_text = (
                    f"a) Thay tọa độ điểm trên đường thẳng \\({data['line']['label']}\\) vào phương trình mặt phẳng "
                    f"\\(({data['plane']['label']})\\): \\({plane_eq}\\).\n\n"
                    f"Ta có: \\({lhs}\\)\n\n"
                    f"\\(\\Rightarrow {data['coeff_line']}t = {rhs}\\)\n\n"
                    f"\\(\\Rightarrow t = 0\\)\n\n"
                    f"Do đó giao điểm \\(A{format_point(data['intersection'])}\\).\n\n"
                    f"Vậy \\({expr} = {data['value']}{status}\\)"
                )
                solutions.append(solution_text)
            elif label == "b":
                data = params["b"]
                comb_parts = []
                append_linear_term(comb_parts, data["coeffs"][0], "(a + x)")
                append_linear_term(comb_parts, data["coeffs"][1], "(b + y)")
                append_linear_term(comb_parts, data["coeffs"][2], "(c + z)")
                comb_expr = " ".join(comb_parts) if comb_parts else "0"
                status = " \\quad(\\text{đúng})" if is_true else f" \\neq {displayed_value} \\Rightarrow \\text{{sai}}"
                
                # Format phương trình mặt cầu
                sphere_eq = format_sphere_expression(data['sphere'])
                
                # Tâm mặt cầu
                center = data['line']['point']
                R_sq = data['sphere']['radius_sq']
                
                solution_text = (
                    f"b) Đường thẳng \\({data['line']['label']}\\) đi qua tâm mặt cầu \\(({data['sphere']['label']})\\): \\({sphere_eq}\\).\n\n"
                    f"Thay tọa độ điểm trên đường thẳng vào phương trình mặt cầu:\n\n"
                    f"\\((x - {center[0]})^2 + (y - {center[1]})^2 + (z - {center[2]})^2 = {R_sq}\\)\n\n"
                    f"\\(\\Leftrightarrow {data['dir_norm']}t^2 = {R_sq}\\)\n\n"
                    f"\\(\\Rightarrow t^2 = {R_sq // data['dir_norm'] if data['dir_norm'] != 0 else 0}\\)\n\n"
                    f"\\(\\Rightarrow t = \\pm {data['step']}\\)\n\n"
                    f"Vậy hai giao điểm là \\(A{format_point(data['points'][0])}\\) và \\(B{format_point(data['points'][1])}\\).\n\n"
                    f"Do đó \\({comb_expr} = {data['value']}{status}\\)"
                )
                solutions.append(solution_text)
            elif label == "c":
                data = params["c"]
                status = " \\quad(\\text{đúng})" if is_true else f" \\neq {displayed_value} \\Rightarrow \\text{{sai}}"
                if data["target_type"] == "plane":
                    factor = data["plane_numerator"] // data["normal_norm"] if data["normal_norm"] != 0 else 0
                    plane_eq = format_plane_equation(
                        data['plane']['normal'][0],
                        data['plane']['normal'][1],
                        data['plane']['normal'][2],
                        data['plane']['d']
                    )
                    solution_text = (
                        f"c) Mặt phẳng \\(({data['plane']['label']})\\): \\({plane_eq}\\) có vector pháp tuyến \\(\\vec{{n}} = {format_point(data['plane']['normal'])}\\).\n\n"
                        f"Điểm \\(M{format_point(data['M'])}\\).\n\n"
                        f"Hình chiếu \\(H\\) của \\(M\\) lên mặt phẳng có dạng: \\(H = M - k\\vec{{n}}\\)\n\n"
                        f"với \\(k = \\dfrac{{\\vec{{n}} \\cdot \\vec{{OM}} + d}}{{\\|\\vec{{n}}\\|^2}} = \\dfrac{{{data['plane_numerator']}}}{{{data['normal_norm']}}} = {factor}\\)\n\n"
                        f"Do đó \\(H = {format_point(data['M'])} - {factor} \\cdot {format_point(data['plane']['normal'])} = {format_point(data['H'])}\\).\n\n"
                        f"Vậy \\(x + y + z = {data['value']}{status}\\)"
                    )
                    solutions.append(solution_text)
                else:
                    t_value = 0
                    if data["dir_norm"] != 0:
                        t_value = data["proj_numerator"] // data["dir_norm"]
                    line_expr = format_line_expression(data['line'])
                    solution_text = (
                        f"c) Đường thẳng \\({data['line']['label']}\\) có vector chỉ phương \\(\\vec{{u}} = {format_point(data['line']['direction'])}\\).\n\n"
                        f"Gọi \\(P_0{format_point(data['line']['point'])}\\) là điểm trên đường thẳng, điểm \\(M{format_point(data['M'])}\\).\n\n"
                        f"Vector \\(\\vec{{P_0M}} = {format_point(data['vector_PM'])}\\).\n\n"
                        f"Hình chiếu \\(H\\) có tham số: \\(t = \\dfrac{{\\vec{{P_0M}} \\cdot \\vec{{u}}}}{{\\|\\vec{{u}}\\|^2}} = \\dfrac{{{data['proj_numerator']}}}{{{data['dir_norm']}}} = {t_value}\\)\n\n"
                        f"Do đó \\(H = P_0 + t\\vec{{u}} = {format_point(data['H'])}\\).\n\n"
                        f"Vậy \\(x + y + z = {data['value']}{status}\\)"
                    )
                    solutions.append(solution_text)
            else:
                data = params["d"]
                status = " \\quad(\\text{đúng})" if is_true else f" \\neq {displayed_value} \\Rightarrow \\text{{sai}}"
                if data["type"] == "line_line":
                    den_expr = angle_denominator(data["norm_u"], data["norm_v"])
                    fraction = (
                        f"{data['numerator']}"
                        if den_expr == "1"
                        else f"\\dfrac{{{data['numerator']}}}{{{den_expr}}}"
                    )
                    line1_expr = format_line_expression(data['line1'])
                    line2_expr = format_line_expression(data['line2'])
                    
                    solution_text = (
                        f"d) Đường thẳng \\({data['line1']['label']}\\) có \\(\\vec{{u}} = {format_point(data['line1']['direction'])}\\).\n\n"
                        f"Đường thẳng \\({data['line2']['label']}\\) có \\(\\vec{{v}} = {format_point(data['line2']['direction'])}\\).\n\n"
                        f"Tích vô hướng: \\(\\vec{{u}} \\cdot \\vec{{v}} = {data['dot_product']}\\)\n\n"
                        f"Độ dài: \\(|\\vec{{u}}| = {sqrt_term(data['norm_u'])}\\), \\(|\\vec{{v}}| = {sqrt_term(data['norm_v'])}\\)\n\n"
                        f"Góc giữa hai đường thẳng: \\(\\cos\\varphi = \\dfrac{{|\\vec{{u}} \\cdot \\vec{{v}}|}}{{|\\vec{{u}}| \\cdot |\\vec{{v}}|}} = {fraction}\\)\n\n"
                        f"Do đó \\(\\varphi \\approx {data['deg_true']}^{{\\circ}}{status}\\)"
                    )
                    solutions.append(solution_text)
                else:
                    den_expr = angle_denominator(data["norm_n"], data["norm_u"])
                    fraction = (
                        f"{data['numerator']}"
                        if den_expr == "1"
                        else f"\\dfrac{{{data['numerator']}}}{{{den_expr}}}"
                    )
                    line_expr = format_line_expression(data['line'])
                    plane_eq = format_plane_equation(
                        data['plane']['normal'][0],
                        data['plane']['normal'][1],
                        data['plane']['normal'][2],
                        data['plane']['d']
                    )
                    
                    solution_text = (
                        f"d) Đường thẳng \\({data['line']['label']}\\) có \\(\\vec{{u}} = {format_point(data['line']['direction'])}\\).\n\n"
                        f"Mặt phẳng \\(({data['plane']['label']})\\): \\({plane_eq}\\) có \\(\\vec{{n}} = {format_point(data['plane']['normal'])}\\).\n\n"
                        f"Tích vô hướng: \\(\\vec{{u}} \\cdot \\vec{{n}} = {data['numerator'] if data['numerator'] == abs(dot(data['line']['direction'], data['plane']['normal'])) else dot(data['line']['direction'], data['plane']['normal'])}\\)\n\n"
                        f"Độ dài: \\(|\\vec{{u}}| = {sqrt_term(data['norm_u'])}\\), \\(|\\vec{{n}}| = {sqrt_term(data['norm_n'])}\\)\n\n"
                        f"Góc giữa đường thẳng và mặt phẳng: \\(\\sin\\theta = \\dfrac{{|\\vec{{u}} \\cdot \\vec{{n}}|}}{{|\\vec{{u}}| \\cdot |\\vec{{n}}|}} = {fraction}\\)\n\n"
                        f"Do đó \\(\\theta \\approx {data['deg_true']}^{{\\circ}}{status}\\)"
                    )
                    solutions.append(solution_text)

        question_body = "\n\n".join(question_lines)
        # Dùng dòng trống giữa các mục để LaTeX chắc chắn xuống dòng
        solution_text = "\n\n".join(solutions)

        content = (
            f"Câu {question_number}: Chọn các mệnh đề đúng.\n\n"
            f"{question_body}\n\n{solution_text}\n"
        )
        return content


class QuestionManager:
    def __init__(self) -> None:
        self.failed_count = 0

    def generate_questions(self, num_questions: int, verbose: bool = False) -> List[str]:
        if num_questions <= 0:
            raise ValueError("Số câu hỏi phải lớn hơn 0")
        questions: List[str] = []
        for idx in range(1, num_questions + 1):
            try:
                question = SpatialGeometryQuestion().generate_question(idx)
                questions.append(question)
                if verbose:
                    print(f"✅ Đã tạo xong câu {idx}")
            except Exception as exc:  # pragma: no cover - chỉ để debug runtime
                self.failed_count += 1
                print(f"❌ Lỗi khi tạo câu {idx}: {exc}")
        if not questions:
            raise ValueError("Không thể tạo được câu hỏi nào")
        if self.failed_count > 0:
            print(f"⚠️ Có {self.failed_count} câu không tạo được")
        return questions


class LaTeXTemplate:
    DOCUMENT_HEADER = r"""\documentclass[a4paper,12pt]{{article}}
\usepackage{{amsmath}}
\usepackage{{amsfonts}}
\usepackage{{amssymb}}
\usepackage{{geometry}}
\geometry{{a4paper, margin=1in}}
\usepackage{{polyglossia}}
\setmainlanguage{{vietnamese}}
\setmainfont{{Times New Roman}}
\usepackage{{tikz}}
\begin{{document}}
\title{{{title}}}
\author{{{author}}}
\maketitle

"""

    DOCUMENT_FOOTER = r"""
\end{document}"""


class LaTeXDocumentBuilder:
    def __init__(self) -> None:
        self.template = LaTeXTemplate()

    def build_document(self, questions: List[str], title: str, author: str = "dev") -> str:
        if not questions:
            raise ValueError("Danh sách câu hỏi không được rỗng")
        header = self.template.DOCUMENT_HEADER.format(title=title, author=author)
        body = "\n\n".join(questions)
        return header + body + self.template.DOCUMENT_FOOTER


DEFAULT_NUM_QUESTIONS = 3
DEFAULT_FILENAME = "geometry_questions.tex"
DEFAULT_TITLE = "Câu hỏi đường thẳng, mặt phẳng và mặt cầu"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generator câu hỏi hình học không gian dạng đúng/sai",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
    python3 duongthang_matphang_matcau.py            # Tạo 3 câu
    python3 duongthang_matphang_matcau.py 5          # Tạo 5 câu
    python3 duongthang_matphang_matcau.py -n 10      # Tạo 10 câu
""",
    )
    parser.add_argument(
        "num_questions",
        nargs="?",
        type=int,
        default=DEFAULT_NUM_QUESTIONS,
        help=f"Số câu cần tạo (mặc định: {DEFAULT_NUM_QUESTIONS})",
    )
    parser.add_argument(
        "-n",
        "--num-questions",
        type=int,
        dest="num_questions_override",
        help="Ghi đè số câu cần tạo",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=DEFAULT_FILENAME,
        help=f"Tên file LaTeX (mặc định: {DEFAULT_FILENAME})",
    )
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        default=DEFAULT_TITLE,
        help=f"Tiêu đề tài liệu (mặc định: '{DEFAULT_TITLE}')",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Hiển thị chi tiết quá trình tạo",
    )
    args = parser.parse_args()
    if args.num_questions_override is not None:
        args.num_questions = args.num_questions_override
    if args.num_questions <= 0:
        parser.error("Số câu phải dương")
    return args


def generate_questions(num_questions: int, verbose: bool = False) -> List[str]:
    manager = QuestionManager()
    return manager.generate_questions(num_questions, verbose)


def create_latex_file(questions: List[str], filename: str, title: str) -> None:
    builder = LaTeXDocumentBuilder()
    content = builder.build_document(questions, title)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> None:
    try:
        args = parse_arguments()
        if args.verbose:
            logging.basicConfig(level=logging.INFO)
        questions = generate_questions(args.num_questions, args.verbose)
        create_latex_file(questions, args.output, args.title)
        print(f"✅ Đã tạo {args.output} với {len(questions)} câu.")
        print(f"📄 Biên dịch bằng: xelatex {args.output}")
    except Exception as exc:
        print(f"❌ Lỗi: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()


