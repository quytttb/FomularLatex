# Ngữ Cảnh Chat: Generator Câu Hỏi Tiệm Cận Nâng Cao

## Mục tiêu
Tạo file Python để generate các câu hỏi về tiệm cận nâng cao với format mệnh đề đúng/sai dựa trên:
- **File solver.tex**: Cách giải và trình bày lời giải
- **File asymptote_mc.py**: Format trình bày và cách tạo đáp án sai

## Quá trình phát triển

### 1. Tạo file Python ban đầu
- Tạo `asymptotic_advanced.py` với 4 dạng câu hỏi:
  - **Câu 1**: Tiệm cận đứng và ngang với tham số m, n
  - **Câu 2**: Diện tích hình chữ nhật tạo bởi tiệm cận
  - **Câu 3**: Số lượng tiệm cận (2 tiệm cận đứng, 3 tiệm cận)
  - **Câu 4**: Tiệm cận xiên

### 2. Thêm logic mệnh đề đúng/sai
- Tạo đáp án sai bằng cách biến đổi hệ số và giá trị
- Random choice giữa mệnh đề đúng/sai cho tất cả câu
- **Format theo true_false_triangle**: Câu a), b), c), d) với dấu `*` cho câu đúng

### 3. Hệ thống chuẩn hóa biểu thức toán học
- **Hàm `standardize_math_expression()`** với 11 quy tắc chuẩn hóa:
  1. Hệ số 1 và -1: `1m → m`, `-1m → -m`
  2. Loại bỏ phép tính với 0: `expr + 0 → expr`
  3. Dấu ngoặc cho số âm: `-2 × 3 → (-2) × 3`
  4. Chuẩn hóa dấu kép: `+ -5 → - 5`, `--` → `+`
  5. Loại bỏ dấu + thừa: `= +4 → = 4`
  6. Chuẩn hóa LaTeX: `\frac{+4 → \frac{4`
  7. Hệ số 1 trong phân số: `\frac{1m}{ → \frac{m}{`
  8. Số mũ đơn giản: `x^{1} → x`
  9. Phép nhân thừa với 1: `1⋅expr → expr`
  10. **Số thập phân**: `4.00 → 4`, `5.50 → 5.5`
  11. Format LaTeX: `x{2} → x^{2}`, `2x{2} → 2x^{2}`

### 4. Sửa format và cấu trúc câu hỏi
- **Cấu trúc theo true_false**: 
  - Tiêu đề: "Câu X: Chọn các mệnh đề đúng:"
  - 4 mệnh đề a), b), c), d) với dấu `*` cho câu đúng
  - Phần "Lời giải:" tập trung ở cuối
  - Kết luận "Đáp án đúng: a, b, c, d."
- **Sửa lỗi căn chỉnh**: Loại bỏ `\\\quad` gây thụt dòng không đều
- **Chuẩn hóa số thập phân**: Loại bỏ .00 thừa, giữ nguyên phần thập phân có ý nghĩa
- **Sửa lỗi LaTeX**: `x{2}` → `x^{2}` cho đúng format số mũ

### 5. Tối ưu hóa cuối cùng
- **Bỏ phần "Kết luận: Mệnh đề ĐÚNG/SAI"** thừa (đã có dấu `*` và đáp án cuối)
- **Sửa lỗi căn chỉnh**: Tất cả dòng a), b), c), d) căn chỉnh đều nhau
- **Dọn dẹp file**: Xóa file thừa, đổi tên cho ngắn gọn

## Files hiện tại

### Core Files
- **`asymptotic_advanced.py`** - File Python chính (đã đổi tên, bỏ chữ "generator")
- **`asymptotic_advanced_questions_generated.tex`** - File LaTeX output
- **`asymptotic_advanced_questions_generated.pdf`** - File PDF 4 trang cuối cùng

### Reference Files
- **`asymptotic_advanced_solver.tex`** - File solver tham khảo
- **`README_CHAT_CONTEXT.md`** - File README này

## Tính năng chính

### Format theo chuẩn true_false_triangle
```latex
Câu X: Chọn các mệnh đề đúng:

*a) Mệnh đề đúng (có dấu *)
b) Mệnh đề sai (không có dấu *)
*c) Mệnh đề đúng (có dấu *)
d) Mệnh đề sai (không có dấu *)

Lời giải:

Lời giải cho mệnh đề a):
[Chi tiết tính toán...]

Lời giải cho mệnh đề b):
[Chi tiết tính toán...]

Lời giải cho mệnh đề c):
[Chi tiết tính toán...]

Lời giải cho mệnh đề d):
[Chi tiết tính toán...]

Đáp án đúng: a, c.
```

### Câu 1 - Tiệm cận với tham số
- 3 format ngẫu nhiên: tiệm cận trực tiếp, qua điểm, giao điểm
- Tính toán m, n từ điều kiện tiệm cận
- Logic đúng/sai với biểu thức `αm + βn`

### Câu 2 - Diện tích hình chữ nhật
- Tính diện tích từ tiệm cận đứng và ngang
- 2 trường hợp nghiệm cho m
- Logic đúng/sai với giá trị m hiển thị

### Câu 3 - Số lượng tiệm cận
- Random giữa "2 tiệm cận đứng" và "3 tiệm cận"
- Phân tích điều kiện Delta và f(a) ≠ 0
- Logic đúng/sai với số lượng giá trị nguyên

### Câu 4 - Tiệm cận xiên
- Phép chia đa thức để tìm tiệm cận xiên
- Format với phương trình đầy đủ
- Logic đúng/sai với hệ số slope, intercept

## Cách sử dụng
```bash
# Tạo câu hỏi mới
python3 asymptotic_advanced.py n
với n là số lượng câu hỏi cần tạo

# Compile thành PDF
xelatex asymptotic_advanced_questions_generated.tex
```

## Đặc điểm kỹ thuật
- **Tiếng Việt**: Polyglossia + Times New Roman
- **Random generation**: Mỗi lần chạy tạo bộ câu hỏi mới (3 câu, mỗi câu 4 mệnh đề)
- **Chuẩn hóa toán học**: Hệ thống 11 quy tắc tự động
- **Format LaTeX**: Đúng chuẩn, không lỗi hiển thị
- **Căn chỉnh hoàn hảo**: Tất cả dòng a), b), c), d) căn chỉnh đều nhau
- **Logic đúng/sai**: Hoạt động cho tất cả 4 loại mệnh đề
- **Output**: PDF 4 trang, format đẹp, dễ đọc

## Vấn đề đã giải quyết
- ✅ Lỗi format xuống dòng (câu 2, 3, 4 bị gộp)
- ✅ Lỗi LaTeX `x{2}` → `x^{2}`
- ✅ Số thập phân thừa `4.00` → `4`
- ✅ Chuẩn hóa biểu thức toán học
- ✅ Logic chia cho 0 trong câu 3
- ✅ Format thống nhất theo true_false_triangle
- ✅ **Căn chỉnh dòng a), b), c), d)** - Loại bỏ `\\\quad` gây thụt lề
- ✅ **Bỏ phần kết luận thừa** - Đã có dấu `*` và đáp án cuối
- ✅ **Dọn dẹp file thừa** - Chỉ giữ file cần thiết
- ✅ **Đổi tên file** - Ngắn gọn hơn: `asymptotic_advanced.py` 