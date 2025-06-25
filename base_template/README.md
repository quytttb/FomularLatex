# Math Question Generator Base Template

Template cơ sở để tạo câu hỏi trắc nghiệm toán học bằng tiếng Việt với LaTeX.

## Tính năng có sẵn

### 🔢 Utilities toán học
- `format_fraction_latex()` - Format phân số cho LaTeX
- `format_coefficient()` - Format hệ số với dấu và biến
- `format_polynomial()` - Format đa thức
- `build_expression_dynamically()` - Xây dựng biểu thức động
- `format_with_parentheses()` - Format số âm với ngoặc

### 📄 LaTeX Document
- Hỗ trợ tiếng Việt với polyglossia
- Font Times New Roman
- Layout A4 với margin 1 inch
- Các package toán học cần thiết

### 🎯 Framework tạo câu hỏi
- Class `MathQuestionGenerator` cơ sở
- Tự động xáo trộn đáp án
- Đánh dấu đáp án đúng bằng `*`
- Template lời giải chi tiết

## Cách sử dụng

### Bước 1: Copy template
```bash
cp math_question_base.py my_new_questions.py
```

### Bước 2: Tạo class generator của bạn
```python
class MyQuestionGenerator(MathQuestionGenerator):
    def __init__(self):
        super().__init__("Tên dạng bài của bạn")
    
    def generate_parameters(self):
        # Tạo các tham số ngẫu nhiên
        return {
            'a': random.randint(1, 10),
            'b': random.randint(-5, 5)
        }
    
    def calculate_solution(self, params):
        # Tính đáp án đúng
        return params['a'] * params['b']
    
    def generate_wrong_answers(self, correct_answer, params):
        # Tạo 3 đáp án sai
        return [
            correct_answer + 1,
            correct_answer - 1, 
            params['a'] + params['b']  # Lỗi thường gặp
        ]
    
    def format_question_stem(self, params):
        # Format câu hỏi
        return f"Tính tích {params['a']} × {params['b']} = ?"
    
    def format_answer_choice(self, answer):
        # Format đáp án (nếu cần đặc biệt)
        return str(answer)
    
    def generate_detailed_solution(self, params, correct_answer):
        # Tạo lời giải chi tiết
        return f\"\"\"\\textbf{{Giải:}}

Ta có: {params['a']} × {params['b']} = {correct_answer}\"\"\"
```

### Bước 3: Thêm main function
```python
if __name__ == "__main__":
    main_template(MyQuestionGenerator, "my_questions.tex", 5)
```

### Bước 4: Chạy và compile
```bash
# Tạo 10 câu hỏi
python3 my_new_questions.py 10

# Compile thành PDF
xelatex my_questions.tex
```

## Ví dụ có sẵn

File `asymptote_mc.py` là một ví dụ hoàn chỉnh sử dụng template này cho bài toán tiệm cận xiên.

## Các utilities hữu ích

### Format phân số
```python
format_fraction_latex(3, 4)  # "\\frac{3}{4}"
format_fraction_latex(5, 1)  # "5"
format_fraction_latex(0, 3)  # "0"
```

### Format đa thức
```python
format_polynomial([1, -2, 3])  # "x^{2} - 2x + 3"
format_polynomial([2, 0, -1])  # "2x^{2} - 1"
```

### Xây dựng biểu thức động
```python
slope = Fraction(2, 3)
intercept = Fraction(-1, 2)
R = Fraction(5, 1)

terms = [
    (slope, "x", slope != 0),
    (intercept, "", intercept != 0), 
    (R, "/(x+1)", R != 0)
]

result = build_expression_dynamically(terms)
# "\\frac{2}{3}x - \\frac{1}{2} + \\frac{5}{x+1}"
```

## Cấu trúc output

### File LaTeX được tạo:
- Header với các package cần thiết
- Title section tự động
- Câu hỏi được đánh số tự động
- Đáp án đúng được đánh dấu `*`
- Lời giải chi tiết

### Format câu hỏi:
```
Câu 1: [Đề bài]

*A. [Đáp án đúng]
B. [Đáp án sai 1]  
C. [Đáp án sai 2]
D. [Đáp án sai 3]

Lời giải:
[Lời giải chi tiết]
```

## Tips và best practices

1. **Tạo đáp án sai thông minh**: Dựa trên lỗi học sinh thường mắc
2. **Sử dụng Fraction**: Để tính toán chính xác với phân số
3. **Kiểm tra edge cases**: Hệ số = 0, = 1, = -1
4. **Format đẹp**: Sử dụng các utility có sẵn cho LaTeX
5. **Test kỹ**: Chạy nhiều lần để đảm bảo logic đúng

## Hỗ trợ

- 🐍 Python 3.6+
- 📦 LaTeX với XeLaTeX
- 🔤 Font Times New Roman
- 🌏 Hỗ trợ tiếng Việt hoàn toàn

Template này giúp bạn tiết kiệm thời gian và tập trung vào logic toán học thay vì formatting!
