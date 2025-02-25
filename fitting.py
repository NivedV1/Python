import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from numpy import*
def determinant(a):
    n=len(a)
    if n==1:
        return(a[0][0])
    if n==2:
        return (a[0][0]*a[1][1])-(a[0][1]*a[1][0])
    det=0
    for i in range(n):
        b=delete(a,0,0)
        b=delete(b,i,1)
        det+=a[0][i]*(-1)**i*determinant(b)
    return(det)

def inv(f):
    y=determinant(f)
    k=len(f)
    t=zeros((k,k),float)
    for i in range(k):
        for j in range(k):
            b=delete(f,j,0)
            b=delete(b,i,1)
            t[i][j]=(((-1)**(i+j))*determinant(b))
    s=t/y
    return(s)
x_data=[1,2,3,4,6,8]
y_data=[2,3,4,4,5,6]

n=int(input("enter the degree of polynomial="))

print(x_data) 
print(y_data)
sum_matrix=zeros((n+1,n+1),int)
for j in range(n+1):
        sum_matrix[i][j]=sum(x**(i+j) for x in x_data)
print(sum_matrix)

for j in range(n+1):
    sum_yx[j]=sum(y * x**j for x, y in zip(x_data, y_data))
invmat=(inv(sum_matrix))
print((sum_matrix))
print(sum_yx)
print(invmat)
ans=dot(invmat,sum_yx)
print(ans)
po=len(ans)
x =linspace(1, 8, 256)

coefficents= ans.flatten()
polyn=poly1d(coefficents[::-1])
print(polyn)
y=polyn(x)

plt.plot(x,y)
plt.plot(x_data,y_data,':dg')
xlabel("x")
ylabel("f(x)")
legend()
show()
plt.show()
