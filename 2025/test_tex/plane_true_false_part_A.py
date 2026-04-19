import math
import random
from typing import List, Tuple, Dict, Optional
from fractions import Fraction
from dataclasses import dataclass

# Constants
COORD_RANGE = (-4, 5)
SMALL_COORD_RANGE = (-3, 4)
PLANE_COEFF_RANGE = (-5, 6)
CONST_TERM_RANGE = (-8, 9)
ANGLE_DELTA_OPTIONS = [-15, -10, 10, 15]
DISTANCE_DELTA_OPTIONS = [1, 2, 3]
FALSE_COORD_DELTA = [-1, 1]
MAX_RETRIES = 100

# Data Classes

@dataclass
class PlaneParams:
    """Represents plane equation ax + by + cz + d = 0"""
    a: int
    b: int
    c: int
    d: int
    
@dataclass
class Point3D:
    """Represents a 3D point"""
    x: int
    y: int
    z: int
    
    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.x, self.y, self.z)

# Utility Classes

class PlaneGenerator:
    """Utility class for generating random planes with various constraints"""
    
    @staticmethod
    def random_coefficients(coeff_range: Tuple[int, int] = COORD_RANGE, 
                          ensure_non_zero: bool = True) -> Tuple[int, int, int]:
        """Generate random plane coefficients (a, b, c)"""
        if ensure_non_zero:
            a = random.choice([v for v in range(*coeff_range) if v != 0])
        else:
            a = random.randint(*coeff_range)
        b = random.randint(*coeff_range)
        c = random.randint(*coeff_range)
        
        # Ensure at least one coefficient is non-zero
        if a == 0 and b == 0 and c == 0:
            a = 1
            
        return a, b, c
    
    @staticmethod
    def random_plane(coeff_range: Tuple[int, int] = COORD_RANGE,
                    const_range: Tuple[int, int] = CONST_TERM_RANGE,
                    ensure_non_zero: bool = True) -> PlaneParams:
        """Generate a random plane"""
        a, b, c = PlaneGenerator.random_coefficients(coeff_range, ensure_non_zero)
        d = random.randint(*const_range)
        return PlaneParams(a, b, c, d)
    
    @staticmethod
    def parallel_plane(base_plane: PlaneParams, scale_factor: Optional[int] = None) -> PlaneParams:
        """Generate a plane parallel to the given plane"""
        if scale_factor is None:
            scale_factor = random.choice([2, 3, -2, -3])
        
        # Parallel planes have proportional normal vectors
        a2 = scale_factor * base_plane.a
        b2 = scale_factor * base_plane.b  
        c2 = scale_factor * base_plane.c
        
        # Different constant term to avoid identical planes
        d2 = random.randint(*CONST_TERM_RANGE)
        while d2 == scale_factor * base_plane.d:
            d2 = random.randint(*CONST_TERM_RANGE)
            
        return PlaneParams(a2, b2, c2, d2)

class PointGenerator:
    """Utility class for generating random points with various constraints"""
    
    @staticmethod
    def random_point(coord_range: Tuple[int, int] = SMALL_COORD_RANGE) -> Point3D:
        """Generate a random 3D point"""
        x = random.randint(*coord_range)
        y = random.randint(*coord_range)
        z = random.randint(*coord_range)
        return Point3D(x, y, z)
    
    @staticmethod
    def point_on_plane(plane: PlaneParams, 
                      coord_range: Tuple[int, int] = SMALL_COORD_RANGE) -> Tuple[Point3D, PlaneParams]:
        """Generate a point that lies on the given plane"""
        x = random.randint(*coord_range)
        y = random.randint(*coord_range)
        
        if plane.c == 0:
            # If c=0, adjust d to ensure point is on plane
            z = random.randint(*coord_range)
            d_adjusted = -(plane.a * x + plane.b * y)
            # Return point with adjusted plane parameters
            return Point3D(x, y, z), PlaneParams(plane.a, plane.b, plane.c, d_adjusted)
        else:
            # Calculate z so that a*x + b*y + c*z + d = 0
            numerator = -(plane.a * x + plane.b * y + plane.d)
            if numerator % plane.c == 0:
                z = numerator // plane.c
            else:
                # Adjust d to get integer z
                z = random.randint(*coord_range)
                d_adjusted = -(plane.a * x + plane.b * y + plane.c * z)
                return Point3D(x, y, z), PlaneParams(plane.a, plane.b, plane.c, d_adjusted)
            
        return Point3D(x, y, z), plane
    
    @staticmethod
    def modify_point(point: Point3D, delta_options: List[int] = FALSE_COORD_DELTA) -> Point3D:
        """Create a slightly modified version of the point"""
        delta = random.choice(delta_options)
        # Modify one coordinate randomly
        coord_to_modify = random.choice(['x', 'y', 'z'])
        if coord_to_modify == 'x':
            return Point3D(point.x + delta, point.y, point.z)
        elif coord_to_modify == 'y':
            return Point3D(point.x, point.y + delta, point.z)
        else:
            return Point3D(point.x, point.y, point.z + delta)

class DistanceCalculator:
    """Utility class for various distance calculations"""
    
    @staticmethod
    def point_to_plane(plane: PlaneParams, point: Point3D) -> Tuple[int, int]:
        """Calculate distance from point to plane. Returns (numerator, norm_squared)"""
        numer = abs(plane.a * point.x + plane.b * point.y + plane.c * point.z + plane.d)
        norm_sq = plane.a * plane.a + plane.b * plane.b + plane.c * plane.c
        return numer, norm_sq
    
    @staticmethod
    def between_parallel_planes(plane1: PlaneParams, plane2: PlaneParams) -> Tuple[int, int]:
        """Calculate distance between two parallel planes. Returns (numerator, norm_squared)"""
        # Assuming planes are parallel (same normal vector up to scaling)
        numer = abs(plane1.d - plane2.d)
        norm_sq = plane1.a * plane1.a + plane1.b * plane1.b + plane1.c * plane1.c
        return numer, norm_sq

