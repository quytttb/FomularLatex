#!/usr/bin/env python3
"""
Standalone Container Mechanics Question Generator
Tạo câu hỏi trắc nghiệm về cơ học container treo 4 dây cáp
File độc lập - không cần import thêm file khác
"""

import random
import math
import sys
import os
from datetime import datetime

def log_info(message):
    """Simple logging function"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - INFO - {message}")

def log_error(message):
    """Simple error logging function"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - ERROR - {message}")

class ContainerMechanicsGenerator:
    """Generator cho câu hỏi cơ học container treo dây cáp"""
    
    def __init__(self):
        self.force_magnitude = 1200  # N - cường độ lực căng cố định
        self.angle_pairs = [
            (120, 30),  # (góc hợp 2 dây, góc với mặt phẳng)
            (90, 45),
            (60, 60)
        ]
    
    def generate_question(self):
        """Tạo một câu hỏi ngẫu nhiên"""
        # Random chọn góc
        angle_pair = random.choice(self.angle_pairs)
        apex_angle, plane_angle = angle_pair
        
        # Random dạng câu hỏi
        question_type = random.choice(["apex_angle", "plane_angle"])
        
        # Tính trọng lượng
        weight = self.calculate_weight(plane_angle)
        
        # Tạo đáp án sai
        wrong_answers = self.generate_wrong_answers(weight)
        
        # Tạo câu hỏi
        return self.create_question_data(apex_angle, plane_angle, weight, wrong_answers, question_type)
    
    def calculate_weight(self, plane_angle_degrees):
        """Tính trọng lượng container từ góc với mặt phẳng"""
        # Góc với phương thẳng đứng = 90° - góc với mặt phẳng
        vertical_angle = 90 - plane_angle_degrees
        vertical_angle_rad = math.radians(vertical_angle)
        
        # Thành phần thẳng đứng mỗi dây = T × cos(góc với phương thẳng đứng)
        vertical_component = self.force_magnitude * math.cos(vertical_angle_rad)
        
        # Tổng lực của 4 dây
        total_weight = 4 * vertical_component
        
        return round(total_weight)
    
    def generate_wrong_answers(self, correct_weight):
        """Tạo đáp án sai hợp lý"""
        wrong_answers = []
        
        # Các sai số thường gặp
        variations = [
            int(correct_weight * 0.7),   # Thiếu 1 factor
            int(correct_weight * 1.2),   # Sai công thức
            int(correct_weight * 0.5),   # Quên nhân 4
            int(correct_weight * 1.4),   # Sai góc
            2400,  # Cố định cho góc 30°
            4800,  # 4 × 1200
            6000   # Sai hoàn toàn
        ]
        
        # Lọc và chọn 3 đáp án sai khác nhau
        for var in variations:
            if var != correct_weight and var not in wrong_answers:
                wrong_answers.append(var)
                if len(wrong_answers) >= 3:
                    break
        
        # Nếu chưa đủ 3, thêm random
        while len(wrong_answers) < 3:
            random_var = correct_weight + random.randint(-1000, 1000)
            if random_var > 0 and random_var != correct_weight and random_var not in wrong_answers:
                wrong_answers.append(random_var)
        
        return wrong_answers[:3]
    
    def create_question_data(self, apex_angle, plane_angle, weight, wrong_answers, question_type):
        """Tạo dữ liệu câu hỏi hoàn chỉnh"""
        
        # Tạo đề bài
        if question_type == "apex_angle":
            problem_statement = f"Góc hợp bởi hai dây EA và EC là {apex_angle}°"
        else:
            problem_statement = f"cùng tạo với mặt phẳng (ABCD) một góc bằng {plane_angle}°"
        
        # Tạo tất cả đáp án
        all_answers = [weight] + wrong_answers
        random.shuffle(all_answers)
        
        # Tìm vị trí đáp án đúng
        correct_index = all_answers.index(weight)
        correct_letter = chr(65 + correct_index)  # A, B, C, D
        
        return {
            'problem_statement': problem_statement,
            'apex_angle': apex_angle,
            'plane_angle': plane_angle,
            'correct_weight': weight,
            'all_answers': all_answers,
            'correct_index': correct_index,
            'correct_letter': correct_letter,
            'question_type': question_type,
            'solution_data': {
                'apex_angle': apex_angle,
                'plane_angle': plane_angle,
                'vertical_angle': 90 - plane_angle,
                'force_magnitude': self.force_magnitude,
                'cos_value': math.cos(math.radians(90 - plane_angle)),
                'vertical_component': self.force_magnitude * math.cos(math.radians(90 - plane_angle)),
                'total_weight': weight
            }
        }
    
    def generate_latex_solution(self, solution_data, question_type):
        """Tạo lời giải chi tiết bằng LaTeX"""
        apex_angle = solution_data['apex_angle']
        plane_angle = solution_data['plane_angle']
        total_weight = solution_data['total_weight']
        
        # Compute sin fraction, EO value, and symbolic P calculation
        if plane_angle == 30:
            sin_fraction = "\\frac{1}{2}"
            eo_value = "600"
            p_calculation = "2400"
        elif plane_angle == 45:
            sin_fraction = "\\frac{\\sqrt{2}}{2}"
            eo_value = "600\\sqrt{2}"
            p_calculation = "2400\\sqrt{2}"
        elif plane_angle == 60:
            sin_fraction = "\\frac{\\sqrt{3}}{2}"
            eo_value = "600\\sqrt{3}"
            p_calculation = "2400\\sqrt{3}"
        else:
            sin_value = math.sin(math.radians(plane_angle))
            sin_fraction = f"{sin_value:.3f}"
            eo_value = f"{1200 * sin_value:.0f}"
            p_calculation = f"{4 * 1200 * sin_value:.0f}"
        
        # Format result line for |P|: omit approximation for integer results
        if p_calculation.isdigit():
            p_line = f"\\( |\\vec{{P}}| = {p_calculation}\\)"
        else:
            p_line = f"\\( |\\vec{{P}}| = {p_calculation} \\approx {total_weight}\\)"
        
        # Tikz picture for diagram
        tikz_diagram = """
\\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\\footnotesize,scale=1]
 
 \\tikzset{icon-xe/.pic={ 
   \\draw[black,fill=white] 
   (0,0)coordinate (A)--(0,10) coordinate (B)--(20,-5) coordinate (C)
   --($(A)+(C)-(B)$) coordinate (D)--cycle
   ;
   \\draw[black,fill=white]  (B)--(C)--(35,8) coordinate (E)--($(B)+(E)-(C)$)coordinate (F)--cycle
   ;
   \\draw[black,fill=white]  (F)--(E)--(40,20) coordinate (H)--($(F)+(H)-(E)$)coordinate (G)--cycle
   ;
   \\draw[black,fill=white]  (G)--(H)--(60,30) coordinate (I) -- ($(G)+(I)-(H)$) coordinate (J)--cycle
   ;
   \\draw[black,fill=white]  (J)--(I)--(70,25) coordinate (L) -- ($(J)+(L)-(I)$) coordinate (K)--cycle
   ;
   
   \\path 
   (75,10)coordinate (M')
   ($(I)+(D)-(H)$) coordinate (D')
   (intersection of D--D' and L--M') coordinate (M) 
   ;
   \\draw (D)--(M)--(L) (E)--(L);
   \\draw[rotate=45,fill=black] ($(D)!1/4!(M)$) ellipse (10cm and 8cm);
   \\draw[rotate=45,fill=white] ($(D)!1/4!(M)$) ellipse (8cm and 6cm);
   \\draw[rotate=45,fill=black] ($(D)!3/4!(M)$) ellipse (10cm and 8cm);
   \\draw[rotate=45,fill=white] ($(D)!3/4!(M)$) ellipse (8cm and 6cm);
 }}


 %   \\path (1,0) pic[scale=0.05]{icon-xe};
 
 \\path 
 (0,0) coordinate (A) 
 (4,-2) coordinate (B)
 (10,0.5) coordinate (C)
 ($(A)+(C)-(B)$) coordinate (D)
 ($(A)!1/2!(C)$) coordinate (O)
 ($(O)+(0,8)$) coordinate (E)
 ;
 \\draw[fill=white] ($(A)+(0,-0.5)$)--($(B)+(0,-0.5)$)--($(C)+(0,-0.5)$)--($(D)+(0,-0.5)$)--cycle;
 \\draw[fill=white] (A)--(B)--(C)--(D)--cycle;
 \\draw[fill=white]
 ($(A)+(0,-0.5)$)--(A)--(B)--($(B)+(0,-0.5)$)--cycle
 ($(B)+(0,-0.5)$)--(B)--(C)--($(C)+(0,-0.5)$)--cycle
 ;
 
 
 \\path 
 (2,0) pic[scale=0.07,rotate=-1]{icon-xe}
 (0,0) coordinate (A) 
 (4,-2) coordinate (B)
 (10,0.5) coordinate (C)
 ($(A)+(C)-(B)$) coordinate (D)
 ($(A)!1/2!(C)$) coordinate (O)
 ($(O)+(0,10)$) coordinate (E)
 ($(A)+(0,5)$) coordinate (A')
 ($(B)+(0,5)$) coordinate (B')
 ($(C)+(0,5)$) coordinate (C')
 ($(D)+(0,5)$) coordinate (D')
 ;
 \\draw[line width=1pt] (A)--(A')(B)--(B')(C)--(C')(D)--(D')
 (A')--(E)(B')--(E)(C')--(E)(D')--(E)
 (A')--(B')--(C')--(D')--cycle
 ;
 \\draw (A')node[left,scale=2]{$A$}
 (B')node[above left=0cm,yshift=0.5cm,scale=2]{$B$}
 (C')node[right,scale=2]{$C$}
 (D')node[above right,scale=2]{$D$}
 (E)node[above,scale=2]{$E$}
 ;
 
 \\draw[->,line width=2pt] (E)--($(E)!1/3!(A')$)node[left,scale=2]{$A'$};
 \\draw[->,line width=2pt] (E)--($(E)!1/3!(B')$)node[left,scale=2]{$B'$};
 \\draw[->,line width=2pt] (E)--($(E)!1/3!(C')$)node[right,scale=2]{$C'$};
 \\draw[->,line width=2pt] (E)--($(E)!1/3!(D')$)node[right,scale=2,xshift=-0.1cm]{$D'$};
 \\path ($(E)!1/3!(A')$) coordinate (Q)
 ($(E)!1/3!(B')$) coordinate (R)
 ($(E)!1/3!(C')$) coordinate (W)
 ($(E)!1/3!(D')$) coordinate (T);
 \\draw[dashed] (Q)--(W) (R)--(T);
  ;
  \\draw ($(Q)!1/2!(W)$)node[below,scale=2,xshift=0.1cm]{$O'$};
\\end{tikzpicture}"""
        
        if question_type == "apex_angle":
            solution = f"""Lời giải:

{tikz_diagram}

Cần tính trọng lượng \\(\\Rightarrow\\) Cần tính \\(|\\vec{{P}}|\\)

Ta có: \\(|\\vec{{P}}| = |\\vec{{F}}_1 + \\vec{{F}}_2 + \\vec{{F}}_3 + \\vec{{F}}_4|\\)

\\(= |4 \\vec{{EO}}|\\)

\\(= 4 \\cdot |\\vec{{EO}}|\\)

Theo đề, 4 đoạn dây cáp có độ dài bằng nhau và góc hợp bởi hai dây EA và EC bằng {apex_angle}°

\\(\\Rightarrow\\) 4 dây cùng hợp với đáy một góc {plane_angle}°

\\(\\Rightarrow\\) \\(\\widehat{{EA'O}} = {plane_angle}°\\)

\\(\\Rightarrow\\) \\(\\sin \\widehat{{EA'O}} = \\frac{{|\\vec{{EO}}|}}{{|\\vec{{F}}_1|}}\\) \\(\\Leftrightarrow \\sin {plane_angle}° = \\frac{{|\\vec{{EO}}|}}{{1200}}\\)

\\(\\Rightarrow\\) \\( |\\vec{{EO}}| = 1200 \\cdot {sin_fraction} = {eo_value}\\)

\\(\\Rightarrow\\) {p_line}

Vậy trọng lượng của thùng container = {total_weight} N."""
        else:
            solution = f"""Lời giải:

{tikz_diagram}

Cần tính trọng lượng \\(\\Rightarrow\\) Cần tính \\(|\\vec{{P}}|\\)

Ta có: \\(|\\vec{{P}}| = |\\vec{{F}}_1 + \\vec{{F}}_2 + \\vec{{F}}_3 + \\vec{{F}}_4|\\)

\\(= |4 \\vec{{EO}}|\\)

\\(= 4 \\cdot |\\vec{{EO}}|\\)

Theo đề, 4 đoạn dây cáp có độ dài bằng nhau và cùng tạo với mặt phẳng (ABCD) một góc bằng {plane_angle}°

\\(\\Rightarrow\\) \\(\\widehat{{EA'O}} = {plane_angle}°\\)

\\(\\Rightarrow\\) \\(\\sin \\widehat{{EA'O}} = \\frac{{|\\vec{{EO}}|}}{{|\\vec{{F}}_1|}}\\) \\(\\Leftrightarrow \\sin {plane_angle}° = \\frac{{|\\vec{{EO}}|}}{{1200}}\\)

\\(\\Rightarrow\\) \\( |\\vec{{EO}}| = 1200 \\cdot {sin_fraction} = {eo_value}\\)

\\(\\Rightarrow\\) {p_line}

Vậy trọng lượng của thùng container = {total_weight} N."""
        
        return solution

