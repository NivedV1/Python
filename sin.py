import matplotlib
from matplotlib import pyplot as plt
from numpy import*
n=int(input("no of data points="))
x_value=linspace(0,26,n)
y_value=sin(x_value)
print(x_value);print(y_value)
x=zeros((n,n))
y=zeros((n,1))
for i in range(n):
    y[i][0]=(y_value[i])
    for j in range(n):
        x[j][i]=(x_value[j]**i)
print("X=",x)
print("Y=",y)
invx=linalg.inv(x)
print(invx)
ans=dot(invx,y)
print(ans)
leng=len(ans)
x =linspace((x_value[0])+5,(x_value[n-1])-5, 2560)
coefficents= ans.flatten()
polyn=poly1d(coefficents[::-1])
print(polyn)
y=polyn(x)
plt.plot(x,y)
plt.plot(x_value,y_value,':dg')
plt.show()