# This file is automatically generated: do not edit this. 
import numpy as np 
from numpy import sin
def func(t, x):
    dxdt = np.zeros_like(x)
    dxdt[0] = x[1]
    dxdt[1] = -9.8*sin(x[0])
    return dxdt
