import math
import random
import sys
import os
from datetime import datetime
from typing import Dict, List

def log_info(message):
    """Simple logging function"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - INFO - {message}")

def log_error(message):
    """Simple error logging function"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - ERROR - {message}")

class ForceResultantQuestion:
    """
    Sinh câu hỏi hợp lực 3 lực đồng quy với 3 góc khác nhau giữa các lực.
    """
    def __init__(self):
        self.parameters = self.generate_parameters()

    def generate_parameters(self) -> Dict:
        # Chọn các bộ số đẹp, 3 góc khác nhau và các lực nguyên
        angle_choices = [60, 90, 120, 110, 150]
        F1_choices = [3, 4, 5, 6, 7, 8, 9]
        F2_choices = [3, 4, 5, 6, 7, 8, 9]
        F3_choices = [3, 4, 5, 6, 7, 8, 9]
        
        max_attempts = 100
        for attempt in range(max_attempts):
            # Chọn 3 góc khác nhau
            angles = random.sample(angle_choices, 3)
            alpha12 = angles[0]  # góc giữa F1 và F2
            alpha23 = angles[1]  # góc giữa F2 và F3  
            alpha13 = angles[2]  # góc giữa F1 và F3
            
            F1 = random.choice(F1_choices)
            F2 = random.choice(F2_choices)
            F3 = random.choice(F3_choices)
            
            # Tính hợp lực theo công thức vector
            cos_alpha12 = math.cos(math.radians(alpha12))
            cos_alpha23 = math.cos(math.radians(alpha23))
            cos_alpha13 = math.cos(math.radians(alpha13))
            
            # |F1 + F2 + F3|² = F1² + F2² + F3² + 2F1F2cos(α12) + 2F2F3cos(α23) + 2F1F3cos(α13)
            resultant_squared = (F1**2 + F2**2 + F3**2 + 
                               2*F1*F2*cos_alpha12 + 
                               2*F2*F3*cos_alpha23 + 
                               2*F1*F3*cos_alpha13)
            
            if resultant_squared > 0:
                resultant = math.sqrt(resultant_squared)
                # Đảm bảo nghiệm đẹp, hợp lực là số nguyên hoặc gần nguyên
                if 8 <= resultant <= 25 and abs(resultant - round(resultant)) < 0.4:
                    return {
                        'F1': F1,
                        'F2': F2,
                        'F3': F3,
                        'alpha12': alpha12,  # góc giữa F1 và F2
                        'alpha23': alpha23,  # góc giữa F2 và F3
                        'alpha13': alpha13,  # góc giữa F1 và F3
                        'resultant': round(resultant)
                    }
        
        # Fallback nếu không tìm được nghiệm đẹp
        return {
            'F1': 4,
            'F2': 5,
            'F3': 6,
            'alpha12': 90,
            'alpha23': 120,
            'alpha13': 90,
            'resultant': 11
        }

    def generate_question_text(self) -> str:
        p = self.parameters
        return (
            f"""Có ba lực cùng tác động vào một vật tại một điểm. Trong đó lực \\(F_1\\) và \\(F_2\\) tạo với nhau một góc {p['alpha12']}\\(^\\circ\\) và có độ lớn lần lượt là {p['F1']} N và {p['F2']} N, lực \\(F_2\\) và \\(F_3\\) tạo với nhau một góc {p['alpha23']}\\(^\\circ\\), lực \\(F_1\\) và \\(F_3\\) tạo với nhau một góc {p['alpha13']}\\(^\\circ\\), lực \\(F_3\\) có độ lớn {p['F3']} N. Độ lớn của hợp lực của ba lực trên là bao nhiêu newton (N)? (Kết quả làm tròn đến hàng đơn vị)"""
        )

    def generate_solution(self) -> str:
        p = self.parameters
        F1, F2, F3 = p['F1'], p['F2'], p['F3']
        alpha12, alpha23, alpha13 = p['alpha12'], p['alpha23'], p['alpha13']
        
        cos_alpha12 = math.cos(math.radians(alpha12))
        cos_alpha23 = math.cos(math.radians(alpha23))
        cos_alpha13 = math.cos(math.radians(alpha13))
        
        # Tính từng thành phần
        sum_squares = F1**2 + F2**2 + F3**2
        dot_product_12 = 2*F1*F2*cos_alpha12
        dot_product_23 = 2*F2*F3*cos_alpha23
        dot_product_13 = 2*F1*F3*cos_alpha13
        
        total = sum_squares + dot_product_12 + dot_product_23 + dot_product_13
        
        s = f"""Lời giải:

Ta có:\\\\
\\(|\\vec{{F_1}} + \\vec{{F_2}} + \\vec{{F_3}}|^2\\)\\\\
\\(= F_1^2 + F_2^2 + F_3^2 + 2\\vec{{F_1}}\\vec{{F_2}} + 2\\vec{{F_2}}\\vec{{F_3}} + 2\\vec{{F_1}}\\vec{{F_3}}\\)\\\\
\\(= F_1^2 + F_2^2 + F_3^2 + 2F_1F_2\\cos({alpha12}^\\circ) + 2F_2F_3\\cos({alpha23}^\\circ) + 2F_1F_3\\cos({alpha13}^\\circ)\\)\\\\
\\(= {F1}^2 + {F2}^2 + {F3}^2 + 2 \\times {F1} \\times {F2} \\times {cos_alpha12:.3f} + 2 \\times {F2} \\times {F3} \\times {cos_alpha23:.3f} + 2 \\times {F1} \\times {F3} \\times {cos_alpha13:.3f}\\)\\\\
\\(= {F1**2} + {F2**2} + {F3**2} + {dot_product_12:.3f} + {dot_product_23:.3f} + {dot_product_13:.3f}\\)\\\\
\\(= {sum_squares} + {dot_product_12 + dot_product_23 + dot_product_13:.3f}\\)\\\\
\\(= {total:.3f}\\)\\\\
\\(\\Rightarrow |\\vec{{F_1}} + \\vec{{F_2}} + \\vec{{F_3}}| = \\sqrt{{{total:.3f}}} \\approx {p['resultant']}\\) (N)

Vậy độ lớn của hợp lực = {p['resultant']} N."""
        return s

    def generate_wrong_answers(self) -> List[str]:
        p = self.parameters
        correct = p['resultant']
        # Sinh 3 đáp án sai, lệch 1-3 đơn vị
        wrongs = set()
        for d in [-3, -2, -1, 1, 2, 3, 4]:
            if 6 <= correct + d <= 30 and d != 0:
                wrongs.add(correct + d)
            if len(wrongs) == 3:
                break
        return list(map(str, sorted(wrongs)))

