# -*- coding: utf-8 -*-
"""
Scipy.optimizeの関数linprogに対するAIP
"""
import scipy.optimize as opt
import sympy as sym
import unittest

class LinearProg():
    """
    線形計画問題を定式化するためのクラス. 関数linprogを用いて解く. 
    """
    def __init__(self, x=None):
        self.x = set()
        self.c = []
        self.A_ub = []
        self.b_ub = []
        self.A_eq = []
        self.b_eq = []
        self.bounds = {}
        self.method = 'interior-point'
        self.callback = None
        self.options = None
        self.x0 = None
        if x:
            self.x = x
    def set_decision_variables(self, x):
        """
        決定変数を設定するメソッド    
        
        :param x: 追加する決定変数
        :type x: Symbol
        """
        self.x = x
    def append_decision_variables(self, x):
        """
        決定変数を追加するメソッド    
        
        :param x: 追加する決定変数
        :type x: Symbol
        """
        if isinstance(x, sym.Symbol):
            self.x.add(x)
        elif isinstance(x, tuple):
            for x_i in x:
                if isinstance(x_i, sym.Symbol):
                    self.x.add(x_i)
                else:
                    raise TypeError()
        else:
            raise TypeError()
    def set_cost_function(self, min_or_max, f):
        """
        費用関数を設定するメソッド    
        
        :param f: 追加する決定変数
        :type f: Symbol
        """
        if isinstance(f, sym.Expr):
            pass
        else:
            raise TypeError()
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
    def append_equality(self, h):
        if isinstance(h, sym.Equality):
            h_canonical = h.lhs - h.rhs
        elif isinstance(h, sym.Expr):
            h_canonical = h
        else:
            raise TypeError()
        coeff = h_canonical.as_coefficients_dict()
        a = []
        for x_i in self.x:
            if x_i in coeff:
                a.append(coeff[x_i])
            else:
                a.append(0)
        b = -coeff[1]
        self.A_eq.append(a)
        self.b_eq.append(b)
    def set_bound(self, x_i, lower, upper):
        self.bounds[x_i] = (lower, upper)
    def get_bounds(self):
        bounds = []
        for x_i in self.x:
            bound_for_xi = self.bounds.get(x_i, (None, None))
            bounds.append(bound_for_xi)
    def get_result(self): 
        """
        最適化問題の解を得るメソッド
        """
        res = opt.linprog(c=self.c, 
                          A_ub=self.A_ub, b_ub=self.b_ub, 
                          bounds=self.get_bounds()
                          )
        """
        linprogの引数:
            linprog(c, A_ub, b_ub, A_eq, b_eq, bounds, method, callback, options, x0) 
        c:
            評価関数 f = c.x の係数c
        A_bu, b_ub:
            不等式制約 A_ub.x <= b_ub の係数
        A_eq, b_eq:
            等式制約 A_eq.x == b_eq の係数
        bounds:    
            変数の上下限(lb <= x <= ub)
        """
        return res


class TestLinearProg(unittest.TestCase):

    def test_append_decision_variables(self):
        prog = LinearProg()
        x = sym.Symbol('x')
        prog.append_decision_variables(x)
        self.assertEqual(prog.x, {x})
        
        prog = LinearProg()
        x = sym.symbols('x:2')
        prog.append_decision_variables(x)
        self.assertEqual(prog.x, set(x))
        
    def test_set_cost_function(self):
        x1, x2 = sym.symbols('x1, x2')
        prog = LinearProg([x1, x2])
        prog.set_cost_function('max', 28*x1 + 16*x2)
        self.assertEqual(prog.c, [-28, -16])

    def test_append_inequality(self):
        x1, x2 = sym.symbols('x1, x2')
        prog = LinearProg([x1, x2])
        prog.append_inequality( 4*x1 + 3*x2 <= 24 )
        self.assertEqual(prog.A_ub, [[4, 3]])
        self.assertEqual(prog.b_ub, [24])
        
    def test_append_equality(self):
        x1, x2 = sym.symbols('x1, x2')
        prog = LinearProg([x1, x2])
        prog.append_equality( 4*x1 + 3*x2 - 24 )
        self.assertEqual(prog.A_eq, [[4, 3]])
        self.assertEqual(prog.b_eq, [24])        
    
    def test_optimization(self):
        x1, x2 = sym.symbols('x1, x2')
        linprog = LinearProg([x1, x2])
        linprog.set_cost_function('max', 28*x1 + 16*x2)
        linprog.append_inequality(4*x1 + 3*x2 <= 24)
        linprog.append_inequality(2*x1 +   x2 <= 10)
        linprog.set_bound(x1, 0, None)
        linprog.set_bound(x2, 0, None)
        res = linprog.get_result()
        self.assertEqual(res.fun, self.sample_result().fun)

    def sample_result(self):
        c = [-28, -16]
        A = [[4,3],[2, 1]]
        b = [24, 10]
        x0_bounds = (0, None)
        x1_bounds = (0, None)
        bounds = [x0_bounds, x1_bounds]
        res = opt.linprog(c, A_ub=A, b_ub=b, bounds=bounds)  
        return res
          
if __name__ == '__main__':     
    unittest.main()
