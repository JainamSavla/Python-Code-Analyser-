#!/usr/bin/env python3
"""
Test script to verify space complexity analysis functionality.
"""

from analyzer.code_analysis import CodeAnalyzer

def test_space_complexity_analysis():
    """Test various space complexity scenarios."""
    analyzer = CodeAnalyzer()
    
    # Test cases with different space complexities
    test_cases = [
        {
            'name': 'O(1) - Constant space',
            'code': '''
def constant_space(n):
    x = 5
    y = 10
    return x + y
'''
        },
        {
            'name': 'O(n) - Linear space with list creation',
            'code': '''
def linear_space(n):
    arr = []
    for i in range(n):
        arr.append(i)
    return arr
'''
        },
        {
            'name': 'O(n) - List comprehension',
            'code': '''
def linear_comprehension(n):
    return [i * 2 for i in range(n)]
'''
        },
        {
            'name': 'O(n²) - Nested data structure',
            'code': '''
def quadratic_space(n):
    matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(i * j)
        matrix.append(row)
    return matrix
'''
        },
        {
            'name': 'O(n) - Recursive fibonacci with memoization',
            'code': '''
def fib_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib_memo(n-1, memo) + fib_memo(n-2, memo)
    return memo[n]
'''
        },
        {
            'name': 'O(n) - Dictionary operations',
            'code': '''
def dict_operations(data):
    result = {}
    for item in data:
        result[item] = item * 2
    return result
'''
        }
    ]
    
    print("Space Complexity Analysis Test Results:")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 30)
        
        # Create a temporary file for analysis
        temp_file = f'temp_test_{i}.py'
        with open(temp_file, 'w') as f:
            f.write(test_case['code'])
        
        try:
            # Analyze the code
            result = analyzer.analyze_file(temp_file)
            
            # Display results
            print(f"Time Complexity: {result['metrics'].get('time_complexity', {}).get('overall', 'Not analyzed')}")
            print(f"Space Complexity: {result['metrics'].get('space_complexity', {}).get('overall', 'Not analyzed')}")
            
            if result['metrics'].get('space_complexity', {}).get('functions'):
                print("Function-level space complexity:")
                for func, complexity in result['metrics']['space_complexity']['functions'].items():
                    print(f"  {func}: {complexity}")
            
            # Clean up
            import os
            os.remove(temp_file)
            
        except Exception as e:
            print(f"Error analyzing {test_case['name']}: {e}")
    
    print("\n" + "=" * 50)
    print("Testing complete!")

if __name__ == '__main__':
    test_space_complexity_analysis()