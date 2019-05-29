# -*- coding: utf-8 -*-
"""
------------------------
sample_with_function.py
------------------------
- 数値計算を実行する関数を直接呼び出すプログラムの例
- scipy.optimizeの関数linprog(線形計画法を解く関数)を直接利用
- linprogの使い方: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html
"""
import sympy as sym
import optimize_linprog_minimal as opt

x1, x2 = sym.symbols('x1, x2')

linprog = opt.LinearProg() # 

linprog.set_decision_variables((x1, x2))

linprog.set_cost_function('max', 28*x1 + 16*x2)
linprog.append_inequality(4*x1 + 3*x2 <= 24)
linprog.append_inequality(2*x1 +   x2 <= 10)
linprog.set_bound(x1, 0, None)
linprog.set_bound(x2, 0, None)

res = linprog.get_result()

print(f'fmax = {-res.fun}')
print(f'x1 = {res.x[0]}, x2 = {res.x[1]}')
 