# 🏗️ Base Architecture - Formula LaTeX

## 📋 Tổng quan

Base architecture này cung cấp một framework mạnh mẽ và có thể mở rộng để tạo các loại câu hỏi toán học khác nhau. Thay vì copy-paste code, các question generators sẽ kế thừa từ base classes.

## 🎯 Kiến trúc

### Base Classes

```
base/
├── question_generator.py      # Abstract base classes
├── math_utils.py             # Math formatting utilities  
├── latex_formatter.py        # LaTeX document formatting
└── constants.py              # Configuration constants
```

#### QuestionGenerator (Abstract)
- **Mục đích**: Base class cho tất cả question generators
- **Abstract methods**: `generate_parameters()`, `calculate_solution()`, `format_question_text()`, `generate_solution_text()`

#### MultipleChoiceGenerator (Abstract) 
- **Kế thừa**: QuestionGenerator
- **Thêm**: Logic cho câu hỏi trắc nghiệm ABCD
- **Abstract methods**: `generate_wrong_answers()`, `format_answer_choice()`

#### TrueFalseGenerator (Abstract)
- **Kế thừa**: QuestionGenerator  
- **Thêm**: Logic cho câu hỏi đúng/sai
- **Abstract methods**: `generate_statements()`

### Implementations

```
generators/
├── asymptote_generator.py    # Câu hỏi tiệm cận
├── triangle_generator.py     # Câu hỏi tam giác
└── ...                      # Các generators khác
```

## 🚀 Cách sử dụng

### 1. Tạo generator mới

```python
from base import MultipleChoiceGenerator

class MyGenerator(MultipleChoiceGenerator):
    def __init__(self):
        super().__init__("My Question Type")
    
    def generate_parameters(self):
        # Tạo parameters ngẫu nhiên
        return {"a": random.randint(1, 10)}
    
    def calculate_solution(self, params):
        # Tính đáp án đúng
        return params["a"] * 2
    
    def format_question_text(self, params):
        # Format câu hỏi
        return f"Tính 2 × {params['a']} = ?"
    
    def generate_wrong_answers(self, correct, params):
        # Tạo đáp án sai
        return [correct + 1, correct - 1, correct * 2]
    
    def format_answer_choice(self, answer):
        # Format lựa chọn
        return str(answer)
    
    def generate_solution_text(self, params, answer):
        # Tạo lời giải
        return f"Ta có: 2 × {params['a']} = {answer}"
```

### 2. Sử dụng generator

```python
from base import generate_latex_document
from generators.my_generator import MyGenerator

# Tạo generator
gen = MyGenerator()

# Tạo document với 5 câu hỏi
document = generate_latex_document(gen, 5, "output.tex")
```

### 3. Demo có sẵn

```bash
# Chạy demo
python demo_base_architecture.py 5

# Compile LaTeX
xelatex demo_asymptote_questions.tex
```

## 🔧 Utilities có sẵn

### Math Utils
- `format_fraction_latex()`: Format phân số
- `format_coefficient()`: Format hệ số với biến
- `format_polynomial()`: Format đa thức
- `standardize_math_expression()`: Chuẩn hóa biểu thức

### LaTeX Formatter
- `format_multiple_choice_question()`: Format câu hỏi ABCD
- `format_true_false_question()`: Format câu hỏi đúng/sai
- `create_complete_document()`: Tạo document hoàn chỉnh

### Constants
- `QuestionConfig`: Các constants như ranges, defaults

## ✨ Ưu điểm

1. **Không trùng lặp code**: Utilities được tái sử dụng
2. **Dễ mở rộng**: Chỉ cần implement abstract methods  
3. **Nhất quán**: Format và style đồng nhất
4. **Type safety**: Type hints đầy đủ
5. **Maintainable**: Dễ maintain và debug

## 🔄 Migration từ code cũ

1. **Copy logic**: Copy logic tính toán từ file cũ
2. **Implement methods**: Implement các abstract methods
3. **Test**: So sánh output với file cũ
4. **Replace**: Thay thế file cũ bằng generator mới

## 📝 Next Steps

1. Migrate `asymptote_mc.py` → `AsymptoteGenerator`
2. Migrate `true_false_triangle_*.py` → `TriangleGenerator`  
3. Migrate `asymptotic_advanced_*.py` → `AdvancedAsymptoteGenerator`
4. Tạo generators mới cho question types khác
