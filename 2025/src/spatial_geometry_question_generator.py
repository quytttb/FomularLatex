"""
Giao điểm đường thẳng với mặt phẳng trong không gian 3D
"""

import random
import math
import sys
import logging
from abc import ABC, abstractmethod
from fractions import Fraction
from typing import List, Dict, Any, Union, Type

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ===================================================================================
# ===== PHẦN 1: CÁC HÀM TIỆN ÍCH LATEX (CẢI TIẾN) =====
# ===================================================================================

def format_fraction_latex(num, denom):
    """Format phân số thành LaTeX - cải tiến từ thuc_te_hinh_hoc.py"""
    if denom == 0:
        return "undefined"

    frac = Fraction(num, denom)
    if frac.denominator == 1:
        return str(frac.numerator)
    elif frac.numerator == 0:
        return "0"
    else:
        return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"


def format_coefficient(coeff, is_first=False, var='x', power=1):
    """Format hệ số với dấu và biến - từ thuc_te_hinh_hoc.py"""
    if coeff == 0:
        return ""

    # Handle Fraction coefficients
    if isinstance(coeff, Fraction):
        num, denom = coeff.numerator, coeff.denominator
    else:
        num, denom = int(coeff), 1

    # Format the coefficient part
    if denom == 1:
        coeff_str = str(abs(num)) if abs(num) != 1 or power == 0 else ""
    else:
        coeff_str = f"\\frac{{{abs(num)}}}{{{denom}}}"

    # Handle variable and power
    if power == 0:
        var_str = coeff_str if coeff_str else "1"
    elif power == 1:
        var_str = f"{coeff_str}{var}" if coeff_str else var
    else:
        var_str = f"{coeff_str}{var}^{{{power}}}" if coeff_str else f"{var}^{{{power}}}"

    # Handle signs
    if is_first:
        if num < 0:
            return f"-{var_str}"
        else:
            return var_str
    else:
        if num < 0:
            return f" - {var_str}"
        else:
            return f" + {var_str}"


def format_polynomial(coeffs, var='x'):
    """Format đa thức thành LaTeX - từ thuc_te_hinh_hoc.py"""
    if not coeffs or all(c == 0 for c in coeffs):
        return "0"

    terms = []
    degree = len(coeffs) - 1

    for i, coeff in enumerate(coeffs):
        if coeff == 0:
            continue

        power = degree - i
        term = format_coefficient(coeff, len(terms) == 0, var, power)
        if term:
            terms.append(term)

    if not terms:
        return "0"

    return "".join(terms)


def format_number_clean(value, precision=2):
    """Format số sạch - cải tiến cho LaTeX Việt Nam"""
    try:
        fval = float(value)
        if abs(fval - round(fval)) < 1e-10:
            return str(int(round(fval)))
        else:
            formatted = f"{fval:.{precision}f}"
            while formatted.endswith('0') and '.' in formatted:
                formatted = formatted[:-1]
            if formatted.endswith('.'):
                formatted = formatted[:-1]
            # Chỉ thay dấu chấm bằng dấu phẩy khi vẫn còn dấu chấm
            if '.' in formatted:
                formatted = formatted.replace('.', ',')
            return formatted
    except Exception:
        return str(value)


def format_coord_solution(coord):
    """Format tọa độ chuẩn Việt Nam cho lời giải"""
    if isinstance(coord, Fraction):
        if coord.denominator == 1:
            return str(coord.numerator)
        else:
            return f"\\dfrac{{{coord.numerator}}}{{{coord.denominator}}}"

    # Sử dụng lại format_number_clean để tránh trùng lặp
    return format_number_clean(coord, precision=10).replace('\\frac', '\\dfrac')


def format_scientific(num: float, precision: int = 3) -> str:
    """Format số khoa học - từ thuc_te_hinh_hoc.py"""
    if abs(num) < 1e-10:
        return "0"

    exponent = int(math.floor(math.log10(abs(num))))
    mantissa = num / (10 ** exponent)

    if exponent == 0:
        return f"{mantissa:.{precision}f}".rstrip('0').rstrip('.')
    else:
        return f"{mantissa:.{precision}f} \\times 10^{{{exponent}}}"


def format_sqrt(number: Union[int, float]) -> str:
    """Format căn bậc hai - từ thuc_te_hinh_hoc.py"""
    if number == int(number) and int(number) >= 0:
        sqrt_val = math.sqrt(number)
        if sqrt_val == int(sqrt_val):
            return f"{int(sqrt_val)}"
        else:
            return f"\\sqrt{{{int(number)}}}"
    else:
        return f"\\sqrt{{{number}}}"


def format_dimension(value: float, unit: str = "mét") -> str:
    """Format kích thước - từ thuc_te_hinh_hoc.py"""
    if abs(value - round(value)) < 1e-10:
        return f"{int(round(value))} {unit}"
    else:
        formatted = f"{value:.1f}"
        if formatted.endswith('.0'):
            formatted = formatted[:-2]
        return f"{formatted} {unit}"


def strip_latex_inline_math(ans: str) -> str:
    """Loại bỏ \( ... \) hoặc $...$ khỏi đáp án để tránh lồng môi trường toán học."""
    if ans.startswith("\\(") and ans.endswith("\\)"):
        return ans[2:-2].strip()
    if ans.startswith("$") and ans.endswith("$"):
        return ans[1:-1].strip()
    return ans


# ===== THÊM FORMAT LATEX MỚI TẠI ĐÂY =====
# Ví dụ thêm hàm format mới:
# def format_your_new_function(value):
#     """Mô tả chức năng"""
#     return formatted_value


# ===================================================================================
# ===== PHẦN 2: CÁC HÌNH VẼ TIKZ (MỞ RỘNG) =====
# ===================================================================================

