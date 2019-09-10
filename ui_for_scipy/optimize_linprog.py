# -*- coding: utf-8 -*-
"""
関数 :py:func:`scipy:scipy.optimize.linprog` に対するAPIを提供するモジュールです. 
下記の :py:class:`LinearProg` クラスを使用してください. 
"""
import scipy.optimize as opt
import sympy as sym
import unittest

class LinearProg:
    """
    線形計画問題を定式化するためのクラス. 
    関数linprogに渡す引数のデータを保持. 
    """
    def __init__(self, x=None):
        """
        linprogの引数一覧:
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
        self.x = []
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
        :param x: 設定する決定変数のタプル
        :type x: :py:class:`tuple`
        
        決定変数を設定するメソッドです. 
        引数には, 
        :py:class:`Symbol <sympy:sympy.core.symbol.Symbol>` オブジェクトを
        要素に持つシーケンスを与えてください. 
        """
        if isinstance(x, sym.Symbol):
            self.x = [x]
        elif hasattr(x, '__iter__'):
            self.x = []
            for x_i in x:
                if isinstance(x_i, sym.Symbol):
                    self.x.append(x_i)
                else:
                    raise TypeError(f'{x}の中身はsym.Symbolにしてください')
        else:
            raise TypeError(f'引数にはsympy.Symbolオブジェクトまたはそれを含むシーケンスを与えてください')
                
    def append_decision_variables(self, x):
        """
        :arg x: 追加する決定変数
        :type x: :py:class:`Symbol <sympy:sympy.core.symbol.Symbol>` or 
                 :py:class:`tuple`

        決定変数を追加するためのメソッドです. 
        引数として, Symbolsクラスのオブジェクト, またはそれらを要素に持つtupleを与えてください.
        なお, 元々設定されている決定変数を上書きする場合には, 
        :py:meth:`set_decision_variables` を使用してください. 
        """
        if isinstance(x, sym.Symbol):
            self.x.append(x)
        elif hasattr(x, '__iter__'):
            for x_i in x:
                if isinstance(x_i, sym.Symbol):
                    self.x.append(x_i)
                else:
                    raise TypeError(f'{x}の中身はsym.Symbolにしてください')
        else:
            raise TypeError(f'引数にはsympy.Symbolオブジェクトまたはそれを含むシーケンスを与えてください')
            
    def set_cost_function(self, min_or_max, f):
        """
        :param min_or_max: 最適化の目的(最小化or最大化)
        :type min_or_max: :py:class:`str`
        :param f: 評価関数
        :type f: :py:class:`Expr <sympy:sympy.core.expr.Expr>`
        
        費用関数を設定するメソッドです. 
        引数min_or_maxには, "min"または"max"のいずれかを指定してください. 
        引数fには, 評価関数を表す :py:class:`Expr <sympy:sympy.core.expr.Expr>` オブジェクトを
        与えてください. 
        """
        if isinstance(f, sym.Expr):
            pass
        else:
            raise TypeError('引数にはsympy.Exprを与えてください')
            
        if min_or_max == 'min':
            f_canonical = f
            
        elif min_or_max == 'max':
            f_canonical = -f
        else:
            raise ValueError('引数min_or_maxには"min"もしくは"max"を指定してください')
            
        coeff = f_canonical.as_coefficients_dict()
        c = []        
        for x_i in self.x:
            if x_i in coeff:
                c.append(coeff[x_i])
            else:
                c.append(0)
        self.c = c
        
    def append_inequality(self, g):
        """
        :param g: 追加する不等式制約
        :type g: :py:class:`LessThan <sympy:sympy.core.relational.LessThan>`
        
        不等式制約を追加するメソッドです. 
        引数として, 不等式制約を直接表す
        :py:class:`LessThan <sympy:sympy.core.relational.LessThan>`
        を与えてください. 
        """
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
        """
        :param h: 追加する等式制約
        :type h: :py:class:`Expr <sympy:sympy.core.expr.Expr>` or 
                 :py:class:`Equality <sympy:sympy.core.relational.Equality>`
        
        等式制約を追加するためのメソッドです. 
        引数には,  
        等式制約h(x)=0の左辺を表す :py:class:`Expr <sympy:sympy.core.expr.Expr>` オブジェクト, 
        または等式制約を直接表す :py:class:`Equality <sympy:sympy.core.relational.Equality>` オブジェクトを与えてください. 
        """
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
        """
        :param x_i: 上下限制約を追加する決定変数
        :param lower: 下限
        :param upper: 上限
        :type x_i: :py:class:`Symbol <sympy:sympy.core.symbol.Symbol>`
        
        ある変数x_iの上下限制約を設定するメソッドです. 
        """
        self.bounds[x_i] = (lower, upper)
        
    def _get_bounds(self):
        """
        変数の上下限制約をすべてまとめるメソッドです.   
        """
        bounds = []
        for x_i in self.x:
            bound_for_xi = self.bounds.get(x_i, (None, None))
            bounds.append(bound_for_xi)
            
    def get_result(self): 
        """
        :return: optimal solution
        :rtype:  :py:class:`scipy:scipy.optimize.OptimizeResult`
        
        最適化問題の解を得るメソッドです. 
        linprog関数を呼び出して, 最適化問題の解を返します. 
        """
        if self.A_ub == [] or self.b_ub == []:
            self.A_ub = None
            self.b_ub = None
        if self.A_eq == [] or self.b_eq == []:
            self.A_eq = None
            self.b_eq = None
            
        res = opt.linprog(c=self.c, 
                          A_ub=self.A_ub, b_ub=self.b_ub, 
                          A_eq=self.A_eq, b_eq=self.b_eq, 
                          bounds=self._get_bounds()
                          )
        return res



class _TestLinearProg(unittest.TestCase):
    """
    LinearProgの単体テスト用のクラスです
    """
    def test_append_decision_variables(self):
        prog = LinearProg()
        x = sym.Symbol('x')
        prog.append_decision_variables(x)
        self.assertEqual(prog.x, [x])
        
        prog = LinearProg()
        x = sym.symbols('x:2')
        prog.append_decision_variables(x)
        self.assertEqual(prog.x, list(x))
        
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
        prog.append_equality( 5*x1 + 1*x2 - 24 )
        self.assertEqual(prog.A_eq, [[5, 1]])
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
