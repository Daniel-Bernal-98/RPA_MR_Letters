import os
import sys

def resource_path(relative_path):
    """
    For PyInstaller build, return the correct path.
    """

    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def close_application(root, launcher_root = None):

    try:
        if launcher_root:
            launcher_root.destroy()
    except:
        pass

    try:
        root.quit()
    except:
        pass

    try:
        root.destroy()
    except:
        pass
