from numpy import*
a=int(input("size of matrix="))
u=zeros((a,2*a),float)
print(u)
for i in range(a):
    u[i][i+a]=1
print(u)