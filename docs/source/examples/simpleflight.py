import numpy as np
from gpkit.shortcuts import *

# Constants
k = Var("k", 1.2, "-", "form factor")
e = Var("e", 0.95, "-", "Oswald efficiency factor")
mu = Var("\\mu", 1.78e-5, "kg/m/s", "viscosity of air")
pi = Var("\\pi", np.pi, "-", "half of the circle constant")
rho = Var("\\rho", 1.23, "kg/m^3", "density of air")
tau = Var("\\tau", 0.12, "-", "airfoil thickness to chord ratio")
N_ult = Var("N_{ult}", 3.8, "-", "ultimate load factor")
V_min = Var("V_{min}", 22, "m/s", "takeoff speed")
C_Lmax = Var("C_{L,max}", 1.5, "-", "max CL with flaps down")
S_wetratio = Var("(\\frac{S}{S_{wet}})", 2.05, "-", "wetted area ratio")
W_W_coeff1 = Var("W_{W_{coeff1}}", 8.71e-5, "1/m", "Wing Weight Coefficent 1")
W_W_coeff2 = Var("W_{W_{coeff2}}", 45.24, "Pa", "Wing Weight Coefficent 2")
CDA0 = Var("(CDA0)", 0.031, "m^2", "fuselage drag area")
W_0 = Var("W_0", 4940.0, "N", "aircraft weight excluding wing")

# Free Variables
D = Var("D", "N", "total drag force")
A = Var("A", "-", "aspect ratio")
S = Var("S", "m^2", "total wing area")
V = Var("V", "m/s", "cruising speed")
W = Var("W", "N", "total aircraft weight")
Re = Var("Re", "-", "Reynold's number")
C_D = Var("C_D", "-", "Drag coefficient of wing")
C_L = Var("C_L", "-", "Lift coefficent of wing")
C_f = Var("C_f", "-", "skin friction coefficient")
W_w = Var("W_w", "N", "wing weight")

constraints = []

# Drag model
C_D_fuse = CDA0/S
C_D_wpar = k*C_f*S_wetratio
C_D_ind = C_L**2/(pi*A*e)
constraints += [C_D >= C_D_fuse + C_D_wpar + C_D_ind]

# Wing weight model
W_w_strc = W_W_coeff1*(N_ult*A**1.5*(W_0*W*S)**0.5)/tau
W_w_surf = W_W_coeff2 * S
constraints += [W_w >= W_w_surf + W_w_strc]

# and the rest of the models
constraints += [D >= 0.5*rho*S*C_D*V**2,
                Re <= (rho/mu)*V*(S/A)**0.5,
                C_f >= 0.074/Re**0.2,
                W <= 0.5*rho*S*C_L*V**2,
                W <= 0.5*rho*S*C_Lmax*V_min**2,
                W >= W_0 + W_w]

print("SINGLE\n======")
m = Model(D, constraints)
sol = m.solve(verbosity=1)

print("SWEEP\n=====")
N = 2
sweeps = {V_min: ("sweep", np.linspace(20, 25, N)),
          V: ("sweep", np.linspace(45, 55, N)), }
m.substitutions.update(sweeps)
m.solve(verbosity=1)
