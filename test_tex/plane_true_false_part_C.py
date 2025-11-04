import math
import random
from typing import List, Tuple, Dict

# Formatters

def format_plane_equation(a: float, b: float, c: float, d: float) -> str:
    parts: List[str] = []
    if a == 1:
        parts.append("x")
    elif a == -1:
        parts.append("-x")
    elif a != 0:
        if a == int(a):
            parts.append(f"{int(a)}x")
        else:
            parts.append(f"{a}x")
    if b != 0:
        if parts:
            if b == 1:
                parts.append("+ y")
            elif b == -1:
                parts.append("- y")
            elif b > 0:
                if b == int(b):
                    parts.append(f"+ {int(b)}y")
                else:
                    parts.append(f"+ {b}y")
            else:
                if b == int(b):
                    parts.append(f"- {int(abs(b))}y")
                else:
                    parts.append(f"- {abs(b)}y")
        else:
            if b == 1:
                parts.append("y")
            elif b == -1:
                parts.append("-y")
            else:
                if b == int(b):
                    parts.append(f"{int(b)}y")
                else:
                    parts.append(f"{b}y")
    if c != 0:
        if parts:
            if c == 1:
                parts.append("+ z")
            elif c == -1:
                parts.append("- z")
            elif c > 0:
                if c == int(c):
                    parts.append(f"+ {int(c)}z")
                else:
                    parts.append(f"+ {c}z")
            else:
                if c == int(c):
                    parts.append(f"- {int(abs(c))}z")
                else:
                    parts.append(f"- {abs(c)}z")
        else:
            if c == 1:
                parts.append("z")
            elif c == -1:
                parts.append("-z")
            else:
                if c == int(c):
                    parts.append(f"{int(c)}z")
                else:
                    parts.append(f"{c}z")
    if d != 0:
        if d > 0 and parts:
            if d == int(d):
                parts.append(f"+ {int(d)}")
            else:
                parts.append(f"+ {d}")
        else:
            if d == int(d):
                parts.append(str(int(d)))
            else:
                parts.append(str(d))
    if not parts:
        parts.append("0")
    return " ".join(parts) + " = 0"


def format_point(pt: Tuple[int, int, int]) -> str:
    return f"({pt[0]};{pt[1]};{pt[2]})"

def format_point_float(pt: Tuple[float, float, float]) -> str:
    x = pt[0] if pt[0] != int(pt[0]) else int(pt[0])
    y = pt[1] if pt[1] != int(pt[1]) else int(pt[1])
    z = pt[2] if pt[2] != int(pt[2]) else int(pt[2])
    return f"({x};{y};{z})"

# Helpers

def point_plane_distance_numer_normsq(a: int, b: int, c: int, d: int, P: Tuple[int, int, int]) -> Tuple[int, int]:
    numer = abs(a*P[0] + b*P[1] + c*P[2] + d)
    norm_sq = a*a + b*b + c*c
    return numer, norm_sq


def sphere_center_radius_from_eq(A: int, B: int, C: int, D: int) -> Tuple[Tuple[float, float, float], float]:
    # x^2 + y^2 + z^2 + 2ux + 2vy + 2wz + D = 0 => center (-u, -v, -w), r^2 = u^2+v^2+w^2 - D
    u, v, w = A/2.0, B/2.0, C/2.0
    cx, cy, cz = -u, -v, -w
    r_sq = u*u + v*v + w*w - D
    r = math.sqrt(abs(r_sq))
    return (cx, cy, cz), r

# Propositions for Part C

# Tangent plane at a point on sphere

def prop_tangent_plane_at_point() -> Dict[str, str]:
    # Sphere: (x-1)^2 + (y+1)^2 + (z-3)^2 = 9; point M(2,1,1) genericized
    center = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
    r = random.choice([3, 4, 5])
    # pick a point on sphere by offsetting along x
    M = (center[0] + r, center[1], center[2])
    # Tangent plane normal is vector CM
    a, b, c = (M[0]-center[0], M[1]-center[1], M[2]-center[2])
    d = -(a*M[0] + b*M[1] + c*M[2])
    true_text = f"Mặt phẳng tiếp xúc với mặt cầu tâm I{format_point(center)} bán kính {r} tại M{format_point(M)} có phương trình \\((P): {format_plane_equation(a,b,c,d)}\\)."
    false_text = f"Mặt phẳng tiếp xúc với mặt cầu tâm I{format_point(center)} bán kính {r} tại M{format_point(M)} có phương trình \\((P): {format_plane_equation(a,b,c,d+1)}\\)."
    return {"true": true_text, "false": false_text}

