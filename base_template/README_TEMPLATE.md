
Template này cho phép bạn dễ dàng tạo và mở rộng hệ thống sinh câu hỏi trắc nghiệm toán tối ưu hóa với đạo hàm.

## 📁 CẤU TRÚC FILE

```
derivative/
├── math_optimization_template.py    # 🏗️ File template chính
├── example_new_problem.py          # 📝 Ví dụ thêm dạng toán mới  
├── README_TEMPLATE.md              # 📖 Hướng dẫn này
└── optimization_questions.tex      # 📄 File LaTeX output
```

## 🎯 TÍNH NĂNG CHÍNH

- ✅ **Tạo câu hỏi tự động**: Sinh câu hỏi trắc nghiệm với 4 đáp án A/B/C/D
- ✅ **Hỗ trợ nhiều dạng toán**: Pool, Fence, Cable, Travel, Rental optimization
- ✅ **Hình vẽ TikZ tích hợp**: Tự động tạo hình vẽ minh họa
- ✅ **Format LaTeX chuẩn**: Xuất ra file .tex compile được ngay
- ✅ **Dễ dàng mở rộng**: Template thiết kế để thêm dạng toán mới
- ✅ **Comment tiếng Việt**: Hướng dẫn chi tiết từng phần

## 🚀 CÁCH SỬ DỤNG CỦ BẢN

### 1. Tạo câu hỏi nhanh
```bash
# Tạo 3 câu hỏi
python main_runner.py 3

# Tạo 5 câu hỏi  
python main_runner.py 5
```

### 2. Biên dịch file LaTeX
```bash
xelatex optimization_questions.tex
```

### 3. Kết quả
- File PDF với câu hỏi trắc nghiệm hoàn chỉnh
- Có đáp án và lời giải chi tiết
- Hình vẽ TikZ đẹp mắt

## 🔧 THÊM DẠNG TOÁN MỚI

### Bước 1: Tạo class dạng toán mới

```python
class YourNewOptimization(BaseOptimizationQuestion):
    """
    Mô tả dạng toán của bạn
    Công thức cơ bản: [ghi công thức]
    """

    def generate_parameters(self) -> Dict[str, Any]:
        """🎲 Sinh tham số ngẫu nhiên"""
        return {
            'param1': value1,
            'param2': value2,
        }

    def calculate_answer(self) -> str:
        """🧮 Tính đáp án đúng"""
        # TODO: Implement
        pass

    def generate_wrong_answers(self) -> List[str]:
        """❌ Sinh 3 đáp án sai"""
        # TODO: Implement  
        pass

    def generate_question_text(self) -> str:
        """📝 Sinh đề bài"""
        # TODO: Implement
        pass

    def generate_solution(self) -> str:
        """📖 Sinh lời giải chi tiết"""
        # TODO: Implement
        pass
```

### Bước 2: Tìm vị trí thêm trong template

```python
# ===== THÊM DẠNG TOÁN MỚI TẠI ĐÂY =====
# Paste class YourNewOptimization vào đây

# Tìm QUESTION_TYPES và thêm:
QUESTION_TYPES = [
    PoolOptimization,
    YourNewOptimization,  # <-- Thêm dòng này
]
```

### Bước 3: Test dạng toán mới

```python
# Test individual methods
problem = YourNewOptimization()
params = problem.generate_parameters()
print("Parameters:", params)

problem.parameters = params
answer = problem.calculate_answer()
print("Answer:", answer)

# Test full question
question = problem.generate_full_question(1)
print("Full question generated!")
```

## 🖼️ THÊM HÌNH VẼ TIKZ MỚI

### Bước 1: Tạo method hình vẽ

```python
@staticmethod
def get_your_new_figure():
    """Mô tả hình vẽ của bạn"""
    return """
\\begin{tikzpicture}
    % Code TikZ của bạn ở đây
    \\draw (0,0) -- (2,2);
    \\node at (1,1) {Text};
\\end{tikzpicture}
"""
```

### Bước 2: Thêm vào TikZFigureLibrary

```python
# Tìm dòng: # ===== THÊM TIKZ FIGURES MỚI TẠI ĐÂY =====
# Paste method get_your_new_figure vào class TikZFigureLibrary
```

### Bước 3: Sử dụng trong câu hỏi

