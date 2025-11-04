#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'test_tex'))

try:
    print("Starting test...")
    from plane_true_false_part_B import (prop_min_volume_with_value, prop_plane_special_ratio_condition,
                                         prop_plane_parallel_distance_between_planes, prop_plane_orthocenter_from_projections)
    print("Import successful")
    
    print("\n=== Volume Function ===")
    result = prop_min_volume_with_value()
    print("True:", result['true'])
    print("False:", result['false'])
    
    print("\n=== Special Ratio Function ===")
    result2 = prop_plane_special_ratio_condition()
    print("True:", result2['true'])
    print("False:", result2['false'])
    
    print("\n=== Distance Function ===")
    result3 = prop_plane_parallel_distance_between_planes()
    print("True:", result3['true'])
    print("False:", result3['false'])
    
    print("\n=== Orthocenter Function ===")
    result4 = prop_plane_orthocenter_from_projections()
    print("True:", result4['true'])
    print("False:", result4['false'])
    
except Exception as e:
    print("Error occurred:", e)
    import traceback
    traceback.print_exc()
