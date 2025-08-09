import re
import math
from typing import List, Tuple, Dict, Optional
from fractions import Fraction

# Types
Vector = Tuple[Fraction, Fraction, Fraction]
Point = Tuple[Fraction, Fraction, Fraction]
Plane = Tuple[Fraction, Fraction, Fraction, Fraction]

# ---------------- Parsing numbers -----------------

def _strip_math(s: str) -> str:
    return s.strip().strip("$").strip().strip("\\(").strip("\\)")


def parse_number_expr(s: str) -> float:
    s0 = _strip_math(s.replace(" ", ""))
    # Replace \dfrac{a}{b} with (a)/(b)
    def repl_dfrac(m):
        return f"({m.group(1)})/({m.group(2)})"
    s0 = re.sub(r"\\dfrac\{([^{}]+)\}\{([^{}]+)\}", repl_dfrac, s0)
    # Replace \sqrt{n} with sqrt(n)
    def repl_sqrt(m):
        return f"sqrt({m.group(1)})"
    s0 = re.sub(r"\\sqrt\{([^{}]+)\}", repl_sqrt, s0)
    # Also handle Unicode √n
    s0 = s0.replace("√", "sqrt(")
    s0 = re.sub(r"sqrt\(([^()]+)\)(?!\))", r"sqrt(\1)", s0)
    # Validate allowed chars
    if not re.fullmatch(r"[0-9./()+\-]*|[0-9./()+\-]*sqrt\([0-9]+\)[0-9./()+\-]*", s0):
        # Fallback: try to parse simple int/fraction
        return float(Fraction(s))
    # Implement sqrt as math.sqrt when evaluating
    def safe_eval(expr: str) -> float:
        expr = expr.replace("--", "+")
        # Tokenize around sqrt(...)
        # Replace sqrt(n) with numeric value
        while True:
            m = re.search(r"sqrt\(([0-9]+)\)", expr)
            if not m:
                break
            val = math.sqrt(int(m.group(1)))
            expr = expr[:m.start()] + str(val) + expr[m.end():]
        # Now only numbers and + - * / ( )
        # Replace implicit multiplication like 5 2 -> 5*2 (unlikely). We'll trust explicit.
        return eval(expr, {"__builtins__": None}, {})
    return float(safe_eval(s0))


def parse_fraction(s: str) -> Fraction:
    s = _strip_math(s)
    m = re.fullmatch(r"\\dfrac\{([^{}]+)\}\{([^{}]+)\}", s)
    if m:
        return parse_fraction(m.group(1)) / parse_fraction(m.group(2))
    if "/" in s and not any(ch.isalpha() for ch in s):
        try:
            n, d = s.split("/")
            return Fraction(n.strip()).limit_denominator() / Fraction(d.strip()).limit_denominator()
        except Exception:
            pass
    try:
        return Fraction(s).limit_denominator()
    except Exception:
        try:
            return Fraction(str(parse_number_expr(s))).limit_denominator()
        except Exception:
            raise


def parse_tuple3(s: str) -> Tuple[Fraction, Fraction, Fraction]:
    s = _strip_math(s)
    s = s.strip("()")
    parts = re.split(r"[;,]", s)
    if len(parts) != 3:
        raise ValueError(f"Expected 3-tuple, got: {s}")
    return (parse_fraction(parts[0]), parse_fraction(parts[1]), parse_fraction(parts[2]))


# ---------------- Basic vector/plane ops -----------------

def vec_cross(u: Vector, v: Vector) -> Vector:
    ux, uy, uz = u
    vx, vy, vz = v
    return (
        uy * vz - uz * vy,
        uz * vx - ux * vz,
        ux * vy - uy * vx,
    )


def vec_dot(u: Vector, v: Vector) -> Fraction:
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


def vec_is_zero(u: Vector) -> bool:
    return u[0] == 0 and u[1] == 0 and u[2] == 0


def are_parallel_vectors(u: Vector, v: Vector) -> bool:
    return vec_is_zero(vec_cross(u, v))


def plane_normal(p: Plane) -> Vector:
    a, b, c, _ = p
    return (a, b, c)


def is_point_on_plane(P: Point, pl: Plane) -> bool:
    x0, y0, z0 = P
    a, b, c, d = pl
    return a * x0 + b * y0 + c * z0 + d == 0