def format_question_block(question_data, idx):
    """Trả về LaTeX phần đề bài và hình vẽ cho câu hỏi idx (1-based)"""
    if question_data['question_type'] == 'apex_angle':
        return f"""Câu {idx+1}: Một thùng hàng container được treo cân bằng bởi 4 sợi dây cáp được nối vào 4 đầu của thùng hàng (như hình vẽ minh họa). Các sợi dây cáp độ được buộc vào mốc E của chiếc cần cẩu sao cho các đoạn dây cáp EA, EB, EC, ED có độ dài bằng nhau. {question_data['problem_statement']}. Chiếc cần cẩu kéo khung sắt lên theo phương thẳng đứng. Tính trọng lượng của thùng hàng container (làm tròn đến hàng đơn vị), biết rằng các lực căng của các sợi dây cáp đều có cường độ là 1200 N.

\\begin{{tikzpicture}}[line join = round, line cap=round,>=stealth,font=\\footnotesize,scale=0.7]
 
 \\tikzset{{icon-xe/.pic={{ 
  \\begin{{scope}}[scale=0.7]
   \\draw[black,fill=white] 
   (0,0)coordinate (A)--(0,10) coordinate (B)--(20,-5) coordinate (C)
   --($(A)+(C)-(B)$) coordinate (D)--cycle
   ;
   \\draw[black,fill=white]  (B)--(C)--(35,8) coordinate (E)--($(B)+(E)-(C)$)coordinate (F)--cycle
   ;
   \\draw[black,fill=white]  (F)--(E)--(40,20) coordinate (H)--($(F)+(H)-(E)$)coordinate (G)--cycle
   ;
   \\draw[black,fill=white]  (G)--(H)--(60,30) coordinate (I) -- ($(G)+(I)-(H)$) coordinate (J)--cycle
   ;
   \\draw[black,fill=white]  (J)--(I)--(70,25) coordinate (L) -- ($(J)+(L)-(I)$) coordinate (K)--cycle
   ;
   
   \\path 
   (75,10)coordinate (M')
   ($(I)+(D)-(H)$) coordinate (D')
   (intersection of D--D' and L--M') coordinate (M) 
   ;
   \\draw (D)--(M)--(L) (E)--(L);
   \\draw[rotate=45,fill=black] ($(D)!1/4!(M)$) ellipse (10cm and 8cm);
   \\draw[rotate=45,fill=white] ($(D)!1/4!(M)$) ellipse (8cm and 6cm);
   \\draw[rotate=45,fill=black] ($(D)!3/4!(M)$) ellipse (10cm and 8cm);
   \\draw[rotate=45,fill=white] ($(D)!3/4!(M)$) ellipse (8cm and 6cm);
   \\end{{scope}}
 }}}}


 %   \\path (1,0) pic[scale=0.05]{{icon-xe}};
 
 \\path 
 (0,0) coordinate (A) 
 (4,-2) coordinate (B)
 (10,0.5) coordinate (C)
 ($(A)+(C)-(B)$) coordinate (D)
 ($(A)!1/2!(C)$) coordinate (O)
 ($(O)+(0,8)$) coordinate (E)
 ;
 \\draw[fill=white] ($(A)+(0,-0.5)$)--($(B)+(0,-0.5)$)--($(C)+(0,-0.5)$)--($(D)+(0,-0.5)$)--cycle;
 \\draw[fill=white] (A)--(B)--(C)--(D)--cycle;
 \\draw[fill=white]
 ($(A)+(0,-0.5)$)--(A)--(B)--($(B)+(0,-0.5)$)--cycle
 ($(B)+(0,-0.5)$)--(B)--(C)--($(C)+(0,-0.5)$)--cycle
 ;
 
 
 \\path 
 (2,0) pic[scale=0.07,rotate=-1]{{icon-xe}}
 (0,0) coordinate (A) 
 (4,-2) coordinate (B)
 (10,0.5) coordinate (C)
 ($(A)+(C)-(B)$) coordinate (D)
 ($(A)!1/2!(C)$) coordinate (O)
 ($(O)+(0,10)$) coordinate (E)
 ($(A)+(0,5)$) coordinate (A')
 ($(B)+(0,5)$) coordinate (B')
 ($(C)+(0,5)$) coordinate (C')
 ($(D)+(0,5)$) coordinate (D')
 ;
 \\draw[line width=1pt] (A)--(A')(B)--(B')(C)--(C')(D)--(D')
 (A')--(E)(B')--(E)(C')--(E)(D')--(E)
 (A')--(B')--(C')--(D')--cycle
 ;
 \\draw (A')node[left,scale=2]{{$A$}}
 (B')node[above left=0cm,yshift=0.5cm,scale=2]{{$B$}}
 (C')node[right,scale=2]{{$C$}}
 (D')node[above right,scale=2]{{$D$}}
 (E)node[above,scale=2]{{$E$}}
 ;
 \\draw[->,line width=2pt] (E)--($(E)!1/3!(A')$)node[left,scale=2]{{$\\overrightarrow{{F}}_1$}};
 \\draw[->,line width=2pt] (E)--($(E)!1/3!(B')$)node[left,scale=2]{{$\\overrightarrow{{F}}_2$}};
 \\draw[->,line width=2pt] (E)--($(E)!1/3!(C')$)node[right,scale=2]{{$\\overrightarrow{{F}}_3$}};
 \\draw[->,line width=2pt] (E)--($(E)!1/2!(D')$)node[below,scale=2,xshift=-0.1cm]{{$\\overrightarrow{{F}}_4$}};
\\end{{tikzpicture}}

"""
    else:
        return f"""Câu {idx+1}: Một thùng hàng container được treo cân bằng bởi 4 sợi dây cáp được nối vào 4 đầu của thùng hàng (như hình vẽ minh họa). Các sợi dây cáp độ được buộc vào mốc E của chiếc cần cẩu sao cho các đoạn dây cáp EA, EB, EC, ED có độ dài bằng nhau và {question_data['problem_statement']}. Chiếc cần cẩu kéo khung sắt lên theo phương thẳng đứng. Tính trọng lượng của thùng hàng container (làm tròn đến hàng đơn vị), biết rằng các lực căng của các sợi dây cáp đều có cường độ là 1200 N.

\\begin{{tikzpicture}}[line join = round, line cap=round,>=stealth,font=\\footnotesize,scale=0.7]
 
 \\tikzset{{icon-xe/.pic={{ 
  \\begin{{scope}}[scale=0.7]
   \\draw[black,fill=white] 
   (0,0)coordinate (A)--(0,10) coordinate (B)--(20,-5) coordinate (C)
   --($(A)+(C)-(B)$) coordinate (D)--cycle
   ;
   \\draw[black,fill=white]  (B)--(C)--(35,8) coordinate (E)--($(B)+(E)-(C)$)coordinate (F)--cycle
   ;
   \\draw[black,fill=white]  (F)--(E)--(40,20) coordinate (H)--($(F)+(H)-(E)$)coordinate (G)--cycle
   ;
   \\draw[black,fill=white]  (G)--(H)--(60,30) coordinate (I) -- ($(G)+(I)-(H)$) coordinate (J)--cycle
   ;
   \\draw[black,fill=white]  (J)--(I)--(70,25) coordinate (L) -- ($(J)+(L)-(I)$) coordinate (K)--cycle
   ;
   
   \\path 
   (75,10)coordinate (M')
   ($(I)+(D)-(H)$) coordinate (D')
   (intersection of D--D' and L--M') coordinate (M) 
   ;
   \\draw (D)--(M)--(L) (E)--(L);
   \\draw[rotate=45,fill=black] ($(D)!1/4!(M)$) ellipse (10cm and 8cm);
   \\draw[rotate=45,fill=white] ($(D)!1/4!(M)$) ellipse (8cm and 6cm);
   \\draw[rotate=45,fill=black] ($(D)!3/4!(M)$) ellipse (10cm and 8cm);
   \\draw[rotate=45,fill=white] ($(D)!3/4!(M)$) ellipse (8cm and 6cm);
   \\end{{scope}}
 }}}}
 
 
 %   \\path (1,0) pic[scale=0.05]{{icon-xe}};
 
 \\path 
 (0,0) coordinate (A) 
 (4,-2) coordinate (B)
 (10,0.5) coordinate (C)
 ($(A)+(C)-(B)$) coordinate (D)
 ($(A)!1/2!(C)$) coordinate (O)
 ($(O)+(0,8)$) coordinate (E)
 ;
 \\draw[fill=white] ($(A)+(0,-0.5)$)--($(B)+(0,-0.5)$)--($(C)+(0,-0.5)$)--($(D)+(0,-0.5)$)--cycle;
 \\draw[fill=white] (A)--(B)--(C)--(D)--cycle;
 \\draw[fill=white]
 ($(A)+(0,-0.5)$)--(A)--(B)--($(B)+(0,-0.5)$)--cycle
 ($(B)+(0,-0.5)$)--(B)--(C)--($(C)+(0,-0.5)$)--cycle
 ;
 
 
 \\path 
 (2,0) pic[scale=0.07,rotate=-1]{{icon-xe}}
 (0,0) coordinate (A) 
 (4,-2) coordinate (B)
 (10,0.5) coordinate (C)
 ($(A)+(C)-(B)$) coordinate (D)
 ($(A)!1/2!(C)$) coordinate (O)
 ($(O)+(0,10)$) coordinate (E)
 ($(A)+(0,5)$) coordinate (A')
 ($(B)+(0,5)$) coordinate (B')
 ($(C)+(0,5)$) coordinate (C')
 ($(D)+(0,5)$) coordinate (D')
 ;
 \\draw[line width=1pt] (A)--(A')(B)--(B')(C)--(C')(D)--(D')
 (A')--(E)(B')--(E)(C')--(E)(D')--(E)
 (A')--(B')--(C')--(D')--cycle
 ;
 \\draw (A')node[left,scale=2]{{$A$}}
 (B')node[above left=0cm,yshift=0.5cm,scale=2]{{$B$}}
 (C')node[right,scale=2]{{$C$}}
 (D')node[above right,scale=2]{{$D$}}
 (E)node[above,scale=2]{{$E$}}
 ;
 \\draw[->,line width=2pt] (E)--($(E)!1/3!(A')$)node[left,scale=2]{{$\\overrightarrow{{F}}_1$}};
 \\draw[->,line width=2pt] (E)--($(E)!1/3!(B')$)node[left,scale=2]{{$\\overrightarrow{{F}}_2$}};
 \\draw[->,line width=2pt] (E)--($(E)!1/3!(C')$)node[right,scale=2]{{$\\overrightarrow{{F}}_3$}};
 \\draw[->,line width=2pt] (E)--($(E)!1/2!(D')$)node[below,scale=2,xshift=-0.1cm]{{$\\overrightarrow{{F}}_4$}};
\\end{{tikzpicture}}

"""

