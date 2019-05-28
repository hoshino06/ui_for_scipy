# -*- coding: utf-8 -*-
"""
Created on Mon May 27 12:37:58 2019

@author: hoshino
"""
import sympy as sym
import optimize_linprog as opt

x1, x2 = sym.symbols('x1, x2')

linprog = opt.LinearProg()

linprog.set_decision_variables((x1, x2))

linprog.set_cost_function('max', 28*x1 + 16*x2)

linprog.append_inequality(4*x1 + 3*x2 <= 24)
linprog.append_inequality(2*x1 +   x2 <= 10)

linprog.set_bound(x1, 0, None)
linprog.set_bound(x2, 0, None)

res = linprog.get_result()
