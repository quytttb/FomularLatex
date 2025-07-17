# 📋 Changelog

Tất cả những thay đổi đáng chú ý của dự án này sẽ được ghi lại trong file này.

## [2.0.0] - 2025-07-16 🎉

### ✨ Added - Kiến trúc mới hoàn toàn
- **Clean Architecture Framework**: Separation of concerns với 3 class chính
  - `LaTeXDocumentBuilder`: Chuyên tạo LaTeX documents
  - `QuestionTypeLoader`: Dynamic loading question types  
  - `QuestionManager`: Quản lý question generation với retry/timeout
- **Professional CLI**: `main_runner.py` với argparse interface
  - Positional arguments: `num_questions`, `format`
  - Optional arguments: `--output`, `--title`, `--verbose`
  - Comprehensive help với examples
- **Timeout Protection**: Tự động timeout sau 30s để tránh hang
- **Retry Logic**: Tự động retry 3 lần khi gặp lỗi tạm thời
- **Statistics Reporting**: Chi tiết về success/failure/retry/timeout
- **LaTeX Author Field**: Thêm `author="dev"` để loại bỏ warnings

### 🔧 Changed - Cải tiến
- **Type Hints**: Thêm type hints cho tất cả functions
- **Error Handling**: Comprehensive exception handling
- **Vietnamese Comments**: Tất cả comments bằng tiếng Việt
- **Verbose Mode**: Debug information chi tiết
- **Custom Output**: Tùy chỉnh file name và document title

### 🗑️ Deprecated - Deprecated
- `BaseOptimizationQuestion.create_latex_document()` → Sử dụng `LaTeXDocumentBuilder`
- `get_available_question_types()` function → Sử dụng `QuestionTypeLoader`
- `generate_mixed_questions()` function → Sử dụng `QuestionManager`

### 🔥 Removed - Đã xóa
- Các deprecated methods trong `base_optimization_question.py`
- Old imports trong `main_runner.py`
- Hardcoded timeout và retry logic (đã move vào classes)

### 🐛 Fixed - Sửa lỗi
- LaTeX compilation warnings về missing author
- Import dependencies issues
- Code duplication trong question generation
- Memory leaks với signal handlers

### 🏗️ Architecture - Kiến trúc
```
Old: main_runner.py → base_optimization_question.py (monolithic)
New: main_runner.py → QuestionManager → QuestionTypeLoader → LaTeXDocumentBuilder
```

### 📊 Performance - Hiệu năng
- ⚡ Faster module loading với caching
- 🛡️ Timeout protection tránh infinite loops  
- 🔄 Smart retry logic giảm failures
- 📈 Better memory management

### 🧪 Testing - Kiểm thử
- ✅ CLI interface testing
- ✅ Format 1 và 2 testing
- ✅ Verbose mode testing
- ✅ Custom output testing
- ✅ LaTeX compilation testing (no warnings)

---

## [1.x.x] - Legacy Versions

### Các phiên bản trước đây
- Individual question generators trong `/src/`
- Basic template system
- Manual LaTeX document creation
- No CLI interface
- No error handling
- No timeout protection

---

## 🔮 Planned Features - Tính năng dự kiến

### v2.1.0
- [ ] Parallel question generation
- [ ] Question type caching  
- [ ] PDF auto-compilation
- [ ] Configuration file support

### v2.2.0
- [ ] Web interface
- [ ] Question bank system
- [ ] Export to multiple formats
- [ ] Advanced TikZ library

### v3.0.0
- [ ] Plugin system
- [ ] Database integration
- [ ] Cloud deployment
- [ ] AI-powered question generation

---

## 📝 Migration Guide - Hướng dẫn migrate

### Từ Legacy sang v2.0.0

#### Before (Legacy)
```python
from base_optimization_question import generate_mixed_questions
content = generate_mixed_questions(5)
```

#### After (v2.0.0)
```bash
cd base_template
python3 main_runner.py 5 2 -v
```

#### Hoặc programmatically
```python
from question_manager import QuestionManager
from question_type_loader import QuestionTypeLoader

loader = QuestionTypeLoader()
types = loader.load_available_types()
manager = QuestionManager(question_types=types)
questions = manager.generate_questions(5, 2, verbose=True)
```

---

**Lưu ý**: Các phiên bản v2.x.x tương thích ngược với legacy code trong `/src/`, chỉ có `base_template/` được refactor hoàn toàn.
