"""
Thư viện hình vẽ TikZ cho hệ thống sinh câu hỏi toán tối ưu hóa
Tách từ math_template.py - PHẦN 2
"""

class TikZFigureLibrary:
    """Thư viện hình vẽ TikZ"""

    @staticmethod
    def get_bird_fish_3d_coordinate_figure():
        """Hình vẽ chim bói cá lặn xuống bắt cá với hệ trục tọa độ 3D"""
        return """
\\begin{tikzpicture}[line join=round, line cap=round,scale=1,transform shape, >=stealth]
% Định nghĩa màu sắc
\\definecolor{columbiablue}{rgb}{0.61, 0.87, 1.0}
\\definecolor{arsenic}{rgb}{0.23, 0.27, 0.29}
\\definecolor{antiquewhite}{rgb}{0.98, 0.92, 0.84}
\\definecolor{cadmiumorange}{rgb}{0.93, 0.53, 0.18}
\\definecolor{coolblack}{rgb}{0.0, 0.18, 0.39}
\\definecolor{brandeisblue}{rgb}{0.0, 0.44, 1.0}
\\definecolor{darkcoral}{rgb}{0.8, 0.36, 0.27}
\\definecolor{amber}{rgb}{1.0, 0.49, 0.0}
% Hệ trục tọa độ 3D
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
% Vẽ chim và cá (simplified)
\\draw[fill=cadmiumorange] (1.5,1) circle (0.3);
\\draw[fill=amber] (-1,-2) circle (0.2);
\\end{tikzpicture}
"""

    @staticmethod
    def get_airplane_3d_coordinate_figure():
        """Hình vẽ máy bay trong không gian 3D với hệ trục tọa độ"""
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
% Vẽ máy bay đơn giản
\\draw[fill=gray] (M) circle (0.3);
\\draw[cyan,line width=2pt,->] (O)--(M);	
\\foreach \\p/\\r in {A/160,B/90,C/180,H/-45}
\\fill (\\p) circle (1.2pt) node[shift={(\\r:3mm)},scale=0.8]{$\\p$};
\\end{tikzpicture}
"""

    @staticmethod
    def get_general_3d_coordinate_figure():
        """Hình vẽ hệ trục tọa độ 3D mở rộng"""
        return """
\\begin{tikzpicture}[line join=round, line cap=round,scale=1,transform shape, >=stealth]
\\definecolor{columbiablue}{rgb}{0.61, 0.87, 1.0}
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
\\end{tikzpicture}
"""

    # ===== THÊM TIKZ FIGURES MỚI TẠI ĐÂY =====
    # @staticmethod
    # def get_your_new_figure():
    #     """Mô tả hình vẽ của bạn"""
    #     return """
    #     \\begin{tikzpicture}
    #         % Code TikZ của bạn ở đây
    #     \\end{tikzpicture}
    #     """