def distance_point_to_plane(P: Point, pl: Plane) -> float:
    x0, y0, z0 = P
    a, b, c, d = pl
    num = abs(float(a * x0 + b * y0 + c * z0 + d))
    den = math.sqrt(float(a * a + b * b + c * c))
    return num / den


def distance_between_parallel_planes(p1: Plane, p2: Plane) -> float:
    n1 = plane_normal(p1)
    n2 = plane_normal(p2)
    if not are_parallel_vectors(n1, n2):
        raise ValueError("not parallel")
    a1, b1, c1, d1 = p1
    a2, b2, c2, d2 = p2
    # find k such that n2 = k * n1
    k = None
    for u, v in [(a1, a2), (b1, b2), (c1, c2)]:
        if u != 0:
            k = float(v) / float(u)
            break
    if k is None:
        k = 1.0
    num = abs(float(d2) - k * float(d1))
    den = math.sqrt(float(a2 * a2 + b2 * b2 + c2 * c2))
    return num / den


def angle_between_planes_deg(p1: Plane, p2: Plane) -> int:
    n1 = plane_normal(p1)
    n2 = plane_normal(p2)
    dot = float(vec_dot(n1, n2))
    n1n = math.sqrt(float(vec_dot(n1, n1)))
    n2n = math.sqrt(float(vec_dot(n2, n2)))
    if n1n == 0 or n2n == 0:
        return 0
    cosang = abs(dot) / (n1n * n2n)
    cosang = max(0.0, min(1.0, cosang))
    ang = math.degrees(math.acos(cosang))
    if ang > 90:
        ang = 180 - ang
    return int(round(ang))


# ---------------- Plane parsing -----------------

def parse_plane_equation(equation_str: str) -> Plane:
    s = equation_str.replace(" ", "")
    # Support 'lhs=0' or 'lhs=rhs' or just 'lhs'
    rhs_val = Fraction(0)
    if '=' in s:
        parts = s.split('=')
        if len(parts) == 2:
            lhs = parts[0]
            rhs_text = parts[1]
            if rhs_text != '0':
                try:
                    rhs_val = Fraction(str(parse_number_expr(rhs_text))).limit_denominator()
                except Exception:
                    rhs_val = Fraction(0)
        else:
            lhs = parts[0]
    else:
        lhs = s
    # Find coefficients for x, y, z from lhs
    def coeff_of(var: str) -> Fraction:
        total = Fraction(0)
        for m in re.finditer(rf"([+\-]?)((?:\d+)?){var}", lhs):
            sign = -1 if m.group(1) == '-' else 1
            num = int(m.group(2)) if m.group(2) else 1
            total += sign * num
        return total
    a = coeff_of('x')
    b = coeff_of('y')
    c = coeff_of('z')
    # Remove variable terms and collect constants on lhs
    tmp = re.sub(r"[+\-]?(?:\d+)?x", "", lhs)
    tmp = re.sub(r"[+\-]?(?:\d+)?y", "", tmp)
    tmp = re.sub(r"[+\-]?(?:\d+)?z", "", tmp)
    const_total = Fraction(0)
    for m in re.finditer(r"[+\-]?\d+", tmp):
        const_total += Fraction(int(m.group(0)))
    # Move rhs to lhs: d = const_total - rhs_val
    d = const_total - rhs_val
    if a == 0 and b == 0 and c == 0:
        raise ValueError(f"Invalid plane: {equation_str}")
    return (a, b, c, d)


# ---------------- LaTeX extraction -----------------
ITEM_HEADER_RE = re.compile(r"\\item\[\\textbf\{([^\]]+)\}\]\s*(.+)")
PLANE_IN_TEXT_RE = re.compile(r"\(P\)\s*:\s*([^\n]+?)(?:=\s*0)?")
PLANE_NAMED_RE = re.compile(r"\((P|Q|R|S|P_1|P_2|\\alpha|\\beta|\\gamma|Oxy)\)\s*:\s*([^\n]+?)(?:=\s*0)?")
POINT_RE = re.compile(r"([A-Z])\((-?\d+);\s*(-?\d+);\s*(-?\d+)\)")
POINT_GENERIC_RE = re.compile(r"\((-?\d+);\s*(-?\d+);\s*(-?\d+)\)")
VECTOR_NAMED_RE = re.compile(r"\\vec\{([a-zA-Z]_?)\}\s*=\s*\((-?\d+);\s*(-?\d+);\s*(-?\d+)\)")
U_V_VECTORS_RE = re.compile(r"u\s*=\s*\((-?\d+);\s*(-?\d+);\s*(-?\d+)\).*?v\s*=\s*\((-?\d+);\s*(-?\d+);\s*(-?\d+)\)")
TASK_LINE_RE = re.compile(r"\\task\s+(.*)")


