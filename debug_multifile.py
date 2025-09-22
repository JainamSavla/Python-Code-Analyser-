#!/usr/bin/env python3
"""
Quick test to verify multi-file analysis triggers trend analysis and distribution tabs.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def create_test_project():
    """Create a small test project with multiple files."""
    
    # Create a test directory
    test_dir = "test_project"
    os.makedirs(test_dir, exist_ok=True)
    
    # File 1: Simple complexity
    with open(f"{test_dir}/simple.py", "w") as f:
        f.write('''
def simple_func():
    return "Hello World"

result = simple_func()
''')
    
    # File 2: Linear complexity
    with open(f"{test_dir}/linear.py", "w") as f:
        f.write('''
def linear_search(arr, target):
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1

data = [1, 2, 3, 4, 5]
index = linear_search(data, 3)
''')
    
    # File 3: Quadratic complexity
    with open(f"{test_dir}/quadratic.py", "w") as f:
        f.write('''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

numbers = [64, 34, 25, 12, 22]
sorted_nums = bubble_sort(numbers)
''')
    
    return test_dir

def test_multi_file_analysis():
    """Test multi-file analysis that should trigger trend/distribution tabs."""
    try:
        # Create test project
        test_dir = create_test_project()
        print(f"Created test project in: {test_dir}")
        
        # Import analyzer
        from analyzer.code_analysis import CodeAnalyzer
        
        # Analyze directory
        analyzer = CodeAnalyzer()
        results = analyzer.analyze_directory(test_dir)
        
        print(f"\\nAnalyzed {len(results)} files:")
        for result in results:
            file_path = result['file_path']
            metrics = result.get('metrics', {})
            time_comp = metrics.get('time_complexity', {}).get('overall', 'N/A')
            space_comp = metrics.get('space_complexity', {}).get('overall', 'N/A')
            print(f"  {file_path}: Time={time_comp}, Space={space_comp}")
        
        # Test if this would trigger the multi-file visualization
        if len(results) > 1:
            print("\\n✅ This analysis would trigger the Trend Analysis and Distribution tabs!")
            print("📊 When you run the GUI and select this directory, you should see:")
            print("   - Trend Analysis tab (showing complexity trends)")
            print("   - Distribution tab (showing complexity distribution)")
        else:
            print("\\n⚠️ Only one file analyzed - trend analysis needs multiple files")
        
        return test_dir
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function."""
    print("🔍 Testing Multi-file Analysis for Trend/Distribution Tabs")
    print("=" * 60)
    
    test_dir = test_multi_file_analysis()
    
    if test_dir:
        print("\\n" + "=" * 60)
        print("📋 INSTRUCTIONS TO SEE TREND ANALYSIS & DISTRIBUTION:")
        print("=" * 60)
        print("1. Run the main application:")
        print("   python main.py")
        print()
        print("2. In the GUI, click 'File' > 'Open Directory'")
        print()
        print(f"3. Select the '{test_dir}' directory")
        print()
        print("4. Look for these tabs in the results panel:")
        print("   • 'Trend Analysis' - shows complexity across files")
        print("   • 'Distribution' - shows complexity distribution charts")
        print()
        print("5. If you don't see these tabs, check that:")
        print("   - You selected a DIRECTORY (not individual files)")
        print("   - The directory contains multiple .py files")
        print("   - All dependencies are installed (matplotlib, numpy, seaborn)")
        
        # Clean up
        import shutil
        print(f"\\n🧹 Cleaning up test directory: {test_dir}")
        shutil.rmtree(test_dir)
        print("✅ Cleanup complete")

if __name__ == "__main__":
    main()