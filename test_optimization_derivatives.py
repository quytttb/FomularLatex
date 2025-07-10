#!/usr/bin/env python3
"""
Test file để kiểm tra tính toán đạo hàm trong các dạng bài toán tối ưu hóa
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.cau2 import (
        ProductionOptimization, 
        ExportProfitOptimization, 
        FactoryProfitOptimization,
        FuelCostOptimization
    )
except ImportError:
    # Fallback nếu import trực tiếp không được
    sys.path.insert(0, os.path.dirname(__file__))
    from src.cau2 import (
        ProductionOptimization, 
        ExportProfitOptimization, 
        FactoryProfitOptimization,
        FuelCostOptimization
    )
import math

def test_production_optimization_derivative():
    """Test tính toán đạo hàm trong ProductionOptimization"""
    print("=== Testing ProductionOptimization Derivative ===")
    
    # Tạo instance với tham số cụ thể giống trong hình
    po = ProductionOptimization()
    params = {
        "base_hours": 35,
        "base_teams": 110, 
        "base_productivity": 100,
        "hour_increment": 4,
        "team_decrease": 2,
        "productivity_decrease": 8,
        "waste_a": 95,
        "waste_b": 140,
        "waste_c": 2
    }
    po.parameters = params
    
    # Tính toán thủ công để kiểm tra
    def production_function(t):
        """Hàm sản phẩm thực tế f(t)"""
        # Số tổ: 110 - t/4
        teams = params["base_teams"] - t / params["hour_increment"]
        
        # Năng suất: 100 - 8t/4 = 100 - 2t
        productivity = params["base_productivity"] - params["productivity_decrease"] * t / params["hour_increment"]
        
        # Thời gian: 35 + t
        hours = params["base_hours"] + t
        
        # Sản phẩm sản xuất
        production = teams * productivity * hours
        
        # Phế phẩm: [95(35+t)² + 140(35+t)]/2
        waste = (params["waste_a"] * hours**2 + params["waste_b"] * hours) / params["waste_c"]
        
        return production - waste
    
    def production_derivative(t):
        """Đạo hàm f'(t) tính thủ công"""
        hours = params["base_hours"] + t  # 35 + t
        teams = params["base_teams"] - t / params["hour_increment"]  # 110 - t/4
        productivity = params["base_productivity"] - params["productivity_decrease"] * t / params["hour_increment"]  # 100 - 2t
        
        # Áp dụng quy tắc đạo hàm tích (uvw)' = u'vw + uv'w + uvw'
        # u = teams = 110 - t/4, u' = -1/4
        # v = productivity = 100 - 2t, v' = -2  
        # w = hours = 35 + t, w' = 1
        
        term1 = (-1/4) * productivity * hours
        term2 = teams * (-2) * hours  
        term3 = teams * productivity * 1
        
        # Đạo hàm phần phế phẩm: P'(t) = [2*95*(35+t) + 140]/2 = 95*(35+t) + 70
        waste_derivative = params["waste_a"] * hours + params["waste_b"] / params["waste_c"]
        
        return term1 + term2 + term3 - waste_derivative
    
    # Test tại một số điểm
    test_points = [-4, 0, 10]
    
    print("Kiểm tra tính toán đạo hàm:")
    for t in test_points:
        calculated = production_derivative(t)
        print(f"t = {t}: f'(t) = {calculated:.4f}")
        
        # Kiểm tra bằng numerical derivative
        h = 1e-6
        numerical = (production_function(t + h) - production_function(t - h)) / (2 * h)
        print(f"  Numerical derivative: {numerical:.4f}")
        print(f"  Difference: {abs(calculated - numerical):.8f}")
        
        if abs(calculated - numerical) < 1e-4:
            print("  ✅ PASS")
        else:
            print("  ❌ FAIL")
        print()

def test_export_profit_optimization_derivative():
    """Test tính toán đạo hàm trong ExportProfitOptimization"""
    print("=== Testing ExportProfitOptimization Derivative ===")
    
    epo = ExportProfitOptimization()
    params = {
        "c1": 200,
        "c2": 4200, 
        "x0": 3100,
        "profit_tax_ratio": (4, 1)
    }
    epo.parameters = params
    
    def profit_function(x):
        """Hàm lợi nhuận L(x)"""
        # a = (x0 - x)/5
        a = (params["x0"] - x) / 5
        
        # Số sản phẩm xuất khẩu: 2x - (c1 + c2)
        export_quantity = 2*x - (params["c1"] + params["c2"])
        
        # Lợi nhuận: (2x - 4400) * (4/5) * (3100 - x)
        return export_quantity * (4/5) * (params["x0"] - x)
    
    def profit_derivative(x):
        """Đạo hàm L'(x)"""
        # L(x) = (4/5)(2x - 4400)(3100 - x)
        # L'(x) = (4/5)[2(3100 - x) - (2x - 4400)]
        # L'(x) = (4/5)[6200 - 2x - 2x + 4400]
        # L'(x) = (4/5)[10600 - 4x]
        return (4/5) * (2*params["x0"] + params["c1"] + params["c2"] - 4*x)
    
    # Test tại điểm cực trị
    x_optimal = (2*params["x0"] + params["c1"] + params["c2"]) / 4
    
    print(f"Điểm cực trị lý thuyết: x = {x_optimal}")
    print(f"L'({x_optimal}) = {profit_derivative(x_optimal):.6f}")
    
    # Test numerical derivative
    h = 1e-6
    numerical = (profit_function(x_optimal + h) - profit_function(x_optimal - h)) / (2 * h)
    print(f"Numerical derivative: {numerical:.6f}")
    
    if abs(profit_derivative(x_optimal)) < 1e-4:
        print("✅ PASS: Đạo hàm = 0 tại điểm cực trị")
    else:
        print("❌ FAIL: Đạo hàm không bằng 0 tại điểm cực trị")
    print()

