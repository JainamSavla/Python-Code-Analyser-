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
            
            # Ensure time complexity is set
            if 'time_complexity' not in self.metrics:
                self.metrics['time_complexity'] = {'overall': 'O(1)', 'functions': {}}
            
            # Ensure space complexity is set
            if 'space_complexity' not in self.metrics:
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
                
                # Check if function is recursive first
                if self._is_recursive_function(node):
                    complexities[func_name] = self._analyze_recursive_space(node)
                else:
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
        def space_complexity_of_nodes(nodes: List[ast.AST], loop_depth=0) -> str:
            max_space_complexity = 'O(1)'

            for n in nodes:
                if isinstance(n, ast.Assign):
                    # Check for data structure allocations
                    for target in n.targets:
                        if isinstance(target, ast.Name):
                            space_from_value = self._analyze_value_space_complexity(n.value, loop_depth)
                            max_space_complexity = self._upgrade_complexity(max_space_complexity, space_from_value)
                
                elif isinstance(n, (ast.For, ast.While)):
                    # Analyze space used in loop body with increased depth
                    body_space = space_complexity_of_nodes(list(ast.iter_child_nodes(n)), loop_depth + 1)
                    
                    # Check for accumulating data structures in this loop
                    if self._has_accumulating_operations(n):
                        # Space grows with loop iterations
                        accumulating_space = self._space_at_depth(loop_depth + 1)
                        max_space_complexity = self._upgrade_complexity(max_space_complexity, accumulating_space)
                    
                    # Combine with body space complexity
                    if body_space != 'O(1)':
                        max_space_complexity = self._upgrade_complexity(max_space_complexity, body_space)
                
                elif isinstance(n, ast.FunctionDef):
                    # Handle recursive functions (but don't double-count if this is the main function)
                    if n != node and self._is_recursive_function(n):
                        recursive_space = self._analyze_recursive_space(n)
                        max_space_complexity = self._upgrade_complexity(max_space_complexity, recursive_space)
                
                elif isinstance(n, ast.Call):
                    call_space = self._analyze_call_space_complexity(n)
                    max_space_complexity = self._upgrade_complexity(max_space_complexity, call_space)
                
                else:
                    # Recursively analyze child nodes
                    children = list(ast.iter_child_nodes(n))
                    if children:
                        child_space = space_complexity_of_nodes(children, loop_depth)
                        max_space_complexity = self._upgrade_complexity(max_space_complexity, child_space)

            return max_space_complexity

        # For recursive functions, handle them specially
        if hasattr(node, 'name') and self._is_recursive_function(node):
            return self._analyze_recursive_space(node)
        
        # Otherwise, analyze the node body normally
        return space_complexity_of_nodes(node.body if hasattr(node, 'body') else [])
    
    def _space_at_depth(self, depth: int) -> str:
        """Return space complexity for given loop nesting depth."""
        if depth == 1:
            return 'O(n)'
        elif depth == 2:
            return 'O(n²)'
        elif depth == 3:
            return 'O(n³)'
        else:
            return 'O(n³+)'

    def _analyze_value_space_complexity(self, value_node: ast.AST, loop_depth: int = 0) -> str:
        """Analyze space complexity of value assignments."""
        base_space = 'O(1)'
        
        if isinstance(value_node, ast.List):
            if len(value_node.elts) == 0:
                base_space = 'O(n)'  # Empty list might grow
            else:
                base_space = 'O(1)'  # Literal list is constant size
        elif isinstance(value_node, ast.Dict):
            if len(value_node.keys) == 0:
                base_space = 'O(n)'  # Empty dict might grow
            else:
                base_space = 'O(1)'  # Literal dict is constant size
        elif isinstance(value_node, ast.Set):
            if len(value_node.elts) == 0:
                base_space = 'O(n)'  # Empty set might grow
            else:
                base_space = 'O(1)'  # Literal set is constant size
        elif isinstance(value_node, ast.ListComp):
            base_space = 'O(n)'  # List comprehensions create O(n) space
        elif isinstance(value_node, ast.DictComp):
            base_space = 'O(n)'  # Dict comprehensions create O(n) space
        elif isinstance(value_node, ast.SetComp):
            base_space = 'O(n)'  # Set comprehensions create O(n) space
        elif isinstance(value_node, ast.Call):
            base_space = self._analyze_call_space_complexity(value_node)
        
        # If we're inside nested loops and creating data structures, multiply complexity
        if base_space != 'O(1)' and loop_depth > 0:
            return self._space_at_depth(loop_depth)
        
        return base_space

    def _analyze_recursive_space(self, func_node: ast.FunctionDef) -> str:
        """Analyze space complexity of recursive functions."""
        func_name = func_node.name
        
        # Count recursive calls and analyze patterns
        recursive_calls = 0
        creates_data_structures = False
        divides_problem = False
        has_slicing = False
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == func_name:
                    recursive_calls += 1
            
            # Check if creates new data structures
            elif isinstance(node, (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)):
                creates_data_structures = True
            
            # Look for problem division patterns (slicing)
            elif isinstance(node, ast.Subscript):
                if isinstance(node.slice, ast.Slice):
                    divides_problem = True
                    has_slicing = True
            
            # Look for halving patterns like mid = len(arr) // 2
            elif isinstance(node, ast.Assign):
                if isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.FloorDiv):
                    if isinstance(node.value.right, ast.Constant) and node.value.right.value == 2:
                        divides_problem = True
        
        # Heuristics for recursive space complexity
        if creates_data_structures:
            if divides_problem and has_slicing:
                return 'O(n)'        # Divide and conquer with copying (like merge sort)
            else:
                return 'O(n²)'       # Each recursive call creates data structures
        else:
            # Only using call stack space
            if divides_problem:
                return 'O(log n)'    # Binary search-like recursion (log depth)
            elif recursive_calls == 1:
                return 'O(n)'        # Linear recursion depth
            else:
                return 'O(n²)'       # Fibonacci-like recursion

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
                
                # Check if function is recursive first
                if self._is_recursive_function(node):
                    complexities[func_name] = self._analyze_recursive_complexity(node)
                else:
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
                    # Check if this is a logarithmic loop (dividing/halving pattern)
                    if self._is_logarithmic_loop(n):
                        loop_complexity = 'O(log n)'
                        body_complexity = complexity_of_nodes(list(ast.iter_child_nodes(n)), 0)  # Don't increase depth for log loops
                        combined = self._combine_complexities(loop_complexity, body_complexity)
                    else:
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
                    call_complexity = self._analyze_call_complexity(n)
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
        elif depth == 3:
            return 'O(n³)'
        else:
            return 'O(n³+)'
    
    def _is_logarithmic_loop(self, loop_node: ast.AST) -> bool:
        """Detect logarithmic loops (dividing/halving patterns)."""
        # Look for patterns where loop variable is divided by 2 or similar
        for node in ast.walk(loop_node):
            if isinstance(node, ast.AugAssign):
                # Check for //= 2, /= 2, >>= 1 patterns
                if isinstance(node.op, (ast.FloorDiv, ast.Div, ast.RShift)):
                    if isinstance(node.value, ast.Constant):
                        if node.value.value in [2, 1]:  # Division by 2 or right shift by 1
                            return True
            elif isinstance(node, ast.Assign):
                # Check for patterns like: mid = (left + right) // 2
                if isinstance(node.value, ast.BinOp):
                    if isinstance(node.value.op, ast.FloorDiv):
                        if isinstance(node.value.right, ast.Constant) and node.value.right.value == 2:
                            return True
                    # Check for left/right pointer updates in binary search
                    elif isinstance(node.value.op, (ast.Add, ast.Sub)):
                        # Pattern: left = mid + 1, right = mid - 1
                        if isinstance(node.value.right, ast.Constant) and node.value.right.value == 1:
                            return True
            elif isinstance(node, ast.While):
                # Check condition for binary search patterns
                if isinstance(node.test, ast.Compare):
                    # Look for left <= right or similar patterns
                    for op in node.test.ops:
                        if isinstance(op, (ast.LtE, ast.Lt, ast.GtE, ast.Gt)):
                            return True
        return False
    
    def _analyze_call_complexity(self, call_node: ast.Call) -> str:
        """Analyze complexity of function calls."""
        # Built-in function complexities
        if isinstance(call_node.func, ast.Name):
            func_name = call_node.func.id
            builtin_complexities = {
                'sorted': 'O(n log n)',
                'max': 'O(n)',
                'min': 'O(n)',
                'sum': 'O(n)',
                'len': 'O(1)',
                'abs': 'O(1)',
                'int': 'O(1)',
                'float': 'O(1)',
                'str': 'O(1)',
                'list': 'O(n)',  # Converting to list
                'tuple': 'O(n)',  # Converting to tuple
                'set': 'O(n)',   # Converting to set
                'dict': 'O(n)',  # Converting to dict
                'enumerate': 'O(1)',  # Iterator creation is O(1)
                'zip': 'O(1)',    # Iterator creation is O(1)
                'range': 'O(1)',  # range is lazy
                'reversed': 'O(1)',  # Iterator creation is O(1)
            }
            return builtin_complexities.get(func_name, 'O(1)')
            
        elif isinstance(call_node.func, ast.Attribute):
            attr_name = call_node.func.attr
            method_complexities = {
                'sort': 'O(n log n)',
                'append': 'O(1)',
                'pop': 'O(1)',
                'insert': 'O(n)',
                'remove': 'O(n)',
                'index': 'O(n)',
                'count': 'O(n)',
                'reverse': 'O(n)',
                'copy': 'O(n)',
                'clear': 'O(1)',
                'extend': 'O(k)',  # k is length of extended iterable
                'split': 'O(n)',
                'join': 'O(n)',
                'replace': 'O(n)',
                'strip': 'O(n)',
                'find': 'O(n)',
                'get': 'O(1)',     # dict.get
                'keys': 'O(1)',    # returns view, not copy
                'values': 'O(1)',  # returns view, not copy
                'items': 'O(1)',   # returns view, not copy
                'update': 'O(k)',  # k is size of update
            }
            return method_complexities.get(attr_name, 'O(1)')
        
        return 'O(1)'
    
    def _analyze_recursive_complexity(self, func_node: ast.FunctionDef) -> str:
        """Analyze complexity of recursive functions."""
        func_name = func_node.name
        
        # Count recursive calls and analyze patterns
        recursive_calls = 0
        divides_problem = False
        has_slicing = False
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == func_name:
                    recursive_calls += 1
            
            # Look for problem division patterns (slicing)
            elif isinstance(node, ast.Subscript):
                if isinstance(node.slice, ast.Slice):
                    divides_problem = True
                    has_slicing = True
            
            # Look for halving patterns like mid = len(arr) // 2
            elif isinstance(node, ast.Assign):
                if isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.FloorDiv):
                    if isinstance(node.value.right, ast.Constant) and node.value.right.value == 2:
                        divides_problem = True
        
        # Heuristics for recursive complexity
        if recursive_calls == 1:
            if divides_problem:
                return 'O(n)'        # Simple divide and conquer like factorial
            else:
                return 'O(n)'        # Linear recursion
        elif recursive_calls == 2:
            if divides_problem and has_slicing:
                return 'O(n log n)'  # Divide and conquer like merge sort
            elif divides_problem:
                return 'O(log n)'    # Binary search-like recursion
            else:
                return 'O(n²)'       # Fibonacci-like recursion
        else:
            return 'O(n³+)'          # Multiple recursive calls
    
    def _is_recursive_function(self, func_node: ast.FunctionDef) -> bool:
        """Check if a function is recursive - improved version."""
        func_name = func_node.name
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == func_name:
                    return True
                # Check for indirect recursion through other functions that might call this function
                elif isinstance(node.func, ast.Attribute) and hasattr(node.func, 'id'):
                    if node.func.id == func_name:
                        return True
        return False
    
    def _combine_complexities(self, c1: str, c2: str) -> str:
        order = ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n²)', 'O(n³)', 'O(n³+)', 'O(n!)']

        def weight(c): return order.index(c) if c in order else 0

        if c1 == 'O(1)':
            return c2
        if c2 == 'O(1)':
            return c1

        # For multiplication of complexities (nested loops)
        # Note: This should only happen when we have true nesting, not sequential operations
        if (c1 == 'O(n)' and c2 == 'O(log n)') or (c1 == 'O(log n)' and c2 == 'O(n)'):
            return 'O(n log n)'
        
        # For sequential operations (not nested), take the maximum
        return max(c1, c2, key=weight)

    def _upgrade_complexity(self, current: str, new: str) -> str:
        order = ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n²)', 'O(n³)', 'O(n³+)', 'O(n!)']
        return max([current, new], key=lambda c: order.index(c) if c in order else 0)

    def _complexity_weight(self, complexity: str) -> int:
        weights = {'O(1)': 0, 'O(log n)': 1, 'O(n)': 2,
                   'O(n log n)': 3, 'O(n²)': 4, 'O(n³)': 5, 'O(n³+)': 6, 'O(n!)': 7}
        return weights.get(complexity, 0)

    def get_detailed_complexity_data(self, file_path: str) -> Dict[str, Any]:
        """Get detailed complexity data suitable for visualization."""
        result = self.analyze_file(file_path)
        metrics = result.get('metrics', {})
        
        # Extract detailed information for visualization
        detailed_data = {
            'file_path': file_path,
            'language': result.get('language', 'unknown'),
            'lines_of_code': metrics.get('lines_of_code', 0),
            'comment_lines': metrics.get('comment_lines', 0),
            'time_complexity': metrics.get('time_complexity', {}),
            'space_complexity': metrics.get('space_complexity', {}),
            'issues_count': sum(len(msgs) for msgs in result.get('issues', {}).values()),
            'issue_types': list(result.get('issues', {}).keys()),
            'code_quality_score': self._calculate_quality_score(metrics, result.get('issues', {}))
        }
        
        return detailed_data
    
    def _calculate_quality_score(self, metrics: Dict[str, Any], issues: Dict[str, List[str]]) -> float:
        """Calculate a simple code quality score (0-100)."""
        score = 100.0
        
        # Deduct points for issues
        issue_count = sum(len(msgs) for msgs in issues.values())
        score -= min(50, issue_count * 5)  # Max 50 points deduction for issues
        
        # Deduct points for poor complexity
        time_comp = metrics.get('time_complexity', {}).get('overall', 'O(1)')
        space_comp = metrics.get('space_complexity', {}).get('overall', 'O(1)')
        
        complexity_penalties = {
            'O(1)': 0, 'O(log n)': 2, 'O(n)': 5, 
            'O(n log n)': 10, 'O(n²)': 20, 'O(n³+)': 30, 'O(n!)': 40
        }
        
        score -= complexity_penalties.get(time_comp, 0)
        score -= complexity_penalties.get(space_comp, 0)
        
        # Add points for good comment ratio
        loc = metrics.get('lines_of_code', 1)
        comment_ratio = metrics.get('comment_lines', 0) / loc
        score += min(10, comment_ratio * 50)  # Max 10 bonus points
        
        return max(0.0, min(100.0, score))
    
    def analyze_directory_detailed(self, directory: str) -> Dict[str, Any]:
        """Analyze directory and return detailed data suitable for visualization."""
        results = self.analyze_directory(directory)
        detailed_results = []
        
        for result in results:
            file_path = result['file_path']
            detailed_data = {
                'file_path': file_path,
                'language': result.get('language', 'unknown'),
                'metrics': result.get('metrics', {}),
                'issues': result.get('issues', {}),
                'detailed': self._extract_detailed_metrics(result)
            }
            detailed_results.append(detailed_data)
        
        # Calculate summary statistics
        summary = self._calculate_directory_summary(detailed_results)
        
        return {
            'files': detailed_results,
            'summary': summary,
            'total_files': len(detailed_results)
        }
    
    def _extract_detailed_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed metrics from analysis result."""
        metrics = result.get('metrics', {})
        issues = result.get('issues', {})
        
        return {
            'quality_score': self._calculate_quality_score(metrics, issues),
            'complexity_score': self._calculate_complexity_score(metrics),
            'maintainability_score': self._calculate_maintainability_score(metrics),
            'issue_density': self._calculate_issue_density(metrics, issues)
        }
    
    def _calculate_complexity_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall complexity score (0-100, lower is better)."""
        time_comp = metrics.get('time_complexity', {}).get('overall', 'O(1)')
        space_comp = metrics.get('space_complexity', {}).get('overall', 'O(1)')
        
        complexity_scores = {
            'O(1)': 10, 'O(log n)': 20, 'O(n)': 30, 
            'O(n log n)': 50, 'O(n²)': 70, 'O(n³+)': 90, 'O(n!)': 100
        }
        
        time_score = complexity_scores.get(time_comp, 10)
        space_score = complexity_scores.get(space_comp, 10)
        
        return (time_score + space_score) / 2
    
    def _calculate_maintainability_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate maintainability score (0-100, higher is better)."""
        loc = metrics.get('lines_of_code', 1)
        comment_lines = metrics.get('comment_lines', 0)
        
        # Base score
        score = 70.0
        
        # Comment ratio bonus
        comment_ratio = comment_lines / loc if loc > 0 else 0
        score += min(20, comment_ratio * 100)  # Max 20 points for good comments
        
        # Penalize very long files
        if loc > 500:
            score -= min(30, (loc - 500) / 50)  # Penalize long files
        
        # Small bonus for moderate file length
        if 50 <= loc <= 200:
            score += 10
        
        return max(0.0, min(100.0, score))
    
    def _calculate_issue_density(self, metrics: Dict[str, Any], issues: Dict[str, List[str]]) -> float:
        """Calculate issue density (issues per 100 lines of code)."""
        loc = metrics.get('lines_of_code', 1)
        issue_count = sum(len(msgs) for msgs in issues.values())
        
        return (issue_count / loc) * 100 if loc > 0 else 0
    
    def _calculate_directory_summary(self, detailed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for a directory analysis."""
        if not detailed_results:
            return {}
        
        total_files = len(detailed_results)
        
        # Language distribution
        languages = {}
        total_loc = 0
        total_issues = 0
        complexity_distribution = {'time': {}, 'space': {}}
        quality_scores = []
        
        for result in detailed_results:
            lang = result.get('language', 'unknown')
            languages[lang] = languages.get(lang, 0) + 1
            
            metrics = result.get('metrics', {})
            total_loc += metrics.get('lines_of_code', 0)
            total_issues += sum(len(msgs) for msgs in result.get('issues', {}).values())
            
            # Track complexity distribution
            time_comp = metrics.get('time_complexity', {}).get('overall', 'O(1)')
            space_comp = metrics.get('space_complexity', {}).get('overall', 'O(1)')
            
            complexity_distribution['time'][time_comp] = complexity_distribution['time'].get(time_comp, 0) + 1
            complexity_distribution['space'][space_comp] = complexity_distribution['space'].get(space_comp, 0) + 1
            
            # Quality scores
            quality_scores.append(result.get('detailed', {}).get('quality_score', 0))
        
        return {
            'total_files': total_files,
            'languages': languages,
            'total_lines_of_code': total_loc,
            'total_issues': total_issues,
            'average_quality_score': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            'complexity_distribution': complexity_distribution,
            'issue_density': (total_issues / total_loc * 100) if total_loc > 0 else 0
        }

    def _check_unused_variables(self, tree: ast.AST):
        """Check for unused variables in Python code."""
        used_vars = set()
        defined_vars = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                defined_vars.add(node.id)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_vars.add(node.id)

        for var in (defined_vars - used_vars):
            self.issues['Unused Variables'].append(f"Unused variable: {var}")