class TikZFigureLibrary:
    """Thư viện hình vẽ TikZ"""

    @staticmethod
    def get_bird_fish_3d_coordinate_figure():
        """Hình vẽ chim bói cá lặn xuống bắt cá với hệ trục tọa độ 3D - từ sample_bai1.tex"""
        return """
\\begin{tikzpicture}[line join=round, line cap=round,scale=1,transform shape, >=stealth]
\\definecolor{columbiablue}{rgb}{0.61, 0.87, 1.0}%màu nước
\\definecolor{arsenic}{rgb}{0.23, 0.27, 0.29}%màu mỏ
\\definecolor{antiquewhite}{rgb}{0.98, 0.92, 0.84}%màu trắng
\\definecolor{cadmiumorange}{rgb}{0.93, 0.53, 0.18}%lông cam
\\definecolor{coolblack}{rgb}{0.0, 0.18, 0.39}%cánh đậm
\\definecolor{brandeisblue}{rgb}{0.0, 0.44, 1.0}%màu xanh đầu
\\definecolor{darkcoral}{rgb}{0.8, 0.36, 0.27}%màu chân
\\definecolor{amber}{rgb}{1.0, 0.49, 0.0}%màu vẽ cá

\\tikzset{san/.pic={ 
    \\path
    (-1.3,-1.5) coordinate (O)
    ($(O)+(-142:2)$) coordinate (y)
    ($(O)+(0:4.7)$) coordinate (x)
    ($(O)+(90:3)$) coordinate (z)
    ($(x)+(y)-(O)$) coordinate (t)
    
    (-.8,-2.2)coordinate (A)
    (1.6,0.8) coordinate (C)
    ($(A)!.13!(C)$) coordinate (B)
    ;
    \\fill[columbiablue] (O)--(x)--(t)--(y)--cycle;
    
    \\foreach\\p/\\g/\\t in {x/-90/y, y/-90/x, z/0/z}
    {
        \\node at (\\p) [shift=(\\g:2mm)] {\\tiny $\\t$};
    }
    
    \\foreach\\p/\\g in {A/180,B/0,C/-50,O/-90}
    {
        \\draw[fill=black](\\p) circle (.5pt) +(\\g:2mm)node{\\tiny $\\p$};
    }
    
    \\draw[->] (O)--(x) ;
    \\draw[->] (O)--(y);
    \\draw[->] (O)--(z);
    \\draw[dashed] (A)--(B);
    \\draw (B)--(C);
    %---------nước
    \\draw (-1,-1.7)
    ..controls +(-120:.5) and +(-160:.5) ..(0,-2)
    (-.9,-1.9)
    ..controls +(-70:.2) and +(-160:.2) ..(-.2,-1.9)
    (-.95,-1.8)
    ..controls +(70:.5) and +(30:.5) ..(0,-1.9)
    (.1,-1.6)
    ..controls +(-20:.2) and +(30:.2) ..(.2,-1.9)
    (-.7,-1.75)
    ..controls +(-170:.2) and +(-160:.3) ..(-.5,-1.9)
    ;
}}

\\tikzset{chim_boi_ca/.pic={
    %==============cánh trái
    \\draw[fill=coolblack]
    (-.55,1.4)
    ..controls +(110:.7) and +(100:.3) ..(-.9,1.8)
    ..controls +(135:.3) and +(120:.3) ..(-1.2,1.8)
    ..controls +(145:.25) and +(110:.25) ..(-1.45,1.7)
    ..controls +(165:.15) and +(85:.15) ..(-1.75,1.63)
    ..controls +(-165:.1) and +(85:.1) ..(-1.9,1.5)
    ..controls +(165:.15) and +(85:.1) ..(-2.1,1.3)
    ..controls +(-165:.1) and +(95:.1) ..(-2.2,1.1)
    ..controls +(-160:.1) and +(95:.1) ..(-2.35,1)--(-1,1.1)
    ;
    %======--------------------
    %Tô lông đầu
    \\def\\L{
        (2,.84)
        ..controls +(170:.2) and +(25:.3) ..(1,.65)
        ..controls +(-145:.5) and +(40:.6) ..(.3,.4)
        ..controls +(-140:.3) and +(-60:.3) ..(0,.6)
        ..controls +(120:.3) and +(-50:.7) ..(-1,1.1)
        ..controls +(90:.3) and +(170:.3) ..(-.55,1.4)%1
        ..controls +(-40:.2) and +(140:.1) ..(-.25,1.2)
        ..controls +(-70:.2) and +(-160:.35) ..(.15,.85)
        ..controls +(75:.7) and +(135:.8) ..(1.9,1.3)--(2.1,1)--cycle
        ;
    }
    \\fill[brandeisblue] \\L;
    %==============================
    \\draw[fill=antiquewhite] (2,1.05)
    ..controls +(165:.2) and +(-35:.2)..(1.7,1.15)
    ..controls +(145:.2) and +(65:.2)..(1.2,1.15)
    ..controls +(-60:.1) and +(165:.1)..(1.4,1)
    ..controls +(-15:.2) and +(-145:.3)..cycle
    ;
    \\draw[fill=arsenic] (1.6,1.2)
    ..controls +(155:.18) and +(55:.15)..(1.23,1.17)
    ..controls +(-75:.2) and +(-95:.2)..cycle
    ;
    \\fill (1.44,1.14) circle(1mm);
    
    \\fill[cadmiumorange] (2,1.05)
    ..controls +(165:.2) and +(-35:.2)..(1.7,1.15)
    ..controls +(145:.2) and +(95:.3)..cycle
    ;
    \\fill[cadmiumorange] (2,.84)
    ..controls +(150:.2) and +(-25:.1) ..(1.7,1)
    ..controls +(155:.2) and +(-50:.3) ..(1.2,1.08)
    ..controls +(130:.2) and +(50:.2) ..(.75,1)
    ..controls +(-130:.2) and +(-10:.2) ..(.21,1)
    ..controls +(-120:.1) and +(70:.1) ..(.15,.84)
    ..controls +(-20:.3) and +(-150:.3) ..(.8,.85)
    ..controls +(-10:.3) and +(150:.5) ..(1.7,.85)
    ..controls +(-10:.1) and +(150:.1) ..cycle
    ;
    %==================
    %viền đen đầu
    \\def\\X{
        (0,.6)
        ..controls +(120:.3) and +(-50:.7) ..(-1,1.1)
        
        (-.55,1.4)%1
        ..controls +(-40:.2) and +(140:.1) ..(-.25,1.2)
        ..controls +(-70:.2) and +(-160:.35) ..(.15,.85)
        ..controls +(75:.7) and +(135:.8) ..(1.9,1.3)
        ;
    }
    \\draw[black]\\X;
    %====================
    %Tô mỏ
    \\def\\N{
        (1.9,1.3)
        ..controls +(-35:.4) and +(140:.3) ..(3.4,.78)
        ..controls +(-175:.2) and +(-10:.3) ..(2,.84)
        ..controls +(150:.2) and +(-25:.1) ..(1.7,1)
        ..controls +(20:.2) and +(175:.1) ..(2,1.05)
        ..controls +(-35:.2) and +(155:.1) ..cycle
        ;
    }
    \\fill[arsenic] \\N;
    %Mỏ
    \\def\\M{
        (1.9,1.3)
        ..controls +(-35:.4) and +(140:.3) ..(3.4,.78)
        ..controls +(-175:.2) and +(-10:.3) ..(2,.84)
        ..controls +(170:.2) and +(25:.3) ..(1,.65)
        ;
    }
    \\draw[black]\\M;
    %==============================
    
    %================Cánh phải
    \\draw[fill=coolblack]
    (-.6,-.3)%3
    ..controls +(-130:.5) and +(-10:.2) ..(-1,-.95)
    ..controls +(170:.1) and +(-10:.15) ..(-1.2,-1.02)
    ..controls +(170:.1) and +(-40:.15) ..(-1.45,-.95)
    ..controls +(160:.1) and +(-80:.15) ..(-1.6,-.8)
    ..controls +(140:.1) and +(-70:.15) ..(-1.75,-.65)
    ..controls +(140:.1) and +(-70:.15) ..(-1.9,-.5)
    ..controls +(160:.1) and +(-70:.15) ..(-2.05,-.35)
    ..controls +(150:.1) and +(-70:.15) ..(-2.25,-.2)
    ..controls +(-160:.1) and +(-20:.15) ..(-2.5,-.18)
    ..controls +(160:.1) and +(-30:.15) ..(-2.75,-.16)
    ..controls +(160:.1) and +(-60:.15) ..(-2.95,-.05)
    ..controls +(160:.1) and +(-80:.15) ..(-3.2,.05)
    ..controls +(160:.1) and +(-90:.15) ..(-3.35,.15)
    ..controls +(160:.1) and +(-95:.15) ..(-3.55,.25)
    ..controls +(-160:.2) and +(-145:.2) ..(-3.7,.35)
    ..controls +(-160:.2) and +(-160:.4) ..(-3.7,.53)
    ..controls +(-160:.2) and +(-160:.3) ..(-3.85,.65)
    ..controls +(160:.5) and +(-170:.3) ..(-2.6,.95)
    ..controls +(0:.5) and +(120:.3) ..(-.6,-.3)%3
    ;
    %===================
    \\fill[brandeisblue]
    (-.8,-1.1)%lông đuôi xanh
    ..controls +(-80:.2) and +(140:.2) ..(-.5,-1.5)
    ..controls +(-40:.2) and +(140:.4) ..(-.3,-2.5)
    ..controls +(135:.7) and +(-85:.6) ..cycle
    ;
    \\draw (-.3,-2.5)
    ..controls +(135:.7) and +(-85:.6) ..(-.8,-1.1)%lông đuôi xanh
    ;
    %=============đuôi
    \\draw[fill=brandeisblue] (-.45,-2.3)
    ..controls +(-95:.2) and +(95:.2) ..(-.4,-2.8)
    --(-.32,-2.8)--(-.25,-2.2)
    (-.25,-2.2)--(-.32,-2.78)--(-.27,-2.78)--(-.16,-2.2)
    ;
    %================
    %Tô lông cam
    \\def\\C{
        (2,.84)
        ..controls +(170:.2) and +(25:.3) ..(1,.65)
        ..controls +(-145:.5) and +(40:.6) ..(.3,.4)
        ..controls +(-140:.3) and +(-60:.3) ..(0,.6)
        ..controls +(120:.3) and +(-50:.7) ..(-1,1.1)%2
        ..controls +(130:.2) and +(20:.3) ..(-2.6,.95)
        ..controls +(-160:.2) and +(145:.3) ..(-1.6,.5)
        ..controls +(-35:.2) and +(145:.3) ..(-1,-.5)
        ..controls +(-35:.2) and +(-145:.2) ..(-.6,-.3)%3
        ..controls +(-135:.2) and +(100:.2) ..(-.8,-1.1)%lông đuôi xanh
        ..controls +(-80:.2) and +(140:.2) ..(-.5,-1.5)
        ..controls +(-40:.2) and +(140:.4) ..(-.3,-2.5)%đuôi dưới
        ..controls +(40:.4) and +(-150:.5) ..(.5,-1.1)%chân
        ..controls +(-20:.2) and +(160:.2) ..(.8,-1.15)
        ..controls +(150:.1) and +(-70:.1) ..(.65,-.9)
        ..controls +(110:.2) and +(-95:.8) ..(1.26,.6)
        ..controls +(75:.1) and +(-160:.2) ..cycle
        ;
    }
    
    \\fill[cadmiumorange] \\C;
    \\draw[black]\\C;
    
    \\draw[black] (-1,1.1)
    ..controls +(130:.2) and +(20:.3) ..(-2.6,.95)
    
    (-.6,-.3)%3
    ..controls +(-135:.2) and +(100:.2) ..(-.8,-1.1)
    ;
    
    %======================chân
    \\draw[fill=darkcoral]
    (.5,-1.1)
    ..controls +(-20:.1) and +(170:.1) ..(1.5,-1.1)%chân
    ..controls +(-10:.1) and +(-10:.3) ..(1.2,-1.2)
    ;
    %móng 2
    \\draw (1.47,-1.15)%chân
    ..controls +(-10:.1) and +(120:.1) ..(1.63,-1.25)
    ;
    %---------------------
    \\draw[fill=darkcoral]
    (.7,-1.15)
    ..controls +(40:.1) and +(170:.1) ..(1.3,-1.08)%chân
    ..controls +(-10:.1) and +(-10:.1) ..(1.2,-1.2)
    ..controls +(170:.1) and +(30:.1) ..(1,-1.2)
    ;
    %móng 2
    \\draw (1.27,-1.15)%chân
    ..controls +(-10:.1) and +(120:.1) ..(1.43,-1.25)
    ;
    %------------------------
    \\draw[fill=darkcoral]
    (.25,-1.1)
    ..controls +(-20:.2) and +(-170:.1) ..(.5,-1.1)%chân
    ..controls +(-20:.2) and +(160:.2) ..(.8,-1.15)
    ..controls +(-20:.2) and +(160:.2) ..(1.1,-1.2)%móng 1
    ..controls +(-20:.1) and +(-50:.1) ..(1.03,-1.25)
    ..controls +(130:.05) and +(-10:.05) ..(.8,-1.26)
    ..controls +(170:.05) and +(10:.05) ..(.5,-1.28)
    ..controls +(-150:.1) and +(-160:.15) ..(.3,-1.25)
    ..controls +(160:.1) and +(-80:.1) ..(.1,-1.15)
    ;
    %móng 1
    \\draw (1.1,-1.25)%móng 1
    ..controls +(-20:.1) and +(95:.1) ..(1.2,-1.35)
    ;
}}

%===========Vẽ cá
\\tikzset{ca/.pic={
    %vây
    \\def\\V{
        (-.35,.74)
        ..controls +(120:.12) and +(40:.22) ..(-.7,.72)--cycle
        (-.7,.32)
        ..controls +(-170:.1) and +(10:.1) ..(-.95,.3)
        ..controls +(60:.1) and +(-140:.1) ..(-.85,.45)--(-.65,.4)--cycle
        (-.3,.32)
        ..controls +(-170:.1) and +(10:.1) ..(-.45,.1)
        ..controls +(-40:.1) and +(-110:.1) ..(-.1,.37)--cycle
        ;
    }
    \\fill[amber] \\V;
    \\draw\\V;
    
    %-----------------
    \\def\\C{
        (-1.25,.83)
        ..controls +(-45:.2) and +(130:.2) ..(-1,.58)
        ..controls +(35:.2) and +(130:.52) ..(.05,.52)
        ..controls +(-90:.1) and +(-110:.1) ..(.05,.52)--(.04,.44)
        ..controls +(-150:.5) and +(-40:.2) ..(-1,.53)
        ..controls +(-140:.1) and +(40:.1) ..(-1.3,.42)
        ..controls +(60:.2) and +(-55:.2) ..cycle
        ;
    }
    
    \\fill[amber] \\C;
    \\draw\\C;
    %-----------------
    \\def\\Cn{
        (-1,.57)
        ..controls +(35:.1) and +(130:.4) ..(.01,.52)
        ..controls +(-140:.4) and +(-40:.2) ..cycle
        ;
    }
    \\fill[amber!70] \\Cn;
    \\draw (-.3,.7)
    ..controls +(-120:.1) and +(120:.2) ..(-.3,.34);
    
    \\draw[fill=white] (-.22,.55) circle (.08);
    \\draw[fill=black] (-.22,.55) circle (.048);
    
}}

\\path
(0,0)pic[scale=1]{san}
;

\\path (-1,-2.5)pic[xscale=-.35,yscale=.35]{ca}
(1.6,1)pic[xscale=-.15,yscale=.15,rotate=-40]{chim_boi_ca}; 
\\end{tikzpicture}
"""

    @staticmethod
    def get_airplane_3d_coordinate_figure():
        """Hình vẽ máy bay trong không gian 3D với hệ trục tọa độ - từ sample_bai1.tex"""
        return """
\\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\\footnotesize,scale=1]

\\path 
(0,0) coordinate (O)
(-2,-2) coordinate (A')
(4,0) coordinate (B')
(0,3) coordinate (C')
($(O)!0.3!(C')$) coordinate (C1)
($(O)!0.3!(B')$) coordinate (B1)
($(O)!0.3!(A')$) coordinate (A1)
($(O)!0.8!(C')$) coordinate (C)
($(O)!0.8!(B')$) coordinate (B)
($(O)!0.8!(A')$) coordinate (A)
;

\\foreach \\diem/\\t/\\r in{A'/x/-90,
    B'/y/60,
    C'/z/60,
    A1/\\overrightarrow{i}/-60,
    B1/\\overrightarrow{j}/-90,
    C1/\\overrightarrow{k}/180}	
\\draw[->,line width=1pt] 	(O)--(\\diem)node[shift={(\\r:4mm)},scale=0.8]{$\\t$};

\\draw[dashed] 
(A)--($(A)+(B)-(O)$) coordinate (H) --(B)
(C)--($(C)+(H)-(O)$)coordinate (M) node[above=0.5cm]{$M$}--(H)
(H)--(O)--(M);

\\draw (M) node[scale=0.7]{	
    \\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\\footnotesize,scale=0.15,rotate=30]
        %%%%%%%%%%%%%%	
        \\draw[fill=black] 
        (0,0) .. controls +(20:1) and +(90:1) .. (8,0)
        ..controls +(-90:1) and +(-20:1) .. (0,0)--cycle
        ;
        %%%%%%%%%%%%%%	
        \\draw [fill=black]
        (4,0)--(3,4)--(3.5,4)--(6,0)--cycle
        (4,0)--(3,-4)--(3.5,-4)--(6,0)--cycle
        (0.5,0)--(0,1)--(0.5,1)--(1.3,0)--cycle
        (0.5,0)--(0,-1)--(0.5,-1)--(1.3,0)--cycle
        ;
        %%%%%%%%%%%%%
    \\end{tikzpicture}	
};
\\draw pic[draw,angle radius=4mm] {right angle = O--A--H}; 
\\draw pic[draw,angle radius=4mm] {right angle = O--B--H}; 
\\draw pic[draw,angle radius=4mm] {right angle = O--C--M}; 
\\draw[cyan,line width=2pt,->] (O)--(M);	

\\foreach \\p/\\r in {A/160,B/90,C/180,H/-45}
\\fill (\\p) circle (1.2pt) node[shift={(\\r:3mm)},scale=0.8]{$\\p$};
\\end{tikzpicture}
"""

    @staticmethod
    def get_general_3d_coordinate_figure():
        """Hình vẽ hệ trục tọa độ 3D mở rộng với mặt nước và vật thể - bổ sung cho những context khác của dạng toán Giao điểm đường thẳng với mặt phẳng"""
        return """
\\begin{tikzpicture}[line join=round, line cap=round,scale=1,transform shape, >=stealth]
\\definecolor{columbiablue}{rgb}{0.61, 0.87, 1.0}%màu nước
\\definecolor{arsenic}{rgb}{0.23, 0.27, 0.29}%màu mỏ
\\definecolor{antiquewhite}{rgb}{0.98, 0.92, 0.84}%màu trắng
\\definecolor{cadmiumorange}{rgb}{0.93, 0.53, 0.18}%lông cam
\\definecolor{coolblack}{rgb}{0.0, 0.18, 0.39}%cánh đậm
\\definecolor{brandeisblue}{rgb}{0.0, 0.44, 1.0}%màu xanh đầu
\\definecolor{darkcoral}{rgb}{0.8, 0.36, 0.27}%màu chân
\\definecolor{amber}{rgb}{1.0, 0.49, 0.0}%màu vẽ cá

\\tikzset{san/.pic={ 
    \\path
    (-1.3,-1.5) coordinate (O)
    ($(O)+(-142:2)$) coordinate (y)
    ($(O)+(0:4.7)$) coordinate (x)
    ($(O)+(90:3)$) coordinate (z)
    ($(x)+(y)-(O)$) coordinate (t)
    
    (-.8,-2.2)coordinate (A)
    (1.6,0.8) coordinate (C)
    ($(A)!.13!(C)$) coordinate (B)
    ;
    \\fill[columbiablue] (O)--(x)--(t)--(y)--cycle;
    
    \\foreach\\p/\\g/\\t in {x/-90/y, y/-90/x, z/0/z}
    {
        \\node at (\\p) [shift=(\\g:2mm)] {\\tiny $\\t$};
    }
    
    \\foreach\\p/\\g in {A/180,B/0,C/-50,O/-90}
    {
        \\draw[fill=black](\\p) circle (.5pt) +(\\g:2mm)node{\\tiny $\\p$};
    }
    
    \\draw[->] (O)--(x) ;
    \\draw[->] (O)--(y);
    \\draw[->] (O)--(z);
    \\draw[dashed] (A)--(B);
    \\draw (B)--(C);
    %---------nước
    \\draw (-1,-1.7)
    ..controls +(-120:.5) and +(-160:.5) ..(0,-2)
    (-.9,-1.9)
    ..controls +(-70:.2) and +(-160:.2) ..(-.2,-1.9)
    (-.95,-1.8)
    ..controls +(70:.5) and +(30:.5) ..(0,-1.9)
    (.1,-1.6)
    ..controls +(-20:.2) and +(30:.2) ..(.2,-1.9)
    (-.7,-1.75)
    ..controls +(-170:.2) and +(-160:.3) ..(-.5,-1.9)
    ;
}}

\\path
(0,0)pic[scale=1]{san}
;

\\end{tikzpicture}
"""

    # ===== THÊM TIKZ FIGURES MỚI TẠI ĐÂY =====
    # Ví dụ thêm hình vẽ mới:
    # @staticmethod
    # def get_your_new_figure():
    #     """Mô tả hình vẽ của bạn"""
    #     return """
    #     \\begin{tikzpicture}
    #         % Code TikZ của bạn ở đây
    #     \\end{tikzpicture}
    #     """


