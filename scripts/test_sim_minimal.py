import numpy as np
from scipy.integrate import odeint
import sys
import os

# 添加项目根目录到路径以便导入 models
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from models.benzene_kinetics import BenzeneKinetics
    print("BenzeneKinetics imported successfully")
except ImportError as e:
    print(f"Error importing models: {e}")
    sys.exit(1)

def reaction_model(y, t, kinetics, T, P_total_initial, catalyst_mass, volume):
    C_B, C_H, C_C = y
    
    R_gas = 0.08314 
    P_B = C_B * R_gas * T
    P_H = C_H * R_gas * T
    P_C = C_C * R_gas * T
    
    P_B = max(0, P_B)
    P_H = max(0, P_H)
    P_C = max(0, P_C)
    
    rate = kinetics.calculate_rate(T, P_B, P_H, P_C)
    
    factor = catalyst_mass / volume
    
    dCB_dt = -1 * rate * factor
    dCH_dt = -3 * rate * factor
    dCC_dt = 1 * rate * factor
    
    return [dCB_dt, dCH_dt, dCC_dt]

def run_simulation():
    print("Initializing parameters...")
    T = 400.0
    P_init = 20.0
    t_max = 3600
    steps = 100
    catalyst_mass = 5.0
    volume = 1.0
    
    R_gas = 0.08314
    C_B0 = (P_init * 1/6) / (R_gas * T)
    C_H0 = (P_init * 5/6) / (R_gas * T)
    C_C0 = 0.0
    
    y0 = [C_B0, C_H0, C_C0]
    t = np.linspace(0, t_max, steps)
    
    kinetics = BenzeneKinetics()
    print(f"Kinetics model initialized: {kinetics}")
    
    print("Starting integration...")
    sol = odeint(reaction_model, y0, t, args=(kinetics, T, P_init, catalyst_mass, volume))
    print("Integration complete!")
    print(f"Final concentrations: {sol[-1]}")

if __name__ == "__main__":
    run_simulation()
