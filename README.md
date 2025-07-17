# 📚 Formula LaTeX - Bộ Tạo Câu Hỏi Toán Học

Dự án tạo câu hỏi trắc nghiệm toán học bằng Python và LaTeX với hỗ trợ tiếng Việt hoàn chỉnh.

## 🎯 Tổng quan

Bộ công cụ này giúp giáo viên và học sinh tạo ra các bài kiểm tra toán học chuyên nghiệp với:
- Câu hỏi được tạo tự động
- Đáp án chi tiết
- Định dạng LaTeX chuẩn
- Hỗ trợ tiếng Việt

## 📁 Cấu trúc thư mục (cập nhật kiến trúc mới)

```
FomularLatex/
├── 📂 src/                         # Chứa các script sinh câu hỏi cũ
│   ├── asymptote_mc.py             # Generator câu hỏi tiệm cận
│   ├── asymptotic_advanced.py      # Generator câu hỏi nâng cao
│   ├── true_false_triangle_questions.py  # Generator tam giác đúng/sai
│   └── ... (các file khác)
├── 📂 base_template/ ⭐             # NEW: Clean Architecture Framework
│   ├── main_runner.py              # CLI chính với argparse
│   ├── base_optimization_question.py    # Abstract base class
│   ├── latex_document_builder.py  # LaTeX document builder
│   ├── question_type_loader.py     # Dynamic module loader
│   ├── question_manager.py         # Question generation manager
│   ├── extremum_from_tikz.py       # Câu hỏi cực trị từ đồ thị
│   └── tikz_figure_library.py      # Thư viện TikZ figures
├── requirements.txt                # Dependencies
└── README.md                       # Tài liệu này
```

## 🚀 Bắt đầu nhanh

### 1. Cài đặt môi trường

```bash
# Clone repository
git clone https://github.com/quytttb/FomularLatex.git
cd FomularLatex

# Cài đặt dependencies (nếu cần)
pip install -r requirements.txt
```

### 2. Sử dụng CLI mới (Khuyến nghị) ⭐

```bash
# Di chuyển đến thư mục base_template
cd base_template

# Sinh 5 câu hỏi, format 1 (đáp án ngay sau câu)
python3 main_runner.py 5 1

# Sinh 10 câu hỏi, format 2 (đáp án ở cuối), verbose mode
python3 main_runner.py 10 2 --verbose

# Tùy chỉnh output file và title
python3 main_runner.py 5 1 -o my_test.tex -t "Bài Kiểm Tra Giữa Kỳ"

# Xem hướng dẫn đầy đủ
python3 main_runner.py --help

# Biên dịch file LaTeX
xelatex optimization_questions.tex
```

### 3. Sử dụng scripts cũ (Legacy)

```bash
# Sinh câu hỏi tiệm cận (5 câu)
python3 src/asymptote_mc.py 5
xelatex asymptote_mc_questions.tex
python3 src/asymptote_mc.py 5
xelatex asymptote_mc_questions.tex

# Sinh câu hỏi tiệm cận nâng cao (10 câu)
python3 src/asymptotic_advanced.py 10
xelatex asymptotic_advanced_questions_generated.tex

# Sinh câu hỏi tam giác đúng/sai (8 câu)
python3 src/true_false_triangle_questions.py 8
xelatex true_false_triangle_questions.tex
```

## 📚 Các module có sẵn

### 🎯 NEW: Clean Architecture Framework ⭐
- **Vị trí**: `base_template/`
- **CLI**: `python3 main_runner.py --help`
- **Chức năng**: 
  - CLI chuyên nghiệp với argparse
  - Timeout protection và retry logic
  - Clean architecture với separation of concerns
  - Hỗ trợ multiple question types
- **Question Types**:
  - ✅ ExtremumFromTikz (Cực trị từ đồ thị TikZ)
  - 🔄 Dễ dàng thêm types mới
- **Trạng thái**: ✅ Production ready

### 🔢 Legacy Modules
#### Asymptote Questions
- **Vị trí**: `src/asymptote_mc.py`
- **Chức năng**: Tạo câu hỏi về tiệm cận xiên
- **Định dạng**: Trắc nghiệm 4 đáp án
- **Trạng thái**: ✅ Hoàn chỉnh