# ===================================================================================
# ===== PHẦN 3: LỚP CƠ SỞ CHO CÂU HỎI TỐI ƯU HÓA =====
# ===================================================================================

class BaseOptimizationQuestion(ABC):
    """
    Lớp cơ sở cho tất cả các dạng bài toán tối ưu hóa

    Mỗi dạng toán con cần implement:
    1. generate_parameters() - Sinh tham số ngẫu nhiên
    2. calculate_answer() - Tính đáp án đúng
    3. generate_wrong_answers() - Sinh đáp án sai
    4. generate_question_text() - Sinh đề bài
    5. generate_solution() - Sinh lời giải
    """

    def __init__(self):
        """Khởi tạo các thuộc tính cơ bản"""
        self.parameters = {}  # Tham số của bài toán
        self.correct_answer = None  # Đáp án đúng
        self.wrong_answers = []  # Danh sách đáp án sai
        self.solution_steps = []  # Các bước giải (nếu cần)

    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        """
        Sinh tham số ngẫu nhiên cho bài toán

        Returns:
            Dict chứa các tham số cần thiết

        Ví dụ:
            return {
                'length': 10,
                'width': 5,
                'cost': 100000
            }
        """
        pass

    @abstractmethod
    def calculate_answer(self) -> str:
        """
        Tính đáp án đúng dựa trên parameters

        Returns:
            Chuỗi LaTeX chứa đáp án (ví dụ: "\\(5\\) mét")
        """
        pass

    @abstractmethod
    def generate_wrong_answers(self) -> List[str]:
        """
        Sinh 3 đáp án sai hợp lý

        Returns:
            List chứa 3 chuỗi LaTeX đáp án sai
        """
        pass

    @abstractmethod
    def generate_question_text(self) -> str:
        """
        Sinh đề bài bằng LaTeX

        Returns:
            Chuỗi LaTeX chứa đề bài hoàn chỉnh (có thể có hình vẽ)
        """
        pass

    @abstractmethod
    def generate_solution(self) -> str:
        """
        Sinh lời giải chi tiết bằng LaTeX

        Returns:
            Chuỗi LaTeX chứa lời giải từng bước
        """
        pass

    def generate_full_question(self, question_number: int = 1) -> str:
        """
        Tạo câu hỏi hoàn chỉnh với 4 đáp án A/B/C/D

        Args:
            question_number: Số thứ tự câu hỏi

        Returns:
            Chuỗi chứa câu hỏi hoàn chỉnh với đáp án và lời giải
        """
        logging.info(f"Đang tạo câu hỏi {question_number}")

        # Bước 1: Sinh tham số và tính toán
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        self.wrong_answers = self.generate_wrong_answers()

        # Bước 2: Tạo nội dung câu hỏi
        question_text = self.generate_question_text()
        solution = self.generate_solution()

        # Bước 3: Trộn đáp án và đánh dấu đáp án đúng
        all_answers = [self.correct_answer] + self.wrong_answers
        random.shuffle(all_answers)
        correct_index = all_answers.index(self.correct_answer)

        # Bước 4: Format câu hỏi
        question_content = f"Câu {question_number}: {question_text}\n\n"

        for j, ans in enumerate(all_answers):
            letter = chr(65 + j)  # A, B, C, D
            marker = "*" if j == correct_index else ""
            question_content += f"{marker}{letter}. {ans}\n\n"

        question_content += f"Lời giải:\n\n{solution}\n\n"

        return question_content

    def generate_question_only(self, question_number: int = 1) -> tuple:
        """Tạo câu hỏi chỉ có đề bài và lời giải"""
        logging.info(f"Đang tạo câu hỏi {question_number}")

        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()

        question_text = self.generate_question_text()
        solution = self.generate_solution()

        question_content = f"Câu {question_number}: {question_text}\n\n"
        question_content += f"Lời giải:\n\n{solution}\n\n"

        return question_content, self.correct_answer

    @staticmethod
    def create_latex_document(questions: List[str], title: str = "Câu hỏi Tối ưu hóa") -> str:
        """
        Tạo document LaTeX hoàn chỉnh (tối ưu cho xelatex)

        Args:
            questions: Danh sách câu hỏi
            title: Tiêu đề document

        Returns:
            Chuỗi LaTeX hoàn chỉnh
        """
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{polyglossia}}
\\setmainlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage{{tikz}}
\\usepackage{{tkz-tab}}
\\usepackage{{tkz-euclide}}
\\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\\begin{{document}}
\\title{{{title}}}
\\maketitle

