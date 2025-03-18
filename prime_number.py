def is_prime(n):
    if n<=1:
        return(False)
    for i in range(2,int(n/2)+1):
        if n%i==0:
            return(False)
    return(True)
a=int(input("initial value="))
b=int(input("final value="))
for l in range(a,b+1):
    print(l," ",is_prime(l))

