"""
Hàm format quadratic root đơn giản và hiệu quả
"""
import math

def simple_quadratic_root_format(discriminant, b_coeff, a_coeff, is_positive_sqrt=True):
    """
    Format nghiệm phương trình bậc hai dạng (-b ± √Δ)/(2a)
    Đơn giản hóa tự động thành dạng đẹp nhất
    """
    
    # Bước 1: Phân tích √discriminant = k√n với n là số không có thừa số chính phương
    def simplify_sqrt(num):
        """Đơn giản √num thành k√n"""
        if num == 0:
            return 0, 1
        
        k = 1
        n = num
        
        # Tìm tất cả thừa số chính phương
        i = 2
        while i * i <= n:
            while n % (i * i) == 0:
                k *= i
                n //= (i * i)
            i += 1
        
        return k, n
    
    sqrt_coeff, sqrt_radical = simplify_sqrt(discriminant)
    
    # Bước 2: Tạo chuỗi √discriminant
    if sqrt_radical == 1:
        sqrt_str = str(sqrt_coeff)  # Số nguyên
    elif sqrt_coeff == 1:
        sqrt_str = f"\\sqrt{{{sqrt_radical}}}"
    else:
        sqrt_str = f"{sqrt_coeff}\\sqrt{{{sqrt_radical}}}"
    
    # Bước 3: Tính nghiệm (-b ± √discriminant)/(2a)
    sign = "+" if is_positive_sqrt else "-"
    
    # Bước 4: Cố gắng đơn giản hóa
    if 2 * a_coeff == 2:  # mẫu số = 2
        # Kiểm tra xem có thể rút gọn không
        if b_coeff % 2 == 0 and sqrt_coeff % 2 == 0:
            const_part = -b_coeff // 2
            new_sqrt_coeff = sqrt_coeff // 2
            
            # Tạo chuỗi kết quả
            parts = []
            
            # Phần hằng số
            if const_part != 0:
                parts.append(str(const_part))
            
            # Phần căn thức
            if sqrt_radical == 1:
                # Không có căn thức (số nguyên)
                sqrt_part = str(new_sqrt_coeff)
            elif new_sqrt_coeff == 1:
                sqrt_part = f"\\sqrt{{{sqrt_radical}}}"
            else:
                sqrt_part = f"{new_sqrt_coeff}\\sqrt{{{sqrt_radical}}}"
            
            # Kết hợp
            if len(parts) == 0:  # const_part = 0
                return f"{'-' if not is_positive_sqrt else ''}{sqrt_part}"
            else:
                return f"{parts[0]} {sign} {sqrt_part}"
    
    # Trường hợp không đơn giản được
    return f"\\frac{{{-b_coeff} {sign} {sqrt_str}}}{{{2*a_coeff}}}"


def test_simple_function():
    """Test hàm đơn giản"""
    test_cases = [
        # (discriminant, b_coeff, a_coeff, description)
        (32, -4, 1, "m² - 4m - 4 = 0"),
        (48, -6, 1, "m² - 6m - 3 = 0"),  
        (96, -6, 1, "m² - 6m - 15 = 0"),
        (36, -6, 1, "m² - 6m + 9 = 0"),   # Perfect square
        (20, -4, 1, "m² - 4m + c = 0"),   # √20 = 2√5
        (12, -4, 2, "2m² - 4m + c = 0"),  # Denominator ≠ 2
    ]
    
    for disc, b, a, desc in test_cases:
        print(f"=== {desc} ===")
        print(f"Δ = {disc}, √Δ = {math.sqrt(disc):.3f}")
        
        root_minus = simple_quadratic_root_format(disc, b, a, False)
        root_plus = simple_quadratic_root_format(disc, b, a, True)
        
        print(f"Root 1: {root_minus}")
        print(f"Root 2: {root_plus}")
        
        # Verify numerically
        actual_root1 = (-b - math.sqrt(disc)) / (2*a)
        actual_root2 = (-b + math.sqrt(disc)) / (2*a)
        print(f"Verify: {actual_root1:.6f}, {actual_root2:.6f}")
        print()

if __name__ == "__main__":
    test_simple_function()