"""
        latex_content += "\n\n".join(questions)
        latex_content += "\n\\end{document}"
        return latex_content

    @staticmethod
    def create_latex_document_with_format(questions_data: List, title: str = "Câu hỏi Tối ưu hóa", fmt: int = 1) -> str:
        """Tạo document LaTeX với 2 format khác nhau"""
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{fontspec}}
\\usepackage{{tikz}}
\\usepackage{{tkz-tab}}
\\usepackage{{tkz-euclide}}
\\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\\begin{{document}}
\\title{{{title}}}
\\maketitle

"""

        if fmt == 1:
            # Format 1: đáp án ngay sau câu hỏi
            latex_content += "\n\n".join(questions_data)
        else:
            # Format 2: câu hỏi + lời giải, đáp án ở cuối
            correct_answers = []
            for question_content, correct_answer in questions_data:
                latex_content += question_content + "\n\n"
                correct_answers.append(correct_answer)

            latex_content += "Đáp án\n\n"
            for idx, answer in enumerate(correct_answers, 1):
                # Loại bỏ ký hiệu LaTeX
                ans = answer
                if ans.startswith("\\(") and ans.endswith("\\)"):
                    ans = ans[2:-2].strip()
                # Nếu là số thập phân (có dấu phẩy), in thêm dạng dấu chấm
                if ',' in ans:
                    ans_dot = ans.replace(',', '.')
                    latex_content += f"{idx}. {ans}|{ans_dot}\n\n"
                else:
                    latex_content += f"{idx}. {ans}\n\n"

        latex_content += "\\end{document}"
        return latex_content