def extract_options(block_lines: List[str]) -> List[str]:
    options: List[str] = []
    for line in block_lines:
        m = TASK_LINE_RE.search(line)
        if m:
            options.append(m.group(1).strip())
    return options


def parse_plane_from_text(text: str) -> Optional[Plane]:
    m = PLANE_IN_TEXT_RE.search(text)
    return parse_plane_equation(m.group(1)) if m else None


def extract_named_planes(text: str) -> Dict[str, Plane]:
    planes: Dict[str, Plane] = {}
    for m in PLANE_NAMED_RE.finditer(text):
        name = m.group(1)
        eq = m.group(2)
        if name == 'Oxy':
            planes[name] = (Fraction(0), Fraction(0), Fraction(1), Fraction(0))
        else:
            try:
                planes[name] = parse_plane_equation(eq)
            except Exception:
                pass
    return planes


def extract_points(text: str) -> Dict[str, Point]:
    pts: Dict[str, Point] = {}
    for m in POINT_RE.finditer(text):
        pts[m.group(1)] = (
            Fraction(int(m.group(2))),
            Fraction(int(m.group(3))),
            Fraction(int(m.group(4))),
        )
    return pts


def extract_uv_vectors(text: str) -> Optional[Tuple[Vector, Vector]]:
    m = U_V_VECTORS_RE.search(text)
    if not m:
        return None
    u = (Fraction(int(m.group(1))), Fraction(int(m.group(2))), Fraction(int(m.group(3))))
    v = (Fraction(int(m.group(4))), Fraction(int(m.group(5))), Fraction(int(m.group(6))))
    return u, v


# ---------------- Handlers -----------------

def handle_normal_from_plane(prompt: str, options: List[str]) -> List[int]:
    if "pháp tuyến" not in prompt or "(P)" not in prompt:
        return []
    p = parse_plane_from_text(prompt)
    if p is None:
        return []
    n = plane_normal(p)
    correct: List[int] = []
    for i, opt in enumerate(options):
        m = re.search(r"\((-?\d+);\s*(-?\d+);\s*(-?\d+)\)", opt)
        if not m:
            continue
        v = (Fraction(int(m.group(1))), Fraction(int(m.group(2))), Fraction(int(m.group(3))))
        if are_parallel_vectors(n, v):
            correct.append(i)
    return correct


def handle_normal_from_uv(prompt: str, options: List[str]) -> List[int]:
    if "véctơ chỉ phương" not in prompt:
        return []
    uv = extract_uv_vectors(prompt)
    if not uv:
        return []
    u, v = uv
    n = vec_cross(u, v)
    correct: List[int] = []
    for i, opt in enumerate(options):
        m = re.search(r"\((-?\d+);\s*(-?\d+);\s*(-?\d+)\)", opt)
        if not m:
            continue
        w = (Fraction(int(m.group(1))), Fraction(int(m.group(2))), Fraction(int(m.group(3))))
        if are_parallel_vectors(n, w):
            correct.append(i)
    return correct


def handle_point_on_plane(prompt: str, options: List[str]) -> List[int]:
    if "thuộc" not in prompt or "(P)" not in prompt:
        return []
    p = parse_plane_from_text(prompt)
    if p is None:
        return []
    correct: List[int] = []
    for i, opt in enumerate(options):
        m = re.search(r"\((-?\d+);\s*(-?\d+);\s*(-?\d+)\)", opt)
        if not m:
            continue
        point = (Fraction(int(m.group(1))), Fraction(int(m.group(2))), Fraction(int(m.group(3))))
        if is_point_on_plane(point, p):
            correct.append(i)
    return correct


