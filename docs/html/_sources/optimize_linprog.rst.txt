optimize\_linprog モジュール
==============================

これは線形計画問題(Linear Programming)の数値解を得るためのモジュールです. 

scipyには :func:`scipy:scipy.optimize.linprog` という関数が用意されており, 
これを使うことで線形計画問題の最適解を得ることができます. 
本モジュールの目的はこの関数をより簡単に扱えるようにすることです. 

また, このモジュールを少し修正することで他の関数(ソルバー)を使うこともできます. 

-------------------------------
linprog関数を直接使う場合
-------------------------------

まず, scipyのlinprog関数を直接使う場合の例を示します. 
ここでは例題として以下の問題(玉置,2005)を考えます. 

.. math::
       
    \begin{align}     
    &\max_{x_1, x_2} & f = 28 x_1 + 14 x_2 \quad \\    
    &\mathrm{subject} \, \mathrm{to} & 4 x_1 + 3 x_2 \le 24  \quad \\
    & & 2 x_1 + x_2 \le 10  \quad \\
    & & x_1, x_2 \ge 0  \quad
    \end{align}

関数linprogにより最適解を得るためには, 問題の行列表現を表すリスト(1D arrayや2D array)を作る必要があります. 
具体的には下記のようなコードとなります
(`ダウンロードはこちら <https://gist.github.com/hoshino06/d407a6093556d5b0b28d4d8c8cf5c5fa>`_). 

.. code-block:: python

    # scipyのoptimizeパッケージを読み込み
    import scipy.optimize as opt
    
    # 関数linprogに渡す引数を定義 (最適化問題を表す行列を作成)
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


-----------------------------------
本モジュールの使用例
-----------------------------------

上記の例で示したようにlinprog関数を使用するためには最適化問題を記述する行列(リスト)を作成する必要があります.
この作業は簡単な例であれば手間ではありませんが, 扱う問題がより大規模なものだと大変です.
本モジュールでは目的関数や制約条件をsympyの代数表現として与えると行列を自動生成してlinprog関数に与えてくれます. 

以下にコードの例を示します
(`ダウンロードはこちら <https://gist.github.com/hoshino06/df0f24df3d4333096ff10920fc7870b7>`_). 

.. code-block:: python

    # optimize_linprogモジュールを読み込み
    import ui_for_scipy.optimize_linprog  as opt
    
    # sympyパッケージの読み込み
    import sympy as sym
    
    # sympyパッケージのsymbols関数を利用して, x1およびx2という変数(Symbol)を定義
    x1, x2 = sym.symbols('x1, x2')
    
    # オブジェクトobj_linprogを作成 
    # (obj_linprogは, optimize_linprog_minimal.pyに定義されたLinProgクラスのオブジェクト)
    obj_linprog = opt.LinearProg()
    
    # obj_linprogに付随するメソッドを利用して, 最適化問題を定義
    # (この部分が読みやすくなっている)
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

    
----------------------------
リファレンス
----------------------------

.. automodule:: optimize_linprog
    :members:
    :undoc-members: 
    :show-inheritance:
