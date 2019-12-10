# -*- coding: utf-8 -*-
"""
これは常微分方程式の初期値問題を数値的に解くためのモジュールです. 

次式で表される問題の解を計算します::  
    
    dy / dt = f(t, y)
    y(t0) = y0

ただし, t は一次元の独立変数（時間など）, y(t) はn次元のベクトル値関数（状態）を表します. 
n次元のベクトル値関数  f(t, y) により常微分方程式（ベクトル場）が記述されます. 
初期値 y(t0)=y0 が与えられた際の微分方程式の近似解を計算します. 

本モジュールの :py:class:`InitialValueProb` クラスを利用して初期値問題を構成すれば, 
内部でScipyの関数 :py:func:`scipy:scipy.integrate.solve_ivp` が呼び出され,  
数値解を得ることができます. 
なお, ベクトル場 f(t, y)のみを得たい場合には, :py:class:`Vectorfield` クラスを利用してください. 

使用例
------------

線形定数係数状微分方程式

.. code-block:: python

    import sympy as sym 
    from ui_for_scipy import InitialValueProb
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


非自励系の場合

.. code-block:: python
 
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
   
リファレンス
------------
 
"""
import sympy as sym
from scipy.integrate import solve_ivp
import importlib

######################################
# Vectorfield class
######################################
class Vectorfield:
    """
    :arg x: 従属変数（状態変数）
    :type x: :py:class:`Symbol <sympy:sympy.core.symbol.Symbol>` or 
             :py:class:`tuple`

    求解したい微分方程式のベクトル場を表す関数を生成するためのクラスです. 
    状態変数y（と必要な場合は独立変数t）を指定してインスタンス化してください. 
    なお, これらの変数はSymbolsクラスのオブジェクト, またはそれらを要素に持つtupleとしてください. 
    
    .. code-block:: python
    
        import sympy as sym 
        from ui_for_scipy import Vectorfield
        # インスタンス（vf）の作成
        x1,x2 = sym.symbols('x1,x2')
        vf = Vectorfield(x=(x1,x2))
        # ベクトル場の生成
        dxdt = {x1: x2,
                x2: -2*x1 }　            
        func = vf.get_function(dxdt) # ベクトル場を表す関数funcを取得
    """
    def __init__(self, x, t=None):
        self.dim = None
        self.derivative = {}
        # 状態変数の設定
        self.x = []
        self._set_dependent_variables(x)
        # 独立変数の設定
        self.t = None
        if t:
            if isinstance(t, sym.Symbol):
                self.t = t
            else: 
                raise TypeError('独立変数tはSymbol型で指定してください')  
        
    def _set_dependent_variables(self, x):
        """
        位相空間の変数を設定する関数です. コンストラクタによって呼び出されます. 
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

    def get_function(self, dxdt, func=None):
        """
        :arg dxdt: 
        :type dxdt: dict
        :return: ベクトル場を表す関数
        
        ベクトル場を表す関数f(y,t)を取得するためのメソッドです. 
        引数dxdtには, 各状態変数の時間変化を記述する関数f_i(x,t)のディクショナリを与えてください. 
        """
        # 引数チェック
        if isinstance(dxdt, dict):
            # dxdtが辞書型の場合
            for variable in dxdt:

                if isinstance(dxdt[variable], sym.Expr):
                    pass
                else:
                    try:
                        dxdt[variable] = sym.Number(dxdt[variable])
                    except:
                        raise TypeError(f'引数dxdt内の{variable}の値が不正です')
                        
            # チェックOK => self.derivativeに格納
            self.derivative = dxdt

        else:
            raise TypeError('引数dxdtには辞書型オブジェクトをあたえてください')
            
        # 関数をファイルに書き込み
        self.write_function('function.py', dxdt, func)

        # 書き込んだファイルをインポート
        import function
        importlib.reload(function) #複数回functionを読んだときに常に再読み込み
        fun = function.func
        return fun

    def write_function(self, filename, dxdt, func=None):
        """
        ベクトル場の関数をf(y,t)をファイルに書き込みます. 
        """
        # ベクトル場をx=(x1,x2,x3,...,xn)という添え字で表現
        deriv =  []
        for i in range(self.dim):
            deriv.append(self.derivative[self.x[i]].subs(self._var2num_list()))
        # ファイルに書き込み
        with open(filename, 'w') as f:
            # プリアンブル
            f.write('# This file is automatically generated: do not edit this. \n')
            f.write('import numpy as np \n')
            # 補助関数などの定義を書き込み
            if func:
                for key in func:
                    f.write(f'{func[key]}\n')
            #　ベクトル場を表す関数書き込み
            f.write('def func(t, x):\n' )
            f.write('    dxdt = np.zeros_like(x)\n')
            for i in range(len(dxdt)):
                f.write(f'    dxdt[{i}] = {deriv[i]}\n')
            f.write('    return dxdt\n')
        return
        # 書き込んだファイルのチェックを追加予定
    
    def _var2num_list(self):
        """
        変数の対応を表すタプル(variable, x[i])のリストを取得
        """
        # 状態変数を置き換えるリスト
        var_list = []
        for i in range(self.dim):
            var_list.append((self.x[i], f'x[{i}]'))
        # 独立変数の置き換え
        if self.t:
            var_list.append((self.t, f't'))
        return var_list
 
        
######################################
# InitialValueProb class
######################################
class InitialValueProb:
    """
    :arg x: 従属変数（状態変数）
    :type x: :py:class:`Symbol <sympy:sympy.core.symbol.Symbol>` or 
             :py:class:`tuple`
    :arg t: 独立変数（時間など）
    :type t: :py:class:`Symbol <sympy:sympy.core.symbol.Symbol>` 
    
    常微分方程式の初期値問題を解くためのクラスです. 使用例を以下に示します.
    """
    def __init__(self, y, t=None):
        '''
        InitialValueProbのコンストラクタ
        '''
        self.x = []
        if y: 
            self._set_dependent_variables(y, t)
        self.t = None
        self.fun = None
        self.t_span = None
        self.y0 = []


    def _set_dependent_variables(self, x, t=None):
        """
        :arg x: 従属変数（状態変数）
        :type x: :py:class:`Symbol <sympy:sympy.core.symbol.Symbol>` or 
                 :py:class:`tuple`
        :arg t: 独立変数（時間など）
        :type t: :py:class:`Symbol <sympy:sympy.core.symbol.Symbol>` 
            
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
        
        if t:
            self.t = t

    def set_derivative(self, dxdt, functions=None):
        """
        :arg dxdt: {x_i: f_i(x)}
        :type dxdt: dict
        :arg functions: 関数
        
        計算する微分方程式\dot{x} = f(x,t)の右辺を設定. 
        """
        vf = Vectorfield(self.x, self.t)
        self.fun = vf.get_function(dxdt, functions)
        
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
        
    def get_solution(self, **kwargs):
        """
        :arg kwargs: 任意のキーワード引数
        
        :return: 初期値問題の解
        :rtype:  :py:func:`scipy:scipy.integrate.solve_ivp` の戻り値
        
        初期値問題の解を得るメソッドです. 
        integrate.solve_ivp関数を呼び出して, その戻り値をそのまま返します. 
        その結果はself.solutionに格納されます
        """            
        sol = solve_ivp(self.fun, self.t_span, y0=self.y0, **kwargs)
        self.solution = sol
        return sol

    def get_timecourse(self, variable):
        """
        指定した変数の時系列データを取り出します. 
        """
        var_idx = self.x.index(variable)
        timecourse = self.solution.y[var_idx]
        
        return timecourse
        
    def get_lastvalue(self, variable=None):
        """
        計算した解の最後の値を返します
        """
        if variable is None:
            
            return self.solution.y[:,-1]
        
        