```python
def generate_question_text(self) -> str:
    # Thêm hình vẽ vào đề bài
    figure = TikZFigureLibrary.get_your_new_figure()
    return f"Đề bài... {figure}"
```

## 📚 VÍ DỤ THỰC TẾ

Xem file `example_new_problem.py` để hiểu cách thêm dạng toán "Tối ưu diện tích hình chữ nhật với chu vi cố định":

```bash
# Chạy demo
python example_new_problem.py
```

Demo sẽ:
- ✅ Test tất cả method của dạng toán mới
- ✅ Hiển thị preview câu hỏi được tạo
- ✅ Hướng dẫn tích hợp vào template chính

## 🎨 CUSTOMIZE FORMAT LATEX

### Thêm hàm format mới

```python
# ===== THÊM FORMAT LATEX MỚI TẠI ĐÂY =====
def format_your_new_function(value):
    """Mô tả chức năng format"""
    # TODO: Implement formatting
    return formatted_value
```

### Các hàm format có sẵn

- `format_fraction_latex(num, denom)` - Format phân số
- `format_money(amount, currency)` - Format tiền tệ  
- `format_number_clean(value)` - Loại bỏ .0 nếu là số nguyên

## 🔍 DEBUGGING VÀ TROUBLESHOOTING

### 1. Lỗi import
```python
# Đảm bảo file template trong cùng thư mục
from math_optimization_template import BaseOptimizationQuestion
```

### 2. Lỗi LaTeX compile
```bash
# Kiểm tra cú pháp LaTeX
# Đảm bảo có packages: tikz, tkz-tab, tkz-euclide
```

### 3. Lỗi đáp án không đúng
```python
# Test từng method riêng biệt
# In ra giá trị trung gian để kiểm tra
print(f"Debug: x_optimal = {x_optimal}")
```

### 4. Enable logging chi tiết
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 CÁC DẠNG TOÁN CÓ SẴN

| Dạng toán | Class | Mô tả |
|-----------|--------|--------|
| 🏊 Hồ chứa nước | `PoolOptimization` | Tối ưu chi phí xây hồ hộp chữ nhật |
| 🏡 Hàng rào chữ E | `FenceOptimization` | Tối ưu diện tích hàng rào dọc sông |
| ⚡ Dây điện | `CableOptimization` | Tối ưu chi phí dây từ bờ ra đảo |
| 🚴 Di chuyển | `TravelOptimization` | Tối ưu thời gian với 2 vận tốc |
| 🏠 Cho thuê | `RentalOptimization` | Tối ưu doanh thu cho thuê |

## 🎯 BEST PRACTICES

### 1. Thiết kế tham số
- ✅ Chọn tham số cho nghiệm đẹp (số nguyên, phân số đơn giản)
- ✅ Tránh nghiệm quá phức tạp (nhiều chữ số thập phân)
- ✅ Đảm bảo nghiệm nằm trong miền xác định

### 2. Tạo đáp án sai
- ✅ Sai số hợp lý (sai công thức, sai tính toán)
- ✅ Tránh đáp án quá xa so với đáp án đúng
- ✅ Đảm bảo có cùng đơn vị với đáp án đúng

### 3. Viết lời giải
- ✅ Trình bày từng bước rõ ràng
- ✅ Có bảng biến thiên nếu cần
- ✅ Kết luận rõ ràng

### 4. Format LaTeX
- ✅ Sử dụng `\\(` `\\)` cho inline math
- ✅ Escape ký tự đặc biệt: `\\`, `{`, `}`
- ✅ Test compile trước khi hoàn thiện

## 📞 HỖ TRỢ VÀ ĐÓNG GÓP

### Cần hỗ trợ?
1. Xem file `example_new_problem.py` để hiểu cách thêm dạng toán
2. Chạy test demo để kiểm tra
3. Kiểm tra log để debug

### Muốn đóng góp?
1. Fork repository
2. Thêm dạng toán mới theo template
3. Test kỹ trước khi submit
4. Tạo pull request với mô tả chi tiết

## 📄 LICENSE

Template này được phát hành dưới MIT License. Bạn có thể tự do sử dụng, chỉnh sửa và phân phối.

---

🎉 **Chúc bạn tạo được những câu hỏi toán hay và bổ ích!** 🎉 