import ast
import os
import re
from typing import Dict, Any, List, Optional
from collections import defaultdict

class CodeAnalyzer:
    def __init__(self):
        self.issues = defaultdict(list)
        self.metrics = {}
        
        # Supported file extensions and their languages
        self.language_map = {
            '.py': 'python',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c++': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.hh': 'cpp',
            '.hxx': 'cpp'
        }

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        self.issues.clear()
        self.metrics = {}

        file_ext = os.path.splitext(file_path)[1].lower()
        language = self.language_map.get(file_ext)
        
        if not language:
            self.issues['General Errors'].append(f"Unsupported file type: {file_ext}")
            return {'issues': self.issues, 'metrics': self.metrics, 'file_path': file_path}

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

            if language == 'python':
                self._analyze_python(code)
            elif language == 'java':
                self._analyze_java(code)
            elif language == 'c':
                self._analyze_c(code)
            elif language == 'cpp':
                self._analyze_cpp(code)

        except Exception as e:
            self.issues['General Errors'].append(f"Error analyzing file: {str(e)}")

        non_empty = {k: v for k, v in self.issues.items() if v}
        return {'issues': non_empty, 'metrics': self.metrics, 'file_path': file_path, 'language': language}

    def analyze_directory(self, directory: str) -> List[Dict[str, Any]]:
        results = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in self.language_map:
                    results.append(self.analyze_file(os.path.join(root, file)))
        return results

    def _analyze_python(self, code: str):
        """Analyze Python code using AST."""
        try:
            tree = ast.parse(code)
            self._check_complexity(tree)
            self._calculate_metrics(tree, code)
            self._check_unused_variables(tree)
            
            if 'time_complexity' not in self.metrics:
                self.metrics['time_complexity'] = {'overall': 'O(1)', 'functions': {}}
            
            # Add space complexity analysis
            space_complexity = self._calculate_space_complexity(tree)
            self.metrics['space_complexity'] = space_complexity
                
        except SyntaxError as e:
            self.issues['Syntax Errors'].append(f"Line {e.lineno}: {e.msg}")

    def _analyze_java(self, code: str):
        """Analyze Java code using regex patterns."""
        self._calculate_basic_metrics(code, 'java')
        self._analyze_java_patterns(code)
        self._estimate_complexity_from_text(code, 'java')
        self._estimate_space_complexity_from_text(code, 'java')

    def _analyze_c(self, code: str):
        """Analyze C code using regex patterns."""
        self._calculate_basic_metrics(code, 'c')
        self._analyze_c_patterns(code)
        self._estimate_complexity_from_text(code, 'c')
        self._estimate_space_complexity_from_text(code, 'c')

    def _analyze_cpp(self, code: str):
        """Analyze C++ code using regex patterns."""
        self._calculate_basic_metrics(code, 'cpp')
        self._analyze_cpp_patterns(code)
        self._estimate_complexity_from_text(code, 'cpp')
        self._estimate_space_complexity_from_text(code, 'cpp')

    def _calculate_basic_metrics(self, code: str, language: str):
        """Calculate basic metrics for any language."""
        lines = code.split('\n')
        self.metrics['lines_of_code'] = len(lines)
        
        # Comment patterns by language
        comment_patterns = {
            'java': [r'//.*', r'/\*[\s\S]*?\*/'],
            'c': [r'//.*', r'/\*[\s\S]*?\*/'],
            'cpp': [r'//.*', r'/\*[\s\S]*?\*/']
        }
        
        comment_lines = 0
        if language in comment_patterns:
            for pattern in comment_patterns[language]:
                comment_lines += len(re.findall(pattern, code, re.MULTILINE))
        
        self.metrics['comment_lines'] = comment_lines
        self.metrics['blank_lines'] = sum(1 for line in lines if not line.strip())

    def _analyze_java_patterns(self, code: str):
        """Analyze Java-specific patterns."""
        # Check for common issues
        if re.search(r'System\.out\.print', code):
            self.issues['Best Practices'].append("Consider using a logging framework instead of System.out.print")
        
        # Check for proper exception handling
        try_blocks = len(re.findall(r'\btry\s*\{', code))
        catch_blocks = len(re.findall(r'\bcatch\s*\(', code))
        if try_blocks > catch_blocks:
            self.issues['Exception Handling'].append("Try blocks without corresponding catch blocks detected")
        
        # Check for magic numbers
        magic_numbers = re.findall(r'\b(?<![\w.])\d+(?![\w.])\b', code)
        if len(magic_numbers) > 5:
            self.issues['Code Quality'].append(f"Consider using constants for magic numbers: {set(magic_numbers)}")

    def _analyze_c_patterns(self, code: str):
        """Analyze C-specific patterns."""
        # Check for memory management
        malloc_count = len(re.findall(r'\bmalloc\s*\(', code))
        free_count = len(re.findall(r'\bfree\s*\(', code))
        if malloc_count > free_count:
            self.issues['Memory Management'].append(f"Potential memory leak: {malloc_count} malloc calls but only {free_count} free calls")
        
        # Check for buffer overflow risks
        if re.search(r'\bstrcpy\s*\(', code):
            self.issues['Security'].append("strcpy() can cause buffer overflows, consider using strncpy()")
        if re.search(r'\bgets\s*\(', code):
            self.issues['Security'].append("gets() is unsafe, use fgets() instead")

    def _analyze_cpp_patterns(self, code: str):
        """Analyze C++-specific patterns."""
        # Include C patterns
        self._analyze_c_patterns(code)
        
        # Check for modern C++ features
        if re.search(r'\braw\s+pointer', code) and not re.search(r'\bstd::(unique_ptr|shared_ptr)', code):
            self.issues['Modern C++'].append("Consider using smart pointers instead of raw pointers")
        
        # Check for range-based for loops opportunity
        traditional_loops = len(re.findall(r'\bfor\s*\(\s*\w+\s*=\s*0\s*;.*\.size\(\)', code))
        if traditional_loops > 0:
            self.issues['Modern C++'].append("Consider using range-based for loops for better readability")

    def _estimate_complexity_from_text(self, code: str, language: str):
        """Estimate time complexity from text patterns."""
        # Count nested loops
        nested_depth = 0
        max_depth = 0
        current_depth = 0
        
        # Pattern matching for different languages
        if language in ['java', 'c', 'cpp']:
            for_pattern = r'\bfor\s*\('
            while_pattern = r'\bwhile\s*\('
            brace_open = r'\{'
            brace_close = r'\}'
        
        # Simple heuristic: count loop nesting
        lines = code.split('\n')
        for line in lines:
            stripped = line.strip()
            if re.search(for_pattern, stripped) or re.search(while_pattern, stripped):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif stripped.endswith('}') and current_depth > 0:
                current_depth = max(0, current_depth - 1)
        
        # Estimate complexity based on max nesting
        if max_depth == 0:
            complexity = 'O(1)'
        elif max_depth == 1:
            complexity = 'O(n)'
        elif max_depth == 2:
            complexity = 'O(n²)'
        else:
            complexity = 'O(n³+)'
        
        # Check for sorting algorithms
        if re.search(r'\bsort\s*\(', code) or re.search(r'\.sort\s*\(', code):
            complexity = 'O(n log n)' if complexity == 'O(1)' else complexity
        
        self.metrics['time_complexity'] = {'overall': complexity, 'estimated': True}

    def _calculate_space_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        """Calculate space complexity for Python code using AST analysis."""
        complexities = {}

        # Analyze all functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                complexities[func_name] = self._analyze_function_space_complexity(node)

        # Analyze top-level (module-level) code
        top_level_space_complexity = self._analyze_function_space_complexity(tree)

        # If no functions and top-level space complexity is O(1), return O(1)
        if not complexities and top_level_space_complexity == 'O(1)':
            return {'overall': 'O(1)', 'functions': {}}

        # Add top-level space complexity with special key if not trivial
        if top_level_space_complexity != 'O(1)':
            complexities['<module-level>'] = top_level_space_complexity

        max_space_complexity = max(complexities.values(), key=self._complexity_weight)
        return {'overall': max_space_complexity, 'functions': complexities}

    def _analyze_function_space_complexity(self, node: ast.AST) -> str:
        """Analyze space complexity of a function or module."""
        def space_complexity_of_nodes(nodes: List[ast.AST], recursion_depth=0) -> str:
            max_space_complexity = 'O(1)'

            for n in nodes:
                if isinstance(n, ast.Assign):
                    # Check for data structure allocations
                    for target in n.targets:
                        if isinstance(target, ast.Name):
                            space_from_value = self._analyze_value_space_complexity(n.value)
                            max_space_complexity = self._upgrade_complexity(max_space_complexity, space_from_value)
                
                elif isinstance(n, (ast.For, ast.While)):
                    # Check if we're creating data structures in loops
                    body_space = space_complexity_of_nodes(list(ast.iter_child_nodes(n)), recursion_depth)
                    
                    # If body allocates space, multiply by loop factor
                    if body_space != 'O(1)':
                        loop_space = self._combine_complexities('O(n)', body_space)
                        max_space_complexity = self._upgrade_complexity(max_space_complexity, loop_space)
                    else:
                        # Check for accumulating data structures
                        if self._has_accumulating_operations(n):
                            max_space_complexity = self._upgrade_complexity(max_space_complexity, 'O(n)')
                
                elif isinstance(n, ast.FunctionDef):
                    # Recursion analysis
                    if self._is_recursive_function(n):
                        recursive_space = self._analyze_recursive_space(n)
                        max_space_complexity = self._upgrade_complexity(max_space_complexity, recursive_space)
                
                elif isinstance(n, ast.Call):
                    call_space = self._analyze_call_space_complexity(n)
                    max_space_complexity = self._upgrade_complexity(max_space_complexity, call_space)
                
                else:
                    # Recursively analyze child nodes
                    children = list(ast.iter_child_nodes(n))
                    if children:
                        child_space = space_complexity_of_nodes(children, recursion_depth)
                        max_space_complexity = self._upgrade_complexity(max_space_complexity, child_space)

            return max_space_complexity

        return space_complexity_of_nodes(node.body if hasattr(node, 'body') else [])

    def _analyze_value_space_complexity(self, value_node: ast.AST) -> str:
        """Analyze space complexity of value assignments."""
        if isinstance(value_node, ast.List):
            return 'O(n)' if len(value_node.elts) == 0 else 'O(1)'  # Empty list might grow, literal list is O(1)
        elif isinstance(value_node, ast.Dict):
            return 'O(n)' if len(value_node.keys) == 0 else 'O(1)'   # Empty dict might grow, literal dict is O(1)
        elif isinstance(value_node, ast.Set):
            return 'O(n)' if len(value_node.elts) == 0 else 'O(1)'   # Empty set might grow, literal set is O(1)
        elif isinstance(value_node, ast.ListComp):
            return 'O(n)'  # List comprehensions create O(n) space
        elif isinstance(value_node, ast.DictComp):
            return 'O(n)'  # Dict comprehensions create O(n) space
        elif isinstance(value_node, ast.SetComp):
            return 'O(n)'  # Set comprehensions create O(n) space
        elif isinstance(value_node, ast.Call):
            return self._analyze_call_space_complexity(value_node)
        
        return 'O(1)'

    def _analyze_call_space_complexity(self, call_node: ast.Call) -> str:
        """Analyze space complexity of function calls."""
        if isinstance(call_node.func, ast.Name):
            func_name = call_node.func.id
            # Built-in functions that create data structures
            if func_name in ['list', 'dict', 'set', 'tuple']:
                return 'O(n)'
            elif func_name in ['range']:
                return 'O(1)'  # range is lazy in Python 3
            elif func_name in ['sorted']:
                return 'O(n)'  # sorted creates a new list
        elif isinstance(call_node.func, ast.Attribute):
            attr_name = call_node.func.attr
            # Method calls that might create space
            if attr_name in ['copy', 'deepcopy']:
                return 'O(n)'
            elif attr_name in ['split', 'splitlines']:
                return 'O(n)'
            elif attr_name in ['keys', 'values', 'items']:
                return 'O(n)'
        
        return 'O(1)'

    def _has_accumulating_operations(self, loop_node: ast.AST) -> bool:
        """Check if a loop has operations that accumulate data."""
        for node in ast.walk(loop_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['append', 'extend', 'add', 'update', 'insert']:
                        return True
        return False

    def _is_recursive_function(self, func_node: ast.FunctionDef) -> bool:
        """Check if a function is recursive."""
        func_name = func_node.name
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == func_name:
                    return True
        return False

    def _analyze_recursive_space(self, func_node: ast.FunctionDef) -> str:
        """Analyze space complexity of recursive functions."""
        # Simple heuristic: check if it's tail recursive or creates new data structures
        max_depth = 0
        creates_data_structures = False
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)):
                creates_data_structures = True
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == func_node.name:
                    max_depth += 1
        
        if creates_data_structures:
            return 'O(n²)'  # Each recursive call creates data structures
        else:
            return 'O(n)'   # Just the call stack
    
    def _estimate_space_complexity_from_text(self, code: str, language: str):
        """Estimate space complexity from text patterns for non-Python languages."""
        space_complexity = 'O(1)'
        
        if language in ['java', 'c', 'cpp']:
            # Check for array/collection allocations
            if re.search(r'new\s+\w+\s*\[', code) or re.search(r'malloc\s*\(', code):
                space_complexity = 'O(n)'
            
            # Check for data structure usage
            if re.search(r'(ArrayList|Vector|HashMap|HashSet|LinkedList)', code):
                space_complexity = 'O(n)'
            
            # Check for recursive patterns
            recursive_patterns = re.findall(r'(\w+)\s*\([^)]*\)\s*\{[^}]*\1\s*\(', code)
            if recursive_patterns:
                space_complexity = 'O(n)'
            
            # Check for nested data structures
            if re.search(r'new\s+\w+\s*\[\s*\]\s*\[\s*\]', code):  # 2D arrays
                space_complexity = 'O(n²)'
            
            # Check for dynamic memory allocation in loops
            lines = code.split('\n')
            in_loop = False
            loop_depth = 0
            for line in lines:
                stripped = line.strip()
                if re.search(r'\b(for|while)\s*\(', stripped):
                    in_loop = True
                    loop_depth += 1
                elif stripped.endswith('}') and in_loop:
                    loop_depth = max(0, loop_depth - 1)
                    if loop_depth == 0:
                        in_loop = False
                elif in_loop and (re.search(r'new\s+\w+', stripped) or re.search(r'malloc\s*\(', stripped)):
                    if loop_depth == 1:
                        space_complexity = self._upgrade_complexity(space_complexity, 'O(n)')
                    elif loop_depth >= 2:
                        space_complexity = self._upgrade_complexity(space_complexity, 'O(n²)')
        
        self.metrics['space_complexity'] = {'overall': space_complexity, 'estimated': True}

    def _check_complexity(self, tree: ast.AST):
        complexity = self._calculate_time_complexity(tree)
        self.metrics['time_complexity'] = complexity

    def _calculate_metrics(self, tree: ast.AST, code: str):
        lines = code.split('\n')
        self.metrics['lines_of_code'] = len(lines)
        self.metrics['comment_lines'] = sum(1 for l in lines if l.strip().startswith('#'))
    
    def _calculate_time_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        complexities = {}

        # Analyze all functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                complexities[func_name] = self._analyze_function_complexity(node)

        # Analyze top-level (module-level) code
        top_level_complexity = self._analyze_function_complexity(tree)

        # If no functions and top-level complexity is O(1), return O(1)
        if not complexities and top_level_complexity == 'O(1)':
            return {'overall': 'O(1)', 'functions': {}}

        # Add top-level complexity with special key if not trivial
        if top_level_complexity != 'O(1)':
            complexities['<module-level>'] = top_level_complexity

        max_complexity = max(complexities.values(), key=self._complexity_weight)
        return {'overall': max_complexity, 'functions': complexities}

    def _analyze_function_complexity(self, node: ast.AST) -> str:
        # Recursively calculate complexity of node list (body) considering sequential and nested loops
        def complexity_of_nodes(nodes: List[ast.AST], current_depth=0) -> str:
            max_seq_complexity = 'O(1)'

            for n in nodes:
                if isinstance(n, (ast.For, ast.While)):
                    body_complexity = complexity_of_nodes(list(ast.iter_child_nodes(n)), current_depth + 1)
                    loop_complexity = self._complexity_at_depth(current_depth + 1)
                    combined = self._combine_complexities(loop_complexity, body_complexity)
                    max_seq_complexity = self._upgrade_complexity(max_seq_complexity, combined)
                elif isinstance(n, ast.If):
                    body_complexity = complexity_of_nodes(n.body, current_depth)
                    orelse_complexity = complexity_of_nodes(n.orelse, current_depth) if n.orelse else 'O(1)'
                    if_complexity = self._upgrade_complexity(body_complexity, orelse_complexity)
                    max_seq_complexity = self._upgrade_complexity(max_seq_complexity, if_complexity)
                elif isinstance(n, ast.Call):
                    call_complexity = 'O(1)'
                    if isinstance(n.func, ast.Name) and n.func.id == 'sorted':
                        call_complexity = 'O(n log n)'
                    elif isinstance(n.func, ast.Attribute) and n.func.attr == 'sort':
                        call_complexity = 'O(n log n)'
                    max_seq_complexity = self._upgrade_complexity(max_seq_complexity, call_complexity)
                else:
                    children = list(ast.iter_child_nodes(n))
                    if children:
                        child_complexity = complexity_of_nodes(children, current_depth)
                        max_seq_complexity = self._upgrade_complexity(max_seq_complexity, child_complexity)

            return max_seq_complexity

        # node can be ast.FunctionDef or ast.Module (both have .body)
        return complexity_of_nodes(node.body if hasattr(node, 'body') else [])

    def _complexity_at_depth(self, depth: int) -> str:
        if depth == 0:
            return 'O(1)'
        elif depth == 1:
            return 'O(n)'
        elif depth == 2:
            return 'O(n²)'
        else:
            return 'O(n³+)'

    def _combine_complexities(self, c1: str, c2: str) -> str:
        order = ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n²)', 'O(n³+)', 'O(n!)']

        def weight(c): return order.index(c) if c in order else 0

        if c1 == 'O(1)':
            return c2
        if c2 == 'O(1)':
            return c1

        # For simplicity, take the max complexity
        return max(c1, c2, key=weight)

    def _upgrade_complexity(self, current: str, new: str) -> str:
        order = ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n²)', 'O(n³+)', 'O(n!)']
        return max([current, new], key=lambda c: order.index(c))

    def _complexity_weight(self, complexity: str) -> int:
        weights = {'O(1)': 0, 'O(log n)': 1, 'O(n)': 2,
                   'O(n log n)': 3, 'O(n²)': 4, 'O(n³+)': 5, 'O(n!)': 6}
        return weights.get(complexity, 0)

    def _check_unused_variables(self, tree: ast.AST):
        used_vars = set()
        defined_vars = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                defined_vars.add(node.id)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_vars.add(node.id)

        for var in (defined_vars - used_vars):
            self.issues['Unused Variables'].append(f"Unused variable: {var}")