# ===================================================================================
# ===== PHẦN 4: DẠNG TOÁN Giao điểm đường thẳng với mặt phẳng =====
# ===================================================================================

class LineIntersectionOptimization(BaseOptimizationQuestion):
    """
    Dạng toán giao điểm đường thẳng với mặt phẳng trong không gian 3D

    Bài toán cốt lõi:
    - Cho điểm A(dưới mặt phẳng) và điểm C(trên mặt phẳng)
    - Tìm giao điểm B của đường thẳng AC với mặt phẳng z = 0
    - Tính tổng T = a + b + c của tọa độ B(a; b; c)

    Công thức:
    - Đường thẳng AC: P = A + t(C - A)
    - Giao với z = 0: A_z + t(C_z - A_z) = 0
    - t = -A_z / (C_z - A_z)
    - B = A + t(C - A)
    """

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán giao điểm đường thẳng với mặt phẳng"""

        # Các ngữ cảnh khác nhau với cùng cấu trúc toán học
        contexts = [
            {
                "name": "bird_fish",
                "upper_object": "chim bói cá",
                "lower_object": "con cá",
                "plane_name": "mặt nước",
                "upper_verb": "đang bay",
                "lower_verb": "đang bơi",
                "action": "phóng thẳng xuống"
            },
            {
                "name": "robot",
                "upper_object": "robot",
                "lower_object": "cảm biến",
                "plane_name": "mặt đất",
                "upper_verb": "đang treo lơ lửng",
                "lower_verb": "được đặt",
                "action": "di chuyển theo đường thẳng"
            },
            {
                "name": "aircraft",
                "upper_object": "máy bay không người lái",
                "lower_object": "mục tiêu",
                "plane_name": "mặt đất",
                "upper_verb": "đang bay",
                "lower_verb": "nằm ở",
                "action": "thả kiện hàng theo đường thẳng"
            },
            {
                "name": "soccer",
                "upper_object": "cầu thủ",
                "lower_object": "quả bóng",
                "plane_name": "mặt sân",
                "upper_verb": "đang bật nhảy",
                "lower_verb": "đang lăn",
                "action": "đánh đầu đưa bóng theo đường thẳng"
            },
            {
                "name": "laser",
                "upper_object": "tia laser",
                "lower_object": "điểm mục tiêu",
                "plane_name": "mặt thủy tinh",
                "upper_verb": "phát ra",
                "lower_verb": "nằm bên trong",
                "action": "chiếu thẳng"
            }
        ]

        # Chọn ngữ cảnh ngẫu nhiên
        context = random.choice(contexts)

        # Sinh khoảng cách thay vì tọa độ trực tiếp
        # Điểm C (trên mặt phẳng) - thường cao 2m đến 5m (đảm bảo z dương)
        c_z = random.randint(2, 5)
        c_x_dist = random.randint(1, 8)  # Khoảng cách đến mặt phẳng (Oyz)
        c_y_dist = random.randint(1, 8)  # Khoảng cách đến mặt phẳng (Oxz)

        # Điểm A (dưới mặt phẳng) - thường sâu 1m đến 3m (đảm bảo z âm)
        a_z = random.randint(-3, -1)
        # Đảm bảo a_x_dist khác c_x_dist
        a_x_dist = random.randint(1, 8)
        while a_x_dist == c_x_dist:
            a_x_dist = random.randint(1, 8)
        # Đảm bảo a_y_dist khác c_y_dist
        a_y_dist = random.randint(1, 8)
        while a_y_dist == c_y_dist:
            a_y_dist = random.randint(1, 8)

        # Tính tọa độ từ khoảng cách
        c_x, c_y = c_x_dist, c_y_dist
        a_x, a_y = a_x_dist, a_y_dist

        # Đảm bảo A có z âm, C có z dương ngay tại đây
        # (logic này đã được đảm bảo bằng cách sinh c_z > 0 và a_z < 0)

        # Tính tọa độ giao điểm B (trên mặt phẳng z = 0)
        t = -a_z / (c_z - a_z)
        b_x = a_x + t * (c_x - a_x)
        b_y = a_y + t * (c_y - a_y)
        b_z = 0

        return {
            'context': context,
            'point_A': (a_x, a_y, a_z),  # Điểm dưới (z < 0)
            'point_C': (c_x, c_y, c_z),  # Điểm trên (z > 0)
            'point_B': (b_x, b_y, b_z),  # Giao điểm
            'distances_A': {'x': a_x_dist, 'y': a_y_dist, 'z': abs(a_z)},
            'distances_C': {'x': c_x_dist, 'y': c_y_dist, 'z': c_z},
            'plane_name': context['plane_name']
        }

    def format_distance_description(self, point_name: str, distances: Dict) -> str:
        """Format mô tả khoảng cách đến các mặt phẳng"""
        z_unit = "m" if distances['z'] >= 1 else "cm"
        z_value = distances['z'] if distances['z'] >= 1 else distances['z'] * 100

        if z_unit == "cm":
            z_desc = f"{z_value} cm"
        else:
            z_desc = f"{z_value} m"

        return f"cách {self.parameters['plane_name']} {z_desc}, cách mặt phẳng \\((Oxz)\\) là {distances['y']} m và cách mặt phẳng \\((Oyz)\\) là {distances['x']} m"

    def calculate_answer(self) -> str:
        """Tính tọa độ giao điểm và tổng T = a + b + c"""
        A = self.parameters['point_A']
        C = self.parameters['point_C']

        # Tính tham số t của giao điểm
        # Đường thẳng AC: P = A + t(C - A)
        # Giao với mặt phẳng z = 0: A_z + t(C_z - A_z) = 0
        t = -A[2] / (C[2] - A[2])

        # Tọa độ giao điểm B
        b_x = A[0] + t * (C[0] - A[0])
        b_y = A[1] + t * (C[1] - A[1])
        b_z = 0  # Luôn là 0 vì nằm trên mặt phẳng z = 0

        # Tính tổng T = a + b + c
        total = b_x + b_y + b_z
        total_float = float(total)

        # Format kết quả - chỉ dùng số thập phân hoặc số nguyên
        if abs(total_float - round(total_float)) < 1e-10:
            # Nếu là số nguyên
            return f"\\({int(round(total_float))}\\)"
        else:
            # Nếu là số thập phân, làm tròn đến 2 chữ số
            return f"\\({format_number_clean(total_float, precision=2)}\\)"

    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai hợp lý"""
        # Lấy đáp án đúng
        correct_answer = self.calculate_answer()

        # Tách số từ đáp án đúng
        import re
        match = re.search(r'\\?\(?(\d+(?:,\d+)?)\\?\)?', correct_answer)
        if match:
            num_str = match.group(1).replace(',', '.')
            correct_value = float(num_str)
        else:
            correct_value = 1.0

        # Sinh các đáp án sai
        wrong_values = []

        # Đáp án sai 1: Cộng thêm hoặc trừ đi một lượng nhỏ
        wrong1 = correct_value + 0.2
        wrong_values.append(wrong1)

        # Đáp án sai 2: Nhân với hệ số gần 1
        wrong2 = correct_value * 0.8
        wrong_values.append(wrong2)

        # Đáp án sai 3: Sai lệch do tính toán sai
        wrong3 = correct_value * 1.2
        wrong_values.append(wrong3)

        # Format các đáp án sai - chỉ dùng số thập phân hoặc số nguyên
        wrong_answers = []
        for val in wrong_values:
            if abs(val - round(val)) < 1e-10:
                # Nếu là số nguyên
                wrong_answers.append(f"\\({int(round(val))}\\)")
            else:
                # Nếu là số thập phân, làm tròn đến 2 chữ số
                wrong_answers.append(f"\\({format_number_clean(val, precision=2)}\\)")

        return wrong_answers

    def generate_question_text(self) -> str:
        """Sinh đề bài với ngữ cảnh cụ thể"""
        context = self.parameters['context']
        distances_A = self.parameters['distances_A']
        distances_C = self.parameters['distances_C']
        plane_name = self.parameters['plane_name']

        # Format mô tả khoảng cách
        a_desc = self.format_distance_description("A", distances_A)
        c_desc = self.format_distance_description("C", distances_C)

        # Chọn hình vẽ phù hợp dựa trên context
        if context['name'] == "bird_fish":
            figure = TikZFigureLibrary.get_bird_fish_3d_coordinate_figure()
        else:
            figure = TikZFigureLibrary.get_general_3d_coordinate_figure()

        question_text = f"""Với hệ trục tọa độ \\(Oxyz\\) sao cho \\(O\\) nằm trên {plane_name}, mặt phẳng \\((Oxy)\\) là {plane_name}, trục \\(Oz\\) hướng lên trên (đơn vị đo: mét), {context['upper_object']} {context['upper_verb']} tại vị trí \\(C\\) {c_desc} và {context['lower_object']} {context['lower_verb']} tại vị trí \\(A\\) {a_desc}. {context['upper_object'].capitalize()} {context['action']} từ \\(C\\) đến \\(A\\). Gọi \\(B(a;b;c)\\) là điểm {context['upper_object']} tiếp xúc với {plane_name}. Tính \\(T = a + b + c\\) (hoặc các tổ hợp của a,b,c). Làm tròn đến 2 chữ số sau dấu phẩy.
        {figure}"""

        return question_text

    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết"""
        A = self.parameters['point_A']
        C = self.parameters['point_C']

        a_str = f"\\left({format_coord_solution(A[0])}; {format_coord_solution(A[1])}; {format_coord_solution(A[2])}\\right)"
        c_str = f"\\left({format_coord_solution(C[0])}; {format_coord_solution(C[1])}; {format_coord_solution(C[2])}\\right)"

        # Tính vector AC
        ac_x = C[0] - A[0]
        ac_y = C[1] - A[1]
        ac_z = C[2] - A[2]

        # Tính tham số t
        t = -A[2] / (C[2] - A[2])

        # Tính tọa độ điểm B
        b_x = A[0] + t * (C[0] - A[0])
        b_y = A[1] + t * (C[1] - A[1])

        answer_str = strip_latex_inline_math(self.calculate_answer())

        # FIX: Sửa vector AB - dùng (0 - A[2]) thay vì (-A[2])
        solution = f"""Ta có \\(A{a_str}\\), \\(B(a;b;0)\\) và \\(C{c_str}\\) suy ra \\(\\overrightarrow{{AC}}\\left({format_coord_solution(ac_x)}; {format_coord_solution(ac_y)}; {format_coord_solution(ac_z)}\\right)\\) và \\(\\overrightarrow{{AB}} = (a - {format_coord_solution(A[0])}; b - {format_coord_solution(A[1])}; {format_coord_solution(0 - A[2])})\\).