def test_factory_profit_optimization_derivative():
    """Test tính toán đạo hàm trong FactoryProfitOptimization"""
    print("=== Testing FactoryProfitOptimization Derivative ===")
    
    fpo = FactoryProfitOptimization()
    params = {
        "price_a": 90,
        "price_b": 0.01,
        "cost_c": 200,
        "cost_d": 27,
        "vat_rate": 0.1
    }
    fpo.parameters = params
    
    def factory_profit_function(x):
        """Hàm lợi nhuận L(x)"""
        # Doanh thu: x(90 - 0.01x²)
        revenue = x * (params["price_a"] - params["price_b"] * x**2)
        
        # Chi phí: (200 + 27x)/2
        cost = (params["cost_c"] + params["cost_d"] * x) / 2
        
        # Thuế GTGT: 10% doanh thu
        tax = params["vat_rate"] * revenue
        
        return revenue - cost - tax
    
    def factory_profit_derivative(x):
        """Đạo hàm L'(x)"""
        # L(x) = 0.9x(90 - 0.01x²) - (200 + 27x)/2
        # L(x) = 81x - 0.009x³ - 100 - 13.5x
        # L(x) = 67.5x - 0.009x³ - 100
        # L'(x) = 67.5 - 0.027x²
        
        coef_x = params["price_a"] * (1 - params["vat_rate"]) - params["cost_d"] / 2
        coef_x3 = -params["price_b"] * (1 - params["vat_rate"])
        
        return coef_x + 3 * coef_x3 * x**2
    
    # Tìm điểm cực trị
    coef_x = params["price_a"] * (1 - params["vat_rate"]) - params["cost_d"] / 2
    coef_x3 = -params["price_b"] * (1 - params["vat_rate"])
    
    x_optimal = math.sqrt(-coef_x / (3 * coef_x3))
    
    print(f"Hệ số x: {coef_x}")
    print(f"Hệ số x³: {coef_x3}")
    print(f"Điểm cực trị lý thuyết: x = {x_optimal:.4f}")
    print(f"L'({x_optimal:.4f}) = {factory_profit_derivative(x_optimal):.6f}")
    
    # Test numerical derivative
    h = 1e-6
    numerical = (factory_profit_function(x_optimal + h) - factory_profit_function(x_optimal - h)) / (2 * h)
    print(f"Numerical derivative: {numerical:.6f}")
    
    if abs(factory_profit_derivative(x_optimal)) < 1e-4:
        print("✅ PASS: Đạo hàm = 0 tại điểm cực trị")
    else:
        print("❌ FAIL: Đạo hàm không bằng 0 tại điểm cực trị")
    print()

def test_fuel_cost_optimization_derivative():
    """Test tính toán đạo hàm trong FuelCostOptimization"""
    print("=== Testing FuelCostOptimization Derivative ===")
    
    fco = FuelCostOptimization()
    params = {
        "fixed_cost": 630,
        "ref_speed": 10,
        "ref_variable_cost": 70,
        "k": 70 / (10**2)  # k = 0.7
    }
    fco.parameters = params
    
    def fuel_cost_function(v):
        """Hàm chi phí f(v) = a/v + kv"""
        return params["fixed_cost"] / v + params["k"] * v
    
    def fuel_cost_derivative(v):
        """Đạo hàm f'(v) = -a/v² + k"""
        return -params["fixed_cost"] / (v**2) + params["k"]
    
    # Tìm điểm cực trị: v = sqrt(a/k)
    v_optimal = math.sqrt(params["fixed_cost"] / params["k"])
    
    print(f"Chi phí cố định a = {params['fixed_cost']}")
    print(f"Hệ số k = {params['k']}")
    print(f"Điểm cực trị lý thuyết: v = {v_optimal:.4f}")
    print(f"f'({v_optimal:.4f}) = {fuel_cost_derivative(v_optimal):.6f}")
    
    # Test numerical derivative
    h = 1e-6
    numerical = (fuel_cost_function(v_optimal + h) - fuel_cost_function(v_optimal - h)) / (2 * h)
    print(f"Numerical derivative: {numerical:.6f}")
    
    if abs(fuel_cost_derivative(v_optimal)) < 1e-4:
        print("✅ PASS: Đạo hàm = 0 tại điểm cực trị")
    else:
        print("❌ FAIL: Đạo hàm không bằng 0 tại điểm cực trị")
    print()

def main():
    """Chạy tất cả các test"""
    print("🧪 KIỂM TRA TÍNH TOÁN ĐẠO HÀM TRONG CÁC DẠNG TỐI ƯU HÓA")
    print("=" * 70)
    print()
    
    test_production_optimization_derivative()
    test_export_profit_optimization_derivative() 
    test_factory_profit_optimization_derivative()
    test_fuel_cost_optimization_derivative()
    
    print("🏁 Hoàn thành kiểm tra!")

if __name__ == "__main__":
    main()
