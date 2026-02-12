import os
os.environ["DDE_BACKEND"] = "pytorch"
import deepxde as dde
import numpy as np
from deepxde.backend import torch

print(f"DeepXDE version: {dde.__version__}")
print(f"Backend: {dde.backend.backend_name}")

# --- DeepXDE Demo: Reaction-Diffusion System (Mass Transfer + Kinetics) ---
# Problem: A simple 1D reaction-diffusion equation (concentration field C)
# dC/dt = D * d^2C/dx^2 - k * C
# Demonstrates: Concentration Distribution, Mass Transfer (Diffusion), Reaction Kinetics
print("\n--- DeepXDE Demo: Reaction-Diffusion (Transport Phenomena) ---")
print("Simulating: dC/dt = D * d^2C/dx^2 - k * C")
print("Target: Concentration Field C(x,t)")

try:
    # Physical parameters
    D = 0.01  # Diffusion coefficient (Mass transfer)
    k = 1.0   # Reaction rate constant (Kinetics)

    # Geometry and Time domain
    geom = dde.geometry.Interval(-1, 1)
    timedomain = dde.geometry.TimeDomain(0, 1)
    geomtime = dde.geometry.GeometryXTime(geom, timedomain)

    # PDE definition
    def pde(x, y):
        dy_t = dde.grad.jacobian(y, x, i=0, j=1)
        dy_xx = dde.grad.hessian(y, x, i=0, j=0)
        # Residual = dC/dt - (D * d^2C/dx^2 - k * C)
        return dy_t - (D * dy_xx - k * y)

    # Initial and Boundary Conditions
    # IC: C(x,0) = exp(-x^2)
    def func_ic(x):
        return np.exp(-x[:, 0:1]**2)

    ic = dde.icbc.IC(geomtime, func_ic, lambda _, on_initial: on_initial)
    
    # Dirichlet BC: C(-1, t) = C(1, t) = 0
    bc = dde.icbc.DirichletBC(geomtime, lambda x: 0, lambda _, on_boundary: on_boundary)

    data = dde.data.TimePDE(
        geomtime,
        pde,
        [bc, ic],
        num_domain=200,   # Residual points inside domain
        num_boundary=40,   # Boundary points
        num_initial=20,    # Initial points
        num_test=100,
    )

    # Neural Network
    net = dde.nn.FNN([2] + [20] * 3 + [1], "tanh", "Glorot uniform")
    model = dde.Model(data, net)
    
    print("Compiling model...")
    model.compile("adam", lr=0.001)
    
    print("Training PINN for 100 iterations (Demonstration)...")
    losshistory, train_state = model.train(iterations=100)
    print("Training finished.")
    
    # Evaluate at a specific point (x=0, t=0.5)
    X_test = np.array([[0.0, 0.5]])
    C_pred = model.predict(X_test)
    print(f"Predicted Concentration C(x=0, t=0.5): {C_pred[0][0]:.4f}")
    print("This demonstrates solving user-defined transport equations.")

except Exception as e:
    print(f"DeepXDE demo failed: {e}")
    # import traceback
    # traceback.print_exc()

# --- PhiFlow Demo: Fluid Dynamics (Momentum Transfer) ---
print("\n--- PhiFlow Demo: Fluid Dynamics (Momentum Transfer) ---")
try:
    # Try importing phiflow
    from phi.flow import *
    from phi import math
    
    print("PhiFlow imported successfully.")
    
    # Define a domain (2D Grid)
    # Simulates Navier-Stokes (Momentum) + Advection (Mass/Heat)
    print("Creating 32x32 Fluid Domain with Buoyancy (Heat/Concentration driven flow)...")
    
    # Domain definition
    # box defines physical size, resolution is grid cells
    # Note: PhiFlow API usually infers domain size from grid creation or explicitly.
    # We will use a standard phiflow construct for a CenteredGrid.
    
    # 1. Initialize Velocity Field (Momentum)
    velocity = StaggeredGrid((0, 0), extrapolation.ZERO, x=32, y=32, bounds=Box(x=100, y=100))
    
    # 2. Initialize Smoke/Temperature Field (Scalar)
    # This represents 'Concentration' or 'Temperature' field
    smoke = CenteredGrid(0, extrapolation.BOUNDARY, x=32, y=32, bounds=Box(x=100, y=100))
    
    # 3. Add a source (Hot spot / High concentration)
    # "Inflow" at bottom
    inflow = Sphere(center=(50, 10), radius=5)
    smoke += inflow
    
    print("Initial State created.")

    # 4. Simulation Step
    def step(v, s, dt=1.0):
        # A. Advection (Mass/Heat Transfer via fluid motion)
        s = advect.mac_cormack(s, v, dt)
        v = advect.semi_lagrangian(v, v, dt)
        
        # B. Buoyancy force (Coupling: Field -> Momentum)
        # Hot smoke rises (Temperature/Concentration affects Momentum)
        buoyancy_force = s * (0, 0.1) # Gravity/Buoyancy generic factor
        v = v + buoyancy_force * dt
        
        # C. Pressure Projection (incompressible flow continuity)
        v, pressure = fluid.make_incompressible(v)
        return v, s

    print("Running 5 simulation steps (Momentum + Mass Transfer)...")
    for i in range(5):
        velocity, smoke = step(velocity, smoke)
        max_val = math.max(smoke.values)
        print(f"Step {i+1}: Max Concentration/Temp = {max_val:.4f}")

    print("PhiFlow simulation completed successfully.")

except ImportError:
    print("PhiFlow import failed. Please check installation.")
except Exception as e:
    print(f"PhiFlow demo failed: {e}")
    # print("Note: PhiFlow API changes frequently. This example assumes 'phi.flow' namespace.")