Vì \\(A\\), \\(B\\), \\(C\\) thẳng hàng nên ta có:

\\(\\dfrac{{a - {format_coord_solution(A[0])}}}{{{format_coord_solution(ac_x)}}} = \\dfrac{{b - {format_coord_solution(A[1])}}}{{{format_coord_solution(ac_y)}}} = \\dfrac{{{format_coord_solution(0 - A[2])}}}{{{format_coord_solution(ac_z)}}} \\Leftrightarrow \\left\\{{\\begin{{array}}{{ll}} \\dfrac{{a - {format_coord_solution(A[0])}}}{{{format_coord_solution(ac_x)}}} = \\dfrac{{{format_coord_solution(0 - A[2])}}}{{{format_coord_solution(ac_z)}}} & \\\\ \\dfrac{{b - {format_coord_solution(A[1])}}}{{{format_coord_solution(ac_y)}}} = \\dfrac{{{format_coord_solution(0 - A[2])}}}{{{format_coord_solution(ac_z)}}} & \\end{{array}}\\right.\\) \\(\\Leftrightarrow \\left\\{{\\begin{{array}}{{ll}} a = {format_coord_solution(A[0])} - \\dfrac{{{format_coord_solution(0 - A[2])} \\cdot {format_coord_solution(ac_x)}}}{{{format_coord_solution(ac_z)}}} & \\\\ b = {format_coord_solution(A[1])} - \\dfrac{{{format_coord_solution(0 - A[2])} \\cdot {format_coord_solution(ac_y)}}}{{{format_coord_solution(ac_z)}}} & \\end{{array}}\\right.\\)

Suy ra \\( B\\left({format_number_clean(b_x)}; {format_number_clean(b_y)}; 0\\right) \\) \\\\
Vậy \\( T = {format_number_clean(b_x)} + {format_number_clean(b_y)} = {answer_str} \\) """

        return solution


# ===================================================================================
# ===== PHẦN 5: DẠNG TOÁN Tọa độ cầu trong không gian =====
# ===================================================================================

class SphericalCoordinateOptimization(BaseOptimizationQuestion):
    """
    Dạng toán chuyển đổi từ tọa độ cầu sang tọa độ Descartes trong không gian 3D

    Bài toán cốt lõi:
    - Cho khoảng cách OM = r
    - Cho góc azimuth (i, OH) = α
    - Cho góc elevation (OH, OM) = β
    - Tính tọa độ điểm M(x, y, z)

    Công thức:
    - x = r × cos(β) × cos(α)
    - y = r × cos(β) × sin(α)
    - z = r × sin(β)
    """

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán tọa độ cầu"""

        # Các ngữ cảnh thực tế
        contexts = [
            {
                "name": "airport",
                "object": "máy bay",
                "location": "sân bay",
                "distance_unit": "mét",
                "angle_description": "hướng bay và độ cao"
            },
            {
                "name": "radar",
                "object": "mục tiêu",
                "location": "trạm radar",
                "distance_unit": "mét",
                "angle_description": "azimuth và elevation"
            },
            {
                "name": "astronomy",
                "object": "vệ tinh",
                "location": "đài thiên văn",
                "distance_unit": "mét",
                "angle_description": "kinh vĩ độ thiên văn"
            },
            {
                "name": "gps",
                "object": "điểm đo",
                "location": "trạm GPS",
                "distance_unit": "mét",
                "angle_description": "tọa độ định vị"
            },
            {
                "name": "crane",
                "object": "đầu cần cẩu",
                "location": "công trình",
                "distance_unit": "mét",
                "angle_description": "góc quay và góc nâng"
            }
        ]

        # Chọn ngữ cảnh ngẫu nhiên
        # context = random.choice(contexts)

        # Chọn ngữ cảnh đầu tiên
        context = contexts[0]

        # Khoảng cách tròn đẹp
        distances = [20, 30, 40, 50, 60, 80, 100]
        distance = random.choice(distances)

        # Góc đẹp cho nghiệm đẹp (sin/cos có giá trị đẹp)
        nice_angles = [30, 37, 45, 53, 60]
        azimuth_angle = random.choice(nice_angles)
        elevation_angle = random.choice(nice_angles)

        return {
            'context': context,
            'distance': distance,  # OM
            'azimuth_angle': azimuth_angle,  # góc (i, OH)
            'elevation_angle': elevation_angle,  # góc (OH, OM)
            'question_type': random.choice([1, 2, 3])  # 1: tọa độ x, 2: tọa độ y, 3: tọa độ z
        }

    def calculate_answer(self) -> str:
        """Tính tọa độ theo loại câu hỏi"""
        r = self.parameters['distance']
        alpha = math.radians(self.parameters['azimuth_angle'])  # góc azimuth
        beta = math.radians(self.parameters['elevation_angle'])  # góc elevation
        q_type = self.parameters['question_type']

        # Công thức chuyển đổi tọa độ cầu
        x = r * math.cos(beta) * math.cos(alpha)
        y = r * math.cos(beta) * math.sin(alpha)
        z = r * math.sin(beta)

        if q_type == 1:  # Tọa độ x
            return f"\\({format_number_clean(x)}\\)"
        elif q_type == 2:  # Tọa độ y
            return f"\\({format_number_clean(y)}\\)"
        else:  # Tọa độ z
            return f"\\({format_number_clean(z)}\\)"

    def generate_wrong_answers(self) -> List[str]:
        """Sinh 3 đáp án sai cho tọa độ cầu, đảm bảo khác biệt với đáp án đúng"""
        import random
        r = self.parameters['distance']
        alpha = math.radians(self.parameters['azimuth_angle'])
        beta = math.radians(self.parameters['elevation_angle'])
        q_type = self.parameters['question_type']

        # Tính đáp án đúng (dạng số thực, chưa format)
        if q_type == 1:
            correct_value = r * math.cos(beta) * math.cos(alpha)
        elif q_type == 2:
            correct_value = r * math.cos(beta) * math.sin(alpha)
        else:
            correct_value = r * math.sin(beta)

        def round2(val):
            return round(val, 2)

        # Sinh các đáp án sai với các sai lầm thường gặp
        wrong_values = []
        # Sai lầm 1: Nhầm lẫn sin/cos
        if q_type == 1:
            wrong1 = r * math.sin(beta) * math.cos(alpha)
        elif q_type == 2:
            wrong1 = r * math.sin(beta) * math.sin(alpha)
        else:
            wrong1 = r * math.cos(beta)
        wrong_values.append(wrong1)

        # Sai lầm 2: Nhầm lẫn α và β
        if q_type == 1:
            wrong2 = r * math.cos(alpha) * math.cos(beta)
        elif q_type == 2:
            wrong2 = r * math.cos(alpha) * math.sin(beta)
        else:
            wrong2 = r * math.sin(alpha)
        wrong_values.append(wrong2)

        # Sai lầm 3: Quên một thành phần
        if q_type in [1, 2]:
            wrong3 = r * math.cos(alpha) if q_type == 1 else r * math.sin(alpha)
        else:
            wrong3 = r
        wrong_values.append(wrong3)

        # Đảm bảo các đáp án sai không trùng với đáp án đúng hoặc trùng nhau (sau khi làm tròn)
        unique_wrongs = set()
        final_wrongs = []
        correct_rounded = round2(correct_value)

        for val in wrong_values:
            val_rounded = round2(val)
            tries = 0  # Di chuyển tries vào trong vòng lặp for

            # Nếu trùng với đáp án đúng hoặc đã có, sinh lại bằng cách cộng/trừ ngẫu nhiên
            while (val_rounded == correct_rounded or val_rounded in unique_wrongs) and tries < 20:
                # Sinh giá trị mới bằng cách cộng/trừ 5-20% giá trị đúng (hoặc ±1-5 nếu đúng = 0)
                if abs(correct_value) > 1e-6:
                    delta = abs(correct_value) * random.uniform(0.05, 0.2)
                else:
                    delta = random.uniform(1, 5)
                sign = random.choice([-1, 1])
                val_rounded = round2(correct_value + sign * delta)
                tries += 1

            # Chỉ thêm vào nếu không trùng
            if val_rounded != correct_rounded and val_rounded not in unique_wrongs:
                unique_wrongs.add(val_rounded)
                final_wrongs.append(val_rounded)

        # Nếu vẫn chưa đủ 3 đáp án sai khác biệt, sinh thêm
        max_attempts = 50
        attempt = 0
        while len(final_wrongs) < 3 and attempt < max_attempts:
            if abs(correct_value) > 1e-6:
                delta = abs(correct_value) * random.uniform(0.1, 0.3)
            else:
                delta = random.uniform(2, 8)
            sign = random.choice([-1, 1])
            val_rounded = round2(correct_value + sign * delta)

            if val_rounded != correct_rounded and val_rounded not in unique_wrongs:
                unique_wrongs.add(val_rounded)
                final_wrongs.append(val_rounded)
            attempt += 1

        # Nếu vẫn chưa đủ 3 đáp án, sinh thêm bằng cách dùng multiplier
        while len(final_wrongs) < 3:
            multipliers = [0.5, 0.7, 0.8, 1.2, 1.3, 1.5, 2.0]
            multiplier = random.choice(multipliers)
            val_rounded = round2(correct_value * multiplier)

            if val_rounded != correct_rounded and val_rounded not in unique_wrongs:
                unique_wrongs.add(val_rounded)
                final_wrongs.append(val_rounded)
            else:
                # Nếu vẫn trùng, thêm/trừ một số cố định
                offset = random.choice([1, 2, 3, 5]) * random.choice([-1, 1])
                val_rounded = round2(correct_value + offset)
                if val_rounded != correct_rounded and val_rounded not in unique_wrongs:
                    unique_wrongs.add(val_rounded)
                    final_wrongs.append(val_rounded)

        # Format các đáp án sai - đảm bảo chỉ lấy 3 đáp án đầu tiên
        wrong_answers = [f"\\({format_number_clean(val)}\\)" for val in final_wrongs[:3]]
        return wrong_answers

    def generate_question_text(self) -> str:
        """Sinh đề bài với ngữ cảnh cụ thể"""
        context = self.parameters['context']
        distance = self.parameters['distance']
        azimuth = self.parameters['azimuth_angle']
        elevation = self.parameters['elevation_angle']
        q_type = self.parameters['question_type']

        coordinate_names = {1: "\\(x\\)", 2: "\\(y\\)", 3: "\\(z\\)"}
        coordinate_question = coordinate_names[q_type]

        question_text = f"""Ở một {context['location']}, vị trí của {context['object']} được xác định bởi điểm \\(M\\) trong không gian \\(Oxyz\\) như hình bên. Gọi \\(H\\) là hình chiếu vuông góc của \\(M\\) xuống mặt phẳng \\((Oxy)\\). Cho biết \\(OM = {distance}\\), \\(\\left(\\overrightarrow{{i}}, \\overrightarrow{{OH}}\\right) = {azimuth}^\\circ\\), \\(\\left(\\overrightarrow{{OH}}, \\overrightarrow{{OM}}\\right) = {elevation}^\\circ\\). Tìm tọa độ {coordinate_question} của điểm \\(M\\).
        {TikZFigureLibrary.get_airplane_3d_coordinate_figure()}"""

        return question_text

    def generate_solution(self) -> str:
        """Sinh lời giải chi tiết cho tọa độ cầu"""
        r = self.parameters['distance']
        alpha_deg = self.parameters['azimuth_angle']
        beta_deg = self.parameters['elevation_angle']
        alpha = math.radians(alpha_deg)
        beta = math.radians(beta_deg)
        q_type = self.parameters['question_type']

        # Tính các giá trị trung gian
        oh = r * math.cos(beta)  # OH = OM × cos(β)
        mh = r * math.sin(beta)  # MH = OM × sin(β) = z
        oa = oh * math.cos(alpha)  # OA = OH × cos(α) = x
        ob = oh * math.sin(alpha)  # OB = OH × sin(α) = y

        answer_str = strip_latex_inline_math(self.calculate_answer())

        solution = f"""Xét \\(\\triangle OMH\\) vuông tại \\(H\\), ta có: \\(OM = {r}\\); \\(\\widehat{{MOH}} = {beta_deg}^\\circ\\) nên:

\\(OH = OM \\cdot \\cos {beta_deg}^\\circ = {r} \\cdot \\cos {beta_deg}^\\circ \\approx {format_number_clean(oh)}\\)

\\(OC = MH = OM \\cdot \\sin {beta_deg}^\\circ = {r} \\cdot \\sin {beta_deg}^\\circ \\approx {format_number_clean(mh)}\\)

Xét \\(\\triangle OAH\\) vuông tại \\(A\\), \\(OH = {format_number_clean(oh)}\\); \\(\\widehat{{AOH}} = {alpha_deg}^\\circ\\) nên ta có:

\\(OA = OH \\cdot \\cos {alpha_deg}^\\circ = {format_number_clean(oh)} \\cdot \\cos {alpha_deg}^\\circ \\approx {format_number_clean(oa)}\\)

\\(OB = AH = OH \\cdot \\sin {alpha_deg}^\\circ = {format_number_clean(oh)} \\cdot \\sin {alpha_deg}^\\circ \\approx {format_number_clean(ob)}\\)

Suy ra: \\(\\overrightarrow{{OM}} = \\overrightarrow{{OC}} + \\overrightarrow{{OH}} = \\overrightarrow{{OC}} + \\overrightarrow{{OA}} + \\overrightarrow{{OB}}\\)

\\(= {format_number_clean(oa)}\\overrightarrow{{i}} + {format_number_clean(ob)}\\overrightarrow{{j}} + {format_number_clean(mh)}\\overrightarrow{{k}}\\)

Vậy \\(M({format_number_clean(oa)}; {format_number_clean(ob)}; {format_number_clean(mh)})\\).

Tọa độ cần tìm là: {answer_str}"""

        return solution


# ===== THÊM DẠNG TOÁN MỚI TẠI ĐÂY =====


# ===================================================================================
# ===== PHẦN 6: GENERATOR CHÍNH =====
# ===================================================================================

class OptimizationGenerator:
    """
    Generator chính để tạo câu hỏi tối ưu hóa
    Quản lý tất cả các dạng toán và tạo document LaTeX
    """

    # Danh sách các dạng toán có sẵn
    QUESTION_TYPES = [
        LineIntersectionOptimization,
        SphericalCoordinateOptimization,
        # ===== THÊM DẠNG TOÁN MỚI VÀO DANH SÁCH NÀY =====
    ]

    @classmethod
    def generate_question(cls, question_number: int,
                          question_type: Type[BaseOptimizationQuestion] = None) -> str:
        """
           Tạo một câu hỏi cụ thể

           Args:
               question_number: Số thứ tự câu hỏi
               question_type: Loại câu hỏi (None = ngẫu nhiên)

           Returns:
               Chuỗi chứa câu hỏi hoàn chỉnh
           """
        if question_type is None:
            question_type = random.choice(cls.QUESTION_TYPES)

        try:
            question_instance = question_type()
            return question_instance.generate_full_question(question_number)
        except Exception as e:
            logging.error(f"Lỗi tạo câu hỏi {question_number}: {e}")
            raise

    @classmethod
    def generate_multiple_questions(cls, num_questions: int = 5) -> List[str]:
        """
        Tạo nhiều câu hỏi

        Args:
            num_questions: Số lượng câu hỏi cần tạo

        Returns:
            Danh sách câu hỏi
        """
        questions = []
        for i in range(1, num_questions + 1):
            try:
                question = cls.generate_question(i)
                questions.append(question)
                logging.info(f"Đã tạo thành công câu hỏi {i}")
            except Exception as e:
                logging.error(f"Lỗi tạo câu hỏi {i}: {e}")
                continue

        return questions

    @classmethod
    def generate_multiple_questions_with_format(cls, num_questions: int = 5, fmt: int = 1):
        """Tạo nhiều câu hỏi với format cụ thể"""
        if fmt == 1:
            return cls.generate_multiple_questions(num_questions)
        else:
            questions_data = []
            for i in range(1, num_questions + 1):
                try:
                    question_type = random.choice(cls.QUESTION_TYPES)
                    question_instance = question_type()
                    question_content, correct_answer = question_instance.generate_question_only(i)
                    questions_data.append((question_content, correct_answer))
                    logging.info(f"Đã tạo thành công câu hỏi {i}")
                except Exception as e:
                    logging.error(f"Lỗi tạo câu hỏi {i}: {e}")
                    continue
            return questions_data

    @classmethod
    def create_latex_file(cls, questions: List[str],
                          filename: str = "questions.tex",
                          title: str = "Câu hỏi") -> str:
        """
        Tạo file LaTeX hoàn chỉnh

        Args:
            questions: Danh sách câu hỏi
            filename: Tên file xuất ra
            title: Tiêu đề document

        Returns:
            Tên file đã tạo
        """
        latex_content = BaseOptimizationQuestion.create_latex_document(questions, title)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(latex_content)
            logging.info(f"Đã tạo file LaTeX: {filename}")
            return filename
        except Exception as e:
            logging.error(f"Lỗi ghi file {filename}: {e}")
            raise

    @classmethod
    def create_latex_file_with_format(cls, questions_data,
                                      filename: str = "questions.tex",
                                      title: str = "Câu hỏi", fmt: int = 1) -> str:
        """
        Tạo file LaTeX với format cụ thể

        Args:
            questions: Danh sách câu hỏi
            filename: Tên file xuất ra
            title: Tiêu đề document
            fmt: Format của câu hỏi (1 là ABCD hoặc 2 là câu hỏi + lời giải, đáp án ở cuối)

        Returns:
            Tên file đã tạo
        """
        latex_content = BaseOptimizationQuestion.create_latex_document_with_format(questions_data, title, fmt)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(latex_content)
            logging.info(f"Đã tạo file LaTeX: {filename}")
            return filename
        except Exception as e:
            logging.error(f"Lỗi ghi file {filename}: {e}")
            raise


# ===================================================================================
# ===== PHẦN 7: HÀM MAIN =====
# ===================================================================================

def main():
    """
    Hàm main để chạy generator với hỗ trợ 2 format
    Cách sử dụng:
    python math_optimization_template.py [số_câu] [format]
    """
    try:
        # Lấy tham số từ command line
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        fmt = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] in ['1', '2'] else 1

        # Tạo generator và sinh câu hỏi
        generator = OptimizationGenerator()
        questions_data = generator.generate_multiple_questions_with_format(num_questions, fmt)

        if not questions_data:
            print("Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)

        # Tạo file LaTeX
        filename = generator.create_latex_file_with_format(questions_data, fmt=fmt)

        print(f"✅ Đã tạo thành công {filename} với {len(questions_data)} câu hỏi")
        print(f"📄 Biên dịch bằng: xelatex {filename}")
        print(f"📋 Format: {fmt} ({'đáp án ngay sau câu hỏi' if fmt == 1 else 'đáp án ở cuối'})")

    except ValueError:
        print("❌ Lỗi: Vui lòng nhập số câu hỏi hợp lệ hợp lệ")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# ===================================================================================
# ===== HƯỚNG DẪN MỞ RỘNG CHI TIẾT =====
"""
🚀 HƯỚNG DẪN THÊM DẠNG TOÁN MỚI:

1. Tạo class mới kế thừa BaseOptimizationQuestion
2. Implement 5 method bắt buộc:
   - generate_parameters(): Sinh tham số
   - calculate_answer(): Tính đáp án đúng
   - generate_wrong_answers(): Sinh đáp án sai
   - generate_question_text(): Sinh đề bài
   - generate_solution(): Sinh lời giải

3. Thêm class vào OptimizationGenerator.QUESTION_TYPES

🎨 HƯỚNG DẪN THÊM HÌNH VẼ MỚI:

1. Thêm static method vào TikZFigureLibrary
2. Return chuỗi TikZ code
3. Sử dụng trong generate_question_text()

📝 HƯỚNG DẪN THÊM FORMAT MỚI:

1. Thêm hàm format vào phần "THÊM FORMAT LATEX MỚI"
2. Sử dụng trong các method generate_*

💡 MẸO HAY:
- Test từng dạng toán riêng biệt trước khi thêm vào danh sách chính
- Sử dụng logging để debug
- Tham khảo PoolOptimization và LineIntersectionOptimization như ví dụ mẫu
"""
