# -*- coding: utf-8 -*-
"""
------------------------
sample_with_object.py
------------------------
- 数値計算を実行するオブジェクトobj_linprogを作成する例
- オブジェクトobj_linprogの仕様(クラス定義)は別ファイルoptimize_linprog_minimal.pyに記述
- オブジェクトojb_linprogが, 関数linprogの引数となるデータの保持および成形を担当
"""
# optimize_linprog_minimalモジュールを読み込んでoptという名前を付ける
import optimize_linprog_minimal as opt

# sympyというパッケージを読み込んでsymという名前を付ける
import sympy as sym

# sympyパッケージのsymbols関数を利用して, x1およびx2という変数(Symbol)を定義
x1, x2 = sym.symbols('x1, x2')

# オブジェクトobj_linprogを作成 
# (obj_linprogは, optimize_linprog_minimal.pyに定義されたLinProgクラスのオブジェクト)
obj_linprog = opt.LinearProg()

# obj_linprogに付随する「メソッド」を利用して, 最適化問題を定義 (この部分が読みやすくなっていることが重要!!)
obj_linprog.set_decision_variables((x1, x2))
obj_linprog.set_cost_function('max', 28*x1 + 16*x2)
obj_linprog.append_inequality(4*x1 + 3*x2 <= 24)
obj_linprog.append_inequality(2*x1 +   x2 <= 10)
obj_linprog.set_bound(x1, 0, None)
obj_linprog.set_bound(x2, 0, None)

# 最適化問題の解(res)を取得
res = obj_linprog.get_result()

# 結果を表示
print(f'fmax = {-res.fun}')
print(f'x1 = {res.x[0]}, x2 = {res.x[1]}')