def generate_latex_document(num_questions=3, fmt=1):
    """Tạo document LaTeX hoàn chỉnh với hai dạng format"""
    generator = ContainerMechanicsGenerator()
    # LaTeX header
    latex_content = """\\documentclass[a4paper,12pt]{article}
\\usepackage{amsmath}
\\usepackage{amsfonts}
\\usepackage{amssymb}
\\usepackage{geometry}
\\geometry{a4paper, margin=1in}
\\usepackage{polyglossia}
\\setmainlanguage{vietnamese}
\\setmainfont{DejaVu Serif}
\\usepackage{tikz}
\\usetikzlibrary{calc}
\\begin{document}
Câu hỏi Trắc nghiệm về Cơ học

"""
    # Chọn format
    correct_answers = []
    if fmt == 1:
        for i in range(num_questions):
            q = generator.generate_question()
            latex_content += format_question_block(q, i)
            # Đáp án lựa chọn
            for j, ans in enumerate(q['all_answers']):
                letter = chr(65 + j)
                marker = "*" if j == q['correct_index'] else ""
                latex_content += f"{marker}{letter}. {ans} N\n\n"
            # Lời giải
            sol = generator.generate_latex_solution(q['solution_data'], q['question_type'])
            latex_content += sol + "\n\n"
    else:
        for i in range(num_questions):
            q = generator.generate_question()
            latex_content += format_question_block(q, i)
            # Lời giải
            sol = generator.generate_latex_solution(q['solution_data'], q['question_type'])
            latex_content += sol + "\n\n"
            correct_answers.append(q['correct_weight'])
        # Phần đáp án cuối
        latex_content += "Đáp án\n\n"
        for idx, weight in enumerate(correct_answers):
            latex_content += f"{idx+1}. {weight} N\n\n"
    latex_content += "\\end{document}"
    return latex_content

def main():
    """Hàm main"""
    try:
        # Số câu hỏi và định dạng từ command line
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        fmt = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] in ['1','2'] else 1
        
        # Tạo nội dung LaTeX với định dạng
        latex_content = generate_latex_document(num_questions, fmt)
        
        # Ghi file vào thư mục hiện tại
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "standalone_container_mechanics_questions.tex")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        log_info(f"Successfully wrote LaTeX content to {filename}")
        print(f"Generated {filename} with {num_questions} question(s). Compile with XeLaTeX.")
        
        # In thông tin về câu hỏi được tạo
        print(f"\nChi tiết:")
        print(f"- Số câu hỏi: {num_questions}")
        print(f"- File LaTeX output: {filename}")
        print(f"- Để biên dịch: xelatex {os.path.basename(filename)}")
        
    except ValueError as e:
        log_error(f"Invalid number of questions: {e}")
        print("Error: Please provide a valid number for questions")
        sys.exit(1)
    except Exception as e:
        log_error(f"Error in main: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
