from numpy import*
a=3
#u=zeros((a,a),float)
#for p in range(a):
#    for l in range(a):
#        b=int(input("enter values="))
#        u[p][l]=b
u=[[5,2,4,1,0,0],[6,5,6,0,1,0],[7,8,9,0,0,1]]
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

