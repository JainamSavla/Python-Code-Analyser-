import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Now use direct imports (no se6_27 prefix)
from gui.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()