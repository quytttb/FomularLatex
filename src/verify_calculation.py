#!/usr/bin/env python3
"""
File verify chi tiết tính toán ProductionOptimization
"""

import sympy as sp
from cau2 import ProductionOptimization

def verify_exact_calculation():
    """Verify tính toán với tham số chính xác từ ảnh"""
    print("🔍 VERIFY CALCULATION - THAM SỐ TỪ ẢNH")
    print("=" * 60)
    
    # Tham số chính xác từ ảnh
    params = {
        'base_hours': 35,
        'base_teams': 150, 
        'base_productivity': 130,
        'hour_increment': 2,
        'team_decrease': 1,
        'productivity_decrease': 10,
        'waste_a': 105,
        'waste_b': 125,
        'waste_c': 10
    }
    
    print("📋 Tham số:")
    for k, v in params.items():
        print(f"   {k}: {v}")
    
    # Manual calculation với SymPy
    t = sp.Symbol('t')
    
    # Theo công thức từ ảnh: (150 - t/2)(130 - 5t)(35 + t) - 10.5(35 + t)² - 12.5(35 + t)
    manual_S = (150 - t/2) * (130 - 5*t) * (35 + t)
    manual_P = sp.Rational(105, 10) * (35 + t)**2 + sp.Rational(125, 10) * (35 + t)
    manual_f = manual_S - manual_P
    manual_f_prime = sp.expand(sp.diff(manual_f, t))
    
    print(f"\n🧮 TÍNH TOÁN THỦ CÔNG:")
    print(f"   S(t) = (150 - t/2)(130 - 5t)(35 + t)")
    print(f"   P(t) = 10.5(35 + t)² + 12.5(35 + t)")
    print(f"   f'(t) = {manual_f_prime}")
    
    # Code calculation
    po = ProductionOptimization()
    po.parameters = params
    solution = po.generate_solution()
    
    # Extract derivative from solution
    for line in solution.split('\n'):
        if "f'(t)" in line and '=' in line and not 'Ta có' in line:
            print(f"\n💻 TÍNH TOÁN TỪ CODE:")
            print(f"   {line}")
            break
    
    # Extract answer
    answer = po.calculate_answer()
    print(f"\n🎯 ĐÁP ÁN: {answer}")
    
    # Verify nghiệm
    solutions = sp.solve(manual_f_prime, t)
    print(f"\n✅ NGHIỆM CHÍNH XÁC:")
    for i, sol in enumerate(solutions, 1):
        t_val = float(sol.evalf())
        hours = 35 + t_val
        print(f"   t_{i} = {t_val:.2f} → x = 35 + {t_val:.2f} = {hours:.0f} giờ")

def test_random_generation():
    """Test với random generation"""
    print(f"\n" + "=" * 60)
    print("🎲 TEST VỚI RANDOM GENERATION")
    print("=" * 60)
    
    for i in range(3):
        print(f"\n📋 Test {i+1}:")
        po = ProductionOptimization()
        po.parameters = po.generate_parameters()
        
        print("Tham số random:")
        for k, v in po.parameters.items():
            print(f"   {k}: {v}")
        
        solution = po.generate_solution()
        
        # Extract derivative
        for line in solution.split('\n'):
            if "f'(t)" in line and '=' in line and not 'Ta có' in line:
                print(f"   Đạo hàm: {line}")
                break
        
        print(f"   Đáp án: {po.calculate_answer()}")

if __name__ == "__main__":
    verify_exact_calculation()
    test_random_generation() 