regula phalsi

from numpy import *

def f(x):
    return x**3 - x - 2

def b(x1, x2, tol=1e-6):
    n = 100

    f1 = f(x1)
    f2 = f(x2)

    if f1 * f2 > 0:
        print('Roots need not exist in the given interval')
    else:
        iteration = 0
        while iteration < n:
            x3 = (x1 * f2 - x2 * f1) / (f2 - f1)
            f3 = f(x3)

            if abs(f3) < tol:
                print(x3)
                return

            if f1 * f3 < 0:
                x2 = x3
                f2 = f3
            else:
                x1 = x3
                f1 = f3

            iteration += 1

        print("Method did not converge.")

b(1, 2)