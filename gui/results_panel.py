import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Optional, Dict, Any, List

class ResultsPanel(ttk.Notebook):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._setup_tabs()
        
    def _setup_tabs(self):
        """Initialize the tabs for different result types."""
        # Preview tab
        self.preview_tab = ttk.Frame(self)
        self.preview_text = ScrolledText(
            self.preview_tab, wrap=tk.WORD, font=('Consolas', 10)
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.add(self.preview_tab, text="Preview")
        
        # Issues tab
        self.issues_tab = ttk.Frame(self)
        self.issues_tree = ttk.Treeview(
            self.issues_tab, columns=('type', 'message'), show='headings'
        )
        self.issues_tree.heading('type', text='Issue Type')
        self.issues_tree.heading('message', text='Message')
        self.issues_tree.column('type', width=150)
        scrollbar = ttk.Scrollbar(
            self.issues_tab, orient="vertical", command=self.issues_tree.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.issues_tree.configure(yscrollcommand=scrollbar.set)
        self.issues_tree.pack(fill=tk.BOTH, expand=True)
        self.add(self.issues_tab, text="Issues")
        
        # Metrics tab
        self.metrics_tab = ttk.Frame(self)
        self.metrics_text = ScrolledText(
            self.metrics_tab, wrap=tk.WORD, font=('Consolas', 10)
        )
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        self.add(self.metrics_tab, text="Metrics")
        
    def preview_file(self, file_path: str):
        """Preview the content of a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.preview_text.config(state=tk.NORMAL)
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(tk.END, content)
                self.preview_text.config(state=tk.DISABLED)
                self.select(self.preview_tab)
        except Exception as e:
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"Error loading file: {str(e)}")
            self.preview_text.config(state=tk.DISABLED)
            
    def display_results(self, results: Dict[str, Any]):
        """Display analysis results."""
        self._display_issues(results.get('issues', {}))
        self._display_metrics(results.get('metrics', {}), results.get('language', 'unknown'))
        
    def display_multiple_results(self, results: List[Dict[str, Any]]):
        """Display results from multiple files."""
        # Clear previous results
        self.issues_tree.delete(*self.issues_tree.get_children())
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
        
        # Language statistics
        language_stats = {}
        total_metrics = {}
        
        for result in results:
            file_path = result['file_path']
            language = result.get('language', 'unknown')
            
            # Track language statistics
            if language not in language_stats:
                language_stats[language] = {'files': 0, 'lines': 0, 'issues': 0}
            language_stats[language]['files'] += 1
            language_stats[language]['lines'] += result.get('metrics', {}).get('lines_of_code', 0)
            language_stats[language]['issues'] += sum(len(msgs) for msgs in result.get('issues', {}).values())
            
            # Add issues with file context
            for issue_type, messages in result.get('issues', {}).items():
                for msg in messages:
                    self.issues_tree.insert(
                        '', 'end', 
                        values=(issue_type, f"{file_path}: {msg}")
                    )
            
            # Sum metrics (excluding non-numeric ones)
            for metric, value in result.get('metrics', {}).items():
                if isinstance(value, (int, float)):
                    total_metrics[metric] = total_metrics.get(metric, 0) + value
        
        # Display statistics
        self.metrics_text.insert(tk.END, "Project Analysis Summary:\n\n")
        
        self.metrics_text.insert(tk.END, "Languages Analyzed:\n")
        for language, stats in language_stats.items():
            self.metrics_text.insert(tk.END, f"  {language.upper()}: {stats['files']} files, ")
            self.metrics_text.insert(tk.END, f"{stats['lines']} lines, {stats['issues']} issues\n")
        
        self.metrics_text.insert(tk.END, "\nAggregated Metrics:\n")
        for metric, value in total_metrics.items():
            self.metrics_text.insert(tk.END, f"  {metric}: {value}\n")
        
        self.metrics_text.config(state=tk.DISABLED)
        self.select(self.issues_tab)
        
    def _display_issues(self, issues: Dict[str, List[str]]):
        """Display issues in the issues tree."""
        self.issues_tree.delete(*self.issues_tree.get_children())
        
        for issue_type, messages in issues.items():
            for msg in messages:
                self.issues_tree.insert('', 'end', values=(issue_type, msg))
        self.select(self.issues_tab) 
        
   # Modify _display_metrics method
    def _display_metrics(self, metrics: Dict[str, Any], language: str = 'unknown'):
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
    
        # Show language and basic metrics
        self.metrics_text.insert(tk.END, f"Language: {language.upper()}\n\n")
        self.metrics_text.insert(tk.END, "Code Metrics:\n")
        self.metrics_text.insert(tk.END, f"  Lines of code: {metrics.get('lines_of_code', 0)}\n")
        self.metrics_text.insert(tk.END, f"  Comment lines: {metrics.get('comment_lines', 0)}\n")
        
        if 'blank_lines' in metrics:
            self.metrics_text.insert(tk.END, f"  Blank lines: {metrics.get('blank_lines', 0)}\n")
    
        # Time complexity display
        complexity = metrics.get('time_complexity', {})
        self.metrics_text.insert(tk.END, "\nTime Complexity:\n")
        self.metrics_text.insert(tk.END, f"  Overall: {complexity.get('overall', 'Not analyzed')}")
        
        if complexity.get('estimated'):
            self.metrics_text.insert(tk.END, " (estimated)")
        self.metrics_text.insert(tk.END, "\n")
    
        if complexity.get('functions'):
            self.metrics_text.insert(tk.END, "\n  Per Function:\n")
            for func, comp in complexity['functions'].items():
                self.metrics_text.insert(tk.END, f"    {func}: {comp}\n")
        
        # Space complexity display
        space_complexity = metrics.get('space_complexity', {})
        self.metrics_text.insert(tk.END, "\nSpace Complexity:\n")
        self.metrics_text.insert(tk.END, f"  Overall: {space_complexity.get('overall', 'Not analyzed')}")
        
        if space_complexity.get('estimated'):
            self.metrics_text.insert(tk.END, " (estimated)")
        self.metrics_text.insert(tk.END, "\n")
    
        if space_complexity.get('functions'):
            self.metrics_text.insert(tk.END, "\n  Per Function:\n")
            for func, comp in space_complexity['functions'].items():
                self.metrics_text.insert(tk.END, f"    {func}: {comp}\n")
    
        self.metrics_text.config(state=tk.DISABLED)