### 📈 Asymptotic Advanced
- **Vị trí**: `src/asymptotic_advanced.py`
- **Chức năng**: Câu hỏi tiệm cận nâng cao
- **Trạng thái**: ✅ Hoàn chỉnh

### 🔺 True/False Triangle
- **Vị trí**: `src/true_false_triangle_questions.py`
- **Chức năng**: Câu hỏi tam giác đúng/sai
- **Trạng thái**: ✅ Hoàn chỉnh

### 🏗️ Base Template (Legacy)
- **Vị trí**: `base_template/base_optimization_question.py`
- **Chức năng**: Abstract base class (đã refactor)
- **Sử dụng**: Framework phát triển cũ
- **Trạng thái**: ✅ Deprecated (Sử dụng new architecture)

## ✨ Tính năng nổi bật

### 🆕 New Architecture Features ⭐
- 🎯 **CLI chuyên nghiệp** với argparse và help
- ⏱️ **Timeout protection** tránh hang process  
- 🔄 **Retry logic** xử lý lỗi tự động
- 📊 **Statistics reporting** chi tiết quá trình
- 🔧 **Clean Architecture** dễ maintain và extend
- 🎛️ **Verbose mode** cho debugging
- 📝 **Custom output** file và title

### 🌟 Core Features
- 🇻🇳 **Hỗ trợ tiếng Việt** hoàn chỉnh với polyglossia
- 📄 **LaTeX chuyên nghiệp** với Times New Roman và author="dev"
- 🔢 **Tính toán chính xác** với Fraction và SymPy
- 🎯 **Framework mở rộng** cho nhiều dạng bài
- 🎲 **Random seed** để tạo bài khác nhau
- 📊 **Multiple choice** và **True/False**
- 🔍 **Lời giải chi tiết** tự động

## 🛠️ Yêu cầu hệ thống

### Python
- Python 3.6+ 
- Không cần thư viện bên ngoài (chỉ dùng built-in)

### LaTeX
- XeLaTeX để compile PDF
- Font Times New Roman

### Cài đặt XeLaTeX

```bash
# Ubuntu/Debian
sudo apt-get install texlive-xetex texlive-latex-extra texlive-fonts-extra

# macOS (với Homebrew)
brew install mactex-no-gui

# Windows
# Tải và cài đặt MiKTeX: https://miktex.org/
# Hoặc TeX Live: https://www.tug.org/texlive/
```

## 📝 Ví dụ output

### CLI Help
```bash
$ python3 main_runner.py --help
usage: main_runner.py [-h] [-o OUTPUT] [-t TITLE] [-v] num_questions format

🎯 Tạo câu hỏi tối ưu hóa với LaTeX

positional arguments:
  num_questions         Số lượng câu hỏi cần tạo (vd: 5, 10)
  format               Định dạng đáp án: 1=đáp án ngay sau câu, 2=đáp án ở cuối

options:
  -h, --help           show this help message and exit
  -o OUTPUT, --output OUTPUT
                       Tên file đầu ra (mặc định: optimization_questions.tex)
  -t TITLE, --title TITLE
                       Tiêu đề tài liệu (mặc định: Câu hỏi Tối ưu hóa)
  -v, --verbose        In chi tiết quá trình tạo câu hỏi

Examples:
  python3 main_runner.py 5 1                    # 5 câu, đáp án sau mỗi câu
  python3 main_runner.py 10 2 -v                # 10 câu, đáp án cuối, verbose
  python3 main_runner.py 3 1 -o test.tex -t "Kiểm tra"  # Custom file và title
```