def handle_find_m_point_on_plane(prompt: str, options: List[str]) -> List[int]:
    if "Tìm" not in prompt or "thuộc" not in prompt or "(P)" not in prompt:
        return []
    p = parse_plane_from_text(prompt)
    if p is None:
        return []
    # Extract semicolon tuple with m inside
    pm = re.search(r"\(([^)m]*m[^)]*)\)", prompt)
    if not pm:
        return []
    parts = [t.strip() for t in pm.group(1).split(";")]
    if len(parts) != 3:
        return []
    # Build expression a*x(m)+b*y(m)+c*z(m)+d == 0 and solve by scanning option candidates
    a, b, c, d = p
    correct: List[int] = []
    for i, opt in enumerate(options):
        try:
            mval = parse_fraction(opt)
        except Exception:
            continue
        def eval_part(expr: str) -> Fraction:
            expr = expr.replace(" ", "")
            expr = expr.replace("m", str(float(mval)))
            val = parse_number_expr(expr)
            return Fraction(val).limit_denominator()
        try:
            x = eval_part(parts[0])
            y = eval_part(parts[1])
            z = eval_part(parts[2])
            if a * x + b * y + c * z + d == 0:
                correct.append(i)
        except Exception:
            pass
    return correct


def handle_distance_point_plane(prompt: str, options: List[str]) -> List[int]:
    if ("Khoảng cách" not in prompt and "Độ dài" not in prompt) or "(P)" not in prompt:
        return []
    p = parse_plane_from_text(prompt)
    if p is None:
        return []
    pts = extract_points(prompt)
    P0 = pts.get('A') or pts.get('M')
    if not P0:
        return []
    dval = distance_point_to_plane(P0, p)
    correct: List[int] = []
    for i, opt in enumerate(options):
        try:
            val = parse_number_expr(opt)
            if abs(val - dval) < 1e-6:
                correct.append(i)
        except Exception:
            pass
    return correct


def handle_reflection_distance(prompt: str, options: List[str]) -> List[int]:
    if "đối xứng" not in prompt and "đốixứng" not in prompt.replace(" ",""):
        return []
    p = parse_plane_from_text(prompt)
    if p is None:
        return []
    pts = extract_points(prompt)
    A = pts.get('A')
    if not A:
        return []
    ab = 2.0 * distance_point_to_plane(A, p)
    correct: List[int] = []
    for i, opt in enumerate(options):
        try:
            val = parse_number_expr(opt)
            if abs(val - ab) < 1e-6:
                correct.append(i)
        except Exception:
            pass
    return correct


def handle_distance_between_planes(prompt: str, options: List[str]) -> List[int]:
    if "Khoảng cách" not in prompt or "(P)" not in prompt or "(Q)" not in prompt:
        return []
    planes = extract_named_planes(prompt)
    if 'P' not in planes or 'Q' not in planes:
        return []
    try:
        dval = distance_between_parallel_planes(planes['P'], planes['Q'])
    except Exception:
        return []
    correct: List[int] = []
    for i, opt in enumerate(options):
        try:
            val = parse_number_expr(opt)
            if abs(val - dval) < 1e-6:
                correct.append(i)
        except Exception:
            pass
    return correct


def handle_angle_between_planes(prompt: str, options: List[str]) -> List[int]:
    if "góc" not in prompt:
        return []
    planes = extract_named_planes(prompt)
    keys = list(planes.keys())
    if len(keys) < 2:
        return []
    p1 = planes[keys[0]]
    p2 = planes[keys[1]]
    ang = angle_between_planes_deg(p1, p2)
    correct: List[int] = []
    for i, opt in enumerate(options):
        m = re.search(r"(\d+)", opt)
        if not m:
            continue
        val = int(m.group(1))
        if val == ang or val == 180 - ang:
            correct.append(i)
    return correct


def handle_write_plane_point_normal(prompt: str, options: List[str]) -> List[int]:
    if "đi qua điểm" not in prompt or "VTPT" not in prompt:
        return []
    pts = extract_points(prompt)
    if not pts:
        return []
    point = list(pts.values())[0]
    vm = VECTOR_NAMED_RE.search(prompt)
    if not vm:
        return []
    normal = (Fraction(int(vm.group(2))), Fraction(int(vm.group(3))), Fraction(int(vm.group(4))))
    correct: List[int] = []
    for i, opt in enumerate(options):
        try:
            eq = opt
            m = re.search(r"\(P\)\s*:\s*([^=]+)=0", opt)
            if m:
                eq = m.group(1)
            plane = parse_plane_equation(eq)
            if are_parallel_vectors(plane_normal(plane), normal) and is_point_on_plane(point, plane):
                correct.append(i)
        except Exception:
            pass
    return correct


