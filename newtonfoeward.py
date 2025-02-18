from pylab import*
x_val=[]
y_val=[]
n=int(input("Enter number of data points="))
for i in range(n):
    x_val.append(float(input("x data=")))
    y_val.append(float(input("y data=")))
print(x_val);print(y_val)
y=[[0]*i for i in range(n-1,0,-1)]
print(y)
for i in range(n-1):   
    y[0][i]=y_val[i+1]-y_val[i]
for k in range(1,n-1):
     for j in range(0,n-1-k):
        y[k][j]=y[k-1][j+1]-y[k-1][j]               
print(y)