class AngleCalculator:
    """Utility class for angle calculations between planes"""
    
    @staticmethod
    def between_planes(plane1: PlaneParams, plane2: PlaneParams) -> float:
        """Calculate angle between two planes in degrees"""
        n1 = (plane1.a, plane1.b, plane1.c)
        n2 = (plane2.a, plane2.b, plane2.c)
        
        num = abs(dot(n1, n2))
        den = math.sqrt((plane1.a**2 + plane1.b**2 + plane1.c**2) * 
                       (plane2.a**2 + plane2.b**2 + plane2.c**2))
        cos_val = min(1.0, max(0.0, num / den if den != 0 else 0.0))
        return math.degrees(math.acos(cos_val))
    
    @staticmethod
    def plane_with_oxy(plane: PlaneParams) -> float:
        """Calculate angle between plane and Oxy coordinate plane"""
        # Normal to Oxy is (0, 0, 1)
        num = abs(plane.c)
        den = math.sqrt(plane.a**2 + plane.b**2 + plane.c**2)
        cos_val = min(1.0, max(0.0, num / den if den != 0 else 0.0))
        return math.degrees(math.acos(cos_val))
    
    @staticmethod
    def plane_with_coordinate_plane(plane: PlaneParams, coord_plane: str) -> Tuple[float, str]:
        """Calculate angle between plane and coordinate plane (Oxy, Oyz, or Oxz)"""
        if coord_plane == "Oxy":
            # Normal to Oxy is (0, 0, 1)
            num = abs(plane.c)
            plane_name = "Oxy"
        elif coord_plane == "Oyz":
            # Normal to Oyz is (1, 0, 0)
            num = abs(plane.a)
            plane_name = "Oyz"
        elif coord_plane == "Oxz":
            # Normal to Oxz is (0, 1, 0)
            num = abs(plane.b)
            plane_name = "Oxz"
        else:
            raise ValueError(f"Unknown coordinate plane: {coord_plane}")
            
        den = math.sqrt(plane.a**2 + plane.b**2 + plane.c**2)
        cos_val = min(1.0, max(0.0, num / den if den != 0 else 0.0))
        angle = math.degrees(math.acos(cos_val))
        return angle, plane_name

# Base Classes for Proposition Generation

from abc import ABC, abstractmethod

class BaseProposition(ABC):
    """Abstract base class for all proposition generators using Template Method pattern"""
    
    def generate(self) -> Dict[str, str]:
        """Template method - defines the algorithm structure"""
        # Step 1: Generate mathematical objects
        data = self.generate_mathematical_objects()
        
        # Step 2: Calculate true result
        true_result = self.calculate_true_result(data)
        
        # Step 3: Generate false result  
        false_result = self.generate_false_result(data, true_result)
        
        # Step 4: Format texts
        true_text = self.format_true_text(data, true_result)
        false_text = self.format_false_text(data, false_result)
        
        return {"true": true_text, "false": false_text}
    
    @abstractmethod
    def generate_mathematical_objects(self) -> Dict:
        """Generate the mathematical objects needed for this proposition type"""
        pass
    
    @abstractmethod
    def calculate_true_result(self, data: Dict) -> Dict:
        """Calculate the true mathematical result"""
        pass
    
    @abstractmethod
    def generate_false_result(self, data: Dict, true_result: Dict) -> Dict:
        """Generate a false result based on the true result"""
        pass
    
    @abstractmethod
    def format_true_text(self, data: Dict, result: Dict) -> str:
        """Format the true proposition text"""
        pass
    
    @abstractmethod
    def format_false_text(self, data: Dict, result: Dict) -> str:
        """Format the false proposition text"""
        pass


class DistanceProposition(BaseProposition):
    """Base class for all distance-related propositions"""
    
    def generate_false_result(self, data: Dict, true_result: Dict) -> Dict:
        """Common false result generation for distance propositions"""
        delta = random.choice(DISTANCE_DELTA_OPTIONS)
        false_numer = true_result['numer'] + delta if true_result['numer'] != 0 else true_result['numer'] + 2
        return {
            'numer': false_numer,
            'norm_sq': true_result['norm_sq']
        }


class AngleProposition(BaseProposition):
    """Base class for all angle-related propositions"""
    
    def generate_false_result(self, data: Dict, true_result: Dict) -> Dict:
        """Common false result generation for angle propositions"""
        false_angle = true_result['angle'] + random.choice(ANGLE_DELTA_OPTIONS)
        return {'angle': false_angle}


# Concrete Proposition Classes

class PointPlaneDistanceProposition(DistanceProposition):
    """Point to plane distance proposition using new architecture"""
    
    def generate_mathematical_objects(self) -> Dict:
        return {
            'plane': PlaneGenerator.random_plane(PLANE_COEFF_RANGE, CONST_TERM_RANGE),
            'point': PointGenerator.random_point(COORD_RANGE)
        }
    
    def calculate_true_result(self, data: Dict) -> Dict:
        numer, norm_sq = DistanceCalculator.point_to_plane(data['plane'], data['point'])
        return {'numer': numer, 'norm_sq': norm_sq}
    
    def format_true_text(self, data: Dict, result: Dict) -> str:
        return f"Khoảng cách từ điểm A{format_point3d(data['point'])} đến mặt phẳng (P): {format_plane_params(data['plane'])} bằng \\( {format_distance(result['numer'], result['norm_sq'])} \\)."
    
    def format_false_text(self, data: Dict, result: Dict) -> str:
        return f"Khoảng cách từ điểm A{format_point3d(data['point'])} đến mặt phẳng (P): {format_plane_params(data['plane'])} bằng \\( {format_distance(result['numer'], result['norm_sq'])} \\)."


class ProjectionDistanceProposition(DistanceProposition):
    """Point projection distance proposition - reuses DistanceProposition logic"""
    
    def generate_mathematical_objects(self) -> Dict:
        return {
            'plane': PlaneGenerator.random_plane(COORD_RANGE, CONST_TERM_RANGE),
            'point': PointGenerator.random_point(SMALL_COORD_RANGE)
        }
    
    def calculate_true_result(self, data: Dict) -> Dict:
        numer, norm_sq = DistanceCalculator.point_to_plane(data['plane'], data['point'])
        return {'numer': numer, 'norm_sq': norm_sq}
    
    def format_true_text(self, data: Dict, result: Dict) -> str:
        return f"Gọi H là hình chiếu của điểm A{format_point3d(data['point'])} lên mặt phẳng \\((P): {format_plane_params(data['plane'])}\\). Độ dài đoạn \\(AH\\) bằng \\({format_distance(result['numer'], result['norm_sq'])}\\)."
    
    def format_false_text(self, data: Dict, result: Dict) -> str:
        return f"Gọi H là hình chiếu của điểm A{format_point3d(data['point'])} lên mặt phẳng \\((P): {format_plane_params(data['plane'])}\\). Độ dài đoạn \\(AH\\) bằng \\({format_distance(result['numer'], result['norm_sq'])}\\)."


class AngleBetweenPlanesProposition(AngleProposition):
    """Angle between two planes proposition"""
    
    def generate_mathematical_objects(self) -> Dict:
        return {
            'plane1': PlaneGenerator.random_plane(SMALL_COORD_RANGE, (-6, 7)),
            'plane2': PlaneGenerator.random_plane(SMALL_COORD_RANGE, (-6, 7))
        }
    
    def calculate_true_result(self, data: Dict) -> Dict:
        angle_deg = AngleCalculator.between_planes(data['plane1'], data['plane2'])
        return {'angle': angle_deg}
    
    def format_true_text(self, data: Dict, result: Dict) -> str:
        angle_disp = f"{result['angle']:.1f}^\\circ"
        return f"Góc giữa hai mặt phẳng \\((P): {format_plane_params(data['plane1'])}\\) và \\((Q): {format_plane_params(data['plane2'])}\\) bằng \\({angle_disp}\\)."
    
    def format_false_text(self, data: Dict, result: Dict) -> str:
        angle_disp = f"{result['angle']:.1f}^\\circ"
        return f"Góc giữa hai mặt phẳng \\((P): {format_plane_params(data['plane1'])}\\) và \\((Q): {format_plane_params(data['plane2'])}\\) bằng \\({angle_disp}\\)."


