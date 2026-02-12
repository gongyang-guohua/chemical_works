import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
print("Path appended")

try:
    print("Importing benzene_kinetics...")
    from models import benzene_kinetics
    print("Imported module")
    model = benzene_kinetics.BenzeneKinetics()
    print("Instantiated model")
except Exception as e:
    print(f"Error: {e}")