# Plane parallel to given plane and tangent to sphere

def prop_plane_parallel_tangent_to_sphere() -> Dict[str, str]:
    # Sphere general: x^2+y^2+z^2+2ux+2vy+2wz + D = 0
    u, v, w = random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)
    D = random.randint(-10, 5)
    center = (-u, -v, -w)
    r = math.sqrt(max(1.0, u*u + v*v + w*w - D))  # ensure r >= 1
    # Given plane: ax+by+cz+d0=0, parallel planes: same (a,b,c) with different d
    a, b, c = random.choice([1, 2, 3]), random.choice([1, 2]), random.choice([-2, -1, 1, 2])
    d0 = random.randint(-10, 10)
    
    # Choose nice values for tangency: use Pythagorean triples or simple ratios
    # For plane ax+by+cz+d=0, distance from center = |a*cx+b*cy+c*cz + d| / sqrt(a^2+b^2+c^2)
    # Choose r and (a,b,c) such that r*sqrt(a^2+b^2+c^2) gives nice integer
    norm_sq = a*a + b*b + c*c
    if norm_sq == 1:  # |a|=1, others=0
        offset = int(r)  # r*1 = r
    elif norm_sq == 4:  # like (2,0,0)
        offset = int(2*r)  # r*2
    elif norm_sq == 5:  # like (2,1,0) 
        offset = random.choice([int(r*2), int(r*3)])  # approximately r*sqrt(5)
    else:
        offset = random.choice([2, 3, 4, 5])  # simple integers
    
    base = a*center[0] + b*center[1] + c*center[2]
    d_true = -base + offset
    d_false = d_true + random.choice([1, -1, 2, -2])
    
    true_text = f"Tồn tại mặt phẳng \\((Q)\\) song song với \\((P): {format_plane_equation(a,b,c,d0)}\\) và tiếp xúc với mặt cầu \\(x^2+y^2+z^2+{2*u}x+{2*v}y+{2*w}z+{D}=0\\) có dạng \\((Q): {format_plane_equation(a,b,c,d_true)}\\)."
    false_text = f"Mặt phẳng \\((Q): {format_plane_equation(a,b,c,d_false)}\\) song song với \\((P): {format_plane_equation(a,b,c,d0)}\\) và tiếp xúc với mặt cầu \\(x^2+y^2+z^2+{2*u}x+{2*v}y+{2*w}z+{D}=0\\)."
    return {"true": true_text, "false": false_text}

# Distance from center to plane equals radius

def prop_radius_from_center_plane_distance() -> Dict[str, str]:
    # Use Pythagorean triple to avoid irrational denominators
    # Choose coefficients that form a Pythagorean triple: (3,4,5) or (5,12,13)
    triple_choices = [(3, 4, 0, 5), (5, 12, 0, 13), (1, 0, 0, 1), (0, 1, 0, 1)]
    a, b, c, norm = random.choice(triple_choices)
    d = random.choice([1, 2, 3])
    I = (random.choice([0, 1, -1]), random.choice([-2, -1, 1]), random.choice([0, 1, 2]))
    
    # Calculate distance numerator: |a*I[0] + b*I[1] + c*I[2] + d|
    numer = abs(a*I[0] + b*I[1] + c*I[2] + d)
    
    # For Pythagorean triples, the radius is numer/norm (integer ratio)
    if norm == 1:
        true_text = f"Hình cầu tâm I{format_point(I)} tiếp xúc với mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) có bán kính \\({numer}\\)."
        false_text = f"Hình cầu tâm I{format_point(I)} tiếp xúc với mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) có bán kính \\({numer+1}\\)."
    else:
        true_text = f"Hình cầu tâm I{format_point(I)} tiếp xúc với mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) có bán kính \\(\\dfrac{{{numer}}}{{{norm}}}\\)."
        false_text = f"Hình cầu tâm I{format_point(I)} tiếp xúc với mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) có bán kính \\(\\dfrac{{{numer+1}}}{{{norm}}}\\)."
    
    return {"true": true_text, "false": false_text}

# Non-intersection (no common point) condition between plane and sphere parameter m

