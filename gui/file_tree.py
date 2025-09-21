from typing import Optional, Dict, List, Any 
import os
import tkinter as tk
from tkinter import ttk
from pathlib import Path

class FileTree(ttk.Treeview):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.heading("#0", text="Project Files", anchor=tk.W)
        self.base_directory = None
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("Treeview", font=('Consolas', 10))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.configure(yscrollcommand=scrollbar.set)
        
    def load_directory(self, directory_path: str):
        """Load a directory into the file tree."""
        self.delete(*self.get_children())
        self.base_directory = directory_path
        path = Path(directory_path)
        
        # Add the root directory
        root_node = self.insert("", "end", text=path.name, 
                              values=[str(path)], open=True)
        self._add_children(root_node, path)
        
    def _add_children(self, parent_node, path: Path):
        """Recursively add children to the tree."""
        try:
            # Supported code file extensions
            supported_extensions = {'.py', '.java', '.c', '.cpp', '.cc', '.cxx', '.c++', '.h', '.hpp', '.hh', '.hxx'}
            
            for item in sorted(path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    node = self.insert(parent_node, "end", text=item.name, 
                                     values=[str(item)])
                    self._add_children(node, item)
                elif item.is_file() and item.suffix.lower() in supported_extensions:
                    # Add different tags based on file type
                    file_type = self._get_file_type(item.suffix.lower())
                    self.insert(parent_node, "end", text=item.name, 
                              values=[str(item)], tags=(file_type,))
        except PermissionError:
            pass
    
    def _get_file_type(self, extension: str) -> str:
        """Get file type tag based on extension."""
        type_map = {
            '.py': 'python',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c++': 'cpp',
            '.h': 'c_header',
            '.hpp': 'cpp_header',
            '.hh': 'cpp_header',
            '.hxx': 'cpp_header'
        }
        return type_map.get(extension, 'file')
            
    def get_selected_file(self) -> Optional[str]:
        """Get the full path of the currently selected file."""
        selected_item = self.focus()
        if selected_item:
            return self.item(selected_item)["values"][0]
        return None