# Factory function to create proposition instances
def create_proposition(prop_type: str) -> BaseProposition:
    """Factory function to create proposition instances"""
    propositions = {
        'point_plane_distance': PointPlaneDistanceProposition,
        'projection_distance': ProjectionDistanceProposition,
        'angle_between_planes': AngleBetweenPlanesProposition,
    }
    
    if prop_type not in propositions:
        raise ValueError(f"Unknown proposition type: {prop_type}")
    
    return propositions[prop_type]()


# Original Utilities

def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


def simplify_fraction(numer: int, denom: int) -> Tuple[int, int]:
    if denom == 0:
        return (numer, denom)
    g = gcd(numer, denom)
    numer //= g
    denom //= g
    if denom < 0:
        numer = -numer
        denom = -denom
    return numer, denom


def format_signed(value: int) -> str:
    return f"+ {abs(value)}" if value > 0 else (f"- {abs(value)}" if value < 0 else "+ 0")


def format_plane_equation(a: int, b: int, c: int, d: int) -> str:
    parts: List[str] = []
    # ax
    if a == 1:
        parts.append("x")
    elif a == -1:
        parts.append("-x")
    elif a != 0:
        parts.append(f"{a}x")
    # by
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
    # cz
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
    # d
    if d != 0:
        if d > 0 and parts:
            parts.append(f"+ {d}")
        else:
            parts.append(str(d))
    if not parts:
        parts.append("0")
    return " ".join(parts) + " = 0"


def format_point(pt: Tuple[int, int, int]) -> str:
    return f"({pt[0]};{pt[1]};{pt[2]})"


def format_point3d(point: Point3D) -> str:
    """Format Point3D object to LaTeX string"""
    return f"({point.x};{point.y};{point.z})"


def format_plane_params(plane: PlaneParams) -> str:
    """Format PlaneParams object to LaTeX equation string"""
    return format_plane_equation(plane.a, plane.b, plane.c, plane.d)


def are_collinear(v: Tuple[int, int, int], w: Tuple[int, int, int]) -> bool:
    x1, y1, z1 = v
    x2, y2, z2 = w
    return (x1 * y2 == y1 * x2) and (x1 * z2 == z1 * x2) and (y1 * z2 == z1 * y2)


def dot(v: Tuple[int, int, int], w: Tuple[int, int, int]) -> int:
    return v[0]*w[0] + v[1]*w[1] + v[2]*w[2]


def cross(u: Tuple[int, int, int], v: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return (
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0]
    )


def point_plane_distance(a: int, b: int, c: int, d: int, P: Tuple[int, int, int]) -> Tuple[int, int]:
    """Calculate distance from point to plane. Returns (numerator, norm_squared) where distance = numerator/sqrt(norm_squared)"""
    numer = abs(a*P[0] + b*P[1] + c*P[2] + d)
    norm_sq = a*a + b*b + c*c
    return numer, norm_sq


def format_distance(numer: int, norm_sq: int) -> str:
    # returns LaTeX like \dfrac{numer}{\sqrt{norm_sq}}
    if norm_sq == 0:
        return "0"
    return f"\\dfrac{{{numer}}}{{\\sqrt{{{norm_sq}}}}}"


# Proposition generators for Part A

# NEW CLASS-BASED GENERATORS (using the new architecture)

def prop_point_plane_distance_new() -> Dict[str, str]:
    """Point-plane distance using new class-based architecture"""
    prop = create_proposition('point_plane_distance')
    return prop.generate()

def prop_point_projection_distance_new() -> Dict[str, str]:
    """Point projection distance using new class-based architecture"""  
    prop = create_proposition('projection_distance')
    return prop.generate()

def prop_angle_between_planes_new() -> Dict[str, str]:
    """Angle between planes using new class-based architecture"""
    prop = create_proposition('angle_between_planes')
    return prop.generate()

# EXISTING GENERATORS (partially refactored with utilities)

# Group: Ví dụ 4,5 (distance point-plane) + Câu 7 (reflection => AB = 2*distance)

def prop_point_plane_distance() -> Dict[str, str]:
    """Generate random plane and point for distance calculation - REFACTORED"""
    # Using new utility classes - much cleaner!
    plane = PlaneGenerator.random_plane(PLANE_COEFF_RANGE, CONST_TERM_RANGE)
    point = PointGenerator.random_point(COORD_RANGE)
    numer, norm_sq = DistanceCalculator.point_to_plane(plane, point)
    
    true_text = f"Khoảng cách từ điểm A{format_point3d(point)} đến mặt phẳng (P): {format_plane_params(plane)} bằng \\( {format_distance(numer, norm_sq)} \\)."
    
    # false: tweak numerator by ±1..3 (ensure different)
    delta = random.choice(DISTANCE_DELTA_OPTIONS)
    false_numer = numer + delta if numer != 0 else numer + 2
    false_text = f"Khoảng cách từ điểm A{format_point3d(point)} đến mặt phẳng (P): {format_plane_params(plane)} bằng \\( {format_distance(false_numer, norm_sq)} \\)."
    return {"true": true_text, "false": false_text}


def prop_reflection_segment_length() -> Dict[str, str]:
    """AB length for reflection across plane equals 2 * distance(A, plane)"""
    a = random.choice([v for v in range(*COORD_RANGE) if v != 0])
    b = random.randint(*COORD_RANGE)
    c = random.randint(*COORD_RANGE)
    if a == 0 and b == 0 and c == 0:
        b = 1
    d = random.randint(-6, 6)
    A = (random.randint(*SMALL_COORD_RANGE), random.randint(*SMALL_COORD_RANGE), random.randint(*SMALL_COORD_RANGE))
    numer, norm_sq = point_plane_distance(a, b, c, d, A)
    
    # AB = 2 * numer / sqrt(norm_sq)
    true_text = f"Gọi B là điểm đối xứng của A{format_point(A)} qua mặt phẳng (P): {format_plane_equation(a,b,c,d)}. Khi đó độ dài \\(AB\\) bằng \\({format_distance(2*numer, norm_sq)}\\)."
    
    # false: tweak numerator
    delta = random.choice([1, 2])
    false_text = f"Gọi B là điểm đối xứng của A{format_point(A)} qua mặt phẳng (P): {format_plane_equation(a,b,c,d)}. Khi đó độ dài \\(AB\\) bằng \\({format_distance(2*numer + delta, norm_sq)}\\)."
    return {"true": true_text, "false": false_text}

