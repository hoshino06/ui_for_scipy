# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 17:39:38 2019
@author: hoshino
integrate_solve_ipv.pyを使用するためのサンプルコード
"""
import integrate_solve_ivp as ivp

import numpy as np
from numpy import sin, cos

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

ipv = ivp.InitialValueProb()

# ベクトル場の設定
G  = 9.8         # 重力加速度
L = 1            # 振り子の長さ
def pendurum_diff(t, state):
    dydt = np.zeros_like(state)
    dydt[0] = state[1]
    dydt[1] = -(G/L)*sin(state[0])
    return dydt
ipv.set_vector_field(pendurum_diff)

import sympy as sym

def fun_gen():
    x1,x2 = sym.symbols('x1, x2')
    x = [x1, x2]
    from sympy import sin
    delta = {}
    delta[x1] = x2
    delta[x2] = -sin(x1)
    def test_fun(state):
        dxdt = np.zeros_like(state)
        rep = []
        for j in range(len(x)):
            rep.append((x[j], state[j]))
        for i in range(len(x)):
            dxdt[i] = delta[x[i]].subs(rep)
        return dxdt
    return test_fun
test = fun_gen()
test([0.5,1])


 # 初期値の設定
theta0 = 30.0      # 角度の初期値[deg]
omega0 = 0.0        # 角速度の初期値[deg]
ipv.set_initial_value(np.radians([theta0, omega0]))

# 時間の設定
ipv.set_time_span(init=0.0, end=25)
dt = 0.05
t = np.arange(0.0, 25, dt)
ipv.set_sampling_times(t)

# 数値積分
sol = ipv.get_solution()
theta = sol.y[0,:]
x = L * sin(theta)
y = - L * cos(theta)

# 図の出力
fig = plt.figure()
ax = fig.add_subplot(111, autoscale_on=False, xlim=(-L, L), ylim=(-L, L))
ax.set_aspect('equal')
ax.grid()
 
line, = ax.plot([], [], 'o-', lw=2)

def animate(i):
    thisx = [0, x[i]]
    thisy = [0, y[i]] 
    line.set_data(thisx, thisy)
    return line,
 
ani = FuncAnimation(fig, animate, frames=np.arange(0, len(t)),interval=25,  blit = True)

plt.show()