### Verbose Output
```bash
$ python3 main_runner.py 2 1 -v
✅ Đã load thành công: ExtremumFromTikz từ extremum_from_tikz
📚 Tổng cộng đã load 1 dạng toán
📋 Có 1 loại câu hỏi khả dụng
Đang tạo câu hỏi 1
✅ Đã tạo thành công câu hỏi 1 (loại: ExtremumFromTikzQuestion)
Đang tạo câu hỏi 2
✅ Đã tạo thành công câu hỏi 2 (loại: ExtremumFromTikzQuestion)
📊 Thống kê sinh câu hỏi:
   - Tổng số sinh thành công: 2
   - Tổng số thất bại: 0
   - Số lần retry: 0
   - Số lần timeout: 0
✅ Đã tạo thành công optimization_questions.tex với 2 câu hỏi
📄 Biên dịch bằng: xelatex optimization_questions.tex
📋 Format: 1 (đáp án ngay sau câu hỏi)
```

### Câu hỏi cực trị từ đồ thị (NEW)
```latex
Câu 1: Cho đồ thị hàm số y=f(x) có đồ thị như hình vẽ dưới đây:

[TikZ graph showing function with extrema]

Dựa vào đồ thị, hãy xác định giá trị cực đại của hàm số.

A. 1
*B. 2
C. 3  
D. 4

Lời giải:
Từ đồ thị ta thấy hàm số đạt cực đại tại điểm (-1, 1)...
```

### Câu hỏi tiệm cận (Legacy)
```latex
Câu 1: Cho hàm số $y = \frac{x^2 + 3x - 2}{x - 1}$.
Phương trình đường tiệm cận xiên của đồ thị hàm số này là:

A. $y = x + 4 + \frac{2}{x - 1}$
B. $y = x + 2 + \frac{1}{x - 1}$
C. $y = 2x + 4 + \frac{1}{x - 1}$
*D. $y = x + 4 + \frac{2}{x - 1}$

Lời giải:
Thực hiện phép chia đa thức...
```

### Câu hỏi tam giác đúng/sai
```latex
Cho tam giác ABC với a = 5, b = 7, c = 8.

a) Tam giác ABC là tam giác nhọn. (Đúng)
b) Diện tích tam giác bằng 10√6. (Đúng)
c) Bán kính đường tròn ngoại tiếp bằng 7√6/6. (Đúng)
d) Chu vi tam giác bằng 21. (Sai)
```

## 🚀 Phát triển module mới

### Phương pháp mới (Clean Architecture) ⭐

#### Bước 1: Tạo question type mới
```python
# Tạo file: my_new_question.py trong base_template/
from base_optimization_question import BaseOptimizationQuestion
from typing import Dict, Any, List

class MyNewQuestion(BaseOptimizationQuestion):
    def generate_parameters(self) -> Dict[str, Any]:
        return {"param1": random.randint(1, 10)}
    
    def calculate_answer(self) -> str:
        return str(self.parameters["param1"] * 2)
    
    def generate_wrong_answers(self) -> List[str]:
        correct = int(self.correct_answer)
        return [str(correct + 1), str(correct - 1), str(correct + 2)]
    
    def generate_question_text(self) -> str:
        return f"Tính 2 × {self.parameters['param1']} = ?"
    
    def generate_solution(self) -> str:
        return f"2 × {self.parameters['param1']} = {self.correct_answer}"
```

#### Bước 2: Test và sử dụng
```bash
# Tự động được load bởi QuestionTypeLoader
python3 main_runner.py 5 1 -v
xelatex optimization_questions.tex
```

### Phương pháp cũ (Legacy)

#### Bước 1: Copy template
```bash
cp base_template/math_question_base.py my_new_module.py
```

#### Bước 2: Tùy chỉnh
- Chỉnh sửa hàm `generate_question()`
- Cập nhật logic tạo đáp án
- Thêm lời giải

#### Bước 3: Test và chạy
```bash
python3 my_new_module.py 5
xelatex output.tex
```

## 🤝 Đóng góp

1. Fork repository
2. Tạo branch mới: `git checkout -b feature-ten-tinh-nang`
3. Commit thay đổi: `git commit -m 'Thêm tính năng mới'`
4. Push: `git push origin feature-ten-tinh-nang`
5. Tạo Pull Request

## 📜 License

Dự án được phát hành dưới MIT License. Xem file LICENSE để biết thêm chi tiết.


## 🙏 Cảm ơn

Cảm ơn cộng đồng LaTeX và Python Việt Nam đã hỗ trợ phát triển dự án này!

---
