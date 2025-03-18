def is_prime(n):
    if n<=1:
        return(False)
    if n==2:
        return(True)
    for i in range(2,int(n/2)+1):
        if n%i==0:
            return(False)
    return(True)
#numb=int(input("enter number to check prime="))
#print(is_prime(numb))
for l in range(0,100):
    print(l," ",is_prime(l))
