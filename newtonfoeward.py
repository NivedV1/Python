from pylab import*
#x_val=[]
#y_val=[]
#n=int(input("Enter number of data points="))
#for i in range(n):
#    x_val.append(float(input("x data=")))
#    y_val.append(float(input("y data=")))
def diff(a):
    for i in range(len(a)-1):
        print(i)
        lst.append(a[i+1]-a[i])
    return(lst)
n=4
x_val=[0,1,2,3]
y_val=[1,10,30,100]

print(x_val);print(y_val)
#lst=[[] for _ in range(n-1)]
lst=[]
y=[[0]*i for i in range(n-1,0,-1)]
print(y)
for i in range(n-1):
    y[0][i]=y_val[i+1]-y_val[i]
for k in range(1,n-1):
     for j in range(0,n-1-k):
        y[k][j]=y[k-1][j+1]-y[k-1][j]               
print(y)
const=1
inter=0
for i in range(n-1):

    inter=inter+(((y[i][0])*const)/fact(i))
print(inter)