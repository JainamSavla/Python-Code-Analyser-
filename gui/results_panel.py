import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Optional, Dict, Any, List

try:
    from analyzer.complexity_visualizer import ComplexityVisualizer, GraphicalResultsPanel
    GRAPHS_AVAILABLE = True
except ImportError:
    # Fallback if visualization dependencies are not available
    GRAPHS_AVAILABLE = False
    ComplexityVisualizer = None
    GraphicalResultsPanel = None

class ResultsPanel(ttk.Notebook):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.visualizer = ComplexityVisualizer() if GRAPHS_AVAILABLE else None
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
        
        # Visualization tabs (if available)
        if GRAPHS_AVAILABLE:
            self._setup_visualization_tabs()
        else:
            # Add a note about missing dependencies
            self.graph_note_tab = ttk.Frame(self)
            note_text = tk.Text(self.graph_note_tab, wrap=tk.WORD, font=('Arial', 11))
            note_text.pack(fill=tk.BOTH, expand=True)
            note_text.insert(tk.END, 
                "Graphical visualizations are not available.\n\n"
                "To enable graphs, install the required dependencies:\n"
                "pip install matplotlib numpy seaborn\n\n"
                "Then restart the application to see complexity graphs.")
            note_text.config(state=tk.DISABLED)
            self.add(self.graph_note_tab, text="Graphs (Unavailable)")
            
    def _setup_visualization_tabs(self):
        """Setup visualization tabs when dependencies are available."""
        # Complexity Comparison tab
        self.comparison_tab = ttk.Frame(self)
        self.add(self.comparison_tab, text="Complexity Charts")
        
        # Trend Analysis tab (for multiple files)
        self.trend_tab = ttk.Frame(self)
        self.add(self.trend_tab, text="Trend Analysis")
        
        # Distribution tab
        self.distribution_tab = ttk.Frame(self)
        self.add(self.distribution_tab, text="Distribution")
        
        # Performance Radar tab
        self.radar_tab = ttk.Frame(self)
        self.add(self.radar_tab, text="Performance Radar")
        
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
        
        # Display graphical results if available
        if GRAPHS_AVAILABLE and self.visualizer:
            self._display_graphical_results(results)
            
    def _display_graphical_results(self, results: Dict[str, Any]):
        """Display graphical visualizations for single file results."""
        try:
            metrics = results.get('metrics', {})
            time_complexity = metrics.get('time_complexity', {})
            space_complexity = metrics.get('space_complexity', {})
            
            # Clear existing graphs
            self._clear_tab(self.comparison_tab)
            self._clear_tab(self.radar_tab)
            
            # Create complexity comparison chart
            if time_complexity or space_complexity:
                comparison_fig = self.visualizer.create_complexity_comparison_chart(
                    time_complexity, space_complexity
                )
                comparison_canvas = self.visualizer.create_tkinter_canvas(
                    self.comparison_tab, comparison_fig
                )
                comparison_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Create performance radar chart
            radar_fig = self.visualizer.create_performance_radar_chart(metrics)
            radar_canvas = self.visualizer.create_tkinter_canvas(
                self.radar_tab, radar_fig
            )
            radar_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            # If graph generation fails, show error in comparison tab
            self._clear_tab(self.comparison_tab)
            error_label = tk.Label(self.comparison_tab, 
                                 text=f"Error generating graphs: {str(e)}", 
                                 wraplength=400)
            error_label.pack(expand=True)
        
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
        
        # Display graphical results for multiple files
        if GRAPHS_AVAILABLE and self.visualizer and results:
            self._display_multiple_file_graphs(results)
            
    def _display_multiple_file_graphs(self, results: List[Dict[str, Any]]):
        """Display graphical visualizations for multiple file results."""
        try:
            # Clear existing graphs
            self._clear_tab(self.trend_tab)
            self._clear_tab(self.distribution_tab)
            
            # Create trend analysis
            trend_fig = self.visualizer.create_complexity_trend_chart(results)
            trend_canvas = self.visualizer.create_tkinter_canvas(
                self.trend_tab, trend_fig
            )
            trend_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Create distribution charts
            distribution_fig = self.visualizer.create_complexity_distribution_pie(results)
            distribution_canvas = self.visualizer.create_tkinter_canvas(
                self.distribution_tab, distribution_fig
            )
            distribution_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            # If graph generation fails, show error
            self._clear_tab(self.trend_tab)
            error_label = tk.Label(self.trend_tab, 
                                 text=f"Error generating trend graphs: {str(e)}", 
                                 wraplength=400)
            error_label.pack(expand=True)
            
    def _clear_tab(self, tab_frame):
        """Clear all widgets from a tab frame."""
        for widget in tab_frame.winfo_children():
            widget.destroy()
        
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