def prop_plane_sphere_no_intersection_param() -> Dict[str, str]:
    # Sphere: (x+1)^2+(y-2)^2+(z-3)^2 = 25 -> x^2+y^2+z^2+2x-4y-6z-11=0
    # Plane: 2x+y-2z+m=0; no intersection if distance from center > radius
    center = (-1, 2, 3)
    r = 5
    a, b, c = 2, 1, -2
    # distance |a*cx+b*cy+c*cz + m| / sqrt(a^2+b^2+c^2) > r => |a*cx+b*cy+c*cz + m| > r*norm
    base = a*center[0] + b*center[1] + c*center[2]
    norm = math.sqrt(a*a + b*b + c*c)
    threshold = r*norm
    # Choose m so that |base + m| > threshold
    m_true = int(math.copysign(math.ceil(threshold) + random.randint(0, 3), random.choice([-1, 1]))) - base
    true_text = f"Với \\((P): 2x+y-2z+m=0\\) và mặt cầu \\((S): (x+1)^2+(y-2)^2+(z-3)^2=25\\), khi \\(m\\) đủ lớn về trị tuyệt đối thì \\((P)\\) và \\((S)\\) không có điểm chung."
    false_text = f"Với mặt phẳng \\((P): 2x+y-2z+m=0\\) và mặt cầu \\((S): (x+1)^2+(y-2)^2+(z-3)^2=25\\), luôn tồn tại giao tuyến là đường tròn với mọi \\(m\\)."
    return {"true": true_text, "false": false_text}

# Plane parallel and equidistant to two given planes

def prop_plane_parallel_equidistant_two_planes() -> Dict[str, str]:
    # Two parallel planes: ax+by+cz+d1=0 and ax+by+cz+d2=0
    a, b, c = random.choice([1, 2, 3]), random.choice([-1, 1]), random.choice([2, 4])
    # Choose d1, d2 such that (d1+d2)/2 is an integer or simple fraction
    d1 = random.choice([-6, -4, -2, 2, 4])
    d2 = d1 + random.choice([2, 4, 6, 8])  # Ensure d2 > d1 and (d1+d2)/2 is integer or half-integer
    
    # Middle plane has d = (d1+d2)/2
    d_middle = (d1 + d2) / 2
    # Format d_middle nicely
    if d_middle == int(d_middle):
        d_middle = int(d_middle)
    
    true_text = f"Cho hai mặt phẳng \\((\\alpha): {format_plane_equation(a,b,c,d1)}\\) và \\((\\beta): {format_plane_equation(a,b,c,d2)}\\). Mặt phẳng \\((P)\\) song song và cách đều hai mặt phẳng \\((\\alpha)\\) và \\((\\beta)\\) có phương trình \\((P): {format_plane_equation(a,b,c,d_middle)}\\)."
    false_text = f"Cho hai mặt phẳng \\((\\alpha): {format_plane_equation(a,b,c,d1)}\\) và \\((\\beta): {format_plane_equation(a,b,c,d2)}\\). Mặt phẳng \\((P): {format_plane_equation(a,b,c,d_middle+1)}\\) song song và cách đều hai mặt phẳng \\((\\alpha)\\) và \\((\\beta)\\)."
    return {"true": true_text, "false": false_text}

# Plane parallel to given plane and intersects sphere with specific circumference

def prop_plane_sphere_intersection_circumference() -> Dict[str, str]:
    # Sphere: (x-h)^2+(y-k)^2+(z-l)^2=R^2
    center = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
    R = random.choice([4, 5, 6])
    # Given plane: ax+by+cz+d0=0, parallel plane: ax+by+cz+d=0
    a, b, c = random.choice([1, 2]), random.choice([1, 2]), random.choice([-1, 1])
    d0 = random.randint(-10, 10)
    # Circumference = 2πr, given circumference = 6π => r = 3
    r_circle = 3
    # Distance from center to plane: sqrt(R^2 - r^2) = sqrt(R^2 - 9)
    dist_center_plane_sq = R*R - r_circle*r_circle  # This is perfect square or simple
    
    # Choose R so that R^2 - 9 is a perfect square
    R_values = {5: 4, 6: 27}  # R=5 -> sqrt(25-9)=4, R=6 -> sqrt(36-9)=sqrt(27)=3sqrt(3)
    R = random.choice([5])  # Use R=5 to get dist = 4 (integer)
    dist_center_plane = 4  # sqrt(25-9) = 4
    
    # For normal vector (a,b,c), choose so that ||(a,b,c)|| gives nice values
    # Use Pythagorean triples: (3,4,5), (1,0,0), etc.
    a, b, c = random.choice([(3, 4, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0)])
    norm = math.sqrt(a*a + b*b + c*c)
    
    base = a*center[0] + b*center[1] + c*center[2]
    if (a, b, c) == (3, 4, 0):  # norm = 5
        d_true = -base + dist_center_plane * 5  # 4*5 = 20
        d_false = -base + (dist_center_plane + 1) * 5  # 5*5 = 25
    else:  # norm = 1
        d_true = -base + dist_center_plane  # 4*1 = 4
        d_false = -base + (dist_center_plane + 1)  # 5*1 = 5
    
    # Format sphere equation properly
    cx_term = f"(x{-center[0]:+})" if center[0] != 0 else "x"
    cy_term = f"(y{-center[1]:+})" if center[1] != 0 else "y"
    cz_term = f"(z{-center[2]:+})" if center[2] != 0 else "z"
    sphere_eq = f"{cx_term}^2+{cy_term}^2+{cz_term}^2={R*R}"
    
    true_text = f"Mặt phẳng \\((P)\\) song song với \\((Q): {format_plane_equation(a,b,c,d0)}\\) và cắt mặt cầu \\((S): {sphere_eq}\\) theo giao tuyến là đường tròn có chu vi \\(6\\pi\\) có phương trình \\((P): {format_plane_equation(a,b,c,d_true)}\\)."
    false_text = f"Mặt phẳng \\((P): {format_plane_equation(a,b,c,d_false)}\\) song song với \\((Q): {format_plane_equation(a,b,c,d0)}\\) và cắt mặt cầu \\((S): {sphere_eq}\\) theo giao tuyến là đường tròn có chu vi \\(6\\pi\\)."
    return {"true": true_text, "false": false_text}