# Group: Ví dụ 3 (point on plane) - Câu 4 (m-parameter point on plane)

def prop_point_on_plane_membership() -> Dict[str, str]:
    a = random.choice([v for v in range(*COORD_RANGE) if v != 0])
    b = random.randint(*COORD_RANGE)
    c = random.randint(*COORD_RANGE)
    d = random.randint(-6, 6)
    
    # Create a point on plane by choosing x,y and calculating z
    x = random.randint(*SMALL_COORD_RANGE)
    y = random.randint(*SMALL_COORD_RANGE)
    
    if c == 0:
        # If c=0, ensure a*x + b*y + d = 0 by adjusting d
        z = random.randint(*SMALL_COORD_RANGE)
        d = -(a*x + b*y)  # Make sure point is on plane
    else:
        # Calculate z so that a*x + b*y + c*z + d = 0
        numerator = -(a*x + b*y + d)
        if numerator % c == 0:
            z = numerator // c  # Exact integer solution
        else:
            # Adjust d to get integer z
            z = random.randint(*SMALL_COORD_RANGE)
            d = -(a*x + b*y + c*z)
    
    P = (x, y, z)
    true_text = f"Điểm M{format_point(P)} thuộc mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\)."
    
    # false: modify one coordinate
    Pf = (P[0] + random.choice(FALSE_COORD_DELTA), P[1], P[2])
    false_text = f"Điểm M{format_point(Pf)} thuộc mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\)."
    return {"true": true_text, "false": false_text}


def prop_point_with_m_on_plane() -> Dict[str, str]:
    """Point A(m; m-1; 1+2m) in plane ax+by+cz+d=0 -> find m value. We convert to T/F: with given m value, statement true/false"""
    a = random.choice([v for v in range(*SMALL_COORD_RANGE) if v != 0])
    b = random.randint(*SMALL_COORD_RANGE)
    c = random.randint(*SMALL_COORD_RANGE)
    d = random.randint(-6, 6)
    
    # Compute m solving a*m + b*(m-1) + c*(1+2m) + d = 0
    coeff_m = a + b + 2*c
    const_term = -b + c + d
    
    # Ensure solvable (coeff_m != 0)
    if coeff_m == 0:
        coeff_m = 1
    
    m_true = -const_term / coeff_m
    
    # Prefer integer m
    if abs(m_true - round(m_true)) < 1e-9:
        m_display = str(int(round(m_true)))
    else:
        # format as fraction p/q
        frac = Fraction(-const_term, coeff_m)
        m_display = f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
    
    true_text = f"Với \\(m = {m_display}\\), điểm \\(A(m;\\, m-1;\\, 1+2m)\\) thuộc mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\)."
    
    # false: tweak m by +1 or -1
    if isinstance(m_true, float) and abs(m_true - round(m_true)) < 1e-9:
        m_false_display = str(int(round(m_true)) + random.choice(FALSE_COORD_DELTA))
    else:
        m_false_display = "0" if m_display != "0" else "1"
    
    false_text = f"Với \\(m = {m_false_display}\\), điểm \\(A(m;\\, m-1;\\, 1+2m)\\) thuộc mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\)."
    return {"true": true_text, "false": false_text}

# Group: Ví dụ 7 (distance constraint) - Câu 12 (equal distances)

def prop_equal_distance_to_plane_and_point_on_Oz() -> Dict[str, str]:
    """Generate M(0,0,k) on Oz such that d(M,P) = d(M,A) with correct calculation"""
    # Use simple, verifiable case to avoid complex quadratic errors
    a = random.choice([1, 2, -1, -2])
    b = random.choice([1, 2, -1, -2])
    c = random.choice([1, 2, -1, -2])
    d = random.randint(-5, 5)
    A = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
    
    # For M(0,0,k), we need d(M,P) = d(M,A)
    # d(M,P) = |a*0 + b*0 + c*k + d| / sqrt(a^2 + b^2 + c^2) = |ck + d| / norm
    # d(M,A) = sqrt((0-Ax)^2 + (0-Ay)^2 + (k-Az)^2) = sqrt(Ax^2 + Ay^2 + (k-Az)^2)
    
    # This leads to: |ck + d|^2 / (a^2 + b^2 + c^2) = Ax^2 + Ay^2 + (k-Az)^2
    # We'll solve this correctly or use fallback
    
    norm_sq = a*a + b*b + c*c
    Ax, Ay, Az = A
    
    # Try to find a reasonable k value with verification
    # We'll use a different approach: pick k and verify
    for attempt in range(10):
        k_candidate = random.randint(-3, 3)
        
        # Calculate both distances
        dist_to_plane = abs(c * k_candidate + d) / math.sqrt(norm_sq)
        dist_to_A = math.sqrt(Ax*Ax + Ay*Ay + (k_candidate - Az)*(k_candidate - Az))
        
        # If they're approximately equal (within tolerance), use this k
        if abs(dist_to_plane - dist_to_A) < 0.1:
            k_true = k_candidate
            break
    else:
        # Fallback to simple verified case
        a, b, c, d = 0, 0, 1, 0
        A = (0, 0, 2)
        k_true = 1  # d(M,P) = |0+0+1*1+0|/1 = 1, d(M,A) = sqrt(0+0+1) = 1 ✓
    
    # Format display
    k_disp = f"{k_true:.2f}" if abs(k_true - round(k_true)) > 1e-9 else str(int(round(k_true)))
    true_text = f"Tồn tại điểm \\(M(0;0;{k_disp})\\) sao cho \\(d(M,(P)) = d(M,A)\\) với \\({{}}A{format_point(A)}\\) và \\((P): {format_plane_equation(a,b,c,d)}\\)."
    
    # False: use a k that definitely doesn't work
    k_false = k_true + random.choice([2, -2, 3, -3])
    k_false_disp = f"{k_false:.2f}" if abs(k_false - round(k_false)) > 1e-9 else str(int(round(k_false)))
    false_text = f"Tồn tại điểm \\(M(0;0;{k_false_disp})\\) sao cho \\(d(M,(P)) = d(M,A)\\) với \\({{}}A{format_point(A)}\\) và \\((P): {format_plane_equation(a,b,c,d)}\\)."
    
    return {"true": true_text, "false": false_text}

# Group: Ví dụ 8 (angle between planes) - Câu 14 (angle with coordinate planes)

