from numpy import*
a=3
#u=zeros((a,a),float)
#for p in range(a):
#    for l in range(a):
#        b=int(input("enter values="))
#        u[p][l]=b
u=[[5,2,3,1,0,0],[6,5,6,0,1,0],[7,8,9,0,0,1]]
u=array(u)
print(u)
while u[0][0]==0:
    for i in range(a):
        u[[0,i]]=u[[i,0]]
print(u)
for i in range(a):
    for j in range(1,a):
        c=(u[i][j])
        u[i][j]=(u[i][j])
        u[j][i]=u[j][i]-(u[0][i]*u[j][i])