# Plane through two points and equidistant to two other points

def prop_plane_through_points_equidistant() -> Dict[str, str]:
    # Two points on plane
    O = (0, 0, 0)
    A = (random.choice([1, 2]), random.choice([1, 2]), 0)
    # Two points to be equidistant
    B = (0, random.choice([3, 4]), 0)
    C = (0, 0, random.choice([2, 3]))
    # Plane through O, A has form: by + cz = 0 (since it passes through origin)
    # Normal vector perpendicular to OA = A
    # Let plane be: bx + cy + dz = 0, substitute A: b*A[0] + c*A[1] + d*A[2] = 0
    # Distance from B to plane = distance from C to plane
    # |b*B[0] + c*B[1] + d*B[2]| / sqrt(b^2+c^2+d^2) = |b*C[0] + c*C[1] + d*C[2]| / sqrt(b^2+c^2+d^2)
    # For plane passing through O(0,0,0) and A(1,2,0): normal can be (b,c,d) where b*1 + c*2 + d*0 = 0 => b = -2c
    # So plane: -2cx + cy + dz = 0 or c(-2x + y) + dz = 0
    # Simplify: take c=1, then -2x + y + (d)z = 0
    # Distance B to plane: |-2*0 + 1*B[1] + d*0| = |B[1]| = B[1]
    # Distance C to plane: |-2*0 + 1*0 + d*C[2]| = |d*C[2]|
    # Equidistant: B[1] = |d*C[2]| => d = ±B[1]/C[2]
    d_coeff = B[1] / C[2]
    # Two solutions: d = B[1]/C[2] or d = -B[1]/C[2]
    true_text = f"Mặt phẳng \\((P)\\) đi qua hai điểm \\(O{format_point(O)}\\), \\(A{format_point(A)}\\) và cách đều hai điểm \\(B{format_point(B)}\\), \\(C{format_point(C)}\\) có dạng \\(6x-3y±4z=0\\)."
    false_text = f"Mặt phẳng đi qua hai điểm \\(O{format_point(O)}\\), \\(A{format_point(A)}\\) và cách đều hai điểm \\(B{format_point(B)}\\), \\(C{format_point(C)}\\) có duy nhất một nghiệm."
    return {"true": true_text, "false": false_text}

# Parameter for plane to be tangent to sphere

