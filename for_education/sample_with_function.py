# -*- coding: utf-8 -*-
"""
------------------------
sample_with_function.py
------------------------
- 数値計算を実行する関数linprogを直接呼び出すプログラムの例
- scipy.optimizeの関数linprog(線形計画法を解く関数)を直接利用
- linprogの使い方: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html
"""
# scipyのoptimizeパッケージを呼び出してoptという名前を付ける
import scipy.optimize as opt

# 関数linprogに渡す引数を定義 (この部分をどのように書くかが問題!!)
c = [-28, -16]
A = [[4,3],[2, 1]]
b = [24, 10]
x0_bounds = (0, None)
x1_bounds = (0, None)
bounds = [x0_bounds, x1_bounds]

# scipy.optimize(opt)のlinprog関数を使って最適化問題の解(res)を取得
res = opt.linprog(c, A_ub=A, b_ub=b, bounds=bounds)

# 結果を表示
print(f'fmax = {-res.fun}')
print(f'x1 = {res.x[0]}, x2 = {res.x[1]}')