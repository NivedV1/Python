from math import*
a=int(input("coeff of X^2="))
b=int(input("coeff of X="))
c=int(input("constant="))
print("qudratic equation is",a,"*X^2+",b,"*X+",c)
d=(-b+(((b**2)-(4*a*c))**0.5))/(2*a)
e=(-b-(((b**2)-(4*a*c))**0.5))/(2*a)
print(complex(round(d.real,4),d.imag))
print(complex(round(e.real,4),e.imag))

    