def prop_angle_between_planes() -> Dict[str, str]:
    """Angle between planes P: a1x+b1y+c1z+d1=0 and Q: a2x+b2y+c2z+d2=0 - REFACTORED"""
    # Using new utility classes - much cleaner angle calculation!
    plane1 = PlaneGenerator.random_plane(SMALL_COORD_RANGE, (-6, 7))
    plane2 = PlaneGenerator.random_plane(SMALL_COORD_RANGE, (-6, 7))
    
    angle_deg = AngleCalculator.between_planes(plane1, plane2)
    angle_disp = f"{angle_deg:.1f}^\\circ"
    
    true_text = f"Góc giữa hai mặt phẳng \\((P): {format_plane_params(plane1)}\\) và \\((Q): {format_plane_params(plane2)}\\) bằng \\({angle_disp}\\)."
    
    # false: tweak by degrees from ANGLE_DELTA_OPTIONS
    false_angle = angle_deg + random.choice(ANGLE_DELTA_OPTIONS)
    false_text = f"Góc giữa hai mặt phẳng \\((P): {format_plane_params(plane1)}\\) và \\((Q): {format_plane_params(plane2)}\\) bằng \\({false_angle:.1f}^\\circ\\)."
    return {"true": true_text, "false": false_text}


def prop_angle_plane_with_coordinate_plane() -> Dict[str, str]:
    """Angle between plane P and coordinate plane (Oxy, Oyz, or Oxz) - REFACTORED"""
    # Using new utility classes - much cleaner!
    plane = PlaneGenerator.random_plane(SMALL_COORD_RANGE, (-6, 7))
    
    # Randomly choose coordinate plane
    coord_plane = random.choice(["Oxy", "Oyz", "Oxz"])
    angle_deg, plane_name = AngleCalculator.plane_with_coordinate_plane(plane, coord_plane)
    angle_disp = f"{angle_deg:.1f}^\\circ"
    
    true_text = f"Góc giữa mặt phẳng \\((P): {format_plane_params(plane)}\\) và mặt phẳng \\(({plane_name})\\) bằng \\({angle_disp}\\)."
    
    false_angle = angle_deg + random.choice(ANGLE_DELTA_OPTIONS)
    false_text = f"Góc giữa mặt phẳng \\((P): {format_plane_params(plane)}\\) và mặt phẳng \\(({plane_name})\\) bằng \\({false_angle:.1f}^\\circ\\)."
    return {"true": true_text, "false": false_text}

# Group: Ví dụ 9 (parallel planes), Câu 16 (intersect), Câu 17 (perpendicular)

def prop_planes_parallel_simple() -> Dict[str, str]:
    """Construct two parallel planes by scaling the normal vector"""
    a, b, c = random.choice([1, 2, 3, 4]), random.choice([-3, -2, -1, 1, 2, 3]), random.choice([-3, -2, -1, 1, 2, 3])
    
    # Ensure non-zero normal
    if a == 0 and b == 0 and c == 0:
        a = 1
    
    k = random.choice([2, 3, -2])
    d1 = random.randint(-6, 6)
    
    # Ensure d2 != k*d1 to avoid identical planes
    d2 = random.randint(-6, 6)
    while d2 == k * d1:
        d2 = random.randint(-6, 6)
    
    true_text = f"Hai mặt phẳng \\((P): {format_plane_equation(a,b,c,d1)}\\) và \\((Q): {format_plane_equation(k*a,k*b,k*c,d2)}\\) song song."
    
    # False: perturb one component to break proportionality
    a2, b2, c2 = k*a, k*b + 1, k*c
    false_text = f"Hai mặt phẳng \\((P): {format_plane_equation(a,b,c,d1)}\\) và \\((Q): {format_plane_equation(a2,b2,c2,d2)}\\) song song."
    return {"true": true_text, "false": false_text}


def prop_planes_intersect_condition_m() -> Dict[str, str]:
    """(P): 2x+2y - z = 0 and (Q): x + y + m z + 1 = 0 intersect iff normals not parallel
    Normals are (2,2,-1) and (1,1,m). Parallel when (1,1,m) = k*(2,2,-1)
    This gives: 1=2k, 1=2k, m=-k, so k=1/2 and m=-1/2
    """
    # Choose m that makes planes intersect (not parallel)
    m_true = random.choice([v for v in range(-4, 5) if v not in [0, -1]])
    # For false case, use m = -1/2 which makes planes parallel
    
    true_text = f"Hai mặt phẳng \\((P): 2x + 2y - z = 0\\) và \\((Q): x + y + {m_true}z + 1 = 0\\) cắt nhau."
    false_text = f"Hai mặt phẳng \\((P): 2x + 2y - z = 0\\) và \\((Q): x + y - \\frac{{1}}{{2}}z + 1 = 0\\) cắt nhau."
    return {"true": true_text, "false": false_text}


def prop_planes_perpendicular_condition_m() -> Dict[str, str]:
    """(alpha): m^2 x - y + (m^2 - 2) z + 2 = 0 and (beta): 2x + m^2 y - 2z + 1 = 0 perpendicular when dot(n1,n2)=0
    dot(n1,n2) = (m^2)*2 + (-1)*(m^2) + (m^2-2)*(-2) = 4 - m^2 => perpendicular iff m^2 = 4
    """
    m_true = random.choice([2, -2])
    m_sq_true = m_true * m_true  # = 4
    
    true_text = f"Hai mặt phẳng \\((\\alpha): {m_sq_true}x - y + {(m_sq_true - 2)}z + 2 = 0\\) và \\((\\beta): 2x + {m_sq_true}y - 2z + 1 = 0\\) vuông góc."
    
    # choose m_false not satisfying m^2=4
    m_false = random.choice([0, 1, 3, -1, -3])
    m_sq_false = m_false * m_false
    false_text = f"Hai mặt phẳng \\((\\alpha): {m_sq_false}x - y + {(m_sq_false - 2)}z + 2 = 0\\) và \\((\\beta): 2x + {m_sq_false}y - 2z + 1 = 0\\) vuông góc."
    return {"true": true_text, "false": false_text}


# NEW PROPOSITION GENERATORS FOR MISSING PROBLEM TYPES

# Group: Ví dụ 1,2 (normal vector) + Câu 1,2 (normal vector from direction vectors)

def prop_normal_vector_from_equation() -> Dict[str, str]:
    """Given plane equation, identify correct normal vector"""
    a = random.choice([v for v in range(*SMALL_COORD_RANGE) if v != 0])
    b = random.randint(*SMALL_COORD_RANGE)
    c = random.choice([v for v in range(*SMALL_COORD_RANGE) if v != 0])
    d = random.randint(-6, 6)
    
    # True normal vector
    true_normal = (a, b, c)
    
    # Generate false options by modifying components
    false_options = [
        (-a, b, c),      # Wrong sign on first component
        (a, -b, c),      # Wrong sign on second component  
        (a, b, -c),      # Wrong sign on third component
        (a, b, d),       # Using constant term instead of c
        (a + 1, b, c),   # Slightly modified component
    ]
    false_normal = random.choice(false_options)
    
    true_text = f"Véctơ \\(\\vec{{n}} = {format_point(true_normal)}\\) là một véctơ pháp tuyến của mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\)."
    false_text = f"Véctơ \\(\\vec{{n}} = {format_point(false_normal)}\\) là một véctơ pháp tuyến của mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\)."
    
    return {"true": true_text, "false": false_text}


