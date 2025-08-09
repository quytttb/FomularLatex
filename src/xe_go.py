import math
import subprocess
import random
import sys


# Biến chứa hình vẽ TikZ
TIKZ_FIGURE = """
\\begin{center}
\\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\\footnotesize,scale=1]
 \\def \\r{3}  \\def \\goc{15} \\def\\xoay{30}
 
 \\path (0,0) coordinate (O)
 ;
 \\draw 
 (O) circle (\\r cm)
 (\\goc:\\r) coordinate (A1)
 (-\\goc:\\r) coordinate (A0)
 (180-\\goc:\\r) coordinate (A2)
 (180+\\goc:\\r) coordinate (A3)
 (90+\\goc:\\r) coordinate (B1)
 (90-\\goc:\\r) coordinate (B0)
 (90+180-\\goc:\\r) coordinate (B2)
 (90+180+\\goc:\\r) coordinate (B3)
 (3*\\goc:\\r) coordinate (C0)
 (9*\\goc:\\r) coordinate (C1)
 (15*\\goc:\\r) coordinate (C2)
 (21*\\goc:\\r) coordinate (C3)
 (intersection of A1--A2 and C1--C2) coordinate (D0) 
 (intersection of A3--A0 and C1--C2) coordinate (D1) 
 (intersection of A1--A2 and C3--C0) coordinate (D3) 
 (intersection of A3--A0 and C3--C0) coordinate (D2)
 %%%%%%
 (intersection of B1--B2 and C1--C0) coordinate (E1) 
 (intersection of B3--B0 and C1--C0) coordinate (E0) 
 (intersection of B1--B2 and C3--C2) coordinate (E2) 
(intersection of B0--B3 and C3--C2) coordinate (E3) 
 ; 
 
 \\fill[brown,opacity=0.8]
 (A3)--(A2)--(D0)--(D1)--cycle
 (B1)--(E1)--(E0)--(B0)--cycle
 (A1)--(D3)--(D2)--(A0)--cycle
 (E2)--(B2)--(B3)--(E3)--cycle
 ;
 



 
 \\draw  (C1)--(C3) ;
 \\draw (C0)--(C1)--(C2)--(C3)--cycle; 
 \\draw[dashed]  (A1)--(A3)  (D3)--(D0)  (D1)--(D2) ;
 
%\\draw[opacity=0.2] (-3,-3) grid (3,3);


 \\fill[brown,opacity=0.8]
(A3)--(A2)--(D0)--(D1)--cycle
(B1)--(E1)--(E0)--(B0)--cycle
(A1)--(D3)--(D2)--(A0)--cycle
(E2)--(B2)--(B3)--(E3)--cycle
;


 \\clip
(A3)--(A2)--(D0)--(D1)--cycle
(B1)--(E1)--(E0)--(B0)--cycle
(A1)--(D3)--(D2)--(A0)--cycle
(E2)--(B2)--(B3)--(E3)--cycle
;


\\draw [line width=1pt,opacity=0.2]
(-2.7,0.5) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
(-2.7,0) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
(-2.7,-0.25) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
(-2.7,-0.5) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
%%%%%%%%%
(-0,-2.75) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
(-0.25,-2.65) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
(-0.5,-2.55) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
(-0.75,-2.35) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
;
% \\foreach \\p/\\r in {A0/0,A1/0,A2/0,A3/0,B0/0,B1/0,B2/0,B3/0,C0/0,C1/0,C2/0,C3/0,D0/0,D1/0,D2/0,D3/0,E0/0,E1/0,E2/0,E3/0
% }
% \\fill (\\p) circle (1.2pt) node[shift={(\\r:3mm)}]{$\\p$}; 

% Vẽ các đường vân gỗ (mở rộng thêm các đường cong)
\\draw[line width=1pt,opacity=0.2]
(-2.7,0.5) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
(-2.7,0) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
(-2.7,-0.25) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
(-2.7,-0.5) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
(-2.7,0.75) ..controls +(25:1.2) and +(155:1.2) .. ++ (3.3,2.8) % Thêm đường cong
(-2.7,0.25) ..controls +(15:0.8) and +(165:0.8) .. ++ (3.2,2.7) % Thêm đường cong
(-2.7,-0.75) ..controls +(22:1.1) and +(158:1.1) .. ++ (3.3,2.9) % Thêm đường cong
%%%%%%%%%
(-0,-2.75) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
(-0.25,-2.65) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
(-0.5,-2.55) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
(-0.75,-2.35) ..controls +(20:1) and +(160:1) .. ++ (3.25,2.75)
(-0.1,-2.85) ..controls +(18:0.9) and +(162:0.9) .. ++ (3.2,2.6) % Thêm đường cong
(-0.35,-2.75) ..controls +(22:1.1) and +(158:1.1) .. ++ (3.3,2.8) % Thêm đường cong
(-0.9,-2.25) ..controls +(25:1.2) and +(155:1.2) .. ++ (3.4,2.9) % Thêm đường cong
;
 
 \\end{tikzpicture}
\\end{center}
"""


