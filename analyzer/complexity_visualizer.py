"""
Complexity Visualization Module for N0VA Code Analyzer
Generates graphs and charts for time and space complexity analysis.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
try:
    # Try newer matplotlib versions first
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvasTkinter
except ImportError:
    try:
        # Fallback for older matplotlib versions
        from matplotlib.backends.backend_tkagg import FigureCanvasTkinter
    except ImportError:
        # If neither works, set to None and handle gracefully
        FigureCanvasTkinter = None
import numpy as np
import seaborn as sns
from typing import Dict, Any, List, Tuple, Optional
import tkinter as tk
from tkinter import ttk
import io
import base64

# Set style for better looking plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class ComplexityVisualizer:
    """Class to create visualizations for time and space complexity."""
    
    def __init__(self):
        self.complexity_colors = {
            'O(1)': '#28a745',        # Green - Excellent
            'O(log n)': '#6f42c1',    # Purple - Very Good
            'O(n)': '#007bff',        # Blue - Good
            'O(n log n)': '#fd7e14',  # Orange - Fair
            'O(n²)': '#dc3545',       # Red - Poor
            'O(n³+)': '#6c757d',      # Gray - Very Poor
            'O(n!)': '#000000'        # Black - Terrible
        }
        
        self.complexity_order = ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n²)', 'O(n³+)', 'O(n!)']
    
    def create_complexity_comparison_chart(self, time_complexity: Dict[str, Any], 
                                         space_complexity: Dict[str, Any], 
                                         figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
        """Create a comparison chart for time and space complexity."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        fig.suptitle('Time vs Space Complexity Analysis', fontsize=16, fontweight='bold')
        
        # Time Complexity Chart
        self._create_single_complexity_chart(ax1, time_complexity, 'Time Complexity', 'time')
        
        # Space Complexity Chart
        self._create_single_complexity_chart(ax2, space_complexity, 'Space Complexity', 'space')
        
        plt.tight_layout()
        return fig
    
    def _create_single_complexity_chart(self, ax, complexity_data: Dict[str, Any], 
                                      title: str, complexity_type: str):
        """Create a single complexity chart (either time or space)."""
        if not complexity_data or not complexity_data.get('functions'):
            # Show only overall complexity
            overall = complexity_data.get('overall', 'O(1)')
            ax.bar(['Overall'], [self._complexity_to_numeric(overall)], 
                  color=self.complexity_colors.get(overall, '#gray'))
            ax.set_title(f'{title}\nOverall: {overall}')
        else:
            # Show function-wise complexity
            functions = complexity_data.get('functions', {})
            func_names = list(functions.keys())
            complexities = [functions[func] for func in func_names]
            colors = [self.complexity_colors.get(comp, '#gray') for comp in complexities]
            
            # Truncate long function names
            display_names = [name[:15] + '...' if len(name) > 15 else name for name in func_names]
            
            bars = ax.bar(display_names, [self._complexity_to_numeric(comp) for comp in complexities], 
                         color=colors)
            
            # Add complexity labels on bars
            for bar, complexity in zip(bars, complexities):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       complexity, ha='center', va='bottom', fontsize=9)
            
            ax.set_title(f'{title}\nOverall: {complexity_data.get("overall", "N/A")}')
            
        ax.set_ylabel('Complexity Score')
        ax.set_ylim(0, 7)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    def create_complexity_trend_chart(self, results: List[Dict[str, Any]], 
                                    figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
        """Create a trend chart showing complexity across multiple files."""
        if not results:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, 'No data to display', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
            ax.set_title('Complexity Trend Analysis')
            return fig
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)
        fig.suptitle('Complexity Trend Across Files', fontsize=16, fontweight='bold')
        
        file_names = []
        time_complexities = []
        space_complexities = []
        
        for result in results:
            file_path = result.get('file_path', '')
            file_name = file_path.split('\\')[-1] if '\\' in file_path else file_path.split('/')[-1]
            file_names.append(file_name)
            
            time_comp = result.get('metrics', {}).get('time_complexity', {}).get('overall', 'O(1)')
            space_comp = result.get('metrics', {}).get('space_complexity', {}).get('overall', 'O(1)')
            
            time_complexities.append(self._complexity_to_numeric(time_comp))
            space_complexities.append(self._complexity_to_numeric(space_comp))
        
        # Time complexity trend
        ax1.plot(range(len(file_names)), time_complexities, 'o-', color='#007bff', 
                linewidth=2, markersize=8, label='Time Complexity')
        ax1.fill_between(range(len(file_names)), time_complexities, alpha=0.3, color='#007bff')
        ax1.set_ylabel('Time Complexity Score')
        ax1.set_title('Time Complexity Trend')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 7)
        
        # Space complexity trend
        ax2.plot(range(len(file_names)), space_complexities, 'o-', color='#28a745', 
                linewidth=2, markersize=8, label='Space Complexity')
        ax2.fill_between(range(len(file_names)), space_complexities, alpha=0.3, color='#28a745')
        ax2.set_ylabel('Space Complexity Score')
        ax2.set_xlabel('Files')
        ax2.set_title('Space Complexity Trend')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 7)
        
        # Set x-axis labels
        ax2.set_xticks(range(len(file_names)))
        ax2.set_xticklabels([name[:10] + '...' if len(name) > 10 else name 
                            for name in file_names], rotation=45, ha='right')
        
        plt.tight_layout()
        return fig
    
    def create_complexity_distribution_pie(self, results: List[Dict[str, Any]], 
                                         complexity_type: str = 'time',
                                         figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
        """Create a pie chart showing distribution of complexity types."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        fig.suptitle(f'{complexity_type.title()} and Space Complexity Distribution', 
                    fontsize=16, fontweight='bold')
        
        # Time complexity distribution
        time_complexities = []
        space_complexities = []
        
        for result in results:
            metrics = result.get('metrics', {})
            time_comp = metrics.get('time_complexity', {}).get('overall', 'O(1)')
            space_comp = metrics.get('space_complexity', {}).get('overall', 'O(1)')
            time_complexities.append(time_comp)
            space_complexities.append(space_comp)
        
        # Create pie charts
        self._create_pie_chart(ax1, time_complexities, 'Time Complexity')
        self._create_pie_chart(ax2, space_complexities, 'Space Complexity')
        
        plt.tight_layout()
        return fig
    
    def _create_pie_chart(self, ax, complexities: List[str], title: str):
        """Create a single pie chart for complexity distribution."""
        # Count occurrences of each complexity
        complexity_counts = {}
        for comp in complexities:
            complexity_counts[comp] = complexity_counts.get(comp, 0) + 1
        
        if not complexity_counts:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title)
            return
        
        labels = list(complexity_counts.keys())
        sizes = list(complexity_counts.values())
        colors = [self.complexity_colors.get(label, '#gray') for label in labels]
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                         startangle=90, textprops={'fontsize': 10})
        
        ax.set_title(title, fontweight='bold')
    
    def create_complexity_heatmap(self, results: List[Dict[str, Any]], 
                                figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
        """Create a heatmap showing complexity across files and functions."""
        if not results:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, 'No data to display', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
            return fig
        
        # Collect all function data
        function_data = []
        file_names = []
        
        for result in results:
            file_path = result.get('file_path', '')
            file_name = file_path.split('\\')[-1] if '\\' in file_path else file_path.split('/')[-1]
            file_names.append(file_name)
            
            metrics = result.get('metrics', {})
            time_funcs = metrics.get('time_complexity', {}).get('functions', {})
            space_funcs = metrics.get('space_complexity', {}).get('functions', {})
            
            # Combine function data
            all_funcs = set(time_funcs.keys()) | set(space_funcs.keys())
            for func in all_funcs:
                time_comp = time_funcs.get(func, 'O(1)')
                space_comp = space_funcs.get(func, 'O(1)')
                function_data.append({
                    'file': file_name,
                    'function': func,
                    'time': self._complexity_to_numeric(time_comp),
                    'space': self._complexity_to_numeric(space_comp)
                })
        
        if not function_data:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, 'No function data to display', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
            return fig
        
        # Create matrix for heatmap
        unique_functions = list(set(item['function'] for item in function_data))
        unique_files = list(set(item['file'] for item in function_data))
        
        # Create two matrices: one for time, one for space
        time_matrix = np.zeros((len(unique_functions), len(unique_files)))
        space_matrix = np.zeros((len(unique_functions), len(unique_files)))
        
        for item in function_data:
            func_idx = unique_functions.index(item['function'])
            file_idx = unique_files.index(item['file'])
            time_matrix[func_idx][file_idx] = item['time']
            space_matrix[func_idx][file_idx] = item['space']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        fig.suptitle('Function Complexity Heatmap', fontsize=16, fontweight='bold')
        
        # Time complexity heatmap
        sns.heatmap(time_matrix, xticklabels=unique_files, yticklabels=unique_functions,
                   ax=ax1, cmap='RdYlGn_r', vmin=0, vmax=6, cbar_kws={'label': 'Complexity Score'})
        ax1.set_title('Time Complexity')
        ax1.set_xlabel('Files')
        ax1.set_ylabel('Functions')
        
        # Space complexity heatmap
        sns.heatmap(space_matrix, xticklabels=unique_files, yticklabels=unique_functions,
                   ax=ax2, cmap='RdYlGn_r', vmin=0, vmax=6, cbar_kws={'label': 'Complexity Score'})
        ax2.set_title('Space Complexity')
        ax2.set_xlabel('Files')
        ax2.set_ylabel('Functions')
        
        plt.tight_layout()
        return fig
    
    def create_performance_radar_chart(self, metrics: Dict[str, Any], 
                                     figsize: Tuple[int, int] = (8, 8)) -> plt.Figure:
        """Create a radar chart showing different performance metrics."""
        fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection='polar'))
        
        # Performance categories
        categories = ['Time Complexity', 'Space Complexity', 'Code Quality', 'Maintainability', 'Readability']
        
        # Extract values (normalize to 0-10 scale)
        time_score = 10 - self._complexity_to_numeric(metrics.get('time_complexity', {}).get('overall', 'O(1)'))
        space_score = 10 - self._complexity_to_numeric(metrics.get('space_complexity', {}).get('overall', 'O(1)'))
        
        # Simple heuristics for other metrics
        loc = metrics.get('lines_of_code', 0)
        comment_ratio = metrics.get('comment_lines', 0) / max(loc, 1) * 100
        
        quality_score = min(10, comment_ratio * 2)  # Based on comment ratio
        maintainability_score = max(0, 10 - (loc / 50))  # Inversely related to LOC
        readability_score = min(10, comment_ratio * 1.5)  # Similar to quality but different weight
        
        values = [time_score, space_score, quality_score, maintainability_score, readability_score]
        
        # Angles for each category
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle
        values += values[:1]  # Complete the circle
        
        # Plot
        ax.plot(angles, values, 'o-', linewidth=2, color='#007bff')
        ax.fill(angles, values, alpha=0.25, color='#007bff')
        
        # Add labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 10)
        ax.grid(True)
        
        plt.title('Code Performance Radar Chart', size=16, fontweight='bold', pad=20)
        return fig
    
    def _complexity_to_numeric(self, complexity: str) -> float:
        """Convert complexity string to numeric value for plotting."""
        mapping = {
            'O(1)': 1,
            'O(log n)': 2,
            'O(n)': 3,
            'O(n log n)': 4,
            'O(n²)': 5,
            'O(n³+)': 6,
            'O(n!)': 7
        }
        return mapping.get(complexity, 1)
    
    def save_figure_to_bytes(self, fig: plt.Figure) -> bytes:
        """Save matplotlib figure to bytes for embedding in GUI."""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        return buffer.getvalue()
    
    def create_tkinter_canvas(self, parent, fig: plt.Figure):
        """Create a Tkinter canvas for matplotlib figure."""
        if FigureCanvasTkinter is None:
            raise ImportError("Tkinter canvas functionality requires matplotlib with tkinter backend")
        canvas = FigureCanvasTkinter(fig, master=parent)
        canvas.draw()
        return canvas


class GraphicalResultsPanel(ttk.Frame):
    """Enhanced results panel with graphical visualizations."""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.visualizer = ComplexityVisualizer()
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the UI with tabs for different visualizations."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Comparison Chart Tab
        self.comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.comparison_frame, text="Complexity Comparison")
        
        # Trend Analysis Tab
        self.trend_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.trend_frame, text="Trend Analysis")
        
        # Distribution Tab
        self.distribution_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.distribution_frame, text="Distribution")
        
        # Heatmap Tab
        self.heatmap_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.heatmap_frame, text="Function Heatmap")
        
        # Radar Chart Tab
        self.radar_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.radar_frame, text="Performance Radar")
        
    def display_single_file_results(self, results: Dict[str, Any]):
        """Display visualizations for a single file."""
        metrics = results.get('metrics', {})
        time_complexity = metrics.get('time_complexity', {})
        space_complexity = metrics.get('space_complexity', {})
        
        # Clear existing widgets
        self._clear_frame(self.comparison_frame)
        self._clear_frame(self.radar_frame)
        
        # Create comparison chart
        comparison_fig = self.visualizer.create_complexity_comparison_chart(
            time_complexity, space_complexity
        )
        comparison_canvas = self.visualizer.create_tkinter_canvas(self.comparison_frame, comparison_fig)
        comparison_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create radar chart
        radar_fig = self.visualizer.create_performance_radar_chart(metrics)
        radar_canvas = self.visualizer.create_tkinter_canvas(self.radar_frame, radar_fig)
        radar_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def display_multiple_file_results(self, results: List[Dict[str, Any]]):
        """Display visualizations for multiple files."""
        if not results:
            return
            
        # Clear existing widgets
        for frame in [self.trend_frame, self.distribution_frame, self.heatmap_frame]:
            self._clear_frame(frame)
        
        # Create trend analysis
        trend_fig = self.visualizer.create_complexity_trend_chart(results)
        trend_canvas = self.visualizer.create_tkinter_canvas(self.trend_frame, trend_fig)
        trend_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create distribution pie charts
        distribution_fig = self.visualizer.create_complexity_distribution_pie(results)
        distribution_canvas = self.visualizer.create_tkinter_canvas(self.distribution_frame, distribution_fig)
        distribution_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create heatmap
        heatmap_fig = self.visualizer.create_complexity_heatmap(results)
        heatmap_canvas = self.visualizer.create_tkinter_canvas(self.heatmap_frame, heatmap_fig)
        heatmap_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _clear_frame(self, frame):
        """Clear all widgets from a frame."""
        for widget in frame.winfo_children():
            widget.destroy()