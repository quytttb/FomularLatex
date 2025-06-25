# True/False Triangle Questions Generator

Bộ sinh câu hỏi đúng/sai về tam giác trong không gian 3D.

## 📋 Mô tả

Hệ thống sinh tự động các câu hỏi đúng/sai về:
- Chân đường vuông góc từ đỉnh xuống cạnh đối
- Độ dài đường cao trong tam giác
- Góc trong tam giác 
- Tính đồng phẳng của 4 điểm

## 🚀 Cách sử dụng

### Sinh câu hỏi mặc định (3 câu):
```bash
python3 true_false_triangle_questions.py
```

### Sinh số câu hỏi tùy chỉnh:
```bash
python3 true_false_triangle_questions.py 10
```

### Compile LaTeX thành PDF:
```bash
xelatex true_false_triangle_questions.tex
```

## 📁 Các file chính

- **`true_false_triangle_questions.py`**: Script chính sinh câu hỏi
- **`true_false_triangle_questions.tex`**: File LaTeX được sinh ra
- **`true_false_triangle_questions.pdf`**: File PDF kết quả
- **`true_false_triangle_solver.tex`**: Mô tả các pattern tam giác

## ⚙️ Yêu cầu hệ thống

- Python 3.6+
- XeLaTeX (để compile PDF)
- Font Times New Roman

### Cài đặt XeLaTeX trên Ubuntu/Debian:
```bash
sudo apt-get install texlive-xetex texlive-latex-extra
```

## 📊 Tính năng

- ✅ **100% tam giác hợp lệ** - không có tam giác suy biến
- ✅ **4 pattern đa dạng** - tạo tam giác với tỷ lệ cạnh khác nhau
- ✅ **Hoán vị tọa độ** - tăng tính đa dạng
- ✅ **Tính toán chính xác** - sử dụng fractions cho độ chính xác cao
- ✅ **Hỗ trợ tiếng Việt** - đầy đủ trong LaTeX
- ✅ **Tự động tạo PDF** - sẵn sàng sử dụng

## 🎯 Ví dụ đầu ra

File PDF sẽ chứa các câu hỏi dạng:

> **Câu 1:** Cho △ABC với A(-2, -3, -1), B(-4, -3, 2), C(2, -4, 9). Chọn các lựa chọn đúng:
> 
> a) Tọa độ chân đường vuông góc kẻ từ A xuống BC = D(-4, -4, 2).
> 
> b) Độ dài đường cao kẻ từ B trong △ABC = 3.48.
> 
> c) △ABC có góc ∠ABC = 100.6°.
> 
> d) Bốn điểm A, B, C, D(-2; 1; -3m + 8) đồng phẳng khi m = 24.3.

## 📝 Phiên bản

- **Version**: 1.0 (Final)
- **Trạng thái**: Hoàn thiện và ổn định
- **Ngày cập nhật**: 22/06/2025

- Python 3.x
- XeLaTeX with Vietnamese support
- Times New Roman font
