import multiprocessing

from app.ui import main

if __name__ == "__main__":
    # Required for Windows when using multiprocessing in frozen (PyInstaller) apps
    multiprocessing.freeze_support()
    main()