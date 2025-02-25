from numpy import*
from numpy import*
a=3
#u=zeros((a,a),float)
#for p in range(a):
#    for l in range(a):
#        b=int(input("enter values="))
#        u[p][l]=b
u=[[6,2,3],[4,5,6],[7,8,9]]
print(u)
for i in range(a):
    for j in range(1,a):
        c=(u[i][j])
        u[i][j]=(u[i][j])/c
        u[j][i]=u[j][i]-(u[0][i]*u[j][i])
print(u)