import os
import sys
import pandas as pd
import numpy as np

# Directorio de trabajo actual
print("Directorio de trabajo actual:", os.getcwd())

# Ruta del script (si estás en un .py)
try:
    print("Directorio del script:", os.path.dirname(os.path.abspath(__file__)))
except NameError:
    print("No estás en un script (probablemente en un entorno interactivo)")

# Intérprete de Python
print("Ruta del intérprete de Python:", sys.executable)