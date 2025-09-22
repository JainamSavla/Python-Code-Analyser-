#!/usr/bin/env python3
"""
Demo script to showcase the graphing capabilities of N0VA Code Analyzer.
This script demonstrates the new visualization features for time and space complexity.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer.code_analysis import CodeAnalyzer
from analyzer.complexity_visualizer import ComplexityVisualizer
import matplotlib.pyplot as plt


def create_test_files():
    """Create some test Python files with different complexities."""
    
    # Simple O(1) file
    with open('test_simple.py', 'w') as f:
        f.write('''def simple_function(x):
    """A simple O(1) function."""
    return x * 2

def another_simple(a, b):
    """Another O(1) function."""
    return a + b

# Simple variable assignment
result = simple_function(5)
print(result)
''')

    # O(n) complexity file
    with open('test_linear.py', 'w') as f:
        f.write('''def linear_search(arr, target):
    """Linear search - O(n) time, O(1) space."""
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1

def sum_array(arr):
    """Sum array elements - O(n) time, O(1) space."""
    total = 0
    for num in arr:
        total += num
    return total

# Create a list - O(n) space
numbers = list(range(1000))
result = linear_search(numbers, 500)
''')

    # O(n²) complexity file
    with open('test_quadratic.py', 'w') as f:
        f.write('''def bubble_sort(arr):
    """Bubble sort - O(n²) time, O(1) space."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def matrix_multiply(A, B):
    """Simple matrix multiplication - O(n²) time, O(n²) space."""
    n = len(A)
    C = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]
    return C

# Test with small matrices
matrix1 = [[1, 2], [3, 4]]
matrix2 = [[5, 6], [7, 8]]
result = matrix_multiply(matrix1, matrix2)
''')

    # Recursive file with different space complexity
    with open('test_recursive.py', 'w') as f:
        f.write('''def fibonacci_recursive(n):
    """Fibonacci - O(2^n) time, O(n) space."""
    if n <= 1:
        return n
    return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)

def factorial(n):
    """Factorial - O(n) time, O(n) space."""
    if n <= 1:
        return 1
    return n * factorial(n-1)

def binary_search(arr, target, left=0, right=None):
    """Binary search - O(log n) time, O(log n) space."""
    if right is None:
        right = len(arr) - 1
    
    if left > right:
        return -1
    
    mid = (left + right) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] > target:
        return binary_search(arr, target, left, mid - 1)
    else:
        return binary_search(arr, target, mid + 1, right)

# Test functions
result1 = fibonacci_recursive(10)
result2 = factorial(5)
result3 = binary_search([1, 3, 5, 7, 9], 5)
''')

    return ['test_simple.py', 'test_linear.py', 'test_quadratic.py', 'test_recursive.py']


def demo_single_file_analysis():
    """Demonstrate single file analysis with graphs."""
    print("=== Single File Analysis Demo ===")
    
    analyzer = CodeAnalyzer()
    visualizer = ComplexityVisualizer()
    
    # Analyze the quadratic complexity file
    result = analyzer.analyze_file('test_quadratic.py')
    
    print(f"File: test_quadratic.py")
    print(f"Language: {result.get('language', 'unknown')}")
    
    metrics = result.get('metrics', {})
    print(f"Lines of code: {metrics.get('lines_of_code', 0)}")
    print(f"Time complexity: {metrics.get('time_complexity', {}).get('overall', 'N/A')}")
    print(f"Space complexity: {metrics.get('space_complexity', {}).get('overall', 'N/A')}")
    
    # Generate and save comparison chart
    time_complexity = metrics.get('time_complexity', {})
    space_complexity = metrics.get('space_complexity', {})
    
    comparison_fig = visualizer.create_complexity_comparison_chart(time_complexity, space_complexity)
    comparison_fig.savefig('single_file_complexity_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: single_file_complexity_comparison.png")
    
    # Generate and save radar chart
    radar_fig = visualizer.create_performance_radar_chart(metrics)
    radar_fig.savefig('single_file_performance_radar.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: single_file_performance_radar.png")
    
    plt.close('all')  # Close figures to free memory


def demo_multiple_file_analysis():
    """Demonstrate multiple file analysis with graphs."""
    print("\n=== Multiple File Analysis Demo ===")
    
    analyzer = CodeAnalyzer()
    visualizer = ComplexityVisualizer()
    
    # Analyze all test files
    test_files = ['test_simple.py', 'test_linear.py', 'test_quadratic.py', 'test_recursive.py']
    results = []
    
    for file_path in test_files:
        if os.path.exists(file_path):
            result = analyzer.analyze_file(file_path)
            results.append(result)
            
            metrics = result.get('metrics', {})
            print(f"{file_path}: {metrics.get('time_complexity', {}).get('overall', 'N/A')} time, "
                  f"{metrics.get('space_complexity', {}).get('overall', 'N/A')} space")
    
    if results:
        # Generate trend analysis
        trend_fig = visualizer.create_complexity_trend_chart(results)
        trend_fig.savefig('multiple_files_trend_analysis.png', dpi=150, bbox_inches='tight')
        print("✓ Saved: multiple_files_trend_analysis.png")
        
        # Generate distribution charts
        distribution_fig = visualizer.create_complexity_distribution_pie(results)
        distribution_fig.savefig('multiple_files_distribution.png', dpi=150, bbox_inches='tight')
        print("✓ Saved: multiple_files_distribution.png")
        
        # Generate heatmap
        heatmap_fig = visualizer.create_complexity_heatmap(results)
        heatmap_fig.savefig('multiple_files_heatmap.png', dpi=150, bbox_inches='tight')
        print("✓ Saved: multiple_files_heatmap.png")
        
        plt.close('all')  # Close figures to free memory


def cleanup_test_files():
    """Remove test files."""
    test_files = ['test_simple.py', 'test_linear.py', 'test_quadratic.py', 'test_recursive.py']
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✓ Cleaned up: {file_path}")


def main():
    """Main demo function."""
    print("N0VA Code Analyzer - Graphing Demo")
    print("=" * 40)
    
    try:
        # Create test files
        print("Creating test files...")
        test_files = create_test_files()
        print(f"✓ Created test files: {', '.join(test_files)}")
        
        # Demo single file analysis
        demo_single_file_analysis()
        
        # Demo multiple file analysis  
        demo_multiple_file_analysis()
        
        print(f"\n=== Demo Complete ===")
        print("Generated graphs:")
        print("• single_file_complexity_comparison.png - Time vs Space complexity comparison")
        print("• single_file_performance_radar.png - Performance radar chart")
        print("• multiple_files_trend_analysis.png - Complexity trends across files")
        print("• multiple_files_distribution.png - Complexity distribution pie charts")
        print("• multiple_files_heatmap.png - Function complexity heatmap")
        
        print(f"\nTo integrate these graphs into the GUI:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the main application: python main.py")
        print("3. Select files/directories to analyze")
        print("4. View graphs in the new visualization tabs")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test files
        print(f"\nCleaning up test files...")
        cleanup_test_files()


if __name__ == "__main__":
    main()