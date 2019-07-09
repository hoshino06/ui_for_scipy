# -*- coding: utf-8 -*-
"""
関数 :py:func:`scipy:scipy.integrate.solve_ivp` に対するAPIを提供するモジュールです. 
初期値問題を解く場合には, :py:class:`InitialValueProb` を利用してください. 
また, integrate.solve_ivpに与える関数のみを得る場合には
:py:class:`Vectorfield` を利用してください. 
"""
import numpy as np
from numpy import sin
import sympy as sym
from scipy.integrate import solve_ivp
import unittest
import importlib

# ############################
def pendurum_diff(t, x):
    dydt = np.zeros_like(x)
    dydt[0] = x[1]
    dydt[1] = -(G/L)*sin(x[0])
    return dydt
 
G  = 9.8         # 重力加速度
L = 1            # 振り子の長さ

th1 = 30.0      # 角度の初期値[deg]
w1 = 0.0        # 角速度の初期値[deg]
 # 初期状態
state = np.radians([th1, w1])

dt = 0.05
t = np.arange(0.0, 25, dt)
sol = solve_ivp(pendurum_diff, t_span=[0,10], y0=[th1,w1])
# ##############################

class Vectorfield:
    """
    求解したい微分方程式のベクトル場を表す関数を生成するクラス. 
    """
    def __init__(self, x):
        """
        :arg x: 従属変数
        :type x: :py:class:`Symbol <sympy:sympy.core.symbol.Symbol>` or 
                 :py:class:`tuple`

        引数として, Symbolsクラスのオブジェクト, またはそれらを要素に持つtupleを与えてください.
        """
        self.x = []
        self.dim = None
        self._set_dependent_variables(x)
        self.derivative = {}
        
    def _set_dependent_variables(self, x):
        """
        従属変数を読み込んで次元を設定
        """
        if isinstance(x, sym.Symbol):
            self.x.append(x)
        elif hasattr(x, "__iter__"):
            for x_i in x:
                if isinstance(x_i, sym.Symbol):
                    self.x.append(x_i)
                else:
                    raise TypeError('引数xの要素はSymbol型にしてください')
        else:
            raise TypeError('引数xはSymbol型ないしそのコンテナにしてください')  
        self.dim = len(self.x)

    def set_derivative(self, dxdt):
        """
        計算する微分方程式\dot{x} = f(x,t)の右辺を設定
        """
        if isinstance(dxdt, dict):
            self.derivative = dxdt
        else:
            raise TypeError()

    def get_function(self):
        """
        :return: ベクトル場を表す関数
        
        :py:func:`solve_ivp <scipy:scipy.integrate.solve_ivp>`
        の引数 fun を生成するためのメソッド 
        """
        self._write_function()
        import function
        importlib.reload(function)
        fun = function.func
        return fun

    def _write_function(self):
        dxdt =  []
        for i in range(self.dim):
            dxdt.append(self.derivative[self.x[i]].subs(self._var2num_list()))
        with open('function.py', 'w') as f:
            f.write('# This file is automatically generated: do not edit this. \n')
            f.write('import numpy as np \n')
            f.write('def func(t, x):\n' )
            f.write('    dxdt = np.zeros_like(x)\n')
            for i in range(len(dxdt)):
                f.write(f'    dxdt[{i}] = {dxdt[i]}\n'  )
            f.write('    return dxdt\n'    )
        return
    
    def _var2num_list(self):
        """
        変数の対応を表すタプル(variable, x[i])のリストを取得
        """
        x = list(self.derivative.keys())
        var_list = []
        for i in range(self.dim):
            var_list.append((x[i], f'x[{i}]'))
        return var_list

    
class _TestVectorField(unittest.TestCase):
    """
    class:Vectorfield のユニットテスト用のクラス
    """  
    def test_1st_order_liner(self):
        """
        dx/dt = -x
        """
        print('-vf 1st order---')
        x = sym.Symbol('x')
        vf = Vectorfield(x)
        dxdt = {x: -x}
        vf.set_derivative(dxdt)
        fun = vf.get_function()
        print(fun)
        print(fun(0,[2]))

    def test_2nd_order_liner(self):
        """
        dx1/dt = x2; dx2/dt = -2*x1
        """
        print('-vf 2nd order---')
        x1,x2 = sym.symbols('x1,x2')
        vf = Vectorfield([x1,x2])
        dxdt = {x1: x2,
                x2: -2*x1}
        vf.set_derivative(dxdt)        
        fun = vf.get_function()
        print(fun)
        print(fun(0,[2,3]))        

    

class InitialValueProb:
    """
    常微分方程式の初期値問題を解くためのクラス
    """
    def __init__(self):
        '''
        solve_ivpの使い方:
            scipy.integrate.solve_ivp(fun: 微分方程式dy/dt = f(t,y)の右辺, 
                                      t_span: , 
                                      y0, 
                                      method='RK45', 
                                      t_eval=None, 
                                      dense_output=False, 
                                      events=None, 
                                      vectorized=False, 
                                      **options)
        '''
        self.x = []
        self.fun = None
        self.t_span = None
        self.y0 = []
        self.method = 'RK45'
        self.t_eval = None
        self.dense_output = False
        self.events = None
        self.vectorized = False
        self.options = None

    def set_dependent_variables(self, x):
        """
        従属変数を読み込んで次元を設定
        """
        if isinstance(x, sym.Symbol):
            self.x.append(x)
        elif isinstance(x, tuple):
            for x_i in x:
                if isinstance(x_i, sym.Symbol):
                    self.x.append(x_i)
                else:
                    raise TypeError()
        else:
            raise TypeError()

    def set_derivative(self, dxdt):
        """
        :arg dxdt: {x_i: f_i(x)}
        :type dxdt: dict
        
        計算する微分方程式\dot{x} = f(x,t)の右辺を設定
        """
        vf = Vectorfield(self.x)
        vf.set_derivative(dxdt)
        self.fun = vf.get_function()
        
    def set_time_span(self, init, end):
        """
        :arg init: 始点 
        :arg end: 終点
        
        独立変数の期間(t_span)を設定するメソッドです. 
        """
        self.t_span = [init, end]
        
    def set_initial_value(self, y0):
        """
        :arg y0: 初期値
        :type y0: dict
        
        初期値を設定するメソッドです. 
        """
        for xi in self.x:
           self.y0.append(y0[xi])
        
    def set_sampling_times(self, t_eval):
        self.t_eval = t_eval
        
    def get_solution(self):
        """
        :return: 初期値問題の解
        :rtype:  :py:func:`scipy:scipy.integrate.solve_ivp` の戻り値
        
        初期値問題の解を得るメソッドです. 
        integrate.solve_ivp関数を呼び出して, その戻り値をそのまま返します. 

        """
        sol = solve_ivp(self.fun, self.t_span, self.y0, 
                        t_eval=self.t_eval)
        return sol        


class _TestIntialValueProb(unittest.TestCase):
    """
    InitialValuProbのユニットテスト用のクラス
    """    

    def test_2nd_order_liner_ipv(self):
        """
        2階線形微分方程式
        """
        x1,x2 = sym.symbols('x1,x2')
        ipv = InitialValueProb()
        ipv.set_dependent_variables((x1,x2)) 
        
        dxdt = {x1: x2,
                x2: -2*x1 }
        ipv.set_derivative(dxdt)
        ipv.set_time_span(0,1)
        init = {x1: 1,
                x2: 0 }
        ipv.set_initial_value(init)
        sol = ipv.get_solution()
        self.assertTrue(sol.success)


if __name__ == '__main__':     
    unittest.main()
    