def prop_normal_vector_from_direction_vectors() -> Dict[str, str]:
    """Find normal vector from two direction vectors using cross product"""
    # Generate two direction vectors
    u = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
    v = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
    
    # Ensure vectors are not collinear
    while are_collinear(u, v) or u == (0,0,0) or v == (0,0,0):
        u = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
        v = (random.randint(-2, 2), random.randint(-2, 2), random.randint(-2, 2))
    
    # True normal vector is cross product
    true_normal = cross(u, v)
    
    # Generate false normal vectors
    false_options = [
        cross(v, u),  # Reversed order (opposite direction)
        (true_normal[0] + 1, true_normal[1], true_normal[2]),  # Modified component
        (true_normal[0], true_normal[1] + 1, true_normal[2]),  # Modified component
        (u[0] + v[0], u[1] + v[1], u[2] + v[2]),  # Sum instead of cross product
    ]
    false_normal = random.choice(false_options)
    
    # Avoid identical vectors
    while false_normal == true_normal:
        false_normal = (true_normal[0] + random.choice([1, -1]), true_normal[1], true_normal[2])
    
    true_text = f"Véctơ \\(\\vec{{n}} = {format_point(true_normal)}\\) là một véctơ pháp tuyến của mặt phẳng có cặp véctơ chỉ phương \\(\\vec{{u}} = {format_point(u)}\\), \\(\\vec{{v}} = {format_point(v)}\\)."
    false_text = f"Véctơ \\(\\vec{{n}} = {format_point(false_normal)}\\) là một véctơ pháp tuyến của mặt phẳng có cặp véctơ chỉ phương \\(\\vec{{u}} = {format_point(u)}\\), \\(\\vec{{v}} = {format_point(v)}\\)."
    
    return {"true": true_text, "false": false_text}


# Group: Câu 3 (simple m parameter finding)

def prop_simple_m_parameter() -> Dict[str, str]:
    """Simple case: find m so that M(m;1;6) belongs to plane"""
    a = random.choice([v for v in range(*SMALL_COORD_RANGE) if v != 0])
    b = random.choice([v for v in range(*SMALL_COORD_RANGE) if v != 0])
    c = random.choice([v for v in range(*SMALL_COORD_RANGE) if v != 0])
    d = random.randint(-6, 6)
    
    # Fixed coordinates
    y = random.randint(-2, 3)
    z = random.randint(1, 6)
    
    # Calculate m so point is on plane: a*m + b*y + c*z + d = 0
    m_true = -(b*y + c*z + d) / a if a != 0 else 0
    
    # Format m value
    if abs(m_true - round(m_true)) < 1e-9:
        m_display = str(int(round(m_true)))
        m_false_display = str(int(round(m_true)) + random.choice([1, -1, 2]))
    else:
        frac = Fraction(-(b*y + c*z + d), a)
        m_display = f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
        m_false_display = str(random.choice([0, 1, -1]))
    
    true_text = f"Với \\(m = {m_display}\\), điểm \\(M(m;{y};{z})\\) thuộc mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\)."
    false_text = f"Với \\(m = {m_false_display}\\), điểm \\(M(m;{y};{z})\\) thuộc mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\)."
    
    return {"true": true_text, "false": false_text}


# Group: Ví dụ 5, Câu 6 (point projection distance)

def prop_point_projection_distance() -> Dict[str, str]:
    """Distance from point to plane equals projection distance - REFACTORED"""
    # Using new utility classes - notice the pattern is IDENTICAL to prop_point_plane_distance!
    plane = PlaneGenerator.random_plane(COORD_RANGE, CONST_TERM_RANGE)
    point = PointGenerator.random_point(SMALL_COORD_RANGE)
    numer, norm_sq = DistanceCalculator.point_to_plane(plane, point)
    
    true_text = f"Gọi H là hình chiếu của điểm A{format_point3d(point)} lên mặt phẳng \\((P): {format_plane_params(plane)}\\). Độ dài đoạn \\(AH\\) bằng \\({format_distance(numer, norm_sq)}\\)."
    
    # False: modify numerator
    delta = random.choice(DISTANCE_DELTA_OPTIONS)
    false_numer = numer + delta if numer > 0 else numer + 2
    false_text = f"Gọi H là hình chiếu của điểm A{format_point3d(point)} lên mặt phẳng \\((P): {format_plane_params(plane)}\\). Độ dài đoạn \\(AH\\) bằng \\({format_distance(false_numer, norm_sq)}\\)."
    
    return {"true": true_text, "false": false_text}


# Group: Ví dụ 6, Câu 9,10 (distance between parallel planes)

def prop_distance_between_parallel_planes() -> Dict[str, str]:
    """Distance between two parallel planes - REFACTORED"""
    # Using new utility classes - automatic parallel plane generation!
    plane1 = PlaneGenerator.random_plane(SMALL_COORD_RANGE, (-8, 9))
    plane2 = PlaneGenerator.parallel_plane(plane1, scale_factor=1)  # Same coefficients, different d
    
    # Distance calculation is now handled by utility
    numer, norm_sq = DistanceCalculator.between_parallel_planes(plane1, plane2)
    
    true_text = f"Khoảng cách giữa hai mặt phẳng \\((P): {format_plane_params(plane1)}\\) và \\((Q): {format_plane_params(plane2)}\\) bằng \\({format_distance(numer, norm_sq)}\\)."
    
    # False: modify numerator
    delta = random.choice([1, 2])
    false_numer = numer + delta
    false_text = f"Khoảng cách giữa hai mặt phẳng \\((P): {format_plane_params(plane1)}\\) và \\((Q): {format_plane_params(plane2)}\\) bằng \\({format_distance(false_numer, norm_sq)}\\)."
    
    return {"true": true_text, "false": false_text}


# Group: Ví dụ 7 (complex distance condition with parameter)

def prop_complex_distance_condition() -> Dict[str, str]:
    """Find m values for specific distance condition"""
    # Generate plane with parameter m in constant term
    a = random.choice([1, 2])
    b = random.choice([1, 2])  
    c = random.choice([1, 2])
    A = (1, 1, 1)  # Fixed point like in example
    target_distance = random.choice([1, 2])
    
    # Distance formula: |a*1 + b*1 + c*1 + m| / sqrt(a^2 + b^2 + c^2) = target_distance
    # |a + b + c + m| = target_distance * sqrt(a^2 + b^2 + c^2)
    
    sum_abc = a + b + c
    norm = math.sqrt(a*a + b*b + c*c)
    rhs = target_distance * norm
    
    # Two solutions: m1 = -sum_abc + rhs, m2 = -sum_abc - rhs
    m1 = -sum_abc + rhs
    m2 = -sum_abc - rhs
    
    # Calculate product and sum
    product = m1 * m2
    sum_m = m1 + m2
    result = product * abs(sum_m)
    
    true_text = f"Cho mặt phẳng \\((P): {a}x + {b}y + {c}z + m = 0\\) và điểm A{format_point(A)}. Có hai giá trị \\(m_1, m_2\\) thỏa mãn \\(d(A,(P)) = {target_distance}\\). Giá trị \\(m_1 m_2 |m_1 + m_2|\\) bằng \\({result:.0f}\\)."
    
    # False: modify the result
    false_result = result + random.choice([10, -10, 20, -20])
    false_text = f"Cho mặt phẳng \\((P): {a}x + {b}y + {c}z + m = 0\\) và điểm A{format_point(A)}. Có hai giá trị \\(m_1, m_2\\) thỏa mãn \\(d(A,(P)) = {target_distance}\\). Giá trị \\(m_1 m_2 |m_1 + m_2|\\) bằng \\({false_result:.0f}\\)."
    
    return {"true": true_text, "false": false_text}


