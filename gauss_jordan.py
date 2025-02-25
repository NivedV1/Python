from numpy import*
from numpy import*
a=3
u=zeros((a,a+1),float)
for p in range(a):
    for l in range(a):
        b=int(input("enter values="))
        u[p][l]=b
print(u)
