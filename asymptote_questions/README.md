# Asymptote Multiple Choice Questions Generator

## Mô tả
Công cụ tự động tạo câu hỏi trắc nghiệm về tiệm cận xiên của hàm số hữu tỷ.

## Tính năng
- Tự động tạo hàm số hữu tỷ có tiệm cận xiên
- Tính toán tiệm cận xiên bằng công thức: y = (A/D)x + (BD-AE)/D²
- Tạo đáp án sai dựa trên các lỗi thường gặp
- Xuất ra file LaTeX hoàn chỉnh với lời giải chi tiết
- Hỗ trợ tiếng Việt với XeLaTeX

## Cách sử dụng

### Chạy với số câu hỏi mặc định (4 câu):
```bash
python3 asymptote_mc.py
```

### Chạy với số câu hỏi tùy chỉnh:
```bash
python3 asymptote_mc.py 10
```

### Compile file LaTeX:
```bash
xelatex asymptote_mc_questions.tex
```

## Cấu trúc file

- `asymptote_mc.py` - Script Python chính
- `asymptote_mc_questions.tex` - File LaTeX được tạo ra
- `asymptote_mc_questions.pdf` - File PDF kết quả

## Yêu cầu hệ thống
- Python 3.x
- XeLaTeX (để compile file LaTeX)
- Font Times New Roman

## Ví dụ câu hỏi
Cho hàm số y = (x² + 3x - 2)/(x - 1).
Phương trình đường tiệm cận xiên của đồ thị hàm số này là:

A. y = x + 4 + 3/(x - 1)
B. y = 2x + 4 + 1/(x - 1)  
C. y = 3x + 2 + 3/(x - 1)
D. y = x + 2 + 1/(x - 1)

## Lời giải tự động
Mỗi câu hỏi đều có lời giải chi tiết bao gồm:
1. Phân tích hàm số thành dạng y = mx + b + R/(dx + e)
2. Tính giới hạn để chứng minh tiệm cận xiên
3. Kết luận phương trình tiệm cận xiên