def prop_param_plane_tangent_sphere() -> Dict[str, str]:
    # Use integer-based calculations to avoid irrational decimals
    # Sphere: x^2+y^2+z^2+2ux+2vy+2wz+D=0, center (-u,-v,-w), r^2=u^2+v^2+w^2-D
    u, v, w = random.choice([-1, 1]), random.choice([-1, 1]), random.choice([-1, 1])
    # Choose D such that r^2 is a perfect square
    r_sq_candidates = [1, 4, 9, 16]  # Perfect squares for integer radius
    r_sq = random.choice(r_sq_candidates)
    D = u*u + v*v + w*w - r_sq  # Ensure r^2 = u^2+v^2+w^2-D is perfect square
    center = (-u, -v, -w)
    r = int(math.sqrt(r_sq))  # Integer radius
    
    # Plane: ax+by+cz+m=0, choose (a,b,c) from Pythagorean patterns
    normal_choices = [(1, 0, 0), (0, 1, 0), (1, 1, 0), (3, 4, 0)]
    a, b, c = random.choice(normal_choices)
    norm = int(math.sqrt(a*a + b*b + c*c))  # Integer norm
    
    # Tangency: distance from center to plane = radius
    # |a*(-u) + b*(-v) + c*(-w) + m| / norm = r
    base = -a*u - b*v - c*w
    # |base + m| = r * norm
    # m = -base ± r*norm
    m1 = -base + r * norm
    m2 = -base - r * norm
    
    # Format sphere equation
    sphere_terms = []
    sphere_terms.append("x^2+y^2+z^2")
    if u != 0:
        sphere_terms.append(f"{2*u:+}x")
    if v != 0:
        sphere_terms.append(f"{2*v:+}y")
    if w != 0:
        sphere_terms.append(f"{2*w:+}z")
    if D != 0:
        sphere_terms.append(f"{D:+}")
    sphere_eq = "".join(sphere_terms) + "=0"
    
    # Format plane equation parts
    plane_parts = []
    if a != 0:
        if a == 1:
            plane_parts.append("x")
        elif a == -1:
            plane_parts.append("-x")
        else:
            plane_parts.append(f"{a}x")
    if b != 0:
        if plane_parts:
            if b > 0:
                plane_parts.append(f"+{b}y" if b != 1 else "+y")
            else:
                plane_parts.append(f"{b}y" if b != -1 else "-y")
        else:
            plane_parts.append(f"{b}y" if b not in [1, -1] else ("y" if b == 1 else "-y"))
    if c != 0:
        if plane_parts:
            if c > 0:
                plane_parts.append(f"+{c}z" if c != 1 else "+z")
            else:
                plane_parts.append(f"{c}z" if c != -1 else "-z")
        else:
            plane_parts.append(f"{c}z" if c not in [1, -1] else ("z" if c == 1 else "-z"))
    plane_base = "".join(plane_parts)
    
    true_text = f"Cho mặt cầu \\((S): {sphere_eq}\\) và mặt phẳng \\((P): {plane_base}+m=0\\). Để \\((P)\\) tiếp xúc với \\((S)\\), ta có \\(m={m1}\\) hoặc \\(m={m2}\\)."
    false_text = f"Cho mặt cầu \\((S): {sphere_eq}\\) và mặt phẳng \\((P): {plane_base}+m=0\\). Chỉ có duy nhất giá trị \\(m={m1}\\) để \\((P)\\) tiếp xúc với \\((S)\\)."
    return {"true": true_text, "false": false_text}

# Parameter for plane to intersect sphere as circle