# Group: Câu 11 (point on axis with distance condition)

def prop_point_on_axis_distance_condition() -> Dict[str, str]:
    """Point M(0,0,m) on Oz axis with specific distance to plane"""
    a = random.choice([v for v in range(-3, 4) if v != 0])
    b = random.choice([v for v in range(-3, 4) if v != 0])
    c = random.choice([v for v in range(-3, 4) if v != 0])
    d = random.randint(-6, 6)
    target_distance = random.choice([1, 2, 3])
    
    # Distance formula: |a*0 + b*0 + c*m + d| / sqrt(a^2 + b^2 + c^2) = target_distance
    # |c*m + d| = target_distance * sqrt(a^2 + b^2 + c^2)
    
    norm = math.sqrt(a*a + b*b + c*c)
    rhs = target_distance * norm
    
    # Two solutions: m1 = (-d + rhs)/c, m2 = (-d - rhs)/c
    if c != 0:
        m1 = (-d + rhs) / c
        m2 = (-d - rhs) / c
        sum_m = m1 + m2
        
        # Format sum
        if abs(sum_m - round(sum_m)) < 1e-9:
            sum_display = str(int(round(sum_m)))
        else:
            sum_display = f"{sum_m:.1f}"
    else:
        sum_display = "0"
    
    true_text = f"Cho điểm \\(M(0;0;m) \\in Oz\\) và mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) thỏa mãn \\(d(M,(P)) = {target_distance}\\). Tổng các giá trị \\(m\\) bằng \\({sum_display}\\)."
    
    # False: modify sum (ensure different from true sum)
    false_options = [0, 1, -1, 2, -2, 3, -3] if sum_display != "0" else [1, 2, -1, -2]
    # Remove true value from options to ensure false statement is actually false
    if sum_display.lstrip('-').isdigit():
        true_value = int(sum_display)
        false_options = [x for x in false_options if x != true_value]
    
    # Ensure we have options left
    if not false_options:
        false_options = [99]  # Fallback extreme value
        
    false_sum = random.choice(false_options)
    false_text = f"Cho điểm \\(M(0;0;m) \\in Oz\\) và mặt phẳng \\((P): {format_plane_equation(a,b,c,d)}\\) thỏa mãn \\(d(M,(P)) = {target_distance}\\). Tổng các giá trị \\(m\\) bằng \\({false_sum}\\)."
    
    return {"true": true_text, "false": false_text}


# Group: Câu 15 (parallel condition with parameter)

def prop_parallel_condition_with_parameter() -> Dict[str, str]:
    """Find parameter m for parallel planes condition with correct logic"""
    # First plane coefficients - simple values
    a1, b1, c1 = random.choice([1, 2]), random.choice([1, 2]), random.choice([1, -1])
    d1 = random.randint(-3, 3)
    
    # Second plane will have parameter m as coefficient of z
    # Format: a2*x + b2*y + m*z + d2 = 0
    k = random.choice([2, 3, -2])  # scaling factor for parallel condition
    a2, b2 = k * a1, k * b1
    d2 = random.randint(-3, 3)
    
    # For parallel: m = k * c1 (so normal vectors are proportional)
    m_true = k * c1
    
    # Ensure planes are not identical by making sure d2 != k * d1
    while d2 == k * d1:
        d2 = random.randint(-3, 3)
    
    # Create equation strings manually for better control
    plane1_eq = format_plane_equation(a1, b1, c1, d1)
    
    # Second plane equation with parameter m
    parts = []
    if a2 == 1:
        parts.append("x")
    elif a2 == -1:
        parts.append("-x")
    elif a2 != 0:
        parts.append(f"{a2}x")
    
    if b2 != 0:
        if parts:
            if b2 == 1:
                parts.append("+ y")
            elif b2 == -1:
                parts.append("- y")
            elif b2 > 0:
                parts.append(f"+ {b2}y")
            else:
                parts.append(f"- {abs(b2)}y")
        else:
            if b2 == 1:
                parts.append("y")
            elif b2 == -1:
                parts.append("-y")
            else:
                parts.append(f"{b2}y")
    
    # Add parameter m for z coefficient (always show as + mz, user will substitute)
    if parts:
        parts.append("+ mz")
    else:
        parts.append("mz")
    
    # Add constant term
    if d2 > 0:
        parts.append(f"+ {d2}")
    elif d2 < 0:
        parts.append(f"- {abs(d2)}")
    
    plane2_eq = " ".join(parts) + " = 0"
    
    true_text = f"Với \\(m = {m_true}\\), hai mặt phẳng \\((P): {plane1_eq}\\) và \\((Q): {plane2_eq}\\) song song."
    
    # False value that breaks parallelism
    m_false = m_true + random.choice([1, -1, 2, -2])
    false_text = f"Với \\(m = {m_false}\\), hai mặt phẳng \\((P): {plane1_eq}\\) và \\((Q): {plane2_eq}\\) song song."
    
    return {"true": true_text, "false": false_text}


# Group: Ví dụ 9 (two parameter parallel condition)

