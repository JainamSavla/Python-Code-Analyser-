#!/usr/bin/env python3
"""
Simple demo to test trend analysis and distribution functionality.
This script will create test files and generate the graphs to verify they work.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def create_demo_files():
    """Create demo files with different complexity levels."""
    files = []
    
    # Simple O(1) complexity
    simple_code = '''
def get_constant():
    """O(1) time and space."""
    return 42

def add_numbers(a, b):
    """O(1) time and space."""
    return a + b

result = get_constant() + add_numbers(1, 2)
print(result)
'''
    with open('demo_simple.py', 'w') as f:
        f.write(simple_code)
    files.append('demo_simple.py')
    
    # O(n) complexity
    linear_code = '''
def find_max(numbers):
    """O(n) time, O(1) space."""
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val

def create_list(n):
    """O(n) time, O(n) space."""
    result = []
    for i in range(n):
        result.append(i * 2)
    return result

data = [1, 5, 3, 9, 2, 8]
maximum = find_max(data)
new_list = create_list(10)
'''
    with open('demo_linear.py', 'w') as f:
        f.write(linear_code)
    files.append('demo_linear.py')
    
    # O(n²) complexity
    quadratic_code = '''
def selection_sort(arr):
    """O(n²) time, O(1) space."""
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

def matrix_operations(matrix):
    """O(n²) time, O(n²) space."""
    n = len(matrix)
    result = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            result[i][j] = matrix[i][j] * 2
    return result

numbers = [64, 34, 25, 12, 22, 11, 90]
sorted_numbers = selection_sort(numbers.copy())
matrix = [[1, 2], [3, 4]]
processed_matrix = matrix_operations(matrix)
'''
    with open('demo_quadratic.py', 'w') as f:
        f.write(quadratic_code)
    files.append('demo_quadratic.py')
    
    # Recursive with different space complexity
    recursive_code = '''
def fibonacci(n):
    """O(2^n) time, O(n) space due to recursion."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    """O(n) time, O(n) space due to recursion."""
    if n <= 1:
        return 1
    return n * factorial(n-1)

def power(base, exp):
    """O(log n) time, O(log n) space."""
    if exp == 0:
        return 1
    if exp % 2 == 0:
        half = power(base, exp // 2)
        return half * half
    else:
        return base * power(base, exp - 1)

fib_result = fibonacci(8)
fact_result = factorial(5)
power_result = power(2, 10)
'''
    with open('demo_recursive.py', 'w') as f:
        f.write(recursive_code)
    files.append('demo_recursive.py')
    
    return files

def test_trend_and_distribution():
    """Test trend analysis and distribution charts specifically."""
    try:
        from analyzer.code_analysis import CodeAnalyzer
        from analyzer.complexity_visualizer import ComplexityVisualizer
        import matplotlib.pyplot as plt
        
        print("🔍 Creating demo files...")
        demo_files = create_demo_files()
        print(f"✅ Created {len(demo_files)} demo files")
        
        print("\n📊 Analyzing files...")
        analyzer = CodeAnalyzer()
        results = []
        
        for filename in demo_files:
            print(f"  Analyzing {filename}...")
            result = analyzer.analyze_file(filename)
            results.append(result)
            
            # Show analysis results
            metrics = result.get('metrics', {})
            time_comp = metrics.get('time_complexity', {}).get('overall', 'N/A')
            space_comp = metrics.get('space_complexity', {}).get('overall', 'N/A')
            print(f"    Time: {time_comp}, Space: {space_comp}")
        
        print(f"\n🎨 Creating visualizations...")
        visualizer = ComplexityVisualizer()
        
        # Test 1: Trend Analysis
        print("  Creating trend analysis chart...")
        trend_fig = visualizer.create_complexity_trend_chart(results)
        trend_fig.savefig('trend_analysis_demo.png', dpi=150, bbox_inches='tight')
        print("  ✅ Saved: trend_analysis_demo.png")
        
        # Test 2: Distribution Charts
        print("  Creating distribution pie charts...")
        distribution_fig = visualizer.create_complexity_distribution_pie(results)
        distribution_fig.savefig('distribution_demo.png', dpi=150, bbox_inches='tight')
        print("  ✅ Saved: distribution_demo.png")
        
        # Test 3: Heatmap (if functions available)
        print("  Creating complexity heatmap...")
        heatmap_fig = visualizer.create_complexity_heatmap(results)
        heatmap_fig.savefig('heatmap_demo.png', dpi=150, bbox_inches='tight')
        print("  ✅ Saved: heatmap_demo.png")
        
        # Clean up matplotlib figures
        plt.close('all')
        
        print(f"\n🎉 SUCCESS! All trend analysis and distribution charts created!")
        print("📁 Generated files:")
        print("  • trend_analysis_demo.png - Shows complexity trends across files")
        print("  • distribution_demo.png - Shows complexity distribution pie charts")
        print("  • heatmap_demo.png - Shows function complexity heatmap")
        
        # Show summary statistics
        print(f"\n📈 Analysis Summary:")
        time_complexities = [r.get('metrics', {}).get('time_complexity', {}).get('overall', 'O(1)') for r in results]
        space_complexities = [r.get('metrics', {}).get('space_complexity', {}).get('overall', 'O(1)') for r in results]
        
        print(f"  Files analyzed: {len(results)}")
        print(f"  Time complexities found: {set(time_complexities)}")
        print(f"  Space complexities found: {set(space_complexities)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up demo files
        print(f"\n🧹 Cleaning up demo files...")
        for filename in ['demo_simple.py', 'demo_linear.py', 'demo_quadratic.py', 'demo_recursive.py']:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"  Removed {filename}")

def main():
    """Main function."""
    print("=" * 60)
    print("🚀 N0VA TREND ANALYSIS & DISTRIBUTION TEST")
    print("=" * 60)
    
    success = test_trend_and_distribution()
    
    print("=" * 60)
    if success:
        print("✅ RESULT: Trend analysis and distribution are working perfectly!")
        print("🖥️  To see them in the GUI:")
        print("   1. Run: python main.py")
        print("   2. Open a directory with multiple Python files")
        print("   3. Check the 'Trend Analysis' and 'Distribution' tabs")
    else:
        print("❌ RESULT: There are issues that need to be fixed.")
    print("=" * 60)

if __name__ == "__main__":
    main()