# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 13:21:47 2019

@author: hoshino
"""
from solve_ivp import Vectorfield, InitialValueProb
import numpy as np

import sympy as sym
import unittest

#############################################################
# Vectorfieldクラス
#############################################################
class Test1_VectorField(unittest.TestCase):
    """
    class:Vectorfield のユニットテスト用のクラス
    """
    def test_1st_order_liner(self):
        """
        dx/dt = -x
        """
        print('\n-vf 1st order---')
        x = sym.Symbol('x')
        vf = Vectorfield(x)
        dxdt = {x: -x}        
        fun = vf.get_function(dxdt)
        print(f'f(t=0,y=2) = {fun(0,[2])}')

    def test_2nd_order_liner(self):
        """
        dx1/dt = x2; dx2/dt = -2*x1
        """
        print('-vf 2nd order---')
        x1,x2 = sym.symbols('x1,x2')
        vf = Vectorfield([x1,x2])
        dxdt = {x1: x2,
                x2: -2*x1}
        fun = vf.get_function(dxdt)
        print(f'f(t=0,y=[2,3]) = {fun(0,[2,3])}') 
        
    def test_3_pendurum(self):
        """
        関数を含む場合のテストです. 
        dx[1]/dt = x[2], dx[2]/dt = -sin(x[1]) 
        """ 
        print('-vf pendurum---')
        # 変数の設定
        theta, omega = sym.symbols('theta, omega')
        vf = Vectorfield([theta, omega])
        # ベクトル場の設定
        G = 9.8
        L = 1
        sin = sym.Function('sin')
        derivatives = {theta: omega,
                       omega: -(G/L)*sin(theta)}
        functions = {sin: 'from numpy import sin'}
        fun = vf.get_function(derivatives, functions)
        print(f'f(t=0,y=[2,3]) = {fun(0,[2,3])}') 

    def test_4_forced_pendurum(self):
        """
        非自励系のテストです. 
        dx[1]/dt = x[2], dx[2]/dt = -sin(x[1]) + sin(0.1t)
        """ 
        print('-vf forced-pendurum---')
        # 変数の設定        
        theta, omega = sym.symbols('theta, omega')
        t = sym.Symbol('t')
        vf = Vectorfield([theta, omega], t)
        # ベクトル場の設定
        G = 9.8
        L = 1
        sin = sym.Function('sin')
        derivatives = {theta: omega,
                       omega: -(G/L)*sin(theta) +sin(t) }
        functions = {sin: 'from numpy import sin'}
        fun = vf.get_function(derivatives, functions)
        print(f'f(t=1,y=[0.0,0.0]) = {fun(t=1.0,x=[0.0,0.0])}')
       
    def test_5_parametric_pendurum(self):
        """
        ベクトル場の設定に0(int型などの数値型)が含まれる場合のテストです. 
        dx[1]/dt = x[2], dx[2]/dt = -K*sin(x[1]) 
        """ 
        print('-vf parametric pendurum---')
        # 変数の設定
        theta, omega, K = sym.symbols('theta, omega, K')
        vf = Vectorfield([theta, omega, K])
        # ベクトル場の設定
        sin = sym.Function('sin')
        derivatives = {theta: omega,
                       omega: -K*sin(theta),
                       K    : 5.0 }
        functions = {sin: 'from numpy import sin'}
        fun = vf.get_function(derivatives, functions)
        print(f'f(t=0,y=[2,3,1]) = {fun(0,[2,3,1])}')


#############################################################
# InitialValueProbクラス: 解を計算するまでの部分
#############################################################
class Test2_IntialValueProb(unittest.TestCase):
    """
    InitialValuProbのユニットテスト用のクラス
    """    

    def test_2nd_order_liner_ipv(self):
        """
        2階線形微分方程式
        """
        # 変数の設定
        x1,x2 = sym.symbols('x1,x2')
        ipv = InitialValueProb([x1,x2])
        # ベクトル場の設定
        dxdt = {x1: x2,
                x2: -2*x1 }
        ipv.set_derivative(dxdt)
        # 初期値の設定
        init = {x1: 1,
                x2: 0 }
        ipv.set_initial_value(init)
        # 数値解の取得
        ipv.set_time_span(0,1)
        sol = ipv.get_solution()
        self.assertTrue(sol.success)

    def test_pendurum_ipv(self):
        """
        dx[1]/dt = x[2], dx[2]/dt = -sin(x[1]) 
        """ 
        # 変数の設定
        theta, omega = sym.symbols('theta, omega')
        ipv = InitialValueProb([theta, omega])
        # ベクトル場の設定
        G = 9.8
        L = 1
        sin = sym.Function('sin')
        derivatives = {theta: omega,
                       omega: -(G/L)*sin(theta)}
        functions = {sin: 'from numpy import sin'}
        ipv.set_derivative(derivatives,functions)
        # 初期値の設定
        init = {theta: np.radians(30.0),
                omega: np.radians(0) }
        ipv.set_initial_value(init)
        # 数値解の計算
        ipv.set_time_span(0,10)
        sol = ipv.get_solution()
        self.assertTrue(sol.success)
        
    def test_forced_pendurum_ipv(self):
        """
        dx[1]/dt = x[2], dx[2]/dt = -sin(x[1]) 
        """ 
        # 変数の設定
        theta, omega = sym.symbols('theta, omega')
        t = sym.Symbol('t')
        ipv = InitialValueProb([theta, omega], t)
        # ベクトル場の設定
        G = 9.8
        L = 1
        sin = sym.Function('sin')
        derivatives = {theta: omega,
                       omega: -(G/L)*sin(theta) + sin(t)}
        functions = {sin: 'from numpy import sin'}
        ipv.set_derivative(derivatives,functions)
        # 初期値の設定
        init = {theta: np.radians(30.0),
                omega: np.radians(0) }
        ipv.set_initial_value(init)
        # 数値解の計算
        ipv.set_time_span(0,10)
        sol = ipv.get_solution(method='RK23')
        self.assertTrue(sol.success)
        

#############################################################
# InitialValueProbクラス: 解を計算してからの部分
#############################################################
class Test3_IntialValueProbPostCal(unittest.TestCase):
    """
    InitialValuProbのユニットテスト用のクラス
    """    
    # 変数の設定
    theta, omega = sym.symbols('theta, omega')
    t = sym.Symbol('t')
    ipv = InitialValueProb([theta, omega], t)
    # ベクトル場の設定
    G = 9.8
    L = 1
    sin = sym.Function('sin')
    derivatives = {theta: omega,
                   omega: -(G/L)*sin(theta) + sin(t)}
    functions = {sin: 'from numpy import sin'}
    ipv.set_derivative(derivatives,functions)
    # 初期値の設定
    init = {theta: np.radians(30.0),
            omega: np.radians(0) }
    ipv.set_initial_value(init)
    # 数値解の計算
    ipv.set_time_span(0,10)
    ipv.get_solution(method='RK23')
    
    def test_last_value(self):
        """
        最終の値を得るためのメソッド
        """
        print('-ivp_post: last value---')
        last_bymethod = self.ipv.get_lastvalue()
        last_bymanual = self.ipv.solution.y[:,-1]
        self.assertTrue( (last_bymethod==last_bymanual).all() )
        print(f'last value = {last_bymethod}')
        #print(self.ipv.solution.y)


if __name__ == '__main__':     
    unittest.main()
    