def prop_two_parameter_parallel_condition() -> Dict[str, str]:
    """Find two parameters m,n for parallel planes condition - Ví dụ 9"""
    # Generate coefficients for the planes like in the example
    # (P): a1*x + b1*y + m*z + d1 = 0
    # (Q): a2*x + n*y + c2*z + d2 = 0
    
    # Choose simple coefficients to get nice results
    a1, b1 = random.choice([1, 2]), random.choice([1, 2])
    a2, c2 = random.choice([1, 2]), random.choice([1, 2])
    d1, d2 = random.randint(-5, 5), random.randint(-5, 5)
    
    # For parallel planes, normal vectors must be proportional
    # (a1, b1, m) = k * (a2, n, c2)
    # This gives us: a1 = k*a2, b1 = k*n, m = k*c2
    
    # Calculate scaling factor k
    k = a1 / a2  # k = a1/a2
    
    # Calculate n and m
    n_true = b1 / k  # n = b1/k
    m_true = k * c2  # m = k*c2
    
    # Format the sum
    sum_mn = m_true + n_true
    
    # Format as decimal with appropriate precision
    if abs(sum_mn - round(sum_mn, 2)) < 1e-10:
        sum_display = f"{sum_mn:.2f}".rstrip('0').rstrip('.')
    else:
        sum_display = f"{sum_mn:.2f}"
    
    # Ensure d1 != k*d2 to avoid identical planes
    while abs(d1 - k*d2) < 1e-9:
        d1 = random.randint(-5, 5)
    
    # Create plane equations manually for better formatting
    # First plane
    plane1_parts = []
    if a1 == 1:
        plane1_parts.append("x")
    elif a1 == -1:
        plane1_parts.append("-x")
    else:
        plane1_parts.append(f"{a1}x")
    
    if b1 > 0:
        plane1_parts.append(f"+ {b1}y" if b1 != 1 else "+ y")
    elif b1 < 0:
        plane1_parts.append(f"- {abs(b1)}y" if abs(b1) != 1 else "- y")
    
    plane1_parts.append("+ mz")
    
    if d1 > 0:
        plane1_parts.append(f"+ {d1}")
    elif d1 < 0:
        plane1_parts.append(f"- {abs(d1)}")
    
    plane1_eq = " ".join(plane1_parts) + " = 0"
    
    # Second plane
    plane2_parts = []
    if a2 == 1:
        plane2_parts.append("x")
    elif a2 == -1:
        plane2_parts.append("-x")
    else:
        plane2_parts.append(f"{a2}x")
    
    plane2_parts.append("+ ny")
    
    if c2 > 0:
        plane2_parts.append(f"+ {c2}z" if c2 != 1 else "+ z")
    elif c2 < 0:
        plane2_parts.append(f"- {abs(c2)}z" if abs(c2) != 1 else "- z")
    
    if d2 > 0:
        plane2_parts.append(f"+ {d2}")
    elif d2 < 0:
        plane2_parts.append(f"- {abs(d2)}")
    
    plane2_eq = " ".join(plane2_parts) + " = 0"
    
    true_text = f"Cho hai mặt phẳng \\((P): {plane1_eq}\\) và \\((Q): {plane2_eq}\\) song song nhau. Tổng \\(m + n\\) bằng \\({sum_display}\\)."
    
    # False: modify the sum slightly
    false_sum_options = [
        round(sum_mn + 0.25, 2),
        round(sum_mn - 0.25, 2), 
        round(sum_mn + 0.5, 2),
        round(sum_mn - 0.5, 2)
    ]
    false_sum = random.choice(false_sum_options)
    false_sum_display = f"{false_sum:.2f}".rstrip('0').rstrip('.')
    
    false_text = f"Cho hai mặt phẳng \\((P): {plane1_eq}\\) và \\((Q): {plane2_eq}\\) song song nhau. Tổng \\(m + n\\) bằng \\({false_sum_display}\\)."
    
    return {"true": true_text, "false": false_text}


# Registry of proposition groups for Part A
PART_A_GROUPS: List[List] = [
    # Original groups
    # Ví dụ 4,5 + Câu 7,8 (distance and reflection)
    [prop_point_plane_distance, prop_reflection_segment_length],
    # Ví dụ 3 - Câu 4 (point membership and parametric)
    [prop_point_on_plane_membership, prop_point_with_m_on_plane],
    # Câu 12 (equal distances)
    [prop_equal_distance_to_plane_and_point_on_Oz],
    # Ví dụ 8 - Câu 13,14 (angles)
    [prop_angle_between_planes, prop_angle_plane_with_coordinate_plane],
    # Ví dụ 9 - Câu 16 - Câu 17 (parallel, intersect, perpendicular)
    [prop_planes_parallel_simple, prop_planes_intersect_condition_m, prop_planes_perpendicular_condition_m],
    
    # New groups for missing problem types
    # Ví dụ 1,2 + Câu 1,2 (normal vectors)
    [prop_normal_vector_from_equation, prop_normal_vector_from_direction_vectors],
    # Câu 3 (simple parameter finding)
    [prop_simple_m_parameter],
    # Ví dụ 5, Câu 6 (point projection)
    [prop_point_projection_distance],
    # Ví dụ 6, Câu 9,10 (distance between parallel planes)
    [prop_distance_between_parallel_planes],
    # Ví dụ 7 (complex distance condition)
    [prop_complex_distance_condition],
    # Câu 11 (point on axis with distance condition)
    [prop_point_on_axis_distance_condition],
    # Câu 15 (parallel condition with parameter)
    [prop_parallel_condition_with_parameter],
    # Ví dụ 9 (two parameter parallel condition)
    [prop_two_parameter_parallel_condition],
]


def generate_question(question_number: int) -> str:
    """Generate a question with 4 propositions from different groups - FIXED LOGIC"""
    # Chọn 1 nhóm mapping trong phần A, lấy 1 mệnh đề từ nhóm đó
    selected_group = random.choice(PART_A_GROUPS)
    primary_gen = random.choice(selected_group)
    
    # Tạo pool còn lại: tất cả generator của phần A trừ nhóm đã chọn (optimized)
    all_gens = [g for grp in PART_A_GROUPS for g in grp]
    remaining_pool = [g for g in all_gens if g not in selected_group]
    
    # Lấy 3 generator khác nhau từ remaining_pool (nếu thiếu thì cho phép lặp)
    if len(remaining_pool) >= 3:
        other_gens = random.sample(remaining_pool, 3)
    else:
        other_gens = [random.choice(remaining_pool) for _ in range(3)] if remaining_pool else [primary_gen]*3
    
    selected_gens = [primary_gen] + other_gens
    
    # Sinh 4 mệnh đề
    propositions: List[Dict[str, str]] = [gen() for gen in selected_gens]
    
    # FIX: Randomly decide which propositions should be mathematically TRUE
    # This ensures mathematical truth = marking consistency
    num_true = random.randint(1, 4)
    true_indices = set(random.sample(range(4), num_true))
    option_labels = ['a', 'b', 'c', 'd']
    content = f"Câu {question_number}: Chọn các mệnh đề đúng.\n\n"
    
    # FIXED LOGIC: Ensure mathematical truth matches marking
    for i in range(4):
        if i in true_indices:
            # This should be a TRUE mathematical statement
            text = propositions[i]['true']
            marker = '*'  # Mark as correct
        else:
            # This should be a FALSE mathematical statement
            text = propositions[i]['false']
            marker = ''   # Don't mark
            
        content += f"{marker}{option_labels[i]}) {text}\n\n"
    
    return content


def create_latex_document(questions: List[str], title: str = "Các bài toán về các thông số liên quan - Đúng/Sai") -> str:
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
    questions = [generate_question(i+1) for i in range(num_questions)]
    tex = create_latex_document(questions)
    out = "plane_true_false_part_A.tex"
    with open(out, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Generated {out} with {len(questions)} question(s). Compile with XeLaTeX.")


if __name__ == "__main__":
    main()