def handle_write_plane_point_parallel_axis(prompt: str, options: List[str]) -> List[int]:
    pts = extract_points(prompt)
    if not pts:
        return []
    point = list(pts.values())[0]
    axis = None
    if "vuông góc với trục Ox" in prompt:
        axis = 'Ox'
    if "\\parallel (Oxy)" in prompt or "parallel (Oxy)" in prompt or "(P) \\parallel (Oxy)" in prompt:
        axis = 'Oxy'
    if axis is None:
        return []
    correct: List[int] = []
    for i, opt in enumerate(options):
        try:
            eq = opt
            m = re.search(r"\(P\)\s*:\s*([^=]+)=0", opt)
            if m:
                eq = m.group(1)
            a, b, c, d = parse_plane_equation(eq)
            ok = False
            if axis == 'Ox':
                ok = (b == 0 and c == 0 and is_point_on_plane(point, (a, b, c, d)))
            elif axis == 'Oxy':
                ok = (a == 0 and b == 0 and is_point_on_plane(point, (a, b, c, d)))
            if ok:
                correct.append(i)
        except Exception:
            pass
    return correct


def handle_write_plane_contains_axis(prompt: str, options: List[str]) -> List[int]:
    pts = extract_points(prompt)
    if not pts:
        return []
    point = list(pts.values())[0]
    axis = None
    if "chứa trục Ox" in prompt:
        axis = 'Ox'
    elif "chứa trục Oy" in prompt:
        axis = 'Oy'
    if axis is None:
        return []
    correct: List[int] = []
    for i, opt in enumerate(options):
        try:
            eq = opt
            m = re.search(r"\(P\)\s*:\s*([^=]+)=0", opt)
            if m:
                eq = m.group(1)
            a, b, c, d = parse_plane_equation(eq)
            if axis == 'Ox':
                ok = (a == 0 and d == 0 and is_point_on_plane(point, (a, b, c, d)))
            else:
                ok = (b == 0 and d == 0 and is_point_on_plane(point, (a, b, c, d)))
            if ok:
                correct.append(i)
        except Exception:
            pass
    return correct


HANDLERS = [
    handle_normal_from_uv,
    handle_normal_from_plane,
    handle_point_on_plane,
    handle_find_m_point_on_plane,
    handle_distance_point_plane,
    handle_reflection_distance,
    handle_distance_between_planes,
    handle_angle_between_planes,
    handle_write_plane_point_normal,
    handle_write_plane_point_parallel_axis,
    handle_write_plane_contains_axis,
]


class ValidationResult:
    def __init__(self, header: str, options: List[str], correct_indices: List[int]):
        self.header = header
        self.options = options
        self.correct_indices = correct_indices


def validate_tex_file(tex_path: str) -> List[ValidationResult]:
    with open(tex_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    results: List[ValidationResult] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = ITEM_HEADER_RE.search(line)
        if m:
            header = m.group(1)
            prompt = m.group(2).strip()
            block_lines = [line]
            j = i + 1
            while j < len(lines) and not ITEM_HEADER_RE.search(lines[j]) and "\\end{tasks}" not in lines[j]:
                block_lines.append(lines[j])
                j += 1
            options = extract_options(block_lines)
            text = prompt + "\n" + "".join(block_lines)
            correct: List[int] = []
            for h in HANDLERS:
                try:
                    idxs = h(text, options)
                except Exception:
                    idxs = []
                if idxs:
                    correct = sorted(list(set(correct + idxs)))
            results.append(ValidationResult(header, options, correct))
            i = j
        else:
            i += 1
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("tex")
    args = parser.parse_args()
    res = validate_tex_file(args.tex)
    for r in res:
        if r.correct_indices:
            labels = [chr(ord('A') + i) for i in r.correct_indices]
            print(f"{r.header}: {', '.join(labels)}")
        else:
            print(f"{r.header}: Unrecognized/None")


if __name__ == "__main__":
    main()