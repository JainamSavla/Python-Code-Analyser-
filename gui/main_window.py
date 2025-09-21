from typing import Optional, Dict, List, Any    
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional
from analyzer.code_analysis import CodeAnalyzer
from gui.file_tree import FileTree
from gui.results_panel import ResultsPanel

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Multi-Language Static Code Analyzer")
        self.geometry("1000x700")
        self.analyzer = CodeAnalyzer()
        
        # Supported file extensions
        self.supported_extensions = {'.py', '.java', '.c', '.cpp', '.cc', '.cxx', '.c++', '.h', '.hpp', '.hh', '.hxx'}
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the main application interface."""
        # Create main panes
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)
        
        # Left pane - file tree
        self.file_tree_frame = ttk.Frame(main_pane, width=200)
        self._setup_file_tree()
        main_pane.add(self.file_tree_frame)
        
        # Right pane - results
        self.results_frame = ttk.Frame(main_pane)
        self._setup_results_area()
        main_pane.add(self.results_frame)
        
        # Menu bar
        self._setup_menu()
        
    def _setup_menu(self):
        """Set up the menu bar."""
        menubar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Directory", command=self._open_directory)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        analysis_menu.add_command(label="Analyze Current File", command=self._analyze_current)
        analysis_menu.add_command(label="Analyze All Files", command=self._analyze_all)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        
        self.config(menu=menubar)
        
    def _setup_file_tree(self):
        """Set up the file tree browser."""
        from .file_tree import FileTree  # Local import to avoid circular imports
        
        self.file_tree = FileTree(self.file_tree_frame)
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        self.file_tree.bind("<<TreeviewSelect>>", self._on_file_select)
        
    def _setup_results_area(self):
        """Set up the results display area."""
        from .results_panel import ResultsPanel  # Local import to avoid circular imports
        
        self.results_panel = ResultsPanel(self.results_frame)
        self.results_panel.pack(fill=tk.BOTH, expand=True)
        
    def _open_directory(self):
        """Open a directory dialog and load files."""
        directory = filedialog.askdirectory()
        if directory:
            self.file_tree.load_directory(directory)
            
    def _analyze_current(self):
        """Analyze the currently selected file."""
        selected_file = self.file_tree.get_selected_file()
        if selected_file:
            file_ext = Path(selected_file).suffix.lower()
            if file_ext in self.supported_extensions:
                result = self.analyzer.analyze_file(selected_file)
                self.results_panel.display_results(result)
            else:
                messagebox.showwarning("Unsupported File", 
                                     f"Please select a supported file type: {', '.join(sorted(self.supported_extensions))}")
        else:
            messagebox.showwarning("No File Selected", 
                                 "Please select a code file to analyze.")
            
    def _analyze_all(self):
        """Analyze all supported code files in the current directory."""
        base_dir = self.file_tree.base_directory
        if base_dir:
            results = self.analyzer.analyze_directory(base_dir)
            if results:
                self.results_panel.display_multiple_results(results)
            else:
                messagebox.showinfo("No Files", "No supported code files found in the directory.")
        else:
            messagebox.showwarning("No Directory", "Please open a directory first.")
            
    def _on_file_select(self, event):
        """Handle file selection event."""
        selected_file = self.file_tree.get_selected_file()
        if selected_file:
            file_ext = Path(selected_file).suffix.lower()
            if file_ext in self.supported_extensions:
                self.results_panel.preview_file(selected_file)