# Tạo đề và lời giải ở dạng LaTeX
def generate_latex_solution(d, question_number=1):
    R = d / 2
    S_square = d ** 2 / 2  # Diện tích hình vuông nội tiếp

    # Dò alpha từ ~45.3° đến ~88.5° để tìm diện tích phụ lớn nhất (theo hình vẽ thực tế)
    max_area = -1
    optimal_alpha = 0
    optimal_alpha_deg = 0

    for i in range(790, 1550):  # alpha từ 0.79 đến 1.55 rad
        alpha = i / 1000
        AB = 2 * R * math.cos(alpha)  # chiều dài miếng phụ
        BC = R * math.sin(alpha) - (R / math.sqrt(2))  # chiều rộng miếng phụ

        if BC > 0:  # Chỉ xét khi chiều rộng dương (hợp lệ)
            area = 4 * AB * BC  # diện tích 4 miếng phụ
            if area > max_area:
                max_area = area
                optimal_alpha = alpha
                optimal_alpha_deg = math.degrees(alpha)

    S_auxiliary = max_area
    S_total = S_square + S_auxiliary
    
    # Tạo 4 đáp án ABCD
    correct_answer = round(S_total)
    
    # Tạo 3 đáp án sai bằng cách thêm/bớt giá trị
    wrong_answers = [
        correct_answer + random.randint(5, 15),  # Thêm 5-15
        correct_answer - random.randint(3, 12),  # Bớt 3-12
        correct_answer + random.randint(-8, -2)  # Bớt 2-8
    ]
    
    # Đảm bảo không có đáp án âm
    wrong_answers = [max(1, ans) for ans in wrong_answers]
    
    # Tạo danh sách 4 đáp án và xáo trộn
    all_answers = [correct_answer] + wrong_answers
    random.shuffle(all_answers)
    
    # Tạo danh sách đáp án với dấu * cho đáp án đúng
    answer_lines = []
    for i, answer in enumerate(all_answers):
        letter = chr(65 + i)  # A, B, C, D
        if answer == correct_answer:
            answer_lines.append(f"*{letter}. {answer} cm\\(^2\\)")
        else:
            answer_lines.append(f"{letter}. {answer} cm\\(^2\\)")
    
    latex = f"""
Câu {question_number}: Từ một khúc gỗ tròn hình trụ có đường kính bằng \\({d}\\,\\text{{cm}}\\), người ta xẻ thành một chiếc xà có tiết diện ngang là hình vuông và bốn miếng phụ được tô màu đen như hình vẽ. Diện tích tiết diện ngang lớn nhất là bao nhiêu \\(\\text{{cm}}^2\\)? (Kết quả làm tròn đến hàng đơn vị.)

{TIKZ_FIGURE}

{answer_lines[0]}

{answer_lines[1]}

{answer_lines[2]}

{answer_lines[3]}

Lời giải:

Khúc gỗ có tiết diện hình tròn đường kính \\({d}\\) cm $\\Rightarrow$ bán kính \\(R = {R:.0f}\\) cm.

1. Diện tích hình vuông ở giữa:

\\[
S_{{\\text{{vuông}}}} = \\frac{{{d}^2}}{2} = {S_square:.1f}\\,\\text{{cm}}^2
\\]



2. Tìm vị trí tối ưu của các miếng phụ:

Dựa theo hình vẽ, ta đặt hệ trục tọa độ Oxy vào tâm khúc gỗ. Xét một miếng phụ phía trên:

Gọi \\(\\alpha\\) là góc tạo bởi bán kính và trục hoành.

Kéo dài các cạnh miếng phụ ta có:

- Chiều dài: \\(AB = 2R\\cos\\alpha = {2*R:.0f}\\cos\\alpha\\) (giảm khi \\(\\alpha\\) tăng)

- Chiều rộng: \\(BC = R\\sin\\alpha - \\frac{{R}}{{\\sqrt{{2}}}} = {R:.0f}\\sin\\alpha - \\frac{{{R:.0f}}}{{\\sqrt{{2}}}}\\) (tăng khi \\(\\alpha\\) tăng, đến một giới hạn)

Để có diện tích phụ lớn nhất, ta cần cân bằng giữa chiều dài và chiều rộng.

Diện tích 1 miếng phụ: \\(AB \\cdot BC\\), tổng 4 miếng:
\\[
S_{{\\text{{phụ}}}} = 4 \\cdot AB \\cdot BC = 4 \\cdot {2*R:.0f}\\cos\\alpha \\cdot \\left({R:.0f}\\sin\\alpha - \\frac{{{R:.0f}}}{{\\sqrt{{2}}}} \\right)
\\]

Bằng phương pháp tối ưu hóa (lấy đạo hàm hàm diện tích theo góc \\(\\alpha\\)), ta tìm được góc tối ưu:

\\(\\alpha \\approx {optimal_alpha:.3f}\\) rad (\\(\\approx {optimal_alpha_deg:.1f}^\\circ\\)) cho diện tích 4 miếng phụ lớn nhất.

Với góc tối ưu này, ta có:
\\[
S_{{\\text{{phụ}}}} \\approx {S_auxiliary:.1f}\\,\\text{{cm}}^2
\\]

3. Tổng diện tích tiết diện ngang lớn nhất:

\\[
S = {S_square:.1f} + {S_auxiliary:.1f} = {S_total:.1f} \\Rightarrow {round(S_total)}\\,\\text{{cm}}^2
\\]

"""
    return latex


