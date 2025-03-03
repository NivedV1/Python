from numpy import*
a=int(input("size of matrix="))
u=zeros((a,2*a),float)
for p in range(a):
    for l in range(a):
        b=int(input("enter values="))
        u[p][l]=b
        u[p][p+a]=1
u=array(u,float)
while u[0][0]==0:
    for i in range(a):
        u[[0,i]]=u[[i,0]]
print(u)
for i in range(a):
    u[i] = u[i]/u[i,i]
    for j in range(a):
        if j != i:
            u[j]=u[j]-u[j,i]*u[i]
print(u[:, a:])

