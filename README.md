# 📚 Formula LaTeX - Bộ Tạo Câu Hỏi Toán Học

Dự án tạo câu hỏi trắc nghiệm toán học bằng Python và LaTeX với hỗ trợ tiếng Việt hoàn chỉnh.

## 🎯 Tổng quan

Bộ công cụ này giúp giáo viên và học sinh tạo ra các bài kiểm tra toán học chuyên nghiệp với:
- Câu hỏi được tạo tự động
- Đáp án chi tiết
- Định dạng LaTeX chuẩn
- Hỗ trợ tiếng Việt

## 📁 Cấu trúc thư mục

```
FomularLatex/
├── 📂 asymptote_questions/          # Module câu hỏi tiệm cận
│   ├── asymptote_mc.py             # Generator câu hỏi tiệm cận (hoàn chỉnh)
│   ├── test_asymptote_fixed.py     # Test cases
│   └── README.md                   # Hướng dẫn module
├── 📂 asymptotic_advanced/         # Module tiệm cận nâng cao
│   ├── asymptotic_advanced.py      # Generator câu hỏi nâng cao
│   ├── asymptotic_advanced_ABCD.py # Version ABCD
│   └── README_CHAT_CONTEXT.md      # Context phát triển
├── 📂 true_false_triangle/         # Module câu hỏi tam giác đúng/sai
│   ├── true_false_triangle_questions.py  # Generator cơ bản
│   ├── true_false_triangle_ABCD.py       # Version ABCD
│   └── README.md                         # Hướng dẫn module
├── 📂 base_template/              # Template cơ sở
│   ├── math_question_base.py      # Template chính
│   └── README.md                  # Hướng dẫn sử dụng template
├── requirements.txt               # Dependencies
└── README.md                     # Tài liệu này
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

### 2. Tạo câu hỏi tiệm cận

```bash
cd asymptote_questions
python3 asymptote_mc.py 5
xelatex asymptote_mc_questions.tex
```

### 3. Tạo câu hỏi tiệm cận nâng cao

```bash
cd asymptotic_advanced
python3 asymptotic_advanced.py 10
xelatex asymptotic_advanced_questions_generated.tex
```

### 4. Tạo câu hỏi tam giác đúng/sai

```bash
cd true_false_triangle
python3 true_false_triangle_questions.py 8
xelatex true_false_triangle_questions.tex
```

## 📚 Các module có sẵn

### 🔢 Asymptote Questions
- **Vị trí**: `asymptote_questions/`
- **Chức năng**: Tạo câu hỏi về tiệm cận xiên
- **Định dạng**: Trắc nghiệm 4 đáp án
- **Trạng thái**: ✅ Hoàn chỉnh

### 📈 Asymptotic Advanced
- **Vị trí**: `asymptotic_advanced/`
- **Chức năng**: Câu hỏi tiệm cận nâng cao
- **Định dạng**: Trắc nghiệm và tự luận
- **Trạng thái**: ✅ Hoàn chỉnh

### 📐 True/False Triangle
- **Vị trí**: `true_false_triangle/`
- **Chức năng**: Câu hỏi đúng/sai về tam giác
- **Định dạng**: Đúng/Sai và ABCD
- **Trạng thái**: ✅ Hoàn chỉnh

### 🏗️ Base Template
- **Vị trí**: `base_template/`
- **Chức năng**: Template để tạo module mới
- **Sử dụng**: Framework phát triển
- **Trạng thái**: ✅ Sẵn sàng

## ✨ Tính năng nổi bật

- 🇻🇳 **Hỗ trợ tiếng Việt** hoàn chỉnh với polyglossia
- 📄 **LaTeX chuyên nghiệp** với Times New Roman
- 🔢 **Tính toán chính xác** với Fraction và SymPy
- 🎯 **Framework mở rộng** cho nhiều dạng bài
- 📱 **Command line** dễ sử dụng
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

### Câu hỏi tiệm cận
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

### Bước 1: Copy template
```bash
cp base_template/math_question_base.py my_new_module.py
```

### Bước 2: Tùy chỉnh
- Chỉnh sửa hàm `generate_question()`
- Cập nhật logic tạo đáp án
- Thêm lời giải

### Bước 3: Test và chạy
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

## 👨‍💻 Tác giả

**quytttb** - [GitHub](https://github.com/quytttb)

## 🙏 Cảm ơn

Cảm ơn cộng đồng LaTeX và Python Việt Nam đã hỗ trợ phát triển dự án này!

---

*Dự án này giúp giáo viên tạo câu hỏi trắc nghiệm toán học chuyên nghiệp một cách nhanh chóng! 🎓*