# Tạo câu hỏi format 2 (chỉ đề bài + lời giải, không có ABCD)
def generate_question_only(d, question_number=1):
    R = d / 2
    S_square = d ** 2 / 2  # Diện tích hình vuông nội tiếp

    # Dò alpha từ ~45.3° đến ~88.5° để tìm diện tích phụ lớn nhất (theo hình vẽ thực tế)
    max_area = -1
    optimal_alpha = 0
    optimal_alpha_deg = 0

    for i in range(790, 1550):  # alpha từ 0.79 đến 1.55 rad
        alpha = i / 1000
        AB = 2 * R * math.cos(alpha)  # chiều dài miếng phụ
        BC = R * math.sin(alpha) - (R / math.sqrt(2))  # chiều rộng miếng phụ

        if BC > 0:  # Chỉ xét khi chiều rộng dương (hợp lệ)
            area = 4 * AB * BC  # diện tích 4 miếng phụ
            if area > max_area:
                max_area = area
                optimal_alpha = alpha
                optimal_alpha_deg = math.degrees(alpha)

    S_auxiliary = max_area
    S_total = S_square + S_auxiliary

    latex = f"""
Câu {question_number}: Từ một khúc gỗ tròn hình trụ có đường kính bằng \\({d}\\,\\text{{cm}}\\), người ta xẻ thành một chiếc xà có tiết diện ngang là hình vuông và bốn miếng phụ được tô màu đen như hình vẽ. Diện tích tiết diện ngang lớn nhất là bao nhiêu \\(\\text{{cm}}^2\\)? (Kết quả làm tròn đến hàng đơn vị.)

{TIKZ_FIGURE}



Lời giải:

Khúc gỗ có tiết diện hình tròn đường kính \\({d}\\) cm $\\Rightarrow$ bán kính \\(R = {R:.0f}\\) cm.



1. Diện tích hình vuông ở giữa:

\\[
S_{{\\text{{vuông}}}} = \\frac{{{d}^2}}{2} = {S_square:.1f}\\,\\text{{cm}}^2
\\]



2. Tìm vị trí tối ưu của các miếng phụ:

Dựa theo hình vẽ, ta đặt hệ trục tọa độ Oxy vào tâm khúc gỗ. Xét một miếng phụ phía trên:

Gọi \\(\\alpha\\) là góc tạo bởi bán kính và trục hoành.

Kéo dài các cạnh miếng phụ ta có:

- Chiều dài: \\(AB = 2R\\cos\\alpha = {2*R:.0f}\\cos\\alpha\\) (giảm khi \\(\\alpha\\) tăng)

- Chiều rộng: \\(BC = R\\sin\\alpha - \\frac{{R}}{{\\sqrt{{2}}}} = {R:.0f}\\sin\\alpha - \\frac{{{R:.0f}}}{{\\sqrt{{2}}}}\\) (tăng khi \\(\\alpha\\) tăng, đến một giới hạn)

Để có diện tích phụ lớn nhất, ta cần cân bằng giữa chiều dài và chiều rộng.

Diện tích 1 miếng phụ: \\(AB \\cdot BC\\), tổng 4 miếng:
\\[
S_{{\\text{{phụ}}}} = 4 \\cdot AB \\cdot BC = 4 \\cdot {2*R:.0f}\\cos\\alpha \\cdot \\left({R:.0f}\\sin\\alpha - \\frac{{{R:.0f}}}{{\\sqrt{{2}}}} \\right)
\\]

Bằng phương pháp tối ưu hóa (lấy đạo hàm hàm diện tích theo góc \\(\\alpha\\)), ta tìm được góc tối ưu:

\\(\\alpha \\approx {optimal_alpha:.3f}\\) rad (\\(\\approx {optimal_alpha_deg:.1f}^\\circ\\)) cho diện tích 4 miếng phụ lớn nhất.

Với góc tối ưu này, ta có:
\\[
S_{{\\text{{phụ}}}} \\approx {S_auxiliary:.1f}\\,\\text{{cm}}^2
\\]



3. Tổng diện tích tiết diện ngang lớn nhất:

\\[
S = {S_square:.1f} + {S_auxiliary:.1f} = {S_total:.1f} \\Rightarrow {round(S_total)}\\,\\text{{cm}}^2
\\]



"""
    return latex


