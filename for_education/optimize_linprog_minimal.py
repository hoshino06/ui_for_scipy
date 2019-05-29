# -*- coding: utf-8 -*-
"""
Created on Sun May 26 16:03:14 2019
@author: hoshino
scipy.optimizeのlinprogを扱いやすくするためのプログラム
"""
import scipy.optimize as opt
import sympy as sym

class LinearProg():
    '''
    linprogの使い方:
        linprog(c, A_ub, b_ub, A_eq, b_eq, bounds, method, callback, options, x0)
        minimize: c @ x
        s.t.:
            A_ub @ x <= b_ub
            A_eq @ x == b_eq
            lb <= x <= ub
    '''
    def __init__(self):
        self.x = set()
        self.c = []
        self.A_ub = []
        self.b_ub = []
        self.bounds = {}
    def set_decision_variables(self, x):
        self.x = x
    def set_cost_function(self, min_or_max, f):
        if min_or_max == 'min':
            f_canonical = f
        elif min_or_max == 'max':
            f_canonical = -f
        else:
            raise TypeError()
        coeff = f_canonical.as_coefficients_dict()
        c = []
        for x_i in self.x:
            if x_i in coeff:
                c.append(coeff[x_i])
            else:
                c.append(0)
        self.c = c
    def append_inequality(self, g):
        if isinstance(g, sym.LessThan):
            g_canonical = g.lhs - g.rhs
        else:
            raise TypeError()
        coeff = g_canonical.as_coefficients_dict()
        a = []
        for x_i in self.x:
            if x_i in coeff:
                a.append(coeff[x_i])
            else:
                a.append(0)
        b = -coeff[1]
        self.A_ub.append(a)
        self.b_ub.append(b)
    def set_bound(self, x_i, lower, upper):
        self.bounds[x_i] = (lower, upper)
    def get_bounds(self):
        bounds = []
        for x_i in self.x:
            bound_for_xi = self.bounds.get(x_i, (None, None))
            bounds.append(bound_for_xi)
    def get_result(self): 
        res = opt.linprog(c=self.c, 
                          A_ub=self.A_ub, b_ub=self.b_ub, 
                          bounds=self.get_bounds()
                          )
        return res
