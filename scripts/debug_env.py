import sys
print(f"Python executable: {sys.executable}")
try:
    import numpy
    print(f"Numpy version: {numpy.__version__}")
    import scipy
    print(f"Scipy version: {scipy.__version__}")
    import pyecharts
    print(f"Pyecharts version: {pyecharts.__version__}")
except Exception as e:
    print(f"Error importing: {e}")
