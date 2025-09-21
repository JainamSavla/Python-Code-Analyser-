#!/usr/bin/env python3
"""
Test script to verify the multi-language code analyzer functionality.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from analyzer.code_analysis import CodeAnalyzer

def test_analyzer():
    """Test the code analyzer with different file types."""
    analyzer = CodeAnalyzer()
    test_dir = project_root / "test_files"
    
    print("Multi-Language Code Analyzer Test")
    print("=" * 50)
    
    # Test individual files
    test_files = [
        "example.py",
        "example.java", 
        "example.c",
        "example.cpp"
    ]
    
    for filename in test_files:
        filepath = test_dir / filename
        if filepath.exists():
            print(f"\nAnalyzing: {filename}")
            print("-" * 30)
            
            result = analyzer.analyze_file(str(filepath))
            
            # Display language
            print(f"Language: {result.get('language', 'unknown').upper()}")
            
            # Display metrics
            metrics = result.get('metrics', {})
            print(f"Lines of code: {metrics.get('lines_of_code', 0)}")
            print(f"Comment lines: {metrics.get('comment_lines', 0)}")
            
            complexity = metrics.get('time_complexity', {})
            print(f"Overall complexity: {complexity.get('overall', 'Not analyzed')}")
            
            # Display issues
            issues = result.get('issues', {})
            if issues:
                print(f"Issues found: {sum(len(msgs) for msgs in issues.values())}")
                for issue_type, messages in issues.items():
                    print(f"  {issue_type}: {len(messages)} issue(s)")
            else:
                print("No issues found")
        else:
            print(f"Test file not found: {filename}")
    
    # Test directory analysis
    print(f"\n\nDirectory Analysis Results")
    print("=" * 50)
    
    results = analyzer.analyze_directory(str(test_dir))
    
    language_stats = {}
    total_lines = 0
    total_issues = 0
    
    for result in results:
        language = result.get('language', 'unknown')
        if language not in language_stats:
            language_stats[language] = {'files': 0, 'lines': 0, 'issues': 0}
        
        language_stats[language]['files'] += 1
        lines = result.get('metrics', {}).get('lines_of_code', 0)
        language_stats[language]['lines'] += lines
        total_lines += lines
        
        issues_count = sum(len(msgs) for msgs in result.get('issues', {}).values())
        language_stats[language]['issues'] += issues_count
        total_issues += issues_count
    
    print(f"Total files analyzed: {len(results)}")
    print(f"Total lines of code: {total_lines}")
    print(f"Total issues found: {total_issues}")
    
    print("\nBreakdown by language:")
    for language, stats in language_stats.items():
        print(f"  {language.upper()}: {stats['files']} files, {stats['lines']} lines, {stats['issues']} issues")

if __name__ == "__main__":
    test_analyzer()
