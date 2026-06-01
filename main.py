# ============================================================================
# MR Letters Generator
#
# Copyright (c) 2026 ABA Centers of America
# All Rights Reserved.
#
# Proprietary and Confidential.
# For internal use only.
#
# Unauthorized copying, distribution, modification, or disclosure
# of this software is strictly prohibited.
# ============================================================================

import multiprocessing

from app.ui import main

if __name__ == "__main__":
    # Required for Windows when using multiprocessing in frozen (PyInstaller) apps
    multiprocessing.freeze_support()
    main()