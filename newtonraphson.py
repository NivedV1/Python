def f(x):
    return x**4-x-10
def df(x):
    return 4*x**3-1
def sol(x):
    while True:
        h=f(x)/df(x)
        if abs(h)<0.000001:
            break
        x=x-h
    return print(x)
sol(2)
