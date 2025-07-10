#!/usr/bin/env python3
"""
Test đơn giản để kiểm tra tính toán đạo hàm trong ProductionOptimization
"""

import math

def test_production_optimization_derivative():
    """Test tính toán đạo hàm với tham số cụ thể từ hình"""
    print("=== Test ProductionOptimization Derivative ===")
    
    # Tham số từ hình
    base_hours = 35
    base_teams = 110
    base_productivity = 100
    hour_increment = 4
    productivity_decrease = 8
    waste_a = 95
    waste_b = 140
    waste_c = 2
    
    def production_function(t):
        """Hàm sản phẩm thực tế f(t) = Sản xuất - Phế phẩm"""
        # Số tổ: 110 - t/4
        teams = base_teams - t / hour_increment
        
        # Năng suất: 100 - 8t/4 = 100 - 2t
        productivity = base_productivity - productivity_decrease * t / hour_increment
        
        # Thời gian: 35 + t
        hours = base_hours + t
        
        # Sản phẩm sản xuất
        production = teams * productivity * hours
        
        # Phế phẩm: [95(35+t)² + 140(35+t)]/2
        waste = (waste_a * hours**2 + waste_b * hours) / waste_c
        
        return production - waste
    
    def production_derivative_manual(t):
        """Đạo hàm f'(t) tính thủ công theo công thức từ hình"""
        hours = base_hours + t  # 35 + t
        teams = base_teams - t / hour_increment  # 110 - t/4
        productivity = base_productivity - productivity_decrease * t / hour_increment  # 100 - 2t
        
        # Theo quy tắc đạo hàm tích (uvw)' = u'vw + uv'w + uvw'
        # u = teams = 110 - t/4, u' = -1/4
        # v = productivity = 100 - 2t, v' = -2  
        # w = hours = 35 + t, w' = 1
        
        term1 = (-1/4) * productivity * hours
        term2 = teams * (-2) * hours  
        term3 = teams * productivity * 1
        
        # Phần đạo hàm phế phẩm (SỬA LẠI THEO HÌNH):
        # P(x) = [95x² + 140x]/2
        # P'(x) = [190x + 140]/2 = 95x + 70
        # Với x = 35 + t: P'(35 + t) = 95(35 + t) + 70
        waste_derivative = waste_a * hours + waste_b / waste_c
        
        return term1 + term2 + term3 - waste_derivative
    
    def production_derivative_wrong(t):
        """Đạo hàm sai như trong hình (để so sánh)"""
        hours = base_hours + t
        teams = base_teams - t / hour_increment
        productivity = base_productivity - productivity_decrease * t / hour_increment
        
        term1 = (-1/4) * productivity * hours
        term2 = teams * (-2) * hours  
        term3 = teams * productivity * 1
        
        # Công thức SAI trong hình: -95/2(35 + t) - 35
        waste_derivative_wrong = (waste_a / 2) * hours + 35
        
        return term1 + term2 + term3 - waste_derivative_wrong
    
    # Test tại điểm t = -4 (điểm cực trị)
    t_test = -4
    
    print(f"Tại t = {t_test}:")
    
    # Tính đạo hàm bằng numerical method
    h = 1e-6
    numerical = (production_function(t_test + h) - production_function(t_test - h)) / (2 * h)
    
    # Tính theo công thức đúng
    analytical_correct = production_derivative_manual(t_test)
    
    # Tính theo công thức sai trong hình
    analytical_wrong = production_derivative_wrong(t_test)
    
    print(f"  Numerical derivative: {numerical:.6f}")
    print(f"  Analytical (ĐÚNG):   {analytical_correct:.6f}")
    print(f"  Analytical (SAI):    {analytical_wrong:.6f}")
    print(f"  Sai số (ĐÚNG):       {abs(numerical - analytical_correct):.8f}")
    print(f"  Sai số (SAI):        {abs(numerical - analytical_wrong):.8f}")
    
    if abs(numerical - analytical_correct) < 1e-4:
        print("  ✅ Công thức ĐÚNG khớp với numerical")
    else:
        print("  ❌ Công thức ĐÚNG không khớp")
        
    if abs(numerical - analytical_wrong) > 1e-3:
        print("  ✅ Công thức SAI trong hình thực sự sai")
    else:
        print("  ❌ Không phát hiện được lỗi")
    
    print()
    
    # Test thêm tại t = 0
    t_test2 = 0
    print(f"Tại t = {t_test2}:")
    
    numerical2 = (production_function(t_test2 + h) - production_function(t_test2 - h)) / (2 * h)
    analytical_correct2 = production_derivative_manual(t_test2)
    analytical_wrong2 = production_derivative_wrong(t_test2)
    
    print(f"  Numerical derivative: {numerical2:.6f}")
    print(f"  Analytical (ĐÚNG):   {analytical_correct2:.6f}")
    print(f"  Analytical (SAI):    {analytical_wrong2:.6f}")
    print(f"  Sai số (ĐÚNG):       {abs(numerical2 - analytical_correct2):.8f}")
    print(f"  Sai số (SAI):        {abs(numerical2 - analytical_wrong2):.8f}")

if __name__ == "__main__":
    test_production_optimization_derivative()
