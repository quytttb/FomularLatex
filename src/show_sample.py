#!/usr/bin/env python3
"""
Tạo và lưu một câu hỏi để xem nội dung đầy đủ
"""

from polynomial_cubic_monotonicity import OptimizationGenerator

def main():
    print("Tạo một câu hỏi và lưu vào file...")
    
    # Tạo câu hỏi
    latex_content = OptimizationGenerator.generate_question(1)
    
    # Lưu vào file
    with open('sample_question.tex', 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print("Đã lưu câu hỏi vào file 'sample_question.tex'")
    
    # Hiển thị một phần nội dung
    lines = latex_content.split('\n')
    print("\nNội dung câu hỏi (50 dòng đầu):")
    for i, line in enumerate(lines[:50]):
        print(f"{i+1:2d}: {line}")

if __name__ == "__main__":
    main()
