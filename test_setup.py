#!/usr/bin/env python3

import sys
print("Python version:", sys.version)
print("\nTesting game development libraries...")

try:
    import pygame
    print("✓ pygame: Available")
    pygame.init()
    pygame.quit()
except Exception as e:
    print("✗ pygame:", e)

try:
    import pygame_ce
    print("✓ pygame-ce: Available")
except Exception as e:
    print("✗ pygame-ce:", e)

try:
    import numpy as np
    print("✓ numpy:", np.__version__)
except ImportError as e:
    print("✗ numpy:", e)

try:
    from PIL import Image
    print("✓ Pillow:", Image.__version__)
except ImportError as e:
    print("✗ Pillow:", e)

try:
    import pydub
    print("✓ pydub: Available")
except ImportError as e:
    print("✗ pydub:", e)

try:
    import OpenGL.GL as gl
    print("✓ PyOpenGL: Available")
except ImportError as e:
    print("✗ PyOpenGL:", e)

try:
    import matplotlib
    print("✓ matplotlib:", matplotlib.__version__)
except ImportError as e:
    print("✗ matplotlib:", e)

try:
    import requests
    print("✓ requests:", requests.__version__)
except ImportError as e:
    print("✗ requests:", e)

print("\nAll core libraries tested!")