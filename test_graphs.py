#!/usr/bin/env python3
"""
Simple test to verify the graphing functionality works.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import matplotlib
        print("✓ matplotlib imported successfully")
    except ImportError as e:
        print(f"✗ matplotlib import failed: {e}")
        return False
    
    try:
        import numpy
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        return False
    
    try:
        import seaborn
        print("✓ seaborn imported successfully")
    except ImportError as e:
        print(f"✗ seaborn import failed: {e}")
        return False
    
    try:
        from analyzer.code_analysis import CodeAnalyzer
        print("✓ CodeAnalyzer imported successfully")
    except ImportError as e:
        print(f"✗ CodeAnalyzer import failed: {e}")
        return False
    
    try:
        from analyzer.complexity_visualizer import ComplexityVisualizer
        print("✓ ComplexityVisualizer imported successfully")
    except ImportError as e:
        print(f"✗ ComplexityVisualizer import failed: {e}")
        return False
    
    return True

def test_basic_analysis():
    """Test basic code analysis functionality."""
    print("\nTesting basic analysis...")
    
    try:
        from analyzer.code_analysis import CodeAnalyzer
        
        # Create a simple test file
        test_code = '''def simple_function(x):
    return x * 2

def loop_function(arr):
    total = 0
    for item in arr:
        total += item
    return total
'''
        
        with open('test_temp.py', 'w') as f:
            f.write(test_code)
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_file('test_temp.py')
        
        print(f"✓ Analysis completed for test file")
        print(f"  Language: {result.get('language')}")
        print(f"  Metrics found: {list(result.get('metrics', {}).keys())}")
        
        metrics = result.get('metrics', {})
        if 'time_complexity' in metrics:
            print(f"  Time complexity: {metrics['time_complexity']}")
        if 'space_complexity' in metrics:
            print(f"  Space complexity: {metrics['space_complexity']}")
        
        # Clean up
        if os.path.exists('test_temp.py'):
            os.remove('test_temp.py')
            
        return True
        
    except Exception as e:
        print(f"✗ Basic analysis failed: {e}")
        return False

def test_visualization():
    """Test visualization functionality."""
    print("\nTesting visualization...")
    
    try:
        from analyzer.complexity_visualizer import ComplexityVisualizer
        import matplotlib.pyplot as plt
        
        visualizer = ComplexityVisualizer()
        
        # Test complexity mapping
        test_complexities = ['O(1)', 'O(n)', 'O(n²)']
        for comp in test_complexities:
            numeric = visualizer._complexity_to_numeric(comp)
            print(f"  {comp} -> {numeric}")
        
        # Test simple chart creation
        time_data = {'overall': 'O(n)', 'functions': {'func1': 'O(1)', 'func2': 'O(n)'}}
        space_data = {'overall': 'O(1)', 'functions': {'func1': 'O(1)', 'func2': 'O(1)'}}
        
        fig = visualizer.create_complexity_comparison_chart(time_data, space_data)
        print("✓ Comparison chart created successfully")
        
        # Save test chart
        fig.savefig('test_chart.png', dpi=100, bbox_inches='tight')
        print("✓ Chart saved as test_chart.png")
        
        plt.close(fig)
        
        # Clean up
        if os.path.exists('test_chart.png'):
            os.remove('test_chart.png')
            print("✓ Cleaned up test chart")
            
        return True
        
    except Exception as e:
        print(f"✗ Visualization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("N0VA Graphing Functionality Test")
    print("=" * 35)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_basic_analysis()
    all_passed &= test_visualization()
    
    print("\n" + "=" * 35)
    if all_passed:
        print("✓ All tests passed! Graphing functionality is working.")
        print("\nTo use the graphs in the main application:")
        print("1. Run: python main.py")
        print("2. Open a file or directory")
        print("3. Check the new visualization tabs")
    else:
        print("✗ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()