# Tính toán đáp án cho format 2
def calculate_answer(d):
    R = d / 2
    S_square = d ** 2 / 2  # Diện tích hình vuông nội tiếp

    # Dò alpha từ ~45.3° đến ~88.5° để tìm diện tích phụ lớn nhất
    max_area = -1
    
    for i in range(790, 1550):  # alpha từ 0.79 đến 1.55 rad
        alpha = i / 1000
        AB = 2 * R * math.cos(alpha)  # chiều dài miếng phụ
        BC = R * math.sin(alpha) - (R / math.sqrt(2))  # chiều rộng miếng phụ

        if BC > 0:  # Chỉ xét khi chiều rộng dương (hợp lệ)
            area = 4 * AB * BC  # diện tích 4 miếng phụ
            if area > max_area:
                max_area = area

    S_auxiliary = max_area
    S_total = S_square + S_auxiliary
    return round(S_total)


# Tạo nhiều câu hỏi
def generate_multiple_questions(num_questions, format_type=1):
    # Danh sách các đường kính khác nhau
    diameters = [16, 18, 20, 22, 24, 26, 28, 30, 32, 34]
    
    # Header LaTeX
    latex_content = """\\documentclass[12pt]{article}
\\usepackage{amsmath}
\\usepackage{geometry}
\\geometry{a4paper, margin=1in}
\\usepackage{fontspec}
\\setmainfont{Times New Roman}
\\usepackage{tikz}
\\usetikzlibrary{intersections}

\\begin{document}

"""
    
    if format_type == 1:
        # Format 1: ABCD + lời giải chi tiết
        for i in range(num_questions):
            d = diameters[i % len(diameters)]
            question_latex = generate_latex_solution(d, i + 1)
            latex_content += question_latex
            
            if i < num_questions - 1:
                latex_content += "\\newpage\n\n"
    
    else:
        # Format 2: Chỉ đề bài + đáp án cuối
        answers = []
        
        # Tạo các câu hỏi
        for i in range(num_questions):
            d = diameters[i % len(diameters)]
            question_latex = generate_question_only(d, i + 1)
            latex_content += question_latex
            
            # Tính đáp án
            answer = calculate_answer(d)
            answers.append(answer)
        
        # Thêm phần đáp án cuối
        latex_content += "\n\nĐÁP ÁN:\n\n"
        
        for i, answer in enumerate(answers):
            latex_content += f"Câu {i + 1}: {answer} cm\\(^2\\)\n\n"
    
    # Footer LaTeX
    latex_content += "\\end{document}\n"
    
    return latex_content