def prop_param_plane_intersect_sphere_circle() -> Dict[str, str]:
    # Use integer calculations to avoid irrational decimals
    # Sphere: x^2+y^2+z^2+Ax+By+Cz+D=0
    A, B, C = random.choice([-2, 2]), random.choice([-2, 2]), random.choice([-2, 2])
    D = random.randint(-8, -5)
    center = (-A//2, -B//2, -C//2)  # Use integer center
    # For integer r^2, choose A,B,C,D carefully
    r_sq = (A*A + B*B + C*C)//4 - D  # Integer r^2
    r = int(math.sqrt(r_sq)) if r_sq > 0 else 2  # Integer radius
    
    # Plane: ax+by+m=0, choose (a,b) from Pythagorean patterns
    plane_patterns = [(3, 4), (5, 12), (1, 0), (0, 1)]
    a, b = random.choice(plane_patterns)
    norm = int(math.sqrt(a*a + b*b))  # Integer norm
    
    # For intersection to be a circle: distance from center < radius
    base = a*center[0] + b*center[1]
    threshold = r * norm  # Integer threshold
    
    # |base + m| < threshold => -threshold < base + m < threshold
    # => -threshold - base < m < threshold - base
    m_min = -threshold - base
    m_max = threshold - base
    
    true_text = f"Cho mặt cầu \\((S): x^2+y^2+z^2{A:+}x{B:+}y{C:+}z{D:+}=0\\) và mặt phẳng \\((P): {a}x{b:+}y+m=0\\). Để \\((P)\\) cắt \\((S)\\) theo giao tuyến là đường tròn, cần \\({m_min}<m<{m_max}\\)."
    false_text = f"Cho mặt cầu \\((S): x^2+y^2+z^2{A:+}x{B:+}y{C:+}z{D:+}=0\\) và mặt phẳng \\((P): {a}x{b:+}y+m=0\\). Điều kiện để \\((P)\\) cắt \\((S)\\) theo giao tuyến là đường tròn là \\(m<{m_min}\\) hoặc \\(m>{m_max}\\)."
    return {"true": true_text, "false": false_text}

# Sphere intersects plane with circle of given area/radius

def prop_sphere_plane_intersection_given_radius() -> Dict[str, str]:
    # Use integer calculations to avoid irrational decimals
    center = (random.choice([1, 2]), random.choice([1, 2]), random.choice([1, 2]))
    r_circle = random.choice([3, 4])  # radius of intersection circle
    
    # Choose plane coefficients from Pythagorean patterns to get integer distance
    plane_patterns = [(3, 4, 0, 5), (1, 0, 0, 1), (0, 1, 0, 2), (5, 12, 0, 13)]
    a, b, c, expected_norm = random.choice(plane_patterns)
    
    # Calculate d such that distance from center to plane is integer
    base = a*center[0] + b*center[1] + c*center[2]
    dist_integer = random.choice([1, 2, 3])  # Integer distance
    d = -base + dist_integer * expected_norm  # or -base - dist_integer * expected_norm
    
    # Verify: distance = |a*center[0] + b*center[1] + c*center[2] + d| / norm
    # = |base + d| / norm = |base + (-base ± dist*norm)| / norm = dist (integer)
    
    # Sphere radius: R^2 = dist^2 + r_circle^2 (both integers, so R^2 is integer)
    R_sq = dist_integer*dist_integer + r_circle*r_circle
    
    # Format sphere equation properly
    cx_term = f"(x{-center[0]:+})" if center[0] != 0 else "x"
    cy_term = f"(y{-center[1]:+})" if center[1] != 0 else "y"
    cz_term = f"(z{-center[2]:+})" if center[2] != 0 else "z"
    sphere_eq = f"{cx_term}^2+{cy_term}^2+{cz_term}^2={R_sq}"
    
    true_text = f"Mặt cầu \\((S)\\) có tâm \\(I{format_point(center)}\\) và cắt mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) theo đường tròn có bán kính \\(r={r_circle}\\) có phương trình \\((S): {sphere_eq}\\)."
    false_text = f"Mặt cầu cần thiết có bán kính \\(R={r_circle}\\)."
    return {"true": true_text, "false": false_text}

# Additional 5 generators to reach 15 total

def prop_sphere_tangent_coordinate_planes() -> Dict[str, str]:
    # Sphere tangent to coordinate planes - use integers
    center = (random.choice([2, 3]), random.choice([2, 3]), random.choice([2, 3]))
    r = min(center)  # radius equals minimum coordinate for tangency
    true_text = f"Mặt cầu có tâm \\(I{format_point(center)}\\) và tiếp xúc với các mặt phẳng tọa độ có bán kính \\(r={r}\\)."
    false_text = f"Mặt cầu có tâm \\(I{format_point(center)}\\) và tiếp xúc với các mặt phẳng tọa độ có bán kính \\(r={r+1}\\)."
    return {"true": true_text, "false": false_text}

def prop_plane_sphere_common_points() -> Dict[str, str]:
    # Number of common points between plane and sphere - use integer distance calculations
    center = (random.choice([-2, -1, 0, 1, 2]), random.choice([-2, -1, 0, 1, 2]), random.choice([-2, -1, 0, 1, 2]))
    r = random.choice([3, 4, 5])
    
    # Use Pythagorean patterns for integer norm calculations
    normal_patterns = [(3, 4, 0), (1, 0, 0), (0, 1, 0), (5, 12, 0)]
    a, b, c = random.choice(normal_patterns)
    norm = int(math.sqrt(a*a + b*b + c*c))  # Integer norm
    
    # Choose d to get specific integer distance
    base = a*center[0] + b*center[1] + c*center[2]
    desired_dist = random.choice([1, 2, 6])  # Integer distances
    d = -base + desired_dist * norm  # Distance will be exactly desired_dist
    
    dist = desired_dist  # Integer distance
    
    if dist < r:
        true_text = f"Mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) và mặt cầu tâm \\(I{format_point(center)}\\) bán kính \\({r}\\) có vô số điểm chung."
        false_text = f"Mặt phẳng \\((P)\\) và mặt cầu có đúng một điểm chung."
    else:
        true_text = f"Mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) và mặt cầu tâm \\(I{format_point(center)}\\) bán kính \\({r}\\) không có điểm chung."
        false_text = f"Mặt phẳng \\((P)\\) và mặt cầu có vô số điểm chung."
    return {"true": true_text, "false": false_text}

def prop_sphere_plane_tangent_point() -> Dict[str, str]:
    # Find tangent point between sphere and plane - use integers
    center = (random.choice([-2, -1, 0, 1, 2]), random.choice([-2, -1, 0, 1, 2]), random.choice([-2, -1, 0, 1, 2]))
    r = random.choice([3, 4])
    
    # Create a tangent plane using Pythagorean patterns
    normal_patterns = [(3, 4, 0), (1, 0, 0), (0, 1, 0)]
    a, b, c = random.choice(normal_patterns)
    norm = int(math.sqrt(a*a + b*b + c*c))  # Integer norm
    
    d = -(a*center[0] + b*center[1] + c*center[2]) + r*norm
    # Tangent point calculation is exact with integer arithmetic
    if norm == 1:  # (1,0,0), (0,1,0), (0,0,1)
        if a == 1:
            tangent_pt = (center[0] + r, center[1], center[2])
        elif b == 1:
            tangent_pt = (center[0], center[1] + r, center[2])
        else:
            tangent_pt = (center[0], center[1], center[2] + r)
    else:  # (3,4,0) with norm=5
        # Unit normal = (3/5, 4/5, 0), tangent_pt = center + r*(3/5, 4/5, 0)
        # For integer results, use r=5 to get integer coordinates
        if r != 5:
            r = 5  # Adjust for integer tangent point
            d = -(a*center[0] + b*center[1] + c*center[2]) + r*norm
        tangent_pt = (center[0] + 3, center[1] + 4, center[2])
    
    true_text = f"Mặt cầu tâm \\(I{format_point(center)}\\) bán kính \\({r}\\) tiếp xúc với mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) tại điểm có tọa độ thực."
    false_text = f"Mặt cầu tâm \\(I{format_point(center)}\\) bán kính \\({r}\\) tiếp xúc với mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) tại điểm có tọa độ phức."
    return {"true": true_text, "false": false_text}

def prop_plane_cuts_sphere_diameter() -> Dict[str, str]:
    # Plane cuts sphere along a diameter - use integers
    center = (random.choice([-2, -1, 0, 1, 2]), random.choice([-2, -1, 0, 1, 2]), random.choice([-2, -1, 0, 1, 2]))
    r = random.choice([4, 5])
    # Plane through center has distance 0 from center
    a, b, c = random.choice([1, 2]), random.choice([1, 2]), random.choice([1, 2])
    d = -(a*center[0] + b*center[1] + c*center[2])  # plane through center
    true_text = f"Mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) cắt mặt cầu tâm \\(I{format_point(center)}\\) bán kính \\({r}\\) theo đường tròn lớn có bán kính \\({r}\\)."
    false_text = f"Mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) cắt mặt cầu tâm \\(I{format_point(center)}\\) bán kính \\({r}\\) theo đường tròn có bán kính \\({r-1}\\)."
    return {"true": true_text, "false": false_text}

def prop_two_planes_sphere_intersection() -> Dict[str, str]:
    # Two parallel planes intersecting sphere - use integers
    center = (random.choice([-1, 0, 1]), random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
    r = random.choice([4, 5])
    a, b, c = random.choice([1, 2]), random.choice([1, 2]), random.choice([1, 2])
    # Two parallel planes at distance < r from center
    d1 = -(a*center[0] + b*center[1] + c*center[2]) + 1
    d2 = -(a*center[0] + b*center[1] + c*center[2]) - 1
    true_text = f"Hai mặt phẳng song song \\((P_1): {format_plane_equation(a,b,c,d1)}\\) và \\((P_2): {format_plane_equation(a,b,c,d2)}\\) đều cắt mặt cầu tâm \\(I{format_point(center)}\\) bán kính \\({r}\\) theo hai đường tròn."
    false_text = f"Trong hai mặt phẳng song song \\((P_1): {format_plane_equation(a,b,c,d1)}\\) và \\((P_2): {format_plane_equation(a,b,c,d2)}\\), chỉ có một mặt phẳng cắt mặt cầu tâm \\(I{format_point(center)}\\) bán kính \\({r}\\)."
    return {"true": true_text, "false": false_text}

PART_C_GROUPS: List[List] = [
    # 1. Tiếp tuyến tại điểm (Ví dụ 30, Câu 1)
    [prop_tangent_plane_at_point],
    # 2. Song song và tiếp xúc (Ví dụ 31, Câu 2,3) 
    [prop_plane_parallel_tangent_to_sphere],
    # 3. Song song và cách đều (Ví dụ 32)
    [prop_plane_parallel_equidistant_two_planes],
    # 4. Song song và cắt theo chu vi (Câu 4)
    [prop_plane_sphere_intersection_circumference],
    # 5. Đi qua điểm và cách đều (Câu 5)
    [prop_plane_through_points_equidistant],
    # 6. Bán kính từ khoảng cách (Ví dụ 33, Câu 6)
    [prop_radius_from_center_plane_distance],
    # 7. Điều kiện không giao (Ví dụ 34)
    [prop_plane_sphere_no_intersection_param],
    # 8. Tham số tiếp xúc (Câu 7)
    [prop_param_plane_tangent_sphere],
    # 9. Điều kiện cắt theo đường tròn (Câu 8)
    [prop_param_plane_intersect_sphere_circle],
    # 10. Giao tuyến có bán kính cho trước (Câu 10)
    [prop_sphere_plane_intersection_given_radius],
    # 11-15. Các generators bổ sung để đủ 15
    [prop_sphere_tangent_coordinate_planes],
    [prop_plane_sphere_common_points],
    [prop_sphere_plane_tangent_point],
    [prop_plane_cuts_sphere_diameter],
    [prop_two_planes_sphere_intersection],
]


def generate_question(question_number: int) -> str:
    # Chọn 1 nhóm mapping trong phần C, lấy 1 mệnh đề từ nhóm đó
    selected_group = random.choice(PART_C_GROUPS)
    primary_gen = random.choice(selected_group)
    # Pool còn lại: tất cả generator của phần C trừ nhóm đã chọn
    all_gens: List = []
    for grp in PART_C_GROUPS:
        for g in grp:
            all_gens.append(g)
    remaining_pool = [g for g in all_gens if g not in selected_group]
    if len(remaining_pool) >= 3:
        other_gens = random.sample(remaining_pool, 3)
    else:
        other_gens = [random.choice(remaining_pool) for _ in range(3)] if remaining_pool else [primary_gen]*3
    selected_gens = [primary_gen] + other_gens
    props: List[Dict[str, str]] = [gen() for gen in selected_gens]
    num_true = random.randint(1, 4)
    true_indices = set(random.sample(range(4), num_true))
    labels = ['a', 'b', 'c', 'd']
    content = f"Câu {question_number}: Chọn các mệnh đề đúng.\n\n"
    for i in range(4):
        txt = props[i]['true'] if i in true_indices else props[i]['false']
        mark = '*' if i in true_indices else ''
        content += f"{mark}{labels[i]}) {txt}\n\n"
    return content


def create_latex_document(questions: List[str], title: str = "Tương giao mặt phẳng và mặt cầu - Đúng/Sai") -> str:
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


def generate_all_propositions() -> List[str]:
    """Generate questions using all 15 proposition types in order, grouping them into 3-4 complete questions"""
    # Use generators in order (không trộn lẫn để tương ứng với file tex gốc)
    all_generators = []
    for group in PART_C_GROUPS:
        for gen in group:
            all_generators.append(gen)
    
    # Generate all 15 propositions in order
    all_props = []
    for gen in all_generators:
        prop = gen()
        all_props.append(prop)
    
    # Group propositions into 4-option questions (3-4 questions total)
    questions = []
    props_per_question = 4
    num_questions = (len(all_props) + props_per_question - 1) // props_per_question  # ceiling division
    
    for q_idx in range(num_questions):
        start_idx = q_idx * props_per_question
        end_idx = min(start_idx + props_per_question, len(all_props))
        question_props = all_props[start_idx:end_idx]
        
        # Create question with these propositions
        question_content = f"Câu {q_idx + 1}: Chọn các mệnh đề đúng.\n\n"
        
        # Determine how many will be true (1-3 for variety)
        num_true = random.randint(1, min(3, len(question_props)))
        true_indices = set(random.sample(range(len(question_props)), num_true))
        
        labels = ['a', 'b', 'c', 'd']
        for i, prop in enumerate(question_props):
            if i < len(labels):
                is_true = i in true_indices
                text = prop['true'] if is_true else prop['false']
                mark = '*' if is_true else ''
                question_content += f"{mark}{labels[i]}) {text}\n\n"
        
        questions.append(question_content)
    
    return questions


def main():
    import sys
    
    # Check if 'all' option is used
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'all':
        qs = generate_all_propositions()
        title = "Tương giao mặt phẳng và mặt cầu - Tất cả các dạng bài"
    else:
        # Original behavior for random questions
        try:
            num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 5
        except Exception:
            num_questions = 5
        qs = [generate_question(i+1) for i in range(num_questions)]
        title = "Tương giao mặt phẳng và mặt cầu - Đúng/Sai"
    
    tex = create_latex_document(qs, title)
    out = "plane_true_false_part_C.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(qs)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()
