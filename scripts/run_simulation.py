import sys
import os
import numpy as np
from scipy.integrate import odeint

# Force unbuffered output
sys.stdout.reconfigure(encoding='utf-8')

print("Imports successful (numpy, scipy).")

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from models.benzene_kinetics import BenzeneKinetics
    print("Model imported successfully.")
except ImportError as e:
    print(f"Error importing models: {e}")
    sys.exit(1)

def reaction_model(y, t, kinetics, T, P_total_initial, catalyst_mass, volume):
    C_B, C_H, C_C = y
    
    R_gas = 0.08314
    # Ideal gas law: P = C * R * T
    P_B = max(0, C_B * R_gas * T)
    P_H = max(0, C_H * R_gas * T)
    P_C = max(0, C_C * R_gas * T)
    
    rate = kinetics.calculate_rate(T, P_B, P_H, P_C)
    
    factor = catalyst_mass / volume
    # dC/dt = rate * (W/V) * stoich
    dCB_dt = -1 * rate * factor
    dCH_dt = -3 * rate * factor
    dCC_dt = 1 * rate * factor
    
    return [dCB_dt, dCH_dt, dCC_dt]

def run_simulation():
    print("Initializing simulation parameters...")
    T = 400.0       # K
    P_init = 20.0   # bar
    t_max = 3600    # s
    steps = 100
    catalyst_mass = 5.0 # g
    volume = 1.0    # L
    
    R_gas = 0.08314
    C_B0 = (P_init * 1/6) / (R_gas * T)
    C_H0 = (P_init * 5/6) / (R_gas * T)
    C_C0 = 0.0
    
    y0 = [C_B0, C_H0, C_C0]
    t = np.linspace(0, t_max, steps)
    
    kinetics = BenzeneKinetics()
    
    print(f"Starting integration (T={T}K, P={P_init}bar, t_max={t_max}s)...")
    try:
        sol = odeint(reaction_model, y0, t, args=(kinetics, T, P_init, catalyst_mass, volume))
        print("Integration complete.")
    except Exception as e:
        print(f"Integration failed: {e}")
        return

    # 提取结果
    C_B = np.round(sol[:, 0], 2)
    C_H = np.round(sol[:, 1], 2)
    C_C = np.round(sol[:, 2], 2)
    print(f"Final concentrations (rounded): B={C_B[-1]}, H={C_H[-1]}, C={C_C[-1]}")
    
    print("Importing pyecharts...")
    try:
        from pyecharts.charts import Line
        from pyecharts import options as opts
        print("Pyecharts imported.")
    except ImportError as e:
        print(f"Pyecharts import failed: {e}")
        return

    print("Generating chart options...")
    line = Line()
    # 时间也保留一位小数，避免横坐标过长
    t_list = [round(x, 1) for x in t]
    line.add_xaxis(t_list)
    line.add_yaxis("Benzene (C6H6)", C_B.tolist(), is_smooth=True)
    line.add_yaxis("Hydrogen (H2)", C_H.tolist(), is_smooth=True)
    line.add_yaxis("Cyclohexane (C6H12)", C_C.tolist(), is_smooth=True)
    
    line.set_global_opts(
        title_opts=opts.TitleOpts(title="Benzene Hydrogenation Kinetics", subtitle=f"T={T}K, P={P_init}bar"),
        xaxis_opts=opts.AxisOpts(name="Time (s)"),
        yaxis_opts=opts.AxisOpts(name="Concentration (mol/L)"),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
        toolbox_opts=opts.ToolboxOpts(is_show=True)
    )
    
    output_file = os.path.join(os.path.dirname(__file__), '..', 'simulation_result.html')
    output_file = os.path.abspath(output_file)
    print(f"Rendering to {output_file}...")
    line.render(output_file)
    print("Render complete. Simulation finished successfully.")

if __name__ == "__main__":
    run_simulation()