def format_question_block(question_instance, idx):
    """Trả về LaTeX phần đề bài cho câu hỏi idx (1-based)"""
    question_text = question_instance.generate_question_text()
    return f"""Câu {idx+1}: {question_text}

"""

def generate_latex_document(num_questions=5, fmt=1):
    """Tạo document LaTeX hoàn chỉnh với hai dạng format"""
    # LaTeX header đơn giản
    latex_content = """\\documentclass[a4paper,12pt]{article}
\\usepackage{amsmath}
\\usepackage{amsfonts}
\\usepackage{amssymb}
\\usepackage{geometry}
\\geometry{a4paper, margin=1in}
\\usepackage{polyglossia}
\\setmainlanguage{vietnamese}
\\setmainfont{DejaVu Serif}
\\begin{document}
Câu hỏi Trắc nghiệm về Hợp lực

"""
    
    # Chọn format
    correct_answers = []
    if fmt == 1:
        # Format 1: đáp án ngay sau câu hỏi
        for i in range(num_questions):
            q = ForceResultantQuestion()
            latex_content += format_question_block(q, i)
            
            # Tạo đáp án lựa chọn
            correct = str(q.parameters['resultant'])
            wrong_answers = q.generate_wrong_answers()
            all_answers = [correct] + wrong_answers
            random.shuffle(all_answers)
            
            correct_index = all_answers.index(correct)
            
            # Đáp án lựa chọn
            for j, ans in enumerate(all_answers):
                letter = chr(65 + j)
                marker = "*" if j == correct_index else ""
                latex_content += f"{marker}{letter}. {ans} N\n\n"
            
            # Lời giải
            solution = q.generate_solution()
            latex_content += solution + "\n\n"
    else:
        # Format 2: chỉ câu hỏi + lời giải, đáp án ở cuối
        for i in range(num_questions):
            q = ForceResultantQuestion()
            latex_content += format_question_block(q, i)
            
            # Lời giải
            solution = q.generate_solution()
            latex_content += solution + "\n\n"
            
            correct_answers.append(q.parameters['resultant'])
        
        # Phần đáp án cuối
        latex_content += "Đáp án\n\n"
        for idx, answer in enumerate(correct_answers):
            latex_content += f"{idx+1}. {answer} N\n\n"
    
    latex_content += "\\end{document}"
    return latex_content

def main():
    """Hàm main"""
    try:
        # Số câu hỏi và định dạng từ command line
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 5
        fmt = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] in ['1','2'] else 1
        
        # Tạo nội dung LaTeX với định dạng
        latex_content = generate_latex_document(num_questions, fmt)
        
        # Ghi file vào thư mục hiện tại
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "force_resultant_questions.tex")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        log_info(f"Successfully wrote LaTeX content to {filename}")
        print(f"Generated {filename} with {num_questions} question(s). Compile with XeLaTeX.")
        
        # In thông tin về câu hỏi được tạo
        print(f"\nChi tiết:")
        print(f"- Số câu hỏi: {num_questions}")
        print(f"- Format: {fmt} ({'đáp án ngay sau câu hỏi' if fmt == 1 else 'đáp án ở cuối'})")
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