# Lưu vào file .tex
def save_latex_to_file(content, filename="solution.tex"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


# Biên dịch .tex thành .pdf bằng xelatex
def compile_latex(filename="solution.tex"):
    try:
        subprocess.run(["xelatex", filename], check=True)
        print("✅ Biên dịch thành công. Đã tạo file PDF.")
    except subprocess.CalledProcessError as e:
        print("❌ Lỗi khi biên dịch LaTeX:", e)
    except FileNotFoundError:
        print("❌ Không tìm thấy `xelatex`. Hãy cài TeX Live hoặc MikTeX và đảm bảo nó có trong PATH.")


# === Chạy toàn bộ quy trình ===
if __name__ == "__main__":
    # Kiểm tra tham số dòng lệnh
    num_questions = 1  # Mặc định 1 câu
    format_type = 1    # Mặc định format 1
    
    if len(sys.argv) > 1:
        try:
            num_questions = int(sys.argv[1])
            if num_questions <= 0:
                print("❌ Số câu hỏi phải là số dương.")
                sys.exit(1)
        except ValueError:
            print("❌ Tham số đầu tiên phải là số nguyên (số câu hỏi).")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            format_type = int(sys.argv[2])
            if format_type not in [1, 2]:
                print("❌ Format phải là 1 hoặc 2.")
                print("   Format 1: ABCD + lời giải chi tiết")
                print("   Format 2: Chỉ đề bài + đáp án cuối")
                sys.exit(1)
        except ValueError:
            print("❌ Tham số thứ hai phải là số nguyên (format 1 hoặc 2).")
            sys.exit(1)
    
    format_name = "ABCD + lời giải" if format_type == 1 else "đề bài + đáp án cuối"
    print(f"🔄 Đang tạo {num_questions} câu hỏi (Format {format_type}: {format_name})...")
    
    # Tạo nội dung LaTeX
    latex_code = generate_multiple_questions(num_questions, format_type)
    
    # Lưu và biên dịch
    save_latex_to_file(latex_code)
    compile_latex()
    
    print(f"✅ Đã tạo xong {num_questions} câu hỏi trong file solution.pdf")
