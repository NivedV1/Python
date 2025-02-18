from matplotlib import*
from numpy import*
from inverse import*
n=int(input("no of data points="))
x_value=[]
y_value=[]
for i in range(n):
    x_value.append(float(input("x data=")))
    y_value.append(float(input("y data=")))
print(x_value);print(y_value)
x=zeros((n,n))
y=zeros((n,1))
for i in range(n):
    y[i][0]=(y_value[i])
    for j in range(n):
        x[j][i]=(x_value[j]**i)
print(x);print(y)
invx=inv(x)
ans=dot(invx,y)
print(ans)
leng=len(ans)
x =linspace((x_value[0])-5,(x_value[n-1])+5, 256)
coefficents= ans.flatten()
polyn=poly1d(coefficents[::-1])
print(polyn)
y=polyn(x)
plot(x,y)
plot(x_value,y_value,':dg')
show()